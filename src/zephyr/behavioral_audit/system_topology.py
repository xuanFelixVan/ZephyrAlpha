# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.system_topology
# [DOMAIN] D-BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-GATE_ENGINE;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_system_topology | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class CTrackLayer(str, Enum):
    L00_MARKET_DATA = "L00_MARKET_DATA"
    L01_FACTOR_FACTORY = "L01_FACTOR_FACTORY"
    L02_ALPHA_FACTORS = "L02_ALPHA_FACTORS"
    L03_PORTFOLIO_OPT = "L03_PORTFOLIO_OPT"
    L04_RISK_CONTROL = "L04_RISK_CONTROL"
    L05_ORDER_ROUTING = "L05_ORDER_ROUTING"
    L06_ORDER_EXECUTION = "L06_ORDER_EXECUTION"
    L07_SETTLEMENT = "L07_SETTLEMENT"
    L08_PERFORMANCE = "L08_PERFORMANCE"
    L09_MONITORING = "L09_MONITORING"
    L10_BACKTEST = "L10_BACKTEST"
    L11_CONFIG = "L11_CONFIG"
    L12_PERSISTENCE = "L12_PERSISTENCE"
    L13_EXPERIMENTATION = "L13_EXPERIMENTATION"


class BTrackSystem(str, Enum):
    SCRIPT_SYSTEM = "SCRIPT_SYSTEM"
    STATE = "STATE"
    STATE_MANAGEMENT = "STATE_MANAGEMENT"
    COMMUNICATION_LAYER = "COMMUNICATION_LAYER"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    GATE_CONTROLLER = "GATE_CONTROLLER"
    ORCHESTRATOR = "ORCHESTRATOR"
    FILE_WATCHER = "FILE_WATCHER"
    SESSION_MANAGER = "SESSION_MANAGER"
    TOKEN_BUDGETER = "TOKEN_BUDGETER"
    OBSERVABLE_STACK = "OBSERVABLE_STACK"
    EXPERIMENTATION = "EXPERIMENTATION"


class RuntimePlane(str, Enum):
    TASK_EXEC = "TASK_EXEC"
    KNOWLEDGE = "KNOWLEDGE"
    SECURITY = "SECURITY"
    FEEDBACK = "FEEDBACK"
    DATA = "DATA"


CTRACK_LABELS: dict[CTrackLayer, str] = {
    CTrackLayer.L00_MARKET_DATA: "市场数据",
    CTrackLayer.L01_FACTOR_FACTORY: "因子工厂",
    CTrackLayer.L02_ALPHA_FACTORS: "Alpha因子",
    CTrackLayer.L03_PORTFOLIO_OPT: "组合优化",
    CTrackLayer.L04_RISK_CONTROL: "风险控制",
    CTrackLayer.L05_ORDER_ROUTING: "订单路由",
    CTrackLayer.L06_ORDER_EXECUTION: "订单执行",
    CTrackLayer.L07_SETTLEMENT: "结算对账",
    CTrackLayer.L08_PERFORMANCE: "性能分析",
    CTrackLayer.L09_MONITORING: "监控告警",
    CTrackLayer.L10_BACKTEST: "回测引擎",
    CTrackLayer.L11_CONFIG: "配置中心",
    CTrackLayer.L12_PERSISTENCE: "数据持久化",
    CTrackLayer.L13_EXPERIMENTATION: "实验平台",
}

BTRACK_LABELS: dict[BTrackSystem, str] = {
    BTrackSystem.SCRIPT_SYSTEM: "Script System",
    BTrackSystem.STATE: "State",
    BTrackSystem.STATE_MANAGEMENT: "状态管理",
    BTrackSystem.COMMUNICATION_LAYER: "CommunicationLayer",
    BTrackSystem.KNOWLEDGE_BASE: "KnowledgeBase",
    BTrackSystem.GATE_CONTROLLER: "GateController",
    BTrackSystem.ORCHESTRATOR: "Orchestrator",
    BTrackSystem.FILE_WATCHER: "FileWatcher",
    BTrackSystem.SESSION_MANAGER: "SessionManager",
    BTrackSystem.TOKEN_BUDGETER: "TokenBudgeter",
    BTrackSystem.OBSERVABLE_STACK: "ObservableStack",
    BTrackSystem.EXPERIMENTATION: "Experimentation",
}

PLANE_LABELS: dict[RuntimePlane, str] = {
    RuntimePlane.TASK_EXEC: "任务执行平面",
    RuntimePlane.KNOWLEDGE: "知识平面",
    RuntimePlane.SECURITY: "安全平面",
    RuntimePlane.FEEDBACK: "反馈平面",
    RuntimePlane.DATA: "数据平面",
}


