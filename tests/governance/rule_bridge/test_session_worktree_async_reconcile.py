# [BLUEPRINT] MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE | docs/03_modules/_domain_governance/blueprint.md | §ARCH-ASYNC-MERGE-RECONCILE-001
# [MODULE] tests.governance.rule_bridge.test_session_worktree_async_reconcile
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.session_worktree (_run_reconcilers_after_merge, _run_reconcilers_after_merge_sync); pytest; unittest.mock
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单元测试——mock launch_reconcile_async 验证 _run_reconcilers_after_merge 异步路径；不依赖真实 git 仓库（mock subprocess.run 返回假 SHA）
# [MODIFY-GUARD] N/A
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] N/A
# [TESTS] N/A
# [A_module] module_id=MOD-GOV_TEST_SESSION_WORKTREE_ASYNC_RECONCILE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_session_worktree_async_reconcile.py — _run_reconcilers_after_merge 异步化测试。

治本（#ARCH-ASYNC-MERGE-RECONCILE-001，2026-07-20）：
原 _run_reconcilers_after_merge 同步调用 reconcile_for()，导致 session_worktree_merge
卡 2-5min。治本改为异步 launch_reconcile_async，merge 立即返回。

测试覆盖：
1. 异步 launch 成功 → 返回 [{"action": "async_pending", ...}]
2. launch 失败 → 回退 sync（_run_reconcilers_after_merge_sync）
3. launch 异常 → 回退 sync
4. SHA 获取失败 → 用 session_id 派生 key（保持异步）
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_enforcement.rule_bridge.session_worktree import (
    _run_reconcilers_after_merge,
    _run_reconcilers_after_merge_sync,
)


class TestRunReconcilersAfterMergeAsync:
    """_run_reconcilers_after_merge 异步路径测试。"""

    def test_async_launch_success_returns_async_pending(self, tmp_path: Path):
        """异步 launch 成功 → 返回 [{"action": "async_pending", ...}]，不调 sync。"""
        # mock subprocess.run 返回假 merge SHA
        fake_sha_result = MagicMock()
        fake_sha_result.returncode = 0
        fake_sha_result.stdout = "abc123def456\n"

        # mock launch_reconcile_async 返回成功
        fake_launch_result = {
            "ok": True,
            "commit_sha": "abc123def456",
            "status": "pending",
            "worker_pid": 12345,
            "payload_file": str(tmp_path / "payload.json"),
            "status_file": str(tmp_path / "status.json"),
            "error": "",
        }

        with (
            patch("subprocess.run", return_value=fake_sha_result),
            patch(
                "zephyr.governance.audit.reconcile_runner.launch_reconcile_async",
                return_value=fake_launch_result,
            ) as mock_launch,
            patch("zephyr.gov_enforcement.rule_bridge.session_worktree._run_reconcilers_after_merge_sync") as mock_sync,
        ):
            result = _run_reconcilers_after_merge(
                ["file1.py", "file2.py"],
                "sess-test",
                tmp_path,
            )

        assert len(result) == 1
        assert result[0]["action"] == "async_pending"
        assert "abc123def456" in result[0]["detail"]
        assert "12345" in result[0]["detail"]
        # launch_reconcile_async 被调用，参数正确
        mock_launch.assert_called_once()
        call_kwargs = mock_launch.call_args
        assert call_kwargs.kwargs["commit_sha"] == "abc123def456"
        assert call_kwargs.kwargs["session_id"] == "sess-test"
        assert call_kwargs.kwargs["committed_files"] == ["file1.py", "file2.py"]
        # sync fallback 不应被调用
        mock_sync.assert_not_called()

    def test_async_launch_failure_falls_back_to_sync(self, tmp_path: Path):
        """launch 失败 → 回退 sync（reconciler 仍需执行）。"""
        fake_sha_result = MagicMock()
        fake_sha_result.returncode = 0
        fake_sha_result.stdout = "abc123\n"

        fake_launch_result = {
            "ok": False,
            "error": "spawn failed: EPERM",
        }

        with (
            patch("subprocess.run", return_value=fake_sha_result),
            patch(
                "zephyr.governance.audit.reconcile_runner.launch_reconcile_async",
                return_value=fake_launch_result,
            ),
            patch(
                "zephyr.gov_enforcement.rule_bridge.session_worktree._run_reconcilers_after_merge_sync",
                return_value=[{"action": "warn", "detail": "sync fallback"}],
            ) as mock_sync,
        ):
            result = _run_reconcilers_after_merge(
                ["file1.py"],
                "sess-test",
                tmp_path,
            )

        assert result == [{"action": "warn", "detail": "sync fallback"}]
        mock_sync.assert_called_once_with(["file1.py"], "sess-test", tmp_path)

    def test_async_launch_exception_falls_back_to_sync(self, tmp_path: Path):
        """launch 异常 → 回退 sync（fail-open）。"""
        fake_sha_result = MagicMock()
        fake_sha_result.returncode = 0
        fake_sha_result.stdout = "abc123\n"

        with (
            patch("subprocess.run", return_value=fake_sha_result),
            patch(
                "zephyr.governance.audit.reconcile_runner.launch_reconcile_async",
                side_effect=OSError("disk full"),
            ),
            patch(
                "zephyr.gov_enforcement.rule_bridge.session_worktree._run_reconcilers_after_merge_sync",
                return_value=[{"action": "warn", "detail": "sync fallback"}],
            ) as mock_sync,
        ):
            result = _run_reconcilers_after_merge(
                ["file1.py"],
                "sess-test",
                tmp_path,
            )

        assert result == [{"action": "warn", "detail": "sync fallback"}]
        mock_sync.assert_called_once()

    def test_sha_fetch_failure_uses_session_id_key(self, tmp_path: Path):
        """SHA 获取失败 → 用 session_id 派生 key（保持异步不阻塞）。"""
        # subprocess.run 返回非零退出码（git rev-parse 失败）
        fake_sha_result = MagicMock()
        fake_sha_result.returncode = 1
        fake_sha_result.stdout = ""

        fake_launch_result = {
            "ok": True,
            "commit_sha": "merge_sess-test",
            "status": "pending",
            "worker_pid": 99999,
            "payload_file": str(tmp_path / "payload.json"),
            "status_file": str(tmp_path / "status.json"),
            "error": "",
        }

        with (
            patch("subprocess.run", return_value=fake_sha_result),
            patch(
                "zephyr.governance.audit.reconcile_runner.launch_reconcile_async",
                return_value=fake_launch_result,
            ) as mock_launch,
            patch("zephyr.gov_enforcement.rule_bridge.session_worktree._run_reconcilers_after_merge_sync") as mock_sync,
        ):
            result = _run_reconcilers_after_merge(
                ["file1.py"],
                "sess-test",
                tmp_path,
            )

        # 仍然走异步路径（不因 SHA 失败而阻塞 merge）
        assert len(result) == 1
        assert result[0]["action"] == "async_pending"
        # launch 用 session_id 派生 key
        call_kwargs = mock_launch.call_args
        assert call_kwargs.kwargs["commit_sha"] == "merge_sess-test"
        # sync 不应被调用
        mock_sync.assert_not_called()

    def test_empty_committed_files_still_launches_async(self, tmp_path: Path):
        """committed_files 为空也应启动异步（保持与原 sync 行为一致——reconciler trigger 自行决定）。"""
        fake_sha_result = MagicMock()
        fake_sha_result.returncode = 0
        fake_sha_result.stdout = "abc123\n"

        fake_launch_result = {
            "ok": True,
            "commit_sha": "abc123",
            "status": "pending",
            "worker_pid": 12345,
            "payload_file": str(tmp_path / "payload.json"),
            "status_file": str(tmp_path / "status.json"),
            "error": "",
        }

        with (
            patch("subprocess.run", return_value=fake_sha_result),
            patch(
                "zephyr.governance.audit.reconcile_runner.launch_reconcile_async",
                return_value=fake_launch_result,
            ) as mock_launch,
        ):
            result = _run_reconcilers_after_merge(
                [],
                "sess-test",
                tmp_path,
            )

        assert len(result) == 1
        assert result[0]["action"] == "async_pending"
        mock_launch.assert_called_once()
        assert mock_launch.call_args.kwargs["committed_files"] == []


