"""scripts/run_local.py — Launch all Zenkai microservices and frontend locally.

Runs:
  - Finance Service:      http://localhost:8001
  - Registration Service: http://localhost:8002
  - Learning Portal:      http://localhost:8003
  - Zenkai Core:          http://localhost:8004
  - React Dashboard:      http://localhost:5173

Press Ctrl+C to stop all services.
"""
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Detect venv Python if available
VENV_PYTHON = REPO_ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
PYTHON_EXE = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

SERVICES = [
    {
        "name": "finance",
        "cmd": [PYTHON_EXE, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"],
        "cwd": str(REPO_ROOT / "services" / "finance"),
    },
    {
        "name": "registration",
        "cmd": [PYTHON_EXE, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8002"],
        "cwd": str(REPO_ROOT / "services" / "registration"),
    },
    {
        "name": "learning",
        "cmd": [PYTHON_EXE, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8003"],
        "cwd": str(REPO_ROOT / "services" / "learning"),
    },
    {
        "name": "zenkai-core",
        "cmd": [PYTHON_EXE, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8004"],
        "cwd": str(REPO_ROOT / "services" / "zenkai-core"),
    },
    {
        "name": "frontend",
        "cmd": ["npm.cmd" if os.name == "nt" else "npm", "run", "dev"],
        "cwd": str(REPO_ROOT / "frontend"),
    },
]


def main():
    print("=" * 60)
    print("  Zenkai Local Multi-Service Runner")
    print("=" * 60)

    # 1. Seed database first
    print("\n[1/2] Seeding initial database...")
    seed_script = REPO_ROOT / "scripts" / "seed.py"
    res = subprocess.run([PYTHON_EXE, str(seed_script)])
    if res.returncode != 0:
        print("Warning: Database seed returned non-zero code.")

    # 2. Launch all services
    print("\n[2/2] Starting microservices and frontend...")
    processes = []
    try:
        for svc in SERVICES:
            print(f"  -> Starting {svc['name']}...")
            p = subprocess.Popen(
                svc["cmd"],
                cwd=svc["cwd"],
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            processes.append((svc["name"], p))

        print("\n" + "=" * 60)
        print("  All services running on localhost:")
        print("    * Frontend UI:    http://localhost:5173")
        print("    * Finance API:    http://localhost:8001/docs")
        print("    * Registration:   http://localhost:8002/docs")
        print("    * Learning API:   http://localhost:8003/docs")
        print("    * Zenkai Core:    http://localhost:8004/docs")
        print("=" * 60)
        print("Press Ctrl+C to stop all services.\n")

        while True:
            time.sleep(1)
            for name, p in processes:
                if p.poll() is not None:
                    print(f"Process {name} exited unexpectedly with code {p.returncode}")
                    return

    except KeyboardInterrupt:
        print("\nStopping all services...")
    finally:
        for name, p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("All services stopped.")


if __name__ == "__main__":
    main()
