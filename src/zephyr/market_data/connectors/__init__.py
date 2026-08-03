# [BLUEPRINT] MOD-MKT-003 | docs/03_modules/_domain_mkt_data/connectors/blueprint.md
# [MODULE] zephyr.market_data.connectors
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_base; zephyr.shared.contracts.market_data; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.market_data.autoload; D_EX_SOR
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ConnectionState/ConnectorConfig/TickData frozen或Enum; MarketDataConnector为ABC; 状态转换+订阅注册表加Lock; callback异常隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConnectorError(ZA-MKT-0003)
# [TESTS] tests/market_data/connectors/test_connector_base.py; tests/market_data/connectors/test_connector_manager.py
# [A_module] module_id=MOD-MKT-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_MKT_DATA — Connectors (行情数据连接器)

MarketDataVendor 抽象基类的连接管理层扩展。增加连接生命周期管理
(connect/disconnect/reconnect) 和实时行情订阅(subscribe/unsubscribe/on_tick)。
ConnectorManager 统一管理多个连接器的生命周期。

属 A 类基础设施(连接框架), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-003
蓝图: docs/03_modules/_domain_mkt_data/connectors/blueprint.md
"""

from zephyr.market_data.connectors.base import (
    ConnectionState,
    ConnectorConfig,
    ConnectorError,
    MarketDataConnector,
    TickCallback,
    TickData,
)
from zephyr.market_data.connectors.manager import ConnectorManager

__all__ = [
    "ConnectionState",
    "ConnectorConfig",
    "ConnectorError",
    "ConnectorManager",
    "MarketDataConnector",
    "TickCallback",
    "TickData",
]
