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

        instructor = InstructorModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role_name="instructor"
        )
        self.session.add(instructor)
        self.session.commit()

        instructor_org_name = await CourseService(self.session).get_instructor_gitea_organization_name()
        await GiteaService().add_user_to_organization(instructor_org_name, onyen)
        await super().create_user_auto_password_auth(onyen)

    async def get_user_by_onyen(self, onyen: str) -> InstructorModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, InstructorModel):
            raise NotAnInstructorException()
        return user