# [A_test] module_id: SRC-TST-2201 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-long_param_list_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_long_param_list_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_long_param_list_gate.py — NO-LONG-PARAM-LIST 门禁单测

权威依据：long_param_list_gate.py（make_long_param_list_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestCountParams: _count_params 纯函数（命中/安全/边界/self/cls 豁免/kwonly/vararg）
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含违规 → 阻断 (passed=False)
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

from zephyr.gov_enforcement.commit_gates.long_param_list_gate import (  # noqa: E402
    _MAX_PARAMS,
    _count_params,
    make_long_param_list_gate,
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


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_long_param_list_gate(), GateSpec)

    def test_gate_id(self):
        assert make_long_param_list_gate().gate_id == "NO-LONG-PARAM-LIST"

    def test_priority(self):
        assert make_long_param_list_gate().priority == 88


# ---------------------------------------------------------------------------
# TestCountParams — 纯函数级检测
# ---------------------------------------------------------------------------
class TestCountParams:
    def _count(self, code):
        return _count_params(ast.parse(code).body[0])

    def test_violation_eight_params(self):
        assert self._count("def f(a, b, c, d, e, f, g, h):\n    pass\n") == 8

    def test_safe_seven_params(self):
        assert self._count("def f(a, b, c, d, e, f, g):\n    pass\n") == 7

    def test_boundary_seven_not_violation(self):
        assert self._count("def f(a, b, c, d, e, f, g):\n    pass\n") == _MAX_PARAMS

    def test_boundary_eight_is_violation(self):
        assert self._count("def f(a, b, c, d, e, f, g, h):\n    pass\n") == _MAX_PARAMS + 1

    def test_self_excluded(self):
        # self 不计入，8 参数含 self → 7 业务参数 → 不违规
        assert self._count("def f(self, a, b, c, d, e, f, g):\n    pass\n") == 7

    def test_cls_excluded(self):
        assert self._count("def f(cls, a, b, c, d, e, f, g):\n    pass\n") == 7

    def test_kwonly_counted(self):
        code = "def f(a, b, *, c, d, e, f, g, h):\n    pass\n"
        assert self._count(code) == 8  # 2 regular + 6 kwonly

    def test_vararg_kwarg_counted(self):
        code = "def f(a, b, c, d, e, f, *args, **kwargs):\n    pass\n"
        assert self._count(code) == 8  # 6 regular + 1 vararg + 1 kwarg

    def test_async_function_counted(self):
        code = "async def f(a, b, c, d, e, f, g, h):\n    pass\n"
        assert self._count(code) == 8

    def test_safe_few_params(self):
        assert self._count("def f(a, b):\n    pass\n") == 2


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_file_violation_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = "def f(a, b, c, d, e, f, g, h):\n    pass\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_long_param_list_gate().check(gw, [])
        assert not passed
        assert "NO-LONG-PARAM-LIST" in msg
        assert "8 params" in msg

    def test_new_file_safe_passes(self):
        blue = "src/zephyr/trading/mod.py"
        content = "def f(a, b, c, d, e, f, g):\n    pass\n"
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_long_param_list_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self):
        red = "tests/governance/test_something.py"
        content = "def f(a, b, c, d, e, f, g, h):\n    pass\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_long_param_list_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_long_param_list_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_long_param_list_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self):
        red = "src/zephyr/trading/mod.py"
        content = "def f(a, b, c, d, e, f, g, h\n    pass\n"  # 语法错误（缺冒号）
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_long_param_list_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""
