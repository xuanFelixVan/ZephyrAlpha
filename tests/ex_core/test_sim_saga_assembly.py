# [BLUEPRINT] MOD-EX-057 | docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md
# [MODULE] tests.ex_core.test_sim_saga_assembly
# [DOMAIN] D_EX_CORE
# [TTL] permanent
"""build_sim_saga 装配入口测试 — F53 夜战批（mock 不实连，零生产 data/ 写入）

覆盖:
    env 守卫: 非 sim 拒绝（fail-closed）
    装配完整性: 五合规件注入 / broker 注册 / 监视器 attach / 注册表接线
    端到端: 模拟单全流程成功 + 补偿注册表动作在失败态触发（tmp_path 审计落盘）
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.saga_compensation_registry import CompensationAction
from zephyr.ex_core.sim_saga_assembly import (
    SIM_ENV,
    SimAssemblyEnvError,
    SimSagaDeps,
    build_sim_saga,
    submit_sim_order,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order


def _make_order(symbol: str = "000001.SZ", nonce: int = 1) -> Order:
    from datetime import UTC, datetime

    from zephyr.shared.contracts.enums.order_enums import OrderStatus

    return Order(
        order_id=f"sim-{symbol}-{nonce}",
        symbol=symbol,
        strategy_id="test-sim",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("10.00"),
        status=OrderStatus.PENDING,
        created_at=datetime.now(UTC),
        idempotency_key=f"sim-key-{nonce}",
    )


class TestEnvGuard:
    def test_live_rejected(self):
        with pytest.raises(SimAssemblyEnvError, match="OWNER-GATE"):
            build_sim_saga(environment="live")

    def test_prod_rejected(self):
        with pytest.raises(SimAssemblyEnvError):
            build_sim_saga(environment="prod")

    def test_paper_rejected(self):
        with pytest.raises(SimAssemblyEnvError):
            build_sim_saga(environment="paper")

    def test_sim_accepted(self):
        stack = build_sim_saga(environment=SIM_ENV)
        assert stack.broker_id == "simulation"

    def test_default_is_sim(self):
        stack = build_sim_saga()
        assert stack.broker.broker_id == "simulation"


class TestAssemblyIntegrity:
    def test_five_gates_injected(self):
        """F62 同口径：OrderManager 五合规件零裸构造。"""
        stack = build_sim_saga()
        om = stack.order_manager
        assert om._report_gate is not None  # noqa: SLF001 — 门注入断言走装配私有面
        assert om.declaration_guard is not None
        assert om.manipulation_monitor is not None
        assert om._registration_guard is not None  # noqa: SLF001
        assert om._avoidance_detector is not None  # noqa: SLF001

    def test_broker_registered_and_wired(self):
        stack = build_sim_saga()
        assert stack.order_manager._brokers["simulation"] is stack.broker  # noqa: SLF001
        assert stack.saga is not None

    def test_compensation_registry_wired(self):
        stack = build_sim_saga()
        assert stack.compensation_registry is not None
        assert stack.compensation_registry.registered_steps == ()

    def test_audit_logger_persist_path(self, tmp_path):
        from zephyr.ex_core.audit_journal.auditor import ExecutionAuditLogger

        audit = ExecutionAuditLogger(persist_path=tmp_path / "audit.jsonl")
        stack = build_sim_saga(deps=SimSagaDeps(audit_logger=audit))
        assert stack.audit_logger is audit

    def test_state_dir_passthrough(self, tmp_path):
        """state_dir 透传 DefaultRiskValidator（测试零生产 data/ 写入）。"""
        stack = build_sim_saga(deps=SimSagaDeps(state_dir=tmp_path / "risk_state"))
        assert stack.risk_validator is not None


class TestEndToEndSim:
    def test_full_success_run(self):
        """模拟单全流程：六步走完 COMPLETED，持仓入账。"""
        stack = build_sim_saga()
        result = submit_sim_order(stack, _make_order(nonce=2), OrderSide.BUY)
        assert result.state.value == "COMPLETED"
        assert result.fill is not None
        assert result.compensated is False

    def test_registry_action_triggers_on_step5_failure(self, tmp_path):
        """失败态：注册表动作在内建补偿后触发（tmp_path 审计落盘，不写生产 data/）。"""
        from zephyr.ex_core.audit_journal.auditor import ExecutionAuditLogger

        calls: list[str] = []
        stack = build_sim_saga(
            deps=SimSagaDeps(audit_logger=ExecutionAuditLogger(persist_path=tmp_path / "audit.jsonl")),
        )
        stack.compensation_registry.register(
            "order_submit",
            CompensationAction("release_reserved", lambda ctx: calls.append(ctx.order_id)),
        )
        # 爆破 step5：首笔入账抛异常
        tracker = stack.position_tracker

        class _BoomTracker(type(tracker)):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                self.calls = 0

            def apply_fill(self, fill, side):
                self.calls += 1
                if self.calls == 1:
                    raise RuntimeError("boom")
                return super().apply_fill(fill, side)

        boom = _BoomTracker(initial_cash=Decimal("1000000"), portfolio_id="boom")
        # 换上爆破 tracker（直接替换栈组件属测试专用；生产路径经 build 装配）
        stack.saga._position_tracker = boom  # noqa: SLF001 — 测试注入点
        result = submit_sim_order(stack, _make_order(nonce=3), OrderSide.BUY)
        assert result.compensated is True
        # 注册表动作收到的是 OrderManager 注册后的真实 order_id（UUID），与 result 一致
        assert calls == [result.order_id]
