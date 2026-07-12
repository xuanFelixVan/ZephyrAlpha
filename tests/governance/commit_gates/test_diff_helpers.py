# [A_test] module_id: SRC-TST-2231 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-diff_helpers | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_diff_helpers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_diff_helpers.py — gate 共享 diff 解析工具模块单测

权威依据：_diff_helpers.py

测试组（聚焦 R95/R96 治本：_extract_docstring_lines 用 ast 精确识别 docstring，
_extract_sql_constant_lines 用 ast 精确识别 SQL_* 常量定义行范围）：
- TestExtractDocstringLinesCore: docstring 标准场景（模块/函数/类/方法）
- TestExtractDocstringLinesManifestBug: __manifest__=\"\"\"...\"\"\" 行内字符串赋值
  不被识别为 docstring（R95 修复核心，cleanup_p0_auto_bridged.py L78/L87 漏检根因）
- TestExtractDocstringLinesEdgeCases: 边界场景（语法错误 fail-open/空文件/无 docstring）
- TestExtractSqlConstantLines: SQL_* 常量定义行范围提取（R96 修复核心，
  file_task_mapper.py L67/L70/L73 误报根因）
- TestIsExemptLine: 行级豁免（注释/import）回归测试
- TestParseDiffWithLineNumbers: git diff 解析回归测试

R95 修复背景：
  旧实现用 ``stripped.startswith('\"\"\"')`` 作判据，是正则近似，无法区分
  docstring vs 行内字符串赋值。``__manifest__ = \"\"\"...\"\"\"`` 的结束独立
  ``\"\"\"`` 行被误判为新 docstring 起始，后续所有行被错误豁免，导致
  cleanup_p0_auto_bridged.py L78/L87 裸 SQL 漏检。
  新实现用 ast 模块精确识别 Module/ClassDef/FunctionDef/AsyncFunctionDef 的
  body[0]（ast.Expr(value=ast.Constant(str))）作为 docstring。

R96 修复背景：
  旧实现用 ``_SQL_CONSTANT_DEF_RE = re.compile(r"^\\s*_?SQL_\\w+\\s*=")``
  只豁免 SQL_* 常量定义行，不跟踪多行续行，导致括号隐式连接的续行含完整
  SQL 字符串字面量时被 ``_SQL_PATTERN`` 误报（file_task_mapper.py L67/L70/L73
  误报根因）。
  新实现用 ast 模块精确识别 Assign 节点，目标名匹配 ``^_?SQL_\\w+$``，
  豁免整个 Assign 节点的行范围（lineno 到 end_lineno）。

测试隔离：纯函数测试，无 mock/无 git/无文件 I/O。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates._diff_helpers import (  # noqa: E402
    _extract_docstring_lines,
    _extract_sql_constant_lines,
    _is_exempt_line,
    _parse_diff_with_line_numbers,
)


