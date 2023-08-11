from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SubmissionModel, StudentModel, ExtraTimeModel
from app.schemas import StudentAssignmentSchema, SubmissionSchema
from app.services import AssignmentService, StudentAssignmentService, StudentService, SubmissionService
from app.api.deps import get_db

router = APIRouter()

@router.get("/assignments", response_model=List[StudentAssignmentSchema])
async def get_student_assignments(
    *,
    db: Session = Depends(get_db),
    onyen: str
):
    student = await StudentService(db).get_user_by_onyen(onyen)
    assignments = await AssignmentService(db).get_assignments()

    # Go through and add student-specific info to the assignment.
    for assignment in assignments:
        assignment_service = StudentAssignmentService(db, student, assignment)

        assignment.adjusted_available_date = assignment_service.get_adjusted_available_date()
        assignment.adjusted_due_date = assignment_service.get_adjusted_due_date()
        assignment.is_available = assignment_service.get_is_available()
        assignment.is_closed = assignment_service.get_is_closed()
        assignment.is_deferred = assignment.adjusted_available_date != assignment.available_date
        assignment.is_extended = assignment.adjusted_due_date != assignment.due_date

    return assignments

@router.get("/assignment/{assignment_id}/submissions", response_model=List[SubmissionSchema])
async def get_assignment_submissions(
    *,
    db: Session = Depends(get_db),
    assignment_id: int,
    onyen: str
):
    return db.query(SubmissionModel) \
        .filter_by(assignment_id=assignment_id) \
        .join(StudentModel) \
        .filter(StudentModel.student_onyen == onyen) \
        .all()