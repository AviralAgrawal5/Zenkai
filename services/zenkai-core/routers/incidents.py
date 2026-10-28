"""routers/incidents.py — Incident management endpoints."""
import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Incident
from schemas import IncidentRecord

logger = logging.getLogger("zenkai-core")

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=List[IncidentRecord])
async def list_incidents(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> List[IncidentRecord]:
    """List incidents, optionally filtered by status (open, resolved)."""
    stmt = select(Incident).order_by(Incident.created_at.desc())
    if status:
        stmt = stmt.where(Incident.status == status)
    result = await db.execute(stmt)
    incidents = result.scalars().all()
    return [IncidentRecord.model_validate(i) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentRecord)
async def get_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
) -> IncidentRecord:
    from fastapi import HTTPException

    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentRecord.model_validate(incident)
