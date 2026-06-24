# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_domain_doc
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
"""G2: 从 depgraph.db nodes+edges 表生成指定域的 MD 文档(含模块清单+内嵌Mermaid依赖图)

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_doc
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到02_domain_architecture_docs/
[MODIFY-GUARD] 修改需通过DM-200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看02_domain_architecture_docs/{编号}_{domain}.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1;域不存在→exit 2
[TESTS] tests/test_dm200910_generators.py
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from domain_name_mapping import get_domain_name_zh

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/02_domain_architecture_docs")

# 层级排序：编号按此顺序分组分配
LAYER_ORDER = ["L0_infrastructure", "L1_foundation", "L1_platform", "L2_domain"]


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


def get_domain_edges(conn: sqlite3.Connection, domain_id: str) -> list[dict]:
    """查询域内依赖边（from_node 和 to_node 都在本域）。

    返回每条边的两端节点路径、名称、设计成熟度，供 Mermaid 图使用。
    """
    cur = conn.execute(
        """SELECT e.from_node_id, e.to_node_id, e.dep_type, e.dep_maturity,
                  n1.path, n2.path, n1.design_maturity, n2.design_maturity,
                  n1.node_name, n2.node_name
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id=? AND n2.domain_id=?
           ORDER BY e.from_node_id, e.to_node_id""",
        (domain_id, domain_id),
    )
    edges = []
    for r in cur.fetchall():
        edges.append(
            {
                "from_node_id": r[0],
                "to_node_id": r[1],
                "dep_type": r[2] or "",
                "dep_maturity": r[3] or "",
                "from_path": r[4] or "",
                "to_path": r[5] or "",
                "from_maturity": r[6] or "",
                "to_maturity": r[7] or "",
                "from_name": r[8] or "",
                "to_name": r[9] or "",
            }
        )
    return edges


def get_cross_domain_deps(conn: sqlite3.Connection, domain_id: str) -> tuple[list[dict], list[dict]]:
    """查询跨域依赖（聚合统计）。

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


def get_cross_domain_edges_detail(
    conn: sqlite3.Connection, domain_id: str, internal_node_ids: list[int]
) -> tuple[list[dict], list[dict]]:
    """查询跨域边的详细信息（涉及指定内部节点的），供 Mermaid 图绘制外部节点和边。

    返回: (出边列表, 入边列表)，每条含 from_path/to_path/成熟度/外部域ID。
    """
    outgoing_edges: list[dict] = []
    incoming_edges: list[dict] = []
    if not internal_node_ids:
        return outgoing_edges, incoming_edges

    placeholders = ",".join("?" * len(internal_node_ids))
    params_out = [domain_id, domain_id] + list(internal_node_ids)

    # 出边：from 内部节点 → 外部节点
    cur = conn.execute(
        f"""SELECT e.dep_type, n1.path, n2.path, n1.design_maturity, n2.design_maturity,
                  n1.node_name, n2.node_name, n2.domain_id
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id=? AND n2.domain_id != ?
             AND e.from_node_id IN ({placeholders})
           LIMIT 15""",
        params_out,
    )
    for r in cur.fetchall():
        outgoing_edges.append(
            {
                "dep_type": r[0] or "",
                "from_path": r[1] or "",
                "to_path": r[2] or "",
                "from_maturity": r[3] or "",
                "to_maturity": r[4] or "",
                "from_name": r[5] or "",
                "to_name": r[6] or "",
                "ext_domain": r[7] or "",
            }
        )

    # 入边：from 外部节点 → 内部节点
    cur = conn.execute(
        f"""SELECT e.dep_type, n1.path, n2.path, n1.design_maturity, n2.design_maturity,
                  n1.node_name, n2.node_name, n1.domain_id
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n2.domain_id=? AND n1.domain_id != ?
             AND e.to_node_id IN ({placeholders})
           LIMIT 15""",
        params_out,
    )
    for r in cur.fetchall():
        incoming_edges.append(
            {
                "dep_type": r[0] or "",
                "from_path": r[1] or "",
                "to_path": r[2] or "",
                "from_maturity": r[3] or "",
                "to_maturity": r[4] or "",
                "from_name": r[5] or "",
                "to_name": r[6] or "",
                "ext_domain": r[7] or "",
            }
        )

    return outgoing_edges, incoming_edges


