# [BLUEPRINT] MOD-GOV-create_guard | tests/test_create_guard.py | §create-guard-tests
# [MODULE] tests.test_create_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.commit_gates.create_guard, zephyr.governance.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 测试隔离——使用 tmp_path 临时 git 仓库，不读/不写真实 registry（create_guard 自己读真实 registry，测试用唯一名避免冲突）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] task_bound
"""test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-06-30 治本补全）

覆盖 create_guard._check 的7个核心场景：
1. 新增 .py 文件无 creation_token → 硬阻断
2. 其他 session 的 staged .py 不误判（files 参数过滤治本）
3. tests/ 目录下 .py 文件豁免
4. 非 .py 文件不检测
5. registry 缺失 → fail-closed 阻断（治本1，防删 registry 绕过 token 检查）
6. registry 解析失败 → fail-closed 阻断（治本1）
7. git diff 失败 → fail-closed 阻断（治本1，对标 directory_contract_gate）

测试隔离：所有测试用 tmp_path 临时 git 仓库，不污染生产 registry。
create_guard 读取真实项目 capability_canonical_file_registry.yaml（fail-closed 设计，治本1），
测试用唯一文件名（__create_guard_test_fake_20260630__.py）避免与真实 registry 冲突。
fail-closed 测试用 monkeypatch REGISTRY_YAML 指向 tmp_path 下临时文件（避免触碰真源）。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.create_guard import make_create_guard  # noqa: E402
from zephyr.governance.git_commit_gateway import GitCommitGateway  # noqa: E402


def _init_git_repo(repo_dir: Path) -> None:
    """初始化 git 仓库（含初始 commit）。

    精简版——不创建 DCR checker stub（create_guard 测试直接调用 gate.check，
    不经过 commit 流程，不触发 DCR gate）。
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
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
    )


def _stage_file(repo_dir: Path, rel_path: str, content: str = "x = 1\n") -> Path:
    """创建文件并 git add（staged），返回绝对路径。"""
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", str(rel_path)], cwd=str(repo_dir), capture_output=True)
    return f


class TestNewPyWithoutTokenBlocked:
    """新增 .py 文件无 creation_token → 硬阻断。"""

    def test_blocks_unregistered_new_py(self, tmp_path: Path) -> None:
        """staged 新增 .py 文件不在 registry creation_tokens 中 → 阻断。

        用唯一名 __create_guard_test_fake_20260630__.py 避免与真实 registry 冲突。
        create_guard 读真实 registry（fail-open 设计），真实 registry 不含此路径 → 阻断。
        """
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/governance/commit_gates/__create_guard_test_fake_20260630__.py",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"无 token 的新增 .py 应被阻断: {detail}"
        assert "creation_token" in detail
        assert "造第二真源" in detail


class TestOtherSessionStagedPyNotBlocked:
    """其他 session 的 staged .py 不误判（files 参数过滤治本）。

    病根：gateway 选择性提交（只提交 files_in_scope，其他 staged 文件 stash），
    create_guard 若检测所有 staged .py 会误判其他 session 的 WIP。
    治本：用 files 参数过滤，只检测 commit 文件中的新增 .py。
    """

    def test_other_session_staged_py_ignored(self, tmp_path: Path) -> None:
        """files=[a.txt] 时，staged 的 b.py 不被检测 → 通过。

        模拟场景：session A commit a.txt，session B 已 stage b.py（WIP）。
        create_guard 只应检测 a.txt（本次 commit 文件），不应检测 b.py。
        a.txt 非 .py → 不检测；b.py 虽 staged .py 但不在 files 中 → 不检测。
        """
        _init_git_repo(tmp_path)
        # b.py 是其他 session staged 的 WIP（不在本次 commit 范围）
        _stage_file(tmp_path, "b.py", "y = 2\n")
        # a.txt 是本次要 commit 的文件
        f_a = _stage_file(tmp_path, "a.txt", "hello\n")
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f_a)])
        assert passed is True, f"其他 session 的 staged .py 不应被误判: {detail}"


