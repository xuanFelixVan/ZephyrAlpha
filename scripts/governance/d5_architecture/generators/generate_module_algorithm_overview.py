# [BLUEPRINT] MOD-GOV_GENERATE_ALGO_OVERVIEW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance.d5_architecture.generators.generate_module_algorithm_overview
# [DOMAIN]
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor; zephyr.governance.persistence.depgraph_reader; zephyr.governance.persistence.battle_map_reader; scripts.governance.d5_architecture.generators._common; scripts.governance.d5_architecture.generators.domain_name_mapping
# [CONSUMERS] 人工查看 docs/02_enterprise_architecture/08_algorithm_overview/index.md; reconciler 触发重生成
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出); 只读 depgraph+battle_map; 三档源优先级(code>blueprint>empty); 不改受治 reader(用公共API); 输出离库到 08_algorithm_overview/; 按作战环节拆分多文件(battle_map.anchors SSoT); 跨环节模块在各环节文件中重复出现
# [MODIFY-GUARD] 修改需同步更新 tests/governance/test_generate_module_algorithm_overview.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph不可用→exit 1; 单模块提取失败→降级empty不阻断; battle_map不可用→全部归未锚定
# [TESTS] tests/governance/test_generate_module_algorithm_overview.py
# [TTL] permanent
"""算法全景图生成器（按作战环节拆分，自动派生，离库）。

从代码 .py docstring + header（运营态）或 blueprint.md（设计态）提取每个模块的核心
算法描述，按 battle_map.anchors 锚点拆分到各作战环节文件（零漂移：环节→模块映射
从 battle_map 数据库自动派生），生成算法全景图，供"检修算法时一眼定位哪些模块算法
有问题/有冲突"。搜索"算法全景图"可命中全部 13 个文件。

输出结构（多文件）：
  index.md                      — 统计 + Mermaid 层级总览 + 按作战环节索引 + 质量报告
  stages/01~11_*.md             — 各作战环节的模块算法卡片（按 layer 二级分组）
  system_foundation.md          — 未锚定到作战环节的模块（基础设施/治理/安全类）

真源优先级（三档）：
  ① 运营态（code）：代表路径 .py 文件真实存在 → extract_algorithm_from_code
  ② 设计态（blueprint）：文件不存在但 blueprint.md 存在 → extract_algorithm_from_blueprint
  ③ 缺失（empty）：两者皆无 → 空摘要 + ❌ 标记

零漂移保障：
  ① HTML 锚点（<a id="mod-xxx">）定位，不依赖行号
  ② 环节→模块映射从 battle_map.anchors 表自动派生，不手写
  ③ 索引和卡片同一次生成器运行产出，不存在时间窗口漂移

[BLUEPRINT] MOD-GOV_GENERATE_ALGO_OVERVIEW | gov_scripts/blueprint.md
[MODULE] scripts.governance.d5_architecture.generators.generate_module_algorithm_overview
[INVARIANTS] 输出幂等; 只读depgraph+battle_map; 三档源优先级; 不改受治reader; 输出离库08; 按作战环节拆分(battle_map.anchors SSoT); 跨环节模块重复出现
[CONSUMERS] 人工查看08/index.md; reconciler触发重生成
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph不可用→exit1; battle_map不可用→全归未锚定; 单模块提取失败→降级empty
[DOMAIN] D_GOVERNANCE

使用方式：
    python scripts/governance/d5_architecture/generators/generate_module_algorithm_overview.py
输出：
    docs/02_enterprise_architecture/08_algorithm_overview/index.md
    docs/02_enterprise_architecture/08_algorithm_overview/stages/01_research_incubation.md
    ...（11 个环节文件）
    docs/02_enterprise_architecture/08_algorithm_overview/system_foundation.md
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
# generators 目录（_common.py / zoomable_html.py / domain_name_mapping.py 所在）
_GENERATORS_DIR = str(_THIS_FILE.parent)
if _GENERATORS_DIR not in sys.path:
    sys.path.insert(0, _GENERATORS_DIR)
# governance 目录（_shared/ 所在，code_algorithm_extractor.py / module_translation_loader.py）
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _common import DB_DISPLAY_NAME, idempotent_date, idempotent_timestamp  # noqa: E402
from zoomable_html import HTML_SUBDIR  # noqa: E402  — 仅用于清理旧 HTML 产物
from domain_name_mapping import get_domain_name_zh  # noqa: E402
from _shared.module_translation_loader import get_module_name_bilingual  # noqa: E402
from _shared.code_algorithm_extractor import (  # noqa: E402
    AlgorithmSummary,
    build_blueprint_index,
    extract_algorithm_from_blueprint,
    extract_algorithm_from_code,
)
from zephyr.governance.persistence.depgraph_reader import DepgraphReader  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

__manifest__ = f"""
args: []
description: 算法全景图：从代码docstring+blueprint派生模块算法，按battle_map作战环节拆分多文件，零漂移离库派生
dimensions:
- D5
priority: P2
timeout_seconds: 120
warn_only: false
"""

OUTPUT_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "08_algorithm_overview"
DOC_BASENAME = "module_algorithm_overview.md"

# layer 顺序与中文名（#ARCH-005 权威 4 层；从 layer_vocabulary.yaml SSoT 动态加载，零漂移）
import yaml as _yaml  # noqa: E402  # gate-vocab: 从 SSoT 动态加载 layer 值

_LAYER_VOCAB_PATH = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies" / "layer_vocabulary.yaml"
with open(_LAYER_VOCAB_PATH, encoding="utf-8") as _f:
    _layer_vocab = _yaml.safe_load(_f)
LAYER_ORDER = [v["value"] for v in _layer_vocab["values"]]
LAYER_NAME_ZH = {
    "L0_infrastructure": "基础设施层",
    "L1_foundation": "基础层",
    "L2_domain": "领域层",
    "L3_application": "应用层",
}
LAYER_EMOJI = {
    "L0_infrastructure": "🏗️",
    "L1_foundation": "🧱",
    "L2_domain": "⚙️",
    "L3_application": "🎯",
}

# 作战环节定义（sync 自 generate_battle_map_diagram.py FLOW_STAGES L100-112）
# 11 个环节（cross_cutting 无独立锚点，不参与文件拆分）
BATTLE_STAGES = [
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
STAGE_ID_TO_FILE = {sid: f"stages/{num}_{sid}.md" for sid, _, num in BATTLE_STAGES}
STAGE_ID_TO_NAME = {sid: zh for sid, zh, _ in BATTLE_STAGES}
STAGE_ORDER = [sid for sid, _, _ in BATTLE_STAGES]

# 三档状态徽章
STATUS_EMOJI = {"operational": "🟦", "design": "🟧", "missing": "⬜"}
STATUS_LABEL_ZH = {"operational": "运营态", "design": "设计态", "missing": "缺失"}
SOURCE_LABEL = {"operational": "code", "design": "blueprint", "missing": "empty"}

# build_status 成熟度聚合优先级（同模块多 path 取最成熟者展示）
_BUILD_STATUS_PRIORITY = {"stable": 5, "generated": 4, "built": 3, "planned": 2, "deprecated": 1}

# import 类依赖（depgraph 实际 dep_type 值，非 imports/calls——DB 实证）
_IMPORT_DEP_TYPES = ("import_depends", "import")

EXIT_ERROR = 1


# ── 数据获取（公共 API，零侵入受治 depgraph_reader）────────────


def load_modules_and_edges() -> tuple[list[dict], list[dict]]:
    """用 DepgraphReader 公共 API 加载模块与依赖边，Python 层做去重/过滤。

    等价于原方案 ``get_all_modules_for_overview``，但不修改受治的 depgraph_reader.py：
      - ``get_all_nodes()`` 取全部节点 → 过滤 node_type='module' 且 path 以 .py 结尾
        （排除 .md/dir 类 doc-module，无代码算法；未开发代码模块 path 仍是 .py）
      - 按 blueprint_id 去重（一个 MOD-xxx 常对应多 .py 路径），代表路径优先
        ``__init__.py``（extractor 会回退扫描子文件找最丰富 docstring），其次最短 path；
        blueprint_id 为空者按 path 单独成条
      - ``get_all_edges()`` 取全部边 → 过滤 dep_type ∈ {import_depends, import}，
        两端均为有 blueprint_id 的 module 节点，按 blueprint_id 聚合去重 + 排除自环

    :return: (modules, edges)；modules 每条含 module_id/path/build_status/domain_id/
             architecture_layer/blueprint_path；edges 每条含 from_module_id/to_module_id/dep_type。
    """
    reader = DepgraphReader()
    try:
        all_nodes = reader.get_all_nodes()
        all_edges = reader.get_all_edges()
    finally:
        reader.close()

    # ── 模块去重 ──
    module_nodes = [
        n for n in all_nodes
        if n.get("node_type") == "module" and (n.get("path") or "").endswith(".py")
    ]
    groups: dict[str, list[dict]] = defaultdict(list)
    for n in module_nodes:
        bp = (n.get("blueprint_id") or "").strip()
        key = bp if bp else f"__unmanaged__{n.get('path')}"
        groups[key].append(n)

    modules: list[dict] = []
    for key, nodes in groups.items():
        # 代表路径：优先 __init__.py，其次最短 path
        nodes.sort(key=lambda n: (
            0 if (n.get("path") or "").endswith("__init__.py") else 1,
            len(n.get("path") or ""),
        ))
        rep = {k: v for k, v in nodes[0].items()}
        rep["module_id"] = key
        rep["build_status"] = _aggregate_build_status([n.get("build_status") for n in nodes])
        # domain_id / architecture_layer 聚合：代表节点（常是 __init__.py）这两列可能为空，
        # 取组内首个非空值，避免纵览里域标注丢失（如同 MOD-REGIME-001 代表 __init__.py
        # 无 domain_id，但子文件 regime_detector.py 有 D_REGIME）。
        for field_name in ("domain_id", "architecture_layer"):
            if not (rep.get(field_name) or "").strip():
                for n in nodes:
                    v = (n.get(field_name) or "").strip()
                    if v:
                        rep[field_name] = v
                        break
        modules.append(rep)

    # ── 依赖边过滤（按 blueprint_id 聚合）──
    nid2bp: dict[str, str] = {}
    for n in all_nodes:
        if n.get("node_type") == "module":
            bp = (n.get("blueprint_id") or "").strip()
            if bp:
                nid2bp[str(n["node_id"])] = bp

    edges_set: set[tuple[str, str, str]] = set()
    for e in all_edges:
        if e.get("dep_type") not in _IMPORT_DEP_TYPES:
            continue
        fb = nid2bp.get(str(e.get("from_node_id")), "")
        tb = nid2bp.get(str(e.get("to_node_id")), "")
        if not fb or not tb or fb == tb:
            continue
        edges_set.add((fb, tb, e.get("dep_type")))

    edges = [
        {"from_module_id": f, "to_module_id": t, "dep_type": d}
        for f, t, d in edges_set
    ]
    return modules, edges


def _aggregate_build_status(statuses: list) -> str:
    """同模块多 path 的 build_status 取最成熟者（stable > generated > built > planned > deprecated）。"""
    if not statuses:
        return ""
    return max(statuses, key=lambda s: _BUILD_STATUS_PRIORITY.get(s or "", 0)) or ""


# ── 三档算法提取 ──────────────────────────────────────────────


def _empty_summary(module_id: str) -> AlgorithmSummary:
    """构造档③缺失摘要。"""
    return AlgorithmSummary(
        source_type="empty",
        module_id=module_id,
        quality_issue="无代码文件无蓝图，需补",
    )


def build_module_summaries(
    modules: list[dict],
    blueprint_index: dict,
) -> list[dict]:
    """对每个模块判定三档（修正点②：看文件是否真实存在）并提取算法摘要。

    :return: 每条含 module_id/path/tier/domain_id/layer/build_status/bp_ref/summary/bi_name。
    """
    rows: list[dict] = []
    for m in modules:
        mid = m["module_id"]
        path = m.get("path") or ""
        py_abs = (REPO_ROOT / path) if path and not Path(path).is_absolute() else Path(path)
        file_exists = bool(path) and py_abs.exists()

        bp_path = blueprint_index.get(mid) if not mid.startswith("__unmanaged__") else None
        bp_ref = ""
        if bp_path:
            try:
                bp_ref = str(bp_path.relative_to(REPO_ROOT)).replace("\\", "/")
            except ValueError:
                bp_ref = str(bp_path).replace("\\", "/")

        if file_exists:
            summary = extract_algorithm_from_code(py_abs, module_id=mid, blueprint_ref=bp_ref)
            tier = "operational"
        elif bp_path:
            summary = extract_algorithm_from_blueprint(bp_path, module_id=mid)
            tier = "design"
        else:
            summary = _empty_summary(mid)
            tier = "missing"

        bi_name = get_module_name_bilingual(path) if path else ""

        rows.append({
            "module_id": mid,
            "path": path,
            "tier": tier,
            "domain_id": m.get("domain_id") or "",
            "layer": m.get("architecture_layer") or "",
            "build_status": m.get("build_status") or "",
            "bp_ref": bp_ref,
            "summary": summary,
            "bi_name": bi_name,
        })
    return rows


# ── battle_map 锚点加载（零漂移：从 battle_map 数据库自动派生环节→模块映射）──


def load_battle_map_anchors() -> dict[str, set[str]]:
    """从 battle_map 数据库加载 模块→环节 映射。

    battle_map.anchors 表是 SSoT（哪个模块锚定到哪个作战环节），
    本函数只做投影，不手写映射——改 battle_map → 重跑生成器 → 索引自动对齐。

    :return: {module_id: {stage_id, ...}}；未锚定模块不在 dict 中。
             跨环节模块（出现在多个 stage）的 value 含多个 stage_id。
    """
    from zephyr.governance.persistence.battle_map_reader import BattleMapReader

    reader = BattleMapReader()
    try:
        all_anchors = reader.get_all_anchors()
        all_steps = reader.get_all_steps()
    finally:
        reader.close()

    # step_id → stage_id
    step_to_stage: dict[str, str] = {}
    for s in all_steps:
        sid = str(s.get("step_id") or "")
        stage = s.get("stage_id") or s.get("flow_stage") or ""
        if sid and stage:
            step_to_stage[sid] = stage

    # module_id → {stage_id, ...}
    mod_to_stages: dict[str, set[str]] = defaultdict(set)
    for a in all_anchors:
        tg = a.get("target_graph") or ""
        tid = str(a.get("target_id") or "")
        sid = str(a.get("step_id") or "")
        if tg == "depgraph" and tid.startswith("MOD-") and sid in step_to_stage:
            mod_to_stages[tid].add(step_to_stage[sid])

    return dict(mod_to_stages)


def classify_rows_by_stage(
    rows: list[dict],
    mod_to_stages: dict[str, set[str]],
) -> tuple[dict[str, list[dict]], list[dict]]:
    """将模块行按作战环节分类。

    :return: (anchored_by_stage, unanchored_rows)
      - anchored_by_stage: {stage_id: [rows]}（跨环节模块出现在多个 stage 中—— intentional，
        检修某环节时需看到该环节涉及的全部模块）
      - unanchored_rows: 未锚定到任何环节的模块行（基础设施/治理/安全类）
    """
    anchored_by_stage: dict[str, list[dict]] = defaultdict(list)
    unanchored_rows: list[dict] = []

    for r in rows:
        mid = r["module_id"]
        stages = mod_to_stages.get(mid)
        if stages:
            for stage_id in stages:
                anchored_by_stage[stage_id].append(r)
        else:
            unanchored_rows.append(r)

    return dict(anchored_by_stage), unanchored_rows


def build_module_to_file_map(
    anchored_by_stage: dict[str, list[dict]],
    unanchored_rows: list[dict],
) -> dict[str, str]:
    """构建 module_id → 文件相对路径 映射（供质量报告/索引链接）。

    跨环节模块链接到第一个（按 STAGE_ORDER）出现的环节文件。
    """
    module_to_file: dict[str, str] = {}
    for stage_id in STAGE_ORDER:
        stage_rows = anchored_by_stage.get(stage_id, [])
        file_rel = STAGE_ID_TO_FILE[stage_id]
        for r in stage_rows:
            if r["module_id"] not in module_to_file:
                module_to_file[r["module_id"]] = file_rel
    for r in unanchored_rows:
        module_to_file[r["module_id"]] = "system_foundation.md"
    return module_to_file


# ── 渲染 ──────────────────────────────────────────────────────


def _file_url(rel_path: str) -> str:
    """相对路径 → file:// URL（Windows 兼容，正斜杠）。"""
    return "file:///" + (REPO_ROOT / rel_path).as_posix()


