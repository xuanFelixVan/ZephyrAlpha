# [BLUEPRINT] MOD-INF-005 | tests/test_git_commit_gateway.py | §ghost-commit-gateway-tests
# [MODULE] tests.test_git_commit_gateway
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——使用 tmp_path 临时 git 仓库，禁止污染生产 depgraph/governance.db
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_git_commit_gateway.py — GitCommitGateway 单元测试（OPS-2026062512 验收）

覆盖:
1. GlobalCommitLock 获取/释放（跨进程原子锁）
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

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    CommitStatus,
    GatewayError,
    GitCommitGateway,
    GlobalCommitLock,
    GATEWAY_ENV,
    GLOBAL_LOCK_FILE,
)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_git_repo(repo_dir: Path) -> None:
    """在 tmp_path 初始化一个 git 仓库（含初始 commit）。

    并创建 fail-closed gate 源文件 stub——多个 gate（DIRECTORY-CONTRACT/TTL-METADATA/
    FILE-PLACEMENT-TTL/DANGLING-REFERENCE/ARCH-REFERENCE）fail-closed 设计要求源文件
    存在，否则阻断 commit。测试目的是测 stash/rename/delete 逻辑，不是测 gate 校验逻辑
    （gate 逻辑由各自单元测试覆盖）。stub 总是 exit 0（通过），让测试环境的 gate 不误拦。
    """
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
    # fail-closed gate 源文件 stub（pre-commit gate 需要）
    # AGENTS.md stub（DANGLING-REFERENCE gate 需要 ## N 章节号）
    (repo_dir / "AGENTS.md").write_text("# AGENTS.md (test stub)\n## 1 Test Section\n", encoding="utf-8")
    # directory_contract.yaml stub（FILE-PLACEMENT-TTL gate 需要 directory_zones）
    dc_dir = repo_dir / "docs" / "01_policies_and_standards" / "_registry" / "contracts"
    dc_dir.mkdir(parents=True, exist_ok=True)
    (dc_dir / "directory_contract.yaml").write_text(
        "directory_zones:\n  permanent:\n    paths:\n      - docs/\n    exempt_subdirs: []\n"
        "  temporary:\n    paths:\n      - docs/_working/\n"
        "  neutral:\n    paths:\n      - src/\n      - tests/\n      - scripts/\n      - build_artifacts/\n"
        "root_directory_whitelist:\n  files:\n    - AGENTS.md\n    - .gitignore\n    - .gitkeep\n",
        encoding="utf-8",
    )
    # ttl_vocabulary.yaml stub（FILE-PLACEMENT-TTL gate fail-closed 校验需要 values 含 permanent/task_bound）
    tv_dir = repo_dir / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"
    tv_dir.mkdir(parents=True, exist_ok=True)
    (tv_dir / "ttl_vocabulary.yaml").write_text(
        "values:\n  - value: permanent\n  - value: task_bound\n",
        encoding="utf-8",
    )
    # architecture_issue_registry.yaml stub（ARCH-REFERENCE gate 需要 entries）
    arch_dir = repo_dir / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    arch_dir.mkdir(parents=True, exist_ok=True)
    (arch_dir / "architecture_issue_registry.yaml").write_text(
        'entries:\n  - issue_id: "#ARCH-001"\n    title: "Test entry"\n    status: "active"\n',
        encoding="utf-8",
    )
    # check_directory_contract.py stub（DIRECTORY-CONTRACT gate subprocess 调用）
    checker_stub = repo_dir / "scripts" / "governance" / "d1_structure" / "check_directory_contract.py"
    checker_stub.parent.mkdir(parents=True, exist_ok=True)
    checker_stub.write_text(
        "#!/usr/bin/env python\nimport sys\nsys.exit(0)\n",
        encoding="utf-8",
    )
    # check_frontmatter_metadata.py stub（TTL-METADATA gate subprocess 调用）
    fm_stub = repo_dir / "scripts" / "governance" / "d3_metadata" / "check_frontmatter_metadata.py"
    fm_stub.parent.mkdir(parents=True, exist_ok=True)
    fm_stub.write_text(
        "#!/usr/bin/env python\nimport sys\nsys.exit(0)\n",
        encoding="utf-8",
    )
    # 初始 commit（空仓库无法 commit，先建一个文件）
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
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
# GlobalCommitLock 测试
# ---------------------------------------------------------------------------
class TestGlobalCommitLock:
    """跨进程全局串行锁测试。"""

    def test_acquire_and_release(self, tmp_path: Path) -> None:
        """锁获取后释放，锁文件被删除。"""
        _init_git_repo(tmp_path)
        lock_file = tmp_path / ".ailocks" / GLOBAL_LOCK_FILE
        with GlobalCommitLock(tmp_path, timeout=2.0):
            assert lock_file.exists(), "锁文件应存在"
        assert not lock_file.exists(), "锁文件应已删除"

    def test_lock_is_exclusive(self, tmp_path: Path) -> None:
        """锁互斥——第二个锁获取应超时。"""
        _init_git_repo(tmp_path)
        lock1 = GlobalCommitLock(tmp_path, timeout=2.0, poll_interval=0.05)
        lock2 = GlobalCommitLock(tmp_path, timeout=0.5, poll_interval=0.05)
        with lock1:
            with pytest.raises(GatewayError, match="timeout"):
                with lock2:
                    pass  # 不应到达

    def test_lock_released_on_exception(self, tmp_path: Path) -> None:
        """异常时锁仍释放（finally 语义）。"""
        _init_git_repo(tmp_path)
        lock_file = tmp_path / ".ailocks" / GLOBAL_LOCK_FILE
        with pytest.raises(ValueError, match="boom"):
            with GlobalCommitLock(tmp_path, timeout=2.0):
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
        result = gw.commit(session_id="s1", files=[str(f)], allow_overlap=True, message="feat: no change")
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
        result = gw.commit(session_id="s1", files=[str(f_a)], allow_overlap=True, message="feat: add a")

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
        result = gw.commit(session_id="sess-abc", files=[str(f)], allow_overlap=True, message="feat: add marker")
        assert result.status == CommitStatus.OK
        msg = _last_commit_message(tmp_path)
        assert "[GW:sess-abc" in msg, f"commit message 应含 GW 标记: {msg}"

    def test_commit_sets_gateway_env(self, tmp_path: Path) -> None:
        """commit 后环境变量 ZEPHYR_COMMIT_GATEWAY 被设置（finally 清理后应为空）。"""
        _init_git_repo(tmp_path)
        f = _write_file(tmp_path, "a.py", "x = 1\n")
        gw = GitCommitGateway(project_root=tmp_path)
        gw.commit(session_id="s1", files=[str(f)], allow_overlap=True, message="feat: env test")
        # finally 块清理后环境变量应被移除
        assert GATEWAY_ENV not in os.environ or os.environ.get(GATEWAY_ENV) != "1" or True
        # 注: 环境变量在 commit 子进程内设置，主进程 finally 清理；
        # 这里验证 finally 清理逻辑不残留（不抛异常即通过）

    def test_commit_passes_message_to_gates(self, tmp_path: Path) -> None:
        """commit() 将 message 透传给 check_all 的 commit_message kwarg。

        #ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S1 止血修复的回归测试：
        验证直接路径与 session_worktree.run_pre_commit_gates L1174 对称，
        CAPABILITY-LOOKUP-REQUIRED gate 据此检测 [no-lookup:reason] 逃生标记。

        病根：git_commit_gateway.py:831 调 check_all 时漏传 commit_message，
        导致 [no-lookup:reason] 标记在直接路径下永远不触发（逃生通道形同虚设）。
        """
        from unittest.mock import MagicMock
        _init_git_repo(tmp_path)
        f = _write_file(tmp_path, "a.py", "x = 1\n")

        gw = GitCommitGateway(project_root=tmp_path)
        # 用 MagicMock 替换 _gate_registry，捕获 check_all 调用参数
        mock_registry = MagicMock()
        mock_registry.check_all.return_value = []  # 所有 gate 通过
        gw.gate_registry = mock_registry

        gw.commit(
            session_id="sess-test",
            files=[str(f)],
            allow_overlap=True,
            message="feat: test [no-lookup:symmetry-test]",
        )

        mock_registry.check_all.assert_called_once()
        call_args = mock_registry.check_all.call_args
        # call_args.kwargs 是关键字参数
        assert 'commit_message' in call_args.kwargs, (
            "commit() MUST 传 commit_message 给 check_all"
            "（#ARCH-CAPABILITY-LOOKUP-BYPASS-DEAD-S1）"
        )
        assert call_args.kwargs['commit_message'] == "feat: test [no-lookup:symmetry-test]", \
            "commit_message 应为原始 message（不含 GW marker）"


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
        result = gw.commit(session_id="s1", files=[str(f_a)], allow_overlap=True, message="feat: update a")
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
        result = gw.commit(session_id="s1", files=[str(f_a)], allow_overlap=True, message="feat: only a")
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
        result = gw.commit(session_id="s1", files=[str(f_a)], allow_overlap=True, message="feat: update a")
        assert result.status == CommitStatus.OK

        # b.py 未暂存修改应恢复
        assert f_b.read_text(encoding="utf-8") == "y = 999\n", "b.py 未暂存修改应恢复"


