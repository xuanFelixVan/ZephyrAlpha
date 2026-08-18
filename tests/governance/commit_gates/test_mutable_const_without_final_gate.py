# [A_test] module_id: MOD-GOV-mutable_const_without_final_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_COMMIT_GATES | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_mutable_const_without_final_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_COMMIT_GATES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_mutable_const_without_final_gate.py — 可变常量缺 Final 标注硬阻断门禁单测（MUTABLE-CONST-WITHOUT-FINAL）

权威依据：mutable_const_without_final_gate.py（make_mutable_const_without_final_gate）
5.114 Final/@final 强制防复发

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestMutableConstBlocked: List/Dict/Set 字面量 + list()/dict()/set() 调用 → hard-block
- TestFinalAnnotatedPasses: X: Final = [...]（AnnAssign）→ 通过
- TestImmutableValuePasses: 不可变值（int/str/tuple）→ 通过
- TestNoqaExemption: # noqa: n114-final  测试gate豁免检测
- TestTestExempt: tests/ 下文件豁免
- TestAddedLinesOnly: 存量违规非 added → 通过
- TestFailOpenGitDiff: git diff 失败 → 通过
- TestFunctionLocalNotDetected: 函数内局部变量 → 通过（非模块级）
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from tests.governance.commit_gates.gate_test_helpers import make_mock_gateway  # noqa: E402
from zephyr.gov_enforcement.commit_gates.mutable_const_without_final_gate import (  # noqa: E402
    make_mutable_const_without_final_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    def test_gate_id(self):
        gate = make_mutable_const_without_final_gate()
        assert gate.gate_id == "MUTABLE-CONST-WITHOUT-FINAL"

    def test_priority(self):
        gate = make_mutable_const_without_final_gate()
        assert gate.priority == 123

    def test_is_gatespec(self):
        gate = make_mutable_const_without_final_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestMutableConstBlocked (hard-block 命中)
# ============================================================================


class TestMutableConstBlocked:
    def test_list_literal_blocked(self):
        """模块级 _X = [1, 2, 3] → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = "_X = [1, 2, 3]\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_X = [1, 2, 3]"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "MUTABLE-CONST-WITHOUT-FINAL" in detail
        assert "Final" in detail

    def test_dict_literal_blocked(self):
        """模块级 _D = {"a": 1} → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = '_D = {"a": 1}\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['_D = {"a": 1}']},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, _ = gate.check(gw, [])
        assert not passed

    def test_set_literal_blocked(self):
        """模块级 _S = {1, 2} → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = "_S = {1, 2}\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_S = {1, 2}"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, _ = gate.check(gw, [])
        assert not passed

    def test_list_call_blocked(self):
        """模块级 _L = list() → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = "_L = list()\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_L = list()"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, _ = gate.check(gw, [])
        assert not passed

    def test_dict_call_blocked(self):
        """模块级 _D = dict() → hard-block"""
        src_file = "src/zephyr/trading/foo.py"
        content = "_D = dict()\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_D = dict()"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, _ = gate.check(gw, [])
        assert not passed


# ============================================================================
# TestFinalAnnotatedPasses (AnnAssign 不检测)
# ============================================================================


class TestFinalAnnotatedPasses:
    def test_final_annotated_list_passes(self):
        """_X: Final = [1, 2, 3]（AnnAssign）→ 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = "from typing import Final\n\n_X: Final = [1, 2, 3]\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_X: Final = [1, 2, 3]"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_final_typed_annotated_passes(self):
        """_X: Final[list] = [1, 2, 3]（AnnAssign + 带类型）→ 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = "from typing import Final\n\n_X: Final[list] = [1, 2, 3]\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_X: Final[list] = [1, 2, 3]"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestImmutableValuePasses (不可变值不检测)
# ============================================================================


class TestImmutableValuePasses:
    def test_int_passes(self):
        """_X = 42（不可变）→ 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = "_X = 42\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_X = 42"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_str_passes(self):
        """_X = "str"（不可变）→ 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = '_X = "hello"\n'
        gw = make_mock_gateway(
            [src_file], {src_file: ['_X = "hello"']},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed

    def test_tuple_passes(self):
        """_T = (1, 2)（tuple 不可变）→ 通过"""
        src_file = "src/zephyr/trading/foo.py"
        content = "_T = (1, 2)\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_T = (1, 2)"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed


# ============================================================================
# TestNoqaExemption
# ============================================================================


class TestNoqaExemption:
    def test_noqa_exempts(self):
        """_X = [1, 2, 3] + noqa:n114-final → 豁免"""
        src_file = "src/zephyr/trading/foo.py"
        content = "_X = [1, 2, 3]  # noqa: n114-final  注册表需运行时修改\n"
        gw = make_mock_gateway(
            [src_file], {src_file: ["_X = [1, 2, 3]  # noqa: n114-final  注册表需运行时修改"]},
            file_contents={src_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestTestExempt
# ============================================================================


class TestTestExempt:
    def test_tests_dir_exempt(self):
        """tests/ 下文件中的模块级可变常量 → 豁免"""
        test_file = "tests/governance/foo.py"
        content = "_X = [1, 2, 3]\n"
        gw = make_mock_gateway(
            [test_file], {test_file: ["_X = [1, 2, 3]"]},
            file_contents={test_file: content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestAddedLinesOnly (存量违规非 added → 通过)
# ============================================================================


class TestAddedLinesOnly:
    def test_existing_violation_not_added_passes(self):
        """存量模块级可变常量（非 added 行）→ 通过（由 M25 监控）"""
        src_file = "src/zephyr/trading/legacy.py"
        full_content = (
            "# header comment\n"
            "\n"
            "_OLD = [1, 2, 3]  # 存量违规，非 added 行\n"
            "\n"
            "def new_func():\n"
            "    pass\n"
        )
        # 只 added 注释行 + new_func，不 added 存量违规行
        gw = make_mock_gateway(
            [src_file],
            {src_file: ["# header comment", "def new_func():", "    pass"]},
            file_contents={src_file: full_content},
        )
        gate = make_mutable_const_without_final_gate()
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
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestFunctionLocalNotDetected (函数内局部变量非模块级 → 通过)
# ============================================================================


class TestFunctionLocalNotDetected:
    def test_function_local_list_passes(self):
        """函数内 _X = [1, 2, 3]（局部变量）→ 通过（非模块级）"""
        src_file = "src/zephyr/trading/foo.py"
        full_content = (
            "def foo():\n"
            "    _X = [1, 2, 3]\n"
            "    return _X\n"
        )
        gw = make_mock_gateway(
            [src_file],
            {src_file: ["def foo():", "    _X = [1, 2, 3]", "    return _X"]},
            file_contents={src_file: full_content},
        )
        gate = make_mutable_const_without_final_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # 函数内局部变量非模块级，不检测
        assert detail == ""
