# [A_test] module_id: SRC-TST-2232 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_ch_batch_size_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_ch_batch_size_gate.py — CH-BATCH-SIZE 门禁单测

权威依据：ch_batch_size_gate.py（make_ch_batch_size_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsWriteResultCall: _is_write_result_call AST 节点判定
- TestIsExemptFile: _is_exempt_file 文件级豁免判定
- TestGatewayIntegration: mock gateway 流程
  - for 循环内 write_result 直接调用 → 阻断
  - for 循环内 ch_writer.write_result 调用 → 阻断
  - for 循环外 write_result 调用 → 放行
  - BufferedWriter 模式 → 放行
  - tests/ 豁免
  - ch_writer.py / buffered_writer.py 豁免
  - async for 循环内调用 → 阻断
  - 嵌套循环内调用 → 阻断
  - fail-open on git diff 失败
  - fail-open on ast.parse 失败
  - 新增 for 循环包裹已有 write_result → 阻断

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

from zephyr.governance.commit_gates.ch_batch_size_gate import (  # noqa: E402
    _build_parent_map,
    _find_enclosing_for,
    _is_exempt_file,
    _is_write_result_call,
    make_ch_batch_size_gate,
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
        assert isinstance(make_ch_batch_size_gate(), GateSpec)

    def test_gate_id(self):
        assert make_ch_batch_size_gate().gate_id == "CH-BATCH-SIZE"

    def test_priority(self):
        assert make_ch_batch_size_gate().priority == 36


# ---------------------------------------------------------------------------
# TestIsWriteResultCall — AST 节点判定
# ---------------------------------------------------------------------------
class TestIsWriteResultCall:
    def test_direct_call(self):
        tree = ast.parse("write_result(r)")
        call = tree.body[0].value  # Expr -> Call
        assert _is_write_result_call(call)

    def test_attribute_call(self):
        tree = ast.parse("ch_writer.write_result(r)")
        call = tree.body[0].value
        assert _is_write_result_call(call)

    def test_short_alias_call(self):
        tree = ast.parse("cw.write_result(r)")
        call = tree.body[0].value
        assert _is_write_result_call(call)

    def test_not_a_call(self):
        tree = ast.parse("x = 1")
        node = tree.body[0].value
        assert not _is_write_result_call(node)

    def test_different_function(self):
        tree = ast.parse("write_tsv(data)")
        call = tree.body[0].value
        assert not _is_write_result_call(call)

    def test_method_with_different_name(self):
        tree = ast.parse("obj.other_method()")
        call = tree.body[0].value
        assert not _is_write_result_call(call)


# ---------------------------------------------------------------------------
# TestIsExemptFile — 文件级豁免判定
# ---------------------------------------------------------------------------
class TestIsExemptFile:
    def test_ch_writer_exempt(self):
        assert _is_exempt_file("src/zephyr/data/ch_writer.py")

    def test_buffered_writer_exempt(self):
        assert _is_exempt_file("src/zephyr/data/buffered_writer.py")

    def test_normal_file_not_exempt(self):
        assert not _is_exempt_file("src/zephyr/data/scheduler.py")

    def test_backfill_not_exempt(self):
        assert not _is_exempt_file("tmp/_backfill.py")

    def test_bare_filename_ch_writer(self):
        assert _is_exempt_file("ch_writer.py")

    def test_windows_path_exempt(self):
        assert _is_exempt_file("src\\zephyr\\data\\ch_writer.py")


# ---------------------------------------------------------------------------
# TestBuildParentMap / TestFindEnclosingFor — AST 工具函数
# ---------------------------------------------------------------------------
class TestFindEnclosingFor:
    def test_inside_for(self):
        code = "for r in items:\n    write_result(r)\n"
        tree = ast.parse(code)
        parent_map = _build_parent_map(tree)
        # 找到 Call 节点
        call_node = None
        for node in ast.walk(tree):
            if _is_write_result_call(node):
                call_node = node
                break
        assert call_node is not None
        for_node = _find_enclosing_for(call_node, parent_map)
        assert for_node is not None
        assert isinstance(for_node, ast.For)

    def test_outside_for(self):
        code = "write_result(r)\n"
        tree = ast.parse(code)
        parent_map = _build_parent_map(tree)
        call_node = None
        for node in ast.walk(tree):
            if _is_write_result_call(node):
                call_node = node
                break
        assert call_node is not None
        for_node = _find_enclosing_for(call_node, parent_map)
        assert for_node is None

    def test_inside_async_for(self):
        code = "async def f():\n    async for r in items:\n        write_result(r)\n"
        tree = ast.parse(code)
        parent_map = _build_parent_map(tree)
        call_node = None
        for node in ast.walk(tree):
            if _is_write_result_call(node):
                call_node = node
                break
        assert call_node is not None
        for_node = _find_enclosing_for(call_node, parent_map)
        assert for_node is not None
        assert isinstance(for_node, ast.AsyncFor)

    def test_nested_inside_for(self):
        """嵌套循环：write_result 在内层 for 循环内。"""
        code = (
            "for outer in items:\n"
            "    for inner in outer:\n"
            "        write_result(inner)\n"
        )
        tree = ast.parse(code)
        parent_map = _build_parent_map(tree)
        call_node = None
        for node in ast.walk(tree):
            if _is_write_result_call(node):
                call_node = node
                break
        assert call_node is not None
        for_node = _find_enclosing_for(call_node, parent_map)
        assert for_node is not None
        # 应返回最近的内层 for
        assert isinstance(for_node, ast.For)

    def test_inside_if_not_for(self):
        """write_result 在 if 语句内（非 for 循环）应放行。"""
        code = "if True:\n    write_result(r)\n"
        tree = ast.parse(code)
        parent_map = _build_parent_map(tree)
        call_node = None
        for node in ast.walk(tree):
            if _is_write_result_call(node):
                call_node = node
                break
        assert call_node is not None
        for_node = _find_enclosing_for(call_node, parent_map)
        assert for_node is None

    def test_inside_while_not_for(self):
        """write_result 在 while 循环内（非 for 循环）应放行。"""
        code = "while True:\n    write_result(r)\n    break\n"
        tree = ast.parse(code)
        parent_map = _build_parent_map(tree)
        call_node = None
        for node in ast.walk(tree):
            if _is_write_result_call(node):
                call_node = node
                break
        assert call_node is not None
        for_node = _find_enclosing_for(call_node, parent_map)
        assert for_node is None


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_for_loop_write_result_blocked(self):
        """for 循环内直接调用 write_result → 阻断。"""
        red = "src/zephyr/data/scheduler.py"
        content = (
            "from zephyr.data.ch_writer import write_result\n"
            "for result in provider.fetch():\n"
            "    write_result(result)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert not passed
        assert "CH-BATCH-SIZE" in msg
        assert "BufferedWriter" in msg

    def test_for_loop_attribute_call_blocked(self):
        """for 循环内 ch_writer.write_result() 调用 → 阻断。"""
        red = "src/zephyr/data/scheduler.py"
        content = (
            "from zephyr.data import ch_writer\n"
            "for result in provider.fetch():\n"
            "    ch_writer.write_result(result)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert not passed
        assert "CH-BATCH-SIZE" in msg

    def test_outside_for_passes(self):
        """for 循环外调用 write_result → 放行。"""
        blue = "src/zephyr/data/scheduler.py"
        content = (
            "from zephyr.data.ch_writer import write_result\n"
            "write_result(single_result)\n"
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_buffered_writer_pattern_passes(self):
        """BufferedWriter 正确模式 → 放行。"""
        blue = "src/zephyr/data/scheduler.py"
        content = (
            "from zephyr.data.buffered_writer import BufferedWriter\n"
            "writer = BufferedWriter(table)\n"
            "for result in provider.fetch():\n"
            "    writer.add(result)\n"
            "writer.flush()\n"
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self):
        """tests/ 目录豁免。"""
        red = "tests/governance/test_something.py"
        content = (
            "for result in items:\n"
            "    write_result(result)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_ch_writer_exempt(self):
        """ch_writer.py 自身豁免（write_result 定义处）。"""
        red = "src/zephyr/data/ch_writer.py"
        content = (
            "def write_result(result):\n"
            "    pass\n"
            "for r in items:\n"
            "    write_result(r)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_buffered_writer_file_exempt(self):
        """buffered_writer.py 自身豁免。"""
        red = "src/zephyr/data/buffered_writer.py"
        content = (
            "for r in items:\n"
            "    write_result(r)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_async_for_blocked(self):
        """async for 循环内调用 → 阻断。"""
        red = "src/zephyr/data/scheduler.py"
        content = (
            "async def download():\n"
            "    async for result in provider.fetch():\n"
            "        write_result(result)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert not passed
        assert "CH-BATCH-SIZE" in msg

    def test_nested_loop_blocked(self):
        """嵌套循环内层调用 → 阻断。"""
        red = "src/zephyr/data/scheduler.py"
        content = (
            "for outer in items:\n"
            "    for inner in outer:\n"
            "        write_result(inner)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert not passed
        assert "CH-BATCH-SIZE" in msg

    def test_while_loop_passes(self):
        """while 循环内调用 → 放行（只检测 for/async for）。"""
        blue = "src/zephyr/data/scheduler.py"
        content = (
            "while True:\n"
            "    write_result(r)\n"
            "    break\n"
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_if_block_passes(self):
        """if 语句内调用（非 for 循环）→ 放行。"""
        blue = "src/zephyr/data/scheduler.py"
        content = (
            "if condition:\n"
            "    write_result(r)\n"
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        """git diff --name-only 失败 → fail-open。"""
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        """git diff 异常 → fail-open。"""
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_syntax_error_fail_open(self):
        """ast.parse 语法错误 → fail-open 跳过该文件。"""
        red = "src/zephyr/data/scheduler.py"
        content = "def broken(:\n    for r in items:\n        write_result(r)\n"
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed  # 语法错误 fail-open
        assert msg == ""

    def test_no_staged_files_passes(self):
        """无 staged .py 文件 → 放行。"""
        gw = _make_gateway(staged_files=[])
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_write_result_in_function_outside_for_passes(self):
        """write_result 在函数内但不在 for 循环内 → 放行。"""
        blue = "src/zephyr/data/scheduler.py"
        content = (
            "def process(result):\n"
            "    write_result(result)\n"
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_multiple_violations_reported(self):
        """多个违规都应报告。"""
        red = "src/zephyr/data/scheduler.py"
        content = (
            "for r in items1:\n"
            "    write_result(r)\n"
            "for r in items2:\n"
            "    write_result(r)\n"
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_ch_batch_size_gate().check(gw, [])
        assert not passed
        # 两个违规都报告
        assert msg.count("write_result") >= 2
