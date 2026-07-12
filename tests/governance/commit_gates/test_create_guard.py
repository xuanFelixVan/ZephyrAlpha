# [BLUEPRINT] MOD-GOV-create_guard | tests/test_create_guard.py | §create-guard-tests
# [MODULE] tests.test_create_guard
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.commit_gates.create_guard, zephyr.governance.rule_bridge.git_commit_gateway
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

覆盖 create_guard._check 的核心场景：
1. 新增 .py 文件无 creation_token → 硬阻断
2. 其他 session 的 staged .py 不误判（files 参数过滤治本）
3. tests/ 目录下 .py 文件豁免
4. 非 .py 文件不检测
5. registry 缺失 → fail-closed 阻断（治本1，防删 registry 绕过 token 检查）
6. registry 解析失败 → fail-closed 阻断（治本1）
7. git diff 失败 → fail-closed 阻断（治本1，对标 directory_contract_gate）
8. 新增 make_*_reconciler 无 # trae_060-reviewed 标记 → 硬阻断（元问题3治本，2026-06-30）
9. 新增 make_*_reconciler 有标记 → 通过
10. 修改已有 make_*_reconciler（未新增函数）→ 通过
11. commit 不含 reconciliation_registry.py → 通过（不触发检测）

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
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway  # noqa: E402


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
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30)
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
        timeout=30,
    )
    (repo_dir / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo_dir),
        capture_output=True,
        env=env,
        check=True,
        timeout=30,
    )


def _stage_file(repo_dir: Path, rel_path: str, content: str = "x = 1\n") -> Path:
    """创建文件并 git add（staged），返回绝对路径。"""
    f = repo_dir / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", str(rel_path)], cwd=str(repo_dir), capture_output=True, timeout=30)
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


# ===========================================================================
# 元问题3治本（2026-06-30，AD-GOV-001 收敛约束技术强制）
# 病根："新增 reconciler 前 MUST 过 trae_060 §4 审查"是君子协定，新 AI 可直接造新 reconciler。
# 治本：扩展已有 create_guard 检测范围——reconciliation_registry.py 新增 make_*_reconciler
# 时需在 def 前 5 行内添加 '# trae_060-reviewed: <审查结论>' 标记，否则硬阻断。
# 规避自指递归：不新增门禁，只扩展已有 create_guard。
# ===========================================================================

class TestNewReconcilerMarker:
    """新增 make_*_reconciler 需 # trae_060-reviewed 标记（元问题3治本）。"""

    _RECONCILER_REL = "src/zephyr/governance/audit/reconciliation_registry.py"

    def _setup_reconciler_registry(
        self, repo_dir: Path, head_content: str, staged_content: str
    ) -> Path:
        """在 repo_dir 下创建 reconciliation_registry.py：先 commit head_content 到 HEAD，
        再 stage staged_content（模拟修改新增 make_*_reconciler）。"""
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        f = repo_dir / self._RECONCILER_REL
        f.parent.mkdir(parents=True, exist_ok=True)
        # HEAD 版本
        f.write_text(head_content, encoding="utf-8")
        subprocess.run(
            ["git", "add", self._RECONCILER_REL],
            cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-m", "head version", "--no-verify"],
            cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30,
        )
        # staged 修改版
        f.write_text(staged_content, encoding="utf-8")
        subprocess.run(
            ["git", "add", self._RECONCILER_REL],
            cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30,
        )
        return f

    def test_new_reconciler_without_marker_blocked(self, tmp_path: Path) -> None:
        """staged 新增 make_test_reconciler 无 # trae_060-reviewed 标记 → 阻断。"""
        _init_git_repo(tmp_path)
        head = '"""mod"""\n\ndef make_existing_reconciler():\n    pass\n'
        staged = (
            '"""mod"""\n\n'
            'def make_existing_reconciler():\n    pass\n\n'
            'def make_test_reconciler():\n    pass\n'
        )
        f = self._setup_reconciler_registry(tmp_path, head, staged)
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"无 trae_060-reviewed 标记的新增 reconciler 应被阻断: {detail}"
        assert "trae_060" in detail
        assert "make_test_reconciler" in detail

    def test_new_reconciler_with_marker_passes(self, tmp_path: Path) -> None:
        """staged 新增 make_test_reconciler 有 # trae_060-reviewed 标记 → 通过。"""
        _init_git_repo(tmp_path)
        head = '"""mod"""\n\ndef make_existing_reconciler():\n    pass\n'
        staged = (
            '"""mod"""\n\n'
            'def make_existing_reconciler():\n    pass\n\n'
            '# trae_060-reviewed: 该存在+治本\n'
            'def make_test_reconciler():\n    pass\n'
        )
        f = self._setup_reconciler_registry(tmp_path, head, staged)
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"有 trae_060-reviewed 标记的新增 reconciler 应通过: {detail}"

    def test_modify_existing_reconciler_passes(self, tmp_path: Path) -> None:
        """修改已有 make_*_reconciler（未新增函数）→ 通过（不触发检测）。"""
        _init_git_repo(tmp_path)
        head = '"""mod"""\n\ndef make_existing_reconciler():\n    return None\n'
        staged = '"""mod"""\n\ndef make_existing_reconciler():\n    return "modified"\n'
        f = self._setup_reconciler_registry(tmp_path, head, staged)
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"修改已有 reconciler 不新增函数应通过: {detail}"

    def test_no_reconciler_file_passes(self, tmp_path: Path) -> None:
        """commit 不含 reconciliation_registry.py → 通过（不触发检测）。"""
        _init_git_repo(tmp_path)
        f = _stage_file(tmp_path, "docs/readme.md", "# readme\n")
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"不含 reconciliation_registry.py 的 commit 应通过: {detail}"


