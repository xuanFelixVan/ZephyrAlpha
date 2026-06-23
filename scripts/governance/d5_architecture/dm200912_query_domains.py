"""DM-200912 Phase4-A: 查询 depgraph.db 域+模块统计，输出 JSON 供视图重写使用

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.5
[MODULE] scripts.governance.d5_architecture.dm200912_query_domains
[INVARIANTS] 只读depgraph.db;输出JSON到stdout
[MODIFY-GUARD] 修改需通过DM-200912任务卡
[CONSUMERS] dm200912_rewrite_views.py
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1
[TESTS] 无(一次性脚本)
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")


def main() -> None:
    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        # 域清单+模块统计
        cur = conn.execute(
            """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                      d.max_modules, d.description,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual_nodes,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as production_count,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'design') as design_count,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'prototype') as prototype_count
               FROM domains d ORDER BY d.layer_id, d.domain_id"""
        )
        domains = []
        for r in cur.fetchall():
            domains.append(
                {
                    "domain_id": r[0],
                    "domain_name": r[1] or "",
                    "layer_id": r[2] or "",
                    "current_modules": r[3] or 0,
                    "max_modules": r[4] or 200,
                    "description": r[5] or "",
                    "actual_nodes": r[6],
                    "production_count": r[7],
                    "design_count": r[8],
                    "prototype_count": r[9],
                }
            )

        # 全局统计
        cur = conn.execute("SELECT COUNT(*) FROM domains")
        total_domains = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM nodes")
        total_nodes = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM edges")
        total_edges = cur.fetchone()[0]
        cur = conn.execute(
            "SELECT design_maturity, COUNT(*) FROM nodes GROUP BY design_maturity ORDER BY COUNT(*) DESC"
        )
        maturity_dist = {r[0] or "NULL": r[1] for r in cur.fetchall()}
        cur = conn.execute("SELECT build_status, COUNT(*) FROM nodes GROUP BY build_status ORDER BY COUNT(*) DESC")
        build_dist = {r[0] or "NULL": r[1] for r in cur.fetchall()}
        cur = conn.execute("SELECT layer_id, COUNT(*) FROM domains GROUP BY layer_id ORDER BY layer_id")
        layer_dist = {r[0] or "NULL": r[1] for r in cur.fetchall()}

        result = {
            "total_domains": total_domains,
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "maturity_distribution": maturity_dist,
            "build_status_distribution": build_dist,
            "layer_distribution": layer_dist,
            "domains": domains,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
