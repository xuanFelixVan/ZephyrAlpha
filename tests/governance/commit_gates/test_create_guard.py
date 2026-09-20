# [BLUEPRINT] MOD-GOV_CREATE_GUARD | tests/test_create_guard.py | §create-guard-tests
# [MODULE] tests.test_create_guard
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.create_guard, zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——使用 tmp_path 临时 git 仓库，不读/不写真实 registry（create_guard 自己读真实 registry，测试用唯一名避免冲突）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=MOD-GOV_CREATE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_create_guard.py — CREATE-GUARD 门禁单元测试（2026-06-30 治本补全）

覆盖 create_guard.check 的核心场景：
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

from zephyr.gov_enforcement.commit_gates.create_guard import make_create_guard  # noqa: E402
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
    subprocess.run(
        ["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, env=env, check=True, timeout=30
    )
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
            "src/zephyr/gov_enforcement/commit_gates/__create_guard_test_fake_20260630__.py",
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
    """非 .py 文件检测（阶段 2 治本 ARCH-TTL-DOC-001：全 7 格式覆盖）。"""

    def test_md_file_blocked_without_token(self, tmp_path: Path) -> None:
        """staged 新增 .md 文件无 creation_token → 硬阻断（阶段 2 治本）。"""
        _init_git_repo(tmp_path)
        f = _stage_file(tmp_path, "docs/__create_guard_test_md_fake_20260717__.md", "# readme\n")
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"无 token 的新增 .md 应被阻断: {detail}"
        assert "creation_token" in detail
        assert "造第二真源" in detail

    def test_md_file_passes_with_token(self, tmp_path: Path, monkeypatch) -> None:
        """staged 新增 .md 文件有 creation_token → 通过（阶段 2 治本）。"""
        _init_git_repo(tmp_path)
        f = _stage_file(tmp_path, "docs/__create_guard_test_md_registered_20260717__.md", "# readme\n")
        import yaml

        registry_data = {
            "creation_tokens": [
                {
                    "file": "docs/__create_guard_test_md_registered_20260717__.md",
                    "token": "auto-test-md-20260717",
                    "created_by": "test",
                    "capability": "test_md",
                }
            ]
        }
        reg_path = tmp_path / "test_registry.yaml"
        reg_path.write_text(yaml.dump(registry_data), encoding="utf-8")
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            reg_path,
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"有 token 的新增 .md 应通过: {detail}"


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
            "src/zephyr/gov_enforcement/commit_gates/__create_guard_test_fake_20260630__.py",
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
            "src/zephyr/gov_enforcement/commit_gates/__create_guard_test_fake_20260630__.py",
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

    def test_git_diff_nonzero_returncode_blocks(self, tmp_path: Path, monkeypatch) -> None:
        """git diff returncode=1 → passed=False + detail 含修复指引。"""
        from unittest.mock import MagicMock

        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/gov_enforcement/commit_gates/__create_guard_test_fake_20260630__.py",
        )
        # mock gateway.run_git 返回 returncode=1（git diff 失败）
        gw = MagicMock()
        gw.project_root = tmp_path
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        gw.run_git.return_value = mock_result
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"git diff 失败应 fail-closed 阻断: {detail}"
        assert "fail-closed" in detail
        assert "git diff" in detail

    def test_git_diff_exception_blocks(self, tmp_path: Path, monkeypatch) -> None:
        """git diff 抛异常 → passed=False + detail 含修复指引。"""
        from unittest.mock import MagicMock

        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/gov_enforcement/commit_gates/__create_guard_test_fake_20260630__.py",
        )
        gw = MagicMock()
        gw.project_root = tmp_path
        gw.run_git.side_effect = RuntimeError("git down")
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

    def _setup_reconciler_registry(self, repo_dir: Path, head_content: str, staged_content: str) -> Path:
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
            cwd=str(repo_dir),
            capture_output=True,
            env=env,
            check=True,
            timeout=30,
        )
        subprocess.run(
            ["git", "commit", "-m", "head version", "--no-verify"],
            cwd=str(repo_dir),
            capture_output=True,
            env=env,
            check=True,
            timeout=30,
        )
        # staged 修改版
        f.write_text(staged_content, encoding="utf-8")
        subprocess.run(
            ["git", "add", self._RECONCILER_REL],
            cwd=str(repo_dir),
            capture_output=True,
            env=env,
            check=True,
            timeout=30,
        )
        return f

    def test_new_reconciler_without_marker_blocked(self, tmp_path: Path) -> None:
        """staged 新增 make_test_reconciler 无 # trae_060-reviewed 标记 → 阻断。"""
        _init_git_repo(tmp_path)
        head = '"""mod"""\n\ndef make_existing_reconciler():\n    pass\n'
        staged = '"""mod"""\n\ndef make_existing_reconciler():\n    pass\n\ndef make_test_reconciler():\n    pass\n'
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
            "def make_existing_reconciler():\n    pass\n\n"
            "# trae_060-reviewed: 该存在+治本\n"
            "def make_test_reconciler():\n    pass\n"
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
        """commit 不含 reconciliation_registry.py → 通过（不触发检测）。

        用 .txt 占位——阶段 2 治本（ARCH-TTL-DOC-001）后 .md/.sh/.ps1/.mmd/.json
        新建需 creation_token，.txt 不在 CREATE-GUARD 检测范围。
        """
        _init_git_repo(tmp_path)
        f = _stage_file(tmp_path, "docs/readme.txt", "readme\n")
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

    def test_non_rules_dir_yaml_with_token_passes(self, tmp_path: Path, monkeypatch) -> None:
        """staged 非 rules/ 目录 .yaml 有 token → 放行。"""
        _init_git_repo(tmp_path)
        yaml_rel = "docs/02_other/trae_999_test_desc.yaml"
        f = _stage_file(tmp_path, yaml_rel, "key: value\n")
        # 写临时 registry（避免触碰真源），登记 token
        registry_file = tmp_path / "registry.yaml"
        registry_file.write_text(
            f"creation_tokens:\n"
            f'  - file: "{yaml_rel}"\n'
            f'    token: "auto-yaml-test-20260701"\n'
            f'    created_by: "test"\n'
            f'    capability: "test"\n',
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
            cwd=str(tmp_path),
            capture_output=True,
            check=True,
            timeout=30,
        )
        # rename 为单段 name
        new_rel = f"{self._RULES_DIR}/trae_999_new.yaml"
        subprocess.run(
            ["git", "mv", old_rel, new_rel],
            cwd=str(tmp_path),
            capture_output=True,
            check=True,
            timeout=30,
        )
        new_file = tmp_path / new_rel
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(new_file)])
        assert passed is False, f"rename 到单段 name 应被阻断: {detail}"
        assert "单段name" in detail


