# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | §battlemap
# [MODULE] scripts.governance.d5_architecture.generators.generate_battle_map_diagram
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.battle_map_reader (BattleMapReader); scripts.governance._shared.module_translation_loader (get_step_*; get_cross_cutting_*); scripts.governance.d5_architecture.generators.zoomable_html (emit_zoomable_html)
# [CONSUMERS] AI/人生成交易决策作战地图可视化（Mermaid + 可缩放 HTML）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读 battle_map三表 + 翻译真源 battle_map_steps段（BM-INV-003）+ battle_map_cross_cutting段（Gap3）；颜色按锚点模块 depgraph build_status 推导五态（panorama §九）；Mermaid 分页防 >100 节点渲染失败
# [MODIFY-GUARD] 对标 generate_trading_flow_diagram.py + zoomable_html.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 不可用→exit 4; YAML 缺失→降级到 DB step_name
# [TESTS] tests/test_generate_battle_map_diagram.py (规划中)
# [TTL] permanent
"""
generate_battle_map_diagram.py — 交易决策作战地图可视化生成器

[BLUEPRINT] | battle_map_positioning.md | §battlemap
[MODULE] scripts.governance.d5_architecture.generators.generate_battle_map_diagram
[INVARIANTS] 只读 battle_map三表 + 翻译真源(battle_map_steps + battle_map_cross_cutting)；颜色按锚点模块 depgraph build_status 推导五态；Mermaid 分页
[CONSUMERS] AI/人生成作战地图可视化
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] DB 不可用→exit 4; YAML 缺失→降级到 DB step_name

从 battle_map 三表（steps/anchors/edges）+ 翻译真源（battle_map_steps + battle_map_cross_cutting 段）生成作战地图：
  - 总指挥图（全部环节 + 流转边，Mermaid 分页）
  - 6 分阶段图（选股/买入/卖出/仓位/执行/对账）
  - 横切视图（Gap3：§13漏斗 / §14盘中事件 / §16冲突矩阵，来自 battle_map_cross_cutting 段）
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
  （battle_map_positioning.md §五：battle_map 取代 decisiongraph+narrative 作为交易流真源）。
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
    get_cross_cutting_all,
    get_step_indicators_zh,
    get_step_mechanism,
    get_step_name_bilingual,
    get_step_plain,
    preload_battle_map_cross_cutting,
    preload_battle_map_steps,
)
from d5_architecture.generators.zoomable_html import emit_zoomable_html  # noqa: E402

from zephyr.governance.persistence.battle_map_reader import BattleMapReader  # noqa: E402
from zephyr.governance.persistence.depgraph_reader import DepgraphReader  # noqa: E402

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

# 灰色主题头（visualization_view_template §4.1 + §13.3 clusterBkg 透明）。
# 每个 Mermaid 代码块第一行必须输出此主题头：节点背景统一浅灰，状态色（蓝/橙）由
# classDef 覆盖；clusterBkg/clusterBorder 透明让 subgraph 与分图背景一致。
_MERMAID_THEME = (
    "%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', "
    "'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', "
    "'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
    "'clusterBkg': 'transparent', 'clusterBorder': 'transparent', "
    "'fontSize': '14px'}}}%%"
)

# classDef 颜色（模板 §4.7 production/design 精确对齐 + battle map 三扩展态）。
# 治本（2026-08-02，模板对齐）：浅填充 + 黑字（color:#000）取代旧深填充白字——
# 与 visualization_view_template §4.7 域文档 classDef 风格一致，图例颜色跨文档统一。
# production/design 取模板精确色值；deprecated/missing/candidate 是 battle map 五态扩展
# （panorama §九），用同风格浅色（红/灰/黄）+ design/candidate 虚线区分"未实线落地"。
_CLASSDEFS = """classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
classDef deprecated fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
classDef missing fill:#eeeeee,stroke:#9e9e9e,stroke-width:2px,color:#000
classDef candidate fill:#fffde7,stroke:#f9a825,stroke-width:2px,color:#000,stroke-dasharray: 5 5"""

