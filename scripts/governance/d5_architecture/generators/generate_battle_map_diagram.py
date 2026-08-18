# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_positioning.md | §battlemap
# [MODULE] scripts.governance.d5_architecture.generators.generate_battle_map_diagram
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.governance.persistence.battle_map_reader (BattleMapReader); scripts.governance._shared.module_translation_loader (get_step_*; get_cross_cutting_*); scripts.governance.d5_architecture.generators.zoomable_html (emit_zoomable_html)
# [CONSUMERS] AI/人生成交易决策作战地图可视化（Mermaid + 可缩放 HTML）
# [STARTUP] event_driven
# [TRIGGER] apply_battle_map commit→reconcile_generators.reconcile('battle_map_db'); boot_hooks启动→reconcile_stale() mtime对比YAML
# [MATURITY] production
# [INVARIANTS] 只读 battle_map三表 + 翻译真源 battle_map_steps段（BM-INV-003）+ battle_map_cross_cutting段（Gap3）；颜色按锚点模块 depgraph build_status 推导五态（panorama §九）；Mermaid 分页防 >100 节点渲染失败
# [MODIFY-GUARD] 对标 generate_trading_flow_diagram.py + zoomable_html.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 不可用→exit 4; YAML 缺失→降级到 DB step_name
# [TESTS] tests/test_generate_battle_map_diagram.py (规划中)
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
  - 11 分阶段图（研究孵化/模型训练/回测验证/仿真验证/选股/买入/卖出/仓位/风控管控/执行/对账）
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

