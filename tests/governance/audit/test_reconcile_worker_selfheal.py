# [BLUEPRINT] MOD-GOV_AUDIT | docs/03_modules/_domain_governance/blueprint.md | §ARCH-RECONCILER-ALERT-SELFHEAL-001
# [MODULE] tests.governance.audit.test_reconcile_worker_selfheal
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconcile_worker; zephyr.governance.audit.reconciliation_registry
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 临时 governance.db 隔离；不依赖真实 Zephyr 项目结构
# [MODIFY-GUARD] 测试函数名与 #ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1 API 对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_AUDIT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_reconcile_worker_selfheal.py — #ARCH-RECONCILER-ALERT-SELFHEAL-001 Phase 1 测试

测试覆盖：
  1. _write_boot_success_clean 写 clean 记录到 reconcile_execution_log
  2. clean 记录消解之前的 critical_warn（活跃告警查询返回 0）
  3. _write_boot_success_clean 失败不抛异常（fail-open 不阻断 worker）
  4. _run_worker 成功路径调用 _write_boot_success_clean（集成验证）
  5. 幂等：多次成功写多条 clean 记录无副作用
"""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _uninstall_inprocess_patch_after_test():
    """同进程 run_worker 会在进程入口装 in-process 删除原语补丁（T1②），
    测试进程不退出则补丁残留——拦截同进程后续测试自身清理删除
    （rule_bridge 等字母序在后目录实证被误拦）。每个测试后卸载复原。"""
    yield
    from scripts.ops_guard import uninstall_inprocess_enforcement

    uninstall_inprocess_enforcement()


@pytest.fixture
def tmp_repo_with_db(tmp_path, monkeypatch):
    """临时项目根 + governance.db（含 reconcile_execution_log 表）。"""
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    (repo / ".runtime" / "reconcile_reports").mkdir(parents=True)
    (repo / "data" / "databases").mkdir(parents=True)

    db_path = repo / "data" / "databases" / "governance.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reconcile_execution_log (
            log_id TEXT PRIMARY KEY,
            logged_at TEXT NOT NULL,
            gate_id TEXT NOT NULL,
            session_id TEXT,
            trigger_source TEXT,
            action TEXT NOT NULL,
            detail TEXT,
            committed_files_summary TEXT,
            acknowledged_at TEXT,
            commit_message TEXT,
            error_pattern_id TEXT
        )
    """)
    conn.commit()
    conn.close()

    monkeypatch.setenv("PYTHONPATH", str(repo / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""))
    return repo


def _query_records(repo: Path, gate_id: str = "RECONCILE-WORKER-BOOT") -> list[dict]:
    """查询 governance.db 中指定 gate_id 的所有记录。"""
    db_path = repo / "data" / "databases" / "governance.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT log_id, logged_at, gate_id, action, detail, acknowledged_at "
        "FROM reconcile_execution_log WHERE gate_id = ? ORDER BY logged_at",
        (gate_id,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def _insert_critical_warn(repo: Path, commit_sha: str = "old123") -> str:
    """插入一条历史 RECONCILE-WORKER-BOOT critical_warn（模拟之前的 worker boot 失败）。"""
    from datetime import datetime, timezone

    from zephyr.governance.audit.reconciliation_registry import (
        ReconcileResult,
        _log_reconcile_results,
    )
    _log_reconcile_results(
        str(repo),
        [ReconcileResult(
            action="critical_warn",
            detail=f"reconcile_worker boot failed (commit={commit_sha}): old failure",
            gate_id="RECONCILE-WORKER-BOOT",
        )],
        "sess-old",
        trigger_source="post_commit_async",
    )
    return commit_sha


# ---------------------------------------------------------------------------
# TestWriteBootSuccessClean
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.silent_failure


class TestWriteBootSuccessClean:
    """_write_boot_success_clean 单元测试。"""

    def test_writes_clean_record(self, tmp_repo_with_db):
        """成功调用后 DB 中应有一条 action=clean 的记录。"""
        from zephyr.governance.audit.reconcile_worker import _write_boot_success_clean

        _write_boot_success_clean(str(tmp_repo_with_db), "abc123", "sess-test")

        records = _query_records(tmp_repo_with_db)
        assert len(records) == 1
        assert records[0]["action"] == "clean"
        assert records[0]["gate_id"] == "RECONCILE-WORKER-BOOT"
        assert "abc123" in records[0]["detail"]
        assert "auto-selfheal" in records[0]["detail"]

    def test_clean_resolves_prior_critical_warn(self, tmp_repo_with_db):
        """历史 critical_warn 后写 clean → 活跃告警查询应返回 0。"""
        from zephyr.governance.audit.reconcile_worker import _write_boot_success_clean
        from zephyr.governance.audit.reconciliation_registry import (
            _check_recent_critical_warns,
        )

        # 1. 插入历史 critical_warn
        _insert_critical_warn(tmp_repo_with_db, "old123")
        records_before = _query_records(tmp_repo_with_db)
        assert len(records_before) == 1
        assert records_before[0]["action"] == "critical_warn"

        # 2. 写 clean（自愈）
        _write_boot_success_clean(str(tmp_repo_with_db), "new456", "sess-new")

        # 3. 活跃告警查询应返回 0（clean 记录消解了 critical_warn）
        #    注意：_check_recent_critical_warns 有 24h 窗口，需用足够近的时间戳
        active_warns = _check_recent_critical_warns(str(tmp_repo_with_db))
        assert len(active_warns) == 0, f"expected 0 active warns, got {active_warns}"

    def test_fail_open_on_db_error(self, tmp_path):
        """_write_boot_success_clean 在 DB 异常时不抛错（fail-open）。"""
        from zephyr.governance.audit.reconcile_worker import _write_boot_success_clean

        # 不存在的项目根 → _log_reconcile_results 内部会处理异常
        # _write_boot_success_clean 应捕获并不抛
        try:
            _write_boot_success_clean(str(tmp_path / "nonexistent"), "abc", "sess")
        except Exception as e:
            pytest.fail(f"_write_boot_success_clean should fail-open, but raised: {e}")

    def test_idempotent_multiple_calls(self, tmp_repo_with_db):
        """多次调用写多条 clean 记录，无副作用。"""
        from zephyr.governance.audit.reconcile_worker import _write_boot_success_clean

        _write_boot_success_clean(str(tmp_repo_with_db), "c1", "s1")
        _write_boot_success_clean(str(tmp_repo_with_db), "c2", "s2")
        _write_boot_success_clean(str(tmp_repo_with_db), "c3", "s3")

        records = _query_records(tmp_repo_with_db)
        assert len(records) == 3
        assert all(r["action"] == "clean" for r in records)

    def test_only_affects_reconcile_worker_boot_gate(self, tmp_repo_with_db):
        """clean 记录只写 RECONCILE-WORKER-BOOT gate_id，不影响其他 gate。"""
        from zephyr.governance.audit.reconcile_worker import _write_boot_success_clean
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            _log_reconcile_results,
        )

        # 插入其他 gate 的 critical_warn
        _log_reconcile_results(
            str(tmp_repo_with_db),
            [ReconcileResult(
                action="critical_warn",
                detail="other gate failure",
                gate_id="SOME-OTHER-GATE",
            )],
            "sess-x",
            trigger_source="post_commit_async",
        )

        # 写 RECONCILE-WORKER-BOOT clean
        _write_boot_success_clean(str(tmp_repo_with_db), "abc", "sess")

        # OTHER-GATE 的 critical_warn 不应被消解
        other_records = _query_records(tmp_repo_with_db, gate_id="SOME-OTHER-GATE")
        assert len(other_records) == 1
        assert other_records[0]["action"] == "critical_warn"


