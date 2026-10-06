# [A_test] module_id: MOD-GOV_test_strategy_correlation_pipeline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-PF-015 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/23_strategy_correlation_validation.md | §
# [MODULE] tests.pf_core.test_strategy_correlation_pipeline
# [TESTS] src/zephyr/pf_core/strategy_correlation_pipeline.py
# [TTL] task_bound
"""G07 策略间相关性验证管线合成数据测试（全部不依赖真实 PnL 序列）。

裁定真源：23_strategy_correlation_validation.md §3.1⑤——
  七部分报告模板 / 0.6 战略级 / 0.85/0.90 运营级互补 / BM-SEL-23-B 5 阶段分层 /
  双矩阵(Pearson+Spearman)/ bootstrap 2000× / LW+Neff / CUSUM-PSI 漂移。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.pf_core.strategy_correlation_pipeline import (
    DEFAULT_NEFF_MIN,
    DEFAULT_STRATEGIC_THRESHOLD,
    ORTHOGONAL_DIMENSIONS,
    ConclusionSection,
    OrthogonalitySection,
    StrategyCorrelationParams,
    StrategyCorrelationReport,
    render_markdown,
    run_strategy_correlation_pipeline,
)

# ── synthetic fixtures ──────────────────────────────────────────────────────


def _make_dates(n: int, freq: str = "B") -> pd.DatetimeIndex:
    return pd.bdate_range(end="2026-08-30", periods=n, freq=freq)


def _make_returns(n: int, strategies: list[str], rho: float, seed: int = 42) -> pd.DataFrame:
    """构造日收益率面板（均值0、方差0.0004≈年化10%波动率），给定两两相关 rho。

    先生成协方差矩阵 Σ，cholesky 分解→独立正态乘积→相关系数矩阵
    精确收敛到 rho（大样本）。
    """
    rng = np.random.default_rng(seed)
    k = len(strategies)
    cov = np.full((k, k), rho * 0.0004) + np.eye(k) * (1 - rho) * 0.0004
    r = rng.multivariate_normal(np.zeros(k), cov, size=n)
    return pd.DataFrame(r, index=_make_dates(n), columns=strategies)


def _make_phase_labels(n: int) -> pd.Series:
    """构造 n 日硬标签（BM-SEL-23-B 五阶段循环，等频分配）。"""
    phases = list(("冰点", "反核", "主升", "疯狂", "退潮"))
    labels = [phases[i % 5] for i in range(n)]
    return pd.Series(labels, index=_make_dates(n))


def _make_grayscale_map(n: int) -> dict[pd.Timestamp, dict]:
    """构造灰度结果映射（duck-typed，Timestamp 键与面板 DatetimeIndex 可交集）。"""
    phases = ("冰点", "反核", "主升", "疯狂", "退潮")
    dates = _make_dates(n)
    out: dict[pd.Timestamp, dict] = {}
    for i, d in enumerate(dates):
        dom = phases[i % 5]
        prob = {p: (0.45 if p == dom else 0.1375) for p in phases}
        out[d] = {"dominant_phase": dom, "confidence": 0.80, "phase_prob": prob}
    return out


class TestPipelineBasics:
    def test_basic_run_no_optional(self) -> None:
        """无分层/无 bootstrap/无漂移/无留口：七部分降维到 1+4+5，不抛错。"""
        r = _make_returns(100, ["S1", "S2", "S3"], rho=0.1)
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(
                run_bootstrap=False, run_drift=False, overfit_audits=None, dimension_map=None
            ),
        )
        assert isinstance(rep, StrategyCorrelationReport)
        # 对数收益率首期丢弃 → 面板 T = 输入 T - 1
        assert rep.part1_full_sample.n_obs == 99
        assert rep.part1_full_sample.strategies == ("S1", "S2", "S3")
        assert rep.part2_stratified is None
        assert rep.part3_bootstrap_ci is None
        assert rep.part4_neff.n_assets == 3
        assert rep.part6_overfitting is None
        assert rep.part7_orthogonality is None
        assert rep.drift_monitoring is None
        # 低相关 → PASS
        assert rep.part5_conclusion.verdict == "PASS"
        assert not rep.part5_conclusion.triggers
        assert rep.part5_conclusion.max_pairs_per_phase is None
        assert rep.meta["n_strategies"] == 3
        # 渲染不抛错
        md = render_markdown(rep)
        assert "## 1. 全样本" in md
        assert "## 2. 情绪周期" in md
        assert "## 3. block-bootstrap" in md
        assert "## 4. 组合层有效下注数" in md
        assert "## 5. 结论" in md
        assert "## 6. 过拟合检测" in md
        assert "## 7. 策略组合正交性" in md

    def test_high_correlation_passes(self) -> None:
        """高度相关(ρ=0.8) → 结论触发 REVIEW_REQUIRED。"""
        r = _make_returns(200, ["A", "B", "C"], rho=0.8)
        rep = run_strategy_correlation_pipeline(
            r, params=StrategyCorrelationParams(run_bootstrap=False, run_drift=False)
        )
        assert rep.part5_conclusion.verdict == "REVIEW_REQUIRED"
        triggers = set(rep.part5_conclusion.triggers)
        assert "max_pairwise>0.6" in triggers
        assert rep.part5_conclusion.neff < DEFAULT_NEFF_MIN
        assert "neff<3.0" in triggers

    def test_negative_returns_guard(self) -> None:
        """单日收益率 <= -1（对数无定义）应抛 ValueError。"""
        r = _make_returns(30, ["A", "B"], rho=0.0)
        r.iloc[5, 0] = -2.0
        with pytest.raises(ValueError):
            run_strategy_correlation_pipeline(r, params=StrategyCorrelationParams(run_bootstrap=False, run_drift=False))

    def test_empty_or_too_few_columns(self) -> None:
        """空/单列应抛 ValueError。"""
        with pytest.raises(ValueError):
            run_strategy_correlation_pipeline(pd.DataFrame())
        with pytest.raises(ValueError):
            run_strategy_correlation_pipeline(
                pd.DataFrame({"A": [0.01]}),
                params=StrategyCorrelationParams(run_bootstrap=False, run_drift=False),
            )


class TestStratifiedSection:
    def test_hard_labels(self) -> None:
        """提供 phase_labels（硬标签）路径：5 阶段全量返回，等频分每阶段 20 日。"""
        n = 120
        r = _make_returns(n, ["X", "Y"], rho=0.3)
        labels = _make_phase_labels(n)
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(phase_labels=labels, run_bootstrap=False, run_drift=False),
        )
        p2 = rep.part2_stratified
        assert p2 is not None
        assert p2.fallback_count == 0
        assert len(p2.phases) == 5
        # 等频 120/5=24 日，对数收益率首期丢弃 → 冰点 23、其余 24
        for sec in p2.phases:
            assert sec.phase in ("冰点", "反核", "主升", "疯狂", "退潮")
            assert sec.n_obs in (23, 24)
            assert not sec.sufficient  # < MIN_PHASE_SAMPLES(30)
            assert sec.spearman is None
        assert sum(sec.n_obs for sec in p2.phases) == n - 1

    def test_grayscale_path(self) -> None:
        """grayscale_map 路径与 phase_labels 路径结果一致（等频构造）。"""
        n = 120
        r = _make_returns(n, ["X", "Y"], rho=0.3)
        rep_label = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(phase_labels=_make_phase_labels(n), run_bootstrap=False, run_drift=False),
        )
        rep_gray = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(
                grayscale_map=_make_grayscale_map(n), run_bootstrap=False, run_drift=False
            ),
        )
        p2_l = rep_label.part2_stratified
        p2_g = rep_gray.part2_stratified
        assert p2_l is not None and p2_g is not None
        assert p2_l.fallback_count == 0
        assert p2_g.fallback_count == 0
        assert [s.phase for s in p2_l.phases] == [s.phase for s in p2_g.phases]

    def test_low_confidence_fallback(self) -> None:
        """置信度低于阈值 → 兜底计数>0。"""
        n = 60
        r = _make_returns(n, ["X", "Y"], rho=0.3)
        labels = _make_phase_labels(n)
        # 构造 50% 低置信度
        conf = pd.Series(0.5, index=labels.index)
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(
                phase_labels=labels,
                phase_confidences=conf,
                confidence_threshold=0.6,
                run_bootstrap=False,
                run_drift=False,
            ),
        )
        assert rep.part2_stratified is not None
        assert rep.part2_stratified.fallback_count > 0

    def test_mutual_exclusivity_error(self) -> None:
        """phase_labels 与 grayscale_map 同时给 → ValueError。"""
        r = _make_returns(60, ["X", "Y"], rho=0.3)
        with pytest.raises(ValueError, match="互斥"):
            run_strategy_correlation_pipeline(
                r,
                params=StrategyCorrelationParams(
                    phase_labels=_make_phase_labels(60),
                    grayscale_map=_make_grayscale_map(60),
                    run_bootstrap=False,
                    run_drift=False,
                ),
            )


class TestBootstrapCI:
    def test_bootstrap_runs(self) -> None:
        """bootstrap 开启、样本够 → part3 不为 None。"""
        r = _make_returns(250, ["S1", "S2", "S3"], rho=0.2)
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(run_bootstrap=True, n_bootstrap=500, seed=1, run_drift=False),
        )
        assert rep.part3_bootstrap_ci is not None
        b = rep.part3_bootstrap_ci
        assert b.n_bootstrap == 500
        assert b.n_obs == 249  # 对数收益率首期丢弃
        assert b.threshold == DEFAULT_STRATEGIC_THRESHOLD
        # Spearman 对有三条
        assert len(b.spearman) == 3
        assert len(b.pearson) == 3
        for pair, ci in b.spearman.items():
            assert -1 <= ci.point <= 1
            assert ci.ci_lower <= ci.ci_upper
            assert 0 <= ci.prob_above_threshold <= 1

    def test_bootstrap_skipped_when_too_small(self) -> None:
        """样本 < BOOTSTRAP_MIN_OBS(8) → part3 降级为 None 不抛错。"""
        r = _make_returns(6, ["S1", "S2"], rho=0.1)
        rep = run_strategy_correlation_pipeline(
            r, params=StrategyCorrelationParams(run_bootstrap=True, run_drift=False)
        )
        assert rep.part3_bootstrap_ci is None


class TestDriftMonitoring:
    def test_drift_runs(self) -> None:
        """drift 开启、样本够 → drift_monitoring 逐对报告结构齐备。"""
        n = 200
        r = _make_returns(n, ["A", "B"], rho=0.3)
        rep = run_strategy_correlation_pipeline(
            r, params=StrategyCorrelationParams(run_drift=True, run_bootstrap=False)
        )
        assert rep.drift_monitoring is not None
        assert len(rep.drift_monitoring) == 1
        assert ("A", "B") in rep.drift_monitoring
        dr = rep.drift_monitoring[("A", "B")]
        assert not dr.cusum.degraded
        assert len(dr.cusum.s_plus) == n - 1
        # PSI 双分布齐备（滚动窗口 63 后有 137 个有效 ρ，基线/近期可切）
        assert dr.psi is not None

    def test_drift_detects_regime_shift(self) -> None:
        """相关性结构断点（前半独立、后半高相关）→ CUSUM 告警 + PSI ALERT。

        注：仅断言漂移对检出（pipeline 编排职责）；"平稳序列不告警"的虚警率
        行为归 tests/factor/test_correlation_drift_monitor.py 覆盖，不在此重复
        （随机噪声上的不告警断言本质脆弱）。
        """
        n = 300
        split = 160
        rng = np.random.default_rng(11)
        f = rng.normal(0.0, 1.0, n)
        e1 = rng.normal(0.0, 1.0, n)
        e2 = rng.normal(0.0, 1.0, n)
        e3 = rng.normal(0.0, 1.0, n)
        # A/B 前半独立、后半同因子高相关(ρ≈0.96)；尺度统一 0.01；C 全程独立对照
        a = np.concatenate([e1[:split], 0.98 * f[split:] + 0.2 * e1[split:]]) * 0.01
        b = np.concatenate([e2[:split], 0.98 * f[split:] + 0.2 * e2[split:]]) * 0.01
        c = e3 * 0.01
        r = pd.DataFrame({"A": a, "B": b, "C": c}, index=_make_dates(n))
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(
                run_bootstrap=False, run_drift=True, drift_window=20, drift_recent_window=40
            ),
        )
        assert rep.drift_monitoring is not None
        assert set(rep.drift_monitoring.keys()) == {("A", "B"), ("A", "C"), ("B", "C")}
        drift_ab = rep.drift_monitoring[("A", "B")]
        # 140 日 ρ≈0.96 长尾 → CUSUM 确定性告警；PSI 分布断裂 → ALERT
        assert drift_ab.cusum.alarm is True
        assert drift_ab.drift_detected is True

    def test_drift_skipped_when_too_small(self) -> None:
        """样本不足窗口+2 → drift 降级为 None。"""
        r = _make_returns(30, ["A", "B"], rho=0.3)
        rep = run_strategy_correlation_pipeline(
            r, params=StrategyCorrelationParams(run_drift=True, run_bootstrap=False)
        )
        assert rep.drift_monitoring is None


class TestConclusion:
    def test_neff_caveat(self) -> None:
        """α>0.5 + Neff>=3 → alpha_caveat 为 True（memo v1.4.1 自洽性）。"""
        # 极端高相关构造 cholesky + 短样本 → 噪声大，LW α 偏大
        r = _make_returns(150, ["A", "B", "C", "D"], rho=0.95)
        rep = run_strategy_correlation_pipeline(
            r, params=StrategyCorrelationParams(run_bootstrap=False, run_drift=False)
        )
        c = rep.part5_conclusion
        assert c.verdict == "REVIEW_REQUIRED"
        if c.lw_alpha > 0.5:
            assert c.alpha_caveat is True

    def test_trigger_max_pairwise(self) -> None:
        """最大两两 >threshold 触发。"""
        r = _make_returns(100, ["A", "B", "C"], rho=0.7)
        rep = run_strategy_correlation_pipeline(
            r, params=StrategyCorrelationParams(run_bootstrap=False, run_drift=False)
        )
        assert "max_pairwise>0.6" in rep.part5_conclusion.triggers

    def test_trigger_phase_pairs(self) -> None:
        """分层高相关对数>=3 触发（需满足样本充足）。"""
        n = 500
        r = _make_returns(n, ["A", "B", "C", "D"], rho=0.75)
        labels = _make_phase_labels(n)
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(phase_labels=labels, run_bootstrap=False, run_drift=False),
        )
        assert rep.part5_conclusion.max_pairs_per_phase is not None
        assert rep.part5_conclusion.max_pairs_per_phase >= 3
        assert "phase_pairs>=3" in rep.part5_conclusion.triggers


class TestOrthogonality:
    def test_full_coverage(self) -> None:
        """四策略覆盖三维度 → 不退化。"""
        dim = {"A": "趋势方向", "B": "执行时机", "C": "风险大小", "D": "趋势方向"}
        o = OrthogonalitySection(dim, ("趋势方向", "执行时机", "风险大小"), (), False, "")
        assert not o.degenerate

    def test_degenerate_one_dim(self) -> None:
        """只覆盖一维度 → 退化。"""
        dim = {"A": "趋势方向", "B": "趋势方向"}
        o = OrthogonalitySection(dim, ("趋势方向",), ("执行时机", "风险大小"), True, "")
        assert o.degenerate

    def test_invalid_dimension_raises(self) -> None:
        """非法维度 → ValueError。"""
        with pytest.raises(ValueError):
            from zephyr.pf_core.strategy_correlation_pipeline import _build_orthogonality

            _build_orthogonality({"A": "invalid"})

    def test_integration_dimension_map(self) -> None:
        """dimension_map 走完整管线 → part7 不为 None。"""
        r = _make_returns(100, ["A", "B", "C"], rho=0.1)
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(
                run_bootstrap=False,
                run_drift=False,
                dimension_map={"A": "趋势方向", "B": "执行时机", "C": "风险大小"},
            ),
        )
        assert rep.part7_orthogonality is not None
        assert not rep.part7_orthogonality.degenerate


class TestRenderMarkdown:
    def test_render_contains_all_parts(self) -> None:
        """完整管线渲染 markdown 覆盖全部七部分。"""
        n = 300
        r = _make_returns(n, ["S1", "S2", "S3"], rho=0.2)
        rep = run_strategy_correlation_pipeline(
            r,
            params=StrategyCorrelationParams(
                phase_labels=_make_phase_labels(n),
                run_bootstrap=True,
                n_bootstrap=200,
                seed=7,
                run_drift=True,
                overfit_audits=None,
                dimension_map={"S1": "趋势方向", "S2": "执行时机", "S3": "风险大小"},
            ),
        )
        md = render_markdown(rep)
        assert "G07 策略间相关性验证报告" in md
        assert "Neff=(Σλ)²/Σλ²" in md
        assert "LW 收缩强度" in md
        assert "情绪周期" in md
        assert "block-bootstrap" in md
        assert "结论" in md
        assert "过拟合检测" in md
        assert "正交性" in md
        assert "漂移监控" in md
