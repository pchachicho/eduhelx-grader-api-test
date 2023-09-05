from typing import List
from sqlalchemy.orm import Session
from app.models import UserModel, StudentModel, InstructorModel, UserRoleModel
from app.models.user import UserType
from app.schemas import RefreshTokenSchema
from app.services import KubernetesService
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
    NotAnInstructorException,
    UserAlreadyExistsException
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

    async def get_user_by_email(self, email: str) -> UserModel:
        user = self.session.query(UserModel).filter_by(email=email).first()
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
        email: str
    ) -> StudentModel:
        from app.services import CourseService

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
        student = StudentModel(
            onyen=onyen,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role_name="student",
            password=PasswordHelper.hash_password(password),
        )
        self.session.add(student)
        self.session.commit()

        course = await CourseService(self.session).get_course()
        KubernetesService().create_credential_secret(
            course_name=course.name,
            onyen=onyen,
            password=password,
            user_type=UserType.STUDENT
        )

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
        email: str
    ) -> InstructorModel:
        from app.services import CourseService

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