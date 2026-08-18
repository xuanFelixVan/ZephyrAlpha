# [BLUEPRINT] MOD-GOV_GENERATE_ALGO_OVERVIEW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance.d5_architecture.generators.generate_module_algorithm_overview
# [DOMAIN]
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor; scripts.governance._shared.constants; zephyr.governance.persistence.depgraph_reader; zephyr.governance.persistence.battle_map_reader; scripts.governance.d5_architecture.generators._common; scripts.governance.d5_architecture.generators.domain_name_mapping
# [CONSUMERS] 人工查看 docs/02_enterprise_architecture/08_algorithm_overview/index.md; reconciler 触发重生成
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出); 只读 depgraph+battle_map; 三档源优先级(code>blueprint>empty); 不改受治 reader(用公共API); 输出离库到 08_algorithm_overview/; 按作战环节拆分多文件(battle_map.anchors SSoT); 跨环节模块在各环节文件中重复出现; ALGO_FLOW标记→Mermaid推导图(§4.16,无标记回退文字卡片,渐进式向后兼容); stages顶部环节总图+卡片下模块关联图(depgraph自动派生,§4.3节点+§4.15断点边)
# [MODIFY-GUARD] 修改需同步更新 tests/governance/test_generate_module_algorithm_overview.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph不可用→exit 1; 单模块提取失败→降级empty不阻断; battle_map不可用→全部归未锚定
# [TESTS] tests/governance/test_generate_module_algorithm_overview.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 生成器由 reconciler/人工按需显式触发（非 cron/daemon 常驻服务），对齐 generate_code_wiki_stats.py 豁免模式
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
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
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
from _shared.code_algorithm_extractor import (  # noqa: E402
    AlgoFlowData,
    AlgoFlowNode,
    AlgorithmSummary,
    build_blueprint_index,
    extract_algorithm_from_blueprint,
    extract_algorithm_from_code,
)
from _shared.constants import DOC_HTTP_BASE  # noqa: E402
from _shared.module_translation_loader import (  # noqa: E402
    derive_name_from_path,
    get_module_name_bilingual,
    get_module_plain,
)
from domain_name_mapping import get_domain_name_zh  # noqa: E402
from zoomable_html import HTML_SUBDIR, emit_zoomable_html  # noqa: E402

from zephyr.governance.persistence.depgraph_reader import DepgraphReader  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

