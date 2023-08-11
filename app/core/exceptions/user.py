from .base import CustomException

class PasswordDoesNotMatchException(CustomException):
    code = 401
    error_code = "USER__PASSWORD_DOES_NOT_MATCH"
    message = "password does not match"

class DuplicateEmailOrOnyen(CustomException):
    code = 400
    error_code = "USER__DUPLICATE_EMAIL_OR_NICKNAME"
    message = "duplicate email or onyen"

class UserNotFoundException(CustomException):
    code = 404
    error_code = "USER__NOT_FOUND"
    message = "user not found"