from typing import List
from app.models import StudentModel
from app.core.utils.auth_helper import PasswordHelper
from app.core.exceptions import PasswordDoesNotMatchException, NotAStudentException
from .user_service import UserService

class StudentService(UserService):
    async def create_student(
        self,
        onyen: str,
        first_name: str,
        last_name: str,
        email: str
    ):
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
