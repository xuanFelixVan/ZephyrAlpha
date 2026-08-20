# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_overfitting_detector
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_overfitting_detector.py
# [TTL] task_bound
"""OverfittingDetector 单元测试(52号 §7 新发现1 测试债清偿).

覆盖: 配置校验、维度1 WF稳定性(正Sharpe占比/CV/灾难fold)、维度2参数敏感性
(相对变化阈值/基准Sharpe≈0跳过)、维度3泛化(占比/CV)、SIM-38样本内外对比
(0.70否决阈值/IS非正跳过)、detect 综合(任一维度不稳即否决/未提供维度默认稳定)。
"""
from __future__ import annotations

import pytest

from zephyr.backtest.core.overfitting_detector import (
    DEFAULT_OOS_SHARPE_THRESHOLD_RATIO,
    OverfittingConfig,
    OverfittingDetector,
    OverfittingError,
    OverfittingGateError,
)


def _wf(sharpes: list[float]) -> list[dict]:
    return [{"sharpe_ratio": s} for s in sharpes]


# ============== 配置校验 ==============


class TestOverfittingConfig:
    def test_defaults(self):
        cfg = OverfittingConfig()
        assert cfg.parameter_perturbation_pct == pytest.approx(0.10)
        assert cfg.oos_sharpe_threshold_ratio == pytest.approx(0.70)
        assert cfg.cross_validation_folds == 5

    def test_perturbation_out_of_range(self):
        with pytest.raises(OverfittingError):
            OverfittingConfig(parameter_perturbation_pct=0.0)
        with pytest.raises(OverfittingError):
            OverfittingConfig(parameter_perturbation_pct=1.5)

    def test_threshold_ratio_out_of_range(self):
        with pytest.raises(OverfittingError):
            OverfittingConfig(oos_sharpe_threshold_ratio=-0.1)
        with pytest.raises(OverfittingError):
            OverfittingConfig(oos_sharpe_threshold_ratio=1.1)

    def test_folds_must_positive(self):
        with pytest.raises(OverfittingError):
            OverfittingConfig(cross_validation_folds=0)

    def test_ssot_constant(self):
        assert DEFAULT_OOS_SHARPE_THRESHOLD_RATIO == pytest.approx(0.70)


# ============== 维度1: Walk-Forward 稳定性 ==============


class TestWalkForwardStability:
    def test_empty_is_stable(self):
        r = OverfittingDetector().check_walk_forward_stability([])
        assert r["is_stable"] is True
        assert r["n_folds"] == 0

    def test_stable_folds(self):
        r = OverfittingDetector().check_walk_forward_stability(
            _wf([0.8, 0.9, 0.7, 0.85])
        )
        assert r["is_stable"] is True
        assert r["positive_ratio"] == pytest.approx(1.0)

    def test_low_positive_ratio_unstable(self):
        # 正Sharpe占比 2/5=40% < 60%
        r = OverfittingDetector().check_walk_forward_stability(
            _wf([0.8, 0.6, -0.1, -0.2, -0.05])
        )
        assert r["is_stable"] is False
        assert any("占比" in x for x in r["reasons"])

    def test_high_cv_unstable(self):
        # mean≈0.1, std大 → CV>1.5
        r = OverfittingDetector().check_walk_forward_stability(
            _wf([1.5, -0.8, 0.6, -0.6, 0.8])
        )
        assert r["is_stable"] is False
        assert any("变异系数" in x for x in r["reasons"])

    def test_disaster_fold_unstable(self):
        r = OverfittingDetector().check_walk_forward_stability(
            _wf([0.8, 0.9, -0.6])  # min=-0.6 < -0.5 灾难fold
        )
        assert r["is_stable"] is False
        assert any("灾难" in x for x in r["reasons"])

    def test_sharpe_key_fallback(self):
        # sharpe_ratio 缺失时回退 sharpe 键
        r = OverfittingDetector().check_walk_forward_stability(
            [{"sharpe": 0.8}, {"sharpe": 0.9}]
        )
        assert r["is_stable"] is True

    def test_invalid_sharpe_treated_zero(self):
        r = OverfittingDetector().check_walk_forward_stability(
            [{"sharpe_ratio": "bad"}, {"sharpe_ratio": None}, {"sharpe_ratio": 0.8}]
        )
        assert r["n_folds"] == 3
        assert r["positive_ratio"] == pytest.approx(1 / 3)

    def test_single_fold_zero_std(self):
        r = OverfittingDetector().check_walk_forward_stability(_wf([0.8]))
        assert r["std_sharpe"] == 0.0
        assert r["cv"] == 0.0


# ============== 维度2: 参数敏感性 ==============


