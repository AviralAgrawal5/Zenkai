"""scripts/seed.py — Insert seed data into the Finance service database.

Inserts a fictional student STU001 with fee cleared for semester SEM-2026-A.
Run:  python scripts/seed.py
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

# Adjust path so we can import the finance service models directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "finance"))

import asyncpg  # noqa: E402  (only asyncpg needed for direct insert)

DATABASE_URL = os.environ.get(
    "FINANCE_DATABASE_URL",
    os.environ.get("DATABASE_URL", ""),
)

SEED_STUDENT_ID = "STU001"
SEED_SEMESTER_ID = "SEM-2026-A"
SEED_AMOUNT_PAID = 85000.00
SEED_ADVISER_APPROVAL_ID = "ADV-001-2026"


async def seed() -> None:
    if not DATABASE_URL:
        print("ERROR: Set DATABASE_URL or FINANCE_DATABASE_URL before running seed.py")
        sys.exit(1)

    # asyncpg needs a plain postgresql:// URL (not +asyncpg)
    url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(url)
    try:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fee_clearances (
                id          TEXT PRIMARY KEY,
                student_id  TEXT NOT NULL,
                semester_id TEXT NOT NULL,
                cleared     BOOLEAN NOT NULL DEFAULT FALSE,
                amount_paid FLOAT NOT NULL DEFAULT 0.0,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )

        existing = await conn.fetchrow(
            "SELECT id FROM fee_clearances WHERE student_id = $1 AND semester_id = $2",
            SEED_STUDENT_ID,
            SEED_SEMESTER_ID,
        )

        if existing:
            print(f"Seed record already exists (id={existing['id']}). Skipping.")
            return

        record_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        await conn.execute(
            """
            INSERT INTO fee_clearances (id, student_id, semester_id, cleared, amount_paid, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            record_id,
            SEED_STUDENT_ID,
            SEED_SEMESTER_ID,
            True,
            SEED_AMOUNT_PAID,
            now,
            now,
        )
        print(f"✓ Seeded fee clearance for {SEED_STUDENT_ID} / {SEED_SEMESTER_ID} (id={record_id})")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed())
