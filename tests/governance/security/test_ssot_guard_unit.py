# [A_test] module_id: MOD-GOV_ssot_guard_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-687 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_ssot_guard
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-687 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
单元测试：src/zephyr/hooks/ssot_guard.py
任务 ID : T-1-26（B07）
覆盖指令：356（测试工程师）+ 999（合规验收）

测试矩阵
--------
C-1  新增治理文件 → 注册表未暂存 → 阻断
C-1  新增治理文件 → 注册表已暂存 → 通过
C-1  无新增治理文件               → 通过（跳过）
C-2  注册表暂存，声明路径存在      → 通过
C-2  注册表暂存，声明路径缺失      → 阻断
C-2  注册表文件本身不存在          → 阻断
C-3  删除治理文件 → 注册表未暂存  → 阻断
C-3  删除治理文件 → 注册表已暂存  → 通过
C-3  无删除治理文件               → 通过（跳过）
C-4  注册表未暂存                 → 通过（跳过）
C-4  注册表暂存，路径格式合法      → 通过
C-4  注册表暂存，存在绝对路径      → 阻断
C-4  注册表暂存，存在反斜杠路径    → 阻断

辅助函数
--------
extract_declared_paths  正常提取 / 空文件 / 无匹配
validate_path_format    合法路径 / 绝对路径 / 反斜杠
is_watched              覆盖所有 WATCHED_PREFIXES / 非监控路径 / 非监控扩展名
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from zephyr.shared.security.ssot_guard import (
    REGISTRY_REL_PATH,
    CheckResult,
    GuardReport,
    SsotGuard,
    extract_declared_paths,
    validate_path_format,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """创建一个最小化的伪 git 仓库目录结构。"""
    # 注册表文件
    registry_dir = tmp_path / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    registry_dir.mkdir(parents=True)
    registry_file = registry_dir / "rule_catalog_registry.yaml"
    registry_file.write_text(
        "# test registry\n"
        "systems_overview:\n"
        "  systems:\n"
        "    - id: S01\n"
        "      core_file: docs/subsystem-registry.yaml\n"
        "      path: scripts/hooks/doc_guard.py\n",
        encoding="utf-8",
    )
    # 实际存在的文件，供 C-2 测试引用
    hooks_dir = tmp_path / "scripts" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "doc_guard.py").write_text("# guard\n", encoding="utf-8")
    # subsystem-registry 也得存在
    (tmp_path / "docs" / "subsystem-registry.yaml").write_text("# ok\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def guard(tmp_repo: Path) -> SsotGuard:
    """返回绑定到 tmp_repo 的 SsotGuard 实例。"""
    return SsotGuard(repo_root=tmp_repo)


# ---------------------------------------------------------------------------
# 辅助：模拟 staged_files 返回值
# ---------------------------------------------------------------------------


def _make_guard_with_staged(
    tmp_repo: Path,
    staged: dict[str, str],
) -> tuple[SsotGuard, Any]:
    """构造绑定 repo 的 guard，并 patch staged_files 返回指定 staged 字典。"""
    g = SsotGuard(repo_root=tmp_repo)
    patcher = patch("zephyr.shared.security.ssot_guard.staged_files", return_value=staged)
    mock = patcher.start()
    return g, (patcher, mock)


# ---------------------------------------------------------------------------
# 单元测试：extract_declared_paths
# ---------------------------------------------------------------------------


class TestExtractDeclaredPaths:
    """P0：路径提取逻辑。"""

    def test_extracts_path_field(self) -> None:
        content = "  path: scripts/hooks/doc_guard.py\n"
        result = extract_declared_paths(content)
        assert "scripts/hooks/doc_guard.py" in result

    def test_extracts_core_file_field(self) -> None:
        content = "  core_file: docs/subsystem-registry.yaml\n"
        result = extract_declared_paths(content)
        assert "docs/subsystem-registry.yaml" in result

    def test_extracts_canonical_path_field(self) -> None:
        content = "  canonical_path: docs/01_GOVERNANCE/\n"
        result = extract_declared_paths(content)
        # 目录路径末尾 '/' 被 rstrip 移除
        assert "docs/01_GOVERNANCE" in result

    def test_deduplicates(self) -> None:
        content = "  path: scripts/hooks/a.py\n  path: scripts/hooks/a.py\n"
        result = extract_declared_paths(content)
        assert result.count("scripts/hooks/a.py") == 1

    def test_empty_content(self) -> None:
        assert extract_declared_paths("") == []

    def test_no_matching_fields(self) -> None:
        content = "description: hello world\n"
        assert extract_declared_paths(content) == []

    def test_ignores_comment_lines(self) -> None:
        content = "  # path: scripts/hooks/commented.py\n"
        result = extract_declared_paths(content)
        assert not any("commented" in p for p in result)


# ---------------------------------------------------------------------------
# 单元测试：validate_path_format
# ---------------------------------------------------------------------------


class TestValidatePathFormat:
    """P0：路径格式校验。"""

    @pytest.mark.parametrize(
        "path",
        [
            "scripts/hooks/doc_guard.py",
            "docs/01_GOVERNANCE/governance-asset-inventory.yaml",
            "src/zephyr/hooks/ssot_guard.py",
            ".github/workflows/ci.yml",
        ],
    )
    def test_valid_paths(self, path: str) -> None:
        assert validate_path_format(path) is None

    def test_absolute_unix_path(self) -> None:
        err = validate_path_format("/etc/passwd")
        assert err is not None
        assert "绝对路径" in err

    def test_absolute_windows_path(self) -> None:
        err = validate_path_format("C:/Users/foo/bar.py")
        assert err is not None
        assert "绝对路径" in err

    def test_backslash_path(self) -> None:
        err = validate_path_format("scripts\\hooks\\doc_guard.py")
        assert err is not None
        assert "反斜杠" in err

    def test_single_char_path_not_flagged_as_windows(self) -> None:
        # 单字符路径不应被误判为 Windows 绝对路径
        assert validate_path_format("a") is None


# ---------------------------------------------------------------------------
# 单元测试：SsotGuard.is_watched
# ---------------------------------------------------------------------------


class TestIsWatched:
    """P0：监控路径判断。"""

    @pytest.mark.parametrize(
        "path",
        [
            "scripts/hooks/new_hook.py",
            "scripts/governance/some_tool.py",
            "scripts/governance/scanner.py",
            "scripts/ci_audit/checker.py",
            ".github/workflows/ci.yml",
            "docs/_working/audit/STANDARDS/new-standard.md",
            "src/zephyr/hooks/ssot_guard.py",
            "src/zephyr/db/task_repo.py",
        ],
    )
    def test_watched_paths(self, guard: SsotGuard, path: str) -> None:
        assert guard.is_watched(path) is True

    @pytest.mark.parametrize(
        "path",
        [
            "src/core/exceptions.py",  # 非 zephyr 包
            "docs/01_GOVERNANCE/some-doc.md",  # 非 STANDARDS
            "README.md",  # 根目录
            "tests/infrastructure/test_core.py",  # 测试文件
        ],
    )
    def test_non_watched_paths(self, guard: SsotGuard, path: str) -> None:
        assert guard.is_watched(path) is False

    def test_non_watched_extension(self, guard: SsotGuard) -> None:
        # .txt 文件不在监控扩展名列表
        assert guard.is_watched("scripts/hooks/readme.txt") is False


# ---------------------------------------------------------------------------
# 单元测试：C-1 检查
# ---------------------------------------------------------------------------


class TestCheckC1:
    """P0：新增治理文件时注册表必须同步暂存。"""

    def test_pass_no_new_files(self, guard: SsotGuard) -> None:
        result = guard.check_c1(watched_staged={}, registry_staged=False)
        assert result.passed is True
        assert "跳过" in result.message

    def test_pass_new_files_registry_staged(self, guard: SsotGuard) -> None:
        watched = {"scripts/hooks/new_hook.py": "A"}
        result = guard.check_c1(watched_staged=watched, registry_staged=True)
        assert result.passed is True
        assert "已同步暂存" in result.message

    def test_fail_new_files_registry_not_staged(self, guard: SsotGuard) -> None:
        watched = {"scripts/hooks/new_hook.py": "A"}
        result = guard.check_c1(watched_staged=watched, registry_staged=False)
        assert result.passed is False
        assert "scripts/hooks/new_hook.py" in result.details

    def test_fail_multiple_new_files(self, guard: SsotGuard) -> None:
        watched = {
            "scripts/hooks/hook_a.py": "A",
            "scripts/governance/tool_b.py": "A",
        }
        result = guard.check_c1(watched_staged=watched, registry_staged=False)
        assert result.passed is False
        assert len(result.details) == 2

    def test_modified_files_not_blocked_without_registry(self, guard: SsotGuard) -> None:
        # 修改（'M'）不是新增，C-1 应该通过
        watched = {"scripts/hooks/existing_hook.py": "M"}
        result = guard.check_c1(watched_staged=watched, registry_staged=False)
        assert result.passed is True


# ---------------------------------------------------------------------------
# 单元测试：C-3 检查
# ---------------------------------------------------------------------------


class TestCheckC3:
    """P0：删除治理文件时注册表必须同步暂存。"""

    def test_pass_no_deleted_files(self, guard: SsotGuard) -> None:
        result = guard.check_c3(watched_staged={}, registry_staged=False)
        assert result.passed is True

    def test_pass_deleted_files_registry_staged(self, guard: SsotGuard) -> None:
        watched = {"scripts/hooks/old_hook.py": "D"}
        result = guard.check_c3(watched_staged=watched, registry_staged=True)
        assert result.passed is True

    def test_fail_deleted_files_registry_not_staged(self, guard: SsotGuard) -> None:
        watched = {"scripts/hooks/old_hook.py": "D"}
        result = guard.check_c3(watched_staged=watched, registry_staged=False)
        assert result.passed is False
        assert "scripts/hooks/old_hook.py" in result.details


# ---------------------------------------------------------------------------
# 单元测试：C-2 检查
# ---------------------------------------------------------------------------


class TestCheckC2:
    """P1：注册表暂存时声明路径必须存在。"""

    def test_pass_all_paths_exist(self, tmp_repo: Path) -> None:
        guard = SsotGuard(repo_root=tmp_repo)
        result = guard.check_c2()
        assert result.passed is True

    def test_fail_missing_declared_path(self, tmp_repo: Path) -> None:
        # 往注册表中写一个不存在的文件路径
        registry = (
            tmp_repo / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule_catalog_registry.yaml"
        )
        registry.write_text(
            "  path: scripts/hooks/nonexistent_hook.py\n",
            encoding="utf-8",
        )
        guard = SsotGuard(repo_root=tmp_repo)
        result = guard.check_c2()
        assert result.passed is False
        assert "nonexistent_hook.py" in result.details[0]

    def test_fail_registry_not_found(self, tmp_path: Path) -> None:
        guard = SsotGuard(repo_root=tmp_path)
        result = guard.check_c2()
        assert result.passed is False
        assert "不存在" in result.message


# ---------------------------------------------------------------------------
# 单元测试：C-4 检查
# ---------------------------------------------------------------------------


class TestCheckC4Format:
    """P1：注册表路径格式合法性。"""

    def test_skip_when_registry_not_staged(self, guard: SsotGuard) -> None:
        result = guard.check_c4_format(registry_staged=False)
        assert result.passed is True
        assert "跳过" in result.message

    def test_pass_valid_paths(self, tmp_repo: Path) -> None:
        guard = SsotGuard(repo_root=tmp_repo)
        result = guard.check_c4_format(registry_staged=True)
        assert result.passed is True

    def test_fail_absolute_path_in_registry(self, tmp_repo: Path) -> None:
        registry = (
            tmp_repo / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule_catalog_registry.yaml"
        )
        registry.write_text(
            "  path: /absolute/path/to/file.py\n",
            encoding="utf-8",
        )
        guard = SsotGuard(repo_root=tmp_repo)
        result = guard.check_c4_format(registry_staged=True)
        assert result.passed is False

    def test_fail_backslash_path_in_registry(self, tmp_repo: Path) -> None:
        registry = (
            tmp_repo / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "rule_catalog_registry.yaml"
        )
        registry.write_text(
            "  path: scripts\\hooks\\hook.py\n",
            encoding="utf-8",
        )
        guard = SsotGuard(repo_root=tmp_repo)
        result = guard.check_c4_format(registry_staged=True)
        assert result.passed is False


# ---------------------------------------------------------------------------
# 单元测试：GuardReport
# ---------------------------------------------------------------------------


class TestGuardReport:
    """P1：报告聚合逻辑。"""

    def test_all_pass(self) -> None:
        report = GuardReport()
        report.add(CheckResult("C-1", True, "pass"))
        report.add(CheckResult("C-2", True, "pass"))
        assert report.passed is True

    def test_any_fail(self) -> None:
        report = GuardReport()
        report.add(CheckResult("C-1", True, "pass"))
        report.add(CheckResult("C-2", False, "fail"))
        assert report.passed is False

    def test_str_contains_verdict(self) -> None:
        report = GuardReport()
        report.add(CheckResult("C-1", True, "pass"))
        text = str(report)
        assert "✅" in text or "通过" in text


# ---------------------------------------------------------------------------
# 集成测试：SsotGuard.run() 完整流程
# ---------------------------------------------------------------------------


class TestSsotGuardRunIntegration:
    """Q2 集成测试：run() 完整流程（patch staged_files）。"""

    def test_no_staged_files_all_pass(self, tmp_repo: Path) -> None:
        with patch("zephyr.shared.security.ssot_guard.staged_files", return_value={}):
            guard = SsotGuard(repo_root=tmp_repo)
            report = guard.run()
        assert report.passed is True

    def test_new_watched_file_without_registry_fails(self, tmp_repo: Path) -> None:
        staged = {"scripts/hooks/new_hook.py": "A"}
        with patch("zephyr.shared.security.ssot_guard.staged_files", return_value=staged):
            guard = SsotGuard(repo_root=tmp_repo)
            report = guard.run()
        assert report.passed is False
        failed_ids = [r.check_id for r in report.results if not r.passed]
        assert "C-1" in failed_ids

    def test_new_watched_file_with_registry_staged_passes(self, tmp_repo: Path) -> None:
        staged = {
            "scripts/hooks/new_hook.py": "A",
            REGISTRY_REL_PATH: "M",
        }
        with patch("zephyr.shared.security.ssot_guard.staged_files", return_value=staged):
            guard = SsotGuard(repo_root=tmp_repo)
            report = guard.run()
        # C-1 和 C-3 均应通过；C-2 和 C-4 在 tmp_repo 中注册表路径合法
        c1 = next(r for r in report.results if r.check_id == "C-1")
        assert c1.passed is True

    def test_git_error_produces_failed_report(self, tmp_repo: Path) -> None:
        with patch(
            "zephyr.shared.security.ssot_guard.staged_files",
            side_effect=subprocess.CalledProcessError(128, "git"),
        ):
            guard = SsotGuard(repo_root=tmp_repo)
            report = guard.run()
        assert report.passed is False
        assert any(r.check_id == "GIT" for r in report.results)


# ---------------------------------------------------------------------------
# 性能测试：大量路径提取不超时
# ---------------------------------------------------------------------------


class TestExtractPerformance:
    """Q4 性能断言：路径提取 1000 行 YAML 在 0.5s 内完成。"""

    def test_bulk_extraction_speed(self) -> None:
        import time

        lines = "\n".join(f"  path: scripts/hooks/hook_{i}.py" for i in range(1000))
        t0 = time.perf_counter()
        result = extract_declared_paths(lines)
        elapsed = time.perf_counter() - t0
        assert len(result) == 1000
        assert elapsed < 0.5, f"路径提取 1000 行耗时 {elapsed:.3f}s > 0.5s 预算"
