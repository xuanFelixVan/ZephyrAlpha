# [A_test] module_id: SRC-TST-2214 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-empty_handler_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_empty_handler_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_empty_handler_gate.py — EMPTY-HANDLER 门禁单测

权威依据：empty_handler_gate.py（make_empty_handler_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsHandler: _is_handler 纯函数（装饰器匹配 / 函数名前缀 / 非 handler）
- TestEmptyBody: _is_empty_handler_body / _is_empty_logger_call / _is_empty_return
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含空 handler → 阻断 (passed=False)
  - handler 含实际逻辑 → 放行
  - 非 handler 函数 pass → 放行
  - tests/ 豁免
  - fail-open on git diff 失败/异常
  - fail-open on AST 解析失败（SyntaxError）

测试隔离：MagicMock 模拟 gateway._run_git，tmp_path 创建真实 .py 文件。
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

from zephyr.governance.commit_gates.empty_handler_gate import (  # noqa: E402
    _extract_decorator_name,
    _is_empty_handler_body,
    _is_empty_logger_call,
    _is_empty_return,
    _is_handler,
    make_empty_handler_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_path, staged_files=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only（--diff-filter=A）返回文件列表；
    --show-toplevel 返回 tmp_path。"""
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
    注入 shadow open：read() 后立即关闭真实 fd。"""
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

    import zephyr.governance.commit_gates.empty_handler_gate as mod
    monkeypatch.setattr(mod, "open", _shadow, raising=False)


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_empty_handler_gate(), GateSpec)

    def test_gate_id(self):
        assert make_empty_handler_gate().gate_id == "EMPTY-HANDLER"

    def test_priority(self):
        assert make_empty_handler_gate().priority == 84


# ---------------------------------------------------------------------------
# TestIsHandler — _is_handler 纯函数
# ---------------------------------------------------------------------------
class TestIsHandler:
    def test_decorator_subscriber(self):
        func = ast.parse("@subscriber\ndef on_x(e): pass\n").body[0]
        assert _is_handler(func)

    def test_decorator_event_handler(self):
        func = ast.parse("@event_handler\ndef foo(e): pass\n").body[0]
        assert _is_handler(func)

    def test_func_name_on_prefix(self):
        func = ast.parse("def on_event(e): pass\n").body[0]
        assert _is_handler(func)

    def test_func_name_handle_prefix(self):
        func = ast.parse("def handle_click(e): pass\n").body[0]
        assert _is_handler(func)

    def test_not_handler_regular_func(self):
        func = ast.parse("def compute(x): return x + 1\n").body[0]
        assert not _is_handler(func)

    def test_decorator_name_extraction(self):
        # @foo.bar 形式
        dec = ast.parse("@foo.bar\ndef f(): pass\n").body[0].decorator_list[0]
        assert _extract_decorator_name(dec) == "bar"


# ---------------------------------------------------------------------------
# TestEmptyBody — body 判定纯函数
# ---------------------------------------------------------------------------
class TestEmptyBody:
    def test_pass_only_is_empty(self):
        func = ast.parse("def on_x(e): pass\n").body[0]
        assert _is_empty_handler_body(func)

    def test_logger_only_is_empty(self):
        func = ast.parse(
            "def on_x(e):\n"
            "    logger.info('got event')\n"
        ).body[0]
        assert _is_empty_handler_body(func)

    def test_return_none_is_empty(self):
        func = ast.parse("def on_x(e): return\n").body[0]
        assert _is_empty_handler_body(func)

    def test_docstring_only_is_empty(self):
        func = ast.parse(
            'def on_x(e):\n'
            '    """handle event"""\n'
        ).body[0]
        assert _is_empty_handler_body(func)

    def test_has_logic_not_empty(self):
        func = ast.parse(
            "def on_x(e):\n"
            "    process(e)\n"
            "    return result\n"
        ).body[0]
        assert not _is_empty_handler_body(func)

    def test_empty_logger_call_detected(self):
        stmt = ast.parse("logger.info('x')\n").body[0]
        assert _is_empty_logger_call(stmt)

    def test_empty_return_detected(self):
        stmt = ast.parse("return\n").body[0]
        assert _is_empty_return(stmt)

    def test_return_value_not_empty_return(self):
        stmt = ast.parse("return 42\n").body[0]
        assert not _is_empty_return(stmt)


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_empty_handler_blocked(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        content = (
            "@subscriber\n"
            "def on_event(event):\n"
            "    pass\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert not passed
        assert "EMPTY-HANDLER" in msg or "空 handler" in msg
        assert "on_event" in msg

    def test_handler_with_logic_passes(self, tmp_path):
        blue = "src/zephyr/trading/mod.py"
        content = (
            "@subscriber\n"
            "def on_event(event):\n"
            "    process(event)\n"
            "    return result\n"
        )
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_handler_pass_passes(self, tmp_path):
        blue = "src/zephyr/trading/mod.py"
        content = (
            "def helper():\n"
            "    pass\n"
        )
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert passed  # 非 handler 函数不检测
        assert msg == ""

    def test_logger_only_handler_blocked(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        content = (
            "@event_handler\n"
            "def handle_click(event):\n"
            "    logger.info('clicked')\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert not passed

    def test_on_prefix_empty_blocked(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        content = (
            "def on_signal(event):\n"
            "    return\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert not passed

    def test_tests_dir_exempt(self, tmp_path):
        red = "tests/governance/test_handler.py"
        content = (
            "@subscriber\n"
            "def on_event(event):\n"
            "    pass\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_fails=True)
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(tmp_path, diff_raises=True)
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self, tmp_path):
        red = "src/zephyr/trading/mod.py"
        content = (
            "@subscriber\n"
            "def on_event(event:\n"  # 语法错误
            "    pass\n"
        )
        _write_file(tmp_path, red, content)
        gw = _make_gateway(tmp_path, staged_files=[red])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert passed  # fail-open
        assert msg == ""

    def test_no_handler_in_file_passes(self, tmp_path):
        blue = "src/zephyr/trading/mod.py"
        content = (
            "def compute(x):\n"
            "    return x + 1\n"
        )
        _write_file(tmp_path, blue, content)
        gw = _make_gateway(tmp_path, staged_files=[blue])
        passed, msg = make_empty_handler_gate().check(gw, [])
        assert passed
        assert msg == ""
