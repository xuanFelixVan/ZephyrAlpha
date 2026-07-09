# [A_test] module_id: SRC-TST-2151 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-commit_gates | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] tests.governance.commit_gates.test_datetime_now_forbidden_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_datetime_now_forbidden_gate.py — 生成器代码 datetime.now() 硬阻断门禁单测（DATETIME-NOW-FORBIDDEN）

权威依据：datetime_now_forbidden_gate.py（make_datetime_now_forbidden_gate）
AGENTS.md §11.1.1 时间戳约定

测试组（14 组 / 31 用例）：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsGeneratorFile: 生成器文件判定（/generators/ 路径 + generate_ 前缀）
- TestDatetimeNowDetected: datetime.now() 命中 → hard-block（passed=False）
- TestDatetimeDatetimeNow: datetime.datetime.now() 亦命中
- TestHardBlockBehavior: 硬阻断行为（passed=False + detail 含修复提示）
- TestNonGeneratorFileExemption: 非生成器文件豁免
- TestTestExempt: tests/ 下文件豁免
- TestImportExemption: import 行豁免
- TestCommentExemption: 注释行豁免
- TestDocstringExemption: docstring 行豁免
- TestNonPyFile: 非 .py 文件豁免
- TestNoStagedFile: 空 staged → 通过
- TestFailOpenGitDiffFails: git diff 失败/异常 → 通过（fail-open）
- TestMultipleViolationsAllReported: 多违规全报告

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

from zephyr.governance.commit_gates.datetime_now_forbidden_gate import (  # noqa: E402
    _is_generator_file,
    make_datetime_now_forbidden_gate,
)
from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


def _make_mock_gateway(
    staged_files: list[str],
    file_diffs: dict[str, list[str]],
    file_contents: dict[str, str] | None = None,
    diff_fail: bool = False,
) -> MagicMock:
    """构造 mock gateway，_run_git 根据 cmd 返回预设结果。

    Args:
        staged_files: git diff --name-only 返回的文件列表（相对路径）
        file_diffs: {py_file: [added_line1, added_line2, ...]}（added 行内容）
        file_contents: {py_file: 完整文件内容}（用于 ``git show :path`` 读取 staged 版本，
            预计算 docstring 行号集合）。若 None，则根据 file_diffs 自动生成
            "纯 added 行拼接"的简化文件内容（行号从 1 开始）。
        diff_fail: True 时 git diff --name-only 返回非 0 returncode（模拟 fail-open）。
    """
    gw = MagicMock()

    def _run_git(cmd):
        result = MagicMock()
        if "--name-only" in cmd:
            if diff_fail:
                result.returncode = 1
                result.stdout = ""
                return result
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
        gate = make_datetime_now_forbidden_gate()
        assert gate.gate_id == "DATETIME-NOW-FORBIDDEN"

    def test_priority(self):
        gate = make_datetime_now_forbidden_gate()
        assert gate.priority == 34

    def test_is_gatespec(self):
        gate = make_datetime_now_forbidden_gate()
        assert isinstance(gate, GateSpec)


# ============================================================================
# TestIsGeneratorFile
# ============================================================================


class TestIsGeneratorFile:
    def test_generators_dir_path(self):
        """路径含 /generators/ → True"""
        assert _is_generator_file("scripts/governance/d5_architecture/generators/generate_domain_doc.py")

    def test_generate_prefix(self):
        """文件名以 generate_ 开头 → True"""
        assert _is_generator_file("scripts/governance/generate_project_depgraph.py")

    def test_backslash_path(self):
        """Windows 反斜杠路径也判定为生成器"""
        assert _is_generator_file("scripts\\governance\\generators\\foo.py")
        assert _is_generator_file("scripts\\generate_bar.py")

    def test_non_generator_file(self):
        """非生成器文件 → False"""
        assert not _is_generator_file("src/zephyr/trading/some_module.py")
        assert not _is_generator_file("src/zephyr/governance/rule_bridge/git_commit_gateway.py")

    def test_non_generate_prefix(self):
        """文件名不以 generate_ 开头且不在 generators/ → False"""
        assert not _is_generator_file("src/zephyr/governance/commit_gates/datetime_now_forbidden_gate.py")


