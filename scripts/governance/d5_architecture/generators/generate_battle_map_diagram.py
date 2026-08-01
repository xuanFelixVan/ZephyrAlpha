# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_panorama.md | §battlemap
# [MODULE] scripts.governance.d5_architecture.generators.generate_battle_map_diagram
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.battle_map_reader (BattleMapReader); scripts.governance._shared.module_translation_loader (get_step_*); scripts.governance.d5_architecture.generators.zoomable_html (emit_zoomable_html)
# [CONSUMERS] AI/人生成交易决策作战地图可视化（Mermaid + 可缩放 HTML）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读 battle_map三表 + 翻译真源 battle_map_steps段（BM-INV-003）；颜色按锚点模块 depgraph build_status 推导五态（panorama §九）；Mermaid 分页防 >100 节点渲染失败
# [MODIFY-GUARD] 对标 generate_trading_flow_diagram.py + zoomable_html.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 不可用→exit 4; YAML 缺失→降级到 DB step_name
# [TESTS] tests/test_generate_battle_map_diagram.py (规划中)
# [TTL] permanent
"""
generate_battle_map_diagram.py — 交易决策作战地图可视化生成器

[BLUEPRINT] | battle_map_panorama.md | §battlemap
[MODULE] scripts.governance.d5_architecture.generators.generate_battle_map_diagram
[INVARIANTS] 只读 battle_map三表 + 翻译真源；颜色按锚点模块 depgraph build_status 推导五态；Mermaid 分页
[CONSUMERS] AI/人生成作战地图可视化
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] DB 不可用→exit 4; YAML 缺失→降级到 DB step_name

从 battle_map 三表（steps/anchors/edges）+ 翻译真源 battle_map_steps 段生成作战地图：
  - 总指挥图（全部环节 + 流转边，Mermaid 分页）
  - 6 分阶段图（选股/买入/卖出/仓位/执行/对账）
  - 每环节 6 件套详情表（trigger/consumes/params/data_flow/code_mapping/degradation）
  - 可缩放 HTML（复用 zoomable_html.emit_zoomable_html）

颜色标注（panorama §九 五态，由锚点模块 depgraph build_status 推导）：
  - production（运营态，stable/generated/testing）→ 🟦 蓝色实线
  - design（设计态，planned）                    → 🟧 橙色虚线
  - deprecated（弃用态）                          → 🟥 红色
  - missing（缺失态，无锚点 BM-INV-001）          → ⬜ 灰色 ⚠
  - candidate（候选态，target_graph=candidate）   → 🟨 黄色

与 generate_trading_flow_diagram.py 的关系：
  旧生成器读 decisiongraph + narrative.yaml；本生成器读 battle_map三表 + 翻译真源
  （battle_map_panorama.md §五：battle_map 取代 decisiongraph+narrative 作为交易流真源）。
  本生成器是 battle_map 上线后的新真源入口；旧生成器待 battle_map 跑顺后退役。

用法:
  python scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py
  python scripts/governance/d5_architecture/generators/generate_battle_map_diagram.py --output-dir custom/dir
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
# d5_architecture/generators 在 sys.path 上（用于 zoomable_html）
_SCRIPTS_DIR = str(_THIS_FILE.parents[3])
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402
from _shared.module_translation_loader import (  # noqa: E402
    get_step_name_bilingual,
    get_step_plain,
    get_step_mechanism,
    get_step_indicators_zh,
    preload_battle_map_steps,
)
from zephyr.governance.persistence.battle_map_reader import BattleMapReader  # noqa: E402
from zephyr.governance.persistence.depgraph_reader import DepgraphReader  # noqa: E402
from d5_architecture.generators.zoomable_html import emit_zoomable_html  # noqa: E402

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 6 阶段定义（与 battle_map_steps.flow_stage 对齐）
FLOW_STAGES = [
    ("stock_selection", "选股", "01"),
    ("buy_flow", "买入", "02"),
    ("sell_flow", "卖出", "03"),
    ("position_management", "仓位", "04"),
    ("execution", "执行", "05"),
    ("reconciliation", "对账", "06"),
]

# Mermaid 分页大小（防 >100 节点渲染失败，memory lesson）
PAGE_SIZE = 30

# 颜色 classDef（panorama §九 五态：运营/设计/弃用/缺失/候选）
# 治本（2026-08-01，Gap1）：颜色改由锚点模块的 depgraph build_status 推导（真实状态），
# 不再用 step.design_maturity 自报。design 用虚线（§九"橙色虚线"）。
_CLASSDEFS = """classDef production fill:#4A90D9,stroke:#2C5F8A,color:#fff,stroke-width:2px;
classDef design fill:#E8A33D,stroke:#B57520,color:#fff,stroke-width:2px,stroke-dasharray: 5 5;
classDef deprecated fill:#D93636,stroke:#A02020,color:#fff,stroke-width:2px;
classDef missing fill:#BBBBBB,stroke:#888888,color:#fff,stroke-width:2px;
classDef candidate fill:#F4D03F,stroke:#B7950B,color:#000,stroke-width:2px;"""