class TestRunReconcilersAfterMergeSyncFallback:
    """_run_reconcilers_after_merge_sync（sync fallback）测试。

    验证 sync fallback 保留原同步行为——只在 async launch 失败时触发。
    """

    def test_sync_function_exists_and_callable(self, tmp_path: Path):
        """sync fallback 函数存在且可调用（不抛异常即视为基本可用）。"""
        # 不实际执行 reconciler（需要完整 GitCommitGateway 环境），
        # 仅验证函数签名和异常处理。mock 内部依赖。
        with (
            patch("zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway") as mock_gw_cls,
            patch("zephyr.governance.audit.reconciliation_registry._log_reconcile_results"),
        ):
            mock_gw = MagicMock()
            mock_gw_cls.return_value = mock_gw
            mock_registry = MagicMock()
            mock_registry.reconcile_for.return_value = []
            mock_gw._reconciliation_registry = mock_registry
            mock_batcher = MagicMock()
            mock_gw._batcher = mock_batcher

            result = _run_reconcilers_after_merge_sync(
                ["file1.py"],
                "sess-test",
                tmp_path,
            )

        assert isinstance(result, list)
        # 无 reconciler 结果时返回空 list
        assert len(result) == 0

    def test_sync_function_exception_returns_warn(self, tmp_path: Path):
        """sync fallback 异常 → 返回 [{"action": "warn", ...}]（不抛异常）。"""
        with patch(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway",
            side_effect=RuntimeError("gateway init failed"),
        ):
            result = _run_reconcilers_after_merge_sync(
                ["file1.py"],
                "sess-test",
                tmp_path,
            )

        assert len(result) == 1
        assert result[0]["action"] == "warn"
        assert "gateway init failed" in result[0]["detail"]
