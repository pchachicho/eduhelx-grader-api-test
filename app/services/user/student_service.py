from typing import List
from fastapi_events.dispatcher import dispatch
from app.models import StudentModel
from app.events import CreateUserCrudEvent
from app.core.role_permissions import student_role
from app.core.exceptions import NotAStudentException, UserAlreadyExistsException, UserNotFoundException
from .user_service import UserService

class StudentService(UserService):
    async def list_students(
        self,
    ) -> List[StudentModel]:
        return self.session.query(StudentModel).all()

    async def create_student(
        self,
        onyen: str,
        name: str,
        email: str
    ) -> StudentModel:
        from app.services import GiteaService, CourseService, CollaboratorPermission

        try:
            await super().get_user_by_onyen(onyen)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass
        
        try:
            await super().get_user_by_email(email)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass

        student = StudentModel(
            onyen=onyen,
            name=name,
            email=email,
            role=student_role
        )
        self.session.add(student)
        self.session.commit()

        password = await super().create_user_auto_password_auth(onyen)

        gitea_service = GiteaService(self.session)
        course_service = CourseService(self.session)

        master_repo_name = await course_service.get_master_repository_name()
        student_repo_name = await course_service.get_student_repository_name(onyen)
        instructor_organization = await course_service.get_instructor_gitea_organization_name()
        
        await gitea_service.create_user(onyen, email, password)
        await gitea_service.add_collaborator_to_repo(
            name=master_repo_name,
            owner=instructor_organization,
            collaborator_name=onyen,
            permission=CollaboratorPermission.READ
        )
        await gitea_service.fork_repository(
            name=master_repo_name,
            owner=instructor_organization,
            new_owner=onyen
        )
        # The remote is subject to change when renamed, so we don't use the remote returned by fork_repository.
        student.fork_remote_url = await gitea_service.modify_repository(
            name=master_repo_name,
            owner=onyen,
            new_name=student_repo_name
        )
        await gitea_service.set_git_hook(
            repository_name=student_repo_name,
            owner=onyen,
            hook_id="pre-receive",
            hook_content=await gitea_service.get_merge_control_hook()
        )
        self.session.commit()

        dispatch(CreateUserCrudEvent(user=student))

    async def delete_user(
        self,
        onyen: str
    ) -> None:
        from app.services import SubmissionService, AssignmentService
        from app.models import ExtraTimeModel

        submission_service = SubmissionService(self.session)
        assignment_service = AssignmentService(self.session)

        student = await self.get_user_by_onyen(onyen)
        assignments = await assignment_service.get_assignments()
        for assignment in assignments:
            submissions = await submission_service.get_submissions(student, assignment)
            for submission in submissions:
                self.session.delete(submission)
        
        extra_times = self.session.query(ExtraTimeModel).filter_by(student_id=student.id)
        for extra_time in extra_times:
            self.session.delete(extra_time)

        self.session.commit()
        
        await super().delete_user(onyen)

    async def get_user_by_onyen(self, onyen: str) -> StudentModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, StudentModel):
            raise NotAStudentException()
        return user
    
    async def set_fork_cloned(self, student: StudentModel) -> None:
        student.fork_cloned = True
        self.session.commit()

    async def get_total_students(self) -> int:
        return self.session.query(StudentModel).count()
