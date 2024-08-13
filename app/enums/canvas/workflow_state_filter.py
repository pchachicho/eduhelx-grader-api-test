from enum import StrEnum

class WorkflowStateFilter(StrEnum):
    SUBMITTED      = 'submitted'
    UNSUBMITTED    = 'unsubmitted'
    GRADED         = 'graded'
    PENDING_REVIEW = 'pending_review'