def sanitize_node_id(path: str) -> str:
    """将文件路径转为合法的 Mermaid 节点ID（只保留字母数字下划线）。"""
    if not path:
        return "node"
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", path)
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip("_")
    return sanitized or "node"


def _sanitize_mermaid_label(text: str) -> str:
    """清理 Mermaid 标签中的特殊字符（方括号/引号/管道符）。"""
    if not text:
        return ""
    return text.replace("[", "(").replace("]", ")").replace('"', "'").replace("|", "/")


def _sanitize_subgraph_label(text: str) -> str:
    """清理 subgraph 标签（额外移除斜杠）。"""
    return _sanitize_mermaid_label(text).replace("/", "_")


def generate_internal_mermaid(
    domain_id: str,
    domain_name: str,
    nodes: list[dict],
    edges: list[dict],
    outgoing: list[dict],
    incoming: list[dict],
) -> str:
    """生成内嵌 Mermaid 依赖图代码（单页，节点子集由调用方传入）。

    - graph TD 格式
    - subgraph 包裹本域模块
    - 实线箭头 --> = 运营态依赖（from和to都是production）
    - 虚线箭头 -.-> = 设计态依赖（任一方非production）
    - 跨域入边和出边用 external 节点表示
    - nodes 参数即当前页的节点子集，由调用方分页传入
    """
    displayed_node_ids = {n["node_id"] for n in nodes}

    lines = ["graph TD"]

    # subgraph 包裹本域模块
    subgraph_id = sanitize_node_id(domain_id)
    safe_domain_name = _sanitize_subgraph_label(domain_name)
    lines.append(f'    subgraph {subgraph_id}["{domain_id} {safe_domain_name}"]')

    # 节点定义 + 构建 path→mermaid_id 映射
    node_id_map: dict[int, str] = {}
    path_to_mermaid: dict[str, str] = {}
    used_ids: set[str] = set()
    for n in nodes:
        mermaid_id = sanitize_node_id(n["path"] or n["node_name"] or f"node{n['node_id']}")
        base_id = mermaid_id
        counter = 1
        while mermaid_id in used_ids:
            mermaid_id = f"{base_id}_{counter}"
            counter += 1
        used_ids.add(mermaid_id)
        node_id_map[n["node_id"]] = mermaid_id
        if n["path"]:
            path_to_mermaid[n["path"]] = mermaid_id

        label_name = _sanitize_mermaid_label(n["node_name"] or n["path"] or "unknown")
        if len(label_name) > 50:
            label_name = label_name[:47] + "..."
        maturity = n["design_maturity"] or "unknown"
        lines.append(f'        {mermaid_id}["{label_name} {maturity}"]')
    lines.append("    end")

    # 域内依赖边
    for e in edges:
        if e["from_node_id"] in displayed_node_ids and e["to_node_id"] in displayed_node_ids:
            from_id = node_id_map.get(e["from_node_id"], sanitize_node_id(e["from_path"]))
            to_id = node_id_map.get(e["to_node_id"], sanitize_node_id(e["to_path"]))
            if e["from_maturity"] == "production" and e["to_maturity"] == "production":
                arrow = "-->"
            else:
                arrow = "-.->"
            dep_label = _sanitize_mermaid_label(e["dep_type"]) or "dep"
            lines.append(f"    {from_id} {arrow}|{dep_label}| {to_id}")

    # 跨域外部节点
    external_nodes: dict[str, tuple[str, str]] = {}  # ext_domain -> (mermaid_id, maturity)

    def _get_or_create_external(ext_domain: str, maturity: str) -> str:
        if ext_domain in external_nodes:
            return external_nodes[ext_domain][0]
        ext_id = sanitize_node_id(ext_domain)
        base = ext_id
        idx = 1
        while ext_id in used_ids:
            ext_id = f"{base}_{idx}"
            idx += 1
        used_ids.add(ext_id)
        external_nodes[ext_domain] = (ext_id, maturity)
        ext_label = _sanitize_mermaid_label(ext_domain)
        lines.append(f'    {ext_id}["{ext_label} {maturity}"]')
        return ext_id

    # 跨域出边
    for e in outgoing:
        from_mermaid = path_to_mermaid.get(e["from_path"])
        if not from_mermaid:
            continue
        ext_id = _get_or_create_external(e["ext_domain"], e["to_maturity"] or "unknown")
        if e["from_maturity"] == "production" and e["to_maturity"] == "production":
            arrow = "-->"
        else:
            arrow = "-.->"
        dep_label = _sanitize_mermaid_label(e["dep_type"]) or "dep"
        lines.append(f"    {from_mermaid} {arrow}|{dep_label}| {ext_id}")

    # 跨域入边
    for e in incoming:
        to_mermaid = path_to_mermaid.get(e["to_path"])
        if not to_mermaid:
            continue
        ext_id = _get_or_create_external(e["ext_domain"], e["from_maturity"] or "unknown")
        if e["from_maturity"] == "production" and e["to_maturity"] == "production":
            arrow = "-->"
        else:
            arrow = "-.->"
        dep_label = _sanitize_mermaid_label(e["dep_type"]) or "dep"
        lines.append(f"    {ext_id} {arrow}|{dep_label}| {to_mermaid}")

    # classDef 样式（所有都加 color:#000 确保黑字）
    lines.append("    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000")
    lines.append("    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5")
    lines.append("    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000")
    lines.append(
        "    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5"
    )

    # 应用样式到内部节点
    prod_nodes = []
    design_nodes = []
    for n in nodes:
        mermaid_id = node_id_map[n["node_id"]]
        if n["design_maturity"] == "production":
            prod_nodes.append(mermaid_id)
        else:
            design_nodes.append(mermaid_id)
    if prod_nodes:
        lines.append(f"    class {','.join(prod_nodes)} production")
    if design_nodes:
        lines.append(f"    class {','.join(design_nodes)} design")

    # 应用样式到外部节点
    ext_prod = []
    ext_design = []
    for ext_domain, (ext_id, maturity) in external_nodes.items():
        if maturity == "production":
            ext_prod.append(ext_id)
        else:
            ext_design.append(ext_id)
    if ext_prod:
        lines.append(f"    class {','.join(ext_prod)} external_prod")
    if ext_design:
        lines.append(f"    class {','.join(ext_design)} external_design")

    return "\n".join(lines)