def _blockquote(text: str) -> str:
    """多行文本每行加 > 前缀（用于详情卡片的算法步骤/概述）。"""
    if not text:
        return ""
    return "\n".join(f"> {ln}" if ln.strip() else ">" for ln in text.splitlines())


def _layer_sort_key(layer: str) -> tuple:
    """layer 排序键：L0→L3 在前，未知/空层置末。"""
    return (0, LAYER_ORDER.index(layer)) if layer in LAYER_ORDER else (1, layer)


def render_stats(rows: list[dict]) -> str:
    """文档基本信息表。"""
    total = len(rows)
    op = sum(1 for r in rows if r["tier"] == "operational")
    de = sum(1 for r in rows if r["tier"] == "design")
    mi = sum(1 for r in rows if r["tier"] == "missing")
    covered = sum(1 for r in rows if r["summary"].algo_steps)
    cov_pct = (covered / total * 100) if total else 0.0
    ts = idempotent_timestamp(_THIS_FILE)
    dt = idempotent_date(_THIS_FILE)
    return f"""## 文档基本信息

| 指标 | 值 |
|---|---|
| 模块总数 | {total} |
| 🟦 运营态（代码存在） | {op} |
| 🟧 设计态（仅蓝图） | {de} |
| ⬜ 缺失（无代码无蓝图） | {mi} |
| 算法覆盖率（有算法步骤） | {covered}/{total}（{cov_pct:.1f}%） |
| 生成时间（幂等·脚本最近 commit） | {ts} |
| 日期 | {dt} |
| 真源 | 代码 docstring + header ｜ blueprint.md §核心规则 ｜ {DB_DISPLAY_NAME} |
"""


