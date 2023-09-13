from pydantic import BaseModel
from app.models.user import UserType
from .user_role import UserRoleSchema

class UserSchema(BaseModel):
    id: int
    user_type: UserType
    onyen: str
    first_name: str
    last_name: str
    email: str
    # role: UserRoleSchema

    class Config:
        orm_mode = True