import jwt
from typing import Optional, Tuple
from pydantic import BaseModel, Field
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection
from app.core.config import settings

class CurrentUser(BaseModel, validate_assignment=True):
    onyen: str = Field(None, description="Onyen of the current user")

class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[bool, Optional[CurrentUser]]:
        current_user = CurrentUser()
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return False, current_user

        try:
            scheme, credentials = authorization.split(" ")
            if scheme.lower() != "bearer":
                return False, current_user
        except ValueError:
            return False, current_user

        if not credentials:
            return False, current_user

        try:
            payload = jwt.decode(
                credentials,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            onyen = payload.get("onyen")
        except jwt.exceptions.PyJWTError:
            return False, current_user

        current_user.onyen = onyen
        return True, current_user


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass