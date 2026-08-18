# [BLUEPRINT] MOD-BT-021 | docs/03_modules/_domain_backtest/param_analyzer/blueprint.md
# [MODULE] tests.backtest.test_param_analyzer
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.services.param_analyzer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-BT-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-BT-021 Parameter Analyzer 单元测试.

覆盖: 最优参数识别、敏感度计算、过拟合检测、稳定性评估、
空列表拒绝、单条记录处理、缓存集成、配置自定义、frozen不可变。
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from zephyr.backtest.services.cache_manager import BacktestCacheManager
from zephyr.backtest.services.param_analyzer import (
    OverfittingCheck,
    ParamAnalysisConfig,
    ParamAnalysisError,
    ParamAnalysisReport,
    ParameterAnalyzer,
    ParamRun,
    ParamSensitivity,
    StabilityAssessment,
)

# ============== 辅助函数 ==============


def make_runs(n: int = 5, **param_overrides) -> list[ParamRun]:
    """构建参数运行列表。"""
    runs = []
    for i in range(n):
        params = {"fast": 5 + i * 5, "slow": 20}
        params.update(param_overrides)
        runs.append(ParamRun(
            params=params,
            objective=1.0 + i * 0.1,
            in_sample=1.5 + i * 0.1,
            out_of_sample=1.0 + i * 0.05,
        ))
    return runs


# ============== 配置 ==============


class TestParamAnalysisConfig:
    def test_defaults(self):
        cfg = ParamAnalysisConfig()
        assert cfg.sensitivity_threshold == 0.5
        assert cfg.overfit_threshold == 0.5
        assert cfg.stability_cv_threshold == 0.1
        assert cfg.top_n == 5

    def test_custom(self):
        cfg = ParamAnalysisConfig(sensitivity_threshold=1.0, top_n=10)
        assert cfg.sensitivity_threshold == 1.0
        assert cfg.top_n == 10

    def test_frozen(self):
        cfg = ParamAnalysisConfig()
        with pytest.raises(FrozenInstanceError):
            cfg.sensitivity_threshold = 2.0  # type: ignore[misc]

    def test_invalid_threshold(self):
        with pytest.raises(ParamAnalysisError):
            ParamAnalysisConfig(sensitivity_threshold=0)

    def test_invalid_top_n(self):
        with pytest.raises(ParamAnalysisError):
            ParamAnalysisConfig(top_n=0)


# ============== Frozen Dataclass ==============


class TestFrozenDataclasses:
    def test_param_run_frozen(self):
        r = ParamRun(params={"a": 1}, objective=1.0)
        with pytest.raises(FrozenInstanceError):
            r.objective = 2.0  # type: ignore[misc]

    def test_sensitivity_frozen(self):
        s = ParamSensitivity(param_name="x", sensitivity=0.5, is_significant=True)
        with pytest.raises(FrozenInstanceError):
            s.sensitivity = 1.0  # type: ignore[misc]

    def test_overfitting_frozen(self):
        o = OverfittingCheck(overfit_score=0.3, is_overfit=False, in_sample=1.0, out_of_sample=0.8)
        with pytest.raises(FrozenInstanceError):
            o.overfit_score = 0.9  # type: ignore[misc]

    def test_stability_frozen(self):
        s = StabilityAssessment(coefficient_of_variation=0.05, is_stable=True, top_n=5)
        with pytest.raises(FrozenInstanceError):
            s.coefficient_of_variation = 0.5  # type: ignore[misc]


# ============== 最优参数识别 ==============


class TestBestRun:
    def test_best_run_identified(self):
        analyzer = ParameterAnalyzer()
        runs = make_runs(5)
        report = analyzer.analyze(runs)
        assert report.best_run is not None
        assert report.best_run.objective == pytest.approx(1.4)  # 1.0 + 4*0.1
        assert report.best_run.params["fast"] == 25

    def test_total_runs(self):
        analyzer = ParameterAnalyzer()
        report = analyzer.analyze(make_runs(7))
        assert report.total_runs == 7

    def test_single_run(self):
        analyzer = ParameterAnalyzer()
        report = analyzer.analyze([ParamRun(params={"x": 1}, objective=1.0)])
        assert report.best_run is not None
        assert report.best_run.objective == 1.0
        assert report.sensitivities == []
        assert report.stability is None


