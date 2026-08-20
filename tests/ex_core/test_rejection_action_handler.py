# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_rejection_action_handler
# [DOMAIN] D_EX_CORE
# [INVARIANTS] 每单至多重试1次; 冻结表只增人工解冻; 注入缺失降级放弃; 分类真源复用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRejectionActionInputError
# [TESTS] self
# [TTL] permanent
"""拒单分类动作执行器测试（40 号 §6.1 gap 4，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.order_manager import RejectionAction
from zephyr.ex_core.rejection_action_handler import (
    InvalidRejectionActionInputError,
    RejectionActionExecutor,
    RejectionOutcome,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order


def _order(order_id: str = "o1", strategy: str = "S1", broker_order_id: str | None = None) -> Order:
    return Order(
        idempotency_key=f"idem-{order_id}",
        order_id=order_id,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        side=OrderSide.BUY,
        strategy_id=strategy,
        symbol="600000",
        limit_price=Decimal("10.00"),
        broker_order_id=broker_order_id,
        created_at=datetime(2026, 8, 20, 10, 0, tzinfo=UTC),
    )


class TestRetryOnce:
    def test_first_rejection_retries(self):
        calls: list[str] = []
        executor = RejectionActionExecutor(retry_fn=lambda order, err: calls.append(order.order_id) or "bo-1")
        result = executor.execute(RejectionAction.RETRY_ONCE, _order())
        assert result.outcome is RejectionOutcome.RETRIED
        assert result.broker_order_id == "bo-1"
        assert calls == ["o1"]

    def test_second_rejection_abandons(self):
        executor = RejectionActionExecutor(retry_fn=lambda order, err: "bo-1")
        order = _order()
        executor.execute(RejectionAction.RETRY_ONCE, order)
        result = executor.execute(RejectionAction.RETRY_ONCE, order)
        assert result.outcome is RejectionOutcome.ABANDONED
        assert result.detail == "retry exhausted"

    def test_missing_retry_fn_degrades(self):
        executor = RejectionActionExecutor()
        result = executor.execute(RejectionAction.RETRY_ONCE, _order())
        assert result.outcome is RejectionOutcome.DEGRADED_ABANDONED

    def test_retry_fn_exception_propagates_to_caller(self):
        # 重试执行器自身异常不在本层吞（由 Saga/会话层接管补偿）
        def _boom(order, err):
            raise RuntimeError("broker still down")

        executor = RejectionActionExecutor(retry_fn=_boom)
        with pytest.raises(RuntimeError):
            executor.execute(RejectionAction.RETRY_ONCE, _order())


class TestAlertFreeze:
    def test_freeze_strategy_and_alert(self):
        alerts: list[tuple[str, dict]] = []
        executor = RejectionActionExecutor(alert_sink=lambda m, c: alerts.append((m, c)))
        result = executor.execute(RejectionAction.ALERT_FREEZE, _order(strategy="S1"))
        assert result.outcome is RejectionOutcome.FROZEN
        assert result.frozen_strategy_id == "S1"
        assert executor.is_strategy_frozen("S1") is True
        assert executor.is_strategy_frozen("S2") is False
        assert len(alerts) == 1 and "冻结" in alerts[0][0]

    def test_manual_unfreeze(self):
        executor = RejectionActionExecutor()
        executor.execute(RejectionAction.ALERT_FREEZE, _order(strategy="S1"))
        assert executor.unfreeze_strategy("S1") is True
        assert executor.is_strategy_frozen("S1") is False
        assert executor.unfreeze_strategy("S1") is False  # 二次解冻幂等 False

    def test_frozen_set_snapshot_readonly(self):
        executor = RejectionActionExecutor()
        executor.execute(RejectionAction.ALERT_FREEZE, _order(strategy="S1"))
        assert executor.frozen_strategies == frozenset({"S1"})

    def test_alert_sink_failure_swallowed(self):
        def _bad_sink(m, c):
            raise RuntimeError("alert down")

        executor = RejectionActionExecutor(alert_sink=_bad_sink)
        result = executor.execute(RejectionAction.ALERT_FREEZE, _order())
        assert result.outcome is RejectionOutcome.FROZEN  # 告警故障不阻断冻结


class TestAlertReconcile:
    def test_reconcile_trigger_invoked(self):
        triggered: list[tuple[str, str]] = []
        executor = RejectionActionExecutor(reconcile_trigger=lambda sid, sym: triggered.append((sid, sym)))
        result = executor.execute(RejectionAction.ALERT_RECONCILE, _order(strategy="S1"))
        assert result.outcome is RejectionOutcome.RECONCILE_TRIGGERED
        assert triggered == [("S1", "600000")]

    def test_missing_trigger_degrades(self):
        executor = RejectionActionExecutor()
        result = executor.execute(RejectionAction.ALERT_RECONCILE, _order())
        assert result.outcome is RejectionOutcome.DEGRADED_ABANDONED


class TestOtherActions:
    def test_abandon(self):
        executor = RejectionActionExecutor()
        result = executor.execute(RejectionAction.ABANDON, _order())
        assert result.outcome is RejectionOutcome.ABANDONED

    def test_idempotent_return(self):
        executor = RejectionActionExecutor()
        result = executor.execute(RejectionAction.IDEMPOTENT_RETURN, _order(broker_order_id="bo-9"))
        assert result.outcome is RejectionOutcome.IDEMPOTENT_RETURNED
        assert result.broker_order_id == "bo-9"


class TestClassifyAndExecute:
    def test_error_code_54_freezes(self):
        executor = RejectionActionExecutor()
        result = executor.classify_and_execute(54, _order(strategy="S1"))
        assert result.action is RejectionAction.ALERT_FREEZE
        assert executor.is_strategy_frozen("S1") is True

    def test_error_code_55_triggers_reconcile(self):
        triggered: list[tuple[str, str]] = []
        executor = RejectionActionExecutor(reconcile_trigger=lambda s, y: triggered.append((s, y)))
        result = executor.classify_and_execute(55, _order())
        assert result.action is RejectionAction.ALERT_RECONCILE
        assert triggered

    def test_error_code_53_retries_once(self):
        executor = RejectionActionExecutor(retry_fn=lambda o, e: "bo-x")
        result = executor.classify_and_execute(53, _order())
        assert result.outcome is RejectionOutcome.RETRIED

    def test_unknown_code_abandons(self):
        executor = RejectionActionExecutor()
        result = executor.classify_and_execute(9999, _order())
        assert result.outcome is RejectionOutcome.ABANDONED


class TestInputValidation:
    def test_missing_order_rejected(self):
        executor = RejectionActionExecutor()
        with pytest.raises(InvalidRejectionActionInputError):
            executor.execute(RejectionAction.ABANDON, None)  # type: ignore[arg-type]
