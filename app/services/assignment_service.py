from sqlalchemy.orm import Session
from app.models import AssignmentModel, StudentModel
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

    async def validate_student_can_submit(self, student: StudentModel, assignment: AssignmentModel) -> bool:
        if not assignment.get_is_created():
            raise HTTPException(status_code=403, detail="Assignment has not been released")
        if not assignment.get_is_available_for_student(db, onyen):
            raise HTTPException(status_code=403, detail="Assignment has not opened yet")
        if assignment.get_is_closed_for_student(db, onyen):
            raise HTTPException(status_code=403, detail="Assignment is closed for submission")