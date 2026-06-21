# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.3
# [MODULE] scripts.migration.update_non_import_refs
# [INVARIANTS] 扫描蓝图头部/注册表/YAML/__init__.py中的旧路径引用并替换
# [MODIFY-GUARD] 新增引用类型需同步TC-6-3~6验收标准
# [CONSUMERS] TC-6-3/4/5/6非import引用更新步骤
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] batch无效->exit 1; 文件写入失败->记录继续
# [TESTS] tests/test_update_non_import_refs.py
"""更新非 import 引用——蓝图头部/注册表/YAML/__init__.py。

用法:
    python scripts/migration/update_non_import_refs.py --batch 1
    python scripts/migration/update_non_import_refs.py --batch 1 --dry-run
    python scripts/migration/update_non_import_refs.py --all
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from _migration_shared import (
    BATCH_TO_GROUP,
    PROJECT_ROOT,
    filter_by_batch,
    load_mapping,
    atomic_write,
)


def _build_replacement_map(batch_mappings: list[dict]) -> list[tuple[str, str]]:
    replacements = []
    for m in batch_mappings:
        op = m.get("old_path", "")
        tp = m.get("target_path", "")
        if not op or not tp or op == tp:
            continue
        replacements.append((op, tp))
        op_dot = op.replace("/", ".").replace("\\", ".").rstrip(".")
        tp_dot = tp.replace("/", ".").replace("\\", ".").rstrip(".")
        if op_dot != op:
            replacements.append((op_dot, tp_dot))
    replacements.sort(key=lambda x: len(x[0]), reverse=True)
    return replacements


def _apply_replacements_to_file(filepath: Path, replacements: list[tuple[str, str]], dry_run: bool = False) -> dict:
    if not filepath.exists():
        return {"file": str(filepath), "status": "missing", "changes": 0}

    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {"file": str(filepath), "status": "skip_binary", "changes": 0}

    original = content
    total_changes = 0

    for old, new in replacements:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            total_changes += count

    if total_changes == 0:
        return {"file": str(filepath), "status": "no_change", "changes": 0}

    if dry_run:
        return {"file": str(filepath), "status": "would_update", "changes": total_changes}

    try:
        tmp_path = f"{filepath}.{os.getpid()}.tmp"
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, filepath)
        return {"file": str(filepath), "status": "updated", "changes": total_changes}
    except (PermissionError, OSError):
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return {"file": str(filepath), "status": "write_error", "changes": 0}


def _scan_blueprint_headers(replacements: list[tuple[str, str]], dry_run: bool = False) -> dict:
    print("  Scanning blueprint headers [BLUEPRINT]...")
    results = {"scanned": 0, "updated": 0, "changes": 0}
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if ".ailocks" in str(py_file) or "__pycache__" in str(py_file):
            continue
        try:
            first_lines = ""
            with open(py_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    first_lines += line
            if "[BLUEPRINT]" not in first_lines:
                continue
            results["scanned"] += 1
            r = _apply_replacements_to_file(py_file, replacements, dry_run)
            if r["status"] in ("updated", "would_update"):
                results["updated"] += 1
                results["changes"] += r["changes"]
        except (OSError, UnicodeDecodeError):
            continue
    return results


def _scan_manifest_yaml(replacements: list[tuple[str, str]], dry_run: bool = False) -> dict:
    print("  Scanning script_manifest.yaml...")
    results = {"scanned": 0, "updated": 0, "changes": 0}
    manifest = PROJECT_ROOT / "scripts" / "script_manifest.yaml"
    if not manifest.exists():
        return results
    results["scanned"] = 1
    r = _apply_replacements_to_file(manifest, replacements, dry_run)
    if r["status"] in ("updated", "would_update"):
        results["updated"] = 1
        results["changes"] += r["changes"]
    return results


def _scan_init_files(replacements: list[tuple[str, str]], batch_mappings: list[dict], dry_run: bool = False) -> dict:
    print("  Scanning __init__.py files...")
    results = {"scanned": 0, "updated": 0, "changes": 0}
    domains = set(m.get("domain", "") for m in batch_mappings if m.get("domain"))
    for py_file in PROJECT_ROOT.rglob("__init__.py"):
        if ".ailocks" in str(py_file) or "__pycache__" in str(py_file):
            continue
        results["scanned"] += 1
        r = _apply_replacements_to_file(py_file, replacements, dry_run)
        if r["status"] in ("updated", "would_update"):
            results["updated"] += 1
            results["changes"] += r["changes"]
    return results


def _scan_config_yaml(replacements: list[tuple[str, str]], dry_run: bool = False) -> dict:
    print("  Scanning config YAML files...")
    results = {"scanned": 0, "updated": 0, "changes": 0}
    config_dir = PROJECT_ROOT / "config"
    if not config_dir.exists():
        return results
    for yml_file in config_dir.rglob("*.yaml"):
        results["scanned"] += 1
        r = _apply_replacements_to_file(yml_file, replacements, dry_run)
        if r["status"] in ("updated", "would_update"):
            results["updated"] += 1
            results["changes"] += r["changes"]
    for yml_file in config_dir.rglob("*.yml"):
        results["scanned"] += 1
        r = _apply_replacements_to_file(yml_file, replacements, dry_run)
        if r["status"] in ("updated", "would_update"):
            results["updated"] += 1
            results["changes"] += r["changes"]
    return results


def update_batch(batch: int, dry_run: bool = False) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Update Non-Import Refs: Batch {batch} ({group}) ===")
    if dry_run:
        print("(dry-run mode)")

    mappings = load_mapping()
    batch_mappings = filter_by_batch(mappings, batch)
    if not batch_mappings:
        print("No mappings for this batch.")
        return 0

    replacements = _build_replacement_map(batch_mappings)
    print(f"Replacement patterns: {len(replacements)}")

    total_updated = 0
    total_changes = 0

    r1 = _scan_blueprint_headers(replacements, dry_run)
    print(f"    Blueprint headers: scanned={r1['scanned']}, updated={r1['updated']}, changes={r1['changes']}")
    total_updated += r1["updated"]
    total_changes += r1["changes"]

    r2 = _scan_manifest_yaml(replacements, dry_run)
    print(f"    Manifest YAML: scanned={r2['scanned']}, updated={r2['updated']}, changes={r2['changes']}")
    total_updated += r2["updated"]
    total_changes += r2["changes"]

    r3 = _scan_init_files(replacements, batch_mappings, dry_run)
    print(f"    __init__.py: scanned={r3['scanned']}, updated={r3['updated']}, changes={r3['changes']}")
    total_updated += r3["updated"]
    total_changes += r3["changes"]

    r4 = _scan_config_yaml(replacements, dry_run)
    print(f"    Config YAML: scanned={r4['scanned']}, updated={r4['updated']}, changes={r4['changes']}")
    total_updated += r4["updated"]
    total_changes += r4["changes"]

    print(f"\n=== Results ===")
    print(f"  Files updated: {total_updated}")
    print(f"  Total changes: {total_changes}")

    return 0


def update_all(dry_run: bool = False) -> int:
    errors = 0
    for batch in range(1, 5):
        errors += update_batch(batch, dry_run)
    return 1 if errors > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Update non-import references for migration batch")
    parser.add_argument("--batch", type=int, help="Batch number (1-4)")
    parser.add_argument("--all", action="store_true", help="Update refs for all batches")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual changes")
    args = parser.parse_args()

    if args.all:
        sys.exit(update_all(args.dry_run))
    elif args.batch:
        sys.exit(update_batch(args.batch, args.dry_run))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
