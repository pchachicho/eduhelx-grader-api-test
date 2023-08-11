from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import SubmissionModel, StudentModel, AssignmentModel
from app.schemas import SubmissionSchema
from app.services import SubmissionService, StudentService, AssignmentService
from app.api.deps import get_db

router = APIRouter()

class SubmissionBody(BaseModel):
    onyen: str
    assignment_id: int
    commit_id: str

@router.post("/submission/", response_model=SubmissionSchema)
async def create_submission(
    *,
    db: Session = Depends(get_db),
    submission: SubmissionBody
):
    student = await StudentService(db).get_user_by_onyen(submission.onyen)
    assignment = await AssignmentService(db).get_assignment_by_id(submission.assignment_id)
    submission = await SubmissionService(db).create_submission(
        student,
        assignment,
        commit_id=submission.commit_id
    )

    return submission

@router.get("/submission/", response_model=str)
async def get_submission(
    *,
    db: Session = Depends(get_db),
    onyen: str,
    assignment_id: int
):
    student = await StudentService(db).get_user_by_onyen(onyen)
    assignment = await AssignmentService(db).get_assignment_by_id(assignment_id)
    submission = await SubmissionService(db).get_latest_submission(student, assignment)

    return submission.commit_id
