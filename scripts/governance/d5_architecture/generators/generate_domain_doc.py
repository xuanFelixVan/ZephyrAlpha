"""G2: 从 depgraph.db nodes+edges 表生成指定域的 MD 文档(含模块清单+依赖图)

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_doc
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到generated/domains/
[MODIFY-GUARD] 修改需通过DM-200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/domains/{domain}.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1;域不存在→exit 2
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
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/generated/domains")


def get_domain_info(conn: sqlite3.Connection, domain_id: str) -> dict | None:
    """查询域基本信息。"""
    cur = conn.execute(
        "SELECT domain_id, domain_name, current_modules, max_modules, layer_id, description "
        "FROM domains WHERE domain_id=?",
        (domain_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "domain_id": row[0],
        "domain_name": row[1] or "",
        "current_modules": row[2] or 0,
        "max_modules": row[3] or 200,
        "layer_id": row[4] or "",
        "description": row[5] or "",
    }


def get_domain_nodes(conn: sqlite3.Connection, domain_id: str) -> list[dict]:
    """查询指定域的所有节点。"""
    cur = conn.execute(
        "SELECT node_id, path, blueprint_id, design_maturity, build_status, node_name, "
        "in_degree, out_degree, architecture_layer, file_path "
        "FROM nodes WHERE domain_id=? ORDER BY path",
        (domain_id,),
    )
    rows = []
    for r in cur.fetchall():
        rows.append(
            {
                "node_id": r[0],
                "path": r[1] or "",
                "blueprint_id": r[2] or "",
                "design_maturity": r[3] or "",
                "build_status": r[4] or "",
                "node_name": r[5] or "",
                "in_degree": r[6] or 0,
                "out_degree": r[7] or 0,
                "architecture_layer": r[8] or "",
                "file_path": r[9] or "",
            }
        )
    return rows


def get_cross_domain_deps(conn: sqlite3.Connection, domain_id: str) -> tuple[list[dict], list[dict]]:
    """查询跨域依赖。

    返回: (本域依赖的其他域列表, 依赖本域的其他域列表)
    """
    # 本域依赖的其他域（出边：from_node 在本域，to_node 在其他域）
    cur = conn.execute(
        """SELECT n2.domain_id as target_domain, COUNT(*) as cnt,
                  GROUP_CONCAT(DISTINCT e.dep_type) as dep_types
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id=? AND n2.domain_id != ?
           GROUP BY n2.domain_id
           ORDER BY cnt DESC""",
        (domain_id, domain_id),
    )
    outgoing = []
    for r in cur.fetchall():
        outgoing.append({"target_domain": r[0], "count": r[1], "dep_types": r[2] or ""})

    # 依赖本域的其他域（入边：from_node 在其他域，to_node 在本域）
    cur = conn.execute(
        """SELECT n1.domain_id as source_domain, COUNT(*) as cnt,
                  GROUP_CONCAT(DISTINCT e.dep_type) as dep_types
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n2.domain_id=? AND n1.domain_id != ?
           GROUP BY n1.domain_id
           ORDER BY cnt DESC""",
        (domain_id, domain_id),
    )
    incoming = []
    for r in cur.fetchall():
        incoming.append({"source_domain": r[0], "count": r[1], "dep_types": r[2] or ""})

    return outgoing, incoming


def generate_domain_doc(domain_id: str, conn: sqlite3.Connection) -> str:
    """生成域文档内容。"""
    info = get_domain_info(conn, domain_id)
    if not info:
        print(f"ERROR: 域 '{domain_id}' 不存在", file=sys.stderr)
        return ""

    nodes = get_domain_nodes(conn, domain_id)
    outgoing, incoming = get_cross_domain_deps(conn, domain_id)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 统计
    design_count = sum(1 for n in nodes if n["design_maturity"] == "design")
    production_count = sum(1 for n in nodes if n["design_maturity"] == "production")
    prototype_count = sum(1 for n in nodes if n["design_maturity"] == "prototype")
    capacity_status = "正常" if info["current_modules"] <= info["max_modules"] else "超容"

    lines = []
    lines.append(f"# {domain_id} {info['domain_name']}架构文档")
    lines.append("")
    lines.append("> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成")
    lines.append(f"> 最后更新: {now}")
    lines.append("> 数据源: depgraph.db nodes表 + edges表")
    lines.append("")

    # 域概览
    lines.append("## 域概览")
    lines.append("")
    lines.append("| 属性 | 值 |")
    lines.append("|------|-----|")
    lines.append(f"| 域ID | {domain_id} |")
    lines.append(f"| 域名称 | {info['domain_name']} |")
    lines.append(f"| 架构层 | {info['layer_id']} |")
    lines.append(f"| 模块总数 | {len(nodes)} |")
    lines.append(f"| 设计态模块 | {design_count} |")
    lines.append(f"| 原型态模块 | {prototype_count} |")
    lines.append(f"| 生产态模块 | {production_count} |")
    lines.append(f"| 容量 | {info['current_modules']}/{info['max_modules']} ({capacity_status}) |")
    if info["description"]:
        lines.append(f"| 描述 | {info['description']} |")
    lines.append("")

    # 模块清单
    lines.append("## 模块清单")
    lines.append("")
    lines.append(f"共 {len(nodes)} 个模块（按路径排序，最多显示前 200 个）")
    lines.append("")
    lines.append("| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |")
    lines.append("|---------|--------|---------|-----------|:---:|:---:|")

    MAX_NODES = 200
    for n in nodes[:MAX_NODES]:
        path_display = n["path"] if len(n["path"]) <= 80 else "..." + n["path"][-77:]
        lines.append(
            f"| {path_display} | {n['blueprint_id']} | {n['build_status']} | "
            f"{n['design_maturity']} | {n['in_degree']} | {n['out_degree']} |"
        )

    if len(nodes) > MAX_NODES:
        lines.append(f"\n> (仅显示前 {MAX_NODES} 个模块，共 {len(nodes)} 个)")
    lines.append("")

    # 跨域依赖
    lines.append("## 跨域依赖")
    lines.append("")

    # 本域依赖的其他域
    lines.append("### 本域依赖的其他域（出边）")
    lines.append("")
    if outgoing:
        lines.append("| 目标域 | 依赖数 | 依赖类型 |")
        lines.append("|--------|:---:|---------|")
        for d in outgoing:
            lines.append(f"| {d['target_domain']} | {d['count']} | {d['dep_types']} |")
    else:
        lines.append("无跨域出边依赖")
    lines.append("")

    # 依赖本域的其他域
    lines.append("### 依赖本域的其他域（入边）")
    lines.append("")
    if incoming:
        lines.append("| 源域 | 依赖数 | 依赖类型 |")
        lines.append("|------|:---:|---------|")
        for d in incoming:
            lines.append(f"| {d['source_domain']} | {d['count']} | {d['dep_types']} |")
    else:
        lines.append("无跨域入边依赖")
    lines.append("")

    # 依赖图引用（文件名用小写 snake_case）
    safe_name_ref = domain_id.replace("-", "_").lower()
    lines.append("## 域内依赖图")
    lines.append("")
    lines.append(f"详见 [{safe_name_ref}_dependency.mmd]({safe_name_ref}_dependency.mmd)")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成指定域的 MD 文档。"""
    parser = argparse.ArgumentParser(description="G2: 生成域架构文档")
    parser.add_argument("domain_id", type=str, help="域ID (如 D-TRADING)")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--all", action="store_true", help="生成所有域的文档")
    args = parser.parse_args()

    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        if args.all:
            # 生成所有域的文档
            cur = conn.execute("SELECT domain_id FROM domains ORDER BY domain_id")
            domain_ids = [r[0] for r in cur.fetchall()]
            success = 0
            for did in domain_ids:
                content = generate_domain_doc(did, conn)
                if content:
                    # 文件名用下划线替换连字符（文件系统友好）
                    safe_name = did.replace("-", "_").lower()
                    out_path = output_dir / f"{safe_name}.md"
                    out_path.write_text(content, encoding="utf-8")
                    print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
                    success += 1
            print(f"\n共生成 {success}/{len(domain_ids)} 个域文档")
        else:
            # 生成单个域的文档
            content = generate_domain_doc(args.domain_id, conn)
            if not content:
                sys.exit(2)
            safe_name = args.domain_id.replace("-", "_").lower()
            out_path = output_dir / f"{safe_name}.md"
            out_path.write_text(content, encoding="utf-8")
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