# ---------------------------------------------------------------------------
# TestExtractDocstringLinesCore — 标准场景
# ---------------------------------------------------------------------------
class TestExtractDocstringLinesCore:
    """docstring 标准场景：模块/函数/类/方法的 docstring 被正确识别。"""

    def test_module_docstring_single_line(self):
        """单行模块 docstring 被识别。"""
        content = '"""module docstring"""\ncode = 1\n'
        assert _extract_docstring_lines(content) == {1}

    def test_module_docstring_multiline(self):
        """多行模块 docstring 整个范围被识别（含中间行）。"""
        content = '"""module\nsql = "SELECT"\n"""\ncode = 1\n'
        assert _extract_docstring_lines(content) == {1, 2, 3}

    def test_function_docstring_single_line(self):
        """单行函数 docstring 被识别。"""
        content = 'def foo():\n    """func docstring"""\n    pass\n'
        assert _extract_docstring_lines(content) == {2}

    def test_function_docstring_multiline(self):
        """多行函数 docstring 被识别。"""
        content = (
            'def foo():\n'
            '    """func\n'
            '    multi\n'
            '    """\n'
            '    pass\n'
        )
        assert _extract_docstring_lines(content) == {2, 3, 4}

    def test_class_docstring(self):
        """类 docstring 被识别。"""
        content = 'class Foo:\n    """class docstring"""\n    pass\n'
        assert _extract_docstring_lines(content) == {2}

    def test_async_function_docstring(self):
        """async 函数 docstring 被识别。"""
        content = (
            'async def foo():\n'
            '    """async func docstring"""\n'
            '    pass\n'
        )
        assert _extract_docstring_lines(content) == {2}

    def test_method_docstring(self):
        """类方法 docstring 被识别。"""
        content = (
            'class Foo:\n'
            '    def method(self):\n'
            '        """method docstring"""\n'
            '        pass\n'
        )
        assert _extract_docstring_lines(content) == {3}

    def test_nested_docstrings_all_recognized(self):
        """嵌套场景下所有 docstring 全部被识别。"""
        content = (
            '"""module docstring"""\n'             # L1
            '\n'                                     # L2
            'def foo():\n'                           # L3
            '    """func docstring"""\n'            # L4
            '    pass\n'                              # L5
            '\n'                                     # L6
            'class Bar:\n'                            # L7
            '    """class docstring"""\n'            # L8
            '    def method(self):\n'                # L9
            '        """method docstring"""\n'       # L10
            '        pass\n'                          # L11
        )
        assert _extract_docstring_lines(content) == {1, 4, 8, 10}

    def test_triple_single_quote_docstring(self):
        """'''...''' 三单引号 docstring 也被识别（ast 不区分引号类型）。"""
        content = "'''module docstring'''\ncode = 1\n"
        assert _extract_docstring_lines(content) == {1}

    def test_no_docstring_returns_empty(self):
        """无 docstring 文件返回空集合。"""
        content = 'x = 1\ny = 2\n'
        assert _extract_docstring_lines(content) == set()

    def test_second_statement_string_not_docstring(self):
        """非 body[0] 的独立字符串表达式不被识别为 docstring。"""
        content = (
            'x = 1\n'                          # L1
            '"""not a docstring"""\n'          # L2 — 模块 body[1]，非 body[0]
            'y = 2\n'                          # L3
        )
        # 只有 body[0] 是 docstring；L2 是独立 Expr(Constant(str)) 但不是 body[0]
        assert _extract_docstring_lines(content) == set()