# ============================================================================
# TestDatetimeNowDetected (hard-block 命中)
# ============================================================================


class TestDatetimeNowDetected:
    def test_simple_datetime_now_blocked(self):
        """生成器中 datetime.now() → hard-block"""
        gen_file = "scripts/governance/d5_architecture/generators/generate_domain_doc.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["    ts = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed  # hard-block
        assert "datetime.now()" in detail
        assert "DATETIME-NOW-FORBIDDEN" in detail

    def test_datetime_now_with_tz(self):
        """datetime.now(tz) → 亦命中（正则只匹配 datetime.now( 前缀）"""
        gen_file = "scripts/governance/d5_architecture/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["    ts = datetime.now(timezone.utc)"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "datetime.now" in detail

    def test_datetime_now_in_assignment(self):
        """ts = datetime.now() → 命中"""
        gen_file = "scripts/governance/generators/bar.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["ts = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed

    def test_generate_prefix_file_blocked(self):
        """文件名以 generate_ 开头（不在 generators/ 目录）→ 亦阻断"""
        gen_file = "scripts/governance/generate_project_depgraph.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["    updated = datetime.now().isoformat()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed


# ============================================================================
# TestDatetimeDatetimeNow (datetime.datetime.now() 亦命中)
# ============================================================================


class TestDatetimeDatetimeNow:
    def test_datetime_datetime_now(self):
        """datetime.datetime.now() → 正则引擎匹配第二个 datetime.now( → 命中"""
        gen_file = "scripts/governance/d5_architecture/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["    ts = datetime.datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert "datetime.now" in detail


# ============================================================================
# TestHardBlockBehavior
# ============================================================================


class TestHardBlockBehavior:
    def test_hard_block_returns_false(self):
        """检出违规 → passed=False（hard-block，非 warn）"""
        gen_file = "scripts/governance/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["x = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, _ = gate.check(gw, [])
        assert passed is False

    def test_detail_contains_fix_hint(self):
        """detail 含修复指引"""
        gen_file = "scripts/governance/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["x = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        _, detail = gate.check(gw, [])
        assert "git log" in detail or "占位符" in detail  # 修复指引

    def test_detail_contains_file_path(self):
        """detail 含违规文件路径"""
        gen_file = "scripts/governance/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["x = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        _, detail = gate.check(gw, [])
        assert gen_file in detail


# ============================================================================
# TestNonGeneratorFileExemption (蓝队)
# ============================================================================


