# [A_test] module_id: SRC-TST-2235 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-domain_fk_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_domain_fk_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_domain_fk_gate.py — GATE-DOMAIN-FK 门禁单测

权威依据：domain_fk_gate.py（make_domain_fk_gate，裁定#ARCH-DRIFT-PREVENTION-001 ADP-1）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestLoadValidDomains: _load_valid_domains 从 YAML 真源解析有效域集合
  - 正常 YAML → 域集合
  - YAML 不可读 → None (fail-open)
  - YAML 无域条目 → None (fail-open)
- TestCheckDomainFk: _check_domain_fk diff-based 检测
  - 有效域 → 无违规
  - 无效域 → 违规
  - docstring 行豁免
- TestFormatViolations: _format_domain_fk_violations 格式化
- TestGatewayIntegration: mock gateway 完整流程
  - 无 staged .py → 放行
  - 有效域 → 放行
  - 无效域 → 阻断
  - YAML 不可达 → fail-open 放行
  - tests/ 路径豁免
  - 存量 [DOMAIN] 行未改动 → 不检测（diff-based）

测试隔离：MagicMock 模拟 gateway._run_git，按 git 子命令路由返回不同结果。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.domain_fk_gate import (  # noqa: E402
    _DOMAIN_REGISTRY_REL,
    _check_domain_fk,
    _format_domain_fk_violations,
    _load_valid_domains,
    make_domain_fk_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------

class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_gate_id(self) -> None:
        gate = make_domain_fk_gate()
        assert gate.gate_id == "GATE-DOMAIN-FK"

    def test_priority(self) -> None:
        gate = make_domain_fk_gate()
        assert gate.priority == 78

    def test_is_gate_spec(self) -> None:
        gate = make_domain_fk_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestLoadValidDomains
# ---------------------------------------------------------------------------

class TestLoadValidDomains:
    """_load_valid_domains 从 functional_domain_registry.yaml 解析有效域集合。"""

    def test_normal_yaml(self) -> None:
        """正常 YAML → 域集合。"""
        yaml_content = (
            "entries:\n"
            "- domain: D_GOV_CODE_QUALITY\n"
            "  subdomain: governance\n"
            "- domain: D_INFRA_A2A\n"
            "  subdomain: infrastructure\n"
        )
        gw = _make_yaml_gateway(yaml_content)
        result = _load_valid_domains(gw)
        assert result is not None
        assert "D_GOV_CODE_QUALITY" in result
        assert "D_INFRA_A2A" in result

    def test_yaml_unreadable_returns_none(self) -> None:
        """YAML 不可读（git show 失败）→ None (fail-open)。"""
        gw = MagicMock()
        gw._run_git = MagicMock(return_value=_MockResult(1, ""))
        result = _load_valid_domains(gw)
        assert result is None

    def test_yaml_no_entries_returns_none(self) -> None:
        """YAML 无域条目（格式异常）→ None (fail-open)。"""
        gw = _make_yaml_gateway("entries: []\n")
        result = _load_valid_domains(gw)
        assert result is None


# ---------------------------------------------------------------------------
# TestCheckDomainFk
# ---------------------------------------------------------------------------

class TestCheckDomainFk:
    """_check_domain_fk diff-based 检测逻辑。"""

    def test_valid_domain_no_violation(self) -> None:
        """有效域 → 无违规。"""
        py_file = "src/zephyr/foo.py"
        file_content = "# [DOMAIN] D_GOV_CODE_QUALITY\n"
        diff = "@@ -0,0 +1,1 @@\n+# [DOMAIN] D_GOV_CODE_QUALITY\n"
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: file_content},
            yaml_content=_SAMPLE_YAML,
        )
        valid = {"D_GOV_CODE_QUALITY", "D_INFRA_A2A"}
        violations = _check_domain_fk(gw, [py_file], valid)
        assert violations == []

    def test_invalid_domain_violation(self) -> None:
        """无效域 → 违规。"""
        py_file = "src/zephyr/foo.py"
        file_content = "# [DOMAIN] D_GOV_DOC_QUALITY\n"
        diff = "@@ -0,0 +1,1 @@\n+# [DOMAIN] D_GOV_DOC_QUALITY\n"
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: file_content},
            yaml_content=_SAMPLE_YAML,
        )
        valid = {"D_GOV_CODE_QUALITY"}
        violations = _check_domain_fk(gw, [py_file], valid)
        assert len(violations) == 1
        assert "D_GOV_DOC_QUALITY" in violations[0]
        assert py_file in violations[0]

    def test_docstring_line_exempt(self) -> None:
        """docstring 内的 [DOMAIN] 行豁免。"""
        py_file = "src/zephyr/foo.py"
        # [DOMAIN] 在 docstring 内（模块 docstring 第 2-4 行）
        file_content = (
            '"""模块文档\n'
            "# [DOMAIN] D_INVALID_DOCSTRING\n"
            '"""\n'
        )
        # diff 显示第 2 行被加入
        diff = "@@ -0,0 +1,3 @@\n+\"\"\"模块文档\n+# [DOMAIN] D_INVALID_DOCSTRING\n+\"\"\"\n"
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: file_content},
            yaml_content=_SAMPLE_YAML,
        )
        valid = {"D_GOV_CODE_QUALITY"}
        violations = _check_domain_fk(gw, [py_file], valid)
        assert violations == []


# ---------------------------------------------------------------------------
# TestFormatViolations
# ---------------------------------------------------------------------------

