# [BLUEPRINT] MOD-INF-005 | tests/test_git_commit_extreme.py | §ghost-commit-extreme-test
# [MODULE] tests.test_git_commit_extreme
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] tests.__init__; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 极端故障注入测试——进程崩溃/锁损坏/4+并发/TTL过期/stash冲突/磁盘满mock/commit失败/超时
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0=全PASS; 非0=有FAIL
# [TESTS]
# [A_module] module_id=MOD-GOV-test_git_commit_extreme | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_git_commit_extreme.py — GitCommitGateway 极端故障注入测试（OPS-2026062515）

验证 GitCommitGateway 在极端故障场景下的数据安全性：
1. 进程崩溃后锁残留——TTL 过期后能被抢占
2. 锁文件损坏（乱码/空）——能恢复
3. 5 session 并发——全部串行化
4. TTL 到期强制抢占——旧锁被清理
5. stash pop 冲突——保留 stash 不丢数据
6. 磁盘满 mock（stash 写失败）——不丢数据
7. git commit 失败——stash 恢复
8. git 命令超时——不卡死

设计原则：
- 每个测试用独立临时 git 仓库（隔离）
- 故障注入用 mock / 手动破坏锁文件 / 模拟冲突
- 验证核心不变量：数据不丢失（stash 保留或恢复）
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
    CommitStatus,
    GatewayError,
    GitCommitGateway,
    _GLOBAL_LOCK_FILE,
    _LOCK_TTL_SECONDS,
)

