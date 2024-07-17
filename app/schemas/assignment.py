from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
from ._unset import UNSET

class AssignmentSchema(BaseModel):
    id: int
    name: str
    directory_path: str
    max_attempts: int | None
    created_date: datetime
    available_date: datetime | None
    due_date: datetime | None
    last_modified_date: datetime
    # Has both an available_date and due_date set
    is_created: bool

    class Config:
        orm_mode = True

class UpdateAssignmentSchema(BaseModel):
    name: str = UNSET
    directory_path: str = UNSET
    max_attempts: int | None
    available_date: datetime | None
    due_date: datetime | None

# Adds in fields relevant for JLP (tailored to the professor)
class InstructorAssignmentSchema(AssignmentSchema):
    is_available: bool
    is_closed: bool

# Adds in student-specific fields to the assignment (tailored to a particular student)
class StudentAssignmentSchema(AssignmentSchema):
    current_attempts: int
    adjusted_available_date: datetime | None
    adjusted_due_date: datetime | None
    is_available: bool
    is_closed: bool
    # Release date is deferred to a later date for the student
    is_deferred: bool
    # Due date is extended to a later date for the student
    is_extended: bool