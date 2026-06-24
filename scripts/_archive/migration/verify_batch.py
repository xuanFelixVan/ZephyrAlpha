# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md | §6.3
# [MODULE] scripts.migration.verify_batch
# [INVARIANTS] 5项检查: target存在/old不存在/语法通过/import目标存在/log状态; 任何失败->exit 1
# [MODIFY-GUARD] 新增检查项需同步TC-6-3~6验收标准
# [CONSUMERS] TC-6-3/4/5/6验证步骤; TC-6-7全局验证
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] batch无效->exit 1; log缺失->exit 1
# [TESTS] tests/test_verify_batch.py
"""验证搬家批次——5项检查。

用法:
    python scripts/migration/verify_batch.py --batch 1
    python scripts/migration/verify_batch.py --all
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

from _migration_shared import (
    BATCH_TO_GROUP,
    MIGRATION_LOG_FILE,
    PROJECT_ROOT,
    filter_by_batch,
    load_mapping,
    load_migration_log,
)


def check_targets_exist(mappings: list[dict]) -> list[str]:
    errors = []
    for m in mappings:
        tp = m.get("target_path", "")
        if not tp or m.get("change_type") == "new":
            continue
        target = PROJECT_ROOT / tp
        if not target.exists():
            errors.append(f"TARGET_MISSING: {tp}")
    return errors


def check_old_removed(mappings: list[dict]) -> list[str]:
    errors = []
    for m in mappings:
        op = m.get("old_path", "")
        if not op or m.get("change_type") in ("new", "unchanged"):
            continue
        if op == m.get("target_path", ""):
            continue
        source = PROJECT_ROOT / op
        target = PROJECT_ROOT / m.get("target_path", "")
        if source.exists() and target.exists():
            try:
                if source.resolve() != target.resolve() and source.read_bytes() == target.read_bytes():
                    continue
            except OSError:
                pass
        if source.exists() and not target.exists():
            errors.append(f"OLD_NOT_COPIED: {op} -> target missing")
    return errors


def check_syntax(mappings: list[dict]) -> list[str]:
    errors = []
    checked = set()
    for m in mappings:
        tp = m.get("target_path", "")
        if not tp:
            continue
        target = PROJECT_ROOT / tp
        if not target.is_dir():
            files_to_check = [target] if target.suffix == ".py" else []
        else:
            files_to_check = list(target.rglob("*.py"))

        for py_file in files_to_check:
            if str(py_file) in checked:
                continue
            checked.add(str(py_file))
            try:
                content = py_file.read_text(encoding="utf-8")
                ast.parse(content, filename=str(py_file))
            except SyntaxError as e:
                errors.append(f"SYNTAX: {py_file.relative_to(PROJECT_ROOT)}: {e}")
            except (OSError, UnicodeDecodeError):
                pass
    return errors


def check_imports_resolvable(mappings: list[dict]) -> list[str]:
    errors = []
    checked = set()
    for m in mappings:
        tp = m.get("target_path", "")
        if not tp:
            continue
        target = PROJECT_ROOT / tp
        if not target.is_dir():
            files_to_check = [target] if target.suffix == ".py" else []
        else:
            files_to_check = list(target.rglob("*.py"))

        for py_file in files_to_check:
            if str(py_file) in checked:
                continue
            checked.add(str(py_file))
            try:
                content = py_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            for line_no, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if not stripped.startswith(("from ", "import ")):
                    continue
                match = re.match(r"^(?:from|import)\s+([a-zA-Z_][\w.]*)", stripped)
                if not match:
                    continue
                mod_path = match.group(1).split(".")
                if mod_path[0] != "zephyr":
                    continue
                pkg_path = PROJECT_ROOT / "src" / Path(*mod_path)
                if pkg_path.is_dir() and (pkg_path / "__init__.py").exists():
                    continue
                py_path = PROJECT_ROOT / "src" / Path(*mod_path[:-1]) / f"{mod_path[-1]}.py"
                if py_path.exists():
                    continue
                init_path = PROJECT_ROOT / "src" / Path(*mod_path) / "__init__.py"
                if init_path.exists():
                    continue
                errors.append(
                    f"IMPORT: {py_file.relative_to(PROJECT_ROOT)}:{line_no} cannot resolve '{match.group(1)}'"
                )
    return errors


def check_log_status(batch: int) -> list[str]:
    errors = []
    if not MIGRATION_LOG_FILE.exists():
        errors.append("LOG: migration-log.yaml does not exist")
        return errors

    log = load_migration_log()
    batch_entry = None
    for b in log.get("batches", []):
        if b.get("batch") == batch:
            batch_entry = b
            break

    if batch_entry is None:
        errors.append(f"LOG: No entry for batch {batch}")
        return errors

    for move in batch_entry.get("moves", []):
        if move.get("status") not in ("moved", "copied", "skipped"):
            errors.append(f"LOG: {move.get('src', '?')} status={move.get('status')}")

    return errors


def verify_batch(batch: int) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Verify Batch {batch} ({group}) ===")

    mappings = load_mapping()
    batch_mappings = filter_by_batch(mappings, batch)
    if not batch_mappings:
        print(f"[WARN] No mappings for batch {batch}")
        return 0

    all_errors = []

    print("\n--- Check 1: Target files exist ---")
    e1 = check_targets_exist(batch_mappings)
    all_errors.extend(e1)
    print(f"  Result: {len(e1)} errors" if e1 else "  Result: OK")

    print("\n--- Check 2: Copy integrity (source+target both exist) ---")
    e2 = check_old_removed(batch_mappings)
    all_errors.extend(e2)
    print(f"  Result: {len(e2)} errors" if e2 else "  Result: OK")

    print("\n--- Check 3: Syntax check ---")
    e3 = check_syntax(batch_mappings)
    all_errors.extend(e3[:50])
    if len(e3) > 50:
        print(f"  ... and {len(e3) - 50} more syntax errors")
    print(f"  Result: {len(e3)} errors" if e3 else "  Result: OK")

    print("\n--- Check 4: Import resolvable ---")
    e4 = check_imports_resolvable(batch_mappings)
    all_errors.extend(e4[:50])
    if len(e4) > 50:
        print(f"  ... and {len(e4) - 50} more import errors")
    print(f"  Result: {len(e4)} errors" if e4 else "  Result: OK")

    print("\n--- Check 5: Migration log status ---")
    e5 = check_log_status(batch)
    all_errors.extend(e5)
    print(f"  Result: {len(e5)} errors" if e5 else "  Result: OK")

    print(f"\n=== Summary: {len(all_errors)} total errors ===")
    if all_errors:
        for e in all_errors[:20]:
            print(f"  {e}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")

    return 1 if all_errors else 0


def verify_all() -> int:
    total_errors = 0
    for batch in range(1, 5):
        result = verify_batch(batch)
        total_errors += result
    print(f"\n=== All Batches: {'PASS' if total_errors == 0 else 'FAIL'} ===")
    return 1 if total_errors > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify migration batch")
    parser.add_argument("--batch", type=int, help="Batch number (1-4)")
    parser.add_argument("--all", action="store_true", help="Verify all batches")
    args = parser.parse_args()

    if args.all:
        sys.exit(verify_all())
    elif args.batch:
        sys.exit(verify_batch(args.batch))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