# ============== 敏感度分析 ==============


class TestSensitivity:
    def test_sensitivity_computed(self):
        analyzer = ParameterAnalyzer()
        runs = [
            ParamRun(params={"fast": 5}, objective=1.0),
            ParamRun(params={"fast": 5}, objective=1.1),
            ParamRun(params={"fast": 10}, objective=2.0),
            ParamRun(params={"fast": 10}, objective=2.1),
        ]
        report = analyzer.analyze(runs)
        assert len(report.sensitivities) == 1
        s = report.sensitivities[0]
        assert s.param_name == "fast"
        assert s.sensitivity > 0
        assert len(s.group_means) == 2

    def test_significant_parameter(self):
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(sensitivity_threshold=0.1))
        runs = [
            ParamRun(params={"p": 1}, objective=1.0),
            ParamRun(params={"p": 2}, objective=5.0),
            ParamRun(params={"p": 3}, objective=1.0),
        ]
        report = analyzer.analyze(runs)
        s = report.sensitivities[0]
        assert s.is_significant is True

    def test_insignificant_parameter(self):
        """参数值变化但 objective 几乎不变 → 低敏感度。"""
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(sensitivity_threshold=5.0))
        runs = [
            ParamRun(params={"p": 1}, objective=1.00),
            ParamRun(params={"p": 2}, objective=1.01),
            ParamRun(params={"p": 3}, objective=1.00),
        ]
        report = analyzer.analyze(runs)
        s = report.sensitivities[0]
        assert s.is_significant is False

    def test_single_value_param_skipped(self):
        """参数只有一个值 → 不计算敏感度。"""
        analyzer = ParameterAnalyzer()
        runs = [
            ParamRun(params={"p": 1, "q": 10}, objective=1.0),
            ParamRun(params={"p": 2, "q": 10}, objective=2.0),
        ]
        report = analyzer.analyze(runs)
        names = [s.param_name for s in report.sensitivities]
        assert "p" in names
        assert "q" not in names

    def test_zero_variance_no_sensitivity(self):
        """所有 objective 相同 → 无敏感度。"""
        analyzer = ParameterAnalyzer()
        runs = [
            ParamRun(params={"p": 1}, objective=1.0),
            ParamRun(params={"p": 2}, objective=1.0),
        ]
        report = analyzer.analyze(runs)
        assert report.sensitivities == []


# ============== 过拟合检测 ==============


class TestOverfitting:
    def test_overfit_detected(self):
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(overfit_threshold=0.3))
        runs = [
            ParamRun(params={"p": 1}, objective=1.0, in_sample=2.0, out_of_sample=1.0),
            ParamRun(params={"p": 2}, objective=0.9, in_sample=1.8, out_of_sample=0.9),
        ]
        report = analyzer.analyze(runs)
        assert report.overfitting is not None
        assert report.overfitting.is_overfit is True
        assert report.overfitting.overfit_score == pytest.approx(0.5, abs=0.01)

    def test_no_overfit(self):
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(overfit_threshold=0.5))
        runs = [
            ParamRun(params={"p": 1}, objective=1.0, in_sample=1.1, out_of_sample=1.0),
            ParamRun(params={"p": 2}, objective=0.9, in_sample=1.0, out_of_sample=0.9),
        ]
        report = analyzer.analyze(runs)
        assert report.overfitting is not None
        assert report.overfitting.is_overfit is False

    def test_no_oos_data_no_overfit_check(self):
        analyzer = ParameterAnalyzer()
        runs = [
            ParamRun(params={"p": 1}, objective=1.0),
            ParamRun(params={"p": 2}, objective=2.0),
        ]
        report = analyzer.analyze(runs)
        assert report.overfitting is None

    def test_zero_is_value(self):
        """IS=0 → overfit_score=0, 不报过拟合。"""
        analyzer = ParameterAnalyzer()
        runs = [
            ParamRun(params={"p": 1}, objective=0.0, in_sample=0.0, out_of_sample=0.0),
            ParamRun(params={"p": 2}, objective=0.0, in_sample=0.0, out_of_sample=0.0),
        ]
        report = analyzer.analyze(runs)
        assert report.overfitting is not None
        assert report.overfitting.overfit_score == 0.0
        assert report.overfitting.is_overfit is False


