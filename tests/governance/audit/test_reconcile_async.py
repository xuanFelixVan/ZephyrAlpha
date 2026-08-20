# [BLUEPRINT] MOD-GOV_TEST_RECONCILE_ASYNC | tests/governance/audit/test_reconcile_async.py | §Ruling-100PCT-AI-GOVERNANCE-P2-3
# [MODULE] tests.governance.audit.test_reconcile_async
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconcile_runner; zephyr.governance.audit.reconcile_worker; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 临时目录隔离；不依赖真实 Zephyr 项目结构（worker 测试用 mock）
# [MODIFY-GUARD] 测试函数名与 P2-3 API 对齐
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败→pytest assert error
# [TESTS] self
# [A_module] module_id=MOD-GOV_TEST_RECONCILE_ASYNC | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_reconcile_async.py — P2-3 reconciler 链路异步化测试

测试覆盖：
  1. reconcile_runner.write_status_file / read_status_file 原子读写 + 僵尸判定
  2. reconcile_runner.launch_reconcile_async spawn subprocess + payload/status file 写入
  3. reconcile_runner.query_reconcile_status 状态查询（running/done/failed/stale/unknown）
  4. reconcile_worker.load_payload 读后即焚
  5. GitCommitGateway.run_post_commit_reconcile 分发（sync env / async 默认）
  6. _run_post_commit_reconcile_async fallback（commit_sha 缺失 / launch 失败）
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_repo(tmp_path, monkeypatch):
    """临时项目根目录 + 确保 .runtime/reconcile_reports/ 存在。"""
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    (repo / ".runtime" / "reconcile_reports").mkdir(parents=True)
    monkeypatch.setenv("PYTHONPATH", str(repo / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""))
    return repo


@pytest.fixture(autouse=True)
def _isolate_governance_db(tmp_repo, monkeypatch):
    """#50 治本：测试审计日志与生产 governance.db 强制隔离。

    病根（2026-08-14 实证 10 行污染）：tests/conftest.py basetemp=<repo>/.runtime/tmp/
    pytest_<pid>，worktree 内跑 pytest 时 tmp_repo 位于 .worktrees/<sid>/ 下，
    strip_session_worktree 剥离后 _governance_db_path 锚定主仓 governance.db——
    测试 SHA（live_heal_sha/live_timeout_sha/orphan_clean_sha/pending_clean_sha 等）
    写入生产 reconcile_execution_log 触发 RECONCILER-HEALTH 误报横幅；且告警计数
    跨测试/跨运行在生产库累积泄漏（test_live_timeout_* 期望 1 实测 2-3 逐次递增）。
    治本：模块级 autouse fixture 强制 governance.db 锚定 tmp_repo（每测试独立空库），
    测试审计写入与生产零共享；_check_recent_critical_warns/_log_reconcile_results
    内部均经模块级 _governance_db_path 解析，patch 一处全链覆盖。
    """
    import zephyr.governance.audit.reconciliation_registry as _reg_mod

    db_path = str(tmp_repo / "data" / "databases" / "governance.db")
    monkeypatch.setattr(_reg_mod, "_governance_db_path", lambda _root: db_path)


# ---------------------------------------------------------------------------
# write_status_file / read_status_file
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


class TestStatusFileIO:
    """status file 原子读写 + 僵尸判定。"""

    def test_write_and_read_roundtrip(self, tmp_repo):
        """写 status=done 后读取应返回相同字段。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_DONE,
            read_status_file,
            write_status_file,
        )

        write_status_file(
            tmp_repo,
            "abc123",
            STATUS_DONE,
            session_id="sess-test",
            started_at=1000,
            finished_at=1010,
            reconcilers_total=30,
            reconcilers_warn=2,
            reconcilers_auto_committed=1,
            errors=["err1"],
        )
        data = read_status_file(tmp_repo, "abc123")
        assert data is not None
        assert data["status"] == STATUS_DONE
        assert data["commit_sha"] == "abc123"
        assert data["session_id"] == "sess-test"
        assert data["started_at"] == 1000
        assert data["finished_at"] == 1010
        assert data["reconcilers_total"] == 30
        assert data["reconcilers_warn"] == 2
        assert data["reconcilers_auto_committed"] == 1
        assert data["errors"] == ["err1"]

    def test_read_nonexistent_returns_none(self, tmp_repo):
        """status file 不存在返回 None。"""
        from zephyr.governance.audit.reconcile_runner import read_status_file

        assert read_status_file(tmp_repo, "nonexistent") is None

    def test_stale_detection(self, tmp_repo):
        """running 状态超过阈值改判为 stale。"""
        from zephyr.governance.audit import reconcile_runner
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            read_status_file,
            write_status_file,
        )

        # 模拟 31 分钟前 started
        old_started = int(time.time()) - 1860  # 31 分钟前
        write_status_file(
            tmp_repo,
            "stale_sha",
            STATUS_RUNNING,
            session_id="sess-stale",
            started_at=old_started,
        )
        data = read_status_file(tmp_repo, "stale_sha")
        assert data is not None
        assert data["status"] == "stale", "超 30min 的 running 应改判 stale"

    def test_running_within_threshold_not_stale(self, tmp_repo):
        """running 状态未超阈值不变。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            read_status_file,
            write_status_file,
        )

        write_status_file(
            tmp_repo,
            "fresh_sha",
            STATUS_RUNNING,
            session_id="sess-fresh",
            started_at=int(time.time()) - 60,  # 1 分钟前
        )
        data = read_status_file(tmp_repo, "fresh_sha")
        assert data is not None
        assert data["status"] == STATUS_RUNNING


# ---------------------------------------------------------------------------
# launch_reconcile_async
# ---------------------------------------------------------------------------