# ===========================================================================
# ARCH-031 防复发（2026-07-02）：governance/ 根禁止新增 .py 文件
# 病根：ARCH-031 治本前 governance/ 根平铺 32 个 .py 文件，治本后迁移到子目录，
# 仅保留高风险核心模块（__init__/capability_lookup/depgraph_schema/evidence_pack/
# integrity/rule_patterns）。2026-07-17 shim 消除 commit 213be2b5a3 删除
# base/merkle_hourly/performance_attribution_report，当前根 .py 文件数稳定为 6（含 __init__）。
# 防复发：禁止在 governance/ 根直接新增 .py（清单随治本进化，真源在磁盘现有文件）。
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
            cwd=tmp_path,
            check=True,
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
        """staged src/zephyr/gov_audit/new_module.py → 不被 ARCH-031 防复发阻断。

        该文件可能被 token 检测阻断（无 creation_token），但 detail 不应含 "防复发"。
        """
        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/gov_audit/new_anti_relapse_subdir_test.py",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        if not passed:
            assert "防复发" not in detail, f"governance 子目录新增 .py 不应触发 ARCH-031 防复发: {detail}"


# ===========================================================================
# 裁定#216 回归测试覆盖先行：补充未覆盖分支测试（类名唯一性 + 字段头完整性）
# 病根：原 21 测试覆盖 Block 1-7 + Block 9 (creation_token)，但 Block 8 (类名唯一性)
# 和 Block 10 (字段头完整性) 的 violation 路径从未被测试。Extract Method 重构前
# MUST 补充分支测试，确保重构后 violation 路径行为等价。
# ===========================================================================