# ============== 稳定性评估 ==============


class TestStability:
    def test_stable_results(self):
        """top_n 结果 CV 很小 → 稳定。"""
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(top_n=3, stability_cv_threshold=0.1))
        runs = [
            ParamRun(params={"p": i}, objective=1.00 + i * 0.001)
            for i in range(5)
        ]
        report = analyzer.analyze(runs)
        assert report.stability is not None
        assert report.stability.is_stable is True
        assert report.stability.top_n == 3

    def test_unstable_results(self):
        """top_n 结果 CV 很大 → 不稳定。"""
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(top_n=3, stability_cv_threshold=0.05))
        runs = [
            ParamRun(params={"p": i}, objective=1.0 + i * 1.0)
            for i in range(5)
        ]
        report = analyzer.analyze(runs)
        assert report.stability is not None
        assert report.stability.is_stable is False

    def test_stability_top_n_capped(self):
        """top_n 不能超过 runs 数量。"""
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(top_n=100))
        runs = make_runs(3)
        report = analyzer.analyze(runs)
        assert report.stability is not None
        assert report.stability.top_n == 3

    def test_single_run_no_stability(self):
        analyzer = ParameterAnalyzer()
        report = analyzer.analyze([ParamRun(params={"x": 1}, objective=1.0)])
        assert report.stability is None


# ============== 空列表 ==============


class TestEmptyInput:
    def test_empty_list_raises(self):
        analyzer = ParameterAnalyzer()
        with pytest.raises(ParamAnalysisError):
            analyzer.analyze([])

    def test_error_code(self):
        assert ParamAnalysisError.error_code == "ZA-BT-0021"


# ============== 缓存集成 ==============


class TestCacheIntegration:
    def test_cache_used(self):
        cache = BacktestCacheManager()
        analyzer = ParameterAnalyzer(cache=cache)
        report = analyzer.analyze(make_runs(3))
        assert report.best_run is not None
        stats = cache.stats()
        assert stats.total_entries == 1

    def test_no_cache_no_error(self):
        analyzer = ParameterAnalyzer()  # no cache
        report = analyzer.analyze(make_runs(3))
        assert report.best_run is not None


# ============== 配置只读 ==============


class TestConfigReadonly:
    def test_config_property(self):
        cfg = ParamAnalysisConfig(top_n=10)
        analyzer = ParameterAnalyzer(cfg)
        assert analyzer.config.top_n == 10
        assert analyzer.config is cfg


# ============== 综合场景 ==============


class TestIntegration:
    def test_full_analysis(self):
        analyzer = ParameterAnalyzer(ParamAnalysisConfig(
            sensitivity_threshold=0.3,
            overfit_threshold=0.4,
            stability_cv_threshold=0.15,
            top_n=3,
        ))
        runs = [
            ParamRun(params={"fast": 5, "slow": 20}, objective=1.5, in_sample=2.0, out_of_sample=1.2),
            ParamRun(params={"fast": 5, "slow": 30}, objective=1.4, in_sample=1.9, out_of_sample=1.1),
            ParamRun(params={"fast": 10, "slow": 20}, objective=0.8, in_sample=1.5, out_of_sample=0.5),
            ParamRun(params={"fast": 10, "slow": 30}, objective=0.7, in_sample=1.4, out_of_sample=0.4),
        ]
        report = analyzer.analyze(runs)
        assert report.total_runs == 4
        assert report.best_run.params["fast"] == 5
        assert len(report.sensitivities) == 2  # fast + slow
        assert report.overfitting is not None
        assert report.stability is not None

    def test_negative_objectives(self):
        """负 objective 也能正确识别最优。"""
        analyzer = ParameterAnalyzer()
        runs = [
            ParamRun(params={"p": 1}, objective=-0.5),
            ParamRun(params={"p": 2}, objective=-0.2),
            ParamRun(params={"p": 3}, objective=-0.8),
        ]
        report = analyzer.analyze(runs)
        assert report.best_run.objective == pytest.approx(-0.2)
