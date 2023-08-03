from datetime import datetime
from pydantic import BaseModel

class StudentSchema(BaseModel):
    id: int
    student_onyen: str
    first_name: str
    last_name: str
    join_date: datetime
    exit_date: datetime | None

    class Config:
        orm_mode = True