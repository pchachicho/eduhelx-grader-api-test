from typing import List
from app.models import StudentModel
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
        first_name: str,
        last_name: str,
        email: str
    ) -> StudentModel:
        from app.services import GiteaService, CourseService

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
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=student_role
        )
        self.session.add(student)
        self.session.commit()

        password = await super().create_user_auto_password_auth(onyen)

        gitea_service = GiteaService()
        course_service = CourseService(self.session)

        master_repo_name = await course_service.get_master_repository_name()
        instructor_organization = await course_service.get_instructor_gitea_organization_name()
        
        await gitea_service.create_user(onyen, email, password)
        student.fork_remote_url = await gitea_service.fork_repository(
            name=master_repo_name,
            owner=instructor_organization,
            new_owner=onyen
        )
        self.session.commit()


    async def get_user_by_onyen(self, onyen: str) -> StudentModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, StudentModel):
            raise NotAStudentException()
        return user