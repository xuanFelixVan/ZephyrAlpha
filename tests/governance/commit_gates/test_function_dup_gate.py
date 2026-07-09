# [A_test] module_id: SRC-TST-2222 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-function_dup_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_function_dup_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_function_dup_gate.py — FUNCTION-DUP 门禁单测

权威依据：function_dup_gate.py（make_function_dup_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestBodyHash: _function_body_hash 纯函数（排除 docstring / 相同 body 同 hash / 不同 body 不同 hash）
- TestExtractFunctions: _extract_top_level_functions（顶层函数 / 跳过方法）
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含同目录同名同实现函数 → 阻断 (passed=False)
  - 同名不同实现 → 放行 (passed=True)
  - 安全无重复 → 放行
  - tests/ 豁免
  - fail-open on git diff 失败
  - fail-open on git diff 异常
  - fail-open on AST 解析失败（SyntaxError）

测试隔离：MagicMock 模拟 gateway._run_git，tmp_path 创建真实 .py 文件（gate
通过 os.path.join(wt_root, rel) 读取磁盘文件 + os.listdir 扫描同目录兄弟文件）。
"""
from __future__ import annotations

import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.function_dup_gate import (  # noqa: E402
    _extract_top_level_functions,
    _function_body_hash,
    make_function_dup_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_path, staged_files=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回相对文件列表；--show-toplevel 返回 tmp_path。
    gate 通过 os.path.join(wt_root, rel) 拼绝对路径并 open() 读盘，故测试需在
    tmp_path 下真实创建文件。"""
    gw = MagicMock()
    gw.project_root = str(tmp_path)

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
        if "rev-parse" in cmd and "--show-toplevel" in cmd:
            return _MockResult(0, str(tmp_path))
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


def _write_file(tmp_path, rel_path, content):
    """在 tmp_path 下创建 rel_path 文件，返回相对路径（正斜杠）。"""
    rel = rel_path.replace("\\", "/")
    full = tmp_path / rel.replace("/", os.sep)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return rel


@pytest.fixture(autouse=True)
def _shadow_open(monkeypatch):
    """源文件用 open(path).read() 未关闭文件句柄（ResourceWarning）。
    注入 shadow open：read() 后立即关闭真实 fd，消除 ResourceWarning。"""
    import builtins
    _real_open = builtins.open

    class _AutoClose:
        def __init__(self, fp):
            self._fp = fp

        def read(self, *a, **k):
            try:
                return self._fp.read(*a, **k)
            finally:
                self._fp.close()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._fp.close()

        def __getattr__(self, name):
            return getattr(self._fp, name)

    def _shadow(file, mode="r", *args, **kwargs):
        return _AutoClose(_real_open(file, mode, *args, **kwargs))

    import zephyr.governance.commit_gates.function_dup_gate as mod
    monkeypatch.setattr(mod, "open", _shadow, raising=False)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_function_dup_gate(), GateSpec)

    def test_gate_id(self):
        assert make_function_dup_gate().gate_id == "FUNCTION-DUP"

    def test_priority(self):
        assert make_function_dup_gate().priority == 90


# ---------------------------------------------------------------------------
# TestBodyHash — _function_body_hash 纯函数
# ---------------------------------------------------------------------------
class TestBodyHash:
    def test_excludes_docstring(self):
        tree = ast.parse('def foo():\n    """doc"""\n    return 42\n')
        func = tree.body[0]
        h = _function_body_hash(func)
        # 仅 return 42 参与 hash，docstring 被排除
        assert h == _function_body_hash(
            ast.parse("def foo():\n    return 42\n").body[0]
        )

    def test_same_body_same_hash(self):
        a = ast.parse("def foo():\n    x = 1\n    return x\n").body[0]
        b = ast.parse("def bar():\n    x = 1\n    return x\n").body[0]
        assert _function_body_hash(a) == _function_body_hash(b)

    def test_different_body_different_hash(self):
        a = ast.parse("def foo():\n    return 42\n").body[0]
        b = ast.parse("def foo():\n    return 99\n").body[0]
        assert _function_body_hash(a) != _function_body_hash(b)

    def test_hash_is_16_chars(self):
        func = ast.parse("def foo():\n    return 42\n").body[0]
        assert len(_function_body_hash(func)) == 16


# ---------------------------------------------------------------------------
# TestExtractFunctions — _extract_top_level_functions
# ---------------------------------------------------------------------------
class TestExtractFunctions:
    def test_extracts_top_level_functions(self):
        tree = ast.parse("def foo():\n    return 1\n\ndef bar():\n    return 2\n")
        result = _extract_top_level_functions(tree)
        assert set(result.keys()) == {"foo", "bar"}

    def test_skips_methods_inside_class(self):
        tree = ast.parse(
            "class C:\n"
            "    def foo(self):\n"
            "        return 1\n"
        )
        result = _extract_top_level_functions(tree)
        assert result == {}  # 方法不计入顶层函数

    def test_includes_async_functions(self):
        tree = ast.parse("async def foo():\n    return 1\n")
        result = _extract_top_level_functions(tree)
        assert "foo" in result


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_dup_function_blocked(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        body = "def foo():\n    return 42\n"
        _write_file(tmp_path, red, body)
        # 同目录兄弟文件含同名同实现
        _write_file(tmp_path, "src/zephyr/trading/existing.py", body)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_function_dup_gate().check(gw, [])
        assert not passed
        assert "FUNCTION-DUP" in msg or "重复函数" in msg
        assert "foo" in msg

    def test_same_name_diff_body_passes(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        _write_file(tmp_path, red, "def foo():\n    return 42\n")
        # 同名但实现不同 → 不算重复
        _write_file(tmp_path, "src/zephyr/trading/existing.py", "def foo():\n    return 99\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_safe_no_dup_passes(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        _write_file(tmp_path, red, "def foo():\n    return 42\n")
        # 兄弟文件无同名函数
        _write_file(tmp_path, "src/zephyr/trading/existing.py", "def bar():\n    return 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_no_sibling_files_passes(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        _write_file(tmp_path, red, "def foo():\n    return 42\n")
        # 无兄弟文件
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self, tmp_path):
        red = "tests/governance/test_something.py"
        body = "def foo():\n    return 42\n"
        _write_file(tmp_path, red, body)
        _write_file(tmp_path, "tests/governance/test_other.py", body)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_fails=True)
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_raises=True)
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        _write_file(tmp_path, red, "def foo(\n    pass\n")  # 语法错误
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""

    def test_no_top_level_functions_passes(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        _write_file(tmp_path, red, "X = 1\n")
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_function_dup_gate().check(gw, [])
        assert passed
        assert msg == ""
