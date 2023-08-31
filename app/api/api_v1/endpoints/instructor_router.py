from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas import InstructorSchema
from app.models.user import UserType
from app.services import InstructorService, CourseService, KubernetesService
from app.core.utils.auth_helper import PasswordHelper
from app.core.dependencies import get_db, PermissionDependency, InstructorListPermission, InstructorCreatePermission

router = APIRouter()

class CreateInstructorWithoutPasswordBody(BaseModel):
    onyen: str
    first_name: str
    last_name: str
    email: str

@router.get("/instructor/{onyen:str}", response_model=InstructorSchema)
async def get_instructor(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(InstructorListPermission)),
    onyen: str
):
    instructor = await InstructorService(db).get_user_by_onyen(onyen)
    return instructor

@router.post("/instructor", response_model=InstructorSchema)
async def create_instructor_without_password(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(InstructorCreatePermission)),
    instructor_body: CreateInstructorWithoutPasswordBody
):
    password = PasswordHelper.generate_password(64)
    instructor = await InstructorService(db).create_instructor(
        **instructor_body.dict(),
        password=password,
        confirm_password=password
    )
    course = await CourseService(db).get_course()
    KubernetesService().create_credential_secret(
        course_name=course.name,
        onyen=instructor_body.onyen,
        password=password,
        user_type=UserType.INSTRUCTOR
    )
    return instructor