from .base import ForbiddenException

class MissingPermissionException(ForbiddenException):
    code = 403
    error_code = "AUTH__MISSING_PERMISSION"

    def __init__(self, permission: str):
        super().__init__(
            message=f'You do not have the permission "{ permission }"'
        )