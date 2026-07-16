# [A_module] module_id=MOD-EXE_adapters | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 5.93.6 修复：from ... import * → 显式导入（消除命名空间污染）
# 注：FillCallback 来自 broker_interface（simulation_broker.__all__ 不含 FillCallback）
# ARCH-GOV-SHIM-001 阶段2：broker_interface import 迁移至 canonical 路径
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
