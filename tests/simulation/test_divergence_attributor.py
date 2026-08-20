# [BLUEPRINT] MOD-SIM-026 | docs/03_modules/_domain_simulation/blueprint.md
# [A_module] module_id=MOD-SIM-026 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-SIM-026 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.simulation.test_divergence_attributor
# [DOMAIN] D_SIMULATION
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/simulation/test_divergence_attributor.py
# [TTL] task_bound
"""BM-BT-05-H 回测-实盘偏差四因子归因单元测试(53号 §3.5).

覆盖: 全通过/单因子失败/多因子失败主导因子定位、None未观测跳过、
数据滞后无门禁仅记录、阈值默认对齐 key_gates、自定义阈值注入、
观测值越界报错、阈值配置校验。
"""

from __future__ import annotations

import pytest

from zephyr.simulation.divergence_attributor import (
    DivergenceAttributionError,
    DivergenceObservation,
    DivergenceThresholds,
    attribute_divergence,
)


def _clean_obs() -> DivergenceObservation:
    return DivergenceObservation(
        signal_match_pct=0.9995,
        slippage_diff_bps=0.5,
        data_lag_ms=20.0,
        latency_ms=50.0,
        pnl_correlation=0.97,
    )


class TestAllPass:
    def test_all_observed_pass(self):
        r = attribute_divergence(_clean_obs())
        assert r.overall_passed is True
        assert r.dominant_factor is None
        assert r.n_observed == 5
        assert r.n_failed == 0

    def test_factor_order(self):
        r = attribute_divergence(_clean_obs())
        assert [f.factor for f in r.factors] == [
            "A_SLIPPAGE",
            "B_DATA_LAG",
            "C_LOOKAHEAD",
            "D_LATENCY",
            "TOTAL_PNL",
        ]


class TestFactorFailures:
    def test_slippage_breach(self):
        obs = _clean_obs()
        r = attribute_divergence(DivergenceObservation(**{**obs.__dict__, "slippage_diff_bps": 2.0}))
        assert r.overall_passed is False
        assert r.dominant_factor == "A_SLIPPAGE"

    def test_signal_match_breach(self):
        r = attribute_divergence(DivergenceObservation(**{**_clean_obs().__dict__, "signal_match_pct": 0.98}))
        assert r.dominant_factor == "C_LOOKAHEAD"

    def test_latency_breach(self):
        r = attribute_divergence(DivergenceObservation(**{**_clean_obs().__dict__, "latency_ms": 150.0}))
        assert r.dominant_factor == "D_LATENCY"

    def test_pnl_correlation_breach(self):
        r = attribute_divergence(DivergenceObservation(**{**_clean_obs().__dict__, "pnl_correlation": 0.90}))
        assert r.dominant_factor == "TOTAL_PNL"

    def test_dominant_is_max_excess(self):
        # 滑点超出100%(0.5→2.0=超阈值1bp的100%), 时延超出20%(100→120)
        r = attribute_divergence(DivergenceObservation(slippage_diff_bps=2.0, latency_ms=120.0))
        assert r.n_failed == 2
        assert r.dominant_factor == "A_SLIPPAGE"


class TestUnobservedSkipped:
    def test_all_none_passes(self):
        r = attribute_divergence(DivergenceObservation())
        assert r.overall_passed is True
        assert r.n_observed == 0
        assert r.dominant_factor is None

    def test_partial_observation(self):
        r = attribute_divergence(DivergenceObservation(pnl_correlation=0.99))
        assert r.n_observed == 1
        assert r.overall_passed is True

    def test_data_lag_no_gate_record_only(self):
        # B 因子默认无门禁: 大滞后也仅记录不否决
        r = attribute_divergence(DivergenceObservation(data_lag_ms=5000.0))
        assert r.overall_passed is True
        b = next(f for f in r.factors if f.factor == "B_DATA_LAG")
        assert b.observed is True
        assert b.passed is True
        assert "无门禁" in b.reason


class TestThresholds:
    def test_defaults_aligned_with_key_gates(self):
        th = DivergenceThresholds()
        assert th.signal_match_min == pytest.approx(0.999)
        assert th.slippage_diff_max_bps == pytest.approx(1.0)
        assert th.pnl_correlation_min == pytest.approx(0.95)
        assert th.latency_max_ms == pytest.approx(100.0)
        assert th.data_lag_max_ms is None

    def test_custom_threshold_injection(self):
        th = DivergenceThresholds(latency_max_ms=200.0)
        r = attribute_divergence(DivergenceObservation(latency_ms=150.0), thresholds=th)
        assert r.overall_passed is True

    def test_custom_data_lag_gate(self):
        th = DivergenceThresholds(data_lag_max_ms=100.0)
        r = attribute_divergence(DivergenceObservation(data_lag_ms=500.0), thresholds=th)
        assert r.dominant_factor == "B_DATA_LAG"

    def test_invalid_thresholds(self):
        with pytest.raises(DivergenceAttributionError):
            DivergenceThresholds(signal_match_min=1.5)
        with pytest.raises(DivergenceAttributionError):
            DivergenceThresholds(slippage_diff_max_bps=0.0)
        with pytest.raises(DivergenceAttributionError):
            DivergenceThresholds(latency_max_ms=-1.0)
        with pytest.raises(DivergenceAttributionError):
            DivergenceThresholds(pnl_correlation_min=0.0)
        with pytest.raises(DivergenceAttributionError):
            DivergenceThresholds(data_lag_max_ms=0.0)


class TestValidation:
    def test_observation_type(self):
        with pytest.raises(DivergenceAttributionError):
            attribute_divergence({"slippage_diff_bps": 0.5})

    def test_negative_value_raises(self):
        with pytest.raises(DivergenceAttributionError):
            attribute_divergence(DivergenceObservation(slippage_diff_bps=-0.1))
        with pytest.raises(DivergenceAttributionError):
            attribute_divergence(DivergenceObservation(latency_ms=-5.0))

    def test_ratio_out_of_range_raises(self):
        with pytest.raises(DivergenceAttributionError):
            attribute_divergence(DivergenceObservation(signal_match_pct=1.5))
        with pytest.raises(DivergenceAttributionError):
            attribute_divergence(DivergenceObservation(pnl_correlation=-1.5))
