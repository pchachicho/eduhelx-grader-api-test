from abc import ABC, abstractmethod
from typing import List, Type

from fastapi import Request
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.base import SecurityBase

from app.services import UserService
from app.core.config import settings
from app.core.dependencies import get_db
from app.models import UserPermissionModel
from app.core.exceptions import UnauthorizedException, MissingPermissionException, UserNotFoundException


class BasePermission(ABC):
    @abstractmethod
    async def verify_permission(self, request: Request):
        pass

class BaseRolePermission(BasePermission):
    admin_role_name = "admin"
    permission_name: str

    # If no permission is specified, the permission should serve as a stand-in for login verification.
    async def only_verify_login(self) -> bool:
        return self.permission_name is None

    async def is_admin(self, user) -> bool:
        return user.role.name == self.admin_role_name

    async def verify_permission(self, request: Request):
        db = next(get_db())
        try:
            user = await UserService(db).get_user_by_onyen(request.user.onyen)
        except UserNotFoundException:
            raise UnauthorizedException()

        if await self.only_verify_login():
            return

        if await self.is_admin(user):
            return

        for permission in user.role.permissions:
            if permission.name == self.permission_name:
                return
                
        raise MissingPermissionException(self.permission_name)

# For the purposes of endpoints where no explicit permissions are required beyond having a user identity (logged in). 
class LoggedInPermission(BaseRolePermission):
    pass

class InstructorListPermission(BaseRolePermission):
    permission_name = "instructor:get"

class AssignmentListPermission(BaseRolePermission):
    permission_name = "assignment:get"


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