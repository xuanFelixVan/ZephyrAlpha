"""Performance Attribution Engine 测试 (MOD-PF-007 / PC-10)

覆盖: Brinson 三因子守恒、因子归因、风险归因(RK-16 复用)、IC 衰减降级、
拥挤检测、OCP 契约实现、退化场景(空/单标的)、幂等性、多期归因。
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
import pytest

from zephyr.pf_core.core.performance_attribution_engine import (
    AttributionContext,
    AttributionDataIncompleteError,
    BrinsonResult,
    CrowdingDetection,
    CrowdingLevel,
    DegradationDetection,
    ICDecayDetectionError,
    PerformanceAttributionEngine,
    RiskDecompositionUnavailable,
    SegmentReturn,
)
from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)

# ──────────────────────────────────────────────────────────────────────────────
# 辅助
# ──────────────────────────────────────────────────────────────────────────────


def _engine(**kwargs) -> PerformanceAttributionEngine:
    return PerformanceAttributionEngine(**kwargs)


def _seg(
    name: str,
    wp: float,
    wb: float,
    rp: float,
    rb: float,
) -> SegmentReturn:
    return SegmentReturn(name, wp, wb, rp, rb)


# ──────────────────────────────────────────────────────────────────────────────
# Brinson 三因子
# ──────────────────────────────────────────────────────────────────────────────


class TestBrinsonAttribution:
    """Brinson-Fachler 三因子归因。"""

    def test_three_factor_conservation(self):
        """守恒: allocation + selection + interaction == excess_return。"""
        engine = _engine()
        segments = [
            _seg("科技", 0.40, 0.30, 0.05, 0.03),
            _seg("金融", 0.60, 0.70, 0.02, 0.01),
        ]
        result = engine.brinson_attribute(segments)

        total = result.allocation_effect + result.selection_effect + result.interaction_effect
        assert math.isclose(total, result.excess_return, abs_tol=1e-12)
        assert result.is_consistent

    def test_excess_equals_portfolio_minus_benchmark(self):
        """excess_return == portfolio_return - benchmark_return。"""
        engine = _engine()
        segments = [
            _seg("A", 0.50, 0.40, 0.10, 0.06),
            _seg("B", 0.50, 0.60, 0.04, 0.02),
        ]
        result = engine.brinson_attribute(segments)
        excess = result.portfolio_return - result.benchmark_return
        assert math.isclose(result.excess_return, excess, abs_tol=1e-12)

    def test_allocation_effect_positive_when_overweight_winner(self):
        """超配上涨行业 → 配置效应为正。"""
        engine = _engine()
        segments = [_seg("科技", 0.60, 0.40, 0.08, 0.08)]
        result = engine.brinson_attribute(segments)
        # allocation = (0.6-0.4) * 0.08 = 0.016
        assert math.isclose(result.allocation_effect, 0.016, abs_tol=1e-9)
        assert result.allocation_effect > 0

    def test_selection_effect_positive_when_better_picks(self):
        """组合选股优于基准 → 选择效应为正。"""
        engine = _engine()
        segments = [_seg("金融", 0.50, 0.50, 0.06, 0.02)]
        result = engine.brinson_attribute(segments)
        # selection = 0.5 * (0.06 - 0.02) = 0.02
        assert math.isclose(result.selection_effect, 0.02, abs_tol=1e-9)
        assert result.selection_effect > 0

    def test_interaction_effect(self):
        """交互效应 = (w_p-w_b) × (r_p-r_b)。"""
        engine = _engine()
        segments = [_seg("X", 0.60, 0.40, 0.05, 0.02)]
        result = engine.brinson_attribute(segments)
        # interaction = (0.6-0.4) * (0.05-0.02) = 0.2 * 0.03 = 0.006
        assert math.isclose(result.interaction_effect, 0.006, abs_tol=1e-9)

    def test_equal_weights_zero_excess(self):
        """组合与基准完全一致 → 三因子全零。"""
        engine = _engine()
        segments = [
            _seg("A", 0.50, 0.50, 0.03, 0.03),
            _seg("B", 0.50, 0.50, 0.02, 0.02),
        ]
        result = engine.brinson_attribute(segments)
        assert math.isclose(result.allocation_effect, 0.0, abs_tol=1e-12)
        assert math.isclose(result.selection_effect, 0.0, abs_tol=1e-12)
        assert math.isclose(result.interaction_effect, 0.0, abs_tol=1e-12)
        assert math.isclose(result.excess_return, 0.0, abs_tol=1e-12)

    def test_empty_segments_raises(self):
        """空分段 → AttributionDataIncompleteError。"""
        engine = _engine()
        with pytest.raises(AttributionDataIncompleteError, match="empty"):
            engine.brinson_attribute([])

    def test_negative_weight_raises(self):
        """负权重 → AttributionDataIncompleteError。"""
        engine = _engine()
        with pytest.raises(AttributionDataIncompleteError, match="negative"):
            engine.brinson_attribute([_seg("A", -0.1, 0.5, 0.01, 0.01)])

    def test_single_segment(self):
        """单分段也能正确归因。"""
        engine = _engine()
        seg = _seg("only", 0.80, 0.50, 0.10, 0.04)
        result = engine.brinson_attribute([seg])
        # allocation = (0.8-0.5)*0.04 = 0.012
        # selection = 0.5*(0.10-0.04) = 0.03
        # interaction = (0.8-0.5)*(0.10-0.04) = 0.018
        assert math.isclose(result.allocation_effect, 0.012, abs_tol=1e-9)
        assert math.isclose(result.selection_effect, 0.03, abs_tol=1e-9)
        assert math.isclose(result.interaction_effect, 0.018, abs_tol=1e-9)

    def test_portfolio_and_benchmark_return(self):
        """portfolio_return = Σ w_p × r_p; benchmark_return = Σ w_b × r_b。"""
        engine = _engine()
        segments = [
            _seg("A", 0.30, 0.20, 0.10, 0.05),
            _seg("B", 0.70, 0.80, 0.02, 0.01),
        ]
        result = engine.brinson_attribute(segments)
        # portfolio = 0.3*0.1 + 0.7*0.02 = 0.03 + 0.014 = 0.044
        # benchmark = 0.2*0.05 + 0.8*0.01 = 0.01 + 0.008 = 0.018
        assert math.isclose(result.portfolio_return, 0.044, abs_tol=1e-9)
        assert math.isclose(result.benchmark_return, 0.018, abs_tol=1e-9)

    def test_segments_preserved(self):
        """结果中保留输入分段。"""
        engine = _engine()
        segs = [_seg("A", 0.5, 0.5, 0.01, 0.01), _seg("B", 0.5, 0.5, 0.02, 0.02)]
        result = engine.brinson_attribute(segs)
        assert len(result.segments) == 2
        assert result.segments[0].segment == "A"


# ──────────────────────────────────────────────────────────────────────────────
# 因子归因
# ──────────────────────────────────────────────────────────────────────────────


class TestFactorAttribution:
    """因子归因。"""

    def test_single_factor_single_asset(self):
        """单因子单标的: contribution = w × exposure × factor_return。"""
        engine = _engine()
        weights = {"A": 0.50}
        exposures = {"A": {"momentum": 1.2}}
        factor_returns = {"momentum": 0.03}
        contrib = engine.factor_attribute(weights, exposures, factor_returns)
        # 0.5 * 1.2 * 0.03 = 0.018
        assert math.isclose(contrib["momentum"], 0.018, abs_tol=1e-9)

    def test_multi_factor_multi_asset(self):
        """多因子多标的。"""
        engine = _engine()
        weights = {"A": 0.60, "B": 0.40}
        exposures = {
            "A": {"momentum": 1.0, "value": -0.5},
            "B": {"momentum": 0.5, "value": 1.0},
        }
        factor_returns = {"momentum": 0.02, "value": 0.01}
        contrib = engine.factor_attribute(weights, exposures, factor_returns)
        # momentum: 0.6*1.0*0.02 + 0.4*0.5*0.02 = 0.012 + 0.004 = 0.016
        # value: 0.6*(-0.5)*0.01 + 0.4*1.0*0.01 = -0.003 + 0.004 = 0.001
        assert math.isclose(contrib["momentum"], 0.016, abs_tol=1e-9)
        assert math.isclose(contrib["value"], 0.001, abs_tol=1e-9)

    def test_missing_exposure_treated_as_zero(self):
        """标的缺少因子暴露 → 贡献为 0 (不报错)。"""
        engine = _engine()
        weights = {"A": 1.0, "B": 0.0}
        exposures = {"A": {"f1": 1.0}}  # B 无暴露
        factor_returns = {"f1": 0.05}
        contrib = engine.factor_attribute(weights, exposures, factor_returns)
        assert math.isclose(contrib["f1"], 0.05, abs_tol=1e-9)

    def test_empty_inputs(self):
        """空输入 → 空字典。"""
        engine = _engine()
        contrib = engine.factor_attribute({}, {}, {})
        assert contrib == {}


# ──────────────────────────────────────────────────────────────────────────────
# 风险归因 (复用 MOD-RK-16)
# ──────────────────────────────────────────────────────────────────────────────


class TestRiskAttribution:
    """风险归因 (复用 RiskDecomposer)。"""

    def test_basic_risk_decomposition(self):
        """基础风险分解 → MCR/CCR 守恒。"""
        engine = _engine()
        cov = np.array([[0.04, 0.01], [0.01, 0.09]])
        weights = np.array([0.6, 0.4])
        result = engine.risk_attribute(cov, weights)
        # ΣCCR = σ_p (守恒)
        assert math.isclose(float(np.sum(result.ccr)), result.total_risk, abs_tol=1e-9)
        assert result.total_risk > 0

    def test_dict_weights(self):
        """字典权重 → 正确分解。"""
        engine = _engine()
        cov = np.array([[0.04, 0.01], [0.01, 0.09]])
        weights = {"A": 0.6, "B": 0.4}
        result = engine.risk_attribute(cov, weights, assets=["A", "B"])
        assert result.assets == ["A", "B"]
        assert math.isclose(float(np.sum(result.ccr)), result.total_risk, abs_tol=1e-9)

    def test_invalid_cov_raises(self):
        """非方阵协方差 → RiskDecompositionUnavailable。"""
        engine = _engine()
        bad_cov = np.array([[0.04, 0.01, 0.02]])
        with pytest.raises(RiskDecompositionUnavailable):
            engine.risk_attribute(bad_cov, np.array([0.5, 0.5, 0.0]))


# ──────────────────────────────────────────────────────────────────────────────
# 策略降级检测
# ──────────────────────────────────────────────────────────────────────────────


class TestDegradationDetection:
    """IC 衰减降级检测。"""

    def test_no_degradation_when_ic_stable(self):
        """IC 无衰减 → 不降级。"""
        engine = _engine()
        deg = engine.detect_degradation("S1", baseline_ic=0.08, recent_ic=0.075)
        assert not deg.degraded
        assert deg.recommended_weight == 1.0
        # decay = (0.08-0.075)/0.08 = 0.0625 = 6.25%
        assert math.isclose(deg.ic_decay_pct, 0.0625, abs_tol=1e-6)

    def test_degradation_when_ic_decays_over_50pct(self):
        """IC 衰减 >50% → 降级, 权重归零。"""
        engine = _engine()
        deg = engine.detect_degradation("S1", baseline_ic=0.10, recent_ic=0.04)
        # decay = (0.10-0.04)/0.10 = 0.60 = 60%
        assert deg.degraded
        assert deg.recommended_weight == 0.0
        assert math.isclose(deg.ic_decay_pct, 0.60, abs_tol=1e-6)

    def test_degradation_boundary_exactly_50pct(self):
        """IC 衰减恰为 50% → 不降级 (严格 >)。"""
        engine = _engine()
        deg = engine.detect_degradation("S1", baseline_ic=0.10, recent_ic=0.05)
        assert not deg.degraded  # 50% 不触发 (需 > 50%)

    def test_degradation_ic_improves(self):
        """IC 改善 → 衰减为负, 不降级。"""
        engine = _engine()
        deg = engine.detect_degradation("S1", baseline_ic=0.05, recent_ic=0.08)
        assert not deg.degraded
        assert deg.ic_decay_pct < 0

    def test_baseline_zero_marks_degraded(self):
        """baseline_ic ≤ 0 → 直接标记降级。"""
        engine = _engine()
        deg = engine.detect_degradation("S1", baseline_ic=0.0, recent_ic=0.0)
        assert deg.degraded
        assert deg.recommended_weight == 0.0

    def test_baseline_negative_marks_degraded(self):
        """baseline_ic 负值 → 降级。"""
        engine = _engine()
        deg = engine.detect_degradation("S1", baseline_ic=-0.02, recent_ic=0.01)
        assert deg.degraded

    def test_custom_threshold(self):
        """自定义阈值 (30%)。"""
        engine = _engine(ic_decay_threshold=0.30)
        # decay = (0.10-0.06)/0.10 = 40% > 30% → 降级
        deg = engine.detect_degradation("S1", baseline_ic=0.10, recent_ic=0.06)
        assert deg.degraded

    def test_strategy_id_preserved(self):
        """策略 ID 保留。"""
        engine = _engine()
        deg = engine.detect_degradation("MY-STRAT", baseline_ic=0.05, recent_ic=0.01)
        assert deg.strategy_id == "MY-STRAT"


# ──────────────────────────────────────────────────────────────────────────────
# 拥挤检测
# ──────────────────────────────────────────────────────────────────────────────


class TestCrowdingDetection:
    """策略拥挤检测。"""

    def test_no_crowding(self):
        """ρ ≤ 0.8 → NONE, scale=1.0。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {"S2": 0.5, "S3": 0.3})
        assert det.crowding_level == CrowdingLevel.NONE
        assert det.recommended_weight_scale == 1.0
        assert det.max_correlation == 0.5

    def test_warn_crowding(self):
        """0.8 < ρ ≤ 0.9 → WARN, scale=0.5。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {"S2": 0.85, "S3": 0.3})
        assert det.crowding_level == CrowdingLevel.WARN
        assert det.recommended_weight_scale == 0.5
        assert det.crowded_with == "S2"

    def test_severe_crowding(self):
        """ρ > 0.9 → SEVERE, scale=0.0。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {"S2": 0.95, "S3": 0.3})
        assert det.crowding_level == CrowdingLevel.SEVERE
        assert det.recommended_weight_scale == 0.0

    def test_negative_correlation_uses_abs(self):
        """负相关取绝对值。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {"S2": -0.92})
        assert det.crowding_level == CrowdingLevel.SEVERE
        assert det.max_correlation == 0.92

    def test_empty_correlations(self):
        """空相关性 → NONE。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {})
        assert det.crowding_level == CrowdingLevel.NONE
        assert det.max_correlation == 0.0
        assert det.crowded_with == ""

    def test_boundary_exactly_0_8(self):
        """ρ=0.8 → NONE (严格 >)。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {"S2": 0.80})
        assert det.crowding_level == CrowdingLevel.NONE

    def test_boundary_exactly_0_9(self):
        """ρ=0.9 → WARN (严格 > 0.9 才 SEVERE)。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {"S2": 0.90})
        assert det.crowding_level == CrowdingLevel.WARN

    def test_finds_max_correlation(self):
        """找到最大相关性对手。"""
        engine = _engine()
        det = engine.detect_crowding("S1", {"S2": 0.3, "S3": 0.88, "S4": 0.5})
        assert det.crowded_with == "S3"
        assert math.isclose(det.max_correlation, 0.88, abs_tol=1e-9)


