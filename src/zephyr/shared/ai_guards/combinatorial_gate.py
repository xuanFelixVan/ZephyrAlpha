# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.ai_guards.combinatorial_gate
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.__init__; zephyr.governance.rule_enforcement.gate_engine; tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CombineOp(Enum):
    AND = "and"
    OR = "or"


@dataclass
class GateCheck:
    name: str
    passed: bool
    message: str


@dataclass
class CombinedResult:
    operation: CombineOp
    checks: list[GateCheck]
    passed: bool


GateResult = GateCheck


class CombinatorialGate:
    def evaluate_and(self, checks: list[GateCheck]) -> CombinedResult:
        passed = all(c.passed for c in checks)
        return CombinedResult(CombineOp.AND, checks, passed)

    def evaluate_or(self, checks: list[GateCheck]) -> CombinedResult:
        passed = any(c.passed for c in checks)
        return CombinedResult(CombineOp.OR, checks, passed)

    def evaluate(self, checks: list[GateCheck], operation: CombineOp = CombineOp.AND) -> CombinedResult:
        if operation is CombineOp.OR:
            return self.evaluate_or(checks)
        return self.evaluate_and(checks)
