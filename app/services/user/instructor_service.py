from typing import List
from app.models import InstructorModel
from app.models.user import UserType
from app.core.utils.auth_helper import PasswordHelper
from app.core.exceptions import NotAnInstructorException, UserAlreadyExistsException, UserNotFoundException
from .user_service import UserService

class InstructorService(UserService):
    async def list_instructors(self) -> List[InstructorModel]:
        return self.session.query(InstructorModel).all()

    async def create_instructor(
        self,
        onyen: str,
        first_name: str,
        last_name: str,
        email: str
    ) -> InstructorModel:
        from app.services import CourseService, KubernetesService

        try:
            await super().get_user_by_onyen(onyen)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass
        
        try:
            await super().get_user_by_email(onyen)
            raise UserAlreadyExistsException()
        except UserNotFoundException:
            pass

        password = PasswordHelper.generate_password(64)
        instructor = InstructorModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=PasswordHelper.hash_password(password),
            role_name="instructor"
        )
        self.session.add(instructor)
        self.session.commit()

        course = await CourseService(self.session).get_course()
        KubernetesService().create_credential_secret(
            course_name=course.name,
            onyen=onyen,
            password=password,
            user_type=UserType.INSTRUCTOR
        )

        return instructor

    async def get_user_by_onyen(self, onyen: str) -> InstructorModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, InstructorModel):
            raise NotAnInstructorException()
        return user