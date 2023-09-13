from fastapi import APIRouter
from .endpoints import submission_router, assignment_router, student_router, course_router, auth_router

api_router = APIRouter()
api_router.include_router(submission_router.router, tags=["submissions"])
api_router.include_router(assignment_router.router, tags=["assignments"])
api_router.include_router(student_router.router, tags=["students"])
api_router.include_router(course_router.router, tags=["course"])
api_router.include_router(auth_router.router, tags=["auth"])