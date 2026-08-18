# [BLUEPRINT] MOD-L06-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-EXE-adapters | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# 5.93.6 修复：from ... import * → 显式导入（消除命名空间污染）
# 注：FillCallback 来自 broker_interface（simulation_broker.__all__ 不含 FillCallback）
# ARCH-GOV-SHIM-001 阶段2：broker_interface import 迁移至 canonical 路径
# 5.152 #9 sanctioned: governance(L2)->trading(L2) 同层契约依赖，层级模型允许。
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface, FillCallback

from .risk_validation_bridge import RiskValidationBridge, RiskValidationPort, RiskViolation
from .simulation_broker import SimulationBroker

__all__ = [
    "BrokerInterface",
    "FillCallback",
    "RiskValidationBridge",
    "RiskValidationPort",
    "RiskViolation",
    "SimulationBroker",
]