class TestParameterSensitivity:
    def test_empty_perturbed_stable(self):
        r = OverfittingDetector().check_parameter_sensitivity({"sharpe_ratio": 1.0}, [])
        assert r["is_stable"] is True

    def test_small_change_stable(self):
        r = OverfittingDetector().check_parameter_sensitivity(
            {"sharpe_ratio": 1.0}, _wf([0.95, 1.05, 0.9])
        )
        assert r["is_stable"] is True
        assert r["max_change"] == pytest.approx(0.10)

    def test_large_change_unstable(self):
        # |0.5-1.0|/1.0=50% > 30%
        r = OverfittingDetector().check_parameter_sensitivity(
            {"sharpe_ratio": 1.0}, _wf([0.5])
        )
        assert r["is_stable"] is False
        assert any("相对变化" in x for x in r["reasons"])

    def test_zero_base_sharpe_skips(self):
        r = OverfittingDetector().check_parameter_sensitivity(
            {"sharpe_ratio": 0.0}, _wf([0.5, -0.3])
        )
        assert r["is_stable"] is True
        assert any("跳过" in x for x in r["reasons"])


# ============== 维度3: 泛化能力 ==============


class TestGeneralization:
    def test_empty_stable(self):
        r = OverfittingDetector().check_generalization([])
        assert r["is_stable"] is True

    def test_stable_periods(self):
        r = OverfittingDetector().check_generalization(_wf([0.7, 0.8, 0.75, 0.9]))
        assert r["is_stable"] is True

    def test_low_positive_ratio_unstable(self):
        r = OverfittingDetector().check_generalization(_wf([0.7, -0.2, -0.1, -0.3]))
        assert r["is_stable"] is False

    def test_high_cv_unstable(self):
        r = OverfittingDetector().check_generalization(_wf([1.5, -0.9, 0.8, -0.7, 0.9]))
        assert r["is_stable"] is False
        assert any("变异系数" in x for x in r["reasons"])


# ============== SIM-38 样本内外对比 ==============


class TestInOutSample:
    def test_pass_above_threshold(self):
        r = OverfittingDetector().compare_in_out_sample(1.0, 0.8)
        assert r["is_overfitting"] is False
        assert r["ratio"] == pytest.approx(0.8)

    def test_boundary_pass(self):
        r = OverfittingDetector().compare_in_out_sample(1.0, 0.7)
        assert r["is_overfitting"] is False  # 0.7 不低于阈值0.7

    def test_veto_below_threshold(self):
        r = OverfittingDetector().compare_in_out_sample(1.0, 0.6)
        assert r["is_overfitting"] is True
        assert "否决" in r["reason"]

    def test_is_non_positive_skips(self):
        r = OverfittingDetector().compare_in_out_sample(0.0, 0.9)
        assert r["is_overfitting"] is False
        assert "跳过" in r["reason"]


# ============== detect 综合 ==============


class TestDetect:
    def test_all_clean_not_overfitting(self):
        r = OverfittingDetector().detect(
            walk_forward_results=_wf([0.8, 0.9, 0.85, 0.75]),
            perturbed_results=_wf([0.95, 1.02]),
            period_results=_wf([0.7, 0.8, 0.9, 0.85]),
            is_sharpe=1.0,
            oos_sharpe=0.85,
        )
        assert r["is_overfitting"] is False
        assert r["oos_is_ratio"] == pytest.approx(0.85)

    def test_no_dimensions_defaults_stable(self):
        r = OverfittingDetector().detect(is_sharpe=1.0, oos_sharpe=0.9)
        assert r["is_overfitting"] is False

    def test_wf_unstable_triggers(self):
        r = OverfittingDetector().detect(
            walk_forward_results=_wf([0.8, 0.9, -0.6]),
            is_sharpe=1.0,
            oos_sharpe=0.9,
        )
        assert r["is_overfitting"] is True
        assert r["walk_forward_stable"] is False

    def test_param_unstable_triggers(self):
        r = OverfittingDetector().detect(
            perturbed_results=_wf([0.4]),
            is_sharpe=1.0,
            oos_sharpe=0.9,
        )
        assert r["is_overfitting"] is True
        assert r["parameter_stable"] is False

    def test_oos_veto_triggers(self):
        r = OverfittingDetector().detect(is_sharpe=1.0, oos_sharpe=0.5)
        assert r["is_overfitting"] is True

    def test_result_keys(self):
        r = OverfittingDetector().detect(is_sharpe=1.0, oos_sharpe=0.9)
        assert set(r) == {
            "is_overfitting", "oos_is_ratio", "walk_forward_stable",
            "parameter_stable", "generalization_stable", "reasons",
        }

    def test_gate_error_subclass(self):
        assert issubclass(OverfittingGateError, OverfittingError)
        err = OverfittingGateError("blocked")
        assert err.error_code == "ZA-BT-0015"
