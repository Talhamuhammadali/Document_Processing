"""FastAPI application main module."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.processing.config_store import seed_configs
from app.core.redis_client import redis_client
from app.routers import chat, documents, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Seed configs, ensure the PDF store, and open/close the arq pool."""
    seed_configs(redis_client(decode_responses=True), settings.configs_dir)
    settings.pdf_store_dir.mkdir(parents=True, exist_ok=True)
    app.state.arq = await create_pool(
        RedisSettings(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            database=settings.redis_db,
        )
    )
    yield
    await app.state.arq.aclose()


app = FastAPI(
    title="Document Processing API",
    description="API for document processing and chat",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)
