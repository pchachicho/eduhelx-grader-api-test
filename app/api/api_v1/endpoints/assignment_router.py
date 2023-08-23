from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import SubmissionModel, StudentModel, ExtraTimeModel
from app.schemas import StudentAssignmentSchema, AssignmentSchema, SubmissionSchema
from app.services import AssignmentService, StudentAssignmentService, StudentService, SubmissionService
from app.core.dependencies import get_db, PermissionDependency, AssignmentListPermission

router = APIRouter()

@router.get(
    "/assignments",
    # If the user is a student, student assignments are returned.
    response_model=List[StudentAssignmentSchema] | List[AssignmentSchema]
)
async def get_assignments(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(AssignmentListPermission)),
    onyen: str
):
    student = await StudentService(db).get_user_by_onyen(onyen)
    assignments = await AssignmentService(db).get_assignments()

    # Go through and add student-specific info to the assignment.
    student_assignments = []
    for assignment in assignments:
        student_assignment = await StudentAssignmentService(db, student, assignment).get_student_assignment_schema()
        student_assignments.append(student_assignment)
        

    return assignments