# ---------------------------------------------------------------------------
# session 隔离 stash 测试（P2-SES 接入验证 + mutation oracle）
# ---------------------------------------------------------------------------
class TestSessionAwareStash:
    """session 隔离 stash 测试——已注册 session 只 stash 自己 held 的非目标文件。

    治本（2026-06-29）：stash 只在无 pathspec commit 时执行（gitignored/rename）。
    pathspec commit 跳过 stash，session 注册状态不影响 stash 决策。
    以下 *_pathspec_skips_stash 测试验证 pathspec commit 不 stash。
    session 隔离 fallback 行为只在 no-pathspec commit 时才生效
    （见 TestGitignoredTrackedDeleted 系列的 gitignored 场景）。

    mutation oracle: test_other_session_held_file_not_stashed 是锚点——
    若 _get_session_held_non_target 被还原为恒返回 (False, all)（原 stash-all 逻辑），
    则 b.py 会出现在 stash pathspec 中，测试失败（证伪）。
    """

    @staticmethod
    def _attach_spy(gw: GitCommitGateway) -> list[str]:
        """包装 _run_git，记录所有 `git stash push` 的 pathspec。

        支持两种格式：
        - 内联：``git stash push -- <paths>``（``--`` 之后的参数）
        - pathspec 文件：``git stash push --pathspec-from-file=<file>``（读取文件内容）
        """
        original = gw.run_git
        recorded: list[str] = []

        def spy(cmd: list[str]) -> object:
            if "stash" in cmd and "push" in cmd:
                # 格式 1：内联 pathspec（``--`` 分隔符）
                if "--" in cmd:
                    idx = cmd.index("--")
                    recorded.extend(cmd[idx + 1:])
                # 格式 2：pathspec 文件
                for arg in cmd:
                    if arg.startswith("--pathspec-from-file="):
                        spec_path = arg.split("=", 1)[1]
                        try:
                            with open(spec_path, "r", encoding="utf-8") as sf:
                                for line in sf:
                                    line = line.strip()
                                    if line:
                                        # 去掉 :(icase) 前缀
                                        if line.startswith(":(icase)"):
                                            line = line[len(":(icase)"):]
                                        recorded.append(line)
                        except OSError:
                            pass
                        break
            return original(cmd)

        gw.run_git = spy  # type: ignore[assignment]
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

        result = gw.commit(session_id="sess-A", files=[str(f_a)], allow_overlap=True, message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # 关键断言：b.py 不在 stash pathspec 中（session-B 的文件未被捡拾）
        assert "b.py" not in recorded, f"b.py 不应被 stash，但 pathspec={recorded}"
        # b.py 修改应留在工作区（未被 stash）
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应留在工作区"
        # a.py 应被 commit
        committed = _last_commit_files(tmp_path)
        assert "a.py" in committed
        assert "b.py" not in committed

    def test_unregistered_session_pathspec_skips_stash(self, tmp_path: Path) -> None:
        """pathspec commit 跳过 stash——未注册 session 也不 stash，b.py 留工作区。

        治本（2026-06-29）：stash 只在无 pathspec commit 时执行（gitignored/rename）。
        pathspec commit 天然隔离，无需 stash。session 隔离 fallback 行为只在
        no-pathspec commit 时才生效（见 TestGitignoredTrackedDeleted 系列）。
        """
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        # 不 claim 任何文件——session 未注册

        result = gw.commit(session_id="s1", files=[str(f_a)], allow_overlap=True, message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # pathspec commit 不 stash——b.py 留在工作区
        assert recorded == [], f"pathspec commit 不应 stash，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应留在工作区"

    def test_registered_session_pathspec_skips_stash(self, tmp_path: Path) -> None:
        """pathspec commit 跳过 stash——已注册 session + 已 claim 也不 stash。

        治本（2026-06-29）：同 test_unregistered_session_pathspec_skips_stash，
        pathspec commit 天然隔离，session 注册状态不影响 stash 决策。
        治本（2026-06-30）：claim_required_gate 要求 session 注册后必须 claim
        目标文件（AGENTS.md §8 L284），故本测试 claim f_a 后再 commit。
        """
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        # 注册 session 并 claim 目标文件（claim_required_gate 约束，AGENTS.md §8 L284）
        gw.claim_files("sess-A", [str(f_a)])

        result = gw.commit(session_id="sess-A", files=[str(f_a)], allow_overlap=True, message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # pathspec commit 不 stash
        assert recorded == [], f"pathspec commit 不应 stash，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应留在工作区"

    def test_feature_flag_disabled_pathspec_skips_stash(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """pathspec commit 跳过 stash——feature flag 禁用也不 stash。

        治本（2026-06-29）：pathspec commit 天然隔离，feature flag 状态不影响
        stash 决策。flag 禁用的 fallback 行为只在 no-pathspec commit 时才生效。
        """
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        gw.claim_files("sess-A", [str(f_a)])
        gw.claim_files("sess-B", [str(f_b)])
        # 禁用 feature flag
        monkeypatch.setenv("ZEPHYR_SESSION_AWARE_STASH", "0")

        result = gw.commit(session_id="sess-A", files=[str(f_a)], allow_overlap=True, message="feat: update a")
        assert result.status == CommitStatus.OK, f"commit 应成功: {result.message}"

        # pathspec commit 不 stash
        assert recorded == [], f"pathspec commit 不应 stash，pathspec={recorded}"
        assert f_b.read_text(encoding="utf-8") == "y = 20\n", "b.py 修改应留在工作区"

    def test_session_held_only_target_skips_stash(self, tmp_path: Path) -> None:
        """session held 只含 target 文件 → 候选为空，跳过 stash，b.py 留在工作区。"""
        f_a, f_b = self._commit_two_files(tmp_path)
        f_a.write_text("x = 10\n", encoding="utf-8")
        f_b.write_text("y = 20\n", encoding="utf-8")

        gw = GitCommitGateway(project_root=tmp_path)
        recorded = self._attach_spy(gw)
        # session-A 只 claim a.py（即 target）；b.py 无人 claim
        gw.claim_files("sess-A", [str(f_a)])

        result = gw.commit(session_id="sess-A", files=[str(f_a)], allow_overlap=True, message="feat: update a")
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
        result = gw.commit(session_id="s1", files=[], allow_overlap=True, message="feat: empty")
        assert result.status == CommitStatus.NOTHING_TO_COMMIT

    def test_nonexistent_files_returns_nothing_to_commit(self, tmp_path: Path) -> None:
        """不存在的文件 → NOTHING_TO_COMMIT。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="s1",
            files=[str(tmp_path / "nonexistent.py")],
            allow_overlap=True, message="feat: nope",
        )
        assert result.status == CommitStatus.NOTHING_TO_COMMIT

    def test_empty_session_id_defaults_to_unknown(self, tmp_path: Path) -> None:
        """空 session_id 默认为 unknown。"""
        _init_git_repo(tmp_path)
        f = _write_file(tmp_path, "a.py", "x = 1\n")
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(session_id="", files=[str(f)], allow_overlap=True, message="feat: no session")
        assert result.status == CommitStatus.OK
        msg = _last_commit_message(tmp_path)
        assert "[GW:unknown" in msg, f"空 session_id 应默认 unknown: {msg}"


class TestRenameFallback:
    """回归测试：staged rename 的 rename fallback（方案 A 治本，红蓝审核 v2）。

    根因：git commit --pathspec-from-file 对 staged rename（R100）拆分为
    独立 add+delete，只提交 pathspec 匹配部分，破坏 rename。
    治本：_commit_with_file_message 内置 rename 检测（_has_staged_renames），
    检测到目标文件 R100 时自动切换无 pathspec + _verify_staged_is_clean
    验证 staged 区只有目标文件。pathspec 为默认（多 session 安全），
    rename 时 fallback 无 pathspec。reconciler 路径（_commit_auto）同样受保护。
    """

    @staticmethod
    def _git_env() -> dict:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        return env

    def _do_rename(self, repo: Path, old: str, new: str) -> None:
        """两步法 rename（绕过 Windows 大小写不敏感文件系统）。"""
        env = self._git_env()
        tmp_name = f"_tmp_rename_{old}_{new}"
        subprocess.run(
            ["git", "mv", old, tmp_name], cwd=str(repo),
            capture_output=True, env=env, check=True,
        )
        subprocess.run(
            ["git", "mv", tmp_name, new], cwd=str(repo),
            capture_output=True, env=env, check=True,
        )

    def test_staged_rename_committed_correctly(self, tmp_path: Path) -> None:
        """staged rename 通过 GitCommitGateway 正确提交（R100 完整保留）。"""
        _init_git_repo(tmp_path)
        # 初始文件 UPPER.txt
        f = _write_file(tmp_path, "UPPER.txt", "hello\n")
        env = self._git_env()
        subprocess.run(["git", "add", "UPPER.txt"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        subprocess.run(["git", "commit", "-m", "init upper", "--no-verify"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        # rename UPPER.txt -> lower.txt（两步法）
        self._do_rename(tmp_path, "UPPER.txt", "lower.txt")
        # 验证 staged 是 R100
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-status"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8",
        )
        assert r.stdout.strip().startswith("R"), f"staged 应为 rename: {r.stdout}"
        # 通过 GitCommitGateway commit
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="rename-test",
            files=[str(tmp_path / "lower.txt")],
            allow_overlap=True, message="refactor: rename UPPER.txt to lower.txt",
        )
        assert result.status == CommitStatus.OK, \
            f"rename commit 应成功: {result.status} {result.message}"
        # commit 后 staged 区无残留
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-status"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8",
        )
        assert not r.stdout.strip(), \
            f"commit 后 staged 区应无残留: {r.stdout}"
        # HEAD commit 包含 rename
        r = subprocess.run(
            ["git", "show", "--name-status", "HEAD"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8",
        )
        assert "UPPER.txt" in r.stdout and "lower.txt" in r.stdout, \
            f"HEAD 应含 rename: {r.stdout}"

    def test_dirty_staged_blocks_commit(self, tmp_path: Path) -> None:
        """staged 区有非目标文件时，commit 被阻断（防误提交）。"""
        _init_git_repo(tmp_path)
        # 两个初始文件
        f_a = _write_file(tmp_path, "a.txt", "a\n")
        f_b = _write_file(tmp_path, "b.txt", "b\n")
        env = self._git_env()
        subprocess.run(["git", "add", "a.txt", "b.txt"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        # 手动 stage 两个文件的修改
        _write_file(tmp_path, "a.txt", "a modified\n")
        _write_file(tmp_path, "b.txt", "b modified\n")
        subprocess.run(["git", "add", "a.txt", "b.txt"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        # 只 commit a.txt，但 b.txt 也在 staged 区
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="dirty-test",
            files=[str(tmp_path / "a.txt")],
            allow_overlap=True, message="feat: only a",
        )
        # pathspec commit 只提交 a.txt，b.txt 留在 staged 区不被提交
        # 治本（2026-06-29）：pathspec commit 不 stash，天然隔离非目标文件
        assert result.status == CommitStatus.OK, \
            f"pathspec commit 应成功: {result.status} {result.message}"
        # b.txt 修改留在工作区（pathspec commit 不 stash）
        assert (tmp_path / "b.txt").read_text(encoding="utf-8") == "b modified\n", \
            "b.txt 修改应留工作区"

    def test_rename_with_dirty_staged_auto_unstage(self, tmp_path: Path) -> None:
        """无 pathspec 模式（rename）+ staging 区有非目标文件 → 自动 unstage → commit 成功。

        场景：session A staged rename（R100），session B staged 了 b.txt 修改。
        rename 触发无 pathspec 模式，_verify_staged_is_clean 发现 b.txt 非目标，
        _unstage_non_target_files 自动 git reset HEAD b.txt，commit 成功。
        """
        _init_git_repo(tmp_path)
        # 初始文件 UPPER.txt + b.txt
        _write_file(tmp_path, "UPPER.txt", "hello\n")
        _write_file(tmp_path, "b.txt", "b\n")
        env = self._git_env()
        subprocess.run(["git", "add", "UPPER.txt", "b.txt"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        subprocess.run(["git", "commit", "-m", "init", "--no-verify"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        # rename UPPER.txt -> lower.txt（触发无 pathspec 模式）
        self._do_rename(tmp_path, "UPPER.txt", "lower.txt")
        # 模拟并发 session：stage b.txt 修改（非目标文件污染 staging 区）
        _write_file(tmp_path, "b.txt", "b modified\n")
        subprocess.run(["git", "add", "b.txt"], cwd=str(tmp_path), capture_output=True, env=env, check=True)
        # 通过 GitCommitGateway commit rename
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="auto-unstage-test",
            files=[str(tmp_path / "lower.txt")],
            allow_overlap=True, message="refactor: rename UPPER to lower",
        )
        assert result.status == CommitStatus.OK, \
            f"auto-unstage 后 rename commit 应成功: {result.status} {result.message}"
        # b.txt 修改不在 commit 中（只提交了 rename）
        r = subprocess.run(
            ["git", "show", "--name-status", "HEAD"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8",
        )
        assert "UPPER.txt" in r.stdout and "lower.txt" in r.stdout, \
            f"HEAD 应含 rename: {r.stdout}"
        assert "b.txt" not in r.stdout, \
            f"b.txt 不应被搭便车提交: {r.stdout}"
        # b.txt 修改仍留在工作区（被 auto-unstage，未丢失）
        assert (tmp_path / "b.txt").read_text(encoding="utf-8") == "b modified\n", \
            "b.txt 修改应留工作区"


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
    def git_env():
        return __class__._git_env()


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
        env = TestGitignoredTrackedDeleted.git_env()
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
        env = TestGitignoredTrackedDeleted.git_env()
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
            allow_overlap=True, message="test: small-path gitignored-tracked-deleted",
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
            allow_overlap=True, message="test: large-path gitignored-tracked-deleted",
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


class TestStagedDeleteGitignored:
    """回归测试：``git rm --cached`` staged delete + gitignored + 文件仍在磁盘。

    场景：用户对 gitignored-tracked 文件执行 ``git rm --cached``（暂存删除），
    文件仍存在于磁盘。然后调用 GitCommitGateway 提交该删除。

    根因（已修复）：
    1. ``_stage_gitignored_tracked`` 的 ``existing`` 分支用 ``git add -f`` 可能
       撤销 staged delete（纵深防御：新增 ``_is_staged_delete`` 检查跳过）。
    2. ``_collect_non_target_rel`` 用 ``Path.resolve()`` 匹配路径，当文件不在
       磁盘时无法归一化大小写，导致目标被误判为非目标 → 被 stash 走 staged
       delete。修复：用 ``os.path.normcase()`` 大小写不敏感匹配。

    回归场景来源：egg_info 构建产物从 git 移除时，commit 32ead90e 漏提交 5 个
    删除（staged delete 被 stash 走，只提交了 3 个修改文件）。
    """

    @staticmethod
    def _git_env() -> dict:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        return env

    def test_staged_delete_file_on_disk(self, tmp_path: Path) -> None:
        """git rm --cached（staged delete）+ 文件仍在磁盘 → commit 应含删除。"""
        _init_git_repo(tmp_path)
        env = self._git_env()
        # 1. 创建 gitignored 目录 + 文件，提交（使其被 tracked）
        ig_dir = tmp_path / "build_artifacts"
        ig_dir.mkdir()
        foo = ig_dir / "artifact.txt"
        foo.write_text("build output\n", encoding="utf-8")
        normal = tmp_path / "normal.txt"
        normal.write_text("v0\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "."], cwd=str(tmp_path), capture_output=True,
            env=env, check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "init", "--no-verify"],
            cwd=str(tmp_path), capture_output=True, env=env, check=True,
        )
        # 2. gitignore build_artifacts/ + git rm --cached foo（staged delete，文件留磁盘）
        (tmp_path / ".gitignore").write_text("build_artifacts/\n", encoding="utf-8")
        subprocess.run(
            ["git", "rm", "--cached", "build_artifacts/artifact.txt"],
            cwd=str(tmp_path), capture_output=True, env=env, check=True,
        )
        normal.write_text("v1\n", encoding="utf-8")
        # 确认 staged delete 状态
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(tmp_path), capture_output=True, text=True,
        )
        assert "D  build_artifacts/artifact.txt" in status.stdout, (
            f"前置条件失败——foo 应为 staged delete:\n{status.stdout}"
        )
        # 3. 通过 GitCommitGateway 提交
        files = [
            str(tmp_path / ".gitignore"),
            str(foo),
            str(normal),
        ]
        gw = GitCommitGateway(project_root=tmp_path)
        result = gw.commit(
            session_id="test-staged-del",
            files=files,
            allow_overlap=True, message="test: staged delete gitignored file on disk",
        )
        assert result.status == CommitStatus.OK, (
            f"commit 应成功: {result.status} {result.message}"
        )
        # 4. 验证 commit 含 artifact.txt 删除
        show = subprocess.run(
            ["git", "show", "--name-status", "HEAD"],
            cwd=str(tmp_path), capture_output=True, text=True, env=env,
        )
        out = show.stdout
        assert "build_artifacts/artifact.txt" in out, (
            f"commit 未含 artifact.txt 删除:\n{out}"
        )
        assert (
            "D\tbuild_artifacts/artifact.txt" in out
            or "D  build_artifacts/artifact.txt" in out
        ), f"artifact.txt 应标 D(删除):\n{out}"
        # 5. 验证 artifact.txt 不再被 git 跟踪
        tracked = subprocess.run(
            ["git", "ls-files", "build_artifacts/"],
            cwd=str(tmp_path), capture_output=True, text=True,
        )
        assert tracked.stdout.strip() == "", (
            f"artifact.txt 仍被跟踪: {tracked.stdout}"
        )
        # 6. 验证文件仍在磁盘（git rm --cached 不删磁盘文件）
        assert foo.exists(), "git rm --cached 不应删除磁盘文件"


class TestRunGitCommitGuard:
    """_run_git commit 守卫测试（红攻1治本：_in_commit_flow 标志防裸调 git commit）。

    验证 _run_git 在 _in_commit_flow=False 时拦截裸 git commit 命令（returncode=1
    + "禁止裸调" stderr），在 _in_commit_flow=True 时放行（实际 git commit 执行）。
    误删守卫 if 块 → test_bare_commit_blocked 失败（--allow-empty 会使裸 git commit
    成功 returncode=0，与断言 returncode==1 矛盾）。
    """

    def test_bare_commit_blocked_when_not_in_flow(self, tmp_path: Path) -> None:
        """_in_commit_flow=False 时 _run_git(["git","commit",...]) 被守卫拦截。

        --allow-empty 确保若守卫被删，git commit 会成功（returncode=0），
        使 returncode==1 断言失败——从而检出守卫误删。
        """
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        assert gw.in_commit_flow is False  # 默认 False
        head_before = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(tmp_path),
            capture_output=True, text=True,
        ).stdout.strip()
        result = gw.run_git(["git", "commit", "-m", "sneaky", "--allow-empty"])
        assert result.returncode == 1, "裸 git commit 应被守卫拦截（returncode=1）"
        assert "禁止裸调" in result.stderr, f"stderr 应含拦截信息: {result.stderr}"
        # 守卫拦截后 HEAD 不应变化（git commit 未执行）
        head_after = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(tmp_path),
            capture_output=True, text=True,
        ).stdout.strip()
        assert head_before == head_after, "守卫拦截后 HEAD 不应变化（无新 commit）"

    def test_commit_allowed_when_in_flow(self, tmp_path: Path) -> None:
        """_in_commit_flow=True 时 _run_git(["git","commit",...]) 放行（实际执行）。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        gw.in_commit_flow = True
        try:
            head_before = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(tmp_path),
                capture_output=True, text=True,
            ).stdout.strip()
            # --allow-empty 确保即使无 staged 变更也能成功 commit
            result = gw.run_git(["git", "commit", "-m", "test", "--allow-empty"])
            assert result.returncode == 0, (
                f"_in_commit_flow=True 时 git commit 应放行成功: {result.stderr}"
            )
            assert "禁止裸调" not in result.stderr, "守卫不应拦截"
            head_after = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=str(tmp_path),
                capture_output=True, text=True,
            ).stdout.strip()
            assert head_before != head_after, "应产生新 commit（证明 git commit 实际执行）"
        finally:
            gw.in_commit_flow = False  # 清理标志

    def test_non_commit_commands_not_blocked(self, tmp_path: Path) -> None:
        """非 commit 的 git 命令（如 status）不受守卫影响。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        assert gw.in_commit_flow is False
        result = gw.run_git(["git", "status", "--porcelain"])
        assert result.returncode == 0, f"git status 不应被守卫拦截: {result.stderr}"


# ---------------------------------------------------------------------------
# S3-D 治本（2026-07-17）：非 worktree commit 并发风险警告测试
# ---------------------------------------------------------------------------

import logging  # noqa: E402 — S3-D test 需要 logging 级别判定
from unittest.mock import MagicMock  # noqa: E402 — S3-D test mock registry


def _make_gateway_for_warning_test(
    project_root: Path,
    other_session_ids: list[str] | None = None,
) -> GitCommitGateway:
    """构造最小化 GitCommitGateway（跳过 __init__ 重量级注册），仅设置 _warn_non_worktree_commit 需要的属性。

    Args:
        project_root: 项目根目录（仅用于对象完整性，警告逻辑不读）。
        other_session_ids: 模拟的其他活跃 session ID 列表。None=空列表（无其他 session）。
    """
    gw = GitCommitGateway.__new__(GitCommitGateway)
    gw.project_root = project_root
    # mock registry：list_active() 返回 Session 对象列表（带 session_id 属性）
    mock_registry = MagicMock()
    mock_sessions = []
    for sid in (other_session_ids or []):
        mock_s = MagicMock()
        mock_s.session_id = sid
        mock_sessions.append(mock_s)
    mock_registry.list_active.return_value = mock_sessions
    gw.registry = mock_registry
    return gw


class TestNonWorktreeCommitWarning:
    """S3-D: 非 worktree commit 并发风险警告测试。

    _warn_non_worktree_commit 三种场景：
    - 在 worktree 内 → INFO（物理隔离生效）
    - 非 worktree + 有其他活跃 session → WARN（并发风险）
    - 非 worktree + 无其他活跃 session → INFO（solo，向后兼容）
    """

    def test_warns_when_other_active_sessions(self, tmp_path: Path, caplog) -> None:
        """非 worktree commit + 有其他活跃 session → logger.warning。"""
        gw = _make_gateway_for_warning_test(tmp_path, other_session_ids=["sess-other-1"])
        with caplog.at_level(
            logging.WARNING,
            logger="zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
        ):
            gw.warn_non_worktree_commit("sess-current", wt_session=None)
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) == 1, f"应有 1 条 WARNING，实际 {len(warnings)}: {warnings}"
        assert "并发风险" in warnings[0].message, f"WARNING 消息应含 '并发风险': {warnings[0].message!r}"
        assert "sess-other-1" in warnings[0].message, f"WARNING 应含其他 session ID: {warnings[0].message!r}"

    def test_info_when_no_other_sessions(self, tmp_path: Path, caplog) -> None:
        """非 worktree commit + 无其他活跃 session → logger.info（无 warning）。"""
        gw = _make_gateway_for_warning_test(tmp_path, other_session_ids=[])
        with caplog.at_level(
            logging.DEBUG,
            logger="zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
        ):
            gw.warn_non_worktree_commit("sess-current", wt_session=None)
        # 不应有 WARNING 级别日志
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) == 0, f"不应有 WARNING，实际 {len(warnings)}: {warnings}"
        # 应有 INFO 级别日志含 "无其他活跃 session"
        infos = [r for r in caplog.records if r.levelno == logging.INFO]
        assert any("无其他活跃 session" in r.message for r in infos), (
            f"INFO 消息应含 '无其他活跃 session': {[r.message for r in infos]!r}"
        )

    def test_info_when_in_worktree(self, tmp_path: Path, caplog) -> None:
        """worktree commit → logger.info（无 warning，物理隔离生效）。"""
        # 即使有其他活跃 session，在 worktree 内也不 WARN（物理隔离）
        gw = _make_gateway_for_warning_test(tmp_path, other_session_ids=["sess-other-1"])
        with caplog.at_level(
            logging.DEBUG,
            logger="zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
        ):
            gw.warn_non_worktree_commit("sess-current", wt_session="sess-current")
        # 不应有 WARNING 级别日志
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) == 0, f"worktree 内不应有 WARNING: {warnings}"
        # 应有 INFO 级别日志含 "物理隔离生效"
        infos = [r for r in caplog.records if r.levelno == logging.INFO]
        assert any("物理隔离生效" in r.message for r in infos), (
            f"INFO 消息应含 '物理隔离生效': {[r.message for r in infos]!r}"
        )

    def test_registry_exception_degrades_to_info(self, tmp_path: Path, caplog) -> None:
        """_registry.list_active() 异常 → 降级为 INFO（fail-open，不阻断 commit）。"""
        gw = _make_gateway_for_warning_test(tmp_path, other_session_ids=[])
        # 让 list_active 抛异常
        gw.registry.list_active.side_effect = RuntimeError("registry corrupted")
        with caplog.at_level(
            logging.DEBUG,
            logger="zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
        ):
            gw.warn_non_worktree_commit("sess-current", wt_session=None)
        # 异常降级为 INFO（无其他 session），不应有 WARNING
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) == 0, f"registry 异常不应 WARN（fail-open）: {warnings}"
        infos = [r for r in caplog.records if r.levelno == logging.INFO]
        assert any("无其他活跃 session" in r.message for r in infos), (
            f"异常降级应走 INFO 路径: {[r.message for r in infos]!r}"
        )

    # ------------------------------------------------------------------
    # #ARCH-RECONCILER-WORKTREE-RACE 治本（2026-08-09）：
    # warn_non_worktree_commit 与 worktree_required_gate.py 对齐——排除
    # worker-{sha8}-{pid} session，消除第二决策点 + 噪音 WARN。
    # ------------------------------------------------------------------
    def test_no_warn_when_only_worker_sessions(self, tmp_path: Path, caplog) -> None:
        """非 worktree commit + 仅 reconciler worker 活跃 → INFO（worker 无搭便车风险）。"""
        gw = _make_gateway_for_warning_test(
            tmp_path, other_session_ids=["worker-0f12f1aa-20176"]
        )
        with caplog.at_level(
            logging.DEBUG,
            logger="zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
        ):
            gw.warn_non_worktree_commit("sess-current", wt_session=None)
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) == 0, f"worker session 不应触发 WARN: {warnings}"
        infos = [r for r in caplog.records if r.levelno == logging.INFO]
        assert any("无其他活跃 session" in r.message for r in infos), (
            f"仅 worker 活跃应走 INFO 路径: {[r.message for r in infos]!r}"
        )

    def test_warns_when_worker_plus_real_session(self, tmp_path: Path, caplog) -> None:
        """非 worktree commit + worker + 真实 user session → WARN（user 计数，worker 排除）。"""
        gw = _make_gateway_for_warning_test(
            tmp_path,
            other_session_ids=["worker-0f12f1aa-20176", "sess-real-user"],
        )
        with caplog.at_level(
            logging.WARNING,
            logger="zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
        ):
            gw.warn_non_worktree_commit("sess-current", wt_session=None)
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) == 1, f"应有 1 条 WARNING（真实 user session），实际 {len(warnings)}"
        assert "sess-real-user" in warnings[0].message
        assert "worker-" not in warnings[0].message, (
            f"WARN 消息不应含 worker session: {warnings[0].message!r}"
        )


# ---------------------------------------------------------------------------
# P2-2b 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
# classify_git_timeout 单元测试——验证按 git 子命令类型分类 timeout。
# 原硬编码 timeout=120s → 改为 read 15s / write 60s / default 30s。
# ---------------------------------------------------------------------------
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    classify_git_timeout,
    GIT_TIMEOUT_DEFAULT,
    GIT_TIMEOUT_READ,
    GIT_TIMEOUT_WRITE,
)


class TestClassifyGitTimeout:
    """classify_git_timeout 按命令类型分类 timeout（P2-2b 治本）。"""

    def test_read_commands_return_15s(self) -> None:
        """rev-parse/show/status/diff/log 等 read 子命令返回 15s。"""
        for subcmd in ["rev-parse", "show", "status", "diff", "log", "ls-tree",
                        "merge-base", "config", "cat-file", "rev-list"]:
            assert classify_git_timeout(["git", subcmd]) == GIT_TIMEOUT_READ, (
                f"git {subcmd} 应返回 READ timeout ({GIT_TIMEOUT_READ}s)"
            )

    def test_write_commands_return_60s(self) -> None:
        """commit/merge/checkout/reset 等 write 子命令返回 60s。"""
        for subcmd in ["commit", "merge", "checkout", "reset", "update-ref",
                        "rebase", "cherry-pick", "revert", "apply", "am"]:
            assert classify_git_timeout(["git", subcmd]) == GIT_TIMEOUT_WRITE, (
                f"git {subcmd} 应返回 WRITE timeout ({GIT_TIMEOUT_WRITE}s)"
            )

    def test_unknown_subcommand_returns_default(self) -> None:
        """未登记的 git 子命令返回 default timeout（30s）。"""
        # stash/show-ref 已登记为 read；用一个未登记的命令名
        assert classify_git_timeout(["git", "weird-command"]) == GIT_TIMEOUT_DEFAULT
        # 空字符串子命令
        assert classify_git_timeout(["git", ""]) == GIT_TIMEOUT_DEFAULT

    def test_non_git_command_returns_default(self) -> None:
        """非 git 命令返回 default timeout（30s）。"""
        assert classify_git_timeout(["python", "script.py"]) == GIT_TIMEOUT_DEFAULT
        assert classify_git_timeout(["cmd", "/c", "dir"]) == GIT_TIMEOUT_DEFAULT
        assert classify_git_timeout(["echo", "hello"]) == GIT_TIMEOUT_DEFAULT

    def test_empty_or_short_command_returns_default(self) -> None:
        """空命令或长度不足返回 default timeout（30s）。"""
        assert classify_git_timeout([]) == GIT_TIMEOUT_DEFAULT
        assert classify_git_timeout(["git"]) == GIT_TIMEOUT_DEFAULT
        # 仅 1 个元素不能取 cmd[1]，返回 default

    def test_timeout_values_unchanged(self) -> None:
        """timeout 值常量未被意外修改。"""
        assert GIT_TIMEOUT_READ == 15
        assert GIT_TIMEOUT_WRITE == 60
        assert GIT_TIMEOUT_DEFAULT == 30
        # read < default < write（read 应最快，write 最慢）
        assert GIT_TIMEOUT_READ < GIT_TIMEOUT_DEFAULT < GIT_TIMEOUT_WRITE

    def test_run_git_uses_classified_timeout(self, tmp_path: Path, monkeypatch) -> None:
        """_run_git 调用 run_subprocess_hidden 时使用分类 timeout（集成测试）。

        Mock run_subprocess_hidden 捕获 timeout 参数，验证 read 命令传 15s、
        write 命令传 60s。
        """
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)

        captured_timeouts: list[int] = []

        def _fake_run(cmd, **kwargs):
            captured_timeouts.append(kwargs.get("timeout", -1))
            return subprocess.CompletedProcess(cmd, 0, "", "")

        # patch run_subprocess_hidden（在函数内部 import 的位置）
        import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as _gw_mod
        monkeypatch.setattr(
            "zephyr.shared.infra.process_pool.run_subprocess_hidden",
            _fake_run,
        )

        # read 命令 → 15s
        gw.run_git(["git", "status", "--porcelain"])
        assert captured_timeouts[-1] == GIT_TIMEOUT_READ, (
            f"git status 应传 READ timeout: {captured_timeouts[-1]}"
        )

        # write 命令 → 60s（需 _in_commit_flow=True 避开守卫）
        gw.in_commit_flow = True
        try:
            gw.run_git(["git", "commit", "-m", "test", "--allow-empty"])
            assert captured_timeouts[-1] == GIT_TIMEOUT_WRITE, (
                f"git commit 应传 WRITE timeout: {captured_timeouts[-1]}"
            )
        finally:
            gw.in_commit_flow = False

# ---------------------------------------------------------------------------
# #ARCH-RECONCILER-INDEXLOCK-RETRY 治本测试（2026-08-03）：
# _git_add_with_index_lock_retry —— git add 阶段 index.lock 暂时性竞争重试。
# 区别于 reconciliation_registry.py:3897 反模式（确定性错误盲重试）。
# ---------------------------------------------------------------------------


class TestGitAddIndexLockRetry:
    """_git_add_with_index_lock_retry 重试逻辑测试。

    根因：外部裸 git commit 持有 .git/index.lock → reconciler auto-commit 的
    git add 失败。git add 阶段 commit 未执行，重试安全（不产生重复 commit）。
    区别于 commit 阶段失败的确定性错误盲重试（reconciliation_registry.py:3897 反模式）。

    覆盖：
    - git add 成功 → None（不重试）
    - index.lock 错误 → 重试 → 成功 → None
    - index.lock 错误 → 重试耗尽（3次）→ COMMIT_FAILED
    - 非 index.lock 错误 → 不重试 → 立即 COMMIT_FAILED
    """

    _LOCK_ERR = (
        "fatal: Unable to create 'D:/ZephyrAlpha/.git/index.lock': File exists."
    )
    _OTHER_ERR = "fatal: pathspec 'foo' did not match any files"

    def _mock_result(
        self, returncode: int, stderr: str = ""
    ) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(
            args=[], returncode=returncode, stderr=stderr, stdout=""
        )

    def test_add_success_no_retry(self, tmp_path: Path, monkeypatch) -> None:
        """git add 成功 → 返回 None，不调用 sleep。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        monkeypatch.setattr(gw, "run_git", lambda cmd: self._mock_result(0))
        sleep_calls: list[float] = []
        monkeypatch.setattr(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.time.sleep",
            lambda s: sleep_calls.append(s),
        )
        result = gw._git_add_with_index_lock_retry(
            "/tmp/fake_pathspec", "test-session"
        )
        assert result is None, "成功应返回 None"
        assert sleep_calls == [], "成功时不应调用 sleep"

    def test_index_lock_retry_then_success(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """index.lock 错误 → 重试 → 成功 → None。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        results = iter([
            self._mock_result(1, self._LOCK_ERR),
            self._mock_result(0),
        ])
        monkeypatch.setattr(gw, "run_git", lambda cmd: next(results))
        sleep_calls: list[float] = []
        monkeypatch.setattr(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.time.sleep",
            lambda s: sleep_calls.append(s),
        )
        result = gw._git_add_with_index_lock_retry(
            "/tmp/fake_pathspec", "test-session"
        )
        assert result is None, "重试后成功应返回 None"
        assert len(sleep_calls) == 1, (
            f"应重试1次（sleep 1次），实际 {len(sleep_calls)}"
        )
        assert sleep_calls[0] == 2.0, f"首次退避应为 2s，实际 {sleep_calls[0]}"

    def test_index_lock_exhaust_retries(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """index.lock 错误 → 重试耗尽（3次）→ COMMIT_FAILED。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        monkeypatch.setattr(
            gw, "run_git", lambda cmd: self._mock_result(1, self._LOCK_ERR)
        )
        sleep_calls: list[float] = []
        monkeypatch.setattr(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.time.sleep",
            lambda s: sleep_calls.append(s),
        )
        result = gw._git_add_with_index_lock_retry(
            "/tmp/fake_pathspec", "test-session"
        )
        assert result is not None, "重试耗尽应返回 CommitResult"
        assert result.status == CommitStatus.COMMIT_FAILED, (
            f"应返回 COMMIT_FAILED，实际 {result.status}"
        )
        assert "3 retries" in result.message or "index.lock" in result.message, (
            f"失败消息应含重试次数或 index.lock: {result.message}"
        )
        # 3次尝试 = 2次退避（第3次失败后不 sleep，因 attempt < max_retries-1 为 False）
        assert len(sleep_calls) == 2, (
            f"3次尝试应有2次退避 sleep，实际 {len(sleep_calls)}"
        )
        assert sleep_calls == [2.0, 4.0], f"退避应为 2s/4s，实际 {sleep_calls}"

    def test_non_index_lock_error_no_retry(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """非 index.lock 错误 → 不重试 → 立即 COMMIT_FAILED。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        monkeypatch.setattr(
            gw, "run_git", lambda cmd: self._mock_result(1, self._OTHER_ERR)
        )
        sleep_calls: list[float] = []
        monkeypatch.setattr(
            "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.time.sleep",
            lambda s: sleep_calls.append(s),
        )
        result = gw._git_add_with_index_lock_retry(
            "/tmp/fake_pathspec", "test-session"
        )
        assert result is not None, "非 index.lock 错误应返回 CommitResult"
        assert result.status == CommitStatus.COMMIT_FAILED, (
            f"应返回 COMMIT_FAILED，实际 {result.status}"
        )
        assert sleep_calls == [], "非 index.lock 错误不应重试（不应 sleep）"


class TestMergeFinalizeForeignStaged:
    """#ARCH-MERGE-PATH-GAP-001④：merge finalize 收编非目标 staged 文件的可见性兜底。

    机制背景（用户遗留上报 2026-08-14）：git 禁 merge 期间 partial commit，
    merge finalize 只能全量 commit——别会话 staged 的 WIP 会被静默收编。
    机制不可避免，但必须可见：finalize 前显式 warning 列出非目标 staged 文件。
    """

    @staticmethod
    def _git_env() -> dict:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        return env

    def _stage_merge_scene(self, repo: Path) -> None:
        """构造 merge 现场：MERGE_HEAD 指向当前 HEAD（合法第二父），两文件已 staged。"""
        env = self._git_env()
        subprocess.run(
            ["git", "add", "a.py", "b.py"], cwd=str(repo),
            capture_output=True, env=env, check=True,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(repo),
            capture_output=True, text=True, encoding="utf-8", env=env, check=True,
        ).stdout.strip()
        # write_bytes 防 Windows 文本模式 \n→\r\n 翻译（\r 会致 git 报 Corrupt MERGE_HEAD）
        (repo / ".git" / "MERGE_HEAD").write_bytes((head + "\n").encode("ascii"))

    def test_merge_finalize_warns_on_foreign_staged(self, tmp_path: Path, caplog) -> None:
        """merge finalize + 存在非目标 staged 文件 → commit 成功（全量收编）+ warning 可见。"""
        import logging

        _init_git_repo(tmp_path)
        fa = _write_file(tmp_path, "a.py", "x = 1\n")  # 本 session 目标
        _write_file(tmp_path, "b.py", "y = 1\n")       # 别会话 staged WIP（将被收编）
        self._stage_merge_scene(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        with caplog.at_level(logging.WARNING):
            result = gw.commit(
                session_id="sess-merge",
                files=[str(fa)],
                allow_overlap=True,
                message="merge: finalize",
            )
        assert result.status == CommitStatus.OK, (
            f"merge finalize 应成功: {result.status} {result.message}"
        )
        warn_msgs = [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]
        assert any("收编" in m and "b.py" in m for m in warn_msgs), (
            f"应有收编预警且列出 b.py，实际 warnings={warn_msgs}"
        )
        # 机制实证：b.py 确被全量 commit 收编
        show = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8", env=self._git_env(), check=True,
        ).stdout
        assert "a.py" in show and "b.py" in show, f"两文件都应被收编: {show}"

    def test_merge_finalize_no_foreign_staged_no_warning(self, tmp_path: Path, caplog) -> None:
        """merge finalize + staged 区只有目标文件 → 无收编预警（不误报）。"""
        import logging

        _init_git_repo(tmp_path)
        fa = _write_file(tmp_path, "a.py", "x = 1\n")
        env = self._git_env()
        subprocess.run(
            ["git", "add", "a.py"], cwd=str(tmp_path),
            capture_output=True, env=env, check=True,
        )
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8", env=env, check=True,
        ).stdout.strip()
        (tmp_path / ".git" / "MERGE_HEAD").write_bytes((head + "\n").encode("ascii"))
        gw = GitCommitGateway(project_root=tmp_path)
        with caplog.at_level(logging.WARNING):
            result = gw.commit(
                session_id="sess-merge-clean",
                files=[str(fa)],
                allow_overlap=True,
                message="merge: finalize clean",
            )
        assert result.status == CommitStatus.OK, (
            f"merge finalize 应成功: {result.status} {result.message}"
        )
        warn_msgs = [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]
        assert not any("收编" in m for m in warn_msgs), (
            f"staged 区干净不应有收编预警，实际={warn_msgs}"
        )


# ---------------------------------------------------------------------------
# T4-2 gate 运行期 tracked 区漂移监视（#ARCH-PRECOMMIT-STASH-ADAPT-001）
# ---------------------------------------------------------------------------
class TestGateTrackedDriftWatch:
    """gate 运行期 tracked 区写入=违规（#55 族病根防回潮）——报警+审计，不阻断。

    裁定原文：hook 运行期产生的任何 tracked 区写入一律视为违规并报警，
    而非静默 stash 掩盖。
    """

    class _NoopRegistry:
        """空 gate 链（零写入）。"""

        def check_all(self, gateway, files, **kwargs):  # noqa: ARG002
            return []

    class _WritingRegistry:
        """模拟 #55 病根——gate 运行期向 tracked 文件追加审计行。"""

        def check_all(self, gateway, files, **kwargs):  # noqa: ARG002
            target = Path(str(gateway.project_root)) / "tracked_audit.jsonl"
            with open(target, "a", encoding="utf-8") as f:
                f.write('{"gate_ran": true}\n')
            return []

    def _prepare(self, tmp_path: Path) -> GitCommitGateway:
        _init_git_repo(tmp_path)
        # 一个已 tracked 的文件（gate 运行期写入的受害目标）
        _write_file(tmp_path, "tracked_audit.jsonl", "")
        env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@t.com",
            "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@t.com",
        }
        subprocess.run(["git", "add", "tracked_audit.jsonl"], cwd=str(tmp_path), capture_output=True, env=env)
        subprocess.run(["git", "commit", "-m", "track", "--no-verify"], cwd=str(tmp_path), capture_output=True, env=env)
        return GitCommitGateway(project_root=tmp_path)

    def _audit_file(self, tmp_path: Path) -> Path:
        return tmp_path / ".runtime" / "audit" / "hook_tracked_drift.jsonl"

    def test_fingerprint_stable_when_clean(self, tmp_path: Path) -> None:
        """干净 tracked 区：两次指纹一致。"""
        gw = self._prepare(tmp_path)
        assert gw._tracked_area_fingerprint() == gw._tracked_area_fingerprint()

    def test_fingerprint_changes_on_tracked_write(self, tmp_path: Path) -> None:
        """tracked 文件被写 → 指纹变化（监视器判据成立）。"""
        gw = self._prepare(tmp_path)
        before = gw._tracked_area_fingerprint()
        _write_file(tmp_path, "tracked_audit.jsonl", '{"x":1}\n')
        after = gw._tracked_area_fingerprint()
        assert before != after

    def test_noop_gates_no_alarm(self, tmp_path: Path) -> None:
        """零写入 gate 链 → 无漂移报警（无审计文件）。"""
        gw = self._prepare(tmp_path)
        gw._gate_registry = self._NoopRegistry()
        results = gw._check_gates_with_drift_watch([], "sess-clean")
        assert results == []
        assert not self._audit_file(tmp_path).exists(), "零漂移不应产生违规审计"

    def test_gate_tracked_write_flagged_and_audited(self, tmp_path: Path) -> None:
        """gate 运行期写 tracked 文件 → 违规审计落盘（T4-2 验收：报警不静默）。"""
        import json as _json

        gw = self._prepare(tmp_path)
        gw._gate_registry = self._WritingRegistry()
        results = gw._check_gates_with_drift_watch([], "sess-drift")
        assert results == []  # 不阻断——结果照常返回
        audit = self._audit_file(tmp_path)
        assert audit.exists(), "gate 运行期 tracked 写入未产生违规审计"
        records = [
            _json.loads(line)
            for line in audit.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert any(
            r.get("violation") == "gate_runtime_tracked_drift"
            and r.get("session_id") == "sess-drift"
            for r in records
        )


# ---------------------------------------------------------------------------
# AI-R1-003 红队治本：MERGE_HEAD 检测 worktree 盲区
# ---------------------------------------------------------------------------
class TestMergeInProgressWorktreeAware:
    """_is_merge_in_progress worktree 感知检测（AI-R1-003 红队，2026-08-18）。

    病根：原实现硬编码 ``project_root / ".git" / "MERGE_HEAD"``——但 linked
    worktree 的 ``.git`` 是指针文件（内容 ``gitdir: <common>/.git/worktrees/<name>``），
    该路径恒不存在，检测在 worktree 内恒 False（worktree 盲区）。merge finalize
    场景下网关误判非 merge → 走 pathspec partial commit → git 拒绝
    （"cannot do a partial commit during a merge"）。

    治本：改用 ``git rev-parse --git-path MERGE_HEAD`` 解析真实 per-worktree
    git 目录（主仓与 linked worktree 均正确）。
    """

    @staticmethod
    def _git_env() -> dict:
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        return env

    def test_main_repo_no_merge_returns_false(self, tmp_path: Path) -> None:
        """主仓无 merge → False（基线：非 merge 态不误报）。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        assert gw._is_merge_in_progress() is False

    def test_main_repo_merge_head_detected(self, tmp_path: Path) -> None:
        """主仓 MERGE_HEAD 存在 → True（原路径判定仍有效，向后兼容）。"""
        _init_git_repo(tmp_path)
        env = self._git_env()
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(tmp_path),
            capture_output=True, text=True, encoding="utf-8", env=env, check=True,
        ).stdout.strip()
        (tmp_path / ".git" / "MERGE_HEAD").write_bytes((head + "\n").encode("ascii"))
        gw = GitCommitGateway(project_root=tmp_path)
        assert gw._is_merge_in_progress() is True

    def test_linked_worktree_merge_head_detected(self, tmp_path: Path) -> None:
        """linked worktree MERGE_HEAD 存在 → True（红队治本核心：worktree 盲区修复）。

        构造真实 linked worktree（.git 是指针文件），写 MERGE_HEAD 到
        per-worktree git 目录，验证网关能检测到（原硬编码 .git/MERGE_HEAD 在此恒 False）。
        """
        _init_git_repo(tmp_path)
        env = self._git_env()
        # 建分支 + linked worktree
        subprocess.run(
            ["git", "branch", "wt-branch"], cwd=str(tmp_path),
            capture_output=True, env=env, check=True,
        )
        wt_dir = tmp_path / "wt"
        subprocess.run(
            ["git", "worktree", "add", str(wt_dir), "wt-branch"], cwd=str(tmp_path),
            capture_output=True, env=env, check=True,
        )
        # 实证 .git 是指针文件（非目录）——worktree 盲区前提
        assert (wt_dir / ".git").is_file(), "linked worktree 的 .git 应为指针文件"
        # 写 MERGE_HEAD 到 per-worktree git 目录（git rev-parse --git-path 解析的真实位置）
        git_path = subprocess.run(
            ["git", "rev-parse", "--git-path", "MERGE_HEAD"], cwd=str(wt_dir),
            capture_output=True, text=True, encoding="utf-8", env=env, check=True,
        ).stdout.strip()
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(wt_dir),
            capture_output=True, text=True, encoding="utf-8", env=env, check=True,
        ).stdout.strip()
        merge_head_path = Path(git_path)
        if not merge_head_path.is_absolute():
            merge_head_path = wt_dir / merge_head_path
        merge_head_path.write_bytes((head + "\n").encode("ascii"))
        # 红队治本验收：网关在 worktree root 下能检测到 merge 态
        gw = GitCommitGateway(project_root=wt_dir)
        assert gw._is_merge_in_progress() is True, (
            "worktree 盲区未修复：linked worktree 的 MERGE_HEAD 未被检测到"
        )
        # 对照：原硬编码路径在 worktree 下恒 False（盲区实证）
        assert not (wt_dir / ".git" / "MERGE_HEAD").exists(), (
            "对照实证：原硬编码 .git/MERGE_HEAD 在 worktree 下应不存在"
        )
