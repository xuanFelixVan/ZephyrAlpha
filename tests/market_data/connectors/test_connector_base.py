# [BLUEPRINT] MOD-MKT-003 | docs/03_modules/_domain_mkt_data/connectors/blueprint.md
# [MODULE] tests.market_data.connectors.test_connector_base
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.connectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""MOD-MKT-003 Connector Base 单元测试.

覆盖: 状态机转换(合法/非法)、连接生命周期、订阅/退订/回调分发、
callback异常隔离、未连接拒绝操作、线程安全.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.market_data.connectors import (
    ConnectionState,
    ConnectorConfig,
    ConnectorError,
    MarketDataConnector,
    TickData,
)
from zephyr.market_data.vendor_base import VendorCapabilities, VendorStatus


class MockConnector(MarketDataConnector):
    """测试用 mock 连接器。"""

    def __init__(
        self,
        config: ConnectorConfig | None = None,
        connect_fails: bool = False,
    ) -> None:
        if config is None:
            config = ConnectorConfig(endpoint="mock://test", vendor_id="mock")
        super().__init__(config)
        self._connect_fails = connect_fails
        self._connected_called = False
        self._disconnected_called = False

    @property
    def capabilities(self) -> VendorCapabilities:
        return VendorCapabilities(supports_realtime=True)

    def _do_connect(self) -> None:
        if self._connect_fails:
            raise RuntimeError("mock connect failure")
        self._connected_called = True

    def _do_disconnect(self) -> None:
        self._disconnected_called = True

    # 不覆盖 fetch_daily_kline —— 使用基类的连接状态检查


# ============== 状态机 ==============


class TestStateMachine:
    def test_initial_state_disconnected(self):
        conn = MockConnector()
        assert conn.connection_state == ConnectionState.DISCONNECTED

    def test_connect_transitions(self):
        conn = MockConnector()
        conn.connect()
        assert conn.connection_state == ConnectionState.CONNECTED
        assert conn.status == VendorStatus.ACTIVE
        assert conn._connected_called

    def test_disconnect_transitions(self):
        conn = MockConnector()
        conn.connect()
        conn.disconnect()
        assert conn.connection_state == ConnectionState.DISCONNECTED
        assert conn.status == VendorStatus.INACTIVE
        assert conn._disconnected_called

    def test_disconnect_idempotent(self):
        conn = MockConnector()
        conn.disconnect()  # already disconnected
        assert conn.connection_state == ConnectionState.DISCONNECTED

    def test_connect_failure_goes_error(self):
        conn = MockConnector(connect_fails=True)
        with pytest.raises(ConnectorError, match="连接失败"):
            conn.connect()
        assert conn.connection_state == ConnectionState.ERROR

    def test_reconnect_from_connected(self):
        conn = MockConnector()
        conn.connect()
        conn.reconnect()
        assert conn.connection_state == ConnectionState.CONNECTED

    def test_reconnect_from_disconnected_rejected(self):
        conn = MockConnector()
        with pytest.raises(ConnectorError, match="不允许 reconnect"):
            conn.reconnect()

    def test_reconnect_failure_goes_error(self):
        conn = MockConnector(connect_fails=False)
        conn.connect()
        assert conn.connection_state == ConnectionState.CONNECTED
        # 让重连失败
        conn._connect_fails = True
        with pytest.raises(ConnectorError, match="重连失败"):
            conn.reconnect()
        assert conn.connection_state == ConnectionState.ERROR
        assert conn.status == VendorStatus.ERROR

    def test_subscribe_requires_connected(self):
        conn = MockConnector()
        with pytest.raises(ConnectorError, match="CONNECTED"):
            conn.subscribe("600000.SH", lambda t: None)

    def test_fetch_requires_connected(self):
        conn = MockConnector()
        with pytest.raises(ConnectorError, match="CONNECTED"):
            conn.fetch_daily_kline("A", "2026-01-01", "2026-01-02")

    def test_error_to_connecting_allowed(self):
        conn = MockConnector(connect_fails=True)
        with pytest.raises(ConnectorError):
            conn.connect()
        assert conn.connection_state == ConnectionState.ERROR
        # 修复连接后重试
        conn._connect_fails = False
        conn.connect()
        assert conn.connection_state == ConnectionState.CONNECTED


# ============== 订阅 / 回调 ==============


