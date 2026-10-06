# [TTL] permanent
"""successor_of DDL 迁移脚本测试（S5 增枝①）：幂等 DDL 文本 + dry-run 零副作用。

零 DB 依赖：fake conn 记录 execute/commit/rollback 调用。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from scripts.governance.migrations import add_library_successor_of as mig


def test_ddl_is_idempotent_add_column() -> None:
    """加列语句必须 IF NOT EXISTS（重跑零副作用，对标 add_acquisition_fields 承诺）。"""
    assert "ADD COLUMN IF NOT EXISTS successor_of" in mig._SQL_DDL_ADD_SUCCESSOR_OF
    assert "TEXT NULL" in mig._SQL_DDL_ADD_SUCCESSOR_OF


def test_ddl_comment_carries_two_state_discipline() -> None:
    """列注释=两态纪律真源（NULL=未评估/''=无后继）挂列上。"""
    assert "COMMENT ON COLUMN lib_assets.successor_of" in mig._SQL_DDL_COMMENT_ON_COLUMN
    assert "NULL=未评估" in mig._SQL_DDL_COMMENT_ON_COLUMN
    assert "确认无后继" in mig._SQL_DDL_COMMENT_ON_COLUMN


def test_module_docstring_documents_rollback() -> None:
    """回滚说明必须落模块文档（DROP COLUMN 语句可检索）。"""
    assert "DROP COLUMN IF EXISTS successor_of" in (mig.__doc__ or "")


class _MigCur:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def __enter__(self) -> _MigCur:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def execute(self, sql: str, *args: object) -> None:
        self.executed.append(sql)

    def fetchall(self) -> list[tuple[str, ...]]:
        return [("successor_of",)]


class _MigConn:
    def __init__(self) -> None:
        self.cur = _MigCur()
        self.committed = False
        self.rolled_back = False

    def cursor(self) -> _MigCur:
        return self.cur

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        pass


def _run(monkeypatch: pytest.MonkeyPatch, dry_run: bool) -> tuple[int, _MigConn]:
    conn = _MigConn()
    monkeypatch.setattr(mig, "get_depgraph_pg_connection", lambda *a, **k: conn)  # type: ignore[arg-type,return-value]
    code: Any = mig.migrate(dry_run=dry_run)
    return code, conn


def test_dry_run_executes_ddl_but_rolls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    """dry-run：DDL 全执行、验证通过、回滚零持久副作用、退出 0。"""
    code, conn = _run(monkeypatch, dry_run=True)
    assert code == 0
    assert any("ADD COLUMN IF NOT EXISTS successor_of" in s for s in conn.cur.executed)
    assert any("COMMENT ON COLUMN" in s for s in conn.cur.executed)
    assert conn.rolled_back is True
    assert conn.committed is False


def test_real_run_commits(monkeypatch: pytest.MonkeyPatch) -> None:
    """正式执行：提交且退出 0。"""
    code, conn = _run(monkeypatch, dry_run=False)
    assert code == 0
    assert conn.committed is True
    assert conn.rolled_back is False


def test_verify_failure_returns_findings(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证列缺失：退出 1（EXIT_FINDINGS）。"""
    conn = _MigConn()
    monkeypatch.setattr(mig, "get_depgraph_pg_connection", lambda *a, **k: conn)  # type: ignore[arg-type,return-value]
    monkeypatch.setattr(conn.cur, "fetchall", lambda: [], raising=True)
    assert mig.migrate(dry_run=False) == 1
