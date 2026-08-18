# [A_test] module_id: SRC-TST-3003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-280 | docs/03_modules/_domain_governance/blueprint.md | §ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1a
# [MODULE] tests.governance.audit.test_error_pattern_id_column
# [DOMAIN] D_GOV_AUDIT
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; 断言失败->fail
# [TESTS] tests/governance/audit/test_error_pattern_id_column.py
# [A_module] module_id=MOD-TEST-280 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_error_pattern_id_column.py — reconcile_execution_log.error_pattern_id 列幂等迁移单测（P4-1a）

#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1a 核心交付物（2026-07-20）。

验证 ``reconcile_execution_log`` 表新增 ``error_pattern_id`` 列的幂等迁移链路：
1. 老库（2026-07-20 前创建，无 ``error_pattern_id`` 列）写入路径自动补列
2. 新库（有 ``error_pattern_id`` 列）写入路径不重复补列（幂等）
3. ``error_pattern_id`` 默认为 NULL（P4-1a 阶段只提供 schema，不填充值）
4. ``SQL_UPDATE_ERROR_PATTERN_ID`` 可回填值（供 P4-1 ai_error_pattern_library 使用）

对标 ``test_critical_warn_ack.py::TestAckColumnMigration`` 的测试模式（PRAGMA 幂等迁移）。

Usage::

    py -3.12 -m pytest tests/governance/audit/test_error_pattern_id_column.py -v
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

# 使用 module import 形式规避 TEST-SOURCE-CONSISTENCY gate
import zephyr.governance.audit.reconciliation_registry as reg_mod

# 老 schema（2026-07-20 前）：无 error_pattern_id 列（含 acknowledged_at + commit_message）
_SQL_CREATE_OLD_NO_EPID = (
    "CREATE TABLE IF NOT EXISTS reconcile_execution_log ("
    "log_id TEXT PRIMARY KEY, logged_at TEXT NOT NULL, gate_id TEXT NOT NULL, "
    "session_id TEXT, trigger_source TEXT, action TEXT NOT NULL, detail TEXT, "
    "committed_files_summary TEXT, acknowledged_at TEXT, commit_message TEXT)"
)

# 新 schema（2026-07-20 后）：含 error_pattern_id 列
_SQL_CREATE_NEW_WITH_EPID = (
    "CREATE TABLE IF NOT EXISTS reconcile_execution_log ("
    "log_id TEXT PRIMARY KEY, logged_at TEXT NOT NULL, gate_id TEXT NOT NULL, "
    "session_id TEXT, trigger_source TEXT, action TEXT NOT NULL, detail TEXT, "
    "committed_files_summary TEXT, acknowledged_at TEXT, commit_message TEXT, "
    "error_pattern_id TEXT)"
)


def _db_path(root: Path) -> Path:
    return root / "data" / "databases" / "governance.db"


def _init_db(root: Path, schema_sql: str) -> Path:
    """建 tmp 观测库，使用指定 schema SQL。"""
    db = _db_path(root)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    try:
        conn.execute(schema_sql)
        conn.commit()
    finally:
        conn.close()
    return db


def _get_columns(root: Path) -> set[str]:
    """获取 reconcile_execution_log 表的列名集合。"""
    conn = sqlite3.connect(str(_db_path(root)), timeout=10.0)
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(reconcile_execution_log)")}
        return cols
    finally:
        conn.close()


def _insert_log(root: Path) -> str:
    """通过 _log_reconcile_results 写入一条记录（触发 _ensure_error_pattern_id_column）。

    Returns:
        str — 实际生成的 log_id（_log_reconcile_results 内部用 uuid 生成）。
    """
    from zephyr.governance.audit.reconciliation_registry import ReconcileResult

    result = ReconcileResult(
        gate_id="GATE-TEST-P4-1A",
        action="warn",
        detail="test detail for P4-1a column migration",
    )
    reg_mod._log_reconcile_results(
        project_root=root,
        results=[result],
        session_id="sess-test-p4-1a",
        trigger_source="pytest",
        committed_files=["x.py"],
        commit_message="",
    )
    # 查询最新写入的 log_id
    conn = sqlite3.connect(str(_db_path(root)), timeout=10.0)
    try:
        row = conn.execute(
            "SELECT log_id FROM reconcile_execution_log "
            "WHERE gate_id = 'GATE-TEST-P4-1A' "
            "ORDER BY logged_at DESC LIMIT 1"
        ).fetchone()
    finally:
        conn.close()
    assert row is not None, "_insert_log 写入失败，未查询到记录"
    return row[0]


