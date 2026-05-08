"""
CTR-ERR-004: RiskLimitViolationError / 风险限额突破错误

L04 检测到当前或计划操作将突破风险限额时抛出的硬错误。L05/L06 MUST 据此阻止订单生成和执行。

SSoT: cross-layer-contracts.yaml → CTR-ERR-004
"""

from __future__ import annotations

from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext


class RiskLimitViolationError(Exception):
    """HALT 级别异常：组合或单笔委托突破风险限额（CTR-ERR-004）。"""

    __slots__ = (
        "actual_value",
        "error_id",
        "idempotency_key",
        "limit_value",
        "portfolio_id",
        "recovery_hint",
        "violated_constraint",
        "violation_detail",
        "schema_version",
        "trace_context",
    )

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
        trace_context: Optional[TraceContext] = None,
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
