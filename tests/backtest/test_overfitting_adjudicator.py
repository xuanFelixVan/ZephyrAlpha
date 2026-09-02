# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_overfitting_adjudicator
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_overfitting_adjudicator.py
# [TTL] task_bound
"""P-5 过拟合裁定组件单元测试（合成数据, TDD 先红后绿）。

覆盖三检验器 + 上线门禁挂钩点:
  1. walk-forward 汇总口径: 各折 OOS/IS 衰减比分布 + 最差折 + 阈值判定;
  2. DSR: 手算解析解对拍 + statistics.NormalDist 独立预言机交叉验证 +
     零试验膨胀(N=1) vs 高试验膨胀(N=1000) 单调折减;
  3. 参数扰动 ±20%: 注入合成伪引擎 callable, 衰减率语义/稳健区间占比;
  4. OverfitGateHook Protocol 挂钩点: 注入记录钩子/缺省 None 两种形态。
"""

from __future__ import annotations

import math
from statistics import NormalDist

import pytest

from zephyr.backtest.core.overfitting_adjudicator import (
    EULER_MASCHERONI,
    DSRVerdict,
    OverfitGateHook,
    OverfittingAdjudicationError,
    OverfittingAdjudicator,
    PerturbationStabilityReport,
    WalkForwardDecaySummary,
    adjudicate_dsr,
    expected_max_sharpe_z,
    perturbation_stability,
    summarize_walk_forward,
)

_NORM = NormalDist()


# ============== ① walk-forward 汇总 ==============


class TestWalkForwardSummary:
    def test_ratio_distribution_and_worst_fold(self):
        # 手算: ratios = (1.6/2.0, 0.9/1.0, 0.6/1.5) = (0.8, 0.9, 0.4)
        summary = summarize_walk_forward([(2.0, 1.6), (1.0, 0.9), (1.5, 0.6)])
        assert isinstance(summary, WalkForwardDecaySummary)
        assert summary.n_folds == 3
        assert summary.n_valid_folds == 3
        assert summary.ratios == pytest.approx((0.8, 0.9, 0.4))
        assert summary.mean_ratio == pytest.approx(0.7)
        # 样本 std(ddof=1): sqrt((0.01+0.04+0.09)/2)=sqrt(0.07)
        assert summary.std_ratio == pytest.approx(math.sqrt(0.07))
        assert summary.min_ratio == pytest.approx(0.4)
        assert summary.worst_fold_index == 2  # 最差折=第3折(原始输入索引)
        # 默认阈值=OOS/IS 0.70 SSoT: 0.4<0.7 -> 1折破线 -> 不稳定
        assert summary.threshold == pytest.approx(0.70)
        assert summary.n_below_threshold == 1
        assert summary.is_stable is False

    def test_all_folds_above_threshold_is_stable(self):
        # 手算: ratios = (1.8/2.0, 0.95/1.0, 1.1/1.2) = (0.90, 0.95, 0.9167)
        summary = summarize_walk_forward([(2.0, 1.8), (1.0, 0.95), (1.2, 1.1)])
        assert summary.is_stable is True
        assert summary.n_below_threshold == 0
        assert summary.min_ratio == pytest.approx(0.90)
        assert summary.worst_fold_index == 0  # min ratio = 1.8/2.0 = 0.90

    def test_non_positive_is_fold_excluded(self):
        # IS<=0 折不适用 OOS/IS 比率(对齐 overfitting_detector.compare_in_out_sample 口径)
        summary = summarize_walk_forward([(2.0, 1.6), (-0.5, 3.0)])
        assert summary.n_folds == 2
        assert summary.n_valid_folds == 1
        assert summary.ratios == pytest.approx((0.8,))
        assert summary.std_ratio == 0.0  # 单折无离散度
        assert summary.worst_fold_index == 0

    def test_all_is_non_positive_no_valid_folds(self):
        summary = summarize_walk_forward([(0.0, 1.0), (-1.0, 2.0)])
        assert summary.n_valid_folds == 0
        assert summary.ratios == ()
        assert summary.worst_fold_index == -1
        assert summary.is_stable is False  # 无有效折无法证明稳定(fail-closed)

    def test_custom_threshold(self):
        summary = summarize_walk_forward([(2.0, 1.6)], threshold=0.9)
        assert summary.threshold == pytest.approx(0.9)
        assert summary.is_stable is False  # 0.8 < 0.9

    def test_empty_folds_raises(self):
        with pytest.raises(OverfittingAdjudicationError):
            summarize_walk_forward([])

    def test_non_finite_raises(self):
        with pytest.raises(OverfittingAdjudicationError):
            summarize_walk_forward([(1.0, float("nan"))])
        with pytest.raises(OverfittingAdjudicationError):
            summarize_walk_forward([(float("inf"), 1.0)])

    def test_frozen_immutable(self):
        summary = summarize_walk_forward([(2.0, 1.6), (1.0, 0.9)])
        with pytest.raises(AttributeError):
            summary.is_stable = True  # type: ignore[misc]


