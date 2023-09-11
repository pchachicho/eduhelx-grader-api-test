from typing import List
from pydantic import BaseModel
from .user_permission import UserPermissionSchema

class UserRoleSchema(BaseModel):
    id: int
    name: str
    permissions: List[UserPermissionSchema]

    class Config:
        orm_mode = True
