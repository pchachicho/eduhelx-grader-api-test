from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CourseModel, InstructorModel
from app.services import CourseService
from app.schemas import CourseWithInstructorsSchema
from app.api.deps import get_db

router = APIRouter()

@router.get("/course", response_model=CourseWithInstructorsSchema)
async def get_course(
    *,
    db: Session = Depends(get_db)
):
    course_service = CourseService(db)
    course = await CourseService(db).get_course_with_instructors_schema()
    return course