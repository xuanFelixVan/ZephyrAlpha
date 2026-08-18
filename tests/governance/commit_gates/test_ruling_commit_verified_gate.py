# [A_test] module_id: MOD-GOV_ruling_commit_verified_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ENFORCEMENT | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ARCH-WORKSPACE-DRIFT-SYSTEMIC-001
# [MODULE] tests.governance.commit_gates.test_ruling_commit_verified_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_ENFORCEMENT | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_ruling_commit_verified_gate.py — RULING-COMMIT-VERIFIED 门禁单测。

#ARCH-WORKSPACE-DRIFT-SYSTEMIC-001 Phase 3（2026-07-20）。

测试 make_ruling_commit_verified_gate() 的 6 个核心场景：
- 触发文件检测（ruling_*.md / architecture_issue_registry.yaml）
- 正则提取"已完成...commit XXX"声明
- diff-based 新增声明检测（HEAD vs current）
- commit hash 真实性验证（git cat-file -e）
- 逃生通道 [no-verify-ruling:<reason>]
- fail-closed 阻断

测试隔离：用 tmp_path + 真实 git 仓库（end-to-end）。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.gov_enforcement.commit_gates.ruling_commit_verified_gate import (  # noqa: E402
    _ESCAPE_MARKER,
    _RULING_COMMIT_RE,
    _extract_commit_hashes,
    _is_trigger_file,
    _verify_commit_exists,
    make_ruling_commit_verified_gate,
)

# ============================================================================
# 辅助函数
# ============================================================================


def _git_env() -> dict:
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    return env


def _init_git_repo(repo_dir: Path) -> None:
    """初始化 git 仓库（含 scripts/governance/d1_structure 标记为 Zephyr 项目）。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = _git_env()
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    # 标记为 Zephyr 项目（gate 用 scripts/governance/d1_structure 判断）
    (repo_dir / "scripts" / "governance" / "d1_structure").mkdir(parents=True, exist_ok=True)
    (repo_dir / "scripts" / "governance" / "d1_structure" / ".gitkeep").write_text("", encoding="utf-8")


def _commit_file(repo_dir: Path, rel_path: str, content: str) -> str:
    """创建/修改文件并 commit，返回 commit hash。"""
    env = _git_env()
    fpath = repo_dir / rel_path
    fpath.parent.mkdir(parents=True, exist_ok=True)
    fpath.write_text(content, encoding="utf-8")
    subprocess.run(
        ["git", "add", rel_path],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"add {rel_path}"],
        cwd=str(repo_dir), capture_output=True, env=env, check=True,
    )
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_dir), capture_output=True, text=True, env=env, check=True,
    )
    return r.stdout.strip()


def _get_head_hash(repo_dir: Path) -> str:
    """获取当前 HEAD commit hash。"""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo_dir), capture_output=True, text=True, check=True,
    )
    return r.stdout.strip()


def _make_gateway(project_root: Path, commit_message: str = "") -> MagicMock:
    """构造 mock gateway，含 project_root。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


# ============================================================================
# 正则提取测试
# ============================================================================


class TestExtractCommitHashes:
    """_extract_commit_hashes 正则提取测试。"""

    def test_simple_format(self):
        """已完成（commit fadd3fdc）"""
        content = "Phase 1 已完成（commit fadd3fdc）"
        hashes = _extract_commit_hashes(content)
        assert hashes == {"fadd3fdc"}

    def test_date_format(self):
        """已完成 2026-07-20，commit 2cee176f81，merge ..."""
        content = "Phase 1 已完成 2026-07-20，commit 2cee176f81，merge 4a0d46508b"
        hashes = _extract_commit_hashes(content)
        assert hashes == {"2cee176f81"}

    def test_multiple_hashes(self):
        """多个"已完成"声明"""
        content = """
        Phase 1 已完成（commit 290df512）
        Phase 2 已完成（commit 0a69d345）
        """
        hashes = _extract_commit_hashes(content)
        assert hashes == {"290df512", "0a69d345"}

    def test_no_match(self):
        """无"已完成"声明"""
        content = "Phase 1 待完成"
        hashes = _extract_commit_hashes(content)
        assert hashes == set()

    def test_short_hash_7_chars(self):
        """7 字符短 hash"""
        content = "已完成（commit abc1234）"
        hashes = _extract_commit_hashes(content)
        assert hashes == {"abc1234"}

    def test_full_hash_40_chars(self):
        """40 字符完整 hash"""
        full_hash = "a" * 40
        content = f"已完成（commit {full_hash}）"
        hashes = _extract_commit_hashes(content)
        assert hashes == {full_hash}

    def test_too_short_hash_ignored(self):
        """6 字符 hash 不匹配（要求 7-40）"""
        content = "已完成（commit abc123）"
        hashes = _extract_commit_hashes(content)
        assert hashes == set()

    def test_case_insensitive_commit(self):
        """COMMIT/Commit 大小写不敏感"""
        content = "已完成（COMMIT fadd3fdc）"
        hashes = _extract_commit_hashes(content)
        assert hashes == {"fadd3fdc"}

    def test_multiline_block_scalar(self):
        """多行 block scalar 中"已完成...commit"跨行"""
        content = """fix_phase: |
  Phase 1 紧急止血（已完成
  2026-07-19，commit 2cee176f81）：
    - 恢复 import
  """
        hashes = _extract_commit_hashes(content)
        assert "2cee176f81" in hashes


