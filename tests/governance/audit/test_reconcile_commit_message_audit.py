# [A_test] module_id: MOD-GOV_RECONCILE_COMMIT_MESSAGE_AUDIT_TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RECONCILIATION_REGISTRY | docs/03_modules/_domain_governance/blueprint.md | §P3.4
# [MODULE] tests.governance.audit.test_reconcile_commit_message_audit
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_RECONCILIATION_REGISTRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_reconcile_commit_message_audit.py — Phase 3.4 commit_message 审计链 e2e smoke test

#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S6 Phase 3.4 治本断点4-7：
验证 commit_message 从 commit() → _run_post_commit_reconcile() → reconcile_for()
→ spec.reconcile() → _log_reconcile_results() → reconcile_execution_log DB 全链路贯通。

测试组：
- TestReconcileForAcceptsCommitMessage: reconcile_for 接收 commit_message 参数
- TestThreeArgReconcilerReceivesCommitMessage: 3-arg reconciler 收到 commit_message
- TestTwoArgReconcilerBackwardCompat: 2-arg reconciler 向后兼容不收 commit_message
- TestLogReconcileResultsStoresCommitMessage: _log_reconcile_results 持久化 commit_message 到 DB
- TestEnsureCommitMessageColumn: 老库幂等迁移 _ensure_commit_message_column

测试隔离：使用 tmp_path + monkeypatch，不污染真实 governance.db。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


# ---------------------------------------------------------------------------
# TestReconcileForAcceptsCommitMessage
# ---------------------------------------------------------------------------


class TestReconcileForAcceptsCommitMessage:
    """reconcile_for 接收 commit_message 参数（断点5 治本）。"""

    def test_reconcile_for_accepts_commit_message_kwarg(self):
        """reconcile_for(commit_message='...') 不抛异常。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        registry = ReconciliationRegistry()

        def _trigger(files):
            return True

        def _reconcile(files, sid):
            return ReconcileResult(action="clean", detail="ok")

        registry.register(
            ReconcilerSpec(
                gate_id="TEST-MSG-001",
                trigger=_trigger,
                reconcile=_reconcile,
                priority=100,
                file_ops=frozenset({"none"}),
            )
        )
        # 不抛异常 = 签名兼容
        results = registry.reconcile_for(["test.py"], "sess-001", commit_message="test message")
        assert len(results) == 1
        assert results[0].action == "clean"

    def test_reconcile_for_default_empty_commit_message(self):
        """reconcile_for 不传 commit_message 时默认空字符串（向后兼容）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        registry = ReconciliationRegistry()

        def _trigger(files):
            return True

        def _reconcile(files, sid):
            return ReconcileResult(action="clean")

        registry.register(
            ReconcilerSpec(
                gate_id="TEST-MSG-002",
                trigger=_trigger,
                reconcile=_reconcile,
                file_ops=frozenset({"none"}),
            )
        )
        # 不传 commit_message = 向后兼容
        results = registry.reconcile_for(["test.py"], "sess-002")
        assert len(results) == 1


# ---------------------------------------------------------------------------
# TestThreeArgReconcilerReceivesCommitMessage
# ---------------------------------------------------------------------------


class TestThreeArgReconcilerReceivesCommitMessage:
    """3-arg reconciler 收到 commit_message（断点6 治本）。"""

    def test_three_arg_reconciler_receives_commit_message(self):
        """reconcile(files, sid, commit_message) 签名的 reconciler 收到 commit_message。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        registry = ReconciliationRegistry()
        received_messages: list[str] = []

        def _trigger(files):
            return True

        def _reconcile(files, sid, commit_message=""):
            received_messages.append(commit_message)
            return ReconcileResult(action="clean", detail=f"msg={commit_message}")

        registry.register(
            ReconcilerSpec(
                gate_id="TEST-MSG-003",
                trigger=_trigger,
                reconcile=_reconcile,
                file_ops=frozenset({"none"}),
            )
        )
        test_msg = "[no-lookup:dogfooding capability lookup mechanism]"
        results = registry.reconcile_for(["test.py"], "sess-003", commit_message=test_msg)
        assert len(results) == 1
        assert results[0].detail == f"msg={test_msg}"
        assert received_messages == [test_msg], f"3-arg reconciler 应收到 commit_message: {received_messages}"

    def test_three_arg_reconciler_with_bypass_marker(self):
        """3-arg reconciler 能检测 [no-lookup:reason] 标记。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        registry = ReconciliationRegistry()

        def _trigger(files):
            return True

        def _reconcile(files, sid, commit_message=""):
            # 模拟审计 reconciler 检测 bypass marker
            if "[no-lookup:" in commit_message:
                reason_start = commit_message.index("[no-lookup:") + len("[no-lookup:")
                reason_end = commit_message.index("]", reason_start)
                reason = commit_message[reason_start:reason_end]
                return ReconcileResult(action="clean", detail=f"bypass reason: {reason}")
            return ReconcileResult(action="warn", detail="no bypass marker")

        registry.register(
            ReconcilerSpec(
                gate_id="TEST-MSG-004",
                trigger=_trigger,
                reconcile=_reconcile,
                file_ops=frozenset({"none"}),
            )
        )
        results = registry.reconcile_for(
            ["test.py"],
            "sess-004",
            commit_message="fix: emergency hotfix [no-lookup:emergency]",
        )
        assert results[0].action == "clean"
        assert "emergency" in results[0].detail


# ---------------------------------------------------------------------------
# TestTwoArgReconcilerBackwardCompat
# ---------------------------------------------------------------------------


