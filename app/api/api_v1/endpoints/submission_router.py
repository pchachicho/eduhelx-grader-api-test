from typing import Dict, List, Optional
from io import BytesIO
from pydantic import BaseModel
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.schemas import SubmissionSchema
from app.services import SubmissionService, StudentService, AssignmentService, GiteaService, CourseService
from app.core.dependencies import get_db, PermissionDependency, UserIsStudentPermission, SubmissionCreatePermission, SubmissionListPermission, SubmissionDownloadPermission

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
    student_onyen: Optional[str] = Query(default=None, description="Student's onyen. Lists all students if omitted.")
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

@router.get("/submissions/download", response_class=FileResponse)
async def download_submission(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(SubmissionListPermission, SubmissionDownloadPermission)),
    submission_id: Optional[int] = Query(default=None, description="Submission ID. Downloads the latest submission if omitted")
):
    gitea_service = GiteaService()
    course_service = CourseService(db)

    course = await course_service.get_course()
    submission = await SubmissionService(db).get_submission_by_id(submission_id)
    student = submission.student
    student_repo_name = await gitea_service.compute_student_repository_name(course.name, student.onyen)

    archive_name = f"assn{ submission.assignment_id }-{ student.onyen }-subm{ submission.id }.zip"
    archive_bytes = await gitea_service.download_repository(student_repo_name, student.onyen, submission.commit_id)
    archive_stream = BytesIO(archive_bytes)
    return StreamingResponse(
        archive_stream,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{archive_name}"'}
    )

@router.get("/submissions/download/active", response_class=FileResponse)
async def download_active_submission(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(SubmissionListPermission, SubmissionDownloadPermission)),
    submission_id: Optional[int] = Query(default=None, description="Submission ID. Downloads the latest submission if omitted")
):
    # We need to define what an active submission is (HLXK-189)
    from app.core.exceptions import CustomException
    raise CustomException("Not implemented")