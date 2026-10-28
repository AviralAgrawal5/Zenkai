"""routers/enrollment.py — Enrollment endpoints for the Registration service."""
import logging
import os
import uuid
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Enrollment
from schemas import EnrollRequest, EnrollResponse, EnrollmentRecord

logger = logging.getLogger("registration")

router = APIRouter(tags=["enrollment"])

FINANCE_SERVICE_URL = os.environ.get("FINANCE_SERVICE_URL", "http://finance:8001")


@router.post("/enroll", response_model=EnrollResponse, status_code=201)
async def enroll_student(
    body: EnrollRequest,
    db: AsyncSession = Depends(get_db),
) -> EnrollResponse:
    """Enroll a student: verifies fee clearance with Finance, then creates enrollment record."""
    workflow_id = str(uuid.uuid4())
    event_id = str(uuid.uuid4())

    logger.info(
        "enrollment_started",
        extra={
            "workflow_id": workflow_id,
            "event_id": event_id,
            "step": "enroll",
            "outcome": "started",
            "student_id": body.student_id,
            "semester_id": body.semester_id,
        },
    )

    # ── Step 1: Verify fee clearance ─────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{FINANCE_SERVICE_URL}/students/{body.student_id}/fee-clearance",
                params={"semester_id": body.semester_id},
            )
    except httpx.RequestError as exc:
        logger.error(
            "finance_unreachable",
            extra={
                "workflow_id": workflow_id,
                "event_id": str(uuid.uuid4()),
                "step": "fee_clearance_check",
                "outcome": "error",
                "error": str(exc),
            },
        )
        raise HTTPException(status_code=503, detail="Finance service unreachable")

    if resp.status_code == 404:
        raise HTTPException(status_code=422, detail="No fee clearance record found for student")

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Finance service returned {resp.status_code}")

    clearance = resp.json()
    if not clearance.get("cleared"):
        logger.warning(
            "fee_not_cleared",
            extra={
                "workflow_id": workflow_id,
                "event_id": str(uuid.uuid4()),
                "step": "fee_clearance_check",
                "outcome": "blocked",
                "student_id": body.student_id,
            },
        )
        raise HTTPException(
            status_code=422,
            detail="Student has not cleared fees for this semester",
        )

    logger.info(
        "fee_clearance_verified",
        extra={
            "workflow_id": workflow_id,
            "event_id": str(uuid.uuid4()),
            "step": "fee_clearance_check",
            "outcome": "success",
        },
    )

    # ── Step 2: Create enrollment record ────────────────────────────────────────
    enrollment = Enrollment(
        id=str(uuid.uuid4()),
        student_id=body.student_id,
        semester_id=body.semester_id,
        adviser_approval_id=body.adviser_approval_id,
        status="enrolled",
    )
    db.add(enrollment)
    await db.flush()

    logger.info(
        "enrollment_created",
        extra={
            "workflow_id": workflow_id,
            "event_id": str(uuid.uuid4()),
            "step": "create_enrollment",
            "outcome": "success",
            "enrollment_id": enrollment.id,
        },
    )

    return EnrollResponse(
        enrollment_id=enrollment.id,
        student_id=enrollment.student_id,
        semester_id=enrollment.semester_id,
        status=enrollment.status,
    )


@router.get("/enrollments/{student_id}", response_model=List[EnrollmentRecord])
async def get_enrollments(
    student_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[EnrollmentRecord]:
    """Return all enrollment records for a student."""
    result = await db.execute(
        select(Enrollment)
        .where(Enrollment.student_id == student_id)
        .order_by(Enrollment.created_at.desc())
    )
    records = result.scalars().all()
    return [EnrollmentRecord.model_validate(r) for r in records]
