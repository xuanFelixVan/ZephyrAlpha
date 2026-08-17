# [BLUEPRINT] MOD-INF-005 | scripts/governance/ci_self_check.py | §
# [MODULE] scripts.governance.ci_self_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
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

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402

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
