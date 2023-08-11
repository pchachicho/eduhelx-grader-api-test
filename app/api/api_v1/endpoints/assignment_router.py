from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SubmissionModel, StudentModel, ExtraTimeModel
from app.schemas import StudentAssignmentSchema, SubmissionSchema
from app.services import AssignmentService, StudentAssignmentService, StudentService, SubmissionService
from app.core.dependencies import get_db

router = APIRouter()

@router.get("/assignments", response_model=List[StudentAssignmentSchema])
async def get_student_assignments(
    *,
    db: Session = Depends(get_db),
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