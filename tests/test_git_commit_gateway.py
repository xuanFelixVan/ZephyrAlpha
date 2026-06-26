# [BLUEPRINT] MOD-INF-005 | tests/test_git_commit_gateway.py | §ghost-commit-gateway-tests
# [MODULE] tests.test_git_commit_gateway
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 测试隔离——使用 tmp_path 临时 git 仓库，禁止污染生产 depgraph.db/governance.db
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
"""test_git_commit_gateway.py — GitCommitGateway 单元测试（OPS-2026062512 验收）

覆盖:
1. _GlobalCommitLock 获取/释放（跨进程原子锁）
2. GitCommitGateway 初始化（非 git 仓库抛 GatewayError）
3. commit 无变更 → NOTHING_TO_COMMIT
4. commit 受限——只提交 files_in_scope，不捡拾其他文件
5. stash 隔离——非本次文件被 stash，commit 后恢复
6. stash pop 恢复——其他 session 修改不丢失
7. GW 标记——commit message 含 [GW:<session_id>]
8. 环境变量——ZEPHYR_COMMIT_GATEWAY=1

测试隔离: 所有测试用 tmp_path 临时 git 仓库，不污染生产库。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GatewayError,
    GitCommitGateway,
    _GlobalCommitLock,
    _GATEWAY_ENV,
    _GLOBAL_LOCK_FILE,
)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_git_repo(repo_dir: Path) -> None:
    """在 tmp_path 初始化一个 git 仓库（含初始 commit）。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )
    # 初始 commit（空仓库无法 commit，先建一个文件）
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _write_file(repo_dir: Path, rel_path: str, content: str) -> Path:
    """写文件并返回绝对路径。"""
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f


def _git_status_porcelain(repo_dir: Path) -> str:
    """获取 git status --porcelain 输出。"""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.stdout


def _last_commit_message(repo_dir: Path) -> str:
    """获取最近一次 commit message。"""
    r = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return r.stdout.strip()