# ============================================================================
# 触发文件检测测试
# ============================================================================


class TestIsTriggerFile:
    """_is_trigger_file 路径匹配测试。"""

    def test_ruling_md(self):
        assert _is_trigger_file("docs/02_enterprise_architecture/ruling_test.md") is True

    def test_ruling_md_subpath(self):
        assert _is_trigger_file("docs/02_enterprise_architecture/ruling_100pct_ai_governance_hardening.md") is True

    def test_architecture_issue_registry(self):
        assert _is_trigger_file(
            "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"
        ) is True

    def test_non_trigger_py(self):
        assert _is_trigger_file("src/zephyr/foo.py") is False

    def test_non_trigger_other_md(self):
        assert _is_trigger_file("docs/02_enterprise_architecture/other.md") is False

    def test_windows_backslash(self):
        """Windows 反斜杠路径"""
        assert _is_trigger_file(
            "docs\\02_enterprise_architecture\\ruling_test.md"
        ) is True


# ============================================================================
# commit hash 存在性验证测试
# ============================================================================


class TestVerifyCommitExists:
    """_verify_commit_exists 真实 git 仓库验证。"""

    def test_existing_commit(self, tmp_path: Path):
        """存在的 commit hash → True"""
        _init_git_repo(tmp_path)
        h = _commit_file(tmp_path, "foo.txt", "bar\n")
        # 用完整 hash 或短 hash
        assert _verify_commit_exists(tmp_path, h) is True
        assert _verify_commit_exists(tmp_path, h[:7]) is True

    def test_nonexistent_hash(self, tmp_path: Path):
        """不存在的 hash → False"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "foo.txt", "bar\n")
        assert _verify_commit_exists(tmp_path, "deadbeef") is False

    def test_invalid_format(self, tmp_path: Path):
        """非法格式 hash → False"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "foo.txt", "bar\n")
        assert _verify_commit_exists(tmp_path, "not-a-hash") is False


# ============================================================================
# Gate 集成测试
# ============================================================================


