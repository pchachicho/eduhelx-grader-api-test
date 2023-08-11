from typing import List
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import AssignmentModel, StudentModel, ExtraTimeModel
from app.core.config import settings
from app.core.utils.token_helper import TokenHelper
from app.core.exceptions import (
    AssignmentNotFoundException,
    AssignmentNotCreatedException,
    AssignmentNotOpenException,
    AssignmentClosedException,
)

class AssignmentService:
    def __init__(self, session: Session):
        self.session = session

    async def get_assignment_by_id(self, id: int) -> AssignmentModel:
        assignment = self.session.query(AssignmentModel).first()
        if assignment is None:
            raise AssignmentNotFoundException()
        return assignment

    async def get_assignments(self) -> List[AssignmentModel]:
        return self.session.query(AssignmentModel) \
            .all()

        

class StudentAssignmentService(AssignmentService):
    def __init__(self, session: Session, student: StudentModel, assignment: AssignmentModel):
        super().__init__(session)
        self.student = student
        self.assignment = assignment
        self.extra_time_model = self._get_extra_time_model()

    def _get_extra_time_model(self) -> ExtraTimeModel | None:
        extra_time_model = self.session.query(ExtraTimeModel) \
            .filter(
                (ExtraTimeModel.assignment_id == self.assignment.id) &
                (ExtraTimeModel.student_id == self.student.id)
            ) \
            .first()
        return extra_time_model

    # The release date for a specific student, considering extra_time
    def get_adjusted_available_date(self) -> datetime:
        if self.assignment.available_date is None: return None

        deferred_time = self.extra_time_model.deferred_time if self.extra_time_model is not None else timedelta(0)
        
        return self.assignment.available_date + deferred_time

    # The due date for a specific student, considering extra_time
    def get_adjusted_due_date(self) -> datetime:
        if self.assignment.due_date is None: return None

        # If a student does not have any extra time allotted for the assignment,
        # allocate them a timedelta of 0.
        if self.extra_time_model is not None:
            deferred_time = self.extra_time_model.deferred_time
            extra_time = self.extra_time_model.extra_time
        else:
            deferred_time = timedelta(0)
            extra_time = timedelta(0)

        return self.assignment.due_date + deferred_time + extra_time + self.student.base_extra_time

    def get_is_available(self) -> bool:
        if not self.assignment.is_created: return False

        current_timestamp = self.session.scalar(func.current_timestamp())
        return current_timestamp >= self.get_adjusted_available_date()
    
    def get_is_closed(self) -> bool:
        if not self.assignment.is_created: return False

        current_timestamp = self.session.scalar(func.current_timestamp())
        return current_timestamp > self.get_adjusted_due_date()

    async def validate_student_can_submit(self):
        if not self.assignment.is_created:
            raise AssignmentNotCreatedException()
        
        if not self.get_is_available():
            raise AssignmentNotOpenException()

        if self.get_is_closed():
            raise AssignmentClosedException()