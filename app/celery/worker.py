from celery import Celery
from celery.result import AsyncResult
from app.core.config import settings

celery_app = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URI,
    backend=settings.CELERY_RESULT_BACKEND
)
celery_app.conf.update(
    imports=["app.celery.tasks"],
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    worker_enable_remote_control=True
)

def get_task_status_by_id(task_id: str) -> AsyncResult:
    return celery_app.AsyncResult(task_id)

def cancel_task_by_id(task_id: str):
    celery_app.control.revoke(task_id, terminate=True, signal="SIGKILL")