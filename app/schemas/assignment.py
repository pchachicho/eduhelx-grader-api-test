from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

class AssignmentSchema(BaseModel):
    id: int
    name: str
    directory_path: str
    created_date: datetime
    released_date: datetime
    last_modified_date: datetime
    base_time: timedelta

    class Config:
        orm_mode = True

class StudentAssignmentSchema(AssignmentSchema):
    extra_time: timedelta
    is_released: bool
    is_closed: bool