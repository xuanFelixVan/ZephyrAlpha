# [BLUEPRINT] MOD-INF-005 | scripts/governance/fix_orphan_exports.py | §
# [MODULE] scripts.governance.fix_orphan_exports
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
# [TTL] permanent
"""fix_orphan_exports.py — 批量修复孤儿模块导出（RULE-TWO 防线 2 修复器）

扫描 src/zephyr/ 下所有 .py 文件，检测未被父包 __init__.py 导出的孤儿模块，
自动更新或创建 __init__.py 确保所有模块可被发现。

策略:
  - 缺少 __init__.py 的包 → 创建包含 __all__ 的基础 __init__.py
  - 已有 __init__.py 但未导出的模块 → 追加到现有 __all__ 中（保留已有内容）
  - 检测逻辑与 audit_registration.py 完全一致（AST-based __all__ 提取）

用法:
    python scripts/governance/fix_orphan_exports.py           # 扫描并修复
    python scripts/governance/fix_orphan_exports.py --dry-run # 只看不修
    python scripts/governance/fix_orphan_exports.py --warn-only

返回码:
    0 = CLEAN（无孤儿）
    1 = 修复完成（有孤儿并被修复）
    2 = 扫描错误
"""

from __future__ import annotations

__manifest__ = """
args: []
description: fix_orphan_exports.py — 批量修复孤儿模块导出（RULE-TWO 防线 2 修复器）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import argparse
import ast
import os
import sys
import textwrap
from collections import defaultdict
from pathlib import Path

from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 _safe_atomic_write→共享 SSoT

PROJECT_ROOT = REPO_ROOT
SRC_ZEPHYR = PROJECT_ROOT / "src" / "zephyr"

EXCLUDE_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git", ".venv"}
EXCLUDE_MODULE_NAMES = {"__init__", "conftest", "setup", "version", "py"}


def _extract_all_entries(source: str) -> set[str]:
    """AST-based __all__ extraction — identical to audit_registration.py logic."""
    entries: set[str] = set()
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    entries.add(elt.value)
    except SyntaxError:
        import re

        for match in re.finditer(r'"([^"]+)"', source):
            entries.add(match.group(1))
    return entries


def _find_orphans() -> dict[str, list[str]]:
    """Scans src/zephyr/ and returns {package_path: [module_names]} for orphans.

    Uses AST-based extraction — same as audit_registration.py.
    """
    orphans: dict[str, list[str]] = defaultdict(list)

    for py_file in sorted(SRC_ZEPHYR.rglob("*.py")):
        rel_parts = py_file.relative_to(SRC_ZEPHYR).parts
        if any(p in EXCLUDE_PARTS for p in rel_parts):
            continue
        if rel_parts[-1] == "__init__.py":
            continue
        if py_file.stem in EXCLUDE_MODULE_NAMES:
            continue

        pkg_dir = "/".join(rel_parts[:-1])
        module_name = rel_parts[-1].replace(".py", "")
        init_path = py_file.parent / "__init__.py"

        if not init_path.exists():
            orphans[pkg_dir].append(module_name)
            continue

        content = init_path.read_text(encoding="utf-8")
        registered = _extract_all_entries(content)

        class_name = "".join(p.capitalize() for p in module_name.split("_"))
        if module_name not in registered and class_name not in registered:
            orphans[pkg_dir].append(module_name)

    return dict(orphans)


def _generate_init_content(pkg_rel: str, modules: list[str], existing_content: str = "") -> str:
    """Generate __init__.py content with proper __all__ exports.

    For existing content with __all__: appends new module names to the END
    of the existing __all__ list using simple text manipulation.
    """
    sorted_modules = sorted(modules)
    pkg_display = pkg_rel.replace("/", ".") if pkg_rel else "zephyr"

    if not existing_content:
        all_line = f"__all__ = [{', '.join(repr(m) for m in sorted_modules)}]\n"
        return (
            textwrap.dedent(f'''\
            """{pkg_display} — auto-generated package init."""

            {all_line}''')
            + "\n"
        )

    try:
        tree = ast.parse(existing_content)
    except SyntaxError:
        all_line = f"__all__ = [{', '.join(repr(m) for m in sorted_modules)}]\n"
        return existing_content.rstrip("\n") + "\n\n" + all_line + "\n"

    all_nodes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
    ]

    if not all_nodes:
        all_line = f"__all__ = [{', '.join(repr(m) for m in sorted_modules)}]\n"
        return existing_content.rstrip("\n") + "\n\n" + all_line + "\n"

    all_node = all_nodes[0]
    if not isinstance(all_node.value, (ast.List, ast.Tuple)):
        return existing_content

    start_line = all_node.lineno - 1
    end_line = (all_node.end_lineno or all_node.lineno) - 1

    lines = existing_content.split("\n")

    bracket_found = False
    for line_idx in range(end_line, start_line - 1, -1):
        current_line = lines[line_idx]
        close_bracket = current_line.rfind("]")
        if close_bracket >= 0:
            new_items = ", ".join(repr(m) for m in sorted_modules)
            before = current_line[:close_bracket]
            stripped = before.rstrip()
            last_char = stripped[-1] if stripped else ""

            if not stripped or last_char == "[":
                # 空列表 [] 或括号独占一行：不加前导逗号
                sep = ""
            elif last_char == ",":
                # 尾随逗号已存在：只补一个空格
                sep = " "
            else:
                # 正常情形：元素紧邻 ]，需要前导逗号
                sep = ", "

            lines[line_idx] = stripped + sep + new_items + current_line[close_bracket:]
            bracket_found = True
            break

    if not bracket_found:
        all_line = f"__all__ = [{', '.join(repr(m) for m in sorted_modules)}]\n"
        return existing_content.rstrip("\n") + "\n\n" + all_line + "\n"

    return "\n".join(lines)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="批量修复孤儿模块导出")
    parser.add_argument("--dry-run", action="store_true", help="只看不修")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="报告孤儿但不修复（同 --dry-run）",
    )
    args = parser.parse_args()

    orphans = _find_orphans()
    total = sum(len(v) for v in orphans.values())
    pkg_count = len(orphans)

    if total == 0:
        print("[PASS] No orphan modules found. CLEAN.")
        sys.exit(EXIT_PASS)

    print(f"Found {total} orphan modules across {pkg_count} packages.")
    dry = args.dry_run or args.warn_only
    print(f"{'DRY RUN' if dry else 'Applying fixes'}...")
    print()

    fixed = 0
    created = 0
    updated = 0

    for pkg_rel, modules in sorted(orphans.items()):
        pkg_name = pkg_rel.replace("/", ".") if pkg_rel else "zephyr"
        if pkg_rel:
            init_path = SRC_ZEPHYR / pkg_rel.replace("/", os.sep) / "__init__.py"
        else:
            init_path = SRC_ZEPHYR / "__init__.py"

        if dry:
            action = "CREATE" if not init_path.exists() else "UPDATE"
            for m in sorted(modules):
                print(f"  [{action}] {pkg_name}.__init__: +'{m}'")
            continue

        existing = init_path.read_text(encoding="utf-8") if init_path.exists() else ""
        new_content = _generate_init_content(pkg_rel, modules, existing)

        atomic_write(init_path, new_content)

        for m in sorted(modules):
            action = "CREATE" if not existing else "UPDATE"
            print(f"  [{action}] {pkg_name}.__init__: +'{m}'")
            fixed += 1
            if not existing:
                created += 1
            else:
                updated += 1

    print()
    print(f"Fixed: {fixed} modules ({created} in new init, {updated} in existing init)")
    sys.exit(1 if fixed > 0 else 0)


if __name__ == "__main__":
    main()
