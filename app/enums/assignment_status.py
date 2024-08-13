from enum import StrEnum

class AssignmentStatus(StrEnum):
    UNPUBLISHED = 'UNPUBLISHED'
    UPCOMING    = 'UPCOMING'
    OPEN        = 'OPEN'
    CLOSED      = 'CLOSED'