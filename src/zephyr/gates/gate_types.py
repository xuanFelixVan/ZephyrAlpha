# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.gates.gate_types

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] zephyr.gates.gate_engine; zephyr.kb.pipeline.triage; zephyr.kb.pipeline.ingest; zephyr.kb.pipeline.extract; zephyr.kb.pipeline.activate; zephyr.kb.pipeline.analyze; zephyr.shared.contracts.core.gate_types; zephyr.shared.contracts.gate

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from zephyr.shared.schema.schemas import Priority

__all__ = [
    "GateViolation",
    "GateResult",
    "GateEngineError",
    "GateViolationError",
]


@dataclass
class GateViolation:
    check_id: str
    check_name: str
    severity: str
    message: str
    detail: str | None = None


@dataclass
class GateResult:
    gate_id: str
    task_id: str
    passed: bool
    violations: list[GateViolation] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    evaluated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def p0_violations(self) -> list[GateViolation]:
        return [v for v in self.violations if v.severity == Priority.P0.value]

    @property
    def has_p0(self) -> bool:
        return bool(self.p0_violations)

    def summary(self) -> str:
        if self.passed:
            return f"[PASS] Gate {self.gate_id} task={self.task_id}"
        p0 = len(self.p0_violations)
        total = len(self.violations)
        return f"[FAIL] Gate {self.gate_id} task={self.task_id} " f"violations={total} (P0={p0})"


class GateEngineError(RuntimeError):
    pass


class GateViolationError(GateEngineError):
    def __init__(self, result: GateResult) -> None:
        self.result = result
        super().__init__(result.summary())
