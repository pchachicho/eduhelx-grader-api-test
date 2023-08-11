from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import StudentModel
from app.schemas import StudentSchema
from app.services import StudentService
from app.core.dependencies import get_db

router = APIRouter()

@router.get("/students", response_model=List[StudentSchema])
async def get_students(
    *,
    db: Session = Depends(get_db)
):
    return []

@router.get("/student", response_model=StudentSchema)
async def get_student(
    *,
    db: Session = Depends(get_db),
    onyen: str
):
    student = await StudentService(db).get_user_by_onyen(onyen)
    return student