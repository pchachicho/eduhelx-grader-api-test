from .base import CustomException

class LMSNoAssignmentFetchedException(CustomException):
    code = 404
    error_code = "ASSIGNMENT__NO_ASSIGNMENT_FETCHED"
    message = "Failed to fetch assignment from LMS"

class LMSNoCourseFetchedException(CustomException):
    code = 404
    error_code = "COURSE__NO_COURSE_FETCHED"
    message = "Failed to fetch course from LMS"

class LMSNoStudentsFetchedException(CustomException):
    code = 404
    error_code = "STUDENT__NO_STUDENTS_FETCHED"
    message = "Failed to fetch students from LMS"
