from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AssignmentModel, SubmissionModel, StudentModel, ExtraTimeModel
from app.schemas import StudentAssignmentSchema, SubmissionSchema
from app.api.deps import get_db

router = APIRouter()

@router.get("/assignments", response_model=List[StudentAssignmentSchema])
def get_student_assignments(
    *,
    db: Session = Depends(get_db),
    onyen: str
):
    assignments = db.query(AssignmentModel).all()
    # Go through and add extra time to any assignments, if alloted.
    for assignment in assignments:
        assignment.adjusted_available_date = assignment.get_adjusted_available_date(db, onyen)
        assignment.adjusted_due_date = assignment.get_adjusted_due_date(db, onyen)
        assignment.is_deferred = assignment.adjusted_available_date != assignment.available_date
        assignment.is_extended = assignment.adjusted_due_date != assignment.due_date
        assignment.is_released = assignment.get_is_released()
        assignment.is_available = assignment.get_is_available_for_student(db, onyen)
        assignment.is_closed = assignment.get_is_closed_for_student(db, onyen)

    return assignments

@router.get("/assignment/{assignment_id}/submissions", response_model=List[SubmissionSchema])
def get_assignment_submissions(
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