# edge_type → 中英双语标签（移入边标签，模板 §4.5 箭头按端点状态而非 edge_type 分）。
# 箭头本身由 _edge_arrow 按 from/to 的 _effective_status 推导：两端均 production→-->，
# 否则 -.->。edge_type 语义保留在标签里（数据流/触发/降级）。
_EDGE_TYPE_LABEL = {
    "data_flow": "数据流 / data_flow",
    "trigger": "触发 / trigger",
    "degradation": "降级 / degradation",
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

# 五态 → 节点标签成熟度前缀（模板 §4.3 要素①：节点首行 "(生产态 / production)" 前缀）。
# battle map 五态在模板 production/design 之外扩展 deprecated/missing/candidate——
# 成熟度前缀同样用"中文 / english"双语格式，与模板四要素风格一致。
_STATE_TO_MATURITY: dict[str, str] = {
    "production": "(生产态 / production)",
    "design": "(设计态 / design)",
    "deprecated": "(弃用态 / deprecated)",
    "missing": "(缺失态 / missing)",
    "candidate": "(候选态 / candidate)",
}

# 本地文档 HTTP server 前缀（模板 §14：HTML 链接必须 http:// 绝对路径，IDE 才会交外部浏览器）。
_HTML_SERVER_PREFIX = "http://localhost:8765/"


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
    preload_battle_map_cross_cutting()  # 预加载 YAML 横切视图缓存（Gap3）
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

    # Gap1：查 depgraph 真实 build_status + gate_reason（替代 step.design_maturity 自报着色）。
    # 治本（2026-08-02，模板 §4.3 要素⑤）：一次查询取回 build_status + gate_reason，
    # 供 ⛔ 受限原因行渲染（design 态 + gate_reason 非空时显示）。
    dg_ids = [a["target_id"] for a in anchors if a.get("target_graph") == "depgraph"]
    status_map: dict[str, str] = {}
    gate_map: dict[str, str] = {}
    if dg_ids:
        dr = DepgraphReader()
        try:
            sg_map = dr.get_status_and_gate_map(dg_ids)
        finally:
            dr.close()
        # 拆成两个 dict：status_map（供 _compute_step_status）+ gate_map（供 ⛔ 行）
        for tid, entry in sg_map.items():
            status_map[tid] = entry["build_status"]
            gr = entry.get("gate_reason") or ""
            if gr:
                gate_map[tid] = gr

    # enrich anchors：附加 live build_status
    for a in anchors:
        if a.get("target_graph") == "depgraph":
            a["_live_build_status"] = status_map.get(a["target_id"], "<未命中>")

    # enrich steps：附加有效状态 + 候选标记 + gate_reason（取 primary depgraph 锚点的）
    for s in steps:
        sid = s["step_id"]
        al = anchors_by_step.get(sid, [])
        s["_effective_status"] = _compute_step_status(al, status_map)
        s["_has_candidate"] = _has_candidate_anchor(al)
        # gate_reason：取该环节 primary depgraph 锚点的 gate_reason（首个非空）
        s["_gate_reason"] = ""
        for a in al:
            if a.get("target_role") == "primary" and a.get("target_graph") == "depgraph":
                gr = gate_map.get(a["target_id"], "")
                if gr:
                    s["_gate_reason"] = gr
                break

    return steps, edges, anchors_by_step


# ---------------------------------------------------------------------------
# Mermaid 生成
# ---------------------------------------------------------------------------


def _sanitize(text: str) -> str:
    """转义 Mermaid 节点标签中的特殊字符（模板 §4.9）。

    注意：不转义 ``<`` ``>`` —— 节点标签用 ``<br/>`` 折行，转义会破坏折行。
    旧版把 ``<>`` 替换为全角 ``〈〉`` 是因为旧标签用 ``\\n`` 折行；改用 ``<br/>`` 后
    必须保留尖括号（模板 §4.10 预折行铁律依赖 ``<br/>``）。
    """
    if not text:
        return ""
    return (
        text.replace("[", "(")
        .replace("]", ")")
        .replace('"', "'")
        .replace("|", "/")
        .replace("\n", " ")
    )


def _wrap_label_text(text: str, max_units: int = 48) -> str:
    """将长节点标签文本按显示宽度预折行（Mermaid 节点内显示用）。

    治本（2026-08-01，模板 §4.10 铁律）：Mermaid 先按标签行数测量节点框宽高，若依赖
    HTML 渲染层 CSS max-width 二次折行，渲染行数 > 测量行数 → 框高不够、文字被上下
    裁剪。必须在生成端用 ``<br/>`` 显式预折行，使测量行数 = 渲染行数。

    逐字复制自 ``generate_domain_doc.py``（真源），保持跨生成器折行逻辑一致。
    折行规则：显示宽度（CJK=2/ASCII=1）超 max_units 断行（48 ≈ 24 个汉字）；优先在
    空格之后、左括号/斜杠之前软断（保持英文词完整），否则硬断。不在下划线处软断——
    会把 context_engine 拆成 context_+engine 导致审计误判。
    """
    if not text:
        return ""
    lines: list[str] = []
    remaining = text.strip()
    while remaining:
        width = 0
        cut = 0
        soft = -1  # 软断点（断在空格之后，或（(/之前）
        for i, ch in enumerate(remaining):
            u = 2 if ord(ch) > 0x2E7F else 1
            if width + u > max_units:
                break
            width += u
            cut = i + 1
            if ch == " ":
                soft = i + 1
            elif ch in "（(/":
                soft = i if i > 0 else -1
        if cut >= len(remaining):
            lines.append(remaining)
            break
        if soft >= 8:  # 软断点至少留 8 单位，避免碎片行
            cut = soft
        line = remaining[:cut].rstrip()
        if line:
            lines.append(line)
        remaining = remaining[cut:].lstrip(" ")
    return "<br/>".join(lines)


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
    """构建节点标签（模板 §4.3 四要素 + ⛔ 第五行 + 状态标记）。

    结构（每行过 ``_wrap_label_text`` 预折行，再用 ``<br/>`` 拼接，模板 §4.10 铁律）：
      第1行：(成熟度) step_id 中文名 / English       ← 要素①②
      第2行：大白话简介                              ← 要素③
      第3行：作战环节 / battle-step                   ← 要素④（流程步骤标识，§9.3 适配）
      第4行（可选）：标记（⚠无锚点 / 🟡候选承载）
      第5行（可选）：⛔ 受限原因（仅 design 态 + gate_reason 非空，要素⑤）
    """
    sid = step["step_id"]
    name_bi = get_step_name_bilingual(sid) or step.get("step_name", sid)
    plain = get_step_plain(sid)
    status = step.get("_effective_status") or "design"
    maturity = _STATE_TO_MATURITY.get(status, "(设计态 / design)")

    parts: list[str] = [f"{maturity} {sid} {name_bi}".strip()]
    parts.append(plain if plain else "—")
    parts.append("作战环节 / battle-step")

    marks: list[str] = []
    if status == "missing":
        marks.append("⚠无锚点")
    if step.get("_has_candidate"):
        marks.append("🟡候选承载")
    if marks:
        parts.append("、".join(marks))

    gate = (step.get("_gate_reason") or "").strip()
    if status == "design" and gate:
        parts.append(f"⛔ {gate}")

    label = "<br/>".join(_wrap_label_text(p) for p in parts if p)
    return _sanitize(label)


def _mermaid_node_id(step_id: str) -> str:
    """Mermaid 节点 ID（step_id 含连字符，替换为下划线的安全 id）。"""
    return step_id.replace("-", "_")


def _edge_arrow(from_status: str, to_status: str) -> str:
    """边箭头（模板 §4.5）：两端均 production → ``-->`` 实线，否则 ``-.->`` 虚线。"""
    if from_status == "production" and to_status == "production":
        return "-->"
    return "-.->"


def _edge_label(edge: dict) -> str:
    """边标签（模板 §4.5：``|中英双语|``）。

    优先用 DB 具体标签（如"标准化行情"）+ edge_type 英文（``标准化行情 / data_flow``）；
    无 DB 标签则用 edge_type 双语（``数据流 / data_flow``）。
    """
    et = edge.get("edge_type") or ""
    db_label = (edge.get("label") or "").strip()
    if db_label and et:
        text = f"{db_label} / {et}"
    elif db_label:
        text = db_label
    else:
        text = _EDGE_TYPE_LABEL.get(et, f"{et} / {et}" if et else "流转 / flow")
    return f"|{_sanitize(text)}|"


def _topological_layers(steps: list[dict], edges: list[dict]) -> dict[str, int]:
    """Kahn 算法计算拓扑层级（模板 §4.6 强制竖排）。

    ``layer(n) = max(layer(前驱)) + 1``；入度 0 = layer 0；环内剩余节点统一放当前层
    （断环兜底）。仅按本图内有效边算（边两端都在 steps 集合内）。

    返回 ``{step_id: layer}``，供 ``_emit_layer_chains`` 输出 ``~~~`` 同层串联。
    """
    step_ids = {s["step_id"] for s in steps}
    preds: dict[str, list[str]] = {sid: [] for sid in step_ids}
    for e in edges:
        f, t = e.get("from_step_id"), e.get("to_step_id")
        if f in step_ids and t in step_ids:
            preds[t].append(f)
    layer: dict[str, int] = {}
    remaining = set(step_ids)
    current = 0
    while remaining:
        ready = [sid for sid in remaining if all(p in layer for p in preds[sid])]
        if not ready:
            # 环：剩余节点统一放当前层，断环保证有层级
            for sid in remaining:
                layer[sid] = current
            break
        for sid in ready:
            layer[sid] = current
            remaining.discard(sid)
        current += 1
    return layer


def _emit_layer_chains(steps: list[dict], layer_map: dict[str, int]) -> list[str]:
    """同层节点用 ``~~~`` 不可见边串联（模板 §4.6：强制同 rank 横排，层间纵向流动）。"""
    by_layer: dict[int, list[str]] = {}
    for s in steps:
        sid = s["step_id"]
        by_layer.setdefault(layer_map.get(sid, 0), []).append(_mermaid_node_id(sid))
    lines: list[str] = []
    for lv in sorted(by_layer):
        ids = by_layer[lv]
        if len(ids) >= 2:
            lines.append("    " + " ~~~ ".join(ids))
    return lines


def _class_statements(steps: list[dict]) -> list[str]:
    """class 应用语句（模板 §4.8：按状态分组 ``class a,b,c production``）。"""
    by_class: dict[str, list[str]] = {}
    for s in steps:
        by_class.setdefault(_node_class(s), []).append(_mermaid_node_id(s["step_id"]))
    out: list[str] = []
    for cls in ("production", "design", "deprecated", "missing", "candidate"):
        ids = by_class.get(cls)
        if ids:
            out.append(f"    class {','.join(ids)} {cls}")
    return out


def _build_mermaid(
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
    title: str,
) -> str:
    """构建一个 Mermaid 流程图块（模板合规：主题头 + TD + 四要素节点 + 拓扑分层 + 状态边 + class）。"""
    lines = ["```mermaid", _MERMAID_THEME, f"%% {title}", "flowchart TD"]
    step_ids = {s["step_id"] for s in steps}
    status_by_id = {s["step_id"]: s.get("_effective_status") or "design" for s in steps}

    # 节点定义（标签含四要素 + 预折行；颜色由末尾 class 语句绑，不内联 :::cls）
    for s in steps:
        nid = _mermaid_node_id(s["step_id"])
        label = _node_label(s)
        lines.append(f'    {nid}["{label}"]')

    # 拓扑分层 ~~~ 同层串联（模板 §4.6 强制竖排）
    layer_map = _topological_layers(steps, edges)
    lines.extend(_emit_layer_chains(steps, layer_map))

    # 边定义（只画两端都在本图 step 集内的边；箭头按端点状态，标签含 edge_type）
    for e in edges:
        if e["from_step_id"] in step_ids and e["to_step_id"] in step_ids:
            from_n = _mermaid_node_id(e["from_step_id"])
            to_n = _mermaid_node_id(e["to_step_id"])
            arrow = _edge_arrow(status_by_id[e["from_step_id"]], status_by_id[e["to_step_id"]])
            lines.append(f"    {from_n} {arrow}{_edge_label(e)} {to_n}")

    # classDef + class 应用（模板 §4.7 + §4.8）
    lines.append(_CLASSDEFS)
    lines.extend(_class_statements(steps))
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
        """_kv implementation."""
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
        "status: active\n"
        'version: "1.0.0"\n'
        f"date: {date.today().isoformat()}\n"
        "---\n"
    )


