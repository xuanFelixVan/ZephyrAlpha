# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md | §6.3
# [MODULE] scripts.migration.create_target_dirs
# [INVARIANTS] 只创建目录不移动文件; os.makedirs(exist_ok=True); 幂等
# [MODIFY-GUARD] 目录结构变更需同步project-path-tree.yaml
# [CONSUMERS] TC-6-2创建目录步骤
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] batch无效->exit 1; mapping文件缺失->exit 1
# [TESTS] tests/test_create_target_dirs.py
"""创建30域目标目录结构。

用法:
    python scripts/migration/create_target_dirs.py --batch 1
    python scripts/migration/create_target_dirs.py --all
"""

from __future__ import annotations

import argparse
import sys

from _migration_shared import (
    BATCH_TO_GROUP,
    PATH_TREE_FILE,
    PROJECT_ROOT,
    filter_by_batch,
    load_mapping,
    load_yaml,
)


def create_dirs_for_batch(batch: int) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Create Target Dirs: Batch {batch} ({group}) ===")

    mappings = load_mapping()
    batch_mappings = filter_by_batch(mappings, batch)

    dirs_created = 0
    dirs_existing = 0

    for m in batch_mappings:
        tp = m.get("target_path", "")
        if not tp:
            continue
        target = PROJECT_ROOT / tp
        if target.is_dir():
            dirs_existing += 1
            continue
        parent = target.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
            dirs_created += 1
            print(f"  CREATED: {parent}")

    print(f"Directories created: {dirs_created}, already existing: {dirs_existing}")
    return dirs_created


def create_dirs_for_all() -> int:
    total = 0
    for batch in range(1, 5):
        total += create_dirs_for_batch(batch)
    return total


def create_domain_root_dirs() -> int:
    print("\n=== Create Domain Root Dirs ===")
    if not PATH_TREE_FILE.exists():
        print("[WARN] project-path-tree.yaml not found, skipping domain root dirs")
        return 0

    pt = load_yaml(PATH_TREE_FILE)
    domains_raw = pt.get("domains", [])
    if not domains_raw:
        domains_by_group = pt.get("domains_by_group", {})
        for gk, gd in domains_by_group.items():
            if isinstance(gd, list):
                domains_raw.extend(gd)

    created = 0
    for d in domains_raw:
        td = d.get("target_directory", "")
        if not td:
            continue
        target = PROJECT_ROOT / td
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created += 1
            print(f"  CREATED: {td}")

    print(f"Domain root dirs created: {created}")
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Create target directory structure for migration")
    parser.add_argument("--batch", type=int, help="Batch number (1-4)")
    parser.add_argument("--all", action="store_true", help="Create dirs for all batches")
    args = parser.parse_args()

    if args.all:
        create_domain_root_dirs()
        create_dirs_for_all()
    elif args.batch:
        create_domain_root_dirs()
        create_dirs_for_batch(args.batch)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
