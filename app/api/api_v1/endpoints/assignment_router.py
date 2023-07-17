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
        assignment.extra_time = assignment.get_extra_time(db, onyen)
        assignment.is_released = assignment.get_is_released(db)
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