class TestTwoArgReconcilerBackwardCompat:
    """2-arg reconciler 向后兼容不收 commit_message。"""

    def test_two_arg_reconciler_still_works(self):
        """2-arg reconcile(files, sid) 签名的 reconciler 不受 commit_message 影响。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        registry = ReconciliationRegistry()

        def _trigger(files):
            return True

        def _reconcile(files, sid):
            # 2-arg 签名，不接收 commit_message
            return ReconcileResult(action="clean", detail="2-arg ok")

        registry.register(
            ReconcilerSpec(
                gate_id="TEST-MSG-005",
                trigger=_trigger,
                reconcile=_reconcile,
                file_ops=frozenset({"none"}),
            )
        )
        # 传 commit_message 但 reconciler 是 2-arg，应向后兼容
        results = registry.reconcile_for(
            ["test.py"],
            "sess-005",
            commit_message="this should not reach 2-arg reconciler",
        )
        assert len(results) == 1
        assert results[0].detail == "2-arg ok"


# ---------------------------------------------------------------------------
# TestLogReconcileResultsStoresCommitMessage
# ---------------------------------------------------------------------------


class TestLogReconcileResultsStoresCommitMessage:
    """_log_reconcile_results 持久化 commit_message 到 DB（断点7 治本）。"""

    def test_log_stores_commit_message_in_db(self, tmp_path: Path):
        """_log_reconcile_results 将 commit_message 写入 reconcile_execution_log 表。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )

        # 准备 governance.db 路径
        db_dir = tmp_path / "data" / "databases"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "governance.db"

        results = [ReconcileResult(action="clean", detail="test", gate_id="TEST-LOG-001")]
        test_msg = "feat: test commit [no-lookup:dogfooding]"

        _log_reconcile_results(
            tmp_path,
            results,
            "sess-log-001",
            trigger_source="post_commit",
            committed_files=["src/test.py"],
            commit_message=test_msg,
        )

        # 验证 DB 中有 commit_message
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT commit_message FROM reconcile_execution_log WHERE gate_id='TEST-LOG-001'"
            ).fetchone()
            assert row is not None, "应有日志记录"
            assert row[0] == test_msg, f"commit_message 应持久化: {row[0]}"
        finally:
            conn.close()

    def test_log_default_empty_commit_message(self, tmp_path: Path):
        """不传 commit_message 时 DB 中存储空字符串。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )

        db_dir = tmp_path / "data" / "databases"
        db_dir.mkdir(parents=True, exist_ok=True)

        results = [ReconcileResult(action="warn", detail="test", gate_id="TEST-LOG-002")]
        # 不传 commit_message
        _log_reconcile_results(
            tmp_path,
            results,
            "sess-log-002",
            trigger_source="post_merge",
        )

        import sqlite3

        db_path = db_dir / "governance.db"
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT commit_message FROM reconcile_execution_log WHERE gate_id='TEST-LOG-002'"
            ).fetchone()
            assert row is not None
            assert row[0] == "" or row[0] is None, f"默认应为空: {row[0]!r}"
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# TestEnsureCommitMessageColumn
# ---------------------------------------------------------------------------


class TestEnsureCommitMessageColumn:
    """老库幂等迁移 _ensure_commit_message_column。"""

    def test_ensure_column_creates_if_missing(self, tmp_path: Path):
        """老库（无 commit_message 列）调用后补列。"""
        import sqlite3

        from zephyr.governance.audit.reconciliation_registry import (
            SQL_CREATE_RECONCILE_EXECUTION_LOG,
            _ensure_commit_message_column,
        )

        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        try:
            # 模拟老库：手动创建不含 commit_message 列的表
            conn.execute("""
                CREATE TABLE reconcile_execution_log (
                    log_id TEXT PRIMARY KEY,
                    logged_at TEXT NOT NULL,
                    gate_id TEXT NOT NULL,
                    session_id TEXT,
                    trigger_source TEXT NOT NULL,
                    action TEXT NOT NULL,
                    detail TEXT,
                    committed_files_summary TEXT,
                    acknowledged_at TEXT
                )
            """)
            conn.commit()
            # 验证列不存在
            cols = {r[1] for r in conn.execute("PRAGMA table_info(reconcile_execution_log)")}
            assert "commit_message" not in cols
            # 补列
            _ensure_commit_message_column(conn)
            cols = {r[1] for r in conn.execute("PRAGMA table_info(reconcile_execution_log)")}
            assert "commit_message" in cols, "补列后 commit_message 应存在"
        finally:
            conn.close()

    def test_ensure_column_idempotent(self, tmp_path: Path):
        """已有 commit_message 列时幂等（不报错）。"""
        import sqlite3

        from zephyr.governance.audit.reconciliation_registry import (
            _ensure_commit_message_column,
        )

        db_path = tmp_path / "test2.db"
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute("""
                CREATE TABLE reconcile_execution_log (
                    log_id TEXT PRIMARY KEY,
                    logged_at TEXT NOT NULL,
                    gate_id TEXT NOT NULL,
                    session_id TEXT,
                    trigger_source TEXT NOT NULL,
                    action TEXT NOT NULL,
                    detail TEXT,
                    committed_files_summary TEXT,
                    acknowledged_at TEXT,
                    commit_message TEXT
                )
            """)
            conn.commit()
            # 已有列，调用应幂等不报错
            _ensure_commit_message_column(conn)
            cols = {r[1] for r in conn.execute("PRAGMA table_info(reconcile_execution_log)")}
            assert "commit_message" in cols
        finally:
            conn.close()
