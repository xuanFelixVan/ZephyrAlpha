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

import re
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


def _clean_note(n: dict) -> str:
    """algo_note 归一：折叠块行接缝的"。 "并句号（YAML >- 语义行→空格）。"""
    note = (n.get("algo_note_zh") or "").replace("\n", " ").strip()
    while "。 " in note:
        note = note.replace("。 ", "。")
    return note


def _node_label(n: dict) -> str:
    """图上节点卡：名称+问+机制速览（机制=algo_note 首句——看图即知怎么算，详解见卡片）。"""
    name = _esc(n.get("name_zh") or n["node_id"])
    badge = " 📄paper" if n.get("ai_autonomy") == "paper" else ""
    q = _esc(n.get("decision_question") or "", 30)
    note = _clean_note(n)
    gist = _esc(note.split("。")[0], 50) if note else "（待补）"
    return f"{name}{badge}<br/>问：{q}<br/>机制：{gist}"


def _load_node_comments() -> dict[str, list[str]]:
    """提取真源 YAML 各节点的注释行（D 裁定原文/失效规则/欠账登记——机制细节最富的矿）。

    yaml.safe_load 丢弃注释，故手工逐行扫 nodes 区。归属规则：
    - 节点块头之后的注释 → 该节点（字段间备注/块内说明）
    - 紧邻下一节点块头的悬空注释（前导说明，实测 86 处）→ 归下一个节点，不误挂上一个
    - 纯装饰线（─/═/-）过滤；nodes 区末尾无主注释丢弃
    """
    lines = SRC_YAML.read_text(encoding="utf-8").split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.rstrip() == "nodes:")
    except StopIteration:
        return {}
    end = start + 1
    while end < len(lines) and (lines[end].startswith(" ") or not lines[end].strip()):
        end += 1
    region = lines[start + 1 : end]

    def is_comment(s: str) -> bool:
        return s.lstrip().startswith("#")

    def is_node_start(s: str) -> bool:
        return s.startswith("  - node_id:")

    def meaningful(s: str) -> bool:
        return bool(s.strip()) and not is_comment(s)

    # 反向预扫：after[i]=位置 i 之后的第一个实质行是否为节点块头（前导注释判据）
    after = [False] * len(region)
    flag = False
    for i in range(len(region) - 1, -1, -1):
        after[i] = flag
        if meaningful(region[i]):
            flag = is_node_start(region[i])

    comments: dict[str, list[str]] = {}
    pending: list[str] = []  # 前导注释缓冲（等下一个节点块头认领）
    cur: str | None = None
    for i, ln in enumerate(region):
        if is_node_start(ln):
            cur = ln.split(":", 1)[1].strip()
            comments[cur] = pending
            pending = []
        elif is_comment(ln):
            txt = ln.strip()[1:].strip()
            if not txt or re.fullmatch(r"[-─=═\s]+", txt):
                continue
            if cur is not None and not after[i]:
                comments[cur].append(txt)
            else:
                pending.append(txt)  # 区首/下一节点的前导注释
    return comments


_REF_LABELS = [
    ("factor_refs", "因子"), ("data_refs", "数据"), ("cost_model_refs", "成本模型"),
    ("risk_limit_refs", "风险限额"), ("threshold_refs", "阈值"), ("event_refs", "事件"),
    ("algo_refs", "算法"), ("universe_refs", "票池"), ("pattern_refs", "形态"),
    ("seat_refs", "席位"), ("macro_refs", "宏观"), ("cycle_refs", "周期"),
    ("benchmark_refs", "基准"), ("portfolio_model_refs", "组合模型"),
]


def _render_node_cards(nodes: list[dict], comments_map: dict[str, list[str]]) -> str:
    """节点详解卡：每节点一卡（问/机制全文/依据锚/治理/裁定原文备注）——优化判断的信息底座。"""
    parts = ["## 节点详解（机制怎么产生）", ""]
    for n in nodes:
        nid = n["node_id"]
        red = " 🔴" if _is_red_node(n) else ""
        parts.append(f"### {nid} {n.get('name_zh', '')}{red}")
        parts.append("")
        parts.append(f"**问**：{n.get('decision_question', '')}")
        parts.append("")
        parts.append(f"**机制（怎么算）**：{_clean_note(n) or '（待补）'}")
        parts.append("")
        anchors = []
        for key, lab in _REF_LABELS:
            vals = n.get(key) or []
            if vals:
                shown = [v.get("strategy_ref", "?") if isinstance(v, dict) else str(v) for v in vals]
                anchors.append(f"{lab} {'、'.join(shown)}")
        mounts = n.get("strategy_mounts") or []
        if mounts:
            shown = [m.get("strategy_ref", "?") if isinstance(m, dict) else str(m) for m in mounts]
            anchors.append(f"策略挂载 {'、'.join(shown)}")
        if anchors:
            parts.append("**依据锚**：" + " ｜ ".join(anchors))
        gov = []
        if n.get("activation"):
            gov.append(f"激活={n['activation']}")
        if n.get("invalidation"):
            gov.append(f"失效={n['invalidation']}")
        if n.get("ai_autonomy"):
            gov.append(f"档位={n['ai_autonomy']}")
        if n.get("module_id"):
            gov.append(f"模块={n['module_id']}")
        if n.get("fallback"):
            gov.append(f"兜底={n['fallback']}")
        if gov:
            parts.append("**治理**：" + " ｜ ".join(gov))
        parts.append("")
        cmts = comments_map.get(nid) or []
        if cmts:
            parts.append("**设计备注（裁定/欠账原文）**：")
            for c in cmts:
                parts.append(f"- {c}")
            parts.append("")
    return "\n".join(parts)


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
        note = _clean_note(n).replace("|", "／")
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


def _render_file(stem: str, title: str, nodes: list[dict], all_edges: list[dict],
                 comments_map: dict[str, list[str]] | None = None) -> str:
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
    cards = _render_node_cards(nodes, comments_map or {})
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
> 每个节点的完整机制（怎么算/依据什么/裁定原文）见下方「节点详解」区。
{_html_link_line(stem)}

## 关系图

```mermaid
{mermaid}
```

## 节点明细（速览）

{_render_detail_table(nodes)}

{cards}

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
    comments_map = _load_node_comments()
    for stem, title, _ in FILE_PLAN:
        group = by_prefix[stem]
        md_path = out_dir / f"{stem}.md"
        content = _render_file(stem, title, group, edges, comments_map)
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
