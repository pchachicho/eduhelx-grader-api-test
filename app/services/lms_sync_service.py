import asyncio
from pydantic import BaseModel, root_validator
from typing import BinaryIO, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services import CourseService, CanvasService, LDAPService, AssignmentService, StudentService, InstructorService, UserService, UpdateCanvasAssignmentBody, LDAPUserInfoSchema
from app.models import AssignmentModel, StudentModel, SubmissionModel, InstructorModel, UserModel
from app.schemas import UpdateCourseSchema, UpdateAssignmentSchema
from app.core.exceptions import (
    AssignmentNotFoundException, NoCourseExistsException, 
    UserNotFoundException, LMSUserNotFoundException
)

class DatabaseLMSResourcePair(BaseModel):
    # User exists in LMS but not DB = create
    # User exists in DB but not LMS = delete
    # User exists in both DB and LMS = update
    db_resource: Any | None
    lms_resource: dict | None

    # User info may not be provided on user deletion, since it isn't needed.
    user_info: LDAPUserInfoSchema | None

    @root_validator
    def check_resource_defined(cls, values):
        db_resource, lms_resource = values.get("db_resource"), values.get("lms_resource")
        if db_resource is None and lms_resource is None:
            raise ValueError('At least one of "db_resource", "lms_resource" must be non-null')
        return values

