# [A_test] module_id: SRC-TST-2203 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-god_class_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_god_class_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_god_class_gate.py — NO-GOD-CLASS 门禁单测

权威依据：god_class_gate.py（make_god_class_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestCountMethods: _count_methods 纯函数（命中/安全/边界/async/嵌套类不计数）
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含 God Class → 阻断 (passed=False)
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

from zephyr.governance.commit_gates.god_class_gate import (  # noqa: E402
    _MAX_METHODS,
    _count_methods,
    make_god_class_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


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


def _make_class_with_methods(n: int, name: str = "Big") -> str:
    """生成含 n 个直接方法定义的类源码（class def 在第 1 行）。"""
    if n == 0:
        return f"class {name}:\n    pass\n"
    methods = "\n".join(f"    def m{i}(self): pass" for i in range(n))
    return f"class {name}:\n{methods}\n"


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_god_class_gate(), GateSpec)

    def test_gate_id(self):
        assert make_god_class_gate().gate_id == "NO-GOD-CLASS"

    def test_priority(self):
        assert make_god_class_gate().priority == 86


# ---------------------------------------------------------------------------
# TestCountMethods — 纯函数级检测
# ---------------------------------------------------------------------------
class TestCountMethods:
    def _count(self, code):
        tree = ast.parse(code)
        # 找到第一个 ClassDef
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        return _count_methods(node)

    def test_violation_twenty_one_methods(self):
        assert self._count(_make_class_with_methods(21)) == 21

    def test_safe_twenty_methods(self):
        assert self._count(_make_class_with_methods(20)) == 20

    def test_boundary_twenty_not_violation(self):
        assert self._count(_make_class_with_methods(20)) == _MAX_METHODS

    def test_boundary_twenty_one_is_violation(self):
        assert self._count(_make_class_with_methods(21)) == _MAX_METHODS + 1

    def test_zero_methods(self):
        assert self._count(_make_class_with_methods(0)) == 0

    def test_async_methods_counted(self):
        code = (
            "class C:\n"
            "    async def a(self): pass\n"
            "    async def b(self): pass\n"
        )
        assert self._count(code) == 2

    def test_nested_class_methods_not_counted(self):
        # 嵌套类的方法不计入外层类
        code = (
            "class Outer:\n"
            "    def m1(self): pass\n"
            "    class Inner:\n"
            "        def im1(self): pass\n"
            "        def im2(self): pass\n"
        )
        node = next(n for n in ast.walk(ast.parse(code)) if isinstance(n, ast.ClassDef) and n.name == "Outer")
        assert _count_methods(node) == 1  # 只计 Outer 直接方法 m1


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_file_god_class_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = _make_class_with_methods(21)
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_god_class_gate().check(gw, [])
        assert not passed
        assert "NO-GOD-CLASS" in msg
        assert "21 methods" in msg

    def test_new_file_safe_passes(self):
        blue = "src/zephyr/trading/mod.py"
        content = _make_class_with_methods(20)
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_god_class_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self):
        red = "tests/governance/test_something.py"
        content = _make_class_with_methods(21)
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_god_class_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_god_class_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_god_class_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self):
        red = "src/zephyr/trading/mod.py"
        content = "class Big(\n    pass\n"  # 语法错误（缺闭括号和冒号）
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_god_class_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""
