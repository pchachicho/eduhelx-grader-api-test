from sqlalchemy import (
    Column, Sequence, ForeignKey,
    Integer, String, DateTime,
    func
)
from sqlalchemy.orm import relationship
from app.database import Base

class SubmissionModel(Base):
    __tablename__ = "submission"

    id = Column(Integer, Sequence("submission_id_seq"), primary_key=True, autoincrement=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignment.id"), nullable=False)
    commit_id = Column(String(255), nullable=False)
    submission_time = Column(DateTime(timezone=True), default=func.current_timestamp())

    student = relationship("StudentModel", foreign_keys="SubmissionModel.student_id")
    assignment = relationship("AssignmentModel", foreign_keys="SubmissionModel.assignment_id")