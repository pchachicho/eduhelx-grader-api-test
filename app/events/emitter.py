from typing import Callable
from pydantic import BaseModel
from pymitter import EventEmitter

EVENT_DELIMITER = ":"

class PydanticEvent(BaseModel):
    __event_name__: str

    @classmethod
    def get_parent_namespace(cls) -> str:
        # NOTE: a "namespace" is just the next-level up category of the event.
        # For example, "crud:assignment:create" -> "crud:assignment".
        # This is mostly useful for wildcarding.
        return cls.__event_name__.rsplit(EVENT_DELIMITER, 1)[0]

class PydanticEventEmitter(EventEmitter):
    def _validate_pydantic_event(event: PydanticEvent) -> tuple[str, dict]:
        if not isinstance(event, PydanticEvent):
            raise TypeError(f"unrecognized event { event }, only Pydantic events are supported")
        
        # By converting the event to a dict, Pydantic performs validation on it.
        name, payload = event.__event_name__, event.dict()
        return name, payload
    
    def on(self, event: str | BaseModel, *args, **kwargs) -> Callable:
        # Support passing in an event model as an event name.
        if isinstance(event, BaseModel):
            event = event.__event_name__
        
        return super().on(event, *args, **kwargs)

    def emit(self, event: BaseModel) -> None:
        name, payload = self._validate_pydantic_event(event)
        super().emit(name, payload)

    async def emit_async(self, event: BaseModel) -> None:
        name, payload = self._validate_pydantic_event(event)
        await super().emit_async(name, payload)

ee = PydanticEventEmitter(wildcard=True, delimiter=":")