# 治本（2026-08-18）：f-string manifest 生成器不识别（提取器仅认静态三引号 YAML），静态化。
__manifest__ = """
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

# 本地 HTTP 文档服务器基址（可缩放 HTML 跳转链接用）：
# IDE 预览面板对 file:/// 和相对路径链接会在编辑器内打开源码，仅 http:// 链接交给
# 外部浏览器渲染。需本地 http server（scripts/serve_docs_http.bat）。
# 真源：_shared.constants.DOC_HTTP_BASE（MOD-INF-005 SSoT，含 ZEPHYR_DOC_HTTP_BASE 环境变量覆盖），
# 6 个 D5 生成器统一引用，不再各自硬编码（治本 NO-HARDCODED-URL 存量）。
_DOC_HTTP_BASE = DOC_HTTP_BASE


def _zoomable_html_url(md_rel: str) -> str:
    """由 md 相对输出路径（如 ``stages/06_buy_flow.md``）派生可缩放 HTML 的 http 链接。

    HTML 由 emit_zoomable_html 联动生成，位于 md 同级 ``_zoomable_html/`` 子目录同名 .html。
    """
    p = Path(md_rel)
    html_abs = OUTPUT_DIR / p.parent / HTML_SUBDIR / f"{p.stem}.html"
    try:
        return f"{_DOC_HTTP_BASE}/{html_abs.relative_to(REPO_ROOT).as_posix()}"
    except ValueError:  # output-dir 在仓库根之外（--output-dir 手动覆盖）时降级相对路径
        return f"{HTML_SUBDIR}/{p.stem}.html"


def _zoomable_html_link_line(html_url: str) -> str:
    """Mermaid 图块上方的可缩放 HTML 跳转链接行（blockquote 风格，与图例一致）。"""
    return f"> **[📊 可缩放大图（HTML）]({html_url})**\n"

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

    return _dedupe_modules(all_nodes), _filter_import_edges(all_nodes, all_edges)


def _dedupe_modules(all_nodes: list[dict]) -> list[dict]:
    """模块去重：过滤 module+.py 节点 → 按 blueprint_id 分组 → 每组选代表路径并聚合字段。"""
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
        nodes.sort(key=_rep_path_sort_key)
        rep = {k: v for k, v in nodes[0].items()}
        rep["module_id"] = key
        rep["build_status"] = _aggregate_build_status([n.get("build_status") for n in nodes])
        # domain_id / architecture_layer 聚合：代表节点（常是 __init__.py）这两列可能为空，
        # 取组内首个非空值，避免纵览里域标注丢失（如同 MOD-REGIME-001 代表 __init__.py
        # 无 domain_id，但子文件 regime_detector.py 有 D_REGIME）。
        for field_name in ("domain_id", "architecture_layer"):
            if not (rep.get(field_name) or "").strip():
                _fill_first_nonempty(rep, nodes, field_name)
        modules.append(rep)
    return modules


def _rep_path_sort_key(n: dict) -> tuple[int, int]:
    """代表路径排序键：__init__.py 优先（0），其次最短 path。"""
    path = n.get("path") or ""
    return (0 if path.endswith("__init__.py") else 1, len(path))


def _fill_first_nonempty(rep: dict, nodes: list[dict], field_name: str) -> None:
    """把 rep[field_name] 补为组内首个非空值（rep 上为空时才补）。"""
    for n in nodes:
        v = (n.get(field_name) or "").strip()
        if v:
            rep[field_name] = v
            break


def _filter_import_edges(all_nodes: list[dict], all_edges: list[dict]) -> list[dict]:
    """依赖边过滤：node_id→blueprint_id 映射 → 仅保留 import 类边，按 blueprint_id 聚合去重+排自环。"""
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

    return [
        {"from_module_id": f, "to_module_id": t, "dep_type": d}
        for f, t, d in edges_set
    ]


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

        # ALGO_FLOW 推导流程（§4.16，仅运营态代码 docstring 有 # [ALGO_FLOW] 标记时非 None；
        # 设计态/缺失态恒为 None → 回退文字卡片，渐进式向后兼容）
        algo_flow = summary.algo_flow

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
            "algo_flow": algo_flow,
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


# ALGO_FLOW 标记注释行（docstring 内 # 开头的 YAML 风格行）：起止标记 / 层:/边: 段头 /
# - id: 节点起点 / key: value 字段行 / A1 --> B1 边行。这些是机器解析标记（§4.16 已解析成
# 推导流程图），原样贴出字大难读——渲染「算法步骤」时剥离，只留人类可读文字。
_ALGO_FLOW_LINE_RE = re.compile(
    r"^#\s*(?:"
    r"\[/?ALGO_FLOW\]"          # [ALGO_FLOW] / [/ALGO_FLOW] 起止标记
    r"|-\s+id\s*:"              # - id: A1 节点起点
    r"|\w+\s*:"                 # name_zh:/code:/层:/边: 等 key: 字段行（半角冒号）
    r"|[A-Za-z0-9_]+\s+-{1,2}"  # I1 --> A1 / I1 -…（截断残行）边行
    r"|$"                       # 裸 "#" 行
    r")"
)


def _strip_algo_flow_comments(text: str) -> str:
    """剥离算法步骤文本里的 ALGO_FLOW 标记注释行，返回剩余人类可读文字（可能为空）。"""
    kept = [
        ln.rstrip()
        for ln in text.splitlines()
        if ln.strip() and not _ALGO_FLOW_LINE_RE.match(ln.strip())
    ]
    return "\n".join(kept).strip()


def _algo_steps_block_lines(r: dict, s: AlgorithmSummary) -> list[str]:
    """「算法步骤」块：剥离 ALGO_FLOW 标记注释行后只显示人类可读文字。

    整段都是标记（如包入口 docstring 全是 # [ALGO_FLOW] YAML 注释）或提取器剥离后
    无纯文字（algo_steps 为空）时：有推导流程图 → 提示看下方图；无 → 省略该段
    （不原样贴 # - id: 这种 YAML 注释）。
    """
    steps = (s.algo_steps or "").strip()
    if not steps:
        if r.get("algo_flow") is not None:
            return ["> **算法步骤**：见下方推导流程图（步骤细节已由 ALGO_FLOW 推导图承载）。", ">"]
        return []
    readable = _strip_algo_flow_comments(steps)
    if not readable:
        if r.get("algo_flow") is not None:
            return ["> **算法步骤**：见下方推导流程图（步骤细节已由 ALGO_FLOW 推导图承载）。", ">"]
        return []
    return ["> **算法步骤**：", _blockquote(readable), ">"]


def _layer_sort_key(layer: str) -> tuple:
    """layer 排序键：L0→L3 在前，未知/空层置末。"""
    return (0, LAYER_ORDER.index(layer)) if layer in LAYER_ORDER else (1, layer)


def render_stats(rows: list[dict]) -> str:
    """文档基本信息表。"""
    total = len(rows)
    op = sum(1 for r in rows if r["tier"] == "operational")
    de = sum(1 for r in rows if r["tier"] == "design")
    mi = sum(1 for r in rows if r["tier"] == "missing")
    # 算法覆盖：有文字算法步骤，或有 ALGO_FLOW 推导图（提取器剥离标记块后纯标记
    # docstring 的 algo_steps 为空，算法细节由推导图承载，不应误判为未覆盖）
    covered = sum(1 for r in rows if r["summary"].algo_steps or r.get("algo_flow") is not None)
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


# ── 环节总图 + 模块关联图（2026-08-12 增强，§4.3 节点格式 + §4.15 断点边）──

# tier → §4.3 成熟度行
_TIER_MATURITY = {
    "operational": "生产态 / production",
    "design": "设计态 / design",
    "missing": "缺失态 / missing",
}

# 断点边/正常边颜色（§4.15.3）
_BREAK_COLOR = "#c62828"   # 暗红 Material Red 900
_NORMAL_COLOR = "#333333"  # 近黑深灰


def _mod_node_id(module_id: str) -> str:
    """module_id → Mermaid 节点 ID（§4.4：只留字母数字下划线）。"""
    nid = re.sub(r"[^A-Za-z0-9_]", "_", module_id)
    nid = re.sub(r"_+", "_", nid).strip("_")
    return nid or "MOD_UNKNOWN"


def _build_providers(edges: list[dict]) -> dict[str, list[str]]:
    """上游依赖图：from_module_id -> [to_module_id, ...]（M import 谁）。"""
    providers: dict[str, list[str]] = defaultdict(list)
    for e in edges:
        providers[e["from_module_id"]].append(e["to_module_id"])
    return dict(providers)


def _build_rel_context(rows: list[dict], edges: list[dict], consumers: dict[str, list[str]]) -> dict:
    """构建模块关联上下文：providers（M import 谁）+ consumers（谁 import M）+ row 索引。

    depgraph 边方向：from_module import to_module（from 依赖 to）。
    """
    return {
        "providers": _build_providers(edges),
        "consumers": consumers,
        "row_by_id": {r["module_id"]: r for r in rows},
    }


def _render_dep_edges(edge_tuples: list[tuple[str, str, bool]]) -> tuple[list[str], str]:
    """渲染依赖边（断点边在前）+ linkStyle（§4.15 复现）。

    :param edge_tuples: (src_nid, dst_nid, is_break)；is_break=True → 红色虚线+断点标签。
    :return: (edge_lines, link_style_str)
    """
    # 确定性排序（depgraph DB 行序不稳定，2026-08-12 幂等性修复）：断点边/正常边各按 (src,dst) 排序
    breaks = sorted((t for t in edge_tuples if t[2]), key=lambda t: (t[0], t[1]))
    normals = sorted((t for t in edge_tuples if not t[2]), key=lambda t: (t[0], t[1]))
    ordered = breaks + normals
    edge_lines: list[str] = []
    break_idx: list[int] = []
    normal_idx: list[int] = []
    for i, (s, d, brk) in enumerate(ordered):
        if brk:
            edge_lines.append(f"    {s} -.->|断点| {d}")
            break_idx.append(i)
        else:
            edge_lines.append(f"    {s} --> {d}")
            normal_idx.append(i)
    link_lines: list[str] = []
    if break_idx:
        link_lines.append(
            f"    linkStyle {','.join(str(i) for i in break_idx)} "
            f"stroke:{_BREAK_COLOR},stroke-width:2px,color:{_BREAK_COLOR}"
        )
    if normal_idx:
        link_lines.append(
            f"    linkStyle {','.join(str(i) for i in normal_idx)} "
            f"stroke:{_NORMAL_COLOR},stroke-width:2px,color:{_NORMAL_COLOR}"
        )
    return edge_lines, "\n".join(link_lines)


# 包入口（__init__.py）通用名：翻译真源 auto-extract 常把 __init__.py 登记为
# "包入口 / Init"（无信息量），命中时改走 _derive_pkg_entry_name 派生友好中文名。
_GENERIC_PKG_ENTRY_NAMES = {"包入口", "包标记", "init", "__init__", "package", "package init"}


def _has_cjk(text: str) -> bool:
    """检测字符串是否含中文字符（CJK Unified Ideographs）。"""
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def _is_pkg_entry(path: str) -> bool:
    """是否包入口文件（__init__.py）。"""
    return path.replace("\\", "/").endswith("__init__.py")


def _derive_pkg_entry_name(r: dict) -> str:
    """包入口友好中文名：``{域中文名}包入口``；域缺失时回退 ``{包目录名} 包入口``。"""
    dom_id = r.get("domain_id") or ""
    dom_zh = get_domain_name_zh(dom_id) if dom_id else ""
    if dom_zh and dom_zh != dom_id:
        return f"{dom_zh}包入口"
    path = (r.get("path") or "").replace("\\", "/")
    pkg = path.rsplit("/", 2)[-2] if "/" in path else ""
    return f"{pkg} 包入口" if pkg else ""


def _module_display_name(r: dict | None) -> str:
    """模块显示名：翻译真源双语名 → docstring 首行 → 路径派生。

    包入口兜底（2026-08-13）：__init__.py 的翻译真源多为 auto-extract 的
    "包入口 / Init"（无信息量中文），命中通用名时派生"{域中文名}包入口"，
    保证图表节点/卡片标题显示有信息量的中文名而非"包入口"。
    """
    if not r:
        return ""
    name = (r.get("bi_name") or "").strip()
    if not name:
        name = (r["summary"].module_name or "").strip()
    if not name:
        name = derive_name_from_path(r.get("path") or r["module_id"])
    if _is_pkg_entry(r.get("path") or ""):
        head = name.split(" / ", 1)[0].strip().lower()
        # 通用名（"包入口 / Init"）或无中文的 docstring 碎片名（如 "# （ALGO_FLOW）"）
        # 都视为无信息量 → 派生"{域中文名}包入口"
        if head in _GENERIC_PKG_ENTRY_NAMES or not _has_cjk(name):
            derived = _derive_pkg_entry_name(r)
            if derived:
                name = derived
    return name


def _module_plain_zh(r: dict) -> str:
    """模块大白话：翻译真源 plain_zh → 包入口派生 → docstring 摘要前 50 字。

    包入口派生（2026-08-13）：__init__.py 的 plain_zh 常为空，直接回退英文
    docstring 会让节点没有中文大白话；此时按域中文名/包目录名派生。
    """
    plain = get_module_plain(r.get("path") or "")
    if plain:
        return plain
    if _is_pkg_entry(r.get("path") or ""):
        dom_id = r.get("domain_id") or ""
        dom_zh = get_domain_name_zh(dom_id) if dom_id else ""
        if dom_zh and dom_zh != dom_id:
            return f"{dom_zh}域各子模块的统一入口（包入口）"
        path = (r.get("path") or "").replace("\\", "/")
        pkg = path.rsplit("/", 2)[-2] if "/" in path else ""
        if pkg:
            return f"{pkg} 包各子模块的统一入口"
    return (r["summary"].summary or "")[:50]


def _zh_name_part(name: str) -> str:
    """取双语名的中文段（"中文 / English" → "中文"）；无中文段时返回原名。"""
    for seg in name.split(" / "):
        seg = seg.strip()
        if any("\u4e00" <= ch <= "\u9fff" for ch in seg):
            return seg
    return name


def _stage_node_label(r: dict) -> str:
    """环节总图节点标签（§4.3 域内节点四要素：成熟度+双语名+大白话+文件路径）。"""
    mat = _TIER_MATURITY.get(r["tier"], r["tier"])
    name = _module_display_name(r)
    plain = _module_plain_zh(r)
    parts = (r.get("path") or "").replace("\\", "/").split("/")
    file_seg = "/".join(parts[-2:]) if len(parts) >= 2 else (r.get("path") or "")
    label = f"({mat}) {name}<br/>{plain}<br/>文件: {file_seg}"
    # 转义 + 预折行（复用算法图同款护栏）
    rendered: list[str] = []
    for seg in label.split("<br/>"):
        seg = seg.strip()
        if seg:
            rendered.append(_wrap_label_text(_sanitize_algo_label(seg), max_units=40))
    return "<br/>".join(rendered)


def render_stage_overview_mermaid(stage_rows: list[dict], edges: list[dict]) -> str:
    """环节总图 Mermaid：该环节全部模块 + 环节内 depgraph 依赖边（§4.3 节点 + §4.15 断点边）。

    边规则：两端都在本环节才画；任一端非运营态 → 断点边（红色虚线+断点标签），否则黑色实线。
    """
    mids = {r["module_id"] for r in stage_rows}
    tier_of = {r["module_id"]: r["tier"] for r in stage_rows}

    lines = ["```mermaid", _ALGO_MERMAID_THEME, "flowchart TD"]
    for r in sorted(stage_rows, key=lambda x: (_layer_sort_key(x["layer"]), x["module_id"])):
        nid = _mod_node_id(r["module_id"])
        lines.append(f'    {nid}["{_stage_node_label(r)}"]')

    seen: set[tuple[str, str]] = set()
    edge_tuples: list[tuple[str, str, bool]] = []
    for e in edges:
        f, t = e["from_module_id"], e["to_module_id"]
        if f not in mids or t not in mids or (f, t) in seen:
            continue
        seen.add((f, t))
        is_break = tier_of.get(f) != "operational" or tier_of.get(t) != "operational"
        edge_tuples.append((_mod_node_id(f), _mod_node_id(t), is_break))

    if edge_tuples:
        edge_lines, link_style = _render_dep_edges(edge_tuples)
        lines.append("")
        lines.append("    %% 断点边（红色虚线+断点标签）在前，正常边（黑色实线）在后")
        lines.extend(edge_lines)
        if link_style:
            lines.append("")
            lines.append("    %% 边样式：断点边=红色虚线，正常边=黑色实线")
            lines.append(link_style)

    lines.append("  classDef default fill:#eef,stroke:#336,stroke-width:1px,color:#003;")
    lines.append("```")
    return "\n".join(lines)


def _rel_node_label(row_by_id: dict, module_id: str, is_center: bool = False) -> str:
    """关联图节点标签：状态emoji+中文名（第一行）+ module_id（第二行），短折行使节点更窄。"""
    rr = row_by_id.get(module_id)
    emoji = STATUS_EMOJI.get(rr["tier"], "⬜") if rr else "⬜"
    name = _module_display_name(rr) if rr else derive_name_from_path(module_id)
    # 节点内容简化（2026-08-13）：第一行只显示中文名（双语名取中文段），
    # module_id 挪到第二行；max_units=24 短折行使节点更窄。
    name = _zh_name_part(name)
    star = "⭐ " if is_center else ""
    text = f"{star}{emoji} {name}<br/>{module_id}"
    rendered: list[str] = []
    for seg in text.split("<br/>"):
        seg = seg.strip()
        if seg:
            rendered.append(_wrap_label_text(_sanitize_algo_label(seg), max_units=24))
    return "<br/>".join(rendered)


def _rel_edge_tuples(
    row_by_id: dict,
    center_nid: str,
    ups: list[str],
    downs: list[str],
) -> list[tuple[str, str, bool]]:
    """关联图边生成：上游→本模块 / 本模块→下游；对端非运营态=断点边。"""
    def _is_break(x: str) -> bool:
        """_is_break implementation."""
        rr = row_by_id.get(x)
        return (rr is None) or rr["tier"] != "operational"

    edge_tuples: list[tuple[str, str, bool]] = []
    for u in ups:  # 上游 → 本模块（上游未实现=断点）
        edge_tuples.append((_mod_node_id(u), center_nid, _is_break(u)))
    for d in downs:  # 本模块 → 下游（下游未实现=断点）
        edge_tuples.append((center_nid, _mod_node_id(d), _is_break(d)))
    return edge_tuples


def _render_module_relation_mermaid(r: dict, rel: dict, html_url: str = "") -> str:
    """模块上下游关联图（卡片下）：上游依赖 → 本模块 → 下游消费者（§4.15 断点边）。

    数据从 depgraph 边自动提取（自动全量）；任一端非运营态的连线用红色虚线断点边。
    上游/下游各最多显示 8 个（防爆），超出在图例注明。
    html_url：本环节文件的可缩放 HTML 链接（非空时图块上方加跳转链接）。
    """
    mid = r["module_id"]
    row_by_id = rel["row_by_id"]
    ups_all = sorted(set(rel["providers"].get(mid, [])))
    downs_all = sorted(set(rel["consumers"].get(mid, [])))
    if not ups_all and not downs_all:
        return ""
    ups, downs = ups_all[:8], downs_all[:8]

    lines = ["```mermaid", _ALGO_MERMAID_THEME, "flowchart LR"]
    center_nid = _mod_node_id(mid)
    for u in ups:
        lines.append(f'    {_mod_node_id(u)}["{_rel_node_label(row_by_id, u)}"]')
    lines.append(f'    {center_nid}["{_rel_node_label(row_by_id, mid, is_center=True)}"]')
    for d in downs:
        lines.append(f'    {_mod_node_id(d)}["{_rel_node_label(row_by_id, d)}"]')

    edge_lines, link_style = _render_dep_edges(_rel_edge_tuples(row_by_id, center_nid, ups, downs))
    lines.append("")
    lines.extend(edge_lines)
    if link_style:
        lines.append("")
        lines.append(link_style)
    lines.append("  classDef default fill:#eef,stroke:#336,stroke-width:1px,color:#003;")
    lines.append("```")

    more: list[str] = []
    if len(ups_all) > 8:
        more.append(f"上游 +{len(ups_all) - 8}")
    if len(downs_all) > 8:
        more.append(f"下游 +{len(downs_all) - 8}")
    more_txt = f"（{'，'.join(more)}）" if more else ""
    legend = (
        f"\n> **上下游关联图**（depgraph 自动派生{more_txt}）："
        f"上游依赖 {len(ups_all)} 个 ｜ 下游消费者 {len(downs_all)} 个。"
        f"红色虚线=对端未实现（设计态/缺失）。\n"
    )
    link = _zoomable_html_link_line(html_url) if html_url else ""
    return legend + link + "\n".join(lines) + "\n"



def _render_cards_by_layer(
    rows: list[dict],
    consumers: dict[str, list[str]],
    rel: dict | None = None,
    html_url: str = "",
) -> str:
    """渲染模块卡片，按 layer（L0→L3）分组。

    用于环节文件和系统基础文件——两者内部都按 layer 二级分组。
    rel：模块关联上下文（providers/consumers/row_by_id），传入时每个卡片追加上下游关联图。
    html_url：本文件的可缩放 HTML 链接（传入时每个 Mermaid 图块上方加跳转链接）。
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
            parts.append(_render_module_card(r, consumers, rel, html_url))

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
            parts.append(_render_module_card(r, consumers, rel, html_url))

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


