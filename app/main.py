
from fastapi import FastAPI, HTTPException
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1 import api_router
from app.core.config import settings

app = FastAPI(openapi_url=f"{ settings.API_V1_STR }/openapi.json")
add_pagination(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix=settings.API_V1_STR)