def render_mermaid_layer_overview(rows: list[dict], edges: list[dict]) -> str:
    """层级总览 Mermaid：4 个 layer 节点（含模块数+三态计数）+ 层间依赖流。

    505 模块全画入 Mermaid 不可读，故层级聚合；逐模块状态见「算法质量报告」表。
    """
    lines = ["```mermaid", "flowchart TD"]
    for layer in LAYER_ORDER:
        lrows = [r for r in rows if r["layer"] == layer]
        if not lrows:
            continue
        cnt_op = sum(1 for r in lrows if r["tier"] == "operational")
        cnt_de = sum(1 for r in lrows if r["tier"] == "design")
        cnt_mi = sum(1 for r in lrows if r["tier"] == "missing")
        label = (
            f"{LAYER_EMOJI[layer]} {layer} {LAYER_NAME_ZH[layer]}\\n"
            f"{len(lrows)} 模块：🟦{cnt_op} 🟧{cnt_de} ⬜{cnt_mi}"
        )
        lines.append(f'  {layer}["{label}"]')

    # 层间依赖流（按 blueprint_id 边聚合到 layer 对）
    layer_of = {r["module_id"]: r["layer"] for r in rows}
    pair_cnt: Counter = Counter()
    for e in edges:
        fl = layer_of.get(e["from_module_id"], "")
        tl = layer_of.get(e["to_module_id"], "")
        if fl and tl and fl != tl and fl in LAYER_ORDER and tl in LAYER_ORDER:
            pair_cnt[(fl, tl)] += 1
    for (fl, tl), c in sorted(pair_cnt.items(), key=lambda x: -x[1]):
        lines.append(f"  {fl} -->|{c} 条依赖| {tl}")

    # 未分层模块提示
    unlayered = [r for r in rows if r["layer"] not in LAYER_ORDER]
    if unlayered:
        lines.append(f'  UNLAYERED["❓ 未分层 {len(unlayered)} 模块"]')

    lines.append("  classDef default fill:#eef,stroke:#336,stroke-width:1px,color:#003;")
    lines.append("```")
    return "\n".join(lines)


