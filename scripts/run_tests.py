#!/usr/bin/env python3
"""Run the test suite with coverage reporting."""

import subprocess
import sys


def main() -> None:
    """Execute pytest with coverage."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
    ]
    result = subprocess.run(cmd, check=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
