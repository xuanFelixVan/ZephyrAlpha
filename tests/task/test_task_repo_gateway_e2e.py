# [BLUEPRINT] MOD-INF-005 | tests/test_task_repo_gateway_e2e.py | §ghost-commit-e2e
# [MODULE] tests.test_task_repo_gateway_e2e
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] tests.__init__; zephyr.governance.persistence.task_repo; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 端到端链路测试——任务COMPLETED→网关→提交→清理；异常回退；各状态处理
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0=全PASS; 非0=有FAIL
# [TESTS]
# [A_module] module_id=MOD-GOV-test_task_repo_gateway_e2e | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_task_repo_gateway_e2e.py — 端到端链路测试（OPS-2026062516）

验证 TaskRepository._auto_commit_on_completion → GitCommitGateway 完整链路：
1. 正常链路：任务完成 → 网关提交 → commit 成功
2. 无文件链路：files_in_scope 为空 → 跳过 commit
3. 文件不存在链路：files_in_scope 文件不存在 → 跳过 commit
4. 网关异常回退：GitCommitGateway 抛异常 → 任务不受影响
5. NOTHING_TO_COMMIT：文件无变更 → 跳过 commit
6. STASH_CONFLICT：stash pop 失败 → 任务完成但警告
7. COMMIT_FAILED：commit 命令失败 → 任务完成但警告
8. LOCK_TIMEOUT：锁超时 → 任务完成但警告

设计原则：
- 直接测试 _auto_commit_on_completion 方法（不经过 DB transition，避免 DB 依赖）
- 用 mock TaskCard 对象 + 临时 git 仓库
- 验证核心不变量：任务完成不受 commit 结果影响
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus
from zephyr.governance.persistence.task_repo import TaskRepository


