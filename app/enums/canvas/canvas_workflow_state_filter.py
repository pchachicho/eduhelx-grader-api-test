from enum import StrEnum

class CanvasWorkflowStateFilter(StrEnum):
    SUBMITTED      = 'submitted'
    UNSUBMITTED    = 'unsubmitted'
    GRADED         = 'graded'
    PENDING_REVIEW = 'pending_review'