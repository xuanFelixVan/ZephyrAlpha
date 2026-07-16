# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/run_adversarial_checks.py | §
# [MODULE] scripts.governance.d6_security.run_adversarial_checks
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
CI Entry: Adversarial Validation — Red-Blue Drift Test
=======================================================
Tier 8 — 每次 CI 运行红蓝对抗：注入混沌漂移 → 蓝队检测 → 裁判对比。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'CI Entry: Adversarial Validation — Red-Blue Drift Test'
dimensions:
- D6
priority: P2
timeout_seconds: 60
warn_only: false
"""


import subprocess
import sys
from pathlib import Path
from _shared.constants import REPO_ROOT

PROJECT_ROOT = REPO_ROOT


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 60)
    print("  ADVERSARIAL VALIDATION — DRIFT RED-BLUE")
    print("=" * 60)

    adversarial_test = str(PROJECT_ROOT / "tests" / "infrastructure" / "test_drift_red_blue_adversarial.py")

    result = subprocess.run(
        [sys.executable, adversarial_test],
        capture_output=False,
        text=True,
        timeout=120,
        cwd=str(PROJECT_ROOT),
    )

    if result.returncode == 0:
        print("\n  ALL INJECTIONS DETECTED — DRIFT DETECTOR OPERATIONAL")
    else:
        print("\n  ROOT CAUSE ANALYSIS REQUIRED — MISSED INJECTIONS DETECTED")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
