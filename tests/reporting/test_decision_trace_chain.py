# [BLUEPRINT] MOD-RPT-033 | docs/03_modules/_domain_reporting/decision_trace_chain/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-RPT-033 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.reporting.test_decision_trace_chain
# [TESTS] src/zephyr/reporting/decision_trace_chain.py
"""MOD-RPT-033 单元测试：decision_trace_chain 决策溯源链。

蓝图验收（B1-00220/CAND-RPT-008，C2 C-030）：
决策链 ID 贯穿信号→计划→订单→成交四段（段记录注入存储）+ 全链反查
（按 decision_id 聚合确定性排序）+ 因子贡献摘要（注入贡献度）+
密度感知置信度调整（分位数→置信度映射注入）。
存储/贡献度/映射/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.reporting.decision_trace_chain",
    reason="decision_trace_chain not importable",
)

from zephyr.reporting.decision_trace_chain import (  # noqa: E402
    DecisionTraceChain,
    DecisionTraceError,
    SegmentRecord,
    TraceSegment,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 25, 9, 31, 0)
_T2 = datetime.datetime(2026, 8, 25, 9, 32, 0)
_T3 = datetime.datetime(2026, 8, 25, 9, 33, 0)

_FACTORS = {"momentum": 0.42, "value": -0.17, "liquidity": 0.42, "volatility": -0.05}
_QCONF = [(0.5, 0.55), (0.8, 0.75), (1.0, 0.95)]


def _chain(
    store: list | None = None,
    factors: dict | None = None,
    qconf=_QCONF,
) -> DecisionTraceChain:
    return DecisionTraceChain(
        segment_store=(lambda r: store.append(r)) if store is not None else None,
        factor_contributions=(lambda did: factors) if factors is not None else None,
        quantile_confidence=qconf,
        clock=lambda: _T0,
    )


def _seg(
    segment: TraceSegment = TraceSegment.SIGNAL,
    decision_id: str = "dec-1",
    at: datetime.datetime = _T0,
) -> SegmentRecord:
    return SegmentRecord(
        decision_id=decision_id,
        segment=segment,
        payload={"note": segment.value if isinstance(segment, TraceSegment) else segment},
        recorded_at=at,
    )


def _full_chain(chain: DecisionTraceChain, decision_id: str = "dec-1") -> None:
    chain.record_segment(_seg(TraceSegment.SIGNAL, decision_id, _T0))
    chain.record_segment(_seg(TraceSegment.PLAN, decision_id, _T1))
    chain.record_segment(_seg(TraceSegment.ORDER, decision_id, _T2))
    chain.record_segment(_seg(TraceSegment.FILL, decision_id, _T3))


# ──────────────────────────────────────────────────────────────────────────────
# 段落痕（注入存储）
# ──────────────────────────────────────────────────────────────────────────────


class TestRecordSegment:
    def test_record_full_chain(self) -> None:
        chain = _chain()
        _full_chain(chain)
        segs = chain.segments_of("dec-1")
        assert [s.segment for s in segs] == [
            TraceSegment.SIGNAL,
            TraceSegment.PLAN,
            TraceSegment.ORDER,
            TraceSegment.FILL,
        ]

    def test_empty_decision_id_raises(self) -> None:
        chain = _chain()
        with pytest.raises(DecisionTraceError):
            chain.record_segment(_seg(decision_id=""))

    def test_invalid_segment_raises(self) -> None:
        chain = _chain()
        with pytest.raises(DecisionTraceError):
            chain.record_segment(_seg(segment="bogus"))

    def test_segment_store_injected_receives_records(self) -> None:
        store: list[SegmentRecord] = []
        chain = _chain(store=store)
        _full_chain(chain)
        assert len(store) == 4
        assert store[0].segment is TraceSegment.SIGNAL

    def test_store_not_injected_still_works(self) -> None:
        chain = _chain()
        chain.record_segment(_seg())
        assert len(chain.segments_of("dec-1")) == 1

    def test_store_failure_wrapped_fail_closed(self) -> None:
        def _bad_store(_r: SegmentRecord) -> None:
            raise RuntimeError("disk full")

        chain = DecisionTraceChain(segment_store=_bad_store, clock=lambda: _T0)
        with pytest.raises(DecisionTraceError):
            chain.record_segment(_seg())
        # 内存视图已留痕（append-only），存储失败 Fail-Closed 抛错
        assert len(chain.segments_of("dec-1")) == 1


# ──────────────────────────────────────────────────────────────────────────────
# 全链反查
# ──────────────────────────────────────────────────────────────────────────────


class TestTraceQuery:
    def test_trace_unknown_decision_id_raises(self) -> None:
        chain = _chain()
        with pytest.raises(DecisionTraceError):
            chain.segments_of("ghost")

    def test_segments_sorted_by_lifecycle_not_insertion(self) -> None:
        chain = _chain()
        chain.record_segment(_seg(TraceSegment.FILL, "dec-1", _T0))
        chain.record_segment(_seg(TraceSegment.SIGNAL, "dec-1", _T3))
        chain.record_segment(_seg(TraceSegment.ORDER, "dec-1", _T1))
        chain.record_segment(_seg(TraceSegment.PLAN, "dec-1", _T2))
        segs = chain.segments_of("dec-1")
        assert [s.segment for s in segs] == [
            TraceSegment.SIGNAL,
            TraceSegment.PLAN,
            TraceSegment.ORDER,
            TraceSegment.FILL,
        ]

    def test_same_segment_sorted_by_recorded_at(self) -> None:
        chain = _chain()
        chain.record_segment(_seg(TraceSegment.ORDER, "dec-1", _T2))
        chain.record_segment(_seg(TraceSegment.ORDER, "dec-1", _T0))
        segs = chain.segments_of("dec-1")
        assert [s.recorded_at for s in segs] == [_T0, _T2]

    def test_trace_without_injectables_lenient(self) -> None:
        chain = DecisionTraceChain(clock=lambda: _T0)
        _full_chain(chain)
        trace = chain.trace("dec-1")
        assert trace.factor_summary == ()
        assert trace.confidence is None
        assert len(trace.segments) == 4

    def test_multi_decision_isolated(self) -> None:
        chain = _chain()
        _full_chain(chain, "dec-1")
        chain.record_segment(_seg(TraceSegment.SIGNAL, "dec-2", _T0))
        assert len(chain.segments_of("dec-1")) == 4
        assert len(chain.segments_of("dec-2")) == 1


# ──────────────────────────────────────────────────────────────────────────────
# 因子贡献摘要
# ──────────────────────────────────────────────────────────────────────────────


class TestFactorSummary:
    def test_sorted_by_abs_contribution_then_name(self) -> None:
        chain = _chain(factors=_FACTORS)
        _full_chain(chain)
        summary = chain.factor_summary("dec-1")
        # |0.42| 同值按名称升序，其后 |−0.17|、|−0.05|
        assert [(f.factor, f.contribution) for f in summary] == [
            ("liquidity", 0.42),
            ("momentum", 0.42),
            ("value", -0.17),
            ("volatility", -0.05),
        ]

    def test_unknown_decision_raises(self) -> None:
        chain = _chain(factors=_FACTORS)
        with pytest.raises(DecisionTraceError):
            chain.factor_summary("ghost")

    def test_not_injected_raises(self) -> None:
        chain = _chain()
        _full_chain(chain)
        with pytest.raises(DecisionTraceError):
            chain.factor_summary("dec-1")


# ──────────────────────────────────────────────────────────────────────────────
# 密度感知置信度调整
# ──────────────────────────────────────────────────────────────────────────────


class TestAdjustedConfidence:
    def test_bins(self) -> None:
        chain = _chain()
        assert chain.adjusted_confidence(0.3) == 0.55
        assert chain.adjusted_confidence(0.7) == 0.75
        assert chain.adjusted_confidence(0.9) == 0.95

    def test_boundary_uses_own_bin(self) -> None:
        chain = _chain()
        assert chain.adjusted_confidence(0.5) == 0.55
        assert chain.adjusted_confidence(0.8) == 0.75

    def test_not_injected_raises(self) -> None:
        chain = _chain(qconf=None)
        with pytest.raises(DecisionTraceError):
            chain.adjusted_confidence(0.5)

    def test_quantile_out_of_range_raises(self) -> None:
        chain = _chain()
        with pytest.raises(DecisionTraceError):
            chain.adjusted_confidence(-0.1)
        with pytest.raises(DecisionTraceError):
            chain.adjusted_confidence(1.1)

    def test_beyond_last_bin_raises(self) -> None:
        chain = _chain(qconf=[(0.5, 0.6)])
        with pytest.raises(DecisionTraceError):
            chain.adjusted_confidence(0.9)

    def test_init_invalid_bins_raise(self) -> None:
        with pytest.raises(DecisionTraceError):
            DecisionTraceChain(quantile_confidence=[])  # 空分桶
        with pytest.raises(DecisionTraceError):
            DecisionTraceChain(quantile_confidence=[(0.8, 0.5), (0.5, 0.6)])  # 非升序
        with pytest.raises(DecisionTraceError):
            DecisionTraceChain(quantile_confidence=[(1.2, 0.5)])  # 上界越界
        with pytest.raises(DecisionTraceError):
            DecisionTraceChain(quantile_confidence=[(0.5, 1.5)])  # 置信度越界


# ──────────────────────────────────────────────────────────────────────────────
# 全链反查集成 + 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestTraceIntegration:
    def test_trace_full(self) -> None:
        chain = _chain(factors=_FACTORS)
        _full_chain(chain)
        trace = chain.trace("dec-1", quantile=0.7)
        assert trace.decision_id == "dec-1"
        assert len(trace.segments) == 4
        assert trace.factor_summary[0].factor == "liquidity"
        assert trace.confidence == 0.75

    def test_deterministic_same_input_same_output(self) -> None:
        chain = _chain(factors=_FACTORS)
        _full_chain(chain)
        t1 = chain.trace("dec-1", quantile=0.3)
        t2 = chain.trace("dec-1", quantile=0.3)
        assert t1 == t2