class TestLaunchReconcileAsync:
    """launch_reconcile_async 启动逻辑（mock subprocess.Popen）。"""

    def test_launch_writes_payload_and_pending_status(self, tmp_repo, monkeypatch):
        """launch 应写 payload file + pending status file，并 spawn subprocess。"""
        from zephyr.governance.audit import reconcile_runner
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_PENDING,
            launch_reconcile_async,
            read_status_file,
        )

        # mock subprocess.Popen（避免实际 spawn worker）
        class FakeProc:
            pid = 99999

        def fake_popen(*args, **kwargs):
            return FakeProc()

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        result = launch_reconcile_async(
            tmp_repo,
            "sha_launch1",
            "sess-launch",
            ["d:/fake/file1.py", "d:/fake/file2.py"],
            commit_message="test commit",
        )
        assert result["ok"] is True
        assert result["status"] == STATUS_PENDING
        assert result["worker_pid"] == 99999

        # payload file 已写入
        payload_path = tmp_repo / ".runtime" / "reconcile_reports" / "reconcile_payload_sha_launch1.json"
        assert payload_path.exists()
        payload_data = json.loads(payload_path.read_text(encoding="utf-8"))
        assert payload_data["commit_sha"] == "sha_launch1"
        assert payload_data["session_id"] == "sess-launch"
        assert payload_data["committed_files"] == ["d:/fake/file1.py", "d:/fake/file2.py"]

        # status file 已写入（pending）
        status_data = read_status_file(tmp_repo, "sha_launch1")
        assert status_data is not None
        assert status_data["status"] == STATUS_PENDING
        assert status_data["worker_pid"] == 99999

    def test_launch_spawn_failure_returns_failed(self, tmp_repo, monkeypatch):
        """subprocess.Popen 失败时返回 ok=False + status=failed。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_FAILED,
            launch_reconcile_async,
            read_status_file,
        )

        def fake_popen(*args, **kwargs):
            raise OSError("mocked spawn failure")

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        result = launch_reconcile_async(
            tmp_repo,
            "sha_fail",
            "sess-fail",
            ["d:/fake/file.py"],
        )
        assert result["ok"] is False
        assert result["status"] == STATUS_FAILED
        assert "mocked spawn failure" in result["error"]

        # status file 应记录 failed
        status_data = read_status_file(tmp_repo, "sha_fail")
        assert status_data is not None
        assert status_data["status"] == STATUS_FAILED

    def test_launch_sets_sync_env_to_prevent_recursion(self, tmp_repo, monkeypatch):
        """launch 必须在 worker env 设 ZEPHYR_RECONCILE_SYNC=1 阻断递归 spawn。

        病根：worker 内 reconciler 调 _commit_auto → commit() → _run_post_commit_reconcile
        dispatcher 默认 async → 又 spawn worker → 无限递归。
        治本：worker env 强制 sync 模式。
        """
        from zephyr.governance.audit.reconcile_runner import launch_reconcile_async

        captured_env: dict = {}

        class FakeProc:
            pid = 88888

        def fake_popen(cmd, *args, env=None, **kwargs):
            captured_env.update(env or {})
            return FakeProc()

        monkeypatch.setattr(subprocess, "Popen", fake_popen)

        launch_reconcile_async(
            tmp_repo,
            "sha_recursion",
            "sess-rec",
            ["d:/fake.py"],
        )
        assert captured_env.get("ZEPHYR_RECONCILE_SYNC") == "1", (
            "worker env 必须设 ZEPHYR_RECONCILE_SYNC=1 阻断递归 spawn"
        )


# ---------------------------------------------------------------------------
# query_reconcile_status
# ---------------------------------------------------------------------------


class TestQueryReconcileStatus:
    """query_reconcile_status 公开 API。"""

    def test_query_unknown_when_no_status_file(self, tmp_repo):
        """status file 不存在返回 status=unknown。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_UNKNOWN,
            query_reconcile_status,
        )

        result = query_reconcile_status(tmp_repo, "missing_sha")
        assert result["ok"] is False
        assert result["status"] == STATUS_UNKNOWN

    def test_query_running_returns_elapsed(self, tmp_repo):
        """running 状态返回 elapsed_seconds = now - started_at。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            query_reconcile_status,
            write_status_file,
        )

        started = int(time.time()) - 30
        write_status_file(
            tmp_repo,
            "running_sha",
            STATUS_RUNNING,
            session_id="sess-run",
            started_at=started,
        )
        result = query_reconcile_status(tmp_repo, "running_sha")
        assert result["ok"] is True
        assert result["status"] == STATUS_RUNNING
        assert result["elapsed_seconds"] >= 30
        assert result["finished_at"] == 0

    def test_query_done_returns_finished_elapsed(self, tmp_repo):
        """done 状态返回 elapsed = finished - started。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_DONE,
            query_reconcile_status,
            write_status_file,
        )

        write_status_file(
            tmp_repo,
            "done_sha",
            STATUS_DONE,
            session_id="sess-done",
            started_at=1000,
            finished_at=1050,
            reconcilers_total=30,
        )
        result = query_reconcile_status(tmp_repo, "done_sha")
        assert result["ok"] is True
        assert result["status"] == STATUS_DONE
        assert result["elapsed_seconds"] == 50
        assert result["reconcilers_total"] == 30


# ---------------------------------------------------------------------------
# reconcile_worker.load_payload
# ---------------------------------------------------------------------------


class TestWorkerLoadPayload:
    """reconcile_worker.load_payload 读后即焚。"""

    def test_load_payload_deletes_file(self, tmp_repo):
        """payload file 读取后立即删除。"""
        from zephyr.governance.audit.reconcile_worker import _load_payload

        payload_path = tmp_repo / "payload_test.json"
        payload_data = {
            "commit_sha": "sha_test",
            "session_id": "sess-test",
            "project_root": str(tmp_repo),
            "committed_files": ["d:/fake.py"],
            "commit_message": "msg",
            "started_at": 12345,
        }
        payload_path.write_text(
            json.dumps(payload_data, ensure_ascii=False),
            encoding="utf-8",
        )

        data = _load_payload(str(payload_path))
        assert data["commit_sha"] == "sha_test"
        assert not payload_path.exists(), "payload file 应已删除"

    def test_load_payload_nonexistent_raises(self, tmp_repo):
        """payload file 不存在抛 FileNotFoundError。"""
        from zephyr.governance.audit.reconcile_worker import _load_payload

        with pytest.raises(FileNotFoundError):
            _load_payload(str(tmp_repo / "nonexistent_payload.json"))


# ---------------------------------------------------------------------------
# GitCommitGateway dispatcher
# ---------------------------------------------------------------------------