# ===========================================================================
# ARCH-037 治本扩展（2026-07-01，DIM-5 commit-time 强制）
# 病根：DIM-5 检测能力已就位（validate_rule_frontmatter.py pre-commit hook），但被
# `git commit --no-verify` 绕过。治本：扩展已有 create_guard 检测范围——rules/ 下新增
# .yaml 文件单段 name（缺主题前缀）→ 硬阻断。
# 规避自指递归：不新增门禁，只扩展已有 create_guard（同 reconciler 审查标记检测先例）。
# ===========================================================================

class TestRulesYamlNamingBlocked:
    """rules/ 新增 .yaml 单段 name → 硬阻断（ARCH-037 DIM-5 commit-time 强制）。"""

    _RULES_DIR = "docs/01_policies_and_standards/rules"

    def test_single_segment_name_blocked(self, tmp_path: Path) -> None:
        """staged rules/ 下 trae_999_test.yaml（单段 name）→ 阻断。"""
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            f"{self._RULES_DIR}/trae_999_test.yaml",
            "rule_id: trae_999\n",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"rules/ 单段 name .yaml 应被阻断: {detail}"
        assert "ARCH-037" in detail
        assert "DIM-5" in detail
        assert "test" in detail

    def test_compliant_name_passes(self, tmp_path: Path) -> None:
        """staged rules/ 下 trae_999_test_desc.yaml（合规 name）→ 放行。"""
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            f"{self._RULES_DIR}/trae_999_test_desc.yaml",
            "rule_id: trae_999\n",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"rules/ 合规 name .yaml 应放行: {detail}"

    def test_non_rules_dir_yaml_without_token_blocked(self, tmp_path: Path) -> None:
        """staged 非 rules/ 目录 .yaml 无 token → 阻断（扩展 CREATE-GUARD 到 .yaml）。

        病根：.yaml 是配置真源（YAML→DB 单向同步硬约束），第二份 .yaml 配置真源
        的危害比 .py 更隐蔽（同步漂移会污染 9 个 readonly DB 表）。
        治本：扩展 CREATE-GUARD 检测范围到非 rules/ .yaml（rules/ 已有命名检查）。
        """
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "docs/02_other/trae_999_test.yaml",
            "key: value\n",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"非 rules/ 目录 .yaml 无 token 应被阻断: {detail}"
        assert "creation_token" in detail
        assert "造第二真源" in detail

    def test_non_rules_dir_yaml_with_token_passes(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """staged 非 rules/ 目录 .yaml 有 token → 放行。"""
        _init_git_repo(tmp_path)
        yaml_rel = "docs/02_other/trae_999_test_desc.yaml"
        f = _stage_file(tmp_path, yaml_rel, "key: value\n")
        # 写临时 registry（避免触碰真源），登记 token
        registry_file = tmp_path / "registry.yaml"
        registry_file.write_text(
            f"creation_tokens:\n"
            f"  - file: \"{yaml_rel}\"\n"
            f"    token: \"auto-yaml-test-20260701\"\n"
            f"    created_by: \"test\"\n"
            f"    capability: \"test\"\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            registry_file,
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"非 rules/ 目录 .yaml 有 token 应放行: {detail}"

    def test_non_trae_named_yaml_blocked(self, tmp_path: Path) -> None:
        """staged rules/ 下 foo.yaml（非 trae 命名）→ 阻断（红蓝漏洞1修复）。"""
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            f"{self._RULES_DIR}/foo.yaml",
            "key: value\n",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"非 trae 命名 .yaml 应被阻断: {detail}"
        assert "非trae命名" in detail

    def test_rename_to_single_segment_blocked(self, tmp_path: Path) -> None:
        """rename rules/ 合规文件→单段 name → 阻断（红蓝漏洞2修复）。"""
        _init_git_repo(tmp_path)
        # 先 commit 一个合规文件（创建 HEAD 历史）
        old_rel = f"{self._RULES_DIR}/trae_999_old_desc.yaml"
        _stage_file(tmp_path, old_rel, "rule_id: trae_999\n")
        subprocess.run(
            ["git", "commit", "-m", "init rule", "--no-verify"],
            cwd=str(tmp_path), capture_output=True, check=True, timeout=30,
        )
        # rename 为单段 name
        new_rel = f"{self._RULES_DIR}/trae_999_new.yaml"
        subprocess.run(
            ["git", "mv", old_rel, new_rel],
            cwd=str(tmp_path), capture_output=True, check=True, timeout=30,
        )
        new_file = tmp_path / new_rel
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(new_file)])
        assert passed is False, f"rename 到单段 name 应被阻断: {detail}"
        assert "单段name" in detail