# ──────────────────────────────────────────────────────────────────────────────
# OCP 契约 + 完整归因
# ──────────────────────────────────────────────────────────────────────────────


class TestOCPContractAndFullAttribution:
    """OCP 契约实现 + 完整归因。"""

    def test_is_attribution_engine_base(self):
        """引擎是 AttributionEngineBase 子类 (OCP 契约)。"""
        from zephyr.reporting.analytics_base import AttributionEngineBase

        engine = _engine()
        assert isinstance(engine, AttributionEngineBase)

    def test_attribute_without_context_raises(self):
        """未注入上下文 → AttributionDataIncompleteError。"""
        engine = _engine()
        with pytest.raises(AttributionDataIncompleteError, match="set_context"):
            engine.attribute("PF-1", "2026-01-01", "2026-03-31", "key-1")

    def test_attribute_with_context(self):
        """通过 set_context + attribute() OCP 路径。"""
        engine = _engine()
        segments = [_seg("A", 0.60, 0.40, 0.05, 0.03)]
        ctx = AttributionContext(segments=segments, portfolio_id="PF-1")
        engine.set_context(ctx)
        report = engine.attribute("PF-1", "2026-01-01", "2026-03-31", "key-1")
        assert isinstance(report, PerformanceAttributionReport)
        assert report.portfolio_id == "PF-1"
        assert report.idempotency_key == "key-1"

    def test_attribute_full_basic(self):
        """完整归因基本流程。"""
        engine = _engine()
        segments = [
            _seg("科技", 0.40, 0.30, 0.05, 0.03),
            _seg("金融", 0.60, 0.70, 0.02, 0.01),
        ]
        report = engine.attribute_full(
            portfolio_id="PF-1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            idempotency_key="attr-q1-001",
            segments=segments,
            transaction_cost_drag=0.002,
        )
        assert isinstance(report, PerformanceAttributionReport)
        assert report.portfolio_id == "PF-1"
        assert report.period_start == "2026-01-01"
        assert report.period_end == "2026-03-31"
        assert report.idempotency_key == "attr-q1-001"
        assert report.schema_version == "1.0"
        # total_return = excess - cost_drag
        excess = report.allocation_effect + report.selection_effect + report.interaction_effect
        assert math.isclose(report.total_return, excess - 0.002, abs_tol=1e-9)
        assert report.transaction_cost_drag == 0.002

    def test_attribute_full_with_factors(self):
        """完整归因 + 因子归因。"""
        engine = _engine()
        segments = [_seg("A", 0.50, 0.50, 0.04, 0.02)]
        weights = {"X": 0.50, "Y": 0.50}
        exposures = {"X": {"mom": 1.0}, "Y": {"mom": 0.5}}
        factor_returns = {"mom": 0.02}
        report = engine.attribute_full(
            portfolio_id="PF-1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            idempotency_key="attr-002",
            segments=segments,
            weights=weights,
            factor_exposures=exposures,
            factor_returns=factor_returns,
        )
        # mom contribution = 0.5*1.0*0.02 + 0.5*0.5*0.02 = 0.01 + 0.005 = 0.015
        assert math.isclose(report.factor_contributions["mom"], 0.015, abs_tol=1e-9)

    def test_attribute_full_with_risk(self):
        """完整归因 + 风险归因 (不报错)。"""
        engine = _engine()
        segments = [_seg("A", 0.50, 0.50, 0.04, 0.02)]
        cov = np.array([[0.04, 0.01], [0.01, 0.09]])
        weights = {"X": 0.6, "Y": 0.4}
        report = engine.attribute_full(
            portfolio_id="PF-1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            idempotency_key="attr-003",
            segments=segments,
            weights=weights,
            covariance=cov,
            assets=["X", "Y"],
        )
        assert isinstance(report, PerformanceAttributionReport)

    def test_attribute_full_risk_failure_graceful(self):
        """风险归因失败 → 降级跳过, 不影响报告产出。"""
        engine = _engine()
        segments = [_seg("A", 0.50, 0.50, 0.04, 0.02)]
        bad_cov = np.array([[0.04, 0.01, 0.02]])  # 非方阵
        report = engine.attribute_full(
            portfolio_id="PF-1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            idempotency_key="attr-004",
            segments=segments,
            covariance=bad_cov,
            weights={"X": 1.0},
        )
        # 风险归因失败但报告仍产出
        assert isinstance(report, PerformanceAttributionReport)

    def test_transaction_cost_drag_non_negative(self):
        """transaction_cost_drag ≥ 0。"""
        engine = _engine()
        segments = [_seg("A", 1.0, 1.0, 0.05, 0.03)]
        with pytest.raises(AttributionDataIncompleteError, match="≥ 0"):
            engine.attribute_full(
                portfolio_id="PF-1",
                period_start="2026-01-01",
                period_end="2026-03-31",
                idempotency_key="attr-005",
                segments=segments,
                transaction_cost_drag=-0.001,
            )

    def test_zero_cost_drag(self):
        """transaction_cost_drag=0 → total_return=excess_return。"""
        engine = _engine()
        segments = [_seg("A", 0.60, 0.40, 0.05, 0.03)]
        report = engine.attribute_full(
            portfolio_id="PF-1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            idempotency_key="attr-006",
            segments=segments,
            transaction_cost_drag=0.0,
        )
        excess = report.allocation_effect + report.selection_effect + report.interaction_effect
        assert math.isclose(report.total_return, excess, abs_tol=1e-12)


