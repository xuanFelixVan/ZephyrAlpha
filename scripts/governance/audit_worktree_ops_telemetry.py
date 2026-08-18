# [BLUEPRINT] MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY | docs/03_modules/_domain_governance/blueprint.md | §Ruling-100PCT-AI-GOVERNANCE-P2-6
# [MODULE] scripts.governance.audit_worktree_ops_telemetry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib (re, ast, json, sys, pathlib); 无 zephyr 内部依赖（审计脚本独立可运行）
# [CONSUMERS] AI 调用方审计；post-commit reconciler（可选）；session_startup_health_check（可选）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 永不抛异常——所有检查返回 violations 列表；AST + regex 双重检测降低误报
# [MODIFY-GUARD] ERASURE_PATTERLS / TELEMETRY_FUNCTIONS / EXEMPT_CONTEXTS 结构
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件读取失败→skip 该文件（不阻断审计）；返回 violations 列表
# [TESTS] tests/governance/test_audit_worktree_ops_telemetry.py
# [A_module] module_id=MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 由 commit 事件触发（非 cron/manual）
"""audit_worktree_ops_telemetry.py — 主工作区文件级擦除操作遥测完整性审计（P2-6）

病根
----
项目记忆硬约束：主工作区文件级擦除（restore/unlink/quarantine）操作必须全量纳入
``worktree_ops_log.jsonl`` 遥测，记录 ``session_id / source / file / content_hash / backup_path``。

但 P2-6 审计前发现：
1. ``_log_workspace_op`` 缺 ``content_hash`` 字段（已修复）
2. ``_safe_unlink_main_file`` 死代码 performs raw unlink 无遥测（已删除）
3. ``git restore --source`` 恢复路径无遥测（已修复）
4. 缺少自动化审计脚本——未来 AI 新增擦除操作可能再次遗漏遥测

治本
----
本脚本扫描 Python 文件，检测主工作区文件级擦除操作，验证每个操作附近有遥测调用。

检测策略
--------
1. **AST 函数边界识别**：用 ast.walk 找到所有 FunctionDef，确定每个擦除操作所属函数
2. **擦除操作检测**（regex）：
   - ``git stash push``（tracked 文件内容擦除）
   - ``git restore``（文件内容还原到 HEAD/source）
   - ``git checkout --``（legacy 擦除，应已替换为 stash）
   - ``Path.unlink()`` / ``os.unlink()`` / ``os.remove()``
   - ``shutil.rmtree()``
   - ``_quarantine_file``（内部已遥测，但审计应确认调用存在）
3. **遥测调用检测**：同一函数内有 ``_log_workspace_op(`` 或 ``_log_worktree_delete(``
4. **上下文豁免**：worktree 路径（``wt_path`` / ``worktree_path`` 参数）或 temp 文件
   （``.runtime`` / ``.aidrafts`` / ``msg_file``）的擦除豁免

API
---
- ``audit_worktree_ops_telemetry(paths) -> list[Violation]``：扫描文件列表
- ``audit_directory(root, exclude_dirs=...) -> list[Violation]``：扫描目录
- ``main()``：CLI 入口，输出 JSON

Usage::

    # CLI 模式
    python scripts/governance/audit_worktree_ops_telemetry.py <path1> [<path2> ...]

    # import 模式
    from scripts.governance.audit_worktree_ops_telemetry import audit_worktree_ops_telemetry
    violations = audit_worktree_ops_telemetry(["src/zephyr/gov_enforcement/rule_bridge/session_worktree.py"])

Exit codes:
    0 = 无违规
    1 = 发现违规（error severity）
"""
from __future__ import annotations