# ============== ② DSR (Deflated Sharpe Ratio) ==============


class TestExpectedMaxSharpeZ:
    def test_single_trial_zero_inflation(self):
        # N=1: 无多重试验膨胀, E[max]=0
        assert expected_max_sharpe_z(1) == 0.0

    def test_two_trials_hand_calc(self):
        # 手算: E[max(Z_2)] = (1-γ)·Φ⁻¹(0.5) + γ·Φ⁻¹(1-1/(2e))
        #      = (1-γ)·0 + γ·Φ⁻¹(0.81606) ≈ 0.577216·0.900454 ≈ 0.51972
        e_max = expected_max_sharpe_z(2)
        oracle = (1.0 - EULER_MASCHERONI) * _NORM.inv_cdf(0.5) + EULER_MASCHERONI * _NORM.inv_cdf(
            1.0 - 1.0 / (2.0 * math.e)
        )
        assert e_max == pytest.approx(oracle, rel=1e-9)
        assert e_max == pytest.approx(0.51972, abs=1e-4)  # 手算锚点

    def test_monotonic_in_num_trials(self):
        vals = [expected_max_sharpe_z(n) for n in (1, 2, 10, 100, 1000, 10000)]
        assert all(a <= b for a, b in zip(vals, vals[1:]))

    def test_invalid_trials_raises(self):
        with pytest.raises(OverfittingAdjudicationError):
            expected_max_sharpe_z(0)
        with pytest.raises(OverfittingAdjudicationError):
            expected_max_sharpe_z(-3)


