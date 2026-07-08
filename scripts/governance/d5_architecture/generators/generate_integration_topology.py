# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_integration_topology
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
"""G4: 从 depgraph (PostgreSQL) edges 表生成所有功能域的集成依赖关系图(.mmd Mermaid格式)

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_integration_topology
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/
[MODIFY-GUARD] 修改需通过DM-200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/integration_topology.mmd
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
description: 'G4: 从 {DB_DISPLAY_NAME} edges 表生成所有功能域的集成依赖关系图(.mmd Mermaid格式)'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from domain_name_mapping import get_domain_name_zh
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

OUTPUT_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "01_global_architecture_diagram"


def get_cross_domain_deps(conn: PgConnExecuteWrapper) -> list[dict]:
    """查询所有跨域依赖（按域对聚合）。"""
    cur = conn.execute(
        """SELECT n1.domain_id as from_domain, n2.domain_id as to_domain,
                  COUNT(*) as cnt, STRING_AGG(DISTINCT e.dep_type, ',') as dep_types
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id != n2.domain_id
             AND n1.domain_id IS NOT NULL
             AND n2.domain_id IS NOT NULL
             AND n1.domain_id != ''
             AND n2.domain_id != ''
           GROUP BY n1.domain_id, n2.domain_id
           ORDER BY cnt DESC"""
    )
    return [
        {
            "from_domain": r["from_domain"],
            "to_domain": r["to_domain"],
            "count": r["cnt"],
            "dep_types": r["dep_types"] or "",
        }
        for r in cur.fetchall()
    ]


def get_domain_info_map(conn: PgConnExecuteWrapper) -> dict[str, dict]:
    """获取所有域的基本信息。"""
    cur = conn.execute("SELECT domain_id, domain_name, current_modules, layer_id FROM domains ORDER BY domain_id")
    return {
        r["domain_id"]: {
            "domain_id": r["domain_id"],
            "domain_name": r["domain_name"] or r["domain_id"],
            "current_modules": r["current_modules"] or 0,
            "layer_id": r["layer_id"] or "",
        }
        for r in cur.fetchall()
    }


def generate_integration_topology(conn: PgConnExecuteWrapper) -> str:
    """生成所有功能域的集成依赖关系图。"""
    deps = get_cross_domain_deps(conn)
    domain_map = get_domain_info_map(conn)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    # Markdown 头部
    lines.append("# 集成拓扑图")
    lines.append("")
    lines.append("> **文档作用 / Purpose**: 展示系统间集成关系和数据流向，包括API调用、事件订阅、数据同步等集成方式。")
    lines.append("")
    lines.append(f"> 自动生成时间: {now}")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} edges表（跨域依赖）")
    lines.append(f"> 跨域依赖对数: {len(deps)}")
    lines.append("")
    lines.append("```mermaid")
    lines.append("")

    lines.append("%% 所有功能域集成依赖关系图")
    lines.append(f"%% 生成时间: {now}")
    lines.append(f"%% 数据源: {DB_DISPLAY_NAME} edges表（跨域依赖）")
    lines.append(f"%% 跨域依赖对数: {len(deps)}")
    lines.append("")
    lines.append("graph LR")
    lines.append("")

    # 按层分组显示域节点
    layer_groups: dict[str, list[str]] = {}
    for did, info in domain_map.items():
        layer = info["layer_id"] or "unknown"
        layer_groups.setdefault(layer, []).append(did)

    # 显示域节点（按层分组）
    lines.append("    %% 功能域节点（按架构层分组）")
    for layer in sorted(layer_groups.keys()):
        domains_in_layer = sorted(layer_groups[layer])
        safe_layer = layer.replace("-", "_").replace(".", "_")
        lines.append(f"    subgraph {safe_layer}[{layer}]")
        for did in domains_in_layer:
            safe_id = did.replace("-", "_")
            name = get_domain_name_zh(did, domain_map[did]["domain_name"])
            mod_count = domain_map[did]["current_modules"]
            lines.append(f'        {safe_id}["{did}<br/>{name}<br/>({mod_count}模块)"]')
        lines.append("    end")
    lines.append("")

    # 跨域依赖边（限制数量避免图表过大）
    MAX_EDGES = 100
    lines.append(f"    %% 跨域依赖（按依赖数排序，最多显示 {MAX_EDGES} 条）")

    # 按依赖数排序，只显示前 N 条
    sorted_deps = sorted(deps, key=lambda x: x["count"], reverse=True)
    for d in sorted_deps[:MAX_EDGES]:
        from_safe = d["from_domain"].replace("-", "_")
        to_safe = d["to_domain"].replace("-", "_")
        cnt = d["count"]
        dep_types = d["dep_types"]
        # 只显示主要的依赖类型
        primary_type = dep_types.split(",")[0] if dep_types else "dep"
        lines.append(f"    {from_safe} -->|{cnt}条 {primary_type}| {to_safe}")

    if len(sorted_deps) > MAX_EDGES:
        lines.append(f"    %% ... 还有 {len(sorted_deps) - MAX_EDGES} 条跨域依赖未显示")
    lines.append("")

    # 统计信息
    lines.append("    %% 统计")
    lines.append(f"    %% 域总数: {len(domain_map)}")
    lines.append(f"    %% 跨域依赖对数: {len(deps)}")
    total_edges = sum(d["count"] for d in deps)
    lines.append(f"    %% 跨域依赖边总数: {total_edges}")

    # Top 10 依赖对
    lines.append("")
    lines.append("    %% Top 10 依赖对")
    for i, d in enumerate(sorted_deps[:10], 1):
        lines.append(f"    %% {i}. {d['from_domain']} -> {d['to_domain']}: {d['count']} 条")
    lines.append("")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成集成依赖关系图。"""
    parser = argparse.ArgumentParser(description="G4: 生成所有功能域集成依赖关系图(.mmd)")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--output-name", type=str, default="integration_topology.md", help="输出文件名")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        content = generate_integration_topology(conn)
        out_path = output_dir / args.output_name
        out_path.write_text(content, encoding="utf-8")
        print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
