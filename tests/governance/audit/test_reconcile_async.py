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
            write_status_file,
            write_heartbeat,
            read_status_file,
        )

        write_status_file(
            tmp_repo, "hb_sha", STATUS_RUNNING,
            session_id="sess-hb", started_at=int(time.time()),
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
            write_status_file,
            write_heartbeat,
            read_status_file,
        )

        write_status_file(
            tmp_repo, "done_sha", STATUS_DONE,
            session_id="sess", started_at=int(time.time()),
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
            ReconcilerSpec,
            ReconciliationRegistry,
            ReconcileResult,
        )

        calls: list[str] = []
        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(
            gate_id="A", priority=10,
            trigger=lambda files: True,
            reconcile=lambda files, sid: ReconcileResult(action="clean", detail=""),
        ))
        reg.register(ReconcilerSpec(
            gate_id="B", priority=20,
            trigger=lambda files: True,
            reconcile=lambda files, sid: ReconcileResult(action="clean", detail=""),
        ))
        reg.register(ReconcilerSpec(
            gate_id="C-skip", priority=30,
            trigger=lambda files: False,  # trigger 不命中
            reconcile=lambda files, sid: ReconcileResult(action="clean", detail=""),
        ))
        reg.reconcile_for(["x.py"], "sess", heartbeat=lambda g: calls.append(g))
        # A、B 命中并触发心跳，C-skip trigger 不命中不触发
        assert calls == ["A", "B"]

    def test_reconcile_for_heartbeat_none_no_effect(self, tmp_repo):
        """heartbeat=None 时行为与原有一致（无心跳）。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcilerSpec,
            ReconciliationRegistry,
            ReconcileResult,
        )

        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(
            gate_id="X", priority=10,
            trigger=lambda files: True,
            reconcile=lambda files, sid: ReconcileResult(action="clean", detail="ok"),
        ))
        results = reg.reconcile_for(["x.py"], "sess", heartbeat=None)
        assert len(results) == 1
        assert results[0].action == "clean"

    def test_heartbeat_callback_exception_does_not_block(self, tmp_repo):
        """心跳回调抛异常时 reconciler 仍正常执行。"""
        from zephyr.governance.audit.reconciliation_registry import (
            ReconcilerSpec,
            ReconciliationRegistry,
            ReconcileResult,
        )

        def bad_hb(gate_id: str) -> None:
            raise RuntimeError("heartbeat boom")

        reg = ReconciliationRegistry()
        reg.register(ReconcilerSpec(
            gate_id="Y", priority=10,
            trigger=lambda files: True,
            reconcile=lambda files, sid: ReconcileResult(action="clean", detail="ran"),
        ))
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
            sweep_stale_workers,
            read_status_file,
            write_status_file,
        )

        # 模拟 31 分钟前 started + 一个绝对不存在的 pid
        old = int(time.time()) - 1860
        write_status_file(
            tmp_repo, "orphan_sha", STATUS_RUNNING,
            session_id="sess-orphan", started_at=old, worker_pid=99999999,
        )
        # pid 99999999 不存在
        n = sweep_stale_workers(tmp_repo)
        assert n == 1
        data = read_status_file(tmp_repo, "orphan_sha")
        assert data is not None
        assert data["status"] == STATUS_STALE
        assert any("orphaned_worker_dead" in e for e in data["errors"])

    def test_does_not_sweep_live_worker(self, tmp_repo, monkeypatch):
        """running + 超阈值但 pid 仍存活 → 不改写（避免误杀慢 worker）。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            sweep_stale_workers,
            read_status_file,
            write_status_file,
        )

        # 当前进程的 pid 必然存活
        old = int(time.time()) - 1860
        write_status_file(
            tmp_repo, "live_sha", STATUS_RUNNING,
            session_id="sess-live", started_at=old, worker_pid=os.getpid(),
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 0
        data = read_status_file(tmp_repo, "live_sha")
        assert data is not None
        assert data["status"] == STATUS_RUNNING  # 未改写

    def test_does_not_sweep_fresh_running(self, tmp_repo):
        """running 未超阈值 → 不 sweep。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            sweep_stale_workers,
            read_status_file,
            write_status_file,
        )

        write_status_file(
            tmp_repo, "fresh_sha", STATUS_RUNNING,
            session_id="sess", started_at=int(time.time()) - 60,
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
            sweep_stale_workers,
            read_status_file,
            write_status_file,
        )

        old = int(time.time()) - 100000
        write_status_file(
            tmp_repo, "old_done", STATUS_DONE,
            session_id="sess", started_at=old, finished_at=old + 10,
        )
        n = sweep_stale_workers(tmp_repo)
        assert n == 0
        assert read_status_file(tmp_repo, "old_done")["status"] == STATUS_DONE

    def test_heartbeat_takes_priority_over_started_at(self, tmp_repo, monkeypatch):
        """有新鲜心跳的 running 文件即使 started_at 很旧也不 sweep。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            sweep_stale_workers,
            read_status_file,
            write_status_file,
            write_heartbeat,
        )

        old = int(time.time()) - 100000  # started 很久以前
        write_status_file(
            tmp_repo, "hb_sha", STATUS_RUNNING,
            session_id="sess", started_at=old, worker_pid=99999999,
        )
        # 写一个新鲜心跳（刚刚）
        write_heartbeat(tmp_repo, "hb_sha", "SOME-RECONCILER")
        n = sweep_stale_workers(tmp_repo)
        assert n == 0, "心跳新鲜（< 阈值）即使 started_at 很旧也不应 sweep"
        data = read_status_file(tmp_repo, "hb_sha")
        assert data["status"] == STATUS_RUNNING

    def test_stale_heartbeat_triggers_sweep(self, tmp_repo):
        """心跳本身超阈值 + pid 已死 → sweep。"""
        from zephyr.governance.audit.reconcile_runner import (
            STATUS_RUNNING,
            STATUS_STALE,
            sweep_stale_workers,
            read_status_file,
        )
        from pathlib import Path
        import json

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
