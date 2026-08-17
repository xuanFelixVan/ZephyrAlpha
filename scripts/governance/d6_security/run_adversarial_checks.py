# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/run_adversarial_checks.py | §
# [MODULE] scripts.governance.d6_security.run_adversarial_checks
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
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

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402

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
