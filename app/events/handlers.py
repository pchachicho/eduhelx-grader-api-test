from fastapi_events.handlers.local import local_handler
from fastapi_events.typing import Event
from .schemas import SyncEvents

@local_handler.register(event_name=SyncEvents.SYNC_CREATE_ASSIGNMENT)
def handle_sync_create_assignment(event: Event):
    event_name, payload = event
    print("Handling sync event", event_name, "payload: ", payload)