# ──────────────────────────────────────────────────────────────────────────────
# 幂等性
# ──────────────────────────────────────────────────────────────────────────────


class TestIdempotency:
    """幂等性: 相同输入 → 相同输出。"""

    def test_same_input_same_output(self):
        """相同输入 → 相同报告。"""
        engine = _engine()
        segments = [
            _seg("A", 0.40, 0.30, 0.05, 0.03),
            _seg("B", 0.60, 0.70, 0.02, 0.01),
        ]
        r1 = engine.attribute_full(
            "PF-1",
            "2026-01-01",
            "2026-03-31",
            "key-idem",
            segments=segments,
            transaction_cost_drag=0.001,
        )
        r2 = engine.attribute_full(
            "PF-1",
            "2026-01-01",
            "2026-03-31",
            "key-idem",
            segments=segments,
            transaction_cost_drag=0.001,
        )
        assert r1.total_return == r2.total_return
        assert r1.allocation_effect == r2.allocation_effect
        assert r1.selection_effect == r2.selection_effect
        assert r1.interaction_effect == r2.interaction_effect
        assert r1.idempotency_key == r2.idempotency_key

    def test_different_key_different_report(self):
        """不同幂等键 → 不同报告 (键保留)。"""
        engine = _engine()
        segments = [_seg("A", 0.50, 0.50, 0.04, 0.02)]
        r1 = engine.attribute_full("PF-1", "s", "e", "key-A", segments=segments)
        r2 = engine.attribute_full("PF-1", "s", "e", "key-B", segments=segments)
        assert r1.idempotency_key == "key-A"
        assert r2.idempotency_key == "key-B"