def _render_module_card(
    r: dict,
    consumers: dict[str, list[str]],
    rel: dict | None = None,
    html_url: str = "",
) -> str:
    """单模块算法详情卡片。"""
    s: AlgorithmSummary = r["summary"]
    algo_flow = r.get("algo_flow")
    if algo_flow is not None:
        return _render_module_card_with_flow(r, consumers, s, algo_flow, rel, html_url)
    return _render_module_card_text(r, consumers, s, rel, html_url)


def _render_module_card_text(
    r: dict,
    consumers: dict[str, list[str]],
    s: AlgorithmSummary,
    rel: dict | None = None,
    html_url: str = "",
) -> str:
    """单模块算法详情卡片（文字版，无 ALGO_FLOW 标记时的回退）。"""
    out = _module_card_header_lines(r, s)
    out.extend(_module_card_body_lines(r, consumers, s))
    card = "\n".join(out)
    # 模块上下游关联图（depgraph 自动全量，§4.15 断点边）
    if rel is not None:
        card += _render_module_relation_mermaid(r, rel, html_url)
    return card


def _module_card_header_lines(r: dict, s: AlgorithmSummary) -> list[str]:
    """卡片头部：锚点 + 标题行（emoji/双语名/layer·域 标签）。"""
    emoji = STATUS_EMOJI[r["tier"]]
    name = _module_display_name(r) or r["module_id"]
    dom_id = r["domain_id"] or ""
    dom_zh = get_domain_name_zh(dom_id) if dom_id else ""
    dom_display = f"{dom_zh}（{dom_id}）" if (dom_zh and dom_zh != dom_id) else (dom_id or "—")
    layer_tag = f"[{r['layer']}·{dom_display}]" if r["layer"] else f"[{dom_display}]"

    # 稳定 HTML 锚点（module_id 小写），供 battle_map/域文档深链接跳转。
    # 不依赖 GitHub 自动锚点（标题含 emoji/中文/特殊字符，自动锚点脆弱）。
    anchor_id = r["module_id"].lower()
    return [f'<a id="{anchor_id}"></a>', f"#### {emoji} {r['module_id']} {name} {layer_tag}", ""]


