# [BLUEPRINT] MOD-EX-057 | docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md
# [MODULE] zephyr.ex_core.sim_saga_assembly
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_execution_saga; zephyr.ex_core.saga_compensation_registry; zephyr.ex_core.order_manager; zephyr.ex_core.position_tracker.tracker; zephyr.ex_core.audit_journal.auditor; zephyr.ex_core.cancel_rate_guard; zephyr.ex_core.programmatic_trading_guard; zephyr.governance.adapters.simulation_broker; zephyr.governance.adapters.risk_validation_bridge; zephyr.risk.implementations.default_risk_validator; zephyr.compliance.compliance_report_registry; zephyr.compliance.manipulation_realtime_monitor; zephyr.compliance.info_asymmetry_manipulation_detector
# [CONSUMERS] 模拟盘面调用方（env='sim' 开箱装配入口；实盘接线=OWNER-GATE 不在本模块）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] environment!='sim' 一律拒绝装配（fail-closed，实盘接线=OWNER-GATE 留 Owner）;OrderManager 构造必注入五合规件（ReportGate/CancelRateGuard/ManipulationRealtimeMonitor/ProgrammaticTradingGuard(SIMULATION)/InfoAsymmetryManipulationDetector——零裸构造，F62 同口径）;broker 缺省=SimulationBroker（真模拟件，不实连）;state_store 透传 DefaultRiskValidator（None=内存态，测试零生产路径写入）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SimAssemblyEnvError（env 非法拒绝装配）
# [TESTS] tests/ex_core/test_sim_saga_assembly.py
# [A_module] module_id=MOD-EX-057-R2 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# create-guard-not-dup: 模拟盘 Saga 开箱装配入口（F53 案卷，env=sim 专用不含实盘路径），与 switch_engine/translator 类装配或切换能力无同源关系
# [TTL] permanent

