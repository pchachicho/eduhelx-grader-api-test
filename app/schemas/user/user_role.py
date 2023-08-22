from typing import List
from collections.abc import Iterable
from pydantic import BaseModel, validator
from .user_permission import UserPermissionSchema

class UserRoleSchema(BaseModel):
    id: int
    name: str
    permissions: List[UserPermissionSchema]

    class Config:
        orm_mode = True

    # `permissions` in the UserRoleModel is actually an AssociationList (association proxy)
    # but for some reason an AssociationList is an Iterable, but not a List, so we need to convert it.
    @validator("permissions", pre=True)
    def permissions_to_list(cls, v: Iterable[UserPermissionSchema]):
        return list(v)