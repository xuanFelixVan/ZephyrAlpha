# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l04_risk_management.test_risk_limits
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l04_risk_management/risk_limits.py + implementations/default_risk_limits_calculator.py
=============================================================================================================

覆盖矩阵：
  RiskLimitsCalculator (ABC):
    - 抽象类不可实例化 × 1
  DefaultRiskLimitsCalculator:
    - calculate 基本路径 × 1
    - calculate 含 factor_signals IV 调整 × 1
    - calculate 空持仓 × 1
    - _estimate_var 集中度分档 × 3
    - 注册表登记 × 1
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from zephyr.l04_risk_management.implementations.default_risk_limits_calculator import (
    DefaultRiskLimitsCalculator,
)
from zephyr.l04_risk_management.risk_limits import RiskLimitsCalculator
from zephyr.trading_contracts.risk.risk_limits import RiskLimits


def _make_risk_limits(**kwargs) -> RiskLimits:
    return RiskLimits(
        as_of_date=datetime.now(UTC),
        idempotency_key="test-001",
        **kwargs,
    )


class TestRiskLimitsCalculatorABC:
    """抽象基类校验"""

    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            RiskLimitsCalculator()


class TestDefaultRiskLimitsCalculator:
    """默认风险限额计算器测试"""

    def test_calculate_basic(self):
        calc = DefaultRiskLimitsCalculator()
        limits = calc.calculate(
            positions={"600519": 0.05, "000858": 0.03},
            market_values={"600519": 50000.0, "000858": 30000.0},
            total_nav=Decimal("1000000"),
        )
        assert isinstance(limits, RiskLimits)
        assert limits.max_single_position == pytest.approx(0.10)
        assert limits.max_gross_leverage == pytest.approx(1.0)
        assert limits.max_sector_concentration == pytest.approx(0.30)
        assert limits.max_drawdown_limit == pytest.approx(0.20)
        assert limits.symbol_overrides == {}

    def test_calculate_with_unstable_signals_iv_adjustment(self):
        calc = DefaultRiskLimitsCalculator(max_single_position=0.10)
        # 构造不稳定信号（绝对值 > 3.0）
        signals = {"600519": 4.0, "000858": -5.0}
        limits = calc.calculate(
            positions={"600519": 0.05},
            market_values={"600519": 50000.0},
            total_nav=Decimal("1000000"),
            factor_signals=signals,
        )
        # 2 个不稳定信号 → adjustment = max(0.5, 1.0 - 2*0.1) = 0.8
        assert limits.max_single_position == pytest.approx(0.08)

    def test_calculate_empty_positions(self):
        calc = DefaultRiskLimitsCalculator()
        limits = calc.calculate(
            positions={},
            market_values={},
            total_nav=Decimal("1000000"),
        )
        assert limits.max_single_position == pytest.approx(0.10)

    def test_estimate_var_high_concentration(self):
        calc = DefaultRiskLimitsCalculator()
        var = calc._estimate_var({"a": 600000.0}, Decimal("1000000"))
        # 集中度 0.6, position_count=1 <=2 → 0.6 * 0.05 = 0.03
        assert var == pytest.approx(Decimal("0.03"))

    def test_estimate_var_medium_concentration(self):
        calc = DefaultRiskLimitsCalculator()
        var = calc._estimate_var(
            {"a": 200000.0, "b": 200000.0, "c": 200000.0},
            Decimal("1000000"),
        )
        # 集中度 0.2, position_count=3 <=5 → 0.2 * 0.03 = 0.006
        assert var == pytest.approx(Decimal("0.006"))

    def test_estimate_var_low_concentration(self):
        calc = DefaultRiskLimitsCalculator()
        var = calc._estimate_var(
            {"a": 100000.0, "b": 100000.0, "c": 100000.0, "d": 100000.0, "e": 100000.0, "f": 100000.0},
            Decimal("1000000"),
        )
        # 集中度 0.1, position_count=6 >5 → 0.1 * 0.02 = 0.002
        assert var == pytest.approx(Decimal("0.002"))

    def test_registry_registration(self):
        from zephyr.l04_risk_management.risk_limits import RiskLimitsCalculator

        assert "default-risk-limits-calculator" in RiskLimitsCalculator._registry


class TestRiskLimitsDataclass:
    """RiskLimits 契约类型测试"""

    def test_risk_limits_creation(self):
        limits = _make_risk_limits(
            max_single_position=0.10,
            max_gross_leverage=1.0,
            max_sector_concentration=0.30,
            max_portfolio_var_1d=0.02,
            max_drawdown_limit=0.20,
            symbol_overrides={"600519": 0.15},
        )
        assert limits.max_single_position == pytest.approx(0.10)
        assert limits.symbol_overrides.get("600519") == pytest.approx(0.15)