class TestAdjudicateDsr:
    def test_hand_calc_single_trial(self):
        # 手算锚点: SR=0.1, T=101, 偏度=0, 超额峰度=0(正态), N=1
        # V[SR]=(1-0·SR+(3-1)/4·SR²)/(T-1)=(1+0.005)/100=0.01005, σ=0.10024984
        # E[max]=0 -> DSR=Φ(0.1/0.10024984)=Φ(0.997509)≈0.84074
        verdict = adjudicate_dsr(sharpe=0.1, num_trials=1, num_obs=101, skewness=0.0, kurtosis=0.0)
        assert isinstance(verdict, DSRVerdict)
        assert verdict.var_sr == pytest.approx(0.01005)
        assert verdict.expected_max_sharpe == 0.0
        assert verdict.dsr == pytest.approx(0.84074, abs=1e-4)
        assert verdict.is_significant is False  # < 0.95 显著性放行线

    def test_oracle_cross_check_with_trials(self):
        # 独立预言机对拍: 用 statistics.NormalDist 重算全流程
        sr, n_obs, n_trials, skew, kurt_excess = 0.35, 252, 50, -0.2, 1.5
        verdict = adjudicate_dsr(sharpe=sr, num_trials=n_trials, num_obs=n_obs, skewness=skew, kurtosis=kurt_excess)
        kurt_pearson = kurt_excess + 3.0
        var_sr = (1.0 - skew * sr + (kurt_pearson - 1.0) / 4.0 * sr * sr) / (n_obs - 1)
        e_max_z = (1.0 - EULER_MASCHERONI) * _NORM.inv_cdf(1.0 - 1.0 / n_trials)
        e_max_z += EULER_MASCHERONI * _NORM.inv_cdf(1.0 - 1.0 / (n_trials * math.e))
        e_max_sr = math.sqrt(var_sr) * e_max_z
        oracle_dsr = _NORM.cdf((sr - e_max_sr) / math.sqrt(var_sr))
        assert verdict.var_sr == pytest.approx(var_sr, rel=1e-12)
        assert verdict.expected_max_sharpe == pytest.approx(e_max_sr, rel=1e-9)
        assert verdict.dsr == pytest.approx(oracle_dsr, rel=1e-9)

    def test_zero_vs_high_trial_inflation(self):
        # 同一观测 Sharpe: N=1(零膨胀) DSR 显著高于 N=1000(高膨胀)
        common = dict(sharpe=0.3, num_obs=252, skewness=0.0, kurtosis=0.0)
        v_low = adjudicate_dsr(num_trials=1, **common)
        v_high = adjudicate_dsr(num_trials=1000, **common)
        assert v_low.expected_max_sharpe == 0.0
        assert v_high.expected_max_sharpe > 0.0
        assert v_high.dsr < v_low.dsr
        # N=1000 时折减幅度 = σ_SR · E[max(Z_1000)] > 0, 且 DSR 跌破显著线
        assert v_high.is_significant is False

    def test_strong_sharpe_single_trial_significant(self):
        verdict = adjudicate_dsr(sharpe=2.0, num_trials=1, num_obs=504, skewness=0.0, kurtosis=0.0)
        assert verdict.dsr > 0.95
        assert verdict.is_significant is True

    def test_custom_threshold(self):
        verdict = adjudicate_dsr(sharpe=0.1, num_trials=1, num_obs=101, skewness=0.0, kurtosis=0.0, threshold=0.80)
        assert verdict.threshold == pytest.approx(0.80)
        assert verdict.is_significant is True  # 0.84074 >= 0.80

    def test_skew_kurtosis_affect_var_sr(self):
        # 负偏度/厚尾放大 V[SR] -> 同等 Sharpe 下 DSR 更低
        base = adjudicate_dsr(sharpe=0.3, num_trials=1, num_obs=252, skewness=0.0, kurtosis=0.0)
        fat = adjudicate_dsr(sharpe=0.3, num_trials=1, num_obs=252, skewness=-0.5, kurtosis=4.0)
        assert fat.var_sr > base.var_sr
        assert fat.dsr < base.dsr

    def test_zero_variance_degenerate(self):
        # 构造 V[SR]<=0: 1-skew·SR+(kurt+2)/4·SR² = 1-3·1+(0+2)/4·1 = -1.5 < 0
        verdict = adjudicate_dsr(sharpe=1.0, num_trials=5, num_obs=100, skewness=3.0, kurtosis=0.0)
        assert verdict.var_sr <= 0.0
        assert verdict.dsr in (0.0, 1.0)

    def test_invalid_inputs_raise(self):
        with pytest.raises(OverfittingAdjudicationError):
            adjudicate_dsr(sharpe=0.3, num_trials=0, num_obs=252)
        with pytest.raises(OverfittingAdjudicationError):
            adjudicate_dsr(sharpe=0.3, num_trials=1, num_obs=1)
        with pytest.raises(OverfittingAdjudicationError):
            adjudicate_dsr(sharpe=float("nan"), num_trials=1, num_obs=252)


# ============== ③ 参数扰动 ±20% 收益稳定性 ==============


