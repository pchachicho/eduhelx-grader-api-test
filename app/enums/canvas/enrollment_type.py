from enum import StrEnum

class EnrollmentType(StrEnum):
    STUDENT     = 'student'
    TEACHER     = 'teacher'
    TA          = 'ta'
    DESIGNER    = 'designer'
    OBSERVER    = 'observer'