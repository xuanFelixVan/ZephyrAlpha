# [BLUEPRINT] MOD-EX_SOR_EXT-001 | docs/03_modules/_domain_ex_sor/slippage_analyzer/blueprint.md
# [TTL] permanent
"""SlippageAnalyzer 单元测试 (MOD-EX_SOR_EXT-001)。多基准滑点 + 三因子归因 + 预测。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.services.slippage_analyzer import (
    InsufficientFillsError,
    InvalidBenchmarkError,
    SlippageAnalyzer,
    SlippageAnalyzerError,
    SlippageAttribution,
    SlippageBenchmark,
    SlippageFillRecord,
    SlippageMetric,
    SlippagePredictor,
    SlippageResult,
    SquareRootImpactPredictor,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide

NOW = datetime(2026, 8, 4, 10, 30, tzinfo=timezone.utc)


# ──────────────────────────────────────────────────────────────────────────────
# 工厂
# ──────────────────────────────────────────────────────────────────────────────


def make_fill(
    price: str = "10.00",
    qty: str = "100",
    side: OrderSide = OrderSide.BUY,
    fid: str = "F-1",
    ts: datetime | None = None,
) -> SlippageFillRecord:
    return SlippageFillRecord(
        fill_id=fid,
        price=Decimal(price),
        quantity=Decimal(qty),
        timestamp=ts or NOW,
        side=side,
    )


def make_benchmarks(**kwargs: str) -> dict[SlippageBenchmark, Decimal]:
    """便捷构造基准映射, 默认 ARRIVAL=10.00。"""
    defaults = {SlippageBenchmark.ARRIVAL: Decimal("10.00")}
    for k, v in kwargs.items():
        defaults[SlippageBenchmark[k]] = Decimal(v)
    return defaults


# ══════════════════════════════════════════════════════════════════════════════
# SlippageFillRecord
# ══════════════════════════════════════════════════════════════════════════════


class TestSlippageFillRecord:
    def test_valid(self):
        f = make_fill("10.50", "200")
        assert f.price == Decimal("10.50")
        assert f.quantity == Decimal("200")

    def test_zero_price_raises(self):
        with pytest.raises(SlippageAnalyzerError, match="成交价必须为正"):
            SlippageFillRecord("F1", Decimal("0"), Decimal("100"), NOW, OrderSide.BUY)

    def test_negative_price_raises(self):
        with pytest.raises(SlippageAnalyzerError, match="成交价必须为正"):
            SlippageFillRecord("F1", Decimal("-1"), Decimal("100"), NOW, OrderSide.BUY)

    def test_zero_quantity_raises(self):
        with pytest.raises(SlippageAnalyzerError, match="成交数量必须为正"):
            SlippageFillRecord("F1", Decimal("10"), Decimal("0"), NOW, OrderSide.BUY)

    def test_frozen(self):
        f = make_fill()
        with pytest.raises(Exception):
            f.price = Decimal("11")  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# SlippageBenchmark
# ══════════════════════════════════════════════════════════════════════════════


class TestSlippageBenchmark:
    def test_str_returns_value(self):
        assert str(SlippageBenchmark.ARRIVAL) == "ARRIVAL"
        assert str(SlippageBenchmark.VWAP) == "VWAP"

    def test_all_five_benchmarks(self):
        assert len(list(SlippageBenchmark)) == 5


# ══════════════════════════════════════════════════════════════════════════════
# 滑点计算 (核心符号约定)
# ══════════════════════════════════════════════════════════════════════════════


class TestSlippageCalculation:
    def test_buy_filled_above_benchmark_is_cost(self):
        """BUY: 成交价 > 基准 → 正滑点 (成本)。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.10", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        m = result.metric_for(SlippageBenchmark.ARRIVAL)
        # (10.10 - 10.00) / 10.00 × 10000 = 100 bps
        assert m.slippage_bps == pytest.approx(Decimal("100"), abs=1)

    def test_buy_filled_below_benchmark_is_benefit(self):
        """BUY: 成交价 < 基准 → 负滑点 (有利)。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("9.90", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        m = result.metric_for(SlippageBenchmark.ARRIVAL)
        # (9.90 - 10.00) / 10.00 × 10000 = -100 bps
        assert m.slippage_bps == pytest.approx(Decimal("-100"), abs=1)

    def test_sell_filled_below_benchmark_is_cost(self):
        """SELL: 成交价 < 基准 → 正滑点 (成本, 卖便宜了)。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.SELL,
            fills=[make_fill("9.90", "100", side=OrderSide.SELL)],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        m = result.metric_for(SlippageBenchmark.ARRIVAL)
        # (10.00 - 9.90) / 10.00 × 10000 = 100 bps
        assert m.slippage_bps == pytest.approx(Decimal("100"), abs=1)

    def test_sell_filled_above_benchmark_is_benefit(self):
        """SELL: 成交价 > 基准 → 负滑点 (有利, 卖贵了)。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.SELL,
            fills=[make_fill("10.10", "100", side=OrderSide.SELL)],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        m = result.metric_for(SlippageBenchmark.ARRIVAL)
        assert m.slippage_bps == pytest.approx(Decimal("-100"), abs=1)

    def test_zero_slippage_when_fill_equals_benchmark(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        m = result.metric_for(SlippageBenchmark.ARRIVAL)
        assert m.slippage_bps == pytest.approx(Decimal("0"), abs=1)


# ══════════════════════════════════════════════════════════════════════════════
# 加权平均成交价
# ══════════════════════════════════════════════════════════════════════════════


class TestWeightedAverage:
    def test_single_fill(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.50", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        assert result.avg_fill_price == pytest.approx(Decimal("10.50"), abs=0.01)

    def test_multiple_fills_weighted(self):
        """两笔成交: 100@10.00 + 200@10.50 → VWAP=10.3333。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[
                make_fill("10.00", "100", fid="F1"),
                make_fill("10.50", "200", fid="F2"),
            ],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        # (10×100 + 10.50×200) / 300 = (1000+2100)/300 = 3100/300 = 10.3333
        assert result.avg_fill_price == pytest.approx(Decimal("10.3333"), abs=0.01)
        assert result.total_quantity == Decimal("300")

    def test_three_fills_weighted(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[
                make_fill("10.00", "100", fid="F1"),
                make_fill("10.20", "150", fid="F2"),
                make_fill("10.50", "250", fid="F3"),
            ],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        # (1000 + 1530 + 2625) / 500 = 5155/500 = 10.31
        assert result.avg_fill_price == pytest.approx(Decimal("10.31"), abs=0.01)
        assert result.total_quantity == Decimal("500")


# ══════════════════════════════════════════════════════════════════════════════
# 多基准对比
# ══════════════════════════════════════════════════════════════════════════════


class TestMultipleBenchmarks:
    def test_multiple_benchmarks_computed(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.10", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00", VWAP="10.05", PREV_CLOSE="9.90"),
            now=NOW,
        )
        assert len(result.metrics) == 3
        arr = result.metric_for(SlippageBenchmark.ARRIVAL)
        vwap = result.metric_for(SlippageBenchmark.VWAP)
        close = result.metric_for(SlippageBenchmark.PREV_CLOSE)
        # ARRIVAL: (10.10-10.00)/10.00×10000 = 100 bps
        assert arr.slippage_bps == pytest.approx(Decimal("100"), abs=1)
        # VWAP: (10.10-10.05)/10.05×10000 ≈ 49.75 bps
        assert vwap.slippage_bps == pytest.approx(Decimal("49.75"), abs=2)
        # PREV_CLOSE: (10.10-9.90)/9.90×10000 ≈ 202 bps
        assert close.slippage_bps == pytest.approx(Decimal("202"), abs=2)

    def test_metric_for_missing_returns_none(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        assert result.metric_for(SlippageBenchmark.VWAP) is None

    def test_all_benchmark_types(self):
        analyzer = SlippageAnalyzer()
        benches = {
            SlippageBenchmark.ARRIVAL: Decimal("10.00"),
            SlippageBenchmark.VWAP: Decimal("10.02"),
            SlippageBenchmark.TWAP: Decimal("10.01"),
            SlippageBenchmark.PREV_CLOSE: Decimal("9.95"),
            SlippageBenchmark.DECISION: Decimal("9.98"),
        }
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.10", "100")],
            benchmarks=benches,
            now=NOW,
        )
        assert len(result.metrics) == 5
        for bench in SlippageBenchmark:
            assert result.metric_for(bench) is not None


