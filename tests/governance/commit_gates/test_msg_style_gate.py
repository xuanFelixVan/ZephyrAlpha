# [A_test] module_id: SRC-TST-2158 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-commit_gates | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_msg_style_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_msg_style_gate.py — MSG-STYLE 门禁单测

权威依据：msg_style_gate.py（make_msg_style_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestDetectMsgStyle: 纯函数级 AST 检测（_detect_msg_style）
  - Unicode 箭头 → 命中（f-string + 普通字符串）
  - 中文句号 。 结尾命中（f-string + 普通字符串）
  - 同时命中 → 和 。
- TestSafePatterns: 安全模式不命中
  - ASCII -> 箭头
  - 无句号结尾
  - 字面量消息 raise Foo("literal")
  - bare raise / raise var
  - Exception()/BaseException() 无参
- TestNoqaExemption: # noqa: MSG-STYLE 行级豁免
- TestGatewayIntegration: mock gateway 流程
  - 新增文件全文件检测
  - 修改文件只检测 diff 新增行
  - tests/ 豁免
  - commit_gates/ 自豁免
  - fail-open on git diff 失败
  - fail-open on AST 解析失败
"""
from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.msg_style_gate import (  # noqa: E402
    _detect_msg_style,
    _extract_string_parts,
    _filter_noqa_violations,
    _is_exception_constructor,
    _is_line_noqa,
    make_msg_style_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_returns_gate_spec_instance(self):
        spec = make_msg_style_gate()
        assert isinstance(spec, GateSpec)

    def test_gate_id(self):
        assert make_msg_style_gate().gate_id == "MSG-STYLE"

    def test_priority_is_92(self):
        # 在 DOC-REF-BROKEN(91) 之后
        assert make_msg_style_gate().priority == 92


# ---------------------------------------------------------------------------
# TestDetectMsgStyle — 纯函数级检测
# ---------------------------------------------------------------------------
class TestDetectMsgStyle:
    def test_unicode_arrow_in_fstring(self):
        code = 'raise ValueError(f"迁移 {a} → {b}")'
        tree = ast.parse(code)
        violations = _detect_msg_style(tree)
        assert len(violations) == 1
        assert violations[0][0] == 1  # lineno
        assert violations[0][1] == "ValueError"
        assert violations[0][2] == "unicode_arrow"

    def test_unicode_arrow_in_plain_string(self):
        code = 'raise RuntimeError("state → trigger")'
        tree = ast.parse(code)
        violations = _detect_msg_style(tree)
        assert len(violations) == 1
        assert violations[0][2] == "unicode_arrow"

    def test_cn_period_end_in_fstring(self):
        code = 'raise ValueError(f"无效参数: {x}。")'
        tree = ast.parse(code)
        violations = _detect_msg_style(tree)
        assert len(violations) == 1
        assert violations[0][2] == "cn_period_end"

    def test_cn_period_end_in_plain_string(self):
        code = 'raise RuntimeError("参数无效。")'
        tree = ast.parse(code)
        violations = _detect_msg_style(tree)
        assert len(violations) == 1
        assert violations[0][2] == "cn_period_end"

    def test_both_arrow_and_period(self):
        code = 'raise ValueError(f"状态 → 触发。")'
        tree = ast.parse(code)
        violations = _detect_msg_style(tree)
        assert len(violations) == 2
        types = {v[2] for v in violations}
        assert types == {"unicode_arrow", "cn_period_end"}

    def test_exception_subclass_detected(self):
        code = 'raise MyCustomError(f"失败 → 终止。")'
        tree = ast.parse(code)
        violations = _detect_msg_style(tree)
        assert len(violations) == 2
        assert violations[0][1] == "MyCustomError"

    def test_attribute_exception_detected(self):
        code = 'raise self.MyError(f"x → y。")'
        tree = ast.parse(code)
        violations = _detect_msg_style(tree)
        assert len(violations) == 2
        assert violations[0][1] == "MyError"


# ---------------------------------------------------------------------------
# TestSafePatterns — 安全模式不命中
# ---------------------------------------------------------------------------
class TestSafePatterns:
    def test_ascii_arrow_safe(self):
        code = 'raise ValueError(f"迁移 {a} -> {b}")'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_no_period_end_safe(self):
        code = 'raise RuntimeError("参数无效")'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_literal_message_safe(self):
        code = 'raise FooError("some literal message")'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_bare_raise_safe(self):
        code = 'raise'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_raise_variable_safe(self):
        code = 'raise some_exception_var'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_exception_no_args_safe(self):
        code = 'raise Exception()'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_non_string_first_arg_safe(self):
        code = 'raise FooError(some_var)'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_period_in_middle_safe(self):
        # 。 在中间不违规（只检查结尾）
        code = 'raise ValueError("x。y")'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []

    def test_fstring_ending_with_formatted_value_safe(self):
        # f-string 以 {var} 结尾，最后一个字面量部分不以 。 结尾
        code = 'raise ValueError(f"prefix {var}")'
        tree = ast.parse(code)
        assert _detect_msg_style(tree) == []


# ---------------------------------------------------------------------------
# TestNoqaExemption — 行级豁免
# ---------------------------------------------------------------------------
class TestNoqaExemption:
    def test_noqa_line_exempted(self):
        code = 'raise ValueError(f"x → y")  # noqa: MSG-STYLE\n'
        violations = _detect_msg_style(ast.parse(code))
        filtered = _filter_noqa_violations(code, violations)
        assert filtered == []

    def test_no_noqa_not_exempted(self):
        code = 'raise ValueError(f"x → y")\n'
        violations = _detect_msg_style(ast.parse(code))
        filtered = _filter_noqa_violations(code, violations)
        assert len(filtered) == 1

    def test_is_line_noqa_positive(self):
        content = 'raise ValueError(f"x → y")  # noqa: MSG-STYLE'
        assert _is_line_noqa(content, 1)

    def test_is_line_noqa_negative(self):
        content = 'raise ValueError(f"x → y")'
        assert not _is_line_noqa(content, 1)


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class _MockResult:
    def __init__(self, returncode=0, stdout=""):
        self.returncode = returncode
        self.stdout = stdout


class TestGatewayIntegration:
    def _make_gateway(self, diff_stdout="", added_stdout="", diff_per_file=None):
        gw = MagicMock()
        gw.project_root = str(_PROJECT_ROOT)

        def _run_git(cmd):
            if cmd[:3] == ["git", "diff", "--cached"] and "--name-only" in cmd:
                if "--diff-filter=A" in cmd:
                    return _MockResult(0, added_stdout)
                return _MockResult(0, diff_stdout)
            if cmd[:3] == ["git", "diff", "--cached"] and "--unified=0" in cmd:
                if diff_per_file:
                    fname = cmd[-1]
                    return _MockResult(0, diff_per_file.get(fname, ""))
                return _MockResult(0, "")
            if cmd == ["git", "rev-parse", "--show-toplevel"]:
                return _MockResult(0, str(_PROJECT_ROOT))
            return _MockResult(0, "")

        gw._run_git = _run_git
        return gw

    def test_new_file_with_arrow_violation(self, tmp_path):
        # 新增文件含 → 违规
        f = tmp_path / "test_new.py"
        f.write_text('raise ValueError(f"x → y")\n', encoding="utf-8")
        rel = str(f).replace("\\", "/")
        gw = self._make_gateway(diff_stdout=rel, added_stdout=rel)
        spec = make_msg_style_gate()
        passed, msg = spec.check(gw, [])
        assert not passed
        assert "unicode_arrow" in msg

    def test_new_file_with_period_violation(self, tmp_path):
        f = tmp_path / "test_new.py"
        f.write_text('raise ValueError("x。")\n', encoding="utf-8")
        rel = str(f).replace("\\", "/")
        gw = self._make_gateway(diff_stdout=rel, added_stdout=rel)
        spec = make_msg_style_gate()
        passed, msg = spec.check(gw, [])
        assert not passed
        assert "cn_period_end" in msg

    def test_new_file_safe(self, tmp_path):
        f = tmp_path / "test_new.py"
        f.write_text('raise ValueError("x -> y")\n', encoding="utf-8")
        rel = str(f).replace("\\", "/")
        gw = self._make_gateway(diff_stdout=rel, added_stdout=rel)
        spec = make_msg_style_gate()
        passed, msg = spec.check(gw, [])
        assert passed

    def test_no_py_files_safe(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("not python", encoding="utf-8")
        rel = str(f).replace("\\", "/")
        gw = self._make_gateway(diff_stdout=rel, added_stdout=rel)
        spec = make_msg_style_gate()
        passed, msg = spec.check(gw, [])
        assert passed

    def test_commit_gates_self_exempt(self, tmp_path):
        # governance/commit_gates/ 下的文件自豁免
        gate_file = tmp_path / "msg_style_gate.py"
        gate_file.write_text('raise ValueError(f"x → y。")\n', encoding="utf-8")
        rel = str(gate_file).replace("\\", "/")
        # 模拟路径含 governance/commit_gates/
        rel_exempt = "src/zephyr/governance/commit_gates/some_gate.py"
        gw = self._make_gateway(diff_stdout=rel_exempt, added_stdout=rel_exempt)
        spec = make_msg_style_gate()
        passed, msg = spec.check(gw, [])
        assert passed  # 自豁免

    def test_fail_open_on_git_diff_error(self):
        gw = MagicMock()
        gw._run_git = MagicMock(return_value=_MockResult(returncode=1))
        spec = make_msg_style_gate()
        passed, msg = spec.check(gw, [])
        assert passed  # fail-open

    def test_fail_open_on_ast_syntax_error(self, tmp_path):
        f = tmp_path / "bad.py"
        f.write_text('raise ValueError(f"x → y"\n', encoding="utf-8")  # 语法错误
        rel = str(f).replace("\\", "/")
        gw = self._make_gateway(diff_stdout=rel, added_stdout=rel)
        spec = make_msg_style_gate()
        passed, msg = spec.check(gw, [])
        assert passed  # fail-open


# ---------------------------------------------------------------------------
# TestExtractStringParts
# ---------------------------------------------------------------------------
class TestExtractStringParts:
    def test_plain_string(self):
        node = ast.parse('"hello"', mode="eval").body
        assert _extract_string_parts(node) == ["hello"]

    def test_f_string(self):
        node = ast.parse('f"prefix {var} suffix"', mode="eval").body
        parts = _extract_string_parts(node)
        assert parts == ["prefix ", " suffix"]

    def test_non_string_constant(self):
        node = ast.parse('42', mode="eval").body
        assert _extract_string_parts(node) == []

    def test_variable(self):
        node = ast.parse('some_var', mode="eval").body
        assert _extract_string_parts(node) == []