def _module_card_body_lines(r: dict, consumers: dict[str, list[str]], s: AlgorithmSummary) -> list[str]:
    """卡片正文：真源/概述/算法步骤/不变量/被依赖/质量。"""
    out: list[str] = []
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
    out.extend(_algo_steps_block_lines(r, s))
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
    return out


# ── ALGO_FLOW 推导流程图渲染（§4.14/§4.15/§4.16）─────────────────

# Mermaid 灰色主题头（clusterBkg 透明，与样本 regime_detector_drilldown_sample.md 对齐）
_ALGO_MERMAID_THEME = (
    "%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', "
    "'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', "
    "'lineColor': '#333333', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
    "'clusterBkg': 'transparent', 'clusterBorder': 'transparent', "
    "'fontSize': '14px'}}}%%"
)

# 5 层 subgraph 定义（顺序固定：输入→特征→指标→算法→输出）
# (layer_name, subgraph_id, subgraph_title_prefix)
_ALGO_LAYERS: list[tuple[str, str, str]] = [
    ("输入", "sg_input", "📥 输入层"),
    ("特征", "sg_feat", "🔬 特征层"),
    ("指标", "sg_indi", "📈 技术指标"),
    ("算法", "sg_algo", "⚙️ 算法层"),
    ("输出", "sg_out", "📤 输出层"),
]

