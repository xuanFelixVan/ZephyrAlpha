# [BLUEPRINT] MOD-RK-35 | docs/03_modules/_domain_risk/atr_stop_engine/blueprint.md | §test
# [MODULE] tests.risk.test_atr_stop_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.atr_stop_engine
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_atr_stop_engine.py
# [A_test] module_id: MOD-RK-35 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-35 单元测试: AtrStopEngine — ATR 动态止损与 Bayesian 参数优化。

覆盖: 体制自适应 k（趋势 3.5/均值回归 1.75/ADX>25 auto）、初始止损、追踪止损只上移
不下移、分批止盈 1/3@1R+1/3@2R+1/3 追踪、时间止损 N 日未达 1R、Bayesian(GP+EI)
与网格 k 优化收敛与留痕、非法输入 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.risk.atr_stop_engine import (
    AtrStopConfig,
    AtrStopEngine,
    AtrStopPlan,
    BayesianOptimizationResult,
    InvalidAtrStopInputError,
    StopRegime,
)


class TestRegimeKMapping:
    def test_trend_regime_k(self):
        engine = AtrStopEngine()
        plan = engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.TREND)
        # k=3.5 → 1R=1.75
        assert plan.r_unit == pytest.approx(3.5 * 0.5)
        assert plan.initial_stop == pytest.approx(10.0 - 1.75)

    def test_mean_reversion_regime_k(self):
        engine = AtrStopEngine()
        plan = engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.MEAN_REVERSION)
        assert plan.r_unit == pytest.approx(1.75 * 0.5)
        assert plan.initial_stop == pytest.approx(10.0 - 0.875)

    def test_auto_regime_adx_above_25_uses_trend_k(self):
        engine = AtrStopEngine()
        plan = engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.AUTO, adx=30.0)
        assert plan.r_unit == pytest.approx(3.5 * 0.5)

    def test_auto_regime_adx_below_25_uses_mean_reversion_k(self):
        engine = AtrStopEngine()
        plan = engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.AUTO, adx=18.0)
        assert plan.r_unit == pytest.approx(1.75 * 0.5)

    def test_auto_regime_requires_adx(self):
        engine = AtrStopEngine()
        with pytest.raises(InvalidAtrStopInputError):
            engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.AUTO)


class TestStopPlan:
    def test_profit_targets_thirds(self):
        engine = AtrStopEngine()
        plan = engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.TREND)
        # 1R=1.75 → TP1=11.75, TP2=13.5
        assert plan.profit_target_1r == pytest.approx(11.75)
        assert plan.profit_target_2r == pytest.approx(13.5)
        assert plan.profit_target_fractions == (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)

    def test_trailing_stop_only_moves_up(self):
        engine = AtrStopEngine()
        plan = engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.TREND)
        # 最高价 12 → 候选 trailing = 12-1.75=10.25（高于 initial 8.25）
        t1 = engine.update_trailing_stop(plan, highest_price=12.0)
        assert t1 == pytest.approx(10.25)
        plan2 = engine.with_trailing_stop(plan, t1)
        # 最高价回落到 11 → 候选 9.25 < 10.25 → 保持 10.25（只上移）
        t2 = engine.update_trailing_stop(plan2, highest_price=11.0)
        assert t2 == pytest.approx(10.25)
        # 最高价升至 13 → 候选 11.25 > 10.25 → 上移
        t3 = engine.update_trailing_stop(plan2, highest_price=13.0)
        assert t3 == pytest.approx(11.25)

    def test_time_stop_due_after_n_days_below_1r(self):
        engine = AtrStopEngine(AtrStopConfig(time_stop_days=5))
        plan = engine.build_plan(entry_price=10.0, atr14=0.5, regime=StopRegime.TREND)
        # 持有 6 日, 现价 10.5（浮盈 0.5 < 1R=1.75）→ 时间止损
        assert engine.check_time_stop(plan, current_price=10.5, holding_days=6) is True
        # 持有 6 日, 现价 12.0（浮盈 2.0 > 1R）→ 不触发
        assert engine.check_time_stop(plan, current_price=12.0, holding_days=6) is False
        # 持有 4 日未超 N → 不触发
        assert engine.check_time_stop(plan, current_price=10.5, holding_days=4) is False


class TestInputValidation:
    def test_rejects_non_positive_entry(self):
        engine = AtrStopEngine()
        with pytest.raises(InvalidAtrStopInputError):
            engine.build_plan(entry_price=0.0, atr14=0.5, regime=StopRegime.TREND)

    def test_rejects_non_positive_atr(self):
        engine = AtrStopEngine()
        with pytest.raises(InvalidAtrStopInputError):
            engine.build_plan(entry_price=10.0, atr14=-0.1, regime=StopRegime.TREND)

    def test_rejects_non_finite(self):
        engine = AtrStopEngine()
        with pytest.raises(InvalidAtrStopInputError):
            engine.build_plan(entry_price=float("nan"), atr14=0.5, regime=StopRegime.TREND)

    def test_config_rejects_bad_k(self):
        with pytest.raises(InvalidAtrStopInputError):
            AtrStopConfig(k_trend=0.0)
        with pytest.raises(InvalidAtrStopInputError):
            AtrStopConfig(k_mean_reversion=-1.0)

    def test_config_rejects_bad_time_stop_days(self):
        with pytest.raises(InvalidAtrStopInputError):
            AtrStopConfig(time_stop_days=0)


class TestBayesianOptimization:
    @staticmethod
    def _synthetic_objective(k: float) -> float:
        # 合成目标：k*=2.3 处单峰（模拟回测评分）
        return -((k - 2.3) ** 2) + 1.0

    def test_grid_search_finds_peak(self):
        engine = AtrStopEngine()
        result = engine.grid_search_k(self._synthetic_objective, k_bounds=(1.0, 4.0), n_points=31)
        assert result.best_k == pytest.approx(2.3, abs=0.1)
        assert result.evaluations  # 留痕非空

    def test_bayesian_optimization_converges_near_peak(self):
        engine = AtrStopEngine()
        result = engine.bayesian_optimize_k(
            self._synthetic_objective,
            k_bounds=(1.0, 4.0),
            n_initial=5,
            n_iterations=12,
        )
        assert isinstance(result, BayesianOptimizationResult)
        assert result.best_k == pytest.approx(2.3, abs=0.25)
        assert result.best_value == pytest.approx(1.0, abs=0.2)
        # 留痕：初探 5 + 序贯 12 = 17 个评估点
        assert len(result.evaluations) == 17

    def test_bayesian_rejects_bad_bounds(self):
        engine = AtrStopEngine()
        with pytest.raises(InvalidAtrStopInputError):
            engine.bayesian_optimize_k(self._synthetic_objective, k_bounds=(4.0, 1.0))

    def test_bayesian_rejects_non_finite_objective(self):
        engine = AtrStopEngine()
        with pytest.raises(InvalidAtrStopInputError):
            engine.bayesian_optimize_k(lambda k: float("nan"), k_bounds=(1.0, 4.0), n_initial=3, n_iterations=2)
