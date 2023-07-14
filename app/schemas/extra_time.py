from datetime import timedelta
from pydantic import BaseModel
from .student import StudentSchema
from .assignment import AssignmentSchema

class ExtraTimeSchema(BaseModel):
    id: int
    time: timedelta
    student: StudentSchema
    assignment: AssignmentSchema


    class Config:
        orm_mode = True