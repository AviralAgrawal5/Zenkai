"""main.py — Learning portal service entry point."""
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from database import Base, engine
from routers.access import router as access_router
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

logger = logging.getLogger("learning")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", extra={"step": "startup", "outcome": "started", "workflow_id": "-", "event_id": "-"})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("startup", extra={"step": "startup", "outcome": "tables_ready", "workflow_id": "-", "event_id": "-"})
    yield
    logger.info("shutdown", extra={"step": "shutdown", "outcome": "complete", "workflow_id": "-", "event_id": "-"})
    await engine.dispose()


app = FastAPI(
    title="Zenkai Learning Portal Service",
    description="Provisions course access after successful semester enrollment.",
    version="0.1.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)
app.include_router(access_router)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="learning",
        timestamp=datetime.now(timezone.utc),
    )