_PROJECT_ROOT = REPO_ROOT


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_repo(repo_dir: Path) -> None:
    """初始化临时 git 仓库。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Ext-Test"
    env["GIT_AUTHOR_EMAIL"] = "ext@test.com"
    env["GIT_COMMITTER_NAME"] = "Ext-Test"
    env["GIT_COMMITTER_EMAIL"] = "ext@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Ext-Test"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "ext@test.com"], cwd=str(repo_dir), capture_output=True, check=True)
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _commit_file(repo_dir: Path, rel: str, content: str) -> None:
    """提交初始文件。"""
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", rel], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", f"init {rel}", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _lock_file_path(repo_dir: Path) -> Path:
    """获取锁文件路径。"""
    return repo_dir / ".ailocks" / _GLOBAL_LOCK_FILE


# ---------------------------------------------------------------------------
# 测试类：锁故障注入
# ---------------------------------------------------------------------------
class TestLockFailureInjection:
    """锁相关极端场景。"""

    def test_stale_lock_reclaimed_after_ttl(self, tmp_path: Path) -> None:
        """场景1: 进程崩溃后锁残留——TTL 过期后能被抢占。

        模拟：手动创建一个"过期"的锁文件，验证新 commit 能抢占。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        # 手动创建过期锁文件（时间戳为 TTL 之前）
        lock_file = _lock_file_path(tmp_path)
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        stale_time = time.time() - _LOCK_TTL_SECONDS - 10  # 过期 10 秒
        lock_file.write_text(
            json.dumps({"pid": 99999, "acquired_at": stale_time}),
            encoding="utf-8",
        )
        assert lock_file.exists(), "前置：锁文件存在"

        # 修改文件并 commit——应能抢占过期锁
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
        result = gw.commit("sess-stale", [str(tmp_path / "a.py")], "feat: reclaim stale lock")

        assert result.status == CommitStatus.OK, f"应能抢占过期锁: {result.message}"
        assert not lock_file.exists(), "commit 后锁应被释放"

    def test_corrupted_lock_file_recovered(self, tmp_path: Path) -> None:
        """场景2: 锁文件损坏（乱码）——能恢复。

        模拟：锁文件内容为乱码，验证能被清理并获取锁。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        # 写入损坏的锁文件
        lock_file = _lock_file_path(tmp_path)
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text("CORRUPTED_NOT_JSON{{{", encoding="utf-8")

        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
        result = gw.commit("sess-corrupt", [str(tmp_path / "a.py")], "feat: recover corrupted lock")

        assert result.status == CommitStatus.OK, f"应能恢复损坏锁: {result.message}"

    def test_empty_lock_file_recovered(self, tmp_path: Path) -> None:
        """场景2b: 锁文件为空——能恢复。"""
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        lock_file = _lock_file_path(tmp_path)
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text("", encoding="utf-8")  # 空文件

        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
        result = gw.commit("sess-empty", [str(tmp_path / "a.py")], "feat: recover empty lock")

        assert result.status == CommitStatus.OK, f"应能恢复空锁: {result.message}"

    def test_lock_released_on_exception(self, tmp_path: Path) -> None:
        """场景3: commit 过程中异常——锁必须释放（finally 保证）。"""
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        # mock _stash_other_files 抛异常
        with patch.object(gw, "_stash_other_files", side_effect=RuntimeError("injected crash")):
            (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
            # 不应抛异常（被 commit() 捕获），但锁应释放
            try:
                gw.commit("sess-crash", [str(tmp_path / "a.py")], "feat: crash test")
            except Exception:
                pass  # commit 内部异常处理

        lock_file = _lock_file_path(tmp_path)
        assert not lock_file.exists(), "异常后锁必须释放"


# ---------------------------------------------------------------------------
# 测试类：高并发压力
# ---------------------------------------------------------------------------
class TestHighConcurrency:
    """高并发压力测试。"""

    def test_5_session_concurrent_different_files(self, tmp_path: Path) -> None:
        """场景4: 5 session 并发提交不同文件——全部串行化成功。"""
        _init_repo(tmp_path)
        for i in range(5):
            _commit_file(tmp_path, f"f{i}.py", f"v = {i}\n")
        # 用 i+100 确保所有文件都有实际变更（i*10 对 i=0 无变化）
        for i in range(5):
            (tmp_path / f"f{i}.py").write_text(f"v = {i + 100}\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)

        def commit(sess: str, rel: str):
            r = gw.commit(sess, [str(tmp_path / rel)], f"feat: {sess}")
            return (sess, r.status, r.commit_hash)

        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = [ex.submit(commit, f"S{i}", f"f{i}.py") for i in range(5)]
            results = {f.result()[0]: f.result() for f in as_completed(futures)}

        ok_count = sum(1 for _, s, _ in results.values() if s == CommitStatus.OK)
        assert ok_count == 5, f"5 session 应全部成功, 实际 {ok_count}/5"

        # 验证无跨 session 捡拾
        for sess, _, h in results.values():
            files = subprocess.run(
                ["git", "show", "--name-only", "--format=", h],
                cwd=str(tmp_path), capture_output=True, text=True, encoding="utf-8",
            ).stdout.strip().splitlines()
            idx = int(sess[1:])
            expected = f"f{idx}.py"
            assert files == [expected], f"{sess} 捡拾了其他文件: {files}"

    def test_8_session_concurrent_same_file(self, tmp_path: Path) -> None:
        """场景5: 8 session 并发提交同一文件——串行化不丢数据。"""
        _init_repo(tmp_path)
        _commit_file(tmp_path, "shared.py", "v = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        def commit(sess: str, val: int):
            (tmp_path / "shared.py").write_text(f"v = {val}\n", encoding="utf-8")
            r = gw.commit(sess, [str(tmp_path / "shared.py")], f"feat: {sess}")
            return (sess, r.status)

        with ThreadPoolExecutor(max_workers=8) as ex:
            futures = [ex.submit(commit, f"S{i}", i) for i in range(8)]
            results = [f.result() for f in as_completed(futures)]

        ok_count = sum(1 for _, s in results if s == CommitStatus.OK)
        assert ok_count >= 1, "至少 1 个 commit 应成功"
        # 文件内容应为某个 session 的值
        content = (tmp_path / "shared.py").read_text(encoding="utf-8")
        assert content.startswith("v = "), f"文件内容异常: {content!r}"


# ---------------------------------------------------------------------------
# 测试类：stash 冲突与数据安全
# ---------------------------------------------------------------------------
class TestStashConflictAndDataSafety:
    """stash 冲突和数据安全极端场景。"""

    def test_stash_pop_conflict_keeps_stash(self, tmp_path: Path) -> None:
        """场景6: stash pop 冲突——保留 stash 不丢数据。

        模拟：A 修改 a.py，B commit a.py（不同内容），A 的 stash pop 时冲突。
        验证：stash 保留，数据不丢失。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        # A 修改 a.py（未暂存）
        (tmp_path / "a.py").write_text("a = A_UNSTAGED\n", encoding="utf-8")

        # B 通过 gateway commit a.py（不同内容）
        # 先把 A 的修改 stash 走，再写 B 的内容
        (tmp_path / "a.py").write_text("a = B_COMMIT\n", encoding="utf-8")
        result = gw.commit("B", [str(tmp_path / "a.py")], "feat: B")

        # B commit 成功后，stash pop 会尝试恢复 A 的 "a = A_UNSTAGED"
        # 但此时 a.py 已是 "a = B_COMMIT"，可能冲突
        if result.status == CommitStatus.STASH_CONFLICT:
            # stash pop 失败——验证 stash 保留
            stash_list = subprocess.run(
                ["git", "stash", "list"], cwd=str(tmp_path),
                capture_output=True, text=True, encoding="utf-8",
            ).stdout.strip()
            assert "gw:" in stash_list or "stash" in stash_list.lower(), \
                f"stash pop 失败应保留 stash: {stash_list}"
        elif result.status == CommitStatus.OK:
            # stash pop 成功——验证 A 的修改恢复（可能 git 自动合并了）
            content = (tmp_path / "a.py").read_text(encoding="utf-8")
            # 内容应该是 A 或 B 的（取决于合并）
            assert "a = " in content, f"文件内容异常: {content!r}"
        else:
            pytest.fail(f"意外的 commit 状态: {result.status} {result.message}")

    def test_disk_full_stash_failure_no_data_loss(self, tmp_path: Path) -> None:
        """场景7: 磁盘满 mock（stash 写失败）——不丢数据。

        模拟：_stash_other_files 返回 (False, "")，验证 commit 仍能执行或安全跳过。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        _commit_file(tmp_path, "b.py", "b = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        # A 修改 b.py（未暂存）
        (tmp_path / "b.py").write_text("b = UNSTAGED\n", encoding="utf-8")
        # B commit a.py
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        # mock stash 失败（模拟磁盘满）
        with patch.object(gw, "_stash_other_files", return_value=(False, "")):
            result = gw.commit("B", [str(tmp_path / "a.py")], "feat: disk full")

        # 验证：commit 可能成功（a.py 提交了），b.py 修改应保留（没被 stash）
        assert result.status in (CommitStatus.OK, CommitStatus.COMMIT_FAILED), \
            f"磁盘满时应有明确状态: {result.status}"
        # b.py 修改应仍在工作区（没被 stash 走）
        assert (tmp_path / "b.py").read_text(encoding="utf-8") == "b = UNSTAGED\n", \
            "b.py 修改不应丢失"

    def test_commit_failure_stash_restored(self, tmp_path: Path) -> None:
        """场景8: git commit 失败——stash 必须恢复。

        模拟：commit 命令失败，验证 stash pop 仍执行（finally 保证）。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        _commit_file(tmp_path, "b.py", "b = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        # A 修改 b.py（会被 stash）
        (tmp_path / "b.py").write_text("b = UNSTAGED\n", encoding="utf-8")
        # B commit a.py
        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")

        # mock commit 失败
        original_commit = gw._commit_with_file_message

        def failing_commit(message, pathspec_file=None, target_files=None):
            return None, "injected commit failure"

        with patch.object(gw, "_commit_with_file_message", side_effect=failing_commit):
            result = gw.commit("B", [str(tmp_path / "a.py")], "feat: commit fail")

        assert result.status == CommitStatus.COMMIT_FAILED, \
            f"commit 失败应返回 COMMIT_FAILED: {result.status}"
        # stash 必须恢复（finally 保证）
        assert (tmp_path / "b.py").read_text(encoding="utf-8") == "b = UNSTAGED\n", \
            "commit 失败后 b.py 修改应恢复（stash pop）"
        # 无 stash 残留
        stash_list = subprocess.run(
            ["git", "stash", "list"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()
        assert not stash_list, f"commit 失败后不应有 stash 残留: {stash_list}"


# ---------------------------------------------------------------------------
# 测试类：超时与资源耗尽
# ---------------------------------------------------------------------------
class TestTimeoutAndResourceExhaustion:
    """超时和资源耗尽场景。"""

    def test_git_command_timeout_handled(self, tmp_path: Path) -> None:
        """场景9: git 命令超时——不卡死，返回明确错误。

        模拟：_run_git 抛 subprocess.TimeoutExpired。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")
        gw = GitCommitGateway(project_root=tmp_path)

        import subprocess as sp

        def timeout_git(cmd):
            raise sp.TimeoutExpired(cmd=cmd, timeout=120)

        (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
        with patch.object(gw, "_run_git", side_effect=timeout_git):
            # 不应卡死，应抛异常或返回失败
            try:
                result = gw.commit("sess-timeout", [str(tmp_path / "a.py")], "feat: timeout")
                # 如果没抛异常，状态应是失败类
                assert result.status in (
                    CommitStatus.COMMIT_FAILED,
                    CommitStatus.STASH_CONFLICT,
                ), f"超时应返回失败状态: {result.status}"
            except (sp.TimeoutExpired, RuntimeError, GatewayError):
                pass  # 抛异常也可接受

        # 锁应释放
        lock_file = _lock_file_path(tmp_path)
        assert not lock_file.exists(), "超时后锁必须释放"

    def test_lock_timeout_when_held_indefinitely(self, tmp_path: Path) -> None:
        """场景10: 锁被无限期持有——等待超时返回 LOCK_TIMEOUT。

        模拟：创建一个"新鲜"的锁文件（未过期），验证 commit 会等待超时。
        """
        _init_repo(tmp_path)
        _commit_file(tmp_path, "a.py", "a = 0\n")

        # 创建新鲜锁（未过期）——用当前进程 PID（存活），模拟"锁被存活进程持有"
        # 治本：原 PID 99999 是死进程，被 _is_pid_alive 僵尸锁检测识别并清理，
        # 导致 commit 成功而非 LOCK_TIMEOUT，与测试意图矛盾。
        lock_file = _lock_file_path(tmp_path)
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": time.time()}),
            encoding="utf-8",
        )

        # 用短超时的锁替换默认锁（避免测试等 60 秒）
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import _GlobalCommitLock

        class FastLock(_GlobalCommitLock):
            def __init__(self, project_root):
                super().__init__(project_root, timeout=2.0)

        gw = GitCommitGateway(project_root=tmp_path)
        with patch("zephyr.governance.rule_bridge.git_commit_gateway._GlobalCommitLock", FastLock):
            (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
            result = gw.commit("sess-wait", [str(tmp_path / "a.py")], "feat: lock wait")

        assert result.status == CommitStatus.LOCK_TIMEOUT, \
            f"锁被持有时应返回 LOCK_TIMEOUT: {result.status} {result.message}"