def _html_link_line(stem: str) -> str:
    """HTML 跳转链接（模板 §14：http:// 绝对路径，IDE 才会交外部浏览器渲染）。

    :param stem: MD 文件名 stem（如 ``battle_map_panorama``），对应 ``_zoomable_html/<stem>.html``
    """
    url = (
        f"{_HTML_SERVER_PREFIX}docs/02_enterprise_architecture/"
        f"07_trading_decision_architecture/battle_map/_zoomable_html/{stem}.html"
    )
    return (
        f"> **[可缩放 HTML 版 / Zoomable HTML]({url})** "
        "— Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式"
    )


def _legend_blockquote() -> str:
    """图例说明 blockquote（模板 §3.1，适配 battle map 五态 + 双箭头）。"""
    return (
        "> **图例说明 / Legend**：\n"
        "> - 🟦 **蓝色实线 = 运营态环节**（production，锚点模块已建）\n"
        "> - 🟧 **橙色虚线 = 设计态环节**（design，锚点模块待施工）\n"
        "> - 🟥 **红色 = 弃用态**（deprecated）\n"
        "> - ⬜ **灰色 = 缺失态**（missing，环节无锚点，BM-INV-001 违例）\n"
        "> - 🟨 **黄色虚线 = 候选态**（candidate，承载模块在候选池）\n"
        "> - **实线箭头 ``-->`` = 运营态流转**（两端均 production）\n"
        "> - **虚线箭头 ``-.->`` = 非运营态流转**（含设计/候选/混合）"
    )


