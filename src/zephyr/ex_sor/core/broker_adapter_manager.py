# [BLUEPRINT] MOD-XS-002 | docs/03_modules/_domain-ex_sor/broker_adapter_manager/blueprint.md
# [MODULE] zephyr.ex_sor.core.broker_adapter_manager
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.contracts.fill; zephyr.shared.foundation.errors; zephyr.ex_sor.api.broker_api_connector; zephyr.ex_sor.api.api_rate_limiter
# [CONSUMERS] MOD-XS-001(Optimal Order Router,路由后下单) ; MOD-EX-CORE(OMS,Fill回调链)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 适配器只做协议转换不含业务逻辑; Fill通过回调链传递至D-EX-CORE; 运行时券商切换零中断(Feature Toggle); 故障转移自动(不同于同券商熔断需人工恢复HB-06)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BrokerAdapterError; NoAvailableBrokerError; FailoverExhaustedError
# [TESTS] tests/ex_sor/test_broker_adapter_manager.py
# [A_module] module_id=MOD-XS-002 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Broker Adapter Manager — 多券商统一适配器 (MOD-XS-002)

D-EX-SOR §2.2 XS-02: 多券商API统一适配 + 接口抽象 + 事务一致性 + 连接熔断 + 故障转移。

职责分层 (与 XS-13 区分):
    XS-13 = 协议/传输层: 单券商连接管理 + 心跳 + 序列化 + 重连 + 限速
    XS-02 = 适配/业务层:  多券商管理 + 故障转移 + Feature Toggle + Fill回调链

关键设计 (D-EX-SOR §6):
    §6.5  券商切换零中断: 运行时切换券商 (Feature Toggle), 不重启服务
    §6.7  交易通道熔断必须人工恢复 (HB-06): 同一券商熔断需 manual_reset_circuit
          但故障转移到备选券商是自动的 (不同于同券商恢复)
    HB-07 下单零重试: 适配器层不重试, 熔断后自动故障转移到备选券商

故障转移流程:
    1. active 券商熔断 OPEN → submit_order 抛 CircuitBreakerOpenError
    2. BrokerAdapterManager 捕获 → 自动 failover() 到下一个备选券商
    3. 用备选券商重试一次 (这不是"下单重试", 是"故障转移后首次尝试")
    4. 所有券商都不可用 → NoAvailableBrokerError

SSoT: depgraph MOD-XS-002
Version: 0.1.0
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Final, Optional

from zephyr.ex_sor.api.api_rate_limiter import TradingSession
from zephyr.ex_sor.api.broker_api_connector import (
    BrokerApiConnector,
    BrokerConnectionError,
    BrokerProtocol,
    BrokerSubmitError,
    BrokerType,
    CircuitBreakerOpenError,
    ConnectionConfig,
    ConnectionState,
    FillCallback,
    RateLimitedError,
)
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "BrokerAdapter",
    "BrokerAdapterManager",
    "BrokerAdapterError",
    "NoAvailableBrokerError",
    "FailoverExhaustedError",
    "BrokerSelection",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class BrokerAdapterError(ZephyrBaseError):
    """适配器层错误——配置非法、状态不一致。"""

    error_code = "ZA-XS-0002"


class NoAvailableBrokerError(BrokerAdapterError):
    """所有券商都不可用——无可用券商下单。"""

    error_code = "ZA-XS-0002-NA"


class FailoverExhaustedError(BrokerAdapterError):
    """故障转移耗尽——所有备选券商都尝试失败。"""

    error_code = "ZA-XS-0002-FE"


# ──────────────────────────────────────────────────────────────────────────────
# BrokerAdapter — 单券商适配器
# ──────────────────────────────────────────────────────────────────────────────


