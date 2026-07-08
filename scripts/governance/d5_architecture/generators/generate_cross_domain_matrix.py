# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_cross_domain_matrix
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
# [TTL] permanent
"""G6: 从 depgraph (PostgreSQL) edges 表生成域间依赖矩阵MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_cross_domain_matrix
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/cross_domain_matrix.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/cross_domain_matrix.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
[TESTS]
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

# 治本（2026-07-04）：DB_DISPLAY_NAME 前移到 __manifest__ 之前，避免 f-string 求值时 NameError。
# _common.py 与本文件同目录（generators/），CLI 运行时 sys.path[0]=本目录，可直接 import。
from _common import DB_DISPLAY_NAME  # noqa: E402

__manifest__ = f"""
args: []
description: 'G6: 从 {DB_DISPLAY_NAME} edges 表生成域间依赖矩阵MD文档'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "01_global_architecture_diagram" / "cross_domain_matrix.md"


def get_cross_domain_edges(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询所有跨域依赖边。"""
    cur = conn.execute(
        """SELECT n1.domain_id as from_domain, n2.domain_id as to_domain,
                  COUNT(*) as edge_count,
                  STRING_AGG(DISTINCT e.dep_type, ',') as dep_types
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id != n2.domain_id
             AND n1.domain_id IS NOT NULL
             AND n2.domain_id IS NOT NULL
           GROUP BY n1.domain_id, n2.domain_id
           ORDER BY edge_count DESC"""
    )
    return [
        {
            "from_domain": r["from_domain"],
            "to_domain": r["to_domain"],
            "edge_count": r["edge_count"],
            "dep_types": r["dep_types"] or "",
        }
        for r in cur.fetchall()
    ]


def get_all_domain_ids(conn: PgConnExecuteWrapper) -> list[str]:
    """查询所有域ID。"""
    cur = conn.execute("SELECT domain_id FROM domains ORDER BY domain_id")
    return [r["domain_id"] for r in cur.fetchall()]


def generate_cross_domain_matrix() -> str:
    """生成域间依赖矩阵MD文档。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        edges = get_cross_domain_edges(conn)
        domain_ids = get_all_domain_ids(conn)
    finally:
        conn.close()

    # 构建矩阵 from_domain -> to_domain -> count
    matrix: dict[str, dict[str, int]] = {}
    for e in edges:
        matrix.setdefault(e["from_domain"], {})[e["to_domain"]] = e["edge_count"]

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: register")
    lines.append("title: 域间依赖矩阵")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 域间依赖矩阵")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 以矩阵形式展示所有功能域之间的依赖关系，识别高耦合域和独立域，为架构解耦提供依据。")
    lines.append("")
    lines.append(f"> 本文档由 generate_cross_domain_matrix.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} edges表 + nodes表")
    lines.append("")

    # 统计概览
    total_edges = sum(e["edge_count"] for e in edges)
    lines.append("## 统计概览")
    lines.append("")
    lines.append("| 指标 / Metric | 值 / Value |")
    lines.append("|------|-----|")
    lines.append(f"| 域总数 | {len(domain_ids)} |")
    lines.append(f"| 跨域依赖对数 | {len(edges)} |")
    lines.append(f"| 跨域依赖边总数 | {total_edges} |")
    lines.append("")

    # 依赖最多的域对（Top 20）
    lines.append("## 跨域依赖 Top 20（按边数降序）")
    lines.append("")
    lines.append("| 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |")
    lines.append("|------|--------|:---:|---------|")
    for e in edges[:20]:
        lines.append(f"| {e['from_domain']} | {e['to_domain']} | {e['edge_count']} | {e['dep_types']} |")
    lines.append("")

    # 完整矩阵（简化版：只显示有依赖的域对）
    lines.append("## 完整跨域依赖清单")
    lines.append("")
    lines.append("| # / No. | 源域 / From Domain | 目标域 / To Domain | 边数 / Edges | 依赖类型 / Dep Types |")
    lines.append("|:---:|------|--------|:---:|---------|")
    for i, e in enumerate(edges, 1):
        lines.append(f"| {i} | {e['from_domain']} | {e['to_domain']} | {e['edge_count']} | {e['dep_types']} |")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成域间依赖矩阵。"""
    content = generate_cross_domain_matrix()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
