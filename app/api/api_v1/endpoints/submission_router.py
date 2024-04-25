from typing import Dict, List
from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas import SubmissionSchema
from app.services import SubmissionService, StudentService, AssignmentService
from app.core.dependencies import get_db, PermissionDependency, UserIsStudentPermission, SubmissionCreatePermission, SubmissionListPermission

router = APIRouter()

class SubmissionBody(BaseModel):
    assignment_id: int
    commit_id: str

@router.post("/submissions", response_model=SubmissionSchema)
async def create_submission(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsStudentPermission, SubmissionCreatePermission)),
    submission: SubmissionBody
):
    onyen = request.user.onyen
    student = await StudentService(db).get_user_by_onyen(onyen)
    assignment = await AssignmentService(db).get_assignment_by_id(submission.assignment_id)
    submission = await SubmissionService(db).create_submission(
        student,
        assignment,
        commit_id=submission.commit_id
    )

    return submission

@router.get("/submissions", response_model=List[SubmissionSchema] | Dict[str, List[SubmissionSchema]])
async def get_submissions(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(SubmissionListPermission)),
    assignment_id: int,
    student_onyen: str | None = None
):
    onyen = request.user.onyen
    assignment = await AssignmentService(db).get_assignment_by_id(assignment_id)
    if student_onyen is None:
        students = await StudentService(db).list_students()
        return { student.onyen : await SubmissionService(db).get_submissions(student, assignment) for student in students }
    else:
        student = await StudentService(db).get_user_by_onyen(student_onyen)
        return await SubmissionService(db).get_submissions(student, assignment)

@router.get("/submissions/self", response_model=List[SubmissionSchema])
async def get_own_submissions(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsStudentPermission)),
    assignment_id: int
):
    onyen = request.user.onyen
    student = await StudentService(db).get_user_by_onyen(onyen)
    assignment = await AssignmentService(db).get_assignment_by_id(assignment_id)
    submissions = await SubmissionService(db).get_submissions(student, assignment)

    return submissions

@router.get("/latest_submission/", response_model=SubmissionSchema)
async def get_latest_submission(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(SubmissionListPermission)),
    onyen: str,
    assignment_id: int
):
    student = await StudentService(db).get_user_by_onyen(onyen)
    assignment = await AssignmentService(db).get_assignment_by_id(assignment_id)
    submission = await SubmissionService(db).get_latest_submission(student, assignment)

    return submission
