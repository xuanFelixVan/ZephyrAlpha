# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.adapters
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.trading.trading_contracts.broker_interface; zephyr.governance.adapters.risk_validation_bridge; zephyr.governance.adapters.simulation_broker; zephyr.ex_core.adapters.miniqmt_broker
# [CONSUMERS] zephyr.ex_core.execution_engine; zephyr.ex_core.order_manager
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_EX_CORE adapters — 券商/风控适配器 re-export wrapper

聚合 trading.trading_contracts.broker_interface、governance.adapters.* 与
ex_core.adapters.miniqmt_broker，提供统一 import 入口。

真源: trading.trading_contracts.broker_interface（BrokerInterface 契约真源）
      ex_core.adapters.miniqmt_broker（MiniQmtBroker 实现真源）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 券商接口契约符号
#   fields: BrokerInterface/FillCallback（契约真源）
#   code: zephyr.trading.trading_contracts.broker_interface (adapters/__init__.py L27)
# - id: I2
#   name: 风控校验桥接符号
#   fields: RiskValidationBridge/RiskValidationPort/RiskViolation
#   code: zephyr.governance.adapters.risk_validation_bridge (adapters/__init__.py L28-32)
# - id: I3
#   name: 模拟券商 SimulationBroker
#   fields: 仿真券商实现
#   code: zephyr.governance.adapters.simulation_broker (adapters/__init__.py L33)
# - id: I4
#   name: MiniQMT 实盘券商适配器符号
#   fields: MiniQmtBroker/MiniQmtBrokerError/XTTRADER_ERROR_CODES
#   code: zephyr.ex_core.adapters.miniqmt_broker (adapters/__init__.py L37-41)
# 层: 算法
# - id: A1
#   name_zh: ① 适配器符号聚合 re-export
#   name_en: ex_core.adapters 统一入口
#   intro: 把券商契约/风控桥/模拟券商/MiniQMT聚成统一import入口，免去记canonical路径
#   desc: 直接import各真源符号并列入__all__（9个符号）（L27-58）
#   inputs: I1 I2 I3
#   outputs: __all__ 9个导出符号
# - id: A2
#   name_zh: ② MiniQMT 直接导入（Fail-Fast）
#   name_en: 直接导入（2026-08-17 拆除 try/except None 兜底）
#   intro: 历史循环导入已消除，直接导入让真实导入错误立即暴露而非静默置None
#   desc: 直接导入 MiniQmtBroker 三符号（miniqmt_broker 对 xtquant 懒加载，模块导入零外部依赖）（L86-94）
#   inputs: I4
#   outputs: MiniQMT符号
# 层: 输出
# - id: O1
#   name_zh: 统一适配器入口 __all__
#   name_en: __all__
#   intro: 9个符号（BrokerInterface/FillCallback/风控桥三件套/SimulationBroker/MiniQMT三件套）供执行核心统一导入
#   downstream: zephyr.ex_core.execution_engine / zephyr.ex_core.order_manager
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A2
# A2 --> A1
# A1 --> O1
"""

# ARCH-GOV-SHIM-001 阶段2：broker_interface import 迁移至 canonical 路径
# v2.2.0 新增 MiniQMT 实盘券商适配器。
# 2026-08-17 治本：原 try/except ImportError 置 None 兜底拆除——历史循环导入
# 已消除（miniqmt_broker 对 xtquant 为懒加载，模块导入无外部依赖），静默 None
# 会掩盖真实导入错误（调用方晚发现 AttributeError），Fail-Fast 直接导入。
from zephyr.ex_core.adapters.miniqmt_broker import (
    XTTRADER_ERROR_CODES,
    MiniQmtBroker,
    MiniQmtBrokerError,
)
from zephyr.governance.adapters.risk_validation_bridge import (
    RiskValidationBridge,
    RiskValidationPort,
    RiskViolation,
)
from zephyr.governance.adapters.simulation_broker import SimulationBroker
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface, FillCallback

__all__ = [
    "BrokerInterface",
    "FillCallback",
    "RiskValidationBridge",
    "RiskValidationPort",
    "RiskViolation",
    "SimulationBroker",
    # v2.2.0 新增
    "MiniQmtBroker",
    "MiniQmtBrokerError",
    "XTTRADER_ERROR_CODES",
]