def build_numbering_map(conn: sqlite3.Connection) -> dict[str, int]:
    """构建域编号映射：按 layer_id 分组排序，生成 {domain_id: number} 映射。

    层级顺序: L0_infrastructure(01-02) → L1_foundation(03-08) → L1_platform(09-15) → L2_domain(16-53)
    """
    cur = conn.execute("SELECT domain_id, layer_id FROM domains")
    domains = [(r[0], r[1] or "") for r in cur.fetchall()]

    def _sort_key(item: tuple[str, str]) -> tuple[int, str]:
        layer = item[1]
        layer_idx = LAYER_ORDER.index(layer) if layer in LAYER_ORDER else len(LAYER_ORDER)
        return (layer_idx, item[0])

    domains.sort(key=_sort_key)
    return {did: idx + 1 for idx, (did, _) in enumerate(domains)}


def generate_domain_doc(domain_id: str, conn: sqlite3.Connection, number: int = 0) -> str:
    """生成域文档内容（中英文对照表格 + 内嵌 Mermaid 依赖图）。"""
    info = get_domain_info(conn, domain_id)
    if not info:
        print(f"ERROR: 域 '{domain_id}' 不存在", file=sys.stderr)
        return ""

    nodes = get_domain_nodes(conn, domain_id)
    edges = get_domain_edges(conn, domain_id)
    outgoing_agg, incoming_agg = get_cross_domain_deps(conn, domain_id)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 统计
    design_count = sum(1 for n in nodes if n["design_maturity"] == "design")
    production_count = sum(1 for n in nodes if n["design_maturity"] == "production")
    prototype_count = sum(1 for n in nodes if n["design_maturity"] == "prototype")
    capacity_status = "正常" if info["current_modules"] <= info["max_modules"] else "超容"
    total_outgoing = sum(d["count"] for d in outgoing_agg)
    total_incoming = sum(d["count"] for d in incoming_agg)

    lines = []
    # frontmatter（G1 门禁要求：doc_type, title, version, status, date, owner, ttl）
    lines.append("---")
    lines.append("doc_type: domain_architecture_doc")
    lines.append(f"title: {domain_id} {get_domain_name_zh(domain_id, info['domain_name'])}架构文档")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split()[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append(f"# {number:02d}_{domain_id.replace('-', '_').lower()} / {get_domain_name_zh(domain_id, info['domain_name'])}")
    lines.append("")
    lines.append(f"> **文档作用 / Purpose**: 展示 {get_domain_name_zh(domain_id, info['domain_name'])}（{domain_id}）功能域的模块清单、域内依赖关系和跨域依赖关系，供架构审查和域治理参考。")
    lines.append("")
    lines.append("> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成")
    lines.append(f"> 最后更新: {now}")
    lines.append("> 数据源: depgraph.db nodes表 + edges表")
    lines.append("")

    # 域基本信息（中英文对照）
    lines.append("## 域基本信息 / Domain Overview")
    lines.append("")
    lines.append("| 字段 | 值 | Field | Value |")
    lines.append("|------|------|-------|-------|")
    lines.append(f"| 编号 | {number:02d} | Number | {number:02d} |")
    lines.append(f"| 域ID | {domain_id} | Domain ID | {domain_id} |")
    lines.append(f"| 域名称 | {get_domain_name_zh(domain_id, info['domain_name'])} | Domain Name | {info['domain_name']} |")
    lines.append(f"| 层级 | {info['layer_id']} | Layer | {info['layer_id']} |")
    lines.append(f"| 模块数 | {len(nodes)} | Module Count | {len(nodes)} |")
    lines.append(f"| 域内依赖 | {len(edges)} | Internal Dependencies | {len(edges)} |")
    lines.append(f"| 跨域入边 | {total_incoming} | Cross-domain Incoming | {total_incoming} |")
    lines.append(f"| 跨域出边 | {total_outgoing} | Cross-domain Outgoing | {total_outgoing} |")
    lines.append(f"| 设计态模块 | {design_count} | Design Modules | {design_count} |")
    lines.append(f"| 原型态模块 | {prototype_count} | Prototype Modules | {prototype_count} |")
    lines.append(f"| 生产态模块 | {production_count} | Production Modules | {production_count} |")
    lines.append(
        f"| 容量 | {info['current_modules']}/{info['max_modules']} ({capacity_status}) | "
        f"Capacity | {info['current_modules']}/{info['max_modules']} ({capacity_status}) |"
    )
    if info["description"]:
        lines.append(f"| 描述 | {info['description']} | Description | {info['description']} |")
    lines.append("")

    # 模块清单（中英文对照）
    lines.append("## 模块清单 / Module List")
    lines.append("")
    lines.append(f"共 {len(nodes)} 个模块（按路径排序，全部显示）")
    lines.append("")
    lines.append(
        "| 模块路径 / Module Path | 模块名称 / Module Name | 设计成熟度 / Maturity | 构建状态 / Build Status |"
    )
    lines.append("|---------|---------|-----------|---------|")
    for n in nodes:
        path_display = n["path"] if len(n["path"]) <= 80 else "..." + n["path"][-77:]
        name_display = n["node_name"] if len(n["node_name"]) <= 40 else n["node_name"][:37] + "..."
        lines.append(
            f"| {path_display} | {name_display} | {n['design_maturity']} | {n['build_status']} |"
        )
    lines.append("")

    # 域内依赖图（内嵌 Mermaid，分页显示全部节点）
    lines.append("## 域内依赖图 / Internal Dependency Diagram")
    lines.append("")
    lines.append("> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。")
    lines.append(">")
    lines.append("> **图例说明 / Legend**：")
    lines.append("> - **实线边框 = 运营态模块**（production，已上线运行）")
    lines.append("> - **虚线边框 = 设计态模块**（design，还在设计中）")
    lines.append("> - **实线箭头 = 运营态依赖**（已生效的依赖关系）")
    lines.append("> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）")
    lines.append("")

    PAGE_SIZE = 30
    total_pages = (len(nodes) + PAGE_SIZE - 1) // PAGE_SIZE if nodes else 1
    for page_idx in range(total_pages):
        start = page_idx * PAGE_SIZE
        end = start + PAGE_SIZE
        page_nodes = nodes[start:end]
        page_node_ids = {n["node_id"] for n in page_nodes}
        # 跨域边详情（仅涉及当前页节点）
        page_outgoing, page_incoming = get_cross_domain_edges_detail(conn, domain_id, [n["node_id"] for n in page_nodes])

        if total_pages > 1:
            lines.append(f"### 第 {page_idx + 1} 页 / 共 {total_pages} 页 / Page {page_idx + 1} of {total_pages}")
            lines.append("")

        mermaid_code = generate_internal_mermaid(
            domain_id, get_domain_name_zh(domain_id, info["domain_name"]), page_nodes, edges, page_outgoing, page_incoming
        )
        lines.append("```mermaid")
        lines.append(mermaid_code)
        lines.append("```")
        lines.append("")

    # 跨域依赖（中英文对照）
    lines.append("## 跨域依赖 / Cross-domain Dependencies")
    lines.append("")

    # 本域依赖的其他域
    lines.append("### 本域依赖的其他域（出边）/ Depends On")
    lines.append("")
    if outgoing_agg:
        lines.append("| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |")
        lines.append("|--------|:---:|---------|")
        for d in outgoing_agg:
            lines.append(f"| {d['target_domain']} | {d['count']} | {d['dep_types']} |")
    else:
        lines.append("无跨域出边依赖 / No cross-domain outgoing dependencies")
    lines.append("")

    # 依赖本域的其他域
    lines.append("### 依赖本域的其他域（入边）/ Depended By")
    lines.append("")
    if incoming_agg:
        lines.append("| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |")
        lines.append("|------|:---:|---------|")
        for d in incoming_agg:
            lines.append(f"| {d['source_domain']} | {d['count']} | {d['dep_types']} |")
    else:
        lines.append("无跨域入边依赖 / No cross-domain incoming dependencies")
    lines.append("")

    # 说明
    lines.append("## 说明 / Notes")
    lines.append("")
    lines.append("- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表")
    lines.append("- **生成器 / Generator**: `generate_domain_doc.py`")
    lines.append("- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新")
    lines.append("- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成指定域的 MD 文档。"""
    parser = argparse.ArgumentParser(description="G2: 生成域架构文档(含内嵌Mermaid依赖图)")
    parser.add_argument(
        "domain_id",
        type=str,
        nargs="?",
        default=None,
        help="域ID (如 D-TRADING)。--all 模式下可省略",
    )
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--all", action="store_true", help="生成所有域的文档")
    args = parser.parse_args()

    if not args.all and not args.domain_id:
        parser.error("domain_id 是必填参数（除非使用 --all）")

    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        # 构建编号映射（按 layer_id 分组排序）
        numbering_map = build_numbering_map(conn)

        if args.all:
            # 生成所有域的文档
            cur = conn.execute("SELECT domain_id FROM domains ORDER BY domain_id")
            domain_ids = [r[0] for r in cur.fetchall()]
            success = 0
            for did in domain_ids:
                number = numbering_map.get(did, 0)
                content = generate_domain_doc(did, conn, number)
                if content:
                    safe_name = did.replace("-", "_").lower()
                    out_path = output_dir / f"{number:02d}_{safe_name}.md"
                    out_path.write_text(content, encoding="utf-8", newline="\n")
                    print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
                    success += 1
            print(f"\n共生成 {success}/{len(domain_ids)} 个域文档")
        else:
            # 生成单个域的文档
            number = numbering_map.get(args.domain_id, 0)
            content = generate_domain_doc(args.domain_id, conn, number)
            if not content:
                sys.exit(2)
            safe_name = args.domain_id.replace("-", "_").lower()
            out_path = output_dir / f"{number:02d}_{safe_name}.md"
            out_path.write_text(content, encoding="utf-8", newline="\n")
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
