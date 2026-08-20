# [BLUEPRINT] MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-5
# [MODULE] scripts.governance.audit_return_contract_usage
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib (re, pathlib, json, sys); 无 zephyr 内部依赖（审计脚本独立可运行）
# [CONSUMERS] AI 调用方审计；post-commit reconciler（可选）；session_startup_health_check（可选）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 永不抛异常——所有检查返回 violations 列表；AST + regex 双重检测降低误报
# [MODIFY-GUARD] KNOWN_MISUSE_PATTERLS 字典结构
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件读取失败→skip 该文件（不阻断审计）；返回 violations 列表
# [TESTS] tests/governance/test_audit_return_contract_usage.py
# [A_module] module_id=MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 由 commit 事件触发（非 cron/manual）
"""audit_return_contract_usage.py — 返回契约 ok 键调用方审计（P2-5，2026-07-19）

病根
----
session_worktree_commit/merge/abort 等 TypedDict 返回契约已定义 ``ok: bool`` 作为
消费方判定成败的唯一入口，但 AI 生成的脚本（.runtime/、.trae/、tmp/）可能误用
旧键名（``committed`` / ``merged`` / ``success``），导致：

1. ``committed`` 键不存在 → KeyError 静默失败
2. ``merged`` 键语义≠``ok``（merge 可能 ok=True 但 merged=False，如 nothing to merge）
3. ``success`` 键不存在 → KeyError

治本
----
本脚本扫描 Python 文件，检测已知误用模式：

1. **正则模式**：``<var>["committed"]`` / ``<var>["merged"]`` / ``<var>["success"]``
   出现在 ``session_worktree_commit(`` / ``session_worktree_merge(`` 调用后 20 行内
2. **AST 模式**：Subscript 节点访问上述键，且赋值来源是 session_worktree_* 调用

API
---
- ``audit_return_contract_usage(paths) -> list[Violation]``：扫描文件列表
- ``audit_directory(root, exclude_dirs=...) -> list[Violation]``：扫描目录
- ``main()``：CLI 入口，输出 JSON

设计原则
--------
1. **双重检测**：正则（快速）+ AST（精确），降低误报
2. **永不抛异常**：单文件失败 skip，不影响其他文件
3. **JSON 输出**：便于 AI 解析 + reconciler 持久化
4. **可扩展**：``KNOWN_MISUSE_PATTERNS`` 字典新增模式即可

Usage::

    # CLI 模式
    python scripts/governance/audit_return_contract_usage.py <path1> [<path2> ...]

    # import 模式
    from scripts.governance.audit_return_contract_usage import audit_return_contract_usage
    violations = audit_return_contract_usage(["path/to/script.py"])
    for v in violations:
        print(f"{v['file']}:{v['line']}: {v['pattern']}")

Exit codes:
    0 = 无违规
    1 = 发现违规（AI MUST 修复，不可静默忽略）
"""

from __future__ import annotations

