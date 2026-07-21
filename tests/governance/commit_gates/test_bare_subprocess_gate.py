# [A_test] module_id: MOD-GOV_bare_subprocess_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §ARCH-RUNCOMMAND-WINDOW-FLASH-001
# [MODULE] tests.governance.commit_gates.test_bare_subprocess_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_bare_subprocess_gate.py — BARE-SUBPROCESS 门禁单测

权威依据：bare_subprocess_gate.py（make_bare_subprocess_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestIsBareSubprocessCall: AST 检测纯函数
  - subprocess.run/Popen/check_output/check_call 检测
  - import subprocess as sp 别名识别
  - 非 subprocess 模块调用豁免
- TestGatewayIntegration: mock gateway 流程
  - 新增 .py 含裸 subprocess.run → warn-only（passed=True + detail）
  - 新增 .py 安全（无 subprocess 调用）→ 放行（passed=True + 空 detail）
  - tests/ 豁免
  - 文件级豁免（process_pool.py / _diff_helpers.py 等）
  - noqa 行级逃生
  - AST 语法错误 fail-open
  - git diff 失败/异常 fail-open
  - 存量违规（非 added 行）放行
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

from zephyr.gov_enforcement.commit_gates.bare_subprocess_gate import (  # noqa: E402
    _collect_subprocess_aliases,
    _is_bare_subprocess_call,
    _is_bare_subprocess_exempt_file,
    _extract_noqa_lines,
    make_bare_subprocess_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files=None, project_root=None, diff_fails=False, diff_raises=False,
                  staged_content_map=None):
    """构造 mock gateway：--name-only 返回 staged 文件列表；
    --unified=0 diff 返回 added 行；git show :path 返回 staged 内容。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:
        def _raise(*a, **k):
            raise RuntimeError("git not found")
        gw._run_git = _raise
        return gw

    staged_content_map = staged_content_map or {}

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if "rev-parse" in cmd:
            return _MockResult(0, str(gw.project_root))
        # git show :path — 返回 staged 文件内容
        if "show" in cmd and ":" in cmd[-1] if cmd else False:
            path = cmd[-1].lstrip(":")
            return _MockResult(0, staged_content_map.get(path, ""))
        # git diff --cached --unified=0 -- <path>
        if "--unified=0" in cmd:
            path = cmd[-1]
            content = staged_content_map.get(path, "")
            # 模拟整个文件都是 added（新增文件场景）
            diff_lines = [f"+{line}" for line in content.splitlines()]
            diff_output = (
                f"diff --git a/{path} b/{path}\n"
                f"new file mode 100644\n"
                f"--- /dev/null\n"
                f"+++ b/{path}\n"
                f"@@ -0,0 +1,{len(diff_lines)} @@\n"
                + "\n".join(diff_lines)
            )
            return _MockResult(0, diff_output)
        return _MockResult(0, "")

    gw._run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_bare_subprocess_gate(), GateSpec)

    def test_gate_id(self):
        assert make_bare_subprocess_gate().gate_id == "BARE-SUBPROCESS"

    def test_priority(self):
        assert make_bare_subprocess_gate().priority == 108  # noqa: bare-subprocess  在 IMPORT-INTEGRITY=107 之后，CAPABILITY-LOOKUP-REQUIRED=110 之前


# ---------------------------------------------------------------------------
# TestIsBareSubprocessCall — AST 检测纯函数
# ---------------------------------------------------------------------------
class TestIsBareSubprocessCall:
    def _check(self, code):
        tree = ast.parse(code)
        aliases = _collect_subprocess_aliases(tree)
        for node in ast.walk(tree):
            if _is_bare_subprocess_call(node, aliases):
                return node
        return None

    def test_detects_subprocess_run(self):
        node = self._check('import subprocess\nsubprocess.run(["ls"])')
        assert node is not None
        assert node.func.attr == "run"

    def test_detects_subprocess_popen(self):
        node = self._check('import subprocess\nsubprocess.Popen(["ls"])')
        assert node is not None
        assert node.func.attr == "Popen"

    def test_detects_subprocess_check_output(self):
        node = self._check('import subprocess\nsubprocess.check_output(["ls"])')
        assert node is not None
        assert node.func.attr == "check_output"

    def test_detects_subprocess_check_call(self):
        node = self._check('import subprocess\nsubprocess.check_call(["ls"])')
        assert node is not None
        assert node.func.attr == "check_call"

    def test_detects_alias_sp_run(self):
        node = self._check('import subprocess as sp\nsp.run(["ls"])')
        assert node is not None
        assert node.func.attr == "run"

    def test_ignores_non_subprocess_module_run(self):
        node = self._check('import os\nos.run(["ls"])')
        assert node is None  # os.run 不是 subprocess 调用

    def test_ignores_attribute_call_on_object(self):
        node = self._check('obj.run(["ls"])')
        assert node is None  # obj 不是 subprocess 别名

    def test_ignores_function_call(self):
        node = self._check('run(["ls"])')
        assert node is None  # 裸函数调用，不是 Attribute


# ---------------------------------------------------------------------------
# TestIsBareSubprocessExemptFile — 文件级豁免
# ---------------------------------------------------------------------------
class TestIsBareSubprocessExemptFile:
    def test_exempt_process_pool(self):
        assert _is_bare_subprocess_exempt_file("src/zephyr/shared/infra/process_pool.py")
        assert _is_bare_subprocess_exempt_file("process_pool.py")

    def test_exempt_diff_helpers(self):
        assert _is_bare_subprocess_exempt_file("src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py")

    def test_exempt_git_call_budget_gate(self):
        assert _is_bare_subprocess_exempt_file("src/zephyr/gov_enforcement/commit_gates/git_call_budget_gate.py")

    def test_exempt_git_commit_gateway(self):
        assert _is_bare_subprocess_exempt_file("src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py")

    def test_exempt_bare_subprocess_gate_self(self):
        assert _is_bare_subprocess_exempt_file("src/zephyr/gov_enforcement/commit_gates/bare_subprocess_gate.py")

    def test_not_exempt_normal_file(self):
        assert not _is_bare_subprocess_exempt_file("src/zephyr/data/cli.py")
        assert not _is_bare_subprocess_exempt_file("scripts/foo.py")

    def test_windows_path_backslash(self):
        assert _is_bare_subprocess_exempt_file("src\\zephyr\\shared\\infra\\process_pool.py")


# ---------------------------------------------------------------------------
# TestExtractNoqaLines — noqa 行级逃生
# ---------------------------------------------------------------------------
class TestExtractNoqaLines:
    def test_detects_noqa_with_reason(self):
        content = (
            'import subprocess\n'
            'subprocess.run(["ls"])  # noqa: bare-subprocess  legit reason here\n'
        )
        lines = _extract_noqa_lines(content)
        assert 2 in lines

    def test_ignores_noqa_without_reason(self):
        content = (
            'import subprocess\n'
            'subprocess.run(["ls"])  # noqa: bare-subprocess\n'  # 无 reason
        )
        lines = _extract_noqa_lines(content)
        assert 2 not in lines  # 无 reason 不豁免

    def test_ignores_noqa_single_space(self):
        content = (
            'import subprocess\n'
            'subprocess.run(["ls"])  # noqa: bare-subprocess reason\n'  # 单空格
        )
        lines = _extract_noqa_lines(content)
        assert 2 not in lines  # 单空格不豁免（要求 2+ 空格）

    def test_no_noqa(self):
        content = 'import subprocess\nsubprocess.run(["ls"])\n'
        lines = _extract_noqa_lines(content)
        assert lines == set()


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_detects_bare_subprocess_run_warn_only(self):
        """新增 .py 含裸 subprocess.run → warn-only（passed=True + detail）"""
        content = 'import subprocess\nsubprocess.run(["ls"])\n'
        gw = _make_gateway(
            staged_files=["src/foo.py"],
            staged_content_map={"src/foo.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/foo.py"])
        assert passed is True  # warn-only 不阻断
        assert "BARE-SUBPROCESS" in detail
        assert "trae_067" in detail
        assert "src/foo.py:2" in detail

    def test_safe_file_passes(self):
        """新增 .py 安全（无 subprocess 调用）→ 放行"""
        content = 'import os\nprint(os.getcwd())\n'
        gw = _make_gateway(
            staged_files=["src/foo.py"],
            staged_content_map={"src/foo.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/foo.py"])
        assert passed is True
        assert detail == ""

    def test_tests_dir_exempt(self):
        """tests/ 目录豁免"""
        content = 'import subprocess\nsubprocess.run(["ls"])\n'
        gw = _make_gateway(
            staged_files=["tests/test_foo.py"],
            staged_content_map={"tests/test_foo.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["tests/test_foo.py"])
        assert passed is True
        assert detail == ""

    def test_process_pool_exempt(self):
        """文件级豁免：process_pool.py"""
        content = 'import subprocess\nsubprocess.run(["ls"])\n'
        gw = _make_gateway(
            staged_files=["src/zephyr/shared/infra/process_pool.py"],
            staged_content_map={"src/zephyr/shared/infra/process_pool.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/zephyr/shared/infra/process_pool.py"])
        assert passed is True
        assert detail == ""

    def test_noqa_escape(self):
        """noqa 行级逃生"""
        content = (
            'import subprocess\n'
            'subprocess.run(["ls"])  # noqa: bare-subprocess  legit reason here\n'
        )
        gw = _make_gateway(
            staged_files=["src/foo.py"],
            staged_content_map={"src/foo.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/foo.py"])
        assert passed is True
        assert detail == ""  # noqa 豁免，无 warning

    def test_syntax_error_fail_open(self):
        """AST 语法错误 fail-open"""
        content = 'import subprocess\nsubprocess.run(["ls"\n'  # 语法错误
        gw = _make_gateway(
            staged_files=["src/foo.py"],
            staged_content_map={"src/foo.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/foo.py"])
        assert passed is True
        assert detail == ""  # fail-open

    def test_git_diff_fails_fail_open(self):
        """git diff 失败 fail-open"""
        gw = _make_gateway(staged_files=[], diff_fails=True)
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_git_diff_raises_fail_open(self):
        """git diff 异常 fail-open"""
        gw = _make_gateway(diff_raises=True)
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, [])
        assert passed is True
        assert detail == ""

    def test_existing_violation_not_added_passes(self):
        """存量违规（非 added 行）放行——只检测 added 行"""
        # 模拟非新增文件：subprocess.run 在第 2 行，但 diff 只显示第 5 行 added
        content = (
            'import subprocess\n'
            'subprocess.run(["ls"])  # 第 2 行，存量\n'
            'x = 1\n'
            'y = 2\n'
            'z = 3  # 第 5 行，新增\n'
        )
        gw = MagicMock()
        gw.project_root = str(_PROJECT_ROOT)

        def _run_git(cmd):
            if "--name-only" in cmd:
                return _MockResult(0, "src/foo.py")
            if "rev-parse" in cmd:
                return _MockResult(0, str(gw.project_root))
            if "show" in cmd and cmd[-1].startswith(":"):
                return _MockResult(0, content)
            if "--unified=0" in cmd:
                # 只有第 5 行是 added
                return _MockResult(0, (
                    "diff --git a/src/foo.py b/src/foo.py\n"
                    "--- a/src/foo.py\n"
                    "+++ b/src/foo.py\n"
                    "@@ -4,0 +5 @@\n"
                    "+z = 3  # 第 5 行，新增\n"
                ))
            return _MockResult(0, "")

        gw._run_git = _run_git
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/foo.py"])
        assert passed is True
        assert detail == ""  # 存量违规放行

    def test_multiple_violations(self):
        """多个违规一起报告"""
        content = (
            'import subprocess\n'
            'subprocess.run(["ls"])\n'
            'subprocess.Popen(["echo", "hi"])\n'
            'subprocess.check_output(["pwd"])\n'
        )
        gw = _make_gateway(
            staged_files=["src/foo.py"],
            staged_content_map={"src/foo.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/foo.py"])
        assert passed is True
        assert "src/foo.py:2" in detail
        assert "src/foo.py:3" in detail
        assert "src/foo.py:4" in detail

    def test_alias_sp_detected(self):
        """import subprocess as sp; sp.run(...) 也检测"""
        content = 'import subprocess as sp\nsp.run(["ls"])\n'
        gw = _make_gateway(
            staged_files=["src/foo.py"],
            staged_content_map={"src/foo.py": content},
        )
        gate = make_bare_subprocess_gate()
        passed, detail = gate.check(gw, ["src/foo.py"])
        assert passed is True
        assert "src/foo.py:2" in detail
