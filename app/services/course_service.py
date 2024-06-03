from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from app.models import CourseModel
from app.schemas import CourseWithInstructorsSchema
from app.core.exceptions import MultipleCoursesExistException, NoCourseExistsException, CourseAlreadyExistsException

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
        from .user import InstructorService
        
        course = await self.get_course()
        course.instructors = await InstructorService(self.session).list_instructors()
        return CourseWithInstructorsSchema.from_orm(course)


    async def create_course(self, name: str, start_at: datetime = None, end_at: datetime = None) -> CourseModel:
        from app.services import GiteaService

        try:
            await self.get_course()
            raise CourseAlreadyExistsException()
        except NoCourseExistsException:
            pass

        gitea_service = GiteaService()
        master_repository_name = f"{ name }-class-master-repo"
        instructor_organization = f"{ name }-instructors"
        
        await gitea_service.create_organization(instructor_organization)
        master_remote_url = await gitea_service.create_repository(
            name=master_repository_name,
            description=f"The class master repository for { name }",
            owner=instructor_organization,
            private=False
        )

        course = CourseModel(
            name=name,
            master_remote_url=master_remote_url,
            start_at=start_at,
            end_at=end_at
        )
        
        self.session.add(course)
        self.session.commit()

        return course
    
    async def get_instructor_gitea_organization_name(self) -> str:
        course = await self.get_course()
        return f"{ course.name }-instructors"
    
    async def get_master_repository_name(self) -> str:
        course = await self.get_course()
        return f"{ course.name }-class-master-repo"
    
    async def get_main_branch_name(self) -> str:
        return "master"
    
    async def update_course_name(self, name: str) -> CourseModel:
        course = await self.get_course()
        course.name = name
        self.session.commit()
        return course
    
    async def update_course_start_at(self, start_at: datetime) -> CourseModel:
        course = await self.get_course()
        course.start_at = start_at
        self.session.commit()
        return course
    
    async def update_course_end_at(self, end_at: datetime) -> CourseModel:
        course = await self.get_course()
        course.end_at = end_at
        self.session.commit()
        return course
        