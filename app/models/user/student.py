from sqlalchemy import Column, Sequence, Integer, Text, Interval, DateTime, func
from app.database import Base

class StudentModel(Base):
    __tablename__ = "student"

    id = Column(Integer, Sequence("student_id_seq"), primary_key=True, autoincrement=True, index=True)

    base_extra_time = Column(Interval, server_default="0")
    join_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    exit_date = Column(DateTime(timezone=True))
    
    mapper_args = {"__polymorphic_identity": "student"}