def _smooth_engine(params: dict[str, float]) -> float:
    """合成伪引擎: 高原型, 参数偏离基准 20% -> 绩效衰减 10%(手算锚点)。"""
    dev = abs(params["window"] - 20.0) / 20.0 + abs(params["thresh"] - 0.5) / 0.5
    return 2.0 * (1.0 - 0.5 * dev)


def _cliff_engine(params: dict[str, float]) -> float:
    """合成伪引擎: 悬崖型, 任何偏离基准 -> 绩效从 2.0 跌至 0.5。"""
    if params["window"] == 20.0 and params["thresh"] == 0.5:
        return 2.0
    return 0.5


class TestPerturbationStability:
    def test_smooth_plateau_decay_semantics(self):
        report = perturbation_stability({"window": 20.0, "thresh": 0.5}, _smooth_engine, pct=0.20, tolerance=0.30)
        assert isinstance(report, PerturbationStabilityReport)
        assert report.base_performance == pytest.approx(2.0)
        assert report.pct == pytest.approx(0.20)
        # one-at-a-time ±20%: 2 参数 × 2 方向 = 4 扰动点
        assert report.n_points == 4
        # 手算: 单参数扰动 dev=0.2 -> sharpe=2.0×(1-0.5×0.2)=1.8 -> 衰减率=(2-1.8)/2=0.1
        assert report.max_decay == pytest.approx(0.10)
        assert report.mean_decay == pytest.approx(0.10)
        # 全部扰动点衰减 0.1 <= 容忍 0.3 -> 稳健区间占比 100%
        assert report.robust_share == pytest.approx(1.0)
        assert report.is_stable is True

    def test_cliff_params_unstable(self):
        report = perturbation_stability({"window": 20.0, "thresh": 0.5}, _cliff_engine)
        # 衰减率=(2.0-0.5)/2.0=0.75 > 0.30 -> 稳健占比 0
        assert report.max_decay == pytest.approx(0.75)
        assert report.robust_share == pytest.approx(0.0)
        assert report.is_stable is False

    def test_improving_perturbation_negative_decay(self):
        # 扰动后绩效更好 -> 衰减率为负, 仍计入稳健区间
        def engine(params: dict[str, float]) -> float:
            return 2.0 + abs(params["window"] - 20.0)  # 偏离越远越好

        report = perturbation_stability({"window": 20.0}, engine, pct=0.20)
        assert report.max_decay < 0.0
        assert report.robust_share == pytest.approx(1.0)
        assert report.is_stable is True

    def test_min_robust_share_partial(self):
        # 一个参数稳定(decay=0.1), 一个参数悬崖(decay=0.75): 稳健占比 0.5
        def engine(params: dict[str, float]) -> float:
            w_dev = abs(params["window"] - 20.0) / 20.0
            t_dev = abs(params["thresh"] - 0.5) / 0.5
            sharpe = 2.0 * (1.0 - 0.5 * w_dev)
            if t_dev > 0:
                sharpe *= 0.25
            return sharpe

        report = perturbation_stability(
            {"window": 20.0, "thresh": 0.5}, engine, pct=0.20, tolerance=0.30, min_robust_share=0.5
        )
        assert report.n_points == 4
        assert report.robust_share == pytest.approx(0.5)
        assert report.is_stable is True  # 达到 min_robust_share=0.5
        report_strict = perturbation_stability(
            {"window": 20.0, "thresh": 0.5}, engine, pct=0.20, tolerance=0.30, min_robust_share=0.75
        )
        assert report_strict.is_stable is False

    def test_backtest_fn_called_with_perturbed_params(self):
        seen: list[dict[str, float]] = []

        def spy_engine(params: dict[str, float]) -> float:
            seen.append(dict(params))
            return 1.0

        perturbation_stability({"window": 20.0}, spy_engine, pct=0.20)
        # 基准 1 次 + ±20% 各 1 次
        assert seen.count({"window": 20.0}) == 1
        assert {"window": 24.0} in seen
        assert {"window": 16.0} in seen

    def test_invalid_inputs_raise(self):
        with pytest.raises(OverfittingAdjudicationError):
            perturbation_stability({}, _smooth_engine)
        with pytest.raises(OverfittingAdjudicationError):
            perturbation_stability({"window": 0.0}, _smooth_engine)  # 零值无法比例扰动
        with pytest.raises(OverfittingAdjudicationError):
            perturbation_stability({"window": 20.0}, _smooth_engine, pct=0.0)
        with pytest.raises(OverfittingAdjudicationError):
            perturbation_stability({"window": 20.0}, lambda p: 0.0)  # 基准绩效≈0 衰减率无定义


