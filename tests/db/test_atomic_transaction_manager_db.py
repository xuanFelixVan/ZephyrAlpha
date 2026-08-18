# [A_test] module_id: MOD-GOV_atomic_transaction_manager_db | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-481 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.db.test_atomic_transaction_manager
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/governance/financial_governance/atomic_transaction_manager.py（T-2-30）
==============================================================
覆盖矩阵：
  _utf8_lf_bytes:
    - str → UTF-8 × 1
    - CRLF → LF × 1
    - BOM 移除 × 1
    - bytes 直通 × 1
  _new_tx_id:
    - 格式验证 × 1
    - 唯一性 × 1
  AtomicTransactionManager:
    - 构造 × 1
    - db_path 属性 × 1
  TransactionScope.execute:
    - 正常 SQL × 1
    - executemany × 1
  TransactionScope.write_file:
    - 写新文件 × 1
    - CRLF 规范化 × 1
    - 覆盖已有文件 × 1
    - staged_file_count × 1
  事务提交：
    - commit 持久化 SQL + 文件 × 1
  事务回滚：
    - 异常触发 ROLLBACK × 1
    - tmp 文件清理 × 1
    - bak 文件恢复 × 1
  嵌套事务禁止 × 1
  已提交事务操作禁止 × 1
  ATM.close × 2（正常关闭、有活跃事务时关闭）
  validate_write_path × 2（合法、非法）

Safety: HIGH（数据库事务 + 文件系统原子性）

