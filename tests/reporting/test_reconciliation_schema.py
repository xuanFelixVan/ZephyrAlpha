# [BLUEPRINT] MOD-TRADING-003 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] tests.reporting.test_reconciliation_schema
# [DOMAIN] D_REPORTING
# [INVARIANTS] 仅定义不执行; 四表齐全; 哈希链字段; SQLite 内存可执行校验(测试侧验证语法合法, 生产侧零连接)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""对账/归因 DB schema 定义测试（54 号 §7 开放问题，AI-NIGHT-001 包P）。

测试侧用 SQLite 内存库验证 DDL 语法合法+表结构齐全——仅测试验证手段，
生产代码路径零连接零执行（模块无任何 DB 调用）。
"""

from __future__ import annotations

import sqlite3

import pytest

from zephyr.reporting.reconciliation_schema import (
    ALL_TABLES,
    get_ddl,
    table_names,
)

_EXPECTED_TABLES = {
    "reconciliation_differences",
    "attribution_results",
    "audit_trail",
    "report_archive",
}


def _sqlite_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


class TestSchemaDefinition:
    def test_four_tables_defined_in_order(self):
        assert table_names() == (
            "reconciliation_differences",
            "attribution_results",
            "audit_trail",
            "report_archive",
        )
        assert len(ALL_TABLES) == 4

    def test_get_ddl_unknown_table_raises(self):
        with pytest.raises(KeyError):
            get_ddl("nonexistent")

    def test_all_ddl_idempotent_if_not_exists(self):
        for ddl in ALL_TABLES:
            assert "CREATE TABLE IF NOT EXISTS" in ddl

    def test_ddl_executes_on_in_memory_sqlite(self, tmp_path):
        # 语法合法性验证（内存库，零生产副作用）
        conn = sqlite3.connect(":memory:")
        try:
            for ddl in ALL_TABLES:
                conn.execute(ddl)
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            }
            assert tables == _EXPECTED_TABLES
        finally:
            conn.close()

    def test_audit_trail_hash_chain_columns(self):
        conn = sqlite3.connect(":memory:")
        try:
            for ddl in ALL_TABLES:
                conn.execute(ddl)
            cols = _sqlite_columns(conn, "audit_trail")
            assert {"stage", "event_type", "payload_json", "prev_hash", "record_hash"} <= cols
            assert "read_only_after" in cols  # 30 天 read-only 触发器口径位
        finally:
            conn.close()

    def test_report_archive_aligns_publisher_hash_chain(self):
        conn = sqlite3.connect(":memory:")
        try:
            for ddl in ALL_TABLES:
                conn.execute(ddl)
            cols = _sqlite_columns(conn, "report_archive")
            # 与 ReportPublisher ArchivedReport 字段对齐
            assert {
                "archive_id",
                "report_id",
                "source",
                "report_type",
                "content_hash",
                "prev_hash",
                "record_hash",
            } <= cols
        finally:
            conn.close()

    def test_attribution_results_two_layer_columns(self):
        conn = sqlite3.connect(":memory:")
        try:
            for ddl in ALL_TABLES:
                conn.execute(ddl)
            cols = _sqlite_columns(conn, "attribution_results")
            # 两层归因（strategy/firm）+ Brinson 3 因子 + 求和不变量 + 幂等键
            assert {"layer", "portfolio_id", "allocation_effect", "selection_effect",
                    "interaction_effect", "invariant_status", "idempotency_key"} <= cols
        finally:
            conn.close()

    def test_reconciliation_differences_drift_columns(self):
        conn = sqlite3.connect(":memory:")
        try:
            for ddl in ALL_TABLES:
                conn.execute(ddl)
            cols = _sqlite_columns(conn, "reconciliation_differences")
            assert {"recon_layer", "drift_type", "system_value", "broker_value", "diff"} <= cols
        finally:
            conn.close()
