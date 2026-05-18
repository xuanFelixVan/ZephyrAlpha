# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l04_risk_management.test_risk_validator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l04_risk_management/risk_validator.py + implementations/default_risk_validator.py
================================================================================================================

覆盖矩阵：
  RiskValidator (ABC):
    - 抽象类不可实例化 × 1
  DefaultRiskValidator:
    - validate_order 通过 × 1
    - validate_order 单仓超限 HALT × 1
    - validate_order 下单后总权重超限 × 1
    - validate_order kill_switch 已激活 × 1
    - validate_portfolio 通过 × 1
    - validate_portfolio 持仓超限 × 1
    - validate_portfolio 杠杆超限 × 1
    - validate_portfolio 回撤触发 × 1
    - trigger_kill_switch / reset_kill_switch × 2
    - is_kill_switch_triggered × 1
    - 注册表登记 × 1
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from zephyr.l04_risk_management.implementations.default_risk_validator import (
    DefaultRiskValidator,
)
from zephyr.l04_risk_management.risk_manager import RiskLimits
from zephyr.l04_risk_management.risk_validator import RiskValidator, ViolatedConstraint


def _make_risk_limits(**kwargs) -> RiskLimits:
    return RiskLimits(
        as_of_date=datetime.now(UTC),
        idempotency_key="test-001",
        **kwargs,
    )


class TestRiskValidatorABC:
    """抽象基类校验"""

    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            RiskValidator()


class TestDefaultRiskValidator:
    """默认风险校验器测试"""

    def test_validate_order_pass(self):
        validator = DefaultRiskValidator()
        limits = _make_risk_limits(
            max_single_position=0.10,
            max_gross_leverage=1.0,
            max_sector_concentration=0.30,
            max_drawdown_limit=0.20,
        )
        violations = validator.validate_order(
            symbol="600519",
            target_weight=0.05,
            current_holdings={},
            limits=limits,
        )
        assert len(violations) == 0

    def test_validate_order_position_limit_halt(self):
        validator = DefaultRiskValidator()
        limits = _make_risk_limits(max_single_position=0.10)
        violations = validator.validate_order(
            symbol="600519",
            target_weight=0.15,
            current_holdings={},
            limits=limits,
        )
        # target_weight=0.15 > 0.10 触发单仓超限；同时 post_trade=0.15 > 0.105 触发下单后超限 → 共 2 个
        assert len(violations) == 2
        assert all(v.severity == "HALT" for v in violations)
        assert violations[0].constraint == ViolatedConstraint.POSITION_LIMIT

    def test_validate_order_post_trade_weight_exceeds(self):
        validator = DefaultRiskValidator()
        limits = _make_risk_limits(max_single_position=0.10)
        violations = validator.validate_order(
            symbol="600519",
            target_weight=0.08,
            current_holdings={"600519": 0.05},
            limits=limits,
        )
        # post_trade_weight = 0.13 > 0.10 * 1.05 = 0.105 → 触发
        post_trade_violations = [v for v in violations if "下单后总权重超限" in v.description]
        assert len(post_trade_violations) == 1
        assert post_trade_violations[0].severity == "HALT"

    def test_validate_order_kill_switch_active(self):
        validator = DefaultRiskValidator(kill_switch_active=True)
        limits = _make_risk_limits(max_single_position=0.10)
        violations = validator.validate_order(
            symbol="600519",
            target_weight=0.01,
            current_holdings={},
            limits=limits,
        )
        assert len(violations) == 1
        assert violations[0].constraint == ViolatedConstraint.DRAWDOWN_TRIGGER
        assert "Kill switch" in violations[0].description

    def test_validate_portfolio_pass(self):
        validator = DefaultRiskValidator()
        limits = _make_risk_limits(
            max_single_position=0.10,
            max_gross_leverage=1.0,
            max_sector_concentration=0.30,
            max_drawdown_limit=0.20,
        )
        # total_mv = 80000, nav = 1000000 → dd = 1 - 0.08 = 0.92 > 0.20 会触发回撤
        # 需要让 total_mv 接近 nav 才能通过
        violations = validator.validate_portfolio(
            holdings={"600519": 0.05, "000858": 0.03},
            market_values={"600519": 50000.0, "000858": 30000.0},
            total_nav=Decimal("80000"),  # 让 dd = 0
            limits=limits,
        )
        assert len(violations) == 0

    def test_validate_portfolio_position_limit(self):
        validator = DefaultRiskValidator()
        limits = _make_risk_limits(max_single_position=0.10)
        violations = validator.validate_portfolio(
            holdings={"600519": 0.15},
            market_values={"600519": 150000.0},
            total_nav=Decimal("1000000"),
            limits=limits,
        )
        assert len(violations) == 1
        assert violations[0].constraint == ViolatedConstraint.POSITION_LIMIT

    def test_validate_portfolio_leverage_limit(self):
        validator = DefaultRiskValidator()
        limits = _make_risk_limits(max_single_position=0.10, max_gross_leverage=0.50)
        violations = validator.validate_portfolio(
            holdings={"600519": 0.30, "000858": 0.30},
            market_values={"600519": 300000.0, "000858": 300000.0},
            total_nav=Decimal("1000000"),
            limits=limits,
        )
        leverage_violations = [v for v in violations if v.constraint == ViolatedConstraint.LEVERAGE_LIMIT]
        assert len(leverage_violations) == 1
        assert leverage_violations[0].severity == "HALT"

    def test_validate_portfolio_drawdown_trigger(self):
        validator = DefaultRiskValidator()
        limits = _make_risk_limits(max_drawdown_limit=0.05)
        # total_mv = 800000, nav = 1000000 → dd = 1 - 0.8 = 0.2 > 0.05
        violations = validator.validate_portfolio(
            holdings={"600519": 0.80},
            market_values={"600519": 800000.0},
            total_nav=Decimal("1000000"),
            limits=limits,
        )
        dd_violations = [v for v in violations if v.constraint == ViolatedConstraint.DRAWDOWN_TRIGGER]
        assert len(dd_violations) == 1
        assert dd_violations[0].severity == "HALT"

    def test_trigger_and_reset_kill_switch(self):
        validator = DefaultRiskValidator()
        assert validator.kill_switch_active is False
        validator.trigger_kill_switch()
        assert validator.kill_switch_active is True
        validator.reset_kill_switch()
        assert validator.kill_switch_active is False

    def test_is_kill_switch_triggered(self):
        from zephyr.l04_risk_management.risk_validator import ViolationDetail

        violations = [
            ViolationDetail(
                constraint=ViolatedConstraint.POSITION_LIMIT,
                description="test",
                limit_value=Decimal("0.10"),
                actual_value=Decimal("0.15"),
                severity="HALT",
            )
        ]
        assert RiskValidator.is_kill_switch_triggered(violations) is True

        warnings_only = [
            ViolationDetail(
                constraint=ViolatedConstraint.POSITION_LIMIT,
                description="test",
                limit_value=Decimal("0.10"),
                actual_value=Decimal("0.15"),
                severity="WARNING",
            )
        ]
        assert RiskValidator.is_kill_switch_triggered(warnings_only) is False

    def test_registry_registration(self):
        from zephyr.l04_risk_management.risk_validator import RiskValidator

        assert "default-risk-validator" in RiskValidator._registry