class LmsSyncService:
    def __init__(self, session: Session):
        self.canvas_service = CanvasService(session)
        self.course_service = CourseService(session)
        self.assignment_service = AssignmentService(session)
        self.student_service = StudentService(session)
        self.instructor_service = InstructorService(session)
        self.user_service = UserService(session)
        self.ldap_service = LDAPService()
        self.session = session

    async def get_assignment(self, assignment_id):
        return await self.canvas_service.get_assignment(assignment_id)

    async def sync_course(self):
        print("SYNC COURSE")
        try:
            canvas_course = await self.canvas_service.get_course()
            print("CANVAS COURSE EXISTS")

            # Check if a course already exists in the database
            if(await self.course_service.get_course()):
                print("COURSE EXISTS ALREADY")
                #update the existing course
                await self.course_service.update_course(UpdateCourseSchema(
                    name=canvas_course["name"],
                    start_at=canvas_course["start_at"],
                    end_at=canvas_course["end_at"]
                ))
                print("UPDATED COURSE")

        except NoCourseExistsException as e:
            print("CREATING COURSE (LMS)", e)
            return await CourseService(self.session).create_course(
                name=canvas_course['name'], 
                start_at=canvas_course['start_at'], 
                end_at=canvas_course['end_at']
            )


    async def sync_assignments(self):
        canvas_assignments = await self.canvas_service.get_assignments()
        db_assignments = await self.assignment_service.get_assignments()

        # Delete assignments that are in the database but not in Canvas
        for assignment in db_assignments:
            if assignment.id not in [a['id'] for a in canvas_assignments]:
                await self.assignment_service.delete_assignment(assignment)

        for assignment in canvas_assignments:
            # Canvas uses -1 for unlimited attempts.
            max_attempts = assignment["allowed_attempts"] if assignment["allowed_attempts"] >= 0 else None
            try:
                db_assignment = await self.assignment_service.get_assignment_by_id(assignment['id'])

                await self.assignment_service.update_assignment(db_assignment, UpdateAssignmentSchema(
                    name=assignment["name"],
                    available_date=assignment["unlock_at"],
                    due_date=assignment["due_at"],
                    is_published=assignment["published"],
                    max_attempts=max_attempts
                ))

            except AssignmentNotFoundException as e:
                #create a new assignment
                await self.assignment_service.create_assignment(
                    id=assignment['id'],
                    name=assignment['name'], 
                    due_date=assignment['due_at'], 
                    available_date=assignment['unlock_at'],
                    directory_path=assignment['name'],
                    is_published=assignment['published'],
                    max_attempts=max_attempts
                )
        
        return canvas_assignments
    
    async def _pair_db_canvas_users(self, db_users: list[UserModel], canvas_users: list[dict], canvas_user_pids: list[str]):
        # User exists in Canvas but not DB = create
        # User exists in DB but not Canvas = delete
        # User exists in both DB and Canvas = update
        pairs = []
        
        async def process_canvas_user(canvas_user) -> DatabaseLMSResourcePair | None:
            pid, email, name = canvas_user.get("sis_user_id"), canvas_user.get("email"), canvas_user.get("name")
            if pid is None or email is None or name is None:
                print("Skipping over pending user", name or email or "<unknown>")
                return None

            try:
                print("getting user info for ", pid)
                user_info = self.ldap_service.get_user_info(pid)
                print(pid, "->", user_info.onyen)
            except UserNotFoundException:
                print("Skipping over student not in LDAP: ", pid or email or "<unknown>")
                return None

            try:
                user = await self.user_service.get_user_by_onyen(user_info.onyen)
                return DatabaseLMSResourcePair(db_resource=user, lms_resource=canvas_user, user_info=user_info)

            except UserNotFoundException:
                return DatabaseLMSResourcePair(db_resource=None, lms_resource=canvas_user, user_info=user_info)
        

        # We begin by checking if there are any users that have been deleted from Canvas.
        # This is 1 DB call per user so doesn't really need optimization.
        for db_user in db_users:
            pid = await self.canvas_service.get_pid_from_onyen(db_user.onyen)
            if pid not in canvas_user_pids:
                pairs.append(DatabaseLMSResourcePair(db_resource=db_user, lms_resource=None))
        
        # Then we process Canvas users
        pairs += await asyncio.gather(*[process_canvas_user(u) for u in canvas_users])

        return [p for p in pairs if p is not None]
    
    async def _pair_db_canvas_assignments(self, db_assignments: list[AssignmentModel], canvas_assignments: list[dict]):
        pairs = []

        canvas_assignment_ids = [a["id"] for a in canvas_assignments]
        for db_assignment in db_assignments:
            if db_assignment.id not in canvas_assignment_ids:
                pairs.append(DatabaseLMSResourcePair(db_resource=db_assignment, lms_resource=None))

        for canvas_assignment in canvas_assignments:
            try:
                db_assignment = await self.assignment_service.get_assignment_by_id(canvas_assignment["id"])
                pairs.append(DatabaseLMSResourcePair(db_resource=db_assignment, lms_resource=canvas_assignment))

            except AssignmentNotFoundException as e:
                pairs.append(DatabaseLMSResourcePair(db_resource=None, lms_resource=canvas_assignment))

        return pairs
    
    async def sync_student(
        self,
        resource_pair: DatabaseLMSResourcePair
    ):
        db_student, canvas_student = resource_pair.db_resource, resource_pair.lms_resource

        if db_student is None and canvas_student is not None:
            # create
            print("creating student", canvas_student["name"])
            await self.student_service.create_student(
                onyen=resource_pair.user_info.onyen,
                name=canvas_student["name"],
                email=canvas_student["email"]
            )
            await self.canvas_service.associate_pid_to_user(resource_pair.user_info.onyen, resource_pair.user_info.pid)

        if db_student is not None and canvas_student is not None:
            # update
            print("updating student", canvas_student["name"])
            pass

        if db_student is not None and canvas_student is None:
            # delete
            print("deleting student", canvas_student["name"])
            await self.student_service.delete_user(db_student)
            
    async def sync_students_conc(self):
        db_students = await self.student_service.list_students()
        canvas_students = await self.canvas_service.get_students()

        # If this course runs on a 2U Digital Campus instance, remove ":UNC" from the PID
        for student in canvas_students:
            sis_user_id = student.get("sis_user_id")
            if sis_user_id and ':' in sis_user_id:
                student["sis_user_id"] = sis_user_id.split(':')[0]

        canvas_student_pids = [s["sis_user_id"] for s in canvas_students]
        
        pairs = await self._pair_db_canvas_users(db_students, canvas_students, canvas_student_pids)
        await asyncio.gather(*[
            self.sync_student(pair)
            for pair in pairs
        ])

    async def sync_instructor(
        self,
        resource_pair: DatabaseLMSResourcePair
    ):
        db_instructor, canvas_instructor = resource_pair.db_resource, resource_pair.lms_resource

        if db_instructor is None and canvas_instructor is not None:
            # create
            print("creating instructor", canvas_instructor["name"])
            await self.instructor_service.create_instructor(
                onyen=resource_pair.user_info.onyen,
                name=canvas_instructor["name"],
                email=canvas_instructor["email"]
            )
            await self.canvas_service.associate_pid_to_user(resource_pair.user_info.onyen, resource_pair.user_info.pid)

        if db_instructor is not None and canvas_instructor is not None:
            # update
            print("updating instructor", canvas_instructor["name"])
            pass

        if db_instructor is not None and canvas_instructor is None:
            # delete
            print("deleting instructor", canvas_instructor["name"])
            await self.instructor_service.delete_user(db_instructor)

    async def sync_instructors_conc(self):
        db_instructors = await self.instructor_service.list_instructors()
        canvas_instructors = await self.canvas_service.get_instructors()

        # If this course runs on a 2U Digital Campus instance, remove ":UNC" from the PID
        for instructor in canvas_instructors:
            sis_user_id = instructor.get("sis_user_id")
            if sis_user_id and ':' in sis_user_id:
                instructor["sis_user_id"] = sis_user_id.split(':')[0]

        canvas_instructor_pids = [i["sis_user_id"] for i in canvas_instructors]
        
        pairs = await self._pair_db_canvas_users(db_instructors, canvas_instructors, canvas_instructor_pids)
        await asyncio.gather(*[
            self.sync_instructor(pair)
            for pair in pairs
        ])


    async def sync_assignment(self, resource_pair: DatabaseLMSResourcePair):
        db_assignment, canvas_assignment = resource_pair.db_resource, resource_pair.lms_resource
        
        # Canvas uses -1 for unlimited attempts.
        max_attempts = canvas_assignment.get("allowed_attempts") if canvas_assignment.get("allowed_attempts", -1) >= 0 else None
            
        if db_assignment is None and canvas_assignment is not None:
            # create
            print("creating assignment", canvas_assignment["name"])
            await self.assignment_service.create_assignment(
                id=canvas_assignment["id"],
                name=canvas_assignment["name"], 
                due_date=canvas_assignment["due_at"], 
                available_date=canvas_assignment["unlock_at"],
                directory_path=canvas_assignment["name"],
                is_published=canvas_assignment["published"],
                max_attempts=max_attempts
            )

        if db_assignment is not None and canvas_assignment is not None:
            # update
            print("updating assignment", canvas_assignment["name"])
            await self.assignment_service.update_assignment(db_assignment, UpdateAssignmentSchema(
                name=canvas_assignment["name"],
                available_date=canvas_assignment["unlock_at"],
                due_date=canvas_assignment["due_at"],
                max_attempts=max_attempts
            ))
        
        if db_assignment is not None and canvas_assignment is None:
            # delete
            print("deleting assignment", canvas_assignment["name"])
            await self.assignment_service.delete_assignment(db_assignment)
    
    async def sync_assignments_conc(self):
        db_assignments = await self.assignment_service.get_assignments()
        canvas_assignments = await self.canvas_service.get_assignments()

        pairs = await self._pair_db_canvas_assignments(db_assignments, canvas_assignments)
        await asyncio.gather(*[
            self.sync_assignment(pair)
            for pair in pairs
        ])

    async def sync_students(self):
        db_students = await self.student_service.list_students()
        canvas_students = await self.canvas_service.get_students()

        # If this course runs on a 2U Digital Campus instance, remove ":UNC" from the PID
        for student in canvas_students:
            sis_user_id = student.get("sis_user_id")
            if sis_user_id and ':' in sis_user_id:
                student["sis_user_id"] = sis_user_id.split(':')[0]

        canvas_student_pids = [s["sis_user_id"] for s in canvas_students]
        
        # Delete students that are in the database but not in Canvas
        for student in db_students:
            print("getting student pid", student.onyen)
            student_pid = await self.canvas_service.get_pid_from_onyen(student.onyen)
            print("student pid is", student_pid)
            if student_pid not in canvas_student_pids:
                await self.student_service.delete_user(student)
       
        for student in canvas_students:
            pid, email, name = student.get("sis_user_id"), student.get("email"), student.get("name")
            if pid is None or email is None or name is None:
                print("Skipping over pending student", name or "<unknown>")
                continue

            try:
                print("getting user info for ", pid)
                user_info = self.ldap_service.get_user_info(pid)
                print(pid, "->", user_info.onyen)
            except UserNotFoundException:
                print("Skipping over student not in LDAP: ", pid or "<unknown>")
                continue

            try:
                await self.student_service.get_user_by_onyen(user_info.onyen)
            except UserNotFoundException:
                #create a new student
                print("student doesn't exist", user_info.onyen)
                await self.student_service.create_student(
                    onyen=user_info.onyen,
                    name=name,
                    email=email
                )
                print("associate pid", pid, "to onyen", user_info.onyen)
                await self.canvas_service.associate_pid_to_user(user_info.onyen, pid)

        return canvas_students
    
    async def sync_instructors(self):
        db_instructors = await self.instructor_service.list_instructors()
        canvas_instructors = await self.canvas_service.get_instructors()

        # If this course runs on a 2U Digital Campus instance, remove ":UNC" from the PID
        for instructor in canvas_instructors:
            sis_user_id = instructor.get("sis_user_id")
            if sis_user_id and ':' in sis_user_id:
                instructor["sis_user_id"] = sis_user_id.split(':')[0]

        canvas_instructor_pids = [i["sis_user_id"] for i in canvas_instructors]
       
        # Delete instructors that are in the database but not in Canvas
        for instructor in db_instructors:
            print("getting instructor pid", instructor.onyen)
            instructor_pid = await self.canvas_service.get_pid_from_onyen(instructor.onyen)
            print("instructor pid is", instructor_pid)
            if instructor_pid not in canvas_instructor_pids:
                await self.instructor_service.delete_user(instructor)
        
        for instructor in canvas_instructors:
            pid, email, name = instructor.get("sis_user_id"), instructor.get("email"), instructor.get("name")
            if pid is None or email is None or name is None:
                print("Skipping over pending instructor", name or "<unknown>")
                continue

            print("getting user info for ", pid)
            user_info = self.ldap_service.get_user_info(pid)
            print(pid, "->", user_info.onyen)

            try:
                await self.instructor_service.get_user_by_onyen(user_info.onyen)

            except UserNotFoundException:
                #create a new instructor
                print("instructor doesn't exit", user_info.onyen)
                await self.instructor_service.create_instructor(
                    onyen=user_info.onyen,
                    name=name,
                    email=email
                )
                print("associate pid", pid, "to onyen", user_info.onyen)
                await self.canvas_service.associate_pid_to_user(user_info.onyen, pid)

        return canvas_instructors

    async def upsync_grade(
        self,
        submission: SubmissionModel,
        grade_percent: float,
        student_notebook: BinaryIO,
        comments: str | None = None,
    ):
        user_pid = await self.canvas_service.get_pid_from_onyen(submission.student.onyen)
        
        # If this course runs on a 2U Digital Campus instance, append ":UNC" to the PID
        if "digitalcampus" in settings.CANVAS_API_URL:
            user_pid += ":UNC"

        student = await self.canvas_service.get_student_by_pid(user_pid)
        await self.canvas_service.upload_grade(
            assignment_id=submission.assignment.id,
            user_id=student["id"],
            grade_percent=grade_percent,
            student_notebook=student_notebook,
            comments=comments
        )
            
    async def upsync_assignment(
        self,
        assignment: AssignmentModel
    ):
        await self.canvas_service.update_assignment(assignment.id, UpdateCanvasAssignmentBody(
            name=assignment.name,
            available_date=assignment.available_date,
            due_date=assignment.due_date,
            is_published=assignment.is_published,
            max_attempts=assignment.max_attempts
        ))
        

    async def downsync(self):
        print("Syncing the LMS with the database")
        await self.sync_course()
        await self.sync_assignments_conc()
        await asyncio.gather(self.sync_students_conc(), self.sync_instructors_conc())
        print("Syncing complete")