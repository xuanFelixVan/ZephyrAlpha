# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.3
# [MODULE] scripts.migration.rollback_batch
# [INVARIANTS] 反向遍历migration_log搬回原路径; 回滚import更新; 原子操作
# [MODIFY-GUARD] log格式变更需同步execute_move.py
# [CONSUMERS] TC-6-3/4/5/6回滚步骤
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] batch无效->exit 1; log缺失->exit 1; 已锁定批次->exit 2
# [TESTS] tests/test_rollback_batch.py
"""回滚搬家批次——从 migration-log 反向搬回。

用法:
    python scripts/migration/rollback_batch.py --batch 1
    python scripts/migration/rollback_batch.py --batch 1 --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from _migration_shared import (
    BATCH_TO_GROUP,
    PROJECT_ROOT,
    MIGRATION_LOG_FILE,
    load_migration_log,
    save_migration_log,
)


def rollback_batch(batch: int, dry_run: bool = False) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Rollback Batch {batch} ({group}) ===")
    if dry_run:
        print("(dry-run mode — no actual rollback)")

    if not MIGRATION_LOG_FILE.exists():
        print("[ERROR] migration-log.yaml does not exist. Cannot rollback.")
        return 1

    log = load_migration_log()

    batch_entry = None
    for b in log.get("batches", []):
        if b.get("batch") == batch:
            batch_entry = b
            break

    if batch_entry is None:
        print(f"[ERROR] No log entry for batch {batch}")
        return 1

    if batch_entry.get("status") == "completed_locked":
        print(f"[ERROR] Batch {batch} is LOCKED. Cannot rollback.")
        return 2

    moves = batch_entry.get("moves", [])
    if not moves:
        print(f"[WARN] No moves recorded for batch {batch}")
        return 0

    print(f"Moves to rollback: {len(moves)}")

    success = 0
    failed = 0
    skipped = 0

    for move in reversed(moves):
        src = move.get("src", "")
        dst = move.get("dst", "")
        status = move.get("status", "")

        if status != "moved":
            skipped += 1
            continue

        dst_path = PROJECT_ROOT / dst
        src_path = PROJECT_ROOT / src

        if not dst_path.exists():
            print(f"  SKIP: {dst} does not exist (already rolled back?)")
            skipped += 1
            continue

        if dry_run:
            print(f"  WOULD ROLLBACK: {dst} -> {src}")
            success += 1
            continue

        try:
            src_path.parent.mkdir(parents=True, exist_ok=True)
            if dst_path.is_dir():
                import shutil
                if src_path.exists():
                    shutil.rmtree(str(src_path))
                shutil.move(str(dst_path), str(src_path))
            else:
                os.replace(str(dst_path), str(src_path))
            move["status"] = "rolled_back"
            success += 1
        except OSError as e:
            print(f"  FAILED: {dst} -> {src}: {e}")
            failed += 1

    batch_entry["status"] = "rolled_back"
    batch_entry["rolled_back_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    batch_entry["rollback_stats"] = {"success": success, "failed": failed, "skipped": skipped}

    if not dry_run:
        save_migration_log(log)

    print(f"\n=== Rollback Results ===")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")

    return 1 if failed > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Rollback migration batch")
    parser.add_argument("--batch", type=int, required=True, help="Batch number (1-4)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual rollback")
    args = parser.parse_args()
    sys.exit(rollback_batch(args.batch, args.dry_run))


if __name__ == "__main__":
    main()
