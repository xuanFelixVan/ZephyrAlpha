# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md | §test
# [MODULE] tests.signal.test_default_signal_aggregator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.gen.implementations.default_signal_aggregator; zephyr.shared.contracts.factor_signal
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_default_signal_aggregator.py
# [A_test] module_id: MOD-L03-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-L03-001 DefaultSignalAggregator 直属单元测试（CAND-SIG-005）。

覆盖现有行为：空信号降级 / 有效因子不足降级 / min_confidence 过滤 /
is_valid 过滤 / 等权+置信度加权+ic_weight 三法 / 未知方法回退等权 /
方向判定（LONG/SHORT/NEUTRAL）/ [-3,3] 截断 / PIT 时间戳 /
contributing_factors 留痕。
组合级输出（aggregate_portfolio）：标的清单 + 归一化权重 + 触发条件明细 /
降级剔除 / 非正向剔除 / 确定性排序。全程内存构造，无 DB。
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

pytest.importorskip(
    "zephyr.signal_fundamental.gen.implementations.default_signal_aggregator",
    reason="default_signal_aggregator not importable",
)

from zephyr.shared.contracts.factor_signal import FactorSignal  # noqa: E402
from zephyr.signal_fundamental.gen.implementations.default_signal_aggregator import (  # noqa: E402
    DefaultSignalAggregator,
    PortfolioSignalOutput,
)

_AS_OF = datetime(2026, 8, 29, 15, 0, tzinfo=UTC)
_AS_OF_LATE = datetime(2026, 8, 30, 15, 0, tzinfo=UTC)


def _fs(
    factor_id: str,
    raw: float,
    *,
    symbol: str = "600000.SH",
    confidence: float = 1.0,
    is_valid: bool = True,
    normalized: float | None = None,
    as_of: datetime = _AS_OF,
) -> FactorSignal:
    return FactorSignal(
        as_of_date=as_of,
        factor_id=factor_id,
        idempotency_key=f"k-{factor_id}-{symbol}",
        raw_value=raw,
        symbol=symbol,
        confidence=confidence,
        is_valid=is_valid,
        normalized_value=normalized,
    )


# ── 现有行为：降级路径 ────────────────────────────────────────────────


class TestDegradedPaths:
    def test_empty_signals_degraded(self):
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([], "600000.SH", "k-empty")
        assert sig.is_degraded is True
        assert sig.signal_value == 0.0
        assert sig.signal_direction == "NEUTRAL"
        assert sig.symbol == "600000.SH"

    def test_insufficient_valid_factors_degraded(self):
        """默认 min_factors=2：仅 1 个有效因子 → 降级，PIT 用因子时间戳"""
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([_fs("f1", 1.0)], "600000.SH", "k-1")
        assert sig.is_degraded is True
        assert sig.as_of_timestamp == _AS_OF

    def test_min_confidence_filter(self):
        """confidence < 0.3 被过滤 → 有效因子不足降级"""
        agg = DefaultSignalAggregator()
        signals = [_fs("f1", 1.0, confidence=0.1), _fs("f2", 1.0, confidence=0.2)]
        sig = agg.aggregate(signals, "600000.SH", "k-2")
        assert sig.is_degraded is True

    def test_invalid_signal_excluded(self):
        agg = DefaultSignalAggregator()
        signals = [_fs("f1", 1.0, is_valid=False), _fs("f2", 1.0)]
        sig = agg.aggregate(signals, "600000.SH", "k-3")
        assert sig.is_degraded is True  # 仅 f2 有效 < 2


# ── 现有行为：聚合方法 ────────────────────────────────────────────────


