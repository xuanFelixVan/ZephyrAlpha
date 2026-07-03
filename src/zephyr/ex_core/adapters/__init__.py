# [A_module] module_id=MOD-EXE_adapters | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""Re-export wrapper: adapters has migrated to zephyr.execution_core.core.adapters"""

from zephyr.governance.trading_contracts.broker_interface import BrokerInterface, FillCallback
from zephyr.governance.adapters.risk_validation_bridge import (
    RiskValidationBridge,
    RiskValidationPort,
    RiskViolation,
)
from zephyr.governance.adapters.simulation_broker import SimulationBroker

# v2.2.0 新增 MiniQMT 实盘券商适配器（try/except 避免循环导入阻断整个包）
try:
    from zephyr.ex_core.adapters.miniqmt_broker import (
        MiniQmtBroker,
        MiniQmtBrokerError,
        XTTRADER_ERROR_CODES,
    )
except ImportError:
    MiniQmtBroker = None  # type: ignore[assignment,misc]
    MiniQmtBrokerError = None  # type: ignore[assignment,misc]
    XTTRADER_ERROR_CODES = {}  # type: ignore[assignment]

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
