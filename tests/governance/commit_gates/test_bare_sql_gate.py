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

from zephyr.gov_enforcement.commit_gates.bare_sql_gate import (  # noqa: E402
    _SQL_PATTERN,
    make_bare_sql_gate,
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

    def test_insert_or_ignore_into(self):
        """R97 修复：INSERT OR IGNORE INTO（SQLite 冲突解决子句）应被检测。"""
        assert _SQL_PATTERN.search('"INSERT OR IGNORE INTO tbl VALUES(1)"')

    def test_insert_or_replace_into(self):
        """R97 修复：INSERT OR REPLACE INTO 应被检测。"""
        assert _SQL_PATTERN.search('"INSERT OR REPLACE INTO tbl VALUES(1)"')

    def test_insert_or_rollback_into(self):
        """R97 修复：INSERT OR ROLLBACK INTO 应被检测（覆盖较少见的冲突子句）。"""
        assert _SQL_PATTERN.search('"INSERT OR ROLLBACK INTO tbl VALUES(1)"')

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
        # SELECT 但无 FROM → 不匹配 SELECT\b.*?\bFROM\b
        assert not _SQL_PATTERN.search('"SELECT col"')

    def test_safe_from_without_select(self):
        assert not _SQL_PATTERN.search('"FROM tbl"')


# ---------------------------------------------------------------------------
# TestSqlPatternExtended — R94 正则修正后新增覆盖（多列/DISTINCT/跨行等）
# ---------------------------------------------------------------------------
class TestSqlPatternExtended:
    """覆盖旧正则 SELECT\s+\S+\s+FROM 漏检的 SQL 模式。

    旧正则中 \\S+ 只匹配单个非空白 token，无法覆盖：
    - 多列 SELECT (col1, col2 FROM)
    - SELECT DISTINCT ... FROM
    - SELECT COUNT(DISTINCT ...) FROM
    - 多表 UPDATE (UPDATE tbl1, tbl2 SET)
    - 跨行 SQL 字面量（DOTALL）
    """

    def test_multi_column_select(self):
        assert _SQL_PATTERN.search('"SELECT col1, col2 FROM tbl"')

    def test_multi_column_select_with_table_prefix(self):
        assert _SQL_PATTERN.search('"SELECT t.col1, t.col2 FROM tbl t"')

    def test_select_distinct(self):
        assert _SQL_PATTERN.search('"SELECT DISTINCT col FROM tbl"')

    def test_select_count_distinct(self):
        assert _SQL_PATTERN.search('"SELECT COUNT(DISTINCT scan_run_id) FROM findings"')

    def test_select_with_join(self):
        assert _SQL_PATTERN.search(
            '"SELECT a.col FROM tbl_a a JOIN tbl_b b ON a.id = b.id"'
        )

    def test_select_with_where(self):
        assert _SQL_PATTERN.search(
            '"SELECT col FROM tbl WHERE id = ? AND status = ?"'
        )

    def test_multi_table_update(self):
        assert _SQL_PATTERN.search('"UPDATE tasks SET status = ? WHERE id = ?"')

    def test_update_with_table_prefix(self):
        assert _SQL_PATTERN.search('"UPDATE schema.tasks SET status = ?"')

    def test_insert_into_with_columns(self):
        assert _SQL_PATTERN.search(
            '"INSERT INTO tbl (col1, col2) VALUES (?, ?)"'
        )

    def test_delete_from_with_where(self):
        assert _SQL_PATTERN.search('"DELETE FROM tbl WHERE id = ?"')

    def test_multiline_sql_dotall(self):
        # DOTALL 模式：跨行 SQL 字面量（三引号字符串中的 SQL）
        multiline = '"""SELECT col\nFROM tbl\nWHERE x=1"""'
        assert _SQL_PATTERN.search(multiline)

    def test_safe_no_sql_keyword_in_string(self):
        assert not _SQL_PATTERN.search('"just a regular string"')

    def test_safe_variable_name_with_select(self):
        # "selection" 不应匹配 SELECT\b（词边界保护）
        assert not _SQL_PATTERN.search('"the selection is from here"')

    def test_safe_settings_not_update_set(self):
        # "settings" 不应匹配 UPDATE...SET（词边界保护）
        assert not _SQL_PATTERN.search('"update the settings"')

    def test_safe_from_in_non_sql_context(self):
        # 无 SELECT 前缀的 FROM 不匹配
        assert not _SQL_PATTERN.search('"data from source"')

    def test_case_insensitive_multi_column(self):
        assert _SQL_PATTERN.search('"select col1, col2 from tbl"')

    def test_select_star(self):
        assert _SQL_PATTERN.search('"SELECT * FROM tbl"')

    def test_select_with_subquery(self):
        assert _SQL_PATTERN.search(
            '"SELECT col FROM (SELECT * FROM sub) t"'
        )


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

    def test_insert_or_ignore_into_blocked(self):
        """R97 修复：INSERT OR IGNORE INTO 裸 SQL 应被阻断（旧正则漏检）。"""
        red = "src/zephyr/trading/mod.py"
        content = 'sql = "INSERT OR IGNORE INTO task_files VALUES (1, 2, 3)"\n'
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert not passed  # R97 修复后应被阻断
        assert "NO-BARE-SQL" in msg
        assert "INSERT" in msg

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

    def test_sql_constant_def_exempt(self):
        """SQL_FOO = 'SELECT col FROM tbl' 行应豁免（SQL 集中化正确做法）。"""
        blue = "src/zephyr/trading/mod.py"
        content = 'SQL_GET_USER = "SELECT col1, col2 FROM tbl WHERE id = ?"\n'
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed  # SQL_* 常量定义行豁免
        assert msg == ""

    def test_private_sql_pattern_def_exempt(self):
        """_SQL_PATTERN = re.compile(...) 行应豁免（gate 自身定义）。"""
        blue = "src/zephyr/trading/mod.py"
        content = (
            '_SQL_PATTERN = re.compile(r"""SELECT col FROM tbl""")\n'
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed  # _SQL_* 常量定义行豁免
        assert msg == ""

    def test_manifest_mode_sql_not_exempt(self):
        """R95 修复：__manifest__ = \"\"\"...\"\"\" 模式中 SQL 应被检测（不再被错误豁免）。

        旧 bug：__manifest__ = \"\"\"...\"\"\" 的结束独立 \"\"\" 行被误判为新 docstring
        起始，导致后续所有行（含裸 SQL）被错误豁免（cleanup_p0_auto_bridged.py
        L78/L87 裸 SQL 漏检根因）。
        新方案：ast 只识别真正 docstring，__manifest__ 是 Assign 节点不豁免。
        """
        red = "src/zephyr/trading/mod.py"
        content = (
            '__manifest__ = """\n'
            'args: []\n'
            '"""\n'
            '\n'
            'sql = "SELECT col FROM tbl"\n'
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert not passed  # 应被阻断（R95 修复）
        assert "NO-BARE-SQL" in msg
        assert "SELECT" in msg

    def test_manifest_with_module_docstring_then_sql(self):
        """R95 修复：模块 docstring + __manifest__ 共存场景下，裸 SQL 仍被检测。

        验证 ast 同时识别模块 docstring（豁免）+ __manifest__（不豁免）+
        后续裸 SQL（应被检测）。
        """
        red = "src/zephyr/trading/mod.py"
        content = (
            '"""module docstring"""\n'      # L1 — 识别为 docstring
            '\n'                             # L2
            '__manifest__ = """\n'          # L3 — Assign，不识别
            'args: []\n'                     # L4
            '"""\n'                          # L5 — manifest 结束
            '\n'                             # L6
            'sql = "UPDATE tasks SET x=1"\n'  # L7 — 应被检测
        )
        gw = _make_gateway(staged_files=[red], file_contents={red: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert not passed  # L7 裸 SQL 应被检测
        assert "NO-BARE-SQL" in msg
        assert "UPDATE" in msg

    def test_multiline_sql_constant_paren_exempt(self):
        """R96 修复：括号多行 SQL 常量定义续行不误报。

        file_task_mapper.py L66-68 实际场景：续行含完整 SELECT...FROM，
        旧 _SQL_CONSTANT_DEF_RE 只豁免定义行，续行被 _SQL_PATTERN 误报。
        新方案：_extract_sql_constant_lines 用 ast 豁免整个 Assign 节点行范围。
        """
        blue = "src/zephyr/trading/mod.py"
        content = (
            'SQL_SELECT = (\n'                                                # L1
            '    "SELECT task_id FROM task_files WHERE file_path = ?"\n'      # L2
            ')\n'                                                             # L3
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed  # R96 修复：整个 Assign 节点豁免
        assert msg == ""

    def test_multiline_sql_constant_triple_quote_exempt(self):
        """R96 修复：三引号多行 SQL 常量定义不误报。"""
        blue = "src/zephyr/trading/mod.py"
        content = (
            'SQL_INSERT = """INSERT INTO tasks\n'     # L1
            '    (id, name) VALUES (?, ?)"""\n'       # L2
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed  # R96 修复
        assert msg == ""

    def test_multiline_sql_constant_backslash_exempt(self):
        """R96 修复：反斜杠续行 SQL 常量定义不误报。"""
        blue = "src/zephyr/trading/mod.py"
        content = (
            'SQL_X = \\\n'                                # L1
            '    "UPDATE tasks SET x=1 WHERE id=?"\n'     # L2
        )
        gw = _make_gateway(staged_files=[blue], file_contents={blue: content})
        passed, msg = make_bare_sql_gate().check(gw, [])
        assert passed  # R96 修复
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