class TestNonGeneratorFileExemption:
    def test_non_generator_file_passes(self):
        """非生成器文件中的 datetime.now() → 豁免"""
        non_gen = "src/zephyr/trading/some_service.py"
        gw = _make_mock_gateway(
            [non_gen], {non_gen: ["    ts = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # 豁免
        assert detail == ""

    def test_runtime_module_passes(self):
        """运行时模块（非生成器）中的 datetime.now() → 豁免"""
        non_gen = "src/zephyr/governance/rule_bridge/session_worktree.py"
        gw = _make_mock_gateway(
            [non_gen], {non_gen: ["    now = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed


# ============================================================================
# TestTestExempt
# ============================================================================


class TestTestExempt:
    def test_tests_dir_exempt(self):
        """tests/ 下生成器文件中的 datetime.now() → 豁免"""
        test_file = "tests/governance/commit_gates/test_datetime_now_forbidden_gate.py"
        gw = _make_mock_gateway(
            [test_file], {test_file: ["    ts = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestImportExemption
# ============================================================================


class TestImportExemption:
    def test_import_datetime_now_passes(self):
        """import 行中的 datetime.now → 豁免（误判保护）"""
        gen_file = "scripts/governance/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["from datetime import datetime.now"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestCommentExemption
# ============================================================================


class TestCommentExemption:
    def test_comment_passes(self):
        """注释行中的 datetime.now() → 豁免"""
        gen_file = "scripts/governance/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file], {gen_file: ["# x = datetime.now()  # 已禁用"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestDocstringExemption
# ============================================================================


class TestDocstringExemption:
    def test_docstring_passes(self):
        """docstring 内的 datetime.now() 示例 → 豁免"""
        gen_file = "scripts/governance/generators/foo.py"
        file_content = '''"""foo.py 生成器

示例（禁止使用）::

    ts = datetime.now()  # 违规，仅文档示例
"""
def foo():
    pass
'''
        gw = _make_mock_gateway(
            [gen_file],
            {gen_file: ['"""foo.py 生成器', "示例（禁止使用）::", "    ts = datetime.now()  # 违规，仅文档示例", '"""', "def foo():", "    pass"]},
            file_contents={gen_file: file_content},
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed  # docstring 行豁免
        assert detail == ""

    def test_manifest_mode_datetime_now_not_exempt(self):
        """R95 修复：__manifest__ = \"\"\"...\"\"\" 模式中 datetime.now() 应被检测（不再被错误豁免）。

        旧 bug：__manifest__ 结束独立 \"\"\" 行被误判为新 docstring 起始，导致后续
        含 datetime.now() 的代码行被错误豁免。
        新方案：ast 只识别真正 docstring，__manifest__ 是 Assign 节点不豁免。
        """
        gen_file = "scripts/governance/generators/foo.py"
        full_content = (
            '__manifest__ = """\n'
            'args: []\n'
            '"""\n'
            '\n'
            'ts = datetime.now()  # 这行应被检测\n'
        )
        gw = _make_mock_gateway(
            [gen_file],
            {gen_file: ["ts = datetime.now()  # 这行应被检测"]},
            file_contents={gen_file: full_content},
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed  # 应被阻断（R95 修复 + hard-block）
        assert "DATETIME-NOW-FORBIDDEN" in detail
        assert "datetime.now()" in detail


# ============================================================================
# TestNonPyFile
# ============================================================================


class TestNonPyFile:
    def test_yaml_file_passes(self):
        """非 .py 文件（如 .yaml）→ 豁免"""
        yaml_file = "scripts/governance/generators/config.yaml"
        gw = _make_mock_gateway(
            [yaml_file], {yaml_file: ["ts: datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_md_file_passes(self):
        """非 .py 文件（如 .md）→ 豁免"""
        md_file = "scripts/governance/generators/README.md"
        gw = _make_mock_gateway(
            [md_file], {md_file: ["ts = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed


# ============================================================================
# TestNoStagedFile
# ============================================================================


class TestNoStagedFile:
    def test_empty_staged_passes(self):
        """空 staged → 通过"""
        gw = _make_mock_gateway([], {})
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""

    def test_no_generator_files_passes(self):
        """staged 全是非生成器 .py → 通过"""
        non_gen = "src/zephyr/trading/foo.py"
        gw = _make_mock_gateway(
            [non_gen], {non_gen: ["x = datetime.now()"]}
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestFailOpenGitDiffFails
# ============================================================================


class TestFailOpenGitDiffFails:
    def test_git_diff_fail_open(self):
        """git diff --name-only returncode != 0 → fail-open（通过）"""
        gw = _make_mock_gateway([], {}, diff_fail=True)
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert passed
        assert detail == ""


# ============================================================================
# TestMultipleViolationsAllReported
# ============================================================================


class TestMultipleViolationsAllReported:
    def test_multiple_violations_in_one_file(self):
        """同一文件多处违规 → 全报告"""
        gen_file = "scripts/governance/generators/foo.py"
        gw = _make_mock_gateway(
            [gen_file],
            {gen_file: ["a = datetime.now()", "b = datetime.now(timezone.utc)", "c = datetime.datetime.now()"]},
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        # 3 处违规都报告
        assert detail.count("datetime.now") >= 3

    def test_multiple_files_all_reported(self):
        """多个生成器文件违规 → 全报告"""
        gen1 = "scripts/governance/generators/foo.py"
        gen2 = "scripts/governance/generate_bar.py"
        gw = _make_mock_gateway(
            [gen1, gen2],
            {gen1: ["a = datetime.now()"], gen2: ["b = datetime.now()"]},
        )
        gate = make_datetime_now_forbidden_gate()
        passed, detail = gate.check(gw, [])
        assert not passed
        assert gen1 in detail
        assert gen2 in detail
