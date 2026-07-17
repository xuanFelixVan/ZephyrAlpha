# [A_test] module_id: SRC-TST-2236 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-blueprint_amodule_consistency_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_blueprint_amodule_consistency_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_blueprint_amodule_consistency_gate.py — BLUEPRINT-AMODULE-CONSISTENCY 门禁单测

权威依据：blueprint_amodule_consistency_gate.py
（make_blueprint_amodule_consistency_gate，裁定#ARCH-DRIFT-PREVENTION-001 ADP-3）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestCheckAmoduleFormat: _check_amodule_format diff-based 检测
  - track 2 文件级合法（MOD-GOV-name）→ 无违规
  - track 1 层码合法（MOD-INF-025）→ 无违规
  - track 2 多段域合法（MOD-INFRA_A2A-005）→ 无违规
  - malformation（MOD-INF_a2a_xxx）→ 违规
  - docstring 行豁免
- TestFormatViolations: _format_amodule_violations 格式化
- TestGatewayIntegration: mock gateway 完整流程
  - 无 staged .py → 放行
  - 合法格式 → 放行
  - malformation → 阻断
  - tests/ 路径豁免
  - 存量 [A_module] 行未改动 → 不检测（diff-based）

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

from zephyr.gov_enforcement.commit_gates.blueprint_amodule_consistency_gate import (  # noqa: E402
    _check_amodule_format,
    _format_amodule_violations,
    make_blueprint_amodule_consistency_gate,
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
        gate = make_blueprint_amodule_consistency_gate()
        assert gate.gate_id == "BLUEPRINT-AMODULE-CONSISTENCY"

    def test_priority(self) -> None:
        gate = make_blueprint_amodule_consistency_gate()
        assert gate.priority == 79

    def test_is_gate_spec(self) -> None:
        gate = make_blueprint_amodule_consistency_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestCheckAmoduleFormat
# ---------------------------------------------------------------------------

class TestCheckAmoduleFormat:
    """_check_amodule_format diff-based 检测逻辑。"""

    def test_track2_file_level_valid(self) -> None:
        """track 2 文件级合法（MOD-GOV-name）→ 无违规。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
            },
        )
        violations = _check_amodule_format(gw, [py_file])
        assert violations == []

    def test_track1_layer_seq_valid(self) -> None:
        """track 1 层码合法（MOD-INF-025）→ 无违规。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id=MOD-INF-025\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id=MOD-INF-025\n"
            },
        )
        violations = _check_amodule_format(gw, [py_file])
        assert violations == []

    def test_track2_multi_segment_valid(self) -> None:
        """track 2 多段域合法（MOD-INFRA_A2A-005）→ 无违规。

        下划线后是大写 A（非小写），不匹配 malformation 正则。
        """
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id=MOD-INFRA_A2A-005\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id=MOD-INFRA_A2A-005\n"
            },
        )
        violations = _check_amodule_format(gw, [py_file])
        assert violations == []

    def test_malformation_violation(self) -> None:
        """malformation（MOD-INF_a2a_xxx）→ 违规。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id=MOD-INF_a2a_agent_blocklist\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id=MOD-INF_a2a_agent_blocklist\n"
            },
        )
        violations = _check_amodule_format(gw, [py_file])
        assert len(violations) == 1
        assert "MOD-INF_a2a_agent_blocklist" in violations[0]
        assert py_file in violations[0]

    def test_colon_separator_malformation(self) -> None:
        """冒号分隔符的 malformation 也检测。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id:MOD-INF_bad_name\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id:MOD-INF_bad_name\n"
            },
        )
        violations = _check_amodule_format(gw, [py_file])
        assert len(violations) == 1

    def test_docstring_line_exempt(self) -> None:
        """docstring 内的 [A_module] 行豁免。"""
        py_file = "src/zephyr/foo.py"
        file_content = (
            '"""模块文档\n'
            "# [A_module] module_id=MOD-INF_bad_name\n"
            '"""\n'
        )
        diff = (
            "@@ -0,0 +1,3 @@\n"
            '+"""模块文档\n'
            "+# [A_module] module_id=MOD-INF_bad_name\n"
            '+"""\n'
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: file_content},
        )
        violations = _check_amodule_format(gw, [py_file])
        assert violations == []


# ---------------------------------------------------------------------------
# TestFormatViolations
# ---------------------------------------------------------------------------

class TestFormatViolations:
    """_format_amodule_violations 格式化。"""

    def test_single_violation(self) -> None:
        passed, msg = _format_amodule_violations(
            ["  foo.py:1: [A_module] module_id='MOD-INF_bad' 格式错误"]
        )
        assert passed is False
        assert "BLUEPRINT-AMODULE-CONSISTENCY" in msg
        assert "ARCH-DRIFT-PREVENTION-001" in msg
        assert "foo.py:1" in msg

    def test_multiple_violations(self) -> None:
        violations = [
            "  a.py:1: [A_module] module_id='MOD-INF_bad' 格式错误",
            "  b.py:2: [A_module] module_id='MOD-INF_worse' 格式错误",
        ]
        passed, msg = _format_amodule_violations(violations)
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
        gw = _make_gateway(diff_files=[], file_diffs={}, staged_contents={})
        gate = make_blueprint_amodule_consistency_gate()
        passed, msg = gate.check(gw, [])
        assert passed is True
        assert msg == ""

    def test_valid_format_passes(self) -> None:
        """合法格式 → 放行。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
            },
        )
        gate = make_blueprint_amodule_consistency_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True

    def test_malformation_blocks(self) -> None:
        """malformation → 阻断。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id=MOD-INF_a2a_agent_blocklist\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id=MOD-INF_a2a_agent_blocklist\n"
            },
        )
        gate = make_blueprint_amodule_consistency_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is False
        assert "BLUEPRINT-AMODULE-CONSISTENCY" in msg
        assert "MOD-INF_a2a_agent_blocklist" in msg

    def test_tests_path_exempt(self) -> None:
        """tests/ 路径豁免（即使 malformation 也放行）。"""
        py_file = "tests/governance/test_foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={
                py_file: "@@ -0,0 +1,1 @@\n"
                "+# [A_module] module_id=MOD-INF_bad_name\n"
            },
            staged_contents={
                py_file: "# [A_module] module_id=MOD-INF_bad_name\n"
            },
        )
        gate = make_blueprint_amodule_consistency_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True

    def test_unchanged_amodule_line_not_checked(self) -> None:
        """存量 [A_module] 行未改动 → 不检测（diff-based）。

        modified 文件只改了其他行，[A_module] 行未在 added 行中→不检测。
        """
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: "@@ -4,0 +5,1 @@\n+print('new')\n"},
            staged_contents={
                py_file: "# [A_module] module_id=MOD-INF_bad_name\nprint('new')\n"
            },
        )
        gate = make_blueprint_amodule_consistency_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_gateway(
    diff_files: list[str],
    file_diffs: dict[str, str],
    staged_contents: dict[str, str],
) -> MagicMock:
    """构造 mock gateway，按 git 子命令路由。

    Args:
        diff_files: _get_staged_py_files 返回的文件列表。
        file_diffs: {py_file: diff_stdout} 每个文件的 added 行 diff。
        staged_contents: {py_file: content} 每个文件的 staged 内容。
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
            return _MockResult(0, staged_contents.get(path, ""))
        return _MockResult(1, "")

    gw = MagicMock()
    gw._run_git = MagicMock(side_effect=_run_git)
    return gw
