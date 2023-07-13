from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import StudentModel
from app.schemas import StudentSchema
from app.api.deps import get_db

router = APIRouter()

@router.get("/student", response_model=StudentSchema)
def get_submission(
    *,
    db: Session = Depends(get_db),
    onyen: str
):
    student = db.query(StudentModel).filter_by(student_onyen=onyen).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student does not exist")
    
    return student