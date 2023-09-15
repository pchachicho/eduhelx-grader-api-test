from app.models import InstructorModel
from app.core.role_permissions import admin_role

data = [
    InstructorModel(
        onyen="admin",
        first_name="Admin",
        last_name="",
        email="admin@renci.org",
        role=admin_role
    )
]