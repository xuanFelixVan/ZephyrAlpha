# [BLUEPRINT] MOD-DATA-064 | docs/03_modules/_domain_data/data_compression_archiver/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA-064 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data.test_data_compression_archiver
# [TESTS] src/zephyr/data/data_compression_archiver.py
"""MOD-DATA-064 单元测试：data_compression_archiver 行情数据压缩与归档。

蓝图验收（B1-00106/CAND-DAT-018，C2 D-DATA-08）：
热→温→冷三层归档编排（plan(cutoff)→应归档分区清单）+ 执行经注入 archiver
回调 + 归档索引登记（SQLite 注入 :memory: 连接）+ DuckDB 冷层查询门面
（注入连接；真 duckdb + tmp_path parquet 端到端一例）。时钟全注入。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

duckdb = pytest.importorskip("duckdb", reason="duckdb not installed")
pytest.importorskip(
    "zephyr.data.data_compression_archiver",
    reason="data_compression_archiver not importable",
)

from zephyr.data.data_compression_archiver import (  # noqa: E402
    ArchivePlan,
    DataCompressionArchiver,
    DataCompressionError,
    StorageTier,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)
_CUTOFF = datetime.date(2026, 8, 1)


def _archiver(
    *,
    archiver=None,
    sqlite_conn=None,
    duckdb_conn=None,
) -> DataCompressionArchiver:
    return DataCompressionArchiver(
        clock=lambda: _T0,
        archiver=archiver if archiver is not None else (lambda p: f"/cold/{p}.parquet"),
        sqlite_conn=sqlite_conn,
        duckdb_conn=duckdb_conn,
    )


def _warm(arch: DataCompressionArchiver, partition: str, month: str, rows: int = 100) -> None:
    arch.register_partition(partition, month=month, tier=StorageTier.WARM, rows=rows)


# ──────────────────────────────────────────────────────────────────────────────
# 分区注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterPartition:
    def test_register_ok(self) -> None:
        arch = _archiver()
        _warm(arch, "bars_1m_2026_06", "2026-06")
        assert arch.partitions() == ("bars_1m_2026_06",)
        assert arch.tier_of("bars_1m_2026_06") is StorageTier.WARM

    def test_register_invalid_args_raise(self) -> None:
        arch = _archiver()
        with pytest.raises(DataCompressionError):
            arch.register_partition("", month="2026-06", tier=StorageTier.WARM)
        with pytest.raises(DataCompressionError):
            arch.register_partition("p", month="202606", tier=StorageTier.WARM)  # 非 YYYY-MM
        with pytest.raises(DataCompressionError):
            arch.register_partition("p", month="2026-13", tier=StorageTier.WARM)  # 月份越界
        with pytest.raises(DataCompressionError):
            arch.register_partition("p", month="2026-06", tier="frozen")  # type: ignore[arg-type]
        with pytest.raises(DataCompressionError):
            arch.register_partition("p", month="2026-06", tier=StorageTier.WARM, rows=-1)

    def test_duplicate_register_raises(self) -> None:
        arch = _archiver()
        _warm(arch, "p1", "2026-06")
        with pytest.raises(DataCompressionError):
            arch.register_partition("p1", month="2026-07", tier=StorageTier.HOT)

    def test_bad_compression_raises(self) -> None:
        with pytest.raises(DataCompressionError):
            DataCompressionArchiver(compression="zstd")  # 冷层锁定 snappy


# ──────────────────────────────────────────────────────────────────────────────
# 归档计划
# ──────────────────────────────────────────────────────────────────────────────


class TestPlan:
    def test_plan_due_warm_partitions_sorted(self) -> None:
        arch = _archiver()
        _warm(arch, "bars_1m_2026_07", "2026-07")
        _warm(arch, "bars_1m_2026_05", "2026-05")
        _warm(arch, "bars_1m_2026_06", "2026-06")
        plan = arch.plan(_CUTOFF)
        assert plan.cutoff_month == "2026-08"
        assert plan.partitions == (
            "bars_1m_2026_05",
            "bars_1m_2026_06",
            "bars_1m_2026_07",
        )  # 确定性排序

    def test_plan_excludes_hot_cold_and_current_month(self) -> None:
        arch = _archiver()
        arch.register_partition("hot_p", month="2026-05", tier=StorageTier.HOT)
        arch.register_partition("cold_p", month="2026-05", tier=StorageTier.COLD)
        _warm(arch, "warm_now", "2026-08")  # cutoff 当月不归档
        assert arch.plan(_CUTOFF).partitions == ()

    def test_plan_invalid_cutoff_raises(self) -> None:
        arch = _archiver()
        with pytest.raises(DataCompressionError):
            arch.plan("2026-08-01")  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 归档执行
# ──────────────────────────────────────────────────────────────────────────────


class TestExecute:
    def test_execute_ok_via_injected_archiver(self) -> None:
        calls: list[str] = []
        arch = _archiver(archiver=lambda p: calls.append(p) or f"/cold/{p}.parquet")
        _warm(arch, "bars_1m_2026_06", "2026-06", rows=42)
        records = arch.execute(arch.plan(_CUTOFF))
        assert calls == ["bars_1m_2026_06"]  # 经注入回调写出
        assert len(records) == 1
        assert records[0].path == "/cold/bars_1m_2026_06.parquet"
        assert records[0].rows == 42
        assert records[0].archived_at == _T0
        assert arch.tier_of("bars_1m_2026_06") is StorageTier.COLD

    def test_execute_without_archiver_fail_closed(self) -> None:
        arch = DataCompressionArchiver(clock=lambda: _T0)  # 未注入 archiver
        _warm(arch, "bars_1m_2026_06", "2026-06")
        with pytest.raises(DataCompressionError):
            arch.execute(arch.plan(_CUTOFF))

    def test_execute_empty_plan_no_archiver_ok(self) -> None:
        arch = DataCompressionArchiver(clock=lambda: _T0)
        assert arch.execute(ArchivePlan(cutoff_month="2026-08", partitions=())) == ()

    def test_execute_invalid_args_raise(self) -> None:
        arch = _archiver()
        _warm(arch, "bars_1m_2026_06", "2026-06")
        with pytest.raises(DataCompressionError):
            arch.execute("not-a-plan")  # type: ignore[arg-type]
        with pytest.raises(DataCompressionError):
            arch.execute(ArchivePlan(cutoff_month="2026-08", partitions=("ghost",)))

    def test_execute_rejects_non_warm_partition(self) -> None:
        arch = _archiver()
        arch.register_partition("hot_p", month="2026-05", tier=StorageTier.HOT)
        with pytest.raises(DataCompressionError):
            arch.execute(ArchivePlan(cutoff_month="2026-08", partitions=("hot_p",)))

    def test_execute_rejects_bad_archiver_return(self) -> None:
        arch = _archiver(archiver=lambda p: "")
        _warm(arch, "bars_1m_2026_06", "2026-06")
        with pytest.raises(DataCompressionError):
            arch.execute(arch.plan(_CUTOFF))

    def test_re_execute_raises_already_cold(self) -> None:
        arch = _archiver()
        _warm(arch, "bars_1m_2026_06", "2026-06")
        arch.execute(arch.plan(_CUTOFF))
        with pytest.raises(DataCompressionError):
            arch.execute(ArchivePlan(cutoff_month="2026-08", partitions=("bars_1m_2026_06",)))


# ──────────────────────────────────────────────────────────────────────────────
# 归档索引（SQLite 注入连接）
# ──────────────────────────────────────────────────────────────────────────────


class TestArchiveIndex:
    def test_inmemory_index_sorted(self) -> None:
        arch = _archiver()
        _warm(arch, "bars_1m_2026_07", "2026-07")
        _warm(arch, "bars_1m_2026_05", "2026-05")
        arch.execute(arch.plan(_CUTOFF))
        assert [r.partition for r in arch.index()] == [
            "bars_1m_2026_05",
            "bars_1m_2026_07",
        ]

    def test_sqlite_index_persisted(self) -> None:
        conn = sqlite3.connect(":memory:")
        arch = _archiver(sqlite_conn=conn)
        _warm(arch, "bars_1m_2026_06", "2026-06", rows=7)
        arch.execute(arch.plan(_CUTOFF))
        rows = conn.execute("SELECT partition, path, rows, archived_at FROM archive_index").fetchall()
        assert rows == [
            (
                "bars_1m_2026_06",
                "/cold/bars_1m_2026_06.parquet",
                7,
                _T0.isoformat(),
            )
        ]
        # 索引以库为准
        assert arch.index()[0].rows == 7


# ──────────────────────────────────────────────────────────────────────────────
# DuckDB 冷层查询门面
# ──────────────────────────────────────────────────────────────────────────────


class TestColdQuery:
    def test_query_without_conn_fail_closed(self) -> None:
        arch = _archiver()
        with pytest.raises(DataCompressionError):
            arch.cold_query("SELECT 1")

    def test_query_invalid_sql_raises(self) -> None:
        arch = _archiver(duckdb_conn=duckdb.connect(":memory:"))
        with pytest.raises(DataCompressionError):
            arch.cold_query("")
        with pytest.raises(DataCompressionError):
            arch.cold_query("DROP TABLE t")  # 非只读 SELECT

    def test_real_duckdb_parquet_roundtrip(self, tmp_path) -> None:
        conn = duckdb.connect(":memory:")
        parquet = tmp_path / "bars_1m_2026_06.parquet"
        conn.execute(
            "COPY (SELECT 1 AS ts_code, 10.5 AS close UNION ALL SELECT 2, 11.0) "
            f"TO '{parquet.as_posix()}' (FORMAT PARQUET, COMPRESSION 'snappy')"
        )
        arch = _archiver(duckdb_conn=conn)
        out = arch.cold_query(f"SELECT close FROM read_parquet('{parquet.as_posix()}') ORDER BY ts_code")
        assert out == [(10.5,), (11.0,)]


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            arch = _archiver()
            _warm(arch, "bars_1m_2026_07", "2026-07", rows=3)
            _warm(arch, "bars_1m_2026_05", "2026-05", rows=1)
            arch.register_partition("hot_p", month="2026-05", tier=StorageTier.HOT)
            plan = arch.plan(_CUTOFF)
            records = arch.execute(plan)
            return (plan, records, arch.index(), arch.partitions())

        assert _run() == _run()
