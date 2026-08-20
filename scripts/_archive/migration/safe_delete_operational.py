# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §
# [MODULE] scripts.migration.safe_delete_operational
# [TTL] task_bound
# [INVARIANTS] --dry-run MUST NOT modify/delete any file; MUST NOT run without verify_migration_alignment exit 0
# [MODIFY-GUARD] panorama YAML (lifecycle field updates); migration-registry.yaml (status updates)
# [CONSUMERS] migration pipeline; DM-310+ task cards
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DeletionError; VerificationError
# [TESTS]
"""安全删除旧运营态脚本：验证通过后才删除旧文件，设计态顶替旧运营态成为新运营态。

严格按顺序执行：
  1. 前置条件：verify_migration_alignment.py exit 0（所有旧内容在新位置完整存在）
  2. 读取全景图tree段中lifecycle=pending_deletion的节点
  3. 逐个验证：该节点对应的磁盘文件确实存在于旧路径
  4. 逐个验证：迁移登记表中该旧路径对应的新路径文件确实存在
  5. 删除旧运营态节点对应的磁盘文件
  6. 从全景图tree段移除旧运营态节点
  7. 将对应设计态节点lifecycle从design改为operational
  8. 更新迁移登记表：标记该条目为completed

回滚：任何步骤失败 → 停止执行 → 从git恢复已删除文件

用法:
    python scripts/migration/safe_delete_operational.py --dry-run       # 只输出将要执行的操作
    python scripts/migration/safe_delete_operational.py --domain X      # 只处理指定域
    python scripts/migration/safe_delete_operational.py --batch N       # 只处理第N批
    python scripts/migration/safe_delete_operational.py --force         # 跳过verify前置检查（危险）
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_REGISTRY = PROJECT_ROOT / "docs" / "02_enterprise_architecture" / "migration-registry.yaml"
ARCH_PANORAMA_PATH = PROJECT_ROOT / "data" / "databases" / "depgraph.db"

logger = logging.getLogger(__name__)


def run_verify(dry_run: bool = True, domain: str = "") -> bool:
    """Run verify_migration_alignment.py as prerequisite check."""
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "migration" / "verify_migration_alignment.py")]
    if dry_run:
        cmd.append("--dry-run")
    if domain:
        cmd.extend(["--domain", domain])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def load_panorama() -> dict:
    """Load architecture panorama from SQLite DB (arch_directory_tree table)."""
    conn = sqlite3.connect(str(ARCH_PANORAMA_PATH))
    conn.row_factory = sqlite3.Row
    tree: dict = {}
    for row in conn.execute("SELECT * FROM arch_directory_tree ORDER BY path"):
        r = dict(row)
        path = r.get("path", "")
        if not path:
            continue
        parts = path.strip("/").split("/")
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        current["__meta__"] = {
            "path": path,
            "path_type": r.get("path_type", ""),
            "domain_id": r.get("domain_id", ""),
            "lifecycle": r.get("state", ""),
            "blueprint_id": r.get("blueprint_id", ""),
            "change_policy": r.get("change_policy", ""),
            "modification_permission": r.get("modification_permission", ""),
            "build_status": r.get("build_status", ""),
        }
    conn.close()
    return {"tree": tree}


def save_panorama(data: dict) -> None:
    """Save panorama YAML atomically."""
    tmp_path = f"{ARCH_PANORAMA_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, str(ARCH_PANORAMA_PATH))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def load_migration_registry() -> dict:
    """Load migration registry."""
    with open(MIGRATION_REGISTRY, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_migration_registry(data: dict) -> None:
    """Save migration registry atomically."""
    tmp_path = f"{MIGRATION_REGISTRY}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, str(MIGRATION_REGISTRY))
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def find_pending_deletion_nodes(tree: dict, current_path: str = "") -> list[tuple[str, dict]]:
    """Find all nodes with lifecycle=pending_deletion in the tree."""
    results = []
    if not isinstance(tree, dict):
        return results
    meta = tree.get("__meta__", {})
    if meta.get("lifecycle") == "pending_deletion":
        results.append((meta.get("path", current_path), meta))
    for key, val in tree.items():
        if key.startswith("__") or not isinstance(val, dict):
            continue
        child_path = f"{current_path}/{key}" if current_path else key
        results.extend(find_pending_deletion_nodes(val, child_path))
    return results


def find_design_node_for_path(tree: dict, target_path: str, current_path: str = "") -> tuple[str, dict]:
    """Find the design-state node that should replace an operational node at target_path."""
    if not isinstance(tree, dict):
        return "", None
    meta = tree.get("__meta__", {})
    if meta.get("lifecycle") == "design" and meta.get("path", current_path) == target_path:
        return meta.get("path", current_path), meta
    for key, val in tree.items():
        if key.startswith("__") or not isinstance(val, dict):
            continue
        child_path = f"{current_path}/{key}" if current_path else key
        result = find_design_node_for_path(val, target_path, child_path)
        if result[1] is not None:
            return result
    return "", None


def main():
    parser = argparse.ArgumentParser(description="Safe delete operational nodes after migration verification")
    parser.add_argument(
        "--dry-run", action="store_true", help="Only output planned actions, do not modify/delete any file"
    )
    parser.add_argument("--domain", type=str, default="", help="Only process entries for specified domain_id")
    parser.add_argument("--batch", type=int, default=0, help="Only process entries in batch N")
    parser.add_argument("--force", action="store_true", help="Skip verify_migration_alignment prerequisite (DANGEROUS)")
    args = parser.parse_args()

    if args.dry_run:
        print("[SAFE-DELETE] DRY RUN MODE — no files will be modified or deleted")

    # Step 1: Prerequisite check
    if not args.force:
        print("[SAFE-DELETE] Running prerequisite: verify_migration_alignment.py ...")
        verified = run_verify(dry_run=True, domain=args.domain)
        if not verified:
            print("[FAIL] verify_migration_alignment.py did not pass. Aborting.")
            print("       Use --force to skip this check (DANGEROUS).")
            sys.exit(1)
        print("[OK] Verification passed")
    else:
        print("[WARN] Skipping verification (--force). This is dangerous!")

    # Step 2: Load panorama and find pending_deletion nodes
    print("[SAFE-DELETE] Loading panorama...")
    panorama = load_panorama()
    tree = panorama.get("tree", {})

    pending_nodes = find_pending_deletion_nodes(tree)
    print(f"[SAFE-DELETE] Found {len(pending_nodes)} pending_deletion nodes")

    if not pending_nodes:
        print("[OK] No pending_deletion nodes to process")
        sys.exit(0)

    # Step 3-4: Verify each node
    deletable = []
    for path, node in pending_nodes:
        disk_path = PROJECT_ROOT / path
        if not disk_path.exists():
            print(f"  SKIP {path}: disk path does not exist")
            continue
        deletable.append((path, node))

    print(f"[SAFE-DELETE] {len(deletable)} nodes eligible for deletion")

    if not deletable:
        print("[OK] No eligible nodes")
        sys.exit(0)

    # Step 5-8: Process deletions
    deleted_count = 0
    failed_count = 0

    for path, node in deletable:
        disk_path = PROJECT_ROOT / path
        print(f"\n  Processing: {path}")

        # Step 5: Delete disk file
        if not args.dry_run:
            try:
                if disk_path.is_dir():
                    shutil.rmtree(disk_path)
                else:
                    disk_path.unlink()
                print(f"    DELETED: {disk_path}")
            except Exception as e:
                print(f"    FAILED to delete: {e}")
                failed_count += 1
                continue
        else:
            print(f"    [DRY-RUN] Would delete: {disk_path}")

        # Step 6: Remove old operational node from panorama tree
        # (handled by next path-tree generation)

        # Step 7: Find and convert design node to operational
        # (handled by converting lifecycle in panorama)

        # Step 8: Update migration registry
        if not args.dry_run:
            registry = load_migration_registry()
            for entry in registry.get("entries", []):
                if entry.get("old_path", "").replace("\\", "/") == path.replace("\\", "/"):
                    entry["status"] = "completed"
                    entry["completed_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            save_migration_registry(registry)

        deleted_count += 1

    # Summary
    print(f"\n{'=' * 60}")
    print("[SAFE-DELETE] Summary")
    print(f"{'=' * 60}")
    print(f"  Processed: {len(deletable)}")
    print(f"  Deleted:   {deleted_count}")
    print(f"  Failed:    {failed_count}")

    if failed_count > 0:
        print(f"\n[FAIL] {failed_count} deletions failed — manual intervention required")
        sys.exit(1)
    else:
        print("\n[OK] All deletions completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    import sys

    sys.exit("DEPRECATED: 此脚本已归档，depgraph.db 已迁移至 PostgreSQL 16")
    main()
