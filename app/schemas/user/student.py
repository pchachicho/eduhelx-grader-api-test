from datetime import datetime
from .user import UserSchema

class StudentSchema(UserSchema):
    join_date: datetime
    exit_date: datetime | None