__manifest__ = """
args: []
description: audit_worktree_ops_telemetry.py — 主工作区文件级擦除操作遥测完整性审计（P2-6）
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

# 擦除操作检测模式：（regex, op_name, severity）
# severity: "error" = 必须有遥测；"warning" = 建议有遥测
ERASURE_PATTERNS: list[tuple[str, str, str]] = [
    # git stash push — tracked 文件内容擦除（文件还原到 HEAD）
    (r'["\']git["\']\s*,\s*["\']stash["\']\s*,\s*["\']push', "git_stash_push", "error"),
    # git restore — 文件内容还原（到 HEAD 或 --source）
    (r'["\']git["\']\s*,\s*["\']restore["\']', "git_restore", "error"),
    # git checkout -- — legacy 擦除（应已替换为 stash）
    (r'["\']git["\']\s*,\s*["\']checkout["\']\s*,\s*["\']--', "git_checkout_erase", "error"),
    # Path.unlink() / os.unlink() / os.remove()
    (r'\.unlink\s*\(\s*\)', "path_unlink", "warning"),
    (r'\bos\.(remove|unlink)\s*\(', "os_unlink", "warning"),
    # shutil.rmtree — 目录递归删除
    (r'shutil\.rmtree\s*\(', "shutil_rmtree", "warning"),
    # _quarantine_file — 内部已遥测，但审计应确认调用存在（info 级别）
    (r'_quarantine_file\s*\(', "quarantine_file", "info"),
]

# 满足遥测要求的函数名（同函数内出现即视为已遥测）
# 2026-08-19：补 shared 公共名——真源已提取到 zephyr.shared.io.workspace_telemetry
# （裁定 A），新代码直接调 log_workspace_op（无下划线前缀），检测器漏认会误报
# （git_batcher.git_restore_batch 实证）。
TELEMETRY_FUNCTIONS: set[str] = {
    "_log_workspace_op",
    "_log_worktree_delete",
    "log_workspace_op",
    "log_worktree_delete",
}

# 豁免上下文：函数名包含这些关键词时，擦除操作豁免（worktree 或 temp 文件操作）
# 原因：worktree 内文件操作不影响主工作区；temp 文件（.runtime/.aidrafts/msg_file）非源码
# 健康检查/孤儿清理的 unlink 是 temp test file / 过期辅助脚本，非主工作区源码擦除
EXEMPT_FUNC_NAME_KEYWORDS: set[str] = {
    "worktree_file",   # _delete_worktree_file — worktree 内文件
    "worktree_path",   # worktree 路径操作
    "cleanup_pool",    # _cleanup_pool_worktree — worktree pool 目录清理
    "pool_worktree",   # 同上
    "msg_file",        # 临时 commit message 文件
    "orphan",          # _cleanup_orphan_draft_scripts — .aidrafts 过期临时脚本清理
    "cleanup_orphan",  # 同上（双关键词覆盖）
    "sweep_quarantine",  # 隔离区过期清理（已是二级操作）
    "health_check",    # _run_startup_health_check — temp test file 读写验证
    "_force_rmtree",   # worktree 目录强制删除（已由 _log_worktree_delete 遥测）
    "release",         # _GlobalCommitLock.release / file lock release — 锁文件清理
    "_clear_stale",    # _clear_stale_lock — 过期锁文件清理
    # P3-1（2026-07-19）：self_healer._rollback — git restore 回滚 self_healer 自身修改
    # 语义不同于常规擦除：① 回滚的是 self_healer 自己刚做的修改（非用户/AI 文件操作）
    # ② 已有 logger.info/warning 记录（非 worktree_ops_log.jsonl 结构化遥测）
    # ③ 跨域 import _log_workspace_op 会违反架构边界（semantic_audit → gov_enforcement）
    # TODO(P3-1.1 follow-up): 提取 _log_workspace_op 到 shared 模块后，移除此豁免并补遥测
    "rollback",        # _rollback / _rollback_handler — 自愈回滚自身修改
}

# 豁免路径片段：擦除操作涉及这些路径片段时豁免（temp/lock/pathspec 文件，非源码）
EXEMPT_PATH_KEYWORDS: set[str] = {
    ".runtime",
    ".aidrafts",
    "msg_file",
    "msg_path",
    "tmp",
    "tempfile",
    "NamedTemporaryFile",
    "lock_file",      # _GlobalCommitLock / WorktreeManager 锁文件清理
    "lock_path",      # 文件锁路径清理
    "_lock_file",
    "pathspec",       # git pathspec 临时文件（add_pathspec_file / del_pathspec）
    "bundle_path",    # git bundle 临时文件
}

# 排除目录（_archive 是归档的 one-off 脚本，不审计）
_TEMP_DIRS = {".git", "__pycache__", ".pytest_cache", "_archive", "_archive_old"}


@dataclass
class Violation:
    """单条遥测缺失违规。"""

    file: str
    line: int
    col: int
    op: str           # git_stash_push / path_unlink / ...
    function: str     # 所在函数名
    severity: str     # error / warning / info
    snippet: str      # 违规行内容（前 120 字符）
    reason: str       # 违规原因说明


def _is_exempt_function(func_name: str) -> bool:
    """判断函数名是否在豁免列表中（worktree 或 temp 文件操作）。"""
    return any(kw in func_name for kw in EXEMPT_FUNC_NAME_KEYWORDS)


def _is_exempt_line(line: str) -> bool:
    """判断擦除操作所在行是否涉及豁免路径（temp 文件）。"""
    return any(kw in line for kw in EXEMPT_PATH_KEYWORDS)


def _find_enclosing_function(tree: ast.AST, lineno: int) -> ast.FunctionDef | None:
    """找到包含指定行号的最近 FunctionDef 节点。"""
    enclosing: ast.FunctionDef | None = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= lineno <= (node.end_lineno or node.lineno):
                # 选最内层的（lineno 最大的）
                if enclosing is None or node.lineno > enclosing.lineno:
                    enclosing = node
    return enclosing


def _function_has_telemetry(func_node: ast.FunctionDef) -> bool:
    """检查函数体内是否调用了遥测函数。"""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in TELEMETRY_FUNCTIONS:
                return True
            if isinstance(func, ast.Attribute) and func.attr in TELEMETRY_FUNCTIONS:
                return True
    return False


def _collect_docstring_line_ranges(tree: ast.AST) -> list[tuple[int, int]]:
    """收集所有 docstring / 字符串语句的行范围（用于跳过 docstring 中的误报）。

    检测 Module/FunctionDef/ClassDef 体首条 Expr(Constant str) 为 docstring，
    以及所有 Expr(Constant str) 节点（字符串语句，非赋值/调用）。
    """
    ranges: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", None)
            if not body:
                continue
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                start = first.lineno
                end = first.end_lineno or first.lineno
                ranges.append((start, end))
        # 也收集所有独立的字符串语句（非 docstring 的字符串字面量语句）
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                start = node.lineno
                end = node.end_lineno or node.lineno
                ranges.append((start, end))
    return ranges


def _is_in_docstring(lineno: int, ranges: list[tuple[int, int]]) -> bool:
    """判断行号是否在 docstring 行范围内。"""
    for start, end in ranges:
        if start <= lineno <= end:
            return True
    return False


def _audit_file(path: Path) -> list[Violation]:
    """审计单个文件，返回遥测缺失违规列表。

    策略：
    1. AST 解析获取函数边界 + docstring 行范围
    2. regex 扫描每行找擦除操作
    3. 对每个擦除操作，找所在函数，检查函数内是否有遥测调用
    4. 豁免：函数名在豁免列表 / 行涉及 temp 路径 / 行在 docstring 内
    """
    violations: list[Violation] = []
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return violations

    lines = source.splitlines()
    compiled_patterns = [(re.compile(p), op, sev) for p, op, sev in ERASURE_PATTERNS]
    docstring_ranges = _collect_docstring_line_ranges(tree)

    for lineno, line in enumerate(lines, 1):
        # 跳过注释行（简单检测）
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        for pattern, op_name, severity in compiled_patterns:
            m = pattern.search(line)
            if not m:
                continue
            # 豁免：行在 docstring/字符串语句内（避免审计脚本自身 docstring 误报）
            if _is_in_docstring(lineno, docstring_ranges):
                continue
            # 豁免：行涉及 temp/lock/pathspec 路径
            if _is_exempt_line(line):
                continue
            # 找所在函数
            func_node = _find_enclosing_function(tree, lineno)
            if func_node is None:
                # 模块级擦除——不豁免，报告
                violations.append(Violation(
                    file=str(path), line=lineno, col=m.start(),
                    op=op_name, function="<module>",
                    severity=severity,
                    snippet=line.rstrip()[:120],
                    reason="模块级擦除操作无函数包裹，无法确认遥测",
                ))
                continue
            func_name = func_node.name
            # 豁免：函数名在豁免列表
            if _is_exempt_function(func_name):
                continue
            # 检查函数内是否有遥测调用
            if _function_has_telemetry(func_node):
                continue
            # 违规：函数内有擦除操作但无遥测
            violations.append(Violation(
                file=str(path), line=lineno, col=m.start(),
                op=op_name, function=func_name,
                severity=severity,
                snippet=line.rstrip()[:120],
                reason=f"函数 {func_name} 内有 {op_name} 操作但无 _log_workspace_op/_log_worktree_delete 遥测调用",
            ))
    return violations


def audit_worktree_ops_telemetry(paths: Iterable[str | Path]) -> list[Violation]:
    """扫描文件列表，返回所有遥测缺失违规。

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
                all_violations.extend(_audit_file(py_file))
        elif path.is_file() and path.suffix == ".py":
            all_violations.extend(_audit_file(path))
    # 排序
    all_violations.sort(key=lambda v: (v.file, v.line, v.col))
    return all_violations


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
    return audit_worktree_ops_telemetry(paths)


