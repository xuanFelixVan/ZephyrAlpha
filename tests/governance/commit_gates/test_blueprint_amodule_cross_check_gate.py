# [A_test] module_id: MOD-GOV_blueprint_amodule_cross_check_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_blueprint_amodule_cross_check_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_blueprint_amodule_cross_check_gate.py — BLUEPRINT-AMODULE-CROSS-CHECK 门禁单测

权威依据：blueprint_amodule_cross_check_gate.py
（make_blueprint_amodule_cross_check_gate，裁定 #ARCH-MODULE-ID-DUAL-SPELLING-001）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestNormalizeModuleId: _ normalize _→- 逻辑
- TestExtractHeaders: 从文件内容提取 [BLUEPRINT] 和 [A_module]
- TestCheckCrossConsistency: diff-based 交叉校验
  - 同模块双拼写（UNDERSCORE vs DASH）→ 违规
  - 不同模块（GATE_ENGINE vs GOV-xxx）→ 无违规
  - 仅有 [BLUEPRINT] 无 [A_module] → 无违规
  - 仅有 [A_module] 无 [BLUEPRINT] → 无违规
  - noqa 逃生 → 无违规
  - 未改动头部 → 不检测（diff-based）
- TestFormatViolations: _format_violations 格式化
- TestGatewayIntegration: mock gateway 完整流程
  - 无 staged .py → 放行
  - 不同模块 → 放行
  - 双拼写 → 阻断
  - tests/ 路径豁免
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

