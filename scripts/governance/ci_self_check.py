# [BLUEPRINT] MOD-INF-005 | scripts/governance/ci_self_check.py | §
"""
CI Entry: Self-Check — Drift Detector 自身完整性验证
=====================================================
Tier 8 — 纯 stdlib 零依赖的完整性检查。
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 60)
    print("  SELF-CHECK — DRIFT DETECTOR INTEGRITY")
    print("=" * 60)

    self_check_path = str(
        PROJECT_ROOT / "src" / "zephyr" / "drift-detector" / "self_check.py"
    )

    result = subprocess.run(
        [sys.executable, self_check_path],
        capture_output=False, text=True, timeout=30,
        cwd=str(PROJECT_ROOT),
    )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
