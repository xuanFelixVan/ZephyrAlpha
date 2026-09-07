# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md
# [MODULE] zephyr.trading.decision_map
# [DOMAIN] D_TRADING
# [DEPENDENCIES] yaml（外部 PyYAML）；dataclasses;pathlib（stdlib）
# [CONSUMERS] V1 api_server 只读端点（规划中）；tests/trading/test_decision_map.py
# [STARTUP] imported（纯函数库，无常驻进程/无事件订阅）
# [MATURITY] production
# [INVARIANTS] INV-1 地图YAML不复制注册表条目只持稳定标识符引用; INV-2 load产出全frozen dataclass; INV-3 validate纯函数无副作用; INV-4 error=0才可被下游消费; INV-5 module_ref=null记warning不记error（V0缺口可视化输入）
# [MODIFY-GUARD] schema_version 变更必须同步升级 dataclasses+校验规则+测试（R1-R36）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DecisionMapSchemaError（load阶段结构错误）; validate不抛异常只产GapReport
# [TESTS] tests/trading/test_decision_map.py
# [A_module] module_id=MOD-TRADING-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 地图真源 YAML（config/trading_decision_map.yaml）
#   fields: nodes/edges/state_matrix/markets（schema v1.0）
#   code: load_decision_map(path) 读入
# - id: I2
#   name: 三个引用注册表（catalogs 目录）
#   fields: strategy_registry.yaml strategies[].strategy_id / factor_registry.yaml factors[].factor_id / data_asset_registry.yaml datasets[].dataset_id
#   code: validate_decision_map(registry_dir) 只读加载
# - id: I3
#   name: known_strategy_ids（可选）
#   fields: 代码 StrategyMeta 真源的 kebab-case 策略 id 集合
#   code: validate_decision_map(known_strategy_ids=...) 注入
# 层: 算法
# - id: A1
#   name_zh: ① 加载（load_decision_map）
#   name_en: load_decision_map
#   intro: YAML → frozen dataclass 图谱（节点/边/状态矩阵/市场），结构错误抛 DecisionMapSchemaError
#   desc: 解析 schema_version/map_id/markets/nodes/edges/state_matrix 五段；必填与枚举在 load 阶段最小校验（字段存在性），语义校验留给 validate
#   inputs: I1
#   outputs: DecisionMap
# - id: A2
#   name_zh: ② 校验（validate_decision_map）
#   name_en: validate_decision_map
#   intro: 引用存在性+治理门禁 R1-R36 → (ok, GapReport)；缺口即地图红节点语义
#   desc: R1 节点枚举; R2 边端点+类型+无环; R3 策略引用（STR-* 查 REG-STR-001，其余查 known_strategy_ids）; R4 因子引用 REG-FCT-001; R5 数据引用 REG-DATAFLOW-001 datasets; R6 置信度枚举+verified必带evidence; R7 矩阵格引用存在性; R8 sequence 边成环检测; R10 市场实例一致性; R12 整装方案; R13 算法引用（IND/EXA）; R14 doc_ref 存在+路径穿越拒绝; R15 治理字段枚举+新节点必填; R16 父子完整+树深≤4+树宽预警; R17 粒度（问题≤100字+禁模糊词）+容量（挂载≤8/因子≤12/数据≤8/算法≤8+各交叉轴上限）; R18 name_zh 唯一; R19 module_ref 存在; R20 node_id 骨架; R21 MOD-* 交叉锚（格式+depgraph 缓存对账+欠账 warning）; R22 矩阵覆盖 warning; R23 流预算 warning（>80）; R24 因子欠账 warning; R25 空转叶子 warning; R26-R36 11 库交叉轴（形态/席位/宏观/周期/宇宙/成本/事件/风险限额/组合模型/基准/告警阈值，表驱动 _XREF_SPECS）; R98 空地图; R99 注册表真源缺失; module_ref=null 记 warning
#   inputs: DecisionMap I2 I3
#   outputs: (bool, list[GapReportItem])
# 层: 输出
# - id: O1
#   name_zh: GapReport（缺口报告）
#   name_en: GapReportItem list
#   intro: level(error|warning)/code(R1-R8)/node_id/detail——下游 V1 API 消费渲染红节点
#   downstream: V1 api_server 端点; tests/trading/test_decision_map.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import yaml

__all__: Final = [
    "DecisionMapSchemaError",
    "StrategyMount",
    "DecisionMapNode",
    "DecisionMapEdge",
    "TdmMatrixCell",
    "StateMatrix",
    "Sleeve",
    "PortfolioPlan",
    "GapReportItem",
    "DecisionMap",
    "load_decision_map",
    "validate_decision_map",
]

# ── 枚举常量（schema v1.1 词表）──────────────────────────────────────────────
_MARKETS = frozenset({"cn_a", "crypto"})
_FLOWS = frozenset({"entry_flow", "position_flow", "exit_flow", "portfolio_flow"})
_NODE_TYPES = frozenset({"gate", "stage", "sensor", "aggregation", "cross_cutting"})
_POINTS = frozenset({"盘前", "盘中", "盘后", "持续"})
_EDGE_TYPES = frozenset({"feed", "sequence", "broadcast", "feedback"})
_CONFIDENCE = frozenset({"verified", "proposed", "untested"})
_SCHEMA_VERSIONS = frozenset({"1.0", "1.1"})
_LAYER_PREFIX_BY_FLOW: Final = {
    "entry_flow": "L",
    "position_flow": "P",
    "exit_flow": "S",  # X 前缀（风控横切）单独放行
    "portfolio_flow": "C",
}

_REG_STRATEGY = "strategy_registry.yaml"
_REG_FACTOR = "factor_registry.yaml"
_REG_DATA = "data_asset_registry.yaml"
_REG_EXA = "execution_algo_registry.yaml"
_REG_IND = "technical_indicator_registry.yaml"

