"""schemas.py — Zenkai core Pydantic v2 schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class IncidentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    service: str
    step: str
    status: str
    error_code: Optional[str] = None
    description: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class WorkflowRunRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    semester_id: str
    status: str
    steps_completed: List[str]
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