# edge_type → Mermaid 线型
_EDGE_STYLE = {
    "data_flow": "---",
    "trigger": "->>",
    "degradation": "-.-",
}

# depgraph build_status（5态生命周期）→ 作战地图展示态（panorama §九 五态）
# 治本（2026-08-01，Gap1）：generated/testing/stable 均"已建"→production(蓝)；
# planned→design(橙)；deprecated→弃用(红)。未命中保守视为 planned（设计态）。
_BUILD_STATUS_TO_STATE: dict[str, str] = {
    "stable": "production",
    "generated": "production",
    "testing": "production",
    "planned": "design",
    "deprecated": "deprecated",
}

# 五态 → 显示标签（图例/详情表用）
_STATE_LABEL: dict[str, str] = {
    "production": "🟦 运营态（已建）",
    "design": "🟧 设计态（待施工）",
    "deprecated": "🟥 弃用态",
    "missing": "⬜ 缺失态（无锚点）",
    "candidate": "🟨 候选态（候选池）",
}


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------


def _compute_step_status(
    anchors: list[dict],
    status_map: dict[str, str],
) -> str:
    """根据锚点的 depgraph build_status 计算环节有效展示态（panorama §九 五态）。

    优先级：primary depgraph 锚点 > 其他 depgraph 锚点 > candidate 锚点 > missing。
    depgraph build_status 未命中时保守视为 planned（设计态）。

    治本（2026-08-01，Gap1）：替代旧的 step.design_maturity 自报——
    环节颜色反映其承载模块的真实落地状态，而非环节自我声明。
    """
    if not anchors:
        return "missing"
    # 1. primary depgraph 锚点（主承载模块决定环节状态）
    for a in anchors:
        if a.get("target_role") == "primary" and a.get("target_graph") == "depgraph":
            bs = status_map.get(a["target_id"], "planned")
            return _BUILD_STATUS_TO_STATE.get(bs, "design")
    # 2. 任意 depgraph 锚点（无 primary 时取首个）
    for a in anchors:
        if a.get("target_graph") == "depgraph":
            bs = status_map.get(a["target_id"], "planned")
            return _BUILD_STATUS_TO_STATE.get(bs, "design")
    # 3. candidate 锚点（候选池承载，未进全景图）
    for a in anchors:
        if a.get("target_graph") == "candidate":
            return "candidate"
    # 4. 仅 blueprint/decisiongraph/dataflowgraph 锚点——有设计依据但无 depgraph 模块
    return "design"


def _has_candidate_anchor(anchors: list[dict]) -> bool:
    """环节是否有候选池锚点（用于 🟡 候选标记，panorama §九 候选态）。"""
    return any(a.get("target_graph") == "candidate" for a in anchors)


