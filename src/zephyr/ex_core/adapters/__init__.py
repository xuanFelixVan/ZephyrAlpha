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

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/adapters__init__.yaml
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
