from typing import List
from datetime import datetime
from pydantic import BaseModel
from .user import InstructorSchema

class CourseSchema(BaseModel):
    id: int
    name: str
    start_at: datetime | None
    end_at: datetime | None
    master_remote_url: str

    class Config:
        orm_mode = True

class CourseWithInstructorsSchema(CourseSchema):
    instructors: List[InstructorSchema]