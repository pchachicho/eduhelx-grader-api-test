from .base import CustomException

class NoAssignmentFetchedException(CustomException):
    code = 404
    error_code = "LMS__NO_ASSIGNMENT_FETCHED"
    message = "Failed to fetch assignment from LMS"

class NoCourseFetchedException(CustomException):
    code = 404
    error_code = "LMS__NO_COURSE_FETCHED"
    message = "Failed to fetch course from LMS"

class NoStudentsFetchedException(CustomException):
    code = 404
    error_code = "LMS__NO_STUDENTS_FETCHED"
    message = "Failed to fetch students from LMS"

class LMSUserNotFoundException(CustomException):
    code = 404
    error_code = "LMS_USER_NOT_FOUND"
    message = "User's onyen is not associated with an LMS user"

class LMSUserPIDAlreadyAssociated(CustomException):
    code = 409
    error_code = "LMS_USER_PID_ALREADY_ASSOCIATED"
    message = "LMS PID is already associated with a different Eduhelx user's onyen"