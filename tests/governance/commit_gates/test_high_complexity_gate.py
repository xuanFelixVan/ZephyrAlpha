# [A_test] module_id: SRC-TST-2204 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-high_complexity_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_high_complexity_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_high_complexity_gate.py — NO-HIGH-COMPLEXITY 门禁单测

权威依据：high_complexity_gate.py（make_high_complexity_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestCyclomaticComplexity: _cyclomatic_complexity 纯函数（命中/安全/边界/If/For/While/Except/BoolOp/comprehension）
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含高复杂度函数 → 阻断 (passed=False)
  - 新增文件安全 → 放行 (passed=True)
  - tests/ 豁免
  - fail-open on git diff 失败
  - fail-open on git diff 异常
  - fail-open on AST 解析失败（SyntaxError）

测试隔离：MagicMock 模拟 gateway._run_git，不读/不写真实仓库。
"""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.high_complexity_gate import (  # noqa: E402
    _MAX_COMPLEXITY,
    _cyclomatic_complexity,
    make_high_complexity_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, file_contents=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回文件列表；git show :path 返回文件内容；
    per-file diff 视为全文件新增（行号 1..N 与文件内容对齐）。"""
    gw = MagicMock()
    gw.project_root = str(_PROJECT_ROOT)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw._run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if len(cmd) >= 3 and cmd[1] == "show" and cmd[2].startswith(":"):
            py_file = cmd[2][1:].replace("\\", "/")
            return _MockResult(0, (file_contents or {}).get(py_file, ""))
        py_file = cmd[-1].replace("\\", "/")
        content = (file_contents or {}).get(py_file, "")
        lines = content.splitlines()
        if not lines:
            return _MockResult(0, f"+++ b/{py_file}")
        diff_lines = [f"+++ b/{py_file}", f"@@ -0,0 +1,{len(lines)} @@"]
        diff_lines.extend(f"+{ln}" for ln in lines)
        return _MockResult(0, "\n".join(diff_lines))

    gw._run_git = _run_git
    return gw


def _make_func_with_n_ifs(n: int) -> str:
    """生成含 n 个 if 语句的函数源码（complexity = 1 + n，def 在第 1 行）。"""
    if n == 0:
        return "def f():\n    pass\n"
    ifs = "\n".join(f"    if x{i}: pass" for i in range(n))
    return f"def f():\n{ifs}\n"


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_high_complexity_gate(), GateSpec)

    def test_gate_id(self):
        assert make_high_complexity_gate().gate_id == "NO-HIGH-COMPLEXITY"

    def test_priority(self):
        assert make_high_complexity_gate().priority == 85


# ---------------------------------------------------------------------------
# TestCyclomaticComplexity — 纯函数级检测
# ---------------------------------------------------------------------------
class TestCyclomaticComplexity:
    def _complexity(self, code):
        node = ast.parse(code).body[0]
        return _cyclomatic_complexity(node)

    def test_base_complexity_one(self):
        assert self._complexity("def f():\n    pass\n") == 1

    def test_violation_sixteen_ifs(self):
        # 15 ifs → complexity = 1 + 15 = 16 > 15
        assert self._complexity(_make_func_with_n_ifs(15)) == 16

    def test_safe_fifteen_ifs(self):
        # 14 ifs → complexity = 1 + 14 = 15 (不违规，>15 才违规)
        assert self._complexity(_make_func_with_n_ifs(14)) == 15

    def test_boundary_fifteen_not_violation(self):
        assert self._complexity(_make_func_with_n_ifs(14)) == _MAX_COMPLEXITY

    def test_boundary_sixteen_is_violation(self):
        assert self._complexity(_make_func_with_n_ifs(15)) == _MAX_COMPLEXITY + 1

    def test_for_and_while_counted(self):
        code = (
            "def f():\n"
            "    for x in y: pass\n"
            "    while a: pass\n"
        )
        # base 1 + For 1 + While 1 = 3
        assert self._complexity(code) == 3

    def test_except_handler_counted(self):
        code = (
            "def f():\n"
            "    try:\n"
            "        pass\n"
            "    except Exception:\n"
            "        pass\n"
        )
        # base 1 + ExceptHandler 1 = 2
        assert self._complexity(code) == 2

    def test_boolop_counted(self):
        code = "def f():\n    return a and b and c\n"
        # base 1 + BoolOp(3 values → +2) = 3
        assert self._complexity(code) == 3

    def test_comprehension_ifs_counted(self):
        code = "def f():\n    return [x for x in y if cond1 if cond2]\n"
        # base 1 + comprehension(2 ifs → +2) = 3
        assert self._complexity(code) == 3

    def test_ifexp_counted(self):
        code = "def f():\n    return 1 if cond else 2\n"
        # base 1 + IfExp 1 = 2
        assert self._complexity(code) == 2


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_file_high_complexity_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = _make_func_with_n_ifs(15)  # complexity=16
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_high_complexity_gate().check(gw, [])
        assert not passed
        assert "NO-HIGH-COMPLEXITY" in msg
        assert "complexity=16" in msg

    def test_new_file_safe_passes(self):
        blue = "src/zephyr/trading/mod.py"
        content = _make_func_with_n_ifs(14)  # complexity=15
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_high_complexity_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self):
        red = "tests/governance/test_something.py"
        content = _make_func_with_n_ifs(15)  # complexity=16
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_high_complexity_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_high_complexity_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_high_complexity_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self):
        red = "src/zephyr/trading/mod.py"
        content = "def f(\n    if x: pass\n"  # 语法错误（缺闭括号）
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_high_complexity_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""
