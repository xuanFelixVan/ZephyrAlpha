# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates._diff_helpers
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] —
# [CONSUMERS] zephyr.governance.commit_gates.unsafe_dict_spread_gate; zephyr.governance.commit_gates.datetime_now_forbidden_gate; zephyr.governance.commit_gates.bare_sql_gate; zephyr.governance.commit_gates.hardcoded_url_gate
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] gate 共享 diff 解析工具模块——提取 unsafe_dict_spread_gate / datetime_now_forbidden_gate / bare_sql_gate / hardcoded_url_gate 公共 diff 解析函数，消除 FUNCTION-DUP 重复定义；纯函数无副作用；不可达路径 fail-open（返回空集/空列表/None）；_extract_docstring_lines 用 ast 精确识别 docstring（R95 治本），不再用正则近似；_extract_sql_constant_lines 用 ast 精确识别 SQL_*/_SQL_* 常量定义行范围（R96 治本），替代 bare_sql_gate 的 _SQL_CONSTANT_DEF_RE 正则近似
# [MODIFY-GUARD] 函数签名：_is_exempt_line(str)->bool, _extract_docstring_lines(str)->set[int], _extract_sql_constant_lines(str)->set[int], _parse_diff_with_line_numbers(str)->list[tuple[int,str]], _read_staged_file(gateway,str)->str|None
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有函数永不抛异常——异常降级为空返回值（set()/[]/None）
# [TESTS] tests/governance/commit_gates/test_diff_helpers.py（直接测试）；tests/governance/commit_gates/test_unsafe_dict_spread_gate.py（间接覆盖）
# [A_module] module_id=MOD-GOV-diff_helpers | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""_diff_helpers.py — gate 共享 diff 解析工具模块

提取自 unsafe_dict_spread_gate.py，供多个 commit-time gate 复用，
消除 FUNCTION-DUP gate 阻断（同目录同 name+body hash 重复函数）。

公共函数：
- _is_exempt_line: 行级豁免判定（注释/import）
- _extract_docstring_lines: docstring 行号集合提取（R95 用 ast 精确识别）
- _extract_sql_constant_lines: SQL_*/_SQL_* 常量定义行号集合提取（R96 用 ast 精确识别）
- _parse_diff_with_line_numbers: git diff 输出解析为 [(line_no, content)]
- _read_staged_file: 读取 staged 文件内容（git show :path）
- _get_staged_py_files: 获取 staged .py 文件列表
- _get_added_lines: 获取文件 added 行列表

Usage::

    from zephyr.governance.commit_gates._diff_helpers import (
        _is_exempt_line,
        _extract_docstring_lines,
        _extract_sql_constant_lines,
        _parse_diff_with_line_numbers,
        _read_staged_file,
    )
