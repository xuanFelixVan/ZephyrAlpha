# [A_test] module_id: MOD-GOV_strategy_portfolio | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-435 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_strategy_portfolio
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.financial_governance.strategy_portfolio import (
    RetirementTrigger,
    StrategyMethod,
    estimate_capacity,
)


class TestStrategyMethod:
    def test_enum_values(self):
        assert StrategyMethod.ONE_OVER_N == "1/N"
        assert StrategyMethod.RISK_PARITY == "RiskParity"
        assert StrategyMethod.KELLY == "Kelly"
        assert StrategyMethod.MAX_DD_LIMIT == "MaxDDLimit"

    def test_enum_members_count(self):
        assert len(StrategyMethod) == 4


class TestRetirementTrigger:
    def test_enum_values(self):
        assert RetirementTrigger.SHARPE_12M_NEGATIVE == "Sharpe 12m < 0"
        assert RetirementTrigger.CALMAR_12M_LOW == "Calmar 12m < 0.3"
        assert RetirementTrigger.SIX_MONTH_NEGATIVE == "6-month consecutive negative"

    def test_enum_members_count(self):
        assert len(RetirementTrigger) == 3


class TestEstimateCapacity:
    def test_basic_calculation(self):
        result = estimate_capacity(
            max_vol=1_000_000_000,
            signal_decay=50_000_000,
            liq_util=0.1,
            impact_ratio=0.5,
        )
        assert result > 0

    def test_result_uses_min_of_decay_and_liq(self):
        result = estimate_capacity(
            max_vol=1_000_000_000,
            signal_decay=50_000_000,
            liq_util=0.1,
            impact_ratio=0.5,
        )
        expected = min(50_000_000, 0.1 * 0.5) * max(10_000_000, 1_000_000_000)
        assert result == expected

    def test_large_max_vol_uses_max_vol(self):
        result = estimate_capacity(
            max_vol=100_000_000_000,
            signal_decay=5_000_000,
            liq_util=1.0,
            impact_ratio=1.0,
        )
        assert result == min(5_000_000, 1.0) * 100_000_000_000

    def test_zero_liq_util(self):
        result = estimate_capacity(
            max_vol=1_000_000_000,
            signal_decay=50_000_000,
            liq_util=0.0,
            impact_ratio=0.5,
        )
        assert result == 0.0

    def test_result_is_float(self):
        result = estimate_capacity(1e9, 5e7, 0.1, 0.5)
        assert isinstance(result, float)
