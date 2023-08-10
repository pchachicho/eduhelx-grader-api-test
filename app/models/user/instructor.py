from sqlalchemy import Column, Sequence, Integer, Text
from app.database import Base

class InstructorModel(Base):
    __tablename__ = "instructor"
    
    __mapper_args__ = {"polymorphic_identity": "instructor"}