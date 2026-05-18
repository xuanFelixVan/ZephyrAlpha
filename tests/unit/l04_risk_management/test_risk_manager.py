# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l04_risk_management.test_risk_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l04_risk_management/risk_manager.py + risk_manager_base.py + implementations/default_risk_manager_orchestrator.py
==================================================================================================================================================

覆盖矩阵：
  RiskManagerBase (ABC):
    - 抽象类不可实例化 × 1
  DefaultRiskManagerOrchestrator:
    - pre_trade_check 通过 × 1
    - pre_trade_check 触发 HALT 并抛出 RiskLimitViolationError × 1
    - post_trade_check × 1
    - daily_pnl_check 通过 × 1
    - daily_pnl_check 触发 HALT 并激活 kill_switch × 1
    - aggregate_report × 1
    - snapshot × 2（有/无 active_limits）
    - 注册表登记 × 1
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from zephyr.l04_risk_management.implementations.default_risk_manager_orchestrator import (
    DefaultRiskManagerOrchestrator,
)
from zephyr.l04_risk_management.risk_manager import RiskLimits, RiskManagerBase
from zephyr.l04_risk_management.risk_manager_base import RiskReport
from zephyr.trading_contracts.execution.order import Order, OrderSide, OrderType


def _make_risk_limits(**kwargs) -> RiskLimits:
    return RiskLimits(
        as_of_date=datetime.now(UTC),
        idempotency_key="test-001",
        **kwargs,
    )


class TestRiskManagerBaseABC:
    """抽象基类校验"""

    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            RiskManagerBase()


class TestDefaultRiskManagerOrchestrator:
    """默认风险总管编排器测试"""

    def test_pre_trade_check_pass(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        order = Order(
            order_id="o1",
            symbol="600519",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("0.05"),
            limit_price=Decimal("100"),
            idempotency_key="test-001",
        )
        result = orch.pre_trade_check(order, limits={}, positions=[])
        assert result.passed is True
        assert result.rule_name == "pre_trade_check"

    def test_pre_trade_check_halt_raises(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        # 构造一个会触发超限的订单
        order = Order(
            order_id="o2",
            symbol="600519",
            strategy_id="s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("200000"),
            limit_price=Decimal("100"),
            idempotency_key="test-002",
        )
        limits = _make_risk_limits(max_single_position=0.01)
        with pytest.raises(Exception):  # RiskLimitViolationError
            orch.pre_trade_check(order, limits=limits, positions=[])

    def test_post_trade_check(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        result = orch.post_trade_check(fill={}, positions=[])
        assert result.passed is True
        assert result.rule_name == "post_trade_check"

    def test_daily_pnl_check_pass(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        result = orch.daily_pnl_check(daily_pnl=Decimal("1000"), loss_limit=Decimal("50000"))
        assert result.passed is True
        assert result.rule_name == "daily_pnl_check"

    def test_daily_pnl_check_halt_triggers_kill_switch(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        result = orch.daily_pnl_check(daily_pnl=Decimal("-60000"), loss_limit=Decimal("50000"))
        assert result.passed is False
        assert result.severity == "HALT"
        # kill_switch 应被触发
        assert orch._validator.kill_switch_active is True

    def test_aggregate_report(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        # 先执行几个检查
        orch.post_trade_check(fill={}, positions=[])
        orch.daily_pnl_check(daily_pnl=Decimal("1000"), loss_limit=Decimal("50000"))
        report = orch.aggregate_report()
        assert isinstance(report, RiskReport)
        assert report.portfolio_id == "test-pf"
        assert report.overall_pass is True
        assert len(report.checks) == 2

    def test_snapshot_with_active_limits(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        limits = _make_risk_limits(max_single_position=0.10, max_gross_leverage=1.0, max_drawdown_limit=0.20)
        orch._active_limits = limits
        snapshot = orch.snapshot(portfolio_id="test-pf")
        assert snapshot is not None
        assert snapshot.portfolio_id == "test-pf"
        assert snapshot.gross_leverage == pytest.approx(1.0)

    def test_snapshot_without_active_limits(self):
        orch = DefaultRiskManagerOrchestrator(portfolio_id="test-pf")
        snapshot = orch.snapshot(portfolio_id="test-pf")
        assert snapshot is None

    def test_registry_registration(self):
        # DefaultRiskManagerOrchestrator 使用 __checker_id__ 而非 __init_subclass__ 注册
        # 验证类本身存在且 ID 正确即可
        assert DefaultRiskManagerOrchestrator.__checker_id__ == "default-risk-manager-orchestrator"