# ---------------------------------------------------------------------------
# TestRunWorkerSelfHealIntegration
# ---------------------------------------------------------------------------


class TestRunWorkerSelfHealIntegration:
    """_run_worker 成功路径调用 _write_boot_success_clean 集成验证。"""

    def test_run_worker_success_calls_selfheal(self, tmp_repo_with_db):
        """_run_worker 成功返回 0 后，DB 中应有 RECONCILE-WORKER-BOOT clean 记录。"""
        import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as gtw_mod
        import zephyr.governance.audit.reconcile_runner as rr_mod
        import zephyr.governance.audit.reconcile_worker as rw_mod

        payload = {
            "commit_sha": "abc123",
            "session_id": "sess-int",
            "project_root": str(tmp_repo_with_db),
            "committed_files": ["README.md"],
            "commit_message": "test",
            "started_at": time.time(),  # 证2 陈旧校验（T4 三证）：硬编码 1000 属远古负载拒启
        }

        # mock 掉 GitCommitGateway 构造 + reconcile（只验证自愈写入被调用）
        # GitCommitGateway/write_status_file 是函数内 import，patch 源模块
        with patch.object(gtw_mod, "GitCommitGateway") as mock_gw_class, \
             patch.object(rr_mod, "write_status_file") as mock_write_status:
            mock_gw = mock_gw_class.return_value
            mock_gw._run_post_commit_reconcile_sync_worker.return_value = []

            rc = rw_mod.run_worker(payload)

        assert rc == 0
        # write_status_file 被调 2 次：running（L154）+ done（L242）
        assert mock_write_status.call_count == 2
        # 验证自愈 clean 记录已写入 DB
        records = _query_records(tmp_repo_with_db)
        clean_records = [r for r in records if r["action"] == "clean"]
        assert len(clean_records) == 1
        assert "abc123" in clean_records[0]["detail"]

    def test_run_worker_failure_does_not_call_selfheal(self, tmp_repo_with_db):
        """_run_worker 失败（gateway 构造失败）不写 clean，只写 critical_warn。"""
        import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as gtw_mod
        import zephyr.governance.audit.reconcile_worker as rw_mod

        payload = {
            "commit_sha": "fail123",
            "session_id": "sess-fail",
            "project_root": str(tmp_repo_with_db),
            "committed_files": [],
            "commit_message": "",
            "started_at": time.time(),  # 证2 陈旧校验（T4 三证）：硬编码 1000 属远古负载拒启
        }

        # mock GitCommitGateway 构造抛异常
        with patch.object(gtw_mod, "GitCommitGateway", side_effect=ImportError("no module")):
            rc = rw_mod.run_worker(payload)

        assert rc == 1
        records = _query_records(tmp_repo_with_db)
        # 应有 critical_warn，无 clean
        warns = [r for r in records if r["action"] == "critical_warn"]
        cleans = [r for r in records if r["action"] == "clean"]
        assert len(warns) == 1
        assert len(cleans) == 0
