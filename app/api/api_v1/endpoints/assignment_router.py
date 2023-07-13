from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AssignmentModel, SubmissionModel, StudentModel
from app.schemas import AssignmentSchema, SubmissionSchema
from app.api.deps import get_db

router = APIRouter()

@router.get("/assignments", response_model=List[AssignmentSchema])
def get_assignments(
    *,
    db: Session = Depends(get_db)
):
    assignments = db.query(AssignmentModel).all()
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