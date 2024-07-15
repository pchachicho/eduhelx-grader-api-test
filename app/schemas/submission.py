from datetime import datetime
from pydantic import BaseModel
from .user import StudentSchema
from .assignment import AssignmentSchema

class DatabaseSubmissionSchema(BaseModel):
    id: int
    commit_id: str
    graded: bool
    submission_time: datetime
    # student: StudentSchema
    # assignment: AssignmentSchema

    class Config:
        orm_mode = True

class SubmissionSchema(DatabaseSubmissionSchema):
    active: bool