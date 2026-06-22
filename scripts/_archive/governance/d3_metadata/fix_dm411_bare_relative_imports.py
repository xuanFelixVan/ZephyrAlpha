"""
DM-411: Fix bare relative imports (from module_name import X -> from .module_name import X)

Bare relative imports fail when importlib resolves them from outside the package,
causing pytest collection errors. This script converts them to standard relative imports.
"""

from __future__ import annotations

import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SRC_ROOT = Path("src/zephyr")


def get_package_modules(package_dir: Path) -> set[str]:
    """Get all module names in a package directory (without .py extension)."""
    names = set()
    if not package_dir.is_dir():
        return names
    for entry in package_dir.iterdir():
        if entry.is_file() and entry.suffix == ".py" and entry.name != "__init__.py":
            names.add(entry.stem)
        elif entry.is_dir() and (entry / "__init__.py").exists():
            names.add(entry.name)
    return names


def scan_file(filepath: Path) -> tuple[int, list[str]]:
    """Scan a file for bare relative imports. Returns (changes_count, change_descriptions)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return 0, []

    package_dir = filepath.parent
    sibling_modules = get_package_modules(package_dir)
    if not sibling_modules:
        return 0, []

    changes = 0
    descriptions = []
    lines = content.split("\n")

    for line_no, line in enumerate(lines, 1):
        m = re.match(r"^(\s*)from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import\s+(.+)$", line)
        if m:
            indent = m.group(1)
            module_name = m.group(2)
            import_list = m.group(3)
            if module_name in sibling_modules:
                changes += 1
                descriptions.append(f"  L{line_no}: from {module_name} import → from .{module_name} import")

    return changes, descriptions


def fix_file(filepath: Path) -> tuple[int, list[str]]:
    """Fix bare relative imports in a single file. Returns (changes_count, change_descriptions)."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return 0, []

    package_dir = filepath.parent
    sibling_modules = get_package_modules(package_dir)
    if not sibling_modules:
        return 0, []

    changes = 0
    descriptions = []
    lines = content.split("\n")
    new_lines = []

    for line_no, line in enumerate(lines, 1):
        m = re.match(r"^(\s*)from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import\s+(.+)$", line)
        if m:
            indent = m.group(1)
            module_name = m.group(2)
            import_list = m.group(3)
            if module_name in sibling_modules:
                new_line = f"{indent}from .{module_name} import {import_list}"
                new_lines.append(new_line)
                changes += 1
                descriptions.append(f"  L{line_no}: from {module_name} → from .{module_name}")
                continue
        new_lines.append(line)

    if changes > 0:
        new_content = "\n".join(new_lines)
        tmp_path = filepath.with_suffix(".py.tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            os.replace(tmp_path, filepath)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return 0, [f"  PermissionError writing {filepath}"]

    return changes, descriptions


def main():
    apply_mode = "--apply" in sys.argv

    print(f"{'APPLY' if apply_mode else 'DRY RUN'} MODE")
    print(f"Scanning {SRC_ROOT} for bare relative imports...")

    py_files = list(SRC_ROOT.rglob("*.py"))
    print(f"Found {len(py_files)} .py files")

    total_changes = 0
    total_files = 0
    all_descriptions = []

    func = fix_file if apply_mode else scan_file

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(func, fp): fp for fp in py_files}
        for future in as_completed(futures):
            fp = futures[future]
            try:
                changes, descriptions = future.result()
                if changes > 0:
                    total_changes += changes
                    total_files += 1
                    if descriptions:
                        all_descriptions.append(f"{fp}:")
                        all_descriptions.extend(descriptions)
            except Exception as e:
                all_descriptions.append(f"{fp}: ERROR {e}")

    action = "Fixed" if apply_mode else "Would fix"
    print(f"\n{action}: {total_changes} imports in {total_files} files")

    if all_descriptions and total_files <= 50:
        print("\nDetails:")
        for d in all_descriptions:
            print(d)
    elif all_descriptions:
        print(f"\n(Too many to list, showing first 100 of {len(all_descriptions)})")
        for d in all_descriptions[:100]:
            print(d)


if __name__ == "__main__":
    main()
