"""schemas.py — Finance service Pydantic v2 schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FeeClearanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_id: str
    semester_id: str
    cleared: bool
    amount_paid: float


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