class TestAggregateMethods:
    def test_equal_weight_manual(self):
        """等权手工验证：(1.0 + 0.5)/2 = 0.75，置信度均值 0.75"""
        agg = DefaultSignalAggregator(aggregation_method="equal_weight")
        signals = [_fs("f1", 1.0, confidence=1.0), _fs("f2", 0.5, confidence=0.5)]
        sig = agg.aggregate(signals, "600000.SH", "k-eq")
        assert sig.is_degraded is False
        assert sig.signal_value == pytest.approx(0.75)
        assert sig.confidence == pytest.approx(0.75)
        assert sig.contributing_factors["f1"] == pytest.approx(0.5)
        assert sig.contributing_factors["f2"] == pytest.approx(0.5)

    def test_confidence_weight_manual(self):
        """置信度加权：w=0.8/0.4 → 1.0×2/3 + 0.0×1/3 = 2/3（confidence 须 ≥0.3 过滤线）"""
        agg = DefaultSignalAggregator(aggregation_method="confidence_weight")
        signals = [_fs("f1", 1.0, confidence=0.8), _fs("f2", 0.0, confidence=0.4)]
        sig = agg.aggregate(signals, "600000.SH", "k-cw")
        assert sig.signal_value == pytest.approx(2.0 / 3.0)
        assert sig.contributing_factors["f1"] == pytest.approx(2.0 / 3.0)
        assert sig.contributing_factors["f2"] == pytest.approx(1.0 / 3.0)

    def test_ic_weight_falls_back_to_equal(self):
        agg = DefaultSignalAggregator(aggregation_method="ic_weight")
        signals = [_fs("f1", 1.0), _fs("f2", 0.5)]
        sig = agg.aggregate(signals, "600000.SH", "k-ic")
        assert sig.signal_value == pytest.approx(0.75)

    def test_unknown_method_falls_back_to_equal(self):
        agg = DefaultSignalAggregator(aggregation_method="no_such_method")
        signals = [_fs("f1", 1.0), _fs("f2", 0.5)]
        sig = agg.aggregate(signals, "600000.SH", "k-unk")
        assert sig.signal_value == pytest.approx(0.75)

    def test_normalized_value_preferred_over_raw(self):
        """normalized_value 非空优先参与聚合：(2.0 + 1.0)/2 = 1.5"""
        agg = DefaultSignalAggregator()
        signals = [_fs("f1", 99.0, normalized=2.0), _fs("f2", 1.0)]
        sig = agg.aggregate(signals, "600000.SH", "k-norm")
        assert sig.signal_value == pytest.approx(1.5)


# ── 现有行为：方向/截断/PIT ───────────────────────────────────────────


class TestDirectionAndPit:
    def test_direction_long(self):
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([_fs("f1", 1.0), _fs("f2", 0.5)], "600000.SH", "k-long")
        assert sig.signal_direction == "LONG"
        assert sig.suggested_position_pct == pytest.approx(abs(sig.signal_value) / 10.0)

    def test_direction_short(self):
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([_fs("f1", -1.0), _fs("f2", -0.5)], "600000.SH", "k-short")
        assert sig.signal_direction == "SHORT"

    def test_direction_neutral(self):
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([_fs("f1", 1.0), _fs("f2", -1.0)], "600000.SH", "k-neu")
        assert sig.signal_direction == "NEUTRAL"

    def test_signal_clipped_to_three(self):
        """signal_value 截断 [-3,3]（基类契约）"""
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([_fs("f1", 10.0), _fs("f2", 8.0)], "600000.SH", "k-clip")
        assert sig.signal_value == pytest.approx(3.0)

    def test_pit_timestamp_from_factor(self):
        """PIT 一致：as_of_timestamp 取因子信号 as_of_date，非 wall-clock"""
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([_fs("f1", 1.0), _fs("f2", 0.5)], "600000.SH", "k-pit")
        assert sig.as_of_timestamp == _AS_OF

    def test_contributing_factors_recorded(self):
        agg = DefaultSignalAggregator()
        sig = agg.aggregate([_fs("f1", 1.0), _fs("f2", 0.5)], "600000.SH", "k-cf")
        assert set(sig.contributing_factors) == {"f1", "f2"}


# ── 组合级输出（CAND-SIG-005）────────────────────────────────────────