# classDef 样式（5 类：input/feature/break/algo/output）
_ALGO_CLASS_DEFS = [
    "    classDef input fill:#e3f2fd,stroke:#01579b,stroke-width:2px,color:#000",
    "    classDef feature fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#000",
    "    classDef break fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000",
    "    classDef algo fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000",
    "    classDef output fill:#fce4ec,stroke:#c62828,stroke-width:2px,color:#000",
]


def _wrap_label_text(text: str, max_units: int = 48) -> str:
    """将长节点标签文本按显示宽度预折行（Mermaid 节点内显示用，§4.10 铁律）。

    折行规则：显示宽度（CJK=2/ASCII=1）超 max_units 断行（48 ≈ 24 个汉字）；
    优先在空格/下划线之后、左括号/斜杠之前软断（保持英文词完整），否则硬断。
    原样复制自 visualization_view_template.md §4.10。
    """
    if not text:
        return ""
    lines: list[str] = []
    remaining = text.strip()
    while remaining:
        width = 0
        cut = 0
        soft = -1
        for i, ch in enumerate(remaining):
            u = 2 if ord(ch) > 0x2E7F else 1
            if width + u > max_units:
                break
            width += u
            cut = i + 1
            if ch in " _":
                soft = i + 1
            elif ch in "（(/":
                soft = i if i > 0 else -1
        if cut >= len(remaining):
            lines.append(remaining)
            break
        if soft >= 8:
            cut = soft
        line = remaining[:cut].rstrip()
        if line:
            lines.append(line)
        remaining = remaining[cut:].lstrip(" ")
    return "<br/>".join(lines)


def _sanitize_algo_label(text: str) -> str:
    """转义 Mermaid 节点标签特殊字符（§4.9）。

    节点标签在 ``["..."]`` 内，需转义 ``"``（闭合标签）和 ``[`` ``]``（破坏语法）。
    半角括号在双引号标签内安全，保留（样本公式含 (C-Ln) 等正常渲染）。
    """
    return text.replace('"', "'").replace("[", "（").replace("]", "）")


