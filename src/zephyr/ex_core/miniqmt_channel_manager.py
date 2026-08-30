# [BLUEPRINT] MOD-EX-058 | docs/03_modules/MOD-EX-058/
# [MODULE] zephyr.ex_core.miniqmt_channel_manager
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-EX-035(Live/Simulation Switcher 实盘通道就绪判定) ; MOD-L06-001(真单通道唯一入口)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 通道非 CONNECTED 状态一切通道调用 Fail-Closed(MiniQmtChannelError); 重连/心跳尝试次数有界(无 while True); 断线检测三信号(心跳失败/调用异常/显式断开); 本模块不真连 QMT(ChannelTransport 协议抽象,生产接线 xttrader,测试用假实现); 状态迁移 DISCONNECTED→CONNECTING→CONNECTED→RECONNECTING→DOWN 单向留痕
# [MODIFY-GUARD] docs/03_modules/MOD-EX-058/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MiniQmtChannelError(ZA-EX-0017)
# [TESTS] tests/ex_core/test_miniqmt_channel_manager.py
# [A_module] module_id=MOD-EX-058 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
miniQMT 交易通道管理器 (MOD-EX-058)

D-EX-CORE-58：xtquant 接口封装的通道底座——连接生命周期 + 心跳 +
断线重连状态机。约束三（miniQMT 下单 10 笔/秒、Tick=3 秒）的接口底座，
KS-L3 通道断开检测信号：心跳失败 / 通道调用异常 / 显式断开。

Fail-Closed 铁律：通道不处于 CONNECTED 状态时，任何真单通道调用一律
MiniQmtChannelError 拒出（本批禁止真实下单路径，本模块只提供门禁与状态机，
不提供下单语义本身——真单调用方经 require_ready/run_channel_call 过闸）。

接口抽象：ChannelTransport 协议（connect/disconnect/ping）注入，本模块
不 import xtquant、不建网络连接；生产接线由适配层把 xttrader 会话适配进
ChannelTransport，测试用 FakeTransport 全确定性。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: transport 参数
#   fields: 参数 transport（无注解）
#   code: miniqmt_channel_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: max_reconnect_attempts 参数
#   fields: 参数 max_reconnect_attempts（无注解）
#   code: miniqmt_channel_manager.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_heartbeat_failures 参数
#   fields: 参数 max_heartbeat_failures（无注解）
#   code: miniqmt_channel_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ChannelTransport
#   name_en: ChannelTransport
#   intro: 通道传输协议（生产接线: xttrader 会话适配；测试: 假实现）。
#   desc: 通道传输协议（生产接线: xttrader 会话适配；测试: 假实现）。 约定： - connect() 返回 True=连接建立；抛异常或返回 False=失败。 - ping…；公共方法（定义序）: connect…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② MiniQmtChannelManager
#   name_en: MiniQmtChannelManager
#   intro: miniQMT 通道管理器（连接生命周期/心跳/断线重连状态机）。
#   desc: miniQMT 通道管理器（连接生命周期/心跳/断线重连状态机）。 Args: transport: ChannelTransport 协议实现（注入，禁真实连接硬编码）。 ma…；公共方法（定义序）: state…
#   inputs: transport max_reconnect_attempts max_heartbeat_failures
#   outputs: 返回值
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: ChannelTransport, MiniQmtChannelManager
#   downstream: MOD-EX-035(Live/Simulation Switcher 实盘通道就绪判定) ; MOD-L06-001(真单通道唯一入口)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Protocol

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ChannelState",
    "ChannelStatus",
    "ChannelTransport",
    "MiniQmtChannelError",
    "MiniQmtChannelManager",
]

_DEFAULT_MAX_RECONNECT_ATTEMPTS: Final[int] = 3
_DEFAULT_MAX_HEARTBEAT_FAILURES: Final[int] = 3


class MiniQmtChannelError(ZephyrBaseError):
    """miniQMT 通道错误（通道不可用拒出 / 状态机非法调用）。"""

    error_code = "ZA-EX-0017"


