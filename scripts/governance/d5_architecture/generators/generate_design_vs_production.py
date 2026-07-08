# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_design_vs_production
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
"""G8: 从 depgraph (PostgreSQL) nodes 表生成设计态vs运营态统计报告MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_design_vs_production
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/design_vs_production.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/design_vs_production.md
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
description: 'G8: 从 {DB_DISPLAY_NAME} nodes 表生成设计态vs运营态统计报告MD文档'
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

from domain_name_mapping import get_domain_name_zh
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

OUTPUT_PATH = REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports" / "design_vs_production.md"


def get_maturity_stats(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询各域的设计态vs运营态统计。"""
    cur = conn.execute(
        """SELECT d.domain_id, d.domain_name,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as total,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as production,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'design') as design,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'prototype') as prototype,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'scaffold_placeholder') as scaffold
           FROM domains d
           ORDER BY d.domain_id"""
    )
    return [
        {
            "domain_id": r["domain_id"],
            "domain_name": r["domain_name"] or "",
            "total": r["total"],
            "production": r["production"],
            "design": r["design"],
            "prototype": r["prototype"],
            "scaffold": r["scaffold"],
        }
        for r in cur.fetchall()
    ]


def get_build_status_stats(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询各 build_status 的统计。"""
    cur = conn.execute(
        """SELECT build_status, COUNT(*) as cnt
           FROM nodes
           GROUP BY build_status
           ORDER BY cnt DESC"""
    )
    return [{"build_status": r["build_status"] or "", "count": r["cnt"]} for r in cur.fetchall()]


def generate_design_vs_production() -> str:
    """生成设计态vs运营态统计报告。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        domain_stats = get_maturity_stats(conn)
        build_stats = get_build_status_stats(conn)
    finally:
        conn.close()

    lines = []
    # frontmatter
    lines.append("---")
    lines.append("doc_type: audit_report")
    lines.append("title: 设计态vs运营态统计报告")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append("date: auto-generated")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 设计态vs运营态统计报告")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 展示各域设计态模块与运营态模块的数量对比和迁移进度，跟踪从设计到落地的完成率。")
    lines.append("")
    lines.append(f"> 本文档由 generate_design_vs_production.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append("> 最后更新以 git log 为准")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} nodes表")
    lines.append("")

    # 全局统计
    total_nodes = sum(d["total"] for d in domain_stats)
    total_production = sum(d["production"] for d in domain_stats)
    total_design = sum(d["design"] for d in domain_stats)
    total_prototype = sum(d["prototype"] for d in domain_stats)
    total_scaffold = sum(d["scaffold"] for d in domain_stats)

    lines.append("## 全局统计")
    lines.append("")
    lines.append("| 设计成熟度 / Maturity | 模块数 / Modules | 占比 / Ratio |")
    lines.append("|-----------|:---:|:---:|")
    if total_nodes > 0:
        lines.append(f"| production（生产态） | {total_production} | {total_production / total_nodes * 100:.1f}% |")
        lines.append(f"| design（设计态） | {total_design} | {total_design / total_nodes * 100:.1f}% |")
        lines.append(f"| prototype（原型态） | {total_prototype} | {total_prototype / total_nodes * 100:.1f}% |")
        lines.append(
            f"| scaffold_placeholder（脚手架） | {total_scaffold} | {total_scaffold / total_nodes * 100:.1f}% |"
        )
    lines.append(f"| **总计** | **{total_nodes}** | **100%** |")
    lines.append("")

    # build_status 统计
    lines.append("## 构建状态统计（build_status）")
    lines.append("")
    lines.append("| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |")
    lines.append("|---------|:---:|:---:|")
    for b in build_stats:
        pct = b["count"] / total_nodes * 100 if total_nodes > 0 else 0
        lines.append(f"| {b['build_status']} | {b['count']} | {pct:.1f}% |")
    lines.append("")

    # 各域统计
    lines.append("## 各域设计成熟度统计")
    lines.append("")
    lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |")
    lines.append("|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|")
    for d in domain_stats:
        production_rate = f"{d['production']/d['total']*100:.1f}%" if d["total"] > 0 else "N/A"
        lines.append(
            f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['total']} | "
            f"{d['production']} | {d['design']} | {d['prototype']} | {d['scaffold']} | "
            f"{production_rate} |"
        )
    lines.append("")

    # 生产化率最低的域（需要优先推进到 production）
    domains_with_nodes = [d for d in domain_stats if d["total"] > 0]
    domains_with_nodes.sort(key=lambda x: x["production"] / x["total"] if x["total"] > 0 else 1)

    lines.append("## 生产化率最低的域（Top 10，需优先推进）")
    lines.append("")
    lines.append("| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |")
    lines.append("|------|--------|:---:|:---:|:---:|")
    for d in domains_with_nodes[:10]:
        rate = d["production"] / d["total"] * 100 if d["total"] > 0 else 0
        lines.append(f"| {d['domain_id']} | {get_domain_name_zh(d['domain_id'], d['domain_name'])} | {d['total']} | {d['production']} | {rate:.1f}% |")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成设计态vs运营态统计报告。"""
    content = generate_design_vs_production()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
