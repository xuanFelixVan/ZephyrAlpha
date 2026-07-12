# [A_test] module_id: SRC-TST-2217 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_tests_coverage_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_tests_coverage_gate.py — META-TESTS-COVERAGE meta-gate 单测

权威依据：tests_coverage_gate.py（make_tests_coverage_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestHeaderRegex: _TESTS_HEADER_RE 正则提取（命中/豁免/无声明/跨行bug修复）
- TestExemptValues: _EXEMPT_VALUES 豁免集合
- TestGatewayIntegration: mock gateway + tmp_path 文件系统测试
  - 无 gate 变更 → 放行
  - gate 变更且全部测试存在 → 放行
  - gate 变更但测试缺失 → 阻断
  - [TESTS] 豁免值 → 放行
  - _ 前缀文件跳过
  - 无 [TESTS] 头部 → 跳过（放行）
  - fail-open on listdir 失败
  - fail-open on gate 目录不存在
  - Windows 路径分隔符

测试隔离：tmp_path 构造临时 gate 目录，MagicMock 模拟 gateway.project_root，
不读/不写真实仓库。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.tests_coverage_gate import (  # noqa: E402
    _EXEMPT_VALUES,
    _TESTS_HEADER_RE,
    make_tests_coverage_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GATE_HEADER_TEMPLATE = """\
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md
# [MODULE] zephyr.governance.commit_gates.{name}
# [DOMAIN] D_GOVERNANCE
# [TESTS] {tests_path}
# [TTL] permanent
\"\"\"{name}.py — sample gate\"\"\"
"""


def _write_gate_file(gate_dir: Path, name: str, tests_path: str = "—") -> Path:
    """在 gate_dir 下创建一个假的 gate .py 文件，头部含 [TESTS] 声明。"""
    gate_dir.mkdir(parents=True, exist_ok=True)
    content = _GATE_HEADER_TEMPLATE.format(name=name, tests_path=tests_path)
    p = gate_dir / f"{name}.py"
    p.write_text(content, encoding="utf-8")
    return p


def _make_gateway(project_root: str):
    """构造 mock gateway——只需 project_root 属性。"""
    gw = MagicMock()
    gw.project_root = project_root
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------

class TestGateSpecFields:
    """验证 make_tests_coverage_gate() 返回的 GateSpec 字段。"""

    def test_returns_gate_spec(self):
        spec = make_tests_coverage_gate()
        assert isinstance(spec, GateSpec)

    def test_gate_id(self):
        spec = make_tests_coverage_gate()
        assert spec.gate_id == "META-TESTS-COVERAGE"

    def test_priority_is_95(self):
        spec = make_tests_coverage_gate()
        assert spec.priority == 95

    def test_check_is_callable(self):
        spec = make_tests_coverage_gate()
        assert callable(spec.check)


# ---------------------------------------------------------------------------
# TestHeaderRegex
# ---------------------------------------------------------------------------

class TestHeaderRegex:
    """验证 _TESTS_HEADER_RE 正则提取逻辑。"""

    def test_extracts_path(self):
        head = "# [TESTS] tests/governance/commit_gates/test_foo.py\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == "tests/governance/commit_gates/test_foo.py"

    def test_extracts_path_with_spaces(self):
        head = "#   [TESTS]    tests/foo/test_bar.py   \n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == "tests/foo/test_bar.py"

    def test_empty_tests_value(self):
        head = "# [TESTS]\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == ""

    def test_dash_exempt(self):
        head = "# [TESTS] —\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == "—"

    def test_none_exempt(self):
        head = "# [TESTS] none\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == "none"

    def test_no_tests_header(self):
        head = "# [MODULE] some.module\n# [DOMAIN] D_GOVERNANCE\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is None

    def test_no_cross_line_extraction_bug(self):
        """正则修复后的关键测试：[TESTS] 后换行不应匹配到下一行内容。

        旧正则用 \\s* 会匹配 \\n，导致从 '# [TESTS]\\nfoo' 中提取 'foo'。
        新正则用 [ \\t]* 只匹配空格和 tab，正确提取空字符串。
        """
        head = "# [TESTS]\n\"\"\"docstring\"\"\"\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        # 应提取空字符串，而非 '"""docstring"""'
        assert m.group(1).strip() == ""

    def test_hash_no_space_before_bracket(self):
        head = "#[TESTS] tests/foo.py\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == "tests/foo.py"

    def test_multiple_lines_finds_first(self):
        head = (
            "# [MODULE] foo\n"
            "# [TESTS] tests/foo/test_bar.py\n"
            "# [TTL] permanent\n"
        )
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == "tests/foo/test_bar.py"

    def test_tab_separator(self):
        head = "#\t[TESTS]\ttests/foo.py\n"
        m = _TESTS_HEADER_RE.search(head)
        assert m is not None
        assert m.group(1).strip() == "tests/foo.py"


# ---------------------------------------------------------------------------
# TestExemptValues
# ---------------------------------------------------------------------------

class TestExemptValues:
    """验证 _EXEMPT_VALUES 豁免集合。"""

    @pytest.mark.parametrize("val", ["", "—", "-", "none", "None", "无", "N/A", "n/a"])
    def test_exempt_value_in_set(self, val):
        assert val in _EXEMPT_VALUES

    def test_real_path_not_exempt(self):
        assert "tests/foo/test_bar.py" not in _EXEMPT_VALUES

    def test_is_frozenset(self):
        assert isinstance(_EXEMPT_VALUES, frozenset)


# ---------------------------------------------------------------------------
# TestGatewayIntegration
# ---------------------------------------------------------------------------

class TestGatewayIntegration:
    """mock gateway + tmp_path 文件系统集成测试。"""

    def test_no_gate_change_passes(self, tmp_path):
        """staged 文件不含 commit_gates/*.py 变更 → 放行。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "dummy_gate", "tests/nonexistent.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/other/file.py"])
        assert ok is True
        assert msg == ""

    def test_all_tests_exist_passes(self, tmp_path):
        """gate 变更且所有 [TESTS] 声明的文件都存在 → 放行。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        tests_dir = tmp_path / "tests" / "governance" / "commit_gates"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_foo.py").write_text("# test", encoding="utf-8")
        _write_gate_file(gate_dir, "foo_gate", "tests/governance/commit_gates/test_foo.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/foo_gate.py"])
        assert ok is True
        assert msg == ""

    def test_missing_test_blocks(self, tmp_path):
        """gate 变更但 [TESTS] 声明的文件不存在 → 阻断。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "foo_gate", "tests/nonexistent/test_foo.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/foo_gate.py"])
        assert ok is False
        assert "META-TESTS-COVERAGE" in msg
        assert "foo_gate.py" in msg
        assert "tests/nonexistent/test_foo.py" in msg

    def test_exempt_value_passes(self, tmp_path):
        """[TESTS] 声明为豁免值 → 放行。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "foo_gate", "—")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/foo_gate.py"])
        assert ok is True

    @pytest.mark.parametrize("exempt", ["", "—", "-", "none", "None", "无", "N/A", "n/a"])
    def test_all_exempt_values_pass(self, tmp_path, exempt):
        """所有豁免值都应放行。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "foo_gate", exempt)
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, _ = spec.check(gw, files=["src/zephyr/governance/commit_gates/foo_gate.py"])
        assert ok is True

    def test_underscore_prefix_skipped(self, tmp_path):
        """_ 前缀文件（helpers）跳过，即使无测试也放行。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "_helper", "tests/nonexistent.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/_helper.py"])
        assert ok is True
        assert msg == ""

    def test_no_tests_header_skipped(self, tmp_path):
        """无 [TESTS] 头部的文件跳过（不声明就不检测）。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        gate_dir.mkdir(parents=True, exist_ok=True)
        (gate_dir / "no_header.py").write_text(
            "# [MODULE] foo\n# just a comment\n", encoding="utf-8"
        )
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/no_header.py"])
        assert ok is True

    def test_fail_open_on_listdir_error(self, tmp_path):
        """gate 目录 listdir 失败 → fail-open（放行）。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "foo_gate", "tests/nonexistent.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        original_listdir = os.listdir

        def _fail_listdir(path):
            if str(path) == str(gate_dir):
                raise OSError("mock listdir failure")
            return original_listdir(path)

        original = os.listdir
        os.listdir = _fail_listdir
        try:
            ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/foo_gate.py"])
            assert ok is True
            assert msg == ""
        finally:
            os.listdir = original

    def test_fail_open_on_gate_dir_not_exist(self, tmp_path):
        """gate 目录不存在 → fail-open（放行）。"""
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/foo_gate.py"])
        assert ok is True
        assert msg == ""

    def test_windows_path_separators(self, tmp_path):
        """Windows 路径反斜杠也应触发检测。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "foo_gate", "tests/nonexistent/test_foo.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        win_path = "src\\zephyr\\governance\\commit_gates\\foo_gate.py"
        ok, msg = spec.check(gw, files=[win_path])
        assert ok is False
        assert "foo_gate.py" in msg

    def test_multiple_violations_all_reported(self, tmp_path):
        """多个 gate 测试缺失时全部报告。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "foo_gate", "tests/missing_foo.py")
        _write_gate_file(gate_dir, "bar_gate", "tests/missing_bar.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/foo_gate.py"])
        assert ok is False
        assert "foo_gate.py" in msg
        assert "bar_gate.py" in msg

    def test_mixed_violation_and_ok(self, tmp_path):
        """一个 gate 测试存在，另一个缺失 → 只报缺失的。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "test_ok.py").write_text("# test", encoding="utf-8")
        _write_gate_file(gate_dir, "ok_gate", "tests/test_ok.py")
        _write_gate_file(gate_dir, "bad_gate", "tests/test_missing.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/ok_gate.py"])
        assert ok is False
        assert "bad_gate.py" in msg
        assert "ok_gate.py" not in msg

    def test_non_py_file_in_gate_dir_ignored(self, tmp_path):
        """gate 目录下的非 .py 文件（如 README.md）被忽略。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        gate_dir.mkdir(parents=True, exist_ok=True)
        (gate_dir / "README.md").write_text("# [TESTS] tests/nonexistent.py", encoding="utf-8")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/README.md"])
        assert ok is True

    def test_trigger_only_on_gate_dir_files(self, tmp_path):
        """只有 commit_gates/*.py 变更才触发，其他 .py 变换不触发。"""
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        ok, msg = spec.check(gw, files=["src/zephyr/other/module.py"])
        assert ok is True
        assert msg == ""

    def test_trigger_on_any_gate_py(self, tmp_path):
        """commit_gates/ 下任意 .py 变更都触发扫描整个目录。"""
        gate_dir = tmp_path / _GATE_DIR_REL
        _write_gate_file(gate_dir, "foo_gate", "tests/nonexistent.py")
        gw = _make_gateway(str(tmp_path))
        spec = make_tests_coverage_gate()
        # 触发文件是 bar_gate.py，但 foo_gate.py 的违规也会被检测到
        ok, msg = spec.check(gw, files=["src/zephyr/governance/commit_gates/bar_gate.py"])
        assert ok is False
        assert "foo_gate.py" in msg


_GATE_DIR_REL = "src/zephyr/governance/commit_gates"
