# -*- coding: utf-8 -*-
"""边界单测：断线重连+状态补齐（GAP-002 + GAP-010）

测试断线重连四步完整流程：
1. xttrader 重连+账户订阅
2. 行情重订阅
3. 订单状态全量同步
4. 策略状态恢复通知
+ 假死心跳检测
"""

import threading
import time
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType


def _spy_on(broker: MiniQmtBroker, name: str, calls: list) -> None:
    """把 broker 的 name 方法替换为记录调用顺序的 mock。"""
    m = MagicMock(name=name)
    m.side_effect = lambda *a, **k: calls.append(name)
    setattr(broker, name, m)


class TestReconnectFourSteps:
    """断线重连四步边界测试。"""

    def test_reconnect_calls_resubscribe(self):
        """重连后调用行情重订阅，且四步顺序完整。"""
        broker = MiniQmtBroker()
        calls: list = []
        for name in (
            "_init_xttrader",
            "_start_once",
            "_do_connect_with_retry",
            "_subscribe_account",
            "_resubscribe_quotes",
            "_sync_order_state_on_reconnect",
            "_notify_reconnect_complete",
        ):
            _spy_on(broker, name, calls)

        assert broker._reconnect() is True
        assert broker._connected is True
        # 四步完整且顺序固定：连接→行情→订单→通知
        assert calls == [
            "_init_xttrader",
            "_start_once",
            "_do_connect_with_retry",
            "_subscribe_account",
            "_resubscribe_quotes",
            "_sync_order_state_on_reconnect",
            "_notify_reconnect_complete",
        ]

    def test_reconnect_syncs_order_state(self):
        """重连后全量同步订单状态：非终态以券商端为准补齐。"""
        broker = MiniQmtBroker()
        broker._account = SimpleNamespace(account_id="test")
        xt_order = SimpleNamespace(
            order_id="ord-1",
            order_status=52,  # 52=FILLED
            traded_volume=100,
            traded_price=10.5,
        )
        broker._xttrader = MagicMock()
        broker._xttrader.query_stock_orders.return_value = [xt_order]

        cached = Order(
            idempotency_key="k-1",
            order_id="ord-1",
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            side=OrderSide.BUY,
            strategy_id="test",
            symbol="600000.SH",
            status=OrderStatus.SUBMITTED,
        )
        broker._order_cache["ord-1"] = cached

        broker._sync_order_state_on_reconnect()

        assert cached.status == OrderStatus.FILLED
        assert cached.filled_quantity == Decimal("100")
        assert cached.avg_fill_price == Decimal("10.5")
        assert cached.updated_at is not None

    def test_reconnect_notifies_callbacks(self):
        """重连后通知注册的回调；单回调异常不阻断后续回调（非致命）。"""
        broker = MiniQmtBroker()
        good = MagicMock()
        bad = MagicMock(side_effect=RuntimeError("callback boom"))
        after = MagicMock()
        broker.register_reconnect_callback(good)
        broker.register_reconnect_callback(bad)
        broker.register_reconnect_callback(after)

        broker._notify_reconnect_complete()

        good.assert_called_once()
        bad.assert_called_once()
        after.assert_called_once()  # bad 抛异常后 after 仍被调用

    def test_status_merge_terminal_no_downgrade(self):
        """终态不降级（FILLED 不被覆盖为 CANCELLED 等）。"""
        broker = MiniQmtBroker()
        assert broker._should_sync_status(OrderStatus.FILLED, OrderStatus.CANCELLED) is False
        assert broker._should_sync_status(OrderStatus.FILLED, OrderStatus.SUBMITTED) is False
        assert broker._should_sync_status(OrderStatus.REJECTED, OrderStatus.FILLED) is False
        assert broker._should_sync_status(OrderStatus.EXPIRED, OrderStatus.FILLED) is False
        assert broker._should_sync_status(OrderStatus.CANCELLED, OrderStatus.REJECTED) is False

    def test_status_merge_cancelled_to_filled(self):
        """CANCELLED 可升级为 FILLED（部分成交后撤单被全成交覆盖）。"""
        broker = MiniQmtBroker()
        assert broker._should_sync_status(OrderStatus.CANCELLED, OrderStatus.FILLED) is True
        # 非终态以券商端为准
        assert broker._should_sync_status(OrderStatus.SUBMITTED, OrderStatus.FILLED) is True
        assert broker._should_sync_status(OrderStatus.PARTIAL, OrderStatus.CANCELLED) is True


class TestHeartbeatDetection:
    """假死心跳检测边界测试。"""

    def test_heartbeat_triggers_reconnect_on_timeout(self):
        """30 秒无 Tick 触发主动重连。"""
        broker = MiniQmtBroker()
        fired = threading.Event()

        def _fake_reconnect():
            fired.set()
            return True

        broker._reconnect = MagicMock(side_effect=_fake_reconnect)
        broker._heartbeat_interval = 0.01  # 测试提速：10ms 巡检
        broker._connected = True
        broker.start_heartbeat()
        try:
            # start_heartbeat 会刷新 _last_tick_ts，之后注入"31 秒无 Tick"假死态
            broker._last_tick_ts = time.monotonic() - 31  # noqa: m46-time — 测试用 monotonic 对齐实现
            assert fired.wait(timeout=2.0), "假死 31 秒未触发重连"
            broker._reconnect.assert_called()
        finally:
            broker.stop_heartbeat()

    def test_heartbeat_no_trigger_when_ticks_flow(self):
        """正常推送时不触发重连。"""
        broker = MiniQmtBroker()
        broker._reconnect = MagicMock()
        broker._heartbeat_interval = 0.01
        broker._connected = True
        broker.start_heartbeat()  # _last_tick_ts 刷新为当前
        try:
            time.sleep(0.1)  # 远超巡检间隔，但 Tick 时间戳新鲜
            broker._reconnect.assert_not_called()
        finally:
            broker.stop_heartbeat()
