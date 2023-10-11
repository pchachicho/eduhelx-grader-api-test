from typing import List
from app.models import InstructorModel
from app.core.role_permissions import instructor_role
from app.core.utils.auth_helper import PasswordHelper
from app.core.exceptions import PasswordDoesNotMatchException, NotAnInstructorException
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
    ):
        instructor = InstructorModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=instructor_role
        )
        self.session.add(instructor)
        self.session.commit()

        await super().create_user_auto_password_auth(onyen)

    async def get_user_by_onyen(self, onyen: str) -> InstructorModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, InstructorModel):
            raise NotAnInstructorException()
        return user