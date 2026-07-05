# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.kb.safety_brake
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.kb.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_safety_brake | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""冷静期引擎 + 魔鬼代言人 + 影响评估
======================================
蓝图: MOD-KB-001 §7.10.5
任务: KB-INF-0050

冷静期: 高风险操作前强制等待 N 秒
魔鬼代言人: 在标记 KE 为 authoritative 前进行反面论证
影响评估: 批量操作前评估受影响KE范围

用法:
    from zephyr.governance.kb.safety_brake import SafetyBrake
    sb = SafetyBrake()
    sb.pre_flight_check("batch_delete", affected_ke_count=50)
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OperationType(str, Enum):
    WRITE = "write"
    DELETE = "delete"
    BATCH_UPDATE = "batch_update"
    MARK_AUTHORITATIVE = "mark_authoritative"
    RECLASSIFY = "reclassify"
    PURGE = "purge"


@dataclass
class PreFlightResult:
    operation: str
    risk_level: RiskLevel
    affected_ke_count: int
    cooling_period_seconds: int
    passed: bool
    devils_advocate_required: bool = False
    # 5.107.5/6 修复: =None 改为 field(default_factory=list),消除类型注解与默认值不一致
    blocking_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _get_project_root() -> Path:
    env = os.environ.get("ZEPHYR_PROJECT_ROOT")
    if env:
        return Path(env)
    return REPO_ROOT


