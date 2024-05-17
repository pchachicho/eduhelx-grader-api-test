from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.services import LmsSyncService
from app.core.dependencies import (
    get_db, PermissionDependency,
    StudentListPermission, StudentCreatePermission, 
    StudentDeletePermission, StudentModifyPermission,
    AssignmentCreatePermission, AssignmentListPermission, 
    AssignmentDeletePermission, AssignmentModifyPermission
)

router = APIRouter()

@router.get("lms/downsync/{course_id}")
async def downsync(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    perm: None = Depends(PermissionDependency(
        StudentListPermission, StudentCreatePermission,
        StudentDeletePermission, StudentModifyPermission,
        AssignmentCreatePermission, AssignmentListPermission,
        AssignmentDeletePermission, AssignmentModifyPermission
    ))
):
    await LmsSyncService(course_id, db).downsync()

@router.get("lms/downsync/{course_id}/students")
async def downsync_students(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    perm: None = Depends(PermissionDependency(
        StudentListPermission, StudentCreatePermission,
        StudentDeletePermission, StudentModifyPermission
    ))
):
    await LmsSyncService(course_id, db).sync_students()

@router.get("lms/downsync/{course_id}/assignments")
async def downsync_assignments(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    perm: None = Depends(PermissionDependency(
        AssignmentCreatePermission, AssignmentListPermission,
        AssignmentDeletePermission, AssignmentModifyPermission
    ))
):
    await LmsSyncService(course_id, db).sync_assignments()