class TestGitCommitGatewayDispatcher:
    """GitCommitGateway.run_post_commit_reconcile 分发逻辑。"""

    def test_sync_mode_dispatches_to_sync(self, tmp_repo, monkeypatch):
        """ZEPHYR_RECONCILE_SYNC=1 时调用 _run_post_commit_reconcile_sync。"""
        # 准备：构造一个最小 gateway stub，只 mock 我们关心的方法
        # 不构造真实 gateway（构造会触发 _register_default_reconcilers 拉起 30+ reconciler）
        # 用 SimpleNamespace + 绑定方法的方式 mock
        from types import SimpleNamespace

        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
        )

        call_log: list[str] = []

        class FakeGateway:
            project_root = tmp_repo

            def _run_post_commit_reconcile_sync(self, existing, session_id, msg="", result=None):
                call_log.append("sync")
                return []

            def _run_post_commit_reconcile_async(self, existing, session_id, sha, msg=""):
                call_log.append("async")

        # 绑定真实 _run_post_commit_reconcile 方法到 fake gateway
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            GitCommitGateway,
        )

        fake_gw = FakeGateway()
        # 把真实方法绑定到 fake 实例（unbound function调用）
        # 确保 scripts/governance/d1_structure 存在以通过 skip 检查
        (tmp_repo / "scripts" / "governance" / "d1_structure").mkdir(parents=True)

        # 调用真实 dispatcher
        result = CommitResult(status=CommitStatus.OK, commit_hash="sha_sync_test")
        monkeypatch.setenv("ZEPHYR_RECONCILE_SYNC", "1")
        # 用 unbound 方法调用
        GitCommitGateway.run_post_commit_reconcile(
            fake_gw,
            ["d:/fake.py"],
            "sess-sync",
            result,
            commit_message="msg",
        )
        assert call_log == ["sync"], f"expected ['sync'], got {call_log}"

    def test_async_mode_dispatches_to_async(self, tmp_repo, monkeypatch):
        """默认（无 env var）调用 _run_post_commit_reconcile_async。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
            GitCommitGateway,
        )

        call_log: list[str] = []

        class FakeGateway:
            project_root = tmp_repo

            def _run_post_commit_reconcile_sync(self, existing, session_id, msg="", result=None):
                call_log.append("sync")
                return []

            def _run_post_commit_reconcile_async(self, existing, session_id, sha, msg=""):
                call_log.append("async")

        fake_gw = FakeGateway()
        (tmp_repo / "scripts" / "governance" / "d1_structure").mkdir(parents=True)

        result = CommitResult(status=CommitStatus.OK, commit_hash="sha_async_test")
        monkeypatch.delenv("ZEPHYR_RECONCILE_SYNC", raising=False)
        GitCommitGateway.run_post_commit_reconcile(
            fake_gw,
            ["d:/fake.py"],
            "sess-async",
            result,
            commit_message="msg",
        )
        assert call_log == ["async"], f"expected ['async'], got {call_log}"

    def test_skips_when_status_not_ok(self, tmp_repo, monkeypatch):
        """commit 失败时（status != OK）跳过 reconcile。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
            GitCommitGateway,
        )

        call_log: list[str] = []

        class FakeGateway:
            project_root = tmp_repo

            def _run_post_commit_reconcile_sync(self, *a, **kw):
                call_log.append("sync")

            def _run_post_commit_reconcile_async(self, *a, **kw):
                call_log.append("async")

        fake_gw = FakeGateway()
        result = CommitResult(status=CommitStatus.COMMIT_FAILED, commit_hash="")
        GitCommitGateway.run_post_commit_reconcile(
            fake_gw,
            [],
            "sess-fail",
            result,
            commit_message="",
        )
        assert call_log == [], "FAILED commit 不应触发 reconcile"

    def test_skips_non_zephyr_project(self, tmp_repo, monkeypatch):
        """非 Zephyr 项目（无 scripts/governance/d1_structure）跳过 reconcile。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
            GitCommitGateway,
        )

        call_log: list[str] = []

        class FakeGateway:
            project_root = tmp_repo  # 无 scripts/governance/d1_structure

            def _run_post_commit_reconcile_sync(self, *a, **kw):
                call_log.append("sync")

            def _run_post_commit_reconcile_async(self, *a, **kw):
                call_log.append("async")

        fake_gw = FakeGateway()
        result = CommitResult(status=CommitStatus.OK, commit_hash="sha")
        GitCommitGateway.run_post_commit_reconcile(
            fake_gw,
            [],
            "sess",
            result,
            commit_message="",
        )
        assert call_log == [], "非 Zephyr 项目应跳过 reconcile"


# ---------------------------------------------------------------------------
# _run_post_commit_reconcile_async fallback
# ---------------------------------------------------------------------------


class TestAsyncFallback:
    """_run_post_commit_reconcile_async fallback 到 sync 的边界条件。"""

    def test_empty_commit_sha_falls_back_to_sync(self, tmp_repo):
        """commit_sha 为空时回退 sync。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            GitCommitGateway,
        )

        call_log: list[str] = []

        class FakeGateway:
            project_root = tmp_repo

            def _run_post_commit_reconcile_sync(self, existing, session_id, msg="", result=None):
                call_log.append("sync")
                return []

        fake_gw = FakeGateway()
        # 绑定真实 _run_post_commit_reconcile_async 方法
        GitCommitGateway.run_post_commit_reconcile_async(
            fake_gw,
            ["d:/fake.py"],
            "sess-no-sha",
            "",
            "msg",
        )
        assert call_log == ["sync"], "空 commit_sha 应回退 sync"

    def test_launch_failure_falls_back_to_sync(self, tmp_repo, monkeypatch):
        """launch_reconcile_async 返回 ok=False 时回退 sync。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            GitCommitGateway,
        )

        call_log: list[str] = []

        class FakeGateway:
            project_root = tmp_repo

            def _run_post_commit_reconcile_sync(self, existing, session_id, msg="", result=None):
                call_log.append("sync")
                return []

        # mock launch_reconcile_async 返回失败
        def fake_launch(*args, **kwargs):
            return {"ok": False, "error": "mocked launch failure"}

        # patch import inside _run_post_commit_reconcile_async
        import zephyr.governance.audit.reconcile_runner as runner_mod

        monkeypatch.setattr(runner_mod, "launch_reconcile_async", fake_launch)

        fake_gw = FakeGateway()
        GitCommitGateway.run_post_commit_reconcile_async(
            fake_gw,
            ["d:/fake.py"],
            "sess-launch-fail",
            "sha_launch_fail",
            "msg",
        )
        assert call_log == ["sync"], "launch 失败应回退 sync"

    def test_launch_exception_falls_back_to_sync(self, tmp_repo, monkeypatch):
        """launch_reconcile_async 抛异常时回退 sync。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            GitCommitGateway,
        )

        call_log: list[str] = []

        class FakeGateway:
            project_root = tmp_repo

            def _run_post_commit_reconcile_sync(self, existing, session_id, msg="", result=None):
                call_log.append("sync")
                return []

        def fake_launch(*args, **kwargs):
            raise RuntimeError("mocked launch exception")

        import zephyr.governance.audit.reconcile_runner as runner_mod

        monkeypatch.setattr(runner_mod, "launch_reconcile_async", fake_launch)

        fake_gw = FakeGateway()
        GitCommitGateway.run_post_commit_reconcile_async(
            fake_gw,
            ["d:/fake.py"],
            "sess-launch-exc",
            "sha_exc",
            "msg",
        )
        assert call_log == ["sync"], "launch 异常应回退 sync"


