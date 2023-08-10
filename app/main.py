from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware import Middleware
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1 import api_router
from app.core.config import settings
from app.core.exceptions import CustomException

def init_routers(app: FastAPI):
    app.include_router(api_router, prefix=settings.API_V1_STR)

def init_listeners(app: FastAPI):
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

def make_middleware() -> List[Middleware]:
    return [
        Middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"]
        )
    ]

def create_app() -> FastAPI:
    app = FastAPI(
        openapi_url=f"{ settings.API_V1_STR }/openapi.json",
        middleware=make_middleware()
    )
    init_routers(app)
    init_listeners(app)
    add_pagination(app)
    
    return app

app = create_app()