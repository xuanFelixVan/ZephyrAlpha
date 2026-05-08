"""
CI Entry: Adversarial Validation — Red-Blue Drift Test
=======================================================
Tier 8 — 每次 CI 运行红蓝对抗：注入混沌漂移 → 蓝队检测 → 裁判对比。
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 60)
    print("  ADVERSARIAL VALIDATION — DRIFT RED-BLUE")
    print("=" * 60)

    adversarial_test = str(
        PROJECT_ROOT / "tests" / "infrastructure" / "test_drift_red_blue_adversarial.py"
    )

    result = subprocess.run(
        [sys.executable, adversarial_test],
        capture_output=False, text=True, timeout=120,
        cwd=str(PROJECT_ROOT),
    )

    if result.returncode == 0:
        print("\n  ALL INJECTIONS DETECTED — DRIFT DETECTOR OPERATIONAL")
    else:
        print("\n  ROOT CAUSE ANALYSIS REQUIRED — MISSED INJECTIONS DETECTED")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