def _algo_node_class(node: AlgoFlowNode) -> str:
    """节点 CSS 类名：断点节点→break，否则按层着色。"""
    if node.is_break:
        return "break"
    layer = node.layer
    if layer == "输入":
        return "input"
    if layer == "输出":
        return "output"
    if layer == "算法":
        return "algo"
    return "feature"  # 特征/指标 非断点


def _algo_node_title(node: AlgoFlowNode) -> str:
    """节点标题行（中文名前英文后，§4.14.3 铁律1）。

    各层标题组装规则不同（样本 regime_detector_drilldown_sample.md）：
      - 输入：name_zh（不含 id，如"沪深300 日线数据"）
      - 特征：id name_zh name_en（如"F1 已实现波动率分位 realized_vol_pct"）
      - 指标：id name_zh（name_en 与 id 相同时去重）
      - 算法：name_zh name_en（不含 id A1，编号①②在 name_zh 内）
      - 输出：name_zh name_en（不含 id O1）
    """
    layer = node.layer
    if layer == "输入":
        return node.name_zh or node.id
    if layer == "特征":
        parts = [p for p in (node.id, node.name_zh, node.name_en) if p]
    elif layer == "指标":
        parts = _indicator_title_parts(node)
    elif layer == "算法":
        parts = [p for p in (node.name_zh, node.name_en) if p and p != node.id]
    elif layer == "输出":
        parts = [p for p in (node.name_zh, node.name_en) if p]
    else:
        parts = [p for p in (node.id, node.name_zh, node.name_en) if p]
    return " ".join(parts) or node.id


def _indicator_title_parts(node: AlgoFlowNode) -> list[str]:
    """指标层标题部件：id + name_zh（+ name_en 与 id 不同名时追加）。"""
    parts = [p for p in (node.id, node.name_zh) if p]
    if node.name_en and node.name_en != node.id:
        parts.append(node.name_en)
    return parts


def _label_lines_input(node: AlgoFlowNode) -> list[str]:
    """_label_lines_input implementation."""
    lines = [_algo_node_title(node)]
    if node.fields:
        lines.append(node.fields)
    if node.code:
        lines.append(f"代码 {node.code}")
    return lines


def _label_lines_feature(node: AlgoFlowNode) -> list[str]:
    """_label_lines_feature implementation."""
    lines = [_algo_node_title(node)]
    if node.intro:
        lines.append(node.intro)
    if node.formula:
        lines.append(f"公式: {node.formula}")
    if node.code:
        lines.append(f"代码: {node.code}")
    if node.registry:
        lines.append(node.registry)
    return lines


def _label_lines_algo(node: AlgoFlowNode) -> list[str]:
    """_label_lines_algo implementation."""
    lines = [_algo_node_title(node)]
    if node.intro:
        lines.append(node.intro)
    if node.desc:
        lines.append(node.desc)
    elif node.formula:
        lines.append(node.formula)
    if node.inputs:
        lines.append(f"输入: {node.inputs}")
    if node.outputs:
        lines.append(f"输出: {node.outputs}")
    if node.invariant:
        lines.append(f"不变量: {node.invariant}")
    return lines


def _label_lines_output(node: AlgoFlowNode) -> list[str]:
    """_label_lines_output implementation."""
    lines = [_algo_node_title(node)]
    if node.intro:
        lines.append(node.intro)
    if node.invariant:
        lines.append(f"不变量: {node.invariant}")
    if node.downstream:
        lines.append(f"→ {node.downstream}")
    return lines


def _render_algo_node_label(node: AlgoFlowNode) -> str:
    """渲染单节点标签（§4.14.2 五类节点格式，<br/> 分隔多行）。"""
    builders = {
        "输入": _label_lines_input,
        "特征": _label_lines_feature,
        "指标": _label_lines_feature,
        "算法": _label_lines_algo,
        "输出": _label_lines_output,
    }
    builder = builders.get(node.layer)
    if builder is not None:
        lines = builder(node)
    else:
        lines = [_algo_node_title(node)]
        if node.intro:
            lines.append(node.intro)

    # 转义 + 预折行（§4.9 + §4.10）。字段内可能含手动 <br/>，逐段折行。
    rendered: list[str] = []
    for ln in lines:
        for seg in ln.split("<br/>"):
            seg = seg.strip()
            if seg:
                rendered.append(_wrap_label_text(_sanitize_algo_label(seg)))
    return "<br/>".join(rendered)


def _render_algo_edges(edges: list) -> tuple[list[str], str]:
    """渲染边定义（断点边在前）+ linkStyle 语句（§4.15）。

    :return: (edge_lines, link_style_str)
    """
    # 断点边在前（linkStyle 按出现顺序索引），各自组内保持原序
    breaks = [e for e in edges if e.is_break]
    normals = [e for e in edges if not e.is_break]
    ordered = breaks + normals

    edge_lines: list[str] = []
    break_idx: list[int] = []
    normal_idx: list[int] = []
    for i, e in enumerate(ordered):
        if e.is_break:
            edge_lines.append(f"    {e.src} -.->|断点| {e.dst}")
            break_idx.append(i)
        else:
            edge_lines.append(f"    {e.src} --> {e.dst}")
            normal_idx.append(i)

    link_lines: list[str] = []
    if break_idx:
        link_lines.append(
            f"    linkStyle {','.join(str(i) for i in break_idx)} "
            f"stroke:{_BREAK_COLOR},stroke-width:2px,color:{_BREAK_COLOR}"
        )
    if normal_idx:
        link_lines.append(
            f"    linkStyle {','.join(str(i) for i in normal_idx)} "
            f"stroke:{_NORMAL_COLOR},stroke-width:2px,color:{_NORMAL_COLOR}"
        )
    return edge_lines, "\n".join(link_lines)


