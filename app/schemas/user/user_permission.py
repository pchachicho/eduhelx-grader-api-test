from pydantic import BaseModel

class UserPermissionSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True