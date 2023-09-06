from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from app.models import CourseModel, InstructorModel
from app.schemas import CourseWithInstructorsSchema
from app.core.config import settings
from app.core.exceptions import MultipleCoursesExistException, NoCourseExistsException

class CourseService:
    def __init__(self, session: Session):
        self.session = session
    
    async def get_course(self) -> CourseModel:
        try:
            return self.session.query(CourseModel).one()
        except MultipleResultsFound as e:
            raise MultipleCoursesExistException()
        except NoResultFound as e:
            raise NoCourseExistsException()
    
    async def get_course_with_instructors_schema(self) -> CourseWithInstructorsSchema:
        from .user_service import InstructorService
        
        course = await self.get_course()
        course.instructors = await InstructorService(self.session).list_instructors()
        return CourseWithInstructorsSchema.from_orm(course)

    async def create_course(self, name: str) -> CourseModel:
        course = CourseModel(
            name=name,
            master_remote_url=""
        )
        
        self.session.add(course)
        self.session.commit()

        return course