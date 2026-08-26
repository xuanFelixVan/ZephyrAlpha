# [BLUEPRINT] MOD-DATA-066 | docs/03_modules/_domain_data/source_sla_tracker/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA-066 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data.test_source_sla_tracker
# [TESTS] src/zephyr/data/source_sla_tracker.py
"""MOD-DATA-066 单元测试：source_sla_tracker 数据源可用性 SLA 追踪器。

蓝图验收（B13-04332/CAND-DAT-020，A3数据架构）：
按源聚合可用率/延迟 P50·P99/失败原因分布（注入性能记录序列）+
日周报生成（周期报表字典）+ SLA 达标率判定（目标注入）+ 看板数据输出。
全内存确定性（最近秩百分位），不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data.source_sla_tracker",
    reason="source_sla_tracker not importable",
)

from zephyr.data.source_sla_tracker import (  # noqa: E402
    ProbeRecord,
    SourceSlaError,
    SourceSlaTracker,
)

_D1 = datetime.datetime(2026, 8, 24, 9, 30, 0)   # 周一（ISO 2026-W35）
_D2 = datetime.datetime(2026, 8, 25, 9, 30, 0)   # 周二


def _tracker() -> SourceSlaTracker:
    tracker = SourceSlaTracker()
    tracker.register_target("tushare", availability=0.99, p99_latency_ms=500.0)
    return tracker


def _rec(
    source: str = "tushare",
    ts: datetime.datetime = _D2,
    ok: bool = True,
    latency: float = 100.0,
    reason: str | None = None,
) -> ProbeRecord:
    return ProbeRecord(source=source, ts=ts, ok=ok, latency_ms=latency, error_reason=reason)


# ──────────────────────────────────────────────────────────────────────────────
# 目标注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterTarget:
    def test_register_ok(self) -> None:
        tracker = _tracker()
        assert tracker.sources() == ("tushare",)
        target = tracker.target_of("tushare")
        assert target.availability == pytest.approx(0.99)
        assert target.p99_latency_ms == pytest.approx(500.0)

    def test_register_invalid_args_raise(self) -> None:
        tracker = SourceSlaTracker()
        with pytest.raises(SourceSlaError):
            tracker.register_target("", availability=0.99, p99_latency_ms=500.0)
        with pytest.raises(SourceSlaError):
            tracker.register_target("s", availability=0.0, p99_latency_ms=500.0)
        with pytest.raises(SourceSlaError):
            tracker.register_target("s", availability=1.01, p99_latency_ms=500.0)
        with pytest.raises(SourceSlaError):
            tracker.register_target("s", availability=0.99, p99_latency_ms=0.0)

    def test_register_duplicate_raises(self) -> None:
        tracker = _tracker()
        with pytest.raises(SourceSlaError):
            tracker.register_target("tushare", availability=0.95, p99_latency_ms=300.0)

    def test_target_of_unknown_raises(self) -> None:
        with pytest.raises(SourceSlaError):
            SourceSlaTracker().target_of("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 记录摄入
# ──────────────────────────────────────────────────────────────────────────────


class TestIngest:
    def test_ingest_ok(self) -> None:
        tracker = _tracker()
        assert tracker.ingest([_rec(), _rec()]) == 2

    def test_ingest_unregistered_source_raises(self) -> None:
        tracker = _tracker()
        with pytest.raises(SourceSlaError):
            tracker.ingest([_rec(source="ghost")])

    def test_ingest_invalid_records_raise(self) -> None:
        tracker = _tracker()
        with pytest.raises(SourceSlaError):
            tracker.ingest([_rec(latency=-1.0)])                     # 负延迟
        with pytest.raises(SourceSlaError):
            tracker.ingest([_rec(ok=False, reason=None)])            # 失败缺原因
        with pytest.raises(SourceSlaError):
            tracker.ingest([_rec(ok=True, reason="timeout")])        # 成功带原因
        with pytest.raises(SourceSlaError):
            tracker.ingest([_rec(ts="2026-08-25")])                  # type: ignore[arg-type]  # 非法时间戳
        with pytest.raises(SourceSlaError):
            tracker.ingest(["not-a-record"])                         # type: ignore[list-item]  # 非法类型


# ──────────────────────────────────────────────────────────────────────────────
# 窗口聚合（可用率 / P50 / P99 / 失败分布）
# ──────────────────────────────────────────────────────────────────────────────


class TestAggregate:
    def _filled(self) -> SourceSlaTracker:
        tracker = _tracker()
        records = [_rec(latency=float(i * 10)) for i in range(1, 6)]  # 10..50
        records.append(_rec(ok=False, latency=600.0, reason="timeout"))
        records.append(_rec(ok=False, latency=700.0, reason="timeout"))
        records.append(_rec(ok=False, latency=800.0, reason="http_500"))
        tracker.ingest(records)
        return tracker

    def test_availability_and_counts(self) -> None:
        tracker = self._filled()
        agg = tracker.aggregate("tushare", _D2, _D2 + datetime.timedelta(days=1))
        assert agg.total == 8
        assert agg.ok_count == 5
        assert agg.availability == pytest.approx(5 / 8)

    def test_percentiles_nearest_rank(self) -> None:
        tracker = self._filled()
        agg = tracker.aggregate("tushare", _D2, _D2 + datetime.timedelta(days=1))
        # 延迟序 [10,20,30,40,50,600,700,800]：p50=rank4=40, p99=rank8=800
        assert agg.p50_ms == pytest.approx(40.0)
        assert agg.p99_ms == pytest.approx(800.0)

    def test_failure_reason_distribution_sorted(self) -> None:
        tracker = self._filled()
        agg = tracker.aggregate("tushare", _D2, _D2 + datetime.timedelta(days=1))
        assert agg.failure_reasons == (("http_500", 1), ("timeout", 2))

    def test_window_filters_records(self) -> None:
        tracker = self._filled()
        tracker.ingest([_rec(ts=_D1, latency=999.0)])  # 窗口外
        agg = tracker.aggregate("tushare", _D2, _D2 + datetime.timedelta(days=1))
        assert agg.total == 8  # 不含 _D1 记录

    def test_aggregate_invalid_args_raise(self) -> None:
        tracker = self._filled()
        with pytest.raises(SourceSlaError):
            tracker.aggregate("ghost", _D2, _D2 + datetime.timedelta(days=1))
        with pytest.raises(SourceSlaError):
            tracker.aggregate("tushare", _D2, _D2)                   # 空区间
        with pytest.raises(SourceSlaError):
            tracker.aggregate("tushare", _D1, _D1 + datetime.timedelta(hours=1))  # 空窗口


# ──────────────────────────────────────────────────────────────────────────────
# 日周报与达标判定
# ──────────────────────────────────────────────────────────────────────────────


class TestReports:
    def _filled(self) -> SourceSlaTracker:
        tracker = _tracker()
        tracker.register_target("akshare", availability=0.50, p99_latency_ms=100.0)
        tracker.ingest([
            _rec(ts=_D2, latency=100.0),
            _rec(ts=_D2, ok=False, latency=600.0, reason="timeout"),   # tushare 违约
            _rec(source="akshare", ts=_D2, latency=50.0),              # akshare 达标
            _rec(ts=_D1, latency=200.0),                               # 日报窗口外
        ])
        return tracker

    def test_daily_report(self) -> None:
        tracker = self._filled()
        report = tracker.report_daily(datetime.date(2026, 8, 25))
        assert report["period"] == {"kind": "daily", "key": "2026-08-25"}
        assert set(report["sources"]) == {"akshare", "tushare"}
        tushare = report["sources"]["tushare"]
        assert tushare["total"] == 2                    # _D1 记录不入日报
        assert tushare["availability"] == pytest.approx(0.5)
        assert tushare["target_met"]["overall"] is False
        assert tushare["target_met"]["availability"] is False
        akshare = report["sources"]["akshare"]
        assert akshare["target_met"]["overall"] is True

    def test_daily_report_omits_recordless_sources(self) -> None:
        tracker = self._filled()
        report = tracker.report_daily(datetime.date(2026, 8, 26))  # 无记录日
        assert report["sources"] == {}

    def test_weekly_report_iso_window(self) -> None:
        tracker = self._filled()
        report = tracker.report_weekly(2026, 35)  # _D1/_D2 同属 W35
        assert report["period"] == {"kind": "weekly", "key": "2026-W35"}
        assert report["sources"]["tushare"]["total"] == 3  # 含周一记录

    def test_report_invalid_args_raise(self) -> None:
        tracker = _tracker()
        with pytest.raises(SourceSlaError):
            tracker.report_daily("2026-08-25")  # type: ignore[arg-type]
        with pytest.raises(SourceSlaError):
            tracker.report_weekly(2026, 99)     # ISO 周越界


# ──────────────────────────────────────────────────────────────────────────────
# 看板输出
# ──────────────────────────────────────────────────────────────────────────────


class TestDashboard:
    def test_dashboard_statuses_sorted(self) -> None:
        tracker = _tracker()
        tracker.register_target("akshare", availability=0.99, p99_latency_ms=100.0)
        tracker.register_target("sina", availability=0.99, p99_latency_ms=100.0)
        tracker.ingest([
            _rec(source="tushare", latency=100.0),                              # ok
            _rec(source="akshare", ok=False, latency=600.0, reason="timeout"),  # breach
        ])
        board = tracker.dashboard()
        assert list(board) == ["akshare", "sina", "tushare"]  # 确定性排序
        assert board["tushare"]["status"] == "ok"
        assert board["akshare"]["status"] == "breach"
        assert board["sina"] == {"total": 0, "status": "no_data"}


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            tracker = _tracker()
            tracker.ingest([
                _rec(latency=10.0),
                _rec(ok=False, latency=900.0, reason="timeout"),
                _rec(ts=_D1, latency=20.0),
            ])
            agg = tracker.aggregate("tushare", _D1, _D1 + datetime.timedelta(days=2))
            daily = tracker.report_daily(datetime.date(2026, 8, 25))
            weekly = tracker.report_weekly(2026, 35)
            return (agg, daily, weekly, tracker.dashboard())

        assert _run() == _run()