def _view_subset(
    steps: list[dict], edges: list[dict], statuses: set[str]
) -> tuple[list[dict], list[dict]]:
    """按展示态筛选视图子集（模板 §3.2：运营态=production，设计态=design）。

    返回 (筛选后 steps, 两端均在筛选集内且两端状态均在 statuses 内的 edges)。
    candidate/deprecated/missing 不进运营/设计视图，仅在全景图展示。
    """
    sel = [s for s in steps if s.get("_effective_status") in statuses]
    sel_ids = {s["step_id"] for s in sel}
    sel_edges = [
        e for e in edges
        if e["from_step_id"] in sel_ids and e["to_step_id"] in sel_ids
    ]
    return sel, sel_edges


def _generate_panorama_md(
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
) -> str:
    """总指挥图 MD（三视图 + 每环节详情，模板 §3.1/§3.2 铁律）。"""
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

    # 三视图子集（模板 §3.2：全景图 → 运营态的图 → 设计态的图）
    prod_steps, prod_edges = _view_subset(steps, edges, {"production"})
    design_steps, design_edges = _view_subset(steps, edges, {"design"})

    parts: list[str] = [
        "# 交易决策作战地图（总指挥图）",
        "",
        _html_link_line("battle_map_panorama"),
        "",
        "> 第四全景图 battle_map 真源：`battle_map_steps` / `battle_map_anchors` / `battle_map_edges` 三表 + 翻译真源 `module_translation_registry.yaml` §battle_map_steps 段。",
        "> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编（改环节→改 DB/YAML 真源→重跑生成器）。",
        "",
        "## 文档基本信息 / Document Overview",
        "",
        "| 字段 | 值 | Field | Value |",
        "|------|------|-------|-------|",
        f"| 环节总数 | {len(steps)} | Steps | {len(steps)} |",
        f"| 流转边 | {len(edges)} | Edges | {len(edges)} |",
        f"| 无锚点环节（BM-INV-001） | {no_anchor_count} | No-Anchor Steps | {no_anchor_count} |",
        f"| 运营态环节 | {len(prod_steps)} | Production Steps | {len(prod_steps)} |",
        f"| 设计态环节 | {len(design_steps)} | Design Steps | {len(design_steps)} |",
        f"| 状态分布 | {dist} | State Distribution | {dist} |",
        "",
        _legend_blockquote(),
        "",
        "## 域内依赖图 / Internal Dependency Diagram",
        "",
        "> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。",
        "",
        "### 全景图（全部环节，颜色区分五态）",
        "",
        f"> 展示全部 {len(steps)} 个环节（运营态 {len(prod_steps)} + 设计态 {len(design_steps)} "
        f"+ 弃用/缺失/候选 {len(steps) - len(prod_steps) - len(design_steps)}），含跨阶段流转边。",
        "",
        _build_mermaid_paged(steps, edges, anchors_by_step, "作战地图总指挥图·全景图"),
        "",
        "### 运营态的图（仅 production 环节和流转）",
        "",
    ]
    if prod_steps:
        parts.append(f"> 仅展示已上线运行的环节（共 {len(prod_steps)} 个），不含跨阶段外部节点。")
        parts.append("")
        parts.append(_build_mermaid_paged(prod_steps, prod_edges, anchors_by_step, "作战地图·运营态"))
    else:
        parts.append("> （无环节 / No steps）")
    parts.append("")

    parts.append("### 设计态的图（仅 design 环节和流转）")
    parts.append("")
    if design_steps:
        parts.append(f"> 仅展示设计态、锚点模块待施工的环节（共 {len(design_steps)} 个）。")
        parts.append("")
        parts.append(_build_mermaid_paged(design_steps, design_edges, anchors_by_step, "作战地图·设计态"))
    else:
        parts.append("> （无环节 / No steps）")
    parts.append("")

    parts += [
        "## 分阶段导航",
        "",
    ]
    for stage_id, stage_name, num in FLOW_STAGES:
        stage_steps = [s for s in steps if s["flow_stage"] == stage_id]
        parts.append(f"- [{stage_name}阶段（{len(stage_steps)} 环节）](battle_map_{num}_{stage_id}.md)")
    parts.append("- [横切视图（§13漏斗 / §14盘中事件 / §16冲突矩阵）](battle_map_07_cross_cutting.md)")
    parts.append("")
    parts.append("## 全环节详情（6 件套）")
    parts.append("")
    for s in sorted(steps, key=lambda x: (x["flow_stage"], x.get("sort_order", 0))):
        parts.append(_format_step_detail(s, anchors_by_step.get(s["step_id"], [])))
    return "\n".join(parts)


