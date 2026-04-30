from contextlib import asynccontextmanager
from typing import Any, Callable

from redis.asyncio.client import Redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from infrastructure.database import redis
from core.config.settings import settings
from application.dependencies.factories import *
from application.dependencies.registrator import dependencies_container

from presentation.api.v1.handlers.user import router as user_router
from presentation.api.v1.handlers.role import router as role_router
from presentation.api.v1.handlers.permission import router as permission_router

def setup_dependencies(app: FastAPI, mapper: dict[Any, Callable] | None = None) -> None:
    if mapper is None:
        mapper = dependencies_container
        
    for interface, dependency in mapper.items():
        app.dependency_overrides[interface] = dependency

@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=True
    )
    yield
    await redis.redis.aclose()
    

def create_app() -> FastAPI:
    app = FastAPI(
        title="Auth Service",
        docs_url="/api/docs",
        openapi_url="/openapi.json",
        description="Auth Service",
        lifespan=lifespan
    )
    
    setup_dependencies(app)
    
    app.include_router(user_router)
    app.include_router(role_router)
    app.include_router(permission_router)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:19006", "http://localhost:8081", "exp://", "http://localhost", "http://localhost:80"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    Instrumentator().instrument(app).expose(app)
    
    return app