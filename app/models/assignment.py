from datetime import timedelta
from sqlalchemy import (
    Column, Sequence, ForeignKey,
    Integer, Text, DateTime, Interval,
    func
)
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base
from .student import StudentModel
from .extra_time import ExtraTimeModel

class AssignmentModel(Base):
    __tablename__ = "assignment"

    id = Column(Integer, Sequence("assignment_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False)
    git_remote_url = Column(Text, nullable=False)
    revision_count = Column(Integer, default=0)
    created_date = Column(DateTime(timezone=True), default=func.current_timestamp())
    released_date = Column(DateTime(timezone=True), nullable=False)
    last_modified_date = Column(DateTime(timezone=True), default=func.current_timestamp())
    base_time = Column(Interval, nullable=False)

    def get_assignment_time(self, db: Session, onyen: str) -> timedelta:
        extra_time = self.get_extra_time(db, onyen)
        return self.base_time + extra_time

    def get_extra_time(self, db: Session, onyen: str) -> timedelta:
        extra_time = db.query(ExtraTimeModel) \
            .join(StudentModel) \
            .filter(
                (ExtraTimeModel.assignment_id == self.id) &
                (StudentModel.student_onyen == onyen)
            ) \
            .first()
        # If a student does not have any extra time allotted for the assignment,
        # allocate them a timedelta of 0.
        return extra_time.time if extra_time is not None else timedelta()

    def get_is_released(self, db: Session) -> bool:
        current_timestamp = db.scalar(func.current_timestamp())
        return current_timestamp >= self.released_date

    def get_is_closed_for_student(self, db: Session, onyen: str) -> bool:
        current_timestamp = db.scalar(func.current_timestamp())
        return current_timestamp > self.released_date + self.get_assignment_time(db, onyen)