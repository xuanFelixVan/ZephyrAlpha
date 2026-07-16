# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] scripts.fix_orphan_all
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.__init__
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
"""fix_orphan_all.py — 自动修复 __init__.py __all__ 孤儿模块

遍历 src/zephyr/ 下所有包，将不在 __all__ 中的 .py 模块添加进去。
同时添加对应的 import 语句和 class/function 名称到 __all__。

用法:
    python scripts/fix_orphan_all.py
    python scripts/fix_orphan_all.py --dry-run
    python scripts/fix_orphan_all.py --no-imports
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT as PROJECT_ROOT  # noqa: E402

SRC_ZEPHYR = PROJECT_ROOT / "src" / "zephyr"

EXCLUDE_DIRS = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".git",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        "egg-info",
        ".ailocks",
        "_backup",
        "_archive",
    }
)
EXCLUDE_FILES = frozenset(
    {
        "__init__.py",
        "conftest.py",
        "setup.py",
        "version.py",
        "py.typed",
    }
)


def strip_bom(source: str) -> str:
    if source.startswith("\ufeff"):
        return source[1:]
    return source


def extract_public_names(py_file: Path) -> list[str]:
    try:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []
    names = []
    for node in ast.iter_child_nodes(tree):
        if (isinstance(node, ast.ClassDef) and not node.name.startswith("_")) or (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
        ):
            names.append(node.name)
    return names


def find_all_assignment(source: str) -> tuple[set[str], int, int, bool] | None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    is_literal = isinstance(node.value, (ast.List, ast.Tuple))
                    entries: set[str] = set()
                    if is_literal:
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                entries.add(elt.value)
                    return entries, node.lineno, node.end_lineno or node.lineno, is_literal
    return None


def get_orphan_modules(pkg_dir: Path, existing_all: set[str]) -> list[tuple[Path, str]]:
    orphans = []
    for py_file in sorted(pkg_dir.glob("*.py")):
        if py_file.name in EXCLUDE_FILES:
            continue
        if py_file.name.startswith("_"):
            continue
        module_name = py_file.stem
        class_name = "".join(p.capitalize() for p in module_name.split("_"))
        if module_name not in existing_all and class_name not in existing_all:
            orphans.append((py_file, module_name))
    return orphans


def format_import_line(pkg_dotted: str, module_name: str, names: list[str]) -> str:
    single_line = f"from zephyr.{pkg_dotted}.{module_name} import {', '.join(names)}"
    if len(single_line) <= 100:
        return single_line
    lines = [f"from zephyr.{pkg_dotted}.{module_name} import ("]
    for name in names:
        lines.append(f"    {name},")
    lines.append(")")
    return "\n".join(lines)


def format_all_block(entries: list[str]) -> str:
    sorted_entries = sorted(entries, key=lambda x: (not x[0].islower(), x.lower()))
    lines = ["__all__ = ["]
    for entry in sorted_entries:
        lines.append(f"    {entry!r},")
    lines.append("]")
    return "\n".join(lines)


def atomic_write(path: Path, content: str) -> None:
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def rebuild_init(source: str, new_imports: list[str], new_all_entries: set[str]) -> str:
    all_info = find_all_assignment(source)
    if all_info is not None:
        existing_all, all_start, all_end, is_literal = all_info
    else:
        existing_all = set()
        all_start = -1
        all_end = -1
        is_literal = True

    merged = sorted(existing_all | new_all_entries, key=lambda x: (not x[0].islower(), x.lower()))
    new_all_block = format_all_block(merged)

    lines = source.split("\n")

    if (all_start > 0 and is_literal) or (all_start > 0 and not is_literal):
        new_lines = lines[: all_start - 1] + [new_all_block] + lines[all_end:]
    else:
        new_lines = lines + ["", new_all_block]

    all_idx = None
    for i, line in enumerate(new_lines):
        if line.startswith("__all__"):
            all_idx = i
            break

    if all_idx is not None and new_imports:
        import_block = "\n".join(new_imports)
        new_lines = new_lines[:all_idx] + [import_block, ""] + new_lines[all_idx:]

    return "\n".join(new_lines)


def verify_package_import(pkg_dotted: str) -> tuple[bool, str]:
    import importlib

    src_path = str(PROJECT_ROOT / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    try:
        importlib.import_module(f"zephyr.{pkg_dotted}")
        return True, ""
    except Exception as e:
        return False, str(e)


def fix_package(pkg_dir: Path, no_imports: bool = False) -> tuple[int, list[str], bool]:
    init_py = pkg_dir / "__init__.py"
    rel_pkg = pkg_dir.relative_to(SRC_ZEPHYR)
    pkg_dotted = ".".join(rel_pkg.parts)

    source = strip_bom(init_py.read_text(encoding="utf-8-sig"))
    all_info = find_all_assignment(source)
    existing_all = all_info[0] if all_info else set()

    orphans = get_orphan_modules(pkg_dir, existing_all)
    if not orphans:
        return 0, [], False

    new_import_lines = []
    new_all_names: set[str] = set()
    skipped = []

    for orphan_path, module_name in orphans:
        public_names = extract_public_names(orphan_path)
        if public_names and not no_imports:
            import_line = format_import_line(pkg_dotted, module_name, public_names)
            new_import_lines.append(import_line)
            new_all_names.update(public_names)
        new_all_names.add(module_name)

    if not new_all_names:
        return 0, skipped, False

    used_imports = False
    if new_import_lines:
        new_source = rebuild_init(source, new_import_lines, new_all_names)
        try:
            compile(new_source, str(init_py), "exec")
        except SyntaxError:
            new_source = None

        if new_source is not None:
            atomic_write(init_py, new_source)
            ok, err = verify_package_import(pkg_dotted)
            if ok:
                used_imports = True
            else:
                new_source_no_imports = rebuild_init(source, [], new_all_names)
                try:
                    compile(new_source_no_imports, str(init_py), "exec")
                    atomic_write(init_py, new_source_no_imports)
                    skipped.append(f"{pkg_dotted}: import fallback ({err[:80]})")
                except SyntaxError as e:
                    skipped.append(f"{pkg_dotted}: syntax error: {e}")
                    return 0, skipped, False

    if not used_imports:
        new_source = rebuild_init(source, [], new_all_names)
        try:
            compile(new_source, str(init_py), "exec")
        except SyntaxError as e:
            skipped.append(f"{pkg_dotted}: syntax error: {e}")
            return 0, skipped, False
        atomic_write(init_py, new_source)

    return len(orphans), skipped, used_imports


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-imports", action="store_true")
    args = parser.parse_args()

    packages = []
    for init_py in SRC_ZEPHYR.rglob("__init__.py"):
        if any(ex in init_py.parts for ex in EXCLUDE_DIRS):
            continue
        packages.append(init_py.parent)
    packages.sort()

    total_fixed = 0
    total_orphans = 0
    total_with_imports = 0
    all_skipped = []

    for pkg_dir in packages:
        rel_pkg = pkg_dir.relative_to(SRC_ZEPHYR)
        pkg_dotted = ".".join(rel_pkg.parts)

        if args.dry_run:
            source = strip_bom((pkg_dir / "__init__.py").read_text(encoding="utf-8-sig"))
            all_info = find_all_assignment(source)
            existing_all = all_info[0] if all_info else set()
            orphans = get_orphan_modules(pkg_dir, existing_all)
            if orphans:
                print(f"  WOULD FIX {pkg_dotted}: +{len(orphans)} orphans")
                for _, mod_name in orphans:
                    names = extract_public_names(pkg_dir / f"{mod_name}.py")
                    print(f"    - {mod_name} -> {names if names else '(no public names)'}")
            continue

        fixed, skipped, used_imports = fix_package(pkg_dir, no_imports=args.no_imports)
        if fixed > 0:
            total_fixed += 1
            total_orphans += fixed
            if used_imports:
                total_with_imports += 1
            print(
                f"  FIXED {pkg_dotted}: +{fixed} orphans {'(with imports)' if used_imports else '(module names only)'}"
            )
        for s in skipped:
            all_skipped.append(s)

    print("\n=== SUMMARY ===")
    print(f"Packages fixed: {total_fixed}")
    print(f"Orphans fixed: {total_orphans}")
    print(f"With imports: {total_with_imports}")
    print(f"Module names only: {total_fixed - total_with_imports}")
    if all_skipped:
        print(f"Skipped/Warnings: {len(all_skipped)}")
        for s in all_skipped:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
