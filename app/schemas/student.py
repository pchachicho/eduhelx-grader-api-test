from datetime import datetime
from pydantic import BaseModel

class StudentSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    professor_onyen: str

    class Config:
        orm_mode = True