# [BLUEPRINT] MOD-EX_SOR_EXT-002 | docs/03_modules/_domain_ex_sor/execution_quality_scorer/blueprint.md
# [TTL] permanent
"""ExecutionQualityScorer 单元测试 (MOD-EX_SOR_EXT-002)。四维度评分+加权+历史追踪。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.services.execution_quality_scorer import (
    DefaultBenchmarkProvider,
    ExecutionDimensionScore,
    ExecutionQualityResult,
    ExecutionQualityScorer,
    InsufficientMetricsError,
    InvalidWeightsError,
    QualityDimension,
    QualityScorerError,
    QualityWeights,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide

NOW = datetime(2026, 8, 4, 14, 30, tzinfo=timezone.utc)


# ══════════════════════════════════════════════════════════════════════════════
# QualityDimension
# ══════════════════════════════════════════════════════════════════════════════


class TestQualityDimension:
    def test_str_returns_value(self):
        assert str(QualityDimension.PRICE) == "PRICE"
        assert str(QualityDimension.TIME) == "TIME"

    def test_four_dimensions(self):
        assert len(list(QualityDimension)) == 4


# ══════════════════════════════════════════════════════════════════════════════
# QualityWeights
# ══════════════════════════════════════════════════════════════════════════════


class TestQualityWeights:
    def test_defaults(self):
        w = QualityWeights()
        assert w.price_weight == pytest.approx(0.35)
        assert w.time_weight == pytest.approx(0.25)
        assert w.cost_weight == pytest.approx(0.25)
        assert w.impact_weight == pytest.approx(0.15)
        assert sum([w.price_weight, w.time_weight, w.cost_weight, w.impact_weight]) == pytest.approx(1.0)

    def test_custom_valid(self):
        w = QualityWeights(0.4, 0.3, 0.2, 0.1)
        assert w.price_weight == pytest.approx(0.4)

    def test_sum_not_one_raises(self):
        with pytest.raises(InvalidWeightsError, match="1.0"):
            QualityWeights(0.3, 0.3, 0.3, 0.3)

    def test_negative_raises(self):
        with pytest.raises(InvalidWeightsError, match="不能为负"):
            QualityWeights(-0.1, 0.5, 0.3, 0.3)

    def test_weight_for(self):
        w = QualityWeights()
        assert w.weight_for(QualityDimension.PRICE) == pytest.approx(0.35)
        assert w.weight_for(QualityDimension.TIME) == pytest.approx(0.25)

    def test_frozen(self):
        w = QualityWeights()
        with pytest.raises(Exception):
            w.price_weight = 0.5  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# ExecutionDimensionScore
# ══════════════════════════════════════════════════════════════════════════════


class TestExecutionDimensionScore:
    def test_valid(self):
        ds = ExecutionDimensionScore(QualityDimension.PRICE, 0.8, 10.0, 50.0, "good")
        assert ds.score == pytest.approx(0.8)

    def test_score_above_one_raises(self):
        with pytest.raises(QualityScorerError, match="必须"):
            ExecutionDimensionScore(QualityDimension.PRICE, 1.5, 10.0, 50.0, "good")

    def test_score_below_zero_raises(self):
        with pytest.raises(QualityScorerError):
            ExecutionDimensionScore(QualityDimension.PRICE, -0.1, 10.0, 50.0, "good")

    def test_frozen(self):
        ds = ExecutionDimensionScore(QualityDimension.PRICE, 0.5, 10.0, 50.0, "acceptable")
        with pytest.raises(Exception):
            ds.score = 0.9  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# 单维度评分
# ══════════════════════════════════════════════════════════════════════════════


class TestSingleDimensionScoring:
    def test_price_zero_slippage_is_perfect(self):
        """零滑点 → 价格评分 = 1.0。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("0"), now=NOW)
        ds = r.score_for(QualityDimension.PRICE)
        assert ds.score == pytest.approx(1.0)
        assert ds.verdict == "good"

    def test_price_at_threshold_is_zero(self):
        """滑点 = 阈值 (50bps) → 评分 = 0。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("50"), now=NOW)
        ds = r.score_for(QualityDimension.PRICE)
        assert ds.score == pytest.approx(0.0)

    def test_price_above_threshold_clamped_zero(self):
        """滑点 > 阈值 → 评分 = 0 (下限钳位)。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("100"), now=NOW)
        ds = r.score_for(QualityDimension.PRICE)
        assert ds.score == pytest.approx(0.0)

    def test_price_negative_slippage_uses_abs(self):
        """负滑点 (有利执行) → 取绝对值 (有利≠质量好, 仍按偏差评分)。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("-10"), now=NOW)
        ds = r.score_for(QualityDimension.PRICE)
        # abs(-10) = 10, threshold=50 → score = 1 - 10/50 = 0.8
        assert ds.score == pytest.approx(0.8)

    def test_time_zero_duration_is_perfect(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, duration_seconds=0.0, now=NOW)
        ds = r.score_for(QualityDimension.TIME)
        assert ds.score == pytest.approx(1.0)

    def test_time_at_threshold_is_zero(self):
        """耗时 = 阈值 (300s) → 评分 = 0。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, duration_seconds=300.0, now=NOW)
        ds = r.score_for(QualityDimension.TIME)
        assert ds.score == pytest.approx(0.0)

    def test_cost_zero_is_perfect(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, total_cost_bps=Decimal("0"), now=NOW)
        assert r.score_for(QualityDimension.COST).score == pytest.approx(1.0)

    def test_cost_at_threshold_is_zero(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, total_cost_bps=Decimal("30"), now=NOW)
        assert r.score_for(QualityDimension.COST).score == pytest.approx(0.0)

    def test_impact_zero_is_perfect(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, impact_bps=Decimal("0"), now=NOW)
        assert r.score_for(QualityDimension.IMPACT).score == pytest.approx(1.0)

    def test_impact_at_threshold_is_zero(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, impact_bps=Decimal("20"), now=NOW)
        assert r.score_for(QualityDimension.IMPACT).score == pytest.approx(0.0)


