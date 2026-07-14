# [BLUEPRINT] MOD-GOV-migrate_metadata | scripts/governance/migrate_to_metadata_tables.py | §depgraph-stage2
# [MODULE] scripts.governance.migrate_to_metadata_tables
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.depgraph_schema
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 一次性迁移脚本（裁定#209 Stage 2）；幂等可重复执行
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=失败
# [TESTS]
# [TTL] task_bound
"""migrate_to_metadata_tables.py — 裁定#209 Stage 2 一次性迁移脚本

将 PRODUCTION_PROTECTED_FIELDS(14) + EDGES_PROTECTED_FIELDS(9) 从 nodes/edges
复制到新建的 nodes_metadata / edges_metadata 表。

执行后 write_depgraph_to_db 将用 SQL UPSERT+UPDATE 维护 metadata 表，
P1/P2 Python 保护机制（load_production_state_from_db 等）下线。

用法::

    python scripts/governance/migrate_to_metadata_tables.py
    python scripts/governance/migrate_to_metadata_tables.py --dry-run
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.governance.depgraph_schema import (  # noqa: E402
    _DDL_NODES_METADATA,
    _DDL_EDGES_METADATA,
    get_depgraph_pg_connection,
)

# 14 个 nodes 保护字段（与 generate_project_depgraph.PRODUCTION_PROTECTED_FIELDS 对齐）
NODES_META_FIELDS = [
    "blueprint_id", "owner", "impact_level", "change_policy",
    "modification_permission", "belongs_to", "build_status",
    "gate_reason", "hard_boundary_ref", "consumed_interfaces",
    "tags", "trust_zone", "deployment_lifecycle", "architecture_layer",
]

# 9 个 edges 保护字段（与 generate_project_depgraph.EDGES_PROTECTED_FIELDS 对齐）
EDGES_META_FIELDS = [
    "failure_mode", "fallback", "activation_condition",
    "data_transfer_description", "resource_impact",
    "ddd_integration_pattern", "event_ref", "api_contract_refs", "verified",
]


def migrate(dry_run: bool = False) -> int:
    """创建 metadata 表并从 nodes/edges 复制数据。

    Args:
        dry_run: True=只打印不执行
    Returns:
        0=成功, 1=失败
    """
    conn = get_depgraph_pg_connection(autocommit=False)
    try:
        cur = conn.cursor()

        # Step 1: 创建 metadata 表
        print("[MIGRATE] Step 1: Creating metadata tables...")
        cur.execute(_DDL_NODES_METADATA)
        cur.execute(_DDL_EDGES_METADATA)
        print("[MIGRATE]   nodes_metadata + edges_metadata 表已创建（IF NOT EXISTS）")

        # Step 2: 复制 nodes → nodes_metadata
        # 只复制 design_maturity='production' 的节点（与 load_production_state_from_db 一致）
        # ON CONFLICT DO NOTHING — 幂等，不覆盖已有 metadata
        print("[MIGRATE] Step 2: Copying nodes → nodes_metadata...")
        node_cols = ", ".join(NODES_META_FIELDS)
        now = datetime.now().isoformat()
        cur.execute(
            f"""
            INSERT INTO nodes_metadata (path, {node_cols}, last_updated)
            SELECT path, {node_cols}, %s
            FROM nodes
            WHERE design_maturity = 'production'
            ON CONFLICT (path) DO NOTHING
            """,
            (now,),
        )
        node_migrated = cur.rowcount
        print(f"[MIGRATE]   复制 {node_migrated} 条 nodes metadata（ON CONFLICT DO NOTHING）")

        # Step 3: 复制 edges → edges_metadata
        # 使用 JOIN 解析 node_id → path 作为稳定键
        # 排除 design 边和涉及 database 节点的边（与 load_edge_production_state_from_db 一致）
        print("[MIGRATE] Step 3: Copying edges → edges_metadata...")
        edge_cols = ", ".join(EDGES_META_FIELDS)
        cur.execute(
            f"""
            INSERT INTO edges_metadata (from_path, to_path, dep_type, {edge_cols}, last_updated)
            SELECT n1.path, n2.path, e.dep_type, {", ".join(f"e.{f}" for f in EDGES_META_FIELDS)}, %s
            FROM edges e
            JOIN nodes n1 ON e.from_node_id = n1.node_id
            JOIN nodes n2 ON e.to_node_id = n2.node_id
            WHERE (e.dep_maturity != 'design' OR e.dep_maturity IS NULL)
              AND e.from_node_id NOT IN (SELECT node_id FROM nodes WHERE node_type = 'database')
              AND e.to_node_id NOT IN (SELECT node_id FROM nodes WHERE node_type = 'database')
            ON CONFLICT (from_path, to_path, dep_type) DO NOTHING
            """,
            (now,),
        )
        edge_migrated = cur.rowcount
        print(f"[MIGRATE]   复制 {edge_migrated} 条 edges metadata（ON CONFLICT DO NOTHING）")

        if dry_run:
            print("[MIGRATE] DRY RUN — 回滚")
            conn.rollback()
        else:
            conn.commit()
            print(f"[MIGRATE] 提交完成: nodes_metadata={node_migrated}, edges_metadata={edge_migrated}")
            print("[MIGRATE] 下一步: 运行 generate_project_depgraph.py 验证 metadata UPSERT 逻辑")

        return 0
    except Exception as e:
        conn.rollback()
        print(f"[MIGRATE] ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="裁定#209 Stage 2: 迁移保护字段到 metadata 表")
    parser.add_argument("--dry-run", action="store_true", help="只打印不执行")
    args = parser.parse_args()
    sys.exit(migrate(dry_run=args.dry_run))
