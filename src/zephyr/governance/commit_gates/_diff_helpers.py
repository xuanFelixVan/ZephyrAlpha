# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates._diff_helpers
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] —
# [CONSUMERS] zephyr.governance.commit_gates.unsafe_dict_spread_gate; zephyr.governance.commit_gates.datetime_now_forbidden_gate
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] gate 共享 diff 解析工具模块——提取 unsafe_dict_spread_gate / datetime_now_forbidden_gate 公共 diff 解析函数，消除 FUNCTION-DUP 重复定义；纯函数无副作用；不可达路径 fail-open（返回空集/空列表/None）
# [MODIFY-GUARD] 函数签名：_is_exempt_line(str)->bool, _extract_docstring_lines(str)->set[int], _parse_diff_with_line_numbers(str)->list[tuple[int,str]], _read_staged_file(gateway,str)->str|None
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 所有函数永不抛异常——异常降级为空返回值（set()/[]/None）
# [TESTS] tests/governance/commit_gates/test_unsafe_dict_spread_gate.py（间接覆盖）
# [A_module] module_id=MOD-GOV-diff_helpers | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""_diff_helpers.py — gate 共享 diff 解析工具模块

提取自 unsafe_dict_spread_gate.py，供多个 commit-time gate 复用，
消除 FUNCTION-DUP gate 阻断（同目录同 name+body hash 重复函数）。

公共函数：
- _is_exempt_line: 行级豁免判定（注释/import）
- _extract_docstring_lines: 多行 docstring 行号集合提取
- _parse_diff_with_line_numbers: git diff 输出解析为 [(line_no, content)]
- _read_staged_file: 读取 staged 文件内容（git show :path）

Usage::

    from zephyr.governance.commit_gates._diff_helpers import (
        _is_exempt_line,
        _extract_docstring_lines,
        _parse_diff_with_line_numbers,
        _read_staged_file,
    )
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

__all__ = [
    "_COMMENT_RE",
    "_IMPORT_RE",
    "_HUNK_HEADER_RE",
    "_is_exempt_line",
    "_extract_docstring_lines",
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


def _is_exempt_line(content: str) -> bool:
    """行级豁免：注释 / import（docstring 由 _extract_docstring_lines 多行跟踪处理）。"""
    return bool(_COMMENT_RE.match(content) or _IMPORT_RE.match(content))


def _extract_docstring_lines(file_content: str) -> set[int]:
    """返回文件中所有 docstring 内的行号集合（1-based）。

    跟踪 ``\"\"\"...\"\"\"`` 和 ``'''...'''`` 多行 docstring 范围。
    单行 docstring（同行开闭）只标记该行。
    用于豁免 docstring 中的示例代码（如 ``SomeClass(**varname)``），
    避免 gate 误报 docstring 示例。
    """
    lines = file_content.splitlines()
    docstring_lines: set[int] = set()
    in_docstring = False
    quote = ""
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if not in_docstring:
            for q in ('"""', "'''"):
                if stripped.startswith(q):
                    in_docstring = True
                    quote = q
                    docstring_lines.add(i)
                    # 检查同行是否结束（单行 docstring）
                    rest = stripped[len(q):]
                    if quote in rest:
                        in_docstring = False
                        quote = ""
                    break
        else:
            docstring_lines.add(i)
            if quote in stripped:
                in_docstring = False
                quote = ""
    return docstring_lines


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
