# [BLUEPRINT] MOD-L00-004 | data_source_integrator_blueprint.md | §4
# [TTL] permanent
"""test_ch_rebuild_news_data_tz2.py — news_data 时区二期换表重建脚本单元测试（CAND-DAT-026）。

覆盖（纯 SQL 构造器，零外部依赖）：
  1. sql_copy_partition —— 16:00 指纹 +8h 修正：指纹谓词只依赖本行字段（教训#2 安全形态）/
     29 列全显式/GROUP BY 键/argMax 去重/full_publish_time 不动（跨月由引擎按值归分区）
  2. sql_verify_months —— 跨月对账：源按 toYYYYMM(fixed_pt) 归月 vs 目标按 publish_time 归月
  3. sql_create_rebuild / sql_rename_swap / sql_delta_backfill —— 克隆/原子换名/增量补捞
  4. 表名常量（pre_tz2 保留名）
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "rebuild_news_data_tz2",
    _ROOT / "scripts" / "ch" / "rebuild_news_data_tz2.py",
)
tz2 = importlib.util.module_from_spec(_spec)
sys.modules["rebuild_news_data_tz2"] = tz2
_spec.loader.exec_module(tz2)


class TestCopyPartition:
    def test_fingerprint_plus_8h(self):
        sql = tz2.sql_copy_partition(202506)
        assert "toHour(publish_time) = 16" in sql
        assert "toMinute(publish_time) = 0" in sql
        assert "toSecond(publish_time) = 0" in sql
        assert "publish_time + INTERVAL 8 HOUR" in sql

    def test_fingerprint_row_local_only(self):
        """谓词只依赖本行字段（DAT-025 教训#2：禁同表子查询/禁 ingest 批次依赖）。"""
        sql = tz2.sql_copy_partition(202506)
        assert "ingest_ts =" not in sql.split("GROUP BY")[0].split("fixed_pt")[0]

    def test_group_by_fixed_key(self):
        sql = tz2.sql_copy_partition(202506)
        assert "GROUP BY news_id, fixed_pt" in sql
        assert "toYYYYMM(publish_time) = 202506" in sql  # 按源分区扫描（局部性）

    def test_full_publish_time_untouched(self):
        sql = tz2.sql_copy_partition(202506)
        # full_publish_time 非纯日期语义（侦察实证全天分布），不修正，argMax 直取
        assert "argMax(full_publish_time, ver_ts)" in sql
        assert "full_publish_time + INTERVAL" not in sql
        assert "full_publish_time - INTERVAL" not in sql

    def test_all_29_columns_and_ver_alias(self):
        sql = tz2.sql_copy_partition(202506)
        assert len(tz2.ALL_COLUMNS) == 29
        for col in tz2.ALL_COLUMNS:
            assert col in sql
        assert "ingest_ts AS ver_ts" in sql
        assert "max(ver_ts) AS ingest_ts" in sql


class TestVerifyMonths:
    def test_source_grouped_by_fixed_pt_month(self):
        src, _ = tz2.sql_verify_months()
        assert "toYYYYMM(fixed_pt)" in src

    def test_source_distinct_keys(self):
        """源侧 DISTINCT（同键物理重复行每月虚多 1-2，首跑对账实证）。"""
        src, _ = tz2.sql_verify_months()
        assert "DISTINCT news_id" in src

    def test_target_grouped_by_publish_time_month(self):
        _, dst = tz2.sql_verify_months()
        assert "toYYYYMM(publish_time)" in dst
        assert tz2.REBUILD_TABLE in dst

    def test_target_key_level_count(self):
        """目标侧按键 uniqExact（跨 INSERT 邻月 fixed 撞键行数虚高，键口径才对账）。"""
        _, dst = tz2.sql_verify_months()
        assert "uniqExact((news_id, publish_time))" in dst


class TestLifecycle:
    def test_create_clone(self):
        assert f"CREATE TABLE IF NOT EXISTS {tz2.REBUILD_TABLE} AS {tz2.SRC_TABLE}" in tz2.sql_create_rebuild()

    def test_atomic_swap(self):
        sql = tz2.sql_rename_swap()
        assert f"{tz2.SRC_TABLE} TO {tz2.OLD_TABLE}" in sql
        assert f"{tz2.REBUILD_TABLE} TO {tz2.SRC_TABLE}" in sql

    def test_delta_backfill(self):
        sql = tz2.sql_delta_backfill("2026-08-28 05:00:00")
        assert "2026-08-28 05:00:00" in sql
        assert tz2.OLD_TABLE in sql and tz2.SRC_TABLE in sql

    def test_table_names(self):
        assert tz2.SRC_TABLE == "c3_fundamental.news_data"
        assert tz2.REBUILD_TABLE == "c3_fundamental.news_data_tz2"
        assert "pre_tz2" in tz2.OLD_TABLE
