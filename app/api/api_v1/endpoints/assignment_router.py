from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.schemas import StudentAssignmentSchema, AssignmentSchema
from app.services import AssignmentService, StudentAssignmentService, StudentService
from app.core.dependencies import get_db, PermissionDependency, UserIsStudentPermission

router = APIRouter()

@router.get(
    "/assignments/self",
    # If the user is a student, student assignments are returned.
    response_model=List[StudentAssignmentSchema] | List[AssignmentSchema]
)
async def get_assignments(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsStudentPermission))
):
    onyen = request.user.onyen

    student = await StudentService(db).get_user_by_onyen(onyen)
    assignments = await AssignmentService(db).get_assignments()

    # Go through and add student-specific info to the assignment.
    student_assignments = []
    for assignment in assignments:
        student_assignment = await StudentAssignmentService(db, student, assignment).get_student_assignment_schema()
        student_assignments.append(student_assignment)
        

    return assignments