# ---------------------------------------------------------------------------
# TestExtractDocstringLinesManifestBug — R95 修复核心
# ---------------------------------------------------------------------------
class TestExtractDocstringLinesManifestBug:
    """R95 修复核心：__manifest__=\"\"\"...\"\"\" 行内字符串赋值不被误判。

    旧 bug：
    - ``__manifest__ = \"\"\"...\"\"\"`` 的结束独立 ``\"\"\"`` 行被误判为新
      docstring 起始，后续所有行被错误豁免。
    - cleanup_p0_auto_bridged.py L78/L87 裸 SQL 漏检根因。

    新方案：
    - ast 只识别 Module/ClassDef/FunctionDef 的 body[0] 为 docstring
    - ``__manifest__ = \"\"\"...\"\"\"`` 是 Assign 节点，不是 docstring
    """

    def test_manifest_inline_string_not_exempt(self):
        """__manifest__ 行内赋值字符串内容不被识别为 docstring。"""
        content = (
            '__manifest__ = """\n'
            'args: []\n'
            '"""\n'
            'sql = "SELECT col FROM tbl"\n'
        )
        # manifest 内容 L2/L3 和后续代码 L4 都不应被豁免
        assert _extract_docstring_lines(content) == set()

    def test_manifest_closing_triple_quote_not_misjudged_as_start(self):
        """R95 修复 Bug B：manifest 结束 \"\"\" 不应误判为新 docstring 起始。

        旧 bug 行为：L3 独立 \"\"\" 行被误判为新 docstring 起始，导致 L4+ 全部
        被错误豁免。
        新方案行为：ast 识别 __manifest__ = \"\"\"...\"\"\" 是 Assign 节点，
        不是 docstring，所有行都不豁免。
        """
        content = (
            '__manifest__ = """\n'      # L1
            'args: []\n'                 # L2
            '"""\n'                      # L3 — manifest 结束（独立三引号行）
            'sql = "SELECT col FROM tbl"\n'  # L4 — 不应被豁免
        )
        # 期望：所有行都不被豁免（manifest 不是 docstring）
        result = _extract_docstring_lines(content)
        # L4 sql 不应被错误豁免（旧 bug 会豁免 L4+）
        assert 4 not in result, f"FAIL: L4 should not be exempted, got {sorted(result)}"
        assert result == set(), f"FAIL: expected empty set, got {sorted(result)}"

    def test_manifest_with_following_independent_docstring_not_cascaded(self):
        """R95 修复 Bug B 级联场景：manifest 结束后跟独立 docstring 不级联误判。"""
        content = (
            '__manifest__ = """\n'      # L1
            'args: []\n'                 # L2
            '"""\n'                       # L3 — manifest 结束
            '\n'                          # L4
            '"""independent docstring"""\n'  # L5 — 独立 Expr，不是 body[0]
            'sql = "SELECT col FROM tbl"\n'  # L6
        )
        # 期望：L6 裸 SQL 不应被错误豁免
        result = _extract_docstring_lines(content)
        assert 6 not in result, f"FAIL: L6 should not be exempted, got {sorted(result)}"
        # L5 独立 docstring 也不应被识别（不是 body[0]）
        assert 5 not in result, f"FAIL: L5 independent docstring should not be recognized, got {sorted(result)}"

    def test_cleanup_p0_auto_bridged_scenario(self):
        """cleanup_p0_auto_bridged.py 实际场景：L36-105 不应被错误豁免。"""
        content = (
            '"""module docstring"""\n'       # L1 — 模块 docstring
            '\n'                              # L2
            '__manifest__ = """\n'           # L3
            'args: []\n'                      # L4
            '"""\n'                           # L5 — manifest 结束
            '\n'                              # L6
            '"""second docstring"""\n'       # L7 — 独立 Expr
            '\n'                              # L8
            'sql = "UPDATE tasks SET x=1"\n'  # L9 — 裸 SQL（不应被豁免）
        )
        result = _extract_docstring_lines(content)
        # 只有 L1 模块 docstring 被识别
        assert result == {1}, f"FAIL: expected {{1}}, got {sorted(result)}"
        # L9 裸 SQL 必须不被豁免（R95 修复核心）
        assert 9 not in result

    def test_manifest_with_sql_inside_not_exempt(self):
        """__manifest__ 内嵌 SQL 不应被豁免（R95 关键回归测试）。

        旧 bug：manifest 内 SQL 被错误豁免
        新方案：manifest 是 Assign 节点，不是 docstring，不豁免
        """
        content = (
            '__manifest__ = """\n'
            'description: >\n'
            '    SELECT col FROM tbl\n'
            '"""\n'
            '\n'
            'sql = "UPDATE tasks SET x=1"\n'
        )
        result = _extract_docstring_lines(content)
        assert result == set(), f"FAIL: expected empty set, got {sorted(result)}"
        # L7 裸 SQL 不应被豁免
        assert 7 not in result

    def test_module_docstring_then_manifest(self):
        """模块 docstring + manifest 共存场景：只豁免模块 docstring。"""
        content = (
            '"""module docstring"""\n'      # L1 — 识别
            '\n'                            # L2
            '__manifest__ = """\n'         # L3 — 不识别（Assign 节点）
            'args: []\n'                    # L4 — 不识别
            '"""\n'                         # L5 — 不识别
            'code = "UPDATE tbl SET x=1"\n'  # L6 — 不应被豁免
        )
        result = _extract_docstring_lines(content)
        assert result == {1}, f"FAIL: expected {{1}}, got {sorted(result)}"
        assert 6 not in result

    def test_string_assignment_not_docstring(self):
        """普通字符串赋值（var = \"\"\"...\"\"\"）不被识别为 docstring。"""
        content = (
            'description = """\n'
            'multi-line string\n'
            '"""\n'
            'sql = "SELECT col FROM tbl"\n'
        )
        # 所有行都不应被豁免（description 是 Assign，不是 docstring）
        assert _extract_docstring_lines(content) == set()


