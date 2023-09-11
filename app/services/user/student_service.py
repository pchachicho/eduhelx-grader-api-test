from typing import List
from app.models import StudentModel
from app.models.user import UserType
from app.core.utils.auth_helper import PasswordHelper
from app.core.exceptions import NotAStudentException, UserAlreadyExistsException, UserNotFoundException
from .user_service import UserService

class StudentService(UserService):
    async def create_student(
        self,
        onyen: str,
        first_name: str,
        last_name: str,
        email: str
    ) -> StudentModel:
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

        student = StudentModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role_name="student"
        )
        self.session.add(student)
        self.session.commit()

        await super().create_user_auto_password_auth(onyen)

    async def get_user_by_onyen(self, onyen: str) -> StudentModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, StudentModel):
            raise NotAStudentException()
        return user