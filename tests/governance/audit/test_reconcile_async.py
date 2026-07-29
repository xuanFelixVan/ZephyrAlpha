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
            tmp_repo, "abc123", STATUS_DONE,
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
            tmp_repo, "stale_sha", STATUS_RUNNING,
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
            tmp_repo, "fresh_sha", STATUS_RUNNING,
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
            tmp_repo, "sha_launch1", "sess-launch",
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
            tmp_repo, "sha_fail", "sess-fail",
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
            tmp_repo, "sha_recursion", "sess-rec",
            ["d:/fake.py"],
        )
        assert captured_env.get("ZEPHYR_RECONCILE_SYNC") == "1", \
            "worker env 必须设 ZEPHYR_RECONCILE_SYNC=1 阻断递归 spawn"


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
            tmp_repo, "running_sha", STATUS_RUNNING,
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
            tmp_repo, "done_sha", STATUS_DONE,
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
            json.dumps(payload_data, ensure_ascii=False), encoding="utf-8",
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
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitResult,
            CommitStatus,
        )

        # 不构造真实 gateway（构造会触发 _register_default_reconcilers 拉起 30+ reconciler）
        # 用 SimpleNamespace + 绑定方法的方式 mock
        from types import SimpleNamespace

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
            fake_gw, ["d:/fake.py"], "sess-sync", result, commit_message="msg",
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
            fake_gw, ["d:/fake.py"], "sess-async", result, commit_message="msg",
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
            fake_gw, [], "sess-fail", result, commit_message="",
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
            fake_gw, [], "sess", result, commit_message="",
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
            fake_gw, ["d:/fake.py"], "sess-no-sha", "", "msg",
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
            fake_gw, ["d:/fake.py"], "sess-launch-fail", "sha_launch_fail", "msg",
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
            fake_gw, ["d:/fake.py"], "sess-launch-exc", "sha_exc", "msg",
        )
        assert call_log == ["sync"], "launch 异常应回退 sync"