def _load_all() -> tuple[list[dict], list[dict], dict[str, list[dict]]]:
    """加载 battle_map 三表 + 翻译真源 + depgraph build_status，并 enrich 到 step/anchor。

    Enrichment（Gap1，治本 2026-08-01）：
      - 每个 step 附加 `_effective_status`（五态）和 `_has_candidate`（bool）
      - 每个 depgraph anchor 附加 `_live_build_status`（depgraph 真实 build_status）

    Returns:
        (steps, edges, anchors_by_step) — steps/edges 全量，anchors_by_step 按 step_id 分组
    """
    preload_battle_map_steps()  # 预加载 YAML 叙事缓存
    reader = BattleMapReader()
    try:
        steps = reader.get_all_steps()
        edges = reader.get_all_edges()
        anchors = reader.get_all_anchors()
    finally:
        reader.close()
    anchors_by_step: dict[str, list[dict]] = {}
    for a in anchors:
        anchors_by_step.setdefault(a["step_id"], []).append(a)

    # Gap1：查 depgraph 真实 build_status（替代 step.design_maturity 自报着色）
    dg_ids = [a["target_id"] for a in anchors if a.get("target_graph") == "depgraph"]
    status_map: dict[str, str] = {}
    if dg_ids:
        dr = DepgraphReader()
        try:
            status_map = dr.get_build_status_map(dg_ids)
        finally:
            dr.close()

    # enrich anchors：附加 live build_status
    for a in anchors:
        if a.get("target_graph") == "depgraph":
            a["_live_build_status"] = status_map.get(a["target_id"], "<未命中>")

    # enrich steps：附加有效状态 + 候选标记
    for s in steps:
        sid = s["step_id"]
        al = anchors_by_step.get(sid, [])
        s["_effective_status"] = _compute_step_status(al, status_map)
        s["_has_candidate"] = _has_candidate_anchor(al)

    return steps, edges, anchors_by_step


# ---------------------------------------------------------------------------
# Mermaid 生成
# ---------------------------------------------------------------------------


def _sanitize(text: str) -> str:
    """转义 Mermaid 节点标签中的特殊字符。"""
    if not text:
        return ""
    return (
        text.replace('"', "'")
        .replace("<", "〈")
        .replace(">", "〉")
        .replace("[", "【")
        .replace("]", "】")
        .replace("\n", " ")
    )


def _node_class(step: dict) -> str:
    """根据环节有效展示态（_effective_status）返回 classDef 类名（panorama §九 五态）。

    治本（2026-08-01，Gap1）：改用锚点模块真实 build_status 推导的状态，
    不再用 step.design_maturity 自报。
    """
    status = step.get("_effective_status") or "design"
    if status in ("production", "design", "deprecated", "missing", "candidate"):
        return status
    return "design"


def _node_label(step: dict) -> str:
    """构建节点标签：step_id + 双语名 + 大白话（截断）+ 状态标记。

    标记（panorama §九）：
      - ⚠无锚点 = 缺失态（BM-INV-001 君子协定违例）
      - 🟡候选 = 环节有候选池锚点（候选承载，未进全景图）
    """
    sid = step["step_id"]
    name_bi = get_step_name_bilingual(sid) or step.get("step_name", sid)
    plain = get_step_plain(sid)
    plain_short = plain[:30] + "…" if len(plain) > 30 else plain
    status = step.get("_effective_status") or "design"
    marks: list[str] = []
    if status == "missing":
        marks.append("⚠无锚点")
    if step.get("_has_candidate"):
        marks.append("🟡候选")
    mark = (" " + " ".join(marks)) if marks else ""
    label = f"{sid}\\n{name_bi}"
    if plain_short:
        label += f"\\n{plain_short}"
    if mark:
        label += mark
    return _sanitize(label)


def _mermaid_node_id(step_id: str) -> str:
    """Mermaid 节点 ID（step_id 含连字符，用引号包裹的安全 id）。"""
    return step_id.replace("-", "_")


