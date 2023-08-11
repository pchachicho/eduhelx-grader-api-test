from datetime import datetime
from .user import UserModel

class StudentSchema(UserSchema):
    join_date: datetime
    exit_date: datetime | None