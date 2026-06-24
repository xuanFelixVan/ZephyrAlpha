"""G5: 从 depgraph.db domains+nodes 表生成域总览索引MD文档

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_index
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到generated/domain_index.md
[MODIFY-GUARD] 修改需通过DM-200911任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/domain_index.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1
[TESTS] tests/test_dm200911_generators.py
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
OUTPUT_PATH = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/02_domain_architecture_docs/domain_index.md")


def get_all_domains(conn: sqlite3.Connection) -> list[dict]:
    """查询所有域及其模块统计。"""
    cur = conn.execute(
        """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                  d.max_modules, d.description,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual_nodes,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as production_count,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'design') as design_count,
                  (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'prototype') as prototype_count
           FROM domains d
           ORDER BY d.domain_id"""
    )
    return [
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
        for r in cur.fetchall()
    ]


def generate_domain_index() -> str:
    """生成域总览索引MD文档。"""
    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        domains = get_all_domains(conn)
    finally:
        conn.close()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    # frontmatter
    lines.append("---")
    lines.append('doc_type: domain_index')
    lines.append('title: 域总览索引')
    lines.append('version: "1.0"')
    lines.append('status: active')
    lines.append(f'date: {now.split()[0]}')
    lines.append('owner: auto-generator')
    lines.append('ttl: permanent')
    lines.append("---")
    lines.append("")
    lines.append("# 域总览索引")
    lines.append("")
    lines.append("> 本文档由 generate_domain_index.py 从 depgraph.db 自动生成")
    lines.append(f"> 最后更新: {now}")
    lines.append("> 数据源: depgraph.db domains表 + nodes表")
    lines.append("")

    # 统计概览
    total_domains = len(domains)
    total_nodes = sum(d["actual_nodes"] for d in domains)
    total_production = sum(d["production_count"] for d in domains)
    total_design = sum(d["design_count"] for d in domains)
    total_prototype = sum(d["prototype_count"] for d in domains)

    lines.append("## 统计概览")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|-----|")
    lines.append(f"| 域总数 | {total_domains} |")
    lines.append(f"| 模块总数 | {total_nodes} |")
    lines.append(f"| 生产态模块 | {total_production} |")
    lines.append(f"| 设计态模块 | {total_design} |")
    lines.append(f"| 原型态模块 | {total_prototype} |")
    lines.append("")

    # 按架构层分组
    layers: dict[str, list[dict]] = {}
    for d in domains:
        layer = d["layer_id"] or "未分类"
        layers.setdefault(layer, []).append(d)

    lines.append("## 域清单（按架构层分组）")
    lines.append("")

    for layer in sorted(layers.keys()):
        layer_domains = layers[layer]
        lines.append(f"### {layer} ({len(layer_domains)} 个域)")
        lines.append("")
        lines.append("| 域ID | 域名称 | 模块数 | 生产态 | 设计态 | 原型态 | 容量 | 文档 |")
        lines.append("|------|--------|:---:|:---:|:---:|:---:|------|------|")
        for d in layer_domains:
            capacity = f"{d['actual_nodes']}/{d['max_modules']}"
            capacity_status = "OK" if d["actual_nodes"] <= d["max_modules"] else "超容"
            safe_name = d["domain_id"].replace("-", "_").lower()
            doc_link = f"[{safe_name}.md](domains/{safe_name}.md)"
            lines.append(
                f"| {d['domain_id']} | {d['domain_name']} | {d['actual_nodes']} | "
                f"{d['production_count']} | {d['design_count']} | {d['prototype_count']} | "
                f"{capacity} ({capacity_status}) | {doc_link} |"
            )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成域总览索引。"""
    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    content = generate_domain_index()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 生成 {OUTPUT_PATH} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
