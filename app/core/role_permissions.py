from typing import List
from enum import Enum
from sqlalchemy import Column, Sequence, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, String
from app.database import Base

class UserPermission(str, Enum):
    ASSIGNMENT__GET    = "assignment:get"
    ASSIGNMENT__CREATE = "assignment:create"
    ASSIGNMENT__MODIFY = "assignment:modify"
    ASSIGNMENT__DELETE = "assignment:delete"

    COURSE__GET    = "course:get"
    COURSE__CREATE = "course:create"
    COURSE__MODIFY = "course:modify"
    COURSE__DELETE = "course:delete"

    STUDENT__GET    = "student:get"
    STUDENT__CREATE = "student:create"
    STUDENT__MODIFY = "student:modify"
    STUDENT__DELETE = "student:delete"

    INSTRUCTOR__GET    = "instructor:get"
    INSTRUCTOR__CREATE = "instructor:create"
    INSTRUCTOR__MODIFY = "instructor:modify"
    INSTRUCTOR__DELETE = "instructor:delete"

    SUBMISSION__GET    = "submission:get"
    SUBMISSION__CREATE = "submission:create"
    SUBMISSION__MODIFY = "submission:modify"
    SUBMISSION__DELETE = "submission:delete"

class UserRole:
    Roles = []
    def __init__(self, name: str, permissions: List[UserPermission]):
        self.name = name
        self.permissions = permissions

        if not any([i.name == name for i in UserRole.Roles]):
            UserRole.Roles.append(self)
        else:
            raise ValueError(f"User role { name } already exists")

class UserRoleType(TypeDecorator):
    impl = String(64)
    
    def process_bind_param(self, value, dialect) -> str | None:
        if value is not None:
            return value.name
        return None

    def process_result_value(self, value, dialect) -> UserRole | None:
        if value is not None:
            for role in UserRole.Roles:
                if role.name == value: return role
        return None

admin_role = UserRole("admin", [p for p in UserPermission])
instructor_role = UserRole("instructor", [
    UserPermission.ASSIGNMENT__GET,
    UserPermission.ASSIGNMENT__CREATE,
    UserPermission.ASSIGNMENT__MODIFY,
    UserPermission.ASSIGNMENT__DELETE,
    UserPermission.COURSE__GET,
    UserPermission.COURSE__CREATE,
    UserPermission.COURSE__MODIFY,
    UserPermission.STUDENT__GET,
    UserPermission.STUDENT__CREATE,
    UserPermission.STUDENT__MODIFY,
    UserPermission.INSTRUCTOR__GET,
    UserPermission.SUBMISSION__GET
])
student_role = UserRole("student", [
    UserPermission.COURSE__GET,
    UserPermission.SUBMISSION__CREATE,
    UserPermission.INSTRUCTOR__GET
])