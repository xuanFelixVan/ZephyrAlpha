# [A_test] test_id=DM-202919 | module=scripts/lock_files.py | gate=pytest
# [BLUEPRINT] MOD-INF-005 | scripts/lock_files.py | §
# [TESTS] tests/test_lock_release_uncommitted.py
# [TTL] task_bound
"""DM-202919 验收测试: lock_files.py release 加 git status 警告.

验证场景:
1. 文件有未提交修改时，release 打印 WARNING
2. 文件无未提交修改时，release 不打印 WARNING
3. 文件不存在时，release 不崩溃
4. 非 git 仓库文件，release 不崩溃
5. cmd_release_all 也检查未提交修改
6. WARNING 不阻止释放（锁仍被释放）
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pytest

# 确保 scripts/ 在 sys.path（ARCH-029 迁移 tests/→tests/git/，需 3 级 parent）
SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lock_files  # noqa: E402


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """创建临时 git 仓库用于测试."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    return repo


@pytest.fixture
def committed_file(temp_git_repo: Path) -> Path:
    """创建一个已提交的文件."""
    f = temp_git_repo / "committed.txt"
    f.write_text("initial content", encoding="utf-8")
    subprocess.run(["git", "add", "committed.txt"], cwd=str(temp_git_repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(temp_git_repo), capture_output=True, check=True)
    return f


@pytest.fixture
def modified_file(temp_git_repo: Path) -> Path:
    """创建一个已提交但有未提交修改的文件."""
    f = temp_git_repo / "modified.txt"
    f.write_text("initial content", encoding="utf-8")
    subprocess.run(["git", "add", "modified.txt"], cwd=str(temp_git_repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(temp_git_repo), capture_output=True, check=True)
    # 制造未提交修改
    f.write_text("modified content", encoding="utf-8")
    return f


@pytest.fixture
def staged_file(temp_git_repo: Path) -> Path:
    """创建一个已暂存未提交的文件."""
    f = temp_git_repo / "staged.txt"
    f.write_text("initial content", encoding="utf-8")
    subprocess.run(["git", "add", "staged.txt"], cwd=str(temp_git_repo), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(temp_git_repo), capture_output=True, check=True)
    # 制造已暂存修改
    f.write_text("staged content", encoding="utf-8")
    subprocess.run(["git", "add", "staged.txt"], cwd=str(temp_git_repo), capture_output=True, check=True)
    return f


@pytest.fixture
def untracked_file(temp_git_repo: Path) -> Path:
    """创建一个未跟踪的文件."""
    f = temp_git_repo / "untracked.txt"
    f.write_text("untracked content", encoding="utf-8")
    return f


class TestWarnIfUncommitted:
    """测试 _warn_if_uncommitted 辅助函数."""

    def test_warns_on_modified_file(self, modified_file: Path):
        """文件有未提交修改时打印 WARNING."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            lock_files.warn_if_uncommitted(str(modified_file))
        output = buf.getvalue()
        assert "WARNING" in output, f"期望 WARNING，实际: {output!r}"
        assert "未提交修改" in output
        assert str(modified_file) in output or modified_file.name in output

    def test_no_warn_on_committed_file(self, committed_file: Path):
        """文件无未提交修改时不打印 WARNING."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            lock_files.warn_if_uncommitted(str(committed_file))
        output = buf.getvalue()
        assert "WARNING" not in output, f"不期望 WARNING，实际: {output!r}"

    def test_warns_on_staged_file(self, staged_file: Path):
        """文件已暂存未提交时打印 WARNING."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            lock_files.warn_if_uncommitted(str(staged_file))
        output = buf.getvalue()
        assert "WARNING" in output, f"期望 WARNING，实际: {output!r}"

    def test_warns_on_untracked_file(self, untracked_file: Path):
        """未跟踪文件打印 WARNING."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            lock_files.warn_if_uncommitted(str(untracked_file))
        output = buf.getvalue()
        assert "WARNING" in output, f"期望 WARNING，实际: {output!r}"

    def test_no_crash_on_nonexistent_file(self, tmp_path: Path):
        """文件不存在时不崩溃."""
        nonexistent = tmp_path / "nonexistent.txt"
        buf = io.StringIO()
        with redirect_stdout(buf):
            lock_files.warn_if_uncommitted(str(nonexistent))
        output = buf.getvalue()
        assert "WARNING" not in output

    def test_no_crash_on_non_git_file(self, tmp_path: Path, monkeypatch):
        """非 git 仓库文件不崩溃."""
        f = tmp_path / "nogit.txt"
        f.write_text("content", encoding="utf-8")

        # 模拟非 git 仓库环境：git status 返回非零退出码
        # （真实非 git 目录中 git status 会失败；测试 tmp_path 可能在
        # ZephyrAlpha repo 内导致 git status 成功，故 mock 确保测试隔离）
        class _FakeResult:
            returncode = 128  # git 在非 git 目录的退出码
            stdout = ""
            stderr = "fatal: not a git repository"

        monkeypatch.setattr("subprocess.run", lambda *a, **kw: _FakeResult())

        buf = io.StringIO()
        with redirect_stdout(buf):
            lock_files.warn_if_uncommitted(str(f))
        output = buf.getvalue()
        # 非 git 仓库应静默跳过
        assert "WARNING" not in output


class TestCmdReleaseWarning:
    """测试 cmd_release 集成 WARNING."""

    def test_release_warns_on_uncommitted(self, modified_file: Path, monkeypatch):
        """cmd_release 释放有未提交修改的文件时打印 WARNING，但锁仍释放."""
        # 指向临时仓库的 .ailocks 目录
        repo_dir = modified_file.parent
        monkeypatch.setattr(lock_files, "LOCK_ROOT", repo_dir / ".ailocks")
        monkeypatch.setattr(lock_files, "REGISTRY_PATH", repo_dir / ".ailocks" / "registry.json")
        lock_files.ensure_lock_root()

        # 使用绝对路径（_warn_if_uncommitted 需要绝对路径才能定位 git 仓库）
        abs_path = str(modified_file)
        rc = lock_files.cmd_acquire(abs_path, "test-session", "test task")
        assert rc == 0

        # 释放锁，捕获输出
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lock_files.cmd_release(abs_path, "test-session")
        output = buf.getvalue()

        assert rc == 0, f"release 应成功，rc={rc}, output={output}"
        assert "RELEASED" in output, f"应打印 RELEASED，实际: {output!r}"
        assert "WARNING" in output, f"应打印 WARNING，实际: {output!r}"

    def test_release_no_warn_on_committed(self, committed_file: Path, monkeypatch):
        """cmd_release 释放已提交文件时不打印 WARNING."""
        repo_dir = committed_file.parent
        monkeypatch.setattr(lock_files, "LOCK_ROOT", repo_dir / ".ailocks")
        monkeypatch.setattr(lock_files, "REGISTRY_PATH", repo_dir / ".ailocks" / "registry.json")
        lock_files.ensure_lock_root()

        abs_path = str(committed_file)
        rc = lock_files.cmd_acquire(abs_path, "test-session", "test task")
        assert rc == 0

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lock_files.cmd_release(abs_path, "test-session")
        output = buf.getvalue()

        assert rc == 0
        assert "RELEASED" in output
        assert "WARNING" not in output, f"不期望 WARNING，实际: {output!r}"

    def test_release_still_releases_on_warning(self, modified_file: Path, monkeypatch):
        """WARNING 不阻止释放——锁仍被释放，可被其他 session 获取."""
        repo_dir = modified_file.parent
        monkeypatch.setattr(lock_files, "LOCK_ROOT", repo_dir / ".ailocks")
        monkeypatch.setattr(lock_files, "REGISTRY_PATH", repo_dir / ".ailocks" / "registry.json")
        lock_files.ensure_lock_root()

        abs_path = str(modified_file)
        lock_files.cmd_acquire(abs_path, "session-a", "task a")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lock_files.cmd_release(abs_path, "session-a")
        assert rc == 0

        # 验证锁已释放：另一个 session 可以获取
        rc2 = lock_files.cmd_acquire(abs_path, "session-b", "task b")
        assert rc2 == 0, "WARNING 不应阻止释放，另一个 session 应能获取锁"


class TestCmdReleaseAllWarning:
    """测试 cmd_release_all 集成 WARNING（治根：批量释放也检查）."""

    def test_release_all_warns_on_uncommitted(self, modified_file: Path, committed_file: Path, monkeypatch):
        """cmd_release_all 释放多个文件时，对有未提交修改的打印 WARNING."""
        repo_dir = modified_file.parent
        monkeypatch.setattr(lock_files, "LOCK_ROOT", repo_dir / ".ailocks")
        monkeypatch.setattr(lock_files, "REGISTRY_PATH", repo_dir / ".ailocks" / "registry.json")
        lock_files.ensure_lock_root()

        # 使用绝对路径
        lock_files.cmd_acquire(str(modified_file), "test-session", "task")
        lock_files.cmd_acquire(str(committed_file), "test-session", "task")

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = lock_files.cmd_release_all("test-session")
        output = buf.getvalue()

        assert rc == 0
        assert "RELEASED" in output
        # modified_file 应有 WARNING，committed_file 不应有
        assert "WARNING" in output, f"应对 modified_file 打印 WARNING，实际: {output!r}"
