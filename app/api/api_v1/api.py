from fastapi import APIRouter
from .endpoints import submission_router

api_router = APIRouter()
api_router.include_router(submission_router.router, tags=["submissions"])