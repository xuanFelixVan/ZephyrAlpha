# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.gate_engine.gate_context
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_gate_context | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""门禁上下文传播——GateContext 构建/序列化/跨模块注入（beta）

v0.2.0: 统一 GateResult 数据模型——GatePipeline 与 GateEngine 共享同一 GateResult。
  - GateResult 同时支持 status: GateStatus (Pipeline 语义) 和 passed: bool (Engine 语义)
  - violations 列表从 GateEngine 原生支持
  - from_engine() 工厂方法桥接 GateEngine 的输出
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Any

logger = logging.getLogger(__name__)


class GateStatus(Enum):
    PASS = auto()
    FAIL = auto()
    SKIP = auto()
    WAIVED = auto()
    ERROR = auto()


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
    status: GateStatus
    reasons: list[str] = field(default_factory=list)
    affected_tasks: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    task_id: str = ""
    violations: list[GateViolation] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == GateStatus.PASS

    @property
    def p0_violations(self) -> list[GateViolation]:
        return [v for v in self.violations if v.severity == "P0"]

    @property
    def has_p0(self) -> bool:
        return bool(self.p0_violations)

    def summary(self) -> str:
        if self.passed:
            return f"[PASS] Gate {self.gate_id} task={self.task_id}"
        p0 = len(self.p0_violations)
        total = len(self.violations)
        return f"[FAIL] Gate {self.gate_id} task={self.task_id} violations={total} (P0={p0})"

    @classmethod
    def from_engine_result(cls, engine_result: Any) -> GateResult:
        if isinstance(engine_result, cls):
            return engine_result
        passed = getattr(engine_result, "passed", False)
        status = GateStatus.PASS if passed else GateStatus.FAIL
        gate_id = getattr(engine_result, "gate_id", "")
        task_id = getattr(engine_result, "task_id", "")
        reasons: list[str] = []
        violations: list[GateViolation] = []
        raw_violations = getattr(engine_result, "violations", None) or []
        for v in raw_violations:
            if isinstance(v, GateViolation):
                violations.append(v)
                reasons.append(v.message)
            elif hasattr(v, "message"):
                violations.append(
                    GateViolation(
                        check_id=getattr(v, "check_id", ""),
                        check_name=getattr(v, "check_name", ""),
                        severity=getattr(v, "severity", "P2"),
                        message=getattr(v, "message", ""),
                        detail=getattr(v, "detail", None),
                    )
                )
                reasons.append(getattr(v, "message", ""))
        details = getattr(engine_result, "details", {}) or {}
        evaluated_at = getattr(engine_result, "evaluated_at", "")
        ts = datetime.now(UTC)
        if evaluated_at:
            try:
                ts = datetime.fromisoformat(evaluated_at)
            except (ValueError, TypeError):
                pass
        return cls(
            gate_id=gate_id,
            status=status,
            reasons=reasons,
            task_id=task_id,
            timestamp=ts,
            violations=violations,
            details=details,
        )


@dataclass
class GateContext:
    session_id: str
    task_id: str | None = None
    layer: str | None = None
    previous_results: list[GateResult] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def serialize(self) -> dict:
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "layer": self.layer,
            "previous_results": [
                {
                    "gate_id": r.gate_id,
                    "status": r.status.name,
                    "passed": r.passed,
                    "reasons": r.reasons,
                    "affected_tasks": r.affected_tasks,
                    "violations": [
                        {
                            "check_id": v.check_id,
                            "severity": v.severity,
                            "message": v.message,
                        }
                        for v in r.violations
                    ],
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.previous_results
            ],
            "metadata": self.metadata,
        }

    @classmethod
    def deserialize(cls, data: dict) -> GateContext:
        return cls(
            session_id=data["session_id"],
            task_id=data.get("task_id"),
            layer=data.get("layer"),
            metadata=data.get("metadata", {}),
        )


__all__ = ["GateContext", "GateResult", "GateStatus", "GateViolation"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