class TestTestsDirExempt:
    """tests/ 目录下 .py 文件豁免（测试非能力真源，对标 capability_overlap_gate）。"""

    def test_tests_dir_py_exempt(self, tmp_path: Path) -> None:
        """staged tests/ 下新增 .py 文件豁免 → 通过。"""
        _init_git_repo(tmp_path)
        f = _stage_file(tmp_path, "tests/test_new_feature.py")
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"tests/ 下 .py 应豁免: {detail}"


class TestNonPyFileNotBlocked:
    """非 .py 文件不检测。"""

    def test_md_file_not_blocked(self, tmp_path: Path) -> None:
        """staged 新增 .md 文件不触发 create_guard → 通过。"""
        _init_git_repo(tmp_path)
        f = _stage_file(tmp_path, "docs/readme.md", "# readme\n")
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"非 .py 文件不应被阻断: {detail}"


# ===========================================================================
# 治本1（2026-06-30）：fail-closed 测试组
# 病根：原 fail-open（return True）会被"删 registry 绕过 token 检查"利用。
# 治本：YAML 不可达 + git diff 失败全改 fail-closed（return False + 修复指引）。
# 对标 directory_contract_gate.py fail-closed 设计。
# ===========================================================================

class TestFailClosedRegistryMissing:
    """registry 缺失 → fail-closed 阻断（治本1，防删 registry 绕过 token 检查）。"""

    def test_registry_missing_blocks(self, tmp_path: Path, monkeypatch) -> None:
        """REGISTRY_YAML 指向不存在文件 → passed=False + detail 含修复指引。"""
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/governance/commit_gates/__create_guard_test_fake_20260630__.py",
        )
        # monkeypatch REGISTRY_YAML 指向不存在文件（避免触碰真源）
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            tmp_path / "nonexistent_registry.yaml",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"registry 缺失应 fail-closed 阻断: {detail}"
        assert "fail-closed" in detail
        assert "不可达" in detail or "缺失" in detail
        assert "恢复" in detail or "checkout" in detail


class TestFailClosedRegistryParseError:
    """registry 解析失败 → fail-closed 阻断（治本1）。"""

    def test_registry_parse_error_blocks(self, tmp_path: Path, monkeypatch) -> None:
        """REGISTRY_YAML 指向非法 YAML → passed=False + detail 含修复指引。"""
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/governance/commit_gates/__create_guard_test_fake_20260630__.py",
        )
        # 写非法 YAML（避免触碰真源）
        bad_yaml = tmp_path / "bad_registry.yaml"
        bad_yaml.write_text("invalid: yaml: content:", encoding="utf-8")
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            bad_yaml,
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"registry 解析失败应 fail-closed 阻断: {detail}"
        assert "fail-closed" in detail
        assert "解析失败" in detail
        assert "YAML" in detail or "语法" in detail


class TestFailClosedGitDiffFailure:
    """git diff 失败 → fail-closed 阻断（治本1，对标 directory_contract_gate）。"""

    def test_git_diff_nonzero_returncode_blocks(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """git diff returncode=1 → passed=False + detail 含修复指引。"""
        from unittest.mock import MagicMock

        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/governance/commit_gates/__create_guard_test_fake_20260630__.py",
        )
        # mock gateway._run_git 返回 returncode=1（git diff 失败）
        gw = MagicMock()
        gw.project_root = tmp_path
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        gw._run_git.return_value = mock_result
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"git diff 失败应 fail-closed 阻断: {detail}"
        assert "fail-closed" in detail
        assert "git diff" in detail

    def test_git_diff_exception_blocks(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """git diff 抛异常 → passed=False + detail 含修复指引。"""
        from unittest.mock import MagicMock

        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/governance/commit_gates/__create_guard_test_fake_20260630__.py",
        )
        gw = MagicMock()
        gw.project_root = tmp_path
        gw._run_git.side_effect = RuntimeError("git down")
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"git diff 异常应 fail-closed 阻断: {detail}"
        assert "fail-closed" in detail
        assert "git diff" in detail
