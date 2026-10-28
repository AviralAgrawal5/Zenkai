"""scripts/demo_happy_path.py — Demonstrate a successful student registration flow.

Calls each service in order:
  1. Finance: verify fee clearance
  2. Registration: enroll student (calls Finance internally)
  3. Learning: provision course access

Run:  python scripts/demo_happy_path.py
"""
import asyncio
import json
import os
import sys
import uuid

import httpx

FINANCE_URL = os.environ.get("FINANCE_SERVICE_URL", "http://localhost:8001")
REGISTRATION_URL = os.environ.get("REGISTRATION_SERVICE_URL", "http://localhost:8002")
LEARNING_URL = os.environ.get("LEARNING_SERVICE_URL", "http://localhost:8003")
ZENKAI_URL = os.environ.get("ZENKAI_CORE_URL", "http://localhost:8004")

STUDENT_ID = "STU001"
SEMESTER_ID = "SEM-2026-A"
ADVISER_APPROVAL_ID = "ADV-001-2026"
COURSES = [
    {"code": "CS401", "name": "Distributed Systems"},
    {"code": "CS402", "name": "Machine Learning"},
    {"code": "CS403", "name": "Software Engineering"},
]


def _print_step(step: str, data: dict | str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {step}")
    print(f"{'─' * 60}")
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, default=str))
    else:
        print(data)


async def run() -> None:
    workflow_id = f"demo-wf-{uuid.uuid4().hex[:8]}"
    headers = {"X-Workflow-ID": workflow_id}
    print(f"Starting registration flow with Workflow ID: {workflow_id}")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # ── Step 0: Health checks ─────────────────────────────────────────────
        print("Zenkai Happy-Path Demo — checking service health…")
        for name, url in [
            ("finance", FINANCE_URL),
            ("registration", REGISTRATION_URL),
            ("learning", LEARNING_URL),
            ("zenkai-core", ZENKAI_URL),
        ]:
            try:
                r = await client.get(f"{url}/health")
                status = r.json().get("status", "?")
                print(f"  [{status.upper()}] {name}")
            except httpx.RequestError as exc:
                print(f"  [UNREACHABLE] {name}: {exc}")

        # ── Step 1: Fee clearance ──────────────────────────────────────────────
        resp = await client.get(
            f"{FINANCE_URL}/students/{STUDENT_ID}/fee-clearance",
            params={"semester_id": SEMESTER_ID},
            headers=headers,
        )
        resp.raise_for_status()
        clearance = resp.json()
        _print_step("1. Fee Clearance (Finance)", clearance)
        if not clearance.get("cleared"):
            print("BLOCKED: Student fees are not cleared. Aborting demo.")
            sys.exit(1)

        # ── Step 2: Enroll ─────────────────────────────────────────────────────
        resp = await client.post(
            f"{REGISTRATION_URL}/enroll",
            json={
                "student_id": STUDENT_ID,
                "semester_id": SEMESTER_ID,
                "adviser_approval_id": ADVISER_APPROVAL_ID,
            },
            headers=headers,
        )
        resp.raise_for_status()
        enrollment = resp.json()
        _print_step("2. Semester Enrollment (Registration)", enrollment)

        enrollment_id = enrollment["enrollment_id"]

        # ── Step 3: Provision course access ────────────────────────────────────
        resp = await client.post(
            f"{LEARNING_URL}/provision-access",
            json={
                "student_id": STUDENT_ID,
                "enrollment_id": enrollment_id,
                "courses": COURSES,
            },
            headers=headers,
        )
        resp.raise_for_status()
        provision = resp.json()
        _print_step("3. Course Access (Learning Portal)", provision)

        # ── Step 4: Verify enrollments ─────────────────────────────────────────
        resp = await client.get(f"{REGISTRATION_URL}/enrollments/{STUDENT_ID}")
        resp.raise_for_status()
        _print_step("4. Enrollment records", resp.json())

        # ── Step 5: Verify course access ──────────────────────────────────────
        resp = await client.get(f"{LEARNING_URL}/access/{STUDENT_ID}")
        resp.raise_for_status()
        _print_step("5. Course access records", resp.json())

        print(f"\n{'═' * 60}")
        print("  ✓ Happy-path registration complete!")
        print(f"    Student   : {STUDENT_ID}")
        print(f"    Semester  : {SEMESTER_ID}")
        print(f"    Enrollment: {enrollment_id}")
        print(f"    Courses   : {[c['code'] for c in COURSES]}")
        print(f"{'═' * 60}\n")


if __name__ == "__main__":
    asyncio.run(run())
