# [A_test] module_id: SRC-TST-0113 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | tests/governance/governance_e2e/test_naming_e2e.py | §
# [MODULE] tests.e2e.test_naming_e2e
# [INVARIANTS] E2E tests verify the full enforcement chain: create file → check_naming_convention → scaffold
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] task_bound

"""DM-398: 命名规范端到端测试 — 验证完整防护链路。

测试链路: 创建违规文件 → check_naming_convention.py 检测 → scaffold.py 强制 kebab-case
不依赖 git pre-commit（CI 环境无 git config），直接调用检查器验证。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

PROJECT_ROOT = REPO_ROOT
CHECK_SCRIPT = PROJECT_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"
SCAFFOLD_SCRIPT = PROJECT_ROOT / "scripts" / "scaffold.py"


def _run_checker(path: str) -> subprocess.CompletedProcess:
    """Run check_naming_convention.py with a positional path argument."""
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), str(path)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
    )


def _run_scaffold(mode: str, name: str, desc: str = "Test") -> subprocess.CompletedProcess:
    """Run scaffold.py with PYTHONPATH set for scripts module import."""
    return subprocess.run(
        [sys.executable, str(SCAFFOLD_SCRIPT), mode, name, "--desc", desc, "--dry-run"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT) + ";" + str(PROJECT_ROOT / "src")},
    )


class TestNamingConventionDetection:
    """验证 check_naming_convention.py 能检测各类违规文件名。"""

    def test_snake_case_yaml_detected(self, tmp_path: Path) -> None:
        """snake_case YAML 文件名应被 N-13 检测为违规。"""
        bad_file = tmp_path / "my_config.yaml"
        bad_file.write_text("key: value\n", encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode != 0, "snake_case YAML 应被检测为违规"
        assert "N-13" in result.stdout or "N-13" in result.stderr

    def test_uppercase_md_detected(self, tmp_path: Path) -> None:
        """大写 MD 文件名应被 N-01 检测为违规。"""
        bad_file = tmp_path / "README.md"
        bad_file.write_text("# Readme\n", encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode != 0, "大写 MD 文件名应被检测为违规"
        assert "N-01" in result.stdout or "N-01" in result.stderr

    def test_kebab_case_yaml_passes(self, tmp_path: Path) -> None:
        """kebab-case YAML 文件名应通过检查。"""
        good_file = tmp_path / "my-config.yaml"
        good_file.write_text("key: value\n", encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode == 0, f"kebab-case YAML 应通过检查, got: {result.stdout}"

    def test_kebab_case_json_passes(self, tmp_path: Path) -> None:
        """kebab-case JSON 文件名应通过检查。"""
        good_file = tmp_path / "my-config.json"
        good_file.write_text('{"key": "value"}\n', encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode == 0, f"kebab-case JSON 应通过检查, got: {result.stdout}"

    def test_kebab_case_md_passes(self, tmp_path: Path) -> None:
        """kebab-case MD 文件名应通过检查。"""
        good_file = tmp_path / "my-guide.md"
        good_file.write_text("# Guide\n", encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode == 0, f"kebab-case MD 应通过检查, got: {result.stdout}"


class TestScaffoldKebabEnforcement:
    """验证 scaffold.py 的 kebab-case 强制执行。"""

    def test_scaffold_yaml_rejects_snake_case(self) -> None:
        """scaffold.py yaml 模式应拒绝 snake_case 文件名。"""
        result = _run_scaffold("yaml", "test_dir/my_test_config", "Test config")
        assert result.returncode != 0, f"snake_case 文件名应被 scaffold 拒绝, got: {result.stdout}{result.stderr}"
        output = result.stdout + result.stderr
        assert "kebab-case" in output

    def test_scaffold_yaml_rejects_uppercase(self) -> None:
        """scaffold.py yaml 模式应拒绝大写文件名。"""
        result = _run_scaffold("yaml", "test_dir/MyConfig", "Test config")
        assert result.returncode != 0, f"大写文件名应被 scaffold 拒绝, got: {result.stdout}{result.stderr}"
        output = result.stdout + result.stderr
        assert "kebab-case" in output

    def test_scaffold_json_rejects_snake_case(self) -> None:
        """scaffold.py json 模式应拒绝 snake_case 文件名。"""
        result = _run_scaffold("json", "test_dir/my_test_data", "Test data")
        assert result.returncode != 0, f"snake_case 文件名应被 scaffold 拒绝, got: {result.stdout}{result.stderr}"

    def test_scaffold_md_rejects_snake_case(self) -> None:
        """scaffold.py md 模式应拒绝 snake_case 文件名。"""
        result = _run_scaffold("md", "test_dir/my_test_guide", "Test guide")
        assert result.returncode != 0, f"snake_case 文件名应被 scaffold 拒绝, got: {result.stdout}{result.stderr}"

    def test_scaffold_md_rejects_uppercase(self) -> None:
        """scaffold.py md 模式应拒绝大写文件名。"""
        result = _run_scaffold("md", "test_dir/MyGuide", "Test guide")
        assert result.returncode != 0, f"大写文件名应被 scaffold 拒绝, got: {result.stdout}{result.stderr}"
        output = result.stdout + result.stderr
        assert "kebab-case" in output

    def test_scaffold_yaml_accepts_kebab_case(self) -> None:
        """scaffold.py yaml 模式应接受 kebab-case 文件名。"""
        result = _run_scaffold("yaml", "test_dir/my-test-config", "Test config")
        assert result.returncode == 0, f"kebab-case 文件名应被 scaffold 接受, got: {result.stdout}{result.stderr}"

    def test_scaffold_json_accepts_kebab_case(self) -> None:
        """scaffold.py json 模式应接受 kebab-case 文件名。"""
        result = _run_scaffold("json", "test_dir/my-test-data", "Test data")
        assert result.returncode == 0, f"kebab-case 文件名应被 scaffold 接受, got: {result.stdout}{result.stderr}"

    def test_scaffold_md_accepts_kebab_case(self) -> None:
        """scaffold.py md 模式应接受 kebab-case 文件名。"""
        result = _run_scaffold("md", "test_dir/my-test-guide", "Test guide")
        assert result.returncode == 0, f"kebab-case 文件名应被 scaffold 接受, got: {result.stdout}{result.stderr}"


class TestWhitelistProtection:
    """验证命名检查器白名单受 AI_AUTONOMY=human_gated 保护。"""

    def test_check_naming_convention_has_human_gated(self) -> None:
        """check_naming_convention.py 头部应包含 AI_AUTONOMY=human_gated。"""
        content = CHECK_SCRIPT.read_text(encoding="utf-8")
        assert "AI_AUTONOMY" in content and "human_gated" in content, (
            "check_naming_convention.py 应包含 AI_AUTONOMY=human_gated 标记"
        )

    def test_check_naming_convention_has_modify_guard(self) -> None:
        """check_naming_convention.py 头部应包含 MODIFY-GUARD 保护白名单。"""
        content = CHECK_SCRIPT.read_text(encoding="utf-8")
        assert "MODIFY-GUARD" in content, "check_naming_convention.py 应包含 MODIFY-GUARD 标记"
        assert "WHITELIST" in content or "EXEMPT" in content, "MODIFY-GUARD 应提及白名单保护"

    def test_whitelist_minimal(self) -> None:
        """白名单应只包含 AGENTS.md（其他已迁移为小写）。"""
        content = CHECK_SCRIPT.read_text(encoding="utf-8")
        assert '"README.md"' not in content, "README.md 应已从白名单移除"
        assert '"index.md"' not in content, "index.md 应已从白名单移除"
        assert '"CHANGELOG.md"' not in content, "CHANGELOG.md 应已从白名单移除"
        assert '"AGENTS.md"' in content, "AGENTS.md 应保留在白名单中"


class TestDirectWriteBypassDetection:
    """验证绕过 scaffold.py 直接创建违规文件时，check_naming_convention.py 仍能检测到。"""

    def test_direct_write_bypass_detected(self, tmp_path: Path) -> None:
        """直接写入违规文件名 → check_naming_convention.py 应检测到 N-13 违规。"""
        bad_file = tmp_path / "BadConfig.yaml"
        bad_file.write_text("key: value\n", encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode != 0, "直接写入的大写 YAML 文件名应被检测为违规"
        assert "N-13" in result.stdout or "N-13" in result.stderr, (
            f"应检测到 N-13 违规, stdout: {result.stdout}, stderr: {result.stderr}"
        )

    def test_direct_write_snake_case_bypass_detected(self, tmp_path: Path) -> None:
        """直接写入 snake_case JSON 文件名 → check_naming_convention.py 应检测到。"""
        bad_file = tmp_path / "my_data_config.json"
        bad_file.write_text('{"key": "value"}\n', encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode != 0, "直接写入的 snake_case JSON 文件名应被检测为违规"
        assert "N-13" in result.stdout or "N-13" in result.stderr

    def test_direct_write_md_bypass_detected(self, tmp_path: Path) -> None:
        """直接写入大写 MD 文件名 → check_naming_convention.py 应检测到。"""
        bad_file = tmp_path / "MyGuide.md"
        bad_file.write_text("# Guide\n", encoding="utf-8")

        result = _run_checker(str(tmp_path))
        assert result.returncode != 0, "直接写入的大写 MD 文件名应被检测为违规"
        assert "N-01" in result.stdout or "N-01" in result.stderr or "N-13" in result.stdout or "N-13" in result.stderr


class TestCIEnforcement:
    """验证 CI 配置中包含全量命名扫描。"""

    def test_governance_yml_has_naming_scan(self) -> None:
        """governance.yml 应包含 GATE-11 全量命名扫描步骤。"""
        ci_path = PROJECT_ROOT / ".github" / "workflows" / "governance.yml"
        content = ci_path.read_text(encoding="utf-8")
        assert "check_naming_convention.py" in content, "governance.yml 应包含 check_naming_convention.py 全量扫描步骤"
        assert "Naming Convention" in content, "governance.yml 应包含命名规范扫描步骤名称"
