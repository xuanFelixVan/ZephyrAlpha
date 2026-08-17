# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/check_drift_e2e.py | §
# [MODULE] scripts.governance.d5_architecture.check_drift_e2e
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.__init__
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
CI Entry: Drift Detector E2E Pipeline Check
============================================
Tier 8 — 每次 CI 全量回归时运行 drift E2E + 自检 + 注册表一致性。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'CI Entry: Drift Detector E2E Pipeline Check'
dimensions:
- D5
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


def run_pytest(test_module: str) -> bool:
    """run_pytest implementation."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_module, "-x", "--tb=short", "-q", "--no-header"],
        capture_output=False,
        text=True,
        timeout=120,
        cwd=str(PROJECT_ROOT),
    )
    return result.returncode == 0


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    failed = 0

    print("=" * 60)
    print("  DRIFT E2E PIPELINE CHECK")
    print("=" * 60)

    tests = [
        "tests/infrastructure/test_drift_e2e_pipeline.py",
    ]

    for test_path in tests:
        full = str(PROJECT_ROOT / test_path)
        print(f"\n  Running: {test_path}")
        ok = run_pytest(full)
        if ok:
            print(f"  PASS: {test_path}")
        else:
            print(f"  FAIL: {test_path}")
            failed += 1

    print(f"\n  Total failures: {failed}")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
