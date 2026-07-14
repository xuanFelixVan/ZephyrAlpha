# [BLUEPRINT] MOD-INF-005 | scripts/governance/ci_self_check.py | §
# [MODULE] scripts.governance.ci_self_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
# [TTL] task_bound
"""
CI Entry: Self-Check — Drift Detector 自身完整性验证
=====================================================
Tier 8 — 纯 stdlib 零依赖的完整性检查。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'CI Entry: Self-Check — Drift Detector 自身完整性验证'
dimensions:
- D1
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
    print("  SELF-CHECK — DRIFT DETECTOR INTEGRITY")
    print("=" * 60)

    self_check_path = str(PROJECT_ROOT / "src" / "zephyr" / "drift-detector" / "self_check.py")

    result = subprocess.run(
        [sys.executable, self_check_path],
        capture_output=False,
        text=True,
        timeout=30,
        cwd=str(PROJECT_ROOT),
    )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