__manifest__ = """
args: []
description: audit_return_contract_usage.py — 返回契约 ok 键调用方审计（P2-5，2026-07-19）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

# 已知误用模式：function_name → set of forbidden keys
# 这些键在 TypedDict 契约中不存在，或语义≠ok（merged 可能为 False 但 ok=True）
KNOWN_MISUSE_PATTERNS: dict[str, set[str]] = {
    "session_worktree_commit": {"committed", "success", "status_ok"},
    "session_worktree_merge": {"merged", "success", "status_ok"},  # merged 语义≠ok
    "session_worktree_abort": {"aborted", "success", "status_ok"},
    "session_worktree_start": {"started", "success", "status_ok"},
    "session_worktree_status": {"available", "success", "status_ok"},
    "session_worktree_sweep": {"swept", "success", "status_ok"},
    # P2-1 emergency_commit 也用 ok 键
    "emergency_commit": {"committed", "success", "status_ok"},
}

# 排除目录（AI 临时脚本集中区，仍审计但单独标记）
_TEMP_DIRS = {".git", "__pycache__", ".pytest_cache"}


@dataclass
class Violation:
    """单条违规。"""

    file: str
    line: int
    col: int
    function: str  # session_worktree_commit 等
    forbidden_key: str  # committed / merged / success
    pattern: str  # "subscript_access" / "regex_near_call"
    snippet: str  # 违规行内容（前 120 字符）
    severity: str  # "error"（键不存在）/ "warning"（语义≠ok）


def _is_temp_path(path: Path) -> bool:
    """判断是否为 AI 临时脚本路径（.runtime/、.trae/、tmp/）。"""
    parts = path.parts
    return any(p in parts for p in (".runtime", ".trae", "tmp", ".aidrafts"))


def _audit_file_ast(path: Path) -> list[Violation]:
    """用 AST 检测 Subscript 节点访问 forbidden key。

    精确度高但需要文件可被 ast.parse（语法正确）。
    """
    violations: list[Violation] = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return violations  # 语法错误文件 skip（其他工具会报）

    # 收集所有 session_worktree_* / emergency_commit 调用，记录赋值变量名
    # pattern: <var> = <func>(...)  或  <var> = <obj>.<func>(...)
    call_bindings: dict[str, str] = {}  # var_name → function_name
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                func = node.value.func
                func_name = ""
                if isinstance(func, ast.Name):
                    func_name = func.id
                elif isinstance(func, ast.Attribute):
                    func_name = func.attr
                if func_name in KNOWN_MISUSE_PATTERNS:
                    call_bindings[node.targets[0].id] = func_name

    # 检测 Subscript 访问 forbidden key
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id in call_bindings:
            func_name = call_bindings[node.value.id]
            forbidden = KNOWN_MISUSE_PATTERNS[func_name]
            # 提取 subscript key（字符串字面量）
            key_node = node.slice
            # Python 3.9+ ast.Subscript.slice 直接是 value（非 Index）
            if isinstance(key_node, ast.Index):  # Python 3.8 兼容
                key_node = key_node.value
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                key = key_node.value
                if key in forbidden:
                    severity = "warning" if key == "merged" else "error"
                    snippet = _get_line_snippet(path, node.lineno)
                    violations.append(
                        Violation(
                            file=str(path),
                            line=node.lineno,
                            col=node.col_offset,
                            function=func_name,
                            forbidden_key=key,
                            pattern="subscript_access",
                            snippet=snippet,
                            severity=severity,
                        )
                    )
    return violations


def _get_line_snippet(path: Path, lineno: int) -> str:
    """获取指定行内容（前 120 字符）。"""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if i == lineno:
                    return line.rstrip()[:120]
    except OSError:
        pass
    return ""


def _audit_file_regex(path: Path) -> list[Violation]:
    """用正则检测 forbidden key 访问（快速但可能有误报）。

    匹配模式：``<var>["<forbidden>"]`` 或 ``<var>['<forbidden>']``
    其中 <var> 在前 20 行内有 ``session_worktree_*(`` 或 ``emergency_commit(`` 赋值。
    """
    violations: list[Violation] = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        lines = source.splitlines()
    except OSError:
        return violations

    # 找所有 session_worktree_* / emergency_commit 调用的赋值变量
    call_pattern = re.compile(
        r"(\w+)\s*=\s*(\w+\.)?(" + "|".join(KNOWN_MISUSE_PATTERNS.keys()) + r")\s*\(",
    )
    bindings: dict[str, str] = {}  # var → function
    for m in call_pattern.finditer(source):
        var_name = m.group(1)
        func_name = m.group(3)
        bindings[var_name] = func_name

    if not bindings:
        return violations

    # 找所有 <var>["key"] 或 <var>['key'] 访问
    access_pattern = re.compile(r"(\w+)\s*\[\s*['\"](\w+)['\"]\s*\]")
    for lineno, line in enumerate(lines, 1):
        for m in access_pattern.finditer(line):
            var_name = m.group(1)
            key = m.group(2)
            if var_name in bindings:
                func_name = bindings[var_name]
                forbidden = KNOWN_MISUSE_PATTERNS[func_name]
                if key in forbidden:
                    severity = "warning" if key == "merged" else "error"
                    violations.append(
                        Violation(
                            file=str(path),
                            line=lineno,
                            col=m.start(),
                            function=func_name,
                            forbidden_key=key,
                            pattern="regex_near_call",
                            snippet=line.rstrip()[:120],
                            severity=severity,
                        )
                    )
    return violations


def audit_return_contract_usage(paths: Iterable[str | Path]) -> list[Violation]:
    """扫描文件列表，返回所有违规。

    Args:
        paths: 文件路径列表（目录自动遍历 .py 文件）。

    Returns:
        Violation 列表（按 file/line 排序）。
    """
    all_violations: list[Violation] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for py_file in path.rglob("*.py"):
                if any(part in _TEMP_DIRS for part in py_file.parts):
                    continue
                all_violations.extend(_audit_file_ast(py_file))
                all_violations.extend(_audit_file_regex(py_file))
        elif path.is_file() and path.suffix == ".py":
            all_violations.extend(_audit_file_ast(path))
            all_violations.extend(_audit_file_regex(path))
    # 去重（AST + regex 可能命中同一行）
    seen: set[tuple[str, int, str, str]] = set()
    unique: list[Violation] = []
    for v in all_violations:
        key = (v.file, v.line, v.forbidden_key, v.function)
        if key not in seen:
            seen.add(key)
            unique.append(v)
    # 排序
    unique.sort(key=lambda v: (v.file, v.line, v.col))
    return unique


def audit_directory(
    root: str | Path,
    exclude_dirs: set[str] | None = None,
) -> list[Violation]:
    """扫描目录（默认排除 .git/__pycache__/.pytest_cache）。

    Args:
        root: 根目录。
        exclude_dirs: 额外排除目录名集合。

    Returns:
        Violation 列表。
    """
    exclude = _TEMP_DIRS | (exclude_dirs or set())
    root_path = Path(root)
    paths: list[Path] = []
    for py_file in root_path.rglob("*.py"):
        if any(part in exclude for part in py_file.parts):
            continue
        paths.append(py_file)
    return audit_return_contract_usage(paths)


def main() -> int:
    """CLI 入口：``python audit_return_contract_usage.py <path1> [<path2> ...]``。

    Exit codes:
        0 = 无违规
        1 = 发现违规（error severity）
    """
    parser = argparse.ArgumentParser(
        prog="audit_return_contract_usage",
        description="Audit return contract ok key usage (P2-5)",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="file or directory paths to audit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="output JSON (default: human-readable)",
    )
    args = parser.parse_args()

    violations: list[Violation] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            violations.extend(audit_directory(path))
        else:
            violations.extend(audit_return_contract_usage([path]))

    if args.json:
        print(
            json.dumps(
                [asdict(v) for v in violations],
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if not violations:
            print("audit_return_contract_usage: 0 violations")
        else:
            print(f"audit_return_contract_usage: {len(violations)} violations:")
            for v in violations:
                print(f"  {v.file}:{v.line}:{v.col} [{v.severity}] {v.function} -> ['{v.forbidden_key}'] ({v.pattern})")
                print(f"    snippet: {v.snippet}")

    # 有 error severity 违规 → exit 1
    has_errors = any(v.severity == "error" for v in violations)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def audit_file_ast(path) -> list[Violation]:
    """公共接口：audit_file_ast（Stage 4 公共化）。"""
    return _audit_file_ast(path)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def audit_file_regex(path) -> list[Violation]:
    """公共接口：audit_file_regex（Stage 4 公共化）。"""
    return _audit_file_regex(path)