# ===========================================================================
# ARCH-031 防复发（2026-07-02）：governance/ 根禁止新增 .py 文件
# 病根：ARCH-031 治本前 governance/ 根平铺 32 个 .py 文件，治本后迁移 24 文件到
# 12 子目录，仅保留 8 个高风险核心模块。防复发：禁止在 governance/ 根直接新增 .py。
# 治本：扩展已有 create_guard 检测范围（不新增门禁，规避自指递归——同 reconciler 先例）。
# ===========================================================================

class TestGovernanceRootNewPyBlocked:
    """governance/ 根新增 .py 文件 → 硬阻断（ARCH-031 防复发）。"""

    def test_governance_root_new_py_blocked(self, tmp_path: Path) -> None:
        """staged src/zephyr/governance/new_module.py → 阻断，提示 ARCH-031 防复发。"""
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/governance/new_anti_relapse_test_module.py",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"governance/ 根新增 .py 应被阻断: {detail}"
        assert "ARCH-031" in detail
        assert "防复发" in detail

    def test_governance_root_rename_blocked(self, tmp_path: Path) -> None:
        """rename 到 governance/ 根 .py → 硬阻断（防 rename 绕过 --diff-filter=A 漏检）。"""
        _init_git_repo(tmp_path)
        # 先在子目录创建并 commit 一个文件，再 rename 到根目录
        src_subdir = tmp_path / "src/zephyr/governance/audit"
        src_subdir.mkdir(parents=True, exist_ok=True)
        original = src_subdir / "original_for_rename_test.py"
        original.write_text("# test\n", encoding="utf-8")
        subprocess.run(["git", "add", str(original)], cwd=tmp_path, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True)
        # rename 到 governance/ 根
        target = tmp_path / "src/zephyr/governance/renamed_to_root_test.py"
        subprocess.run(
            ["git", "mv", str(original), str(target)],
            cwd=tmp_path, check=True,
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(target)])
        assert passed is False, f"rename 到 governance/ 根 .py 应被阻断: {detail}"
        assert "ARCH-031" in detail
        assert "防复发" in detail


class TestGovernanceSubdirNewPyNotAntiRelapse:
    """governance/<subdir>/ 新增 .py 文件不触发 ARCH-031 防复发。"""

    def test_governance_subdir_new_py_not_anti_relapse(self, tmp_path: Path) -> None:
        """staged src/zephyr/governance/audit/new_module.py → 不被 ARCH-031 防复发阻断。

        该文件可能被 token 检测阻断（无 creation_token），但 detail 不应含 "防复发"。
        """
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/governance/audit/new_anti_relapse_subdir_test.py",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        if not passed:
            assert "防复发" not in detail, (
                f"governance 子目录新增 .py 不应触发 ARCH-031 防复发: {detail}"
            )
