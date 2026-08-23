# [BLUEPRINT] MOD-EX-058 | docs/03_modules/MOD-EX-058/
# [MODULE] tests.ex_core.test_miniqmt_channel_manager
# [DOMAIN] D_EX_CORE
# [INVARIANTS] FakeTransport 全确定性(无真实连接/无网络); 状态机迁移可断言; Fail-Closed 拒出可断言; 重连有界
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MiniQmtChannelError
# [TESTS] self
# [TTL] permanent
"""miniQMT 通道管理器测试（MOD-EX-058，阶段9 执行链路批）。"""

from __future__ import annotations

import pytest

from zephyr.ex_core.miniqmt_channel_manager import (
    ChannelState,
    MiniQmtChannelError,
    MiniQmtChannelManager,
)


class FakeTransport:
    """确定性假传输：脚本化 connect/ping 结果队列。"""

    def __init__(self, *, connect_results=None, ping_results=None):
        self.connect_results = list(connect_results or [True])
        self.ping_results = list(ping_results or [0.01])
        self.connect_calls = 0
        self.ping_calls = 0
        self.disconnect_calls = 0

    def _next(self, queue, default):
        if queue:
            return queue.pop(0)
        return default

    def connect(self) -> bool:
        self.connect_calls += 1
        outcome = self._next(self.connect_results, True)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def disconnect(self) -> None:
        self.disconnect_calls += 1

    def ping(self) -> float:
        self.ping_calls += 1
        outcome = self._next(self.ping_results, 0.01)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class TestConfig:
    def test_invalid_params_rejected(self):
        with pytest.raises(MiniQmtChannelError):
            MiniQmtChannelManager(FakeTransport(), max_reconnect_attempts=0)
        with pytest.raises(MiniQmtChannelError):
            MiniQmtChannelManager(FakeTransport(), max_heartbeat_failures=-1)


class TestConnect:
    def test_connect_success(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        assert mgr.state is ChannelState.DISCONNECTED
        assert mgr.connect() is True
        assert mgr.state is ChannelState.CONNECTED
        assert mgr.is_ready is True

    def test_connect_failure_goes_down_after_bounded_retries(self):
        transport = FakeTransport(connect_results=[False, False, False, False])
        mgr = MiniQmtChannelManager(transport, max_reconnect_attempts=3)
        assert mgr.connect() is False
        assert mgr.state is ChannelState.DOWN
        assert mgr.is_ready is False
        assert transport.connect_calls == 4  # 首连 1 次 + 重连 3 次（有界）

    def test_connect_retry_then_success(self):
        transport = FakeTransport(connect_results=[False, True])
        mgr = MiniQmtChannelManager(transport, max_reconnect_attempts=3)
        assert mgr.connect() is True
        assert mgr.state is ChannelState.CONNECTED
        assert mgr.status().reconnect_attempts == 0  # 成功后复位

    def test_already_connected_is_idempotent(self):
        transport = FakeTransport()
        mgr = MiniQmtChannelManager(transport)
        mgr.connect()
        assert mgr.connect() is True
        assert transport.connect_calls == 1


class TestHeartbeat:
    def test_heartbeat_ok_resets_failures(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        mgr.connect()
        assert mgr.heartbeat() is True
        assert mgr.status().consecutive_heartbeat_failures == 0

    def test_heartbeat_not_connected_returns_false(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        assert mgr.heartbeat() is False

    def test_heartbeat_failures_trigger_reconnect_success(self):
        transport = FakeTransport(
            ping_results=[ConnectionError("x"), ConnectionError("x"), ConnectionError("x")],
        )
        mgr = MiniQmtChannelManager(transport, max_heartbeat_failures=3)
        mgr.connect()
        assert mgr.heartbeat() is False
        assert mgr.heartbeat() is False
        assert mgr.state is ChannelState.CONNECTED  # 未达阈值不迁移
        assert mgr.heartbeat() is True  # 第3次失败→重连成功（默认 transport.connect True）
        assert mgr.state is ChannelState.CONNECTED
        assert mgr.status().consecutive_heartbeat_failures == 0

    def test_heartbeat_failures_reconnect_exhausted_goes_down(self):
        transport = FakeTransport(
            ping_results=[ConnectionError("x")],
            connect_results=[True, False, False, False],  # 首连成功，重连全败
        )
        mgr = MiniQmtChannelManager(
            transport, max_heartbeat_failures=1, max_reconnect_attempts=3
        )
        mgr.connect()
        assert mgr.heartbeat() is False
        assert mgr.state is ChannelState.DOWN


class TestFailClosed:
    def test_require_ready_blocks_when_disconnected(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        with pytest.raises(MiniQmtChannelError):
            mgr.require_ready()

    def test_require_ready_blocks_when_down(self):
        transport = FakeTransport(connect_results=[False, False, False, False])
        mgr = MiniQmtChannelManager(transport, max_reconnect_attempts=3)
        mgr.connect()
        with pytest.raises(MiniQmtChannelError) as exc_info:
            mgr.require_ready()
        assert exc_info.value.error_code == "ZA-EX-0017"

    def test_run_channel_call_passes_through_when_connected(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        mgr.connect()
        assert mgr.run_channel_call(lambda x: x * 2, 21) == 42

    def test_run_channel_call_fail_closed(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        called = []

        def _order():
            called.append(1)

        with pytest.raises(MiniQmtChannelError):
            mgr.run_channel_call(_order)
        assert called == []  # 闸门在调用前拦截，真单永不发出

    def test_run_channel_call_exception_counts_and_raises(self):
        transport = FakeTransport()
        mgr = MiniQmtChannelManager(transport, max_heartbeat_failures=2)
        mgr.connect()

        def _boom():
            raise RuntimeError("xttrader error")

        with pytest.raises(RuntimeError):
            mgr.run_channel_call(_boom)
        assert mgr.status().consecutive_heartbeat_failures == 1
        with pytest.raises(RuntimeError):
            mgr.run_channel_call(_boom)  # 达阈值触发重连（默认成功）
        assert mgr.state is ChannelState.CONNECTED


class TestDisconnect:
    def test_disconnect_blocks_further_calls(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        mgr.connect()
        mgr.disconnect()
        assert mgr.state is ChannelState.DISCONNECTED
        with pytest.raises(MiniQmtChannelError):
            mgr.require_ready()

    def test_reconnect_after_disconnect(self):
        mgr = MiniQmtChannelManager(FakeTransport())
        mgr.connect()
        mgr.disconnect()
        assert mgr.connect() is True
        assert mgr.is_ready is True
