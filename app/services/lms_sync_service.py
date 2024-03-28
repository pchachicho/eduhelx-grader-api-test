from fastapi import HTTPException
import requests
from app.core.exceptions import NoCourseFetchedException, NoAssignmentFetchedException
from services.canvas_service import CanvasService

class LmsSyncService:
    def __init__(self):
        self.canvas_service = CanvasService()

    async def sync_courses(self):
        try:
            courses = await self.canvas_service.get_courses()
            # Do something with courses
            return courses
        except NoCourseFetchedException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException as e:
            raise e

    async def sync_assignments(self, course_id):
        try:
            assignments = await self.canvas_service.get_assignments(course_id)
            # Do something with assignments
            return assignments
        except NoAssignmentFetchedException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except HTTPException as e:
            raise e
        
