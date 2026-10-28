"""models.py — Finance service SQLAlchemy async models."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FeeClearance(Base):
    """Records whether a student has cleared their fees for a semester."""

    __tablename__ = "fee_clearances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    semester_id: Mapped[str] = mapped_column(String(64), nullable=False)
    cleared: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    amount_paid: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
