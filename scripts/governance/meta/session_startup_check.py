# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/session_startup_check.py | §
# [MODULE] scripts.governance.meta.session_startup_check
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.ops_governance.phase_manager; zephyr.governance.ops_governance.phase_check_registry
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
"""Session 冷启动自检 — 运行 Phase 0 全部 14 个检查并输出状态报告.

用法:
    python scripts/governance/session_startup_check.py
    python scripts/governance/session_startup_check.py --json
    python scripts/governance/session_startup_check.py --phase 0  # 仅 Phase 0

退出码:
    0 = ALL GREEN（可以开工）
    1 = 有 YELLOW（警告，可以开工但需注意）
    2 = 有 RED（阻断，禁止开工）

集成方式:
    在 project_rules.md 冷启动序列 STEP 4.5 后执行本脚本。
    或作为 RULE-FIRST-READ 的自动化实现。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Session 冷启动自检 — 运行 Phase 0 全部 14 个检查并输出状态报告.
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import json
import sys
from datetime import UTC, datetime

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent))

from zephyr.governance.ops_governance.phase_manager import (
    PHASE_SEQUENCE,
    ConstructionPhase,
    GateResult,
)


def _emoji(result: GateResult) -> str:
    """_emoji implementation."""
    if result == GateResult.GREEN:
        return "[GREEN]"
    if result == GateResult.YELLOW:
        return "[YELLOW]"
    return "[RED]"


def _run_phase(phase: ConstructionPhase, label: str) -> dict:
    """_run_phase implementation."""
    from zephyr.governance.ops_governance.phase_check_registry import run_check

    phase_gate = PHASE_SEQUENCE[phase]
    result = phase_gate.run_checks()
    checks: list[dict] = []
    for check_name in phase_gate.gate_checks:
        r = run_check(check_name)
        checks.append({"name": check_name, "result": r.value})
    return {
        "phase": phase.value,
        "label": label,
        "check_count": phase_gate.check_count,
        "overall": result.value,
        "checks": checks,
    }


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Session 冷启动自检")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--phase", type=int, default=0, help="检查阶段 (0/1/2)")
    args = parser.parse_args()

    phase_map = {
        0: (ConstructionPhase.PHASE_0_SKELETON, "Phase 0"),
        1: (ConstructionPhase.PHASE_1_FUNCTIONAL, "Phase 1"),
        2: (ConstructionPhase.PHASE_2_E2E, "Phase 2"),
    }

    phases_to_run = [phase_map[args.phase]] if args.phase in phase_map else list(phase_map.values())

    results = []
    for phase, label in phases_to_run:
        results.append(_run_phase(phase, label))

    if args.json:
        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "phases": results,
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("  ZephyrAlpha Session 冷启动自检")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        for r in results:
            print(f"\n{r['label']} ({r['check_count']} checks): {_emoji(GateResult(r['overall']))} {r['overall']}")
            for c in r["checks"]:
                print(f"  {_emoji(GateResult(c['result']))} {c['name']}: {c['result']}")

        worst = max(
            (GateResult(r["overall"]) for r in results), key=lambda x: ["GREEN", "YELLOW", "RED"].index(x.value)
        )
        print(f"\n{'=' * 60}")
        print(f"  最终判定: {_emoji(worst)} {worst.value}")
        if worst == GateResult.GREEN:
            print("  可以开工。")
        elif worst == GateResult.YELLOW:
            print("  有警告，可以开工但需注意以上 YELLOW 项。")
        else:
            print("  BLOCKED——必须先修复以上 RED 项才能开工。")
        print("=" * 60)

    worst = max((GateResult(r["overall"]) for r in results), key=lambda x: ["GREEN", "YELLOW", "RED"].index(x.value))
    if worst == GateResult.RED:
        return EXIT_ERROR
    if worst == GateResult.YELLOW:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
