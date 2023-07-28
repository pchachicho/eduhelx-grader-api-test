from datetime import timedelta
from re import L
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
    directory_path = Column(Text, nullable=False)
    created_date = Column(DateTime(timezone=True), default=func.current_timestamp())
    available_date = Column(DateTime(timezone=True))
    assignment_duration = Column(Interval)
    last_modified_date = Column(DateTime(timezone=True), default=func.current_timestamp())

    @hybrid_property
    def due_date(self):
        if self.available_date is None or self.assignment_duration is None: return None
        return self.available_date + self.assignment_duration

    def _get_extra_time_model(self, db: Session, onyen: str):
        extra_time_model = db.query(ExtraTimeModel) \
            .join(StudentModel) \
            .filter(
                (ExtraTimeModel.assignment_id == self.id) &
                (StudentModel.student_onyen == onyen)
            ) \
            .first()
        return extra_time_model

    # The release date for a specific student, considering extra_time
    def get_adjusted_available_date(self, db: Session, onyen: str):
        if self.available_date is None: return None

        extra_time_model = self._get_extra_time_model(db, onyen)
        if extra_time_model is not None:
            if extra_time_model.deferred_date is not None:
                return extra_time_model.deferred_date
        
        return self.available_date

    # The due date for a specific student, considering extra_time
    def get_adjusted_due_date(self, db: Session, onyen: str):
        if self.due_date is None: return None

        extra_time_model = self._get_extra_time_model(db, onyen)
        # If a student does not have any extra time allotted for the assignment,
        # allocate them a timedelta of 0.
        extra_time = extra_time_model.extra_time if extra_time_model is not None else timedelta(0)

        return self.due_date + extra_time
    
    def get_is_released(self):
        return self.available_date is not None and self.assignment_duration is not None

    def get_is_available_for_student(self, db: Session, onyen: str) -> bool:
        if not self.get_is_released(): return False

        current_timestamp = db.scalar(func.current_timestamp())
        return current_timestamp >= self.get_adjusted_available_date(db, onyen)

    def get_is_closed_for_student(self, db: Session, onyen: str) -> bool:
        if not self.get_is_released(): return False

        current_timestamp = db.scalar(func.current_timestamp())
        return current_timestamp > self.get_adjusted_due_date(db, onyen)