def _build_mermaid(
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
    title: str,
) -> str:
    """构建一个 Mermaid 流程图块。"""
    lines = [f"```mermaid", f"%% {title}", "flowchart LR"]
    step_ids = {s["step_id"] for s in steps}
    # 节点定义（颜色/标记由 step._effective_status 推导，Gap1）
    for s in steps:
        nid = _mermaid_node_id(s["step_id"])
        cls = _node_class(s)
        label = _node_label(s)
        lines.append(f'    {nid}["{label}"]:::{cls}')
    # 边定义（只画两端都在本图 step 集内的边）
    for e in edges:
        if e["from_step_id"] in step_ids and e["to_step_id"] in step_ids:
            from_n = _mermaid_node_id(e["from_step_id"])
            to_n = _mermaid_node_id(e["to_step_id"])
            style = _EDGE_STYLE.get(e["edge_type"], "---")
            label = e.get("label") or ""
            label_part = f'|{_sanitize(label)}|' if label else ""
            lines.append(f"    {from_n} {style} {label_part} {to_n}")
    lines.append(_CLASSDEFS)
    lines.append("```")
    return "\n".join(lines)


def _build_mermaid_paged(
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
    title: str,
) -> str:
    """构建分页 Mermaid（每页 PAGE_SIZE 个节点，防 >100 节点渲染失败）。"""
    if len(steps) <= PAGE_SIZE:
        return _build_mermaid(steps, edges, anchors_by_step, title)
    parts: list[str] = []
    total_pages = (len(steps) + PAGE_SIZE - 1) // PAGE_SIZE
    for i in range(total_pages):
        chunk = steps[i * PAGE_SIZE : (i + 1) * PAGE_SIZE]
        parts.append(
            _build_mermaid(
                chunk, edges, anchors_by_step, f"{title}（第 {i + 1}/{total_pages} 页）"
            )
        )
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# 详情表生成（6 件套）
# ---------------------------------------------------------------------------


def _format_indicators_table(step: dict) -> str:
    """把 indicators JSONB 6 件套格式化为 Markdown 表。"""
    ind = step.get("indicators") or {}
    rows: list[str] = []

    def _kv(items):
        if not items:
            return "—"
        if isinstance(items, list):
            return "<br>".join(
                f"{it.get('item', it)}" + (f"（来自 {it['source']}）" if isinstance(it, dict) and it.get("source") else "")
                for it in items
            )
        if isinstance(items, dict):
            return "<br>".join(f"{k}: {v}" for k, v in items.items())
        return str(items)

    # ① 触发条件
    trig = ind.get("trigger") or {}
    rows.append(f"| ① 触发条件 | {trig.get('condition', '—')} |")
    if trig.get("threshold"):
        rows[-1] = rows[-1].rstrip(" |") + f" 阈值: {trig['threshold']} |"
    # ② 消费数据/因子
    rows.append(f"| ② 消费数据/因子 | {_kv(ind.get('consumes'))} |")
    # ③ 参数
    params = ind.get("params") or []
    if params:
        p_lines = [
            f"{p.get('name', '?')}={p.get('default', '?')}（范围 {p.get('range', '—')}，"
            f"代码当前: {p.get('current_code_value', '—')}，状态: {p.get('status', '—')}）"
            for p in params
        ]
        rows.append(f"| ③ 参数 | {'<br>'.join(p_lines)} |")
    else:
        rows.append("| ③ 参数 | — |")
    # ④ 数据流
    df = ind.get("data_flow") or {}
    rows.append(
        f"| ④ 数据流 | 输入: {df.get('input', '—')} → 处理: {df.get('process', '—')} "
        f"→ 输出: {df.get('output', '—')} → 下游: {df.get('downstream', '—')} |"
    )
    # ⑤ 代码映射
    cm = ind.get("code_mapping") or {}
    rows.append(f"| ⑤ 代码映射 | {cm.get('module_id', '—')} / {cm.get('source_ref', '—')} |")
    # ⑥ 降级/中止
    deg = ind.get("degradation") or {}
    deg_text = deg.get("condition", "—")
    if deg.get("action"):
        deg_text += f" → {deg['action']}"
    rows.append(f"| ⑥ 降级/中止 | {deg_text} |")

    return "| 要素 | 内容 |\n|---|---|\n" + "\n".join(rows)