class LayerTopology(BaseModel):
    layer: CTrackLayer
    label: str
    index: int
    upstream_layers: list[CTrackLayer] = Field(default_factory=list)
    downstream_layers: list[CTrackLayer] = Field(default_factory=list)
    b_track_deps: list[BTrackSystem] = Field(default_factory=list)
    plane_assignments: list[RuntimePlane] = Field(default_factory=list)

    @property
    def is_source(self) -> bool:
        return len(self.upstream_layers) == 0

    @property
    def is_sink(self) -> bool:
        return len(self.downstream_layers) == 0


LAYER_GRAPH: dict[CTrackLayer, LayerTopology] = {
    CTrackLayer.L00_MARKET_DATA: LayerTopology(
        layer=CTrackLayer.L00_MARKET_DATA,
        label="市场数据",
        index=0,
        upstream_layers=[],
        downstream_layers=[CTrackLayer.L01_FACTOR_FACTORY],
        b_track_deps=[BTrackSystem.SCRIPT_SYSTEM, BTrackSystem.OBSERVABLE_STACK],
        plane_assignments=[RuntimePlane.DATA],
    ),
    CTrackLayer.L01_FACTOR_FACTORY: LayerTopology(
        layer=CTrackLayer.L01_FACTOR_FACTORY,
        label="因子工厂",
        index=1,
        upstream_layers=[CTrackLayer.L00_MARKET_DATA],
        downstream_layers=[CTrackLayer.L02_ALPHA_FACTORS],
        b_track_deps=[BTrackSystem.SCRIPT_SYSTEM, BTrackSystem.KNOWLEDGE_BASE],
        plane_assignments=[RuntimePlane.TASK_EXEC, RuntimePlane.DATA],
    ),
    CTrackLayer.L02_ALPHA_FACTORS: LayerTopology(
        layer=CTrackLayer.L02_ALPHA_FACTORS,
        label="Alpha因子",
        index=2,
        upstream_layers=[CTrackLayer.L01_FACTOR_FACTORY],
        downstream_layers=[CTrackLayer.L03_PORTFOLIO_OPT],
        b_track_deps=[BTrackSystem.KNOWLEDGE_BASE, BTrackSystem.TOKEN_BUDGETER],
        plane_assignments=[RuntimePlane.TASK_EXEC, RuntimePlane.KNOWLEDGE],
    ),
    CTrackLayer.L03_PORTFOLIO_OPT: LayerTopology(
        layer=CTrackLayer.L03_PORTFOLIO_OPT,
        label="组合优化",
        index=3,
        upstream_layers=[CTrackLayer.L02_ALPHA_FACTORS],
        downstream_layers=[CTrackLayer.L04_RISK_CONTROL, CTrackLayer.L05_ORDER_ROUTING],
        b_track_deps=[BTrackSystem.ORCHESTRATOR, BTrackSystem.STATE_MANAGEMENT],
        plane_assignments=[RuntimePlane.TASK_EXEC],
    ),
    CTrackLayer.L04_RISK_CONTROL: LayerTopology(
        layer=CTrackLayer.L04_RISK_CONTROL,
        label="风险控制",
        index=4,
        upstream_layers=[CTrackLayer.L03_PORTFOLIO_OPT],
        downstream_layers=[CTrackLayer.L05_ORDER_ROUTING],
        b_track_deps=[BTrackSystem.GATE_CONTROLLER, BTrackSystem.STATE],
        plane_assignments=[RuntimePlane.SECURITY, RuntimePlane.TASK_EXEC],
    ),
    CTrackLayer.L05_ORDER_ROUTING: LayerTopology(
        layer=CTrackLayer.L05_ORDER_ROUTING,
        label="订单路由",
        index=5,
        upstream_layers=[CTrackLayer.L03_PORTFOLIO_OPT, CTrackLayer.L04_RISK_CONTROL],
        downstream_layers=[CTrackLayer.L06_ORDER_EXECUTION],
        b_track_deps=[BTrackSystem.COMMUNICATION_LAYER, BTrackSystem.ORCHESTRATOR],
        plane_assignments=[RuntimePlane.TASK_EXEC],
    ),
    CTrackLayer.L06_ORDER_EXECUTION: LayerTopology(
        layer=CTrackLayer.L06_ORDER_EXECUTION,
        label="订单执行",
        index=6,
        upstream_layers=[CTrackLayer.L05_ORDER_ROUTING],
        downstream_layers=[CTrackLayer.L07_SETTLEMENT],
        b_track_deps=[BTrackSystem.GATE_CONTROLLER, BTrackSystem.COMMUNICATION_LAYER],
        plane_assignments=[RuntimePlane.TASK_EXEC, RuntimePlane.SECURITY],
    ),
    CTrackLayer.L07_SETTLEMENT: LayerTopology(
        layer=CTrackLayer.L07_SETTLEMENT,
        label="结算对账",
        index=7,
        upstream_layers=[CTrackLayer.L06_ORDER_EXECUTION],
        downstream_layers=[CTrackLayer.L08_PERFORMANCE],
        b_track_deps=[BTrackSystem.STATE_MANAGEMENT, BTrackSystem.OBSERVABLE_STACK],
        plane_assignments=[RuntimePlane.FEEDBACK, RuntimePlane.DATA],
    ),
    CTrackLayer.L08_PERFORMANCE: LayerTopology(
        layer=CTrackLayer.L08_PERFORMANCE,
        label="性能分析",
        index=8,
        upstream_layers=[CTrackLayer.L07_SETTLEMENT],
        downstream_layers=[CTrackLayer.L09_MONITORING, CTrackLayer.L10_BACKTEST],
        b_track_deps=[BTrackSystem.KNOWLEDGE_BASE, BTrackSystem.OBSERVABLE_STACK],
        plane_assignments=[RuntimePlane.FEEDBACK, RuntimePlane.KNOWLEDGE],
    ),
    CTrackLayer.L09_MONITORING: LayerTopology(
        layer=CTrackLayer.L09_MONITORING,
        label="监控告警",
        index=9,
        upstream_layers=[CTrackLayer.L08_PERFORMANCE],
        downstream_layers=[],
        b_track_deps=[BTrackSystem.OBSERVABLE_STACK, BTrackSystem.SESSION_MANAGER],
        plane_assignments=[RuntimePlane.FEEDBACK],
    ),
    CTrackLayer.L10_BACKTEST: LayerTopology(
        layer=CTrackLayer.L10_BACKTEST,
        label="回测引擎",
        index=10,
        upstream_layers=[CTrackLayer.L08_PERFORMANCE],
        downstream_layers=[],
        b_track_deps=[BTrackSystem.TOKEN_BUDGETER, BTrackSystem.KNOWLEDGE_BASE],
        plane_assignments=[RuntimePlane.TASK_EXEC, RuntimePlane.KNOWLEDGE],
    ),
    CTrackLayer.L11_CONFIG: LayerTopology(
        layer=CTrackLayer.L11_CONFIG,
        label="配置中心",
        index=11,
        upstream_layers=[],
        downstream_layers=[],
        b_track_deps=[BTrackSystem.STATE, BTrackSystem.SESSION_MANAGER],
        plane_assignments=[RuntimePlane.KNOWLEDGE],
    ),
    CTrackLayer.L12_PERSISTENCE: LayerTopology(
        layer=CTrackLayer.L12_PERSISTENCE,
        label="数据持久化",
        index=12,
        upstream_layers=[],
        downstream_layers=[],
        b_track_deps=[BTrackSystem.STATE, BTrackSystem.COMMUNICATION_LAYER],
        plane_assignments=[RuntimePlane.DATA],
    ),
    CTrackLayer.L13_EXPERIMENTATION: LayerTopology(
        layer=CTrackLayer.L13_EXPERIMENTATION,
        label="实验平台",
        index=13,
        upstream_layers=[CTrackLayer.L10_BACKTEST],
        downstream_layers=[],
        b_track_deps=[BTrackSystem.EXPERIMENTATION, BTrackSystem.ORCHESTRATOR],
        plane_assignments=[RuntimePlane.TASK_EXEC, RuntimePlane.FEEDBACK],
    ),
}