# D32 门禁包常量（R15 治理字段枚举 / R17 粒度门禁 / R16 树深上限）
_ACTIVATIONS = frozenset({"premarket", "intraday", "postmarket", "weekly", "on_demand", "continuous"})
_AI_AUTONOMY = frozenset({"shadow", "paper", "pilot", "daily_review", "auto"})
_VAGUE_WORDS = ("视情况", "看情况", "酌情", "到时候再说")
_MAX_QUESTION_LEN = 100
_MAX_TREE_DEPTH = 4
# D33 节点容量门禁（Owner 裁定"单节点承载必须限死，不能全写在一个节点里"）：字段级数量上限
_MAX_MOUNTS = 8        # strategy_mounts 上限（超出=该拆环节）
_MAX_FACTOR_REFS = 12  # factor_refs 上限
_MAX_DATA_REFS = 8     # data_refs 上限
_MAX_ALGO_REFS = 8     # algo_refs 上限
_WARN_CHILDREN = 12    # 单父节点子节点数 warning 阈值（超=提示分层，不阻断）
# D34 交叉索引门禁（Owner 裁定"最细节点须能交叉定位其他全景图"）+ 膨胀预算
_MAX_NODES_PER_FLOW = 80  # 单流节点数 warning 阈值（防血肉阶段无限膨胀）
_NODE_ID_RE = r"TDM-[A-Z]-[A-Z0-9]+(-[A-Z0-9]+)*"  # R20：TDM-{流}-{层}-{序号}… 骨架
_MOD_ID_RE = r"MOD-[A-Z0-9]+(-[A-Z0-9]+)*"        # R21：MOD-* 交叉锚格式
_DEPGRAPH_CACHE = ".runtime/depgraph_scan_cache.json"  # path→blueprint_id 映射（派生缓存，缺失记 warning）

# D36 全库交叉轴（Owner 裁定"按消费场景分批打通全库"）：八业务库引用字段
# 表驱动——新增库只需在此加一行 + 容量表加一行；治理类注册表不入 TDM（裁定）
_XREF_SPECS: Final = (
    # (节点字段, 注册表文件, list section, 条目 key, 门禁码, 库名)
    ("pattern_refs", "chart_pattern_registry.yaml", "chart_patterns", "pattern_id", "R26", "形态库 PAT"),
    ("seat_refs", "seat_registry.yaml", "seats", "seat_id", "R27", "席位库 SEAT"),
    ("macro_refs", "macro_indicator_registry.yaml", "indicators", "indicator_id", "R28", "宏观指标库 MAC"),
    ("cycle_refs", "regime_cycle_registry.yaml", "cycles", "cycle_id", "R29", "周期库 CYC"),
    ("universe_refs", "universe_registry.yaml", "universes", "universe_id", "R30", "宇宙库 UNI"),
    ("cost_model_refs", "cost_model_registry.yaml", "cost_models", "cost_model_id", "R31", "成本模型库 CST"),
    ("event_refs", "event_calendar_registry.yaml", "event_types", "event_type_id", "R32", "事件日历库 EVT"),
    ("risk_limit_refs", "risk_limit_registry.yaml", "risk_limits", "risk_limit_id", "R33", "风险限额库 RLM"),
    ("portfolio_model_refs", "portfolio_model_registry.yaml", "portfolio_models", "model_id", "R34", "组合模型库 PFM"),
    ("benchmark_refs", "benchmark_registry.yaml", "benchmarks", "benchmark_id", "R35", "基准库 BMK"),
    ("threshold_refs", "alert_threshold_registry.yaml", "thresholds", "threshold_id", "R36", "告警阈值库 THD"),
)
_XREF_MAX: Final = {  # 各轴容量上限（D33 同款：超出=粒度过粗强制拆节点）
    "pattern_refs": 12,
    "seat_refs": 8,
    "macro_refs": 12,
    "cycle_refs": 8,
    "universe_refs": 4,
    "cost_model_refs": 4,
    "event_refs": 8,
    "risk_limit_refs": 12,
    "portfolio_model_refs": 4,
    "benchmark_refs": 4,
    "threshold_refs": 8,
}


class DecisionMapSchemaError(ValueError):
    """地图真源结构错误（load 阶段）。"""


@dataclass(frozen=True)
class StrategyMount:
    """环节上的策略挂载（D5：置信度分级治理）。"""

    strategy_ref: str
    confidence: str
    evidence: str | None = None


@dataclass(frozen=True)
class DecisionMapNode:
    """决策链节点（环节/传感器/聚合/横切；v1.5 增治理七字段，D17/D18/D32）。"""

    node_id: str
    name_zh: str
    market: str
    flow: str
    layer: str
    node_type: str
    point: str
    decision_question: str
    factor_refs: tuple[str, ...] = ()
    data_refs: tuple[str, ...] = ()
    module_ref: str | None = None
    strategy_mounts: tuple[StrategyMount, ...] = ()
    # v1.5 治理字段（D16 节点规范+D17 字段审计+D18 治理阶梯）
    parent_node: str | None = None
    activation: str | None = None
    invalidation: str | None = None
    ai_autonomy: str | None = None
    fallback: str | None = None
    algo_refs: tuple[str, ...] = ()
    doc_ref: str | None = None
    # v1.6（D34 交叉索引）：MOD-* 交叉锚——对齐五图体系（depgraph 以 module_id 为对齐 key）
    module_id: str | None = None
    # v1.7（D36/D37 全库交叉轴）：11 业务库引用（PAT/SEAT/MAC/CYC/UNI/CST/EVT/RLM/PFM/BMK/THD；表驱动见 _XREF_SPECS）
    # v1.8（Owner 2026-09-07 裁定）：大白话算法说明——"这个节点怎么算的"给全景图读者看（含关键指标与阈值口径）；
    #   必填（全景图可读性门禁），写作标准=大白话+具体参数（如"振幅≥3%/价差≥0.3%"），禁止空话
    algo_note_zh: str = ""
    pattern_refs: tuple[str, ...] = ()
    seat_refs: tuple[str, ...] = ()
    macro_refs: tuple[str, ...] = ()
    cycle_refs: tuple[str, ...] = ()
    universe_refs: tuple[str, ...] = ()
    cost_model_refs: tuple[str, ...] = ()
    event_refs: tuple[str, ...] = ()
    risk_limit_refs: tuple[str, ...] = ()
    portfolio_model_refs: tuple[str, ...] = ()
    benchmark_refs: tuple[str, ...] = ()
    threshold_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisionMapEdge:
    """决策依赖边（有依赖的地图才能推理）。"""

    from_node: str
    to_node: str
    edge_type: str


