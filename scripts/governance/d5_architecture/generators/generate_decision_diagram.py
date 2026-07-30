# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.d5_architecture.generators.generate_decision_diagram
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); architecture_model/domain/decision_graph_model.yaml (invariants 真源); _common (cleanup_stale_files, DB_DISPLAY_NAME)
# [CONSUMERS] CI自动触发;人工查看06_decision_architecture/
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出22文件);只读decisiongraph;输出到06_decision_architecture/;序号硬编码稳定
# [MODIFY-GUARD] 修改需通过TRAE-061任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] decisiongraph不存在→exit 1;无tracks/layers→exit 2;域集合漂移→exit 3
# [TESTS] tests/test_generate_decision_diagram.py
# [TTL] permanent
"""G-decision: 从 decisiongraph (PostgreSQL) 生成决策流图(.md 文档，Mermaid 内嵌)

依据：TRAE-061 任务（2026-07-06）；拆分重构（2026-07-19）。

功能：
  - 从 decision_tracks / decision_layers / decision_nodes / decision_edges 表读取决策流图
  - 从 decision_graph_model.yaml 读取 invariants 定义（5 条承重墙不变量）
  - 生成 Mermaid 图表并内嵌在 Markdown ```mermaid 代码块中
  - 输出到 docs/02_enterprise_architecture/06_decision_architecture/

输出文件（22 个，治本拆分，对标 02_domain_architecture_docs/ 模式）：
  - decision_index.md              主索引（纯导航，0 个 mermaid）
  - 01..05_decision_track_*.md     5 个 Track 文件（各 3 视图：合并/设计态/运营态）
  - 06..12_decision_l2a_*.md       7 个 L2A 功能域文件
  - 13..19_decision_l3_*.md        7 个 L3 功能域文件
  - 20_decision_layers.md          层级详情图
  - 21_decision_invariants.md      不变量图

用法
----
    python scripts/governance/d5_architecture/generators/generate_decision_diagram.py
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
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

from _shared.constants import EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR
try:
    from _common import DB_DISPLAY_NAME, cleanup_stale_files  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

    def cleanup_stale_files(output_dir: Path, expected: set[str], pattern: str) -> list[str]:  # noqa: ARG001
        """降级 stub：_common 不可用时不动文件。"""
        return []

from zephyr.governance.persistence.decisiongraph_schema import (  # noqa: E402
    get_decisiongraph_pg_connection,
)

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "06_decision_architecture"
_YAML_PATH = _REPO_ROOT / "architecture_model" / "domain" / "decision_graph_model.yaml"

# --- 文件编号（硬编码，字母序保证跨重生成稳定） ---
# Track 01-05 按 priority（DB ORDER BY priority）；L2A 06-12 按域名字母序；L3 13-19 按域名字母序
_L2A_DOMAINS_ALPHA = ["data", "factor", "frontend", "research", "sell", "signal", "simulation"]
_L3_DOMAINS_ALPHA = ["aut_core", "ex_core", "ex_sor", "pf_alloc", "pf_core", "position", "trading"]
_L2A_DOMAIN_LAYER = "L2A"
_L3_DOMAIN_LAYER = "L3"
_L2A_SEQ_OFFSET = 6   # 06..12
_L3_SEQ_OFFSET = 13   # 13..19
_LAYERS_FILE_NAME = "20_decision_layers.md"
_INVARIANTS_FILE_NAME = "21_decision_invariants.md"
_STALE_FILE_REGEX = r"^\d{2}_decision_[a-z0-9_]+\.md$"
# 架构层 ID 正则：L0-L6（含 L2A/L2B/L2C/L2D 子层）。decision_layers 表还含
# 模块级条目（MOD-*/CFG-*/INFRA-*/SH-*/SYS-*，约 650 个），层级详情图只画
# L0-L6 架构层——模块详情已在 01-19 per-track/per-domain 文件覆盖，全画会导致
# mermaid 节点数超限（>300）渲染失败。
_ARCH_LAYER_RE = re.compile(r"^L[0-6]")

# --- Mermaid 主题策略（用户 VS Code 1.129.1 实测确认 2026-07-30）---
# 用户在 VS Code Markdown Preview 中实测确认：
#   1. %%{init}%% 主题变量生效——flowchart 节点填充为 #eaeaea 灰色 ✓
#   2. subgraph 内节点使用 secondaryColor 而非 primaryColor——若不设
#      secondaryColor，subgraph 内节点回退白色（_gen_overview_mmd 有 track subgraph）
#   3. clusterBkg/clusterBorder 不被 VS Code mermaid 渲染器识别，已移除
# 故：primaryColor + secondaryColor + tertiaryColor 全设 #eaeaea，保证无论
# 节点是否在 subgraph 内都显示灰色。_gen_layers_mmd/invariants/cross_domain
# 已去掉 subgraph（扁平布局），_gen_overview_mmd 保留 track subgraph（需 secondaryColor）。
# _build_status_color() 保留供测试使用；生成逻辑用文字标注 build_status。
_MERMAID_INIT = (
    "%%{init: {'theme': 'base', 'themeVariables': "
    "{'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', "
    "'primaryBorderColor': '#666666', 'lineColor': '#666666', "
    "'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
    "'fontSize': '14px'}}}%%"
)

# 功能域英文→中文映射（双语标题/节点标签用）
_DOMAIN_NAME_ZH: dict[str, str] = {
    # L2A 信号层
    "data": "数据", "factor": "因子", "frontend": "前端", "research": "研究",
    "sell": "卖出", "signal": "信号", "simulation": "仿真",
    # L3 策略组合层
    "aut_core": "自主核心", "ex_core": "执行核心", "ex_sor": "执行排序",
    "pf_alloc": "组合分配", "pf_core": "组合核心", "position": "持仓", "trading": "交易",
}

# 边类型英文→中文映射（mermaid 边标签用 英文 / 中文 格式，参考 dataflow 风格）
_EDGE_TYPE_ZH: dict[str, str] = {
    "triggering": "触发",
    "informing": "告知",
    "approving": "批准",
    "feedback": "反馈",
    "portfolio_target": "仓位目标",
    "risk_check": "风控检查",
}


def _git_commit_timestamp() -> str:
    """获取本生成器脚本最近一次 git commit 时间（ISO 8601 秒精度）。

    幂等时间源：相同 commit → 相同时间戳，避免 datetime.now() 导致输出非确定性。
    git 不可用或文件未入库时返回固定占位符。
    """
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", __file__],
            capture_output=True, text=True, timeout=5,
            cwd=str(_REPO_ROOT),
        )
        if r.returncode == 0 and r.stdout.strip():
            # %cI 输出形如 2026-07-19T13:47:00+08:00，截到秒
            return r.stdout.strip()[:19]
    except Exception:  # noqa: BLE001 — git 不可用时降级
        pass
    return "unknown"


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
                   decision_frequency, design_maturity, build_status,
                   module_id, source_code_ref
            FROM decision_layers ORDER BY layer_id
        """)
        layers = [
            {
                "id": r[0], "name": r[1], "name_en": r[2], "track": r[3],
                "desc": r[4], "freq": r[5], "maturity": r[6], "build": r[7],
                "module_id": r[8], "source_code_ref": r[9],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT node_id, layer_id, node_type, path, module_id, decision_name,
                   build_status, design_maturity, evidence_hash, source_code_ref
            FROM decision_nodes ORDER BY layer_id, node_id
        """)
        nodes = [
            {
                "id": r[0], "layer_id": r[1], "type": r[2], "path": r[3],
                "module_id": r[4], "name": r[5], "build": r[6],
                "maturity": r[7], "hash": r[8], "source_code_ref": r[9],
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


def _resolve_blueprint_names(conn, layers: list[dict]) -> dict[str, str]:
    """从 depgraph 查 module_id→blueprint_name 映射。

    :return: {module_id: blueprint_name}，查不到的 module_id 不包含在映射中
    """
    module_ids = {l.get("module_id") for l in layers if l.get("module_id")}
    if not module_ids:
        return {}
    result: dict[str, str] = {}
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT blueprint_id, node_name
                FROM nodes
                WHERE blueprint_id = ANY(%s)
                  AND node_name IS NOT NULL
                  AND node_name != ''
                """,
                (list(module_ids),),
            )
            for row in cur.fetchall():
                bp_id = row[0] if isinstance(row, (list, tuple)) else row.get("blueprint_id")
                bp_name = row[1] if isinstance(row, (list, tuple)) else row.get("node_name")
                if bp_id and bp_name:
                    result[bp_id] = bp_name
    except Exception:  # noqa: BLE001 — depgraph 查询失败时静默降级为仅展示 module_id
        pass
    return result


def _truncate(text: str, max_len: int = 20) -> str:
    """截断文本到指定长度，超出加省略号。"""
    if not text:
        return ""
    text = text.strip().replace("\n", " ").replace(">", "》")
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"


def _build_status_color(build: str) -> str:
    """build_status → mermaid 颜色类。"""
    return {
        "stable": "bsStable",
        "generated": "bsGenerated",
        "testing": "bsTesting",
        "planned": "bsPlanned",
        "deprecated": "bsDeprecated",
    }.get(build, "bsGenerated")


def _edge_label(edge_type: str) -> str:
    """边类型 → 中英文标签（英文 / 中文），参考 dataflow 的 produces / 产出风格。"""
    zh = _EDGE_TYPE_ZH.get(edge_type)
    if zh:
        return f"{edge_type} / {zh}"
    return edge_type


def _maturity_tag(maturity: str | None) -> str:
    """design_maturity → 标注标签（[production]/[design]/空）。"""
    if not maturity:
        return ""
    return f"[{maturity}]"


def _node_domain(path: str) -> str:
    """path 第 2 段（功能域），如 'decision/sell/sell_00' → 'sell'。

    path 不足 2 段返回空串（调用方负责跳过）。
    """
    parts = (path or "").split("/")
    return parts[1] if len(parts) >= 2 else ""


def _filter_overview_inputs(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
    *, maturity: str | None = None,
    track_id: str | None = None, path_prefix: str | None = None,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """全景图输入过滤辅助（复杂度收口，避免 _gen_overview_mmd 超 15）。

    过滤顺序：maturity → track_id → path_prefix（path 第 2 段精确匹配）→ 边端点 → 空 track。
    返回新列表，不修改输入。maturity 取值："production" / "design" / None（不过滤）。
    """
    # maturity 过滤
    if maturity is not None:
        layers = [l for l in layers if l.get("maturity") == maturity]
        layer_ids = {l["id"] for l in layers}
        nodes = [n for n in nodes if n["layer_id"] in layer_ids and n.get("maturity") == maturity]
    # track_id 过滤
    if track_id is not None:
        layers = [l for l in layers if l["track"] == track_id]
        layer_ids = {l["id"] for l in layers}
        nodes = [n for n in nodes if n["layer_id"] in layer_ids]
    # path_prefix 过滤（path 第 2 段精确匹配，不用 startswith 避免 sell/sell_algo 误匹配）
    if path_prefix is not None:
        nodes = [n for n in nodes if _node_domain(n.get("path", "")) == path_prefix]
    # 边端点必须都在过滤后节点集中
    node_ids = {n["id"] for n in nodes}
    edges = [e for e in edges if e["from"] in node_ids and e["to"] in node_ids]
    # tracks 过滤：只保留仍有 layer 的 track
    used_track_ids = {l["track"] for l in layers}
    tracks = [t for t in tracks if t["id"] in used_track_ids]
    return tracks, layers, nodes, edges


def _gen_overview_mmd(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
    production_only: bool = False, design_only: bool = False,
    track_id: str | None = None, path_prefix: str | None = None,
    skeleton_only: bool = False,
) -> tuple[str, int, int, int]:
    """生成全景图：L0-L6 层级 + 节点/边（扁平布局，无 subgraph）。

    Args:
        production_only: True 时仅 design_maturity='production'。
        design_only: True 时仅 design_maturity='design'。与 production_only 互斥。
        track_id: 仅生成该 track（用于 per-Track 文件）。
        path_prefix: 仅生成该 path 第 2 段域的节点（用于 per-domain 文件）。
        skeleton_only: True 时仅画 Layer 节点 + 层间边，跳过决策节点（用于 Track 概览图）。
    """
    # 将 production_only/design_only 转换为 maturity 单参（保持 _gen_overview_mmd 签名不变）
    _maturity = "production" if production_only else ("design" if design_only else None)
    tracks, layers, nodes, edges = _filter_overview_inputs(
        tracks, layers, nodes, edges,
        maturity=_maturity,
        track_id=track_id, path_prefix=path_prefix,
    )

    lines = [_MERMAID_INIT, "flowchart TD"]

    # 扁平布局（不使用 subgraph）——与 _gen_layers_mmd/_gen_invariants_mmd 一致。
    # 用户实测确认（2026-07-30）：subgraph 内节点使用 secondaryColor 而非 primaryColor，
    # 导致 %%{init}%% 设的 primaryColor 不生效（节点白色）；subgraph 容器背景
    # (clusterBkg) VS Code 渲染器不识别主题变量，回退白色，与灰色节点不协调且
    # 增加整体高度。去掉 subgraph 后 primaryColor 生效（节点灰色）、高度更紧凑。
    # per-track/per-domain 文件经 track_id/path_prefix 过滤后只有 1 个 track，无需分组。
    for track in tracks:
        tid = track["id"]
        track_layers = [l for l in layers if l["track"] == tid]
        for layer in track_layers:
            lid = layer["id"]
            safe_lid = lid.replace("-", "_")
            # 精简 label：层 ID+名称+maturity/build+功能简介（截断）。蓝图/代码/频率在表格。
            _mat = layer.get("maturity") or "-"
            _desc = _truncate(layer.get("desc", ""), 30)
            label = f'{layer["id"]}: {layer["name"]}<br/>{_mat}/{layer["build"]}'
            if _desc:
                label = f'{label}<br/>{_desc}'
            lines.append(f'    L{safe_lid}["{label}"]')
            if not skeleton_only:
                layer_nodes = [n for n in nodes if n["layer_id"] == lid]
                for n in layer_nodes:
                    # 精简：仅 type+name（1 行），path 在 Node 清单表
                    nlabel = f'{n["type"]}: {n["name"]}'
                    lines.append(f'    N{n["id"]}("{nlabel}")')
                    lines.append(f'    L{safe_lid} --- N{n["id"]}')

    # 层间边（triggering，按 layer 顺序）
    layer_ids = [l["id"] for l in layers]
    for i in range(len(layer_ids) - 1):
        from_lid = layer_ids[i].replace("-", "_")
        to_lid = layer_ids[i + 1].replace("-", "_")
        lines.append(f'    L{from_lid} -.->|{_edge_label("triggering")}| L{to_lid}')

    # 节点间边（skeleton_only 模式下跳过——无决策节点）
    if not skeleton_only:
        for e in edges:
            lines.append(f'    N{e["from"]} -->|{_edge_label(e["type"])}| N{e["to"]}')

    return "\n".join(lines) + "\n", len(tracks), len(layers), len(edges)


def _gen_layers_mmd(tracks: list[dict], layers: list[dict]) -> str:
    """生成层级详情图：L0-L6 架构层卡片 + 频率/成熟度/状态 + 流向箭头。

    只渲染 L0-L6 架构层（约 10 个节点），过滤 decision_layers 表中的模块级/
    基础设施级条目（MOD-*/CFG-*/INFRA-*/SH-*/SYS-*）——这些详情已在 01-19
    per-track/per-domain 文件覆盖。全量渲染（~660 节点）会导致 mermaid 渲染失败。

    用户实测确认（2026-07-30）：subgraph 内的节点使用 secondaryColor 而非
    primaryColor，导致 %%{init}%% 设的 primaryColor 不生效（节点白色）。
    去掉 subgraph 后 primaryColor 生效（节点灰色）。布局用 TD 竖向（方案 L）。
    """
    layers = [l for l in layers if _ARCH_LAYER_RE.match(l["id"])]
    lines = [_MERMAID_INIT, "flowchart TD"]

    for layer in layers:
        lid = layer["id"].replace("-", "_")
        # 精简 label：层 ID+名称+maturity/build+功能简介（截断）。蓝图/代码/频率详情在
        # 同文件 Layer 清单表（_layer_table），图只承载视觉概览。
        _mat = layer.get("maturity") or "-"
        _desc = _truncate(layer.get("desc", ""), 30)
        label = f'{layer["id"]} {layer["name"]}<br/>{_mat}/{layer["build"]}'
        if _desc:
            label = f'{label}<br/>{_desc}'
        lines.append(f'    L{lid}["{label}"]')

    layer_ids = [l["id"] for l in layers]
    for i in range(len(layer_ids) - 1):
        from_lid = layer_ids[i].replace("-", "_")
        to_lid = layer_ids[i + 1].replace("-", "_")
        lines.append(f'    L{from_lid} -->|{_edge_label("triggering")}| L{to_lid}')

    # 反馈边（L6 → L1/L5，学习闭环）。节点 ID = "L" + layer_id（与上方定义一致）
    if len(layer_ids) >= 6:
        l1 = f"L{layer_ids[1].replace('-', '_')}" if len(layer_ids) > 1 else None
        l5 = f"L{layer_ids[-2].replace('-', '_')}"  # 倒数第 2 = L5
        l6 = f"L{layer_ids[-1].replace('-', '_')}"  # 最后 = L6
        if l1:
            lines.append(f'    {l6} -.->|{_edge_label("feedback")}| {l1}')
        lines.append(f'    {l6} -.->|{_edge_label("feedback")}| {l5}')

    return "\n".join(lines) + "\n"


def _gen_invariants_mmd(invariants: list[dict]) -> str:
    """生成不变量图：6 节点类型 + 5 不变量标注 + 合法/非法连接。

    不使用 subgraph——subgraph 内节点使用 secondaryColor 而非 primaryColor，
    导致 %%{init}%% 设的 primaryColor 不生效（节点白色）。扁平布局保证灰色。
    """
    lines = [_MERMAID_INIT, "flowchart TD"]

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
        lines.append(f'    NT_{safe}["{label}"]')

    lines.append(f"    NT_signal -->|{_edge_label('portfolio_target')}| NT_portfolio_target")
    lines.append(f"    NT_portfolio_target -->|{_edge_label('risk_check')}| NT_risk_check")
    lines.append(f"    NT_risk_check -->|{_edge_label('approving')}| NT_order")
    lines.append(f"    NT_order -->|{_edge_label('triggering')}| NT_execution")
    lines.append(f"    NT_execution -.->|{_edge_label('feedback')}| NT_feedback")
    lines.append(f"    NT_feedback -.->|{_edge_label('informing')}| NT_signal")

    lines.append("    NT_signal -.->|禁止| NT_order")
    lines.append("    linkStyle 6 stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5")

    for inv in invariants:
        iid = inv["id"]
        safe_iid = iid.replace("-", "_")
        label = f'{iid}<br/>{inv["name"]}<br/>{inv["name_en"]}'
        lines.append(f'    INV_{safe_iid}(["{label}"])')

    lines.append("    INV_DEC_INV_001 -.- NT_order")
    lines.append("    INV_DEC_INV_002 -.- NT_signal")
    lines.append("    INV_DEC_INV_003 -.- NT_feedback")
    lines.append("    INV_DEC_INV_005 -.- NT_signal")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 文件编号与域索引
# ---------------------------------------------------------------------------


def _track_filename(track: dict) -> str:
    """01_decision_track_<track_id>.md — 序号取自 track['priority']。"""
    seq = track.get("priority") or 0
    safe_tid = track["id"].replace("-", "_")
    return f"{seq:02d}_decision_track_{safe_tid}.md"


def _domain_filename(layer_id: str, domain: str) -> str:
    """NN_decision_<layer_lower>_<domain>.md — NN 由硬编码字母序索引+偏移推得。"""
    if layer_id == _L2A_DOMAIN_LAYER:
        idx = _L2A_DOMAINS_ALPHA.index(domain)
        seq = _L2A_SEQ_OFFSET + idx
    elif layer_id == _L3_DOMAIN_LAYER:
        idx = _L3_DOMAINS_ALPHA.index(domain)
        seq = _L3_SEQ_OFFSET + idx
    else:
        raise ValueError(f"未知 layer_id {layer_id}，仅支持 L2A/L3")
    return f"{seq:02d}_decision_{layer_id.lower()}_{domain}.md"


def _build_domain_index(tracks: list[dict], layers: list[dict], nodes: list[dict]) -> list[dict]:
    """构建 14 个功能域索引（L2A 7 + L3 7）。

    返回 [{track, layer_id, domain, node_count, filename, seq}]，按 seq 升序。
    空域（node_count=0）仍保留以稳定编号。
    """
    track_by_id = {t["id"]: t for t in tracks}
    layer_track = {l["id"]: l["track"] for l in layers}
    index: list[dict] = []
    for domain in _L2A_DOMAINS_ALPHA:
        layer_id = _L2A_DOMAIN_LAYER
        domain_nodes = [n for n in nodes if n["layer_id"] == layer_id and _node_domain(n.get("path", "")) == domain]
        fname = _domain_filename(layer_id, domain)
        seq = _L2A_SEQ_OFFSET + _L2A_DOMAINS_ALPHA.index(domain)
        tid = layer_track.get(layer_id, "")
        index.append({
            "track": track_by_id.get(tid, {"id": tid, "name": tid, "name_en": tid}),
            "layer_id": layer_id, "domain": domain,
            "node_count": len(domain_nodes), "filename": fname, "seq": seq,
        })
    for domain in _L3_DOMAINS_ALPHA:
        layer_id = _L3_DOMAIN_LAYER
        domain_nodes = [n for n in nodes if n["layer_id"] == layer_id and _node_domain(n.get("path", "")) == domain]
        fname = _domain_filename(layer_id, domain)
        seq = _L3_SEQ_OFFSET + _L3_DOMAINS_ALPHA.index(domain)
        tid = layer_track.get(layer_id, "")
        index.append({
            "track": track_by_id.get(tid, {"id": tid, "name": tid, "name_en": tid}),
            "layer_id": layer_id, "domain": domain,
            "node_count": len(domain_nodes), "filename": fname, "seq": seq,
        })
    return index


def _aggregate_cross_domain_edges(
    nodes: list[dict], edges: list[dict], self_domain: str,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """聚合跨域边：返回 (outgoing_agg, incoming_agg, outgoing_detail, incoming_detail)。

    - agg: [{other_domain, count, types:set}]
    - detail: [{from_path, to_path, type, condition}]
    域 = node['path'] 第 2 段；path 不足 2 段的节点跳过并 stderr 警告。
    """
    node_id_to_domain: dict[int, str] = {}
    for n in nodes:
        d = _node_domain(n.get("path", ""))
        if not d:
            print(f"[WARN] 节点 {n.get('id')} path 残缺（{n.get('path')!r}），跳过跨域边聚合", file=sys.stderr)
            continue
        node_id_to_domain[n["id"]] = d

    outgoing_agg_map: dict[str, dict] = {}
    incoming_agg_map: dict[str, dict] = {}
    outgoing_detail: list[dict] = []
    incoming_detail: list[dict] = []

    for e in edges:
        from_d = node_id_to_domain.get(e["from"])
        to_d = node_id_to_domain.get(e["to"])
        if from_d is None or to_d is None:
            continue
        if from_d == self_domain and to_d != self_domain:
            entry = outgoing_agg_map.setdefault(to_d, {"other_domain": to_d, "count": 0, "types": set()})
            entry["count"] += 1
            entry["types"].add(e["type"])
            outgoing_detail.append({"from_path": _node_path(nodes, e["from"]), "to_path": _node_path(nodes, e["to"]), "type": e["type"], "condition": e.get("condition")})
        elif to_d == self_domain and from_d != self_domain:
            entry = incoming_agg_map.setdefault(from_d, {"other_domain": from_d, "count": 0, "types": set()})
            entry["count"] += 1
            entry["types"].add(e["type"])
            incoming_detail.append({"from_path": _node_path(nodes, e["from"]), "to_path": _node_path(nodes, e["to"]), "type": e["type"], "condition": e.get("condition")})

    outgoing_agg = [{"other_domain": v["other_domain"], "count": v["count"], "types": sorted(v["types"])} for v in outgoing_agg_map.values()]
    incoming_agg = [{"other_domain": v["other_domain"], "count": v["count"], "types": sorted(v["types"])} for v in incoming_agg_map.values()]
    return outgoing_agg, incoming_agg, outgoing_detail, incoming_detail


def _node_path(nodes: list[dict], node_id: int) -> str:
    """查 node_id → path（跨域边表格用）。"""
    for n in nodes:
        if n["id"] == node_id:
            return n.get("path", "")
    return ""


def _gen_cross_domain_mermaid(
    self_domain: str, outgoing_agg: list[dict], incoming_agg: list[dict],
) -> str:
    """跨域依赖图：graph LR，本域居中，外部域为外围节点，边标计数。

    参照 generate_domain_doc.py L544-598 改写（决策边只有单个 type 字段）。
    不使用 subgraph——subgraph 内节点使用 secondaryColor 而非 primaryColor，
    导致 %%{init}%% 设的 primaryColor 不生效（节点白色）。扁平布局保证灰色。
    """
    lines = [_MERMAID_INIT, "flowchart LR"]
    safe_self = self_domain.replace("-", "_")
    _self_zh = _DOMAIN_NAME_ZH.get(self_domain, self_domain)
    lines.append(f'    SELF["{self_domain}（{_self_zh}）"]')
    seen: set[str] = set()
    for d in outgoing_agg:
        other = d["other_domain"]
        safe = other.replace("-", "_")
        if other not in seen:
            _other_zh = _DOMAIN_NAME_ZH.get(other, other)
            lines.append(f'    EXT_{safe}["{other}（{_other_zh}）"]')
            seen.add(other)
        lines.append(f'    SELF -->|出 {d["count"]}| EXT_{safe}')
    for d in incoming_agg:
        other = d["other_domain"]
        safe = other.replace("-", "_")
        if other not in seen:
            _other_zh = _DOMAIN_NAME_ZH.get(other, other)
            lines.append(f'    EXT_{safe}["{other}（{_other_zh}）"]')
            seen.add(other)
        lines.append(f'    EXT_{safe} -->|入 {d["count"]}| SELF')
    return "\n".join(lines) + "\n"


def _atomic_write(path: Path, content: str) -> None:
    """原子写入文件（tmp + os.replace）。本地复制自 generate_domain_doc.py L1016-1028，避免跨模块耦合。"""
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


def _assert_domain_set_stable(layers: list[dict], nodes: list[dict]) -> None:
    """断言 DB 派生的 L2A/L3 域集合 == 硬编码列表（防 schema drift）。

    不匹配则 exit 3 并打印可操作信息。空 DB（无节点）时跳过断言（允许空库生成空文件）。
    """
    if not nodes:
        return
    l2a_layer = next((l for l in layers if l["id"] == _L2A_DOMAIN_LAYER), None)
    l3_layer = next((l for l in layers if l["id"] == _L3_DOMAIN_LAYER), None)
    db_l2a = {d for d in (_node_domain(n.get("path", "")) for n in nodes if n["layer_id"] == _L2A_DOMAIN_LAYER) if d} if l2a_layer else set()
    db_l3 = {d for d in (_node_domain(n.get("path", "")) for n in nodes if n["layer_id"] == _L3_DOMAIN_LAYER) if d} if l3_layer else set()
    expected_l2a = set(_L2A_DOMAINS_ALPHA)
    expected_l3 = set(_L3_DOMAINS_ALPHA)
    drift_l2a = db_l2a - expected_l2a
    drift_l3 = db_l3 - expected_l3
    if drift_l2a or drift_l3:
        msg = (
            f"[ERROR] decisiongraph 域集合漂移（schema drift）。\n"
            f"  L2A 新增域（未在 _L2A_DOMAINS_ALPHA）: {sorted(drift_l2a)}\n"
            f"  L3 新增域（未在 _L3_DOMAINS_ALPHA）: {sorted(drift_l3)}\n"
            f"  请更新 generate_decision_diagram.py 的 _L2A_DOMAINS_ALPHA / _L3_DOMAINS_ALPHA 后重跑。"
        )
        print(msg, file=sys.stderr)
        sys.exit(3)


# ---------------------------------------------------------------------------
# 文件构建函数
# ---------------------------------------------------------------------------


def _md_header(title: str, breadcrumb: str) -> list[str]:
    """统一的文件头部（标题 + 真源 + 生成时间）。"""
    return [
        f"# {title}",
        "",
        f"> 生成时间: {_git_commit_timestamp()}",
        f"> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）",
        f"> 数据库: {DB_DISPLAY_NAME}",
        f"> 导航: [返回主索引 decision_index.md](decision_index.md) | {breadcrumb}",
        "",
    ]


def _layer_table(layers: list[dict]) -> list[str]:
    """Layer 清单表（Markdown 行列表）。"""
    lines = [
        "| layer_id | 名称 | 英文名 | 所属轨 | 蓝图(module_id) | 蓝图名(派生) | 代码引用 | 功能简述 | 决策频率 | 成熟度 | build_status |",
        "|----------|------|--------|--------|-----------------|--------------|----------|----------|----------|--------|--------------|",
    ]
    for l in layers:
        mid = l.get("module_id") or "-"
        bp_name = l.get("blueprint_name") or "-"
        scr = l.get("source_code_ref") or "-"
        desc = (l.get("desc") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| {l['id']} | {l['name']} | {l['name_en']} | {l['track']} | "
            f"{mid} | {bp_name} | {scr} | {desc} | "
            f"{l['freq'] or '-'} | {l['maturity']} | {l['build']} |"
        )
    return lines


def _node_table(nodes: list[dict]) -> list[str]:
    """Node 清单表。"""
    if not nodes:
        return ["> （无节点）"]
    lines = [
        "| node_id | layer | type | name | path | module_id | 代码引用 | 成熟度 | build_status |",
        "|---------|-------|------|------|------|-----------|----------|--------|--------------|",
    ]
    for n in nodes:
        nscr = n.get("source_code_ref") or "-"
        lines.append(
            f"| {n['id']} | {n['layer_id']} | {n['type']} | {n['name']} | "
            f"{n['path']} | {n['module_id'] or '-'} | {nscr} | {n.get('maturity') or '-'} | {n['build']} |"
        )
    return lines


def _edge_table(edges: list[dict]) -> list[str]:
    """Edge 清单表。"""
    if not edges:
        return ["> （无决策因果边）"]
    lines = [
        "| edge_id | from | to | type | condition | track |",
        "|---------|-------|-----|------|-----------|-------|",
    ]
    for e in edges:
        lines.append(
            f"| {e['id']} | {e['from']} | {e['to']} | {e['type']} | "
            f"{e['condition'] or '-'} | {e['track'] or '-'} |"
        )
    return lines


def _filter_track_data(
    tid: str, layers: list[dict], nodes: list[dict], edges: list[dict],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """过滤本轨的 Layer/Node/Edge + 跨轨边（Extract Method 降低 _gen_track_file_md 复杂度）。"""
    track_layers = [l for l in layers if l["track"] == tid]
    track_layer_ids = {l["id"] for l in track_layers}
    track_nodes = [n for n in nodes if n["layer_id"] in track_layer_ids]
    track_node_ids = {n["id"] for n in track_nodes}
    track_edges = [e for e in edges if e["from"] in track_node_ids and e["to"] in track_node_ids]
    cross_track_edges = [e for e in edges if (e["from"] in track_node_ids) ^ (e["to"] in track_node_ids)]
    return track_layers, track_nodes, track_edges, cross_track_edges


def _gen_track_views_section(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict], tid: str,
) -> list[str]:
    """生成 Layer 骨架图 + 统计表（概览模式，不画决策节点；Extract Method 降低复杂度）。

    Track 文件改为「概览+导航」角色：仅画 Layer 节点 + 层间边，决策节点详情在各
    功能域文件（L2A/L3）中查看。避免 model_driven 等大轨重复展示数百节点导致文件过长。

    无决策节点的 track（如 placeholder/human_override/emergency）不画骨架图——
    骨架图是为决策节点提供 Layer 上下文，无节点时画图无意义（placeholder 轨有 645 个
    占位 Layer 但 0 决策节点，画图会产生无用的巨型 mermaid）。
    """
    track_layers, track_nodes, track_edges, cross_track_edges = _filter_track_data(tid, layers, nodes, edges)

    lines = [
        "## 统计", "",
        "| Layer 数 | 决策节点数 | 域内边数 | 跨轨边数 |",
        "|----------|-----------|----------|----------|",
        f"| {len(track_layers)} | {len(track_nodes)} | {len(track_edges)} | {len(cross_track_edges)} |",
        "",
        "## Layer 骨架图",
        "",
    ]

    if not track_nodes:
        # 无决策节点的 track 不画骨架图（骨架图是为决策节点提供上下文，无节点时无意义）
        lines += ["> 本轨无决策节点，骨架图省略。Layer 清单见下方表格。", ""]
    else:
        # Layer 骨架图（仅 Layer 节点 + 层间边，跳过决策节点）
        skeleton_mmd, _, _, _ = _gen_overview_mmd(
            tracks, layers, nodes, edges, track_id=tid, skeleton_only=True
        )
        lines += [
            "> 仅展示 Layer 节点与层间流向；决策节点详情见下方「功能域文件」链接。",
            "",
            "```mermaid", skeleton_mmd.rstrip("\n"), "```", "",
        ]
    return lines


def _gen_track_file_md(
    track: dict, tracks: list[dict], layers: list[dict],
    nodes: list[dict], edges: list[dict],
    domain_index: list[dict],
) -> str:
    """Per-Track 文件：Layer 骨架图 + 统计 + 功能域链接 + Layer 清单 + 跨轨边（概览+导航模式）。

    决策节点详情不在此文件展示（避免大轨数百节点导致文件过长），改由各功能域文件
    （L2A/L3）承载。Track 文件聚焦：骨架概览 + 功能域导航 + Layer/跨轨边清单。
    """
    tid = track["id"]
    track_layers, track_nodes, track_edges, cross_track_edges = _filter_track_data(tid, layers, nodes, edges)

    lines = _md_header(
        f"决策流图 · {track['name']}（{track['name_en']}）",
        f"Track {track.get('priority', '-')}",
    )
    lines += [
        f"**track_id**: `{tid}` | **优先级**: {track.get('priority', '-')} | **激活条件**: {track.get('activation') or '-'}",
        "",
        track.get("desc") or "",
        "",
    ]
    lines += _gen_track_views_section(tracks, layers, nodes, edges, tid)

    # 功能域文件链接（突出导航作用，紧跟骨架图之后）
    track_domains = [d for d in domain_index if d["track"]["id"] == tid]
    if track_domains:
        lines += ["## 功能域文件（L2A/L3 拆分）", ""]
        lines += ["| 序号 | 层 | 功能域 | Node 数 | 文档 |", "|------|------|--------|---------|------|"]
        for d in track_domains:
            lines.append(f"| {d['seq']:02d} | {d['layer_id']} | {d['domain']} | {d['node_count']} | [📄 {d['filename']}]({d['filename']}) |")
        lines += [""]
    else:
        lines += ["## 功能域文件（L2A/L3 拆分）", "", "> （本轨无功能域文件——决策节点未按域拆分）", ""]

    lines += ["## Layer 清单", ""] + _layer_table(track_layers) + [""]

    lines += ["## 跨轨边", ""]
    if cross_track_edges:
        lines += [
            "| edge_id | from | to | type | condition |",
            "|---------|-------|-----|------|-----------|",
        ]
        for e in cross_track_edges:
            lines.append(f"| {e['id']} | {e['from']} | {e['to']} | {e['type']} | {e['condition'] or '-'} |")
    else:
        lines += ["> （无跨轨边）"]
    lines += [""]

    return "\n".join(lines) + "\n"


def _gen_domain_file_md(
    track: dict, layer_id: str, domain: str,
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
) -> str:
    """Per-domain 文件：1 设计态 mermaid + 本域 Node 表 + 出/入边表 + 跨域 mermaid。"""
    domain_nodes = [n for n in nodes if n["layer_id"] == layer_id and _node_domain(n.get("path", "")) == domain]
    domain_node_ids = {n["id"] for n in domain_nodes}
    domain_edges = [e for e in edges if e["from"] in domain_node_ids and e["to"] in domain_node_ids]
    outgoing_agg, incoming_agg, outgoing_detail, incoming_detail = _aggregate_cross_domain_edges(nodes, edges, domain)

    mmd, _, l_count, e_count = _gen_overview_mmd(
        tracks, layers, nodes, edges,
        design_only=True, track_id=track["id"], path_prefix=domain,
    )

    _domain_zh = _DOMAIN_NAME_ZH.get(domain, domain)
    lines = _md_header(
        f"Decision Flow · {layer_id} Functional Domain {domain}（{_domain_zh}）",
        f"{track['name']} → {layer_id} → {domain}",
    )
    lines += [
        f"**所属轨**: {track['name']}（`{track['id']}`） | **所属层**: {layer_id} | **功能域**: `{domain}`（{_domain_zh}）",
        "",
        "## 统计",
        "",
        f"- 设计态节点数: {len(domain_nodes)}",
        f"- 域内边数: {len(domain_edges)}",
        f"- 跨域出边: {sum(d['count'] for d in outgoing_agg)}（{len(outgoing_agg)} 个外部域）",
        f"- 跨域入边: {sum(d['count'] for d in incoming_agg)}（{len(incoming_agg)} 个外部域）",
        "",
        "## 设计态全景图",
        "",
        f"> 共 {l_count} 层，{e_count} 边。",
        "",
        "```mermaid",
        mmd.rstrip("\n"),
        "```",
        "",
        "## Node 清单",
        "",
    ]
    lines += _node_table(domain_nodes) + [""]
    lines += ["## Edge 清单（域内）", ""] + _edge_table(domain_edges) + [""]

    # 跨域出边
    lines += ["## 跨域出边（Depends On）", ""]
    if outgoing_detail:
        lines += ["| # | 本域节点 | → | 外部域-目标节点 | type |", "|:--:|---------|:--:|---------|---------|"]
        for i, d in enumerate(outgoing_detail, 1):
            lines.append(f"| {i} | {d['from_path']} | → | {d['to_path']} | {d['type']} |")
    else:
        lines += ["> （无跨域出边）"]
    lines += [""]

    # 跨域入边
    lines += ["## 跨域入边（Depended By）", ""]
    if incoming_detail:
        lines += ["| # | 外部域-源节点 | → | 本域节点 | type |", "|:--:|---------|:--:|---------|---------|"]
        for i, d in enumerate(incoming_detail, 1):
            lines.append(f"| {i} | {d['from_path']} | → | {d['to_path']} | {d['type']} |")
    else:
        lines += ["> （无跨域入边）"]
    lines += [""]

    # 跨域 mermaid
    lines += ["## 跨域依赖图（Cross-Domain Dependency Graph）", ""]
    if outgoing_agg or incoming_agg:
        _ext_count = len(outgoing_agg) + len(incoming_agg)
        lines += [
            f"> 本域与 {_ext_count} 个外部域直接连接 / This domain directly connects to {_ext_count} external domain(s).",
            "",
            "```mermaid",
            _gen_cross_domain_mermaid(domain, outgoing_agg, incoming_agg).rstrip("\n"),
            "```",
        ]
    else:
        lines += ["> （无跨域依赖）"]
    lines += [""]

    return "\n".join(lines) + "\n"


def _gen_layers_file_md(tracks: list[dict], layers: list[dict]) -> str:
    """层级详情图独立文件。"""
    mmd = _gen_layers_mmd(tracks, layers)
    lines = _md_header("决策流图 · 层级详情图", "辅助图")
    lines += [
        "L0-L6 层级卡片 + 频率/成熟度/状态 + 流向箭头 + 学习闭环反馈边。",
        "",
        "```mermaid",
        mmd.rstrip("\n"),
        "```",
        "",
    ]
    return "\n".join(lines) + "\n"


def _gen_invariants_file_md(invariants: list[dict]) -> str:
    """不变量图独立文件。"""
    mmd = _gen_invariants_mmd(invariants)
    lines = _md_header("决策流图 · 不变量图", "辅助图")
    lines += [
        "6 节点类型 + 5 承重墙不变量 + 合法/非法连接标注。",
        "",
        "```mermaid",
        mmd.rstrip("\n"),
        "```",
        "",
    ]
    return "\n".join(lines) + "\n"


def _gen_index_md(
    tracks: list[dict],
    layers: list[dict],
    nodes: list[dict],
    edges: list[dict],
    invariants: list[dict] | None = None,
    domain_index: list[dict] | None = None,
) -> str:
    """生成主索引（纯导航，0 个 mermaid）。

    保留概述 + 统计 + Track/L2A/L3 导航表 + 辅助图链接 + 旧锚点重定向。
    """
    invariants = invariants or []
    domain_index = domain_index or []

    prod_layers = [l for l in layers if l.get("maturity") == "production"]
    design_layers = [l for l in layers if l.get("maturity") == "design"]
    prod_nodes = [n for n in nodes if n.get("maturity") == "production"]
    design_nodes = [n for n in nodes if n.get("maturity") == "design"]

    lines = [
        "# 决策流图（decisiongraph）索引",
        "",
        f"> 生成时间: {_git_commit_timestamp()}",
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
        "> 本索引为纯导航枢纽。各 Track / 功能域 / 辅助图分别独立成文件，避免单文件过大无法阅读。",
        "",
        "## 统计",
        "",
        "| 类型 | 数量 |",
        "|------|------|",
        f"| Track（轨） | {len(tracks)} |",
        f"| Layer（层） | {len(layers)} |",
        f"| Node（节点） | {len(nodes)} |",
        f"| Edge（边） | {len(edges)} |",
        f"| 运营态 Layer（design_maturity=production） | {len(prod_layers)} |",
        f"| 设计态 Layer（design_maturity=design） | {len(design_layers)} |",
        f"| 运营态 Node（design_maturity=production） | {len(prod_nodes)} |",
        f"| 设计态 Node（design_maturity=design） | {len(design_nodes)} |",
        "",
        "> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。对标 depgraph 的设计态/运营态机制。",
        "",
        "## Track 导航（按优先级）",
        "",
        "| 序号 | track_id | 名称 | 优先级 | Layer 数 | Node 数 | [📄 文档](.) |",
        "|------|----------|------|--------|----------|---------|------|",
    ]
    for t in tracks:
        t_layers = [l for l in layers if l["track"] == t["id"]]
        t_layer_ids = {l["id"] for l in t_layers}
        t_nodes = [n for n in nodes if n["layer_id"] in t_layer_ids]
        fname = _track_filename(t)
        lines.append(
            f"| {t.get('priority', 0):02d} | {t['id']} | {t['name']} | {t.get('priority', '-')} | "
            f"{len(t_layers)} | {len(t_nodes)} | [📄 {fname}]({fname}) |"
        )

    # L2A 域导航
    l2a_entries = [d for d in domain_index if d["layer_id"] == _L2A_DOMAIN_LAYER]
    lines += [
        "",
        f"## L2A 信号层 · 功能域导航（{len(l2a_entries)} 域）",
        "",
        "| 序号 | 功能域 | Node 数 | [📄 文档](.) |",
        "|------|--------|---------|------|",
    ]
    for d in l2a_entries:
        lines.append(f"| {d['seq']:02d} | {d['domain']} | {d['node_count']} | [📄 {d['filename']}]({d['filename']}) |")

    # L3 域导航
    l3_entries = [d for d in domain_index if d["layer_id"] == _L3_DOMAIN_LAYER]
    lines += [
        "",
        f"## L3 策略组合层 · 功能域导航（{len(l3_entries)} 域）",
        "",
        "| 序号 | 功能域 | Node 数 | [📄 文档](.) |",
        "|------|--------|---------|------|",
    ]
    for d in l3_entries:
        lines.append(f"| {d['seq']:02d} | {d['domain']} | {d['node_count']} | [📄 {d['filename']}]({d['filename']}) |")

    # 辅助图
    lines += [
        "",
        "## 辅助图",
        "",
        f"- [📄 {_LAYERS_FILE_NAME}]({_LAYERS_FILE_NAME}) — 层级详情图（L0-L6 卡片 + 流向）",
        f"- [📄 {_INVARIANTS_FILE_NAME}]({_INVARIANTS_FILE_NAME}) — 不变量图（6 节点类型 + 5 承重墙不变量）",
        "",
        "## 旧锚点重定向",
        "",
        "原单文件 `decision_index.md` 的各 section 已拆分到对应文件，外部 wiki 链接请按下方映射更新：",
        "",
        "- `#全景图` / `#运营态全景图` / `#设计态全景图` → 见各 [Track 文件](#track-导航按优先级)",
        "- `#层级详情图` → [20_decision_layers.md](20_decision_layers.md)",
        "- `#不变量图` → [21_decision_invariants.md](21_decision_invariants.md)",
        "- `#track-清单` → 上方 Track 导航表",
        "- `#layer-清单` → 各 Track 文件内的 Layer 清单 section",
        "- `#node-清单` → 各 Track / 功能域文件内的 Node 清单 section",
        "- `#edge-清单` → 各 Track 文件内的 Edge 清单 section",
        "",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="从 decisiongraph (PostgreSQL) 生成决策流图（Mermaid + Markdown，22 文件）",
    )
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    args = parser.parse_args()

    try:
        conn = get_decisiongraph_pg_connection()
    except Exception as e:
        print(f"[ERROR] decisiongraph 连接失败: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    try:
        tracks, layers, nodes, edges = _fetch_decision_data(conn)
        bp_map = _resolve_blueprint_names(conn, layers)
        for l in layers:
            mid = l.get("module_id")
            if mid and mid in bp_map:
                l["blueprint_name"] = bp_map[mid]
    finally:
        conn.close()

    if not tracks and not layers:
        print("[WARN] decisiongraph 表为空，请先运行 generate_decision_graph.py 同步 decision_graph_model.yaml")
        return EXIT_ERROR
    invariants = _load_invariants()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 写文件前断言域集合稳定（失败 exit 3，不留半成品）
    _assert_domain_set_stable(layers, nodes)

    domain_index = _build_domain_index(tracks, layers, nodes)
    expected_basenames: set[str] = set()

    # 1. 主索引（纯导航）
    index_md = _gen_index_md(tracks, layers, nodes, edges, invariants, domain_index)
    _atomic_write(out_dir / "decision_index.md", index_md)

    # 2. Per-Track 文件（01-05）
    for track in tracks:
        fname = _track_filename(track)
        expected_basenames.add(fname)
        _atomic_write(out_dir / fname, _gen_track_file_md(track, tracks, layers, nodes, edges, domain_index))

    # 3. Per-domain 文件（06-19）
    for entry in domain_index:
        expected_basenames.add(entry["filename"])
        _atomic_write(
            out_dir / entry["filename"],
            _gen_domain_file_md(
                entry["track"], entry["layer_id"], entry["domain"],
                tracks, layers, nodes, edges,
            ),
        )

    # 4. 辅助图（20, 21）
    _atomic_write(out_dir / _LAYERS_FILE_NAME, _gen_layers_file_md(tracks, layers))
    _atomic_write(out_dir / _INVARIANTS_FILE_NAME, _gen_invariants_file_md(invariants))
    expected_basenames.add(_LAYERS_FILE_NAME)
    expected_basenames.add(_INVARIANTS_FILE_NAME)

    # 5. 清理陈旧文件
    deleted = cleanup_stale_files(out_dir, expected_basenames, _STALE_FILE_REGEX)
    if deleted:
        print(f"[CLEANUP] 删除 {len(deleted)} 个残留文件: {deleted}")

    total_files = len(expected_basenames) + 1  # +1 for decision_index.md
    print(
        f"[OK] 生成 {total_files} 文件 (1 index + {len(tracks)} tracks + "
        f"{len(domain_index)} domains + 2 aux) 到 {out_dir}"
    )
    return EXIT_PASS


# ── Stage 4 公共 API 别名（for testing, thin wrappers） ──
# 模块级私有函数/常量的公共别名，消除测试对 _mod._xxx 的私有访问。
build_status_color = _build_status_color
load_invariants = _load_invariants
gen_overview_mmd = _gen_overview_mmd
gen_layers_mmd = _gen_layers_mmd
gen_invariants_mmd = _gen_invariants_mmd
gen_index_md = _gen_index_md
resolve_blueprint_names = _resolve_blueprint_names
truncate = _truncate
maturity_tag = _maturity_tag
filter_overview_inputs = _filter_overview_inputs
gen_track_file_md = _gen_track_file_md
gen_domain_file_md = _gen_domain_file_md
gen_layers_file_md = _gen_layers_file_md
gen_invariants_file_md = _gen_invariants_file_md
track_filename = _track_filename
domain_filename = _domain_filename
build_domain_index = _build_domain_index
node_domain = _node_domain
fetch_decision_data = _fetch_decision_data
STALE_FILE_REGEX = _STALE_FILE_REGEX
YAML_PATH = _YAML_PATH

if __name__ == "__main__":
    sys.exit(main())
