from typing import List
from sqlalchemy.orm import Session
from app.models import UserModel, StudentModel, InstructorModel, UserRoleModel
from app.schemas import RefreshTokenSchema
from app.core.config import settings
from app.core.utils.token_helper import TokenHelper
from app.core.utils.auth_helper import PasswordHelper
from app.core.middleware.authentication import CurrentUser
from app.core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrOnyen,
    UserNotFoundException,
    PasswordDoesNotMatchException,
    NotAStudentException,
    NotAnInstructorException
)

class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def get_user_by_id(self, id: int) -> UserModel:
        user = self.session.query(UserModel).filter_by(id=id).first()
        if user is None:
            raise UserNotFoundException()
        return user

    async def get_user_by_onyen(self, onyen: str) -> UserModel:
        user = self.session.query(UserModel).filter_by(onyen=onyen).first()
        if user is None:
            raise UserNotFoundException()
        return user

    async def login(self, onyen: str, password: str) -> RefreshTokenSchema:
        user = self.session.query(UserModel).filter_by(onyen=onyen).first()
        if not user:
            raise UserNotFoundException()
        if not PasswordHelper.verify_password(password, user.password):
            raise PasswordDoesNotMatchException()

        current_user = CurrentUser(id=user.id, onyen=user.onyen)

        response = RefreshTokenSchema(
            access_token=TokenHelper.encode(payload=current_user.dict(), expire_period=settings.ACCESS_TOKEN_EXPIRES_MINUTES),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh", **current_user.dict()}, expire_period=settings.REFRESH_TOKEN_EXPIRES_MINUTES)
        )
        return response

class StudentService(UserService):
    async def create_student(
        self,
        onyen: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str
    ) -> StudentModel:
        if password != confirm_password:
            raise PasswordDoesNotMatchException()
        student = StudentModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role_name="student",
            password=PasswordHelper.hash_password(password)
        )
        self.session.add(student)
        self.session.commit()

        return student

    async def get_user_by_onyen(self, onyen: str) -> StudentModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, StudentModel):
            raise NotAStudentException()
        return user

class InstructorService(UserService):
    async def list_instructors(self) -> List[InstructorModel]:
        return self.session.query(InstructorModel).all()

    async def create_instructor(
        self,
        onyen: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str
    ) -> InstructorModel:
        if password != confirm_password:
            raise PasswordDoesNotMatchException()
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

        return instructor

    async def get_user_by_onyen(self, onyen: str) -> InstructorModel:
        user = await super().get_user_by_onyen(onyen)
        if not isinstance(user, InstructorModel):
            raise NotAnInstructorException()
        return user