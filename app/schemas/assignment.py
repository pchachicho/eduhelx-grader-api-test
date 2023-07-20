from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel

class AssignmentSchema(BaseModel):
    id: int
    name: str
    directory_path: str
    created_date: datetime
    available_date: datetime | None
    due_date: datetime | None
    last_modified_date: datetime

    class Config:
        orm_mode = True

class StudentAssignmentSchema(AssignmentSchema):
    adjusted_available_date: datetime | None
    adjusted_due_date: datetime | None
    is_released: bool
    is_available: bool
    is_closed: bool
    # Release date is deferred to a later date for the student
    is_deferred: bool
    # Due date is extended to a later date for the student
    is_extended: bool