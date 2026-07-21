# [A_test] module_id: MOD-GOV_e_strategy_portfolio | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_strategy_portfolio
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.financial_governance.strategy_portfolio import (
    RetirementTrigger,
    StrategyMethod,
    estimate_capacity,
)


class TestStrategyMethod:
    def test_has_four_members(self):
        assert len(StrategyMethod) == 4

    def test_correct_values(self):
        assert StrategyMethod.ONE_OVER_N.value == "1/N"
        assert StrategyMethod.RISK_PARITY.value == "RiskParity"
        assert StrategyMethod.KELLY.value == "Kelly"
        assert StrategyMethod.MAX_DD_LIMIT.value == "MaxDDLimit"


class TestRetirementTrigger:
    def test_has_three_members(self):
        assert len(RetirementTrigger) == 3

    def test_correct_values(self):
        assert RetirementTrigger.SHARPE_12M_NEGATIVE.value == "Sharpe 12m < 0"
        assert RetirementTrigger.CALMAR_12M_LOW.value == "Calmar 12m < 0.3"
        assert RetirementTrigger.SIX_MONTH_NEGATIVE.value == "6-month consecutive negative"


class TestEstimateCapacity:
    def test_returns_float(self):
        result = estimate_capacity(1_000_000, 0.8, 0.6, 0.5)
        assert isinstance(result, float)

    def test_signal_decay_smaller(self):
        result = estimate_capacity(5_000_000, 0.3, 0.8, 0.6)
        assert result == pytest.approx(0.3 * 10_000_000)

    def test_liq_util_product_smaller(self):
        result = estimate_capacity(5_000_000, 0.9, 0.4, 0.5)
        assert result == pytest.approx(0.4 * 0.5 * 10_000_000)

    def test_max_vol_below_10m_floor(self):
        result = estimate_capacity(1_000_000, 0.5, 0.5, 0.8)
        assert result == pytest.approx(min(0.5, 0.5 * 0.8) * 10_000_000)

    def test_max_vol_above_10m(self):
        result = estimate_capacity(50_000_000, 0.5, 0.5, 0.8)
        assert result == pytest.approx(min(0.5, 0.5 * 0.8) * 50_000_000)

    def test_zero_values(self):
        result = estimate_capacity(0, 0, 0, 0)
        assert result == 0.0

    def test_large_values(self):
        result = estimate_capacity(100_000_000.0, 1.0, 1.0, 1.0)
        assert result == pytest.approx(100_000_000.0)
