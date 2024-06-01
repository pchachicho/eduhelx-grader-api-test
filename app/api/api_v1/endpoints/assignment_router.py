from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models import AssignmentModel
from app.schemas import StudentAssignmentSchema, AssignmentSchema
from app.services import AssignmentService, StudentAssignmentService, StudentService, LmsSyncService
from app.core.dependencies import get_db, PermissionDependency, UserIsStudentPermission, UserIsInstructorPermission

router = APIRouter()

class UpdateAssignmentBody(BaseModel):
    new_name: str | None
    directory_path: str | None
    available_date: datetime | None
    due_date: datetime | None

@router.patch("/assignments/{assignment_name}", response_model=AssignmentSchema)
async def update_assignment_fields(
    *,
    db: Session = Depends(get_db),
    assignment_name: str,
    assignment_body: UpdateAssignmentBody,
    perm: None = Depends(PermissionDependency(UserIsInstructorPermission))
):
    # Assumption is that the Name is unique
    assignment = await AssignmentService(db).get_assignment_by_name(assignment_name)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment does not exist")

    # Differentiate between fields that are set as None and fields that are not set at all
    updated_set_fields = assignment_body.dict(exclude_unset=True)

    # validate the first two fields since they are non nullable in our model, the two date fields are nullable
    if "new_name" in updated_set_fields and updated_set_fields["new_name"] is not None:
        assignment = await AssignmentService(db).update_assignment_name(assignment, updated_set_fields["new_name"])
    if "directory_path" in updated_set_fields and updated_set_fields["directory_path"] is not None:
        assignment = await AssignmentService(db).update_assignment_directory_path(assignment, updated_set_fields["directory_path"])
    if "available_date" in updated_set_fields:
        assignment = await AssignmentService(db).update_assignment_available_date(assignment, updated_set_fields["available_date"])
    if "due_date" in updated_set_fields:
        assignment = await AssignmentService(db).update_assignment_due_date(assignment, updated_set_fields["due_date"])
    if "available_date" in updated_set_fields or "due_date" in updated_set_fields:
        await LmsSyncService(db).upsync_assignment(assignment)
        
    
    return assignment

@router.get(
    "/assignments/self",
    response_model=List[StudentAssignmentSchema]
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
        
    return student_assignments
