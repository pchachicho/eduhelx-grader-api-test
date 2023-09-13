from .base import CustomException

class AssignmentNotOpenException(CustomException):
    code = 403
    error_code = "ASSIGNMENT__NOT_OPEN"
    message = "assignment not open to student yet"

class AssignmentClosedException(CustomException):
    code = 403
    error_code = "ASSIGNMENT__CLOSED"
    message = "assignment closed for student"

class AssignmentNotCreatedException(CustomException):
    code = 403
    error_code = "ASSIGNMENT__NOT_CREATED"
    message = "assignment not created"

class AssignmentNotFoundException(CustomException):
    code = 404
    error_code = "ASSIGNMENT__NOT_FOUND"
    message = "assignment not found"