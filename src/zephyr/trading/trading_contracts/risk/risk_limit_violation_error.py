# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.risk_limit_violation_error
# [DOMAIN] D_TRADING
# [DEPENDENCIES]
# [CONSUMERS] risk; pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_limit_violation_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent


from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.shared.contracts.trace_context import TraceContext  # 5.150.8 修复: 补充类型注解导入


class RiskLimitViolationError(Exception):
    # 5.113.1 修复：删除 __slots__。Exception 基类未声明 __slots__，所有 Exception 子类
    # 实例始终携带 __dict__，__slots__ 的内存优化完全失效，仅给人"已优化"的错觉。
    # 同时解决 5.125.1 WeakRef 兼容性问题（无 __slots__ 则默认支持 __weakref__）。

    error_code = "ZA-TR-0001"

    def __init__(
        self,
        *,
        error_id: str,
        portfolio_id: str,
        violated_constraint: str,
        violation_detail: str,
        limit_value: float,
        actual_value: float,
        recovery_hint: str,
        idempotency_key: str,
        schema_version: str = "1.0",
        trace_context: TraceContext | None = None,
        error_code: str | None = None,
    ) -> None:
        super().__init__(violation_detail)
        self.actual_value = actual_value
        self.error_id = error_id
        self.idempotency_key = idempotency_key
        self.limit_value = limit_value
        self.portfolio_id = portfolio_id
        self.recovery_hint = recovery_hint
        self.violated_constraint = violated_constraint
        self.violation_detail = violation_detail
        self.schema_version = schema_version
        self.trace_context = trace_context
        if error_code is not None:
            self.error_code = error_code
