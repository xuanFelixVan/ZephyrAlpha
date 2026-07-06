# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.d5_architecture.generators.generate_decision_diagram
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); architecture_model/domain/decision_graph_model.yaml (invariants 真源)
# [CONSUMERS] CI自动触发;人工查看generated/decisions/
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读decisiongraph;输出到generated/decisions/
# [MODIFY-GUARD] 修改需通过TRAE-061任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] decisiongraph不存在→exit 1;无tracks/layers→exit 2
# [TESTS] tests/test_generate_decision_diagram.py
# [TTL] permanent
"""G-decision: 从 decisiongraph (PostgreSQL) 生成决策流图(.mmd Mermaid格式 + .md 文档)

依据：TRAE-061 任务（2026-07-06）

功能：
  - 从 decision_tracks / decision_layers / decision_nodes / decision_edges 表读取决策流图
  - 从 decision_graph_model.yaml 读取 invariants 定义（5 条承重墙不变量）
  - 生成 Mermaid 图表（flowchart TD/LR）
  - 输出到 docs/02_enterprise_architecture/generated/decisions/

输出文件：
  - decision_overview.mmd          全景图（L0-L6 层级 + 四轨并行 + 节点/边）
  - decision_layers.mmd            层级详情图（10 层卡片 + 频率/成熟度/状态）
  - decision_invariants.mmd        不变量图（6 节点类型 + 5 不变量 + 合法/非法连接）
  - decision_index.md              索引文档（含统计+图嵌入+tracks/layers 清单）

用法
----
    python scripts/governance/d5_architecture/generators/generate_decision_diagram.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from _common import DB_DISPLAY_NAME  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

from zephyr.governance.persistence.decisiongraph_schema import (  # noqa: E402
    get_decisiongraph_pg_connection,
)

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "generated" / "decisions"
_YAML_PATH = _REPO_ROOT / "architecture_model" / "domain" / "decision_graph_model.yaml"


def _fetch_decision_data(conn) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """从 PG 读取 tracks/layers/nodes/edges。"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT track_id, track_name, track_name_en, description, priority, activation_condition
            FROM decision_tracks ORDER BY priority
        """)
        tracks = [
            {
                "id": r[0], "name": r[1], "name_en": r[2], "desc": r[3],
                "priority": r[4], "activation": r[5],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT layer_id, layer_name, layer_name_en, track, description,
                   decision_frequency, design_maturity, build_status
            FROM decision_layers ORDER BY layer_id
        """)
        layers = [
            {
                "id": r[0], "name": r[1], "name_en": r[2], "track": r[3],
                "desc": r[4], "freq": r[5], "maturity": r[6], "build": r[7],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT node_id, layer_id, node_type, path, module_id, decision_name,
                   build_status, evidence_hash
            FROM decision_nodes ORDER BY layer_id, node_id
        """)
        nodes = [
            {
                "id": r[0], "layer_id": r[1], "type": r[2], "path": r[3],
                "module_id": r[4], "name": r[5], "build": r[6], "hash": r[7],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT edge_id, from_node_id, to_node_id, edge_type, condition, track
            FROM decision_edges ORDER BY edge_id
        """)
        edges = [
            {
                "id": r[0], "from": r[1], "to": r[2], "type": r[3],
                "condition": r[4], "track": r[5],
            }
            for r in cur.fetchall()
        ]

    return tracks, layers, nodes, edges


def _load_invariants() -> list[dict]:
    """从 YAML 真源读取 invariants 定义（5 条承重墙不变量）。"""
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("invariants", [])


def _build_status_color(build: str) -> str:
    """build_status → mermaid 颜色类。"""
    return {
        "stable": "bsStable",
        "generated": "bsGenerated",
        "testing": "bsTesting",
        "planned": "bsPlanned",
        "deprecated": "bsDeprecated",
    }.get(build, "bsGenerated")


def _gen_overview_mmd(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict]
) -> tuple[str, int, int, int]:
    """生成全景图：L0-L6 层级 + 四轨并行 subgraph + 节点/边。"""
    lines = ["flowchart TD"]

    # 按 track 分 subgraph
    for track in tracks:
        tid = track["id"]
        safe_tid = tid.replace("-", "_")
        lines.append(f'    subgraph track_{safe_tid}["{track["name"]}（{track["name_en"]}）"]')
        track_layers = [l for l in layers if l["track"] == tid]
        for layer in track_layers:
            lid = layer["id"]
            safe_lid = lid.replace("-", "_")
            label = f'{layer["id"]}: {layer["name"]}'
            if layer["freq"]:
                label += f'<br/>freq: {layer["freq"]}'
            label += f'<br/>build: {layer["build"]}'
            cls = _build_status_color(layer["build"])
            lines.append(f'        L{safe_lid}["{label}"]:::{cls}')
            # 该层下的节点
            layer_nodes = [n for n in nodes if n["layer_id"] == lid]
            for n in layer_nodes:
                nlabel = f'{n["type"]}: {n["name"]}<br/>path: {n["path"]}'
                ncls = _build_status_color(n["build"])
                lines.append(f'        N{n["id"]}("{nlabel}"):::{ncls}')
                lines.append(f'        L{safe_lid} --- N{n["id"]}')
        lines.append("    end")

    # 层间边（informing/triggering，按 layer 顺序）
    layer_ids = [l["id"] for l in layers]
    for i in range(len(layer_ids) - 1):
        from_lid = layer_ids[i].replace("-", "_")
        to_lid = layer_ids[i + 1].replace("-", "_")
        lines.append(f'    L{from_lid} -.->|triggering| L{to_lid}')

    # 节点间边
    for e in edges:
        lines.append(f'    N{e["from"]} -->|{e["type"]}| N{e["to"]}')

    # 样式
    lines.append("")
    lines.append("    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px")
    lines.append("    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px")
    lines.append("    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px")
    lines.append("    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px")
    lines.append("    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px")

    return "\n".join(lines) + "\n", len(tracks), len(layers), len(edges)


