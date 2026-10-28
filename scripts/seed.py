"""scripts/seed.py — Insert seed data into the Finance service database.

Inserts a fictional student STU001 with fee cleared for semester SEM-2026-A.
Works with both Neon PostgreSQL and local SQLite.
Run:  python scripts/seed.py
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Adjust path so we can import the finance service models directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "services" / "finance"))

from sqlalchemy import select
from database import Base, engine, AsyncSessionLocal
from models import FeeClearance

SEED_STUDENT_ID = "STU001"
SEED_SEMESTER_ID = "SEM-2026-A"
SEED_AMOUNT_PAID = 85000.00
SEED_ADVISER_APPROVAL_ID = "ADV-001-2026"


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(FeeClearance).where(
                FeeClearance.student_id == SEED_STUDENT_ID,
                FeeClearance.semester_id == SEED_SEMESTER_ID,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"Seed record already exists (id={existing.id}). Skipping.")
            return

        record = FeeClearance(
            id=str(uuid.uuid4()),
            student_id=SEED_STUDENT_ID,
            semester_id=SEED_SEMESTER_ID,
            cleared=True,
            amount_paid=SEED_AMOUNT_PAID,
        )
        session.add(record)
        await session.commit()
        print(f"[OK] Seeded fee clearance for {SEED_STUDENT_ID} / {SEED_SEMESTER_ID} (id={record.id})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
