"""main.py — Finance service entry point."""
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from database import Base, engine
from routers.fee_clearance import router as fee_clearance_router
from schemas import HealthResponse

# ── Structured JSON logging ───────────────────────────────────────────────────
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

logger = logging.getLogger("finance")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", extra={"step": "startup", "outcome": "started", "workflow_id": "-", "event_id": "-"})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("startup", extra={"step": "startup", "outcome": "tables_ready", "workflow_id": "-", "event_id": "-"})
    yield
    logger.info("shutdown", extra={"step": "shutdown", "outcome": "complete", "workflow_id": "-", "event_id": "-"})
    await engine.dispose()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Zenkai Finance Service",
    description="Provides fee clearance status for student registration workflows.",
    version="0.1.0",
    lifespan=lifespan,
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Routers
app.include_router(fee_clearance_router)


@app.get("/health", response_model=HealthResponse, tags=["ops"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="finance",
        timestamp=datetime.now(timezone.utc),
    )
