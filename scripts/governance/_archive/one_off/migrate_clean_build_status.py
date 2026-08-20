"""OPS-2026062504: 数据清洗 depgraph (PostgreSQL) 历史脏值

3类清洗（裁定#178-193）：
A. build_status脏值归一化 → 5态枚举
B. 删除非标准node_type节点（白名单准入，裁定#184）
C. 删除7682个无blueprint_id的design_maturity='design'幽灵节点（裁定#192）

执行顺序：先删非标准节点 → 删幽灵节点 → 归一化build_status → 归一化design_maturity

P2迁移后：全景图数据库为 depgraph (PostgreSQL)，连接由 get_depgraph_pg_connection 统一管理。
"""

import sys
from pathlib import Path

# ── _shared 模块 import bootstrap（P2迁移：复用 get_depgraph_pg_connection）──
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import (
    EXIT_FINDINGS,
    get_depgraph_pg_connection,  # noqa: E402
)

VALID_BUILD_STATUS = {"planned", "generated", "testing", "stable", "deprecated"}  # noqa: gate-vocab  build_status 枚举，非 module_lifecycle_status
VALID_DESIGN_MATURITY = {"design", "production", "prototype"}  # noqa: gate-vocab  design_maturity 业务子集（排除 legacy）
NODES_WHITELIST = {"module", "script", "test", "config"}  # noqa: gate-vocab  nodes 白名单业务子集


