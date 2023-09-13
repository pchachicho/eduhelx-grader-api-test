from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models import AssignmentModel
from app.schemas import StudentAssignmentSchema, AssignmentSchema
from app.services import AssignmentService, StudentAssignmentService, StudentService
from app.core.dependencies import get_db, PermissionDependency, UserIsStudentPermission

router = APIRouter()

class UpdateAssignmentBody(BaseModel):
    new_name: str | None
    directory_path: str | None
    available_date: datetime | None
    due_date: datetime | None

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

@router.patch("/assignment/{assignment_name}", response_model=AssignmentSchema)
def update_assignment_fields(
    *,
    db: Session = Depends(get_db),
    assignment_name: str,
    assignment_body: UpdateAssignmentBody
):
    # Assumption is that the Name is unique
    assignment = db.query(AssignmentModel).filter_by(name=assignment_name).first()
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment does not exist")

    # Differentiate between fields that are set as None and fields that are not set at all
    updated_set_fields = assignment_body.dict(exclude_unset=True)

    if updated_set_fields.new_name is not None:
        assignment.name = updated_set_fields.new_name
    if updated_set_fields.directory_path is not None:
        assignment.directory_path = updated_set_fields.directory_path

    assignment.available_date = updated_set_fields.available_date
    assignment.due_date = updated_set_fields.due_date

    assignment.last_modified_date = datetime.now()
    db.commit()

    return assignment
