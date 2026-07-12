# [BLUEPRINT] MOD-INF-005 | tests/test_git_commit_concurrent.py | §ghost-commit-red-blue
# [MODULE] tests.test_git_commit_concurrent
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 红蓝对抗测试——模拟2 session并发commit，验证无幽灵提交；测试隔离用tmp_path临时git仓库
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] task_bound
"""test_git_commit_concurrent.py — 幽灵提交红蓝对抗测试（OPS-2026062514）

用 ThreadPoolExecutor 模拟 2 session 并发 commit，验证 GitCommitGateway 串行化+stash隔离
根治幽灵提交（本 session 修改被并发 session 的 commit 一并提交）。

测试场景:
  (a) A 提交 file_X + B 提交 file_Y 并发 → 各自只含自己的文件
  (b) A 有未暂存修改 + B commit → B 不捡拾 A 的未暂存修改
  (c) 交错提交：A stage file_X → B stage file_Y → A commit → B commit

断言: 每个 commit 只含本 session 的 files_in_scope，无跨 session 捡拾。

对标: STORM（arXiv 2605.20563）写时一致性测试方法论。
"""

from __future__ import annotations

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GitCommitGateway,
)


def _init_git_repo(repo_dir: Path) -> None:
    """初始化临时 git 仓库。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _commit_file(repo_dir: Path, rel_path: str, content: str, msg: str = "init") -> None:
    """提交一个文件到仓库（用于初始化已跟踪文件）。"""
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    env = {**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com"}
    subprocess.run(["git", "add", rel_path], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "commit", "-m", msg, "--no-verify"], cwd=str(repo_dir), capture_output=True, env=env, check=True)


def _commit_files_in_hash(repo_dir: Path, commit_hash: str) -> list[str]:
    """获取指定 commit 修改的文件列表。"""
    r = subprocess.run(
        ["git", "show", "--name-only", "--format=", commit_hash],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


def _git_log_hashes(repo_dir: Path, count: int = 5) -> list[str]:
    """获取最近 N 个 commit hash（最新在前）。"""
    r = subprocess.run(
        ["git", "log", f"-{count}", "--format=%H"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# 场景 (a): A 提交 file_X + B 提交 file_Y 并发
# ---------------------------------------------------------------------------
class TestConcurrentCommitDifferentFiles:
    """场景 (a): 两个 session 并发提交不同文件，互不捡拾。"""

    def test_concurrent_commit_no_cross_pickup(self, tmp_path: Path) -> None:
        """A commit file_X + B commit file_Y 并发 → 各自只含自己的文件。"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "file_x.py", "x = 0\n", "init x")
        _commit_file(tmp_path, "file_y.py", "y = 0\n", "init y")

        # 两个 session 同时修改各自的文件
        (tmp_path / "file_x.py").write_text("x = 100\n", encoding="utf-8")
        (tmp_path / "file_y.py").write_text("y = 200\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)

        def commit_session(session_id: str, file_rel: str) -> tuple[str, CommitStatus, str]:
            f = str((tmp_path / file_rel).resolve())
            result = gw.commit(
                session_id=session_id,
                files=[f],
                message=f"feat: update {file_rel} by {session_id}",
            )
            return (session_id, result.status, result.commit_hash)

        # 并发提交
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(commit_session, "sess-A", "file_x.py"),
                executor.submit(commit_session, "sess-B", "file_y.py"),
            ]
            results = {f.result()[0]: f.result() for f in as_completed(futures)}

        # 断言: 两个 commit 都成功
        assert results["sess-A"][1] == CommitStatus.OK, f"sess-A commit 失败: {results['sess-A']}"
        assert results["sess-B"][1] == CommitStatus.OK, f"sess-B commit 失败: {results['sess-B']}"

        # 获取两个 commit 的文件列表
        hashes = _git_log_hashes(tmp_path, count=3)  # [A_or_B, B_or_A, init_y]
        commit_a_hash = results["sess-A"][2]
        commit_b_hash = results["sess-B"][2]

        files_a = _commit_files_in_hash(tmp_path, commit_a_hash)
        files_b = _commit_files_in_hash(tmp_path, commit_b_hash)

        # 核心断言: 无跨 session 捡拾（幽灵提交防护）
        assert "file_x.py" in files_a, f"sess-A 应含 file_x.py: {files_a}"
        assert "file_y.py" not in files_a, f"sess-A 不应捡拾 file_y.py（幽灵提交！）: {files_a}"
        assert "file_y.py" in files_b, f"sess-B 应含 file_y.py: {files_b}"
        assert "file_x.py" not in files_b, f"sess-B 不应捡拾 file_x.py（幽灵提交！）: {files_b}"