# ══════════════════════════════════════════════════════════════════════════════
# 多维度加权
# ══════════════════════════════════════════════════════════════════════════════


class TestMultiDimensionScoring:
    def test_all_four_dimensions(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("10"),
            duration_seconds=60.0,
            total_cost_bps=Decimal("6"),
            impact_bps=Decimal("4"),
            now=NOW,
        )
        assert len(r.dimension_scores) == 4
        # price: 1-10/50=0.8, time: 1-60/300=0.8, cost: 1-6/30=0.8, impact: 1-4/20=0.8
        for ds in r.dimension_scores:
            assert ds.score == pytest.approx(0.8)

    def test_overall_weighted_average(self):
        """overall = Σ(score×weight) / Σ(weight)。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("0"),  # price=1.0
            duration_seconds=300.0,  # time=0.0
            total_cost_bps=Decimal("0"),  # cost=1.0
            impact_bps=Decimal("0"),  # impact=1.0
            now=NOW,
        )
        # (1.0×0.35 + 0.0×0.25 + 1.0×0.25 + 1.0×0.15) / 1.0 = 0.35+0+0.25+0.15 = 0.75
        assert r.overall_score == pytest.approx(0.75)

    def test_overall_all_perfect(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("0"),
            duration_seconds=0.0,
            total_cost_bps=Decimal("0"),
            impact_bps=Decimal("0"),
            now=NOW,
        )
        assert r.overall_score == pytest.approx(1.0)
        assert r.verdict == "good"

    def test_overall_all_worst(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("100"),
            duration_seconds=600.0,
            total_cost_bps=Decimal("60"),
            impact_bps=Decimal("40"),
            now=NOW,
        )
        assert r.overall_score == pytest.approx(0.0)
        assert r.verdict == "poor"

    def test_partial_dimensions_renormalizes_weights(self):
        """仅提供部分维度 → 权重重新归一化。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("0"),  # price=1.0, weight=0.35
            total_cost_bps=Decimal("0"),  # cost=1.0, weight=0.25
            now=NOW,
        )
        # only 2 dims, both perfect → overall=1.0
        assert r.overall_score == pytest.approx(1.0)
        assert len(r.dimension_scores) == 2

    def test_partial_dims_one_good_one_bad(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("0"),  # price=1.0, w=0.35
            duration_seconds=300.0,  # time=0.0, w=0.25
            now=NOW,
        )
        # (1.0×0.35 + 0.0×0.25) / (0.35+0.25) = 0.35/0.60 = 0.5833
        assert r.overall_score == pytest.approx(0.5833, abs=0.01)