"""

Sim Saga Assembly — Saga 模拟盘面开箱装配入口 (MOD-EX-057-R2 / F53 夜战批)

背景（F53 案卷：Saga 零生产调用方 + 总筹裁定）: OrderExecutionSaga 六步编排器
本体已建成（894 行+68 用例）但无装配入口，模拟盘面无法开箱使用。总筹裁定：
**只做 Saga 编排器本体（模拟盘面 env='sim' 可用），不做实盘切换**——实盘接线
（TradingSession 切 Saga）=OWNER-GATE 留 Owner，本模块物理上不提供该路径。

职责:
    build_sim_saga(...) 一站式装配模拟盘 Saga 栈：
        SimulationBroker + OrderManager（五合规件注入，零裸构造）+
        PositionTracker + ExecutionAuditLogger + DefaultRiskValidator 桥 +
        补偿动作注册表（空表，供调用方按需 register）+ OrderExecutionSaga。

红线:
    - environment 参数只接受 "sim"：任何其他值（含 "live"/"prod"/"paper"）
      抛 SimAssemblyEnvError（fail-closed，防本入口被挪作实盘装配捷径）。
    - OrderManager 构造必带五合规件（F62 P0 口径：SIMULATION 模式豁免语义
      =模拟盘天然放行、零行为变化；模式一旦 LIVE 且未报备即拒发保险丝）。

SSoT: depgraph MOD-EX-057-R2
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/order_execution_saga.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Final

from zephyr.compliance.compliance_report_registry import ReportGate
from zephyr.compliance.info_asymmetry_manipulation_detector import (
    InfoAsymmetryManipulationDetector,
)
from zephyr.compliance.manipulation_realtime_monitor import ManipulationRealtimeMonitor
from zephyr.ex_core.audit_journal.auditor import ExecutionAuditLogger
from zephyr.ex_core.cancel_rate_guard import CancelRateGuard
from zephyr.ex_core.order_execution_saga import (
    OrderExecutionSaga,
    SagaConfig,
)
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.ex_core.programmatic_trading_guard import (
    ProgrammaticTradingGuard,
    ProgrammaticTradingGuardConfig,
    TradingMode,
)
from zephyr.ex_core.saga_compensation_registry import SagaCompensationRegistry
from zephyr.governance.adapters.risk_validation_bridge import RiskValidationBridge
from zephyr.governance.adapters.simulation_broker import SimulationBroker
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.state_store import JsonStateStore

__all__: Final = [
    "SIM_ENV",
    "SimAssemblyEnvError",
    "SimSagaStack",
    "build_sim_saga",
]

#: 唯一放行的运行环境（fail-closed 白名单）
SIM_ENV: Final = "sim"

_BROKER_ID: Final = "simulation"


@dataclass
class SimSagaDeps:
    """可选依赖五柄打包（NO-LONG-PARAM-LIST 治本：参数对象替代 9 参签名）。

    全部缺省 None=内建默认件（内存态/默认目录）；测试注入自定义件用本对象。
    """

    broker: SimulationBroker | None = None
    audit_logger: ExecutionAuditLogger | None = None
    state_store: JsonStateStore | None = None
    state_dir: Path | str | None = None
    signal_confirmer: object | None = None


class SimAssemblyEnvError(Exception):
    """装配环境非法（非 sim 环境拒绝——实盘接线=OWNER-GATE，不走本入口）。"""


@dataclass(frozen=True)
class SimSagaStack:
    """装配完成的模拟盘 Saga 栈（组件只读暴露，供调用方喂单/查账）。"""

    saga: OrderExecutionSaga
    order_manager: OrderManager
    broker: SimulationBroker
    position_tracker: PositionTracker
    audit_logger: ExecutionAuditLogger
    compensation_registry: SagaCompensationRegistry
    risk_validator: DefaultRiskValidator
    broker_id: str


def build_sim_saga(
    environment: str = SIM_ENV,
    initial_cash: Decimal = Decimal("1000000"),
    portfolio_id: str = "sim-saga-book",
    config: SagaConfig | None = None,
    deps: SimSagaDeps | None = None,
) -> SimSagaStack:
    """一站式装配模拟盘 Saga 栈（env='sim' fail-closed）。

    Args:
        environment: 运行环境，只接受 "sim"（默认）；其他值一律拒绝。
        initial_cash: 模拟盘初始资金（透传 SimulationBroker/PositionTracker）。
        portfolio_id: 持仓账本组合标识。
        deps: 可选依赖五柄（SimSagaDeps：broker/audit_logger/state_store/
            state_dir/signal_confirmer；None=全内建默认）。
        config: Saga 配置（None=默认 ≤5s 超时 + broker_id=simulation）。

    Returns:
        SimSagaStack（frozen，组件已互连：broker 已注册进 OrderManager，
       操纵监视器已 attach）。

    Raises:
        SimAssemblyEnvError: environment != "sim"。
    """
    if environment != SIM_ENV:
        raise SimAssemblyEnvError(
            f"build_sim_saga 只接受 environment={SIM_ENV!r}（实盘接线=OWNER-GATE，不经本入口；got {environment!r}）"
        )

    d = deps or SimSagaDeps()

    # ── 模拟券商（真模拟件，不实连） ──
    broker = d.broker
    if broker is None:
        broker = SimulationBroker(initial_cash=initial_cash)
    # 开箱可用语义：装配即连接（SimulationBroker.connect 纯内存置位，零外部副作用；
    # 未连接时 submit_order 直接拒单——模拟盘装配入口不该交付一只"必拒单"的栈）
    broker.connect()

    # ── 五合规件（F62 同口径，零裸构造；SIMULATION 豁免语义=模拟盘天然放行） ──
    registration_guard = ProgrammaticTradingGuard(
        config=ProgrammaticTradingGuardConfig(
            mode=TradingMode.SIMULATION,
            live_broker_ids={_BROKER_ID},
        ),
    )
    manipulation_monitor = ManipulationRealtimeMonitor()
    order_manager = OrderManager(
        report_gate=ReportGate(),
        declaration_guard=CancelRateGuard(),
        manipulation_monitor=manipulation_monitor,
        registration_guard=registration_guard,
        avoidance_detector=InfoAsymmetryManipulationDetector(),
    )
    manipulation_monitor.attach_order_manager(order_manager)
    order_manager.register_broker(_BROKER_ID, broker)

    # ── 持仓账本 + 审计 + 风控桥 ──
    position_tracker = PositionTracker(initial_cash=initial_cash, portfolio_id=portfolio_id)
    audit = d.audit_logger or ExecutionAuditLogger()
    state_store = d.state_store
    if state_store is None and d.state_dir is not None:
        state_store = JsonStateStore(d.state_dir)
    validator = DefaultRiskValidator(state_store=state_store)
    risk_bridge = RiskValidationBridge(validator)

    # ── 补偿注册表（空表开箱，调用方按需 register）+ Saga ──
    compensation_registry = SagaCompensationRegistry()
    saga = OrderExecutionSaga(
        order_manager=order_manager,
        risk_validator=risk_bridge,
        position_tracker=position_tracker,
        audit_logger=audit,
        broker=broker,
        broker_id=_BROKER_ID,
        config=config or SagaConfig(broker_id=_BROKER_ID),
        signal_confirmer=d.signal_confirmer,
        compensation_registry=compensation_registry,
    )
    return SimSagaStack(
        saga=saga,
        order_manager=order_manager,
        broker=broker,
        position_tracker=position_tracker,
        audit_logger=audit,
        compensation_registry=compensation_registry,
        risk_validator=validator,
        broker_id=_BROKER_ID,
    )


def submit_sim_order(stack: SimSagaStack, order, side: OrderSide = OrderSide.BUY):
    """便捷入口：在已装配栈上执行单笔 Saga（返回 SagaResult）。

    独立函数而非栈方法：保持 SimSagaStack 为纯数据载体（frozen），
    行为只存在于 OrderExecutionSaga（单一编排真源）。
    """
    return stack.saga.execute(order, side)


if __name__ == "__main__":  # ORPHAN-MODULE 入口豁免形态：装配入口自检（env=sim fail-closed，只装配不下单）
    stack = build_sim_saga()
    print(
        f"sim saga assembled ok: broker_id={stack.broker_id} components=saga/order_manager/broker/position_tracker/audit/compensation_registry/risk_validator"
    )
