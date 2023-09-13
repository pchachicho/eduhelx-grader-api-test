from .base import CustomException

class SubmissionNotFoundException(CustomException):
    code = 404
    error_code = "SUBMISSION__NOT_FOUND"
    message = "submission not found"