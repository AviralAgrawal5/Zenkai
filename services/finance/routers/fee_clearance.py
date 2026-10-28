"""routers/fee_clearance.py — Fee clearance endpoints for the Finance service."""
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import FeeClearance
from schemas import FeeClearanceResponse

logger = logging.getLogger("finance")

router = APIRouter(prefix="/students", tags=["fee-clearance"])


@router.get("/{student_id}/fee-clearance", response_model=FeeClearanceResponse)
async def get_fee_clearance(
    student_id: str,
    request: Request,
    semester_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> FeeClearanceResponse:
    """Return the fee clearance status for a student, optionally scoped to a semester."""
    # Propagate workflow_id from upstream caller for cross-service log correlation
    workflow_id = request.headers.get("X-Workflow-ID", str(uuid.uuid4()))
    logger.info(
        "fee_clearance_lookup",
        extra={
            "workflow_id": workflow_id,
            "event_id": str(uuid.uuid4()),
            "step": "lookup",
            "outcome": "started",
            "student_id": student_id,
            "semester_id": semester_id,
        },
    )

    stmt = select(FeeClearance).where(FeeClearance.student_id == student_id)
    if semester_id:
        stmt = stmt.where(FeeClearance.semester_id == semester_id)
    stmt = stmt.order_by(FeeClearance.created_at.desc()).limit(1)

    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if record is None:
        logger.warning(
            "fee_clearance_not_found",
            extra={
                "workflow_id": workflow_id,
                "event_id": str(uuid.uuid4()),
                "step": "lookup",
                "outcome": "not_found",
                "student_id": student_id,
            },
        )
        raise HTTPException(
            status_code=404,
            detail=f"No fee clearance record found for student {student_id}",
        )

    logger.info(
        "fee_clearance_found",
        extra={
            "workflow_id": workflow_id,
            "event_id": str(uuid.uuid4()),
            "step": "lookup",
            "outcome": "success",
            "student_id": student_id,
            "cleared": record.cleared,
        },
    )
    return FeeClearanceResponse(
        student_id=record.student_id,
        semester_id=record.semester_id,
        cleared=record.cleared,
        amount_paid=record.amount_paid,
    )