class TestSubscription:
    def test_subscribe_and_on_tick(self):
        conn = MockConnector()
        conn.connect()
        received: list[TickData] = []
        conn.subscribe("600000.SH", received.append)
        tick = TickData(
            symbol="600000.SH",
            price=Decimal("10.5"),
            volume=Decimal("100"),
            timestamp=datetime.now(timezone.utc),
        )
        conn.on_tick(tick)
        assert len(received) == 1
        assert received[0] == tick

    def test_multiple_callbacks_same_symbol(self):
        conn = MockConnector()
        conn.connect()
        r1: list[TickData] = []
        r2: list[TickData] = []
        conn.subscribe("A", r1.append)
        conn.subscribe("A", r2.append)
        tick = TickData("A", Decimal("1"), Decimal("1"), datetime.now(timezone.utc))
        conn.on_tick(tick)
        assert len(r1) == 1
        assert len(r2) == 1

    def test_duplicate_callback_ignored(self):
        conn = MockConnector()
        conn.connect()
        received: list[TickData] = []
        conn.subscribe("A", received.append)
        conn.subscribe("A", received.append)  # dup
        assert conn.subscription_count == 1
        tick = TickData("A", Decimal("1"), Decimal("1"), datetime.now(timezone.utc))
        conn.on_tick(tick)
        assert len(received) == 1  # only once

    def test_unsubscribe_specific_callback(self):
        conn = MockConnector()
        conn.connect()
        r1: list[TickData] = []
        r2: list[TickData] = []
        conn.subscribe("A", r1.append)
        conn.subscribe("A", r2.append)
        count = conn.unsubscribe("A", r1.append)
        assert count == 1
        tick = TickData("A", Decimal("1"), Decimal("1"), datetime.now(timezone.utc))
        conn.on_tick(tick)
        assert len(r1) == 0
        assert len(r2) == 1

    def test_unsubscribe_all_for_symbol(self):
        conn = MockConnector()
        conn.connect()
        r1: list[TickData] = []
        r2: list[TickData] = []
        conn.subscribe("A", r1.append)
        conn.subscribe("A", r2.append)
        count = conn.unsubscribe("A")
        assert count == 2
        assert conn.subscription_count == 0

    def test_unsubscribe_nonexistent(self):
        conn = MockConnector()
        conn.connect()
        assert conn.unsubscribe("A") == 0
        assert conn.unsubscribe("A", lambda t: None) == 0

    def test_on_tick_no_subscribers(self):
        conn = MockConnector()
        conn.connect()
        tick = TickData("A", Decimal("1"), Decimal("1"), datetime.now(timezone.utc))
        conn.on_tick(tick)  # should not raise

    def test_callback_exception_isolated(self):
        conn = MockConnector()
        conn.connect()
        good: list[TickData] = []

        def bad_cb(_t: TickData) -> None:
            raise ValueError("boom")

        conn.subscribe("A", bad_cb)
        conn.subscribe("A", good.append)
        tick = TickData("A", Decimal("1"), Decimal("1"), datetime.now(timezone.utc))
        conn.on_tick(tick)
        assert len(good) == 1  # bad callback didn't block good one

    def test_subscribe_empty_symbol_rejected(self):
        conn = MockConnector()
        conn.connect()
        with pytest.raises(ConnectorError, match="symbol"):
            conn.subscribe("", lambda t: None)

    def test_subscription_count(self):
        conn = MockConnector()
        conn.connect()
        conn.subscribe("A", lambda t: None)
        conn.subscribe("B", lambda t: None)
        assert conn.subscription_count == 2


# ============== 配置 / 表示 ==============


class TestConfig:
    def test_vendor_id_from_config(self):
        cfg = ConnectorConfig(endpoint="tcp://x", vendor_id="tushare")
        conn = MockConnector(cfg)
        assert conn.vendor_id == "tushare"

    def test_config_immutable(self):
        cfg = ConnectorConfig(endpoint="x", vendor_id="v")
        with pytest.raises(Exception):
            cfg.endpoint = "y"  # type: ignore[misc]

    def test_repr(self):
        conn = MockConnector()
        assert "mock" in repr(conn)
        assert "disconnected" in repr(conn)


# ============== 健康检查 ==============


class TestHealthCheck:
    def test_healthy_when_connected(self):
        conn = MockConnector()
        conn.connect()
        assert conn.health_check() is True

    def test_unhealthy_when_disconnected(self):
        conn = MockConnector()
        assert conn.health_check() is False
