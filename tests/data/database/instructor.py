from app.models import InstructorModel
from app.core.role_permissions import instructor_role, admin_role

basic_instructor = InstructorModel(
    onyen="pfessor",
    first_name="Pam",
    last_name="Fessor",
    email="pfessor@unc.edu",
    role=instructor_role
)

admin = InstructorModel(
    onyen="admin",
    first_name="Admin",
    last_name="",
    email="admin@renci.org",
    role=admin_role
)

data = [
    basic_instructor,
    admin
]