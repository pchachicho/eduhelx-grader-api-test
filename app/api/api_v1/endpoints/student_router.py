from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas import StudentSchema
from app.services import StudentService
from app.core.dependencies import get_db, PermissionDependency, UserIsStudentPermission

router = APIRouter()

@router.get("/student/self", response_model=StudentSchema)
async def get_student(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(UserIsStudentPermission))
):
    onyen = request.user.onyen
    student = await StudentService(db).get_user_by_onyen(onyen)
    return student