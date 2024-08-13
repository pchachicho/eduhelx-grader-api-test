from enum import StrEnum
from datetime import datetime, timedelta

from app.schemas.assignment import InstructorAssignmentSchema, StudentAssignmentSchema
from app.schemas.course import CourseSchema
from app.schemas.extra_time import ExtraTimeSchema

class AssignmentStatus(StrEnum):
    UNPUBLISHED = 'UNPUBLISHED'
    UPCOMING    = 'UPCOMING'
    OPEN        = 'OPEN'
    CLOSED      = 'CLOSED'

    # def __call__(self, *args, **kwargs):
    #     return self.value(*args, **kwargs)
        
    @classmethod
    def get_value_for(cls,
                      assignment: StudentAssignmentSchema | InstructorAssignmentSchema,
                      course: CourseSchema,
                      currentDateTime: datetime,
                      extra_time: ExtraTimeSchema | None = None,
                      base_extra_time: timedelta | None = None
    ):
        if not assignment.is_published: return cls.UNPUBLISHED

        assignmentOpenDate: datetime = None
        if extra_time is not None: 
            assignmentOpenDate = extra_time.deferred_date
        elif assignment.available_date is None: 
            assignmentOpenDate = course.start_at 
        else: 
            assignmentOpenDate = assignment.available_date

        if assignmentOpenDate > currentDateTime: return cls.UPCOMING

        # assignmentCloseDate: datetime = None
        # if assignment.due_date is None: 
        #     assignmentCloseDate = course.start_at 
        # elif extra_time is not None: 
        #     assignmentCloseDate = assignment.due_date + extra_time.extra_time
        # else: 
        #     assignmentCloseDate = assignment.due_date

        assignmentDueDate = assignment.due_date if assignment.due_date is not None else course.start_at 

        if extra_time is not None:
            deferred_time = extra_time.deferred_time
            extra_time = extra_time.extra_time
        else:
            deferred_time = timedelta(0)
            extra_time = timedelta(0)

        return assignmentDueDate + deferred_time + extra_time + self.student_model.base_extra_time

        return cls.OPEN if assignmentCloseDate > currentDateTime else cls.CLOSED