# ---------------------------------------------------------------------------
# 场景 (b): A 有未暂存修改 + B commit
# ---------------------------------------------------------------------------
class TestUnstagedChangesNotPickedUp:
    """场景 (b): A 的未暂存修改不被 B 的 commit 捡拾。"""

    def test_unstaged_changes_preserved(self, tmp_path: Path) -> None:
        """A 有未暂存修改 + B commit → B 不捡拾 A 的修改，A 的修改不丢失。"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "file_a.py", "a = 0\n", "init a")
        _commit_file(tmp_path, "file_b.py", "b = 0\n", "init b")

        # A 修改 file_a.py（未暂存）
        (tmp_path / "file_a.py").write_text("a = 999\n", encoding="utf-8")
        # B 修改 file_b.py（本次 commit）
        (tmp_path / "file_b.py").write_text("b = 888\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="sess-B",
            files=[str((tmp_path / "file_b.py").resolve())],
            message="feat: B updates file_b",
        )
        assert result.status == CommitStatus.OK, f"B commit 应成功: {result.message}"

        # B 的 commit 只含 file_b.py
        files_b = _commit_files_in_hash(tmp_path, result.commit_hash)
        assert "file_b.py" in files_b
        assert "file_a.py" not in files_b, "B 不应捡拾 A 的未暂存修改（幽灵提交！）"

        # A 的未暂存修改应保留（stash pop 恢复）
        assert (tmp_path / "file_a.py").read_text(encoding="utf-8") == "a = 999\n", \
            "A 的未暂存修改应保留"


# ---------------------------------------------------------------------------
# 场景 (c): 交错提交
# ---------------------------------------------------------------------------
class TestInterleavedCommit:
    """场景 (c): 交错提交——A stage → B stage → A commit → B commit。"""

    def test_interleaved_staged_files_not_cross_committed(self, tmp_path: Path) -> None:
        """A stage file_X → B stage file_Y → A commit → B commit → 各自只含自己的文件。"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "file_x.py", "x = 0\n", "init x")
        _commit_file(tmp_path, "file_y.py", "y = 0\n", "init y")

        # A 修改并 stage file_x
        (tmp_path / "file_x.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "file_x.py"], cwd=str(tmp_path), capture_output=True)

        # B 修改并 stage file_y
        (tmp_path / "file_y.py").write_text("y = 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "file_y.py"], cwd=str(tmp_path), capture_output=True)

        gw = GitCommitGateway(project_root=tmp_path)

        # A commit（只提交 file_x）
        result_a = gw.commit(
            session_id="sess-A",
            files=[str((tmp_path / "file_x.py").resolve())],
            message="feat: A updates file_x",
        )
        assert result_a.status == CommitStatus.OK, f"A commit 应成功: {result_a.message}"

        # B commit（只提交 file_y）
        result_b = gw.commit(
            session_id="sess-B",
            files=[str((tmp_path / "file_y.py").resolve())],
            message="feat: B updates file_y",
        )
        assert result_b.status == CommitStatus.OK, f"B commit 应成功: {result_b.message}"

        # 断言: A 的 commit 只含 file_x，B 的 commit 只含 file_y
        files_a = _commit_files_in_hash(tmp_path, result_a.commit_hash)
        files_b = _commit_files_in_hash(tmp_path, result_b.commit_hash)

        assert "file_x.py" in files_a, f"A 应含 file_x: {files_a}"
        assert "file_y.py" not in files_a, f"A 不应捡拾 B staged 的 file_y（幽灵提交！）: {files_a}"
        assert "file_y.py" in files_b, f"B 应含 file_y: {files_b}"
        assert "file_x.py" not in files_b, f"B 不应捡拾 A 已 commit 的 file_x: {files_b}"


# ---------------------------------------------------------------------------
# 场景 (d): 并发同一文件（冲突场景）
# ---------------------------------------------------------------------------
class TestConcurrentSameFile:
    """场景 (d): 两个 session 并发修改同一文件——串行化后不丢数据。"""

    def test_concurrent_same_file_serialized(self, tmp_path: Path) -> None:
        """A + B 并发修改同一文件 → 串行化 commit，不丢数据。"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "shared.py", "v = 0\n", "init shared")

        gw = GitCommitGateway(project_root=tmp_path)

        def commit_version(session_id: str, new_content: str) -> tuple[str, CommitStatus]:
            f = tmp_path / "shared.py"
            f.write_text(new_content, encoding="utf-8")
            result = gw.commit(
                session_id=session_id,
                files=[str(f.resolve())],
                message=f"feat: {session_id} updates shared",
            )
            return (session_id, result.status)

        # 并发提交（串行锁保证一次只一个）
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(commit_version, "sess-A", "v = 1\n"),
                executor.submit(commit_version, "sess-B", "v = 2\n"),
            ]
            results = [f.result() for f in as_completed(futures)]

        # 至少一个成功（串行化后可能两个都成功，或第二个 NOTHING_TO_COMMIT）
        ok_count = sum(1 for _, status in results if status == CommitStatus.OK)
        assert ok_count >= 1, f"至少一个 commit 应成功: {results}"

        # 文件内容应为某个 session 的修改（不丢数据）
        content = (tmp_path / "shared.py").read_text(encoding="utf-8")
        assert content in ("v = 1\n", "v = 2\n"), f"文件内容应为某 session 修改: {content!r}"
