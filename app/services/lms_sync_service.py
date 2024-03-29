from fastapi import HTTPException
import requests
from app.core.exceptions import NoCourseFetchedException, NoAssignmentFetchedException
from services.canvas_service import CanvasService
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from app.models import CourseModel
from app.schemas import CourseWithInstructorsSchema

class LmsSyncService:
    def __init__(self, session: Session):
        self.canvas_service = CanvasService()

    async def sync_courses(self):
        try:
            courses = await self.canvas_service.get_courses()
            # Update the database table


            return courses
        except NoCourseFetchedException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException as e:
            raise e

    async def sync_assignments(self, course_id):
        try:
            assignments = await self.canvas_service.get_assignments(course_id)
            # Update the database table
            
            return assignments
        except NoAssignmentFetchedException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException as e:
            raise e
        
    async def sync_recent_students(self, course_id):
        try:
            recent_students = await self.canvas_service.get_recent_students(course_id)
            # Update the database table

            return recent_students
        except NoCourseFetchedException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException as e:
            raise e
        
