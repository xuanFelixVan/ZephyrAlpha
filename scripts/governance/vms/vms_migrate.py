# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_migrate.py | §
# [MODULE] scripts.governance.vms_migrate
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
VMS Phase 2 数据迁移脚本 — MOD-INF-011
=========================================
蓝图 §11.2 · 8 Collection 落地 + kb/ → VMS 迁移

用法
----
    python scripts/governance/vms_migrate.py --dry-run
    python scripts/governance/vms_migrate.py --execute
"""

from __future__ import annotations

__manifest__ = """
args: []
description: VMS Phase 2 数据迁移脚本 — MOD-INF-011
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from zephyr.governance.knowledge_management.vector_memory.bridge_layer import MIGRATION_MAP, BridgeLayer
from zephyr.governance.knowledge_management.vector_memory.collection_manager import CollectionManager


def run_migration(dry_run: bool = False) -> None:
    """run_migration implementation."""
    print("VMS Phase 2 迁移脚本")
    print("=====================")
    print(f"模式: {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print()

    cm = CollectionManager()
    bridge = BridgeLayer(cm)

    print("初始化 8 Collection...")
    results = cm.init_all_collections()
    for r in results:
        status = "已存在" if r.exists else "新创建"
        print(f"  {r.name:25s} {r.dimension:5d}d {status}")
    print()

    dry_run_results = BridgeLayer.dry_run_topic_split()
    print(f"unified_memory topic 分布: {len(dry_run_results)} 条")
    print()

    print("静态迁移映射:")
    print("-" * 80)
    print(f"{'source':<22} {'target':<22} {'dim_change':<14} {'re_embed':<10}")
    print("-" * 80)
    for source, mapping in MIGRATION_MAP.items():
        dim_change = f"{mapping['source_dim']}→{mapping['target_dim']}"
        print(f"{source:<22} {mapping['target']:<22} {dim_change:<14} {mapping['re_embed']!s:<10}")
    print("-" * 80)

    if dry_run:
        print()
        print("Dry-run 完成。使用 --execute 执行实际迁移。")
        return

    print()
    print("开始执行迁移...")
    for source, mapping in MIGRATION_MAP.items():
        try:
            info = bridge.migrate_collection(source, mapping["target"])
            print(f"  ✅ {source} → {mapping['target']} ({info.metadata.get('dimension', '?')}d)")
        except KeyError:
            print(f"  ⚠️ 跳过 {source} → 源 Collection 不存在")
        except Exception as e:
            print(f"  ❌ {source} 迁移失败: {e}")

    print()
    print("迁移完成。当前 Collection 状态:")
    for r in cm.list_collections():
        status = "已存在" if r.exists else "缺失"
        print(f"  {r.name:25s} {status}")

    print()
    bridge.mark_deprecated_after_migration()
    print("kb/ 已标记 DEPRECATED。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VMS Phase 2 迁移")
    parser.add_argument("--dry-run", action="store_true", help="仅预览不执行")
    parser.add_argument("--execute", action="store_true", help="执行迁移")
    args = parser.parse_args()
    run_migration(dry_run=not args.execute)
