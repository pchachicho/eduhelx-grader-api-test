from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SubmissionModel, StudentModel
from app.schemas import SubmissionSchema
from app.api.deps import get_db

router = APIRouter()

@router.get("/submissions", response_model=Page[SubmissionSchema])
def get_student_submissions(
    *,
    db: Session = Depends(get_db),
    student_id: int
):
    return paginate(db, select(SubmissionModel).filter_by(student_id=student_id).order_by(SubmissionModel.submission_time))

@router.get("/submission/{submission_id}", response_model=SubmissionSchema)
def get_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int
):
    submission = db.query(SubmissionModel).filter_by(id=submission_id).first()
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission does not exist")
    
    return submission

@router.post("/submission/", response_model=SubmissionSchema)
def create_submission(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    commit_id: str
):
    student = db.query(StudentModel).filter_by(id=student_id).first()
    if student is None:
        raise HTTPException(status_code=400, detail="Student does not exist")
    submission = SubmissionModel(student_id=student_id, commit_id=commit_id)
    
    db.add(submission)
    db.commit()

    return submission