@dataclass(frozen=True)
class TdmMatrixCell:
    """环节×市场状态矩阵格子（D5：proposed 起步）。"""

    node_id: str
    state: str
    mounted: tuple[str, ...]
    confidence: str


@dataclass(frozen=True)
class StateMatrix:
    """状态矩阵骨架（列轴 V0 占位，情绪周期细化留血肉阶段）。"""

    states: tuple[str, ...]
    cells: tuple[TdmMatrixCell, ...]


@dataclass(frozen=True)
class Sleeve:
    """整装组合的单策略仓位（v1.1：拼装回测的可执行单元）。"""

    strategy_ref: str
    weight: float
    # v1.2：null=全状态激活；str=单状态；tuple=多状态（六段列轴下打板跨 3 段/做T跨 2 段）
    activation_state: str | tuple[str, ...] | None = None


@dataclass(frozen=True)
class PortfolioPlan:
    """整装仿真组合方案（v1.1：地图=整装仿真系统蓝图的可执行实例）。

    拼装回测引擎直接消费：多回测按权重合成整装净值（业界已验证）。
    """

    plan_id: str
    name_zh: str
    confidence: str
    sleeves: tuple[Sleeve, ...]
    aggregator: dict  # max_total_position/max_single_sleeve/correlation_cap 等（proposed 占位）


@dataclass(frozen=True)
class DecisionMap:
    """交易决策地图（图谱存储：节点+边；视图=投影；v1.1+整装方案层）。"""

    map_id: str
    schema_version: str
    markets: tuple[str, ...]
    nodes: tuple[DecisionMapNode, ...]
    edges: tuple[DecisionMapEdge, ...]
    state_matrix: StateMatrix
    portfolio_plan: PortfolioPlan | None = None  # v1.1：None=schema v1.0 无整装层


@dataclass(frozen=True)
class GapReportItem:
    """缺口报告项——地图上"有没有"灯的数据载体（N2 需求）。

    level=error  → 引用断链/结构违规，下游禁止消费
    level=warning → 缺口占位（module_ref=null 等），可视化红节点输入
    """

    level: str
    code: str
    node_id: str
    detail: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DecisionMapSchemaError(message)


def _parse_mount(raw: dict, node_id: str) -> StrategyMount:
    _require(isinstance(raw, dict), f"nodes[{node_id}].strategy_mounts 条目必须是映射")
    _require("strategy_ref" in raw, f"nodes[{node_id}] strategy_mounts 缺 strategy_ref")
    _require("confidence" in raw, f"nodes[{node_id}] strategy_mounts 缺 confidence")
    return StrategyMount(
        strategy_ref=str(raw["strategy_ref"]),
        confidence=str(raw["confidence"]),
        evidence=raw.get("evidence"),
    )


def _parse_node(raw: dict) -> DecisionMapNode:
    node_id = str(raw.get("node_id", ""))
    _require(node_id, "nodes 条目缺 node_id")
    for key in ("name_zh", "market", "flow", "layer", "node_type", "point", "decision_question"):
        _require(key in raw, f"nodes[{node_id}] 缺必填字段 {key}")
    mounts = tuple(_parse_mount(m, node_id) for m in raw.get("strategy_mounts", []) or [])
    return DecisionMapNode(
        node_id=node_id,
        name_zh=str(raw["name_zh"]),
        market=str(raw["market"]),
        flow=str(raw["flow"]),
        layer=str(raw["layer"]),
        node_type=str(raw["node_type"]),
        point=str(raw["point"]),
        decision_question=str(raw["decision_question"]),
        factor_refs=tuple(str(x) for x in raw.get("factor_refs", []) or []),
        data_refs=tuple(str(x) for x in raw.get("data_refs", []) or []),
        module_ref=raw.get("module_ref"),
        strategy_mounts=mounts,
        # v1.5 治理字段（缺失=None，校验按"有则校验+新节点必填"分级）
        parent_node=(str(raw["parent_node"]) if raw.get("parent_node") else None),
        activation=(str(raw["activation"]) if raw.get("activation") else None),
        invalidation=(str(raw["invalidation"]) if raw.get("invalidation") else None),
        ai_autonomy=(str(raw["ai_autonomy"]) if raw.get("ai_autonomy") else None),
        fallback=(str(raw["fallback"]) if raw.get("fallback") else None),
        algo_refs=tuple(str(x) for x in raw.get("algo_refs", []) or []),
        doc_ref=(str(raw["doc_ref"]) if raw.get("doc_ref") else None),
        module_id=(str(raw["module_id"]) if raw.get("module_id") else None),
        # v1.8 大白话算法说明（全景图可读性）
        algo_note_zh=str(raw.get("algo_note_zh", "") or ""),
        # v1.7 11 库交叉轴（表驱动字段，全部可选默认空）
        **{field: tuple(str(x) for x in raw.get(field, []) or []) for field, *_ in _XREF_SPECS},
    )


