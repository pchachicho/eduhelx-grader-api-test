from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/student/{student_id}", response_model=schemas.Student)
async def get_student(
    *,
    db: Session = Depends(deps.get_db),
    student_id: str
):
    student = db.query(models.Student).filter_by(id=student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student