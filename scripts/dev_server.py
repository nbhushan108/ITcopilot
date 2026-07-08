#!/usr/bin/env python3
"""Development server startup script."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Start the FastAPI development server."""
    project_root = Path(__file__).resolve().parent.parent
    api_dir = project_root / "apps" / "api"

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
        "--app-dir",
        str(api_dir),
    ]

    print(f"Starting ITcopilot API from {api_dir}")
    subprocess.run(cmd, cwd=str(project_root), check=True)


if __name__ == "__main__":
    main()