# ══════════════════════════════════════════════════════════════════════════════
# Verdict
# ══════════════════════════════════════════════════════════════════════════════


class TestVerdict:
    def test_good_threshold(self):
        """overall ≥ 0.8 → good。"""
        scorer = ExecutionQualityScorer()
        # slippage=10 → price=0.8, 其他全完美
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("10"),
            duration_seconds=0.0,
            total_cost_bps=Decimal("0"),
            impact_bps=Decimal("0"),
            now=NOW,
        )
        assert r.overall_score >= 0.8
        assert r.verdict == "good"

    def test_acceptable_threshold(self):
        """0.5 ≤ overall < 0.8 → acceptable。"""
        scorer = ExecutionQualityScorer()
        # price=0 (slippage=50), 其他完美
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("50"),
            duration_seconds=0.0,
            total_cost_bps=Decimal("0"),
            impact_bps=Decimal("0"),
            now=NOW,
        )
        # (0×0.35 + 1×0.25 + 1×0.25 + 1×0.15) / 1.0 = 0.65
        assert 0.5 <= r.overall_score < 0.8
        assert r.verdict == "acceptable"

    def test_poor_threshold(self):
        """overall < 0.5 → poor。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score(
            "O1",
            "X",
            OrderSide.BUY,
            slippage_bps=Decimal("50"),
            duration_seconds=300.0,
            total_cost_bps=Decimal("30"),
            impact_bps=Decimal("20"),
            now=NOW,
        )
        assert r.overall_score < 0.5
        assert r.verdict == "poor"


# ══════════════════════════════════════════════════════════════════════════════
# score_from_results (消费上游)
# ══════════════════════════════════════════════════════════════════════════════


class TestScoreFromResults:
    def test_score_from_results_same_as_score(self):
        """score_from_results 与 score 行为一致 (都接受原始指标)。"""
        scorer = ExecutionQualityScorer()
        r1 = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("10"), total_cost_bps=Decimal("5"), now=NOW)
        scorer.clear_history()
        r2 = scorer.score_from_results(
            "O1", "X", OrderSide.BUY, slippage_bps=Decimal("10"), total_cost_bps=Decimal("5"), now=NOW
        )
        assert r1.overall_score == r2.overall_score

    def test_consume_slippage_and_cost_results(self):
        """模拟从 EXT-001/EXT-003 结果提取指标后评分。"""
        scorer = ExecutionQualityScorer()
        # 模拟 SlippageResult 提取的 ARRIVAL 滑点
        slip_bps = Decimal("15")  # 15bps 滑点
        impact_bps = Decimal("8")  # 8bps 冲击
        # 模拟 TransactionCostResult 提取的总成本
        cost_bps = Decimal("7")  # 7bps 总成本
        r = scorer.score_from_results(
            "O1",
            "000001.SZ",
            OrderSide.BUY,
            slippage_bps=slip_bps,
            impact_bps=impact_bps,
            total_cost_bps=cost_bps,
            duration_seconds=90.0,
            now=NOW,
        )
        assert len(r.dimension_scores) == 4
        assert r.overall_score > 0


# ══════════════════════════════════════════════════════════════════════════════
# 自定义权重 & 基准
# ══════════════════════════════════════════════════════════════════════════════


class TestCustomConfig:
    def test_custom_weights_affect_overall(self):
        """价格优先权重 → 价格差时 overall 更低。"""
        w_price = QualityWeights(0.7, 0.1, 0.1, 0.1)
        w_balanced = QualityWeights(0.25, 0.25, 0.25, 0.25)
        s_price = ExecutionQualityScorer(weights=w_price)
        s_balanced = ExecutionQualityScorer(weights=w_balanced)
        # price=0, others=1.0
        kwargs = dict(
            slippage_bps=Decimal("50"), duration_seconds=0.0, total_cost_bps=Decimal("0"), impact_bps=Decimal("0")
        )
        r_price = s_price.score("O1", "X", OrderSide.BUY, now=NOW, **kwargs)
        r_balanced = s_balanced.score("O2", "X", OrderSide.BUY, now=NOW, **kwargs)
        # price-heavy → overall lower when price is bad
        assert r_price.overall_score < r_balanced.overall_score

    def test_custom_benchmark_provider(self):
        """自定义基准 → 阈值不同影响评分。"""

        class StrictBenchmark:
            def price_threshold_bps(self):
                return 10.0  # 10bps = 最差 (更严格)

            def time_threshold_s(self):
                return 60.0

            def cost_threshold_bps(self):
                return 5.0

            def impact_threshold_bps(self):
                return 5.0

        strict = ExecutionQualityScorer(benchmark=StrictBenchmark())
        default = ExecutionQualityScorer()
        # slippage=10bps: strict → 0.0, default → 0.8
        r_strict = strict.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        r_default = default.score("O2", "X", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        assert r_strict.score_for(QualityDimension.PRICE).score < r_default.score_for(QualityDimension.PRICE).score


# ══════════════════════════════════════════════════════════════════════════════
# 历史追踪
# ══════════════════════════════════════════════════════════════════════════════


class TestHistoryTracking:
    def test_history_accumulates(self):
        scorer = ExecutionQualityScorer()
        for i in range(3):
            scorer.score(f"O{i}", "X", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        assert len(scorer.history) == 3

    def test_history_filtered_by_symbol(self):
        scorer = ExecutionQualityScorer()
        scorer.score("O1", "000001.SZ", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        scorer.score("O2", "600519.SH", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        sz = scorer.get_history(symbol="000001.SZ")
        assert len(sz) == 1

    def test_history_filtered_by_min_score(self):
        scorer = ExecutionQualityScorer()
        scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("0"), now=NOW)  # score=1.0
        scorer.score("O2", "X", OrderSide.BUY, slippage_bps=Decimal("50"), now=NOW)  # score=0.0
        good = scorer.get_history(min_score=0.5)
        assert len(good) == 1
        assert good[0].order_id == "O1"

    def test_average_score(self):
        scorer = ExecutionQualityScorer()
        scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("0"), now=NOW)  # 1.0
        scorer.score("O2", "X", OrderSide.BUY, slippage_bps=Decimal("50"), now=NOW)  # 0.0
        avg = scorer.average_score()
        assert avg == pytest.approx(0.5)

    def test_average_score_empty(self):
        scorer = ExecutionQualityScorer()
        assert scorer.average_score() == 0.0

    def test_average_score_by_symbol(self):
        scorer = ExecutionQualityScorer()
        scorer.score("O1", "SZ", OrderSide.BUY, slippage_bps=Decimal("0"), now=NOW)
        scorer.score("O2", "SH", OrderSide.BUY, slippage_bps=Decimal("50"), now=NOW)
        sz_avg = scorer.average_score(symbol="SZ")
        assert sz_avg == pytest.approx(1.0)

    def test_clear_history(self):
        scorer = ExecutionQualityScorer()
        scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        scorer.clear_history()
        assert len(scorer.history) == 0


# ══════════════════════════════════════════════════════════════════════════════
# 异常 & 边界
# ══════════════════════════════════════════════════════════════════════════════


class TestErrorsAndEdgeCases:
    def test_no_metrics_raises(self):
        scorer = ExecutionQualityScorer()
        with pytest.raises(InsufficientMetricsError, match="至少需要"):
            scorer.score("O1", "X", OrderSide.BUY, now=NOW)

    def test_default_now(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("10"))
        assert r.evaluated_at is not None

    def test_result_frozen(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        with pytest.raises(Exception):
            r.overall_score = 0.0  # type: ignore[misc]

    def test_score_for_missing_returns_none(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, slippage_bps=Decimal("10"), now=NOW)
        assert r.score_for(QualityDimension.TIME) is None

    def test_sell_side_works(self):
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.SELL, slippage_bps=Decimal("10"), total_cost_bps=Decimal("5"), now=NOW)
        assert r.side == OrderSide.SELL
        assert r.overall_score > 0

    def test_default_benchmark_provider(self):
        bp = DefaultBenchmarkProvider()
        assert bp.price_threshold_bps() == 50.0
        assert bp.time_threshold_s() == 300.0
        assert bp.cost_threshold_bps() == 30.0
        assert bp.impact_threshold_bps() == 20.0

    def test_single_dimension_only(self):
        """仅一个维度也能评分。"""
        scorer = ExecutionQualityScorer()
        r = scorer.score("O1", "X", OrderSide.BUY, impact_bps=Decimal("10"), now=NOW)
        assert len(r.dimension_scores) == 1
        assert r.dimension_scores[0].dimension == QualityDimension.IMPACT
        # 1 - 10/20 = 0.5
        assert r.overall_score == pytest.approx(0.5)
