# [BLUEPRINT] MOD-D_GOV_SCRIPTS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""交易决策地图全景图生成器（10 号目录，8 MD + 8 可缩放 HTML）。

真源: config/trading_decision_map.yaml（YAML 型触发: git commit → reconcile_stale mtime 对比）
派生: docs/02_enterprise_architecture/10_trading_map/trading_map_00~07 *.md + _zoomable_html/*.html
规范: visualization_view_template.md v1.6（四要素/运营态蓝实线/设计态橙虚线/双产物）
拆分(D91): 00 总览(横切层+跨流边) / 01-04 E 流按层 L1-L4 / 05 P 流 / 06 X 流(含 R1) / 07 F 流

[STARTUP] event_driven（通过 reconcile_generators 编排器自动触发，禁止手动跑作为唯一手段）
"""
from __future__ import annotations

import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from scripts.governance._shared.constants import DOC_HTTP_BASE  # noqa: E402  URL SSoT（NO-HARDCODED-URL）

SRC_YAML = REPO_ROOT / "config" / "trading_decision_map.yaml"
DEFAULT_OUT = REPO_ROOT / "docs" / "02_enterprise_architecture" / "10_trading_map"
# 模板 §14：HTML 链接必须 http:// 绝对路径，IDE 才会交外部浏览器渲染
_HTML_SERVER_PREFIX = DOC_HTTP_BASE + "/"

# D91 拆分规则: (文件名, 中文标题, node_id 前缀组)
FILE_PLAN = [
    ("trading_map_00_panorama", "总览·横切层与四流骨架", ("TDM-C-",)),
    ("trading_map_01_e_l1_regime", "建仓流 L1·大盘判定（四层温度计）", ("TDM-E-L1",)),
    ("trading_map_02_e_l2_sector", "建仓流 L2·板块漏斗", ("TDM-E-L2",)),
    ("trading_map_03_e_l3_stock", "建仓流 L3·个股漏斗", ("TDM-E-L3",)),
    ("trading_map_04_e_l4_exec", "建仓流 L4·执行", ("TDM-E-L4",)),
    ("trading_map_05_p_position", "持仓流 P·体检/做T/加仓", ("TDM-P-",)),
    ("trading_map_06_x_exit", "离场流 X·信号/执行/R1 应急", ("TDM-X-",)),
    ("trading_map_07_f_portfolio", "组合流 F·聚合/归因反馈", ("TDM-F-",)),
]

PAPER_BADGE = "📄paper"
EDGE_STYLE = {"sequence": "-->", "feed": "-->", "feedback": "<-.->", "broadcast": "==>"}
EDGE_LABEL = {"sequence": "顺序", "feed": "喂给", "feedback": "反馈", "broadcast": "广播"}


def _is_red_node(n: dict) -> bool:
    """红节点=设计态: module_ref 缺失或含 planned（橙虚线）。"""
    mr = n.get("module_ref")
    return mr is None or "planned" in str(mr).lower()


def _mid(node_id: str) -> str:
    """mermaid 安全 id（连字符→下划线）。"""
    return node_id.replace("-", "_")


def _esc(text: str, limit: int = 0) -> str:
    if limit and text and len(text) > limit:
        text = text[:limit] + "…"
    return (text or "").replace('"', "'").replace("[", "（").replace("]", "）").replace("|", "/").replace("\n", " ")


def _node_label(n: dict) -> str:
    q = _esc(n.get("decision_question") or "", 42)
    badge = f" {PAPER_BADGE}" if n.get("ai_autonomy") == "paper" else ""
    return f"{_esc(n.get('name_zh') or n['node_id'])}{badge}<br/>{q}"


def _render_mermaid(nodes: list[dict], edges: list[dict], external: dict[str, list[dict]]) -> str:
    lines = ["flowchart TD"]
    ids = {n["node_id"] for n in nodes}
    for n in nodes:
        mid = _mid(n["node_id"])
        lines.append(f'  {mid}["{_node_label(n)}"]')
    # 跨文件入口: 外部→本文件的边, 画虚拟入口（去重）
    declared_ext: set[str] = set()
    for target, srcs in external.items():
        if target in ids:
            for s in srcs:
                if s not in declared_ext:
                    lines.append(f'  EXT_{_mid(s)}(["⧉ {_esc(s)}（见对应文件）"])')
                    declared_ext.add(s)
    for e in edges:
        a, b, t = e["from_node"], e["to_node"], e.get("edge_type", "feed")
        if a in ids and b in ids:
            lbl = EDGE_LABEL.get(t, "")
            arrow = EDGE_STYLE.get(t, "-->")
            lbl_txt = f"|{_esc(lbl)}|" if lbl else ""
            lines.append(f"  {_mid(a)} {arrow}{lbl_txt} {_mid(b)}")
        elif b in ids and a not in ids:
            lines.append(f"  EXT_{_mid(a)} --> {_mid(b)}")
        elif a in ids and b not in ids:
            lines.append(f"  {_mid(a)} --> EXT_OUT_{_mid(b)}([→ {_esc(b)}])")
    reds = [ _mid(n["node_id"]) for n in nodes if _is_red_node(n) ]
    papers = [ _mid(n["node_id"]) for n in nodes if n.get("ai_autonomy") == "paper" ]
    # 配色=模板 §4.7 跨文档统一（对齐 battle_map/域文档浅色系；深色主题由 HTML 主题层处理）
    lines.append("  classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;")
    lines.append("  classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5;")
    lines.append("  classDef paper fill:#e8f5e9,stroke:#2e7d32,stroke-width:2.5px,color:#000;")
    prod = [ _mid(n["node_id"]) for n in nodes if not _is_red_node(n) ]
    if prod:
        lines.append(f"  class {','.join(prod)} production;")
    if reds:
        lines.append(f"  class {','.join(reds)} design;")
    if papers:
        lines.append(f"  class {','.join(papers)} paper;")  # paper 优先级最高（覆盖 production/design 底色）
    return "\n".join(lines)


def _fmt_mounts(n: dict) -> str:
    items = []
    for m in n.get("strategy_mounts") or []:
        if isinstance(m, dict):
            ref = m.get("strategy_ref") or "?"
            conf = f"({m['confidence']})" if m.get("confidence") else ""
            items.append(f"{ref}{conf}")
        else:
            items.append(str(m))
    return "、".join(items) if items else "—"


def _render_detail_table(nodes: list[dict]) -> str:
    rows = ["| node_id | 名称 | 怎么算（大白话） | 时点 | 档位 | 模块锚 |",
            "|---|---|---|---|---|---|"]
    for n in nodes:
        red = "🔴" if _is_red_node(n) else ""
        mod = n.get("module_ref") or "—"
        if n.get("module_id"):
            mod = f"{n['module_id']}"
        note = (n.get("algo_note_zh") or "（待补）").strip().replace("|", "／")
        rows.append(
            f"| {n['node_id']}{red} | {_esc(n.get('name_zh'))} | {note.strip()} "
            f"| {n.get('point') or '—'} | {n.get('ai_autonomy') or '—'} | {mod} |"
        )
    return "\n".join(rows)


def _render_mounts(nodes: list[dict]) -> str:
    mods, strs = set(), set()
    for n in nodes:
        if n.get("module_ref") and n["module_ref"] != "null":
            mods.add(f"{n['module_id']} {n['module_ref']}" if n.get("module_id") else str(n["module_ref"]))
        for m in n.get("strategy_mounts") or []:
            strs.add(m["strategy_ref"] if isinstance(m, dict) else str(m))
    out = []
    if mods:
        out.append("**模块锚（MOD）**：" + "、".join(sorted(mods)))
    if strs:
        out.append("**策略挂载（STR）**：" + "、".join(sorted(strs)))
    return "\n\n".join(out) if out else "（本文件无挂载）"


def _html_link_line(stem: str) -> str:
    """网页版跳转行（对齐 battle_map 先例：http:// 绝对路径 + 操作提示）。"""
    url = f"{_HTML_SERVER_PREFIX}docs/02_enterprise_architecture/10_trading_map/_zoomable_html/{stem}.html"
    return f"> **[可缩放 HTML 版 / Zoomable HTML]({url})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式"


def _render_file(stem: str, title: str, nodes: list[dict], all_edges: list[dict]) -> str:
    ids = {n["node_id"] for n in nodes}
    in_edges = [e for e in all_edges if e["from_node"] in ids or e["to_node"] in ids]
    external: dict[str, list[dict]] = defaultdict(list)
    for e in in_edges:
        if e["from_node"] not in ids and e["to_node"] in ids:
            external[e["to_node"]].append(e["from_node"])
    mermaid = _render_mermaid(nodes, in_edges, external)
    counts = f"{len(nodes)} 节点"
    reds = sum(1 for n in nodes if _is_red_node(n))
    papers = sum(1 for n in nodes if n.get("ai_autonomy") == "paper")
    return f"""---
doc_type: architecture_view
title: 交易决策地图·{title}
version: "1.0.0"
status: active
date: {date.today().isoformat()}
owner: auto-generator
ttl: permanent
source: config/trading_decision_map.yaml
---

# 交易决策地图 · {title}（自动派生）

> **本文件由生成器自动派生，禁止手编**。真源=`config/trading_decision_map.yaml`（改动后 git commit → 运行时启动自动重生成）。
> 规模：{counts}｜🔴设计态（红节点）{reds}｜{PAPER_BADGE} 实盘执行 {papers}｜图例：橙虚线=设计态，蓝底={PAPER_BADGE} 实盘执行节点（D18 治理阶梯）。
{_html_link_line(stem)}

## 关系图

```mermaid
{mermaid}
```

## 节点明细

{_render_detail_table(nodes)}

## 挂载清单

{_render_mounts(nodes)}
"""


def regenerate(output_dir: Path | None = None) -> dict:
    """编排器入口：生成 8 MD + 8 HTML，返回 {outputs, nodes, edges, files}。"""
    dm = yaml.safe_load(SRC_YAML.read_text(encoding="utf-8"))
    nodes = dm["nodes"]
    edges = dm["edges"]
    out_dir = Path(output_dir) if output_dir else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)

    by_prefix: dict[str, list[dict]] = {stem: [] for stem, _, _ in FILE_PLAN}
    assigned: dict[str, str] = {}
    for n in nodes:
        nid = n["node_id"]
        for stem, _, prefixes in FILE_PLAN:
            if any(nid == p.rstrip("-") or nid.startswith(p) for p in prefixes):
                by_prefix[stem].append(n)
                assigned[nid] = stem
                break
    unassigned = [n["node_id"] for n in nodes if n["node_id"] not in assigned]
    if unassigned:
        raise ValueError(f"节点未归入任何文件（检查 FILE_PLAN 前缀）: {unassigned}")

    outputs: list[str] = []
    for stem, title, _ in FILE_PLAN:
        group = by_prefix[stem]
        md_path = out_dir / f"{stem}.md"
        content = _render_file(stem, title, group, edges)
        md_path.write_text(content, encoding="utf-8")
        outputs.append(str(md_path.relative_to(REPO_ROOT)))
        from scripts.governance.d5_architecture.generators.zoomable_html import emit_zoomable_html
        html = emit_zoomable_html(md_path, content)
        if html:
            outputs.append(str(html.relative_to(REPO_ROOT)))

    return {
        "generator": "trading_decision_map",
        "status": "ok",
        "outputs": outputs,
        "nodes": len(nodes),
        "edges": len(edges),
        "files": {stem: len(g) for stem, g in by_prefix.items()},
    }


def main() -> int:
    result = regenerate()
    print(f"✓ 交易决策地图全景图: {result['nodes']} 节点 / {result['edges']} 边 → {len(result['outputs'])} 个产物")
    for stem, cnt in result["files"].items():
        print(f"  {stem}: {cnt} 节点")
    print(f"  对账: 文件合计 {sum(result['files'].values())} == 真源 {result['nodes']} → {'✓' if sum(result['files'].values()) == result['nodes'] else '✗ 不一致!'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
