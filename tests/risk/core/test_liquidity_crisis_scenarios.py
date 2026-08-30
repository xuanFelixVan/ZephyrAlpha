# [BLUEPRINT] MOD-RK-047 | docs/03_modules/_domain_risk/liquidity_crisis_scenarios/blueprint.md | §test
# [MODULE] tests.risk.core.test_liquidity_crisis_scenarios
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.liquidity_crisis_scenarios; zephyr.risk.core.stress_test_engine
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_liquidity_crisis_scenarios.py
# [A_test] module_id: MOD-RK-047 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [TTL] task_bound
"""MOD-RK-047 流动性危机情景族单元测试（CAND-RSK-022）。

覆盖：三维情景族（市场枯竭/持仓封死/融资断裂）+ 全员出逃极端情形 +
出场滑点评估（exit_days 复用 MOD-RK-08 口径）+ StressTestEngine 消费集成 +
边界（空持仓/负值/非法配置/地板截断）。全程内存构造，无 DB。
"""

from __future__ import annotations

import math

import pytest

pytest.importorskip(
    "zephyr.risk.core.liquidity_crisis_scenarios",
    reason="liquidity_crisis_scenarios not importable",
)

from zephyr.risk.core.liquidity_crisis_scenarios import (  # noqa: E402
    CrisisPosition,
    InvalidLiquidityScenarioError,
    LiquidityCrisisFamily,
    LiquidityCrisisScenarioConfig,
    build_bank_run_scenario,
    build_funding_break_scenario,
    build_market_dryup_scenario,
    build_position_frozen_scenario,
    run_liquidity_crisis_family,
)
from zephyr.risk.core.stress_test_engine import StressScenarioType, StressTestEngine  # noqa: E402

#: 默认危机半价差 = 0.005（MOD-RK-10 阈值）×4 / 2 = 0.01
_HALF_SPREAD = 0.005 * 4.0 / 2.0


def _positions() -> list[CrisisPosition]:
    return [
        CrisisPosition(symbol="600000.SH", position_value=1_000_000.0, adv_value=100_000_000.0),
        CrisisPosition(symbol="300001.SZ", position_value=500_000.0, adv_value=10_000_000.0, is_limit_down=True),
        CrisisPosition(symbol="688002.SH", position_value=200_000.0, adv_value=5_000_000.0, is_suspended=True),
    ]


class TestScenarioConfig:
    def test_defaults_valid(self):
        cfg = LiquidityCrisisScenarioConfig()
        assert cfg.crisis_spread_multiplier == 4.0
        assert cfg.dryup_adv_discount == 0.3

    def test_invalid_multiplier_raises(self):
        with pytest.raises(InvalidLiquidityScenarioError):
            LiquidityCrisisScenarioConfig(crisis_spread_multiplier=0.5)

    def test_invalid_frozen_days_raises(self):
        with pytest.raises(InvalidLiquidityScenarioError):
            LiquidityCrisisScenarioConfig(frozen_days=0)

    def test_invalid_floor_ratio_raises(self):
        with pytest.raises(InvalidLiquidityScenarioError):
            LiquidityCrisisScenarioConfig(run_adv_floor_ratio=1.5)


class TestMarketDryup:
    def test_uniform_shock(self):
        """市场枯竭：全线 shock = -(0.005×4) = -2%"""
        r = build_market_dryup_scenario(_positions())
        assert r.family is LiquidityCrisisFamily.MARKET_DRYUP
        assert r.scenario.scenario_type is StressScenarioType.HYPOTHETICAL
        assert set(r.scenario.shocks) == {"600000.SH", "300001.SZ", "688002.SH"}
        assert r.scenario.shocks["600000.SH"] == pytest.approx(-0.02)

    def test_slippage_uses_stress_adv(self):
        """出场滑点：exit_days = 持仓/(ADV×0.3×0.10)，滑点 = 半价差×√天数"""
        r = build_market_dryup_scenario(_positions())
        slip = {s.symbol: s for s in r.slippage}["600000.SH"]
        assert slip.exit_days == pytest.approx(1_000_000.0 / 3_000_000.0)
        assert slip.slippage_pct == pytest.approx(_HALF_SPREAD * math.sqrt(1.0 / 3.0))
        assert slip.sellable is True

    def test_zero_adv_slippage_capped(self):
        """ADV=0 → exit_days=inf → 滑点封顶 1.0"""
        pos = [CrisisPosition(symbol="X", position_value=1.0, adv_value=0.0)]
        r = build_market_dryup_scenario(pos)
        assert r.slippage[0].exit_days == float("inf")
        assert r.slippage[0].slippage_pct == 1.0


