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

def validate_submission(db: Session, onyen: int, assignment_id: int):
    student = db.query(StudentModel).filter_by(student_onyen=onyen).first()
    assignment = db.query(AssignmentModel).filter_by(id=assignment_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student does not exist")
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment does not exist")
    if not assignment.get_is_released():
        raise HTTPException(status_code=423, detail="Assignment has not been released")
    if assignment.get_is_closed_for_student(db, onyen):
        raise HTTPException(status_code=423, detail="Assignment is closed for submission")
    
    return student, assignment

@router.post("/submission/", response_model=SubmissionSchema)
def create_submission(
    *,
    db: Session = Depends(get_db),
    onyen: int,
    assignment_id: int,
    commit_id: str
):
    student, assignment = validate_submission(db, onyen, assignment_id)
    submission = SubmissionModel(
        student_id=student.id,
        assignment_id=assignment.id,
        commit_id=commit_id
    )
    
    db.add(submission)
    db.commit()

    return submission

@router.get("/submission/", response_model=Page[SubmissionSchema])
def get_submission(
    *,
    db: Session = Depends(get_db),
    onyen: int,
    assignment_id: int
):
    student, assignment = validate_submission(db, onyen, assignment_id)
    submission = db.query(SubmissionModel).filter_by(student_id=student.id, assignment_id=assignment.id, submission_time=assignment.get_latest_submission_time(db, onyen)).first()
    return submission