def render_algo_flow_mermaid(algo_flow: AlgoFlowData) -> str:
    """按 ALGO_FLOW 数据生成 Mermaid 推导流程图（§4.14/§4.15/§4.16）。

    结构：灰色主题头 + flowchart TD + 5 层 subgraph + 节点定义 +
    边定义（断点边在前）+ linkStyle + classDef + class 绑定。
    参考 regime_detector_drilldown_sample.md 的 Mermaid 块格式。
    """
    # 按 layer 分组
    by_layer: dict[str, list[AlgoFlowNode]] = defaultdict(list)
    for n in algo_flow.nodes:
        by_layer[n.layer].append(n)

    lines = ["```mermaid", _ALGO_MERMAID_THEME, "flowchart TD"]

    # subgraph 分层渲染（顺序固定）
    for layer_name, sg_id, sg_title in _ALGO_LAYERS:
        layer_nodes = by_layer.get(layer_name, [])
        if not layer_nodes:
            continue
        lines.append(f'    subgraph {sg_id} ["{sg_title}（{len(layer_nodes)} 节点）"]')
        for n in layer_nodes:
            label = _render_algo_node_label(n)
            lines.append(f'        {n.id}["{label}"]:::{_algo_node_class(n)}')
        lines.append("    end")
        lines.append("")

    # 边定义（断点边在前）+ linkStyle
    if algo_flow.edges:
        edge_lines, link_style = _render_algo_edges(algo_flow.edges)
        if edge_lines:
            lines.append("    %% 断点边（红色虚线+断点标签）在前，正常边（黑色实线）在后")
            lines.extend(edge_lines)
            lines.append("")
        if link_style:
            lines.append("    %% 边样式：断点边=红色虚线，正常边=黑色实线")
            lines.append(link_style)
            lines.append("")

    # classDef 样式定义
    lines.extend(_ALGO_CLASS_DEFS)
    lines.append("")

    # class 绑定（按类分组节点 ID）
    class_groups: dict[str, list[str]] = defaultdict(list)
    for n in algo_flow.nodes:
        class_groups[_algo_node_class(n)].append(n.id)
    for cls in ("input", "feature", "break", "algo", "output"):
        ids = class_groups.get(cls, [])
        if ids:
            lines.append(f"    class {','.join(ids)} {cls}")

    lines.append("```")
    return "\n".join(lines)


def _render_module_card_with_flow(
    r: dict,
    consumers: dict[str, list[str]],
    s: AlgorithmSummary,
    algo_flow: AlgoFlowData,
    rel: dict | None = None,
    html_url: str = "",
) -> str:
    """单模块算法详情卡片（含 ALGO_FLOW 推导流程图）。

    文字卡片 + 追加 Mermaid 推导图块（§4.16 渐进式：有标记才追加）。
    """
    # 复用文字卡片渲染（真源/概述/算法步骤/不变量/被依赖/质量 + 上下游关联图）
    text_card = _render_module_card_text(r, consumers, s, rel, html_url)
    # 追加 Mermaid 推导图块
    mermaid_block = render_algo_flow_mermaid(algo_flow)

    # 断点统计（图例说明）
    break_nodes = [n for n in algo_flow.nodes if n.is_break]
    break_edges = [e for e in algo_flow.edges if e.is_break]
    legend_lines = [
        "",
        "> **推导流程图 / ALGO_FLOW**（`# [ALGO_FLOW]` 标记自动解析，§4.16）：",
        "> 图例：**红色虚线 + 断点标签** = 断点边（连到断点节点）｜ **黑色实线** = 正常边。",
    ]
    if break_nodes:
        break_names = ", ".join(
            f"{n.id}（{n.name_zh or n.name_en or '未命名'}）" for n in break_nodes
        )
        legend_lines.append(
            f"> 断点节点 {len(break_nodes)} 个：{break_names}｜断点边 {len(break_edges)} 条。"
        )
    legend_lines.append("")
    legend = "\n".join(legend_lines)
    link = _zoomable_html_link_line(html_url) if html_url else ""

    return text_card + legend + link + mermaid_block + "\n"


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
    index_html_url = _zoomable_html_url('index.md')
    header = f"""# 算法全景图 — 索引（自动派生·离库·按作战环节拆分）

> **真源**：代码 docstring + header ｜ blueprint.md §核心规则 ｜ {DB_DISPLAY_NAME}（nodes/edges）。
> 改真源 → 重跑生成器 → 本文档自动更新（派生产物，不入 git，按需生成）。
> **重生成命令**：`python scripts/governance/d5_architecture/generators/generate_module_algorithm_overview.py`
> **生成时间**（幂等）：{ts}
> **[可缩放 HTML 版 / Zoomable HTML]({index_html_url})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

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
        + _zoomable_html_link_line(index_html_url)
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
    rel: dict | None = None,
) -> str:
    """组装单个作战环节文件（stages/XX_stage.md）。

    结构：头部 + 环节总图（§4.3 节点 + §4.15 断点边，depgraph 自动派生）+ 算法详情卡片。
    """
    ts = idempotent_timestamp(_THIS_FILE)
    zh = STAGE_ID_TO_NAME[stage_id]
    file_rel = STAGE_ID_TO_FILE[stage_id]
    html_url = _zoomable_html_url(file_rel)

    op = sum(1 for r in stage_rows if r["tier"] == "operational")
    de = sum(1 for r in stage_rows if r["tier"] == "design")
    mi = sum(1 for r in stage_rows if r["tier"] == "missing")

    header = f"""# 算法全景图 — 作战环节「{zh}」（{len(stage_rows)} 模块）

> [← 返回索引](../index.md)
> **[可缩放 HTML 版 / Zoomable HTML]({html_url})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式
> **真源**：代码 docstring + header ｜ blueprint.md §核心规则 ｜ {DB_DISPLAY_NAME}
> 自动派生，离库不入 git。改真源 → 重跑生成器 → 本文档自动更新。
> **生成时间**（幂等）：{ts}
> **三档**：🟦运营 {op} ｜ 🟧设计 {de} ｜ ⬜缺失 {mi}

