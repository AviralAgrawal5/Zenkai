"""routers/workflows.py — Workflow run tracking endpoints."""
import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import WorkflowRun
from schemas import WorkflowRunRecord

logger = logging.getLogger("zenkai-core")

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=List[WorkflowRunRecord])
async def list_workflows(
    student_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> List[WorkflowRunRecord]:
    """List workflow runs, optionally filtered by student_id."""
    stmt = select(WorkflowRun).order_by(WorkflowRun.created_at.desc())
    if student_id:
        stmt = stmt.where(WorkflowRun.student_id == student_id)
    result = await db.execute(stmt)
    runs = result.scalars().all()
    return [WorkflowRunRecord.model_validate(r) for r in runs]