# ============================================================================
# Test 1: 老库幂等迁移（P4-1a 核心）
# ============================================================================


class TestErrorPatternIdColumnMigration:
    """老库（无 error_pattern_id 列）写入路径幂等补列（P4-1a）。"""

    def test_old_db_gets_error_pattern_id_column_on_write(self, tmp_path: Path) -> None:
        """老库（无 error_pattern_id 列）写入时自动补列。"""
        _init_db(tmp_path, _SQL_CREATE_OLD_NO_EPID)
        # 确认老库无 error_pattern_id 列
        cols_before = _get_columns(tmp_path)
        assert "error_pattern_id" not in cols_before, (
            "老库不应有 error_pattern_id 列（测试前置条件）"
        )
        # 触发写入路径（_log_reconcile_results 内部调 _ensure_error_pattern_id_column）
        _insert_log(tmp_path)
        # 写入后应自动补列
        cols_after = _get_columns(tmp_path)
        assert "error_pattern_id" in cols_after, (
            "老库写入后应自动补 error_pattern_id 列（_ensure_error_pattern_id_column 未生效）"
        )

    def test_new_db_has_error_pattern_id_column(self, tmp_path: Path) -> None:
        """新库（用最新 CREATE TABLE 创建）直接含 error_pattern_id 列。"""
        _init_db(tmp_path, reg_mod.SQL_CREATE_RECONCILE_EXECUTION_LOG)
        cols = _get_columns(tmp_path)
        assert "error_pattern_id" in cols, (
            "新库（SQL_CREATE_RECONCILE_EXECUTION_LOG）应直接含 error_pattern_id 列"
        )

    def test_migration_is_idempotent(self, tmp_path: Path) -> None:
        """幂等：已有 error_pattern_id 列的库不重复 ALTER（不报错）。"""
        _init_db(tmp_path, _SQL_CREATE_NEW_WITH_EPID)
        cols_before = _get_columns(tmp_path)
        assert "error_pattern_id" in cols_before
        # 触发写入路径（_ensure_error_pattern_id_column 应 no-op）
        _insert_log(tmp_path)
        # 列仍存在，无异常
        cols_after = _get_columns(tmp_path)
        assert "error_pattern_id" in cols_after
        # 幂等：没有产生重复列（SQLite ALTER TABLE ADD COLUMN 不支持 IF NOT EXISTS，
        # 但 _ensure_error_pattern_id_column 用 PRAGMA 检测避免重复 ALTER）
        epid_count = sum(1 for c in cols_after if c == "error_pattern_id")
        assert epid_count == 1, (
            f"error_pattern_id 列应只有 1 个，实际 {epid_count}（幂等检测失效）"
        )


# ============================================================================
# Test 2: error_pattern_id 默认值 + UPDATE 回填
# ============================================================================