class TestPositionFrozen:
    def test_limit_down_three_day_shock(self):
        """跌停封死：shock = -10%×3 = -30%，不可卖"""
        r = build_position_frozen_scenario(_positions())
        assert r.family is LiquidityCrisisFamily.POSITION_FROZEN
        assert r.scenario.shocks["300001.SZ"] == pytest.approx(-0.30)
        slip = {s.symbol: s for s in r.slippage}["300001.SZ"]
        assert slip.sellable is False
        assert slip.exit_days == float("inf")
        assert slip.slippage_pct == 1.0

    def test_suspended_single_gap_shock(self):
        """停牌：复牌跳空单日 -10%"""
        r = build_position_frozen_scenario(_positions())
        assert r.scenario.shocks["688002.SH"] == pytest.approx(-0.10)
        assert {s.symbol: s for s in r.slippage}["688002.SH"].sellable is False

    def test_normal_position_zero_shock(self):
        r = build_position_frozen_scenario(_positions())
        assert r.scenario.shocks["600000.SH"] == 0.0

    def test_shock_floor_capped(self):
        """连续封死 20 日 → shock 下限 -0.95 不击穿清零"""
        cfg = LiquidityCrisisScenarioConfig(frozen_days=20)
        pos = [CrisisPosition(symbol="X", position_value=1.0, adv_value=1.0, is_limit_down=True)]
        r = build_position_frozen_scenario(pos, config=cfg)
        assert r.scenario.shocks["X"] == pytest.approx(-0.95)


class TestFundingBreak:
    def test_forced_discount_times_leverage(self):
        """融资断裂：shock = -(10% × 1.5) = -15%"""
        r = build_funding_break_scenario(_positions())
        assert r.family is LiquidityCrisisFamily.FUNDING_BREAK
        assert r.scenario.shocks["600000.SH"] == pytest.approx(-0.15)

    def test_leverage_floor_capped(self):
        """杠杆 20× → shock 下限 -0.95"""
        r = build_funding_break_scenario(_positions(), leverage_ratio=20.0)
        assert r.scenario.shocks["600000.SH"] == pytest.approx(-0.95)

    def test_invalid_leverage_raises(self):
        with pytest.raises(InvalidLiquidityScenarioError):
            build_funding_break_scenario(_positions(), leverage_ratio=0.5)


class TestBankRun:
    def test_worst_of_families(self):
        """全员出逃：正常持仓 = 枯竭+断裂叠加 -17%；封死持仓取封死 -30%"""
        r = build_bank_run_scenario(_positions())
        assert r.family is LiquidityCrisisFamily.BANK_RUN
        assert r.scenario.shocks["600000.SH"] == pytest.approx(-0.17)
        assert r.scenario.shocks["300001.SZ"] == pytest.approx(-0.30)
        assert r.scenario.shocks["688002.SH"] == pytest.approx(-0.17)

    def test_adv_floor_raises_slippage(self):
        """ADV 地板比 0.05 → 退出天数抬升 → 滑点上升"""
        pos = [CrisisPosition(symbol="A", position_value=1_000_000.0, adv_value=100_000_000.0)]
        base = build_market_dryup_scenario(pos).slippage[0]
        run = build_bank_run_scenario(pos).slippage[0]
        assert run.exit_days == pytest.approx(1_000_000.0 / 150_000.0)
        assert run.slippage_pct > base.slippage_pct

    def test_total_slippage_value(self):
        """组合滑点金额 = Σ 持仓×滑点占比"""
        pos = [CrisisPosition(symbol="A", position_value=1_000_000.0, adv_value=100_000_000.0)]
        r = build_bank_run_scenario(pos)
        assert r.total_slippage_value == pytest.approx(1_000_000.0 * r.slippage[0].slippage_pct)


class TestFamilyRunner:
    def test_family_returns_four_in_order(self):
        results = run_liquidity_crisis_family(_positions())
        assert [r.family for r in results] == [
            LiquidityCrisisFamily.MARKET_DRYUP,
            LiquidityCrisisFamily.POSITION_FROZEN,
            LiquidityCrisisFamily.FUNDING_BREAK,
            LiquidityCrisisFamily.BANK_RUN,
        ]

    def test_empty_positions_raise(self):
        with pytest.raises(InvalidLiquidityScenarioError):
            run_liquidity_crisis_family([])

    def test_negative_position_raises(self):
        pos = [CrisisPosition(symbol="A", position_value=-1.0, adv_value=1.0)]
        with pytest.raises(InvalidLiquidityScenarioError):
            run_liquidity_crisis_family(pos)

    def test_duplicate_symbol_raises(self):
        pos = [
            CrisisPosition(symbol="A", position_value=1.0, adv_value=1.0),
            CrisisPosition(symbol="A", position_value=2.0, adv_value=1.0),
        ]
        with pytest.raises(InvalidLiquidityScenarioError):
            run_liquidity_crisis_family(pos)


class TestStressEngineIntegration:
    def test_scenario_consumed_by_engine(self):
        """产出 StressScenario 可直接喂 MOD-RK-12 run_hypothetical"""
        r = build_position_frozen_scenario(_positions())
        engine = StressTestEngine()
        result = engine.run_hypothetical(
            weights={"600000.SH": 0.5, "300001.SZ": 0.3, "688002.SH": 0.2},
            portfolio_value=10_000_000.0,
            shocks=r.scenario.shocks,
            name=r.scenario.name,
        )
        # loss = 0.5×0 + 0.3×(-0.30) + 0.2×(-0.10) = -0.11
        assert result.portfolio_loss_pct == pytest.approx(-0.11)
        assert result.is_severe is True
