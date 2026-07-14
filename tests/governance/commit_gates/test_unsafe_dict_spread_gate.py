# [A_test] module_id: SRC-TST-2150 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-commit_gates | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_unsafe_dict_spread_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_unsafe_dict_spread_gate.py — ``**data`` 直接展开 warn 级门禁单测（UNSAFE-DICT-SPREAD）

权威依据：unsafe_dict_spread_gate.py（make_unsafe_dict_spread_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestUnsafeSpreadDetected: SomeClass(**data) 命中 → warn（passed=True + detail 非空）
- TestWarnLevelNotBlocking: warn 级永不阻断（passed 始终 True）
- TestKwargsExemption: **kwargs / **kwds 合法
- TestFilterDataclassFieldsExemption: **filter_dataclass_fields(...) 合法（正则不匹配）
- TestDictLiteralExemption: **{...} 字典字面量合法（正则不匹配）
- TestFuncCallExemption: **func(...) 函数调用合法（正则不匹配）
- TestImportExemption: import 行豁免
- TestCommentExemption: 注释行豁免
- TestDocstringExemption: docstring 行豁免
- TestTestExempt: tests/ 下文件豁免
- TestNonPyFile: 非 .py 文件豁免
- TestNoStagedFile: 空 staged → 通过
- TestFailOpenGitDiffFails: git diff 失败/异常 → 通过（fail-open）
- TestMultipleViolationsAllReported: 多违规全报告
- TestMixedSafeUnsafe: 同文件混合安全/危险模式只报危险项