def _build_consumers(edges: list[dict]) -> dict[str, list[str]]:
    """被依赖图：to_module_id -> [from_module_id, ...]。"""
    consumers: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        consumers[e["to_module_id"]].append(e["from_module_id"])
    return dict(consumers)


def _render_cards_by_layer(
    rows: list[dict],
    consumers: dict[str, list[str]],
) -> str:
    """渲染模块卡片，按 layer（L0→L3）分组。

    用于环节文件和系统基础文件——两者内部都按 layer 二级分组。
    """
    parts: list[str] = []
    present_layers = [l for l in LAYER_ORDER if any(r["layer"] == l for r in rows)]
    has_unlayered = any(r["layer"] not in LAYER_ORDER for r in rows)

    for layer in present_layers:
        lrows = sorted(
            [r for r in rows if r["layer"] == layer],
            key=lambda r: r["module_id"],
        )
        parts.append(f"### {LAYER_EMOJI[layer]} {layer} — {LAYER_NAME_ZH[layer]}（{len(lrows)} 模块）")
        parts.append("")
        for r in lrows:
            parts.append(_render_module_card(r, consumers))

    if has_unlayered:
        urows = sorted(
            [r for r in rows if r["layer"] not in LAYER_ORDER],
            key=lambda r: r["module_id"],
        )
        parts.append(f"### ❓ 未分层（{len(urows)} 模块）")
        parts.append("")
        parts.append("> 这些模块的 architecture_layer 为空，未归入 L0–L3。建议在 depgraph 补 layer。")
        parts.append("")
        for r in urows:
            parts.append(_render_module_card(r, consumers))

    return "\n".join(parts)


