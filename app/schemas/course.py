from datetime import datetime
from pydantic import BaseModel

class CourseSchema(BaseModel):
    id: int
    name: str
    master_remote_url: str

    class Config:
        orm_mode = True