# ──────────────────────────────────────────────────────────────────────────────
# 多期归因
# ──────────────────────────────────────────────────────────────────────────────


class TestMultiPeriodAttribution:
    """多期归因 (链式链接)。"""

    def test_multi_period_sum(self):
        """多期归因 = 各期效应之和。"""
        engine = _engine()
        p1 = engine.brinson_attribute([_seg("A", 0.60, 0.40, 0.05, 0.03)])
        p2 = engine.brinson_attribute([_seg("A", 0.50, 0.50, 0.04, 0.02)])
        multi = engine.attribute_multi_period([p1, p2])
        assert math.isclose(multi.allocation_effect, p1.allocation_effect + p2.allocation_effect)
        assert math.isclose(multi.selection_effect, p1.selection_effect + p2.selection_effect)
        assert math.isclose(multi.excess_return, p1.excess_return + p2.excess_return)
        assert multi.is_consistent

    def test_multi_period_empty_raises(self):
        """空期间 → AttributionDataIncompleteError。"""
        engine = _engine()
        with pytest.raises(AttributionDataIncompleteError, match="empty"):
            engine.attribute_multi_period([])

    def test_multi_period_segments_aggregated(self):
        """多期分段聚合。"""
        engine = _engine()
        p1 = engine.brinson_attribute([_seg("A", 0.5, 0.5, 0.01, 0.01)])
        p2 = engine.brinson_attribute([_seg("B", 0.5, 0.5, 0.02, 0.02)])
        multi = engine.attribute_multi_period([p1, p2])
        assert len(multi.segments) == 2


