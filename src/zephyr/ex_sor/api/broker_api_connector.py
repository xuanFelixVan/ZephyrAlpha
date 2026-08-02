# [BLUEPRINT] MOD-XS-013 | docs/03_modules/_domain_ex_sor/broker_api_connector/blueprint.md
# [MODULE] zephyr.ex_sor.api.broker_api_connector
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.contracts.fill; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors; zephyr.ex_sor.api.api_rate_limiter
# [CONSUMERS] MOD-XS-002(Broker Adapter,协议层消费者) ; MOD-XS-005(Algo Trading Engine,下单通道)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 下单零重试(HB-07); 熔断需人工恢复(HB-06); 心跳3次失败→断开; 所有API调用经XS-014限速; 连接状态机单向不可逆(FILLED/CANCELLED不可回SUBMITTED)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BrokerConnectionError; BrokerSubmitError; CircuitBreakerOpenError; HeartbeatTimeoutError
# [TESTS] tests/ex_sor/test_broker_api_connector.py
# [A_module] module_id=MOD-XS-013 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Broker API Connector — 券商 API 连接器 (MOD-XS-013)

D-EX-SOR §2.2 XS-13: REST/FIX 4.2+ 连接 + 心跳 + 消息序列化 + 重连 + API 版本迁移适配。

职责分层 (与 XS-02 Broker Adapter 区分):
    XS-13 (本模块) = 协议/传输层: 连接管理 + 心跳 + 序列化 + 重连 + 限速
    XS-02          = 适配/业务层:  多券商统一适配 + 事务一致性 + 故障转移

关键约束 (D-EX-SOR §6):
    HB-07: 下单操作零重试——submit_order 失败立即返回错误, 禁止自动重试 (防重复下单)
    HB-06: 交易通道熔断必须人工恢复——CircuitBreaker OPEN 后需 manual_reset()
    §8.5:  会话超时 30 分钟无操作自动断开; 心跳间隔 30s

依赖:
    XS-014 ApiRateLimiter: 所有出站 API 调用 MUST 先经限速检查

SSoT: depgraph MOD-XS-013
Version: 0.1.0
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum, auto
from typing import Final, Optional

