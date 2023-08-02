from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SubmissionModel, StudentModel, AssignmentModel
from app.schemas import SubmissionSchema
from app.api.deps import get_db

router = APIRouter()

@router.post("/submission/", response_model=SubmissionSchema)
def create_submission(
    *,
    db: Session = Depends(get_db),
    onyen: int,
    assignment_id: int,
    commit_id: str
):
    student = db.query(StudentModel).filter_by(student_onyen=onyen).first()
    assignment = db.query(AssignmentModel).filter_by(id=assignment_id).first()
    if student is None:
        raise HTTPException(status_code=400, detail="Student does not exist")
    if assignment is None:
        raise HTTPException(status_code=400, detail="Assignment does not exist")
    if not assignment.get_is_released():
        raise HTTPException(status_code=400, detail="Assignment has not been released")
    if assignment.get_is_closed_for_student(db, onyen):
        raise HTTPException(status_code=400, detail="Assignment is closed for submission")
    submission = SubmissionModel(
        student_id=student.id,
        assignment_id=assignment_id,
        commit_id=commit_id
    )
    
    db.add(submission)
    db.commit()

    return submission