def _gen_layers_mmd(tracks: list[dict], layers: list[dict]) -> str:
    """生成层级详情图：10 层卡片 + 频率/成熟度/状态 + 流向箭头。"""
    lines = ["flowchart LR"]

    for layer in layers:
        lid = layer["id"].replace("-", "_")
        label = f'{layer["id"]} {layer["name"]}<br/>{layer["name_en"]}'
        if layer["freq"]:
            label += f'<br/>频率: {layer["freq"]}'
        label += f'<br/>成熟度: {layer["maturity"]}'
        label += f'<br/>build: {layer["build"]}'
        cls = _build_status_color(layer["build"])
        lines.append(f'    L{lid}["{label}"]:::{cls}')

    # 层间流向（informing/triggering/approving/feedback）
    layer_ids = [l["id"] for l in layers]
    for i in range(len(layer_ids) - 1):
        from_lid = layer_ids[i].replace("-", "_")
        to_lid = layer_ids[i + 1].replace("-", "_")
        lines.append(f'    L{from_lid} -->|triggering| L{to_lid}')

    # 反馈边（L6 → L1/L5，学习闭环）
    if len(layer_ids) >= 6:
        l1 = layer_ids[1].replace("-", "_") if len(layer_ids) > 1 else None
        l5 = "L5"
        l6 = "L6"
        if l1:
            lines.append(f'    {l6} -.->|feedback| {l1}')
        lines.append(f'    {l6} -.->|feedback| {l5}')

    # 图例
    lines.append("")
    lines.append("    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px")
    lines.append("    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px")
    lines.append("    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px")
    lines.append("    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px")
    lines.append("    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px")

    return "\n".join(lines) + "\n"


def _gen_invariants_mmd(invariants: list[dict]) -> str:
    """生成不变量图：6 节点类型 + 5 不变量标注 + 合法/非法连接。"""
    lines = ["flowchart TD"]

    # 6 节点类型
    node_types = [
        ("signal", "信号节点<br/>Signal"),
        ("portfolio_target", "仓位目标节点<br/>Portfolio Target"),
        ("risk_check", "风控节点<br/>Risk Check"),
        ("order", "订单节点<br/>Order"),
        ("execution", "执行节点<br/>Execution"),
        ("feedback", "反馈节点<br/>Feedback"),
    ]
    for nt, label in node_types:
        safe = nt.replace("-", "_")
        lines.append(f'    NT_{safe}["{label}"]:::nodeType')

    # 合法连接（实线）
    lines.append("    NT_signal -->|portfolio_target| NT_portfolio_target")
    lines.append("    NT_portfolio_target -->|risk_check| NT_risk_check")
    lines.append("    NT_risk_check -->|approving| NT_order")
    lines.append("    NT_order -->|triggering| NT_execution")
    lines.append("    NT_execution -.->|feedback| NT_feedback")
    lines.append("    NT_feedback -.->|informing| NT_signal")

    # 非法连接（DEC-INV-002，红色虚线）
    lines.append("    NT_signal -.->|禁止| NT_order")
    lines.append("    linkStyle 6 stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5")

    # 不变量标注节点
    for inv in invariants:
        iid = inv["id"]
        safe_iid = iid.replace("-", "_")
        label = f'{iid}<br/>{inv["name"]}<br/>{inv["name_en"]}'
        lines.append(f'    INV_{safe_iid}(["{label}"]):::invariant')

    # 不变量关联到节点类型
    lines.append("    INV_DEC_INV_001 -.- NT_order")
    lines.append("    INV_DEC_INV_002 -.- NT_signal")
    lines.append("    INV_DEC_INV_003 -.- NT_feedback")
    lines.append("    INV_DEC_INV_005 -.- NT_signal")

    # 样式
    lines.append("")
    lines.append("    classDef nodeType fill:#e3f2fd,stroke:#1565c0,stroke-width:2px")
    lines.append("    classDef invariant fill:#fff8e1,stroke:#ff8f00,stroke-width:2px")

    return "\n".join(lines) + "\n"


