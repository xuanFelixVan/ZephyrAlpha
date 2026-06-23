"""查询并更新depgraph.db中RBAC核心节点的design_maturity状态."""
import sqlite3
import sys

DB_PATH = r"D:\ZephyrAlpha\data\databases\depgraph.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 查找RBAC核心节点
    cur.execute("""
        SELECT node_id, path, design_maturity, node_type
        FROM nodes
        WHERE path LIKE '%genesis_bootstrap%'
           OR path LIKE '%bootstrap_superadmin%'
           OR path LIKE '%auto_runtime_core%'
           OR path LIKE '%governance_bridges%'
        ORDER BY path
    """)
    rows = cur.fetchall()
    print(f"RBAC core nodes: {len(rows)}")
    for r in rows:
        print(f"  id={r[0]} maturity={r[2]} type={r[3]} path={r[1]}")

    # 查找所有design_only或design状态的access_control节点
    cur.execute("""
        SELECT node_id, path, design_maturity, node_type
        FROM nodes
        WHERE (path LIKE '%access_control%' OR path LIKE '%agent_rbac%')
          AND design_maturity IN ('design', 'design_only', 'draft', 'prototype')
        ORDER BY path
    """)
    design_rows = cur.fetchall()
    print(f"\nDesign/prototype access_control nodes: {len(design_rows)}")
    for r in design_rows:
        print(f"  id={r[0]} maturity={r[2]} type={r[3]} path={r[1]}")

    conn.close()

if __name__ == "__main__":
    main()