class TestClassUniquenessBlocked:
    """类名跨模块冲突 → 硬阻断（ARCH-034 CLASS-UNIQUENESS）。

    Block 8 violation 路径覆盖：staged .py 定义与已 tracked 文件同名的 class。
    """

    def test_class_name_conflict_blocks(self, tmp_path: Path) -> None:
        """staged .py 定义 class 与已 commit 文件同名 class → 阻断。"""
        _init_git_repo(tmp_path)
        # 1. 先 commit 一个已有文件，定义 _TestConflictClass20260715
        existing = tmp_path / "src/zephyr/gov_enforcement/existing_module_for_test.py"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("class _TestConflictClass20260715:\n    pass\n", encoding="utf-8")
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        subprocess.run(
            ["git", "add", "src/zephyr/gov_enforcement/existing_module_for_test.py"],
            cwd=str(tmp_path),
            capture_output=True,
            timeout=30,
            env=env,
        )
        subprocess.run(
            ["git", "commit", "-m", "add existing", "--no-verify"],
            cwd=str(tmp_path),
            capture_output=True,
            timeout=30,
            env=env,
        )
        # 2. Stage 新文件，定义同名 class（无 alias 标记）
        f = _stage_file(
            tmp_path,
            "src/zephyr/gov_enforcement/commit_gates/__test_class_conflict_20260715__.py",
            "class _TestConflictClass20260715:\n    pass\n",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"类名冲突应被阻断: {detail}"
        assert "CLASS-UNIQUENESS" in detail or "类名" in detail

    def test_class_name_with_alias_marker_passes(self, tmp_path: Path) -> None:
        """staged .py 定义同名 class 但有 '# class-name-alias' 标记 → 通过（合法 re-export）。"""
        _init_git_repo(tmp_path)
        existing = tmp_path / "src/zephyr/gov_enforcement/existing_module_for_test2.py"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("class _TestAliasedClass20260715:\n    pass\n", encoding="utf-8")
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@test.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@test.com"
        subprocess.run(
            ["git", "add", "src/zephyr/gov_enforcement/existing_module_for_test2.py"],
            cwd=str(tmp_path),
            capture_output=True,
            timeout=30,
            env=env,
        )
        subprocess.run(
            ["git", "commit", "-m", "add existing2", "--no-verify"],
            cwd=str(tmp_path),
            capture_output=True,
            timeout=30,
            env=env,
        )
        # Stage 新文件，定义同名 class 但有 alias 标记
        f = _stage_file(
            tmp_path,
            "src/zephyr/gov_enforcement/commit_gates/__test_class_alias_20260715__.py",
            "# class-name-alias: legitimate re-export for testing\nclass _TestAliasedClass20260715:\n    pass\n",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        # 应通过类名检测（有 alias 标记），但可能被后续 token 检测阻断
        # 关键断言：不因 CLASS-UNIQUENESS 被阻断
        if not passed:
            assert "CLASS-UNIQUENESS" not in detail, f"有 alias 标记的类名不应触发 CLASS-UNIQUENESS: {detail}"


class TestFieldHeaderIncomplete:
    """字段头部不完整 → 硬阻断（ARCH-031 14字段治本）。

    Block 10 violation 路径覆盖：staged .py 文件头部缺字段标注。
    需要先通过 Block 9 (creation_token)，所以 mock registry 登记该文件。
    """

    def test_missing_fields_blocks(self, tmp_path: Path, monkeypatch) -> None:
        """staged .py 有 token 但缺字段头 → 阻断（ARCH-031 字段头完整性）。"""
        _init_git_repo(tmp_path)
        rel = "src/zephyr/gov_enforcement/commit_gates/__test_field_header_20260715__.py"
        f = _stage_file(tmp_path, rel, "x = 1\n")  # 无任何字段标注
        # mock registry 登记此文件（通过 Block 9 creation_token 检测）
        registry_file = tmp_path / "registry.yaml"
        registry_file.write_text(
            f"creation_tokens:\n"
            f'  - file: "{rel}"\n'
            f'    token: "auto-field-header-test-20260715"\n'
            f'    created_by: "test"\n'
            f'    capability: "test"\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            registry_file,
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"缺字段头应被阻断: {detail}"
        assert "字段头部" in detail or "ARCH-031" in detail


# ===========================================================================
# B1 撕裂读重试（2026-09-16，st-commitspeed）
# 病根：并发会话写 capability registry 时存在瞬态撕裂读，单次 yaml.safe_load
# 失败即 fail-closed 会把"设施瞬态故障"误报成"违规阻断"（假阳性阻断无辜提交人）。
# 治本：读取单点 _read_registry_text + 3 次重试（0.3s 退避）；耗尽仍 fail-closed
# （不变量不动），消息区分「设施故障（非违规）」+ 审计 jsonl 留痕。
# 测试隔离：REGISTRY_YAML monkeypatch 到 tmp_path；审计落 gateway.project_root
# （tmp git repo）下的 .runtime/audit/，不触碰生产 .runtime/。
# ===========================================================================


class TestRegistryTornReadRetry:
    """B1：registry 撕裂读重试——先坏后好放行；恒坏阻断且落审计。"""

    def test_transient_tear_retries_then_passes(self, tmp_path: Path, monkeypatch) -> None:
        """第 1 次读撕裂（坏 YAML）、第 2 次读恢复 → 重试后放行，恰读 2 次。"""
        import zephyr.gov_enforcement.commit_gates.create_guard as _cg

        _init_git_repo(tmp_path)
        rel = "docs/__test_torn_read_md_20260916__.md"
        f = _stage_file(tmp_path, rel, "# readme\n")
        registry_file = tmp_path / "torn_read_registry.yaml"
        registry_file.write_text(
            f"creation_tokens:\n"
            f'  - file: "{rel}"\n'
            f'    token: "auto-torn-read-20260916"\n'
            f'    created_by: "test"\n'
            f'    capability: "test"\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            registry_file,
        )
        # monkeypatch 读取单点：第 1 次返回撕裂内容，第 2 次起返回真实文件内容
        calls = {"n": 0}
        _real_read = _cg._read_registry_text

        def _flaky_read(path):
            calls["n"] += 1
            if calls["n"] == 1:
                return "invalid: yaml: torn: content:"  # 撕裂窗口读到的半截写入
            return _real_read(path)

        monkeypatch.setattr(_cg, "_read_registry_text", _flaky_read)

        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is True, f"瞬态撕裂读重试后应放行: {detail}"
        assert calls["n"] == 2, f"应恰读 2 次（坏1次+好1次），实际 {calls['n']} 次"

    def test_persistent_tear_blocks_with_infra_audit(self, tmp_path: Path, monkeypatch) -> None:
        """恒坏（3 次重试全失败）→ fail-closed 阻断，消息含设施故障 + 审计落 tmp_path。"""
        import json as _json

        _init_git_repo(tmp_path)
        f = _stage_file(
            tmp_path,
            "src/zephyr/gov_enforcement/commit_gates/__test_torn_read_bad_20260916__.py",
        )
        bad_registry = tmp_path / "bad_registry_torn.yaml"
        bad_registry.write_text("invalid: yaml: content:", encoding="utf-8")
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            bad_registry,
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        passed, detail = gate.check(gw, [str(f)])
        assert passed is False, f"恒坏 registry 应 fail-closed 阻断: {detail}"
        assert "设施故障" in detail
        assert "非违规" in detail
        # 审计落 tmp_path（gateway.project_root = tmp git repo，不写生产 .runtime/）
        audit_path = tmp_path / ".runtime" / "audit" / "create_guard_parse_fail.jsonl"
        assert audit_path.exists(), f"审计文件应落 tmp_path: {audit_path}"
        lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
        assert lines, "审计 jsonl 应有记录"
        record = _json.loads(lines[-1])
        assert record["event"] == "registry_parse_fail"
        assert str(bad_registry) in record["path"]
        assert record["reason"]  # 非空 reason（截前 200 字）


# ===========================================================================
# 裁定#375 内收判据门禁化（2026-09-20，P9③）：新建资产 token 条目缺
# merge_evaluation 字段 → warn+审计（首期 warn-only 不阻断——硬阻断会把存量
# token 全打红，留过渡窗由季度审计评估升级）。
# 检测面=own-scope（本提交文件面，非 tests/）。用 .yaml 资产验证（同走
# _filter_new_py_and_yaml → _filter_to_commit_files 管线，.py 同路径）。
# ===========================================================================


class TestMergeEvaluationWarn:
    """裁定#375：merge_evaluation 缺失两态 + own-scope 过滤验证。"""

    _AUDIT_REL = Path(".runtime") / "gate_audit" / "create_guard_merge_evaluation.jsonl"

    @staticmethod
    def _write_registry(tmp_path: Path, yaml_rel: str, merge_evaluation: str | None) -> None:
        """写临时 registry（token 条目带/不带 merge_evaluation 字段）。"""
        me_line = f'    merge_evaluation: "{merge_evaluation}"\n' if merge_evaluation is not None else ""
        registry_file = tmp_path / "registry.yaml"
        registry_file.write_text(
            f"creation_tokens:\n"
            f'  - file: "{yaml_rel}"\n'
            f'    token: "auto-me-test-20260920"\n'
            f'    created_by: "test"\n'
            f'    capability: "test"\n'
            f"{me_line}",
            encoding="utf-8",
        )

    def test_without_merge_evaluation_warns_but_passes(self, tmp_path: Path, monkeypatch, caplog) -> None:
        """红证①：无 merge_evaluation 字段 → passed=True + warn（#375）+ 审计 jsonl 落盘。"""
        import json as _json
        import logging as _logging

        _init_git_repo(tmp_path)
        yaml_rel = "docs/02_other/me_test_missing_20260920.yaml"
        f = _stage_file(tmp_path, yaml_rel, "key: value\n")
        self._write_registry(tmp_path, yaml_rel, merge_evaluation=None)
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            tmp_path / "registry.yaml",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        with caplog.at_level(_logging.WARNING, logger="zephyr.gov_enforcement.commit_gates.create_guard"):
            passed, detail = gate.check(gw, [str(f)], session_id="st-test-me-20260920")
        assert passed is True, f"缺 merge_evaluation 应 warn 不阻断（首期 warn-only）: {detail}"
        assert "merge_evaluation" in caplog.text, "warn 应出现在输出（logger.warning）"
        assert "#375" in caplog.text
        # 审计落 tmp_path（gateway.project_root = tmp git repo，不写生产 .runtime/）
        audit_path = tmp_path / self._AUDIT_REL
        assert audit_path.is_file(), f"审计文件应落 tmp_path: {audit_path}"
        record = _json.loads(audit_path.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert record["event"] == "merge_evaluation_missing"
        assert record["session_id"] == "st-test-me-20260920"
        assert yaml_rel in record["missing_files"]
        assert record["missing_count"] == 1

    def test_with_merge_evaluation_zero_warn(self, tmp_path: Path, monkeypatch, caplog) -> None:
        """红证②：有 merge_evaluation 字段 → passed=True 零 warn 零审计。"""
        import logging as _logging

        _init_git_repo(tmp_path)
        yaml_rel = "docs/02_other/me_test_present_20260920.yaml"
        f = _stage_file(tmp_path, yaml_rel, "key: value\n")
        self._write_registry(
            tmp_path,
            yaml_rel,
            merge_evaluation="grep+计划任务+注册表三查零同域消费方，新对象",
        )
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            tmp_path / "registry.yaml",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        with caplog.at_level(_logging.WARNING, logger="zephyr.gov_enforcement.commit_gates.create_guard"):
            passed, detail = gate.check(gw, [str(f)], session_id="st-test-me-20260920")
        assert passed is True, f"有 merge_evaluation 应零 warn 放行: {detail}"
        assert "#375" not in caplog.text, f"不应出现 #375 warn: {caplog.text}"
        assert not (tmp_path / self._AUDIT_REL).exists(), "不应写审计 jsonl"

    def test_own_scope_foreign_new_yaml_not_warned(self, tmp_path: Path, monkeypatch, caplog) -> None:
        """own-scope 过滤验证：staged 新建件缺字段但不在本提交 files 面 → 不查不 warn。"""
        import logging as _logging

        _init_git_repo(tmp_path)
        # b.yaml：他会话 staged 的新建件（token 无 merge_evaluation），但不在本次 commit 范围
        _stage_file(tmp_path, "docs/02_other/me_test_foreign_20260920.yaml", "key: value\n")
        # a.txt：本次要 commit 的文件（非资产格式）
        f_a = _stage_file(tmp_path, "a.txt", "hello\n")
        self._write_registry(tmp_path, "docs/02_other/me_test_foreign_20260920.yaml", merge_evaluation=None)
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            tmp_path / "registry.yaml",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        with caplog.at_level(_logging.WARNING, logger="zephyr.gov_enforcement.commit_gates.create_guard"):
            passed, detail = gate.check(gw, [str(f_a)], session_id="st-test-me-20260920")
        assert passed is True, f"外来 staged 新建件不应误判: {detail}"
        assert "#375" not in caplog.text, f"own-scope 外新建件不应触发 warn: {caplog.text}"
        assert not (tmp_path / self._AUDIT_REL).exists(), "不应写审计 jsonl"

    def test_blank_merge_evaluation_still_warns(self, tmp_path: Path, monkeypatch, caplog) -> None:
        """空串字段视同缺失（值为空白 → warn）。"""
        import logging as _logging

        _init_git_repo(tmp_path)
        yaml_rel = "docs/02_other/me_test_blank_20260920.yaml"
        f = _stage_file(tmp_path, yaml_rel, "key: value\n")
        self._write_registry(tmp_path, yaml_rel, merge_evaluation="   ")
        monkeypatch.setattr(
            "zephyr.governance.capability_lookup.REGISTRY_YAML",
            tmp_path / "registry.yaml",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        gate = make_create_guard()
        with caplog.at_level(_logging.WARNING, logger="zephyr.gov_enforcement.commit_gates.create_guard"):
            passed, detail = gate.check(gw, [str(f)], session_id="st-test-me-20260920")
        assert passed is True
        assert "#375" in caplog.text, "空白值应视同缺失触发 warn"
