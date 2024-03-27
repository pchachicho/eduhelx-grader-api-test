from .user import StudentSchema, InstructorSchema, UserRoleSchema, UserPermissionSchema
from .submission import SubmissionSchema
from .assignment import AssignmentSchema, InstructorAssignmentSchema, StudentAssignmentSchema
from .extra_time import ExtraTimeSchema
from .course import CourseSchema, CourseWithInstructorsSchema
from .jwt import RefreshTokenSchema