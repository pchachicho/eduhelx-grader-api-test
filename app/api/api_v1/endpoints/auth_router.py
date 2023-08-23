from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import RefreshTokenSchema, UserRoleSchema
from app.services import UserService, JwtService
from app.core.dependencies import get_db

router = APIRouter()

class LoginBody(BaseModel):
    onyen: str
    password: str
    

@router.post("/login", response_model=RefreshTokenSchema)
async def login(
    *,
    db: Session = Depends(get_db),
    login_body: LoginBody
):
    token = await UserService(db).login(login_body.onyen, login_body.password)
    return token

@router.post("/refresh", response_model=RefreshTokenSchema)
async def refresh(
    *,
    db: Session = Depends(get_db),
    refresh_body: RefreshTokenSchema
):
    token = await JwtService().create_refresh_token(refresh_body.access_token, refresh_body.refresh_token)
    return token

@router.get("/role", response_model=UserRoleSchema)
async def get_role(
    *,
    db: Session = Depends(get_db),
    onyen: str
):
    user = await UserService(db).get_user_by_onyen(onyen)
    return user.role
    