# [BLUEPRINT] MOD-MKT-003 | docs/03_modules/_domain_mkt_data/connectors/blueprint.md
# [MODULE] zephyr.market_data.connectors.base
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_base; zephyr.shared.contracts.market_data; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.market_data.connectors.manager; D_EX_SOR
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ConnectionState/ConnectorConfig/TickData frozen或Enum; MarketDataConnector为ABC; 状态转换+订阅注册表加Lock; callback异常隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConnectorError(ZA-MKT-0003)
# [TESTS] tests/market_data/connectors/test_connector_base.py
# [A_module] module_id=MOD-MKT-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_MKT_DATA — Connector Base (行情数据连接器基类)

扩展 MarketDataVendor, 增加连接生命周期管理和实时行情订阅。
子类(具体厂商连接器)实现 _do_connect/_do_disconnect/fetch_daily_kline/health_check。

属 A 类基础设施(连接框架), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-003
蓝图: docs/03_modules/_domain_mkt_data/connectors/blueprint.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from threading import Lock
from typing import Any, Callable

from zephyr.market_data.vendor_base import MarketDataVendor, VendorStatus
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class ConnectorError(ZephyrBaseError):
    """连接器操作异常——非法状态转换/未连接/连接失败。"""

    error_code = "ZA-MKT-0003"