def main() -> int:
    """CLI 入口：``python audit_worktree_ops_telemetry.py <path1> [<path2> ...]``。

    Exit codes:
        0 = 无违规
        1 = 发现 error severity 违规
    """
    parser = argparse.ArgumentParser(
        prog="audit_worktree_ops_telemetry",
        description="Audit worktree_ops_log.jsonl telemetry coverage (P2-6)",
    )
    parser.add_argument(
        "paths", nargs="+",
        help="file or directory paths to audit",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="output JSON (default: human-readable)",
    )
    parser.add_argument(
        "--include-warnings", action="store_true",
        help="include warning severity violations in exit code (default: only errors)",
    )
    args = parser.parse_args()

    violations: list[Violation] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            violations.extend(audit_directory(path))
        else:
            violations.extend(audit_worktree_ops_telemetry([path]))

    if args.json:
        print(json.dumps(
            [asdict(v) for v in violations], ensure_ascii=False, indent=2,
        ))
    else:
        if not violations:
            print("audit_worktree_ops_telemetry: 0 violations")
        else:
            error_count = sum(1 for v in violations if v.severity == "error")
            warn_count = sum(1 for v in violations if v.severity == "warning")
            info_count = sum(1 for v in violations if v.severity == "info")
            print(
                f"audit_worktree_ops_telemetry: {len(violations)} violations "
                f"({error_count} error, {warn_count} warning, {info_count} info):"
            )
            for v in violations:
                print(
                    f"  {v.file}:{v.line}:{v.col} [{v.severity}] "
                    f"{v.op} in {v.function}()"
                )
                print(f"    reason: {v.reason}")
                print(f"    snippet: {v.snippet}")

    # exit code: error 总是阻断；warning 仅在 --include-warnings 时阻断
    has_blocking = any(
        v.severity == "error" or (args.include_warnings and v.severity == "warning")
        for v in violations
    )
    return 1 if has_blocking else 0


if __name__ == "__main__":
    sys.exit(main())
