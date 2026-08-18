# [A_test] module_id: MOD-GOV-open_without_with_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_open_without_with_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_open_without_with_gate.py — open() 未在 with 内硬阻断门禁单测（OPEN-WITHOUT-WITH）

权威依据：open_without_with_gate.py（make_open_without_with_gate）
5.144 资源清理顺序防复发

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestBareOpenBlocked: 裸 open() → hard-block
- TestWithOpenPasses: with open(...) as f → 通过
- TestAsyncWithOpenPasses: async with open(...) → 通过
- TestOsOpenPasses: os.open()（Attribute）→ 通过（系统调用不检测）
- TestNoqaExemption: # noqa: r144-open  测试gate豁免检测
- TestTestExempt: tests/ 下文件豁免
- TestAddedLinesOnly: 存量违规非 added → 通过
- TestFailOpenGitDiff: git diff 失败 → 通过
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from tests.governance.commit_gates.gate_test_helpers import make_mock_gateway  # noqa: E402
from zephyr.gov_enforcement.commit_gates.open_without_with_gate import (  # noqa: E402
    make_open_without_with_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    def test_gate_id(self):
        gate = make_open_without_with_gate()
        assert gate.gate_id == "OPEN-WITHOUT-WITH"

    def test_priority(self):
        gate = make_open_without_with_gate()
        assert gate.priority == 124

    def test_is_gatespec(self):
        gate = make_open_without_with_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestBareOpenBlocked (hard-block 命中)
# ============================================================================


class TestBareOpenBlocked:
    def test_bare_open_blocked(self):
        """f = open("x") → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'f = open("x")\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['f = open("x")']},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "OPEN-WITHOUT-WITH" in detail
        assert "open()" in detail

    def test_open_in_call_chain_blocked(self):
        """data = open("x").read() → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'data = open("x").read()\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['data = open("x").read()']},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, _ = gate.check(gw, [])
        assert not passed

    def test_open_as_argument_blocked(self):
        """process(open("x")) → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'process(open("x"))\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['process(open("x"))']},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, _ = gate.check(gw, [])
        assert not passed


# ============================================================================
# TestWithOpenPasses (with open(...) as f → 通过)
# ============================================================================


class TestWithOpenPasses:
    def test_with_open_passes(self):
        """with open("x") as f: → 通过（open 在 with item context_expr）"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'with open("x") as f:\n    data = f.read()\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['with open("x") as f:', "    data = f.read()"]},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_with_open_multiple_items_passes(self):
        """with open("a") as fa, open("b") as fb: → 通过（两个 open 都在 with items）"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'with open("a") as fa, open("b") as fb:\n    pass\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['with open("a") as fa, open("b") as fb:', "    pass"]},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_nested_with_open_passes(self):
        """嵌套 with 内的 open → 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = (
            'with open("a") as fa:\n'
            '    with open("b") as fb:\n'
            "        pass\n"
        )
        gw = make_mock_gateway(
            [src_file],
            {src_file: ['with open("a") as fa:', '    with open("b") as fb:', "        pass"]},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestAsyncWithOpenPasses (async with open(...) → 通过)
# ============================================================================


class TestAsyncWithOpenPasses:
    def test_async_with_open_passes(self):
        """async with open("x") as f: → 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'async def foo():\n    async with open("x") as f:\n        pass\n'
        gw = make_mock_gateway(
            [src_file],
            {src_file: ["async def foo():", '    async with open("x") as f:', "        pass"]},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestOsOpenPasses (os.open() 是 Attribute → 不检测)
# ============================================================================


class TestOsOpenPasses:
    def test_os_open_passes(self):
        """os.open()（系统调用，Attribute）→ 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'fd = os.open("x", os.O_RDONLY)\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['fd = os.open("x", os.O_RDONLY)']},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestNoqaExemption
# ============================================================================


class TestNoqaExemption:
    def test_noqa_exempts(self):
        """f = open("x") + noqa:r144-open → 豁免"""
        src_file = "src/zephyr/trading/foo.py"
        content = 'f = open("x")  # noqa: r144-open  低层封装手动管理生命周期\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['f = open("x")  # noqa: r144-open  低层封装手动管理生命周期']},
            file_contents={src_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestTestExempt
# ============================================================================


class TestTestExempt:
    def test_tests_dir_exempt(self):
        """tests/ 下文件中的裸 open() → 豁免"""
        test_file = "tests/governance/foo.py"
        content = 'f = open("x")\n'
        gw = make_mock_gateway(
            [test_file], {test_file: ['f = open("x")']},
            file_contents={test_file: content},
        )
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestAddedLinesOnly (存量违规非 added → 通过)
# ============================================================================


class TestAddedLinesOnly:
    def test_existing_violation_not_added_passes(self):
        """存量裸 open（非 added 行）→ 通过（由 M27 监控）"""
        src_file = "src/zephyr/trading/legacy.py"
        full_content = (
            "# header comment\n"
            "\n"
            'f = open("x")  # 存量违规，非 added 行\n'
            "\n"
            "def new_func():\n"
            "    pass\n"
        )
        gw = make_mock_gateway(
            [src_file],
            {src_file: ["# header comment", "def new_func():", "    pass"]},
            file_contents={src_file: full_content},
        )
        gate = make_open_without_with_gate()
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
        gate = make_open_without_with_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""
