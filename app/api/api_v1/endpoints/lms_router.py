from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.services import LmsSyncService
from app.core.dependencies import (
    get_db, PermissionDependency,
    UserIsInstructorPermission
)

router = APIRouter()

@router.get("lms/downsync")
async def downsync(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    return await LmsSyncService(db).downsync()

@router.get("lms/downsync/students")
async def downsync_students(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    return await LmsSyncService(db).sync_students()

@router.get("lms/downsync/assignments")
async def downsync_assignments(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    return await LmsSyncService(db).sync_assignments()

@router.post("lms/grades")
async def post_grades(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission)),
    file: UploadFile = File(...)
):
    contents = await file.read()
    return await LmsSyncService(db).upload_grades_from_csv(contents)