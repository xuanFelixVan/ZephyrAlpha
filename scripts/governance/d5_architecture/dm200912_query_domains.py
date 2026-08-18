# [BLUEPRINT] MOD-GOV_DM200912_QUERY_DOMAINS
# [MODULE]# [MODULE] scripts.governance.d5_architecture.dm200912_query_domains
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
# [TTL] task_bound
"""DM-200912 Phase4-A: 查询 depgraph (PostgreSQL) 域+模块统计，输出 JSON 供视图重写使用

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.5
[MODULE] scripts.governance.d5_architecture.dm200912_query_domains
[INVARIANTS] 只读depgraph (PostgreSQL);输出JSON到stdout
[MODIFY-GUARD] 修改需通过DM-200912任务卡
[CONSUMERS] dm200912_rewrite_views.py
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
[TESTS] 无(一次性脚本)
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'DM-200912 Phase4-A: 查询 depgraph (PostgreSQL) 域+模块统计，输出 JSON 供视图重写使用'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        # 域清单+模块统计
        cur = conn.execute(
            """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                      d.max_modules, d.description,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual_nodes,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as production_count,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'design') as design_count
               FROM domains d ORDER BY d.layer_id, d.domain_id"""
        )
        domains = []
        for r in cur.fetchall():
            domains.append(
                {
                    "domain_id": r["domain_id"],
                    "domain_name": r["domain_name"] or "",
                    "layer_id": r["layer_id"] or "",
                    "current_modules": r["current_modules"] or 0,
                    "max_modules": r["max_modules"] or 200,
                    "description": r["description"] or "",
                    "actual_nodes": r["actual_nodes"],
                    "production_count": r["production_count"],
                    "design_count": r["design_count"],
                }
            )

        # 全局统计
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM domains")
        total_domains = cur.fetchone()["cnt"]
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM nodes")
        total_nodes = cur.fetchone()["cnt"]
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM edges")
        total_edges = cur.fetchone()["cnt"]
        cur = conn.execute(
            "SELECT design_maturity, COUNT(*) AS cnt FROM nodes GROUP BY design_maturity ORDER BY COUNT(*) DESC"
        )
        maturity_dist = {r["design_maturity"] or "NULL": r["cnt"] for r in cur.fetchall()}
        cur = conn.execute("SELECT build_status, COUNT(*) AS cnt FROM nodes GROUP BY build_status ORDER BY COUNT(*) DESC")
        build_dist = {r["build_status"] or "NULL": r["cnt"] for r in cur.fetchall()}
        cur = conn.execute("SELECT layer_id, COUNT(*) AS cnt FROM domains GROUP BY layer_id ORDER BY layer_id")
        layer_dist = {r["layer_id"] or "NULL": r["cnt"] for r in cur.fetchall()}

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