def clean_depgraph():
    """clean_depgraph implementation."""
    conn = get_depgraph_pg_connection(autocommit=False)
    # P2迁移后：PostgreSQL 无 PRAGMA foreign_keys；手动管理边删除（先删 edges 再删 nodes）
    cur = conn.cursor()

    # 记录清洗前状态
    cur.execute("SELECT COUNT(*) AS cnt FROM nodes")
    before_total = cur.fetchone()["cnt"]
    cur.execute("SELECT build_status, COUNT(*) AS cnt FROM nodes GROUP BY build_status")
    before_bs = {r["build_status"]: r["cnt"] for r in cur.fetchall()}
    cur.execute("SELECT node_type, COUNT(*) AS cnt FROM nodes GROUP BY node_type")
    before_nt = {r["node_type"]: r["cnt"] for r in cur.fetchall()}
    print(f"[BEFORE] total nodes: {before_total}")
    print(f"[BEFORE] build_status: {before_bs}")

    try:
        # ========== Step 1: 删除非标准node_type节点（裁定#184白名单准入） ==========
        # 白名单={module,script,test,config}，其余全部删除
        placeholders = ",".join(["%s"] * len(NODES_WHITELIST))
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM nodes WHERE node_type NOT IN ({})".format(placeholders),
            tuple(NODES_WHITELIST),
        )
        non_standard = cur.fetchone()["cnt"]
        print(f"\n[Step1] Deleting {non_standard} non-standard node_type nodes...")

        # 先删除这些节点的边
        cur.execute(
            "DELETE FROM edges WHERE from_node_id IN (SELECT node_id FROM nodes WHERE node_type NOT IN ({}))".format(
                placeholders
            ),
            tuple(NODES_WHITELIST),
        )
        edges_del_1 = cur.rowcount
        cur.execute(
            "DELETE FROM edges WHERE to_node_id IN (SELECT node_id FROM nodes WHERE node_type NOT IN ({}))".format(
                placeholders
            ),
            tuple(NODES_WHITELIST),
        )
        edges_del_2 = cur.rowcount
        print(f"  Deleted {edges_del_1 + edges_del_2} edges referencing non-standard nodes")

        cur.execute(
            "DELETE FROM nodes WHERE node_type NOT IN ({})".format(placeholders),
            tuple(NODES_WHITELIST),
        )
        print(f"  Deleted {cur.rowcount} non-standard nodes")

        # ========== Step 2: 删除幽灵设计节点（裁定#192） ==========
        # design_maturity='design' AND (blueprint_id IS NULL OR blueprint_id='')
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM nodes WHERE design_maturity='design' "
            "AND (blueprint_id IS NULL OR blueprint_id='')"
        )
        ghost = cur.fetchone()["cnt"]
        print(f"\n[Step2] Deleting {ghost} ghost design nodes (no blueprint_id)...")

        # 先删除这些节点的边
        cur.execute(
            "DELETE FROM edges WHERE from_node_id IN ("
            "SELECT node_id FROM nodes WHERE design_maturity='design' "
            "AND (blueprint_id IS NULL OR blueprint_id=''))"
        )
        edges_del_3 = cur.rowcount
        cur.execute(
            "DELETE FROM edges WHERE to_node_id IN ("
            "SELECT node_id FROM nodes WHERE design_maturity='design' "
            "AND (blueprint_id IS NULL OR blueprint_id=''))"
        )
        edges_del_4 = cur.rowcount
        print(f"  Deleted {edges_del_3 + edges_del_4} edges referencing ghost nodes")

        cur.execute("DELETE FROM nodes WHERE design_maturity='design' AND (blueprint_id IS NULL OR blueprint_id='')")
        print(f"  Deleted {cur.rowcount} ghost design nodes")

        # ========== Step 3: build_status脏值归一化（裁定#178-180） ==========
        print("\n[Step3] Normalizing build_status...")

        # design_only → planned
        cur.execute("UPDATE nodes SET build_status='planned' WHERE build_status='design_only'")
        print(f"  design_only→planned: {cur.rowcount}")

        # draft → 按design_maturity推导
        cur.execute("UPDATE nodes SET build_status='planned' WHERE build_status='draft' AND design_maturity='design'")
        print(f"  draft+design→planned: {cur.rowcount}")
        cur.execute(
            "UPDATE nodes SET build_status='generated' WHERE build_status='draft' AND design_maturity='production'"
        )
        print(f"  draft+production→generated: {cur.rowcount}")
        cur.execute(
            "UPDATE nodes SET build_status='generated' WHERE build_status='draft' AND design_maturity='prototype'"
        )
        print(f"  draft+prototype→generated: {cur.rowcount}")
        cur.execute(
            "UPDATE nodes SET build_status='generated' WHERE build_status='draft' AND design_maturity='scaffold_placeholder'"
        )
        print(f"  draft+scaffold_placeholder→generated: {cur.rowcount}")
        # 剩余draft（无design_maturity匹配）→ generated
        cur.execute("UPDATE nodes SET build_status='generated' WHERE build_status='draft'")
        print(f"  draft(remaining)→generated: {cur.rowcount}")

        # orphan → deprecated（RULE-THREE审判：保守标记为deprecated，待audit脚本复查）
        cur.execute("UPDATE nodes SET build_status='deprecated' WHERE build_status='orphan'")
        print(f"  orphan→deprecated: {cur.rowcount}")

        # production → stable
        cur.execute("UPDATE nodes SET build_status='stable' WHERE build_status='production'")
        print(f"  production→stable: {cur.rowcount}")

        # active → stable
        cur.execute("UPDATE nodes SET build_status='stable' WHERE build_status='active'")
        print(f"  active→stable: {cur.rowcount}")

        # unbuilt → generated
        cur.execute("UPDATE nodes SET build_status='generated' WHERE build_status='unbuilt'")
        print(f"  unbuilt→generated: {cur.rowcount}")

        # path_invalid → 删除节点
        cur.execute("SELECT COUNT(*) AS cnt FROM nodes WHERE build_status='path_invalid'")
        path_invalid = cur.fetchone()["cnt"]
        if path_invalid > 0:
            cur.execute(
                "DELETE FROM edges WHERE from_node_id IN (SELECT node_id FROM nodes WHERE build_status='path_invalid')"
            )
            cur.execute(
                "DELETE FROM edges WHERE to_node_id IN (SELECT node_id FROM nodes WHERE build_status='path_invalid')"
            )
            cur.execute("DELETE FROM nodes WHERE build_status='path_invalid'")
            print(f"  path_invalid→deleted: {cur.rowcount} nodes")

        # ========== Step 4: design_maturity归一化（裁定#179） ==========
        print("\n[Step4] Normalizing design_maturity...")
        cur.execute("UPDATE nodes SET design_maturity='prototype' WHERE design_maturity='scaffold_placeholder'")
        print(f"  scaffold_placeholder→prototype: {cur.rowcount}")

        # ========== 验证 ==========
        print("\n=== VERIFICATION ===")
        cur.execute("SELECT COUNT(*) AS cnt FROM nodes")
        after_total = cur.fetchone()["cnt"]
        cur.execute("SELECT build_status, COUNT(*) AS cnt FROM nodes GROUP BY build_status")
        after_bs = {r["build_status"]: r["cnt"] for r in cur.fetchall()}
        cur.execute("SELECT design_maturity, COUNT(*) AS cnt FROM nodes GROUP BY design_maturity")
        after_dm = {r["design_maturity"]: r["cnt"] for r in cur.fetchall()}
        cur.execute("SELECT node_type, COUNT(*) AS cnt FROM nodes GROUP BY node_type")
        after_nt = {r["node_type"]: r["cnt"] for r in cur.fetchall()}
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM nodes WHERE design_maturity='design' "
            "AND (blueprint_id IS NULL OR blueprint_id='')"
        )
        ghost_remaining = cur.fetchone()["cnt"]

        print(f"[AFTER] total nodes: {after_total} (deleted {before_total - after_total})")
        print(f"[AFTER] build_status: {after_bs}")
        print(f"[AFTER] design_maturity: {after_dm}")
        print(f"[AFTER] node_type: {after_nt}")
        print(f"[AFTER] ghost design nodes remaining: {ghost_remaining}")

        # 验收检查
        invalid_bs = set(after_bs.keys()) - VALID_BUILD_STATUS
        invalid_dm = set(after_dm.keys()) - VALID_DESIGN_MATURITY
        invalid_nt = set(after_nt.keys()) - NODES_WHITELIST

        if invalid_bs:
            print(f"\n[FAIL] Invalid build_status values: {invalid_bs}")
            raise ValueError(f"Invalid build_status: {invalid_bs}")
        if invalid_dm:
            print(f"\n[FAIL] Invalid design_maturity values: {invalid_dm}")
            raise ValueError(f"Invalid design_maturity: {invalid_dm}")
        if invalid_nt:
            print(f"\n[FAIL] Invalid node_type values: {invalid_nt}")
            raise ValueError(f"Invalid node_type: {invalid_nt}")
        if ghost_remaining > 0:
            print(f"\n[FAIL] Ghost design nodes remaining: {ghost_remaining}")
            raise ValueError(f"Ghost nodes: {ghost_remaining}")

        print("\n[PASS] All verification checks passed!")
        conn.commit()
        print(f"[COMMITTED] Changes saved to {DB_DISPLAY_NAME}")

    except Exception as e:
        conn.rollback()
        print(f"\n[ROLLBACK] Error: {e}", file=sys.stderr)
        print(f"All changes rolled back. {DB_DISPLAY_NAME} is unchanged.", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)
    finally:
        conn.close()


if __name__ == "__main__":
    clean_depgraph()
