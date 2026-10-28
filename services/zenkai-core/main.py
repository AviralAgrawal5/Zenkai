"""main.py — Zenkai core entry point (monitor, diagnose, recover)."""
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from database import Base, engine
from routers.incidents import router as incidents_router
from routers.workflows import router as workflows_router
from schemas import HealthResponse

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    rename_fields={"asctime": "timestamp", "levelname": "level", "name": "service"},
)
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.handlers = [handler]
root_logger.setLevel(LOG_LEVEL)

logger = logging.getLogger("zenkai-core")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "startup",
        extra={
            "step": "startup",
            "outcome": "started",
            "workflow_id": "-",
            "event_id": "-",
            "service": "zenkai-core",
        },
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(
        "startup",
        extra={
            "step": "startup",
            "outcome": "tables_ready",
            "workflow_id": "-",
            "event_id": "-",
            "service": "zenkai-core",
        },
    )
    yield
    logger.info(
        "shutdown",
        extra={
            "step": "shutdown",
            "outcome": "complete",
            "workflow_id": "-",
            "event_id": "-",
            "service": "zenkai-core",
        },
    )
    await engine.dispose()


app = FastAPI(
    title="Zenkai Core",
    description="AI-powered self-healing recovery engine for university ERP workflows.",
    version="0.1.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)
app.include_router(incidents_router)
app.include_router(workflows_router)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="zenkai-core",
        timestamp=datetime.now(timezone.utc),
    )
