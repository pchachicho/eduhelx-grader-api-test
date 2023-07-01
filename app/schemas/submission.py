from datetime import datetime
from pydantic import BaseModel
from .student import Student

class Submission(BaseModel):
    id: int
    student_id: int
    commit_id: str
    submission_time: datetime

    class Config:
        orm_mode = True