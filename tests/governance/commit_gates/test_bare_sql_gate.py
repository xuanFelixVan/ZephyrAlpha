# [A_test] module_id: SRC-TST-2202 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-bare_sql_gate | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_bare_sql_gate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_bare_sql_gate.py — NO-BARE-SQL 门禁单测

权威依据：bare_sql_gate.py（make_bare_sql_gate）

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestSqlPattern: _SQL_PATTERN 纯正则检测（命中/安全/边界/大小写/引号类型）
- TestGatewayIntegration: mock gateway 流程
  - 新增文件含裸SQL → 阻断 (passed=False)
  - 新增文件安全 → 放行 (passed=True)
  - tests/ 豁免
  - docstring 行豁免
  - 注释行豁免
  - fail-open on git diff 失败
  - fail-open on git diff 异常

注意：bare_sql 不做 AST 解析，按行扫描 added 行 + 正则匹配；
docstring/注释/import 行级豁免由 _extract_docstring_lines / _is_exempt_line 处理。

测试隔离：MagicMock 模拟 gateway._run_git，不读/不写真实仓库。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.commit_gates.bare_sql_gate import (  # noqa: E402
    _SQL_PATTERN,
    make_bare_sql_gate,
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


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_bare_sql_gate(), GateSpec)

    def test_gate_id(self):
        assert make_bare_sql_gate().gate_id == "NO-BARE-SQL"

    def test_priority(self):
        assert make_bare_sql_gate().priority == 87


# ---------------------------------------------------------------------------
# TestSqlPattern — 纯正则检测
# ---------------------------------------------------------------------------
class TestSqlPattern:
    def test_select_from_double_quote(self):
        assert _SQL_PATTERN.search('"SELECT col FROM tbl"')

    def test_select_from_single_quote(self):
        assert _SQL_PATTERN.search("'SELECT col FROM tbl'")

    def test_insert_into(self):
        assert _SQL_PATTERN.search('"INSERT INTO tbl VALUES(1)"')

    def test_update_set(self):
        assert _SQL_PATTERN.search('"UPDATE tbl SET x=1"')

    def test_delete_from(self):
        assert _SQL_PATTERN.search('"DELETE FROM tbl"')

    def test_case_insensitive(self):
        assert _SQL_PATTERN.search('"select col from tbl"')

    def test_minimal_select_from(self):
        assert _SQL_PATTERN.search('"SELECT a FROM b"')

    def test_safe_no_sql(self):
        assert not _SQL_PATTERN.search('"no sql here"')

    def test_safe_no_quote(self):
        assert not _SQL_PATTERN.search("x = 1")

    def test_safe_select_without_from(self):
        # SELECT 但无 FROM → 不匹配 SELECT\s+\S+\s+FROM
        assert not _SQL_PATTERN.search('"SELECT col"')

    def test_safe_from_without_select(self):
        assert not _SQL_PATTERN.search('"FROM tbl"')


# ---------------------------------------------------------------------------
# TestGatewayIntegration — mock gateway 流程
# ---------------------------------------------------------------------------
class TestGatewayIntegration:
    def test_new_file_with_sql_blocked(self):
        red = "src/zephyr/trading/mod.py"
        content = 'sql = "SELECT col FROM tbl"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert not passed
        assert "NO-BARE-SQL" in msg
        assert "SELECT" in msg

    def test_new_file_safe_passes(self):
        blue = "src/zephyr/trading/mod.py"
        content = 'x = "no sql here"\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_tests_dir_exempt(self):
        red = "tests/governance/test_something.py"
        content = 'sql = "SELECT col FROM tbl"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_docstring_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = (
            '"""module docstring\n'
            'sql = "SELECT col FROM tbl"\n'
            '"""\n'
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed  # docstring 内行豁免
        assert msg == ""

    def test_comment_line_exempt(self):
        blue = "src/zephyr/trading/mod.py"
        content = '# sql = "SELECT col FROM tbl"\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed  # 注释行豁免
        assert msg == ""

    def test_fail_open_on_git_diff_failure(self):
        gw = _make_gateway(diff_fails=True)
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self):
        gw = _make_gateway(diff_raises=True)
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed
        assert msg == ""