from zephyr.gov_enforcement.commit_gates.blueprint_amodule_cross_check_gate import (  # noqa: E402
    _check_cross_consistency,
    _extract_headers,
    _format_violations,
    _normalize_module_id,
    make_blueprint_amodule_cross_check_gate,
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
        gate = make_blueprint_amodule_cross_check_gate()
        assert gate.gate_id == "BLUEPRINT-AMODULE-CROSS-CHECK"

    def test_priority(self) -> None:
        gate = make_blueprint_amodule_cross_check_gate()
        assert gate.priority == 119

    def test_is_gate_spec(self) -> None:
        gate = make_blueprint_amodule_cross_check_gate()
        assert isinstance(gate, GateSpec)


# ---------------------------------------------------------------------------
# TestNormalizeModuleId
# ---------------------------------------------------------------------------

class TestNormalizeModuleId:
    """_normalize_module_id 将 _ 替换为 -。"""

    def test_underscore_to_dash(self) -> None:
        assert _normalize_module_id("MOD-GOV_error_pattern_library") == "MOD-GOV-error-pattern-library"

    def test_already_dash(self) -> None:
        assert _normalize_module_id("MOD-GOV-error_pattern_library") == "MOD-GOV-error-pattern-library"

    def test_no_separator(self) -> None:
        assert _normalize_module_id("MOD-GATE_ENGINE") == "MOD-GATE-ENGINE"

    def test_multi_segment(self) -> None:
        assert _normalize_module_id("MOD-INFRA_A2A-005") == "MOD-INFRA-A2A-005"


# ---------------------------------------------------------------------------
# TestExtractHeaders
# ---------------------------------------------------------------------------

class TestExtractHeaders:
    """_extract_headers 从文件内容前 20 行提取两头部。"""

    def test_both_present(self) -> None:
        content = (
            "# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-error_pattern_library\n"
        )
        bp, am = _extract_headers(content)
        assert bp == "MOD-GOV_error_pattern_library"
        assert am == "MOD-GOV-error_pattern_library"

    def test_only_blueprint(self) -> None:
        content = "# [BLUEPRINT] MOD-GATE_ENGINE | docs/foo.md\n"
        bp, am = _extract_headers(content)
        assert bp == "MOD-GATE_ENGINE"
        assert am is None

    def test_only_amodule(self) -> None:
        content = "# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
        bp, am = _extract_headers(content)
        assert bp is None
        assert am == "MOD-GOV-domain_fk_gate"

    def test_neither(self) -> None:
        content = "print('hello')\n"
        bp, am = _extract_headers(content)
        assert bp is None
        assert am is None

    def test_colon_separator(self) -> None:
        content = "# [A_module] module_id:MOD-GOV-foo\n"
        bp, am = _extract_headers(content)
        assert am == "MOD-GOV-foo"

    def test_beyond_line_20(self) -> None:
        """超过 20 行的头部不提取。"""
        lines = [f"# line {i}" for i in range(20)]
        lines.append("# [BLUEPRINT] MOD-GOV-foo")
        content = "\n".join(lines)
        bp, am = _extract_headers(content)
        assert bp is None


# ---------------------------------------------------------------------------
# TestCheckCrossConsistency
# ---------------------------------------------------------------------------

class TestCheckCrossConsistency:
    """_check_cross_consistency diff-based 交叉校验。"""

    def test_dual_spelling_violation(self) -> None:
        """同模块双拼写（UNDERSCORE vs DASH）→ 违规。"""
        py_file = "src/zephyr/foo.py"
        content = (
            "# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-error_pattern_library\n"
        )
        diff = (
            "@@ -0,0 +1,2 @@\n"
            "+# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "+# [A_module] module_id=MOD-GOV-error_pattern_library\n"
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert len(violations) == 1
        assert "MOD-GOV_error_pattern_library" in violations[0]
        assert "MOD-GOV-error_pattern_library" in violations[0]

    def test_different_modules_pass(self) -> None:
        """不同模块（GATE_ENGINE vs GOV-xxx）→ 无违规。"""
        py_file = "src/zephyr/foo.py"
        content = (
            "# [BLUEPRINT] MOD-GATE_ENGINE | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
        )
        diff = (
            "@@ -0,0 +1,2 @@\n"
            "+# [BLUEPRINT] MOD-GATE_ENGINE | docs/foo.md\n"
            "+# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert violations == []

    def test_same_spelling_pass(self) -> None:
        """同模块同拼写（bp==am 完全相同，项目 2284 文件惯例）→ 无违规。

        治本（#ARCH-130 P0-A 连带，2026-08-19）：原 normalize 相等即判违规，
        把同模块同拼写（如 bp=MOD-INF-016, am=MOD-INF-016）误判为双拼写——
        实为项目惯例且语义正确。修复后仅原始不同但 normalize 相等才阻断。
        """
        py_file = "src/zephyr/foo.py"
        content = (
            "# [BLUEPRINT] MOD-INF-016 | docs/foo.md\n"
            "# [A_module] module_id=MOD-INF-016\n"
        )
        diff = (
            "@@ -0,0 +1,2 @@\n"
            "+# [BLUEPRINT] MOD-INF-016 | docs/foo.md\n"
            "+# [A_module] module_id=MOD-INF-016\n"
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert violations == []

    def test_only_blueprint_no_amodule(self) -> None:
        """仅有 [BLUEPRINT] 无 [A_module] → 无违规。"""
        py_file = "src/zephyr/foo.py"
        content = "# [BLUEPRINT] MOD-GATE_ENGINE | docs/foo.md\nprint('hi')\n"
        diff = "@@ -0,0 +1,1 @@\n+# [BLUEPRINT] MOD-GATE_ENGINE | docs/foo.md\n"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert violations == []

    def test_noqa_escape(self) -> None:
        """noqa 逃生标记 → 无违规。"""
        py_file = "src/zephyr/foo.py"
        content = (
            "# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-error_pattern_library\n"
            "# noqa: blueprint-amodule-cross-check legacy header migration\n"
        )
        diff = (
            "@@ -0,0 +1,3 @@\n"
            "+# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "+# [A_module] module_id=MOD-GOV-error_pattern_library\n"
            "+# noqa: blueprint-amodule-cross-check legacy header migration\n"
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert violations == []

    def test_unchanged_header_not_checked(self) -> None:
        """存量头部未改动 → 不检测（diff-based）。"""
        py_file = "src/zephyr/foo.py"
        content = (
            "# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-error_pattern_library\n"
            "print('new')\n"
        )
        diff = "@@ -2,0 +3,1 @@\n+print('new')\n"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert violations == []

    def test_no_added_lines_skip(self) -> None:
        """无 added 行 → 跳过。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: ""},
            staged_contents={py_file: "# [BLUEPRINT] MOD-GOV_foo\n"},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert violations == []

    def test_empty_content_skip(self) -> None:
        """空文件内容 → 跳过。"""
        py_file = "src/zephyr/foo.py"
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: "@@ -0,0 +1,1 @@\n+# foo\n"},
            staged_contents={py_file: ""},
        )
        violations = _check_cross_consistency(gw, [py_file])
        assert violations == []


# ---------------------------------------------------------------------------
# TestFormatViolations
# ---------------------------------------------------------------------------

class TestFormatViolations:
    """_format_violations 格式化。"""

    def test_single_violation(self) -> None:
        passed, msg = _format_violations(
            ["  foo.py: [BLUEPRINT] module_id='MOD-GOV_foo' 与 [A_module] module_id='MOD-GOV-foo' 是同模块双拼写"]
        )
        assert passed is False
        assert "BLUEPRINT-AMODULE-CROSS-CHECK" in msg
        assert "ARCH-MODULE-ID-DUAL-SPELLING-001" in msg
        assert "foo.py" in msg

    def test_multiple_violations(self) -> None:
        violations = [
            "  a.py: dual-spelling",
            "  b.py: dual-spelling",
        ]
        passed, msg = _format_violations(violations)
        assert passed is False
        assert "a.py" in msg
        assert "b.py" in msg


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------

class TestGatewayIntegration:
    """mock gateway 完整流程测试。"""

    def test_no_py_files_passes(self) -> None:
        """无 staged .py → 放行。"""
        gw = _make_gateway(diff_files=[], file_diffs={}, staged_contents={})
        gate = make_blueprint_amodule_cross_check_gate()
        passed, msg = gate.check(gw, [])
        assert passed is True
        assert msg == ""

    def test_different_modules_passes(self) -> None:
        """不同模块 → 放行。"""
        py_file = "src/zephyr/foo.py"
        content = (
            "# [BLUEPRINT] MOD-GATE_ENGINE | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
        )
        diff = (
            "@@ -0,0 +1,2 @@\n"
            "+# [BLUEPRINT] MOD-GATE_ENGINE | docs/foo.md\n"
            "+# [A_module] module_id=MOD-GOV-domain_fk_gate\n"
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        gate = make_blueprint_amodule_cross_check_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is True

    def test_dual_spelling_blocks(self) -> None:
        """双拼写 → 阻断。"""
        py_file = "src/zephyr/foo.py"
        content = (
            "# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-error_pattern_library\n"
        )
        diff = (
            "@@ -0,0 +1,2 @@\n"
            "+# [BLUEPRINT] MOD-GOV_error_pattern_library | docs/foo.md\n"
            "+# [A_module] module_id=MOD-GOV-error_pattern_library\n"
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        gate = make_blueprint_amodule_cross_check_gate()
        passed, msg = gate.check(gw, [py_file])
        assert passed is False
        assert "BLUEPRINT-AMODULE-CROSS-CHECK" in msg
        assert "MOD-GOV_error_pattern_library" in msg

    def test_tests_path_exempt(self) -> None:
        """tests/ 路径豁免。"""
        py_file = "tests/governance/test_foo.py"
        content = (
            "# [BLUEPRINT] MOD-GOV_test_foo | docs/foo.md\n"
            "# [A_module] module_id=MOD-GOV-test_foo\n"
        )
        diff = (
            "@@ -0,0 +1,2 @@\n"
            "+# [BLUEPRINT] MOD-GOV_test_foo | docs/foo.md\n"
            "+# [A_module] module_id=MOD-GOV-test_foo\n"
        )
        gw = _make_gateway(
            diff_files=[py_file],
            file_diffs={py_file: diff},
            staged_contents={py_file: content},
        )
        gate = make_blueprint_amodule_cross_check_gate()
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
    gw.run_git = MagicMock(side_effect=_run_git)
    return gw
