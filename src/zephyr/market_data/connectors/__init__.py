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
"""

D_MKT_DATA — Connectors (行情数据连接器)

MarketDataVendor 抽象基类的连接管理层扩展。增加连接生命周期管理
(connect/disconnect/reconnect) 和实时行情订阅(subscribe/unsubscribe/on_tick)。
ConnectorManager 统一管理多个连接器的生命周期。

属 A 类基础设施(连接框架), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-003
蓝图: docs/03_modules/_domain_mkt_data/connectors/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: ConnectorConfig 连接配置
#   fields: endpoint/vendor_id/timeout_ms/reconnect_max_retries/params（frozen 不可变）
#   code: base.py ConnectorConfig L89
# - id: I2
#   name: TickData 实时行情快照
#   fields: symbol/price/volume/timestamp/bid/ask（frozen 不可变）
#   code: base.py TickData L108
# - id: I3
#   name: 订阅回调函数
#   fields: TickCallback = Callable[[TickData], None]
#   code: base.py L130 / subscribe() L279
# 层: 算法
# - id: A1
#   name_zh: ① 连接状态机
#   name_en: MarketDataConnector._transition
#   intro: 用白名单转换表守住 6 态连接状态机的合法跳转
#   desc: 6 态 _VALID_TRANSITIONS 白名单校验（base.py L63）；非法转换 raise ConnectorError(ZA-MKT-0003)；加 Lock 线程安全
#   inputs: I1
#   outputs: 当前 ConnectionState
#   invariant: 非法状态转换必抛异常
# - id: A2
#   name_zh: ② 连接生命周期管理
#   name_en: connect/disconnect/reconnect
#   intro: 按状态机执行建连/断连/重连并联动 vendor 状态
#   desc: connect: →CONNECTING→子类_do_connect→CONNECTED→set_status(ACTIVE)；disconnect 幂等且断开异常忽略；reconnect=断+连，失败置 ERROR
#   inputs: A1
#   outputs: 连接结果与 vendor 状态联动
# - id: A3
#   name_zh: ③ 实时订阅与行情分发
#   name_en: subscribe/unsubscribe/on_tick
#   intro: 管理 symbol→回调集合的订阅表并把行情快照分发给回调
#   desc: 订阅须 CONNECTED 状态；同 symbol 多回调 set 去重；on_tick 取快照后锁外调用，单回调异常隔离不影响其他
#   inputs: I2 I3 A2
#   outputs: 回调分发
#   invariant: callback 异常隔离
# - id: A4
#   name_zh: ④ 连接器批量管理
#   name_en: ConnectorManager
#   intro: 批量连接/断开/健康检查所有已注册连接器
#   desc: connect_all/disconnect_all/health_check_all 返回 {connector_id: bool}；单个失败记 False 不阻断；注销时锁外自动断开
#   inputs: A2
#   outputs: 批量操作结果映射
# 层: 输出
# - id: O1
#   name_zh: 连接状态与订阅行情分发
#   name_en: MarketDataConnector/ConnectorManager
#   intro: 统一连接生命周期与实时行情订阅框架，供执行层消费实时行情
#   downstream: autoload MOD-MKT-005；D_EX_SOR（#[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A3
# I3 --> A3
# A2 --> A3
# A2 --> A4
# A3 --> O1
# A4 --> O1
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