"""

from __future__ import annotations

import ast
import logging
import re

logger = logging.getLogger(__name__)

__all__ = [
    "_COMMENT_RE",
    "_IMPORT_RE",
    "_HUNK_HEADER_RE",
    "_SQL_CONSTANT_NAME_RE",
    "_is_exempt_line",
    "_extract_docstring_lines",
    "_extract_sql_constant_lines",
    "_parse_diff_with_line_numbers",
    "_read_staged_file",
    "_get_staged_py_files",
    "_get_added_lines",
]

# 行级豁免：注释 / import
_COMMENT_RE = re.compile(r"^\s*#")
_IMPORT_RE = re.compile(r"^\s*(from\s+\S+\s+import|import\s)")

# hunk header: @@ -old_start,old_count +new_start,new_count @@
_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

# SQL 常量名判定：匹配 _?SQL_ 前缀的变量名（SQL_FOO / _SQL_PATTERN 等）
# R96 治本：替代 bare_sql_gate._SQL_CONSTANT_DEF_RE 正则近似（只豁免定义行不跟踪多行）
_SQL_CONSTANT_NAME_RE = re.compile(r"^_?SQL_\w+$")


def _is_exempt_line(content: str) -> bool:
    """行级豁免：注释 / import（docstring 由 _extract_docstring_lines 多行跟踪处理）。"""
    return bool(_COMMENT_RE.match(content) or _IMPORT_RE.match(content))


def _extract_docstring_lines(file_content: str) -> set[int]:
    """返回文件中所有 docstring 内的行号集合（1-based）。

    使用 ast 模块精确识别 Module/ClassDef/FunctionDef/AsyncFunctionDef 的
    docstring（body[0] 是 ``ast.Expr(value=ast.Constant(str))``）。

    设计意图（R95 治本，2026-07-10）：
    - 只豁免真正的 docstring（模块/类/函数的文档字符串 body[0]）
    - 不豁免行内字符串赋值（如 ``__manifest__ = \"\"\"...\"\"\"``）
    - 不豁免独立字符串表达式（非 body[0]）

    旧实现用 ``stripped.startswith('\"\"\"')`` 作判据，是正则近似，无法区分
    上述场景，导致 ``__manifest__ = \"\"\"...\"\"\"`` 的结束独立 ``\"\"\"`` 行
    被误判为新 docstring 起始，后续所有行被错误豁免（cleanup_p0_auto_bridged.py
    L78/L87 裸 SQL 漏检根因）。

    fail-open：ast.parse 失败（语法错误）时返回空集合——所有行都不豁免，
    可能误报但不漏检（语法错误文件本就会在其他阶段失败）。

    Args:
        file_content: Python 文件完整内容。

    Returns:
        docstring 覆盖的行号集合（1-based）。
    """
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        logger.warning(
            "_extract_docstring_lines: ast.parse 失败（语法错误），"
            "fail-open 返回空集合——所有行都不豁免",
            exc_info=True,
        )
        return set()

    docstring_lines: set[int] = set()
    for node in ast.walk(tree):
        # docstring 仅出现在 Module/ClassDef/FunctionDef/AsyncFunctionDef 的 body[0]
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            if not node.body:
                continue
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                start = first.lineno
                end = getattr(first, "end_lineno", start)
                for i in range(start, end + 1):
                    docstring_lines.add(i)
    return docstring_lines


def _extract_sql_constant_lines(file_content: str) -> set[int]:
    """返回文件中所有 SQL_* / _SQL_* 常量定义覆盖的行号集合（1-based）。

    使用 ast 模块精确识别 Assign 节点，目标名匹配 ``^_?SQL_\\w+$``。
    豁免整个 Assign 节点的行范围（lineno 到 end_lineno），覆盖：
    - 单行定义：``SQL_X = "SELECT..."``
    - 括号多行：``SQL_X = (\\n    "SELECT..."\\n)``
    - 三引号多行：``SQL_X = \"\"\"\\nSELECT...\\n\"\"\"``
    - 反斜杠续行：``SQL_X = \\\\\\n    "SELECT..."``

    设计意图（R96 治本，2026-07-10）：
    旧实现用 ``_SQL_CONSTANT_DEF_RE = re.compile(r"^\\s*_?SQL_\\w+\\s*=")``
    只豁免定义行，不跟踪多行续行，导致括号隐式连接的续行含完整 SQL
    字符串字面量时被 ``_SQL_PATTERN`` 误报（file_task_mapper.py L67/L70/L73
    误报根因）。

    fail-open：ast.parse 失败（语法错误）时返回空集合——所有行都不豁免，
    可能误报但不漏检（语法错误文件本就会在其他阶段失败）。

    Args:
        file_content: Python 文件完整内容。

    Returns:
        SQL 常量定义覆盖的行号集合（1-based）。
    """
    try:
        tree = ast.parse(file_content)
    except SyntaxError:
        logger.warning(
            "_extract_sql_constant_lines: ast.parse 失败（语法错误），"
            "fail-open 返回空集合——所有行都不豁免",
            exc_info=True,
        )
        return set()

    sql_const_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and _SQL_CONSTANT_NAME_RE.match(target.id)
                ):
                    start = node.lineno
                    end = getattr(node, "end_lineno", start)
                    for i in range(start, end + 1):
                        sql_const_lines.add(i)
                    break  # 一个 target 命中即可豁免整个 Assign
    return sql_const_lines


def _parse_diff_with_line_numbers(diff_stdout: str) -> list[tuple[int, str]]:
    """解析 git diff --unified=0 输出，返回 [(line_no, added_content), ...]。

    line_no 是新文件中的 1-based 行号。
    hunk header ``@@ -a,b +c,d @@`` 中 c 是新文件起始行号。
    added 行（``+`` 前缀）占用新行号；删除行（``-`` 前缀）不占用；上下文行占用。
    """
    result: list[tuple[int, str]] = []
    current_line = 0
    for raw_line in diff_stdout.splitlines():
        m = _HUNK_HEADER_RE.match(raw_line)
        if m:
            current_line = int(m.group(1))
            continue
        if raw_line.startswith("+++"):
            continue
        if raw_line.startswith("+"):
            result.append((current_line, raw_line[1:]))
            current_line += 1
        elif raw_line.startswith("-"):
            pass  # 删除行不递增新行号
        else:
            current_line += 1  # 上下文行（unified=0 通常无，保险处理）
    return result


def _read_staged_file(gateway, py_file: str) -> str | None:
    """读取 staged 文件内容（index 版本，``git show :path``）。"""
    try:
        result = gateway._run_git(["git", "show", ":" + py_file])
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass
    return None


def _get_staged_py_files(gateway, gate_name: str = "gate") -> list[str]:
    """获取 staged added/modified .py 文件列表（fail-open）。

    失败时返回空列表并记录 warning。调用方应在返回空时 return True, ""（fail-open）。
    注意：不过滤 tests/，由调用方用 is_test_exempt() 过滤。
    """
    try:
        result = gateway._run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"]
        )
        if result.returncode != 0:
            logger.warning(
                "%s fail-open: git diff 失败(rc=%d)。", gate_name, result.returncode,
            )
            return []
        return [
            f.replace("\\", "/")
            for f in result.stdout.strip().splitlines()
            if f and f.endswith(".py")
        ]
    except Exception as e:
        logger.warning(
            "%s fail-open: git diff 异常(%s: %s)。",
            gate_name, type(e).__name__, e, exc_info=True,
        )
        return []


def _get_added_lines(
    gateway, py_file: str, gate_name: str = "gate"
) -> list[tuple[int, str]]:
    """获取文件的 added 行列表（fail-open）。

    失败时返回空列表并记录 warning。
    """
    try:
        result = gateway._run_git(
            ["git", "diff", "--cached", "--unified=0", "--", py_file]
        )
        if result.returncode != 0:
            return []
        return _parse_diff_with_line_numbers(result.stdout)
    except Exception as e:
        logger.warning("%s: git diff 失败 file=%s, %s", gate_name, py_file, e)
        return []
