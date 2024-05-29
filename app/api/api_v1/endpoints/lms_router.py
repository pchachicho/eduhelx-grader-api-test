from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.services import LmsSyncService
from app.core.dependencies import (
    get_db, PermissionDependency,
    UserIsInstructorPermission
)

router = APIRouter()

@router.get("lms/downsync/{course_id}")
async def downsync(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    await LmsSyncService(db, course_id).downsync()

@router.get("lms/downsync/{course_id}/students")
async def downsync_students(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    await LmsSyncService(db, course_id).sync_students()

@router.get("lms/downsync/{course_id}/assignments")
async def downsync_assignments(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    await LmsSyncService(db, course_id).sync_assignments()