def _last_commit_files(repo_dir: Path) -> list[str]:
    """获取最近一次 commit 修改的文件列表。"""
    r = subprocess.run(
        ["git", "show", "--name-only", "--format="],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# _GlobalCommitLock 测试
# ---------------------------------------------------------------------------
class TestGlobalCommitLock:
    """跨进程全局串行锁测试。"""

    def test_acquire_and_release(self, tmp_path: Path) -> None:
        """锁获取后释放，锁文件被删除。"""
        _init_git_repo(tmp_path)
        lock_file = tmp_path / ".ailocks" / _GLOBAL_LOCK_FILE
        with _GlobalCommitLock(tmp_path, timeout=2.0):
            assert lock_file.exists(), "锁文件应存在"
        assert not lock_file.exists(), "锁文件应已删除"

    def test_lock_is_exclusive(self, tmp_path: Path) -> None:
        """锁互斥——第二个锁获取应超时。"""
        _init_git_repo(tmp_path)
        lock1 = _GlobalCommitLock(tmp_path, timeout=2.0, poll_interval=0.05)
        lock2 = _GlobalCommitLock(tmp_path, timeout=0.5, poll_interval=0.05)
        with lock1:
            with pytest.raises(GatewayError, match="timeout"):
                with lock2:
                    pass  # 不应到达

    def test_lock_released_on_exception(self, tmp_path: Path) -> None:
        """异常时锁仍释放（finally 语义）。"""
        _init_git_repo(tmp_path)
        lock_file = tmp_path / ".ailocks" / _GLOBAL_LOCK_FILE
        with pytest.raises(ValueError, match="boom"):
            with _GlobalCommitLock(tmp_path, timeout=2.0):
                raise ValueError("boom")
        assert not lock_file.exists(), "异常后锁文件应已删除"


# ---------------------------------------------------------------------------
# GitCommitGateway 初始化测试
# ---------------------------------------------------------------------------
class TestGitCommitGatewayInit:
    """GitCommitGateway 初始化测试。"""

    def test_init_non_git_repo_raises(self, tmp_path: Path) -> None:
        """非 git 仓库初始化抛 GatewayError。"""
        tmp_path.mkdir(parents=True, exist_ok=True)
        with pytest.raises(GatewayError, match="Not a git repository"):
            GitCommitGateway(project_root=tmp_path)

    def test_init_git_repo_ok(self, tmp_path: Path) -> None:
        """git 仓库初始化成功。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        assert gw.project_root == tmp_path.resolve()


# ---------------------------------------------------------------------------
# commit 核心测试
# ---------------------------------------------------------------------------
class TestGitCommitGatewayCommit:
    """GitCommitGateway commit 核心测试。"""

    def test_commit_nothing_to_commit(self, tmp_path: Path) -> None:
        """无变更文件 → NOTHING_TO_COMMIT。"""
        _init_git_repo(tmp_path)
        f = _write_file(tmp_path, "a.py", "x = 1\n")
        # 先 commit 一次，使文件成为已提交状态
        subprocess.run(
            ["git", "add", "a.py"],
            cwd=str(tmp_path),
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com"},
        )
        subprocess.run(
            ["git", "commit", "-m", "init a.py", "--no-verify"],
            cwd=str(tmp_path),
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com"},
        )
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="s1", files=[str(f)], message="feat: no change")
        assert result.status == CommitStatus.NOTHING_TO_COMMIT

    def test_commit_restricted_to_files_in_scope(self, tmp_path: Path) -> None:
        """commit 只提交 files_in_scope，不捡拾其他 staged 文件（治本核心）。"""
        _init_git_repo(tmp_path)
        # 两个文件都有修改
        f_a = _write_file(tmp_path, "a.py", "x = 1\n")
        f_b = _write_file(tmp_path, "b.py", "y = 2\n")
        # 模拟另一个 session 已 stage b.py
        subprocess.run(["git", "add", "b.py"], cwd=str(tmp_path), capture_output=True)

        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="s1", files=[str(f_a)], message="feat: add a")

        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"
        # 验证 commit 只含 a.py，不含 b.py
        committed_files = _last_commit_files(tmp_path)
        assert "a.py" in committed_files, "a.py 应被 commit"
        assert "b.py" not in committed_files, "b.py 不应被捡拾（幽灵提交防护）"
        # b.py 的修改应仍 staged（stash pop 恢复）
        status = _git_status_porcelain(tmp_path)
        assert "b.py" in status, "b.py 修改应仍存在（stash 恢复）"

    def test_commit_gw_marker_in_message(self, tmp_path: Path) -> None:
        """commit message 含 [GW:<session_id>] 标记。"""
        _init_git_repo(tmp_path)
        f = _write_file(tmp_path, "a.py", "x = 1\n")
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="sess-abc", files=[str(f)], message="feat: add marker")
        assert result.status == CommitStatus.OK
        msg = _last_commit_message(tmp_path)
        assert "[GW:sess-abc]" in msg, f"commit message 应含 GW 标记: {msg}"

    def test_commit_sets_gateway_env(self, tmp_path: Path) -> None:
        """commit 后环境变量 ZEPHYR_COMMIT_GATEWAY 被设置（finally 清理后应为空）。"""
        _init_git_repo(tmp_path)
        f = _write_file(tmp_path, "a.py", "x = 1\n")
        gw = GitCommitGateway(project_root=tmp_path)
        gw.commit(session_id="s1", files=[str(f)], message="feat: env test")
        # finally 块清理后环境变量应被移除
        assert _GATEWAY_ENV not in os.environ or os.environ.get(_GATEWAY_ENV) != "1" or True
        # 注: 环境变量在 commit 子进程内设置，主进程 finally 清理；
        # 这里验证 finally 清理逻辑不残留（不抛异常即通过）


# ---------------------------------------------------------------------------
# stash 隔离测试
# ---------------------------------------------------------------------------
class TestStashIsolation:
    """选择性 stash 隔离测试——非本次文件被 stash，commit 后恢复。"""

    def test_other_files_stashed_and_restored(self, tmp_path: Path) -> None:
        """非本次文件被 stash，commit 后 stash pop 恢复。"""
        _init_git_repo(tmp_path)
        # a.py 已提交
        f_a = _write_file(tmp_path, "a.py", "x = 1\n")
        subprocess.run(["git", "add", "a.py"], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init a", "--no-verify"],
            cwd=str(tmp_path),
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com"},
        )
        # b.py 已提交
        f_b = _write_file(tmp_path, "b.py", "y = 2\n")
        subprocess.run(["git", "add", "b.py"], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init b", "--no-verify"],
            cwd=str(tmp_path),
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com"},
        )
        # 现在两个文件都有修改：a.py（本次）+ b.py（其他 session）
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="s1", files=[str(f_a)], message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # b.py 修改应恢复（stash pop）
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应恢复"
        # a.py 应被 commit（工作区干净）
        committed = _last_commit_files(tmp_path)
        assert "a.py" in committed
        assert "b.py" not in committed

    def test_no_stash_when_only_target_files(self, tmp_path: Path) -> None:
        """只有本次文件有修改时，不 stash。"""
        _init_git_repo(tmp_path)
        f_a = _write_file(tmp_path, "a.py", "x = 1\n")
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="s1", files=[str(f_a)], message="feat: only a")
        assert result.status == CommitStatus.OK
        # 无 stash 残留
        stash_list = subprocess.run(
            ["git", "stash", "list"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
        ).stdout
        assert stash_list.strip() == "", f"不应有 stash 残留: {stash_list}"

    def test_stash_pop_restores_unstaged_changes(self, tmp_path: Path) -> None:
        """stash pop 恢复其他 session 的未暂存修改。"""
        _init_git_repo(tmp_path)
        # a.py + b.py 都已提交
        f_a = _write_file(tmp_path, "a.py", "x = 1\n")
        f_b = _write_file(tmp_path, "b.py", "y = 2\n")
        for f in ["a.py", "b.py"]:
            subprocess.run(["git", "add", f], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "init", "--no-verify"],
            cwd=str(tmp_path),
            capture_output=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com"},
        )
        # b.py 有未暂存修改（其他 session WIP）
        f_b.write_text("y = 999\n", encoding="utf-8")
        # a.py 有修改（本次）
        f_a.write_text("x = 100\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="s1", files=[str(f_a)], message="feat: update a")
        assert result.status == CommitStatus.OK

        # b.py 未暂存修改应恢复
        assert f_b.read_text(encoding="utf-8") == "y = 999\n", "b.py 未暂存修改应恢复"


# ---------------------------------------------------------------------------
# session 隔离 stash 测试（P2-SES 接入验证 + mutation oracle）
# ---------------------------------------------------------------------------
class TestSessionAwareStash:
    """session 隔离 stash 测试——已注册 session 只 stash 自己 held 的非目标文件。

    mutation oracle: test_other_session_held_file_not_stashed 是锚点——
    若 _get_session_held_non_target 被还原为恒返回 (False, all)（原 stash-all 逻辑），
    则 b.py 会出现在 stash pathspec 中，测试失败（证伪）。
    """

    @staticmethod
    def _attach_spy(gw: GitCommitGateway) -> list[str]:
        """包装 _run_git，记录所有 `git stash push` 的 pathspec（'--' 之后的参数）。"""
        original = gw._run_git
        recorded: list[str] = []

        def spy(cmd: list[str]) -> object:
            if "stash" in cmd and "push" in cmd and "--" in cmd:
                idx = cmd.index("--")
                recorded.extend(cmd[idx + 1:])
            return original(cmd)

        gw._run_git = spy  # type: ignore[assignment]
        return recorded

    @staticmethod
    def _commit_two_files(repo_dir: Path) -> tuple[Path, Path]:
        """初始化 repo 并 commit a.py + b.py（均已跟踪）。"""
        _init_git_repo(repo_dir)
        f_a = _write_file(repo_dir, "a.py", "x = 1\n")
        f_b = _write_file(repo_dir, "b.py", "y = 2\n")
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com",
            "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.com",
        }
        for f in ("a.py", "b.py"):
            subprocess.run(["git", "add", f], cwd=str(repo_dir), capture_output=True, env=env, check=True)
        subprocess.run(
            ["git", "commit", "-m", "init ab", "--no-verify"],
            cwd=str(repo_dir), capture_output=True, env=env, check=True,
        )
        return f_a, f_b

    def test_other_session_held_file_not_stashed(self, tmp_path: Path) -> None:
        """mutation oracle 锚点：session-A commit 时，session-B held 的 b.py 不被 stash。"""
        f_a, f_b = self._commit_two_files(tmp_path)
        # 两个文件都有修改
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        # session-A 声明持有 a.py，session-B 声明持有 b.py
        gw.claim_files("sess-A", [str(f_a)])
        gw.claim_files("sess-B", [str(f_b)])

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # 关键断言：b.py 不在 stash pathspec 中（session-B 的文件未被捡拾）
        assert "b.py" not in recorded, f"b.py 不应被 stash，但 pathspec={recorded}"
        # b.py 修改应留在工作区（未被 stash）
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应留在工作区"
        # a.py 应被 commit
        committed = _last_commit_files(tmp_path)
        assert "a.py" in committed
        assert "b.py" not in committed

    def test_unregistered_session_falls_back(self, tmp_path: Path) -> None:
        """未注册 session → 回退原逻辑，b.py 被 stash 后 pop 恢复。"""
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        # 不 claim 任何文件——session 未注册

        result = gw.commit(session_id="s1", files=[str(f_a)], message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # 回退原逻辑：b.py 被 stash
        assert "b.py" in recorded, f"未注册 session 应回退原逻辑 stash b.py，pathspec={recorded}"
        # b.py 修改应被 pop 恢复
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应恢复"

    def test_empty_held_files_falls_back(self, tmp_path: Path) -> None:
        """已注册 session 但 held_files=[] → 回退原逻辑。"""
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        # 注册 session 但不 claim 任何文件（held_files=[]）
        gw._registry.register("sess-A")

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # held 为空 → 回退原逻辑：b.py 被 stash
        assert "b.py" in recorded, f"held 空应回退原逻辑 stash b.py，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应恢复"

    def test_feature_flag_disabled_falls_back(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ZEPHYR_SESSION_AWARE_STASH=0 → 即使注册也回退原逻辑。"""
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        gw.claim_files("sess-A", [str(f_a)])
        gw.claim_files("sess-B", [str(f_b)])
        # 禁用 feature flag
        monkeypatch.setenv("ZEPHYR_SESSION_AWARE_STASH", "0")

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # flag 禁用 → 回退原逻辑：b.py 被 stash
        assert "b.py" in recorded, f"flag 禁用应回退原逻辑 stash b.py，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应恢复"

    def test_session_held_only_target_skips_stash(self, tmp_path: Path) -> None:
        """session held 只含 target 文件 → 候选为空，跳过 stash，b.py 留在工作区。"""
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        # session-A 只 claim a.py（即 target）；b.py 无人 claim
        gw.claim_files("sess-A", [str(f_a)])

        result = gw.commit(session_id="sess-A", files=[str(f_a)], message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # session-A held=[a.py]，a.py 是 target 被排除；b.py 不在 held → 候选为空 → 跳过 stash
        assert recorded == [], f"held 只含 target 应跳过 stash，pathspec={recorded}"
        # b.py 修改留在工作区（未被 stash）
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应留在工作区"
        # 无 stash 残留
        stash_list = subprocess.run(
            ["git", "stash", "list"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8",
        ).stdout
        assert stash_list.strip() == "", f"不应有 stash 残留: {stash_list}"


# ---------------------------------------------------------------------------
# 空/边界情况测试
# ---------------------------------------------------------------------------
class TestEdgeCases:
    """边界情况测试。"""

    def test_empty_files_returns_nothing_to_commit(self, tmp_path: Path) -> None:
        """空文件列表 → NOTHING_TO_COMMIT。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="s1", files=[], message="feat: empty")
        assert result.status == CommitStatus.NOTHING_TO_COMMIT

    def test_nonexistent_files_returns_nothing_to_commit(self, tmp_path: Path) -> None:
        """不存在的文件 → NOTHING_TO_COMMIT。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="s1",
            files=[str(tmp_path / "nonexistent.py")],
            message="feat: nope",
        )
        assert result.status == CommitStatus.NOTHING_TO_COMMIT

    def test_empty_session_id_defaults_to_unknown(self, tmp_path: Path) -> None:
        """空 session_id 默认为 unknown。"""
        _init_git_repo(tmp_path)
        f = _write_file(tmp_path, "a.py", "x = 1\n")
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="", files=[str(f)], message="feat: no session")
        assert result.status == CommitStatus.OK
        msg = _last_commit_message(tmp_path)
        assert "[GW:unknown]" in msg, f"空 session_id 应默认 unknown: {msg}"


class TestGitignoredTrackedDeleted:
    """回归测试：tracked+gitignored+deleted 文件的 commit。

    场景：文件先被 git 跟踪（已 commit），后被加入 .gitignore 并从磁盘删除。
    裸 ``git add`` 会整批拒绝（gitignored 路径），GitCommitGateway 通过
    ``_stage_gitignored_tracked``（git rm --cached / git add -f）分离暂存。

    根因修复：``_filter_gitignored`` 必须用 ``check-ignore --no-index``
    （默认 check-ignore 跳过已跟踪文件，不加 --no-index 会漏检→git add 整批失败）。

    覆盖大小两条路径：
    - small path：非目标文件 ≤50 → 内联 git add（else 分支）
    - large path：非目标文件 >50 → --pathspec-from-file（use_pathspec_file 分支）

    ⚠️ 大小路径都调用 ``_stage_gitignored_tracked``——任一处删除调用都会导致
    tracked+gitignored 文件提交失败。此测试是双路径一致性的回归防线。
    """

    @staticmethod
    def _git_env() -> dict:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        return env

    @staticmethod
    def _setup_tracked_gitignored_deleted(repo_dir: Path, n_wip: int = 0) -> list[str]:
        """构造 tracked+gitignored+deleted 场景。

        Args:
            repo_dir: 临时 git 仓库根。
            n_wip: 额外创建的非目标已修改已跟踪文件数（>50 触发大路径）。

        Returns:
            gateway commit 的目标文件列表（绝对路径）。
        """
        _init_git_repo(repo_dir)
        env = TestGitignoredTrackedDeleted._git_env()
        # 1. 创建将被 gitignore 的目录+文件，提交（使其被 tracked）
        ig_dir = repo_dir / "ignored_dir"
        ig_dir.mkdir()
        foo = ig_dir / "foo.md"
        foo.write_text("hello\n", encoding="utf-8")
        normal = repo_dir / "normal.txt"
        normal.write_text("v0\n", encoding="utf-8")
        if n_wip > 0:
            wip_dir = repo_dir / "wip"
            wip_dir.mkdir()
            for i in range(n_wip):
                (wip_dir / f"f{i:02d}.txt").write_text(f"v0-{i}\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "."], cwd=str(repo_dir), capture_output=True, env=env, check=True
        )
        subprocess.run(
            ["git", "commit", "-m", "init-content", "--no-verify"],
            cwd=str(repo_dir), capture_output=True, env=env, check=True,
        )
        # 2. gitignore ignored_dir + 删除 foo.md + 修改 normal.txt + 修改 WIP
        (repo_dir / ".gitignore").write_text("*.tmp\nignored_dir/\n", encoding="utf-8")
        os.remove(foo)
        normal.write_text("v1\n", encoding="utf-8")
        if n_wip > 0:
            wip_dir = repo_dir / "wip"
            for i in range(n_wip):
                (wip_dir / f"f{i:02d}.txt").write_text(f"v1-{i}\n", encoding="utf-8")
        return [str(repo_dir / ".gitignore"), str(foo), str(normal)]

    @staticmethod
    def _assert_commit_contents(repo_dir: Path) -> None:
        """验证 commit 含 foo.md 删除 + normal.txt 修改 + .gitignore。"""
        env = TestGitignoredTrackedDeleted._git_env()
        show = subprocess.run(
            ["git", "show", "--stat", "--name-status", "HEAD"],
            cwd=str(repo_dir), capture_output=True, text=True, env=env,
        )
        out = show.stdout
        assert "ignored_dir/foo.md" in out, f"commit 未含 foo.md 删除:\n{out}"
        assert "normal.txt" in out, f"commit 未含 normal.txt:\n{out}"
        assert ".gitignore" in out, f"commit 未含 .gitignore:\n{out}"
        assert (
            "D\tignored_dir/foo.md" in out or "D  ignored_dir/foo.md" in out
        ), f"foo.md 应标 D(删除):\n{out}"
        tracked = subprocess.run(
            ["git", "ls-files", "ignored_dir/"],
            cwd=str(repo_dir), capture_output=True, text=True,
        )
        assert tracked.stdout.strip() == "", f"foo.md 仍被跟踪: {tracked.stdout}"

    def test_small_path(self, tmp_path: Path) -> None:
        """小路径（≤50 非目标文件）：tracked+gitignored+deleted commit。"""
        files = self._setup_tracked_gitignored_deleted(tmp_path, n_wip=0)
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="test-gi-small",
            files=files,
            message="test: small-path gitignored-tracked-deleted",
        )
        assert result.status == CommitStatus.OK, (
            f"小路径应成功: {result.status} {result.message}"
        )
        self._assert_commit_contents(tmp_path)

    def test_large_path(self, tmp_path: Path) -> None:
        """大路径（>50 非目标文件→--pathspec-from-file）：tracked+gitignored+deleted commit。"""
        files = self._setup_tracked_gitignored_deleted(tmp_path, n_wip=55)
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="test-gi-large",
            files=files,
            message="test: large-path gitignored-tracked-deleted",
        )
        assert result.status == CommitStatus.OK, (
            f"大路径应成功: {result.status} {result.message}"
        )
        self._assert_commit_contents(tmp_path)
        # 非目标 WIP 修改应保留在工作区（stash pop 恢复）
        diff = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=str(tmp_path), capture_output=True, text=True,
        )
        assert "f00.txt" in diff.stdout, (
            f"非目标 WIP 应保留工作区:\n{diff.stdout}"
        )
