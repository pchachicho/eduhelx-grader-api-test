from abc import ABC, abstractmethod
from typing import List, Type

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase

from app.services import UserService
from app.core.config import settings
from app.database import SessionLocal
from app.models import StudentModel, InstructorModel
from app.core.exceptions import (
    UnauthorizedException, MissingPermissionException, UserNotFoundException,
    NotAStudentException, NotAnInstructorException
)

ADMIN_ROLE_NAME = "admin"

class BasePermission(ABC):
    def __init__(self, db, user):
        self.db = db
        self.user = user

    @abstractmethod
    async def verify_permission(self, request: Request):
        pass

# For endpoints that require a user to be logged in, but nothing beyond that.
class RequireLoginPermission(BasePermission):
    async def verify_permission(self, request: Request):
        if self.user is None:
            raise UnauthorizedException()

class UserIsStudentPermission(RequireLoginPermission):
    async def verify_permission(self, request: Request):
        await super().verify_permission(request)
        
        if not isinstance(self.user, StudentModel):
            raise NotAStudentException()

class UserIsInstructorPermission(RequireLoginPermission):
    async def verify_permission(self, request: Request):
        await super().verify_permission(request)

        if not isinstance(self.user, InstructorModel):
            raise NotAnInstructorException()
        

class BaseRolePermission(RequireLoginPermission):
    permission_name: str

    async def verify_permission(self, request: Request):
        await super().verify_permission(request)

        # Always allow for admin role
        if self.user.role.name == ADMIN_ROLE_NAME:
            return

        for permission in self.user.role.permissions:
            if permission.name == self.permission_name:
                return
                
        raise MissingPermissionException(self.permission_name)


class AssignmentListPermission(BaseRolePermission):
    permission_name = "assignment:get"
class AssignmentCreatePermission(BaseRolePermission):
    permission_name = "assignment:create"
class AssignmentModifyPermission(BaseRolePermission):
    permission_name = "assignment:modify"
class AssignmentDeletePermission(BaseRolePermission):
    permission_name = "assignment:delete"

class CourseListPermission(BaseRolePermission):
    permission_name = "course:get"
class CourseCreatePermission(BaseRolePermission):
    permission_name = "course:create"
class CourseModifyPermission(BaseRolePermission):
    permission_name = "course:modify"
class CourseDeletePermission(BaseRolePermission):
    permission_name = "course:delete"

class StudentListPermission(BaseRolePermission):
    permission_name = "student:get"
class StudentCreatePermission(BaseRolePermission):
    permission_name = "student:create"
class StudentModifyPermission(BaseRolePermission):
    permission_name = "student:modify"
class StudentDeletePermission(BaseRolePermission):
    permission_name = "student:delete"

class InstructorListPermission(BaseRolePermission):
    permission_name = "instructor:get"
class InstructorCreatePermission(BaseRolePermission):
    permission_name = "instructor:create"
class InstructorModifyPermission(BaseRolePermission):
    permission_name = "instructor:modify"
class InstructorDeletePermission(BaseRolePermission):
    permission_name = "instructor:delete"

class SubmissionListPermission(BaseRolePermission):
    permission_name = "submission:get"
class SubmissionCreatePermission(BaseRolePermission):
    permission_name = "submission:create"
class SubmissionModifyPermission(BaseRolePermission):
    permission_name = "submission:modify"
class SubmissionDeletePermission(BaseRolePermission):
    permission_name = "submission:delete"


class PermissionDependency(SecurityBase):
    def __init__(self, *permissions: List[Type[BasePermission]]):
        self.permissions = permissions
        self.model: APIKey = APIKey(**{"in": APIKeyIn.header}, name="Authorization")
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request):
        if settings.DISABLE_AUTHENTICATION:
            # If authentication is disabled, we treat the anonymous user as if they have every permission.
            return

        db = SessionLocal()
        try:
            user = await UserService(db).get_user_by_onyen(request.user.onyen)
        except UserNotFoundException:
            user = None
        
        for permission in self.permissions:
            cls = permission(db, user)
            await cls.verify_permission(request=request)
        db.close()