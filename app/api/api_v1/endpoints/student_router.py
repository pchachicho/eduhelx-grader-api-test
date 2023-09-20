from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas import StudentSchema
from app.models.user import UserType
from app.services import StudentService, CourseService, KubernetesService
from app.core.dependencies import get_db, PermissionDependency, UserIsStudentPermission, StudentListPermission, StudentCreatePermission
from app.core.utils.auth_helper import PasswordHelper

router = APIRouter()

class CreateStudentWithoutPasswordBody(BaseModel):
    onyen: str
    first_name: str
    last_name: str
    email: str

@router.get("/student/{onyen:str}", response_model=StudentSchema)
async def get_student(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(StudentListPermission)),
    onyen: str
):
    student = await StudentService(db).get_user_by_onyen(onyen)
    return student

@router.get("/students", response_model=List[StudentSchema])
async def list_students(
    *,
    request: Request,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(StudentListPermission))
):
    students = await StudentService(db).list_students()
    return students

@router.post("/student", response_model=StudentSchema)
async def create_student_with_autogen_password(
    *,
    db: Session = Depends(get_db),
    perm: None = Depends(PermissionDependency(StudentCreatePermission)),
    student_body: CreateStudentWithoutPasswordBody
):
    student = await StudentService(db).create_student(
        **student_body.dict()
    )
    return student