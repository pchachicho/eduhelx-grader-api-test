from sqlalchemy import Column, Integer, ForeignKey
from .base import UserModel, UserType

class InstructorModel(UserModel):
    __tablename__ = "instructor"
    __mapper_args__ = {"polymorphic_identity": UserType.INSTRUCTOR}
    id = Column(Integer, ForeignKey("user.id"), primary_key=True)

    