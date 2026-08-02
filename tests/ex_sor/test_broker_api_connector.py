# [BLUEPRINT] MOD-XS-013 | docs/03_modules/_domain-ex_sor/broker_api_connector/blueprint.md | §
# [TTL] permanent
"""BrokerApiConnector 单元测试 (MOD-XS-013)。协议层 + 心跳 + 限速 + 熔断。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.api.api_rate_limiter import (
    ApiRateLimiter,
    RateLimitConfig,
    TradingSession,
)
from zephyr.ex_sor.api.broker_api_connector import (
    BrokerApiConnector,
    BrokerConnectionError,
    BrokerProtocol,
    BrokerSubmitError,
    BrokerType,
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitBreakerState,
    ConnectionConfig,
    ConnectionState,
    HeartbeatManager,
    HeartbeatTimeoutError,
    RateLimitedError,
    ReconnectPolicy,
    SimulatedProtocol,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order

NOW = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)


def make_order(order_id: str = "ORD-001") -> Order:
    """构造测试用 Order。"""
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


# ── ConnectionConfig ──────────────────────────────────────────────────────────


def test_config_defaults():
    cfg = ConnectionConfig()
    assert cfg.broker == BrokerType.SIMULATED
    assert cfg.heartbeat_interval == pytest.approx(30.0)
    assert cfg.heartbeat_max_missed == 3
    assert cfg.session_timeout == pytest.approx(1800.0)
    assert cfg.reconnect_max_attempts == 3
    assert cfg.reconnect_backoff_base == pytest.approx(1.0)
    assert cfg.circuit_failure_threshold == 5


def test_config_invalid_heartbeat_interval():
    with pytest.raises(BrokerConnectionError):
        ConnectionConfig(heartbeat_interval=0)


def test_config_invalid_max_missed():
    with pytest.raises(BrokerConnectionError):
        ConnectionConfig(heartbeat_max_missed=0)


def test_config_invalid_reconnect_attempts():
    with pytest.raises(BrokerConnectionError):
        ConnectionConfig(reconnect_max_attempts=-1)


def test_config_frozen():
    cfg = ConnectionConfig()
    with pytest.raises(Exception):
        cfg.heartbeat_interval = 99  # type: ignore[misc]


# ── HeartbeatManager ──────────────────────────────────────────────────────────


def test_heartbeat_start_resets():
    hm = HeartbeatManager(ConnectionConfig())
    hm.start(now=100.0)
    assert hm.missed_count == 0
    assert hm.is_healthy is True


def test_heartbeat_success_resets_missed():
    hm = HeartbeatManager(ConnectionConfig())
    hm.start(now=100.0)
    hm.on_heartbeat_failure()
    hm.on_heartbeat_failure()
    assert hm.missed_count == 2
    hm.on_heartbeat_success(now=200.0)
    assert hm.missed_count == 0
    assert hm.is_healthy is True


def test_heartbeat_failure_trips_at_max():
    cfg = ConnectionConfig(heartbeat_max_missed=3)
    hm = HeartbeatManager(cfg)
    hm.start(now=100.0)
    assert hm.on_heartbeat_failure() is False  # 1
    assert hm.on_heartbeat_failure() is False  # 2
    assert hm.on_heartbeat_failure() is True  # 3 → 超限


def test_heartbeat_is_due():
    cfg = ConnectionConfig(heartbeat_interval=0.1)
    hm = HeartbeatManager(cfg)
    hm.start(now=100.0)
    assert hm.is_due(now=100.0) is False
    assert hm.is_due(now=100.15) is True


def test_heartbeat_not_started_not_due():
    hm = HeartbeatManager(ConnectionConfig())
    assert hm.is_due() is False


# ── ReconnectPolicy ───────────────────────────────────────────────────────────


def test_reconnect_should_retry():
    rp = ReconnectPolicy(ConnectionConfig(reconnect_max_attempts=3))
    assert rp.should_retry() is True
    assert rp.remaining == 3


def test_reconnect_backoff_exponential():
    rp = ReconnectPolicy(ConnectionConfig(reconnect_max_attempts=4, reconnect_backoff_base=1.0))
    assert rp.next_backoff() == pytest.approx(1.0)  # 2^0
    assert rp.next_backoff() == pytest.approx(2.0)  # 2^1
    assert rp.next_backoff() == pytest.approx(4.0)  # 2^2
    assert rp.next_backoff() == pytest.approx(8.0)  # 2^3
    assert rp.should_retry() is False


def test_reconnect_reset():
    rp = ReconnectPolicy(ConnectionConfig(reconnect_max_attempts=2))
    rp.next_backoff()
    rp.next_backoff()
    assert rp.should_retry() is False
    rp.reset()
    assert rp.should_retry() is True
    assert rp.attempt == 0


def test_reconnect_zero_attempts():
    rp = ReconnectPolicy(ConnectionConfig(reconnect_max_attempts=0))
    assert rp.should_retry() is False
    assert rp.remaining == 0


# ── CircuitBreaker ────────────────────────────────────────────────────────────


def test_circuit_breaker_initial_closed():
    cb = CircuitBreaker(threshold=5)
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.is_open is False
    assert cb.failure_count == 0


def test_circuit_breaker_records_failures():
    cb = CircuitBreaker(threshold=3)
    assert cb.record_failure() is False  # 1
    assert cb.record_failure() is False  # 2
    assert cb.record_failure() is True  # 3 → OPEN


def test_circuit_breaker_open_rejects():
    cb = CircuitBreaker(threshold=1)
    cb.record_failure()  # → OPEN
    assert cb.is_open is True
    with pytest.raises(CircuitBreakerOpenError):
        cb.check()


def test_circuit_breaker_success_resets_count():
    cb = CircuitBreaker(threshold=3)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb.failure_count == 0
    assert cb.state == CircuitBreakerState.CLOSED


def test_circuit_breaker_manual_reset():
    cb = CircuitBreaker(threshold=1)
    cb.record_failure()  # → OPEN
    assert cb.is_open is True
    cb.manual_reset()
    assert cb.is_open is False
    assert cb.failure_count == 0


def test_circuit_breaker_success_does_not_clear_open():
    """OPEN 状态下 record_success 不自动恢复 (HB-06 需人工)。"""
    cb = CircuitBreaker(threshold=1)
    cb.record_failure()  # → OPEN
    cb.record_success()
    assert cb.is_open is True  # 仍 OPEN


def test_circuit_breaker_invalid_threshold():
    with pytest.raises(BrokerConnectionError):
        CircuitBreaker(threshold=0)


# ── BrokerApiConnector: 连接 ─────────────────────────────────────────────────


def test_connector_initial_state():
    conn = BrokerApiConnector(SimulatedProtocol())
    assert conn.state == ConnectionState.DISCONNECTED
    assert conn.is_connected is False


def test_connector_connect_success():
    proto = SimulatedProtocol()
    conn = BrokerApiConnector(proto)
    conn.connect()
    assert conn.is_connected is True
    assert proto.is_connected is True


def test_connector_connect_idempotent():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    conn.connect()  # 不抛异常
    assert conn.is_connected is True


def test_connector_disconnect():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    conn.disconnect()
    assert conn.state == ConnectionState.DISCONNECTED
    assert conn.is_connected is False


def test_connector_disconnect_idempotent():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.disconnect()  # 未连接也能调
    conn.connect()
    conn.disconnect()
    conn.disconnect()  # 不抛异常


# ── BrokerApiConnector: 下单 (HB-07 零重试) ──────────────────────────────────


def test_submit_order_success():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    order = make_order()
    broker_id = conn.submit_order(order)
    assert broker_id == f"BROKER-{order.order_id}"


def test_submit_order_zero_retry_hb07():
    """下单失败不重试 (HB-07), 直接抛 BrokerSubmitError。"""
    proto = SimulatedProtocol()
    proto.set_failure_mode(submit=True)
    conn = BrokerApiConnector(proto)
    conn.connect()
    with pytest.raises(BrokerSubmitError, match="HB-07"):
        conn.submit_order(make_order())
    # 验证只调用了一次 (零重试)
    assert proto.submit_call_count == 1


def test_submit_order_not_connected():
    conn = BrokerApiConnector(SimulatedProtocol())
    with pytest.raises(BrokerConnectionError, match="未连接"):
        conn.submit_order(make_order())


def test_submit_order_circuit_open():
    """熔断 OPEN 时下单被拒 (HB-06)。"""
    proto = SimulatedProtocol()
    cfg = ConnectionConfig(circuit_failure_threshold=1)
    conn = BrokerApiConnector(proto, cfg)
    conn.connect()
    proto.set_failure_mode(submit=True)
    with pytest.raises(BrokerSubmitError):
        conn.submit_order(make_order())  # 失败 → 熔断 OPEN
    # 再次下单 → 被熔断拦截
    with pytest.raises(CircuitBreakerOpenError):
        conn.submit_order(make_order())


# ── BrokerApiConnector: 撤单 / 查询 ──────────────────────────────────────────


def test_cancel_order_success():
    proto = SimulatedProtocol()
    conn = BrokerApiConnector(proto)
    conn.connect()
    order = make_order()
    broker_id = conn.submit_order(order)
    assert conn.cancel_order(broker_id) is True


def test_cancel_order_not_found():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    assert conn.cancel_order("NONEXIST") is False


def test_query_position():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    positions = conn.query_position()
    assert isinstance(positions, list)


# ── BrokerApiConnector: 心跳 ─────────────────────────────────────────────────


def test_heartbeat_success():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    assert conn.send_heartbeat() is True
    assert conn.heartbeat.missed_count == 0


def test_heartbeat_failure_increments():
    proto = SimulatedProtocol()
    proto.set_failure_mode(heartbeat=True)
    cfg = ConnectionConfig(heartbeat_max_missed=3)
    conn = BrokerApiConnector(proto, cfg)
    conn.connect()
    assert conn.send_heartbeat() is False  # 1
    assert conn.heartbeat.missed_count == 1
    assert conn.send_heartbeat() is False  # 2
    assert conn.heartbeat.missed_count == 2


def test_heartbeat_timeout_disconnects():
    """心跳连续失败达上限 → 断开连接。"""
    proto = SimulatedProtocol()
    proto.set_failure_mode(heartbeat=True)
    cfg = ConnectionConfig(heartbeat_max_missed=2)
    conn = BrokerApiConnector(proto, cfg)
    conn.connect()
    conn.send_heartbeat()  # 1 fail
    with pytest.raises(HeartbeatTimeoutError):
        conn.send_heartbeat()  # 2 fail → 超限
    assert conn.state == ConnectionState.DISCONNECTED


def test_heartbeat_not_connected_returns_false():
    conn = BrokerApiConnector(SimulatedProtocol())
    assert conn.send_heartbeat() is False


# ── BrokerApiConnector: 限速集成 (XS-014) ────────────────────────────────────


def test_rate_limited_blocks_submit():
    """L1 全局限流满时, 下单被拦截。"""
    cfg = RateLimitConfig(l1_global_qps=1, l2_system_tps=100, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    conn = BrokerApiConnector(SimulatedProtocol(), rate_limiter=limiter)
    conn.connect()
    conn.submit_order(make_order())  # 消耗唯一配额
    with pytest.raises(RateLimitedError):
        conn.submit_order(make_order("ORD-002"))


def test_rate_limited_blocks_cancel():
    cfg = RateLimitConfig(l1_global_qps=1, l2_system_tps=100, l3_intraday_tps=100)
    limiter = ApiRateLimiter(cfg)
    conn = BrokerApiConnector(SimulatedProtocol(), rate_limiter=limiter)
    conn.connect()
    broker_id = conn.submit_order(make_order())
    with pytest.raises(RateLimitedError):
        conn.cancel_order(broker_id)


def test_rate_limit_off_hours_blocks_non_p0():
    """非交易时段, 撤单 (P1) 被限速器拦截。"""
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    with pytest.raises(RateLimitedError):
        conn.cancel_order("X", session=TradingSession.OFF_HOURS)


# ── BrokerApiConnector: 熔断恢复 ─────────────────────────────────────────────


def test_manual_reset_circuit():
    """HB-06: 熔断后需人工 manual_reset_circuit 恢复。"""
    proto = SimulatedProtocol()
    cfg = ConnectionConfig(circuit_failure_threshold=2)
    conn = BrokerApiConnector(proto, cfg)
    conn.connect()
    proto.set_failure_mode(submit=True)
    # 2 次失败 → 熔断 OPEN
    with pytest.raises(BrokerSubmitError):
        conn.submit_order(make_order("O1"))
    with pytest.raises(BrokerSubmitError):
        conn.submit_order(make_order("O2"))
    assert conn.circuit_breaker.is_open is True
    # 下单被熔断拦截
    with pytest.raises(CircuitBreakerOpenError):
        conn.submit_order(make_order("O3"))
    # 人工恢复
    conn.manual_reset_circuit()
    assert conn.circuit_breaker.is_open is False
    assert conn.state == ConnectionState.DISCONNECTED


def test_circuit_accumulates_failures():
    """多次下单失败累积到阈值才熔断。"""
    proto = SimulatedProtocol()
    cfg = ConnectionConfig(circuit_failure_threshold=3)
    conn = BrokerApiConnector(proto, cfg)
    conn.connect()
    proto.set_failure_mode(submit=True)
    for i in range(3):
        with pytest.raises(BrokerSubmitError):
            conn.submit_order(make_order(f"O{i}"))
    assert conn.circuit_breaker.is_open is True


# ── BrokerApiConnector: 成交回调 ─────────────────────────────────────────────


def test_fill_callback_registered_and_called():
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    received: list = []
    conn.register_fill_callback(lambda f: received.append(f))
    # 模拟收到成交回报
    from zephyr.shared.contracts.fill import Fill

    fill = Fill(
        fill_id="F1",
        fill_price=Decimal("10.50"),
        fill_timestamp=NOW,
        filled_quantity=Decimal("100"),
        idempotency_key="IK1",
        order_id="ORD-001",
        strategy_id="STRAT-1",
        symbol="000001.SZ",
    )
    conn.on_fill_received(fill)
    assert len(received) == 1
    assert received[0].fill_id == "F1"


def test_fill_callback_exception_isolated():
    """一个回调异常不影响其他回调。"""
    conn = BrokerApiConnector(SimulatedProtocol())
    conn.connect()
    ok: list = []

    def bad_cb(f):
        raise RuntimeError("boom")

    conn.register_fill_callback(bad_cb)
    conn.register_fill_callback(lambda f: ok.append(f))
    from zephyr.shared.contracts.fill import Fill

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
    conn.on_fill_received(fill)
    assert len(ok) == 1  # 第二个回调仍执行


# ── 状态机非法转换 ────────────────────────────────────────────────────────────


def test_illegal_transition_disconnected_to_connected():
    """不能从 DISCONNECTED 直接跳到 CONNECTED (必须经过 CONNECTING)。"""
    conn = BrokerApiConnector(SimulatedProtocol())
    with pytest.raises(BrokerConnectionError, match="非法状态转换"):
        conn._transition(ConnectionState.CONNECTED)


def test_illegal_transition_circuit_open_to_connected():
    """CIRCUIT_OPEN 不能直接到 CONNECTED (需 manual_reset → DISCONNECTED → CONNECTING)。"""
    conn = BrokerApiConnector(SimulatedProtocol())
    conn._transition(ConnectionState.CONNECTING)
    conn._transition(ConnectionState.CONNECTED)
    conn._transition(ConnectionState.CIRCUIT_OPEN)
    with pytest.raises(BrokerConnectionError, match="非法状态转换"):
        conn._transition(ConnectionState.CONNECTED)


# ── SimulatedProtocol ─────────────────────────────────────────────────────────


def test_simulated_protocol_failure_injection():
    proto = SimulatedProtocol()
    proto.connect()
    proto.set_failure_mode(submit=True, heartbeat=True, cancel=True)
    with pytest.raises(BrokerSubmitError):
        proto.submit_order_raw(make_order())
    assert proto.send_heartbeat() is False
    assert proto.cancel_order_raw("X") is False


def test_simulated_protocol_tracks_call_counts():
    proto = SimulatedProtocol()
    proto.connect()
    proto.send_heartbeat()
    proto.send_heartbeat()
    assert proto.heartbeat_call_count == 2