class ChannelState(str, Enum):
    """通道状态机五态。"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    DOWN = "down"


class ChannelTransport(Protocol):
    """通道传输协议（生产接线: xttrader 会话适配；测试: 假实现）。

    约定：
      - connect() 返回 True=连接建立；抛异常或返回 False=失败。
      - ping() 返回 RTT 秒（float）；抛异常=心跳失败。
      - disconnect() 幂等，不抛。
    """

    def connect(self) -> bool:
        """建立连接，成功返回 True。"""
        ...

    def disconnect(self) -> None:
        """断开连接（幂等）。"""
        ...

    def ping(self) -> float:
        """心跳探活，返回 RTT 秒；抛异常=心跳失败。"""
        ...


@dataclass(frozen=True)
class ChannelStatus:
    """通道状态快照（frozen，监控/看板消费）。"""

    state: ChannelState
    consecutive_heartbeat_failures: int
    reconnect_attempts: int
    ready: bool


class MiniQmtChannelManager:
    """miniQMT 通道管理器（连接生命周期/心跳/断线重连状态机）。

    Args:
        transport: ChannelTransport 协议实现（注入，禁真实连接硬编码）。
        max_reconnect_attempts: 单次断线重连尝试上限（默认 3，对齐
            55 号 §3.1A 自动重启 ≤3 次口径）。
        max_heartbeat_failures: 连续心跳失败多少次触发重连（默认 3）。
    """

    def __init__(
        self,
        transport: ChannelTransport,
        *,
        max_reconnect_attempts: int = _DEFAULT_MAX_RECONNECT_ATTEMPTS,
        max_heartbeat_failures: int = _DEFAULT_MAX_HEARTBEAT_FAILURES,
    ) -> None:
        if max_reconnect_attempts <= 0 or max_heartbeat_failures <= 0:
            raise MiniQmtChannelError(
                "max_reconnect_attempts/max_heartbeat_failures 必须为正",
                details={
                    "max_reconnect_attempts": max_reconnect_attempts,
                    "max_heartbeat_failures": max_heartbeat_failures,
                },
            )
        self._transport = transport
        self._max_reconnect_attempts = max_reconnect_attempts
        self._max_heartbeat_failures = max_heartbeat_failures
        self._state = ChannelState.DISCONNECTED
        self._heartbeat_failures = 0
        self._reconnect_attempts = 0

    # ── 状态查询 ──

    @property
    def state(self) -> ChannelState:
        """当前通道状态。"""
        return self._state

    @property
    def is_ready(self) -> bool:
        """通道可下单唯一判据（CONNECTED）。"""
        return self._state is ChannelState.CONNECTED

    def status(self) -> ChannelStatus:
        """通道状态快照。"""
        return ChannelStatus(
            state=self._state,
            consecutive_heartbeat_failures=self._heartbeat_failures,
            reconnect_attempts=self._reconnect_attempts,
            ready=self.is_ready,
        )

    # ── 连接生命周期 ──

    def connect(self) -> bool:
        """建立通道。成功→CONNECTED；失败在尝试上限内→DOWN（Fail-Closed 待命）。

        返回 True=已连接。失败不抛——DOWN 是合法终态，由 require_ready 把关。
        """
        if self._state is ChannelState.CONNECTED:
            return True
        self._state = ChannelState.CONNECTING
        if self._try_connect_once():
            return True
        # 首次失败：走有界重连（CONNECTING 视同断线，补满尝试上限）
        return self._reconnect_loop(from_state=ChannelState.CONNECTING)

    def disconnect(self) -> None:
        """显式断开（KS-L3 信号之三）。此后一切通道调用 Fail-Closed。"""
        try:
            self._transport.disconnect()
        except Exception as exc:  # noqa: BLE001 — 断开失败不掩盖状态迁移
            _logger.warning("通道断开调用异常(按已断开处理): %s", type(exc).__name__)
        self._state = ChannelState.DISCONNECTED
        self._heartbeat_failures = 0
        self._reconnect_attempts = 0

    # ── 心跳与断线重连 ──

    def heartbeat(self) -> bool:
        """心跳一次。CONNECTED 下 ping 失败累计；超阈值→有界重连→CONNECTED/DOWN。

        非 CONNECTED 状态心跳无意义，直接返回 False（不迁移状态）。
        """
        if self._state is not ChannelState.CONNECTED:
            return False
        try:
            self._transport.ping()
        except Exception as exc:  # noqa: BLE001 — 心跳失败=断线证据，不抛
            self._heartbeat_failures += 1
            _logger.warning(
                "通道心跳失败(第 %d 次): %s",
                self._heartbeat_failures,
                type(exc).__name__,
            )
        else:
            self._heartbeat_failures = 0
            return True
        if self._heartbeat_failures >= self._max_heartbeat_failures:
            return self._reconnect_loop(from_state=ChannelState.RECONNECTING)
        return False

    # ── Fail-Closed 闸门（真单通道调用唯一入口） ──

    def require_ready(self) -> None:
        """通道可用性硬闸。非 CONNECTED 一律 MiniQmtChannelError（Fail-Closed）。"""
        if self._state is not ChannelState.CONNECTED:
            raise MiniQmtChannelError(
                f"miniQMT 通道不可用(state={self._state.value})，拒绝通道调用",
                details={"state": self._state.value},
            )

    def run_channel_call(self, call: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """包裹一次真单通道调用：先过 Fail-Closed 闸，异常计入断线信号并透传。

        通道调用异常是 KS-L3 断线检测信号之一——异常计数累计达心跳失败阈值
        即触发有界重连；调用本身的异常原样上抛（不吞不包装）。
        """
        self.require_ready()
        try:
            return call(*args, **kwargs)
        except Exception:
            self._heartbeat_failures += 1
            _logger.warning(
                "通道调用异常(累计 %d 次): %s",
                self._heartbeat_failures,
                type(call).__name__,
            )
            if self._heartbeat_failures >= self._max_heartbeat_failures:
                self._reconnect_loop(from_state=ChannelState.RECONNECTING)
            raise

    # ── 内部：有界重连（无 while True） ──

    def _try_connect_once(self) -> bool:
        try:
            outcome = self._transport.connect()
        except Exception as exc:  # noqa: BLE001 — 连接失败=DOWN 证据，不抛
            _logger.warning("通道连接失败: %s", type(exc).__name__)
            return False
        if outcome:
            self._state = ChannelState.CONNECTED
            self._heartbeat_failures = 0
            self._reconnect_attempts = 0
            return True
        return False

    def _reconnect_loop(self, *, from_state: ChannelState) -> bool:
        self._state = from_state
        for attempt in range(1, self._max_reconnect_attempts + 1):
            self._reconnect_attempts = attempt
            if self._try_connect_once():
                _logger.info("通道重连成功(第 %d 次)", attempt)
                return True
        self._state = ChannelState.DOWN
        _logger.error(
            "通道重连 %d 次全部失败→DOWN（Fail-Closed，一切通道调用拒出）",
            self._max_reconnect_attempts,
        )
        return False
