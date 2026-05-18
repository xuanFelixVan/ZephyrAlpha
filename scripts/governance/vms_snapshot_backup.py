# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_snapshot_backup.py | §
"""
VMS Snapshot 备份脚本 — MOD-INF-011 · mitigates R4
====================================================
蓝图 §10 · 定期 snapshot 备份 + 启动时完整性校验

用法
----
    python scripts/governance/vms_snapshot_backup.py
    python scripts/governance/vms_snapshot_backup.py --persist-dir data/vector_db --backup-dir data/vector_db/_snapshots
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from zephyr.vector_memory.index_health_monitor import IndexHealthMonitor
from zephyr.vector_memory.collection_manager import CollectionManager


def run_backup(persist_dir: str = "data/vector_db", backup_dir: str = "data/vector_db/_snapshots") -> None:
    """run_backup implementation."""
    resolved_persist = Path(persist_dir)
    resolved_backup = Path(backup_dir)
    if not resolved_persist.is_absolute():
        resolved_persist = PROJECT_ROOT / resolved_persist
    if not resolved_backup.is_absolute():
        resolved_backup = PROJECT_ROOT / resolved_backup

    print(f"VMS Snapshot 备份 (mitigates R4)")
    print(f"================================")
    print(f"持久化目录: {resolved_persist}")
    print(f"备份目录:   {resolved_backup}")
    print()

    cm = CollectionManager(persist_dir=resolved_persist)
    monitor = IndexHealthMonitor(cm)

    integrity = monitor.integrity_check()
    print(f"完整性检查: {integrity['status']}")
    for issue in integrity.get("issues", []):
        print(f"  - {issue}")
    print()

    snapshot_path = monitor.snapshot_backup(backup_dir=resolved_backup)
    print(f"Snapshot 已保存: {snapshot_path}")

    result = {
        "timestamp": datetime.now(UTC).isoformat(),
        "snapshot_path": str(snapshot_path),
        "integrity": integrity,
    }
    manifest_path = resolved_backup / "snapshot_manifest.json"
    existing = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing.append(result)
    manifest_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest 已更新: {manifest_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VMS Snapshot 备份")
    parser.add_argument("--persist-dir", default="data/vector_db", help="ChromaDB 持久化目录")
    parser.add_argument("--backup-dir", default="data/vector_db/_snapshots", help="备份目标目录")
    args = parser.parse_args()
    run_backup(args.persist_dir, args.backup_dir)
