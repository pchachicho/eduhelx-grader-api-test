from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CourseModel
from app.schemas import CourseSchema
from app.api.deps import get_db

router = APIRouter()

@router.get("/course", response_model=CourseSchema)
def get_course(
    *,
    db: Session = Depends(get_db)
):
    return CourseModel.get_course(db)