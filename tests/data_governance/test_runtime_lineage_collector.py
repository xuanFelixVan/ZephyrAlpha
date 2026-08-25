# [BLUEPRINT] MOD-DATA_GOV-006 | docs/03_modules/_domain_data_governance/runtime_lineage_collector/blueprint.md | §test
# [MODULE] tests.data_governance.test_runtime_lineage_collector
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] zephyr.data_governance.core.runtime_lineage_collector
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_runtime_lineage_collector.py
# [A_test] module_id: MOD-DATA_GOV-006 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA_GOV-006 单元测试: M8-S03 动态采集器。

覆盖: emit 正常入缓冲、畸形事件丢弃计数 fail-open 不抛、缓冲溢出丢弃新事件、
flush 成功排空/sink 失败事件回滚+计数不抛、盘后汇总入图（去重/幂等/环拒记复用
S01 语义）、空缓冲汇总零报告、构造参数 Fail-Closed、端到端 emit→汇总→上下游查询。
"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.lineage_tracker import LineageTracker
from zephyr.data_governance.core.runtime_lineage_collector import (
    CollectorStats,
    RuntimeLineageCollector,
    RuntimeLineageError,
    RuntimeLineageEvent,
)


class TestEmit:
    def test_emit_normal_event(self) -> None:
        c = RuntimeLineageCollector()
        ok = c.emit("market.kline_daily", "factor.momentum_20d", "compute", run_id="r1")
        assert ok is True
        stats = c.stats()
        assert stats.emitted == 1
        assert stats.buffered == 1
        assert stats.dropped == 0

    def test_emit_event_object(self) -> None:
        c = RuntimeLineageCollector()
        ev = RuntimeLineageEvent(source="a", target="b", transformation="t")
        assert c.emit_event(ev) is True
        assert c.stats().buffered == 1

    def test_malformed_event_dropped_fail_open(self) -> None:
        c = RuntimeLineageCollector()
        assert c.emit("  ", "factor.x") is False
        assert c.emit("market.x", "") is False
        stats = c.stats()
        assert stats.emitted == 0
        assert stats.dropped == 2
        assert stats.buffered == 0

    def test_buffer_overflow_drops_new_fail_open(self) -> None:
        c = RuntimeLineageCollector(max_buffer=2)
        assert c.emit("a", "b") is True
        assert c.emit("b", "c") is True
        assert c.emit("c", "d") is False  # 缓冲满，丢弃新事件
        stats = c.stats()
        assert stats.emitted == 2
        assert stats.dropped == 1
        assert stats.buffered == 2

    def test_invalid_max_buffer_fail_closed(self) -> None:
        with pytest.raises(RuntimeLineageError):
            RuntimeLineageCollector(max_buffer=0)


class TestFlush:
    def test_flush_success_drains_buffer(self) -> None:
        c = RuntimeLineageCollector()
        c.emit("a", "b")
        c.emit("b", "c")
        received: list[RuntimeLineageEvent] = []
        n = c.flush(received.extend)
        assert n == 2
        assert len(received) == 2
        assert received[0].source == "a"
        assert c.stats().buffered == 0

    def test_flush_sink_error_rolls_back_fail_open(self) -> None:
        c = RuntimeLineageCollector()
        c.emit("a", "b")

        def bad_sink(events: list[RuntimeLineageEvent]) -> None:
            raise RuntimeError("io 故障")

        n = c.flush(bad_sink)
        assert n == 0
        stats = c.stats()
        assert stats.flush_errors == 1
        assert stats.buffered == 1  # 事件回滚不丢

    def test_flush_empty_buffer_zero(self) -> None:
        c = RuntimeLineageCollector()
        assert c.flush(lambda evts: None) == 0


class TestAggregateIntoTracker:
    def test_aggregate_drains_and_ingests(self) -> None:
        c = RuntimeLineageCollector()
        c.emit("market.kline_daily", "factor.momentum_20d", "compute")
        c.emit("factor.momentum_20d", "signal.alpha", "generate")
        tracker = LineageTracker()
        report = c.aggregate_into_tracker(tracker)
        assert report.edges == 2
        assert report.added == 2
        assert c.stats().buffered == 0
        assert tracker.get_upstream("signal.alpha") == ["factor.momentum_20d", "market.kline_daily"]

    def test_aggregate_dedup_and_idempotent(self) -> None:
        c = RuntimeLineageCollector()
        c.emit("a", "b")
        c.emit("a", "b")  # 批内重复→去重首条胜出
        tracker = LineageTracker()
        report = c.aggregate_into_tracker(tracker)
        assert report.edges == 2
        assert report.added == 1
        assert report.skipped == 1
        # 二次汇总同边→幂等 updated
        c.emit("a", "b")
        report2 = c.aggregate_into_tracker(tracker)
        assert report2.added == 0
        assert report2.updated == 1

    def test_aggregate_cycle_rejected_not_interrupting(self) -> None:
        c = RuntimeLineageCollector()
        c.emit("a", "b")
        c.emit("b", "a")  # 成环→拒记不中断
        c.emit("b", "c")
        tracker = LineageTracker()
        report = c.aggregate_into_tracker(tracker)
        assert report.added == 2
        assert len(report.rejected) == 1
        assert report.rejected[0][0] == "b"
        assert report.rejected[0][1] == "a"

    def test_aggregate_empty_buffer_zero_report(self) -> None:
        c = RuntimeLineageCollector()
        tracker = LineageTracker()
        report = c.aggregate_into_tracker(tracker)
        assert report.edges == 0
        assert report.added == 0

    def test_aggregate_none_tracker_fail_closed(self) -> None:
        c = RuntimeLineageCollector()
        with pytest.raises(RuntimeLineageError):
            c.aggregate_into_tracker(None)

    def test_end_to_end_stats_consistency(self) -> None:
        c = RuntimeLineageCollector()
        c.emit("s1", "t1", "compute", run_id="r1", emitted_at="2026-08-25T15:00:00")
        c.emit("", "t2")  # 畸形
        tracker = LineageTracker()
        c.aggregate_into_tracker(tracker)
        stats = c.stats()
        assert isinstance(stats, CollectorStats)
        assert stats.emitted == 1
        assert stats.dropped == 1
        assert stats.buffered == 0