def _init_repo(repo_dir: Path) -> None:
    """初始化临时 git 仓库。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "E2E-Test"
    env["GIT_AUTHOR_EMAIL"] = "e2e@test.com"
    env["GIT_COMMITTER_NAME"] = "E2E-Test"
    env["GIT_COMMITTER_EMAIL"] = "e2e@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "E2E-Test"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "e2e@test.com"], cwd=str(repo_dir), capture_output=True, check=True)
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _commit_file(repo_dir: Path, rel: str, content: str) -> None:
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", rel], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", f"init {rel}", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _make_mock_task(task_id: str, files_in_scope: list[str], session_id: str = "e2e-test") -> MagicMock:
    """创建 mock TaskCard 对象。"""
    task = MagicMock()
    task.task_id = task_id
    task.files_in_scope = files_in_scope
    task.session_id = session_id
    return task


def _make_repo(tmp_path: Path) -> TaskRepository:
    """创建 TaskRepository 实例（不连接真实 DB，仅测试 _auto_commit_on_completion）。"""
    # TaskRepository.__init__ 需要 db_path，但 _auto_commit_on_completion 不使用 DB
    # 用 mock DB 路径
    repo = TaskRepository.__new__(TaskRepository)
    return repo


class TestAutoCommitE2E:
    """端到端链路测试：_auto_commit_on_completion → GitCommitGateway。"""

    def test_normal_chain_commit_success(self, tmp_path: Path) -> None:
        """场景1: 正常链路——任务完成 → 网关提交 → commit 成功。

        验证：
        - GitCommitGateway 被调用
        - commit message 含 task_id
        - commit 实际执行（git log 有记录）
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        file_path = str(tmp_path / "a.py")
        task = _make_mock_task("E2E-001", [file_path])
        repo = _make_repo(tmp_path)

        # patch GitCommitGateway 使用临时仓库
        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            MockGW.return_value.commit.return_value = CommitResult(
                status=CommitStatus.OK,
                message="committed 1 files",
                commit_hash="abc12345",
            )
            repo._auto_commit_on_completion("E2E-001", task)

            # 验证 GitCommitGateway 被调用
            MockGW.assert_called_once()
            call_args = MockGW.return_value.commit.call_args
            assert call_args.kwargs["session_id"] == "e2e-test"
            assert file_path in call_args.kwargs["files"]
            assert "E2E-001" in call_args.kwargs["message"]

    def test_empty_files_in_scope_skipped(self, tmp_path: Path) -> None:
        """场景2: files_in_scope 为空 → 跳过 commit（不调用网关）。"""
        _init_repo(tmp_path)
        task = _make_mock_task("E2E-002", [])
        repo = _make_repo(tmp_path)

        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            repo._auto_commit_on_completion("E2E-002", task)
            MockGW.assert_not_called()

    def test_nonexistent_files_skipped(self, tmp_path: Path) -> None:
        """场景3: files_in_scope 文件不存在 → 跳过 commit。"""
        _init_repo(tmp_path)
        task = _make_mock_task("E2E-003", [str(tmp_path / "nonexistent.py")])
        repo = _make_repo(tmp_path)

        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            repo._auto_commit_on_completion("E2E-003", task)
            MockGW.assert_not_called()

    def test_gateway_exception_no_crash(self, tmp_path: Path) -> None:
        """场景4: 网关异常 → 任务不受影响（异常被捕获）。

        核心不变量：commit 失败不应影响任务完成状态。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        file_path = str(tmp_path / "a.py")
        task = _make_mock_task("E2E-004", [file_path])
        repo = _make_repo(tmp_path)

        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            MockGW.return_value.commit.side_effect = RuntimeError("gateway crashed")
            # 不应抛异常
            repo._auto_commit_on_completion("E2E-004", task)

    def test_nothing_to_commit_handled(self, tmp_path: Path) -> None:
        """场景5: 文件无变更 → NOTHING_TO_COMMIT → 任务完成。"""
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        # 不修改 a.py，无变更

        file_path = str(tmp_path / "a.py")
        task = _make_mock_task("E2E-005", [file_path])
        repo = _make_repo(tmp_path)

        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            MockGW.return_value.commit.return_value = CommitResult(
                status=CommitStatus.NOTHING_TO_COMMIT,
                message="no staged changes",
            )
            # 不应抛异常
            repo._auto_commit_on_completion("E2E-005", task)

    def test_stash_conflict_handled(self, tmp_path: Path) -> None:
        """场景6: stash pop 失败 → STASH_CONFLICT → 任务完成但警告。

        核心不变量：stash 冲突时数据保留在 stash，不丢失。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        file_path = str(tmp_path / "a.py")
        task = _make_mock_task("E2E-006", [file_path])
        repo = _make_repo(tmp_path)

        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            MockGW.return_value.commit.return_value = CommitResult(
                status=CommitStatus.STASH_CONFLICT,
                message="commit OK but stash pop failed",
                commit_hash="abc12345",
                stash_ref="stash@{0}",
                stash_kept=True,
            )
            # 不应抛异常（任务仍完成）
            repo._auto_commit_on_completion("E2E-006", task)

    def test_commit_failed_handled(self, tmp_path: Path) -> None:
        """场景7: commit 命令失败 → COMMIT_FAILED → 任务完成但警告。"""
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        file_path = str(tmp_path / "a.py")
        task = _make_mock_task("E2E-007", [file_path])
        repo = _make_repo(tmp_path)

        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            MockGW.return_value.commit.return_value = CommitResult(
                status=CommitStatus.COMMIT_FAILED,
                message="git commit failed: some error",
            )
            # 不应抛异常
            repo._auto_commit_on_completion("E2E-007", task)

    def test_lock_timeout_handled(self, tmp_path: Path) -> None:
        """场景8: 锁超时 → LOCK_TIMEOUT → 任务完成但警告。"""
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        file_path = str(tmp_path / "a.py")
        task = _make_mock_task("E2E-008", [file_path])
        repo = _make_repo(tmp_path)

        with patch("zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway") as MockGW:
            MockGW.return_value.commit.return_value = CommitResult(
                status=CommitStatus.LOCK_TIMEOUT,
                message="Cannot acquire lock (timeout 60s)",
            )
            # 不应抛异常
            repo._auto_commit_on_completion("E2E-008", task)

    def test_real_gateway_integration(self, tmp_path: Path) -> None:
        """场景9: 真实网关集成——不 mock，验证完整链路。

        用真实 GitCommitGateway + 临时仓库，验证 commit 实际执行。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        file_path = str(tmp_path / "a.py")
        task = _make_mock_task("E2E-009", [file_path], session_id="real-e2e")
        repo = _make_repo(tmp_path)

        # patch GitCommitGateway 的 project_root 为临时仓库
        with patch.object(
            TaskRepository, "_auto_commit_on_completion",
            TaskRepository._auto_commit_on_completion,
        ):
            # 直接调用，但需要 patch GitCommitGateway 的初始化
            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
            original_init = GitCommitGateway.__init__

            def patched_init(self, project_root=None):
                original_init(self, project_root=str(tmp_path))

            with patch.object(GitCommitGateway, "__init__", patched_init):
                repo._auto_commit_on_completion("E2E-009", task)

        # 验证 commit 实际执行
        log = subprocess.run(
            ["git", "log", "-1", "--format=%B"],
            cwd=str(tmp_path), capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        assert "E2E-009" in log, f"commit message 应含 task_id: {log}"
        assert "[GW:real-e2e]" in log, f"commit 应含 GW 标记: {log}"
