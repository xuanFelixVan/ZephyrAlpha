# [BLUEPRINT] MOD-XS-002 | docs/03_modules/_domain_ex_sor/broker_adapter_manager/blueprint.md | §
# [TTL] permanent
"""BrokerAdapterManager 单元测试 (MOD-XS-002)。多券商 + 故障转移 + Feature Toggle。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.api.api_rate_limiter import TradingSession
from zephyr.ex_sor.api.broker_api_connector import (
    BrokerApiConnector,
    BrokerType,
    CircuitBreakerOpenError,
    ConnectionConfig,
    SimulatedProtocol,
)
from zephyr.ex_sor.core.broker_adapter_manager import (
    BrokerAdapter,
    BrokerAdapterError,
    BrokerAdapterManager,
    BrokerSelection,
    FailoverExhaustedError,
    NoAvailableBrokerError,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)


def make_order(order_id: str = "ORD-001") -> Order:
    return Order(
        order_id=order_id,
        idempotency_key=f"IDEMP-{order_id}",
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        side=OrderSide.BUY,
        strategy_id="STRAT-1",
        symbol="000001.SZ",
        limit_price=Decimal("10.50"),
    )


def make_adapter(
    broker: BrokerType = BrokerType.SIMULATED,
    circuit_threshold: int = 5,
) -> BrokerAdapter:
    """构造已连接的 BrokerAdapter (使用 SimulatedProtocol)。"""
    proto = SimulatedProtocol()
    cfg = ConnectionConfig(broker=broker, circuit_failure_threshold=circuit_threshold)
    conn = BrokerApiConnector(proto, cfg)
    return BrokerAdapter(broker, conn)


# ── BrokerAdapter ─────────────────────────────────────────────────────────────


def test_adapter_initial_state():
    adapter = make_adapter()
    assert adapter.broker_type == BrokerType.SIMULATED
    assert adapter.is_connected is False
    assert adapter.is_available is False


def test_adapter_connect():
    adapter = make_adapter()
    adapter.connect()
    assert adapter.is_connected is True
    assert adapter.is_available is True


def test_adapter_disconnect():
    adapter = make_adapter()
    adapter.connect()
    adapter.disconnect()
    assert adapter.is_connected is False


def test_adapter_submit_order():
    adapter = make_adapter()
    adapter.connect()
    order = make_order()
    broker_id = adapter.submit_order(order)
    assert broker_id == f"BROKER-{order.order_id}"


def test_adapter_cancel_order():
    adapter = make_adapter()
    adapter.connect()
    order = make_order()
    broker_id = adapter.submit_order(order)
    assert adapter.cancel_order(broker_id) is True


def test_adapter_circuit_open_not_available():
    """熔断开启后 is_available 为 False。"""
    proto = SimulatedProtocol()
    cfg = ConnectionConfig(circuit_failure_threshold=1)
    conn = BrokerApiConnector(proto, cfg)
    adapter = BrokerAdapter(BrokerType.SIMULATED, conn)
    adapter.connect()
    proto.set_failure_mode(submit=True)
    with pytest.raises(Exception):
        adapter.submit_order(make_order())
    assert adapter.is_available is False
    assert adapter.is_connected is True  # 仍连接, 只是熔断


def test_adapter_reset_circuit():
    adapter = make_adapter(circuit_threshold=1)
    adapter.connect()
    adapter.connector.circuit_breaker.record_failure()  # OPEN
    assert adapter.is_available is False
    adapter.reset_circuit()
    assert adapter.is_available is True


# ── BrokerAdapterManager: 注册 ────────────────────────────────────────────────


def test_mgr_initial_empty():
    mgr = BrokerAdapterManager()
    assert mgr.active_broker is None
    assert mgr.registered_brokers == []
    assert mgr.available_brokers == []


def test_mgr_register_primary():
    mgr = BrokerAdapterManager()
    adapter = make_adapter(BrokerType.MINIQMT)
    mgr.register_adapter(adapter, primary=True)
    assert mgr.active_broker == BrokerType.MINIQMT
    assert BrokerType.MINIQMT in mgr.registered_brokers


def test_mgr_register_duplicate():
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT))
    with pytest.raises(BrokerAdapterError, match="已注册"):
        mgr.register_adapter(make_adapter(BrokerType.MINIQMT))


def test_mgr_register_multiple():
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.register_adapter(make_adapter(BrokerType.XTP))
    assert mgr.registered_brokers == [BrokerType.MINIQMT, BrokerType.XTP]
    assert mgr.active_broker == BrokerType.MINIQMT


def test_mgr_first_registered_becomes_active():
    """无 primary 时, 首个注册的自动成为 active。"""
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.XTP))
    assert mgr.active_broker == BrokerType.XTP


# ── BrokerAdapterManager: 连接 ────────────────────────────────────────────────


def test_mgr_connect_all():
    mgr = BrokerAdapterManager()
    a1 = make_adapter(BrokerType.MINIQMT)
    a2 = make_adapter(BrokerType.XTP)
    mgr.register_adapter(a1, primary=True)
    mgr.register_adapter(a2)
    mgr.connect_all()
    assert a1.is_connected
    assert a2.is_connected


def test_mgr_disconnect_all():
    mgr = BrokerAdapterManager()
    a1 = make_adapter(BrokerType.MINIQMT)
    mgr.register_adapter(a1, primary=True)
    mgr.connect_all()
    mgr.disconnect_all()
    assert not a1.is_connected


# ── BrokerAdapterManager: 下单 ────────────────────────────────────────────────


def test_mgr_submit_order_primary():
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.connect_all()
    sel = mgr.submit_order(make_order())
    assert sel.broker == BrokerType.MINIQMT
    assert sel.failovered is False
    assert sel.broker_order_id.startswith("BROKER-")


def test_mgr_submit_no_brokers():
    mgr = BrokerAdapterManager()
    with pytest.raises(NoAvailableBrokerError):
        mgr.submit_order(make_order())


# ── BrokerAdapterManager: 故障转移 ───────────────────────────────────────────


def test_mgr_failover_on_circuit_open():
    """active 券商熔断 → 自动故障转移到备选。"""
    mgr = BrokerAdapterManager()
    # primary: miniQMT, 容易熔断 (threshold=1)
    proto1 = SimulatedProtocol()
    cfg1 = ConnectionConfig(broker=BrokerType.MINIQMT, circuit_failure_threshold=1)
    conn1 = BrokerApiConnector(proto1, cfg1)
    mgr.register_adapter(BrokerAdapter(BrokerType.MINIQMT, conn1), primary=True)

    # backup: XTP
    proto2 = SimulatedProtocol()
    cfg2 = ConnectionConfig(broker=BrokerType.XTP, circuit_failure_threshold=5)
    conn2 = BrokerApiConnector(proto2, cfg2)
    mgr.register_adapter(BrokerAdapter(BrokerType.XTP, conn2))

    mgr.connect_all()

    # 第一次下单成功
    sel1 = mgr.submit_order(make_order("O1"))
    assert sel1.broker == BrokerType.MINIQMT
    assert sel1.failovered is False

    # 注入故障 → 熔断
    proto1.set_failure_mode(submit=True)
    # 第二次下单 → 熔断 → 故障转移到 XTP
    sel2 = mgr.submit_order(make_order("O2"))
    assert sel2.broker == BrokerType.XTP
    assert sel2.failovered is True
    assert mgr.active_broker == BrokerType.XTP
    assert mgr.failover_count == 1


def test_mgr_failover_all_exhausted():
    """所有券商都熔断 → FailoverExhaustedError。"""
    mgr = BrokerAdapterManager()

    # 两个券商都 threshold=1
    for bt in (BrokerType.MINIQMT, BrokerType.XTP):
        proto = SimulatedProtocol()
        proto.set_failure_mode(submit=True)  # 直接故障
        cfg = ConnectionConfig(broker=bt, circuit_failure_threshold=1)
        conn = BrokerApiConnector(proto, cfg)
        mgr.register_adapter(BrokerAdapter(bt, conn), primary=(bt == BrokerType.MINIQMT))

    mgr.connect_all()

    # 第一次: miniQMT 熔断
    with pytest.raises(Exception):
        mgr.submit_order(make_order("O1"))
    # 第二次: 尝试故障转移, XTP 也熔断
    with pytest.raises(FailoverExhaustedError):
        mgr.submit_order(make_order("O2"))


def test_mgr_manual_failover():
    """手动触发故障转移。"""
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.register_adapter(make_adapter(BrokerType.XTP))
    mgr.connect_all()
    assert mgr.active_broker == BrokerType.MINIQMT
    new = mgr.failover()
    assert new == BrokerType.XTP
    assert mgr.active_broker == BrokerType.XTP


def test_mgr_manual_failover_no_backup():
    """无备选时手动故障转移返回 None。"""
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.connect_all()
    assert mgr.failover() is None


# ── BrokerAdapterManager: Feature Toggle ──────────────────────────────────────


def test_mgr_switch_broker():
    """运行时切换券商 (Feature Toggle, §6.5)。"""
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.register_adapter(make_adapter(BrokerType.XTP))
    mgr.connect_all()
    assert mgr.active_broker == BrokerType.MINIQMT
    mgr.switch_broker(BrokerType.XTP)
    assert mgr.active_broker == BrokerType.XTP
    # 下单走新 active
    sel = mgr.submit_order(make_order())
    assert sel.broker == BrokerType.XTP


def test_mgr_switch_unregistered():
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    with pytest.raises(BrokerAdapterError, match="未注册"):
        mgr.switch_broker(BrokerType.OKX)


# ── BrokerAdapterManager: 撤单 ───────────────────────────────────────────────


def test_mgr_cancel_order():
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.connect_all()
    sel = mgr.submit_order(make_order())
    result = mgr.cancel_order(sel.broker, sel.broker_order_id)
    assert result is True


def test_mgr_cancel_wrong_broker():
    """撤单时指定未注册的券商 → 报错。"""
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.connect_all()
    with pytest.raises(BrokerAdapterError, match="未注册"):
        mgr.cancel_order(BrokerType.OKX, "BROKER-X")


# ── BrokerAdapterManager: 成交回调 ───────────────────────────────────────────


def test_mgr_fill_callback_global():
    """全局回调应用到所有适配器。"""
    mgr = BrokerAdapterManager()
    a1 = make_adapter(BrokerType.MINIQMT)
    a2 = make_adapter(BrokerType.XTP)
    mgr.register_adapter(a1, primary=True)
    mgr.register_adapter(a2)

    received: list[Fill] = []
    mgr.register_fill_callback(lambda f: received.append(f))

    fill = Fill(
        fill_id="F1",
        fill_price=Decimal("10"),
        fill_timestamp=NOW,
        filled_quantity=Decimal("100"),
        idempotency_key="IK1",
        order_id="O1",
        strategy_id="S1",
        symbol="000001.SZ",
    )
    a1.on_fill_received(fill)
    a2.on_fill_received(fill)
    assert len(received) == 2  # 每个适配器各收到一次


def test_mgr_fill_callback_late_register():
    """后注册的适配器也获得已有全局回调。"""
    mgr = BrokerAdapterManager()
    received: list[Fill] = []
    mgr.register_fill_callback(lambda f: received.append(f))

    # 回调注册后再添加适配器
    a1 = make_adapter(BrokerType.MINIQMT)
    mgr.register_adapter(a1, primary=True)

    fill = Fill(
        fill_id="F1",
        fill_price=Decimal("10"),
        fill_timestamp=NOW,
        filled_quantity=Decimal("100"),
        idempotency_key="IK1",
        order_id="O1",
        strategy_id="S1",
        symbol="000001.SZ",
    )
    a1.on_fill_received(fill)
    assert len(received) == 1


# ── BrokerAdapterManager: 诊断 ───────────────────────────────────────────────


def test_mgr_get_broker_status():
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.register_adapter(make_adapter(BrokerType.XTP))
    mgr.connect_all()
    status = mgr.get_broker_status()
    assert BrokerType.MINIQMT in status
    assert status[BrokerType.MINIQMT]["is_connected"] is True
    assert status[BrokerType.MINIQMT]["is_active"] is True
    assert status[BrokerType.XTP]["is_active"] is False


def test_mgr_available_brokers():
    mgr = BrokerAdapterManager()
    mgr.register_adapter(make_adapter(BrokerType.MINIQMT), primary=True)
    mgr.register_adapter(make_adapter(BrokerType.XTP))
    mgr.connect_all()
    assert len(mgr.available_brokers) == 2


def test_mgr_available_brokers_excludes_circuit_open():
    """熔断的券商不在可用列表。"""
    proto = SimulatedProtocol()
    cfg = ConnectionConfig(broker=BrokerType.MINIQMT, circuit_failure_threshold=1)
    conn = BrokerApiConnector(proto, cfg)
    adapter = BrokerAdapter(BrokerType.MINIQMT, conn)
    mgr = BrokerAdapterManager()
    mgr.register_adapter(adapter, primary=True)
    mgr.connect_all()
    # 触发熔断
    conn.circuit_breaker.record_failure()
    assert BrokerType.MINIQMT not in mgr.available_brokers


# ── BrokerSelection ───────────────────────────────────────────────────────────


def test_broker_selection_dataclass():
    sel = BrokerSelection(
        broker=BrokerType.MINIQMT,
        broker_order_id="BROKER-001",
        failovered=False,
    )
    assert sel.broker == BrokerType.MINIQMT
    assert sel.broker_order_id == "BROKER-001"
    assert sel.failovered is False


def test_broker_selection_frozen():
    sel = BrokerSelection(BrokerType.MINIQMT, "X")
    with pytest.raises(Exception):
        sel.broker = BrokerType.XTP  # type: ignore[misc]
