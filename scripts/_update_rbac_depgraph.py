# [BLUEPRINT]
# [MODULE] scripts._update_rbac_depgraph
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""更新depgraph.db中RBAC核心节点从prototype升级为production."""
import sqlite3
import sys

DB_PATH = r"D:\ZephyrAlpha\data\databases\depgraph.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 需要更新的节点
    targets = [
        (50581, "src/zephyr/security/access_control/governance_bridges/bootstrap_superadmin.py"),
        (51072, "src/zephyr/trading/auto_runtime_core.py"),
    ]

    for node_id, path in targets:
        # 先查询当前状态
        cur.execute(
            "SELECT node_id, path, design_maturity FROM nodes WHERE node_id = ?",
            (node_id,),
        )
        row = cur.fetchone()
        if row is None:
            print(f"SKIP: node_id={node_id} not found")
            continue
        print(f"BEFORE: id={row[0]} maturity={row[2]} path={row[1]}")

        # 更新为production
        cur.execute(
            "UPDATE nodes SET design_maturity = 'production' WHERE node_id = ?",
            (node_id,),
        )
        affected = cur.rowcount
        print(f"UPDATE: {affected} row(s) affected")

        # 验证更新
        cur.execute(
            "SELECT node_id, path, design_maturity FROM nodes WHERE node_id = ?",
            (node_id,),
        )
        row = cur.fetchone()
        print(f"AFTER:  id={row[0]} maturity={row[2]} path={row[1]}")
        print()

    conn.commit()
    print("COMMITTED")

    # 验证所有RBAC核心节点状态
    print("\n=== Final RBAC core node status ===")
    cur.execute("""
        SELECT node_id, path, design_maturity
        FROM nodes
        WHERE path LIKE '%genesis_bootstrap%'
           OR path LIKE '%bootstrap_superadmin%'
           OR path LIKE '%auto_runtime_core%'
           OR path LIKE '%governance_bridges/bootstrap%'
        ORDER BY path
    """)
    for r in cur.fetchall():
        print(f"  id={r[0]} maturity={r[2]} path={r[1]}")

    conn.close()

if __name__ == "__main__":
    main()
