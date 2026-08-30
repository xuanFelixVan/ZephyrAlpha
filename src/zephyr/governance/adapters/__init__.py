# [BLUEPRINT] MOD-L06-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_module] module_id=MOD-EXE-adapters | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# 5.93.6 修复：from ... import * → 显式导入（消除命名空间污染）
# 注：FillCallback 来自 broker_interface（simulation_broker.__all__ 不含 FillCallback）
# ARCH-GOV-SHIM-001 阶段2：broker_interface import 迁移至 canonical 路径
# 5.152 #9 sanctioned: governance(L2)->trading(L2) 同层契约依赖，层级模型允许。
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: BrokerInterface, FillCallback, RiskValidationBridge, RiskValidationPo…
#   code: __init__.py import L38
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BrokerInterface, FillCallback, RiskValidationBridge, RiskValidationPort, Ri…
#   desc: __init__ import L38；__all__ 6 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（6 符号）
#   name_en: __all__
#   intro: BrokerInterface, FillCallback, RiskValidationBridge, RiskValidationPort, RiskVi…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
