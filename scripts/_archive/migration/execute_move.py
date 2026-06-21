# [BLUEPRINT] MOD-INF-037 | docs/02_enterprise_architecture/domain-model-migration-plan.md | §6.8
# [MODULE] scripts.migration.execute_move
# [INVARIANTS] 按文件逐个复制(非目录级移动); 复制到新位置旧文件暂不删除; 每步记录migration_log; 失败不中断; 排除scripts/migration/和data/asset_index/
# [MODIFY-GUARD] log格式变更需同步rollback_batch.py
# [CONSUMERS] TC-6-3/4/5/6搬家步骤
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] batch无效->exit 1; mapping缺失->exit 1; 源文件缺失->记录失败继续
# [TESTS] tests/test_execute_move.py
"""批量文件复制——搬家核心引擎（文件级，复制模式）。

策略: 从 path-migration-mapping.yaml 读取文件级映射，逐文件复制到新位置。
旧文件暂不删除（由后续 cleanup 步骤统一处理）。
每个文件用 shutil.copy2 保留元数据，目标目录自动创建。

用法:
    python scripts/migration/execute_move.py --batch 1 --dry-run
    python scripts/migration/execute_move.py --batch 1
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from _migration_shared import (
    BATCH_TO_GROUP,
    PROJECT_ROOT,
    MIGRATION_LOG_FILE,
    filter_by_batch,
    load_mapping,
    load_migration_log,
    save_migration_log,
)

EXCLUDED_PREFIXES = [
    "scripts/migration/",
    "scripts\\migration\\",
    "data/asset_index/",
    "data\\asset_index\\",
]


def _is_excluded(path: str) -> bool:
    for prefix in EXCLUDED_PREFIXES:
        if prefix in path:
            return True
    return False


def _build_file_copy_plan(batch_mappings: list[dict]) -> list[dict]:
    plan: list[dict] = []
    seen_targets: set[str] = set()

    for m in batch_mappings:
        op = m.get("old_path", "")
        tp = m.get("target_path", "")
        change_type = m.get("change_type", "")

        if not op or not tp:
            continue
        if change_type == "unchanged":
            continue
        if change_type == "new":
            continue
        if _is_excluded(op):
            continue

        source = PROJECT_ROOT / op
        target = PROJECT_ROOT / tp

        if not source.exists():
            continue
        if not source.is_file():
            continue

        target_key = str(target)
        if target_key in seen_targets:
            continue
        seen_targets.add(target_key)

        plan.append({
            "src": str(source),
            "dst": str(target),
            "domain": m.get("domain", ""),
            "module_id": m.get("module_id", ""),
            "module_name": m.get("module_name", ""),
        })

    return plan


def _copy_single_file(src_str: str, dst_str: str) -> dict:
    source = Path(src_str)
    target = Path(dst_str)

    if not source.exists():
        return {"src": src_str, "dst": dst_str, "status": "failed", "reason": "source_missing"}

    if not source.is_file():
        return {"src": src_str, "dst": dst_str, "status": "skipped", "reason": "not_a_file"}

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        if source.resolve() == target.resolve():
            return {"src": src_str, "dst": dst_str, "status": "skipped", "reason": "same_path"}
        try:
            if target.stat().st_size == source.stat().st_size:
                if target.read_bytes() == source.read_bytes():
                    return {"src": src_str, "dst": dst_str, "status": "skipped", "reason": "already_exists_same_content"}
        except OSError:
            pass

    try:
        shutil.copy2(str(source), str(target))
        return {"src": src_str, "dst": dst_str, "status": "copied", "reason": ""}
    except OSError as e:
        return {"src": src_str, "dst": dst_str, "status": "failed", "reason": str(e)}


def execute_batch(batch: int, dry_run: bool = False) -> int:
    group = BATCH_TO_GROUP.get(batch, "unknown")
    print(f"=== Execute Move: Batch {batch} ({group}) ===")
    if dry_run:
        print("(dry-run mode — no files will be copied)")

    mappings = load_mapping()
    batch_mappings = filter_by_batch(mappings, batch)
    if not batch_mappings:
        print(f"[WARN] No mappings for batch {batch}")
        return 0

    plan = _build_file_copy_plan(batch_mappings)
    print(f"File copy plan: {len(plan)} files")

    if dry_run:
        domains_in_plan: dict[str, int] = {}
        for p in plan:
            d = p.get("domain", "unknown")
            domains_in_plan[d] = domains_in_plan.get(d, 0) + 1
        for d, c in sorted(domains_in_plan.items()):
            print(f"  {d}: {c} files")
        print(f"\nSample copies:")
        for p in plan[:10]:
            rel_src = Path(p["src"]).relative_to(PROJECT_ROOT) if p["src"].startswith(str(PROJECT_ROOT)) else p["src"]
            rel_dst = Path(p["dst"]).relative_to(PROJECT_ROOT) if p["dst"].startswith(str(PROJECT_ROOT)) else p["dst"]
            print(f"  {rel_src} -> {rel_dst}")
        if len(plan) > 10:
            print(f"  ... and {len(plan) - 10} more")
        return 0

    log = load_migration_log()

    batch_entry = None
    for b in log.get("batches", []):
        if b.get("batch") == batch:
            batch_entry = b
            break

    if batch_entry is None:
        batch_entry = {
            "batch": batch,
            "domain_group": group,
            "started_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "in_progress",
            "mode": "copy",
            "moves": [],
        }
        log.setdefault("batches", []).append(batch_entry)

    success = 0
    failed = 0
    skipped = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for p in plan:
            futures[executor.submit(_copy_single_file, p["src"], p["dst"])] = p

        for future in as_completed(futures):
            result = future.result()
            p = futures[future]
            move_record = {
                "src": result["src"],
                "dst": result["dst"],
                "status": result["status"],
                "reason": result.get("reason", ""),
                "domain": p.get("domain", ""),
                "module_id": p.get("module_id", ""),
                "verified": False,
            }
            batch_entry["moves"].append(move_record)

            if result["status"] == "copied":
                success += 1
            elif result["status"] == "skipped":
                skipped += 1
            else:
                failed += 1
                rel_src = Path(result["src"]).relative_to(PROJECT_ROOT) if result["src"].startswith(str(PROJECT_ROOT)) else result["src"]
                print(f"  FAILED: {rel_src} ({result.get('reason', '')})")

    batch_entry["completed_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    batch_entry["stats"] = {"success": success, "failed": failed, "skipped": skipped}

    if failed > 0:
        batch_entry["status"] = "partial"
    else:
        batch_entry["status"] = "copied"

    save_migration_log(log)

    print(f"\n=== Results ===")
    print(f"  Copied:  {success}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Log: {MIGRATION_LOG_FILE}")

    return 1 if failed > 0 else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute file copies for migration batch")
    parser.add_argument("--batch", type=int, required=True, help="Batch number (1-4)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run — no actual copies")
    args = parser.parse_args()
    sys.exit(execute_batch(args.batch, args.dry_run))


if __name__ == "__main__":
    main()
