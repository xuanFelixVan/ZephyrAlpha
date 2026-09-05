# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md
# [MODULE] zephyr.trading.decision_map
# [DOMAIN] D_TRADING
# [DEPENDENCIES] yaml（外部 PyYAML）；dataclasses;pathlib（stdlib）
# [CONSUMERS] V1 api_server 只读端点（规划中）；tests/trading/test_decision_map.py
# [STARTUP] imported（纯函数库，无常驻进程/无事件订阅）
# [MATURITY] production
# [INVARIANTS] INV-1 地图YAML不复制注册表条目只持稳定标识符引用; INV-2 load产出全frozen dataclass; INV-3 validate纯函数无副作用; INV-4 error=0才可被下游消费; INV-5 module_ref=null记warning不记error（V0缺口可视化输入）
# [MODIFY-GUARD] schema_version 变更必须同步升级 dataclasses+校验规则+测试（R1-R8）
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
#   intro: 引用存在性校验 R1-R8 → (ok, GapReport)；缺口即地图红节点语义
#   desc: R1 节点枚举; R2 边端点+类型+无环; R3 策略引用（STR-* 查 REG-STR-001，其余查 known_strategy_ids）; R4 因子引用 REG-FCT-001; R5 数据引用 REG-DATAFLOW-001 datasets; R6 置信度枚举+verified必带evidence; R7 矩阵格引用存在性; R8 sequence 边成环检测; module_ref=null 记 warning
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
    "GapReportItem",
    "DecisionMap",
    "load_decision_map",
    "validate_decision_map",
]

# ── 枚举常量（schema v1.0 词表）──────────────────────────────────────────────
_MARKETS = frozenset({"cn_a", "crypto"})
_FLOWS = frozenset({"entry_flow", "position_flow", "exit_flow"})
_NODE_TYPES = frozenset({"gate", "stage", "sensor", "aggregation", "cross_cutting"})
_POINTS = frozenset({"盘前", "盘中", "盘后", "持续"})
_EDGE_TYPES = frozenset({"feed", "sequence", "broadcast", "feedback"})
_CONFIDENCE = frozenset({"verified", "proposed", "untested"})

_REG_STRATEGY = "strategy_registry.yaml"
_REG_FACTOR = "factor_registry.yaml"
_REG_DATA = "data_asset_registry.yaml"


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
    """决策链节点（环节/传感器/聚合/横切）。"""

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
class DecisionMap:
    """交易决策地图（图谱存储：节点+边；视图=投影）。"""

    map_id: str
    schema_version: str
    markets: tuple[str, ...]
    nodes: tuple[DecisionMapNode, ...]
    edges: tuple[DecisionMapEdge, ...]
    state_matrix: StateMatrix


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
    )


def load_decision_map(path: Path) -> DecisionMap:
    """加载地图真源 YAML → frozen DecisionMap（结构错误抛 DecisionMapSchemaError）。"""
    path = Path(path)
    _require(path.exists(), f"地图真源不存在: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    _require(isinstance(raw, dict), "地图真源顶层必须是映射")
    for key in ("schema_version", "map_id", "markets", "nodes", "edges", "state_matrix"):
        _require(key in raw, f"地图真源缺顶层字段 {key}")
    _require(str(raw["schema_version"]) == "1.0", "schema_version 必须为 1.0")

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
    return DecisionMap(
        map_id=str(raw["map_id"]),
        schema_version=str(raw["schema_version"]),
        markets=tuple(str(m) for m in raw["markets"]),
        nodes=nodes,
        edges=edges,
        state_matrix=matrix,
    )


def _load_registry_ids(registry_dir: Path, filename: str, section: str, key: str) -> frozenset[str]:
    """只读加载注册表条目键集合（REG-STR-001/REG-FCT-001/REG-DATAFLOW-001）。"""
    p = registry_dir / filename
    if not p.exists():
        return frozenset()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    entries = raw.get(section) or []
    return frozenset(str(e.get(key)) for e in entries if isinstance(e, dict) and e.get(key))


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
    # layer 前缀与 flow 一致性（二元：entry→L*/position→P*/exit→S*|X*；防复制粘贴错档）
    prefix_ok = {
        "entry_flow": n.layer.startswith("L"),
        "position_flow": n.layer.startswith("P"),
        "exit_flow": n.layer.startswith(("S", "X")),
    }.get(n.flow, False)
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
    c: MatrixCell,
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


def validate_decision_map(
    dm: DecisionMap,
    registry_dir: Path,
    known_strategy_ids: frozenset[str] | None = None,
) -> tuple[bool, list[GapReportItem]]:
    """引用存在性校验（纯函数，R1-R8）→ (error 数为 0, GapReport 列表)。"""
    issues: list[GapReportItem] = []

    def add(level: str, code: str, node_id: str, detail: str) -> None:
        issues.append(GapReportItem(level=level, code=code, node_id=node_id, detail=detail))

    registry_dir = Path(registry_dir)
    strat_ids = _load_registry_ids(registry_dir, _REG_STRATEGY, "strategies", "strategy_id")
    factor_ids = _load_registry_ids(registry_dir, _REG_FACTOR, "factors", "factor_id")
    dataset_ids = _load_registry_ids(registry_dir, _REG_DATA, "datasets", "dataset_id")
    by_id = {n.node_id: n for n in dm.nodes}

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

    return (not any(i.level == "error" for i in issues), issues)
