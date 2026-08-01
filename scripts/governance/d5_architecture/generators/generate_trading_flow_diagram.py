# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §trading-flow-panorama
# [MODULE] scripts.governance.d5_architecture.generators.generate_trading_flow_diagram
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.decision_graph_reader (DecisionGraphReader); architecture_model/domain/decision_graph_model.yaml + trading_flow_narrative.yaml (叙事真源)
# [CONSUMERS] 人工查看07_trading_decision_architecture/;CI自动触发(GATE-ARCH-DIAGRAM reconciler post-commit)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读decisiongraph+YAML;输出到07_trading_decision_architecture/;序号硬编码稳定
# [MODIFY-GUARD] 修改需通过TRAE任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] decisiongraph不存在→exit 1;narrative.yaml不存在→exit 2
# [TESTS] (待补)
# [TTL] permanent
"""G-trading-flow: 从 decisiongraph + 叙事YAML + 候选库 生成交易决策架构视图(.md + .html)

功能：
  - 从 decision_graph_model.yaml 读 flow_stages 定义（6阶段）
  - 从 trading_flow_narrative.yaml 读叙事（大白话/ASCII框图/ai_directive/sub_flows）
  - 从 decisiongraph (PostgreSQL) 按 flow_stage 读节点 + 边（含 design_maturity 区分主图/附录）
  - 从 candidate_module_registry.yaml 读候选模块（附录2，按 target_track 归类到阶段）
  - 生成 Mermaid 可视化（总指挥图 + 6 分阶段图），联动可缩放 HTML
  - 生成 9 个 MD + 7 个 HTML 到 07_trading_decision_architecture/

输出文件（9 MD + 7 HTML）：
  - 00_panorama.md + .html     总指挥图（全部141节点按6阶段 subgraph 分层，单张 Mermaid 大图）
  - trading_flow_index.md       总览（四轨+6阶段+三态图例+指挥AI用法+共享信号注入+跨阶段候选附录）
  - 01_stock_selection.md + .html   选股（Mermaid 分图 + 叙事）
  - 02_buy_flow.md + .html          买入（Mermaid 分图 + 叙事）
  - 03_sell_flow.md + .html         卖出（Mermaid 分图 + 叙事）
  - 04_position_flow.md + .html     仓位（Mermaid 分图 + 叙事）
  - 05_execution_flow.md + .html    执行（Mermaid 分图 + 叙事）
  - 06_reconciliation.md + .html    对账（Mermaid 分图 + 叙事）
  - 07_modes.md                 回测/Paper/Shadow/实盘 四模式开关 + 应急保命降级（无 Mermaid）

真源分工（SSoT）：
  - 结构化数据（节点/边/flow_stage）真源 = decisiongraph (PostgreSQL)
  - 叙事层（大白话/ASCII框图/指挥AI提示）真源 = trading_flow_narrative.yaml
  - 候选模块（附录2）真源 = candidate_module_registry.yaml
  - 本生成器输出 = 派生产物（只读视图）

用法
----
    python scripts/governance/d5_architecture/generators/generate_trading_flow_diagram.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# 治本：_shared 在 scripts/governance/_shared，须将其父目录加入 sys.path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

try:
    from _common import DB_DISPLAY_NAME, cleanup_stale_files  # noqa: E402  # noqa: import-integrity  same-dir module via sys.path insert
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

    def cleanup_stale_files(output_dir: Path, expected: set[str], pattern: str) -> list[str]:  # noqa: ARG001
        """降级 stub：_common 不可用时不动文件。"""
        return []

from zephyr.governance.persistence.decision_graph_reader import (  # noqa: E402
    DecisionGraphReader,
)

# 治本：zoomable_html 在同目录（generators/），须将其加入 sys.path
_GENERATORS_DIR = str(Path(__file__).resolve().parent)
if _GENERATORS_DIR not in sys.path:
    sys.path.insert(0, _GENERATORS_DIR)

try:
    from zoomable_html import emit_zoomable_html, HTML_SUBDIR  # noqa: E402  # noqa: import-integrity  same-dir module via sys.path insert
except ImportError:
    emit_zoomable_html = None  # type: ignore[assignment]
    HTML_SUBDIR = "_zoomable_html"

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "07_trading_decision_architecture"
_ZOOMABLE_HTML_DIR = OUTPUT_DIR / HTML_SUBDIR
# HTML 跳转链接必须用 http:// — IDE 预览对相对路径/file:/// 会在编辑器内打开源码，
# 只有 http:// 链接交给外部浏览器渲染（需本地 doc http server，对标 generate_domain_doc.py）
_DOC_HTTP_BASE = "http://localhost:8765"
_DECISION_MODEL_YAML = _REPO_ROOT / "architecture_model" / "domain" / "decision_graph_model.yaml"
_NARRATIVE_YAML = _REPO_ROOT / "architecture_model" / "domain" / "trading_flow_narrative.yaml"
_CANDIDATE_REGISTRY_YAML = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "candidate_module_registry.yaml"
)

# flow_stage → 文件名映射（序号硬编码稳定，对标 06_decision_architecture 模式）
_FLOW_STAGE_FILES: dict[str, str] = {
    "stock_selection": "01_stock_selection.md",
    "buy_flow": "02_buy_flow.md",
    "sell_flow": "03_sell_flow.md",
    "position_management": "04_position_flow.md",
    "execution": "05_execution_flow.md",
    "reconciliation": "06_reconciliation.md",
}

# 06_modes.md → 07_modes.md（让出 06 给 reconciliation）
_MODES_FILE = "07_modes.md"
# 总指挥图：全部节点按 6 阶段 subgraph 分层的单张 Mermaid 大图
_PANORAMA_FILE = "00_panorama.md"
_INDEX_FILE = "trading_flow_index.md"
_ALL_OUTPUT_FILES = set(_FLOW_STAGE_FILES.values()) | {_MODES_FILE, _INDEX_FILE, _PANORAMA_FILE}

# 候选模块 target_track → flow_stage 映射（交易流相关 track）
# 映射依据：target_track 语义对应交易流阶段（比 target_layer 粗粒度更准）。
# 基础设施 track（backtest/simulation/disaster_recovery/data迁移）+ 死域/无位置候选
# 不归属任何交易流阶段，归入 index 跨阶段附录（避免污染业务流视图）。
_TRACK_TO_FLOW_STAGE: dict[str, str] = {
    "signal": "stock_selection",        # 信号生成 → 选股漏斗
    "factor": "stock_selection",        # 因子计算 → 选股
    "intelligence": "stock_selection",  # AI舆情 → 信号 → 选股
    "risk": "execution",                # 风控/熔断 → 执行
    "execution": "execution",           # 执行链路 → 执行
    "integration": "execution",         # 推理优化 → 执行链路
}
# 展示的候选状态（未落地的候选才进附录2；promoted 已进 depgraph 不展示）
_CANDIDATE_DISPLAY_STATUSES = {"candidate", "deferred", "rejected"}


# ============================================================
# YAML 真源加载
# ============================================================

def _load_yaml(path: Path) -> dict:
    """加载 YAML 真源。"""
    if not path.exists():
        print(f"ERROR: YAML 真源不存在: {path}", file=sys.stderr)
        sys.exit(2 if path == _NARRATIVE_YAML else 1)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _find_stage_narrative(narrative: dict, stage_id: str) -> dict | None:
    """从叙事 YAML 找指定 stage_id 的叙事段。"""
    for stage in narrative.get("flow_stages", []):
        if stage.get("stage_id") == stage_id:
            return stage
    return None


# ============================================================
# DB 节点查询（容错：flow_stage 列未迁移时返回空）
# ============================================================

def _load_nodes_by_stage(reader: DecisionGraphReader, stage_id: str) -> tuple[list[dict], list[dict]]:
    """按 flow_stage 查节点，返回 (production_nodes, design_nodes)。"""
    try:
        prod_nodes = reader.get_nodes_by_flow_stage(stage_id, design_maturity="production")
        design_nodes = reader.get_nodes_by_flow_stage(stage_id, design_maturity="design")
    except Exception as exc:  # noqa: BLE001
        # flow_stage 列未迁移或 DB 不可用 → 返回空，MD 显示"待标定"
        print(f"WARN: 查询 flow_stage={stage_id} 节点失败: {exc}", file=sys.stderr)
        return [], []
    return prod_nodes, design_nodes


# ============================================================
# 候选库加载（附录2 数据源）
# ============================================================

def _load_candidates_by_stage() -> tuple[dict[str, list[dict]], list[dict]]:
    """读候选库，按 flow_stage 分组。

    返回 (stage_to_candidates, cross_cutting_candidates)。

    映射规则：panorama_position.decisiongraph.target_track → flow_stage
    （_TRACK_TO_FLOW_STAGE）。基础设施 track + 死域/无位置候选 → cross_cutting
    （在 index 跨阶段附录展示，不污染业务流视图）。

    只展示未落地候选（candidate/deferred/rejected）；promoted 已进 depgraph 不展示。
    """
    if not _CANDIDATE_REGISTRY_YAML.exists():
        print(f"WARN: 候选库不存在: {_CANDIDATE_REGISTRY_YAML}", file=sys.stderr)
        return {}, []
    with open(_CANDIDATE_REGISTRY_YAML, encoding="utf-8") as f:
        reg = yaml.safe_load(f)
    entries = reg.get("entries", [])
    stage_map: dict[str, list[dict]] = {sid: [] for sid in _FLOW_STAGE_FILES}
    cross_cutting: list[dict] = []
    for e in entries:
        if e.get("status") not in _CANDIDATE_DISPLAY_STATUSES:
            continue
        dg = e.get("panorama_position", {}).get("decisiongraph", {})
        track = dg.get("target_track", "")
        stage = _TRACK_TO_FLOW_STAGE.get(track)
        if stage and stage in stage_map:
            stage_map[stage].append(e)
        else:
            cross_cutting.append(e)
    return stage_map, cross_cutting


# ============================================================
# DB 边查询（总图/分图 Mermaid 用）
# ============================================================

def _load_all_edges(reader: DecisionGraphReader, calibrated_node_ids: set[int]) -> list[dict]:
    """加载 decisiongraph 全部边，过滤为只连接已标定节点的边。"""
    try:
        all_edges = reader.get_all_edges()
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: 查询 decision_edges 失败: {exc}", file=sys.stderr)
        return []
    return [
        e for e in all_edges
        if e.get("from_node_id") in calibrated_node_ids
        and e.get("to_node_id") in calibrated_node_ids
    ]


# ============================================================
# Mermaid 可视化生成（遵循 visualization_view_template.md 规范）
# ============================================================

_MERMAID_THEME = (
    "%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', "
    "'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', "
    "'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
    "'clusterBkg': 'transparent', 'clusterBorder': 'transparent', "
    "'fontSize': '14px'}}}%%"
)

_CLASSDEF_LINES = (
    "    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000\n"
    "    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5"
)


def _sanitize_mermaid_label(text: str) -> str:
    """转义 Mermaid 标签特殊字符（对标 §4.9）。"""
    return (
        str(text)
        .replace("[", "(")
        .replace("]", ")")
        .replace('"', "'")
        .replace("|", "/")
        .replace("\n", " ")
    )


def _maturity_label(maturity: str | None) -> str:
    if maturity == "production":
        return "(生产态 / production)"
    return "(设计态 / design)"


def _mermaid_node_id(node_id: int) -> str:
    return f"n{node_id}"


def _mermaid_node_def(node: dict) -> str:
    """生成 Mermaid 节点定义行（成熟度+决策名+类型/层+路径）。"""
    nid = _mermaid_node_id(node["node_id"])
    mat = _maturity_label(node.get("design_maturity"))
    name = _sanitize_mermaid_label(node.get("decision_name", "?"))
    ntype = node.get("node_type", "?")
    layer = node.get("layer_id", "?")
    path = _sanitize_mermaid_label(node.get("path", "?"))
    label = f"{mat} {name}<br/>{ntype} | {layer} | {path}"
    return f'    {nid}["{label}"]'


def _mermaid_edge_def(edge: dict, maturity_map: dict[int, str]) -> str:
    """production→production 实线, 其他虚线。"""
    from_id = _mermaid_node_id(edge["from_node_id"])
    to_id = _mermaid_node_id(edge["to_node_id"])
    from_mat = maturity_map.get(edge["from_node_id"], "design")
    to_mat = maturity_map.get(edge["to_node_id"], "design")
    if from_mat == "production" and to_mat == "production":
        return f"    {from_id} --> {to_id}"
    return f"    {from_id} -.-> {to_id}"


def _mermaid_class_assign(node_ids: list[int], maturity: str = "design") -> str:
    if not node_ids:
        return ""
    cls = "production" if maturity == "production" else "design"
    ids = ",".join(_mermaid_node_id(nid) for nid in node_ids)
    return f"    class {ids} {cls}"


def _build_mermaid_stage(nodes: list[dict], edges: list[dict],
                         maturity_map: dict[int, str]) -> str:
    """构建单阶段 Mermaid 图代码（分图用）。"""
    if not nodes:
        return ""
    node_ids = {n["node_id"] for n in nodes}
    lines = [_MERMAID_THEME, "flowchart TD"]
    for n in nodes:
        lines.append(_mermaid_node_def(n))
    for e in edges:
        if e["from_node_id"] in node_ids and e["to_node_id"] in node_ids:
            lines.append(_mermaid_edge_def(e, maturity_map))
    lines.append(_CLASSDEF_LINES)
    prod_ids = [n["node_id"] for n in nodes if n.get("design_maturity") == "production"]
    design_ids = [n["node_id"] for n in nodes if n.get("design_maturity") != "production"]
    if prod_ids:
        lines.append(_mermaid_class_assign(prod_ids, "production"))
    if design_ids:
        lines.append(_mermaid_class_assign(design_ids, "design"))
    return "\n".join(lines)


def _build_mermaid_total(
    stage_nodes: dict[str, list[dict]],
    stage_names: dict[str, str],
    edges: list[dict],
    maturity_map: dict[int, str],
) -> str:
    """构建总图 Mermaid 代码（全部节点按6阶段 subgraph 分层）。"""
    all_ids: set[int] = set()
    subgraph_ids: list[str] = []  # 跟踪 subgraph ID，用于显式 style 着色
    lines = [_MERMAID_THEME, "flowchart TD"]
    for sid, nodes in stage_nodes.items():
        if not nodes:
            continue
        sname = stage_names.get(sid, sid)
        sg_id = f"S_{sid}"
        lines.append(f'    subgraph {sg_id}["{sname}（{len(nodes)}节点）"]')
        subgraph_ids.append(sg_id)
        for n in nodes:
            lines.append(_mermaid_node_def(n))
            all_ids.add(n["node_id"])
        lines.append("    end")
    for e in edges:
        if e["from_node_id"] in all_ids and e["to_node_id"] in all_ids:
            lines.append(_mermaid_edge_def(e, maturity_map))
    lines.append(_CLASSDEF_LINES)
    prod_ids = [nid for nid in all_ids if maturity_map.get(nid) == "production"]
    design_ids = [nid for nid in all_ids if maturity_map.get(nid) != "production"]
    if prod_ids:
        lines.append(_mermaid_class_assign(prod_ids, "production"))
    if design_ids:
        lines.append(_mermaid_class_assign(design_ids, "design"))
    return "\n".join(lines)


def _html_link_line(md_filename: str) -> str:
    """生成 MD 顶部的 HTML 跳转链接行（http:// 绝对链接，IDE 预览点击直达浏览器）。

    必须用 http:// 链接：Trae/VSCode 预览面板对相对路径和 file:/// 会在编辑器内打开源码，
    只有 http:// 链接交给外部浏览器渲染（对标 generate_domain_doc.py line 1093-1105）。
    """
    stem = Path(md_filename).stem
    html_rel = (_ZOOMABLE_HTML_DIR / f"{stem}.html").relative_to(_REPO_ROOT).as_posix()
    html_url = f"{_DOC_HTTP_BASE}/{html_rel}"
    return (
        f"> **[可缩放 HTML 版 / Zoomable HTML]({html_url})** — "
        f"Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式"
    )


# ============================================================
# MD 生成
# ============================================================

def _format_node_table(nodes: list[dict]) -> str:
    """格式化节点清单为 MD 表格。"""
    if not nodes:
        return "_（暂无已标定节点，待 Phase B 全量标定）_\n"
    rows = ["| node_id | 决策名称 | 节点类型 | layer | module_id | path |",
            "|---|---|---|---|---|---|"]
    for n in nodes:
        rows.append(
            f"| {n.get('node_id', '?')} | {n.get('decision_name', '?')} | "
            f"{n.get('node_type', '?')} | {n.get('layer_id', '?')} | "
            f"{n.get('module_id') or '-'} | `{n.get('path', '?')}` |"
        )
    return "\n".join(rows) + "\n"


def _format_candidate_table(candidates: list[dict]) -> str:
    """格式化候选模块清单为 MD 表格（附录2）。"""
    if not candidates:
        return "_（本阶段暂无候选模块）_\n"
    rows = [
        "| 候选ID | 名称 | 状态 | 优先级 | 卡在哪问 | 解决什么痛点 |",
        "|---|---|---|---|---|---|",
    ]
    for c in candidates:
        fq = c.get("four_question", {}) or {}
        blocking = fq.get("blocking_question", "-") or "-"
        problem = (c.get("problem_it_solves") or "-").replace("|", "\\|").replace("\n", " ")
        if len(problem) > 60:
            problem = problem[:57] + "..."
        rows.append(
            f"| {c.get('id', '?')} | {c.get('name', '?')} | "
            f"{c.get('status', '?')} | {c.get('priority', '-')} | "
            f"{blocking} | {problem} |"
        )
    return "\n".join(rows) + "\n"


def _generate_index(flow_stages_def: list[dict], narrative: dict, stage_node_counts: dict[str, tuple[int, int]],
                    cross_cutting_candidates: list[dict] | None = None) -> str:
    """生成总览 trading_flow_index.md。"""
    cc = narrative.get("cross_cutting", {})
    lines = [
        "---",
        "ttl: permanent",
        "doc_type: architecture_view",
        "generator: generate_trading_flow_diagram.py",
        "---",
        "",
        "# 交易决策架构总览（07_ 视图）",
        "",
        "> 版本：v1.0.0 | 2026-07-31",
        "> 读者：项目 Owner（主要）+ AI 开发 Agent（次要）",
        "> 写法：大白话为主。本视图是 decisiongraph 的业务流程视图，不是新图。",
        "",
        "## 这是什么？大白话讲交易决策架构",
        "",
        "这份文档是**交易决策架构视图**——把 decisiongraph 里的决策节点按「交易动作」",
        "（选股→买入→卖出→仓位→执行→对账）重新组织，串成一条「钱怎么赚」的完整流程。",
        "",
        "和 [06_decision_architecture/](../06_decision_architecture/decision_index.md) 的区别：",
        "- 06_ 是**零件决策流**（按层/轨拆分的节点清单，回答「决策怎么分层」）",
        "- 07_ 是**交易决策架构**（按业务流程串成的叙事，回答「钱怎么赚、每步做什么」）",
        "",
        "## 怎么用这份文档指挥 AI",
        "",
        "1. 找到你要改的流程阶段（选股/买入/卖出/仓位/执行）",
        "2. 看该阶段的「指挥 AI 提示」，知道改这个流程要动哪些模块",
        "3. 用 module_id 锚点让 AI 定位到具体代码文件（链回 depgraph）",
        "4. AI 改之前必须先查 decisiongraph 确认节点存在（防幻觉）",
        "",
        "## 总指挥图（一张图看全流程）",
        "",
        f"> 详见 [{_PANORAMA_FILE}]({_PANORAMA_FILE})——全部决策节点按6阶段分层，单张 Mermaid 大图 + 可缩放 HTML。",
        "",
        "## 四轨并行架构",
        "",
        cc.get("four_tracks", {}).get("narrative", "_（待补充）_"),
        "",
        "## 共享信号注入层",
        "",
        cc.get("shared_signal_injection", {}).get("narrative", "_（待补充）_"),
        "",
        "## 6 阶段业务流程",
        "",
        "| 阶段 | 文档 | 运营态节点 | 设计态节点 | 产出 |",
        "|---|---|---|---|---|",
    ]
    for stage in flow_stages_def:
        sid = stage["stage_id"]
        fname = _FLOW_STAGE_FILES.get(sid, "?")
        prod_cnt, design_cnt = stage_node_counts.get(sid, (0, 0))
        lines.append(
            f"| [{stage['stage_name']}]({fname}) | {fname} | {prod_cnt} | {design_cnt} | "
            f"`{stage.get('output_contract', '-')}` |"
        )
    lines.extend([
        "",
        "## 应急保命降级路径",
        "",
        cc.get("emergency_degradation", {}).get("narrative", "_（待补充）_"),
        "",
        "## 三态图例",
        "",
        "- **运营态（production）**：实盘主链路节点，主图展示",
        "- **设计态（design, approved）**：通过四问过滤、待施工，附录1展示",
        "- **候选库（candidate/deferred/rejected）**：过度工程/超前设计，附录2展示（从 candidate_module_registry.yaml 提取）",
        "",
        "## 四模式开关",
        "",
        "详见 [07_modes.md](07_modes.md)（回测/Paper/Shadow/实盘）",
        "",
    ])
    # 跨阶段附录：基础设施类候选（backtest/simulation/DR/死域等不归属任何交易流阶段）
    if cross_cutting_candidates:
        from collections import Counter
        status_counts = Counter(e.get("status", "?") for e in cross_cutting_candidates)
        status_summary = "、".join(f"{s}×{c}" for s, c in status_counts.most_common())
        lines.extend([
            "## 附录·跨阶段候选（基础设施类）",
            "",
            f"以下候选不归属任何交易流阶段（回测/仿真/灾备/死域等），共 "
            f"**{len(cross_cutting_candidates)} 条**（{status_summary}）。",
            "",
            "> 完整清单见 `docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml`。",
            "",
            "样例（前10条）：",
            "",
            _format_candidate_table(cross_cutting_candidates[:10]),
        ])
    lines.append(f"> 数据源：{DB_DISPLAY_NAME} + trading_flow_narrative.yaml + candidate_module_registry.yaml")
    return "\n".join(lines) + "\n"


def _generate_stage_doc(stage_def: dict, stage_narrative: dict | None,
                        prod_nodes: list[dict], design_nodes: list[dict],
                        edges: list[dict], maturity_map: dict[int, str],
                        md_filename: str,
                        candidates: list[dict] | None = None) -> str:
    """生成单个 flow_stage 的 MD（分阶段图，含 Mermaid + HTML 联动）。"""
    sid = stage_def["stage_id"]
    name = stage_def["stage_name"]
    narr = stage_narrative or {}
    all_nodes = prod_nodes + design_nodes
    mermaid_code = _build_mermaid_stage(all_nodes, edges, maturity_map)
    lines = [
        "---",
        "ttl: permanent",
        "doc_type: architecture_view",
        "generator: generate_trading_flow_diagram.py",
        f"flow_stage: {sid}",
        "---",
        "",
        f"# {name}",
        "",
        f"> flow_stage: `{sid}` | 映射层: {stage_def.get('mapped_layers', [])} | "
        f"产出契约: `{stage_def.get('output_contract', '-')}`",
        "",
        _html_link_line(md_filename),
        "",
        "## 大白话讲这个流程",
        "",
        narr.get("narrative", "_（待补充叙事）_"),
        "",
        "## 流程框图",
        "",
        "```",
        narr.get("ascii_diagram", "_（待补充框图）_"),
        "```",
        "",
        "## 决策流可视化（Mermaid）",
        "",
        "> 本阶段决策节点 + 同阶段内依赖边。运营态蓝色实线，设计态橙色虚线。",
        "> 网页版可 Ctrl+滚轮缩放查看细节。",
        "> 图例：🟦 蓝色=运营态(production) ｜ 🟧 橙色虚线=设计态(design) ｜ 实线=运营态依赖 ｜ 虚线=非运营态依赖",
        "",
    ]
    if mermaid_code:
        lines.append("```mermaid")
        lines.append(mermaid_code)
        lines.append("```")
    else:
        lines.append("_（暂无已标定节点，待 Phase B 全量标定）_")
    lines.extend([
        "",
        "## 运营态节点（实盘主链路）",
        "",
        _format_node_table(prod_nodes),
        "",
        "## 指挥 AI 提示",
        "",
        narr.get("ai_directive", "_（待补充）_"),
        "",
    ])
    # 子流程
    sub_flows = narr.get("sub_flows", [])
    if sub_flows:
        lines.append("## 子流程")
        lines.append("")
        for sf in sub_flows:
            lines.append(f"### {sf.get('name', sf.get('sub_id', '?'))}")
            lines.append("")
            lines.append(sf.get("narrative", ""))
            anchors = sf.get("module_anchors", [])
            if anchors:
                lines.append("")
                lines.append("模块锚点: " + ", ".join(f"`{a}`" for a in anchors))
            lines.append("")
    # 附录1：设计态节点
    lines.extend([
        "## 附录1·待施工（设计态节点）",
        "",
        _format_node_table(design_nodes),
        "",
        "## 附录2·未来增强（候选库）",
        "",
        "_从 candidate_module_registry.yaml 按 target_track 归类到本阶段；"
        "基础设施类候选（回测/仿真/灾备/死域）见 [总览](trading_flow_index.md) 跨阶段附录_",
        "",
        _format_candidate_table(candidates or []),
    ])
    return "\n".join(lines) + "\n"


def _generate_modes_doc(narrative: dict) -> str:
    """生成 06_modes.md（四模式开关 + 应急保命降级）。"""
    cc = narrative.get("cross_cutting", {})
    fm = cc.get("four_modes", {})
    modes = fm.get("modes", [])
    lines = [
        "---",
        "ttl: permanent",
        "doc_type: architecture_view",
        "generator: generate_trading_flow_diagram.py",
        "---",
        "",
        "# 四模式开关 + 应急保命降级",
        "",
        "## 四模式开关（回测/Paper/Shadow/实盘）",
        "",
        fm.get("narrative", "_（待补充）_"),
        "",
        "| 模式 | 数据源 | 下单方式 |",
        "|---|---|---|",
    ]
    for m in modes:
        lines.append(
            f"| {m.get('mode_name', m.get('mode_id', '?'))} | "
            f"{m.get('data_source', '-')} | {m.get('order_mode', '-')} |"
        )
    lines.extend([
        "",
        "## 应急保命降级路径",
        "",
        cc.get("emergency_degradation", {}).get("narrative", "_（待补充）_"),
        "",
        f"> 数据源：trading_flow_narrative.yaml",
    ])
    return "\n".join(lines) + "\n"


def _generate_panorama_doc(stage_nodes_all: dict[str, list[dict]],
                           stage_names: dict[str, str],
                           edges: list[dict], maturity_map: dict[int, str],
                           total_nodes: int, total_edges: int) -> str:
    """生成总指挥图 00_panorama.md（全部节点按6阶段 subgraph 分层的单张 Mermaid 大图）。"""
    mermaid_code = _build_mermaid_total(stage_nodes_all, stage_names, edges, maturity_map)
    lines = [
        "---",
        "ttl: permanent",
        "doc_type: architecture_view",
        "generator: generate_trading_flow_diagram.py",
        "---",
        "",
        "# 交易决策总指挥图（全流程全景）",
        "",
        f"> 本图包含全部 {total_nodes} 个决策节点（按6阶段 subgraph 分层）+ {total_edges} 条决策边（含跨阶段）。",
        "> 一张图看懂「钱怎么赚」的完整交易决策流程。",
        "",
        _html_link_line(_PANORAMA_FILE),
        "",
        "## 怎么看这张图",
        "",
        "1. **6 个 subgraph** = 6 个业务阶段（选股→买入→卖出→仓位→执行→对账），从上到下是钱的流向",
        "2. **节点颜色**：🟦 蓝色=运营态(production, 已上线) ｜ 🟧 橙色虚线=设计态(design, 待施工)",
        "3. **边样式**：实线=运营态依赖 ｜ 虚线=非运营态依赖（含设计态/混合）",
        "4. **跨阶段边**：连接不同 subgraph 的边，体现阶段间数据/触发流转",
        "5. 网页版可 Ctrl+滚轮无限缩放，拖动平移查看每个节点细节",
        "",
        "## 各阶段分图",
        "",
    ]
    for sid, fname in _FLOW_STAGE_FILES.items():
        sname = stage_names.get(sid, sid)
        cnt = len(stage_nodes_all.get(sid, []))
        lines.append(f"- [{sname}]({fname})（{cnt} 节点）")
    lines.extend([
        "",
        "## 总指挥图（Mermaid）",
        "",
        "> 全部决策节点 + 决策边。大图请在 HTML 网页版查看（Ctrl+滚轮缩放）。",
        "",
        "```mermaid",
        mermaid_code,
        "```",
        "",
        f"> 数据源：{DB_DISPLAY_NAME} decision_nodes + decision_edges（flow_stage 已标定节点）",
    ])
    return "\n".join(lines) + "\n"


# ============================================================
# 主入口
# ============================================================

def main() -> None:
    """主入口：加载 YAML + 读 DB + 读候选库 → 生成 9 个 MD + 7 个 HTML。"""
    parser = argparse.ArgumentParser(description="G-trading-flow: 生成交易决策架构视图")
    parser.add_argument("--dry-run", action="store_true", help="预演：不写文件，只打印")
    parser.add_argument("--no-html", action="store_true", help="跳过 HTML 联动生成")
    args = parser.parse_args()

    # 1. 加载 YAML 真源
    model_def = _load_yaml(_DECISION_MODEL_YAML)
    narrative = _load_yaml(_NARRATIVE_YAML)
    flow_stages_def = model_def.get("flow_stages", [])
    if not flow_stages_def:
        print("ERROR: decision_graph_model.yaml 无 flow_stages 段", file=sys.stderr)
        sys.exit(1)

    # 2. 读 DB 节点（按 flow_stage）+ 边
    reader = DecisionGraphReader()
    stage_node_counts: dict[str, tuple[int, int]] = {}
    stage_nodes: dict[str, tuple[list[dict], list[dict]]] = {}
    stage_nodes_all: dict[str, list[dict]] = {}
    stage_names: dict[str, str] = {}
    maturity_map: dict[int, str] = {}
    for stage in flow_stages_def:
        sid = stage["stage_id"]
        stage_names[sid] = stage.get("stage_name", sid)
        if sid not in _FLOW_STAGE_FILES:
            continue
        prod, design = _load_nodes_by_stage(reader, sid)
        stage_nodes[sid] = (prod, design)
        stage_node_counts[sid] = (len(prod), len(design))
        all_n = prod + design
        stage_nodes_all[sid] = all_n
        for n in all_n:
            maturity_map[n["node_id"]] = n.get("design_maturity", "design")
    calibrated_ids = set(maturity_map.keys())
    edges = _load_all_edges(reader, calibrated_ids)
    reader.close()

    # 3. 读候选库（附录2 数据源）
    cand_by_stage, cross_cutting = _load_candidates_by_stage()

    # 4. 生成 MD
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[tuple[str, str]] = []
    total_nodes = len(calibrated_ids)
    total_edges = len(edges)

    # 总指挥图
    outputs.append((_PANORAMA_FILE, _generate_panorama_doc(
        stage_nodes_all, stage_names, edges, maturity_map, total_nodes, total_edges)))
    # 总览
    outputs.append((_INDEX_FILE, _generate_index(
        flow_stages_def, narrative, stage_node_counts, cross_cutting)))
    # 6 阶段分图
    for stage in flow_stages_def:
        sid = stage["stage_id"]
        if sid not in _FLOW_STAGE_FILES:
            continue
        fname = _FLOW_STAGE_FILES[sid]
        stage_narr = _find_stage_narrative(narrative, sid)
        prod, design = stage_nodes.get(sid, ([], []))
        outputs.append((fname, _generate_stage_doc(
            stage, stage_narr, prod, design, edges, maturity_map, fname,
            cand_by_stage.get(sid, []))))
    # 模式
    outputs.append((_MODES_FILE, _generate_modes_doc(narrative)))

    # 5. 写 MD + 联动生成 HTML
    cleanup_stale_files(OUTPUT_DIR, _ALL_OUTPUT_FILES, r"^[a-z0-9_]+\.md$")
    written = 0
    html_count = 0
    for fname, content in outputs:
        out_path = OUTPUT_DIR / fname
        if args.dry_run:
            print(f"[DRY-RUN] would write {out_path} ({len(content)} bytes)")
            continue
        out_path.write_text(content, encoding="utf-8")
        print(f"[OK] {out_path} ({len(content)} bytes)")
        written += 1
        if not args.no_html and emit_zoomable_html is not None:
            html_path = emit_zoomable_html(out_path, content, output_dir=_ZOOMABLE_HTML_DIR)
            if html_path:
                print(f"[OK] {html_path}")
                html_count += 1

    print(f"\n生成完成：{written} 个 MD + {html_count} 个 HTML → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
