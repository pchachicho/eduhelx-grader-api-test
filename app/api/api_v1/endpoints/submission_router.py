from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SubmissionModel, StudentModel, AssignmentModel
from app.schemas import SubmissionSchema
from app.api.deps import get_db

router = APIRouter()

class SubmissionBody(BaseModel):
    onyen: str
    assignment_id: int
    commit_id: str

def validate_submission(db: Session, onyen: int, assignment_id: int):
    student = db.query(StudentModel).filter_by(student_onyen=onyen).first()
    assignment = db.query(AssignmentModel).filter_by(id=assignment_id).first()

    # TODO: We should validate that the submitted commit id actually exists in gitea before persisting it in the database.
    # We don't want another component of EduHeLx to assume the commit we return exists and crash when it doesn't.
    # Alternatively, we could bake this logic into the endpoints to get submissions, rather than into this one.
    if student is None:
        raise HTTPException(status_code=404, detail="Student does not exist")
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment does not exist")
    if not assignment.get_is_released():
        raise HTTPException(status_code=403, detail="Assignment has not been released")
    if assignment.get_is_closed_for_student(db, onyen):
        raise HTTPException(status_code=403, detail="Assignment is closed for submission")
    
    return student, assignment

@router.post("/submission/", response_model=SubmissionSchema)
def create_submission(
    *,
    db: Session = Depends(get_db),
    submission: SubmissionBody
):
    student, assignment = validate_submission(db, submission.onyen, submission.assignment_id)

    submission = SubmissionModel(
        student_id=student.id,
        assignment_id=submission.assignment_id,
        commit_id=submission.commit_id
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
    student = db.query(StudentModel).filter_by(student_onyen=onyen).first()
    assignment = db.query(AssignmentModel).filter_by(id=assignment_id).first()
    submission_commit_id = assignment.get_latest_submission_commit(db, student.id)
    return submission_commit_id
