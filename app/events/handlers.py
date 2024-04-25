from fastapi import Depends
from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
from sqlalchemy.orm import Session

from .schemas import SyncEvents
from app.models import AssignmentModel
from app.services import AssignmentService
from app.core.dependencies import get_db_persistent

"""
NOTE: Use `get_db_persistent` instead of `get_db`. FastAPI-Events does not support generator-based DI.
You MUST call Session.close() once you are done with the database session. 
"""


@local_handler.register(event_name=SyncEvents.SYNC_CREATE_ASSIGNMENT)
async def handle_sync_create_assignment(event: Event, session: Session = Depends(get_db_persistent)):
    event_name, payload = event
    assignment_id = payload["assignment_id"]

    assignment = await AssignmentService(session).get_assignment_by_id(assignment_id)
    print("Handling sync event <Create Assignment>, assignment name:", assignment.name)

    session.close()