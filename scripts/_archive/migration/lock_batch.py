# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.3
# [MODULE] scripts.migration.lock_batch
# [INVARIANTS] 验证log中所有moves的verified/状态; 锁定后禁止回滚
# [MODIFY-GUARD] log格式变更需同步rollback_batch.py
# [CONSUMERS] TC-6-3/4/5/6锁定步骤
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] batch无效->exit 1; log缺失->exit 1; 有未验证move->exit 1
# [TESTS] tests/test_lock_batch.py
"""锁定搬家批次——验证通过后禁止回滚。

用法:
    python scripts/migration/lock_batch.py --batch 1
    python scripts/migration/lock_batch.py --batch 1 --dry-run
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime

from _migration_shared import (
    BATCH_TO_GROUP,
    MIGRATION_LOG_FILE,
    load_migration_log,
    save_migration_log,
)


def lock_batch(batch: int, dry_run: bool = False) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Lock Batch {batch} ({group}) ===")
    if dry_run:
        print("(dry-run mode — no actual lock)")

    if not MIGRATION_LOG_FILE.exists():
        print("[ERROR] migration-log.yaml does not exist. Cannot lock.")
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
        print(f"[INFO] Batch {batch} is already locked.")
        return 0

    moves = batch_entry.get("moves", [])
    unverified = [m for m in moves if m.get("status") not in ("moved", "skipped")]
    if unverified:
        print(f"[ERROR] Batch {batch} has {len(unverified)} unverified/failed moves:")
        for m in unverified[:10]:
            print(f"  {m.get('src', '?')} -> {m.get('dst', '?')} status={m.get('status')}")
        return 1

    for move in moves:
        move["verified"] = True

    batch_entry["status"] = "completed_locked"
    batch_entry["locked_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    stats = batch_entry.get("stats", {})
    print(f"Moves verified: {len(moves)}")
    print(f"Stats: {stats.get('success', 0)} success, {stats.get('failed', 0)} failed, {stats.get('skipped', 0)} skipped")

    if not dry_run:
        save_migration_log(log)
        print(f"Batch {batch} LOCKED. Rollback is now disabled.")
    else:
        print(f"Would lock batch {batch}.")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Lock migration batch after verification")
    parser.add_argument("--batch", type=int, required=True, help="Batch number (1-4)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual lock")
    args = parser.parse_args()
    sys.exit(lock_batch(args.batch, args.dry_run))


if __name__ == "__main__":
    main()
