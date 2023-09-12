from pydantic import BaseModel
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AssignmentModel, SubmissionModel, StudentModel, ExtraTimeModel
from app.schemas import StudentAssignmentSchema, SubmissionSchema, AssignmentSchema
from app.api.deps import get_db


router = APIRouter()

class UpdateAssignmentBody(BaseModel):
    new_name: str | None
    directory_path: str | None
    available_date: datetime | None
    due_date: datetime | None

@router.get("/assignments", response_model=List[StudentAssignmentSchema])
def get_student_assignments(
    *,
    db: Session = Depends(get_db),
    onyen: str
):
    assignments = db.query(AssignmentModel).all()
    # Go through and add extra time to any assignments, if alloted.
    for assignment in assignments:
        assignment.adjusted_available_date = assignment.get_adjusted_available_date(db, onyen)
        assignment.adjusted_due_date = assignment.get_adjusted_due_date(db, onyen)
        assignment.is_deferred = assignment.adjusted_available_date != assignment.available_date
        assignment.is_extended = assignment.adjusted_due_date != assignment.due_date
        assignment.is_created = assignment.get_is_created()
        assignment.is_available = assignment.get_is_available_for_student(db, onyen)
        assignment.is_closed = assignment.get_is_closed_for_student(db, onyen)

    return assignments

@router.get("/assignment/{assignment_id}/submissions", response_model=List[SubmissionSchema])
def get_assignment_submissions(
    *,
    db: Session = Depends(get_db),
    assignment_id: int,
    onyen: str
):
    return db.query(SubmissionModel) \
        .filter_by(assignment_id=assignment_id) \
        .join(StudentModel) \
        .filter(StudentModel.student_onyen == onyen) \
        .all()

@router.patch("/assignment/{assignment_name}", response_model=AssignmentSchema)
def update_assignment_fields(
    *,
    db: Session = Depends(get_db),
    assignment_name: str,
    assignment_body: UpdateAssignmentBody
):
    # Assumption that the Name is unique
    assignment = db.query(AssignmentModel).filter_by(name=assignment_name).first()
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment does not exist")
    
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