# ──────────────────────────────────────────────────────────────────────────────
# 构造器校验
# ──────────────────────────────────────────────────────────────────────────────


class TestConstructorValidation:
    """构造器参数校验。"""

    def test_invalid_ic_decay_threshold(self):
        """ic_decay_threshold 越界 → ICDecayDetectionError。"""
        with pytest.raises(ICDecayDetectionError):
            _engine(ic_decay_threshold=1.5)

    def test_invalid_crowding_thresholds(self):
        """warn ≥ severe → AttributionDataIncompleteError。"""
        with pytest.raises(AttributionDataIncompleteError):
            _engine(crowding_warn_threshold=0.9, crowding_severe_threshold=0.8)

    def test_custom_thresholds(self):
        """自定义阈值生效。"""
        engine = _engine(
            ic_decay_threshold=0.3,
            crowding_warn_threshold=0.7,
            crowding_severe_threshold=0.85,
        )
        assert engine.ic_decay_threshold == 0.3
        assert engine.crowding_warn_threshold == 0.7
        assert engine.crowding_severe_threshold == 0.85

    def test_clock_injection(self):
        """时间源注入。"""
        fixed = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        engine = _engine(clock=lambda: fixed)
        result = engine.brinson_attribute([_seg("A", 0.5, 0.5, 0.01, 0.01)])
        # brinson_attribute 内部使用 now 但 BrinsonResult 不存时间
        # 通过 risk_attribute 验证
        cov = np.array([[0.04]])
        risk = engine.risk_attribute(cov, np.array([1.0]))
        assert risk.timestamp == fixed