class TestRulingCommitVerifiedGate:
    """make_ruling_commit_verified_gate 集成测试。"""

    def test_valid_new_commit_hash_passes(self, tmp_path: Path):
        """新增"已完成"声明中的 commit hash 存在 → pass"""
        _init_git_repo(tmp_path)
        # 先创建一个 commit 获取其 hash
        real_hash = _commit_file(tmp_path, "foo.txt", "bar\n")
        short_hash = real_hash[:7]

        # 创建 ruling 文档，引用这个 hash
        ruling_path = "docs/02_enterprise_architecture/ruling_test.md"
        ruling_content = f"# 裁定\n\nPhase 1 已完成（commit {short_hash}）\n"
        _commit_file(tmp_path, ruling_path, ruling_content)

        # 修改 ruling 文档，添加新的"已完成"声明
        # 由于 ruling 文档已经在 HEAD 中，需要修改后再 stage
        new_content = ruling_content + f"\nPhase 2 已完成（commit {short_hash}）\n"
        (tmp_path / ruling_path).write_text(new_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(gateway, [str(tmp_path / ruling_path)])
        assert passed is True, f"valid hash should pass: {detail}"

    def test_invalid_new_commit_hash_blocked(self, tmp_path: Path):
        """新增"已完成"声明中的 commit hash 不存在 → fail-closed 阻断"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "foo.txt", "bar\n")

        ruling_path = "docs/02_enterprise_architecture/ruling_test.md"
        ruling_content = "# 裁定\n\nPhase 1 待完成\n"
        _commit_file(tmp_path, ruling_path, ruling_content)

        # 修改 ruling 文档，添加不存在的 hash
        new_content = ruling_content + "\nPhase 2 已完成（commit deadbeef）\n"
        (tmp_path / ruling_path).write_text(new_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(gateway, [str(tmp_path / ruling_path)])
        assert passed is False
        assert "RULING_COMMIT_VERIFIED_VIOLATION" in detail
        assert "deadbeef" in detail

    def test_existing_declaration_not_blocked(self, tmp_path: Path):
        """HEAD 已存在的"已完成"声明不阻断（diff-based）"""
        _init_git_repo(tmp_path)
        real_hash = _commit_file(tmp_path, "foo.txt", "bar\n")
        short_hash = real_hash[:7]

        ruling_path = "docs/02_enterprise_architecture/ruling_test.md"
        # 初始 ruling 已含"已完成"声明
        ruling_content = f"# 裁定\n\nPhase 1 已完成（commit {short_hash}）\n"
        _commit_file(tmp_path, ruling_path, ruling_content)

        # 修改 ruling 文档但不改"已完成"声明（只改其他内容）
        new_content = ruling_content + "\n# 新增章节\n\n这是新内容。\n"
        (tmp_path / ruling_path).write_text(new_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(gateway, [str(tmp_path / ruling_path)])
        assert passed is True, f"existing declaration should not be blocked: {detail}"

    def test_new_file_all_declarations_treated_as_new(self, tmp_path: Path):
        """新文件（HEAD 不存在）的全部声明视为新增"""
        _init_git_repo(tmp_path)
        real_hash = _commit_file(tmp_path, "foo.txt", "bar\n")
        short_hash = real_hash[:7]

        # 创建新 ruling 文件（不在 HEAD 中），含有效 hash
        ruling_path = "docs/02_enterprise_architecture/ruling_new.md"
        ruling_content = f"# 裁定\n\nPhase 1 已完成（commit {short_hash}）\n"
        fpath = tmp_path / ruling_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(ruling_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(gateway, [str(tmp_path / ruling_path)])
        assert passed is True, f"new file with valid hash should pass: {detail}"

    def test_new_file_with_invalid_hash_blocked(self, tmp_path: Path):
        """新文件含无效 hash → 阻断"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "foo.txt", "bar\n")

        ruling_path = "docs/02_enterprise_architecture/ruling_new.md"
        ruling_content = "# 裁定\n\nPhase 1 已完成（commit deadbeef）\n"
        fpath = tmp_path / ruling_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(ruling_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(gateway, [str(tmp_path / ruling_path)])
        assert passed is False
        assert "deadbeef" in detail

    def test_non_trigger_file_skipped(self, tmp_path: Path):
        """非触发文件 → skip"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "foo.txt", "bar\n")

        # 普通文件含"已完成"声明但不是触发文件
        other_path = "src/foo.py"
        other_content = "# 已完成（commit deadbeef）\nx = 1\n"
        (tmp_path / other_path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / other_path).write_text(other_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, _ = gate.check(gateway, [str(tmp_path / other_path)])
        assert passed is True  # 非触发文件 skip

    def test_escape_marker_in_commit_message(self, tmp_path: Path):
        """commit message 含 [no-verify-ruling:<reason>] → skip"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "foo.txt", "bar\n")

        ruling_path = "docs/02_enterprise_architecture/ruling_new.md"
        ruling_content = "# 裁定\n\nPhase 1 已完成（commit deadbeef）\n"
        fpath = tmp_path / ruling_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(ruling_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(
            gateway,
            [str(tmp_path / ruling_path)],
            commit_message="test [no-verify-ruling:dummy reason]",
        )
        assert passed is True
        assert "escape" in detail.lower()

    def test_non_zephyr_project_skipped(self, tmp_path: Path):
        """非 Zephyr 项目（无 scripts/governance/d1_structure）→ skip"""
        repo_dir = tmp_path / "non-zephyr"
        repo_dir.mkdir(parents=True, exist_ok=True)
        env = _git_env()
        subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(repo_dir), capture_output=True, env=env, check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=str(repo_dir), capture_output=True, env=env, check=True,
        )

        ruling_path = "docs/02_enterprise_architecture/ruling_test.md"
        ruling_content = "# 已完成（commit deadbeef）\n"
        (repo_dir / ruling_path).parent.mkdir(parents=True, exist_ok=True)
        (repo_dir / ruling_path).write_text(ruling_content, encoding="utf-8")

        gateway = _make_gateway(repo_dir)
        gate = make_ruling_commit_verified_gate()
        passed, _ = gate.check(gateway, [str(repo_dir / ruling_path)])
        assert passed is True  # 非 Zephyr 项目 skip

    def test_architecture_issue_registry_yaml_triggered(self, tmp_path: Path):
        """architecture_issue_registry.yaml 触发检测"""
        _init_git_repo(tmp_path)
        real_hash = _commit_file(tmp_path, "foo.txt", "bar\n")
        short_hash = real_hash[:7]

        registry_path = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"
        registry_content = "entries:\n  - issue_id: '#ARCH-TEST-001'\n    status: resolved\n"
        _commit_file(tmp_path, registry_path, registry_content)

        # 添加含无效 hash 的"已完成"声明
        new_content = registry_content + "    fix_phase: 已完成（commit deadbeef）\n"
        (tmp_path / registry_path).write_text(new_content, encoding="utf-8")

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(gateway, [str(tmp_path / registry_path)])
        assert passed is False
        assert "deadbeef" in detail

    def test_multiple_files_violations_aggregated(self, tmp_path: Path):
        """多个文件违规 → 聚合详情"""
        _init_git_repo(tmp_path)
        _commit_file(tmp_path, "foo.txt", "bar\n")

        # 两个 ruling 文件都含无效 hash
        ruling1_path = "docs/02_enterprise_architecture/ruling_a.md"
        ruling2_path = "docs/02_enterprise_architecture/ruling_b.md"

        (tmp_path / ruling1_path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / ruling1_path).write_text(
            "# 已完成（commit aaaaaaa）\n", encoding="utf-8",
        )
        (tmp_path / ruling2_path).write_text(
            "# 已完成（commit bbbbbbb）\n", encoding="utf-8",
        )

        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, detail = gate.check(
            gateway,
            [str(tmp_path / ruling1_path), str(tmp_path / ruling2_path)],
        )
        assert passed is False
        assert "aaaaaaa" in detail
        assert "bbbbbbb" in detail

    def test_empty_files_list_passes(self, tmp_path: Path):
        """空 files 列表 → pass"""
        _init_git_repo(tmp_path)
        gateway = _make_gateway(tmp_path)
        gate = make_ruling_commit_verified_gate()
        passed, _ = gate.check(gateway, [])
        assert passed is True


# ============================================================================
# GateSpec 元数据测试
# ============================================================================


class TestGateSpecMetadata:
    """GateSpec 元数据正确性。"""

    def test_gate_id(self):
        gate = make_ruling_commit_verified_gate()
        assert gate.gate_id == "RULING-COMMIT-VERIFIED"

    def test_priority(self):
        gate = make_ruling_commit_verified_gate()
        # priority=109：原 77 与 BLUEPRINT-FORMAT 撞号（#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 1 治本）
        assert gate.priority == 109

    def test_check_callable(self):
        gate = make_ruling_commit_verified_gate()
        assert callable(gate.check)


# ============================================================================
# 逃生通道标记测试
# ============================================================================


class TestEscapeMarker:
    """逃生通道标记检测。"""

    def test_escape_marker_constant(self):
        assert _ESCAPE_MARKER == "[no-verify-ruling:"

    def test_escape_marker_in_message(self):
        """commit message 含标记 → 检测到"""
        from zephyr.gov_enforcement.commit_gates.ruling_commit_verified_gate import (
            _check_escape_marker,
        )
        assert _check_escape_marker({"commit_message": "test [no-verify-ruling:reason]"}) is True

    def test_escape_marker_not_in_message(self):
        """commit message 不含标记 → 未检测到"""
        from zephyr.gov_enforcement.commit_gates.ruling_commit_verified_gate import (
            _check_escape_marker,
        )
        assert _check_escape_marker({"commit_message": "normal commit"}) is False

    def test_escape_marker_empty_message(self):
        """空 commit message → 未检测到"""
        from zephyr.gov_enforcement.commit_gates.ruling_commit_verified_gate import (
            _check_escape_marker,
        )
        assert _check_escape_marker({"commit_message": ""}) is False
        assert _check_escape_marker({}) is False
