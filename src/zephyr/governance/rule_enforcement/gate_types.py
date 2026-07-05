# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.gate_types
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS] zephyr.governance.rule_enforcement.gate_engine; zephyr.knowledge.kb.pipeline.triage; zephyr.knowledge.kb.pipeline.ingest; zephyr.knowledge.kb.pipeline.extract; zephyr.knowledge.kb.pipeline.activate; zephyr.knowledge.kb.pipeline.analyze; zephyr.shared.contracts.core.gate_types; zephyr.governance.rule_enforcement.gate_types
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_gate_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from zephyr.integration.shared.schema.schemas import Priority

__all__ = [
    "GateEngineError",
    "GateResult",
    "GateViolation",
    "GateViolationError",
]


@dataclass
class GateViolation:
    check_id: str
    check_name: str
    severity: str
    message: str
    detail: str | None = None
    rule_ids: list[str] = field(default_factory=list)


@dataclass
class GateResult:
    gate_id: str
    task_id: str
    passed: bool
    violations: list[GateViolation] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    evaluated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    rule_ids: list[str] = field(default_factory=list)

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
        return f"[FAIL] Gate {self.gate_id} task={self.task_id} violations={total} (P0={p0})"


class GateEngineError(RuntimeError):
    pass


class GateViolationError(GateEngineError):
    def __init__(self, result: GateResult) -> None:
        self.result = result
        super().__init__(result.summary())