class ConnectionState(str, Enum):
    """连接状态——6级状态机。"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    RECONNECTING = "reconnecting"
    ERROR = "error"


# 合法状态转换表
_VALID_TRANSITIONS: dict[ConnectionState, frozenset[ConnectionState]] = {
    ConnectionState.DISCONNECTED: frozenset({ConnectionState.CONNECTING}),
    ConnectionState.CONNECTING: frozenset({ConnectionState.CONNECTED, ConnectionState.ERROR}),
    ConnectionState.CONNECTED: frozenset(
        {
            ConnectionState.DISCONNECTING,
            ConnectionState.RECONNECTING,
            ConnectionState.ERROR,
        }
    ),
    ConnectionState.DISCONNECTING: frozenset({ConnectionState.DISCONNECTED, ConnectionState.ERROR}),
    ConnectionState.RECONNECTING: frozenset({ConnectionState.CONNECTED, ConnectionState.ERROR}),
    ConnectionState.ERROR: frozenset({ConnectionState.CONNECTING, ConnectionState.DISCONNECTED}),
}


@dataclass(frozen=True)
class ConnectorConfig:
    """连接器配置——不可变。

    Attributes:
        endpoint: 连接端点(如 'tcp://127.0.0.1:7709' 或 API base URL)
        vendor_id: vendor 唯一标识
        timeout_ms: 连接/请求超时(毫秒)
        reconnect_max_retries: 重连最大重试次数
        params: 厂商特定参数(credentials/protocol 等)
    """

    endpoint: str
    vendor_id: str
    timeout_ms: int = 5000
    reconnect_max_retries: int = 3
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TickData:
    """实时行情快照——不可变。

    Attributes:
        symbol: 标的代码
        price: 最新价
        volume: 成交量
        timestamp: 行情时间(UTC)
        bid: 买一价(可选)
        ask: 卖一价(可选)
    """

    symbol: str
    price: Decimal
    volume: Decimal
    timestamp: datetime
    bid: Decimal | None = None
    ask: Decimal | None = None


# 实时行情回调类型
TickCallback = Callable[[TickData], None]


class MarketDataConnector(MarketDataVendor):
    """行情数据连接器抽象基类——扩展 MarketDataVendor。

    在 vendor_base 的数据获取接口之上增加:
      - 连接生命周期: connect/disconnect/reconnect + 状态机
      - 实时订阅: subscribe/unsubscribe/on_tick

    子类需实现:
      - vendor_id (property, 来自 config.vendor_id)
      - capabilities (property)
      - _do_connect(): 实际连接逻辑
      - _do_disconnect(): 实际断开逻辑
      - fetch_daily_kline(): 日K获取(继承自 vendor_base)
      - health_check(): 健康检查

    状态管理:
      - 初始状态 DISCONNECTED
      - connect() 转换 DISCONNECTED->CONNECTING->CONNECTED
      - disconnect() 转换 CONNECTED->DISCONNECTING->DISCONNECTED
      - 非法转换 raise ConnectorError

    Usage:
        class TushareConnector(MarketDataConnector):
            def _do_connect(self): ...  # 登录 API
            def _do_disconnect(self): ...
            def fetch_daily_kline(self, symbol, start, end): ...
            def health_check(self): return True

        conn = TushareConnector(ConnectorConfig(endpoint="...", vendor_id="tushare"))
        conn.connect()
        conn.subscribe("600000.SH", on_tick_callback)
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__()
        self._config = config
        self._conn_state: ConnectionState = ConnectionState.DISCONNECTED
        self._state_lock = Lock()
        # 订阅注册表: symbol -> set[callback]
        self._subscriptions: dict[str, set[TickCallback]] = {}
        self._sub_lock = Lock()

    @property
    def connection_state(self) -> ConnectionState:
        """当前连接状态(线程安全读取)。"""
        with self._state_lock:
            return self._conn_state

    @property
    def config(self) -> ConnectorConfig:
        """连接器配置(只读)。"""
        return self._config

    @property
    def vendor_id(self) -> str:
        """vendor ID(来自 config)。"""
        return self._config.vendor_id

    # ---- 连接生命周期 ----

    def connect(self) -> None:
        """建立连接。

        状态转换: DISCONNECTED/ERROR -> CONNECTING -> CONNECTED
        调用子类 _do_connect() 执行实际连接逻辑。
        连接成功后 set_status(ACTIVE)。

        Raises:
            ConnectorError: 当前状态不允许 connect / 连接失败
        """
        self._transition(ConnectionState.CONNECTING)
        try:
            self._do_connect()
        except Exception as e:
            self._transition(ConnectionState.ERROR)
            raise ConnectorError(
                f"连接失败: {self.vendor_id}: {e}",
                details={"vendor_id": self.vendor_id, "error": str(e)},
            ) from e
        self._transition(ConnectionState.CONNECTED)
        self.set_status(VendorStatus.ACTIVE)
        _logger.info("连接器已连接: %s", self.vendor_id)

    def disconnect(self) -> None:
        """断开连接。

        状态转换: CONNECTED/RECONNECTING/ERROR -> DISCONNECTING -> DISCONNECTED
        调用子类 _do_disconnect() 执行实际断开逻辑。
        断开后 set_status(INACTIVE)。
        """
        if self.connection_state == ConnectionState.DISCONNECTED:
            return  # 幂等
        # 允许从 ERROR/RECONNECTING 直接断开
        if self.connection_state not in (
            ConnectionState.CONNECTED,
            ConnectionState.RECONNECTING,
            ConnectionState.ERROR,
        ):
            raise ConnectorError(
                f"当前状态 {self.connection_state.value} 不允许 disconnect",
                details={
                    "vendor_id": self.vendor_id,
                    "state": self.connection_state.value,
                },
            )
        self._transition(ConnectionState.DISCONNECTING)
        try:
            self._do_disconnect()
        except Exception:
            _logger.exception("断开连接异常(忽略): %s", self.vendor_id)
        finally:
            self._transition(ConnectionState.DISCONNECTED)
            self.set_status(VendorStatus.INACTIVE)
            _logger.info("连接器已断开: %s", self.vendor_id)

    def reconnect(self) -> None:
        """重连——disconnect() + connect()。

        状态转换: CONNECTED -> RECONNECTING -> CONNECTED
        """
        prev = self.connection_state
        if prev != ConnectionState.CONNECTED:
            raise ConnectorError(
                f"当前状态 {prev.value} 不允许 reconnect(需 CONNECTED)",
                details={"vendor_id": self.vendor_id, "state": prev.value},
            )
        self._transition(ConnectionState.RECONNECTING)
        try:
            self._do_disconnect()
        except Exception:
            _logger.exception("重连-断开异常(忽略): %s", self.vendor_id)
        try:
            self._do_connect()
        except Exception as e:
            self._transition(ConnectionState.ERROR)
            self.set_status(VendorStatus.ERROR)
            raise ConnectorError(
                f"重连失败: {self.vendor_id}: {e}",
                details={"vendor_id": self.vendor_id, "error": str(e)},
            ) from e
        self._transition(ConnectionState.CONNECTED)
        self.set_status(VendorStatus.ACTIVE)
        _logger.info("连接器重连成功: %s", self.vendor_id)

    # ---- 实时订阅 ----

    def subscribe(self, symbol: str, callback: TickCallback) -> None:
        """订阅实时行情。

        - 必须在 CONNECTED 状态调用, 否则 raise ConnectorError
        - 同一 symbol 可注册多个 callback
        - 重复注册同一 callback 忽略(set 去重)

        Args:
            symbol: 标的代码
            callback: 行情回调函数

        Raises:
            ConnectorError: 未连接 / symbol 为空
        """
        if not symbol:
            raise ConnectorError("symbol 不能为空")
        if self.connection_state != ConnectionState.CONNECTED:
            raise ConnectorError(
                f"订阅需 CONNECTED 状态(当前: {self.connection_state.value})",
                details={
                    "vendor_id": self.vendor_id,
                    "state": self.connection_state.value,
                    "symbol": symbol,
                },
            )
        with self._sub_lock:
            self._subscriptions.setdefault(symbol, set()).add(callback)
        _logger.info(
            "订阅: %s -> %s (回调数=%d)",
            self.vendor_id,
            symbol,
            len(self._subscriptions[symbol]),
        )

    def unsubscribe(self, symbol: str, callback: TickCallback | None = None) -> int:
        """退订实时行情。

        Args:
            symbol: 标的代码
            callback: 指定退订的回调; None=退订该 symbol 的所有回调

        Returns:
            退订的回调数量
        """
        with self._sub_lock:
            if symbol not in self._subscriptions:
                return 0
            if callback is None:
                count = len(self._subscriptions.pop(symbol))
            else:
                callbacks = self._subscriptions[symbol]
                removed = callback in callbacks
                callbacks.discard(callback)
                count = 1 if removed else 0
                if not callbacks:
                    self._subscriptions.pop(symbol, None)
        if count:
            _logger.info("退订: %s -> %s (退订 %d 个回调)", self.vendor_id, symbol, count)
        return count

    def on_tick(self, tick: TickData) -> None:
        """收到实时行情时调用——分发给已注册的回调。

        - 未订阅的 symbol 忽略
        - 单个 callback 异常被捕获记录, 不影响其他 callback
        - 线程安全: 取出回调快照后释放锁再调用

        Args:
            tick: 实时行情数据
        """
        with self._sub_lock:
            callbacks = list(self._subscriptions.get(tick.symbol, ()))
        if not callbacks:
            return
        for cb in callbacks:
            try:
                cb(tick)
            except Exception:
                _logger.exception(
                    "回调异常(已隔离): %s symbol=%s callback=%s",
                    self.vendor_id,
                    tick.symbol,
                    getattr(cb, "__name__", repr(cb)),
                )

    @property
    def subscription_count(self) -> int:
        """已订阅的 symbol 数量。"""
        with self._sub_lock:
            return len(self._subscriptions)

    # ---- 子类实现的抽象方法 ----

    def _do_connect(self) -> None:
        """实际连接逻辑——子类实现(登录 API/建立 TCP 等)。"""
        ...

    def _do_disconnect(self) -> None:
        """实际断开逻辑——子类实现(登出/关闭 socket 等)。"""
        ...

    @property
    def capabilities(self):  # type: ignore[override]
        """能力声明——子类实现。"""
        ...

    def fetch_daily_kline(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> list[NormalizedMarketData]:
        """日K获取——子类实现。必须在 CONNECTED 状态调用。"""
        if self.connection_state != ConnectionState.CONNECTED:
            raise ConnectorError(
                f"fetch 需 CONNECTED 状态(当前: {self.connection_state.value})",
                details={
                    "vendor_id": self.vendor_id,
                    "state": self.connection_state.value,
                },
            )
        raise NotImplementedError("子类必须实现 fetch_daily_kline")

    def health_check(self) -> bool:
        """健康检查——连接状态为 CONNECTED 且 vendor 健康。"""
        return self.connection_state == ConnectionState.CONNECTED

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(vendor_id={self.vendor_id!r}, "
            f"conn={self.connection_state.value}, "
            f"vendor_status={self.status.value})"
        )

    # ---- 内部方法 ----

    def _transition(self, target: ConnectionState) -> None:
        """状态转换(线程安全)。非法转换 raise ConnectorError。"""
        with self._state_lock:
            current = self._conn_state
            allowed = _VALID_TRANSITIONS.get(current, frozenset())
            if target not in allowed and current != target:
                raise ConnectorError(
                    f"非法状态转换: {current.value} -> {target.value}(合法: {[s.value for s in allowed] or '无'})",
                    details={
                        "vendor_id": self.vendor_id,
                        "from": current.value,
                        "to": target.value,
                    },
                )
            self._conn_state = target


__all__ = [
    "ConnectionState",
    "ConnectorConfig",
    "ConnectorError",
    "MarketDataConnector",
    "TickCallback",
    "TickData",
]
