from .base import CustomException

class OtterConfigViolationException(CustomException):
    code = 403
    error_code = "GRADING__OTTER_CONFIG_VIOLATION"
    message = "otterconfig is invalid or cannot be generated for assignment"