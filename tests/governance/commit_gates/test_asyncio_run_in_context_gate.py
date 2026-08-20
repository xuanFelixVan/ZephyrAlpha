# [A_test] module_id: MOD-GOV-asyncio_run_in_context_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_asyncio_run_in_context_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_asyncio_run_in_context_gate.py — asyncio API 误用硬阻断门禁单测（ASYNCIO-RUN-IN-CONTEXT）

权威依据：asyncio_run_in_context_gate.py（make_asyncio_run_in_context_gate）
5.100 异步资源生命周期防复发

测试组（8 组 / 12 用例）：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestAsyncioRunDetected: asyncio.run() 命中 → hard-block
- TestAsyncioGetEventLoopDetected: asyncio.get_event_loop() 命中
- TestAsyncioNewEventLoopDetected: asyncio.new_event_loop() 命中
- TestCleanFilePasses: 干净文件通过
- TestNoqaExemption: # noqa: a100-asyncio  测试gate豁免检测
- TestTestExempt: tests/ 下文件豁免
- TestNonSrcZephyrExempt: 非 src/zephyr/ 文件豁免
- TestAddedLinesOnly: 存量违规非 added → 通过
- TestFailOpenGitDiff: git diff 失败 → 通过
- TestImportExemption: import 行豁免
- TestDocstringExemption: docstring 行豁免
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from tests.governance.commit_gates.gate_test_helpers import make_mock_gateway  # noqa: E402
from zephyr.gov_enforcement.commit_gates.asyncio_run_in_context_gate import (  # noqa: E402
    make_asyncio_run_in_context_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    def test_gate_id(self):
        gate = make_asyncio_run_in_context_gate()
        assert gate.gate_id == "ASYNCIO-RUN-IN-CONTEXT"

    def test_priority(self):
        gate = make_asyncio_run_in_context_gate()
        assert gate.priority == 122

    def test_is_gatespec(self):
        gate = make_asyncio_run_in_context_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestAsyncioRunDetected (hard-block 命中)
# ============================================================================


class TestAsyncioRunDetected:
    def test_asyncio_run_blocked(self):
        """src/zephyr/ 中 asyncio.run() → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway([src_file], {src_file: ["    result = asyncio.run(coro())"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "asyncio.run()" in detail
        assert "ASYNCIO-RUN-IN-CONTEXT" in detail

    def test_asyncio_run_in_assignment(self):
        """result = asyncio.run(...) → 命中"""
        src_file = "src/zephyr/gov_enforcement/bar.py"
        gw = make_mock_gateway([src_file], {src_file: ["result = asyncio.run(main())"]})
        gate = make_asyncio_run_in_context_gate()
        passed, _ = gate.check(gw, [])
        assert not passed


class TestAsyncioGetEventLoopDetected:
    def test_get_event_loop_blocked(self):
        """asyncio.get_event_loop() → hard-block"""
        src_file = "src/zephyr/infrastructure/foo.py"
        gw = make_mock_gateway([src_file], {src_file: ["    loop = asyncio.get_event_loop()"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "asyncio.get_event_loop()" in detail


class TestAsyncioNewEventLoopDetected:
    def test_new_event_loop_blocked(self):
        """asyncio.new_event_loop() → hard-block"""
        src_file = "src/zephyr/integration/foo.py"
        gw = make_mock_gateway([src_file], {src_file: ["    loop = asyncio.new_event_loop()"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "asyncio.new_event_loop()" in detail


# ============================================================================
# TestCleanFilePasses (干净文件通过)
# ============================================================================


class TestCleanFilePasses:
    def test_clean_src_zephyr_passes(self):
        """src/zephyr/ 中无 asyncio 调用 → 通过"""
        src_file = "src/zephyr/trading/clean.py"
        gw = make_mock_gateway([src_file], {src_file: ["    x = 1 + 2"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_run_coroutine_sync_passes(self):
        """canonical 替代 async_utils.run_coroutine_sync → 通过"""
        src_file = "src/zephyr/trading/good.py"
        gw = make_mock_gateway([src_file], {src_file: ["    result = async_utils.run_coroutine_sync(coro())"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestNoqaExemption
# ============================================================================


class TestNoqaExemption:
    def test_noqa_exempts(self):
        """src/zephyr/ 中 asyncio.run() + noqa:a100-asyncio → 豁免"""
        src_file = "src/zephyr/trading/legacy.py"
        gw = make_mock_gateway(
            [src_file],
            {src_file: ["    result = asyncio.run(coro())  # noqa: a100-asyncio  合法桥接场景"]},
        )
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestTestExempt
# ============================================================================


class TestTestExempt:
    def test_tests_dir_exempt(self):
        """tests/ 下文件中的 asyncio.run() → 豁免"""
        test_file = "tests/governance/commit_gates/test_foo.py"
        gw = make_mock_gateway([test_file], {test_file: ["    result = asyncio.run(coro())"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestNonSrcZephyrExempt
# ============================================================================


class TestNonSrcZephyrExempt:
    def test_non_src_zephyr_passes(self):
        """非 src/zephyr/ 文件中的 asyncio.run() → 豁免"""
        ext_file = "scripts/ops/foo.py"
        gw = make_mock_gateway([ext_file], {ext_file: ["    result = asyncio.run(coro())"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestAddedLinesOnly (存量违规非 added → 通过)
# ============================================================================


class TestAddedLinesOnly:
    def test_existing_violation_not_added_passes(self):
        """存量 asyncio.run（非 added 行）→ 通过（由 M23 监控）"""
        src_file = "src/zephyr/trading/legacy.py"
        full_content = (
            "# header comment\n\nresult = asyncio.run(coro())  # 存量违规，非 added 行\n\ndef new_func():\n    pass\n"
        )
        # 只 added 注释行 + new_func，不 added 存量违规行
        gw = make_mock_gateway(
            [src_file],
            {src_file: ["# header comment", "def new_func():", "    pass"]},
            file_contents={src_file: full_content},
        )
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # 存量违规非 added，不阻断
        assert detail == ""


# ============================================================================
# TestFailOpenGitDiff
# ============================================================================


class TestFailOpenGitDiff:
    def test_git_diff_fail_open(self):
        """git diff --name-only returncode != 0 → fail-open（通过）"""
        gw = make_mock_gateway([], {}, diff_fail=True)
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestImportExemption
# ============================================================================


class TestImportExemption:
    def test_import_line_passes(self):
        """import 行中的 asyncio.run → 豁免（误判保护）"""
        src_file = "src/zephyr/trading/foo.py"
        gw = make_mock_gateway([src_file], {src_file: ["from asyncio import run"]})
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed


# ============================================================================
# TestDocstringExemption
# ============================================================================


class TestDocstringExemption:
    def test_docstring_passes(self):
        """docstring 内的 asyncio.run() 示例 → 豁免"""
        src_file = "src/zephyr/trading/foo.py"
        full_content = (
            '"""foo.py 模块\n'
            "\n"
            "示例（禁止使用）::\n"
            "\n"
            "    result = asyncio.run(coro())  # 违规示例\n"
            '"""\n'
            "def foo():\n"
            "    pass\n"
        )
        gw = make_mock_gateway(
            [src_file],
            {
                src_file: [
                    '"""foo.py 模块',
                    "示例（禁止使用）::",
                    "    result = asyncio.run(coro())  # 违规示例",
                    '"""',
                    "def foo():",
                    "    pass",
                ]
            },
            file_contents={src_file: full_content},
        )
        gate = make_asyncio_run_in_context_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # docstring 行豁免
        assert detail == ""