class SafetyBrake:
    _QUIET_PERIOD_SECONDS = 30
    _MAX_EPIDEMIC_CHANGES = 50
    _PRE_FLIGHT_CHECKS = 3

    def __init__(self, project_root: Path | None = None):
        self._root = project_root or _get_project_root()

    def pre_flight_check(
        self,
        operation: OperationType,
        affected_ke_count: int = 1,
        skip_cooling: bool = False,
    ) -> PreFlightResult:
        risk = self._assess_risk(operation, affected_ke_count)
        blocking: list[str] = []
        warnings: list[str] = []

        if affected_ke_count > self._MAX_EPIDEMIC_CHANGES:
            blocking.append(
                f"Epidemic threshold exceeded: {affected_ke_count} > {self._MAX_EPIDEMIC_CHANGES}. "
                "Split into smaller batches."
            )

        if operation is OperationType.DELETE and affected_ke_count > 5:
            warnings.append(f"Deleting {affected_ke_count} KEs. Verify tombstone before proceeding.")

        if operation is OperationType.MARK_AUTHORITATIVE:
            warnings.append("Devil's advocate check required: verify there is no contradictory evidence.")

        if operation is OperationType.PURGE:
            warnings.append("Irreversible operation. Confirm backup exists.")

        cooling = 0
        if risk in (RiskLevel.HIGH, RiskLevel.CRITICAL) and not skip_cooling:
            cooling = self._QUIET_PERIOD_SECONDS

        dv_required = operation is OperationType.MARK_AUTHORITATIVE or risk is RiskLevel.CRITICAL

        return PreFlightResult(
            operation=operation.value,
            risk_level=risk,
            affected_ke_count=affected_ke_count,
            cooling_period_seconds=cooling,
            passed=len(blocking) == 0,
            devils_advocate_required=dv_required,
            blocking_issues=blocking,
            warnings=warnings,
        )

    def _assess_risk(self, operation: OperationType, count: int) -> RiskLevel:
        if operation is OperationType.PURGE:
            return RiskLevel.CRITICAL
        if operation is OperationType.DELETE:
            if count > 10:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
        if operation is OperationType.BATCH_UPDATE:
            if count > self._MAX_EPIDEMIC_CHANGES:
                return RiskLevel.CRITICAL
            if count > 20:
                return RiskLevel.HIGH
            if count > 5:
                return RiskLevel.MEDIUM
            return RiskLevel.LOW
        if operation is OperationType.MARK_AUTHORITATIVE:
            return RiskLevel.HIGH
        if operation is OperationType.RECLASSIFY:
            if count > 10:
                return RiskLevel.MEDIUM
            return RiskLevel.LOW
        return RiskLevel.LOW

    def cooling_period(
        self,
        seconds: int | None = None,
        reason: str = "High-risk operation",
        callback: callable | None = None,
    ) -> bool:
        wait = seconds or self._QUIET_PERIOD_SECONDS
        logger.warning("SAFETY BRAKE: %d-second cooling for: %s", wait, reason)
        print(f"\n{'=' * 60}")
        print(f"  SAFETY BRAKE ENGAGED — {reason}")
        print(f"  Cooling period: {wait} seconds")
        print("  Press Ctrl+C to abort.")
        print(f"{'=' * 60}\n")

        try:
            for remaining in range(wait, 0, -1):
                if callback:
                    callback(remaining)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n  OPERATION ABORTED BY USER.")
            return False

        print("\n  Cooling period completed. Proceeding...\n")
        return True

    def devils_advocate(
        self,
        claim: str,
        evidence_for: list[str] = None,
        evidence_against: list[str] = None,
    ) -> dict:
        result = {
            "claim": claim,
            "timestamp": datetime.now(UTC).isoformat(),
            "for_count": len(evidence_for) if evidence_for else 0,
            "against_count": len(evidence_against) if evidence_against else 0,
            "verdict": "undecided",
        }
        for_count = len(evidence_for) if evidence_for else 0
        against_count = len(evidence_against) if evidence_against else 0
        if against_count > for_count:
            result["verdict"] = "rejected"
            result["reason"] = f"Evidence against ({against_count}) outweighs evidence for ({for_count})"
        elif for_count > against_count:
            result["verdict"] = "accepted"
            result["reason"] = f"Evidence for ({for_count}) outweighs evidence against ({against_count})"
        elif for_count == 0 and against_count == 0:
            result["verdict"] = "insufficient_evidence"
            result["reason"] = "No evidence provided for either side"
        else:
            result["verdict"] = "tied"
            result["reason"] = "Equal evidence on both sides — requires human judgment"
        return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KB Safety Brake")
    sub = parser.add_subparsers(dest="cmd")

    pf = sub.add_parser("pre-flight", help="Run pre-flight check")
    pf.add_argument("operation", choices=[o.value for o in OperationType], help="Operation type")
    pf.add_argument("--count", type=int, default=1, help="Affected KE count")

    da = sub.add_parser("devils-advocate", help="Run devil's advocate check")
    da.add_argument("claim", help="The claim to evaluate")

    args = parser.parse_args()
    sb = SafetyBrake()

    if args.cmd == "pre-flight":
        op = OperationType(args.operation)
        result = sb.pre_flight_check(op, affected_ke_count=args.count)
        print(f"Pre-Flight: {result.risk_level.value.upper()} risk — {'PASS' if result.passed else 'BLOCKED'}")
        print(f"  Operation: {result.operation}")
        print(f"  Affected:  {result.affected_ke_count} KEs")
        print(f"  Cooling:   {result.cooling_period_seconds}s")
        print(f"  Devil's Advocate: {'required' if result.devils_advocate_required else 'not required'}")
        if result.blocking_issues:
            print("  BLOCKING:")
            for b in result.blocking_issues:
                print(f"    - {b}")
        if result.warnings:
            print("  WARNINGS:")
            for w in result.warnings:
                print(f"    - {w}")
        if not result.passed:
            import sys

            sys.exit(1)
        return

    if args.cmd == "devils-advocate":
        result = sb.devils_advocate(args.claim)
        print(f"Devil's Advocate: {result['verdict'].upper()}")
        print(f"  Claim:  {result['claim']}")
        print(f"  For:    {result['for_count']} evidences")
        print(f"  Against: {result['against_count']} evidences")
        print(f"  Reason: {result.get('reason', '')}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