__manifest__ = """
args: []
description: generate_battle_map_diagram.py — 交易决策作战地图可视化生成器
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
# d5_architecture/generators 在 sys.path 上（用于 zoomable_html + _common）
_SCRIPTS_DIR = str(_THIS_FILE.parents[3])
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
# 治本（#ARCH-REGEN-NONIDEMPOTENT-001）：generators 目录加入 sys.path，
# in-process 加载（reconciler/tests）时 _common 可解析（正典先例：generate_data_acquisition_flow.py）
_THIS_DIR = str(_THIS_FILE.parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from _common import idempotent_date  # noqa: E402  # noqa: import-integrity  sys.path动态加载的本地模块
from _shared.constants import (  # noqa: E402  # noqa: import-integrity  sys.path动态加载的本地模块
    DOC_HTTP_BASE,
    REPO_ROOT,
)
from _shared.module_translation_loader import (  # noqa: E402  # noqa: import-integrity  sys.path动态加载的本地模块
    get_cross_cutting_all,
    get_step_indicators_zh,
    get_step_mechanism,
    get_step_name_bilingual,
    get_step_plain,
    preload_battle_map_cross_cutting,
    preload_battle_map_steps,
)
from d5_architecture.generators.zoomable_html import (
    emit_zoomable_html,  # noqa: E402  # noqa: import-integrity  sys.path动态加载的本地模块
)

from zephyr.governance.persistence.battle_map_reader import BattleMapReader  # noqa: E402
from zephyr.governance.persistence.depgraph_reader import DepgraphReader  # noqa: E402

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 11 阶段定义（与 battle_map_steps.flow_stage 对齐）
# 2026-08-03 全生命周期扩展：+5 新阶段 + 生命周期重排号
# 生命周期序：研究孵化→模型训练→回测验证→仿真验证→选股→买入→卖出→仓位→风控管控→执行→对账
# 横切视图（cross_cutting）单独处理，编号 12（非 flow_stage，来自 YAML battle_map_cross_cutting 段）
FLOW_STAGES = [
    ("research_incubation", "研究孵化", "01"),
    ("model_training", "模型训练", "02"),
    ("backtest_validation", "回测验证", "03"),
    ("simulation_validation", "仿真验证", "04"),
    ("stock_selection", "选股", "05"),
    ("buy_flow", "买入", "06"),
    ("sell_flow", "卖出", "07"),
    ("position_management", "仓位", "08"),
    ("risk_control", "风控管控", "09"),
    ("execution", "执行", "10"),
    ("reconciliation", "对账", "11"),
]

# flow_stage -> 节点标签第4行"所属阶段"（V1.5：替换原"作战环节 / battle-step"冗余标识）
FLOW_STAGE_LABELS = {fs_id: f"{zh}阶段 / {fs_id}" for fs_id, zh, _ in FLOW_STAGES}

# step_id 前缀（BM-<阶段缩写>）→ 分阶段文档文件名（不含 battle_map_ 前缀和 .md 后缀）
# 2026-08-03 全生命周期扩展：从 6 阶段扩展到 11 阶段，与 FLOW_STAGES 编号对齐
# 用于 _related_steps_links() 把横切视图里的 related_steps 渲染为指向分阶段文档的链接
_STEP_PREFIX_TO_STAGE_FILE = {
    "BM-RES": "01_research_incubation",
    "BM-MT": "02_model_training",
    "BM-BT": "03_backtest_validation",
    "BM-SIM": "04_simulation_validation",
    "BM-SEL": "05_stock_selection",
    "BM-BUY": "06_buy_flow",
    "BM-SELL": "07_sell_flow",
    "BM-POS": "08_position_management",
    "BM-RC": "09_risk_control",
    "BM-EXE": "10_execution",
    "BM-REC": "11_reconciliation",
}

# flow_stage → 算法纵览环节文件路径（用于深链接到 08_algorithm_overview/stages/XX.md）
_FLOW_STAGE_TO_ALGO_FILE = {fs_id: f"stages/{num}_{fs_id}.md" for fs_id, _, num in FLOW_STAGES}

# Mermaid 分页大小（防 >100 节点渲染失败，memory lesson）
# V1.5：48 环节全景图分 2 页用户反馈不直观，调到 60 合并为单图
PAGE_SIZE = 60

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

# acquisition_method → emoji 标记（2026-08-05 acquisition 字段基础设施）。
# 枚举真源 = DDL CHECK 约束（depgraph_schema._DDL_NODES_METADATA），此处仅展示层映射，
# 不复制枚举列表——非法值不会从 DB 返回（被 CHECK 拒绝），故 .get(am, "") 兜底即可。
_ACQUISITION_BADGE: dict[str, str] = {
    "self_build": "[🔴自建]",
    "opensource": "[🟢开源]",
    "borrow": "[🟡借鉴]",
    "deprecate": "[⬜弃用]",
}

# 本地文档 HTTP server 前缀（模板 §14：HTML 链接必须 http:// 绝对路径，IDE 才会交外部浏览器）。
# 真源：_shared.constants.DOC_HTTP_BASE（MOD-INF-005 SSoT），不再此处硬编码。
_HTML_SERVER_PREFIX = DOC_HTTP_BASE + "/"


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
    # 治本（2026-08-05，acquisition 字段基础设施）：同查询取回 acquisition_method，
    # 供环节详情渲染 [🔴自建]/[🟢开源]/[🟡借鉴] 标记，避免二次 DB 往返。
    dg_ids = [a["target_id"] for a in anchors if a.get("target_graph") == "depgraph"]
    status_map: dict[str, str] = {}
    gate_map: dict[str, str] = {}
    acq_map: dict[str, str] = {}
    if dg_ids:
        dr = DepgraphReader()
        try:
            sg_map = dr.get_status_and_gate_map(dg_ids)
        finally:
            dr.close()
        # 拆成三个 dict：status_map（供 _compute_step_status）+ gate_map（供 ⛔ 行）
        # + acq_map（供 acquisition 标记）
        for tid, entry in sg_map.items():
            status_map[tid] = entry["build_status"]
            gr = entry.get("gate_reason") or ""
            if gr:
                gate_map[tid] = gr
            am = entry.get("acquisition_method") or ""
            if am:
                acq_map[tid] = am

    # enrich anchors：附加 live build_status
    for a in anchors:
        if a.get("target_graph") == "depgraph":
            a["_live_build_status"] = status_map.get(a["target_id"], "<未命中>")

    # enrich steps：附加有效状态 + 候选标记 + gate_reason + acquisition_method
    # （gate_reason/acquisition_method 取 primary depgraph 锚点的，首个非空优先）
    for s in steps:
        sid = s["step_id"]
        al = anchors_by_step.get(sid, [])
        # #ARCH-OE-007~009 治理裁定优先（2026-08-11）：step.design_maturity='deprecated'
        # 直接生效为弃用态（红🟥），覆盖 depgraph 锚点推导——wontfix 裁定是权威的。
        if (s.get("design_maturity") or "").strip() == "deprecated":
            s["_effective_status"] = "deprecated"
            s["_has_candidate"] = _has_candidate_anchor(al)
            s["_gate_reason"] = ""
            s["_acquisition_method"] = ""
            continue
        s["_effective_status"] = _compute_step_status(al, status_map)
        s["_has_candidate"] = _has_candidate_anchor(al)
        # gate_reason：取该环节 primary depgraph 锚点的 gate_reason（首个非空）
        s["_gate_reason"] = ""
        # acquisition_method：取该环节 primary depgraph 锚点的 acquisition_method
        s["_acquisition_method"] = ""
        for a in al:
            if a.get("target_role") == "primary" and a.get("target_graph") == "depgraph":
                gr = gate_map.get(a["target_id"], "")
                if gr:
                    s["_gate_reason"] = gr
                am = acq_map.get(a["target_id"], "")
                if am:
                    s["_acquisition_method"] = am
                break

    # V0.4.0 子环节状态继承：子环节无自身锚点时，继承父环节的状态
    # （子环节是父环节的内部结构，锚点通过父环节间接获得，不应显示 missing/无锚点）
    #
    # 治本（2026-08-03，设计态子环节渲染修复）：子环节显式声明 design_maturity='design'
    # 时，即使无自身锚点也不继承父环节的 production 状态——父环节已建不代表所有子环节
    # 都已实现，部分子环节可能是待施工的设计态（如 BM-RC-04-E 流动性风险监控）。
    # 继承父的 production 会掩盖这些设计态子环节，让用户误以为全部已实现。
    step_by_id = {s["step_id"]: s for s in steps}
    for s in steps:
        pid = s.get("parent_step_id")
        if pid and pid in step_by_id:
            parent = step_by_id[pid]
            if not anchors_by_step.get(s["step_id"]):  # 子环节无自身锚点
                own_maturity = (s.get("design_maturity") or "").strip()
                if own_maturity in ("design", "deprecated"):
                    # 子环节显式声明 design/deprecated——保持，不继承父状态
                    # design：父已建不代表所有子环节已实现（如 BM-RC-04-E 流动性风险监控）
                    # deprecated（#ARCH-OE-009，2026-08-11）：子环节 wontfix 裁定，保持弃用态
                    s["_effective_status"] = own_maturity
                    s["_has_candidate"] = False
                    s["_gate_reason"] = ""
                    s["_acquisition_method"] = ""
                else:
                    # 未声明或声明 production——继承父状态（向后兼容）
                    s["_effective_status"] = parent.get("_effective_status", "design")
                    s["_has_candidate"] = parent.get("_has_candidate", False)
                    s["_gate_reason"] = parent.get("_gate_reason", "")
                    s["_acquisition_method"] = parent.get("_acquisition_method", "")

    return steps, edges, anchors_by_step


# ---------------------------------------------------------------------------
# Mermaid 生成
# ---------------------------------------------------------------------------


def _sanitize(text: str) -> str:
    """转义 Mermaid 标签中的特殊字符（模板 §4.9）。

    治本（2026-08-03，渲染失败修复）：``&`` ``<`` ``>`` 必须转义为 XML 实体——
    Mermaid 渲染为 SVG（XML-based），未转义的 ``&`` 导致 XML 解析失败（如
    ``Data Ingestion & Preprocessing``）；未转义的 ``<`` 被误判为 HTML 标签起始
    （如 ``期<40%直接拦截``）。``<br/>`` 折行标签需保护——先替换为占位符，
    转义后恢复。
    """
    if not text:
        return ""
    # 保护 <br/> 折行标签（转义 < > 前先暂存，转义后恢复）
    text = text.replace("<br/>", "\x00BR\x00")
    # XML 实体转义（& 必须先转，否则后续 &lt; &gt; 中的 & 会被二次转义）
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    # 恢复 <br/> 折行标签
    text = text.replace("\x00BR\x00", "<br/>")
    # Mermaid 语法字符转义
    # [ ] -> 全角【】会改变语义，用全角（）更安全（节点标签和边标签中都不会冲突）
    # ( ) -> 边标签 |...| 中的半角()被 Mermaid 误解析为节点形状（如 node(text)），
    #        导致 Parse error（2026-08-03 渲染失败修复，如 |T指令(底仓不变)→仓位裁决|）
    return (
        text.replace("[", "（")
        .replace("]", "）")
        .replace("(", "（")
        .replace(")", "）")
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

    # 拆分中英文名（name_bi 格式："中文名 / English" 或单名）
    if " / " in name_bi:
        name_zh, name_en = name_bi.split(" / ", 1)
    else:
        name_zh, name_en = name_bi, ""

    parts: list[str] = []

    # ⛔ 受限原因（放最前面，仅 design 态 + gate_reason 非空）
    gate = (step.get("_gate_reason") or "").strip()
    if status == "design" and gate:
        parts.append(f"⛔ {gate}")

    # 环节标识（step_id + 中文名，用【】包裹放最前面）
    # #ARCH-OE-055（2026-08-12）：弃用环节标签加【已弃用】显眼前缀，防 AI 误读为活设计而复建
    if status == "deprecated":
        parts.append(f"【已弃用】【{sid} {name_zh}】")
    else:
        parts.append(f"【{sid} {name_zh}】")

    # 大白话
    parts.append(plain if plain else "—")

    # 成熟度
    parts.append(maturity)

    # acquisition 徽标（2026-08-07：放成熟度行下方，节点卡内一目了然"怎么搞到手"）。
    # _sanitize 会把半角 [] 转成全角（），emoji 保留——显示为（🔴自建）/（🟢开源）等。
    # 完整 acquisition_source 在详情区"获取方式"行 + depgraph DB，此处仅展示层标记。
    am = step.get("_acquisition_method") or ""
    if am:
        badge = _ACQUISITION_BADGE.get(am, "")
        if badge:
            parts.append(badge)

    # 标记（⚠无锚点 / 🟡候选承载 / 🟧设计态子环节）
    marks: list[str] = []
    if status == "missing":
        marks.append("⚠无锚点")
    if step.get("_has_candidate"):
        marks.append("🟡候选承载")
    # 🟧设计态子环节标记（治本 2026-08-03）：子环节（depth>=1）处于设计态时加特殊
    # 标记，与父环节的 production 状态视觉区分——父已建但此子环节待施工，易被忽略
    if status == "design" and (step.get("depth") or 0) >= 1:
        marks.append("🟧设计态子环节")
    if marks:
        parts.append("、".join(marks))

    # 英文名（用【】包裹放最后，有英文名时才加）
    if name_en:
        parts.append(f"【{name_en}】")

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


def _build_children_map(steps: list[dict]) -> dict[str, list[dict]]:
    """构建 parent_step_id → 子环节列表 映射（BM-INV-006 父子嵌套渲染用）。

    只有 parent_step_id 非空且指向的父环节也在 steps 集合内时才建立关系
    （悬空父引用由 align_battle_map.py BM-INV-006 报告，生成器兜底跳过）。
    返回的子环节列表按 sort_order 排序。
    """
    step_ids = {s["step_id"] for s in steps}
    children: dict[str, list[dict]] = {}
    for s in steps:
        pid = s.get("parent_step_id")
        if pid and pid in step_ids:
            children.setdefault(pid, []).append(s)
    for pid in children:
        children[pid].sort(key=lambda x: x.get("sort_order", 0))
    return children


def _emit_nodes_with_subgraphs(
    steps: list[dict],
    children_map: dict[str, list[dict]],
    parent_id: str | None = None,
    indent: int = 4,
) -> list[str]:
    """递归输出节点定义，有子环节的父环节用 subgraph 包裹（BM-INV-006）。

    结构：
      根环节（无 parent）→ 独立节点 or subgraph（若有子）
      子环节（有 parent）→ 在父的 subgraph 内
      孙环节（depth=2）→ 嵌套 subgraph

    subgraph 标题用父环节名，父节点本身也在 subgraph 内作为第一个节点
    （保留完整四要素信息），子环节跟在后面。
    """
    lines: list[str] = []
    pad = " " * indent
    if parent_id is None:
        nodes = [s for s in steps if not s.get("parent_step_id")]
    else:
        nodes = children_map.get(parent_id, [])
    nodes = sorted(nodes, key=lambda x: x.get("sort_order", 0))

    for s in nodes:
        sid = s["step_id"]
        nid = _mermaid_node_id(sid)
        label = _node_label(s)
        children = children_map.get(sid)
        if children:
            sg_title = _sanitize(s.get("step_name", sid))
            lines.append(f'{pad}subgraph sg_{nid} ["{sg_title}"]')
            lines.append(f'{pad}    {nid}["{label}"]')
            # 子节点定义（递归处理孙环节）
            lines.extend(_emit_nodes_with_subgraphs(steps, children_map, sid, indent + 4))
            # 父→子嵌套边（虚线表示组成关系，与 data_flow 实线区分）
            child_pad = " " * (indent + 4)
            for child in children:
                child_nid = _mermaid_node_id(child["step_id"])
                lines.append(f"{child_pad}{nid} -.->|嵌套| {child_nid}")
            lines.append(f"{pad}end")
        else:
            lines.append(f'{pad}{nid}["{label}"]')
    return lines


def _build_mermaid(
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
    title: str,
) -> str:
    """构建一个 Mermaid 流程图块（模板合规：主题头 + TD + 四要素节点 + 拓扑分层 + 状态边 + class）。

    BM-INV-006 父子嵌套：有子环节的父环节用 subgraph 包裹，子环节在 subgraph 内渲染，
    支持嵌套（孙环节在子环节的 subgraph 内）。无 parent_step_id 的环节平铺为根节点。
    """
    lines = ["```mermaid", _MERMAID_THEME, f"%% {title}", "flowchart TD"]
    step_ids = {s["step_id"] for s in steps}
    status_by_id = {s["step_id"]: s.get("_effective_status") or "design" for s in steps}

    # 节点定义（BM-INV-006：父子嵌套用 subgraph，无 parent 的为根节点）
    children_map = _build_children_map(steps)
    lines.extend(_emit_nodes_with_subgraphs(steps, children_map))

    # 拓扑分层 ~~~ 同层串联（模板 §4.6 强制竖排）
    layer_map = _topological_layers(steps, edges)
    lines.extend(_emit_layer_chains(steps, layer_map))

    # 边定义（只画两端都在本图 step 集内的边；箭头按端点状态，标签含 edge_type）
    # #ARCH-OE-054（2026-08-12）：两端含 deprecated 环节的流转边不渲染——弃用环节不在流转路径上
    for e in edges:
        if e["from_step_id"] in step_ids and e["to_step_id"] in step_ids:
            if "deprecated" in (
                status_by_id.get(e["from_step_id"]),
                status_by_id.get(e["to_step_id"]),
            ):
                continue
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
    """构建分页 Mermaid（每页 PAGE_SIZE 个节点，防 >100 节点渲染失败）。

    家族式分页（治本 2026-08-03，depth=2 孙环节跨页丢失修复）：
    旧逻辑按扁平 sort_order 切片 steps[i*PAGE_SIZE:(i+1)*PAGE_SIZE]，会切断父子树——
    跨页的子/孙环节因父环节不在同页，_build_children_map 的 ``pid in step_ids``
    判定为 False 无法建立父子关系，且有 parent_step_id 不被当根节点 → 完全丢失不渲染。

    修复：遍历排序后的环节，遇到未分配的环节时连同其所有后代（子+孙）整体收集为一个
    "家族"，保证家族不拆分到不同页。当前页剩余空间放不下整个家族时换新页。
    极端情况（单家族 > PAGE_SIZE）该页超限但完整，优于丢失节点。
    """
    if len(steps) <= PAGE_SIZE:
        return _build_mermaid(steps, edges, anchors_by_step, title)
    children_map = _build_children_map(steps)
    step_by_id = {s["step_id"]: s for s in steps}
    sorted_steps = sorted(steps, key=lambda x: x.get("sort_order", 0))

    def _collect_family(step_id: str, acc: list[dict]) -> None:
        """_collect_family implementation."""
        acc.append(step_by_id[step_id])
        for child in children_map.get(step_id, []):
            _collect_family(child["step_id"], acc)

    assigned: set[str] = set()
    pages: list[list[dict]] = []
    current: list[dict] = []
    for s in sorted_steps:
        sid = s["step_id"]
        if sid in assigned:
            continue  # 已被某家族收集
        family: list[dict] = []
        _collect_family(sid, family)
        # 当前页非空且放不下整个家族 → 换页（保证家族不拆分）
        if current and len(current) + len(family) > PAGE_SIZE:
            pages.append(current)
            current = []
        current.extend(family)
        for f in family:
            assigned.add(f["step_id"])
    if current:
        pages.append(current)

    parts: list[str] = []
    total_pages = len(pages)
    for i, page in enumerate(pages):
        parts.append(_build_mermaid(page, edges, anchors_by_step, f"{title}（第 {i + 1}/{total_pages} 页）"))
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# 详情表生成（6 件套）
# ---------------------------------------------------------------------------


def _format_indicators_table(step: dict) -> str:
    """把 indicators JSONB 6 件套格式化为 Markdown 表。

    防御性渲染（治本 2026-08-03，BM-MT-01-A/B/05-A params 为字符串致全量生成崩溃）：
    indicators 各字段可能是 dict / list / str / None——历史数据写入不规范时，
    逐字段降级为纯文本展示，禁止因单环节格式异常崩溃全量生成（259 环节受牵连）。
    """
    ind = step.get("indicators") or {}
    if not isinstance(ind, dict):
        # indicators 整体非 dict（极端情况）——纯文本兜底，不崩溃
        return f"| 要素 | 内容 |\n|---|---|\n| indicators | {str(ind)[:200]} |"
    rows: list[str] = []

    def _kv(items):
        """_kv implementation."""
        if not items:
            return "—"
        if isinstance(items, list):
            return "<br>".join(
                f"{it.get('item', it) if isinstance(it, dict) else it}"
                + (f"（来自 {it['source']}）" if isinstance(it, dict) and it.get("source") else "")
                for it in items
            )
        if isinstance(items, dict):
            return "<br>".join(f"{k}: {v}" for k, v in items.items())
        return str(items)

    # ① 触发条件（防御：trigger 可能是 str 而非 dict，降级为纯文本展示）
    trig = ind.get("trigger")
    if isinstance(trig, str) and trig.strip():
        # 字符串格式——原样展示（批量补填场景）
        rows.append(f"| ① 触发条件 | {trig} |")
    elif isinstance(trig, dict):
        rows.append(f"| ① 触发条件 | {trig.get('condition', '—')} |")
        if trig.get("threshold"):
            rows[-1] = rows[-1].rstrip(" |") + f" 阈值: {trig['threshold']} |"
    else:
        rows.append("| ① 触发条件 | — |")
    # ② 消费数据/因子（防御：consumes 可能是 str 而非 list[dict]）
    consumes = ind.get("consumes")
    if isinstance(consumes, str) and consumes.strip():
        rows.append(f"| ② 消费数据/因子 | {consumes} |")
    else:
        rows.append(f"| ② 消费数据/因子 | {_kv(consumes)} |")
    # ③ 参数（防御：params 可能是 str 而非 list[dict]，降级为纯文本展示）
    params = ind.get("params")
    if isinstance(params, str) and params.strip():
        # 历史脏数据：params 写成了逗号/顿号分隔的纯文本——原样展示
        rows.append(f"| ③ 参数 | {params} |")
    elif isinstance(params, list) and params:
        p_lines = []
        for p in params:
            if isinstance(p, dict):
                p_lines.append(
                    f"{p.get('name', '?')}={p.get('default', '?')}（范围 {p.get('range', '—')}，"
                    f"代码当前: {p.get('current_code_value', '—')}，状态: {p.get('status', '—')}）"
                )
            else:
                # 列表元素非 dict（如纯字符串参数名）——原样展示
                p_lines.append(str(p))
        rows.append(f"| ③ 参数 | {'<br>'.join(p_lines)} |")
    else:
        rows.append("| ③ 参数 | — |")
    # ④ 数据流（防御：data_flow 可能是 str 而非 dict）
    df = ind.get("data_flow")
    if isinstance(df, str) and df.strip():
        rows.append(f"| ④ 数据流 | {df} |")
    elif isinstance(df, dict):
        rows.append(
            f"| ④ 数据流 | 输入: {df.get('input', '—')} → 处理: {df.get('process', '—')} "
            f"→ 输出: {df.get('output', '—')} → 下游: {df.get('downstream', '—')} |"
        )
    else:
        rows.append("| ④ 数据流 | — |")
    # ⑤ 代码映射（防御：code_mapping 可能是 str 而非 dict）
    cm = ind.get("code_mapping")
    if isinstance(cm, str) and cm.strip():
        rows.append(f"| ⑤ 代码映射 | {cm} |")
    elif isinstance(cm, dict):
        rows.append(f"| ⑤ 代码映射 | {cm.get('module_id', '—')} / {cm.get('source_ref', '—')} |")
    else:
        rows.append("| ⑤ 代码映射 | — |")
    # ⑥ 降级/中止（防御：degradation 可能是 str 而非 dict）
    deg = ind.get("degradation")
    if isinstance(deg, str) and deg.strip():
        rows.append(f"| ⑥ 降级/中止 | {deg} |")
    elif isinstance(deg, dict):
        deg_text = deg.get("condition", "—")
        if deg.get("action"):
            deg_text += f" → {deg['action']}"
        rows.append(f"| ⑥ 降级/中止 | {deg_text} |")
    else:
        rows.append("| ⑥ 降级/中止 | — |")

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
    # acquisition 小标记（2026-08-05）：标题下方加 [🔴自建]/[🟢开源]/[🟡借鉴]/[⬜弃用] 标记，
    # 不展开完整获取方式（避免污染展示层）。完整信息（含 acquisition_source）在 depgraph DB。
    am = step.get("_acquisition_method") or ""
    if am:
        badge = _ACQUISITION_BADGE.get(am, "")
        if badge:
            parts += [f"> **获取方式**：{badge}", ""]
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
        # 深链接：锚点模块的算法详情见跨域算法纵览（08_algorithm_overview，按作战环节拆分）
        # 仅对 depgraph 锚点的 MOD-xxx 模块生成链接（CAND-xxx/其他不在纵览中）
        # 环节文件路径由 step 的 flow_stage 决定（零漂移：映射从 FLOW_STAGES 派生）
        flow_stage = step.get("flow_stage", "")
        stage_file = _FLOW_STAGE_TO_ALGO_FILE.get(flow_stage, "system_foundation.md")
        algo_link_base = f"../../08_algorithm_overview/{stage_file}"
        algo_index_link = "../../08_algorithm_overview/index.md"
        depgraph_mods = [
            a for a in anchors
            if a.get("target_graph") == "depgraph"
            and (a.get("target_id") or "").startswith("MOD-")
        ]
        if depgraph_mods:
            mod_links = [
                f"[{a['target_id']}]({algo_link_base}#{a['target_id'].lower()})"
                for a in depgraph_mods
            ]
            parts.append(
                f"> 🔗 **算法详情**：见[算法全景图]({algo_index_link})，"
                f"本环节锚点模块：{' / '.join(mod_links)}"
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
        f"date: {idempotent_date(_THIS_FILE)}\n"
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
        f"> **[可缩放 HTML 版 / Zoomable HTML]({url})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式"
    )


def _legend_blockquote() -> str:
    """图例说明 blockquote（模板 §3.1，适配 battle map 五态 + 双箭头）。"""
    return (
        "> **图例说明 / Legend**：\n"
        "> - 🟦 **蓝色实线 = 运营态环节**（production，锚点模块已建）\n"
        "> - 🟧 **橙色虚线 = 设计态环节**（design，锚点模块待施工）\n"
        "> - 🟧**设计态子环节** = 父环节已建但此子环节待施工（特殊标记，易被忽略）\n"
        "> - 🟥 **红色 = 弃用态**（deprecated）\n"
        "> - ⬜ **灰色 = 缺失态**（missing，环节无锚点，BM-INV-001 违例）\n"
        "> - 🟨 **黄色虚线 = 候选态**（candidate，承载模块在候选池）\n"
        "> - **实线箭头 ``-->`` = 运营态流转**（两端均 production）\n"
        "> - **虚线箭头 ``-.->`` = 非运营态流转**（含设计/候选/混合）"
    )


def _view_subset(steps: list[dict], edges: list[dict], statuses: set[str]) -> tuple[list[dict], list[dict]]:
    """按展示态筛选视图子集（模板 §3.2：运营态=production，设计态=design）。

    返回 (筛选后 steps, 两端均在筛选集内且两端状态均在 statuses 内的 edges)。
    candidate/deprecated/missing 不进运营/设计视图，仅在全景图展示。
    """
    sel = [s for s in steps if s.get("_effective_status") in statuses]
    sel_ids = {s["step_id"] for s in sel}
    sel_edges = [e for e in edges if e["from_step_id"] in sel_ids and e["to_step_id"] in sel_ids]
    return sel, sel_edges


def _generate_panorama_md(
    steps: list[dict],
    edges: list[dict],
    anchors_by_step: dict[str, list[dict]],
) -> str:
    """总指挥图 MD（三视图 + 分阶段导航，模板 §3.1/§3.2 铁律）。

    V1.5（2026-08-03）：移除"全环节详情（6 件套）"——总图聚焦大局全貌，
    各环节 6 件套详情由 12 个分阶段文档承载，避免 panorama.md 膨胀且信息重复。
    """
    no_anchor_count = sum(1 for s in steps if s.get("_effective_status") == "missing")
    # 锚点总数（双向对齐枢纽显化，BM-INV-005）：battle_map_anchors 是 step↔module 唯一双向查找真源
    anchor_count = sum(len(v) for v in anchors_by_step.values())
    # 五态分布统计（Gap1）
    state_counts: dict[str, int] = {}
    for s in steps:
        st = s.get("_effective_status", "design")
        state_counts[st] = state_counts.get(st, 0) + 1
    dist = " ｜ ".join(
        f"{_STATE_LABEL.get(st, st)}={cnt}" for st, cnt in sorted(state_counts.items(), key=lambda x: -x[1])
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
        "> 🔑 **双向对齐枢纽**：`battle_map_anchors` 表是作战环节 ↔ 全景图模块/候选池的**唯一双向查找真源**（方向A: step→modules / 方向B: module→step 均从此表查），是连接作战地图与 depgraph/dataflowgraph/decisiongraph 三大全景图的桥梁。禁止在其他全景图表反向加 battle_map 字段（BM-INV-005）。",
        "> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编（改环节→改 DB/YAML 真源→重跑生成器）。",
        "",
        "## 文档基本信息 / Document Overview",
        "",
        "| 字段 | 值 | Field | Value |",
        "|------|------|-------|-------|",
        f"| 环节总数 | {len(steps)} | Steps | {len(steps)} |",
        f"| 流转边 | {len(edges)} | Edges | {len(edges)} |",
        f"| 锚点总数（双向对齐枢纽） | {anchor_count} | Anchors (Bidirectional Hub) | {anchor_count} |",
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
    parts.append("- [横切视图（§13漏斗 / §14盘中事件 / §16冲突矩阵）](battle_map_12_cross_cutting.md)")
    parts.append("")
    # V1.5：全景图不再展示"全环节详情（6 件套）"——总图看大局全貌，详情在 12 个分阶段文档里
    # 重复输出会让 panorama.md 膨胀到几百 KB 且无信息增量。
    # 各环节 6 件套（触发/消费/参数/数据流/代码映射/降级）见上方对应分阶段文档。
    parts.append(
        "> **环节详情**：各环节的 6 件套（触发/消费/参数/数据流/代码映射/降级）+ 锚点 + 有效状态，见上方对应分阶段文档。总图聚焦大局全貌，不重复详情。"
    )
    parts.append("")
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
    # 边：两端都在本阶段（计数口径修复 2026-08-12，#ARCH-OE-054 批次——头部声明数必须与
    # 图内实际渲染边数一致；跨阶段边在阶段图中本就不渲染（_build_mermaid 只画两端同页），
    # 用 OR 计入会造成"声明 N 条 vs 图 M 条"口径打架）
    stage_edges = [e for e in edges if e["from_step_id"] in stage_step_ids and e["to_step_id"] in stage_step_ids]
    # 本阶段锚点数（双向对齐枢纽显化，BM-INV-005）
    stage_anchor_count = sum(len(anchors_by_step.get(s["step_id"], [])) for s in stage_steps)
    # 五态分布统计
    state_counts: dict[str, int] = {}
    for s in stage_steps:
        st = s.get("_effective_status", "design")
        state_counts[st] = state_counts.get(st, 0) + 1
    dist = (
        " ｜ ".join(
            f"{_STATE_LABEL.get(st, st)}={cnt}" for st, cnt in sorted(state_counts.items(), key=lambda x: -x[1])
        )
        or "—"
    )
    stem = f"battle_map_{stage_num}_{stage_id}"

    parts: list[str] = [
        f"# 作战地图·{stage_name}阶段",
        "",
        _html_link_line(stem),
        "",
        f"> battle_map §{stage_id} 阶段，{len(stage_steps)} 环节（{stage_anchor_count} 锚点）。",
        "> 🔑 锚点表 `battle_map_anchors` 是环节↔模块**双向对齐枢纽**（step↔module 唯一查找真源），详见各环节「锚点」小节。",
        "> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。",
        "",
        "## 文档基本信息 / Document Overview",
        "",
        "| 字段 | 值 | Field | Value |",
        "|------|------|-------|-------|",
        f"| 阶段 | {stage_name}（{stage_id}） | Stage | {stage_name} |",
        f"| 环节数 | {len(stage_steps)} | Steps | {len(stage_steps)} |",
        f"| 锚点数（双向对齐） | {stage_anchor_count} | Anchors (Bidirectional) | {stage_anchor_count} |",
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
    # step_id → 所在分阶段文档（BM-SEL-* → 05_stock_selection，依此类推）
    # 2026-08-03 全生命周期扩展：11 阶段映射（_STEP_PREFIX_TO_STAGE_FILE），禁止手编回退旧编号
    links: list[str] = []
    for sid in related_steps:
        prefix = "-".join(sid.split("-")[:2])
        doc = _STEP_PREFIX_TO_STAGE_FILE.get(prefix)
        if doc:
            links.append(f"[{sid}](battle_map_{doc}.md)")
        else:
            links.append(sid)
    return "、".join(links)


def _format_funnel_md(item: dict) -> str:
    """渲染 §13 筛选漏斗模型为 Markdown（6层漏斗表 + 机制说明）。"""
    name_bi = item.get("name_zh", "") + (f" / {item['name_en']}" if item.get("name_en") else "")
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
    name_bi = item.get("name_zh", "") + (f" / {item['name_en']}" if item.get("name_en") else "")
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
    name_bi = item.get("name_zh", "") + (f" / {item['name_en']}" if item.get("name_en") else "")
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
            parts.append(f"| {h.get('rank', '?')} | {h.get('holder', '—')} | {note} |")
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
    name_bi = item.get("name_zh", "") + (f" / {item['name_en']}" if item.get("name_en") else "")
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
            parts.append(f"| {ph.get('name_zh', '—')} | {ph.get('time_range', '—')} | {act_text} |")
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
    name_bi = item.get("name_zh", "") + (f" / {item['name_en']}" if item.get("name_en") else "")
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
    name_bi = item.get("name_zh", "") + (f" / {item['name_en']}" if item.get("name_en") else "")
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
            parts.append(f"| {t.get('trigger', '—')} | {t.get('failed_layer', '—')} | {t.get('fallback', '—')} |")
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
    # 信号生命周期：lifecycle_stages 表（来源 D-SIGNAL 域，2026-08-03）
    lifecycle_stages = item.get("lifecycle_stages") or []
    if lifecycle_stages:
        parts += [
            "### 生命周期阶段",
            "",
            "| 阶段 | 名称 | 能力 | 说明 |",
            "|---|---|---|---|",
        ]
        for s in lifecycle_stages:
            parts.append(
                f"| {s.get('stage', '—')} | {s.get('name_zh', '—')} "
                f"| {s.get('capability', '—')} | {s.get('note', '—')} |"
            )
        parts.append("")
    # 信号生命周期：degradation_levels 表
    degradation_levels = item.get("degradation_levels") or []
    if degradation_levels:
        parts += [
            "### 降级级别",
            "",
            "| 级别 | 触发条件 | 动作 | 下游影响 |",
            "|---|---|---|---|",
        ]
        for d in degradation_levels:
            parts.append(
                f"| {d.get('level', '—')} | {d.get('trigger', '—')} "
                f"| {d.get('action', '—')} | {d.get('downstream', '—')} |"
            )
        parts.append("")
    # 因子治理：governance_stages 表（来源 D-FACTOR 域，2026-08-03）
    governance_stages = item.get("governance_stages") or []
    if governance_stages:
        parts += [
            "### 治理阶段",
            "",
            "| 阶段 | 名称 | 能力 | 说明 |",
            "|---|---|---|---|",
        ]
        for g in governance_stages:
            parts.append(
                f"| {g.get('stage', '—')} | {g.get('name_zh', '—')} "
                f"| {g.get('capability', '—')} | {g.get('note', '—')} |"
            )
        parts.append("")
    # 因子治理：pool_management 表
    pool_mgmt = item.get("pool_management") or {}
    if pool_mgmt:
        cap = pool_mgmt.get("capacity") or {}
        if cap:
            parts += [
                "### 因子池容量",
                "",
                "| 参数 | 值 |",
                "|---|---|",
                f"| 运行上限 N_max | {cap.get('n_max', '—')} |",
                f"| 活跃池上限 | {cap.get('active_pool_limit', '—')} |",
                f"| 休眠上限 | {cap.get('dormant_limit', '—')} |",
                f"| 设计容量 | {cap.get('design_capacity', '—')} |",
                "",
            ]
        mechs = pool_mgmt.get("mechanisms") or []
        if mechs:
            parts += [
                "### 因子池管理机制",
                "",
                "| 机制 | 名称 | 触发条件 | 说明 |",
                "|---|---|---|---|",
            ]
            for m in mechs:
                parts.append(
                    f"| {m.get('mechanism', '—')} | {m.get('name_zh', '—')} "
                    f"| {m.get('trigger', '—')} | {m.get('note', '—')} |"
                )
            parts.append("")
    # 硬边界约束体系：boundary_categories 表（来源 01-跨域交叉点，2026-08-03）
    boundary_cats = item.get("boundary_categories") or []
    if boundary_cats:
        parts += [
            "### 硬边界分类（4类 56条约束）",
            "",
            "| 类别 | 名称 | 前缀 | 条数 | 范围 | 关键约束 |",
            "|---|---|---|---|---|---|",
        ]
        for bc in boundary_cats:
            parts.append(
                f"| {bc.get('category', '—')} | {bc.get('name_zh', '—')} "
                f"| {bc.get('code_prefix', '—')} | {bc.get('count', '—')} "
                f"| {bc.get('scope', '—')} | {bc.get('key_constraints', '—')} |"
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
    # 以下 2 项来源 D-SIGNAL/D-FACTOR 域依赖图文档（选股流程丰富，2026-08-03）
    "signal_lifecycle": _format_generic_cross_cutting_md,
    "factor_governance": _format_generic_cross_cutting_md,
    # 以下 1 项来源 01-跨域交叉点与因果链.md（硬边界约束体系，2026-08-03）
    "hard_boundary_constraints": _format_generic_cross_cutting_md,
    # 以下 1 项来源交易决策架构 v8.1 横切层（模型量化，2026-08-05）
    "model_quantization": _format_generic_cross_cutting_md,
    # 以下 2 项来源交易决策架构 v7.0/v8.2（因子直通层/投票优先多Agent，§5.4.3 横切归轨，2026-08-05）
    "factor_direct_fusion": _format_generic_cross_cutting_md,
    "voting_first_multi_agent": _format_generic_cross_cutting_md,
    # 以下 1 项来源交易决策架构 v8.0 可建设项#16/#17（事件溯源/配置中心，2026-08-05）
    "event_sourcing_config_center": _format_generic_cross_cutting_md,
    # 以下 1 项来源学习系统架构 §1 对标表（外部对标清单，2026-08-05 Owner 拍板）
    "benchmark_mapping": _format_generic_cross_cutting_md,
}


def _generate_cross_cutting_mermaid(items: list[dict]) -> str:
    """横切视图总览 Mermaid 图（9 类横切机制总览，模板合规）。

    每个横切类别一个节点，含 §章节引用 + 中英双语名 + 大白话简介。
    无 depgraph 锚点（横切机制是架构概念非代码模块），统一标 design 态。
    """
    lines = ["```mermaid", _MERMAID_THEME, "%% 横切视图总览", "flowchart TD"]
    nids: list[str] = []
    for i, item in enumerate(items, 1):
        cat = item.get("category", f"cat_{i}")
        name_zh = item.get("name_zh", cat)
        name_en = item.get("name_en", "")
        sketch = item.get("sketch_ref", "")
        plain = (item.get("plain_zh") or "").strip()
        nid = f"CC_{i:02d}"
        nids.append(nid)
        name_bi = f"{name_zh} / {name_en}" if name_en else name_zh
        parts = [f"(设计态 / design) {sketch} {name_bi}".strip()]
        if plain:
            parts.append(plain)
        parts.append("横切机制 / cross-cutting")
        label = "<br/>".join(_wrap_label_text(p) for p in parts if p)
        label = _sanitize(label)
        lines.append(f'    {nid}["{label}"]')
    # 同层 ~~~ 串联（竖排对齐）
    if len(nids) >= 2:
        lines.append("    " + " ~~~ ".join(nids))
    lines.append(_CLASSDEFS)
    if nids:
        lines.append(f"    class {','.join(nids)} design")
    lines.append("```")
    return "\n".join(lines)


def _generate_cross_cutting_md() -> str:
    """横切视图 MD（§13漏斗 + §14盘中事件 + §16冲突矩阵 + 4 退役迁移段，Gap3）。

    横切内容来自翻译真源 battle_map_cross_cutting 段（规则数据，TRAE-062），
    不属任何单一阶段，贯穿选股→买入→卖出→仓位→执行→对账全流程。

    2026-08-02 退役迁移：trading_flow_narrative.yaml §cross_cutting 的 4 个系统级横切段
    （four_modes / emergency_degradation / four_tracks / shared_signal_injection）
    迁入本段，由 _format_generic_cross_cutting_md 渲染。

    2026-08-03 模板对齐：补 HTML 链接 + 基本信息表 + 图例 + 横切总览 Mermaid 图，
    使横切视图文档与其他 battle_map 文档结构一致（模板 §9.1 MD+HTML 双产物）。
    """
    items = get_cross_cutting_all()
    parts = [
        "# 交易决策作战地图（横切视图）",
        "",
    ]
    if not items:
        parts.append("⚠ 未加载到横切视图数据（YAML battle_map_cross_cutting 段缺失或解析失败）。")
        return "\n".join(parts)

    parts.append(_html_link_line("battle_map_12_cross_cutting"))
    parts.append("")
    parts.extend(
        [
            "> 横切贯穿全流程的全局机制：§13 筛选漏斗 / §14 盘中实时事件处理 / §16 能力冲突矩阵与仲裁规则",
            ">           + 4 系统级横切（四模式开关 / 应急保命降级 / 四轨并行 / 共享信号注入，迁移自 trading_flow_narrative.yaml）",
            ">           + 3 域来源横切（信号生命周期治理 / 因子治理引擎 / 硬边界约束体系，来源 D-SIGNAL/D-FACTOR/跨域交叉点）。",
            "> 真源：`module_translation_registry.yaml` §battle_map_cross_cutting 段（规则数据，TRAE-062）。",
            "> 本文档由 `generate_battle_map_diagram.py` 自动生成，禁止手编。",
            "",
            "## 文档基本信息 / Document Overview",
            "",
            "| 字段 | 值 | Field | Value |",
            "|------|------|-------|-------|",
            f"| 横切类别数 | {len(items)} | Categories | {len(items)} |",
            "| 涵盖章节 | §13 / §14 / §16 / §15 / §1.7 + 4 系统级 + 3 域来源 | Sections | §13 / §14 / §16 / §15 / §1.7 + 4 sys + 3 domain |",
            "| 真源 | module_translation_registry.yaml | Source | YAML registry |",
            "",
            _legend_blockquote(),
            "",
            "## 横切视图总览 / Cross-Cutting Overview",
            "",
            f"> 展示全部 {len(items)} 个横切机制，颜色区分五态。",
            "",
            _generate_cross_cutting_mermaid(items),
            "",
        ]
    )
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


def regenerate(output_dir: Path | None = None) -> dict:
    """重生成 battle_map 全部 MD + HTML（可调用接口，供 reconcile_generators 编排器调用）。

    不 print，返回结果 dict。main() 包装此函数加 print。
    apply_battle_map.py 写完 DB 后经 reconcile_generators.reconcile() 调用此函数；
    boot_hooks 启动时经 reconcile_stale() mtime 对比后调用此函数。

    Args:
        output_dir: 输出目录，None 时用默认 battle_map 目录

    Returns:
        {"status": "ok"|"failed", "generator": "battle_map",
         "outputs": [path, ...], "steps": N, "edges": N, "anchors": N}
    """
    try:
        if output_dir is None:
            output_dir = (
                REPO_ROOT / "docs" / "02_enterprise_architecture" / "07_trading_decision_architecture" / "battle_map"
            )
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        steps, edges, anchors_by_step = _load_all()
        outputs: list[str] = []

        # 总指挥图
        panorama_md = _generate_panorama_md(steps, edges, anchors_by_step)
        panorama_md = f"{_make_frontmatter()}\n{panorama_md}"
        panorama_path = output_dir / "battle_map_panorama.md"
        panorama_path.write_text(panorama_md, encoding="utf-8")
        outputs.append(str(panorama_path))
        html = emit_zoomable_html(panorama_path, panorama_md)
        if html:
            outputs.append(str(html))

        # 6 分阶段图
        for stage_id, stage_name, num in FLOW_STAGES:
            stage_md = _generate_stage_md(stage_id, stage_name, num, steps, edges, anchors_by_step)
            stage_md = f"{_make_frontmatter()}\n{stage_md}"
            stage_path = output_dir / f"battle_map_{num}_{stage_id}.md"
            stage_path.write_text(stage_md, encoding="utf-8")
            outputs.append(str(stage_path))
            html = emit_zoomable_html(stage_path, stage_md)
            if html:
                outputs.append(str(html))

        # 横切视图（Gap3：§13漏斗 / §14盘中事件 / §16冲突矩阵）
        cross_md = _generate_cross_cutting_md()
        cross_md = f"{_make_frontmatter()}\n{cross_md}"
        cross_path = output_dir / "battle_map_12_cross_cutting.md"
        cross_path.write_text(cross_md, encoding="utf-8")
        outputs.append(str(cross_path))
        html = emit_zoomable_html(cross_path, cross_md)
        if html:
            outputs.append(str(html))

        return {
            "status": "ok",
            "generator": "battle_map",
            "outputs": outputs,
            "steps": len(steps),
            "edges": len(edges),
            "anchors": sum(len(v) for v in anchors_by_step.values()),
        }
    except Exception as e:  # noqa: BLE001 - 顶层兜底：生成器不可崩溃，降级返回错误 dict
        import traceback as _tb

        _tb.print_exc()
        return {
            "status": "failed",
            "generator": "battle_map",
            "error": f"{type(e).__name__}: {e}",
        }


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="生成交易决策作战地图可视化")
    parser.add_argument(
        "--output-dir",
        default=str(
            REPO_ROOT / "docs" / "02_enterprise_architecture" / "07_trading_decision_architecture" / "battle_map"
        ),
        help="输出目录",
    )
    args = parser.parse_args()

    print("加载 battle_map 三表 + 翻译真源...")
    result = regenerate(Path(args.output_dir))
    if result["status"] == "ok":
        print(f"  steps={result['steps']} edges={result['edges']} anchors={result['anchors']}")
        print(f"\n完成。输出 {len(result['outputs'])} 文件。输出目录: {args.output_dir}")
        return 0
    else:
        print(f"ERROR: {result.get('error')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
