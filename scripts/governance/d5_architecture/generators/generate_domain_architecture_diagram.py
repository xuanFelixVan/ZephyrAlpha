# [BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
# [MODULE] scripts.governance.d5_architecture.generators.generate_domain_architecture_diagram
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] depgraph.db(nodes,edges,domains)
# [CONSUMERS] CI自动触发;人工查看02_domain_architecture_docs/{编号}_{域名}_architecture.md
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到02_domain_architecture_docs/
# [MODIFY-GUARD] 修改需通过任务卡
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph.db不存在→exit 1;域不存在→exit 2
# [TESTS] tests/test_dm200910_generators.py
"""G10: 从 depgraph.db 为每个功能域生成ASCII架构图文档(可视化分层架构+依赖关系)

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_architecture_diagram
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db;输出到02_domain_architecture_docs/
[MODIFY-GUARD] 修改需通过任务卡
[CONSUMERS] CI自动触发;人工查看02_domain_architecture_docs/{编号}_{域名}_architecture.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1;域不存在→exit 2
[TESTS] tests/test_dm200910_generators.py
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from domain_name_mapping import get_domain_name_zh

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/02_domain_architecture_docs")

# 层级排序：编号按此顺序分组分配（复制自 generate_domain_doc.py，保持生成器独立）
LAYER_ORDER = ["L0_infrastructure", "L1_foundation", "L1_platform", "L2_domain"]

# 层级中文显示名映射
LAYER_DISPLAY = {
    "L0_infrastructure": "L0 基础设施层 / Infrastructure Layer",
    "L1_foundation": "L1 基础层 / Foundation Layer",
    "L1_platform": "L1 平台层 / Platform Layer",
    "L2_domain": "L2 领域层 / Domain Layer",
    "L3_application": "L3 应用层 / Application Layer",
}

# ASCII box 内部宽度
BOX_WIDTH = 64


# ---------------------------------------------------------------------------
# 数据库查询函数（复制自 generate_domain_doc.py，保持生成器独立）
# ---------------------------------------------------------------------------


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

    返回每条边的两端节点路径、名称、设计成熟度，供依赖图使用。
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


# ---------------------------------------------------------------------------
# ASCII art 辅助函数
# ---------------------------------------------------------------------------


def _display_width(s: str) -> int:
    """计算字符串显示宽度（CJK字符算2，其余算1）。"""
    width = 0
    for ch in s:
        code = ord(ch)
        if (
            0x4E00 <= code <= 0x9FFF
            or 0x3000 <= code <= 0x303F
            or 0xFF00 <= code <= 0xFFEF
            or 0x2E80 <= code <= 0x2EFF
            or 0x3400 <= code <= 0x4DBF
        ):
            width += 2
        else:
            width += 1
    return width


def _pad_to_width(s: str, width: int) -> str:
    """按显示宽度右填充空格到指定宽度。"""
    current = _display_width(s)
    if current >= width:
        return s
    return s + " " * (width - current)


def _truncate(text: str, max_len: int = 40) -> str:
    """截断文本到指定显示宽度，超出则加'...'。"""
    if not text:
        return ""
    if _display_width(text) <= max_len:
        return text
    # 按显示宽度截断
    result = ""
    w = 0
    for ch in text:
        cw = 2 if ord(ch) > 0x7F else 1
        if w + cw > max_len - 3:
            break
        result += ch
        w += cw
    return result + "..."


def _layer_sort_key(layer: str) -> tuple[int, str]:
    """层级排序键：LAYER_ORDER 优先，其余按字母序，空值最后。"""
    if layer in LAYER_ORDER:
        return (LAYER_ORDER.index(layer), layer)
    elif layer:
        return (len(LAYER_ORDER), layer)
    else:
        return (len(LAYER_ORDER) + 1, "")


def _make_box(title: str, content_lines: list[str], width: int = BOX_WIDTH) -> list[str]:
    """生成ASCII box（带标题行和内容行）。

    结构:
    ┌──────┐
    │ title │  (居中)
    ├──────┤
    │ line │  (左对齐)
    └──────┘
    """
    inner = width
    top = "┌" + "─" * (inner + 2) + "┐"
    bottom = "└" + "─" * (inner + 2) + "┘"
    separator = "├" + "─" * (inner + 2) + "┤"

    lines = [top]
    # 标题行（居中）
    title_w = _display_width(title)
    if title_w >= inner:
        title_padded = _truncate(title, inner)
    else:
        left_pad = (inner - title_w) // 2
        title_padded = " " * left_pad + title
    lines.append(f"│ {_pad_to_width(title_padded, inner)} │")

    if content_lines:
        lines.append(separator)
        for line in content_lines:
            line_trunc = _truncate(line, inner)
            lines.append(f"│ {_pad_to_width(line_trunc, inner)} │")

    lines.append(bottom)
    return lines


def _arrow_down(width: int = BOX_WIDTH) -> list[str]:
    """生成向下箭头（层间连接）。"""
    center = width // 2 + 2  # +2 for "│ " prefix offset
    return [" " * center + "│", " " * center + "▼"]


# ---------------------------------------------------------------------------
# 文档章节生成函数
# ---------------------------------------------------------------------------


def generate_ascii_architecture_overview(
    domain_id: str, domain_name: str, nodes: list[dict]
) -> str:
    """生成ASCII架构全景图（按 architecture_layer 分层显示）。

    - 按 architecture_layer 分组节点
    - 每层一个ASCII box，最多显示20个模块（超过显示前18个+"...还有N个"）
    - 层与层之间用箭头连接
    """
    # 按 architecture_layer 分组
    layer_groups: dict[str, list[dict]] = {}
    for n in nodes:
        layer = n["architecture_layer"] or ""
        layer_groups.setdefault(layer, []).append(n)

    # 排序层级
    sorted_layers = sorted(layer_groups.keys(), key=_layer_sort_key)

    if not sorted_layers:
        return "（无模块 / No modules）\n"

    lines: list[str] = []
    lines.append("```")
    lines.append("")

    for idx, layer in enumerate(sorted_layers):
        layer_nodes = layer_groups[layer]
        display_name = LAYER_DISPLAY.get(layer, layer) if layer else "未分类 / Unclassified"
        count = len(layer_nodes)

        # 最多显示20个模块（前18 + "...还有N个"）
        MAX_PER_LAYER = 20
        if count <= MAX_PER_LAYER:
            shown = layer_nodes
            more_count = 0
        else:
            shown = layer_nodes[: MAX_PER_LAYER - 2]
            more_count = count - (MAX_PER_LAYER - 2)

        # 构建内容行：每行一个模块名
        content = []
        for n in shown:
            name = n["node_name"] or n["path"] or f"node_{n['node_id']}"
            maturity = n["design_maturity"] or "unknown"
            content.append(f"  {name}  [{maturity}]")

        if more_count > 0:
            content.append(f"  ...还有 {more_count} 个模块 / {more_count} more modules")

        title = f"{display_name} ({count} modules)"
        box_lines = _make_box(title, content)

        # 层间箭头
        if idx > 0:
            lines.extend(_arrow_down())

        lines.extend(box_lines)

    lines.append("")
    lines.append("```")
    return "\n".join(lines)


def generate_module_layered_list(nodes: list[dict]) -> str:
    """生成模块分层清单表格（按 architecture_layer 分组，中英文表头）。"""
    # 按 architecture_layer 分组
    layer_groups: dict[str, list[dict]] = {}
    for n in nodes:
        layer = n["architecture_layer"] or ""
        layer_groups.setdefault(layer, []).append(n)

    sorted_layers = sorted(layer_groups.keys(), key=_layer_sort_key)

    if not sorted_layers:
        return "（无模块 / No modules）\n"

    lines: list[str] = []

    MAX_PER_LAYER = 200
    for layer in sorted_layers:
        layer_nodes = layer_nodes_all = layer_groups[layer]
        display_name = LAYER_DISPLAY.get(layer, layer) if layer else "未分类 / Unclassified"

        lines.append(f"### {display_name} ({len(layer_nodes_all)} modules)")
        lines.append("")

        shown = layer_nodes_all[:MAX_PER_LAYER]
        lines.append(
            "| # | 模块路径 / Module Path | 模块名称 / Module Name | "
            "成熟度 / Maturity | 构建状态 / Build Status |"
        )
        lines.append("|:--:|---------|---------|:---:|:---:|")

        for i, n in enumerate(shown, 1):
            path_display = _truncate(n["path"] or "", 60)
            name_display = _truncate(n["node_name"] or n["path"] or "", 40)
            lines.append(
                f"| {i} | {path_display} | {name_display} | "
                f"{n['design_maturity']} | {n['build_status']} |"
            )

        if len(layer_nodes_all) > MAX_PER_LAYER:
            lines.append(f"\n> (仅显示前 {MAX_PER_LAYER} 个模块，共 {len(layer_nodes_all)} 个)")
        lines.append("")

    return "\n".join(lines)


def _display_edge_name(name: str, path: str, max_len: int = 28) -> str:
    """生成依赖边的节点显示名：优先 node_name，否则用 path 的 basename。"""
    if name:
        return _truncate(name, max_len)
    if path:
        # 用 basename 提高可读性（如 auto_dispatcher.py 而非完整路径）
        base = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        return _truncate(base, max_len)
    return "?"


def generate_ascii_dependency_graph(edges: list[dict]) -> str:
    """生成ASCII依赖关系图（按 dep_type 分组显示域内依赖边）。

    - 按 dep_type 分组
    - 最多显示50条依赖边（超过显示前48条+"...还有N条"）
    - 使用 → 表示方向
    """
    if not edges:
        return "（无域内依赖 / No internal dependencies）\n"

    # 按 dep_type 分组
    type_groups: dict[str, list[dict]] = {}
    for e in edges:
        dtype = e["dep_type"] or "unknown"
        type_groups.setdefault(dtype, []).append(e)

    # 排序 dep_type（按数量降序）
    sorted_types = sorted(type_groups.keys(), key=lambda t: -len(type_groups[t]))

    MAX_EDGES = 50
    total = len(edges)

    lines: list[str] = []
    lines.append("```")
    lines.append("")

    # 总览 box
    overview_title = f"依赖关系图 / Dependency Graph (共 {total} 条 / {total} edges)"
    overview_content = [f"  依赖类型数 / Dependency Types: {len(sorted_types)}"]
    for dtype in sorted_types:
        overview_content.append(
            f"  [{dtype}]: {len(type_groups[dtype])} 条 / edges"
        )
    lines.extend(_make_box(overview_title, overview_content))
    lines.append("")

    # 分组详情
    shown_total = 0
    for dtype in sorted_types:
        group_edges = type_groups[dtype]
        remaining = MAX_EDGES - shown_total
        # 剩余空间不足以显示至少1条边时，输出摘要行而非空box
        if remaining <= 1:
            lines.append(f"**[{dtype}]** ({len(group_edges)} 条 / edges) — 已达显示上限，省略 / limit reached")
            lines.append("")
            continue

        if len(group_edges) <= remaining:
            shown = group_edges
            more = 0
        else:
            shown = group_edges[: remaining - 1]
            more = len(group_edges) - (remaining - 1)

        shown_total += len(shown)

        group_title = f"[{dtype}] ({len(group_edges)} 条 / edges)"
        content = []
        for e in shown:
            from_name = _display_edge_name(e["from_name"], e["from_path"])
            to_name = _display_edge_name(e["to_name"], e["to_path"])
            content.append(f"  {from_name} → {to_name}")

        if more > 0:
            content.append(f"  ...还有 {more} 条 / {more} more edges")

        lines.extend(_make_box(group_title, content))
        lines.append("")

    if total > MAX_EDGES:
        lines.append(f"> (最多显示前 {MAX_EDGES} 条依赖边，共 {total} 条)")
        lines.append("")

    lines.append("```")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主文档生成
# ---------------------------------------------------------------------------


def generate_domain_architecture_diagram(
    domain_id: str, conn: sqlite3.Connection, number: int = 0
) -> str:
    """生成域架构图文档完整内容。"""
    info = get_domain_info(conn, domain_id)
    if not info:
        print(f"ERROR: 域 '{domain_id}' 不存在", file=sys.stderr)
        return ""

    nodes = get_domain_nodes(conn, domain_id)
    edges = get_domain_edges(conn, domain_id)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_name = domain_id.replace("-", "_").lower()
    domain_name = get_domain_name_zh(domain_id, info["domain_name"])

    lines: list[str] = []

    # frontmatter
    lines.append("---")
    lines.append("doc_type: domain_architecture_diagram")
    lines.append(f"title: {domain_id} {domain_name}架构图")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split()[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")

    # 标题
    lines.append(f"# {number:02d}_{safe_name} / {domain_name} 架构图")
    lines.append("")
    lines.append(
        f"> **文档作用 / Purpose**: 以ASCII art可视化展示{domain_name}（{domain_id}）"
        "功能域的模块分层架构和依赖关系。"
    )
    lines.append("")
    lines.append("> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成")
    lines.append(f"> 最后更新 / Last Updated: {now}")
    lines.append("> 数据源 / Data Source: depgraph.db nodes表 + edges表")
    lines.append("")

    # 架构全景图
    lines.append("## 架构全景图 / Architecture Overview")
    lines.append("")
    lines.append(
        f"> 按 architecture_layer 分层显示 {domain_name}（{domain_id}）的模块分布。"
        f"共 {len(nodes)} 个模块 / {len(nodes)} modules。"
    )
    lines.append("")
    lines.append(generate_ascii_architecture_overview(domain_id, domain_name, nodes))
    lines.append("")

    # 模块分层清单
    lines.append("## 模块分层清单 / Module Layered List")
    lines.append("")
    lines.append(
        f"> 按 architecture_layer 分组的模块清单（共 {len(nodes)} 个模块 / {len(nodes)} modules）。"
    )
    lines.append("")
    lines.append(generate_module_layered_list(nodes))

    # 依赖关系图
    lines.append("## 依赖关系图 / Dependency Graph")
    lines.append("")
    lines.append(
        f"> 域内模块依赖关系（共 {len(edges)} 条 / {len(edges)} edges）。"
        "按依赖类型分组，使用 → 表示方向。"
    )
    lines.append("")
    lines.append(generate_ascii_dependency_graph(edges))
    lines.append("")

    # 说明
    lines.append("## 说明 / Notes")
    lines.append("")
    lines.append("- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表")
    lines.append("- **生成器 / Generator**: `generate_domain_architecture_diagram.py`")
    lines.append("- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新")
    lines.append(
        "- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，"
        f"如 `{number:02d}_{safe_name}_architecture.md`"
    )
    lines.append(
        "- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / "
        "`[prototype]`=原型 / `[unknown]`=未知"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 原子写入
# ---------------------------------------------------------------------------


def _atomic_write(path: Path, content: str) -> None:
    """原子写入文件（tmp文件 + os.replace）。"""
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main() -> None:
    """入口：生成指定域的ASCII架构图文档。"""
    parser = argparse.ArgumentParser(
        description="G10: 为每个功能域生成ASCII架构图文档(可视化分层架构+依赖关系)"
    )
    parser.add_argument(
        "domain_id",
        type=str,
        nargs="?",
        default=None,
        help="域ID (如 D-TRADING)。--all 模式下可省略",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(OUTPUT_DIR),
        help="输出目录 (默认: 02_domain_architecture_docs)",
    )
    parser.add_argument("--all", action="store_true", help="生成所有域的架构图")
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
        numbering_map = build_numbering_map(conn)

        if args.all:
            cur = conn.execute("SELECT domain_id FROM domains ORDER BY domain_id")
            domain_ids = [r[0] for r in cur.fetchall()]
            success = 0
            for did in domain_ids:
                number = numbering_map.get(did, 0)
                content = generate_domain_architecture_diagram(did, conn, number)
                if content:
                    safe_name = did.replace("-", "_").lower()
                    out_path = output_dir / f"{number:02d}_{safe_name}_architecture.md"
                    _atomic_write(out_path, content)
                    print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
                    success += 1
            print(f"\n共生成 {success}/{len(domain_ids)} 个域架构图")
        else:
            number = numbering_map.get(args.domain_id, 0)
            content = generate_domain_architecture_diagram(args.domain_id, conn, number)
            if not content:
                sys.exit(2)
            safe_name = args.domain_id.replace("-", "_").lower()
            out_path = output_dir / f"{number:02d}_{safe_name}_architecture.md"
            _atomic_write(out_path, content)
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
