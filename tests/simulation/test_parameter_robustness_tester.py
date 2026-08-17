# [BLUEPRINT] MOD-SIM-021 | docs/03_modules/_domain_simulation/parameter_robustness_tester/blueprint.md
# [MODULE] tests.simulation.test_parameter_robustness_tester
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.simulation.parameter_robustness_tester
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SIM-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIM-021 Parameter Robustness Tester 单元测试.

覆盖: 鲁棒参数(宽稳定区间→LOW)、过拟合参数(窄峰→HIGH)、稳定区间检测、
扰动测试、多参数汇总、边界值(空/单值)、配置自定义、frozen不可变、审计摘要.
"""

from __future__ import annotations

import math

import pytest

from zephyr.simulation.parameter_robustness_tester import (
    OverfitRisk,
    ParameterPoint,
    ParameterRobustnessTester,
    ParameterSensitivity,
    PerturbationResult,
    RobustnessConfig,
    RobustnessReport,
    SimulationError,
    StableRegion,
)

# ============== 辅助函数 ==============


def robust_objective(p: float) -> float:
    """鲁棒目标函数: 在 [10, 30] 范围内表现稳定(接近最优)。"""
    # 宽平顶: 10-30 区间目标值~1.0, 外侧衰减
    if 10 <= p <= 30:
        return 1.0 - 0.001 * abs(p - 20)
    if p < 10:
        return 0.5 + 0.05 * p  # 0.5→1.0
    return max(0.0, 1.0 - 0.05 * (p - 30))  # 30→衰减


def overfit_objective(p: float) -> float:
    """过拟合目标函数: 仅在 p=20 附近有尖峰。"""
    return math.exp(-((p - 20) ** 2) / 2.0)  # 窄峰


# ============== 配置 ==============


class TestRobustnessConfig:
    def test_defaults(self):
        cfg = RobustnessConfig()
        assert cfg.stable_threshold_ratio == 0.9
        assert cfg.low_risk_min_ratio == 0.5
        assert cfg.high_risk_max_ratio == 0.2
        assert cfg.default_perturbations == (-0.1, -0.05, 0.05, 0.1)

    def test_frozen(self):
        cfg = RobustnessConfig()
        with pytest.raises(Exception):
            cfg.stable_threshold_ratio = 0.8  # type: ignore[misc]

    def test_custom(self):
        cfg = RobustnessConfig(
            stable_threshold_ratio=0.95,
            low_risk_min_ratio=0.6,
            high_risk_max_ratio=0.3,
        )
        assert cfg.stable_threshold_ratio == 0.95
        assert cfg.low_risk_min_ratio == 0.6


class TestFrozenDataclasses:
    def test_parameter_point_frozen(self):
        p = ParameterPoint(param_value=1.0, objective=2.0)
        with pytest.raises(Exception):
            p.objective = 3.0  # type: ignore[misc]

    def test_stable_region_frozen(self):
        r = StableRegion(low=1.0, high=5.0, width=4.0, point_count=5)
        with pytest.raises(Exception):
            r.width = 10.0  # type: ignore[misc]

    def test_sensitivity_frozen(self):
        s = ParameterSensitivity(param_name="x")
        with pytest.raises(Exception):
            s.overfit_risk = OverfitRisk.LOW  # type: ignore[misc]

    def test_report_frozen(self):
        r = RobustnessReport()
        with pytest.raises(Exception):
            r.is_robust = True  # type: ignore[misc]


# ============== 鲁棒参数测试 ==============


class TestRobustParameter:
    def test_robust_has_wide_stable_region(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(robust_objective, "ma", params)
        assert sens.stable_region is not None
        # 稳定区间应覆盖 10-30
        assert sens.stable_region.low <= 10
        assert sens.stable_region.high >= 30
        assert sens.stable_region.width >= 20

    def test_robust_low_risk(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(robust_objective, "ma", params)
        assert sens.overfit_risk == OverfitRisk.LOW
        assert sens.stability_ratio >= 0.5

    def test_stability_ratio_in_range(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(robust_objective, "ma", params)
        assert 0.0 <= sens.stability_ratio <= 1.0


# ============== 过拟合参数测试 ==============


class TestOverfitParameter:
    def test_overfit_has_narrow_peak(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(overfit_objective, "ma", params)
        # 窄峰: 稳定区间应很窄或 None
        if sens.stable_region is not None:
            assert sens.stable_region.width < 10

    def test_overfit_high_risk(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(overfit_objective, "ma", params)
        assert sens.overfit_risk == OverfitRisk.HIGH

    def test_overfit_low_stability_ratio(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(overfit_objective, "ma", params)
        assert sens.stability_ratio < 0.2


# ============== 稳定区间检测 ==============


class TestStableRegion:
    def test_optimal_value_is_max(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(robust_objective, "ma", params)
        # 最优目标值应 >= 所有其他
        for p in sens.points:
            assert sens.optimal_objective >= p.objective - 1e-9

    def test_no_stable_region_when_all_below_threshold(self):
        """所有目标值都很低且差异大→可能无稳定区间。"""
        tester = ParameterRobustnessTester(RobustnessConfig(stable_threshold_ratio=0.999))
        params = [1, 2, 3, 4, 5]

        def steep(p: float) -> float:
            return p  # 单调递增, 仅最高点接近 baseline

        sens = tester.test_parameter(steep, "x", params)
        # threshold=0.999*5=4.995, 仅 p=5 满足 → 单点区间 width=0
        # 但单点也构成区间(width=0)
        if sens.stable_region is not None:
            assert sens.stable_region.width == 0.0

    def test_stable_region_point_count(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(robust_objective, "ma", params)
        if sens.stable_region is not None:
            assert sens.stable_region.point_count >= 1

    def test_baseline_override(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        # 用更高的 baseline → 稳定区间变窄
        sens_high = tester.test_parameter(
            robust_objective, "ma", params, baseline=1.5
        )
        sens_default = tester.test_parameter(robust_objective, "ma", params)
        # 高 baseline 阈值更高 → 稳定点更少
        h_count = sens_high.stable_region.point_count if sens_high.stable_region else 0
        d_count = sens_default.stable_region.point_count if sens_default.stable_region else 0
        assert h_count <= d_count


# ============== 扰动测试 ==============


class TestPerturbation:
    def test_stable_perturbation(self):
        """鲁棒函数扰动后退化小。"""
        tester = ParameterRobustnessTester()
        result = tester.perturb_parameter(
            robust_objective, "ma", baseline_value=20.0
        )
        assert isinstance(result, PerturbationResult)
        assert result.baseline_objective > 0
        assert len(result.objectives) == 4
        # 鲁棒函数在 20 附近扰动退化小
        assert result.max_degradation < 0.1
        assert result.is_stable is True

    def test_unstable_perturbation(self):
        """过拟合函数扰动后退化大。"""
        tester = ParameterRobustnessTester()
        result = tester.perturb_parameter(
            overfit_objective, "ma", baseline_value=20.0
        )
        # 尖峰函数 ±5% 扰动退化巨大
        assert result.max_degradation > 0.1
        assert result.is_stable is False

    def test_custom_perturbations(self):
        tester = ParameterRobustnessTester()
        result = tester.perturb_parameter(
            robust_objective, "ma", baseline_value=20.0,
            perturbations=[0.01, -0.01],
        )
        assert len(result.objectives) == 2
        assert result.perturbations == (0.01, -0.01)

    def test_zero_baseline_raises(self):
        tester = ParameterRobustnessTester()
        with pytest.raises(SimulationError):
            tester.perturb_parameter(lambda p: 1.0, "x", baseline_value=0.0)


# ============== 多参数汇总 ==============


class TestAssess:
    def test_robust_report(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        s1 = tester.test_parameter(robust_objective, "ma_fast", params)
        s2 = tester.test_parameter(robust_objective, "ma_slow", params)
        report = tester.assess([s1, s2])
        assert report.is_robust is True
        assert report.overall_overfit_risk == OverfitRisk.LOW
        assert report.overall_stability > 0.5

    def test_overfit_report(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        s1 = tester.test_parameter(overfit_objective, "ma_fast", params)
        s2 = tester.test_parameter(overfit_objective, "ma_slow", params)
        report = tester.assess([s1, s2])
        assert report.is_robust is False
        assert report.overall_overfit_risk == OverfitRisk.HIGH

    def test_mixed_report_takes_worst(self):
        """混合参数: 总体风险取最高(HIGH)。"""
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        s_robust = tester.test_parameter(robust_objective, "robust", params)
        s_overfit = tester.test_parameter(overfit_objective, "overfit", params)
        report = tester.assess([s_robust, s_overfit])
        assert report.overall_overfit_risk == OverfitRisk.HIGH
        assert report.is_robust is False

    def test_empty_assess_raises(self):
        tester = ParameterRobustnessTester()
        with pytest.raises(SimulationError):
            tester.assess([])

    def test_overall_stability_is_average(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        s1 = tester.test_parameter(robust_objective, "a", params)
        s2 = tester.test_parameter(robust_objective, "b", params)
        report = tester.assess([s1, s2])
        expected = (s1.stability_ratio + s2.stability_ratio) / 2
        assert report.overall_stability == pytest.approx(expected, rel=1e-9)


# ============== 边界值 ==============


class TestEdgeCases:
    def test_empty_params_raises(self):
        tester = ParameterRobustnessTester()
        with pytest.raises(SimulationError):
            tester.test_parameter(lambda p: p, "x", [])

    def test_single_value_raises(self):
        tester = ParameterRobustnessTester()
        with pytest.raises(SimulationError):
            tester.test_parameter(lambda p: p, "x", [5.0])

    def test_error_code(self):
        assert SimulationError.error_code == "ZA-SIM-0021"

    def test_objective_std_populated(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        sens = tester.test_parameter(overfit_objective, "ma", params)
        # 过拟合函数目标值差异大 → std 较大
        assert sens.objective_std > 0


# ============== 枚举 ==============


class TestEnums:
    def test_overfit_risk_values(self):
        assert OverfitRisk.LOW.value == "low"
        assert OverfitRisk.MEDIUM.value == "medium"
        assert OverfitRisk.HIGH.value == "high"

    def test_enum_is_str(self):
        assert isinstance(OverfitRisk.LOW, str)


# ============== 配置只读 ==============


class TestConfigReadonly:
    def test_config_property(self):
        cfg = RobustnessConfig(low_risk_min_ratio=0.6)
        tester = ParameterRobustnessTester(cfg)
        assert tester.config.low_risk_min_ratio == 0.6
        assert tester.config is cfg


# ============== 审计摘要 ==============


class TestAuditSummary:
    def test_robust_summary(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        s = tester.test_parameter(robust_objective, "ma", params)
        report = tester.assess([s])
        summary = tester.audit_summary(report)
        assert "PASS" in summary
        assert "ma" in summary

    def test_overfit_summary(self):
        tester = ParameterRobustnessTester()
        params = [5, 10, 15, 20, 25, 30, 35]
        s = tester.test_parameter(overfit_objective, "ma", params)
        report = tester.assess([s])
        summary = tester.audit_summary(report)
        assert "FAIL" in summary
        assert "high" in summary.lower()