# ---------------------------------------------------------------------------
# TestExtractDocstringLinesEdgeCases — 边界场景
# ---------------------------------------------------------------------------
class TestExtractDocstringLinesEdgeCases:
    """边界场景：语法错误 fail-open / 空文件 / 异常输入。"""

    def test_syntax_error_fail_open(self):
        """语法错误文件 fail-open 返回空集合（不抛异常）。"""
        content = 'def foo(\n    """unclosed'
        # 不应抛异常，返回空集合
        result = _extract_docstring_lines(content)
        assert result == set()

    def test_empty_file(self):
        """空文件返回空集合。"""
        assert _extract_docstring_lines("") == set()

    def test_only_comments(self):
        """只有注释的文件返回空集合。"""
        content = '# comment 1\n# comment 2\n'
        assert _extract_docstring_lines(content) == set()

    def test_unclosed_triple_quote_syntax_error(self):
        """未闭合三引号字符串触发 SyntaxError，fail-open 返回空集合。"""
        content = '"""unclosed\nsql = "SELECT col FROM tbl"\n'
        # ast.parse 会失败，fail-open
        result = _extract_docstring_lines(content)
        assert result == set()

    def test_binary_like_content_fail_open(self):
        """非 Python 内容（二进制/乱码）触发 SyntaxError，fail-open。"""
        content = '\x00\x01\x02\n'
        result = _extract_docstring_lines(content)
        assert result == set()

    def test_complex_real_world_file(self):
        """复杂真实文件场景：frontmatter + 模块 docstring + manifest + 函数。

        验证 frontmatter 注释 + 模块 docstring + __manifest__ + 函数 docstring
        共存时，ast 精确识别模块 docstring + 函数 docstring，不豁免 manifest
        内容和函数体内的裸 SQL。
        """
        content = (
            '# [BLUEPRINT] MOD-X\n'                          # L1 frontmatter
            '# [MODULE] test\n'                              # L2 frontmatter
            '"""module docstring"""\n'                       # L3 模块 docstring
            '\n'                                              # L4
            '__manifest__ = """\n'                           # L5 manifest 起
            'args: []\n'                                      # L6
            '"""\n'                                           # L7 manifest 终
            '\n'                                              # L8
            'def foo():\n'                                    # L9
            '    """func docstring"""\n'                     # L10 函数 docstring
            '    sql = "SELECT col FROM tbl"\n'              # L11 — 不应被豁免
            '    return sql\n'                                # L12
        )
        result = _extract_docstring_lines(content)
        # L3 模块 docstring + L10 函数 docstring 被识别
        assert 3 in result, "L3 module docstring should be recognized"
        assert 10 in result, "L10 function docstring should be recognized"
        # L11 裸 SQL 不应被豁免（R95 修复核心）
        assert 11 not in result, "L11 SQL should NOT be exempted (R95 fix)"
        # L5-L7 manifest 内容不应被豁免（ast 识别为 Assign，不是 docstring）
        assert 5 not in result and 6 not in result and 7 not in result
        assert result == {3, 10}, f"FAIL: expected {{3, 10}}, got {sorted(result)}"


# ---------------------------------------------------------------------------
# TestIsExemptLine — 行级豁免回归测试
# ---------------------------------------------------------------------------
class TestIsExemptLine:
    """行级豁免：注释行 / import 行。"""

    def test_comment_line_exempt(self):
        assert _is_exempt_line('# sql = "SELECT col FROM tbl"') is True

    def test_indented_comment_exempt(self):
        assert _is_exempt_line('    # comment') is True

    def test_import_line_exempt(self):
        assert _is_exempt_line('from foo import bar') is True

    def test_plain_import_exempt(self):
        assert _is_exempt_line('import os') is True

    def test_code_not_exempt(self):
        assert _is_exempt_line('sql = "SELECT col FROM tbl"') is False

    def test_empty_line_not_exempt(self):
        assert _is_exempt_line('') is False


# ---------------------------------------------------------------------------
# TestParseDiffWithLineNumbers — git diff 解析回归测试
# ---------------------------------------------------------------------------
class TestParseDiffWithLineNumbers:
    """git diff --unified=0 输出解析为 [(line_no, content), ...]。"""

    def test_simple_added_line(self):
        diff = '+++ b/file.py\n@@ -0,0 +1,1 @@\n+code = 1\n'
        result = _parse_diff_with_line_numbers(diff)
        assert result == [(1, 'code = 1')]

    def test_multiple_added_lines(self):
        diff = '+++ b/file.py\n@@ -0,0 +1,3 @@\n+a = 1\n+b = 2\nc = 3\n'
        result = _parse_diff_with_line_numbers(diff)
        # +a, +b 是 added，c 是 context（无 + 前缀，unified=0 通常无 context）
        assert (1, 'a = 1') in result
        assert (2, 'b = 2') in result

    def test_hunk_header_parsed(self):
        diff = '+++ b/file.py\n@@ -10,2 +12,3 @@\n+code = 1\n'
        result = _parse_diff_with_line_numbers(diff)
        # 行号从 12 开始
        assert result == [(12, 'code = 1')]

    def test_empty_diff(self):
        assert _parse_diff_with_line_numbers('') == []

    def test_no_added_lines(self):
        diff = '+++ b/file.py\n@@ -0,0 +1,0 @@\n'
        assert _parse_diff_with_line_numbers(diff) == []


