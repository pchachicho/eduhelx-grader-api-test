from sqlalchemy import Column, Sequence, Integer, Text
from .base import UserModel

class InstructorModel(UserModel):
    __tablename__ = "instructor"
    
    __mapper_args__ = {"polymorphic_identity": "instructor"}