def load_decision_map(path: Path) -> DecisionMap:
    """加载地图真源 YAML → frozen DecisionMap（结构错误抛 DecisionMapSchemaError）。"""
    path = Path(path)
    _require(path.exists(), f"地图真源不存在: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    _require(isinstance(raw, dict), "地图真源顶层必须是映射")
    for key in ("schema_version", "map_id", "markets", "nodes", "edges", "state_matrix"):
        _require(key in raw, f"地图真源缺顶层字段 {key}")
    _require(str(raw["schema_version"]) in _SCHEMA_VERSIONS, "schema_version 必须为 1.0 或 1.1")

    nodes = tuple(_parse_node(n) for n in raw["nodes"])
    _require(len({n.node_id for n in nodes}) == len(nodes), "node_id 重复")
    edges = tuple(
        DecisionMapEdge(from_node=str(e["from_node"]), to_node=str(e["to_node"]), edge_type=str(e["edge_type"]))
        for e in raw["edges"]
    )
    sm = raw["state_matrix"]
    cells = tuple(
        TdmMatrixCell(
            node_id=str(c["node_id"]),
            state=str(c["state"]),
            mounted=tuple(str(x) for x in c.get("mounted", []) or []),
            confidence=str(c["confidence"]),
        )
        for c in sm.get("cells", []) or []
    )
    matrix = StateMatrix(states=tuple(str(s) for s in sm.get("states", []) or []), cells=cells)

    plan: PortfolioPlan | None = None
    if raw.get("portfolio_plan") is not None:
        pp = raw["portfolio_plan"]
        _require("plan_id" in pp, "portfolio_plan 缺 plan_id")
        sleeves = tuple(
            Sleeve(
                strategy_ref=str(s["strategy_ref"]),
                weight=float(s["weight"]),
                # v1.2：list→tuple（frozen dataclass 可哈希），str 原样
                activation_state=(
                    tuple(str(x) for x in s["activation_state"])
                    if isinstance(s.get("activation_state"), list)
                    else s.get("activation_state")
                ),
            )
            for s in pp.get("sleeves", []) or []
        )
        plan = PortfolioPlan(
            plan_id=str(pp["plan_id"]),
            name_zh=str(pp.get("name_zh", "")),
            confidence=str(pp.get("confidence", "proposed")),
            sleeves=sleeves,
            aggregator=dict(pp.get("aggregator", {}) or {}),
        )
    return DecisionMap(
        map_id=str(raw["map_id"]),
        schema_version=str(raw["schema_version"]),
        markets=tuple(str(m) for m in raw["markets"]),
        nodes=nodes,
        edges=edges,
        state_matrix=matrix,
        portfolio_plan=plan,
    )


def _load_registry_ids(registry_dir: Path, filename: str, section: str, key: str) -> frozenset[str]:
    """只读加载注册表条目键集合（REG-STR-001/REG-FCT-001/REG-DATAFLOW-001）。"""
    p = registry_dir / filename
    if not p.exists():
        return frozenset()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    entries = raw.get(section) or []
    return frozenset(str(e.get(key)) for e in entries if isinstance(e, dict) and e.get(key))


def _load_depgraph_entries(cache_path: Path) -> dict[str, dict[str, dict]] | None:
    """只读加载 depgraph 扫描缓存原始条目 {path: {content_hash: entry}}；缺失返回 None。

    缓存按 content_hash 累积多版本条目（增量扫描不清旧条目），现役条目由
    _resolve_mod_id 按当前文件 sha256 现算匹配（防陈旧 hash 遮蔽已治理的文件头）。
    """
    if not cache_path.exists():
        return None
    try:
        import json

        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    entries = data.get("entries") or {}
    return entries if isinstance(entries, dict) else {}


def _resolve_mod_id(entries: dict[str, dict[str, dict]], repo_root: Path, path: str) -> str | None:
    """解析 path 的现役 blueprint_id：优先匹配当前文件 sha256 的条目，回退首条；清洗 supplement 后缀。"""
    hashes = entries.get(path)
    if not isinstance(hashes, dict) or not hashes:
        return None
    entry: dict | None = None
    try:
        import hashlib

        actual = hashlib.sha256((repo_root / path).read_bytes()).hexdigest()
        entry = hashes.get(actual)
    except OSError:
        entry = None
    if entry is None:
        entry = next(iter(hashes.values()))
    if not isinstance(entry, dict) or not entry.get("blueprint_id"):
        return None
    bid = str(entry["blueprint_id"]).strip()
    # 清洗 "MOD-SIG-026 supplement" 类后缀 → MOD-SIG-026（辅助文件归属主模块）
    if not re.fullmatch(_MOD_ID_RE, bid):
        first = bid.split()[0] if bid.split() else ""
        if re.fullmatch(_MOD_ID_RE, first):
            bid = first
    return bid


def _collect_sequence_cycle(dm: DecisionMap) -> list[str]:
    """R8：sequence 边成环检测（DFS，返回环路径描述列表）。"""
    seq: dict[str, list[str]] = {}
    for e in dm.edges:
        if e.edge_type == "sequence":
            seq.setdefault(e.from_node, []).append(e.to_node)
    cycles: list[str] = []
    for start in seq:
        stack, path, found = [(start, [start])], set(), None
        while stack and not found:
            node, trail = stack.pop()
            for nxt in seq.get(node, []):
                if nxt == start:
                    found = " -> ".join([*trail, nxt])
                    break
                if nxt not in path:
                    stack.append((nxt, [*trail, nxt]))
                    path.add(nxt)
        if found:
            cycles.append(found)
    return cycles


def _validate_node_refs(
    n: DecisionMapNode,
    add,
    strat_ids: frozenset[str],
    factor_ids: frozenset[str],
    dataset_ids: frozenset[str],
    known_strategy_ids: frozenset[str] | None,
) -> None:
    """R1 枚举+layer 前缀 + R3/R4/R5 引用 + R6 置信度 + module_ref 缺口 warning。"""
    if n.market not in _MARKETS:
        add("error", "R1", n.node_id, f"market 非法: {n.market}")
    if n.flow not in _FLOWS:
        add("error", "R1", n.node_id, f"flow 非法: {n.flow}")
    if n.node_type not in _NODE_TYPES:
        add("error", "R1", n.node_id, f"node_type 非法: {n.node_type}")
    if n.point not in _POINTS:
        add("error", "R1", n.node_id, f"point 非法: {n.point}")
    # layer 前缀与 flow 一致性（二元：entry→L*/position→P*/exit→S*|X*/portfolio→C*；防复制粘贴错档）
    if n.flow == "exit_flow":
        prefix_ok = n.layer.startswith(("S", "X"))
    else:
        prefix_ok = n.layer.startswith(_LAYER_PREFIX_BY_FLOW.get(n.flow, "\0"))
    if not prefix_ok:
        add("error", "R1", n.node_id, f"layer 前缀与 flow 不一致: flow={n.flow} layer={n.layer}")
    # 缺口可视化：module_ref 缺失=warning（N2 需求：缺的东西自动浮出）
    if not n.module_ref:
        add("warning", "R1", n.node_id, "module_ref 缺失（环节无对应实现模块=红节点占位）")
    for f in n.factor_refs:
        if f not in factor_ids:
            add("error", "R4", n.node_id, f"factor_ref 不存在: {f}")
    for d in n.data_refs:
        if d not in dataset_ids:
            add("error", "R5", n.node_id, f"data_ref 不存在: {d}")
    for m in n.strategy_mounts:
        _validate_mount(m, n.node_id, add, strat_ids, known_strategy_ids)


def _validate_mount(
    m: StrategyMount,
    node_id: str,
    add,
    strat_ids: frozenset[str],
    known_strategy_ids: frozenset[str] | None,
) -> None:
    """R3 策略引用存在性（REG-STR-001 或代码 StrategyMeta）+ R6 置信度治理。"""
    in_registry = m.strategy_ref in strat_ids
    in_code = bool(known_strategy_ids) and m.strategy_ref in known_strategy_ids
    if not (in_registry or in_code):
        add(
            "error",
            "R3",
            node_id,
            f"strategy_ref 不存在: {m.strategy_ref}（REG-STR-001 与代码 StrategyMeta 均无）",
        )
    if m.confidence not in _CONFIDENCE:
        add("error", "R6", node_id, f"confidence 非法: {m.confidence}")
    elif m.confidence == "verified" and not m.evidence:
        add("error", "R6", node_id, f"verified 挂载缺 evidence: {m.strategy_ref}")


def _validate_edge(e: DecisionMapEdge, by_id: dict[str, DecisionMapNode], add) -> None:
    """R2 边端点存在性 + edge_type 枚举。"""
    if e.from_node not in by_id:
        add("error", "R2", e.from_node, f"边 from_node 不存在（→{e.to_node}）")
    if e.to_node not in by_id:
        add("error", "R2", e.to_node, f"边 to_node 不存在（←{e.from_node}）")
    if e.edge_type not in _EDGE_TYPES:
        add("error", "R2", e.from_node, f"edge_type 非法: {e.edge_type}")


def _validate_matrix_cell(
    c: TdmMatrixCell,
    dm: DecisionMap,
    add,
    strat_ids: frozenset[str],
    known_strategy_ids: frozenset[str] | None,
) -> None:
    """R7 矩阵格：引用环节/策略存在性 + state 在列轴 + confidence 枚举 + mounted ⊆ 节点挂载。"""
    node = {n.node_id: n for n in dm.nodes}.get(c.node_id)
    if node is None:
        add("error", "R7", c.node_id, "矩阵格引用环节不存在")
    if c.state not in dm.state_matrix.states:
        add("error", "R7", c.node_id, f"矩阵格 state 不在列轴: {c.state}")
    for s in c.mounted:
        known = s in strat_ids or (bool(known_strategy_ids) and s in known_strategy_ids)
        if not known:
            add("error", "R7", c.node_id, f"矩阵格 mounted 策略不存在: {s}")
        # mounted ⊆ 该环节 strategy_mounts（状态激活的必须是环节可挂载的子集，防两处漂移）
        if node is not None and s not in {m.strategy_ref for m in node.strategy_mounts}:
            add(
                "error",
                "R7",
                c.node_id,
                f"矩阵格 mounted {s} 不在该环节 strategy_mounts 中（先挂环节再进矩阵）",
            )
    if c.confidence not in _CONFIDENCE:
        add("error", "R7", c.node_id, f"矩阵格 confidence 非法: {c.confidence}")


def _validate_xrefs(n, xref_ids: dict[str, frozenset[str]], add) -> None:
    """R26-R33 八库交叉轴存在性+容量（表驱动：轴定义见 _XREF_SPECS）。"""
    for field, _fname, _sec, _key, code, lib_name in _XREF_SPECS:
        refs = getattr(n, field)
        if not refs:
            continue
        known = xref_ids.get(field)
        if known is None:  # 注册表缺失已由 R99 全局报 error，此处跳过防重复噪音
            continue
        for ref in refs:
            if ref not in known:
                add("error", code, n.node_id, f"{field} 不存在于{lib_name}: {ref}")
        cap = _XREF_MAX.get(field, 8)
        if len(refs) > cap:
            add("error", "R17", n.node_id, f"{field} {len(refs)} 个超上限 {cap}（该拆节点）")


def _validate_governance(
    dm: DecisionMap,
    registry_dir: Path,
    algo_ids: frozenset[str],
    add,
    emit_stats: bool = False,
    depgraph_entries: dict[str, dict[str, dict]] | None = None,
    xref_ids: dict[str, frozenset[str]] | None = None,
) -> None:
    """D32/D33/D34 门禁包：R13 算法引用 / R14 附件存在 / R15 治理字段 / R16 父子完整性+树宽 / R17 粒度+容量 / R18 命名唯一 / R19 模块存在 / R20 node_id 骨架 / R21 MOD 交叉锚 / R22 矩阵覆盖 / R23 流预算 / R24 因子欠账 / R25 空转叶子。"""
    by_id = {n.node_id: n for n in dm.nodes}

    # R18 name_zh 全图唯一（防同名歧义/防撞车延伸）
    seen_names: dict[str, str] = {}
    for n in dm.nodes:
        if n.name_zh in seen_names:
            add("error", "R18", n.node_id, f"name_zh 与 {seen_names[n.name_zh]} 重复: {n.name_zh}")
        else:
            seen_names[n.name_zh] = n.node_id

    # R14/R19 附件与模块存在性（相对仓库根；registry_dir=catalogs，parents[3]=仓库根）
    repo_root = registry_dir.parents[3]

    # R15/R17/R13/R14/R19/R20/R21 逐节点
    import re

    for n in dm.nodes:
        # R20 node_id 命名骨架（TDM-{流}-{层}-{序号}…；防小写/畸形/空段）
        if not re.fullmatch(_NODE_ID_RE, n.node_id):
            add("error", "R20", n.node_id, f"node_id 不符合 TDM-{{流}}-{{层}}-{{序号}} 骨架: {n.node_id}")
        for a in n.algo_refs:
            if a not in algo_ids:
                add("error", "R13", n.node_id, f"algo_ref 不存在于算法库（IND/EXA）: {a}")
        for rel_field, rel_val in (("doc_ref", n.doc_ref), ("module_ref", n.module_ref)):
            # V3 路径穿越/绝对路径拒绝（防 ../ 与盘符绕过仓库根）
            if rel_val and (Path(rel_val).is_absolute() or ".." in Path(rel_val).parts):
                add("error", "R14" if rel_field == "doc_ref" else "R19", n.node_id, f"{rel_field} 禁止绝对路径/上跳: {rel_val}")
        if n.doc_ref:
            rel = n.doc_ref.split("#", 1)[0]
            if rel and not (repo_root / rel).is_file():
                add("error", "R14", n.node_id, f"doc_ref 文件不存在（或非文件）: {rel}")
        if n.module_ref and not (repo_root / n.module_ref).is_file():
            add("error", "R19", n.node_id, f"module_ref 文件不存在（或非文件）: {n.module_ref}")
        # R21 MOD-* 交叉锚：格式校验 + 与 depgraph 缓存映射对账（现役 hash 条目）
        if n.module_id is not None and not re.fullmatch(_MOD_ID_RE, n.module_id):
            add("error", "R21", n.node_id, f"module_id 不符合 MOD-* 格式: {n.module_id}")
        if n.module_id and n.module_ref and depgraph_entries is not None:
            actual = _resolve_mod_id(depgraph_entries, repo_root, n.module_ref)
            if actual is not None and actual != n.module_id:
                add("error", "R21", n.node_id, f"module_id {n.module_id} 与 depgraph 缓存 {actual} 不一致（module_ref={n.module_ref}）")
        if n.module_ref and not n.module_id:
            add("warning", "R21", n.node_id, "有 module_ref 无 module_id（MOD-* 交叉锚欠账，五图对齐 key 缺失）")
        # R26-R33 八库交叉轴（表驱动）
        _validate_xrefs(n, xref_ids or {}, add)
        if n.activation is not None and n.activation not in _ACTIVATIONS:
            add("error", "R15", n.node_id, f"activation 非法: {n.activation}")
        if n.ai_autonomy is not None and n.ai_autonomy not in _AI_AUTONOMY:
            add("error", "R15", n.node_id, f"ai_autonomy 非法: {n.ai_autonomy}")
        # v1.5 节点（有 parent_node=新规范节点）治理字段必填；老节点 grandfather（有则校验）
        if n.parent_node:
            if n.activation is None:
                add("error", "R15", n.node_id, "v1.5 节点缺 activation（时效窗必填）")
            if n.ai_autonomy is None:
                add("error", "R15", n.node_id, "v1.5 节点缺 ai_autonomy（治理档位必填）")
        # R17 粒度门禁：一句话说清楚（长度上限+禁模糊词）
        if len(n.decision_question) > _MAX_QUESTION_LEN:
            add(
                "error",
                "R17",
                n.node_id,
                f"decision_question {len(n.decision_question)} 字超上限 {_MAX_QUESTION_LEN}（粒度过粗信号）",
            )
        for w in _VAGUE_WORDS:
            if w in n.decision_question:
                add("error", "R17", n.node_id, f"decision_question 含模糊词「{w}」（IF-THEN 粒度门禁）")
                break
        # R37 全景图可读性（Owner 2026-09-07 裁定）：大白话算法说明必填——无它读者看不懂"怎么算的"
        if not n.algo_note_zh.strip():
            add("error", "R37", n.node_id, "缺 algo_note_zh（大白话算法说明——含关键指标与阈值口径，全景图可读性门禁）")
        # D33 节点容量门禁：单节点承载上限（超出=粒度过粗，必须拆节点）
        if len(n.strategy_mounts) > _MAX_MOUNTS:
            add("error", "R17", n.node_id, f"strategy_mounts {len(n.strategy_mounts)} 个超上限 {_MAX_MOUNTS}（该拆环节）")
        if len(n.factor_refs) > _MAX_FACTOR_REFS:
            add("error", "R17", n.node_id, f"factor_refs {len(n.factor_refs)} 个超上限 {_MAX_FACTOR_REFS}")
        if len(n.data_refs) > _MAX_DATA_REFS:
            add("error", "R17", n.node_id, f"data_refs {len(n.data_refs)} 个超上限 {_MAX_DATA_REFS}")
        if len(n.algo_refs) > _MAX_ALGO_REFS:
            add("error", "R17", n.node_id, f"algo_refs {len(n.algo_refs)} 个超上限 {_MAX_ALGO_REFS}")

    # R16 父子存在性+环+深度（成环时跳过深度检查——环已报错，且深度计算在环上无定义）
    has_parent_cycle = False
    for n in dm.nodes:
        if n.parent_node and n.parent_node not in by_id:
            add("error", "R16", n.node_id, f"parent_node 不存在: {n.parent_node}")
    for n in dm.nodes:
        trail = {n.node_id}
        cur = n.parent_node
        while cur and cur in by_id:
            if cur in trail:
                add("error", "R16", n.node_id, f"parent 链成环（经过 {cur}）")
                has_parent_cycle = True
                break
            trail.add(cur)
            cur = by_id[cur].parent_node

    if not has_parent_cycle:
        depth_cache: dict[str, int] = {}

        def _depth(nid: str) -> int:
            if nid in depth_cache:
                return depth_cache[nid]
            node = by_id.get(nid)
            if node is None or not node.parent_node or node.parent_node not in by_id:
                depth_cache[nid] = 0
                return 0
            d = _depth(node.parent_node) + 1
            depth_cache[nid] = d
            return d

        for n in dm.nodes:
            if n.parent_node and n.parent_node in by_id:
                d = _depth(n.node_id)
                if d > _MAX_TREE_DEPTH:
                    add("error", "R16", n.node_id, f"树深度 {d} 超上限 {_MAX_TREE_DEPTH}")

    # R16b 树宽预警（warning 级）：单父节点子节点过多=该分层信号，不阻断
    children_count: dict[str, int] = {}
    for n in dm.nodes:
        if n.parent_node:
            children_count[n.parent_node] = children_count.get(n.parent_node, 0) + 1
    for pid, cnt in sorted(children_count.items()):
        if cnt > _WARN_CHILDREN:
            add("warning", "R16", pid, f"子节点 {cnt} 个超预警线 {_WARN_CHILDREN}（树宽过大，建议分层）")

    # R23 流预算（warning）：单流节点数超阈值=血肉膨胀信号，提示收口而非继续加
    by_flow: dict[str, int] = {}
    for n in dm.nodes:
        by_flow[n.flow] = by_flow.get(n.flow, 0) + 1
    anchor = dm.nodes[0].node_id if dm.nodes else ""
    for flow, cnt in sorted(by_flow.items()):
        if cnt > _MAX_NODES_PER_FLOW:
            add("warning", "R23", anchor, f"flow={flow} 节点数 {cnt} 超预算 {_MAX_NODES_PER_FLOW}（膨胀预警，考虑收口）")

    # R24 因子交叉欠账（warning）：挂策略的节点 factor_refs 空=因子链路断
    for n in dm.nodes:
        if n.strategy_mounts and not n.factor_refs:
            add("warning", "R24", n.node_id, "挂载策略但 factor_refs 为空（因子交叉索引欠账，血肉阶段补挂）")

    # R25 空转叶子（warning）：叶子节点（无人以它为 parent）且全引用轴皆空=决策断头路
    parented = {n.parent_node for n in dm.nodes if n.parent_node}
    for n in dm.nodes:
        if n.node_id in parented:
            continue
        no_refs = not (
            n.strategy_mounts
            or n.factor_refs
            or n.data_refs
            or n.algo_refs
            or n.module_ref
            or n.module_id
            or n.doc_ref
        )
        if no_refs:
            add("warning", "R25", n.node_id, "叶子节点无任何引用锚（空转节点：决策无落点也无交叉索引）")

    # R22 矩阵覆盖（warning）：挂策略的环节未进任何状态格子=状态路由断链
    mouted_nodes = {n.node_id for n in dm.nodes if n.strategy_mounts}
    covered_nodes = {c.node_id for c in dm.state_matrix.cells}
    for nid in sorted(mouted_nodes - covered_nodes):
        add("warning", "R22", nid, "挂载策略但未进任何状态矩阵格子（状态路由未覆盖）")

    # 粒度统计（info 级，emit_stats=True 时输出各 flow 节点数）
    if emit_stats:
        for flow, cnt in sorted(by_flow.items()):
            add("info", "R17", anchor, f"粒度统计 flow={flow}: {cnt} 节点")


def validate_decision_map(
    dm: DecisionMap,
    registry_dir: Path,
    known_strategy_ids: frozenset[str] | None = None,
    depgraph_cache: Path | None = None,
) -> tuple[bool, list[GapReportItem]]:
    """引用存在性+治理门禁校验（纯函数，R1-R25）→ (error 数为 0, GapReport 列表)。

    depgraph_cache：depgraph 扫描缓存路径（path→blueprint_id 映射，R21 对账用）；
    None=默认仓库根 .runtime/depgraph_scan_cache.json；缓存缺失记 warning 不硬阻断。
    """
    issues: list[GapReportItem] = []

    def add(level: str, code: str, node_id: str, detail: str) -> None:
        issues.append(GapReportItem(level=level, code=code, node_id=node_id, detail=detail))

    registry_dir = Path(registry_dir)
    # V1 注册表真源缺失=error（文件不存在时引用校验静默通过=假阴性漏洞）
    anchor0 = dm.nodes[0].node_id if dm.nodes else ""
    for fname in (_REG_STRATEGY, _REG_FACTOR, _REG_DATA, _REG_EXA, _REG_IND, *(spec[1] for spec in _XREF_SPECS)):
        if not (registry_dir / fname).exists():
            add("error", "R99", anchor0, f"注册表真源缺失: {fname}（引用校验不可信）")
    strat_ids = _load_registry_ids(registry_dir, _REG_STRATEGY, "strategies", "strategy_id")
    factor_ids = _load_registry_ids(registry_dir, _REG_FACTOR, "factors", "factor_id")
    dataset_ids = _load_registry_ids(registry_dir, _REG_DATA, "datasets", "dataset_id")
    by_id = {n.node_id: n for n in dm.nodes}

    # V4 空地图防御：空节点/空市场/空列轴=结构残缺，禁止静默全绿
    if not dm.nodes:
        add("error", "R98", "", "nodes 为空（空地图不可消费）")
    if not dm.markets:
        add("error", "R98", "", "markets 为空（市场分片声明缺失）")
    if not dm.state_matrix.states:
        add("error", "R98", anchor0, "状态矩阵列轴为空（六段情绪周期列轴缺失）")

    for n in dm.nodes:
        _validate_node_refs(n, add, strat_ids, factor_ids, dataset_ids, known_strategy_ids)
        # R10 市场实例一致性：节点的 market 必须在顶层 markets 声明内
        if n.market not in dm.markets:
            add("error", "R10", n.node_id, f"market {n.market} 不在顶层 markets 声明 {list(dm.markets)} 中")
    for e in dm.edges:
        _validate_edge(e, by_id, add)
    for c in dm.state_matrix.cells:
        _validate_matrix_cell(c, dm, add, strat_ids, known_strategy_ids)
    for path_desc in _collect_sequence_cycle(dm):
        add("error", "R8", dm.nodes[0].node_id if dm.nodes else "", f"sequence 边成环: {path_desc}")
    # R10b 每个声明市场必须有 ≥1 节点（防市场实例空壳漂移——空壳也按同 schema 长骨架）
    node_markets = {n.market for n in dm.nodes}
    for m in dm.markets:
        if m not in node_markets:
            add("error", "R10", dm.nodes[0].node_id if dm.nodes else "", f"声明市场 {m} 无任何节点")

    # D32/D33/D34 门禁包 R13-R25（算法/附件/治理/父子/粒度容量/命名/模块/node_id/交叉锚/矩阵/预算/欠账）
    exa_ids = _load_registry_ids(registry_dir, _REG_EXA, "execution_algos", "execution_algo_id")
    ind_ids = _load_registry_ids(registry_dir, _REG_IND, "indicators", "indicator_id")
    repo_root = registry_dir.parents[3]
    cache_path = depgraph_cache if depgraph_cache is not None else repo_root / _DEPGRAPH_CACHE
    depgraph_entries = _load_depgraph_entries(cache_path)
    if depgraph_entries is None:
        add("warning", "R21", anchor0, f"depgraph 扫描缓存缺失（{cache_path}）——MOD 对账降级为格式校验")
    # D36 八库交叉轴 ID 集合（表驱动加载）
    xref_ids: dict[str, frozenset[str]] = {
        field: _load_registry_ids(registry_dir, fname, sec, key)
        for field, fname, sec, key, _code, _lib in _XREF_SPECS
    }
    _validate_governance(
        dm, registry_dir, exa_ids | ind_ids, add,
        depgraph_entries=depgraph_entries, xref_ids=xref_ids,
    )

    # R12 整装方案（v1.1）：sleeve 引用存在性+权重范围+和≤1+activation_state 在列轴+置信度
    if dm.portfolio_plan is not None:
        plan = dm.portfolio_plan
        if plan.sleeves:
            weight_sum = 0.0
            seen_refs: set[str] = set()
            for s in plan.sleeves:
                known = s.strategy_ref in strat_ids or (
                    bool(known_strategy_ids) and s.strategy_ref in known_strategy_ids
                )
                if not known:
                    add("error", "R12", plan.plan_id, f"sleeve strategy_ref 不存在: {s.strategy_ref}")
                if s.strategy_ref in seen_refs:
                    add("error", "R12", plan.plan_id, f"sleeve 重复: {s.strategy_ref}")
                seen_refs.add(s.strategy_ref)
                if not (0 < s.weight <= 1.0):
                    add("error", "R12", plan.plan_id, f"sleeve {s.strategy_ref} weight 越界: {s.weight}")
                weight_sum += s.weight
                # v1.2：activation_state 支持 str 或 tuple[str, ...]（多状态激活）
                if s.activation_state is not None:
                    states_required = (
                        (s.activation_state,)
                        if isinstance(s.activation_state, str)
                        else tuple(s.activation_state)
                    )
                    for st in states_required:
                        if st not in dm.state_matrix.states:
                            add(
                                "error",
                                "R12",
                                plan.plan_id,
                                f"sleeve {s.strategy_ref} activation_state 不在列轴: {st}",
                            )
            if weight_sum > 1.0 + 1e-9:
                add("error", "R12", plan.plan_id, f"sleeve 权重总和 {weight_sum:.4f} > 1.0")
        if plan.confidence not in _CONFIDENCE:
            add("error", "R12", plan.plan_id, f"plan confidence 非法: {plan.confidence}")
        elif plan.confidence == "verified" and not plan.sleeves:
            add("error", "R12", plan.plan_id, "plan 标 verified 但无任何 sleeve 归因支撑")

    return (not any(i.level == "error" for i in issues), issues)