# ---------------------------------------------------------------------------
# TestExtractSqlConstantLines — SQL_* 常量定义行范围提取（R96 治本）
# ---------------------------------------------------------------------------
class TestExtractSqlConstantLines:
    """SQL_* / _SQL_* 常量定义行范围提取（R96 用 ast 精确识别）。

    覆盖4种多行定义模式 + 边界场景。
    """

    def test_single_line_constant(self):
        """单行定义：SQL_X = "SELECT..." → 豁免 L1。"""
        content = 'SQL_GET_USER = "SELECT col FROM tbl"\n'
        assert _extract_sql_constant_lines(content) == {1}

    def test_paren_multiline_complete_sql(self):
        """括号多行定义（模式1，误报根因）：续行含完整 SQL → 全部豁免。

        file_task_mapper.py L66-68 实际场景。
        """
        content = (
            'SQL_SELECT = (\n'           # L1
            '    "SELECT task_id FROM task_files WHERE file_path = ?"\n'  # L2
            ')\n'                         # L3
        )
        assert _extract_sql_constant_lines(content) == {1, 2, 3}

    def test_triple_quote_multiline(self):
        """三引号多行定义（模式3）：整个三引号范围豁免。"""
        content = (
            'SQL_INSERT = """INSERT INTO tasks\n'  # L1
            '    (id, name) VALUES (?, ?)"""\n'   # L2
        )
        assert _extract_sql_constant_lines(content) == {1, 2}

    def test_backslash_continuation(self):
        """反斜杠续行定义：续行也被豁免。"""
        content = (
            'SQL_X = \\\n'                          # L1
            '    "SELECT * FROM users"\n'            # L2
        )
        assert _extract_sql_constant_lines(content) == {1, 2}

    def test_paren_multiline_sql_fragments(self):
        """括号多行 + SQL 跨行拼接（模式2）：每行都被豁免。"""
        content = (
            'SQL_JOIN = (\n'                              # L1
            '    "SELECT tf.task_id, tf.file_path "\n'    # L2
            '    "FROM task_files tf JOIN tasks t "\n'    # L3
            '    "WHERE tf.task_id = ?"\n'                 # L4
            ')\n'                                         # L5
        )
        assert _extract_sql_constant_lines(content) == {1, 2, 3, 4, 5}

    def test_multiple_sql_constants(self):
        """多个 SQL 常量混合：每个 Assign 节点都被识别。"""
        content = (
            'SQL_A = "SELECT 1"\n'           # L1
            'foo = "not sql"\n'              # L2（非 SQL_* 前缀）
            'SQL_B = "INSERT INTO t VALUES(1)"\n'  # L3
        )
        assert _extract_sql_constant_lines(content) == {1, 3}

    def test_non_sql_prefix_not_exempt(self):
        """非 SQL_* 前缀变量不豁免。"""
        content = (
            'QUERY = "SELECT * FROM tbl"\n'     # L1
            'FOO_SQL = "SELECT 1"\n'            # L2（SQL 不在开头）
        )
        assert _extract_sql_constant_lines(content) == set()

    def test_private_sql_prefix_exempt(self):
        """_SQL_PATTERN 等 _SQL_* 前缀也豁免（gate 内部变量）。"""
        content = '_SQL_PATTERN = re.compile(r"SELECT")\n'
        assert _extract_sql_constant_lines(content) == {1}

    def test_syntax_error_fail_open(self):
        """语法错误时 fail-open 返回空集合（不豁免，可能误报但不漏检）。"""
        content = 'def foo(:\n    SQL_X = "SELECT 1"\n'
        assert _extract_sql_constant_lines(content) == set()

    def test_empty_file(self):
        """空文件返回空集合。"""
        assert _extract_sql_constant_lines('') == set()