class BrokerAdapter:
    """单券商适配器——封装 BrokerApiConnector, 提供统一接口。

    约束: 适配器只做协议转换, 不含业务逻辑 (§2.2 XS-02)。
    """

    def __init__(
        self,
        broker_type: BrokerType,
        connector: BrokerApiConnector,
    ) -> None:
        self._broker_type = broker_type
        self._connector = connector
        self._fill_callbacks: list[FillCallback] = []

    @property
    def broker_type(self) -> BrokerType:
        return self._broker_type

    @property
    def connector(self) -> BrokerApiConnector:
        return self._connector

    @property
    def is_connected(self) -> bool:
        return self._connector.is_connected

    @property
    def is_available(self) -> bool:
        """是否可用——已连接且熔断未开启。"""
        return self._connector.is_connected and not self._connector.circuit_breaker.is_open

    def connect(self) -> None:
        """建立连接。"""
        self._connector.connect()

    def disconnect(self) -> None:
        """断开连接。"""
        self._connector.disconnect()

    def submit_order(
        self,
        order: Order,
        session: TradingSession = TradingSession.INTRADAY,
    ) -> str:
        """提交订单 (HB-07: 零重试, 失败抛异常)。"""
        return self._connector.submit_order(order, session)

    def cancel_order(
        self,
        broker_order_id: str,
        session: TradingSession = TradingSession.INTRADAY,
    ) -> bool:
        """撤销订单。"""
        return self._connector.cancel_order(broker_order_id, session)

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册成交回报回调。"""
        self._fill_callbacks.append(callback)
        self._connector.register_fill_callback(callback)

    def on_fill_received(self, fill: Fill) -> None:
        """收到成交回报——分发到所有回调。"""
        self._connector.on_fill_received(fill)

    def reset_circuit(self) -> None:
        """人工恢复熔断 (HB-06)。"""
        self._connector.manual_reset_circuit()


# ──────────────────────────────────────────────────────────────────────────────
# BrokerSelection — 下单结果
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BrokerSelection:
    """下单结果——记录使用哪个券商 + broker_order_id。

    Attributes:
        broker: 使用的券商类型
        broker_order_id: 券商返回的订单 ID
        failovered: 是否经过故障转移
    """

    broker: BrokerType
    broker_order_id: str
    failovered: bool = False


# ──────────────────────────────────────────────────────────────────────────────
# BrokerAdapterManager — 多券商管理 + 故障转移
# ──────────────────────────────────────────────────────────────────────────────


class BrokerAdapterManager:
    """多券商统一适配器管理——故障转移 + Feature Toggle。

    用法:
        mgr = BrokerAdapterManager()
        mgr.register_adapter(BrokerAdapter(BrokerType.MINIQMT, conn1), primary=True)
        mgr.register_adapter(BrokerAdapter(BrokerType.XTP, conn2))
        mgr.connect_all()

        selection = mgr.submit_order(order)
        # → BrokerSelection(broker=MINIQMT, broker_order_id="BROKER-...", failovered=False)

        # 运行时切换券商 (Feature Toggle, §6.5)
        mgr.switch_broker(BrokerType.XTP)

    故障转移:
        submit_order 时 active 券商熔断 → 自动 failover 到备选
        所有备选不可用 → NoAvailableBrokerError
    """

    def __init__(self) -> None:
        self._adapters: dict[BrokerType, BrokerAdapter] = {}
        self._priority: list[BrokerType] = []  # 故障转移优先级顺序
        self._active: BrokerType | None = None
        self._global_fill_callbacks: list[FillCallback] = []
        self._failover_count = 0

    # ── 属性 ──

    @property
    def active_broker(self) -> BrokerType | None:
        """当前活跃券商 (None=未配置)。"""
        return self._active

    @property
    def registered_brokers(self) -> list[BrokerType]:
        """已注册的券商列表 (按优先级)。"""
        return list(self._priority)

    @property
    def failover_count(self) -> int:
        """累计故障转移次数。"""
        return self._failover_count

    @property
    def available_brokers(self) -> list[BrokerType]:
        """当前可用的券商 (已连接 + 未熔断)。"""
        return [bt for bt in self._priority if self._adapters[bt].is_available]

    # ── 注册管理 ──

    def register_adapter(
        self,
        adapter: BrokerAdapter,
        primary: bool = False,
    ) -> None:
        """注册券商适配器。

        Args:
            adapter: 券商适配器
            primary: 是否设为主券商 (首个 primary 替换当前 active)
        """
        bt = adapter.broker_type
        if bt in self._adapters:
            raise BrokerAdapterError(
                f"券商已注册: {bt.value}",
                details={"broker": bt.value},
            )
        self._adapters[bt] = adapter
        self._priority.append(bt)
        if primary or self._active is None:
            self._active = bt
        # 注册全局回调到新适配器
        for cb in self._global_fill_callbacks:
            adapter.register_fill_callback(cb)
        logger.info("Registered broker adapter: %s (primary=%s)", bt.value, primary)

    # ── 连接管理 ──

    def connect_all(self) -> None:
        """连接所有已注册券商。"""
        for bt, adapter in self._adapters.items():
            try:
                adapter.connect()
                logger.info("Connected: %s", bt.value)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Connect failed for %s: %s", bt.value, exc)

    def disconnect_all(self) -> None:
        """断开所有券商。"""
        for bt, adapter in self._adapters.items():
            try:
                adapter.disconnect()
            except Exception:
                logger.exception("Disconnect error for %s", bt.value)

    # ── 下单 (带自动故障转移) ──

    def submit_order(
        self,
        order: Order,
        session: TradingSession = TradingSession.INTRADAY,
    ) -> BrokerSelection:
        """提交订单——active 券商失败时自动故障转移。

        故障转移逻辑:
            1. 用 active 券商下单
            2. 如果熔断 (CircuitBreakerOpenError) → failover 到下一个可用券商
            3. 用备选券商重试一次
            4. 所有券商不可用 → NoAvailableBrokerError

        注意: 这不是"下单重试" (HB-07), 而是"故障转移后首次尝试"。

        Returns:
            BrokerSelection: 使用的券商 + broker_order_id + 是否故障转移
        """
        if self._active is None:
            raise NoAvailableBrokerError("未注册任何券商适配器")

        # 尝试 active 券商
        active = self._adapters.get(self._active)
        if active is None:
            raise NoAvailableBrokerError(
                f"活跃券商未注册: {self._active.value}",
                details={"active": self._active.value},
            )

        try:
            broker_id = active.submit_order(order, session)
            return BrokerSelection(
                broker=active.broker_type,
                broker_order_id=broker_id,
                failovered=False,
            )
        except (CircuitBreakerOpenError, BrokerSubmitError) as exc:
            # 熔断已开启 (CircuitBreakerOpenError) 或下单失败触发熔断 (BrokerSubmitError)
            # → 自动故障转移到备选券商
            if not active.connector.circuit_breaker.is_open:
                # 非熔断类失败 (如限速) → 不故障转移, 直接抛
                raise
            logger.warning(
                "Active broker %s circuit open (%s), attempting failover",
                self._active.value,
                type(exc).__name__,
            )
            return self._failover_and_submit(order, session)

    def _failover_and_submit(
        self,
        order: Order,
        session: TradingSession,
    ) -> BrokerSelection:
        """故障转移到备选券商并下单。"""
        self._failover_count += 1
        failed = set()
        failed.add(self._active)

        for bt in self._priority:
            if bt in failed:
                continue
            adapter = self._adapters.get(bt)
            if adapter is None or not adapter.is_available:
                continue
            try:
                broker_id = adapter.submit_order(order, session)
                # 故障转移成功 → 切换 active
                old = self._active
                self._active = bt
                logger.warning(
                    "Failover: %s -> %s (order=%s)",
                    old.value if old else "None",
                    bt.value,
                    order.order_id,
                )
                return BrokerSelection(
                    broker=bt,
                    broker_order_id=broker_id,
                    failovered=True,
                )
            except (CircuitBreakerOpenError, BrokerSubmitError, BrokerConnectionError) as exc:
                logger.warning("Failover to %s failed: %s", bt.value, exc)
                failed.add(bt)
                continue

        raise FailoverExhaustedError(
            "所有备选券商均不可用",
            details={
                "tried": [bt.value for bt in self._priority],
                "failed": [bt.value for bt in failed],
            },
        )

    # ── 撤单 ──

    def cancel_order(
        self,
        broker: BrokerType,
        broker_order_id: str,
        session: TradingSession = TradingSession.INTRADAY,
    ) -> bool:
        """撤销指定券商的订单。

        Args:
            broker: 哪个券商的订单 (从 BrokerSelection.broker 获取)
            broker_order_id: 券商订单 ID
        """
        adapter = self._adapters.get(broker)
        if adapter is None:
            raise BrokerAdapterError(
                f"券商未注册: {broker.value}",
                details={"broker": broker.value},
            )
        return adapter.cancel_order(broker_order_id, session)

    # ── Feature Toggle: 运行时券商切换 (§6.5) ──

    def switch_broker(self, broker: BrokerType) -> None:
        """运行时切换活跃券商 (Feature Toggle, §6.5 零中断)。

        Args:
            broker: 要切换到的券商

        Raises:
            BrokerAdapterError: 券商未注册
        """
        if broker not in self._adapters:
            raise BrokerAdapterError(
                f"无法切换: 券商未注册 {broker.value}",
                details={"broker": broker.value},
            )
        old = self._active
        self._active = broker
        logger.info(
            "Broker switch (Feature Toggle): %s -> %s",
            old.value if old else "None",
            broker.value,
        )

    # ── 故障转移 (手动触发) ──

    def failover(self) -> BrokerType | None:
        """手动触发故障转移——切换到下一个可用券商。

        Returns:
            新的活跃券商, None 如果无可用备选
        """
        if self._active is None:
            return None
        current = self._active
        for bt in self._priority:
            if bt == current:
                continue
            adapter = self._adapters.get(bt)
            if adapter is not None and adapter.is_available:
                self._active = bt
                self._failover_count += 1
                logger.warning("Manual failover: %s -> %s", current.value, bt.value)
                return bt
        return None

    # ── 成交回调 ──

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册全局成交回调——应用到所有已注册和未来的适配器。"""
        self._global_fill_callbacks.append(callback)
        for adapter in self._adapters.values():
            adapter.register_fill_callback(callback)

    # ── 诊断 ──

    def get_broker_status(self) -> dict[BrokerType, dict[str, object]]:
        """获取所有券商状态摘要。"""
        status: dict[BrokerType, dict[str, object]] = {}
        for bt, adapter in self._adapters.items():
            status[bt] = {
                "is_connected": adapter.is_connected,
                "is_available": adapter.is_available,
                "is_active": bt == self._active,
                "circuit_open": adapter.connector.circuit_breaker.is_open,
                "state": adapter.connector.state.name,
            }
        return status
