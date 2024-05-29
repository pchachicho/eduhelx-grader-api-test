from datetime import datetime, timedelta
import json
from fastapi import Depends, HTTPException
import requests
import asyncio
from app.core.config import settings
from app.core.exceptions import NoCourseFetchedException, NoAssignmentFetchedException
from app.core.exceptions.assignment import AssignmentNotFoundException
from app.core.exceptions.course import NoCourseExistsException
from app.core.exceptions.user import UserNotFoundException
from app.services.canvas_service import CanvasService
from app.services.course_service import CourseService
from app.services.assignment_service import AssignmentService
from app.services.user.student_service import StudentService
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from app.models import CourseModel
from app.schemas import CourseWithInstructorsSchema


class LmsSyncService:
    def __init__(self, session: Session): #, session: Session):
        self.canvas_service = CanvasService(session)
        self.course_service = CourseService(session)
        self.assignment_service = AssignmentService(session)
        self.student_service = StudentService(session)
        self.session = session

    async def sync_course(self):
        try:
            canvas_course = await self.canvas_service.get_course({"include[]": "total_students"})

            # Remove this after deciding what to do about null start/end dates
            if canvas_course['start_at'] is None:
                canvas_course['start_at'] = datetime(2000, 1, 1)
            if canvas_course['end_at'] is None:
                canvas_course['end_at'] = datetime.now() + timedelta(days=365*100)

            # Check if a course already exists in the database
            if(await self.course_service.get_course()):
                #update the existing course
                return await self.course_service.update_course(
                    name=canvas_course['name'], 
                    start_at=canvas_course['start_at'], 
                    end_at=canvas_course['end_at']
                )

        except NoCourseExistsException as e:
            return await CourseService(self.session).create_course(
                id=canvas_course['id'],
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
                await self.assignment_service.delete_assignment(assignment.id)

        for assignment in canvas_assignments:
            try:
                if(await self.assignment_service.get_assignment_by_id(assignment['id'])):
                    #update the existing assignment
                    await self.assignment_service.update_assignment_name(
                        id=assignment['id'], 
                        new_name=assignment['name']
                    )

                    await self.assignment_service.update_assignment_available_date(
                        id=assignment['id'],
                        available_date=assignment['unlock_at']
                    )

                    await self.assignment_service.update_assignment_due_date(
                        id=assignment['id'],
                        due_date=assignment['due_at']
                    )

            except AssignmentNotFoundException as e:
                #create a new assignment
                await self.assignment_service.create_assignment(
                    id=assignment['id'],
                    name=assignment['name'], 
                    due_date=assignment['due_at'], 
                    available_date=assignment['unlock_at'],
                    directory_path=assignment['name']
                )
        
        return canvas_assignments

    async def sync_students(self):
        canvas_students = await self.canvas_service.get_students({
            "enrollment_type": "student"
        })
        db_students = await self.student_service.list_students()

        # Delete students that are in the database but not in Canvas
        for student in db_students:
            if student.onyen not in [s['sis_user_id'] for s in canvas_students]:
                await self.student_service.delete_student(student.onyen)

        for student in canvas_students:
            try:
                # Currently no onyen in the canvas response, 
                # we need to use sis_user_id (the PID) to get onyen from LDAP
                # For now, using sis_user_id in place of onyen
                await self.student_service.get_user_by_onyen(student['sis_user_id'])

            except UserNotFoundException:
                #create a new student
                print('foo')
                await self.student_service.create_student(
                    onyen=student['sis_user_id'],
                    name=student['name'],
                    email=student['email']
                )

        return canvas_students
    
    async def downsync(self):
        await self.sync_course()
        await self.sync_assignments()
        await self.sync_students()



if __name__ == "__main__" or True:
    # Currently only for testing purposes: a script that can be run to sync the LMS with the database
    # from app.database import SessionLocal
    from app.database import SessionLocal

    sess = SessionLocal()
    lms = LmsSyncService(sess)
    asyncio.run(lms.sync_course())
    sess.close()