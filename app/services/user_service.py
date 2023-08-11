from sqlalchemy.orm import Session
from app.models import UserModel, StudentModel, InstructorModel
from app.schemas import RefreshTokenSchema
from app.core.config import settings
from app.core.utils.token_helper import TokenHelper
from app.core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrOnyen,
    UserNotFoundException
)

class UserService:
    def __init__(self, session: Session):
        self.session = session

    async def login(self, onyen: str, password: str) -> RefreshTokenSchema:
        user = self.session.query(UserModel).filter_by(onyen=onyen, password=password).first()
        if not user:
            raise UserNotFoundException()

        response = RefreshTokenSchema(
            access_token=TokenHelper.encode(payload={"id": user.id, "onyen": user.onyen}, expire_period=settings.ACCESS_TOKEN_EXPIRES_MINUTES),
            refresh_token=TokenHelper.encode(payload={"sub": "refresh"}, expire_period=settings.REFRESH_TOKEN_EXPIRES_MINUTES)
        )
        return response

class StudentService(UserService):
    async def get_user_by_onyen(self, onyen: str) -> StudentModel:
        user = self.session.query(StudentModel).filter_by(onyen=onyen).first()
        if user is None:
            raise UserNotFoundException()
        return user

    async def create_student(
        self,
        onyen: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str
    ):
        if password != confirm_password:
            raise PasswordDoesNotMatchException()
        student = StudentModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        self.session.add(student)
        self.session.commit()

class InstructorService(UserService):
    async def get_instructor_by_onyen(self, onyen: str) -> InstructorModel:
        user = self.session.query(InstructorModel).filter_by(onyen=onyen).first()
        if user is None:
            raise UserNotFoundException()
        return user

    async def create_instructor(
        self,
        onyen: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        confirm_password: str
    ):
        if password != confirm_password:
            raise PasswordDoesNotMatchException()
        instructor = InstructorModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        self.session.add(instructor)
        self.session.commit()