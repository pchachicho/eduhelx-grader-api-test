from pydantic import BaseModel
from datetime import datetime
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.models import AssignmentModel, StudentModel, InstructorModel
from app.schemas import InstructorAssignmentSchema, StudentAssignmentSchema, AssignmentSchema, UpdateAssignmentSchema
from app.schemas._unset import UNSET
from app.services import (
    AssignmentService, InstructorAssignmentService, StudentAssignmentService,
    StudentService, UserService, LmsSyncService
)
from app.core.dependencies import get_db, PermissionDependency, RequireLoginPermission, AssignmentModifyPermission

router = APIRouter()

# Note: we don't want to reuse UpdateAssignmentSchema here because it is
# intended for internal use only, and may have private values in the future.
class UpdateAssignmentBody(BaseModel):
    new_name: str | None = UNSET
    directory_path: str | None = UNSET
    available_date: datetime | None
    due_date: datetime | None

@router.patch("/assignments/{assignment_name}", response_model=AssignmentSchema)
async def update_assignment_fields(
    *,
    db: Session = Depends(get_db),
    assignment_name: str,
    assignment_body: UpdateAssignmentBody,
    perm: None = Depends(PermissionDependency(AssignmentModifyPermission))
):
    # Assumption is that the Name is unique
    assignment = await AssignmentService(db).get_assignment_by_name(assignment_name)

    # Differentiate between fields that are set as None and fields that are not set at all
    updated_set_fields = assignment_body.dict(exclude_unset=True)
    update_schema = UpdateAssignmentSchema(**updated_set_fields)
    assignment = await AssignmentService(db).update_assignment(assignment, update_schema)

    await LmsSyncService(db).upsync_assignment(assignment)

    return assignment

@router.get(
    "/assignments/self",
    response_model=List[Union[StudentAssignmentSchema, InstructorAssignmentSchema, AssignmentSchema]]
)
async def get_assignments(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(RequireLoginPermission))
):
    onyen = request.user.onyen

    user = await UserService(db).get_user_by_onyen(onyen)
    assignments = await AssignmentService(db).get_assignments()

    if isinstance(user, InstructorModel):
        return [
            await InstructorAssignmentService(db, user, assignment).get_instructor_assignment_schema()
            for assignment in assignments
        ]
    elif isinstance(user, StudentModel):   
        return [
            await StudentAssignmentService(db, user, assignment).get_student_assignment_schema()
            for assignment in assignments
        ]
    else:
        return assignments