def render_battle_stage_index(
    anchored_by_stage: dict[str, list[dict]],
    unanchored_rows: list[dict],
) -> str:
    """按作战环节索引（从 battle_map.anchors 自动派生，零漂移）。"""
    lines = [
        "## 按作战环节索引（自动派生自 battle_map 锚点）",
        "",
        "> 环节→模块映射从 `battle_map.anchors` 表自动派生，改 battle_map → 重跑生成器 → 本索引自动对齐。",
        "> 跨环节模块在每个所属环节文件中均出现（检修某环节时需看到该环节涉及的全部模块）。",
        "",
    ]

    for stage_id in STAGE_ORDER:
        stage_rows = anchored_by_stage.get(stage_id, [])
        if not stage_rows:
            continue
        zh = STAGE_ID_TO_NAME[stage_id]
        file_rel = STAGE_ID_TO_FILE[stage_id]
        # 统计三档
        op = sum(1 for r in stage_rows if r["tier"] == "operational")
        de = sum(1 for r in stage_rows if r["tier"] == "design")
        mi = sum(1 for r in stage_rows if r["tier"] == "missing")
        lines.append(
            f"- **{zh}**（{len(stage_rows)} 模块：🟦{op} 🟧{de} ⬜{mi}）"
            f" → [`{file_rel}`]({file_rel})"
        )

    if unanchored_rows:
        op = sum(1 for r in unanchored_rows if r["tier"] == "operational")
        de = sum(1 for r in unanchored_rows if r["tier"] == "design")
        mi = sum(1 for r in unanchored_rows if r["tier"] == "missing")
        lines.append("")
        lines.append(
            f"- **系统基础**（{len(unanchored_rows)} 模块：🟦{op} 🟧{de} ⬜{mi}，未锚定到作战环节）"
            f" → [`system_foundation.md`](system_foundation.md)"
        )

    return "\n".join(lines)


