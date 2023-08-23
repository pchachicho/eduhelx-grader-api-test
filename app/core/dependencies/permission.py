from abc import ABC, abstractmethod
from typing import List, Type

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase

from app.services import UserService
from app.core.config import settings
from app.core.dependencies import get_db
from app.models import UserPermissionModel
from app.core.exceptions import CustomException, UnauthorizedException, ForbiddenException, UserNotFoundException


class BasePermission(ABC):
    @abstractmethod
    async def verify_permission(self, request: Request):
        pass

class RolePermission(BasePermission):
    permission_name: str

    async def verify_permission(self, request: Request):
        db = next(get_db())
        try:
            user = await UserService(db).get_user_by_onyen(request.user.onyen)
        except UserNotFoundException:
            raise UnauthorizedException()
        permissions = user.role.permissions if user.role is not None else []
        if not any([permission.name == self.permission_name for permission in user.role.permissions]):
            raise ForbiddenException()


class InstructorListPermission(RolePermission):
    permission_name = "instructor:list"

class AssignmentListPermission(RolePermission):
    permission_name = "assignment:list"


class PermissionDependency(SecurityBase):
    def __init__(self, *permissions: List[Type[BasePermission]]):
        self.permissions = permissions
        self.model: APIKey = APIKey(**{"in": APIKeyIn.header}, name="Authorization")
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request):
        if settings.DISABLE_AUTHENTICATION:
            # If authentication is disabled, we treat the anonymous user as if they have every permission.
            return
        for permission in self.permissions:
            cls = permission()
            await cls.verify_permission(request=request)