def _gen_index_md(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict]
) -> str:
    """生成索引文档（含统计+图嵌入+tracks/layers 清单）。"""
    lines = [
        "# 决策流图（decisiongraph）索引",
        "",
        f"> 生成时间: {datetime.now().isoformat(timespec='seconds')}",
        f"> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）",
        f"> 数据库: {DB_DISPLAY_NAME}",
        "",
        "## 概述",
        "",
        "决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图。",
        '- depgraph 表达"谁依赖谁"（模块依赖，静态）',
        '- dataflowgraph 表达"数据从哪流到哪"（数据流向，动态）',
        '- decisiongraph 表达"决策如何产生"（决策流，动态）',
        "- 三图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）",
        "",
        "## 统计",
        "",
        "| 类型 | 数量 |",
        "|------|------|",
        f"| Track（轨） | {len(tracks)} |",
        f"| Layer（层） | {len(layers)} |",
        f"| Node（节点） | {len(nodes)} |",
        f"| Edge（边） | {len(edges)} |",
        "",
        "## Mermaid 图表",
        "",
        "### 全景图（L0-L6 层级 + 四轨并行）",
        "- [decision_overview.mmd](decision_overview.mmd)",
        "",
        "### 层级详情图（10 层卡片 + 频率/状态）",
        "- [decision_layers.mmd](decision_layers.mmd)",
        "",
        "### 不变量图（6 节点类型 + 5 承重墙不变量）",
        "- [decision_invariants.mmd](decision_invariants.mmd)",
        "",
        "## Track 清单（四轨）",
        "",
        "| track_id | 名称 | 英文名 | 优先级 | 激活条件 |",
        "|----------|------|--------|--------|----------|",
    ]
    for t in tracks:
        lines.append(
            f"| {t['id']} | {t['name']} | {t['name_en']} | {t['priority']} | {t['activation'] or '-'} |"
        )

    lines.extend([
        "",
        "## Layer 清单（L0-L6）",
        "",
        "| layer_id | 名称 | 英文名 | 所属轨 | 决策频率 | 成熟度 | build_status |",
        "|----------|------|--------|--------|----------|--------|--------------|",
    ])
    for l in layers:
        lines.append(
            f"| {l['id']} | {l['name']} | {l['name_en']} | {l['track']} | "
            f"{l['freq'] or '-'} | {l['maturity']} | {l['build']} |"
        )

    if nodes:
        lines.extend([
            "",
            "## Node 清单（运行时决策节点）",
            "",
            "| node_id | layer | type | name | path | module_id | build_status |",
            "|---------|-------|------|------|------|-----------|--------------|",
        ])
        for n in nodes:
            lines.append(
                f"| {n['id']} | {n['layer_id']} | {n['type']} | {n['name']} | "
                f"{n['path']} | {n['module_id'] or '-'} | {n['build']} |"
            )

    if edges:
        lines.extend([
            "",
            "## Edge 清单（决策因果边）",
            "",
            "| edge_id | from | to | type | condition | track |",
            "|---------|-------|-----|------|-----------|-------|",
        ])
        for e in edges:
            lines.append(
                f"| {e['id']} | {e['from']} | {e['to']} | {e['type']} | "
                f"{e['condition'] or '-'} | {e['track'] or '-'} |"
            )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 decisiongraph (PostgreSQL) 生成决策流图（Mermaid + Markdown）",
    )
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    args = parser.parse_args()

    # 验证连接
    try:
        conn = get_decisiongraph_pg_connection()
    except Exception as e:
        print(f"[ERROR] decisiongraph 连接失败: {e}", file=sys.stderr)
        return 1

    try:
        tracks, layers, nodes, edges = _fetch_decision_data(conn)
    finally:
        conn.close()

    if not tracks and not layers:
        print("[WARN] decisiongraph 表为空，请先运行 generate_decision_graph.py 同步 decision_graph_model.yaml")
        return 2

    # 加载 invariants（从 YAML 真源）
    invariants = _load_invariants()

    # 创建输出目录
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 生成全景图
    overview_mmd, t_count, l_count, e_count = _gen_overview_mmd(tracks, layers, nodes, edges)
    (out_dir / "decision_overview.mmd").write_text(overview_mmd, encoding="utf-8")
    print(f"[OK] 生成 decision_overview.mmd ({t_count} tracks, {l_count} layers, {len(nodes)} nodes, {e_count} edges)")

    # 生成层级详情图
    layers_mmd = _gen_layers_mmd(tracks, layers)
    (out_dir / "decision_layers.mmd").write_text(layers_mmd, encoding="utf-8")
    print(f"[OK] 生成 decision_layers.mmd ({l_count} layers)")

    # 生成不变量图
    invariants_mmd = _gen_invariants_mmd(invariants)
    (out_dir / "decision_invariants.mmd").write_text(invariants_mmd, encoding="utf-8")
    print(f"[OK] 生成 decision_invariants.mmd ({len(invariants)} invariants)")

    # 生成索引文档
    md = _gen_index_md(tracks, layers, nodes, edges)
    (out_dir / "decision_index.md").write_text(md, encoding="utf-8")
    print(f"[OK] 生成 decision_index.md")

    print(f"\n输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
