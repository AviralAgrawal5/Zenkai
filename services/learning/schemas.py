"""schemas.py — Learning portal Pydantic v2 schemas."""
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class CourseItem(BaseModel):
    code: str
    name: str = ""


class ProvisionRequest(BaseModel):
    student_id: str
    enrollment_id: str
    courses: List[CourseItem]


class CourseAccessRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    student_id: str
    enrollment_id: str
    course_code: str
    course_name: str
    status: str
    created_at: datetime


class ProvisionResponse(BaseModel):
    provisioned: int
    student_id: str
    enrollment_id: str
    courses: List[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
