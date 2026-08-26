# [BLUEPRINT] MOD-INF-082 | docs/03_modules/_domain_infrastructure_operations/observability_triad/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-082 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infrastructure.test_observability_triad
# [TESTS] src/zephyr/infrastructure/system_telemetry/observability_triad.py
"""MOD-INF-082 单元测试：observability_triad 可观测性三支柱整合门面。

蓝图验收（B11-02678/CAND-INFRATEL-002，A7-Agent架构）：
TriadSink 统一入口（emit_trace/emit_metric/emit_log）+ Metrics Prometheus 文本
导出 + Logs JSON 不可变追加哈希链 + 热 7 天/冷归档裁决（注入时钟 + 归档执行
回调注入）+ 审计链对接回调。时钟/回调全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.observability_triad",
    reason="observability_triad not importable",
)

from zephyr.infrastructure.system_telemetry.observability_triad import (  # noqa: E402
    LogEntry,
    ObservabilityTriad,
    ObservabilityTriadError,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


class _Clock:
    """可变注入时钟（确定性推进）。"""

    def __init__(self, t: datetime.datetime) -> None:
        self._t = t

    def __call__(self) -> datetime.datetime:
        return self._t

    def advance(self, **kw) -> None:
        self._t += datetime.timedelta(**kw)


def _triad(**kw) -> ObservabilityTriad:
    kw.setdefault("clock", _Clock(_T0))
    return ObservabilityTriad(**kw)


# ──────────────────────────────────────────────────────────────────────────────
# Traces
# ──────────────────────────────────────────────────────────────────────────────


class TestEmitTrace:
    def test_emit_trace_ok_and_order(self) -> None:
        triad = _triad()
        r1 = triad.emit_trace("trace-1", "意图解析", {"agent": "signal"})
        r2 = triad.emit_trace("trace-1", "工具调用")
        assert r1.trace_id == "trace-1"
        assert r1.attributes == {"agent": "signal"}
        assert r1.ts == _T0
        assert triad.traces == (r1, r2)  # 发射序确定性

    def test_emit_trace_empty_id_raises(self) -> None:
        with pytest.raises(ObservabilityTriadError):
            _triad().emit_trace("", "意图解析")

    def test_emit_trace_empty_name_raises(self) -> None:
        with pytest.raises(ObservabilityTriadError):
            _triad().emit_trace("trace-1", "")


# ──────────────────────────────────────────────────────────────────────────────
# Metrics（Prometheus 文本导出）
# ──────────────────────────────────────────────────────────────────────────────


class TestMetrics:
    def test_counter_inc_and_render(self) -> None:
        triad = _triad()
        triad.register_counter("orders_total", "订单总数")
        triad.inc_counter("orders_total")
        triad.inc_counter("orders_total", 2)
        assert triad.render_prometheus() == (
            "# HELP orders_total 订单总数\n"
            "# TYPE orders_total counter\n"
            "orders_total 3\n"
        )

    def test_gauge_set_and_render(self) -> None:
        triad = _triad()
        triad.register_gauge("queue_depth")
        triad.set_gauge("queue_depth", 4.5)
        assert triad.render_prometheus() == (
            "# TYPE queue_depth gauge\nqueue_depth 4.5\n"
        )

    def test_render_sorted_by_name(self) -> None:
        triad = _triad()
        triad.register_gauge("z_last")
        triad.register_counter("a_first")
        out = triad.render_prometheus()
        assert out.index("a_first") < out.index("z_last")  # 确定性排序

    def test_render_empty(self) -> None:
        assert _triad().render_prometheus() == ""

    def test_duplicate_register_raises(self) -> None:
        triad = _triad()
        triad.register_counter("m1")
        with pytest.raises(ObservabilityTriadError):
            triad.register_gauge("m1")

    def test_inc_unknown_raises(self) -> None:
        with pytest.raises(ObservabilityTriadError):
            _triad().inc_counter("ghost")

    def test_set_unknown_raises(self) -> None:
        with pytest.raises(ObservabilityTriadError):
            _triad().set_gauge("ghost", 1)

    def test_counter_negative_inc_raises(self) -> None:
        triad = _triad()
        triad.register_counter("c1")
        with pytest.raises(ObservabilityTriadError):
            triad.inc_counter("c1", -1)

    def test_kind_mismatch_raises(self) -> None:
        triad = _triad()
        triad.register_gauge("g1")
        triad.register_counter("c1")
        with pytest.raises(ObservabilityTriadError):
            triad.inc_counter("g1")  # gauge 不可增量
        with pytest.raises(ObservabilityTriadError):
            triad.set_gauge("c1", 1)  # counter 不可设值


# ──────────────────────────────────────────────────────────────────────────────
# Logs（JSON 结构化不可变追加 + 哈希链）
# ──────────────────────────────────────────────────────────────────────────────


class TestLogs:
    def test_genesis_entry(self) -> None:
        entry = _triad().emit_log("INFO", "启动", {"pid": 1})
        assert entry.seq == 0
        assert entry.prev_hash == "0" * 64
        assert len(entry.entry_hash) == 64
        assert entry.fields == {"pid": 1}

    def test_chain_links(self) -> None:
        triad = _triad()
        e1 = triad.emit_log("INFO", "第一条")
        e2 = triad.emit_log("WARN", "第二条")
        assert e2.prev_hash == e1.entry_hash
        assert e2.seq == 1

    def test_logs_view_immutable(self) -> None:
        triad = _triad()
        triad.emit_log("INFO", "x")
        assert isinstance(triad.logs, tuple)

    def test_verify_chain_ok(self) -> None:
        triad = _triad()
        for i in range(5):
            triad.emit_log("INFO", f"msg-{i}", {"i": i})
        assert triad.verify_log_chain() is True

    def test_empty_level_raises(self) -> None:
        with pytest.raises(ObservabilityTriadError):
            _triad().emit_log("", "msg")


# ──────────────────────────────────────────────────────────────────────────────
# 审计链对接
# ──────────────────────────────────────────────────────────────────────────────


class TestAudit:
    def test_audit_receives_events(self) -> None:
        events: list[tuple[str, dict]] = []
        triad = _triad(audit_sink=lambda e, p: events.append((e, dict(p))))
        triad.emit_trace("t-1", "n1")
        triad.register_counter("c1")
        triad.inc_counter("c1")
        triad.emit_log("INFO", "m1")
        kinds = [e for e, _ in events]
        assert kinds == ["trace", "metric", "log"]
        assert events[1][1]["name"] == "c1"

    def test_audit_exception_swallowed(self) -> None:
        def _bad(event, payload) -> None:
            raise RuntimeError("审计后端故障")

        triad = _triad(audit_sink=_bad)
        entry = triad.emit_log("INFO", "m1")  # 不阻断主链路
        assert isinstance(entry, LogEntry)


# ──────────────────────────────────────────────────────────────────────────────
# 归档裁决（热 7 天 / 冷 Parquet）
# ──────────────────────────────────────────────────────────────────────────────


class TestArchive:
    def test_archivable_after_window(self) -> None:
        clock = _Clock(_T0)
        triad = _triad(clock=clock)
        old = triad.emit_log("INFO", "旧日志")
        clock.advance(days=8)
        fresh = triad.emit_log("INFO", "新日志")
        assert triad.archivable_logs() == (old,)
        assert fresh not in triad.archivable_logs()

    def test_run_archive_ok(self) -> None:
        clock = _Clock(_T0)
        archived: list[tuple[LogEntry, ...]] = []
        triad = _triad(clock=clock, archive_executor=lambda e: archived.append(e))
        triad.emit_log("INFO", "旧1")
        triad.emit_log("INFO", "旧2")
        clock.advance(days=8)
        keep = triad.emit_log("INFO", "新")
        assert triad.run_archive() == 2
        assert len(archived) == 1
        assert [e.message for e in archived[0]] == ["旧1", "旧2"]
        assert triad.logs == (keep,)  # 热存仅余新日志

    def test_run_archive_no_executor_raises(self) -> None:
        clock = _Clock(_T0)
        triad = _triad(clock=clock)
        triad.emit_log("INFO", "旧")
        clock.advance(days=8)
        with pytest.raises(ObservabilityTriadError):
            triad.run_archive()

    def test_run_archive_nothing_returns_zero(self) -> None:
        calls: list = []
        triad = _triad(archive_executor=lambda e: calls.append(e))
        triad.emit_log("INFO", "热数据")
        assert triad.run_archive() == 0
        assert calls == []  # 无可归档不触发执行

    def test_run_archive_executor_failure_raises(self) -> None:
        clock = _Clock(_T0)

        def _bad(entries) -> None:
            raise RuntimeError("Parquet 写失败")

        triad = _triad(clock=clock, archive_executor=_bad)
        triad.emit_log("INFO", "旧")
        clock.advance(days=8)
        with pytest.raises(ObservabilityTriadError):
            triad.run_archive()

    def test_hot_days_invalid_raises(self) -> None:
        with pytest.raises(ObservabilityTriadError):
            _triad(hot_days=0)
        with pytest.raises(ObservabilityTriadError):
            _triad(hot_days=-1)