from zephyr.ex_sor.api.api_rate_limiter import (
    ApiRateLimiter,
    RateLimitDecision,
    RequestPriority,
    TradingSession,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "BrokerType",
    "BrokerProtocol",
    "ConnectionState",
    "ConnectionConfig",
    "HeartbeatManager",
    "ReconnectPolicy",
    "CircuitBreakerState",
    "CircuitBreaker",
    "BrokerApiConnector",
    "BrokerConnectionError",
    "BrokerSubmitError",
    "CircuitBreakerOpenError",
    "HeartbeatTimeoutError",
    "RateLimitedError",
    "FillCallback",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class BrokerConnectionError(ZephyrBaseError):
    """券商连接错误——连接失败、断线、状态机非法跳转。"""

    error_code = "ZA-XS-0013"


class BrokerSubmitError(ZephyrBaseError):
    """下单提交错误——券商拒绝、协议层失败 (HB-07: 不重试)。"""

    error_code = "ZA-XS-0013-S"


class CircuitBreakerOpenError(BrokerConnectionError):
    """熔断器已开启——需人工 manual_reset() 后才能恢复 (HB-06)。"""

    error_code = "ZA-XS-0013-CB"


class HeartbeatTimeoutError(BrokerConnectionError):
    """心跳超时——连续 N 次心跳未收到响应。"""

    error_code = "ZA-XS-0013-HB"


class RateLimitedError(BrokerConnectionError):
    """被 XS-014 限速器拦截——请求被限流, 需等待 retry_after_seconds。"""

    error_code = "ZA-XS-0013-RL"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class BrokerType(Enum):
    """支持的券商类型 (API 版本迁移适配, §2.2 XS-13)。"""

    MINIQMT = "miniQMT"  # 国金证券 MiniQMT (xttrader API)
    XTP = "XTP"  # 中泰证券 XTP
    CTP = "CTP"  # 期货 CTP
    OKX = "OKX"  # OKX 数字资产
    SIMULATED = "simulated"  # 模拟券商 (测试/回测)


class ConnectionState(Enum):
    """连接状态机。

    合法转换:
        DISCONNECTED → CONNECTING → CONNECTED
        CONNECTED → DISCONNECTING → DISCONNECTED
        CONNECTING → RECONNECTING → CONNECTED
        CONNECTED → CIRCUIT_OPEN (熔断, 需人工恢复)
        CIRCUIT_OPEN → CONNECTING (manual_reset 后)
    """

    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTING = auto()
    RECONNECTING = auto()
    CIRCUIT_OPEN = auto()  # HB-06: 熔断, 需人工恢复


class CircuitBreakerState(Enum):
    """熔断器状态 (HB-06: OPEN 需人工恢复)。"""

    CLOSED = auto()  # 正常
    OPEN = auto()  # 熔断 (人工恢复)


# 类型别名
FillCallback = Callable[[Fill], None]


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConnectionConfig:
    """券商连接配置。

    Attributes:
        broker: 券商类型
        endpoint: 连接端点 (URL / FIX host:port)
        heartbeat_interval: 心跳间隔秒 (§8.5 默认 30s)
        heartbeat_max_missed: 连续心跳失败上限 (超限→断开)
        session_timeout: 会话超时秒 (§8.5 默认 1800=30min)
        reconnect_max_attempts: 重连最大尝试次数 (不含首次连接)
        reconnect_backoff_base: 指数退避基数秒
        circuit_failure_threshold: 熔断失败次数阈值
    """

    broker: BrokerType = BrokerType.SIMULATED
    endpoint: str = ""
    heartbeat_interval: float = 30.0
    heartbeat_max_missed: int = 3
    session_timeout: float = 1800.0
    reconnect_max_attempts: int = 3
    reconnect_backoff_base: float = 1.0
    circuit_failure_threshold: int = 5

    def __post_init__(self) -> None:
        if self.heartbeat_interval <= 0:
            raise BrokerConnectionError("heartbeat_interval must be >0")
        if self.heartbeat_max_missed <= 0:
            raise BrokerConnectionError("heartbeat_max_missed must be >0")
        if self.session_timeout <= 0:
            raise BrokerConnectionError("session_timeout must be >0")
        if self.reconnect_max_attempts < 0:
            raise BrokerConnectionError("reconnect_max_attempts must be >=0")
        if self.reconnect_backoff_base <= 0:
            raise BrokerConnectionError("reconnect_backoff_base must be >0")
        if self.circuit_failure_threshold <= 0:
            raise BrokerConnectionError("circuit_failure_threshold must be >0")


# ──────────────────────────────────────────────────────────────────────────────
# 协议抽象 (REST / FIX 4.2+)
# ──────────────────────────────────────────────────────────────────────────────


class BrokerProtocol(ABC):
    """券商协议抽象——REST / FIX 4.2+ 统一接口。

    子类实现具体协议交互 (网络层), BrokerApiConnector 负责状态机/心跳/限速/熔断。
    测试时可用 SimulatedProtocol 替换真实网络调用。
    """

    @abstractmethod
    def connect(self) -> None:
        """建立底层连接。"""

    @abstractmethod
    def disconnect(self) -> None:
        """断开底层连接。"""

    @abstractmethod
    def send_heartbeat(self) -> bool:
        """发送心跳, 返回是否收到响应。"""

    @abstractmethod
    def submit_order_raw(self, order: Order) -> str:
        """提交订单到券商, 返回 broker_order_id。

        HB-07: 协议层不重试, 失败直接抛异常。
        """

    @abstractmethod
    def cancel_order_raw(self, broker_order_id: str) -> bool:
        """撤销订单, 返回是否成功。"""

    @abstractmethod
    def query_position_raw(self) -> list[dict[str, object]]:
        """查询持仓, 返回原始字典列表。"""


class SimulatedProtocol(BrokerProtocol):
    """模拟协议——用于测试/回测, 无真实网络调用。

    可注入故障: set_failure_mode() 控制后续操作是否失败。
    """

    def __init__(self) -> None:
        self._connected = False
        self._orders: dict[str, Order] = {}
        self._fail_submit = False
        self._fail_heartbeat = False
        self._fail_cancel = False
        self._heartbeat_call_count = 0
        self._submit_call_count = 0

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def send_heartbeat(self) -> bool:
        self._heartbeat_call_count += 1
        return not self._fail_heartbeat

    def submit_order_raw(self, order: Order) -> str:
        self._submit_call_count += 1
        if self._fail_submit:
            raise BrokerSubmitError("simulated submit failure")
        broker_order_id = f"BROKER-{order.order_id}"
        self._orders[broker_order_id] = order
        return broker_order_id

    def cancel_order_raw(self, broker_order_id: str) -> bool:
        if self._fail_cancel:
            return False
        return broker_order_id in self._orders

    def query_position_raw(self) -> list[dict[str, object]]:
        return []

    # ── 测试辅助: 故障注入 ──

    def set_failure_mode(
        self,
        *,
        submit: bool = False,
        heartbeat: bool = False,
        cancel: bool = False,
    ) -> None:
        self._fail_submit = submit
        self._fail_heartbeat = heartbeat
        self._fail_cancel = cancel

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def heartbeat_call_count(self) -> int:
        return self._heartbeat_call_count

    @property
    def submit_call_count(self) -> int:
        return self._submit_call_count


# ──────────────────────────────────────────────────────────────────────────────
# 心跳管理器
# ──────────────────────────────────────────────────────────────────────────────


class HeartbeatManager:
    """心跳管理器——定期发送心跳, 连续 N 次失败触发断开。

    不变量: 0 <= missed_count <= max_missed + 1
    """

    def __init__(self, config: ConnectionConfig) -> None:
        self._interval = config.heartbeat_interval
        self._max_missed = config.heartbeat_max_missed
        self._missed_count = 0
        self._last_pong: float = 0.0
        self._started = False

    @property
    def interval(self) -> float:
        return self._interval

    @property
    def max_missed(self) -> int:
        return self._max_missed

    @property
    def missed_count(self) -> int:
        return self._missed_count

    @property
    def is_healthy(self) -> bool:
        """心跳是否健康 (未超连续失败上限)。"""
        return self._missed_count < self._max_missed

    def start(self, now: float | None = None) -> None:
        """启动心跳计时。"""
        self._started = True
        self._missed_count = 0
        self._last_pong = now if now is not None else time.monotonic()

    def stop(self) -> None:
        """停止心跳计时。"""
        self._started = False

    def on_heartbeat_success(self, now: float | None = None) -> None:
        """心跳成功——重置失败计数。"""
        self._missed_count = 0
        self._last_pong = now if now is not None else time.monotonic()

    def on_heartbeat_failure(self) -> bool:
        """心跳失败——递增失败计数, 返回是否超限。

        Returns:
            True 如果失败次数已达上限 (应触发断开)
        """
        self._missed_count += 1
        return self._missed_count >= self._max_missed

    def is_due(self, now: float | None = None) -> bool:
        """是否到了发送下一次心跳的时间。"""
        if not self._started:
            return False
        current = now if now is not None else time.monotonic()
        return (current - self._last_pong) >= self._interval


# ──────────────────────────────────────────────────────────────────────────────
# 重连策略 (HB-07: 不适用于下单)
# ──────────────────────────────────────────────────────────────────────────────


class ReconnectPolicy:
    """重连策略——指数退避, 仅用于连接层 (不适用于下单, HB-07)。

    用法:
        policy = ReconnectPolicy(config)
        while policy.should_retry():
            wait = policy.next_backoff()
            time.sleep(wait)
            try: connect()
            except: policy.on_failure()
    """

    def __init__(self, config: ConnectionConfig) -> None:
        self._max_attempts = config.reconnect_max_attempts
        self._base = config.reconnect_backoff_base
        self._attempt = 0

    @property
    def attempt(self) -> int:
        return self._attempt

    @property
    def remaining(self) -> int:
        return max(0, self._max_attempts - self._attempt)

    def should_retry(self) -> bool:
        """是否还有重连机会。"""
        return self._attempt < self._max_attempts

    def next_backoff(self) -> float:
        """计算下一次退避等待秒数 (指数退避: base * 2^attempt)。"""
        backoff = self._base * (2**self._attempt)
        self._attempt += 1
        return backoff

    def reset(self) -> None:
        """重置重连计数 (连接成功后调用)。"""
        self._attempt = 0


# ──────────────────────────────────────────────────────────────────────────────
# 熔断器 (HB-06: OPEN 需人工恢复)
# ──────────────────────────────────────────────────────────────────────────────


class CircuitBreaker:
    """熔断器——失败次数达阈值后 OPEN, 需 manual_reset() 恢复 (HB-06)。

    状态:
        CLOSED → 正常, 计数失败
        OPEN   → 熔断, 拒绝所有请求, 需人工 manual_reset()

    不变量: failure_count <= threshold 时 CLOSED; > threshold 时 OPEN
    """

    def __init__(self, threshold: int) -> None:
        if threshold <= 0:
            raise BrokerConnectionError(f"circuit breaker threshold must be >0, got {threshold}")
        self._threshold = threshold
        self._failure_count = 0
        self._state = CircuitBreakerState.CLOSED

    @property
    def threshold(self) -> int:
        return self._threshold

    @property
    def failure_count(self) -> int:
        return self._failure_count

    @property
    def state(self) -> CircuitBreakerState:
        return self._state

    @property
    def is_open(self) -> bool:
        return self._state == CircuitBreakerState.OPEN

    def record_success(self) -> None:
        """记录成功——重置失败计数 (但不清除 OPEN 状态, 需 manual_reset)。"""
        self._failure_count = 0

    def record_failure(self) -> bool:
        """记录失败——超阈值时切换到 OPEN。

        Returns:
            True 如果本次失败触发了熔断 (CLOSED→OPEN)
        """
        if self._state == CircuitBreakerState.OPEN:
            return False
        self._failure_count += 1
        if self._failure_count >= self._threshold:
            self._state = CircuitBreakerState.OPEN
            return True
        return False

    def manual_reset(self) -> None:
        """人工恢复熔断器 (HB-06: 必须人工调用)。

        将状态从 OPEN → CLOSED, 重置失败计数。
        如果当前不是 OPEN 状态, 则为无操作。
        """
        if self._state == CircuitBreakerState.OPEN:
            logger.warning("Circuit breaker manual reset: OPEN→CLOSED (HB-06 人工恢复)")
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0

    def check(self) -> None:
        """检查熔断状态——OPEN 时抛 CircuitBreakerOpenError。"""
        if self._state == CircuitBreakerState.OPEN:
            raise CircuitBreakerOpenError(
                "熔断器已开启 (HB-06), 需人工 manual_reset() 恢复",
                details={
                    "failure_count": self._failure_count,
                    "threshold": self._threshold,
                },
            )


# ──────────────────────────────────────────────────────────────────────────────
# 券商 API 连接器 (主入口)
# ──────────────────────────────────────────────────────────────────────────────


class BrokerApiConnector:
    """券商 API 连接器——协议层状态机 + 心跳 + 限速 + 熔断。

    生命周期:
        connector = BrokerApiConnector(protocol, config, rate_limiter)
        connector.connect()
        broker_id = connector.submit_order(order)  # HB-07: 零重试
        connector.cancel_order(broker_id)
        connector.disconnect()

    约束:
        - 所有出站 API 调用先经 XS-014 限速检查 (submit/cancel/query)
        - submit_order 失败不重试 (HB-07), 直接抛 BrokerSubmitError
        - 连续心跳失败 → 自动断开 → 触发重连 (非下单路径)
        - 熔断 OPEN → 所有请求被拒, 需 manual_reset_circuit() (HB-06)
    """

    def __init__(
        self,
        protocol: BrokerProtocol,
        config: ConnectionConfig | None = None,
        rate_limiter: ApiRateLimiter | None = None,
    ) -> None:
        self._protocol = protocol
        self._config = config or ConnectionConfig()
        self._rate_limiter = rate_limiter or ApiRateLimiter()
        self._heartbeat = HeartbeatManager(self._config)
        self._reconnect = ReconnectPolicy(self._config)
        self._circuit = CircuitBreaker(self._config.circuit_failure_threshold)
        self._state = ConnectionState.DISCONNECTED
        self._fill_callbacks: list[FillCallback] = []
        self._last_activity: float = time.monotonic()

    # ── 属性 ──

    @property
    def state(self) -> ConnectionState:
        return self._state

    @property
    def is_connected(self) -> bool:
        """底层连接是否存活 (CIRCUIT_OPEN 时连接仍在, 只是熔断)。"""
        return self._state in (
            ConnectionState.CONNECTED,
            ConnectionState.CIRCUIT_OPEN,
        )

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        return self._circuit

    @property
    def heartbeat(self) -> HeartbeatManager:
        return self._heartbeat

    # ── 连接管理 ──

    def connect(self) -> None:
        """建立连接——状态机 DISCONNECTED→CONNECTING→CONNECTED。

        失败时进入重连流程; 重连耗尽→熔断。
        """
        if self._state == ConnectionState.CONNECTED:
            return  # 幂等
        if self._state == ConnectionState.CIRCUIT_OPEN:
            self._circuit.check()  # 抛 CircuitBreakerOpenError

        self._transition(ConnectionState.CONNECTING)
        try:
            self._protocol.connect()
            self._transition(ConnectionState.CONNECTED)
            self._heartbeat.start()
            self._reconnect.reset()
            self._circuit.record_success()
            self._last_activity = time.monotonic()
            logger.info("Broker connected: %s", self._config.broker.value)
        except Exception as exc:
            self._on_connection_failure(exc)
            raise

    def disconnect(self) -> None:
        """主动断开——状态机 →DISCONNECTED。"""
        if self._state == ConnectionState.DISCONNECTED:
            return  # 幂等
        self._transition(ConnectionState.DISCONNECTING)
        self._heartbeat.stop()
        try:
            self._protocol.disconnect()
        finally:
            self._transition(ConnectionState.DISCONNECTED)

    def reconnect(self) -> None:
        """重连——指数退避重试 (非下单路径)。

        重连耗尽 → 熔断 OPEN。
        """
        if self._state == ConnectionState.CIRCUIT_OPEN:
            self._circuit.check()

        self._transition(ConnectionState.RECONNECTING)
        while self._reconnect.should_retry():
            backoff = self._reconnect.next_backoff()
            logger.info(
                "Reconnect attempt %d, backing off %.1fs",
                self._reconnect.attempt,
                backoff,
            )
            time.sleep(backoff)
            try:
                self._protocol.connect()
                self._transition(ConnectionState.CONNECTED)
                self._heartbeat.start()
                self._reconnect.reset()
                self._circuit.record_success()
                logger.info("Reconnected successfully")
                return
            except Exception as exc:  # noqa: BLE001
                logger.warning("Reconnect failed: %s", exc)

        # 重连耗尽 → 熔断
        self._circuit.record_failure()
        if self._circuit.is_open:
            self._transition(ConnectionState.CIRCUIT_OPEN)
        else:
            self._transition(ConnectionState.DISCONNECTED)
        raise BrokerConnectionError(
            f"重连失败, 已尝试 {self._reconnect.attempt} 次",
            details={"max_attempts": self._config.reconnect_max_attempts},
        )

    # ── 下单 (HB-07: 零重试) ──

    def submit_order(
        self,
        order: Order,
        session: TradingSession = TradingSession.INTRADAY,
    ) -> str:
        """提交订单到券商——零重试 (HB-07)。

        Args:
            order: 委托指令 (CTR-004)
            session: 当前交易时段 (限速用)

        Returns:
            broker_order_id: 券商返回的订单 ID

        Raises:
            CircuitBreakerOpenError: 熔断已开启 (HB-06)
            RateLimitedError: 被 XS-014 限速拦截
            BrokerSubmitError: 券商拒绝/协议失败 (不重试)
        """
        self._ensure_connected()
        self._circuit.check()
        self._check_rate_limit(session, RequestPriority.P0_TRADING)

        try:
            broker_order_id = self._protocol.submit_order_raw(order)
            self._circuit.record_success()
            self._last_activity = time.monotonic()
            logger.info(
                "Order submitted: %s -> broker_id=%s (HB-07 零重试)",
                order.order_id,
                broker_order_id,
            )
            return broker_order_id
        except Exception as exc:
            # HB-07: 下单失败不重试, 直接抛异常
            tripped = self._circuit.record_failure()
            if tripped:
                self._transition(ConnectionState.CIRCUIT_OPEN)
            raise BrokerSubmitError(
                f"下单失败 (HB-07 不重试): {exc}",
                details={"order_id": order.order_id},
            ) from exc

    def cancel_order(
        self,
        broker_order_id: str,
        session: TradingSession = TradingSession.INTRADAY,
    ) -> bool:
        """撤销订单。

        Returns:
            True 撤销成功, False 券商返回失败
        """
        self._ensure_connected()
        self._circuit.check()
        self._check_rate_limit(session, RequestPriority.P1_RISK)

        try:
            result = self._protocol.cancel_order_raw(broker_order_id)
            if result:
                self._circuit.record_success()
            else:
                self._circuit.record_failure()
            self._last_activity = time.monotonic()
            return result
        except Exception as exc:
            self._circuit.record_failure()
            raise BrokerConnectionError(
                f"撤单失败: {exc}",
                details={"broker_order_id": broker_order_id},
            ) from exc

    def query_position(
        self,
        session: TradingSession = TradingSession.POST_CLOSE,
    ) -> list[dict[str, object]]:
        """查询持仓。"""
        self._ensure_connected()
        self._circuit.check()
        self._check_rate_limit(session, RequestPriority.P2_MARKET_DATA)

        try:
            result = self._protocol.query_position_raw()
            self._circuit.record_success()
            self._last_activity = time.monotonic()
            return result
        except Exception as exc:
            self._circuit.record_failure()
            raise BrokerConnectionError(f"查询持仓失败: {exc}") from exc

    # ── 心跳 ──

    def send_heartbeat(self) -> bool:
        """发送一次心跳。

        Returns:
            True 心跳成功, False 心跳失败 (可能触发断开)

        Raises:
            HeartbeatTimeoutError: 连续失败达上限
        """
        if not self.is_connected:
            return False

        success = self._protocol.send_heartbeat()
        if success:
            self._heartbeat.on_heartbeat_success()
            return True

        tripped = self._heartbeat.on_heartbeat_failure()
        if tripped:
            logger.error(
                "Heartbeat timeout: %d consecutive failures",
                self._heartbeat.missed_count,
            )
            # 心跳超时 → 断开 (非 CIRCUIT_OPEN, 可自动重连)
            self._transition(ConnectionState.DISCONNECTED)
            self._heartbeat.stop()
            raise HeartbeatTimeoutError(
                f"心跳连续 {self._heartbeat.missed_count} 次失败, 连接断开",
                details={"max_missed": self._heartbeat.max_missed},
            )
        return False

    # ── 成交回报回调 ──

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册成交回报回调。"""
        self._fill_callbacks.append(callback)

    def on_fill_received(self, fill: Fill) -> None:
        """收到券商成交回报时调用——分发到所有注册的回调。"""
        for cb in self._fill_callbacks:
            try:
                cb(fill)
            except Exception:
                logger.exception("Fill callback error")

    # ── 熔断恢复 (HB-06) ──

    def manual_reset_circuit(self) -> None:
        """人工恢复熔断器 (HB-06)。

        熔断 OPEN → CLOSED, 允许重新 connect()。
        """
        self._circuit.manual_reset()
        if self._state == ConnectionState.CIRCUIT_OPEN:
            self._transition(ConnectionState.DISCONNECTED)

    # ── 内部方法 ──

    def _transition(self, new_state: ConnectionState) -> None:
        """状态机转换 (带合法性校验)。"""
        valid = {
            ConnectionState.DISCONNECTED: {
                ConnectionState.CONNECTING,
                ConnectionState.DISCONNECTED,
            },
            ConnectionState.CONNECTING: {
                ConnectionState.CONNECTED,
                ConnectionState.RECONNECTING,
                ConnectionState.DISCONNECTED,
                ConnectionState.CIRCUIT_OPEN,
            },
            ConnectionState.CONNECTED: {
                ConnectionState.DISCONNECTING,
                ConnectionState.DISCONNECTED,
                ConnectionState.CIRCUIT_OPEN,
            },
            ConnectionState.DISCONNECTING: {ConnectionState.DISCONNECTED},
            ConnectionState.RECONNECTING: {
                ConnectionState.CONNECTED,
                ConnectionState.DISCONNECTED,
                ConnectionState.CIRCUIT_OPEN,
            },
            ConnectionState.CIRCUIT_OPEN: {
                ConnectionState.DISCONNECTED,  # manual_reset 后
            },
        }
        allowed = valid.get(self._state, set())
        if new_state not in allowed:
            raise BrokerConnectionError(
                f"非法状态转换: {self._state.name} -> {new_state.name}",
                details={"from": self._state.name, "to": new_state.name},
            )
        old = self._state
        self._state = new_state
        logger.debug("State transition: %s -> %s", old.name, new_state.name)

    def _ensure_connected(self) -> None:
        """确保已连接, 否则抛异常。

        CIRCUIT_OPEN 状态走专门的熔断检查 (抛 CircuitBreakerOpenError, 更具体)。
        """
        if self._state == ConnectionState.CIRCUIT_OPEN:
            self._circuit.check()  # 抛 CircuitBreakerOpenError (HB-06)
        if self._state != ConnectionState.CONNECTED:
            raise BrokerConnectionError(
                f"未连接 (state={self._state.name}), 无法执行操作",
                details={"state": self._state.name},
            )

    def _check_rate_limit(self, session: TradingSession, priority: RequestPriority) -> None:
        """经 XS-014 限速检查——被拦截时抛 RateLimitedError。"""
        system = self._config.broker.value
        decision = self._rate_limiter.check(system=system, session=session, priority=priority)
        if not decision.allowed:
            raise RateLimitedError(
                f"被限速器拦截: {decision.reason}",
                details={
                    "blocked_level": decision.blocked_level.name if decision.blocked_level else None,
                    "retry_after_seconds": decision.retry_after_seconds,
                    "system": system,
                },
            )

    def _on_connection_failure(self, exc: Exception) -> None:
        """连接失败处理——重连或熔断。"""
        self._transition(ConnectionState.DISCONNECTED)
        tripped = self._circuit.record_failure()
        if tripped:
            self._transition(ConnectionState.CIRCUIT_OPEN)
