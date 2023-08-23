from typing import List
from sqlalchemy.orm import Session
from app.models import CourseModel, InstructorModel
from app.schemas import CourseWithInstructorsSchema
from app.core.config import settings
from .user_service import InstructorService

class CourseService:
    def __init__(self, session: Session):
        self.session = session
    
    async def get_course(self) -> CourseModel:
        return self.session.query(CourseModel).first()
    
    async def get_course_with_instructors_schema(self) -> CourseWithInstructorsSchema:
        course = await self.get_course()
        course.instructors = await InstructorService(self.session).list_instructors()
        return CourseWithInstructorsSchema.from_orm(course)