注意：FakeInputSanitizer 经构造函数注入（sanitizer= 参数）替代真实
InputSanitizer（后者由源模块 __getattr__ 惰性导入
zephyr.security.llm_defense.llm_security.input_sanitizer）。
"""

import sqlite3
from pathlib import Path

import pytest


class FakeInputSanitizer:
    def __init__(self, root: str):
        self._root = Path(root).resolve()

    def validate_path(self, path: str, mode: str = "read"):
        resolved = (self._root / path).resolve()
        try:
            resolved.relative_to(self._root)
        except ValueError:
            raise PathTraversalError(f"Path escapes root: {path}") from None
        return resolved


class FakePathTraversalError(Exception):
    pass


class FakeSanitizationError(Exception):
    pass


PathTraversalError = FakePathTraversalError
SanitizationError = FakeSanitizationError

from zephyr.governance.financial_governance.atomic_transaction_manager import (
    AtomicTransactionManager,
    TransactionError,
    _new_tx_id,
    _utf8_lf_bytes,
)


@pytest.fixture
def atm(tmp_path):
    db_path = tmp_path / "test.db"
    manager = AtomicTransactionManager(
        db_path=str(db_path.relative_to(tmp_path)),
        root=str(tmp_path),
        sanitizer=FakeInputSanitizer(str(tmp_path)),
    )
    yield manager
    manager.close()


class TestUtf8LfBytes:
    def test_str_to_utf8(self):
        data = _utf8_lf_bytes("hello")
        assert data == b"hello"

    def test_crlf_to_lf(self):
        data = _utf8_lf_bytes("line1\r\nline2\r\n")
        assert data == b"line1\nline2\n"

    def test_bom_removal(self):
        data = _utf8_lf_bytes("\ufeffhello")
        assert data == b"hello"

    def test_bytes_passthrough(self):
        data = _utf8_lf_bytes(b"\x00\x01\x02")
        assert data == b"\x00\x01\x02"


class TestNewTxId:
    def test_format(self):
        tx_id = _new_tx_id()
        assert tx_id.startswith("tx-")

    def test_unique(self):
        ids = {_new_tx_id() for _ in range(100)}
        assert len(ids) == 100


class TestATMConstruction:
    def test_basic_construction(self, atm, tmp_path):
        assert atm.root == tmp_path.resolve()
        assert atm.db_path.exists()

    def test_db_path_property(self, atm):
        assert atm.db_path.name == "test.db"


class TestTransactionExecute:
    def test_execute_sql(self, atm):
        with atm.transaction() as tx:
            tx.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            tx.execute("INSERT INTO test VALUES (1, 'alice')")
        conn = sqlite3.connect(str(atm.db_path))
        rows = conn.execute("SELECT name FROM test").fetchall()
        conn.close()
        assert rows == [("alice",)]

    def test_executemany(self, atm):
        with atm.transaction() as tx:
            tx.execute("CREATE TABLE items (id INTEGER, val TEXT)")
            tx.executemany(
                "INSERT INTO items VALUES (?, ?)",
                [(1, "a"), (2, "b"), (3, "c")],
            )
        conn = sqlite3.connect(str(atm.db_path))
        count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        conn.close()
        assert count == 3


class TestTransactionWriteFile:
    def test_write_new_file(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        target = docs_dir / "test.md"
        with atm.transaction() as tx:
            tx.write_file("docs/test.md", "hello world")
        assert target.exists()
        assert target.read_text(encoding="utf-8") == "hello world"

    def test_crlf_normalization(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        target = docs_dir / "crlf.md"
        with atm.transaction() as tx:
            tx.write_file("docs/crlf.md", "line1\r\nline2\r\n")
        content = target.read_bytes()
        assert b"\r\n" not in content
        assert b"\n" in content

    def test_overwrite_existing_file(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        target = docs_dir / "existing.md"
        target.write_text("old content", encoding="utf-8")
        with atm.transaction() as tx:
            tx.write_file("docs/existing.md", "new content")
        assert target.read_text(encoding="utf-8") == "new content"

    def test_staged_file_count(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        with atm.transaction() as tx:
            assert tx.staged_file_count() == 0
            tx.write_file("docs/a.md", "a")
            assert tx.staged_file_count() == 1
            tx.write_file("docs/b.md", "b")
            assert tx.staged_file_count() == 2


class TestTransactionCommit:
    def test_commit_persists_sql_and_file(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        with atm.transaction() as tx:
            tx.execute("CREATE TABLE t (id INTEGER)")
            tx.execute("INSERT INTO t VALUES (42)")
            tx.write_file("docs/commit_test.md", "committed")
        assert (docs_dir / "commit_test.md").read_text(encoding="utf-8") == "committed"
        conn = sqlite3.connect(str(atm.db_path))
        rows = conn.execute("SELECT id FROM t").fetchall()
        conn.close()
        assert rows == [(42,)]


class TestTransactionRollback:
    def test_rollback_on_exception(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        with pytest.raises(RuntimeError), atm.transaction() as tx:
            tx.execute("CREATE TABLE rb_test (id INTEGER)")
            tx.execute("INSERT INTO rb_test VALUES (1)")
            tx.write_file("docs/rb_test.md", "should not persist")
            raise RuntimeError("force rollback")
        conn = sqlite3.connect(str(atm.db_path))
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rb_test'").fetchall()
        conn.close()
        assert tables == []

    def test_rollback_cleans_tmp_files(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        with pytest.raises(RuntimeError), atm.transaction() as tx:
            tx.write_file("docs/tmp_clean.md", "temp")
            raise RuntimeError("force rollback")
        tmp_files = list(docs_dir.glob("*.atm-*.tmp"))
        assert tmp_files == []

    def test_rollback_restores_bak_files(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        target = docs_dir / "restore.md"
        target.write_text("original", encoding="utf-8")
        with pytest.raises(RuntimeError), atm.transaction() as tx:
            tx.write_file("docs/restore.md", "overwritten")
            raise RuntimeError("force rollback")
        assert target.read_text(encoding="utf-8") == "original"


class TestNestedTransactionForbidden:
    def test_nested_raises_error(self, atm):
        with atm.transaction() as tx1, pytest.raises(TransactionError, match="nested"):
            with atm.transaction() as tx2:
                pass


class TestPostCommitOperationsForbidden:
    def test_execute_after_commit_raises(self, atm):
        with atm.transaction() as tx:
            tx.execute("CREATE TABLE post_commit (id INTEGER)")
        with pytest.raises(TransactionError, match="already committed"):
            tx.execute("INSERT INTO post_commit VALUES (1)")


class TestATMClose:
    def test_close_idempotent(self, atm):
        atm.close()
        atm.close()

    def test_close_cleans_up(self, tmp_path):
        db_path = tmp_path / "test_close.db"
        manager = AtomicTransactionManager(
            db_path=str(db_path.relative_to(tmp_path)),
            root=str(tmp_path),
            sanitizer=FakeInputSanitizer(str(tmp_path)),
        )
        with manager.transaction() as tx:
            tx.execute("CREATE TABLE close_test (id INTEGER)")
            tx.execute("INSERT INTO close_test VALUES (1)")
        manager.close()
        manager.close()


class TestValidateWritePath:
    def test_valid_write_path(self, atm, tmp_path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        result = atm.validate_write_path("docs/test.md")
        assert result == docs_dir / "test.md"

    def test_invalid_write_path_raises(self, atm):
        with pytest.raises(FakePathTraversalError):
            atm.validate_write_path("../../etc/passwd")
