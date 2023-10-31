""" User router should contain endpoints that are able to be generalized to a user, rather than a specific account type. """

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.schemas import StudentSchema, InstructorSchema
from app.services import UserService
from app.core.dependencies import get_db

router = APIRouter()

@router.get("/user/self", response_model=StudentSchema | InstructorSchema)
async def get_own_user(
    *,
    request: Request,
    db: Session = Depends(get_db)
):
    onyen = request.user.onyen
    user = await UserService(db).get_user_by_onyen(onyen)
    return user