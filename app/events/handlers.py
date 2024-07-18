from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import AssignmentModel
from app.events.schemas import AssignmentCrudEvent
from app.events.emitter import event_emitter
from app.core.dependencies import get_db_persistent

"""
NOTE: Use `get_db_persistent` instead of `get_db`. FastAPI-Events does not support generator-based DI.
You MUST call Session.close() once you are done with the database session. 
"""


@event_emitter.on("crud:assignment:*")
async def handle_sync_create_assignment(event: AssignmentCrudEvent):
    from app.services import GiteaService, StudentService, CourseService
    
    assignment = event.assignment
    raise Exception("testing")
    print(123948123094813290132809, assignment.id, "changed")

    with SessionLocal() as session:
        course_service = CourseService(session)
        gitea_service = GiteaService(session)

        hook_content = await gitea_service.get_merge_control_hook()    
        master_repository_name = await course_service.get_master_repository_name()
        instructor_organization_name = await course_service.get_instructor_gitea_organization_name()

        await GiteaService(session).set_git_hook(
            repository_name=master_repository_name,
            owner=instructor_organization_name,
            hook_id="pre-receive",
            hook_content=hook_content
        )