def get_layer(layer: CTrackLayer) -> LayerTopology | None:
    return LAYER_GRAPH.get(layer)


def get_layer_by_index(index: int) -> LayerTopology | None:
    for lt in LAYER_GRAPH.values():
        if lt.index == index:
            return lt
    return None


def get_upstream_chain(layer: CTrackLayer) -> list[CTrackLayer]:
    result: list[CTrackLayer] = []
    lt = get_layer(layer)
    if lt is None:
        return result
    for u in lt.upstream_layers:
        result.append(u)
        result.extend(get_upstream_chain(u))
    return result


def get_downstream_chain(layer: CTrackLayer) -> list[CTrackLayer]:
    result: list[CTrackLayer] = []
    lt = get_layer(layer)
    if lt is None:
        return result
    for d in lt.downstream_layers:
        result.append(d)
        result.extend(get_downstream_chain(d))
    return result


def layers_by_plane(plane: RuntimePlane) -> list[CTrackLayer]:
    return [lt.layer for lt in LAYER_GRAPH.values() if plane in lt.plane_assignments]


def btrack_systems_for_layer(layer: CTrackLayer) -> list[BTrackSystem]:
    lt = get_layer(layer)
    if lt is None:
        return []
    return list(lt.b_track_deps)


CTRACK_LAYER_COUNT: int = 14
BTRACK_SYSTEM_COUNT: int = 12
RUNTIME_PLANE_COUNT: int = 5
