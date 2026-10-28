"""schemas.py — Registration service Pydantic v2 schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnrollRequest(BaseModel):
    student_id: str
    semester_id: str
    adviser_approval_id: str


class EnrollResponse(BaseModel):
    enrollment_id: str
    student_id: str
    semester_id: str
    status: str


class EnrollmentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    semester_id: str
    adviser_approval_id: str
    status: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
