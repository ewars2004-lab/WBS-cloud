from __future__ import annotations

import subprocess
import sys


def run_self_check() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent),
    )
    return result.returncode
