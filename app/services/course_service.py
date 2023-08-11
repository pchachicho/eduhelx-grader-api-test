from typing import List
from sqlalchemy.orm import Session
from app.models import CourseModel, InstructorModel
from app.schemas import CourseWithInstructorsSchema
from app.core.config import settings

class CourseService:
    def __init__(self, session: Session):
        self.session = session

    async def get_course_instructors(self) -> List[InstructorModel]:
        return self.session.query(InstructorModel).all()

    async def get_course(self) -> CourseModel:
        return self.session.query(CourseModel).first()
    
    async def get_course_with_instructors_schema(self) -> CourseWithInstructorsSchema:
        course = await self.get_course()
        course.instructors = await self.get_course_instructors()
        return CourseWithInstructorsSchema.from_orm(course)