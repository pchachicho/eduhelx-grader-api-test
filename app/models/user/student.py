from sqlalchemy import Column, Sequence, Integer, Text, Interval, DateTime, func
from app.database import Base

class StudentModel(Base):
    __tablename__ = "student"

    base_extra_time = Column(Interval, server_default="0")
    join_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    exit_date = Column(DateTime(timezone=True))
    
    __mapper_args__ = {"polymorphic_identity": "student"}