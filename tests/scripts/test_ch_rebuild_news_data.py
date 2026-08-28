# [BLUEPRINT] MOD-L00-004 | data_source_integrator_blueprint.md | §4
# [TTL] permanent
"""test_ch_rebuild_news_data.py — news_data 换表重建脚本单元测试（CAND-DAT-025 事故处置）。

覆盖（纯 SQL 构造器，零外部依赖）：
  1. sql_copy_partition —— argMax 按键去重：29 列全显式/GROUP BY 键/误伤批 -8h 精确反演
     （ ingest 批次时间戳全等谓词，仅 08:00 命中；full_publish_time 同步反演带默认值守卫）
  2. sql_create_rebuild —— schema 克隆（AS 复制引擎定义）
  3. sql_rename_swap —— 原子双 RENAME
  4. sql_months / sql_verify_partition / sql_delta_backfill —— 对账与增量补捞
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "rebuild_news_data",
    _ROOT / "scripts" / "ch" / "rebuild_news_data.py",
)
rb = importlib.util.module_from_spec(_spec)
sys.modules["rebuild_news_data"] = rb
_spec.loader.exec_module(rb)


class TestCopyPartition:
    def test_group_by_fixed_key(self):
        sql = rb.sql_copy_partition(202506)
        assert "GROUP BY news_id, fixed_pt" in sql
        assert "toYYYYMM(publish_time) = 202506" in sql

    def test_all_29_columns_present(self):
        sql = rb.sql_copy_partition(202506)
        assert len(rb.ALL_COLUMNS) == 29
        for col in rb.ALL_COLUMNS:
            assert col in sql

    def test_argmax_per_non_key_column(self):
        sql = rb.sql_copy_partition(202506)
        # 非键列逐列 argMax(col, ver_ts)；版本列取 max；ver_ts 别名规避聚合嵌套（CH 184 实证）
        assert "argMax(title, ver_ts)" in sql
        assert "argMax(related_symbols, ver_ts)" in sql  # Array 列同样可 argMax
        assert "max(ver_ts) AS ingest_ts" in sql
        assert "ingest_ts AS ver_ts" in sql

    def test_miscorrection_exact_reversal(self):
        sql = rb.sql_copy_partition(202506)
        # 仅误伤批（ingest 全等于 18:58:02.495）且 08:00:00 指纹的行 -8h
        assert "2026-08-26 18:58:02.495" in sql
        assert "toHour(publish_time) = 8" in sql
        assert "INTERVAL 8 HOUR" in sql
        # full_publish_time 反演带默认值守卫（DateTime64 直接比较，规避 toUnixTimestamp UInt32 溢出）
        assert "full_publish_time > toDateTime64('1970-01-02" in sql

    def test_month_parametrized(self):
        assert "202401" in rb.sql_copy_partition(202401)
        assert "202401" not in rb.sql_copy_partition(202506)


class TestCreateRebuild:
    def test_schema_clone(self):
        sql = rb.sql_create_rebuild()
        assert f"CREATE TABLE IF NOT EXISTS {rb.REBUILD_TABLE} AS {rb.SRC_TABLE}" in sql


class TestRenameSwap:
    def test_atomic_double_rename(self):
        sql = rb.sql_rename_swap()
        assert "RENAME TABLE" in sql
        assert f"{rb.SRC_TABLE} TO {rb.CORRUPT_TABLE}" in sql
        assert f"{rb.REBUILD_TABLE} TO {rb.SRC_TABLE}" in sql
        assert "," in sql  # 单语句多 rename = 原子交换


class TestVerifyAndDelta:
    def test_months_query(self):
        assert "DISTINCT toYYYYMM(publish_time)" in rb.sql_months()

    def test_verify_partition(self):
        src, dst = rb.sql_verify_partition(202506)
        assert "DISTINCT news_id" in src  # 源侧 DISTINCT 键数（含误伤反演同口径）
        assert "fixed_pt" in src
        assert "202506" in src and "202506" in dst

    def test_delta_backfill_uses_cutoff(self):
        sql = rb.sql_delta_backfill("2026-08-28 04:00:00")
        assert "2026-08-28 04:00:00" in sql
        assert rb.CORRUPT_TABLE in sql  # 换名后从旧表补捞窗口期新行
        assert rb.SRC_TABLE in sql  # 写入新表（已顶名）


class TestConstants:
    def test_table_names(self):
        assert rb.SRC_TABLE == "c3_fundamental.news_data"
        assert rb.REBUILD_TABLE == "c3_fundamental.news_data_rebuild"
        assert "corrupt" in rb.CORRUPT_TABLE