"""
    overview = (
        "## 环节总图（depgraph 自动派生）\n\n"
        "> 本环节全部模块及环节内依赖关系。红色虚线+断点标签 = 对端未实现（设计态/缺失）。\n"
        + _zoomable_html_link_line(html_url)
        + "\n"
        + render_stage_overview_mermaid(stage_rows, edges)
        + "\n\n"
    )
    body = _render_cards_by_layer(stage_rows, consumers, rel, html_url)
    footer = f"""

---

> 环节 `{stage_id}`（{zh}）｜ {len(stage_rows)} 模块 ｜ 生成时间 {ts}（幂等）。
> 跨环节模块（同时属于多个环节）在本文件中重复出现——intentional，检修时需看到该环节涉及的全部模块。
"""
    return header + overview + "## 算法详情\n\n" + body + footer


def render_system_foundation_doc(
    unanchored_rows: list[dict],
    edges: list[dict],
    consumers: dict[str, list[str]],
    rel: dict | None = None,
) -> str:
    """组装系统基础文件（system_foundation.md，未锚定模块）。"""
    ts = idempotent_timestamp(_THIS_FILE)
    html_url = _zoomable_html_url('system_foundation.md')

    op = sum(1 for r in unanchored_rows if r["tier"] == "operational")
    de = sum(1 for r in unanchored_rows if r["tier"] == "design")
    mi = sum(1 for r in unanchored_rows if r["tier"] == "missing")

    header = f"""# 算法全景图 — 系统基础（未锚定模块，{len(unanchored_rows)} 模块）

> [← 返回索引](index.md)
> **[可缩放 HTML 版 / Zoomable HTML]({html_url})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式
> **真源**：代码 docstring + header ｜ blueprint.md §核心规则 ｜ {DB_DISPLAY_NAME}
> 这些模块未锚定到任何作战环节（基础设施/治理/安全/数据类），按 architecture_layer（L0→L3）内部分组。
> 自动派生，离库不入 git。改真源 → 重跑生成器 → 本文档自动更新。
> **生成时间**（幂等）：{ts}
> **三档**：🟦运营 {op} ｜ 🟧设计 {de} ｜ ⬜缺失 {mi}

"""
    body = _render_cards_by_layer(unanchored_rows, consumers, rel, html_url)
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


@dataclass
class _WriteInputs:
    """_write_md_files 的参数对象（§5.150 长参数列表规避，NO-LONG-PARAM-LIST gate）。"""

    rows: list[dict]
    edges: list[dict]
    anchored_by_stage: dict[str, list[dict]]
    unanchored_rows: list[dict]
    module_to_file: dict[str, str]
    consumers: dict[str, list[str]]
    rel: dict


def _write_md_files(out_dir: Path, wi: _WriteInputs) -> list[tuple[str, int]]:
    """写入全部 MD 文件（index + 各环节 + system_foundation），返回 (相对路径, 字符数) 列表。"""
    written: list[tuple[str, int]] = []

    # index.md
    index_md = render_index_doc(wi.rows, wi.edges, wi.anchored_by_stage, wi.unanchored_rows, wi.module_to_file)
    index_path = out_dir / "index.md"
    _atomic_write(index_path, index_md)
    written.append(("index.md", len(index_md)))

    # stages/XX_stage.md
    for stage_id in STAGE_ORDER:
        stage_rows = wi.anchored_by_stage.get(stage_id, [])
        if not stage_rows:
            continue
        stage_md = render_stage_doc(stage_id, stage_rows, wi.edges, wi.consumers, wi.rel)
        stage_path = out_dir / STAGE_ID_TO_FILE[stage_id]
        _atomic_write(stage_path, stage_md)
        written.append((STAGE_ID_TO_FILE[stage_id], len(stage_md)))

    # system_foundation.md
    if wi.unanchored_rows:
        sf_md = render_system_foundation_doc(wi.unanchored_rows, wi.edges, wi.consumers, wi.rel)
        sf_path = out_dir / "system_foundation.md"
        _atomic_write(sf_path, sf_md)
        written.append(("system_foundation.md", len(sf_md)))

    return written


def _cleanup_old_files(out_dir: Path, stages_dir: Path) -> None:
    """清理旧单文件产物（md+html）与不在当前 STAGE_ORDER 的过时环节文件。"""
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
        rel_name = f"stages/{f.name}"
        if f.is_file() and rel_name not in current_stage_files:
            f.unlink()
            print(f"[CLEANUP] 删除过时环节文件: {rel_name}")


def _emit_html_files(out_dir: Path, written: list[tuple[str, int]]) -> None:
    """联动生成可缩放 HTML（mermaid 渲染验证用，离库派生不入 git）；单文件失败不阻断。"""
    html_cnt = 0
    for rel_, _s in written:
        md_path = out_dir / rel_
        try:
            html_path = emit_zoomable_html(md_path, md_path.read_text(encoding="utf-8"))
            if html_path is not None:
                html_cnt += 1
        except Exception as e:  # noqa: BLE001 — HTML 派生失败不阻断主产物
            print(f"  [WARN] HTML 生成失败 {rel_}: {type(e).__name__}: {e}")
    print(f"[OK] 可缩放 HTML {html_cnt} 个（{HTML_SUBDIR}/）")


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
    rel = _build_rel_context(rows, edges, consumers)
    written = _write_md_files(out_dir, _WriteInputs(
        rows=rows, edges=edges, anchored_by_stage=anchored_by_stage,
        unanchored_rows=unanchored_rows, module_to_file=module_to_file,
        consumers=consumers, rel=rel,
    ))
    _cleanup_old_files(out_dir, stages_dir)

    print(f"\n[OK] 生成 {len(written)} 个文件：")
    for rel_, size in written:
        print(f"  {rel_:45s} {size:>8,} 字符")
    total_chars = sum(s for _, s in written)
    print(f"  {'合计':45s} {total_chars:>8,} 字符")

    _emit_html_files(out_dir, written)


if __name__ == "__main__":
    main()
