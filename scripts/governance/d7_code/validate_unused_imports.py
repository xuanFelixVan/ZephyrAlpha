# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/validate_unused_imports.py | §
# [MODULE] scripts.governance.d7_code.validate_unused_imports
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
validate_unused_imports.py — 未使用导入检测



对标：PEP 8 — imports should be used or removed
     PS-STD-003 COND-43（代码质量维度补全）

检测 src/zephyr/ 下所有 .py 文件中导入但未使用的模块。

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 未使用导入检测——AST 级扫描，检查 import 了但未引用的模块
dimensions:
- D7
priority: P1
timeout_seconds: 30
warn_only: false
"""


import argparse
import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import EXIT_PASS, REPO_ROOT, SRC_DIR

SKIP_NAMES = {"__future__.annotations", "__future__.division", "__future__.print_function"}


def _collect_used_names(tree: ast.AST) -> set[str]:
    """_collect_used_names implementation."""
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                used.add(node.value.id)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                used.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    used.add(node.func.value.id)
    return used


def _get_imported_names(tree: ast.AST) -> list[tuple[int, str, str]]:
    """_get_imported_names implementation."""
    imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                imports.append((node.lineno, name, alias.name))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                name = alias.asname or alias.name
                imports.append((node.lineno, name, f"{node.module}.{alias.name}" if node.module else alias.name))
    return imports


def scan_unused_imports(source_path: Path) -> list[tuple[int, str, str]]:
    """扫描未使用的 import."""
    with open(source_path, encoding="utf-8") as f:
        """扫描未使用的 import."""
        """扫描并返回发现列表."""
        source = f.read()
    tree = ast.parse(source, filename=str(source_path))

    used = _collect_used_names(tree)
    imported = _get_imported_names(tree)

    unused = []
    for lineno, name, full_name in imported:
        if full_name in SKIP_NAMES:
            continue
        if name not in used:
            unused.append((lineno, name, full_name))
    return unused
    """扫描未使用的 import."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="未使用导入检测")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    findings = []
    total_files = 0

    for py_file in SRC_DIR.rglob("*.py"):
        total_files += 1
        unused = scan_unused_imports(py_file)
        if unused:
            try:
                rel = py_file.relative_to(REPO_ROOT)
            except ValueError:
                rel = py_file
            for lineno, name, full_name in unused:
                findings.append(f"[P2] {rel}:{lineno}  unused import '{full_name}'")

    if findings:
        print(f"\n[UNUSED-IMPORTS] {len(findings)} 个未使用导入（扫描 {total_files} 文件）:\n", file=sys.stderr)
        for f_item in findings:
            print(f_item, file=sys.stderr)
        print(file=sys.stderr)
    else:
        print(f"\n[UNUSED-IMPORTS] 全部 {total_files} 文件无未使用导入 ✅\n", file=sys.stderr)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
