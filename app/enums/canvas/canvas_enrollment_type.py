from enum import StrEnum

class CanvasEnrollmentType(StrEnum):
    STUDENT     = 'student'
    TEACHER     = 'teacher'
    TA          = 'ta'
    DESIGNER    = 'designer'
    OBSERVER    = 'observer'