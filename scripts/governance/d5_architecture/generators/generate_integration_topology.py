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
"""G4: 从 depgraph.db edges 表生成所有功能域的集成依赖关系图(.mmd Mermaid格式)

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_integration_topology
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到generated/
[MODIFY-GUARD] 修改需通过DM-200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/integration_topology.mmd
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1
[TESTS] tests/test_dm200910_generators.py
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/01_global_architecture_diagram")


def get_cross_domain_deps(conn: sqlite3.Connection) -> list[dict]:
    """查询所有跨域依赖（按域对聚合）。"""
    cur = conn.execute(
        """SELECT n1.domain_id as from_domain, n2.domain_id as to_domain,
                  COUNT(*) as cnt, GROUP_CONCAT(DISTINCT e.dep_type) as dep_types
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
            "from_domain": r[0],
            "to_domain": r[1],
            "count": r[2],
            "dep_types": r[3] or "",
        }
        for r in cur.fetchall()
    ]


def get_domain_info_map(conn: sqlite3.Connection) -> dict[str, dict]:
    """获取所有域的基本信息。"""
    cur = conn.execute("SELECT domain_id, domain_name, current_modules, layer_id FROM domains ORDER BY domain_id")
    return {
        r[0]: {
            "domain_id": r[0],
            "domain_name": r[1] or r[0],
            "current_modules": r[2] or 0,
            "layer_id": r[3] or "",
        }
        for r in cur.fetchall()
    }


def generate_integration_topology(conn: sqlite3.Connection) -> str:
    """生成所有功能域的集成依赖关系图。"""
    deps = get_cross_domain_deps(conn)
    domain_map = get_domain_info_map(conn)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    # Markdown 头部
    lines.append("# 集成拓扑图")
    lines.append("")
    lines.append(f"> 自动生成时间: {now}")
    lines.append("> 数据源: depgraph.db edges表（跨域依赖）")
    lines.append(f"> 跨域依赖对数: {len(deps)}")
    lines.append("")
    lines.append("```mermaid")
    lines.append("")

    lines.append("%% 所有功能域集成依赖关系图")
    lines.append(f"%% 生成时间: {now}")
    lines.append("%% 数据源: depgraph.db edges表（跨域依赖）")
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
            name = domain_map[did]["domain_name"]
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

    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        content = generate_integration_topology(conn)
        out_path = output_dir / args.output_name
        out_path.write_text(content, encoding="utf-8")
        print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
