# [BLUEPRINT] MOD-INF-005 | scripts/governance/vms_migration_dry_run.py | §
# [MODULE] scripts.governance.vms_migration_dry_run
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
# [TTL] task_bound
"""
VMS 迁移 dry-run 脚本 — MOD-INF-011 Phase 2 前置检查
======================================================
蓝图 §5.2 · R15 缓解 · unified_memory topic → Collection 映射预览

用法
----
    python scripts/governance/vms_migration_dry_run.py
    python scripts/governance/vms_migration_dry_run.py --persist-dir .audit_cache/vector_index
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from zephyr.governance.knowledge_management.vector_memory.bridge_layer import MIGRATION_MAP, BridgeLayer

TOPIC_STATS: dict[str, int] = {}


def run_dry_run(persist_dir: str = ".audit_cache/vector_index") -> None:
    """run_dry_run implementation."""
    resolved = Path(persist_dir)
    if not resolved.is_absolute():
        resolved = PROJECT_ROOT / resolved

    print("VMS 迁移 Dry-Run")
    print("=================")
    print(f"kb/ 持久化目录: {resolved}")
    print("")

    mappings = BridgeLayer.dry_run_topic_split(resolved)
    if not mappings:
        print("未找到 unified_memory Collection 或 Collection 为空")
    else:
        for m in mappings:
            topic = m["topic"]
            TOPIC_STATS[topic] = TOPIC_STATS.get(topic, 0) + 1

        print("topic → 目标 Collection 映射表")
        print("-" * 60)
        print(f"{'topic':<25} {'count':<8} {'target_collection':<20}")
        print("-" * 60)
        for topic, count in sorted(TOPIC_STATS.items()):
            target = BridgeLayer.TOPIC_TO_COLLECTION.get(topic, "unknown")
            print(f"{topic:<25} {count:<8} {target:<20}")
        print("-" * 60)
        print(f"总计: {len(mappings)} 条记录")

    print("")
    print("静态迁移映射（kb/ 4 Collection → VMS 8 Collection）:")
    print("-" * 70)
    print(f"{'source':<20} {'target':<20} {'dim_change':<14} {'re_embed':<10}")
    print("-" * 70)
    for source, mapping in MIGRATION_MAP.items():
        dim_change = f"{mapping['source_dim']}→{mapping['target_dim']}"
        print(f"{source:<20} {mapping['target']:<20} {dim_change:<14} {mapping['re_embed']!s:<10}")
    print("-" * 70)

    result = {
        "unified_memory_record_count": len(mappings),
        "topic_distribution": TOPIC_STATS,
        "static_migrations": [
            {
                "source": s,
                "target": m["target"],
                "dim_change": f"{m['source_dim']}→{m['target_dim']}",
                "re_embed": m["re_embed"],
            }
            for s, m in MIGRATION_MAP.items()
        ],
    }

    output_path = PROJECT_ROOT / "data/vector_db/_migration_dry_run_result.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n输出已写入: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VMS 迁移 dry-run")
    parser.add_argument(
        "--persist-dir",
        default=".audit_cache/vector_index",
        help="kb/ ChromaDB 持久化目录路径",
    )
    args = parser.parse_args()
    run_dry_run(args.persist_dir)