def render_quality_report(
    rows: list[dict],
    module_to_file: dict[str, str] | None = None,
) -> str:
    """算法质量报告表（逐模块，强制曝光缺口/低质量）。

    module_to_file: module_id → 文件相对路径（用于链接到对应环节/系统基础文件）。
    """
    lines = [
        "## 算法质量报告（强制曝光）",
        "",
        "按 layer → module_id 排序。⚠/❌ 行需优先补全。点击模块名跳转对应文件算法卡片。",
        "",
        "| 模块 | 状态 | 来源 | 域 | layer | build_status | 位置 | 质量问题 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    ordered = sorted(rows, key=lambda r: (_layer_sort_key(r["layer"]), r["module_id"]))
    for r in ordered:
        s = r["summary"]
        emoji = STATUS_EMOJI[r["tier"]]
        qi = (s.quality_issue or "").replace("|", "/").replace("\n", " ")
        # 位置链接
        if module_to_file and r["module_id"] in module_to_file:
            file_rel = module_to_file[r["module_id"]]
            anchor_id = r["module_id"].lower()
            location = f"[→]({file_rel}#{anchor_id})"
        else:
            location = "—"
        lines.append(
            f"| {r['module_id']} | {emoji}{STATUS_LABEL_ZH[r['tier']]} | "
            f"{SOURCE_LABEL[r['tier']]} | {r['domain_id']} | {r['layer'] or '—'} | "
            f"{r['build_status'] or '—'} | {location} | {qi} |"
        )
    return "\n".join(lines)


def _render_module_card(r: dict, consumers: dict[str, list[str]]) -> str:
    """单模块算法详情卡片。"""
    s: AlgorithmSummary = r["summary"]
    emoji = STATUS_EMOJI[r["tier"]]
    name = r["bi_name"] or s.module_name or r["module_id"]
    dom_id = r["domain_id"] or ""
    dom_zh = get_domain_name_zh(dom_id) if dom_id else ""
    dom_display = f"{dom_zh}（{dom_id}）" if (dom_zh and dom_zh != dom_id) else (dom_id or "—")
    layer_tag = f"[{r['layer']}·{dom_display}]" if r["layer"] else f"[{dom_display}]"

    # 稳定 HTML 锚点（module_id 小写），供 battle_map/域文档深链接跳转。
    # 不依赖 GitHub 自动锚点（标题含 emoji/中文/特殊字符，自动锚点脆弱）。
    anchor_id = r["module_id"].lower()
    out: list[str] = [f'<a id="{anchor_id}"></a>', f"#### {emoji} {r['module_id']} {name} {layer_tag}", ""]

    # 真源行
    src_parts = []
    if s.source_path:
        anchor = f"{s.source_path}:{s.source_line_range}" if s.source_line_range else s.source_path
        src_parts.append(f"[`{anchor}`]({_file_url(s.source_path)})")
    if r["bp_ref"]:
        src_parts.append(f"[蓝图 `{r['bp_ref']}`]({_file_url(r['bp_ref'])})")
    if src_parts:
        out.append(f"> **真源**：{' ｜ '.join(src_parts)}")
        out.append(">")

    if s.summary:
        out.append(f"> **概述**：{s.summary}")
        out.append(">")
    if s.algo_steps:
        out.append("> **算法步骤**：")
        out.append(_blockquote(s.algo_steps))
        out.append(">")
    if s.invariants:
        out.append(f"> **不变量**：{s.invariants}")
        out.append(">")

    cons = sorted(set(consumers.get(r["module_id"], [])))
    if cons:
        shown = ", ".join(cons[:10])
        more = f"（+{len(cons) - 10}）" if len(cons) > 10 else ""
        out.append(f"> **被依赖**（上层消费者，看影响面）：{shown}{more}")
        out.append(">")

    out.append(f"> **质量**：{s.quality_issue}")
    out.append("")
    return "\n".join(out)


def render_index_doc(
    rows: list[dict],
    edges: list[dict],
    anchored_by_stage: dict[str, list[dict]],
    unanchored_rows: list[dict],
    module_to_file: dict[str, str],
) -> str:
    """组装索引文档（入口文件 index.md）。

    索引不含算法卡片——卡片按作战环节拆分到 stages/ 和 system_foundation.md。
    索引含：统计 + Mermaid 层级总览 + 按作战环节索引 + 质量报告 + 冲突提示。
    """
    ts = idempotent_timestamp(_THIS_FILE)
    header = f"""# 算法全景图 — 索引（自动派生·离库·按作战环节拆分）

> **真源**：代码 docstring + header ｜ blueprint.md §核心规则 ｜ {DB_DISPLAY_NAME}（nodes/edges）。
> 改真源 → 重跑生成器 → 本文档自动更新（派生产物，不入 git，按需生成）。
> **重生成命令**：`python scripts/governance/d5_architecture/generators/generate_module_algorithm_overview.py`
> **生成时间**（幂等）：{ts}

> **三档状态**：🟦运营态（代码存在，以代码为准）｜🟧设计态（代码未落盘，以蓝图为准）｜⬜缺失（无代码无蓝图，需补）。
> **检修入口**：先看「按作战环节索引」定位环节 → 进入环节文件看算法卡片 → 沿「被依赖」看影响面。
> 也可先看「算法质量报告」表找 ⚠/❌ 模块 → 点击「位置」列跳转对应文件卡片。

> **文件结构**：
> - 本文件（`index.md`）：统计 + 层级总览 + 环节索引 + 质量报告
> - `stages/01~11_*.md`：各作战环节的模块算法卡片（按 layer 二级分组）
> - `system_foundation.md`：未锚定到作战环节的模块（基础设施/治理/安全类）

"""
    conflict_placeholder = """## 潜在冲突提示（P2，本次仅留框架）

> 跨模块算法语义矛盾检测（如两个模块对同一不变量给出冲突约束）留 P2。
> 本次纵览已把各模块算法并列展示，为后续语义比对奠定结构基础。
"""
    footer = f"""

---

> 本索引由 `scripts/governance/d5_architecture/generators/generate_module_algorithm_overview.py` 自动派生。
> 模块 {len(rows)} 个 ｜ 依赖边 {len(edges)} 条 ｜ 生成时间 {ts}（幂等）。
"""
    return (
        header
        + render_stats(rows)
        + "\n"
        + render_mermaid_layer_overview(rows, edges)
        + "\n\n"
        + render_battle_stage_index(anchored_by_stage, unanchored_rows)
        + "\n\n"
        + render_quality_report(rows, module_to_file)
        + "\n"
        + conflict_placeholder
        + footer
    )


def render_stage_doc(
    stage_id: str,
    stage_rows: list[dict],
    edges: list[dict],
    consumers: dict[str, list[str]],
) -> str:
    """组装单个作战环节文件（stages/XX_stage.md）。"""
    ts = idempotent_timestamp(_THIS_FILE)
    zh = STAGE_ID_TO_NAME[stage_id]
    file_rel = STAGE_ID_TO_FILE[stage_id]

    op = sum(1 for r in stage_rows if r["tier"] == "operational")
    de = sum(1 for r in stage_rows if r["tier"] == "design")
    mi = sum(1 for r in stage_rows if r["tier"] == "missing")

    header = f"""# 算法全景图 — 作战环节「{zh}」（{len(stage_rows)} 模块）

> [← 返回索引](../index.md)
> **真源**：代码 docstring + header ｜ blueprint.md §核心规则 ｜ {DB_DISPLAY_NAME}
> 自动派生，离库不入 git。改真源 → 重跑生成器 → 本文档自动更新。
> **生成时间**（幂等）：{ts}
> **三档**：🟦运营 {op} ｜ 🟧设计 {de} ｜ ⬜缺失 {mi}

"""
    body = _render_cards_by_layer(stage_rows, consumers)
    footer = f"""

---

> 环节 `{stage_id}`（{zh}）｜ {len(stage_rows)} 模块 ｜ 生成时间 {ts}（幂等）。
> 跨环节模块（同时属于多个环节）在本文件中重复出现——intentional，检修时需看到该环节涉及的全部模块。
"""
    return header + "## 算法详情\n\n" + body + footer


def render_system_foundation_doc(
    unanchored_rows: list[dict],
    edges: list[dict],
    consumers: dict[str, list[str]],
) -> str:
    """组装系统基础文件（system_foundation.md，未锚定模块）。"""
    ts = idempotent_timestamp(_THIS_FILE)

    op = sum(1 for r in unanchored_rows if r["tier"] == "operational")
    de = sum(1 for r in unanchored_rows if r["tier"] == "design")
    mi = sum(1 for r in unanchored_rows if r["tier"] == "missing")

    header = f"""# 算法全景图 — 系统基础（未锚定模块，{len(unanchored_rows)} 模块）

> [← 返回索引](index.md)
> **真源**：代码 docstring + header ｜ blueprint.md §核心规则 ｜ {DB_DISPLAY_NAME}
> 这些模块未锚定到任何作战环节（基础设施/治理/安全/数据类），按 architecture_layer（L0→L3）内部分组。
> 自动派生，离库不入 git。改真源 → 重跑生成器 → 本文档自动更新。
> **生成时间**（幂等）：{ts}
> **三档**：🟦运营 {op} ｜ 🟧设计 {de} ｜ ⬜缺失 {mi}

"""
    body = _render_cards_by_layer(unanchored_rows, consumers)
    footer = f"""

---

> 系统基础（未锚定模块）｜ {len(unanchored_rows)} 模块 ｜ 生成时间 {ts}（幂等）。
"""
    return header + "## 算法详情\n\n" + body + footer


# ── 写入 ──────────────────────────────────────────────────────


def _atomic_write(path: Path, content: str) -> None:
    """原子写入（tmp + os.replace，newline=\\n 保证跨平台一致）。"""
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


# ── CLI 入口 ──────────────────────────────────────────────────


def main() -> None:
    """入口：生成模块核心算法纵览（按作战环节拆分，多文件输出）。"""
    parser = argparse.ArgumentParser(
        description="模块核心算法纵览生成器：按作战环节拆分，三档源(code>blueprint>empty)派生"
    )
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stages_dir = out_dir / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)

    print("[1/5] 加载模块与依赖边（公共 API get_all_nodes/get_all_edges）...")
    modules, edges = load_modules_and_edges()
    print(f"      模块 {len(modules)} 条（按 blueprint_id 去重）｜模块间 import 边 {len(edges)} 条")

    print("[2/5] 构建 blueprint 索引（扫描 docs/03_modules/**/blueprint.md）...")
    blueprint_index = build_blueprint_index()
    print(f"      blueprint 索引 {len(blueprint_index)} 条")

    print("[3/5] 提取算法摘要（三档：code>blueprint>empty）...")
    rows = build_module_summaries(modules, blueprint_index)
    tier_cnt = Counter(r["tier"] for r in rows)
    print(
        f"      🟦运营 {tier_cnt.get('operational', 0)} ｜ "
        f"🟧设计 {tier_cnt.get('design', 0)} ｜ ⬜缺失 {tier_cnt.get('missing', 0)}"
    )

    print("[4/5] 加载 battle_map 锚点 + 按作战环节分类...")
    mod_to_stages = load_battle_map_anchors()
    anchored_by_stage, unanchored_rows = classify_rows_by_stage(rows, mod_to_stages)
    module_to_file = build_module_to_file_map(anchored_by_stage, unanchored_rows)
    anchored_total = sum(len(v) for v in anchored_by_stage.values())
    anchored_unique = len(mod_to_stages)
    cross_stage = sum(1 for m, s in mod_to_stages.items() if len(s) > 1)
    print(
        f"      锚定 {anchored_total} 模块实例（{anchored_unique} 去重模块）"
        f"｜未锚定 {len(unanchored_rows)} 模块｜跨环节 {cross_stage} 模块"
    )

    print("[5/5] 渲染多文件输出（index + 11 stages + system_foundation）...")
    consumers = _build_consumers(edges)
    written: list[tuple[str, int]] = []

    # index.md
    index_md = render_index_doc(rows, edges, anchored_by_stage, unanchored_rows, module_to_file)
    index_path = out_dir / "index.md"
    _atomic_write(index_path, index_md)
    written.append(("index.md", len(index_md)))

    # stages/XX_stage.md
    for stage_id in STAGE_ORDER:
        stage_rows = anchored_by_stage.get(stage_id, [])
        if not stage_rows:
            continue
        stage_md = render_stage_doc(stage_id, stage_rows, edges, consumers)
        stage_path = out_dir / STAGE_ID_TO_FILE[stage_id]
        _atomic_write(stage_path, stage_md)
        written.append((STAGE_ID_TO_FILE[stage_id], len(stage_md)))

    # system_foundation.md
    if unanchored_rows:
        sf_md = render_system_foundation_doc(unanchored_rows, edges, consumers)
        sf_path = out_dir / "system_foundation.md"
        _atomic_write(sf_path, sf_md)
        written.append(("system_foundation.md", len(sf_md)))

    # 清理旧的单文件产物（module_algorithm_overview.md）+ 过时 stages
    old_single = out_dir / DOC_BASENAME
    if old_single.exists():
        old_single.unlink()
        print(f"[CLEANUP] 删除旧单文件产物: {DOC_BASENAME}")
    old_html = out_dir / HTML_SUBDIR / DOC_BASENAME.replace(".md", ".html")
    if old_html.exists():
        old_html.unlink()
        print(f"[CLEANUP] 删除旧 HTML: {old_html.name}")

    # 清理过时 stages（不在当前 STAGE_ORDER 的文件）
    current_stage_files = {STAGE_ID_TO_FILE[s] for s in STAGE_ORDER}
    for f in sorted(stages_dir.iterdir()):
        rel = f"stages/{f.name}"
        if f.is_file() and rel not in current_stage_files:
            f.unlink()
            print(f"[CLEANUP] 删除过时环节文件: {rel}")

    print(f"\n[OK] 生成 {len(written)} 个文件：")
    for rel, size in written:
        print(f"  {rel:45s} {size:>8,} 字符")
    total_chars = sum(s for _, s in written)
    print(f"  {'合计':45s} {total_chars:>8,} 字符")


if __name__ == "__main__":
    main()