# ============== ④ 上线门禁挂钩点 + 综合裁定 ==============


class _RecordingHook:
    """合成门禁钩子: 记录收到的裁定报告(伪装成 Protocol 消费方)。"""

    def __init__(self) -> None:
        self.reports: list = []

    def on_adjudication(self, report) -> None:  # noqa: ANN001
        self.reports.append(report)


class TestGateHookAndAdjudicator:
    def _stable_inputs(self) -> dict:
        return {
            "walk_forward_folds": [(2.0, 1.8), (1.0, 0.9), (1.2, 1.1)],
            "dsr_kwargs": dict(sharpe=2.0, num_trials=1, num_obs=504, skewness=0.0, kurtosis=0.0),
            "perturbation_kwargs": dict(base_params={"window": 20.0, "thresh": 0.5}, backtest_fn=_smooth_engine),
        }

    def test_hook_protocol_structural(self):
        # Protocol 挂钩点: 鸭子类型满足即可注入
        assert isinstance(_RecordingHook(), OverfitGateHook)

    def test_hook_receives_report(self):
        hook = _RecordingHook()
        adjudicator = OverfittingAdjudicator()
        report = adjudicator.adjudicate(**self._stable_inputs(), gate_hook=hook)
        assert hook.reports == [report]

    def test_no_hook_default(self):
        # 挂钩点预留不接真门禁: gate_hook=None 不影响裁定产出
        report = OverfittingAdjudicator().adjudicate(**self._stable_inputs())
        assert report.is_overfitting is False
        assert report.reasons == ()
        assert report.walk_forward is not None
        assert report.dsr is not None
        assert report.perturbation is not None

    def test_any_check_failure_flags_overfitting(self):
        inputs = self._stable_inputs()
        inputs["dsr_kwargs"] = dict(sharpe=0.05, num_trials=1000, num_obs=252, skewness=0.0, kurtosis=0.0)
        report = OverfittingAdjudicator().adjudicate(**inputs)
        assert report.is_overfitting is True
        assert any("DSR" in r for r in report.reasons)

    def test_walk_forward_failure_reason(self):
        inputs = self._stable_inputs()
        inputs["walk_forward_folds"] = [(2.0, 0.5)]  # ratio=0.25 < 0.70
        report = OverfittingAdjudicator().adjudicate(**inputs)
        assert report.is_overfitting is True
        assert any("walk-forward" in r.lower() or "Walk-Forward" in r for r in report.reasons)

    def test_perturbation_failure_reason(self):
        inputs = self._stable_inputs()
        inputs["perturbation_kwargs"] = dict(base_params={"window": 20.0, "thresh": 0.5}, backtest_fn=_cliff_engine)
        report = OverfittingAdjudicator().adjudicate(**inputs)
        assert report.is_overfitting is True
        assert any("扰动" in r for r in report.reasons)

    def test_partial_checks_allowed(self):
        # 只跑 DSR 单检验器
        report = OverfittingAdjudicator().adjudicate(
            dsr_kwargs=dict(sharpe=2.0, num_trials=1, num_obs=504, skewness=0.0, kurtosis=0.0)
        )
        assert report.walk_forward is None
        assert report.perturbation is None
        assert report.is_overfitting is False
