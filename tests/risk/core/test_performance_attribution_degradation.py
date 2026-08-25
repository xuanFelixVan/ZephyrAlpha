# [BLUEPRINT] MOD-RK-37 | docs/03_modules/_domain_risk/performance_attribution_degradation/blueprint.md | §test
# [MODULE] tests.risk.core.test_performance_attribution_degradation
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.performance_attribution_degradation
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_performance_attribution_degradation.py
# [A_test] module_id: MOD-RK-37 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-37 单元测试: PerformanceAttributionDegradationGuard — 统一绩效归因与策略退化检测。

覆盖: IC 60 日均线计算、衰减 >50% 退化判定与边界、reference≤0 语义、拥挤度联动
HALVE、degraded 优先 ZERO、统一 Brinson 归因入口委托（不重算）、reasons 留痕、
非法输入 Fail-Closed。
"""

from __future__ import annotations

import pytest

from zephyr.risk.core.performance_attribution_degradation import (
    DegradationAction,
    DegradationGuardConfig,
    InvalidDegradationInputError,
    PerformanceAttributionDegradationGuard,
    StrategyDegradationVerdict,
)


def _ic_series(reference: float, current: float, window: int = 60) -> list[float]:
    """前 window 个=reference，后 window 个=current（构造 MA60 衰减场景）。"""
    return [reference] * window + [current] * window


class TestIcMa60:
    def test_ma60_reference_and_current(self):
        guard = PerformanceAttributionDegradationGuard()
        ref, cur = guard.compute_ic_ma60(_ic_series(0.08, 0.04))
        assert ref == pytest.approx(0.08)
        assert cur == pytest.approx(0.04)

    def test_series_shorter_than_window_rejected(self):
        guard = PerformanceAttributionDegradationGuard()
        with pytest.raises(InvalidDegradationInputError):
            guard.compute_ic_ma60([0.05] * 59)

    def test_non_finite_ic_rejected(self):
        guard = PerformanceAttributionDegradationGuard()
        series = _ic_series(0.08, 0.04)
        series[100] = float("nan")
        with pytest.raises(InvalidDegradationInputError):
            guard.compute_ic_ma60(series)


class TestDegradationVerdict:
    def test_decay_above_50pct_is_zero(self):
        guard = PerformanceAttributionDegradationGuard()
        v = guard.assess_strategy("STRAT-A", ic_series=_ic_series(0.08, 0.039))
        assert isinstance(v, StrategyDegradationVerdict)
        assert v.degraded is True
        assert v.action is DegradationAction.ZERO
        assert v.weight_multiplier == 0.0
        assert v.ic_decay_pct == pytest.approx((0.08 - 0.039) / 0.08)

    def test_decay_below_50pct_is_keep(self):
        guard = PerformanceAttributionDegradationGuard()
        v = guard.assess_strategy("STRAT-A", ic_series=_ic_series(0.08, 0.045))
        assert v.degraded is False
        assert v.action is DegradationAction.KEEP
        assert v.weight_multiplier == 1.0

    def test_reference_non_positive_marks_degraded(self):
        guard = PerformanceAttributionDegradationGuard()
        v = guard.assess_strategy("STRAT-B", ic_series=_ic_series(0.0, 0.01))
        assert v.degraded is True
        assert v.action is DegradationAction.ZERO

    def test_crowding_above_warn_halves_weight(self):
        guard = PerformanceAttributionDegradationGuard()
        v = guard.assess_strategy(
            "STRAT-C",
            ic_series=_ic_series(0.08, 0.06),
            crowding_score=0.7,
        )
        assert v.degraded is False
        assert v.action is DegradationAction.HALVE
        assert v.weight_multiplier == 0.5

    def test_degraded_dominates_crowding(self):
        guard = PerformanceAttributionDegradationGuard()
        v = guard.assess_strategy(
            "STRAT-D",
            ic_series=_ic_series(0.08, 0.02),
            crowding_score=0.9,
        )
        assert v.action is DegradationAction.ZERO
        assert v.weight_multiplier == 0.0
        assert any("拥挤" in r for r in v.reasons)  # 拥挤理由仍留痕

    def test_crowding_score_out_of_range_rejected(self):
        guard = PerformanceAttributionDegradationGuard()
        with pytest.raises(InvalidDegradationInputError):
            guard.assess_strategy("STRAT-E", ic_series=_ic_series(0.08, 0.06), crowding_score=1.5)

    def test_reasons_recorded(self):
        guard = PerformanceAttributionDegradationGuard()
        v = guard.assess_strategy("STRAT-F", ic_series=_ic_series(0.08, 0.039), crowding_score=0.7)
        assert len(v.reasons) >= 2  # 退化 + 拥挤


class TestUnifiedAttributionEntry:
    def test_brinson_delegates_to_pf007(self):
        from zephyr.pf_core.core.performance_attribution_engine import SegmentReturn

        guard = PerformanceAttributionDegradationGuard()
        segments = [
            SegmentReturn("科技", 0.40, 0.30, 0.05, 0.03),
            SegmentReturn("金融", 0.60, 0.70, 0.02, 0.01),
        ]
        result = guard.brinson_attribute(segments)
        # 委托真源口径：excess = allocation + selection + interaction（守恒）
        assert result.excess_return == pytest.approx(
            result.allocation_effect + result.selection_effect + result.interaction_effect
        )


class TestConfigValidation:
    def test_window_floor(self):
        with pytest.raises(InvalidDegradationInputError):
            DegradationGuardConfig(ic_window=5)

    def test_decay_threshold_range(self):
        with pytest.raises(InvalidDegradationInputError):
            DegradationGuardConfig(ic_decay_threshold=1.5)

    def test_crowding_warn_range(self):
        with pytest.raises(InvalidDegradationInputError):
            DegradationGuardConfig(crowding_warn=-0.1)
