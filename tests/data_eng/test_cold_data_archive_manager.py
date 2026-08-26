# [BLUEPRINT] MOD-DATENG-002 | docs/03_modules/_domain_data_eng/cold_data_archive_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATENG-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_eng.test_cold_data_archive_manager
# [TESTS] src/zephyr/data_eng/cold_data_archive_manager.py
"""MOD-DATENG-002 单元测试：cold_data_archive_manager 冷数据归档管理器。

蓝图验收（B13-04331/CAND-DATENG-005，A3数据架构）：
CH老分区→Parquet(zstd)归档编排（plan/run + 注入 archiver）+ 归档索引
（SQLite 注入连接，partition/path/hash/archived_at）+ 保留期清理裁决
（注册表 + purge_executor）+ 只读检索 + auto_archive 周期计划。
索引用 :memory: SQLite，archiver/purge 全内存替身，不触网不触盘。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.data_eng.cold_data_archive_manager",
    reason="cold_data_archive_manager not importable",
)

from zephyr.data_eng.cold_data_archive_manager import (  # noqa: E402
    ColdArchiveError,
    ColdDataArchiveManager,
    PartitionInfo,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_DAY = datetime.timedelta(days=1)


def _mgr(
    *,
    archiver=None,
    purge_executor=None,
    alerts: list | None = None,
    clock=lambda: _T0,
) -> ColdDataArchiveManager:
    return ColdDataArchiveManager(
        index_conn=sqlite3.connect(":memory:"),
        clock=clock,
        archiver=archiver if archiver is not None else (lambda p: (f"/arch/{p.table}/{p.partition}.parquet", "h-" + p.partition)),
        purge_executor=purge_executor,
        alert_sink=(lambda m: alerts.append(m)) if alerts is not None else None,
    )


def _p(table: str, partition: str, days_ago: int) -> PartitionInfo:
    return PartitionInfo(table=table, partition=partition, max_ts=_T0 - days_ago * _DAY, row_count=100)


# ── 构造 Fail-Closed ─────────────────────────────────────────────────────


def test_init_requires_index_conn():
    with pytest.raises(ColdArchiveError, match="index_conn"):
        ColdDataArchiveManager(index_conn=None)


def test_init_creates_index_table():
    mgr = _mgr()
    row = mgr._conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='archive_index'"
    ).fetchone()
    assert row is not None


# ── plan_archive ──────────────────────────────────────────────────────────


def test_plan_archive_selects_old_partitions_sorted():
    mgr = _mgr()
    parts = [
        _p("bars", "2026_07", 40),
        _p("bars", "2026_08", 5),
        _p("ticks", "2026_06", 80),
    ]
    plan = mgr.plan_archive(parts, cutoff=_T0 - 30 * _DAY)
    assert [p.partition for p in plan.partitions] == ["2026_07", "2026_06"]
    assert [p.table for p in plan.partitions] == ["bars", "ticks"]


def test_plan_archive_empty_when_nothing_old():
    mgr = _mgr()
    plan = mgr.plan_archive([_p("bars", "2026_08", 1)], cutoff=_T0 - 30 * _DAY)
    assert plan.partitions == ()


def test_plan_archive_boundary_excludes_equal_cutoff():
    mgr = _mgr()
    info = PartitionInfo(table="bars", partition="p1", max_ts=_T0 - 30 * _DAY)
    plan = mgr.plan_archive([info], cutoff=_T0 - 30 * _DAY)
    assert plan.partitions == ()


def test_plan_archive_rejects_empty_table():
    mgr = _mgr()
    with pytest.raises(ColdArchiveError, match="table 为空"):
        mgr.plan_archive([PartitionInfo(table="", partition="p1", max_ts=_T0)], cutoff=_T0)


def test_plan_archive_rejects_negative_row_count():
    mgr = _mgr()
    info = PartitionInfo(table="t", partition="p", max_ts=_T0, row_count=-1)
    with pytest.raises(ColdArchiveError, match="row_count"):
        mgr.plan_archive([info], cutoff=_T0)


# ── run_archive + 索引 ────────────────────────────────────────────────────


def test_run_archive_registers_index_and_records():
    mgr = _mgr()
    recs = mgr.run_archive([_p("bars", "2026_06", 60)], cutoff=_T0 - 30 * _DAY)
    assert len(recs) == 1
    rec = recs[0]
    assert rec.path == "/arch/bars/2026_06.parquet"
    assert rec.content_hash == "h-2026_06"
    assert rec.archived_at == _T0
    assert mgr.lookup("bars", "2026_06") == rec


def test_run_archive_duplicate_partition_rejected():
    mgr = _mgr()
    mgr.run_archive([_p("bars", "2026_06", 60)], cutoff=_T0 - 30 * _DAY)
    with pytest.raises(ColdArchiveError, match="重复归档"):
        mgr.run_archive([_p("bars", "2026_06", 90)], cutoff=_T0 - 30 * _DAY)


def test_run_archive_requires_archiver_callback():
    mgr = ColdDataArchiveManager(index_conn=sqlite3.connect(":memory:"), clock=lambda: _T0)
    with pytest.raises(ColdArchiveError, match="archiver 未注入"):
        mgr.run_archive([_p("bars", "2026_06", 60)], cutoff=_T0 - 30 * _DAY)


def test_run_archive_rejects_empty_archiver_result():
    mgr = _mgr(archiver=lambda p: ("", "h"))
    with pytest.raises(ColdArchiveError, match="archiver 返回非法"):
        mgr.run_archive([_p("bars", "2026_06", 60)], cutoff=_T0 - 30 * _DAY)


def test_run_archive_deterministic_order():
    mgr = _mgr()
    parts = [_p("ticks", "p2", 50), _p("bars", "p1", 50), _p("bars", "p0", 50)]
    recs = mgr.run_archive(parts, cutoff=_T0 - 30 * _DAY)
    assert [(r.table, r.partition) for r in recs] == [("bars", "p0"), ("bars", "p1"), ("ticks", "p2")]


# ── 只读检索 ──────────────────────────────────────────────────────────────


def test_lookup_miss_returns_none():
    mgr = _mgr()
    assert mgr.lookup("bars", "nope") is None


def test_lookup_rejects_empty_args():
    mgr = _mgr()
    with pytest.raises(ColdArchiveError):
        mgr.lookup("", "p1")


def test_list_archived_filter_and_sort():
    mgr = _mgr()
    mgr.run_archive(
        [_p("ticks", "t1", 60), _p("bars", "b2", 60), _p("bars", "b1", 60)],
        cutoff=_T0 - 30 * _DAY,
    )
    assert [r.partition for r in mgr.list_archived()] == ["b1", "b2", "t1"]
    assert [r.partition for r in mgr.list_archived(table="bars")] == ["b1", "b2"]


# ── 保留策略与清理 ────────────────────────────────────────────────────────


def test_register_retention_rejects_non_positive():
    mgr = _mgr()
    with pytest.raises(ColdArchiveError, match="retention_days"):
        mgr.register_retention("bars", 0)
    with pytest.raises(ColdArchiveError, match="table 为空"):
        mgr.register_retention("", 10)


def test_plan_purge_respects_retention_and_unregistered_tables():
    mgr = _mgr()
    mgr.run_archive([_p("bars", "b1", 130), _p("ticks", "t1", 130)], cutoff=_T0 - 30 * _DAY)
    mgr.register_retention("bars", 30)
    # 时钟推进 31 天：bars 超期，ticks 未注册策略不参与（注册表闭合）
    mgr._clock = lambda: _T0 + 31 * _DAY
    verdicts = mgr.plan_purge()
    assert [(v.table, v.partition) for v in verdicts] == [("bars", "b1")]
    assert "超保留期" in verdicts[0].reason


def test_run_purge_executes_and_removes_index():
    purged: list = []
    alerts: list = []
    mgr = _mgr(purge_executor=lambda rec: purged.append(rec), alerts=alerts)
    mgr.run_archive([_p("bars", "b1", 130)], cutoff=_T0 - 30 * _DAY)
    mgr.register_retention("bars", 30)
    mgr._clock = lambda: _T0 + 31 * _DAY
    verdicts = mgr.run_purge()
    assert len(verdicts) == 1
    assert [r.partition for r in purged] == ["b1"]
    assert mgr.lookup("bars", "b1") is None
    assert any("已清理" in m for m in alerts)


def test_run_purge_requires_executor():
    mgr = _mgr()
    mgr.run_archive([_p("bars", "b1", 130)], cutoff=_T0 - 30 * _DAY)
    mgr.register_retention("bars", 30)
    mgr._clock = lambda: _T0 + 31 * _DAY
    with pytest.raises(ColdArchiveError, match="purge_executor 未注入"):
        mgr.run_purge()


def test_run_purge_noop_when_nothing_expired():
    mgr = _mgr(purge_executor=lambda rec: None)
    mgr.run_archive([_p("bars", "b1", 40)], cutoff=_T0 - 30 * _DAY)
    mgr.register_retention("bars", 365)
    assert mgr.run_purge() == ()
    assert mgr.lookup("bars", "b1") is not None


# ── auto_archive 周期计划 ─────────────────────────────────────────────────


def test_auto_archive_schedule_generates_periodic_runs():
    mgr = _mgr()
    parts = [_p("bars", "old", 400), _p("bars", "new", 1)]
    runs = mgr.auto_archive_schedule(
        parts,
        cutoff=_T0 - 30 * _DAY,
        period=7 * _DAY,
        horizon=35 * _DAY,
    )
    assert len(runs) == 5
    assert runs[0].run_at == _T0 + 7 * _DAY
    assert runs[4].run_at == _T0 + 35 * _DAY
    # 每次 cutoff 前移，老分区始终应归档，新分区随 cutoff 前移最终也变老归档
    assert [p.partition for p in runs[0].plan.partitions] == ["old"]
    assert [p.partition for p in runs[4].plan.partitions] == ["new", "old"]


def test_auto_archive_schedule_rejects_bad_period():
    mgr = _mgr()
    with pytest.raises(ColdArchiveError, match="period"):
        mgr.auto_archive_schedule([], cutoff=_T0, period=datetime.timedelta(0), horizon=_DAY)
    with pytest.raises(ColdArchiveError, match="horizon"):
        mgr.auto_archive_schedule([], cutoff=_T0, period=_DAY, horizon=-_DAY)


def test_auto_archive_schedule_empty_when_horizon_lt_period():
    mgr = _mgr()
    runs = mgr.auto_archive_schedule([], cutoff=_T0, period=7 * _DAY, horizon=3 * _DAY)
    assert runs == ()


# ── 确定性 ────────────────────────────────────────────────────────────────


def test_same_input_same_output():
    def _run():
        mgr = _mgr()
        parts = [_p("ticks", "t2", 90), _p("bars", "b1", 60), _p("ticks", "t1", 45)]
        recs = mgr.run_archive(parts, cutoff=_T0 - 30 * _DAY)
        return [(r.table, r.partition, r.path, r.content_hash, r.archived_at) for r in recs]

    assert _run() == _run()
