from datetime import datetime
from pydantic import BaseModel

class InstructorSchema(BaseModel):
    id: int
    instructor_onyen: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True