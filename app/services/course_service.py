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

    async def create_course(self, course_name: str) -> CourseModel:
        from app.services import GiteaService

        try:
            await self.get_course()
            raise CourseAlreadyExistsException()
        except NoCourseExistsException:
            pass

        gitea_service = GiteaService()
        master_repository_name = await self._compute_master_repository_name(course_name)
        instructor_organization_name = await self._compute_instructor_gitea_organization_name(course_name)
        
        await gitea_service.create_organization(instructor_organization_name)
        master_remote_url = await gitea_service.create_repository(
            name=master_repository_name,
            description=f"The class master repository for { course_name }",
            owner=instructor_organization_name,
            private=False
        )

        course = CourseModel(
            name=course_name,
            master_remote_url=master_remote_url
        )
        
        self.session.add(course)
        self.session.commit()

        return course

    async def get_instructor_gitea_organization_name(self) -> str:
        course = await self.get_course()
        return self._compute_instructor_gitea_organization_name(course.name)
    
    async def get_master_repository_name(self) -> str:
        course = await self.get_course()
        # No spaces allowed! (learned the hard way...)
        return self._compute_master_repository_name(course.name)
        
    async def get_student_repository_name(self, student_onyen: str) -> str:
        course = await self.get_course()
        return self._compute_student_repository_name(course.name)
    

    @staticmethod
    def _compute_instructor_gitea_organization_name(course_name: str) -> str:
        return f"{ course_name.replace(' ', '_') }-instructors"
    
    @staticmethod
    def _compute_master_repository_name(course_name: str) -> str:
        return f"{ course_name.replace(' ', '_') }-class-master-repo"
    
    @classmethod
    def _compute_student_repository_name(cls, course_name: str) -> str:
        return f"{ course_name.replace(' ', '_') }-student-repo"