# ══════════════════════════════════════════════════════════════════════════════
# 归因
# ══════════════════════════════════════════════════════════════════════════════


class TestAttribution:
    def test_attribution_components_sum_with_residual(self):
        """归因三因子 + 残差 ≈ 总滑点 (守恒)。"""
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("10"))
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.20", "100")],  # 200 bps vs 10.00
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            adv=Decimal("100000"),
            volatility=Decimal("0.02"),
            start_price=Decimal("10.00"),
            end_price=Decimal("10.05"),
            now=NOW,
        )
        attr = result.attribution
        total = attr.market_impact_bps + attr.timing_bps + attr.spread_bps + attr.residual_bps
        assert total == pytest.approx(Decimal("200"), abs=2)

    def test_market_impact_increases_with_size(self):
        """订单越大 → 市场冲击越大。"""
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("0"))
        # 小单
        r1 = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            adv=Decimal("1000000"),
            volatility=Decimal("0.02"),
            now=NOW,
        )
        # 大单
        r2 = analyzer.analyze(
            order_id="O2",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100000")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            adv=Decimal("1000000"),
            volatility=Decimal("0.02"),
            now=NOW,
        )
        assert r2.attribution.market_impact_bps > r1.attribution.market_impact_bps

    def test_timing_buy_price_up_is_cost(self):
        """BUY: 执行期间价格上涨 → 时机成本 (正)。"""
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("0"))
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            start_price=Decimal("10.00"),
            end_price=Decimal("10.10"),
            now=NOW,
        )
        # drift = (10.10-10.00)/10.00×10000 = 100 bps → 时机=100
        assert result.attribution.timing_bps == pytest.approx(Decimal("100"), abs=1)

    def test_timing_sell_price_down_is_cost(self):
        """SELL: 执行期间价格下跌 → 时机成本 (正)。"""
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("0"))
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.SELL,
            fills=[make_fill("10.00", "100", side=OrderSide.SELL)],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            start_price=Decimal("10.10"),
            end_price=Decimal("10.00"),
            now=NOW,
        )
        # drift = (10.00-10.10)/10.10×10000 ≈ -99 bps → SELL timing = 99
        assert result.attribution.timing_bps > 0
        assert result.attribution.timing_bps == pytest.approx(Decimal("99"), abs=2)

    def test_spread_uses_half(self):
        """价差分量 = spread_bps / 2 (half-spread)。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            spread_bps=Decimal("20"),
            now=NOW,
        )
        assert result.attribution.spread_bps == pytest.approx(Decimal("10"), abs=1)

    def test_spread_defaults_to_half_spread_bps(self):
        """无 spread_bps 时用构造器 half_spread_bps。"""
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("15"))
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        assert result.attribution.spread_bps == Decimal("15")

    def test_no_attribution_inputs_gives_only_spread(self):
        """无 adv/vol/start/end → 仅 spread 分量, 残差=总滑点-spread。"""
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("10"))
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.10", "100")],  # 100 bps
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        attr = result.attribution
        assert attr.market_impact_bps == Decimal("0")
        assert attr.timing_bps == Decimal("0")
        assert attr.spread_bps == Decimal("10")
        # residual = 100 - 10 = 90
        assert attr.residual_bps == pytest.approx(Decimal("90"), abs=2)

    def test_total_attributed_excludes_residual(self):
        """total_attributed_bps 不含残差。"""
        attr = SlippageAttribution(
            market_impact_bps=Decimal("30"),
            timing_bps=Decimal("20"),
            spread_bps=Decimal("10"),
            residual_bps=Decimal("5"),
        )
        assert attr.total_attributed_bps == Decimal("60")


# ══════════════════════════════════════════════════════════════════════════════
# SquareRootImpactPredictor
# ══════════════════════════════════════════════════════════════════════════════


class TestSquareRootImpactPredictor:
    def test_predict_positive(self):
        p = SquareRootImpactPredictor()
        val = p.predict(Decimal("1000"), Decimal("100000"), Decimal("0.02"), Decimal("10"))
        assert val > 0

    def test_predict_zero_size_returns_zero(self):
        p = SquareRootImpactPredictor()
        val = p.predict(Decimal("0"), Decimal("100000"), Decimal("0.02"), Decimal("10"))
        assert val == Decimal("0")

    def test_predict_increases_with_size(self):
        """订单越大 → 预测滑点越大。"""
        p = SquareRootImpactPredictor()
        small = p.predict(Decimal("100"), Decimal("100000"), Decimal("0.02"), Decimal("10"))
        large = p.predict(Decimal("10000"), Decimal("100000"), Decimal("0.02"), Decimal("10"))
        assert large > small

    def test_predict_increases_with_volatility(self):
        """波动率越大 → 预测滑点越大。"""
        p = SquareRootImpactPredictor()
        low_vol = p.predict(Decimal("1000"), Decimal("100000"), Decimal("0.01"), Decimal("10"))
        high_vol = p.predict(Decimal("1000"), Decimal("100000"), Decimal("0.05"), Decimal("10"))
        assert high_vol > low_vol

    def test_predict_zero_adv_raises(self):
        p = SquareRootImpactPredictor()
        with pytest.raises(InvalidBenchmarkError, match="ADV"):
            p.predict(Decimal("100"), Decimal("0"), Decimal("0.02"), Decimal("10"))

    def test_predict_includes_half_spread(self):
        """预测值含 half-spread 分量。"""
        p = SquareRootImpactPredictor(coefficient=0.0)  # 零冲击系数
        val = p.predict(Decimal("1000"), Decimal("100000"), Decimal("0.02"), Decimal("20"))
        # 系数=0 → 仅 half_spread = 20/2 = 10
        assert val == pytest.approx(Decimal("10"), abs=1)

    def test_custom_coefficient(self):
        p1 = SquareRootImpactPredictor(coefficient=0.1)
        p2 = SquareRootImpactPredictor(coefficient=0.5)
        v1 = p1.predict(Decimal("1000"), Decimal("100000"), Decimal("0.02"), Decimal("10"))
        v2 = p2.predict(Decimal("1000"), Decimal("100000"), Decimal("0.02"), Decimal("10"))
        assert v2 > v1


# ══════════════════════════════════════════════════════════════════════════════
# SlippageAnalyzer.analyze 集成
# ══════════════════════════════════════════════════════════════════════════════


class TestAnalyzeIntegration:
    def test_full_analysis_with_all_inputs(self):
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("10"))
        result = analyzer.analyze(
            order_id="ORD-001",
            symbol="600519.SH",
            side=OrderSide.BUY,
            fills=[
                make_fill("10.05", "200", fid="F1"),
                make_fill("10.15", "300", fid="F2"),
            ],
            benchmarks=make_benchmarks(ARRIVAL="10.00", VWAP="10.08"),
            adv=Decimal("500000"),
            volatility=Decimal("0.025"),
            start_price=Decimal("10.00"),
            end_price=Decimal("10.20"),
            spread_bps=Decimal("16"),
            now=NOW,
        )
        assert result.order_id == "ORD-001"
        assert result.symbol == "600519.SH"
        assert result.side == OrderSide.BUY
        assert result.total_quantity == Decimal("500")
        # VWAP = (10.05×200 + 10.15×300)/500 = (2010+3045)/500 = 5055/500 = 10.11
        assert result.avg_fill_price == pytest.approx(Decimal("10.11"), abs=0.01)
        assert len(result.metrics) == 2
        assert result.predicted_slippage_bps is not None
        assert result.predicted_slippage_bps > 0
        assert result.analyzed_at == NOW

    def test_predict_none_without_adv(self):
        """无 adv → predicted_slippage_bps = None。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            now=NOW,
        )
        assert result.predicted_slippage_bps is None

    def test_predict_none_without_volatility(self):
        """有 adv 无 volatility → predicted = None。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            adv=Decimal("100000"),
            now=NOW,
        )
        assert result.predicted_slippage_bps is None

    def test_predict_with_adv_and_volatility(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.00", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00"),
            adv=Decimal("100000"),
            volatility=Decimal("0.02"),
            now=NOW,
        )
        assert result.predicted_slippage_bps is not None
        assert result.predicted_slippage_bps > 0

    def test_primary_metric_prefers_arrival(self):
        """主指标优先选 ARRIVAL。"""
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.10", "100")],
            benchmarks=make_benchmarks(ARRIVAL="10.00", VWAP="10.05", DECISION="9.98"),
            now=NOW,
        )
        # 归因基于 ARRIVAL (200 bps)
        arr = result.metric_for(SlippageBenchmark.ARRIVAL)
        # 总归因 (含残差) 应接近 ARRIVAL 滑点
        attr = result.attribution
        total = attr.market_impact_bps + attr.timing_bps + attr.spread_bps + attr.residual_bps
        assert total == pytest.approx(arr.slippage_bps, abs=2)

    def test_primary_metric_falls_back_to_decision(self):
        """无 ARRIVAL 时选 DECISION。"""
        analyzer = SlippageAnalyzer(half_spread_bps=Decimal("0"))
        result = analyzer.analyze(
            order_id="O1",
            symbol="000001.SZ",
            side=OrderSide.BUY,
            fills=[make_fill("10.10", "100")],
            benchmarks={SlippageBenchmark.DECISION: Decimal("10.00"), SlippageBenchmark.VWAP: Decimal("10.05")},
            now=NOW,
        )
        attr = result.attribution
        total = attr.market_impact_bps + attr.timing_bps + attr.spread_bps + attr.residual_bps
        # 基于DECISION: (10.10-10.00)/10.00×10000=100 bps
        assert total == pytest.approx(Decimal("100"), abs=2)


# ══════════════════════════════════════════════════════════════════════════════
# 历史追踪
# ══════════════════════════════════════════════════════════════════════════════


class TestHistoryTracking:
    def test_history_accumulates(self):
        analyzer = SlippageAnalyzer()
        for i in range(3):
            analyzer.analyze(
                order_id=f"O{i}",
                symbol="000001.SZ",
                side=OrderSide.BUY,
                fills=[make_fill("10.00", "100")],
                benchmarks=make_benchmarks(ARRIVAL="10.00"),
                now=NOW,
            )
        assert len(analyzer.history) == 3

    def test_history_filtered_by_symbol(self):
        analyzer = SlippageAnalyzer()
        analyzer.analyze(
            "O1", "000001.SZ", OrderSide.BUY, [make_fill("10.00", "100")], make_benchmarks(ARRIVAL="10.00"), now=NOW
        )
        analyzer.analyze(
            "O2", "600519.SH", OrderSide.BUY, [make_fill("10.00", "100")], make_benchmarks(ARRIVAL="10.00"), now=NOW
        )
        sz = analyzer.get_history(symbol="000001.SZ")
        assert len(sz) == 1
        assert sz[0].symbol == "000001.SZ"

    def test_get_history_all(self):
        analyzer = SlippageAnalyzer()
        analyzer.analyze(
            "O1", "000001.SZ", OrderSide.BUY, [make_fill("10.00", "100")], make_benchmarks(ARRIVAL="10.00"), now=NOW
        )
        all_hist = analyzer.get_history()
        assert len(all_hist) == 1

    def test_clear_history(self):
        analyzer = SlippageAnalyzer()
        analyzer.analyze(
            "O1", "000001.SZ", OrderSide.BUY, [make_fill("10.00", "100")], make_benchmarks(ARRIVAL="10.00"), now=NOW
        )
        assert len(analyzer.history) == 1
        analyzer.clear_history()
        assert len(analyzer.history) == 0


# ══════════════════════════════════════════════════════════════════════════════
# 异常 & 边界
# ══════════════════════════════════════════════════════════════════════════════


class TestErrorsAndEdgeCases:
    def test_empty_fills_raises(self):
        analyzer = SlippageAnalyzer()
        with pytest.raises(InsufficientFillsError, match="无成交记录"):
            analyzer.analyze("O1", "000001.SZ", OrderSide.BUY, [], make_benchmarks(), now=NOW)

    def test_empty_benchmarks_raises(self):
        analyzer = SlippageAnalyzer()
        with pytest.raises(InvalidBenchmarkError, match="未提供任何基准"):
            analyzer.analyze("O1", "000001.SZ", OrderSide.BUY, [make_fill()], {}, now=NOW)

    def test_zero_benchmark_price_raises(self):
        analyzer = SlippageAnalyzer()
        with pytest.raises(InvalidBenchmarkError, match="必须为正"):
            analyzer.analyze(
                "O1", "000001.SZ", OrderSide.BUY, [make_fill()], {SlippageBenchmark.ARRIVAL: Decimal("0")}, now=NOW
            )

    def test_negative_benchmark_price_raises(self):
        analyzer = SlippageAnalyzer()
        with pytest.raises(InvalidBenchmarkError, match="必须为正"):
            analyzer.analyze(
                "O1", "000001.SZ", OrderSide.BUY, [make_fill()], {SlippageBenchmark.ARRIVAL: Decimal("-1")}, now=NOW
            )

    def test_default_now_when_not_provided(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze("O1", "000001.SZ", OrderSide.BUY, [make_fill()], make_benchmarks())
        assert result.analyzed_at is not None

    def test_slippage_result_frozen(self):
        analyzer = SlippageAnalyzer()
        result = analyzer.analyze("O1", "000001.SZ", OrderSide.BUY, [make_fill()], make_benchmarks(), now=NOW)
        with pytest.raises(Exception):
            result.order_id = "X"  # type: ignore[misc]

    def test_slippage_metric_frozen(self):
        m = SlippageMetric(
            benchmark=SlippageBenchmark.ARRIVAL,
            benchmark_price=Decimal("10"),
            avg_fill_price=Decimal("10.1"),
            slippage_bps=Decimal("100"),
            side=OrderSide.BUY,
        )
        with pytest.raises(Exception):
            m.slippage_bps = Decimal("0")  # type: ignore[misc]

    def test_custom_predictor_injected(self):
        """注入自定义预测器。"""

        class FixedPredictor:
            def predict(self, order_size, adv, volatility, spread_bps):
                return Decimal("42.00")

        analyzer = SlippageAnalyzer(predictor=FixedPredictor())
        result = analyzer.analyze(
            "O1",
            "000001.SZ",
            OrderSide.BUY,
            [make_fill("10.00", "100")],
            make_benchmarks(ARRIVAL="10.00"),
            adv=Decimal("100000"),
            volatility=Decimal("0.02"),
            now=NOW,
        )
        assert result.predicted_slippage_bps == Decimal("42.00")
