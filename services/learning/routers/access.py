"""routers/access.py — Course access provisioning endpoints."""
import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import CourseAccess
from schemas import CourseAccessRecord, ProvisionRequest, ProvisionResponse

logger = logging.getLogger("learning")

router = APIRouter(tags=["access"])


@router.post("/provision-access", response_model=ProvisionResponse, status_code=201)
async def provision_access(
    body: ProvisionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ProvisionResponse:
    """Provision learning portal access for a set of courses after enrollment."""
    workflow_id = request.headers.get("X-Workflow-ID", str(uuid.uuid4()))
    logger.info(
        "provision_access_started",
        extra={
            "workflow_id": workflow_id,
            "event_id": str(uuid.uuid4()),
            "step": "provision_access",
            "outcome": "started",
            "student_id": body.student_id,
            "enrollment_id": body.enrollment_id,
            "course_count": len(body.courses),
        },
    )

    # ── Idempotency: skip already-provisioned courses ─────────────────────────
    existing_result = await db.execute(
        select(CourseAccess.course_code).where(
            CourseAccess.student_id == body.student_id,
            CourseAccess.enrollment_id == body.enrollment_id,
        )
    )
    already_provisioned = {row[0] for row in existing_result.all()}

    records: List[CourseAccess] = []
    skipped: List[str] = []
    for course in body.courses:
        if course.code in already_provisioned:
            skipped.append(course.code)
            continue
        access = CourseAccess(
            id=str(uuid.uuid4()),
            student_id=body.student_id,
            enrollment_id=body.enrollment_id,
            course_code=course.code,
            course_name=course.name,
            status="active",
        )
        db.add(access)
        records.append(access)

    if skipped:
        logger.info(
            "provision_access_skipped_duplicates",
            extra={
                "workflow_id": workflow_id,
                "event_id": str(uuid.uuid4()),
                "step": "provision_access",
                "outcome": "partial_skip",
                "skipped": skipped,
            },
        )

    if not records and skipped:
        raise HTTPException(
            status_code=409,
            detail=f"All courses already provisioned for enrollment {body.enrollment_id}",
        )

    await db.flush()

    logger.info(
        "provision_access_complete",
        extra={
            "workflow_id": workflow_id,
            "event_id": str(uuid.uuid4()),
            "step": "provision_access",
            "outcome": "success",
            "student_id": body.student_id,
            "enrollment_id": body.enrollment_id,
            "provisioned": len(records),
        },
    )

    return ProvisionResponse(
        provisioned=len(records),
        student_id=body.student_id,
        enrollment_id=body.enrollment_id,
        courses=[r.course_code for r in records],
    )


@router.get("/access/{student_id}", response_model=List[CourseAccessRecord])
async def get_access(
    student_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> List[CourseAccessRecord]:
    """Return all active course access records for a student (paginated)."""
    result = await db.execute(
        select(CourseAccess)
        .where(CourseAccess.student_id == student_id)
        .order_by(CourseAccess.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    records = result.scalars().all()
    return [CourseAccessRecord.model_validate(r) for r in records]