# ---------------------------------------------------------------------------
# #ARCH-RECONCILE-WORKER-HEARTBEAT-001 治本（2026-08-01）
# 心跳信号 + 主动孤儿扫描 + 跨平台进程探活
# ---------------------------------------------------------------------------
class TestHeartbeat:
    """write_heartbeat 刷新 last_heartbeat_at + current_reconciler。"""

    def test_heartbeat_updates_running_file(self, tmp_repo):
        """running 状态文件被心跳刷新。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            read_status_file,
            write_heartbeat,
            write_status_file,
        )

        write_status_file(
            tmp_repo,
            "hb_sha",
            STATUS_RUNNING,
            session_id="sess-hb",
            started_at=int(time.time()),
        )
        write_heartbeat(tmp_repo, "hb_sha", "MANIFEST-RECONCILER")
        data = read_status_file(tmp_repo, "hb_sha")
        assert data is not None
        assert data["status"] == STATUS_RUNNING
        assert data["current_reconciler"] == "MANIFEST-RECONCILER"
        assert data["last_heartbeat_at"] > 0

    def test_heartbeat_skips_nonexistent_file(self, tmp_repo):
        """文件不存在时心跳静默跳过不抛异常。"""
        from zephyr.governance.audit.reconcile_runner import write_heartbeat

        # 不抛异常即通过
        write_heartbeat(tmp_repo, "no_such_sha", "X")

    def test_heartbeat_skips_done_file(self, tmp_repo):
        """非 running 状态（done）心跳不写入。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_DONE,
            read_status_file,
            write_heartbeat,
            write_status_file,
        )

        write_status_file(
            tmp_repo,
            "done_sha",
            STATUS_DONE,
            session_id="sess",
            started_at=int(time.time()),
            finished_at=int(time.time()),
        )
        before = read_status_file(tmp_repo, "done_sha")
        write_heartbeat(tmp_repo, "done_sha", "X")
        after = read_status_file(tmp_repo, "done_sha")
        # 心跳未写入（last_heartbeat_at 仍为缺省 0）
        assert after.get("last_heartbeat_at", 0) == before.get("last_heartbeat_at", 0) == 0

    def test_reconcile_for_heartbeat_callback_invoked(self, tmp_repo):
        """reconcile_for 接收 heartbeat 回调，每个 trigger 命中的 reconciler 调用一次。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        calls: list[str] = []
        reg = ReconciliationRegistry()
        reg.register(
            ReconcilerSpec(
                gate_id="A",
                priority=10,
                trigger=lambda files: True,
                reconcile=lambda files, sid: ReconcileResult(action="clean", detail=""),
                file_ops=frozenset({"read"}),
            )
        )
        reg.register(
            ReconcilerSpec(
                gate_id="B",
                priority=20,
                trigger=lambda files: True,
                reconcile=lambda files, sid: ReconcileResult(action="clean", detail=""),
                file_ops=frozenset({"read"}),
            )
        )
        reg.register(
            ReconcilerSpec(
                gate_id="C-skip",
                priority=30,
                trigger=lambda files: False,  # trigger 不命中
                reconcile=lambda files, sid: ReconcileResult(action="clean", detail=""),
                file_ops=frozenset({"read"}),
            )
        )
        reg.reconcile_for(["x.py"], "sess", heartbeat=lambda g: calls.append(g))
        # A、B 命中并触发心跳，C-skip trigger 不命中不触发
        assert calls == ["A", "B"]

    def test_reconcile_for_heartbeat_none_no_effect(self, tmp_repo):
        """heartbeat=None 时行为与原有一致（无心跳）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        reg = ReconciliationRegistry()
        reg.register(
            ReconcilerSpec(
                gate_id="X",
                priority=10,
                trigger=lambda files: True,
                reconcile=lambda files, sid: ReconcileResult(action="clean", detail="ok"),
                file_ops=frozenset({"read"}),
            )
        )
        results = reg.reconcile_for(["x.py"], "sess", heartbeat=None)
        assert len(results) == 1
        assert results[0].action == "clean"

    def test_heartbeat_callback_exception_does_not_block(self, tmp_repo):
        """心跳回调抛异常时 reconciler 仍正常执行。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcileResult,
            ReconcilerSpec,
            ReconciliationRegistry,
        )

        def bad_hb(gate_id: str) -> None:
            raise RuntimeError("heartbeat boom")

        reg = ReconciliationRegistry()
        reg.register(
            ReconcilerSpec(
                gate_id="Y",
                priority=10,
                trigger=lambda files: True,
                reconcile=lambda files, sid: ReconcileResult(action="clean", detail="ran"),
                file_ops=frozenset({"read"}),
            )
        )
        results = reg.reconcile_for(["x.py"], "sess", heartbeat=bad_hb)
        assert len(results) == 1
        assert results[0].detail == "ran"  # reconciler 仍执行成功


class TestSweepStaleWorkers:
    """sweep_stale_workers 主动改写孤儿 status file。"""

    def test_sweeps_dead_orphan_running_file(self, tmp_repo, monkeypatch):
        """running + 超阈值 + pid 已死 → 改写为 stale。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            STATUS_STALE,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        # 模拟 31 分钟前 started + 一个绝对不存在的 pid
        old = int(time.time()) - 1860
        write_status_file(
            tmp_repo,
            "orphan_sha",
            STATUS_RUNNING,
            session_id="sess-orphan",
            started_at=old,
            worker_pid=99999999,
        )
        # pid 99999999 不存在
        n = sweep_stale_workers(tmp_repo)
        assert n == 1
        data = read_status_file(tmp_repo, "orphan_sha")
        assert data is not None
        assert data["status"] == STATUS_STALE
        assert any("orphaned_worker_dead" in e for e in data["errors"])

    def test_dead_orphan_logs_clean_not_critical_warn(self, tmp_repo):
        """#ARCH-RECONCILE-WORKER-STALE-SEVERITY-001：死孤儿收割记 clean（自愈成功），
        不记 critical_warn——收割即自愈，记 critical_warn 是语义倒置 + 无配对 clean 自愈。
        """
        import sqlite3

        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            sweep_stale_workers,
            write_status_file,
        )
        from zephyr.governance.audit.reconciliation_registry import (
            _check_recent_critical_warns,
            _governance_db_path,
        )

        # _log_reconcile_results 不 mkdir 父目录，预先创建以保证 DB 写入成功
        (tmp_repo / "data" / "databases").mkdir(parents=True, exist_ok=True)
        # 死孤儿：31min 前 started + 绝对不存在的 pid
        old = int(time.time()) - 1860
        write_status_file(
            tmp_repo,
            "orphan_clean_sha",
            STATUS_RUNNING,
            session_id="sess-clean-test",
            started_at=old,
            worker_pid=99999999,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 1

        # DB 行应为 clean（自愈成功），非 critical_warn
        db_path = _governance_db_path(tmp_repo)
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            cur = conn.execute(
                "SELECT action, gate_id, detail FROM reconcile_execution_log "
                "WHERE gate_id='RECONCILE-WORKER-STALE' ORDER BY logged_at DESC LIMIT 1"
            )
            row = cur.fetchone()
        finally:
            conn.close()
        assert row is not None, "sweep 应写一条 RECONCILE-WORKER-STALE DB 记录"
        action, gate_id, detail = row
        assert action == "clean", (
            f"死孤儿应记 clean（自愈成功），实际 action={action}——"
            f"#ARCH-RECONCILE-WORKER-STALE-SEVERITY-001 严重度对齐未生效"
        )
        assert gate_id == "RECONCILE-WORKER-STALE"
        assert "self-heal" in detail or "no active threat" in detail

        # clean 不应进 critical_warn banner 查询（自愈闭环验证）
        warns = _check_recent_critical_warns(tmp_repo)
        stale_warns = [w for w in warns if w["gate_id"] == "RECONCILE-WORKER-STALE"]
        assert not stale_warns, f"clean 记录不应出现在 critical_warn 查询中，实际={stale_warns}"

    def test_does_not_sweep_live_worker(self, tmp_repo, monkeypatch):
        """running + 超阈值但 pid 仍存活 → 不改写（避免误杀慢 worker）。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        # 当前进程的 pid 必然存活
        old = int(time.time()) - 1860
        write_status_file(
            tmp_repo,
            "live_sha",
            STATUS_RUNNING,
            session_id="sess-live",
            started_at=old,
            worker_pid=os.getpid(),
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 0
        data = read_status_file(tmp_repo, "live_sha")
        assert data is not None
        assert data["status"] == STATUS_RUNNING  # 未改写

    def test_live_timeout_logs_critical_warn(self, tmp_repo):
        """#ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001：活进程超时记 critical_warn（真 active threat），
        不记 clean，不标记 stale（worker 仍在运行）——激活原防御性死代码分支。
        """
        import sqlite3

        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )
        from zephyr.governance.audit.reconciliation_registry import (
            _check_recent_critical_warns,
            _governance_db_path,
        )

        (tmp_repo / "data" / "databases").mkdir(parents=True, exist_ok=True)
        # 活进程超时：31min 前 started + 当前进程 PID（必存活）
        old = int(time.time()) - 1860
        write_status_file(
            tmp_repo,
            "live_timeout_sha",
            STATUS_RUNNING,
            session_id="sess-live-timeout",
            started_at=old,
            worker_pid=os.getpid(),
        )
        n = sweep_stale_workers(tmp_repo)
        # live worker 不改写 status file → swept=0（swept 只计 dead-orphan reaped）
        assert n == 0

        # DB 行应为 critical_warn（真 active threat），非 clean
        db_path = _governance_db_path(tmp_repo)
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            cur = conn.execute(
                "SELECT action, gate_id, detail FROM reconcile_execution_log "
                "WHERE gate_id='RECONCILE-WORKER-STALE' ORDER BY logged_at DESC LIMIT 1"
            )
            row = cur.fetchone()
        finally:
            conn.close()
        assert row is not None, "sweep 应写一条 RECONCILE-WORKER-STALE DB 记录"
        action, gate_id, detail = row
        assert action == "critical_warn", (
            f"活进程超时应记 critical_warn（真 active threat），实际 action={action}——"
            f"#ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001 检测路径未激活"
        )
        assert gate_id == "RECONCILE-WORKER-STALE"
        assert "live worker timeout" in detail

        # 活进程不标记 stale（worker 仍在运行）——status file 仍 running
        # （read_status_file 会再触发 _log_stale_to_db live 分支，但 dedup 跳过）
        data = read_status_file(tmp_repo, "live_timeout_sha")
        assert data is not None
        assert data["status"] == STATUS_RUNNING, "活进程不应标记 stale"

        # critical_warn 应进活跃告警查询（真活跃告警，无配对 clean）
        warns = _check_recent_critical_warns(tmp_repo)
        stale_warns = [w for w in warns if w["gate_id"] == "RECONCILE-WORKER-STALE"]
        assert len(stale_warns) == 1, f"活进程超时 critical_warn 应为活跃告警，实际={stale_warns}"

    def test_live_timeout_self_heals_on_completion(self, tmp_repo):
        """#ARCH-RECONCILE-WORKER-LIVE-TIMEOUT-001：活进程超时 critical_warn + worker 终态 clean → 自愈 ack。

        场景：worker 超阈值运行（sweep 记 critical_warn）→ worker 最终到达终态
        （_write_stale_healed_clean 记 clean）→ SQL_AUTO_ACK_HEALED_BY_GATE ack 历史
        critical_warn → 不再进活跃告警查询。补全告警生命周期对称性（对齐 BOOT 先例）。
        """
        import sqlite3

        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            sweep_stale_workers,
            write_status_file,
        )
        from zephyr.governance.audit.reconcile_worker import _write_stale_healed_clean
        from zephyr.governance.audit.reconciliation_registry import (
            _check_recent_critical_warns,
            _governance_db_path,
        )

        (tmp_repo / "data" / "databases").mkdir(parents=True, exist_ok=True)
        old = int(time.time()) - 1860
        write_status_file(
            tmp_repo,
            "live_heal_sha",
            STATUS_RUNNING,
            session_id="sess-heal",
            started_at=old,
            worker_pid=os.getpid(),
        )
        # 1. sweep 记 live-timeout critical_warn
        sweep_stale_workers(tmp_repo)

        db_path = _governance_db_path(tmp_repo)
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            cur = conn.execute(
                "SELECT COUNT(*) FROM reconcile_execution_log "
                "WHERE gate_id='RECONCILE-WORKER-STALE' AND action='critical_warn' "
                "AND acknowledged_at IS NULL"
            )
            unacked_before = cur.fetchone()[0]
        finally:
            conn.close()
        assert unacked_before == 1, f"应有 1 条未 ack 的 live-timeout critical_warn，实际={unacked_before}"

        # 2. worker 到达终态（超阈值）→ _write_stale_healed_clean 写 clean + auto-ack
        _write_stale_healed_clean(tmp_repo, "live_heal_sha", "sess-heal", old)

        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            cur = conn.execute(
                "SELECT COUNT(*) FROM reconcile_execution_log WHERE gate_id='RECONCILE-WORKER-STALE' AND action='clean'"
            )
            clean_count = cur.fetchone()[0]
            cur = conn.execute(
                "SELECT COUNT(*) FROM reconcile_execution_log "
                "WHERE gate_id='RECONCILE-WORKER-STALE' AND action='critical_warn' "
                "AND acknowledged_at IS NULL"
            )
            unacked_after = cur.fetchone()[0]
        finally:
            conn.close()
        assert clean_count >= 1, "终态 clean 应已写入"
        assert unacked_after == 0, (
            f"critical_warn 应被 SQL_AUTO_ACK_HEALED_BY_GATE auto-ack，仍剩 {unacked_after} 条未 ack"
        )

        # 3. 活跃告警查询应不含 STALE（自愈完成）
        warns = _check_recent_critical_warns(tmp_repo)
        stale_warns = [w for w in warns if w["gate_id"] == "RECONCILE-WORKER-STALE"]
        assert not stale_warns, f"终态 clean 后 STALE 不应进活跃告警，实际={stale_warns}"

    def test_does_not_sweep_fresh_running(self, tmp_repo):
        """running 未超阈值 → 不 sweep。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        write_status_file(
            tmp_repo,
            "fresh_sha",
            STATUS_RUNNING,
            session_id="sess",
            started_at=int(time.time()) - 60,
            worker_pid=99999999,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 0
        data = read_status_file(tmp_repo, "fresh_sha")
        assert data is not None
        assert data["status"] == STATUS_RUNNING

    def test_does_not_sweep_done_files(self, tmp_repo):
        """done 状态文件不参与 sweep（即使很旧）。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_DONE,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        old = int(time.time()) - 100000
        write_status_file(
            tmp_repo,
            "old_done",
            STATUS_DONE,
            session_id="sess",
            started_at=old,
            finished_at=old + 10,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 0
        assert read_status_file(tmp_repo, "old_done")["status"] == STATUS_DONE

    def test_heartbeat_takes_priority_over_started_at(self, tmp_repo, monkeypatch):
        """有新鲜心跳的 running 文件即使 started_at 很旧也不 sweep。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            read_status_file,
            sweep_stale_workers,
            write_heartbeat,
            write_status_file,
        )

        old = int(time.time()) - 100000  # started 很久以前
        write_status_file(
            tmp_repo,
            "hb_sha",
            STATUS_RUNNING,
            session_id="sess",
            started_at=old,
            worker_pid=99999999,
        )
        # 写一个新鲜心跳（刚刚）
        write_heartbeat(tmp_repo, "hb_sha", "SOME-RECONCILER")
        n = sweep_stale_workers(tmp_repo)
        assert n == 0, "心跳新鲜（< 阈值）即使 started_at 很旧也不应 sweep"
        data = read_status_file(tmp_repo, "hb_sha")
        assert data["status"] == STATUS_RUNNING

    def test_stale_heartbeat_triggers_sweep(self, tmp_repo):
        """心跳本身超阈值 + pid 已死 → sweep。"""
        import json
        from pathlib import Path

        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            STATUS_STALE,
            read_status_file,
            sweep_stale_workers,
        )

        # 直接构造一个心跳超阈值的 running 文件（write_heartbeat 写当前时间，
        # 这里手写文件以注入过期心跳）
        now = int(time.time())
        data = {
            "commit_sha": "stale_hb_sha",
            "session_id": "sess",
            "status": STATUS_RUNNING,
            "started_at": now - 200000,
            "finished_at": 0,
            "reconcilers_total": 0,
            "reconcilers_warn": 0,
            "reconcilers_auto_committed": 0,
            "errors": [],
            "trigger_source": "post_commit_async",
            "worker_pid": 99999999,
            "last_heartbeat_at": now - 1860,  # 心跳 31 分钟前（超阈值）
            "current_reconciler": "OLD",
        }
        p = Path(tmp_repo) / ".runtime" / "reconcile_reports" / "reconcile_status_stale_hb_sha.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        n = sweep_stale_workers(tmp_repo)
        assert n == 1
        result = read_status_file(tmp_repo, "stale_hb_sha")
        assert result["status"] == STATUS_STALE

    def test_empty_reports_dir_returns_zero(self, tmp_repo):
        """无 status 文件时返回 0 不抛异常。"""
        from zephyr.governance.audit.reconcile_runner import sweep_stale_workers

        assert sweep_stale_workers(tmp_repo) == 0

    def test_no_reports_dir_returns_zero(self, tmp_path):
        """reports 目录不存在时返回 0 不抛异常。"""
        from zephyr.governance.audit.reconcile_runner import sweep_stale_workers

        empty_repo = tmp_path / "empty"
        empty_repo.mkdir()
        assert sweep_stale_workers(empty_repo) == 0


