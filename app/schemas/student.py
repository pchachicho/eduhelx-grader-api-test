from datetime import datetime
from pydantic import BaseModel

class StudentSchema(BaseModel):
    id: int
    student_onyen: str
    first_name: str
    last_name: str
    professor_onyen: str
    join_date: str
    exit_date: str | None

    class Config:
        orm_mode = True