from sqlalchemy import (
    Column, Sequence, ForeignKey,
    Integer, Interval, DateTime,
    func
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class ExtraTimeModel(Base):
    __tablename__ = "extra_time"

    id = Column(Integer, Sequence("extra_time_id_seq"), primary_key=True, autoincrement=True, index=True)
    time = Column(Interval, nullable=False)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)

    student = relationship("StudentModel", foreign_keys="ExtraTimeModel.student_id")
    assignment = relationship("AssignmentModel", foreign_keys="ExtraTimeModel.assignment_id")

    __table_args__ = (UniqueConstraint("student_id", "assignment_id"),)