class TestFormatViolations:
    """_format_domain_fk_violations 格式化。"""

    def test_single_violation(self) -> None:
        passed, msg = _format_domain_fk_violations(["  foo.py:1: [DOMAIN] D_X不在"])
        assert passed is False
        assert "GATE-DOMAIN-FK" in msg
        assert "functional_domain_registry.yaml" in msg
        assert "foo.py:1" in msg

    def test_multiple_violations(self) -> None:
        violations = [
            "  a.py:1: [DOMAIN] D_X",
            "  b.py:2: [DOMAIN] D_Y",
        ]
        passed, msg = _format_domain_fk_violations(violations)
        assert passed is False
        assert "a.py:1" in msg
        assert "b.py:2" in msg


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------

class TestGatewayIntegration:
    """mock gateway 完整流程测试。"""

    def test_no_py_files_passes(self) -> None:
        """无 staged .py → 放行。"""
        gw = _make_full_gateway(
            diff_files=[], file_diffs={}, staged_contents={}, yaml_content=_SAMPLE_YAML,
        )
        gate = make_domain_fk_gate()
        passed, msg = gate.check(gw, [])
        assert passed is True
        assert msg == ""

    def test_valid_domain_passes(self) -> None:
        """有效域 → 放行。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: "@@ -0,0 +1,1 @@\n+# [DOMAIN] D_GOV_CODE_QUALITY\n"},
            staged_contents={py_file: "# [DOMAIN] D_GOV_CODE_QUALITY\n"},
            yaml_content=_SAMPLE_YAML,
        )
        gate = make_domain_fk_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True

    def test_invalid_domain_blocks(self) -> None:
        """无效域 → 阻断。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: "@@ -0,0 +1,1 @@\n+# [DOMAIN] D_GOV_DOC_QUALITY\n"},
            staged_contents={py_file: "# [DOMAIN] D_GOV_DOC_QUALITY\n"},
            yaml_content=_SAMPLE_YAML,
        )
        gate = make_domain_fk_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is False
        assert "GATE-DOMAIN-FK" in msg
        assert "D_GOV_DOC_QUALITY" in msg

    def test_yaml_unreachable_fail_open(self) -> None:
        """YAML 不可达 → fail-open 放行。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: "@@ -0,0 +1,1 @@\n+# [DOMAIN] D_INVALID\n"},
            staged_contents={py_file: "# [DOMAIN] D_INVALID\n"},
            yaml_content=None,  # YAML 不可读
        )
        gate = make_domain_fk_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True

    def test_tests_path_exempt(self) -> None:
        """tests/ 路径豁免（即使域无效也放行）。"""
        py_file = "tests/governance/test_foo.py"
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: "@@ -0,0 +1,1 @@\n+# [DOMAIN] D_INVALID\n"},
            staged_contents={py_file: "# [DOMAIN] D_INVALID\n"},
            yaml_content=_SAMPLE_YAML,
        )
        gate = make_domain_fk_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True

    def test_unchanged_domain_line_not_checked(self) -> None:
        """存量 [DOMAIN] 行未改动 → 不检测（diff-based）。

        modified 文件只改了其他行，[DOMAIN] 行未在 added 行中→不检测。
        """
        py_file = "src/zephyr/foo.py"
        # diff 只有第 5 行 added（非 [DOMAIN] 行）
        gw = _make_full_gateway(
            diff_files=[py_file],
            file_diffs={py_file: "@@ -4,0 +5,1 @@\n+print('new')\n"},
            staged_contents={py_file: "# [DOMAIN] D_INVALID\nprint('new')\n"},
            yaml_content=_SAMPLE_YAML,
        )
        gate = make_domain_fk_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAMPLE_YAML = (
    "entries:\n"
    "- domain: D_GOV_CODE_QUALITY\n"
    "  subdomain: governance\n"
    "- domain: D_INFRA_A2A\n"
    "  subdomain: infrastructure\n"
)


def _make_yaml_gateway(yaml_content: str) -> MagicMock:
    """构造只响应 YAML 读取的 gateway（用于 _load_valid_domains 单测）。"""
    def _run_git(args):
        if "show" in args and args[2] == ":" + _DOMAIN_REGISTRY_REL:
            return _MockResult(0, yaml_content)
        return _MockResult(1, "")
    gw = MagicMock()
    gw._run_git = MagicMock(side_effect=_run_git)
    return gw


def _make_full_gateway(
    diff_files: list[str],
    file_diffs: dict[str, str],
    staged_contents: dict[str, str],
    yaml_content: str | None,
) -> MagicMock:
    """构造完整流程 mock gateway，按 git 子命令路由。

    Args:
        diff_files: _get_staged_py_files 返回的文件列表。
        file_diffs: {py_file: diff_stdout} 每个文件的 added 行 diff。
        staged_contents: {py_file: content} 每个文件的 staged 内容。
        yaml_content: functional_domain_registry.yaml 内容；None=不可读。
    """
    def _run_git(args):
        cmd = list(args)
        if "diff" in cmd and "--name-only" in cmd:
            return _MockResult(0, "\n".join(diff_files))
        if "diff" in cmd and "--unified=0" in cmd:
            py_file = cmd[-1]
            return _MockResult(0, file_diffs.get(py_file, ""))
        if "show" in cmd:
            path = cmd[2][1:]  # strip ":"
            if path == _DOMAIN_REGISTRY_REL:
                if yaml_content is None:
                    return _MockResult(1, "")
                return _MockResult(0, yaml_content)
            return _MockResult(0, staged_contents.get(path, ""))
        return _MockResult(1, "")

    gw = MagicMock()
    gw._run_git = MagicMock(side_effect=_run_git)
    return gw
