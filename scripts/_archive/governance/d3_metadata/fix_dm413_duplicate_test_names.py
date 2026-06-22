"""
DM-413: Fix duplicate test file names (N-16 violations)

Renames test files to include directory-level suffix for uniqueness:
  tests/test_xxx.py → tests/test_xxx_root.py
  tests/{dir}/test_xxx.py → tests/{dir}/test_xxx_{dir}.py
  tests/{dir1}/{dir2}/test_xxx.py → tests/{dir1}/{dir2}/test_xxx_{dir2}.py

Exempt: conftest.py, __init__.py
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

TESTS_ROOT = Path("tests")
_N16_EXEMPT = {"conftest.py", "__init__.py"}


def find_duplicates() -> dict[str, list[Path]]:
    """Find all duplicate test file names."""
    name_to_paths: dict[str, list[Path]] = defaultdict(list)
    for py_file in TESTS_ROOT.rglob("*.py"):
        basename = py_file.name
        if basename in _N16_EXEMPT:
            continue
        if not basename.startswith("test_"):
            continue
        name_to_paths[basename].append(py_file)
    return {k: v for k, v in name_to_paths.items() if len(v) > 1}


def compute_new_name(filepath: Path) -> str:
    """Compute new filename with directory suffix for uniqueness."""
    basename = filepath.name
    stem = filepath.stem  # e.g., test_circuit_breaker
    ext = filepath.suffix  # .py

    # Get the nearest parent directory name (under tests/)
    rel = filepath.relative_to(TESTS_ROOT)
    parts = rel.parts  # e.g., ('unit', 'resilience', 'test_circuit_breaker.py')

    if len(parts) == 1:
        # Directly under tests/ → add _root suffix
        return f"{stem}_root{ext}"
    else:
        # Use the immediate parent directory name as suffix
        parent_dir = parts[-2]  # e.g., 'resilience'
        # Avoid redundant suffix (if stem already contains the dir name)
        if parent_dir in stem:
            return basename  # No rename needed
        return f"{stem}_{parent_dir}{ext}"


def rename_file(filepath: Path, new_name: str) -> tuple[bool, str]:
    """Rename a single file. Returns (success, message)."""
    if new_name == filepath.name:
        return True, f"SKIP (already unique): {filepath}"

    new_path = filepath.parent / new_name

    # Check if new path already exists
    if new_path.exists():
        return False, f"CONFLICT: {new_path} already exists, skipping {filepath}"

    try:
        os.rename(filepath, new_path)
        return True, f"OK: {filepath} → {new_name}"
    except Exception as e:
        return False, f"ERROR: {filepath} → {new_name}: {e}"


def update_module_id(filepath: Path, new_name: str) -> None:
    """Update [A_test] module_id and [MODULE] header in the renamed file."""
    new_path = filepath.parent / new_name
    if not new_path.exists():
        return

    try:
        with open(new_path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return

    new_stem = new_name.replace(".py", "")
    old_stem = filepath.name.replace(".py", "")

    # Update module_id in [A_test] header
    content = re.sub(r"(module_id=T-[A-Z]+_)" + re.escape(old_stem), r"\g<1>" + new_stem, content)

    # Update [MODULE] line
    old_module = old_stem.replace("_", ".")
    new_module = new_stem.replace("_", ".")
    content = content.replace(f"[MODULE] tests.{old_module}", f"[MODULE] tests.{new_module}")

    # Update [TESTS] line
    content = content.replace(f"[TESTS] {filepath}", f"[TESTS] {new_path}")
    content = content.replace(f"[TESTS] tests/{old_stem}.py", f"[TESTS] tests/{new_stem}.py")

    # Atomic write
    tmp_path = new_path.with_suffix(".py.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, new_path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def main():
    apply_mode = "--apply" in sys.argv
    print(f"{'APPLY' if apply_mode else 'DRY RUN'} MODE")

    duplicates = find_duplicates()
    print(f"Found {len(duplicates)} groups of duplicate test names")

    # Compute all renames
    renames: list[tuple[Path, str]] = []
    for basename, paths in sorted(duplicates.items()):
        for filepath in paths:
            new_name = compute_new_name(filepath)
            renames.append((filepath, new_name))

    # Check for new conflicts after rename
    new_name_counts: dict[str, list[int]] = defaultdict(list)
    for i, (_, new_name) in enumerate(renames):
        new_name_counts[new_name].append(i)

    still_conflicted = {k: v for k, v in new_name_counts.items() if len(v) > 1}
    if still_conflicted:
        print(f"\nWARNING: {len(still_conflicted)} names still have conflicts after first pass:")
        for name, indices in still_conflicted.items():
            print(f"  {name}: {len(indices)} files")
        # For still-conflicted names, use full directory path as suffix
        for name, indices in still_conflicted.items():
            for idx in indices:
                filepath = renames[idx][0]
                rel = filepath.relative_to(TESTS_ROOT)
                dir_parts = rel.parts[:-1]  # all directory parts
                # Build suffix from full directory path
                suffix = "_".join(dir_parts) if dir_parts else "root"
                stem = filepath.stem
                renames[idx] = (filepath, f"{stem}_{suffix}.py")

        # Re-check after second pass
        new_name_counts2: dict[str, int] = defaultdict(int)
        for _, new_name in renames:
            new_name_counts2[new_name] += 1
        still2 = {k: v for k, v in new_name_counts2.items() if v > 1}
        if still2:
            print(f"\nSTILL CONFLICTED after 2nd pass: {len(still2)}")
            for name, cnt in still2.items():
                print(f"  {name}: {cnt} files — will need manual resolution")

    if not apply_mode:
        print(f"\nWould rename {sum(1 for _, n in renames if n != _.name)} files:")
        for filepath, new_name in renames[:30]:
            if new_name != filepath.name:
                print(f"  {filepath} → {new_name}")
        if len(renames) > 30:
            print(f"  ... and {len(renames) - 30} more")
        return

    # Apply renames
    success = 0
    errors = 0
    skipped = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for filepath, new_name in renames:
            if new_name == filepath.name:
                skipped += 1
                continue
            futures[executor.submit(rename_file, filepath, new_name)] = (filepath, new_name)

        for future in as_completed(futures):
            filepath, new_name = futures[future]
            ok, msg = future.result()
            if ok:
                if "SKIP" in msg:
                    skipped += 1
                else:
                    success += 1
                    # Update module_id in the renamed file
                    update_module_id(filepath, new_name)
            else:
                errors += 1
            print(msg)

    print(f"\nDone: {success} renamed, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
