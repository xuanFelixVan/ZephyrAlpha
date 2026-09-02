# [BLUEPRINT] MOD-SIG-111 | docs/03_modules/_domain_fundamental_signal/trace_context_store/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-111 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.signal_fundamental.audit.test_trace_context_store
# [TESTS] src/zephyr/signal_fundamental/audit/trace_context_store.py
"""MOD-SIG-111 单元测试：trace_context_store 信号追踪上下文存储。

蓝图验收（B2-05117/CAND-FUNDAMEN-002，D-SIGNAL §1.1）：
SQLite 追踪上下文表（trace_id→因子批次/信号/订单）+ 幂等写入 +
trace_chain 确定性排序 + signal_origin 单笔信号反查因子批次与原始行情 +
lineage 对接（sink 注入，异常不阻断）。:memory: 库 + tmp_path 文件库，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_fundamental.audit.trace_context_store",
    reason="trace_context_store not importable",
)

from zephyr.signal_fundamental.audit.trace_context_store import (  # noqa: E402
    TraceContextStore,
    TraceContextStoreError,
    TraceLayer,
    TraceSpanRecord,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _span(
    trace_id: str,
    span_id: str,
    layer: TraceLayer,
    ref_id: str,
    parent_span_id: str | None = None,
    detail: str = "",
) -> TraceSpanRecord:
    return TraceSpanRecord(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
        layer=layer,
        ref_id=ref_id,
        recorded_at=_T0,
        detail=detail,
    )


def _build_chain(store: TraceContextStore, trace_id: str = "t-1") -> None:
    """data 行情批次 → factor 因子批次 → signal 信号 → order 订单。"""
    store.record_span(_span(trace_id, "s-data", TraceLayer.DATA, "mkt-batch-001"))
    store.record_span(_span(trace_id, "s-factor", TraceLayer.FACTOR, "factor-batch-007", "s-data"))
    store.record_span(_span(trace_id, "s-signal", TraceLayer.SIGNAL, "sig-9001", "s-factor"))
    store.record_span(_span(trace_id, "s-order", TraceLayer.ORDER, "ord-3001", "s-signal"))


# ──────────────────────────────────────────────────────────────────────────────
# 写入与幂等
# ──────────────────────────────────────────────────────────────────────────────


class TestRecordSpan:
    def test_record_ok(self) -> None:
        store = TraceContextStore()
        assert store.record_span(_span("t-1", "s-1", TraceLayer.SIGNAL, "sig-1")) is True

    def test_duplicate_span_idempotent_reject(self) -> None:
        store = TraceContextStore()
        rec = _span("t-1", "s-1", TraceLayer.SIGNAL, "sig-1")
        assert store.record_span(rec) is True
        assert store.record_span(rec) is False  # 同 (trace_id, span_id) 拒绝

    def test_same_span_id_different_trace_ok(self) -> None:
        store = TraceContextStore()
        assert store.record_span(_span("t-1", "s-1", TraceLayer.SIGNAL, "sig-1")) is True
        assert store.record_span(_span("t-2", "s-1", TraceLayer.SIGNAL, "sig-2")) is True

    def test_invalid_inputs_raise(self) -> None:
        store = TraceContextStore()
        with pytest.raises(TraceContextStoreError):
            store.record_span(_span("", "s-1", TraceLayer.SIGNAL, "sig-1"))
        with pytest.raises(TraceContextStoreError):
            store.record_span(_span("t-1", "", TraceLayer.SIGNAL, "sig-1"))
        with pytest.raises(TraceContextStoreError):
            store.record_span(_span("t-1", "s-1", TraceLayer.SIGNAL, ""))
        with pytest.raises(TraceContextStoreError):
            TraceSpanRecord(
                trace_id="t-1",
                span_id="s-x",
                parent_span_id=None,
                layer="bogus",  # type: ignore[arg-type]
                ref_id="sig-1",
                recorded_at=_T0,
            )


# ──────────────────────────────────────────────────────────────────────────────
# trace_chain 反查
# ──────────────────────────────────────────────────────────────────────────────


class TestTraceChain:
    def test_chain_ordered(self) -> None:
        store = TraceContextStore()
        _build_chain(store)
        chain = store.trace_chain("t-1")
        assert [s.span_id for s in chain] == ["s-data", "s-factor", "s-signal", "s-order"]
        assert [s.layer for s in chain] == [
            TraceLayer.DATA,
            TraceLayer.FACTOR,
            TraceLayer.SIGNAL,
            TraceLayer.ORDER,
        ]

    def test_unknown_trace_returns_empty(self) -> None:
        store = TraceContextStore()
        assert store.trace_chain("t-unknown") == []


# ──────────────────────────────────────────────────────────────────────────────
# signal_origin 单笔信号反查
# ──────────────────────────────────────────────────────────────────────────────


class TestSignalOrigin:
    def test_origin_full_chain(self) -> None:
        store = TraceContextStore()
        _build_chain(store)
        origin = store.signal_origin("sig-9001")
        assert origin.signal_span.ref_id == "sig-9001"
        assert [s.ref_id for s in origin.factor_spans] == ["factor-batch-007"]
        assert [s.ref_id for s in origin.data_spans] == ["mkt-batch-001"]
        assert [s.ref_id for s in origin.order_spans] == ["ord-3001"]

    def test_origin_unknown_signal_raises(self) -> None:
        store = TraceContextStore()
        with pytest.raises(TraceContextStoreError):
            store.signal_origin("sig-unknown")

    def test_origin_multi_factor_batch(self) -> None:
        store = TraceContextStore()
        store.record_span(_span("t-9", "s-d", TraceLayer.DATA, "mkt-b1"))
        store.record_span(_span("t-9", "s-f1", TraceLayer.FACTOR, "fb-1", "s-d"))
        store.record_span(_span("t-9", "s-f2", TraceLayer.FACTOR, "fb-2", "s-d"))
        store.record_span(_span("t-9", "s-s", TraceLayer.SIGNAL, "sig-9", "s-f1"))
        origin = store.signal_origin("sig-9")
        assert [s.ref_id for s in origin.factor_spans] == ["fb-1"]
        assert [s.ref_id for s in origin.data_spans] == ["mkt-b1"]


# ──────────────────────────────────────────────────────────────────────────────
# lineage 对接
# ──────────────────────────────────────────────────────────────────────────────


class TestLineageSync:
    def test_sync_registers_edges(self) -> None:
        edges: list[tuple[str, str, str]] = []
        store = TraceContextStore(lineage_sink=lambda s, t, tr: edges.append((s, t, tr)))
        _build_chain(store)
        n = store.sync_to_lineage("t-1")
        assert n == 3  # data→factor、factor→signal、signal→order
        assert ("mkt-batch-001", "factor-batch-007") in [(s, t) for s, t, _ in edges]
        assert ("factor-batch-007", "sig-9001") in [(s, t) for s, t, _ in edges]
        assert ("sig-9001", "ord-3001") in [(s, t) for s, t, _ in edges]

    def test_sink_exception_not_blocking(self) -> None:
        def _bad_sink(s: str, t: str, tr: str) -> None:
            raise RuntimeError("sink down")

        store = TraceContextStore(lineage_sink=_bad_sink)
        _build_chain(store)
        n = store.sync_to_lineage("t-1")  # 不抛
        assert n == 0

    def test_sync_unknown_trace_returns_zero(self) -> None:
        store = TraceContextStore(lineage_sink=lambda s, t, tr: None)
        assert store.sync_to_lineage("t-unknown") == 0


# ──────────────────────────────────────────────────────────────────────────────
# 文件库持久化往返
# ──────────────────────────────────────────────────────────────────────────────


class TestFilePersistence:
    def test_file_db_round_trip(self, tmp_path) -> None:
        db = tmp_path / "trace.db"
        store = TraceContextStore(db_path=str(db))
        _build_chain(store, "t-file")
        store.close()

        store2 = TraceContextStore(db_path=str(db))
        chain = store2.trace_chain("t-file")
        assert [s.span_id for s in chain] == ["s-data", "s-factor", "s-signal", "s-order"]
        origin = store2.signal_origin("sig-9001")
        assert origin.signal_span.trace_id == "t-file"
        store2.close()
