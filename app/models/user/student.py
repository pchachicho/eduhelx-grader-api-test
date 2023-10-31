from sqlalchemy import Column, Integer, Interval, DateTime, ForeignKey, func
from .user import UserModel, UserType

class StudentModel(UserModel):
    __tablename__ = "student"
    __mapper_args__ = {"polymorphic_identity": UserType.STUDENT}
    id = Column(Integer, ForeignKey("user_account.id"), primary_key=True)

    base_extra_time = Column(Interval, server_default="0")
    join_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    exit_date = Column(DateTime(timezone=True))
    