# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.gate_types
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.shared.schema.schemas
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement.gate_engine; zephyr.shared.contracts.core.gate_types; zephyr.gov_enforcement.rule_enforcement.gate_types
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
门禁类型定义——GateType 枚举与 gate 相关 dataclass（GateContext/GateResult 等）。

定义门禁系统的类型契约，供 gate_engine / gate_pipeline / gate_simulator 共用。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gate_types.py
# 层: 算法
# - id: A1
#   name_zh: ① GateResult
#   name_en: GateResult
#   intro: class GateResult 源码 L77-L99
#   desc: 公共方法（定义序）: p0_violations, has_p0, summary；源码 L77-L99
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: GateResult
#   downstream: zephyr.gov_enforcement.rule_enforcement.gate_engine; zephyr.shared.contracts.co…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from zephyr.shared.schema.schemas import Priority

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
    error_code = "ZA-GV-0041"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class GateViolationError(GateEngineError):
    error_code = "ZA-GV-0042"

    def __init__(self, result: GateResult, *, error_code: str | None = None) -> None:
        self.result = result
        super().__init__(result.summary())
        if error_code is not None:
            self.error_code = error_code