def _generate_stage_md(
    stage_id: str,
    stage_name: str,
    stage_num: str,
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
) -> str:
    """单阶段 MD（模板合规：HTML链接 + 基本信息表 + 图例 + 阶段图 + 详情）。

    治本（2026-08-02，模板对齐）：补齐 HTML 跳转链接、文档基本信息表、图例说明，
    与 panorama 文档结构一致；阶段图是单视图（§9.2 视图数量按需，阶段级无需三视图）。
    """
    stage_steps = [s for s in steps if s["flow_stage"] == stage_id]
    stage_step_ids = {s["step_id"] for s in stage_steps}
    # 边：任一端在本阶段
    stage_edges = [
        e for e in edges
        if e["from_step_id"] in stage_step_ids or e["to_step_id"] in stage_step_ids
    ]
    # 五态分布统计
    state_counts: dict[str, int] = {}
    for s in stage_steps:
        st = s.get("_effective_status", "design")
        state_counts[st] = state_counts.get(st, 0) + 1
    dist = " ｜ ".join(
        f"{_STATE_LABEL.get(st, st)}={cnt}"
        for st, cnt in sorted(state_counts.items(), key=lambda x: -x[1])
    ) or "—"
    stem = f"battle_map_{stage_num}_{stage_id}"

    parts: list[str] = [
        f"# 作战地图·{stage_name}阶段",
        "",
        _html_link_line(stem),
        "",
        f"> battle_map §{stage_id} 阶段，{len(stage_steps)} 环节。",
        "> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。",
        "",
        "## 文档基本信息 / Document Overview",
        "",
        "| 字段 | 值 | Field | Value |",
        "|------|------|-------|-------|",
        f"| 阶段 | {stage_name}（{stage_id}） | Stage | {stage_name} |",
        f"| 环节数 | {len(stage_steps)} | Steps | {len(stage_steps)} |",
        f"| 流转边 | {len(stage_edges)} | Edges | {len(stage_edges)} |",
        f"| 状态分布 | {dist} | State Distribution | {dist} |",
        "",
        _legend_blockquote(),
        "",
        "## 阶段图 / Stage Diagram",
        "",
        f"> 展示 {stage_name} 阶段全部 {len(stage_steps)} 个环节及流转边，颜色区分五态。",
        "",
        _build_mermaid_paged(stage_steps, stage_edges, anchors_by_step, f"{stage_name}阶段图"),
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
# 横切视图生成（Gap3，2026-08-01）
# ---------------------------------------------------------------------------


def _related_steps_links(related_steps: list[str]) -> str:
    """把 related_steps 列表渲染为指向分阶段文档的链接串（找不到则纯文本）。"""
    if not related_steps:
        return "—"
    # step_id → 所在分阶段文档（BM-SEL-* → 01_stock_selection，依此类推）
    stage_prefix = {
        "BM-SEL": "01_stock_selection",
        "BM-BUY": "02_buy_flow",
        "BM-SELL": "03_sell_flow",
        "BM-POS": "04_position_management",
        "BM-EXE": "05_execution",
        "BM-REC": "06_reconciliation",
    }
    links: list[str] = []
    for sid in related_steps:
        prefix = "-".join(sid.split("-")[:2])
        doc = stage_prefix.get(prefix)
        if doc:
            links.append(f"[{sid}](battle_map_{doc}.md)")
        else:
            links.append(sid)
    return "、".join(links)


def _format_funnel_md(item: dict) -> str:
    """渲染 §13 筛选漏斗模型为 Markdown（6层漏斗表 + 机制说明）。"""
    name_bi = item.get("name_zh", "") + (
        f" / {item['name_en']}" if item.get("name_en") else ""
    )
    parts = [
        f"## {name_bi}（{item.get('sketch_ref', '')}）",
        "",
        f"> **大白话**：{item.get('plain_zh', '').strip()}",
        "",
    ]
    mech = item.get("mechanism_zh", "").strip()
    if mech:
        parts += ["**机制说明**：", "", mech, ""]
    related = item.get("related_steps") or []
    if related:
        parts.append(f"**关联环节**：{_related_steps_links(related)}")
        parts.append("")
    levels = item.get("levels") or []
    if levels:
        parts += [
            "### 漏斗层级（6层过滤）",
            "",
            "| 层 | 名称 | 延迟 | 吞吐 | 筛选条件 |",
            "|---|---|---|---|---|",
        ]
        for lv in levels:
            filters = lv.get("filters") or []
            filt_text = "<br>".join(f"- {f}" for f in filters) if filters else "—"
            status = lv.get("status")
            name = lv.get("name_zh", "—")
            if status:
                name = f"{name}（{status}）"
            parts.append(
                f"| L{lv.get('level', '?')} | {name} | {lv.get('latency', '—')} "
                f"| {lv.get('throughput', '—')} | {filt_text} |"
            )
        parts.append("")
    return "\n".join(parts)


def _format_intraday_events_md(item: dict) -> str:
    """渲染 §14 盘中实时事件处理为 Markdown（事件类型表 + 流水线 + 对账）。"""
    name_bi = item.get("name_zh", "") + (
        f" / {item['name_en']}" if item.get("name_en") else ""
    )
    parts = [
        f"## {name_bi}（{item.get('sketch_ref', '')}）",
        "",
        f"> **大白话**：{item.get('plain_zh', '').strip()}",
        "",
    ]
    mech = item.get("mechanism_zh", "").strip()
    if mech:
        parts += ["**机制说明**：", "", mech, ""]
    related = item.get("related_steps") or []
    if related:
        parts.append(f"**关联环节**：{_related_steps_links(related)}")
        parts.append("")
    # 事件类型表
    event_types = item.get("event_types") or []
    if event_types:
        parts += [
            "### 事件类型清单（7类）",
            "",
            "| 级别 | 事件类型 | 触发源 | 影响范围 | 重算粒度 | 延迟 |",
            "|---|---|---|---|---|---|",
        ]
        for et in event_types:
            parts.append(
                f"| **{et.get('level', '—')}** | {et.get('types', '—')} "
                f"| {et.get('source', '—')} | {et.get('scope', '—')} "
                f"| {et.get('recompute', '—')} | {et.get('latency', '—')} |"
            )
        parts.append("")
    # 处理流水线
    pipeline = item.get("pipeline") or []
    if pipeline:
        parts += ["### 事件处理流水线", ""]
        for i, step in enumerate(pipeline, 1):
            parts.append(f"{i}. {step}")
        parts.append("")
    # 持仓对账
    recon = item.get("position_reconciliation") or {}
    if recon:
        parts += [
            "### 盘中持仓对账机制",
            "",
            "| 维度 | 规则 |",
            "|---|---|",
            f"| 对账频率 | {recon.get('frequency', '—')} |",
            f"| 差异处理 | {recon.get('diff_handling', '—')} |",
            f"| 审计记录 | {recon.get('audit', '—')} |",
            f"| 降级模式 | {recon.get('degradation', '—')} |",
            "",
        ]
    return "\n".join(parts)


def _format_conflict_matrix_md(item: dict) -> str:
    """渲染 §16 能力冲突矩阵为 Markdown（优先级表 + 31冲突场景表）。"""
    name_bi = item.get("name_zh", "") + (
        f" / {item['name_en']}" if item.get("name_en") else ""
    )
    parts = [
        f"## {name_bi}（{item.get('sketch_ref', '')}）",
        "",
        f"> **大白话**：{item.get('plain_zh', '').strip()}",
        "",
    ]
    mech = item.get("mechanism_zh", "").strip()
    if mech:
        parts += ["**机制说明**：", "", mech, ""]
    related = item.get("related_steps") or []
    if related:
        parts.append(f"**关联环节**：{_related_steps_links(related)}")
        parts.append("")
    # 优先级层次
    hierarchy = item.get("priority_hierarchy") or []
    if hierarchy:
        parts += [
            "### 仲裁优先级总原则（防御永远优先于进攻）",
            "",
            "| 排名 | 优先级持有者 | 说明 |",
            "|---|---|---|",
        ]
        for h in hierarchy:
            note = h.get("note") or "—"
            parts.append(
                f"| {h.get('rank', '?')} | {h.get('holder', '—')} | {note} |"
            )
        parts.append("")
    # 冲突场景表
    conflicts = item.get("conflicts") or []
    if conflicts:
        parts += [
            f"### 冲突场景清单（{len(conflicts)} 条）",
            "",
            "| # | 冲突方 | 冲突场景 | 仲裁规则 | 胜出 |",
            "|---|---|---|---|---|",
        ]
        for i, cf in enumerate(conflicts, 1):
            parts.append(
                f"| {i} | {cf.get('parties', '—')} | {cf.get('scenario', '—')} "
                f"| {cf.get('arbitration', '—')} | {cf.get('winner', '—')} |"
            )
        parts.append("")
    return "\n".join(parts)


def _format_timeline_md(item: dict) -> str:
    """渲染 §15 计算节奏与时序为 Markdown（三段式时序阶段 + 计算频率表）。"""
    name_bi = item.get("name_zh", "") + (
        f" / {item['name_en']}" if item.get("name_en") else ""
    )
    parts = [
        f"## {name_bi}（{item.get('sketch_ref', '')}）",
        "",
        f"> **大白话**：{item.get('plain_zh', '').strip()}",
        "",
    ]
    mech = item.get("mechanism_zh", "").strip()
    if mech:
        parts += ["**机制说明**：", "", mech, ""]
    related = item.get("related_steps") or []
    if related:
        parts.append(f"**关联环节**：{_related_steps_links(related)}")
        parts.append("")
    # 三段式时序阶段
    phases = item.get("phases") or []
    if phases:
        parts += [
            "### 时序阶段（盘前→盘中→盘后）",
            "",
            "| 阶段 | 时间 | 关键动作 |",
            "|---|---|---|",
        ]
        for ph in phases:
            actions = ph.get("actions") or []
            act_text = "<br>".join(actions) if actions else "—"
            parts.append(
                f"| {ph.get('name_zh', '—')} | {ph.get('time_range', '—')} | {act_text} |"
            )
        parts.append("")
    # 计算频率汇总
    freqs = item.get("compute_frequencies") or []
    if freqs:
        parts += [
            "### 计算频率汇总",
            "",
            "| 频率 | 计算内容 | 标的数 | CPU负载 | 数据源 |",
            "|---|---|---|---|---|",
        ]
        for fr in freqs:
            parts.append(
                f"| {fr.get('frequency', '—')} | {fr.get('content', '—')} "
                f"| {fr.get('scope', '—')} | {fr.get('cpu_load', '—')} "
                f"| {fr.get('data_source', '—')} |"
            )
        parts.append("")
    return "\n".join(parts)


def _format_distribution_awareness_md(item: dict) -> str:
    """渲染 §1.7 分布感知增强体系为 Markdown（四方法论表 + 叠加态模式）。"""
    name_bi = item.get("name_zh", "") + (
        f" / {item['name_en']}" if item.get("name_en") else ""
    )
    parts = [
        f"## {name_bi}（{item.get('sketch_ref', '')}）",
        "",
        f"> **大白话**：{item.get('plain_zh', '').strip()}",
        "",
    ]
    mech = item.get("mechanism_zh", "").strip()
    if mech:
        parts += ["**机制说明**：", "", mech, ""]
    related = item.get("related_steps") or []
    if related:
        parts.append(f"**关联环节**：{_related_steps_links(related)}")
        parts.append("")
    # 四方法论分工表
    methods = item.get("four_methods") or []
    if methods:
        parts += [
            "### 四方法论分工（从点估计升级为完整分布描述）",
            "",
            "| 方法论 | 回答的问题 | 输出 | 下游消费 | 实现阶段 | 关联环节 |",
            "|---|---|---|---|---|---|",
        ]
        for m in methods:
            m_related = m.get("related_steps") or []
            m_rel_text = ", ".join(m_related) if m_related else "—"
            parts.append(
                f"| {m.get('name_zh', '—')} | {m.get('question', '—')} "
                f"| {m.get('output', '—')} | {m.get('downstream', '—')} "
                f"| {m.get('stage', '—')} | {m_rel_text} |"
            )
        parts.append("")
    # 叠加态模式
    overlay = item.get("overlay_mode")
    if overlay:
        parts += [
            f"### {overlay.get('name_zh', '叠加态模式')}",
            "",
            overlay.get("description", "").strip(),
            "",
        ]
    return "\n".join(parts)


def _format_generic_cross_cutting_md(item: dict) -> str:
    """渲染通用横切视图项（标题+大白话+机制说明+关联环节+可选结构化表）。

    用于退役迁移自 trading_flow_narrative.yaml §cross_cutting 的 4 个系统级横切段
    （four_modes / emergency_degradation / four_tracks / shared_signal_injection）。
    这些段无对应草图§ref（sketch_ref="—"），结构化字段按类别可选渲染：
      - four_modes              → modes 表
      - emergency_degradation   → degradation_tiers 表
      - four_tracks             → tracks 表
      - shared_signal_injection → 纯叙事（无结构化表）
    """
    name_bi = item.get("name_zh", "") + (
        f" / {item['name_en']}" if item.get("name_en") else ""
    )
    parts = [
        f"## {name_bi}（{item.get('sketch_ref', '—')}）",
        "",
        f"> **大白话**：{item.get('plain_zh', '').strip()}",
        "",
    ]
    mech = item.get("mechanism_zh", "").strip()
    if mech:
        parts += ["**机制说明**：", "", mech, ""]
    related = item.get("related_steps") or []
    if related:
        parts.append(f"**关联环节**：{_related_steps_links(related)}")
        parts.append("")
    # 四模式开关：modes 表
    modes = item.get("modes") or []
    if modes:
        parts += [
            "### 模式清单",
            "",
            "| 模式ID | 名称 | 数据源 | 下单方式 |",
            "|---|---|---|---|",
        ]
        for m in modes:
            parts.append(
                f"| {m.get('mode_id', '—')} | {m.get('mode_name', '—')} "
                f"| {m.get('data_source', '—')} | {m.get('order_mode', '—')} |"
            )
        parts.append("")
    # 应急保命降级：degradation_tiers 表
    tiers = item.get("degradation_tiers") or []
    if tiers:
        parts += [
            "### 降级路径（逐级保命）",
            "",
            "| 触发条件 | 失效层 | 降级行为 |",
            "|---|---|---|",
        ]
        for t in tiers:
            parts.append(
                f"| {t.get('trigger', '—')} | {t.get('failed_layer', '—')} "
                f"| {t.get('fallback', '—')} |"
            )
        parts.append("")
    # 四轨并行：tracks 表
    tracks = item.get("tracks") or []
    if tracks:
        parts += [
            "### 四轨清单",
            "",
            "| 轨道 | 角色 | 优先级 | 说明 |",
            "|---|---|---|---|",
        ]
        for tr in tracks:
            parts.append(
                f"| {tr.get('track_id', '—')} | {tr.get('role', '—')} "
                f"| {tr.get('priority', '—')} | {tr.get('description', '—')} |"
            )
        parts.append("")
    return "\n".join(parts)


# 横切类别 → 渲染函数分派（ Gap3 + 退役迁移横切段 ）
_CROSS_CUTTING_RENDERERS = {
    "funnel": _format_funnel_md,
    "intraday_events": _format_intraday_events_md,
    "timeline": _format_timeline_md,
    "conflict_matrix": _format_conflict_matrix_md,
    "distribution_awareness": _format_distribution_awareness_md,
    # 以下 4 项退役迁移自 trading_flow_narrative.yaml §cross_cutting（2026-08-02）
    "four_modes": _format_generic_cross_cutting_md,
    "emergency_degradation": _format_generic_cross_cutting_md,
    "four_tracks": _format_generic_cross_cutting_md,
    "shared_signal_injection": _format_generic_cross_cutting_md,
}


def _generate_cross_cutting_md() -> str:
    """横切视图 MD（§13漏斗 + §14盘中事件 + §16冲突矩阵 + 4 退役迁移段，Gap3）。

    横切内容来自翻译真源 battle_map_cross_cutting 段（规则数据，TRAE-062），
    不属任何单一阶段，贯穿选股→买入→卖出→仓位→执行→对账全流程。

    2026-08-02 退役迁移：trading_flow_narrative.yaml §cross_cutting 的 4 个系统级横切段
    （four_modes / emergency_degradation / four_tracks / shared_signal_injection）
    迁入本段，由 _format_generic_cross_cutting_md 渲染。
    """
    items = get_cross_cutting_all()
    parts = [
        "# 交易决策作战地图（横切视图）",
        "",
        "> 横切贯穿全流程的全局机制：§13 筛选漏斗 / §14 盘中实时事件处理 / §16 能力冲突矩阵与仲裁规则",
        ">           + 4 系统级横切（四模式开关 / 应急保命降级 / 四轨并行 / 共享信号注入，迁移自 trading_flow_narrative.yaml）。",
        "> 真源：`module_translation_registry.yaml` §battle_map_cross_cutting 段（规则数据，TRAE-062）。",
        "> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。",
        "",
    ]
    if not items:
        parts.append("⚠ 未加载到横切视图数据（YAML battle_map_cross_cutting 段缺失或解析失败）。")
        return "\n".join(parts)
    parts.append(
        f"**横切类别数**：{len(items)}（funnel / intraday_events / conflict_matrix / "
        f"timeline / distribution_awareness / four_modes / emergency_degradation / "
        f"four_tracks / shared_signal_injection）"
    )
    parts.append("")
    for item in items:
        cat = item.get("category", "")
        renderer = _CROSS_CUTTING_RENDERERS.get(cat)
        if renderer:
            parts.append(renderer(item))
        else:
            # 未知类别兜底：渲染基础字段
            parts.append(f"## {item.get('name_zh', cat)}（{item.get('sketch_ref', '')}）")
            parts.append("")
            parts.append(f"> {item.get('plain_zh', '').strip()}")
            parts.append("")
    parts.append("[← 返回总指挥图](battle_map_panorama.md)")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
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
        stage_md = _generate_stage_md(stage_id, stage_name, num, steps, edges, anchors_by_step)
        stage_md = f"{_make_frontmatter()}\n{stage_md}"
        stage_path = out_dir / f"battle_map_{num}_{stage_id}.md"
        stage_path.write_text(stage_md, encoding="utf-8")
        html = emit_zoomable_html(stage_path, stage_md)
        print(f"  {stage_name}阶段: {stage_path}" + (f" + HTML: {html}" if html else ""))

    # 横切视图（Gap3：§13漏斗 / §14盘中事件 / §16冲突矩阵）
    cross_md = _generate_cross_cutting_md()
    cross_md = f"{_make_frontmatter()}\n{cross_md}"
    cross_path = out_dir / "battle_map_07_cross_cutting.md"
    cross_path.write_text(cross_md, encoding="utf-8")
    html = emit_zoomable_html(cross_path, cross_md)
    print(f"  横切视图: {cross_path}" + (f" + HTML: {html}" if html else ""))

    print(f"\n完成。输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