class TestSweepPendingDead:
    """#ARCH-SPAWN-JOB-KILL-001：pending 即死检测（spawn 传输层失败的兜底观测）。

    spawn 成功的 worker 数秒内翻 running；pending 超 120s + pid 已死 =
    spawn 即死（Job Object kill-on-close 连坐实证场景），必须标 stale 可见。
    """

    def test_pending_dead_pid_swept_to_stale(self, tmp_repo):
        """pending + 超阈值 + pid 已死 → 改写 stale（errors 含 spawn_dead_pending）。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_PENDING,
            STATUS_STALE,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        old = int(time.time()) - 300  # 5 分钟前（超 120s 阈值）
        write_status_file(
            tmp_repo,
            "pending_dead_sha",
            STATUS_PENDING,
            session_id="sess-pending-dead",
            started_at=old,
            worker_pid=99999999,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 1
        data = read_status_file(tmp_repo, "pending_dead_sha")
        assert data is not None
        assert data["status"] == STATUS_STALE
        assert any("spawn_dead_pending" in e for e in data["errors"])

    def test_pending_young_not_swept(self, tmp_repo):
        """pending 未超阈值（worker 可能正在启动）→ 不改写。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_PENDING,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        young = int(time.time()) - 30  # 30s（阈值 120s 内）
        write_status_file(
            tmp_repo,
            "pending_young_sha",
            STATUS_PENDING,
            session_id="sess-pending-young",
            started_at=young,
            worker_pid=99999999,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 0
        data = read_status_file(tmp_repo, "pending_young_sha")
        assert data is not None
        assert data["status"] == STATUS_PENDING

    def test_pending_live_pid_not_swept(self, tmp_repo):
        """pending + 超阈值 + pid 存活（PID 复用边界）→ 不改写。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_PENDING,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        old = int(time.time()) - 300
        write_status_file(
            tmp_repo,
            "pending_live_sha",
            STATUS_PENDING,
            session_id="sess-pending-live",
            started_at=old,
            worker_pid=os.getpid(),
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 0
        data = read_status_file(tmp_repo, "pending_live_sha")
        assert data is not None
        assert data["status"] == STATUS_PENDING

    def test_pending_no_pid_swept(self, tmp_repo):
        """pending + 超阈值 + 无 pid（极端残留）→ 标 stale（无法自证存活的 pending 不可信）。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_PENDING,
            STATUS_STALE,
            read_status_file,
            sweep_stale_workers,
            write_status_file,
        )

        old = int(time.time()) - 300
        write_status_file(
            tmp_repo,
            "pending_npid_sha",
            STATUS_PENDING,
            session_id="sess-pending-npid",
            started_at=old,
            worker_pid=0,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 1
        data = read_status_file(tmp_repo, "pending_npid_sha")
        assert data is not None
        assert data["status"] == STATUS_STALE
        assert any("spawn_dead_pending" in e for e in data["errors"])

    def test_pending_dead_logs_clean_not_critical_warn(self, tmp_repo):
        """死孤儿语义对齐 #ARCH-RECONCILE-WORKER-STALE-SEVERITY-001：
        pending 即死收割记 clean（收割即自愈），不记 critical_warn。
        """
        import sqlite3

        from zephyr.governance.audit.reconcile_runner import (
            STATUS_PENDING,
            sweep_stale_workers,
            write_status_file,
        )
        from zephyr.governance.audit.reconciliation_registry import (
            _governance_db_path,
        )

        (tmp_repo / "data" / "databases").mkdir(parents=True, exist_ok=True)
        old = int(time.time()) - 300
        write_status_file(
            tmp_repo,
            "pending_clean_sha",
            STATUS_PENDING,
            session_id="sess-pending-clean",
            started_at=old,
            worker_pid=99999999,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 1

        db_path = _governance_db_path(tmp_repo)
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            cur = conn.execute(
                "SELECT action, gate_id FROM reconcile_execution_log "
                "WHERE gate_id='RECONCILE-WORKER-STALE' ORDER BY logged_at DESC LIMIT 1"
            )
            row = cur.fetchone()
        finally:
            conn.close()
        assert row is not None, "pending 即死收割应写 RECONCILE-WORKER-STALE DB 记录"
        action, gate_id = row
        assert action == "clean", f"pending 即死属死孤儿（收割即自愈），应记 clean，实际 action={action}"
        assert gate_id == "RECONCILE-WORKER-STALE"


class TestIsPidAlive:
    """_is_pid_alive 跨平台进程探活（真源：process_pool.is_pid_alive 别名）。"""

    def test_current_pid_alive(self):
        from zephyr.governance.audit.reconcile_runner import _is_pid_alive

        assert _is_pid_alive(os.getpid()) is True

    def test_nonexistent_pid_dead(self):
        from zephyr.governance.audit.reconcile_runner import _is_pid_alive

        # 99999999 几乎不可能存在
        assert _is_pid_alive(99999999) is False

    def test_zero_pid_dead(self):
        from zephyr.governance.audit.reconcile_runner import _is_pid_alive

        assert _is_pid_alive(0) is False
        assert _is_pid_alive(-1) is False


# ---------------------------------------------------------------------------
# T2 worker 启动三证（#ARCH-RECONCILER-AUTO-DELETE-GOV-001，2026-08-14）
# ---------------------------------------------------------------------------
class TestWorkerAdmission:
    """_check_worker_admission 三证：锚定存活/payload 新鲜度/session 活性。"""

    def _payload(self, tmp_repo, **over):
        base = {
            "commit_sha": "sha_admit",
            "session_id": "sess-admit",
            "project_root": str(tmp_repo),
            "committed_files": [],
            "commit_message": "m",
            "started_at": int(time.time()),
        }
        base.update(over)
        return base

    def test_accepts_fresh_main_repo_payload(self, tmp_repo):
        """主仓锚定 + 新鲜 payload → 放行（免证1/证3）。"""
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission

        ok, reason = _check_worker_admission(self._payload(tmp_repo))
        assert ok, f"主仓新鲜 payload 应放行，实际拒：{reason}"

    def test_rejects_stale_payload(self, tmp_repo):
        """证2：started_at 超 15min → 拒启（远古负载）。"""
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission

        stale = int(time.time()) - 20 * 60
        ok, reason = _check_worker_admission(self._payload(tmp_repo, started_at=stale))
        assert not ok
        assert "证2" in reason

    def test_rejects_missing_worktree_anchor(self, tmp_repo):
        """证1：锚定 .worktrees/<sid>/ 但目录不存在 → 拒启（rogue worker 场景）。"""
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission

        wt = str(tmp_repo / ".worktrees" / "AI-GONE-001")
        ok, reason = _check_worker_admission(self._payload(tmp_repo, project_root=wt))
        assert not ok
        assert "证1" in reason and "不存在" in reason

    def test_rejects_missing_git_pointer(self, tmp_repo):
        """证1：worktree 目录在但 .git 指针被扫走 → 拒启（sweeper 后遗症防穿透）。"""
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission

        wt = tmp_repo / ".worktrees" / "AI-BROKEN-001"
        wt.mkdir(parents=True)  # 目录存在但无 .git 指针
        ok, reason = _check_worker_admission(self._payload(tmp_repo, project_root=str(wt)))
        assert not ok
        assert "证1" in reason and ".git" in reason

    def test_rejects_worktree_with_dead_session(self, tmp_repo):
        """证3：worktree 完好但锚定 session 无活跃记录 → 拒启。"""
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission

        wt = tmp_repo / ".worktrees" / "AI-DEAD-001"
        wt.mkdir(parents=True)
        (wt / ".git").write_text("gitdir: x", encoding="utf-8")
        ok, reason = _check_worker_admission(self._payload(tmp_repo, project_root=str(wt), session_id="AI-DEAD-001"))
        assert not ok
        assert "证3" in reason

    def test_accepts_worktree_with_live_session(self, tmp_repo):
        """证3 通过：worktree 完好 + session 在 registry 活跃 → 放行。"""
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        wt = tmp_repo / ".worktrees" / "AI-LIVE-001"
        wt.mkdir(parents=True)
        (wt / ".git").write_text("gitdir: x", encoding="utf-8")
        SessionRegistry(tmp_repo).register("AI-LIVE-001", pid=os.getpid())
        ok, reason = _check_worker_admission(self._payload(tmp_repo, project_root=str(wt), session_id="AI-LIVE-001"))
        assert ok, f"三证齐全应放行，实际拒：{reason}"

    def test_accepts_recently_active_session_dead_pid(self, tmp_repo):
        """证3 宽限回归（086d0e24 拒启实证治本）：一次性 commit 进程退出后
        PID 死亡但心跳在 15min 宽限窗内 → 放行。

        竞态机制：claim_file auto-register 以网关 python pid 注册，git_commit.py
        退出即 PID 死亡；detached worker 秒级启动时 list_active 已收割该记录——
        原"仅当前活跃"口径对全部一次性 commit 系统性误杀（4/5 commit 中招实证）。
        """
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        wt = tmp_repo / ".worktrees" / "AI-ONESHOT-001"
        wt.mkdir(parents=True)
        (wt / ".git").write_text("gitdir: x", encoding="utf-8")
        # 死 pid（网关进程已退出）+ 新鲜心跳（commit 时刻刚 claim 刷新）
        SessionRegistry(tmp_repo).register("AI-ONESHOT-001", pid=99999999)
        ok, reason = _check_worker_admission(self._payload(tmp_repo, project_root=str(wt), session_id="AI-ONESHOT-001"))
        assert ok, f"近期活跃（心跳在宽限窗内）应放行，实际拒：{reason}"

    def test_rejects_ancient_session_record(self, tmp_repo):
        """证3 安全边界：心跳超 15min 宽限窗的远古记录（死 pid）→ 仍拒启。"""
        from zephyr.governance.audit.reconcile_worker import _check_worker_admission
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        wt = tmp_repo / ".worktrees" / "AI-ANCIENT-001"
        wt.mkdir(parents=True)
        (wt / ".git").write_text("gitdir: x", encoding="utf-8")
        registry = SessionRegistry(tmp_repo)
        registry.register("AI-ANCIENT-001", pid=99999999)
        # 篡改心跳为 20min 前（超出 PAYLOAD_TTL_SECONDS=15min 宽限窗）
        data = registry.load()
        data["AI-ANCIENT-001"]["last_heartbeat"] = time.time() - 20 * 60
        registry.save(data)
        ok, reason = _check_worker_admission(self._payload(tmp_repo, project_root=str(wt), session_id="AI-ANCIENT-001"))
        assert not ok
        assert "证3" in reason


# ---------------------------------------------------------------------------
# TestDenialStatusPlacement — #109 拒启 status 落点分诊回归
# ---------------------------------------------------------------------------


class TestDenialStatusPlacement:
    """#109 治本回归：worker 拒启（三证）时 status 落点按拒启类型分诊。

    病灶（2026-08-17 AI-GOVB-001 复现）：launch 在 worktree 写 pending，
    证2/证3 拒启却把 failed 写主仓（anchor_main_root 无条件剥离）——
    pending@worktree 永不更新 + failed@主仓双文件分裂，外部观测即
    「worktree 状态文件未落盘」。分诊：worktree 根存活→落 worktree 原位；
    根已失（证1）→落主仓（原行为）。
    """

    def _wt_payload(self, tmp_repo, sid, **over):
        wt = tmp_repo / ".worktrees" / sid
        wt.mkdir(parents=True)
        (wt / ".git").write_text("gitdir: x", encoding="utf-8")
        (wt / ".runtime" / "reconcile_reports").mkdir(parents=True)
        base = {
            "commit_sha": "sha_deny_" + sid.lower(),
            "session_id": sid,
            "project_root": str(wt),
            "committed_files": [],
            "commit_message": "m",
            "started_at": int(time.time()),
        }
        base.update(over)
        return wt, base

    def test_denial_writes_failed_status_to_live_worktree(self, tmp_repo):
        """证3 拒启（session 无活跃）且 worktree 存活 → failed status 落 worktree 原位。"""
        from zephyr.governance.audit.reconcile_worker import _run_worker

        wt, payload = self._wt_payload(tmp_repo, "AI-DENY-001")
        rc = _run_worker(payload)
        assert rc == 1
        sf = wt / ".runtime" / "reconcile_reports" / ("reconcile_status_" + payload["commit_sha"] + ".json")
        assert sf.is_file(), "worktree 原位应有 failed status（#109 split-brain 回归）"
        data = json.loads(sf.read_text(encoding="utf-8"))
        assert data["status"] == "failed"
        assert any("三证拒启" in e for e in data["errors"])

    def test_denial_writes_failed_status_to_main_when_worktree_gone(self, tmp_repo):
        """证1 拒启（worktree 目录不存在）→ failed status 落主仓（原行为保留）。"""
        from zephyr.governance.audit.reconcile_worker import _run_worker

        wt = tmp_repo / ".worktrees" / "AI-GONE-002"
        payload = {
            "commit_sha": "sha_gone_002",
            "session_id": "AI-GONE-002",
            "project_root": str(wt),
            "committed_files": [],
            "commit_message": "m",
            "started_at": int(time.time()),
        }
        rc = _run_worker(payload)
        assert rc == 1
        sf = tmp_repo / ".runtime" / "reconcile_reports" / "reconcile_status_sha_gone_002.json"
        assert sf.is_file(), "主仓应有 failed status（证1 原行为保留）"
        data = json.loads(sf.read_text(encoding="utf-8"))
        assert data["status"] == "failed"
        assert any("三证拒启" in e for e in data["errors"])
