# [MODULE] tests.governance.test_merge_domain_fk_scan_guard
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/test_merge_domain_fk_scan_guard.py
# [TTL] permanent
"""test_merge_domain_fk_scan_guard.py — W7 R8 红蓝对抗回归（2026-09-18）。

病根：--merge-domain 的 B1 全表 TEXT 列兜底做子串 REPLACE，会命中引用 domains 的
FK 列中的复合历史值（如 domain_events.source_domain='D_DATA_ENG'），替换成
'D_MKT_DATA_ENG' 后 domains 中无此域 → 提交时 FK 违例，整笔 merge 中途崩
（事务回滚保住了数据，但 merge 功能对"有同名前缀子域值"的域必死）。

治本：兜底扫描动态排除 domains-FK 引用列（pg_constraint 现查，勿手工清单），
这些列由 step2-17 专职精确迁移。本测试用脚本化假 cursor 证明：FK 列不再被
子串 REPLACE 触碰、非 FK 描述列照常兜底（撤销修复必红）。
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "governance" / "apply_depgraph.py"


def _load_adg():
    spec = importlib.util.spec_from_file_location("adg_fk_scan_guard", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


adg = _load_adg()


class _FakeCursor:
    """按 SQL 文本分发的脚本化 cursor；记录全部 UPDATE 调用。"""

    def __init__(self, fk_rows, tables, columns_by_table, like_counts):
        self._fk_rows = fk_rows
        self._tables = tables
        self._columns = columns_by_table
        self._like_counts = like_counts
        self._pending = None
        self.updates: list[tuple[str, str, str, str]] = []

    def execute(self, sql, params=None):
        if sql is adg.SQL_DOMAINS_FK_COLUMNS or "pg_constraint" in sql:
            self._pending = ("rows", self._fk_rows)
        elif "information_schema.tables" in sql:
            self._pending = ("rows", self._tables)
        elif "information_schema.columns" in sql:
            self._pending = ("rows", self._columns[params[0]])
        elif sql.startswith("SELECT COUNT"):
            self._pending = ("one", {"cnt": self._like_counts.get(params[-1].strip("%"), 0)})
        elif sql.startswith("UPDATE"):
            tbl = sql.split("UPDATE ")[1].split(" ")[0]
            col = sql.split("SET ")[1].split("=")[0]
            self.updates.append((tbl, col, params[0], params[1]))
            self._pending = ("one", None)
        else:
            self._pending = ("rows", [])
        return self

    def fetchall(self):
        kind, data = self._pending
        return data if kind == "rows" else []

    def fetchone(self):
        kind, data = self._pending
        return data if kind == "one" else None


def _run_scan(cursor, *, old="D_DATA", new="D_MKT_DATA"):
    total = adg._scan_replace_all_text_columns(
        cursor, old, new, dry_run=False, mode="[TEST]"
    )
    return total


def _basic_fixture():
    tables = [{"name": "domain_events"}, {"name": "nodes"}]
    columns = {
        "domain_events": [
            {"column_name": "source_domain", "data_type": "text"},
            {"column_name": "description", "data_type": "text"},
        ],
        "nodes": [
            {"column_name": "tags", "data_type": "character varying"},
        ],
    }
    counts = {"D\\_DATA": 5}
    return tables, columns, counts


class TestFkColumnScanGuard:
    def test_fk_column_not_substring_replaced(self):
        """domain_events.source_domain 在 FK 清单中 → 兜底子串 REPLACE 必须跳过它。"""
        tables, columns, counts = _basic_fixture()
        cur = _FakeCursor(
            fk_rows=[{"table_name": "domain_events", "column_name": "source_domain"}],
            tables=tables,
            columns_by_table=columns,
            like_counts=counts,
        )
        _run_scan(cur)
        touched = {(t, c) for t, c, _, _ in cur.updates}
        assert ("domain_events", "source_domain") not in touched

    def test_non_fk_text_columns_still_scanned(self):
        """描述型非 FK 列（description/tags）兜底替换不变——防修复过度致盲。"""
        tables, columns, counts = _basic_fixture()
        cur = _FakeCursor(
            fk_rows=[{"table_name": "domain_events", "column_name": "source_domain"}],
            tables=tables,
            columns_by_table=columns,
            like_counts=counts,
        )
        total = _run_scan(cur)
        touched = {(t, c) for t, c, _, _ in cur.updates}
        assert ("domain_events", "description") in touched
        assert ("nodes", "tags") in touched
        assert total == 10  # description 5 + tags 5（source_domain 的 5 行被护栏挡住）

    def test_fk_query_targets_domains_constraint(self):
        """FK 排除清单来源=pg_constraint 现查且锚定 domains——防误写成静态清单。"""
        sql = adg.SQL_DOMAINS_FK_COLUMNS
        assert "pg_constraint" in sql
        assert "'domains'::regclass" in sql
        assert "contype = 'f'" in sql
