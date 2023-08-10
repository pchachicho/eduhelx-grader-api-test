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
from .user import StudentModel
from .extra_time import ExtraTimeModel

class AssignmentModel(Base):
    __tablename__ = "assignment"

    id = Column(Integer, Sequence("assignment_id_seq"), primary_key=True, autoincrement=True, index=True)
    name = Column(Text, nullable=False)
    directory_path = Column(Text, nullable=False)
    created_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    available_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    last_modified_date = Column(DateTime(timezone=True), server_default=func.current_timestamp())

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
        deferred_time = extra_time_model.deferred_time if extra_time_model is not None else timedelta(0)
        
        return self.available_date + deferred_time

    # The due date for a specific student, considering extra_time
    def get_adjusted_due_date(self, db: Session, onyen: str):
        if self.due_date is None: return None

        extra_time_model = self._get_extra_time_model(db, onyen)
        # If a student does not have any extra time allotted for the assignment,
        # allocate them a timedelta of 0.
        if extra_time_model is not None:
            deferred_time = extra_time_model.deferred_time
            extra_time = extra_time_model.extra_time
        else:
            deferred_time = timedelta(0)
            extra_time = timedelta(0)

        student_base_extra_time = db.query(StudentModel.base_extra_time).filter_by(student_onyen=onyen).scalar()

        return self.due_date + deferred_time + extra_time + student_base_extra_time
    
    def get_is_created(self):
        return self.available_date is not None and self.due_date is not None

    def get_is_available_for_student(self, db: Session, onyen: str) -> bool:
        if not self.get_is_created(): return False

        current_timestamp = db.scalar(func.current_timestamp())
        return current_timestamp >= self.get_adjusted_available_date(db, onyen)

    def get_is_closed_for_student(self, db: Session, onyen: str) -> bool:
        if not self.get_is_created(): return False

        current_timestamp = db.scalar(func.current_timestamp())
        return current_timestamp > self.get_adjusted_due_date(db, onyen)