def _format_step_detail(step: dict, anchors: list[dict]) -> str:
    """单个环节的完整详情段落。"""
    sid = step["step_id"]
    name_bi = get_step_name_bilingual(sid) or step.get("step_name", sid)
    plain = get_step_plain(sid)
    mechanism = get_step_mechanism(sid)
    indicators_zh = get_step_indicators_zh(sid)

    parts = [
        f"### {sid} {name_bi}",
        "",
        f"> **大白话**：{plain}" if plain else "",
        "",
    ]
    if mechanism:
        parts += ["**机制说明**：", "", mechanism, ""]
    parts += ["**6 件套（结构化，DB indicators JSONB）**：", "", _format_indicators_table(step), ""]
    if indicators_zh:
        parts += ["**指标文案（翻译真源 indicators_zh）**：", "", indicators_zh, ""]
    # 锚点（双向查找）
    if anchors:
        parts += ["**锚点（环节↔模块双向关联）**：", ""]
        parts.append("| 目标图 | 目标ID | 角色 | 状态快照 | 真实build_status |")
        parts.append("|---|---|---|---|---|")
        for a in anchors:
            live = a.get("_live_build_status")
            live_text = live if live else "—"
            parts.append(
                f"| {a['target_graph']} | {a['target_id']} | {a['target_role']} | "
                f"{a.get('status_snapshot') or '—'} | {live_text} |"
            )
        parts.append("")
    else:
        parts += ["**锚点**：⚠ 无（BM-INV-001 君子协定违例——环节无锚点=悬空决策）", ""]
    eff = step.get("_effective_status", "—")
    eff_label = _STATE_LABEL.get(eff, eff)
    parts.append(
        f"**有效状态**：{eff_label} ｜ **环节自报**：{step.get('design_maturity', '—')} "
        f"｜ **层**：{step.get('layer', '—')} ｜ **阶段**：{step.get('flow_stage', '—')}"
    )
    parts.append("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# 文档生成
# ---------------------------------------------------------------------------


def _make_frontmatter() -> str:
    """生成 YAML frontmatter（TTL-METADATA gate 要求 permanent zone 文档带 ttl+doc_type）。

    治本（2026-08-01）：07_trading_decision_architecture/battle_map/ 属 permanent zone，
    生成器 MUST 输出 frontmatter，否则 GATE-TTL-METADATA 阻断 commit。
    """
    return (
        "---\n"
        "ttl: permanent\n"
        "doc_type: architecture_view\n"
        "status: draft\n"
        'version: "0.2.0"\n'
        f"date: {date.today().isoformat()}\n"
        "---\n"
    )


def _generate_panorama_md(
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
) -> str:
    """总指挥图 MD（全部环节 + 流转边 + 每环节详情）。"""
    no_anchor_count = sum(1 for s in steps if s.get("_effective_status") == "missing")
    # 五态分布统计（Gap1）
    state_counts: dict[str, int] = {}
    for s in steps:
        st = s.get("_effective_status", "design")
        state_counts[st] = state_counts.get(st, 0) + 1
    dist = " ｜ ".join(
        f"{_STATE_LABEL.get(st, st)}={cnt}"
        for st, cnt in sorted(state_counts.items(), key=lambda x: -x[1])
    )
    parts = [
        "# 交易决策作战地图（总指挥图）",
        "",
        "> 第四全景图 battle_map 真源：`battle_map_steps` / `battle_map_anchors` / `battle_map_edges` 三表 + 翻译真源 `module_translation_registry.yaml` §battle_map_steps 段。",
        "> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编（改环节→改 DB/YAML 真源→重跑生成器）。",
        "",
        f"**环节总数**：{len(steps)} ｜ **流转边**：{len(edges)} ｜ **无锚点环节**（BM-INV-001）: {no_anchor_count}",
        "",
        f"**状态分布**：{dist}",
        "",
        "## 颜色标注说明（panorama §九 五态）",
        "",
        "- 🟦 蓝色实线 = 运营态（锚点模块 build_status=stable/generated/testing，已建）",
        "- 🟧 橙色虚线 = 设计态（锚点模块 build_status=planned，待施工）",
        "- 🟥 红色 = 弃用态（锚点模块 build_status=deprecated）",
        "- ⬜ 灰色 = 缺失态（环节无锚点，BM-INV-001 君子协定违例，悬空决策风险）",
        "- 🟨 黄色 = 候选态（承载模块在候选池，未进全景图）",
        "- 🟡 标记 = 环节有候选池锚点（候选承载备选）",
        "",
        "## 总指挥图（全流程）",
        "",
        _build_mermaid_paged(steps, edges, anchors_by_step, "作战地图总指挥图"),
        "",
        "## 分阶段导航",
        "",
    ]
    for stage_id, stage_name, num in FLOW_STAGES:
        stage_steps = [s for s in steps if s["flow_stage"] == stage_id]
        parts.append(f"- [{stage_name}阶段（{len(stage_steps)} 环节）](battle_map_{num}_{stage_id}.md)")
    parts.append("")
    parts.append("## 全环节详情（6 件套）")
    parts.append("")
    for s in sorted(steps, key=lambda x: (x["flow_stage"], x.get("sort_order", 0))):
        parts.append(_format_step_detail(s, anchors_by_step.get(s["step_id"], [])))
    return "\n".join(parts)


def _generate_stage_md(
    stage_id: str,
    stage_name: str,
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
) -> str:
    """单阶段 MD（该阶段环节 + 相关边 + 详情）。"""
    stage_steps = [s for s in steps if s["flow_stage"] == stage_id]
    stage_step_ids = {s["step_id"] for s in stage_steps}
    # 边：任一端在本阶段
    stage_edges = [
        e for e in edges
        if e["from_step_id"] in stage_step_ids or e["to_step_id"] in stage_step_ids
    ]
    parts = [
        f"# 作战地图·{stage_name}阶段",
        "",
        f"> battle_map §{stage_id} 阶段，{len(stage_steps)} 环节。",
        "",
        "## 阶段图",
        "",
        _build_mermaid(stage_steps, stage_edges, anchors_by_step, f"{stage_name}阶段图"),
        "",
        "## 环节详情",
        "",
    ]
    for s in sorted(stage_steps, key=lambda x: x.get("sort_order", 0)):
        parts.append(_format_step_detail(s, anchors_by_step.get(s["step_id"], [])))
    parts.append("")
    parts.append("[← 返回总指挥图](battle_map_panorama.md)")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="生成交易决策作战地图可视化")
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "docs" / "02_enterprise_architecture" / "07_trading_decision_architecture" / "battle_map"),
        help="输出目录",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("加载 battle_map 三表 + 翻译真源...")
    steps, edges, anchors_by_step = _load_all()
    print(f"  steps={len(steps)} edges={len(edges)} anchors={sum(len(v) for v in anchors_by_step.values())}")

    # 总指挥图
    panorama_md = _generate_panorama_md(steps, edges, anchors_by_step)
    panorama_md = f"{_make_frontmatter()}\n{panorama_md}"
    panorama_path = out_dir / "battle_map_panorama.md"
    panorama_path.write_text(panorama_md, encoding="utf-8")
    html = emit_zoomable_html(panorama_path, panorama_md)
    print(f"  总指挥图: {panorama_path}" + (f" + HTML: {html}" if html else ""))

    # 6 分阶段图
    for stage_id, stage_name, num in FLOW_STAGES:
        stage_md = _generate_stage_md(stage_id, stage_name, steps, edges, anchors_by_step)
        stage_md = f"{_make_frontmatter()}\n{stage_md}"
        stage_path = out_dir / f"battle_map_{num}_{stage_id}.md"
        stage_path.write_text(stage_md, encoding="utf-8")
        html = emit_zoomable_html(panorama_path, stage_md)
        print(f"  {stage_name}阶段: {stage_path}" + (f" + HTML" if html else ""))

    print(f"\n完成。输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