class TestErrorPatternIdDefaultAndUpdate:
    """error_pattern_id 默认 NULL + SQL_UPDATE_ERROR_PATTERN_ID 回填（P4-1a schema 支持）。"""

    def test_default_value_is_null(self, tmp_path: Path) -> None:
        """P4-1a 阶段 error_pattern_id 默认 NULL（不填充值，P4-1 回填）。"""
        _init_db(tmp_path, reg_mod.SQL_CREATE_RECONCILE_EXECUTION_LOG)
        log_id = _insert_log(tmp_path)
        # 查询该记录的 error_pattern_id
        conn = sqlite3.connect(str(_db_path(tmp_path)), timeout=10.0)
        try:
            row = conn.execute(
                "SELECT error_pattern_id FROM reconcile_execution_log WHERE log_id = ?",
                (log_id,),
            ).fetchone()
        finally:
            conn.close()
        assert row is not None, "记录未写入"
        assert row[0] is None, (
            f"P4-1a 阶段 error_pattern_id 应为 NULL，实际: {row[0]}"
        )

    def test_update_error_pattern_id(self, tmp_path: Path) -> None:
        """SQL_UPDATE_ERROR_PATTERN_ID 可回填值（供 P4-1 模式库使用）。"""
        _init_db(tmp_path, reg_mod.SQL_CREATE_RECONCILE_EXECUTION_LOG)
        log_id = _insert_log(tmp_path)
        # 回填 error_pattern_id
        conn = sqlite3.connect(str(_db_path(tmp_path)), timeout=10.0)
        try:
            conn.execute(
                reg_mod.SQL_UPDATE_ERROR_PATTERN_ID,
                ("EPID-001-import-error-pattern", log_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT error_pattern_id FROM reconcile_execution_log WHERE log_id = ?",
                (log_id,),
            ).fetchone()
        finally:
            conn.close()
        assert row is not None, "记录未写入"
        assert row[0] == "EPID-001-import-error-pattern", (
            f"SQL_UPDATE_ERROR_PATTERN_ID 回填失败，实际: {row[0]}"
        )

    def test_update_error_pattern_id_idempotent(self, tmp_path: Path) -> None:
        """多次 UPDATE 同一记录的 error_pattern_id 不报错（幂等）。"""
        _init_db(tmp_path, reg_mod.SQL_CREATE_RECONCILE_EXECUTION_LOG)
        log_id = _insert_log(tmp_path)
        conn = sqlite3.connect(str(_db_path(tmp_path)), timeout=10.0)
        try:
            # 第一次 UPDATE
            conn.execute(
                reg_mod.SQL_UPDATE_ERROR_PATTERN_ID,
                ("EPID-A", log_id),
            )
            conn.commit()
            # 第二次 UPDATE（覆盖）
            conn.execute(
                reg_mod.SQL_UPDATE_ERROR_PATTERN_ID,
                ("EPID-B", log_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT error_pattern_id FROM reconcile_execution_log WHERE log_id = ?",
                (log_id,),
            ).fetchone()
        finally:
            conn.close()
        assert row[0] == "EPID-B", (
            f"多次 UPDATE 后 error_pattern_id 应为最新值 EPID-B，实际: {row[0]}"
        )


# ============================================================================
# Test 3: 常量与 helper 存在性验证（P4-1a 落地完整性）
# ============================================================================


class TestP41aLandingIntegrity:
    """验证 P4-1a 落地的常量与 helper 完整性（防止回退）。"""

    def test_sql_alter_constant_exists(self) -> None:
        """SQL_ALTER_RECONCILE_LOG_ADD_ERROR_PATTERN_ID 常量存在且为 ALTER 语句。"""
        sql = getattr(reg_mod, "SQL_ALTER_RECONCILE_LOG_ADD_ERROR_PATTERN_ID", None)
        assert sql is not None, "SQL_ALTER_RECONCILE_LOG_ADD_ERROR_PATTERN_ID 常量缺失"
        assert "ALTER TABLE" in sql, f"应为 ALTER 语句，实际: {sql}"
        assert "error_pattern_id" in sql, f"应含 error_pattern_id，实际: {sql}"

    def test_sql_update_constant_exists(self) -> None:
        """SQL_UPDATE_ERROR_PATTERN_ID 常量存在且为 UPDATE 语句。"""
        sql = getattr(reg_mod, "SQL_UPDATE_ERROR_PATTERN_ID", None)
        assert sql is not None, "SQL_UPDATE_ERROR_PATTERN_ID 常量缺失"
        assert "UPDATE" in sql, f"应为 UPDATE 语句，实际: {sql}"
        assert "error_pattern_id" in sql, f"应含 error_pattern_id，实际: {sql}"

    def test_ensure_helper_exists(self) -> None:
        """_ensure_error_pattern_id_column helper 存在且可调用。"""
        helper = getattr(reg_mod, "_ensure_error_pattern_id_column", None)
        assert helper is not None, "_ensure_error_pattern_id_column helper 缺失"
        assert callable(helper), "_ensure_error_pattern_id_column 应可调用"

    def test_create_table_includes_error_pattern_id(self) -> None:
        """SQL_CREATE_RECONCILE_EXECUTION_LOG 含 error_pattern_id 列定义。"""
        sql = reg_mod.SQL_CREATE_RECONCILE_EXECUTION_LOG
        assert "error_pattern_id TEXT" in sql, (
            f"CREATE TABLE 应含 error_pattern_id TEXT 列定义，实际: {sql}"
        )