class TestAggregatePortfolio:
    def test_empty_map_empty_output(self):
        agg = DefaultSignalAggregator()
        out = agg.aggregate_portfolio({}, "pf-empty")
        assert isinstance(out, PortfolioSignalOutput)
        assert out.entries == ()
        assert out.total_weight == 0.0
        assert out.degraded_symbols == ()

    def test_weights_normalized_sum_to_one(self):
        """两标的入选：权重 ∝ |signal|×confidence，Σ=1，按 symbol 升序"""
        agg = DefaultSignalAggregator()
        # A: (1.0+1.0)/2=1.0 conf 1.0 → score 1.0；B: (0.5+0.5)/2=0.5 conf 0.8 → score 0.4
        out = agg.aggregate_portfolio(
            {
                "B": [_fs("f1", 0.5, symbol="B", confidence=0.8), _fs("f2", 0.5, symbol="B", confidence=0.8)],
                "A": [_fs("f1", 1.0, symbol="A"), _fs("f2", 1.0, symbol="A")],
            },
            "pf-1",
        )
        assert [e.symbol for e in out.entries] == ["A", "B"]
        a, b = out.entries
        assert a.weight == pytest.approx(1.0 / 1.4)
        assert b.weight == pytest.approx(0.4 / 1.4)
        assert out.total_weight == pytest.approx(1.0)
        assert a.direction == "LONG"

    def test_degraded_symbol_recorded(self):
        """有效因子不足的标的进 degraded_symbols，不进清单"""
        agg = DefaultSignalAggregator()
        out = agg.aggregate_portfolio(
            {
                "GOOD": [_fs("f1", 1.0, symbol="GOOD"), _fs("f2", 1.0, symbol="GOOD")],
                "BAD": [_fs("f1", 1.0, symbol="BAD")],
            },
            "pf-2",
        )
        assert [e.symbol for e in out.entries] == ["GOOD"]
        assert out.degraded_symbols == ("BAD",)
        assert out.entries[0].weight == pytest.approx(1.0)

    def test_non_positive_signal_excluded(self):
        """NEUTRAL/SHORT 信号不入组合清单（A股无做空）"""
        agg = DefaultSignalAggregator()
        out = agg.aggregate_portfolio(
            {
                "UP": [_fs("f1", 1.0, symbol="UP"), _fs("f2", 1.0, symbol="UP")],
                "DOWN": [_fs("f1", -1.0, symbol="DOWN"), _fs("f2", -1.0, symbol="DOWN")],
                "FLAT": [_fs("f1", 1.0, symbol="FLAT"), _fs("f2", -1.0, symbol="FLAT")],
            },
            "pf-3",
        )
        assert [e.symbol for e in out.entries] == ["UP"]
        assert out.degraded_symbols == ()

    def test_trigger_conditions_detail(self):
        """触发条件明细：贡献因子+权重，升序留痕"""
        agg = DefaultSignalAggregator()
        out = agg.aggregate_portfolio(
            {"A": [_fs("f2", 1.0, symbol="A"), _fs("f1", 1.0, symbol="A")]},
            "pf-4",
        )
        assert out.entries[0].trigger_conditions == ("f1:w=0.5000", "f2:w=0.5000")

    def test_entry_idempotency_derived(self):
        """条目幂等键 = 父键-标的派生"""
        agg = DefaultSignalAggregator()
        out = agg.aggregate_portfolio(
            {"A": [_fs("f1", 1.0, symbol="A"), _fs("f2", 1.0, symbol="A")]},
            "pf-5",
        )
        assert out.entries[0].idempotency_key == "pf-5-A"
        assert out.idempotency_key == "pf-5"

    def test_timestamp_max_of_entries(self):
        """组合时间戳 = 入选信号 as_of 最大值（PIT 一致）"""
        agg = DefaultSignalAggregator()
        out = agg.aggregate_portfolio(
            {
                "A": [_fs("f1", 1.0, symbol="A"), _fs("f2", 1.0, symbol="A")],
                "B": [
                    _fs("f1", 1.0, symbol="B", as_of=_AS_OF_LATE),
                    _fs("f2", 1.0, symbol="B", as_of=_AS_OF_LATE),
                ],
            },
            "pf-6",
        )
        assert out.timestamp == _AS_OF_LATE
