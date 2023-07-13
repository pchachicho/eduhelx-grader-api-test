from datetime import datetime
from pydantic import BaseModel

class AssignmentSchema(BaseModel):
    id: int
    name: str
    git_remote_url: str
    revision_count: int
    created_date: datetime
    released_date: datetime | None
    last_modified_date: datetime
    due_date: datetime

    class Config:
        orm_mode = True