import asyncio
from datetime import timedelta
from app.celery import celery_app
from app.database import SessionLocal
from app.services import LmsSyncService

@celery_app.task(name="downsync")
def downsync_from_canvas():
    with SessionLocal() as session:
        lms_sync_service = LmsSyncService(session)
        return asyncio.run(lms_sync_service.downsync())