# [BLUEPRINT] MOD-L00-004 | data_source_integrator_blueprint.md | §4
# [TTL] permanent
"""test_ch_purge_news_data_rr_dup.py — news_data 研报冗余清扫脚本单元测试（CAND-DAT-025）。

覆盖（纯 SQL 构造器，零外部依赖）：
  1. sql_fix_orphan_insert —— 老批单行 +8h 修正重插：29 列显式清单/版本列 now64(3)/
     full_publish_time 默认值守卫/仅单行 id 集合/分区上限放宽
  2. sql_delete_old_rows —— 删除谓词：老批截止+内联 id 子查询+category 限定+
     "有新版本行"守卫（不丢数据）
  3. sql_orphan_where / sql_dry_counts —— 谓词与对账项存在性
  4. recent_backup_ok —— 近 24h 备份检查（真源=backup_state.json）
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "purge_news_data_rr_dup",
    _ROOT / "scripts" / "ch" / "purge_news_data_rr_dup.py",
)
pg = importlib.util.module_from_spec(_spec)
sys.modules["purge_news_data_rr_dup"] = pg
_spec.loader.exec_module(pg)


class TestFixOrphanInsert:
    def test_shifts_publish_time_plus_8h(self):
        sql = pg.sql_fix_orphan_insert()
        assert "publish_time + INTERVAL 8 HOUR" in sql
        assert "now64(3)" in sql  # 版本列取当前（ReplacingMergeTree 视新版本）

    def test_full_publish_time_default_guard(self):
        sql = pg.sql_fix_orphan_insert()
        # 默认空值（epoch≈0）不偏移，防 1970 行被 +8h 污染
        assert "full_publish_time" in sql and "86400" in sql

    def test_only_single_row_old_ids(self):
        sql = pg.sql_fix_orphan_insert()
        assert "HAVING count() = 1" in sql
        assert pg.CUTOFF in sql
        assert "category = 'research_report'" in sql

    def test_column_list_matches_schema(self):
        # 29 列（system.columns 实测）：缺列会写 DEFAULT 造成数据丢失
        assert len(pg.FIX_INSERT_COLUMNS) == 29
        assert "ingest_ts" in pg.FIX_INSERT_COLUMNS
        for col in pg.FIX_INSERT_COLUMNS:
            assert col in pg.sql_fix_orphan_insert()

    def test_partition_limit_lifted(self):
        # 单行老批跨 2010-2026 全月分区（>100），单次 INSERT 须显式放宽分区数上限
        assert "max_partitions_per_insert_block" in pg.sql_fix_orphan_insert()


class TestDeleteOldRows:
    def test_predicate_scoped(self):
        sql = pg.sql_delete_old_rows()
        assert "ALTER TABLE c3_fundamental.news_data DELETE" in sql
        assert "category = 'research_report'" in sql
        assert pg.CUTOFF in sql
        assert "ingest_ts <" in sql  # 只删老批
        assert "SELECT news_id FROM" in sql  # id 集内联子查询（writer 无 TRUNCATE/DROP 授权，已实证）

    def test_requires_newer_twin(self):
        """防数据丢失底线：只有存在新批/修正行（ingest>=cutoff）的多行 id 才进删除集。"""
        sql = pg.sql_delete_old_rows()
        assert "count() > 1" in sql
        assert "countIf(ingest_ts >=" in sql and ">= 1" in sql


class TestDryRunCounts:
    def test_count_queries_exist(self):
        queries = pg.sql_dry_counts()
        kinds = {k for k, _ in queries}
        # 对账四件套：双版本 id 数/待删老行数/老批单行待修正数/全老批残留 id 数
        assert {"dup_ids", "delete_rows", "orphan_fix_rows", "stuck_old_only_ids"} <= kinds

    def test_orphan_where(self):
        w = pg.sql_orphan_where()
        assert "category = 'research_report'" in w and pg.CUTOFF in w


class TestBackupGuard:
    """近 24h 备份检查（真源=backup_state.json，system.backups 本部署为空已实证）。"""

    _NOW = pg.datetime(2026, 8, 27, 3, 0).astimezone()

    def test_fresh_verified_backup_ok(self):
        ok, _ = pg.recent_backup_ok(
            {"last_ch_backup_time": "2026-08-26T09:41:06.2+08:00", "last_ch_backup_verified": True},
            self._NOW,
        )
        assert ok

    def test_stale_backup_rejected(self):
        ok, msg = pg.recent_backup_ok(
            {"last_ch_backup_time": "2026-08-25T01:00:00+08:00", "last_ch_backup_verified": True},
            self._NOW,
        )
        assert not ok and "24h" in msg

    def test_unverified_rejected(self):
        ok, _ = pg.recent_backup_ok({"last_ch_backup_time": "2026-08-27T02:00:00+08:00"}, self._NOW)
        assert not ok

    def test_missing_state_rejected(self):
        assert not pg.recent_backup_ok({}, self._NOW)[0]

    def test_bad_timestamp_rejected(self):
        assert not pg.recent_backup_ok(
            {"last_ch_backup_time": "not-a-time", "last_ch_backup_verified": True}, self._NOW
        )[0]
