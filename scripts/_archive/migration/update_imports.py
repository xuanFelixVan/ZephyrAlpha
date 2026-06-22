# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.3
# [MODULE] scripts.migration.update_imports
# [INVARIANTS] 逐文件替换old->new import; 原子写入(RULE-ONE); 按批次筛选; 文件路径通过mapping解析
# [MODIFY-GUARD] import manifest格式变更需同步
# [CONSUMERS] TC-6-4 import更新步骤
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] batch无效->exit 1; manifest缺失->exit 1
# [TESTS] tests/test_update_imports.py
"""批量更新 import 引用。

文件路径解析策略:
  1. import manifest 中的 file 字段是旧架构路径
  2. 搬家后文件可能在新位置(target_path)
  3. 本脚本同时更新旧位置和新位置上的文件
  4. 旧位置文件存在则更新旧位置; 新位置文件存在则更新新位置

用法:
    python scripts/migration/update_imports.py --batch 1
    python scripts/migration/update_imports.py --batch 1 --dry-run
    python scripts/migration/update_imports.py --all
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from _migration_shared import (
    BATCH_TO_GROUP,
    PROJECT_ROOT,
    get_domain_dirs_for_batch,
    load_import_manifest,
    load_mapping,
)


def _build_path_resolver(mappings: list[dict]) -> dict[str, str]:
    old_to_new: dict[str, str] = {}
    new_to_old: dict[str, str] = {}
    for m in mappings:
        op = m.get("old_path", "")
        tp = m.get("target_path", "")
        if op and tp and op != tp:
            old_to_new[op] = tp
            new_to_old[tp] = op
    return {"old_to_new": old_to_new, "new_to_old": new_to_old}


def _resolve_filepath(filepath: str, resolver: dict) -> list[str]:
    paths_to_try = [filepath]
    old_to_new = resolver.get("old_to_new", {})
    new_to_old = resolver.get("new_to_old", {})

    if filepath in old_to_new:
        paths_to_try.append(old_to_new[filepath])
    if filepath in new_to_old:
        paths_to_try.append(new_to_old[filepath])

    parts = filepath.replace("\\", "/").split("/")
    for i in range(len(parts) - 1, 0, -1):
        prefix = "/".join(parts[:i]) + "/"
        for old_p, new_p in old_to_new.items():
            if old_p.startswith(prefix):
                suffix = filepath[len(old_p) :]
                candidate = new_p + suffix
                if candidate not in paths_to_try:
                    paths_to_try.append(candidate)

    return paths_to_try


def _update_file_imports(filepath: str, changes: list[dict], resolver: dict, dry_run: bool = False) -> dict:
    paths_to_try = _resolve_filepath(filepath, resolver)

    actual_path = None
    for p in paths_to_try:
        full = PROJECT_ROOT / p
        if full.exists() and full.is_file():
            actual_path = p
            break

    if actual_path is None:
        return {"file": filepath, "status": "missing", "changes_applied": 0}

    full_path = PROJECT_ROOT / actual_path

    try:
        content = full_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {"file": filepath, "status": "read_error", "changes_applied": 0, "reason": str(e)}

    applied = 0

    for change in changes:
        old = change.get("old", "")
        new = change.get("new", "")
        if not old or not new:
            continue
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            applied += count

    if applied == 0:
        return {"file": filepath, "status": "no_change", "changes_applied": 0}

    if dry_run:
        return {"file": filepath, "status": "would_update", "changes_applied": applied, "actual_path": actual_path}

    tmp_path = f"{full_path}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(content, encoding="utf-8")
        os.replace(tmp_path, full_path)
        return {"file": filepath, "status": "updated", "changes_applied": applied, "actual_path": actual_path}
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return {"file": filepath, "status": "write_error", "changes_applied": 0}
    except OSError as e:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return {"file": filepath, "status": "write_error", "changes_applied": 0, "reason": str(e)}


def update_batch(batch: int, dry_run: bool = False) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Update Imports: Batch {batch} ({group}) ===")
    if dry_run:
        print("(dry-run mode)")

    domain_dirs = get_domain_dirs_for_batch(batch)
    all_updates = load_import_manifest()
    mappings = load_mapping()
    resolver = _build_path_resolver(mappings)

    batch_updates = []

    for upd in all_updates:
        filepath = upd.get("file", "")
        changes = upd.get("changes", [])
        matched = False
        for change in changes:
            old = change.get("old", "")
            new = change.get("new", "")
            for dd in domain_dirs:
                if dd in old or dd in new:
                    matched = True
                    break
            if matched:
                break
        if not matched:
            fp_parts = filepath.replace("\\", "/")
            for dd in domain_dirs:
                if dd in fp_parts:
                    matched = True
                    break
        if not matched:
            paths = _resolve_filepath(filepath, resolver)
            for p in paths:
                p_parts = p.replace("\\", "/").split("/")
                for dd in domain_dirs:
                    if dd in p_parts:
                        matched = True
                        break
                if matched:
                    break
        if matched:
            batch_updates.append(upd)

    if not batch_updates:
        print("No import updates needed for this batch.")
        return 0

    print(f"Files to update: {len(batch_updates)}")

    total_updated = 0
    total_changes = 0
    total_errors = 0
    error_samples: list[str] = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for upd in batch_updates:
            filepath = upd.get("file", "")
            changes = upd.get("changes", [])
            futures[executor.submit(_update_file_imports, filepath, changes, resolver, dry_run)] = filepath

        for future in as_completed(futures):
            result = future.result()
            if result["status"] in ("updated", "would_update"):
                total_updated += 1
                total_changes += result["changes_applied"]
            elif result["status"] == "no_change":
                pass
            else:
                total_errors += 1
                if len(error_samples) < 10:
                    error_samples.append(f"  {result['file']} -> {result['status']}")

    print("\n=== Results ===")
    print(f"  Files updated: {total_updated}")
    print(f"  Import changes: {total_changes}")
    print(f"  Errors: {total_errors}")
    if error_samples:
        print("  Error samples:")
        for s in error_samples:
            print(s)

    return 1 if total_errors > 0 else 0


def update_all(dry_run: bool = False) -> int:
    errors = 0
    for batch in range(1, 5):
        errors += update_batch(batch, dry_run)
    return 1 if errors > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Update import references for migration batch")
    parser.add_argument("--batch", type=int, help="Batch number (1-4)")
    parser.add_argument("--all", action="store_true", help="Update imports for all batches")
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