测试隔离：MagicMock 模拟 gateway._run_git 返回预设 staged 文件列表 + diff content；
不读/不写真实仓库，不依赖真实 registry。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.unsafe_dict_spread_gate import (  # noqa: E402
    make_unsafe_dict_spread_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


def _make_mock_gateway(
    staged_files: list[str],
    file_diffs: dict[str, list[str]],
    file_contents: dict[str, str] | None = None,
) -> MagicMock:
    """构造 mock gateway，_run_git 根据 cmd 返回预设结果。

    Args:
        staged_files: git diff --name-only 返回的文件列表（相对路径）
        file_diffs: {py_file: [added_line1, added_line2, ...]}（added 行内容）
        file_contents: {py_file: 完整文件内容}（用于 ``git show :path`` 读取 staged 版本，
            预计算 docstring 行号集合）。若 None，则根据 file_diffs 自动生成
            "纯 added 行拼接"的简化文件内容（行号从 1 开始）。
    """
    gw = MagicMock()

    def _run_git(cmd):
        result = MagicMock()
        if "--name-only" in cmd:
            result.returncode = 0
            result.stdout = "\n".join(staged_files)
            return result
        # git show :path —— 读 staged 完整文件
        if len(cmd) >= 3 and cmd[1] == "show" and cmd[2].startswith(":"):
            py_file = cmd[2][1:].replace("\\", "/")
            content = (file_contents or {}).get(py_file)
            if content is None:
                # 默认：added 行拼成文件，行号从 1 开始
                lines = file_diffs.get(py_file, [])
                content = "\n".join(lines)
            result.returncode = 0
            result.stdout = content
            return result
        # per-file diff: cmd[-1] 是 py_file
        py_file = cmd[-1].replace("\\", "/")
        lines = file_diffs.get(py_file, [])
        # 如果提供 file_contents，查找 added 行在完整文件中的真实行号（用于 docstring 跟踪）
        if file_contents and py_file in file_contents:
            file_lines = file_contents[py_file].splitlines()
            added_with_lineno: list[tuple[int, str]] = []
            for added_content in lines:
                lineno = None
                for i, fl in enumerate(file_lines, 1):
                    if fl == added_content:
                        lineno = i
                        break
                if lineno is None:
                    lineno = 1  # 默认第 1 行
                added_with_lineno.append((lineno, added_content))
            # 若 file_diffs 未指定 added 行，用 file_contents 所有行（模拟新增文件）
            if not added_with_lineno:
                added_with_lineno = list(enumerate(file_lines, 1))
        else:
            # 无 file_contents，added 行从第 1 行开始
            added_with_lineno = list(enumerate(lines, 1))

        if added_with_lineno:
            start = added_with_lineno[0][0]
            diff_lines = [f"+++ b/{py_file}", f"@@ -0,0 +{start},{len(added_with_lineno)} @@"]
            diff_lines.extend(f"+{content}" for _, content in added_with_lineno)
        else:
            diff_lines = [f"+++ b/{py_file}"]
        result.returncode = 0
        result.stdout = "\n".join(diff_lines)
        return result

    gw._run_git.side_effect = _run_git
    return gw


# ============================================================================
# TestGateSpecFields
# ============================================================================


class TestGateSpecFields:
    def test_gate_id(self):
        gate = make_unsafe_dict_spread_gate()
        assert gate.gate_id == "UNSAFE-DICT-SPREAD"

    def test_priority(self):
        gate = make_unsafe_dict_spread_gate()
        assert gate.priority == 66

    def test_is_gatespec(self):
        gate = make_unsafe_dict_spread_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestUnsafeSpreadDetected (warn 级命中)
# ============================================================================


class TestUnsafeSpreadDetected:
    def test_simple_data_spread_warns(self, capsys):
        """SomeClass(**data) → warn（passed=True + detail 含提示）"""
        red_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["obj = WorkDAG(**data)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        # warn 级：不阻断
        assert passed
        # detail 含违规信息
        assert "WorkDAG" in detail
        assert "**data" in detail
        assert "filter_dataclass_fields" in detail  # 提示修复方式
        # stderr 输出（用户可见）
        captured = capsys.readouterr()
        assert "UNSAFE-DICT-SPREAD" in captured.err

    def test_payload_spread_warns(self):
        """SomeClass(**payload) → warn"""
        red_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["entry = NightShiftEntry(**payload)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert "NightShiftEntry" in detail
        assert "**payload" in detail

    def test_row_spread_warns(self):
        """SomeClass(**row) → warn（DB row 场景）"""
        red_file = "src/zephyr/infrastructure/some_module.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["rec = PreemptionRecord(**row)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert "PreemptionRecord" in detail
        assert "**row" in detail

    def test_nested_attribute_not_matched(self):
        """SomeClass(**data.get('x')) 不匹配（非纯标识符）—— 留给 AI 判断"""
        red_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["obj = WorkDAG(**data.get('config'))"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""  # 不匹配正则，不 warn

    def test_return_stmt_warns(self):
        """return SomeClass(**data) → warn"""
        red_file = "src/zephyr/autonomy_core/some_module.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["    return FeedbackSignal(**data)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert "FeedbackSignal" in detail


# ============================================================================
# TestWarnLevelNotBlocking
# ============================================================================


class TestWarnLevelNotBlocking:
    def test_warn_always_passes(self):
        """warn 级 gate passed 始终 True（不阻断 commit）"""
        red_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [red_file], {red_file: ["obj = WorkDAG(**data)", "obj2 = Other(**payload)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # 永远 True
        assert "WorkDAG" in detail
        assert "Other" in detail

    def test_no_violation_empty_detail(self):
        """无违规 → passed=True + detail 空"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["obj = WorkDAG(**kwargs)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestKwargsExemption (蓝队)
# ============================================================================


class TestKwargsExemption:
    def test_kwargs_passes(self):
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["obj = WorkDAG(**kwargs)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_kwds_passes(self):
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["obj = WorkDAG(**kwds)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_mixed_kwargs_and_field_passes(self):
        """field=val, **kwargs → kwargs 豁免，整行不报"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["obj = WorkDAG(name='x', **kwargs)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestFilterDataclassFieldsExemption (蓝队)
# ============================================================================


class TestFilterDataclassFieldsExemption:
    def test_filter_dataclass_fields_not_matched(self):
        """SomeClass(**filter_dataclass_fields(Cls, data)) 正则不匹配（** 后跟函数调用）"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["obj = WorkDAG(**filter_dataclass_fields(WorkDAG, data))"]},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_aliased_filter_not_matched(self):
        """SomeClass(**_filter_dataclass_fields(Cls, data)) 也豁免（函数调用）"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["obj = WorkDAG(**_filter_dataclass_fields(WorkDAG, data))"]},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestDictLiteralExemption (蓝队)
# ============================================================================


class TestDictLiteralExemption:
    def test_dict_literal_not_matched(self):
        """SomeClass(**{**data, 'extra': 1}) 正则不匹配（** 后是 {）"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["obj = WorkDAG(**{**data, 'name': 'x'})"]},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_empty_dict_literal_not_matched(self):
        """SomeClass(**{}) 正则不匹配"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["obj = WorkDAG(**{})"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestFuncCallExemption (蓝队)
# ============================================================================


class TestFuncCallExemption:
    def test_func_call_not_matched(self):
        """SomeClass(**build_kwargs()) 正则不匹配（** 后跟函数调用，结尾是 ))）"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["obj = WorkDAG(**build_kwargs())"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestImportExemption (蓝队)
# ============================================================================


class TestImportExemption:
    def test_from_import_passes(self):
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["from zephyr.shared.io.serialization import filter_dataclass_fields"]},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_plain_import_passes(self):
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["import json"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestCommentExemption (蓝队)
# ============================================================================


class TestCommentExemption:
    def test_comment_with_spread_passes(self):
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["# obj = WorkDAG(**data)  # 旧代码"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestDocstringExemption (蓝队)
# ============================================================================


class TestDocstringExemption:
    def test_docstring_with_spread_passes(self):
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ['"""obj = WorkDAG(**data)"""']}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_triple_single_quote_passes(self):
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["'''obj = WorkDAG(**data)'''"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_multiline_docstring_inner_line_exempt(self):
        """多行 docstring 中间的 ``**data`` 示例不报（行号在 docstring 集合内）"""
        blue_file = "src/zephyr/gov_enforcement/commit_gates/unsafe_dict_spread_gate.py"
        # 完整文件内容：第 2-4 行在 docstring 内
        full_content = (
            '"""模块 docstring\n'
            '检测 SomeClass(**varname) 模式\n'
            '以及 Other(**payload) 模式\n'
            '"""'
        )
        # added 行是第 3 行（docstring 内）
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["以及 Other(**payload) 模式"]},
            file_contents={blue_file: full_content},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""  # docstring 内，豁免

    def test_multiline_docstring_triple_single_quote_exempt(self):
        """多行 ''' docstring 中间的 ``**data`` 示例不报"""
        blue_file = "src/zephyr/trading/some_module.py"
        full_content = (
            "'''模块 docstring\n"
            "示例: WorkDAG(**data)\n"
            "'''"
        )
        gw = _make_mock_gateway(
            [blue_file],
            {blue_file: ["示例: WorkDAG(**data)"]},
            file_contents={blue_file: full_content},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_code_after_docstring_still_detected(self):
        """docstring 结束后的代码行仍检测——确保 docstring 跟踪正确闭合"""
        red_file = "src/zephyr/trading/some_module.py"
        full_content = (
            '"""模块 docstring\n'
            '示例: WorkDAG(**data)\n'
            '"""\n'
            "obj = RealCode(**payload)  # 这行应被检测"
        )
        # added 行是第 4 行（docstring 外）
        gw = _make_mock_gateway(
            [red_file],
            {red_file: ["obj = RealCode(**payload)  # 这行应被检测"]},
            file_contents={red_file: full_content},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert "RealCode" in detail
        assert "**payload" in detail

    def test_manifest_mode_spread_not_exempt(self):
        """R95 修复：__manifest__ = \"\"\"...\"\"\" 模式中 **data 展开应被检测（不再被错误豁免）。

        旧 bug：__manifest__ 结束独立 \"\"\" 行被误判为新 docstring 起始，导致后续
        含 ``SomeClass(**data)`` 的代码行被错误豁免。
        新方案：ast 只识别真正 docstring，__manifest__ 是 Assign 节点不豁免。
        """
        red_file = "src/zephyr/trading/some_module.py"
        full_content = (
            '__manifest__ = """\n'
            'args: []\n'
            '"""\n'
            '\n'
            'obj = RealCode(**payload)  # 这行应被检测\n'
        )
        gw = _make_mock_gateway(
            [red_file],
            {red_file: ["obj = RealCode(**payload)  # 这行应被检测"]},
            file_contents={red_file: full_content},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # UNSAFE-DICT-SPREAD 是 warn 级，passed 始终 True
        assert "RealCode" in detail
        assert "**payload" in detail

    def test_gate_self_docstring_no_warn(self):
        """gate 自身 docstring 中的示例不触发 warn（修复目标场景）"""
        gate_file = "src/zephyr/gov_enforcement/commit_gates/unsafe_dict_spread_gate.py"
        # 模拟 gate 文件的真实 docstring 片段
        full_content = (
            '"""unsafe_dict_spread_gate.py\n'
            '\n'
            '检测 SomeClass(**varname) 直接展开模式。\n'
            '豁免 **kwargs / **kwds、**filter_dataclass_fields(...)。\n'
            '"""'
        )
        gw = _make_mock_gateway(
            [gate_file],
            {gate_file: ["检测 SomeClass(**varname) 直接展开模式。"]},
            file_contents={gate_file: full_content},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""  # docstring 内，豁免


# ============================================================================
# TestTestExempt (蓝队)
# ============================================================================


class TestTestExempt:
    def test_tests_dir_passes(self):
        blue_file = "tests/governance/test_something.py"
        gw = _make_mock_gateway(
            [blue_file], {blue_file: ["obj = WorkDAG(**data)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""  # tests/ 豁免


# ============================================================================
# TestNonPyFile
# ============================================================================


class TestNonPyFile:
    def test_yaml_file_passes(self):
        gw = _make_mock_gateway(
            ["docs/registry.yaml"], {"docs/registry.yaml": ["WorkDAG(**data)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_md_file_passes(self):
        gw = _make_mock_gateway(
            ["docs/readme.md"], {"docs/readme.md": ["WorkDAG(**data)"]}
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestNoStagedFile
# ============================================================================


class TestNoStagedFile:
    def test_empty_staged_passes(self):
        gw = _make_mock_gateway([], {})
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_no_py_file_passes(self):
        gw = _make_mock_gateway(["docs/notes.md"], {})
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestFailOpenGitDiffFails
# ============================================================================


class TestFailOpenGitDiffFails:
    def test_git_diff_name_only_fails_passes(self):
        """git diff --name-only 失败 → fail-open（passed=True, detail 空）"""
        gw = MagicMock()
        result = MagicMock()
        result.returncode = 1
        result.stdout = ""
        gw._run_git.return_value = result
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # fail-open
        assert detail == ""

    def test_git_diff_exception_passes(self):
        """git diff 异常 → fail-open"""
        gw = MagicMock()
        gw._run_git.side_effect = RuntimeError("git not found")
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # fail-open
        assert detail == ""

    def test_per_file_diff_failure_skipped(self, caplog):
        """单文件 diff 失败 → 跳过该文件，不阻断整体"""
        gw = MagicMock()
        # 第一次调用 --name-only 成功
        name_result = MagicMock()
        name_result.returncode = 0
        name_result.stdout = "src/zephyr/trading/some_module.py"
        # 第二次调用 per-file diff 失败
        file_result = MagicMock()
        file_result.returncode = 1
        file_result.stdout = ""
        gw._run_git.side_effect = [name_result, file_result]
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""  # 该文件无 added 行 → 无 warn


# ============================================================================
# TestMultipleViolationsAllReported
# ============================================================================


class TestMultipleViolationsAllReported:
    def test_multiple_violations_in_same_file(self):
        red_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [red_file],
            {red_file: ["a = WorkDAG(**data)", "b = Other(**payload)"]},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert "WorkDAG" in detail
        assert "Other" in detail
        assert "**data" in detail
        assert "**payload" in detail

    def test_multiple_violations_across_files(self):
        f1 = "src/zephyr/trading/some_module.py"
        f2 = "src/zephyr/autonomy_core/other.py"
        gw = _make_mock_gateway(
            [f1, f2],
            {f1: ["a = WorkDAG(**data)"], f2: ["b = FeedbackSignal(**payload)"]},
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert "WorkDAG" in detail
        assert "FeedbackSignal" in detail
        assert f1 in detail
        assert f2 in detail


# ============================================================================
# TestMixedSafeUnsafe (蓝队 + 红队混合)
# ============================================================================


class TestMixedSafeUnsafe:
    def test_mixed_only_reports_unsafe(self):
        """同文件混合安全/危险模式，只报危险项"""
        blue_file = "src/zephyr/trading/some_module.py"
        gw = _make_mock_gateway(
            [blue_file],
            {
                blue_file: [
                    "safe = WorkDAG(**kwargs)",  # 安全
                    "safe2 = WorkDAG(**filter_dataclass_fields(WorkDAG, data))",  # 安全
                    "unsafe = Other(**payload)",  # 危险
                ]
            },
        )
        gate = make_unsafe_dict_spread_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        # 违规列表（-> 之前的部分）只含危险项
        violations_part = detail.split("->")[0]
        assert "Other" in violations_part
        assert "**payload" in violations_part
        # 安全项不在违规列表
        assert "**kwargs" not in violations_part
        assert "filter_dataclass_fields" not in violations_part
