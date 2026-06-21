# [A_module] module_id=MOD-SHR_combinatorial_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
        if operation == CombineOp.OR:
            return self.evaluate_or(checks)
        return self.evaluate_and(checks)
