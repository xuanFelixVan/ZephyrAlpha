# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] tests/ex_core/test_open_order_resolver.py
# [TTL] task_bound
# 对应: src/zephyr/ex_core/open_order_resolver.py
# 覆盖: gap 6 未成交续接（Make-or-Take / PARTIAL / 尾盘清退 / 幂等）
"""OpenOrderResolver 单元测试（40_execution_broker §决策⑪ gap 6）。

覆盖场景：
  1. SUBMITTED 未成交：≤T秒等待 / >T秒 Make-or-Take 切换
  2. Make-or-Take：撤单成功+对手价重挂 / 撤单失败 / 无对手价数据跳过重挂
  3. PARTIAL：剩余<min_unit忽略转CANCELLED / urgency=高补单 / urgency=低留单
  4. 14:55 尾盘清退：正常撤单 / 撤单失败
  5. 幂等：终态订单跳过 / 未注册订单跳过
  6. 异常鲁棒：单笔异常不阻断其他订单
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.open_order_resolver import (
    OpenOrderResolver,
    OpenOrderResolverConfig,
    ResolveAction,
    ResolveActionType,
    Urgency,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.order import Order

# ───────────────────────── Fixtures ─────────────────────────


def _make_order(
    order_id: str = "ord-1",
    symbol: str = "600000.SH",
    side: OrderSide = OrderSide.BUY,
    status: OrderStatus = OrderStatus.SUBMITTED,
    quantity: Decimal = Decimal("500"),
    filled_quantity: Decimal = Decimal("0"),
) -> Order:
    """构造测试用 Order。"""
    return Order(
        order_id=order_id,
        idempotency_key=f"idem-{order_id}",
        symbol=symbol,
        strategy_id="test-strat",
        side=side,
        order_type=OrderType.LIMIT,
        quantity=quantity,
        limit_price=Decimal("10.00"),
        status=status,
        filled_quantity=filled_quantity,
        created_at=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
    )


def _make_mock_order_manager(
    open_orders: list[Order] | None = None,
    cancel_returns: bool = True,
    create_returns: Order | None = None,
    submit_returns: str = "broker-new-1",
) -> MagicMock:
    """构造 mock OrderManager。"""
    om = MagicMock()
    om.get_open_orders.return_value = open_orders or []
    om.cancel_order.return_value = cancel_returns
    if create_returns is not None:
        om.create_order.return_value = create_returns
    om.submit_order.return_value = submit_returns
    return om


@pytest.fixture
def frozen_clock() -> Any:
    """可控时钟（返回固定值，每调用一次 +step）。"""
    state = {"t": 0.0}

    def _clock() -> float:
        return state["t"]

    def _advance(step: float) -> None:
        state["t"] += step

    def _set(t: float) -> None:
        state["t"] = t

    _clock.advance = _advance  # type: ignore[attr-defined]
    _clock.set = _set  # type: ignore[attr-defined]
    return _clock


@pytest.fixture
def trading_now() -> Any:
    """可控 datetime（交易时段，避免触发 14:55 清退）。"""
    state = {"dt": datetime(2026, 8, 10, 10, 30, tzinfo=timezone.utc)}

    def _now() -> datetime:
        return state["dt"]

    def _set(dt: datetime) -> None:
        state["dt"] = dt

    _now.set = _set  # type: ignore[attr-defined]
    return _now


# ───────────────────────── SUBMITTED 状态 ─────────────────────────


class TestSubmittedNotFilled:
    """SUBMITTED 未成交场景。"""

    def test_within_timeout_waits(self, frozen_clock, trading_now):
        """挂单 ≤ T 秒 → WAIT。"""
        order = _make_order()
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(100.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(110.0)  # elapsed = 10s ≤ 30s

        actions = resolver.scan_and_resolve()

        assert len(actions) == 1
        assert actions[0].action_type is ResolveActionType.WAIT
        assert actions[0].success is True
        om.cancel_order.assert_not_called()

    def test_timeout_triggers_make_or_take(self, frozen_clock, trading_now):
        """挂单 > T 秒 → Make-or-Take 切换。"""
        order = _make_order()
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(100.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(200.0)  # elapsed = 100s > 30s

        actions = resolver.scan_and_resolve()

        assert len(actions) == 1
        assert actions[0].action_type is ResolveActionType.MAKE_OR_TAKE
        assert actions[0].success is True
        om.cancel_order.assert_called_once_with(order.order_id)

    def test_cancel_fail_marks_unsuccessful(self, frozen_clock, trading_now):
        """撤单失败（已成交）→ success=False。"""
        order = _make_order()
        om = _make_mock_order_manager(open_orders=[order], cancel_returns=False)
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.MAKE_OR_TAKE
        assert actions[0].success is False

    def test_no_opponent_provider_skips_resubmit(self, frozen_clock, trading_now):
        """无 opponent_price_provider → 撤单成功但跳过重挂。"""
        order = _make_order()
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=None,  # 无盘口
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.MAKE_OR_TAKE
        assert actions[0].success is True
        om.create_order.assert_not_called()  # 没重挂

    def test_opponent_returns_none_skips_resubmit(self, frozen_clock, trading_now):
        """对手价返回 None（盘口空）→ 撤单成功但跳过重挂。"""
        order = _make_order()
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: None,  # 盘口空
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.MAKE_OR_TAKE
        assert actions[0].success is True
        om.create_order.assert_not_called()

    def test_resubmit_callback_invoked(self, frozen_clock, trading_now):
        """注入 resubmit_callback → 调用回调而非 order_manager.create_order。"""
        order = _make_order()
        om = _make_mock_order_manager(open_orders=[order])
        callback = MagicMock(return_value="broker-cb-1")
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
            resubmit_callback=callback,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()

        assert actions[0].success is True
        callback.assert_called_once()
        # 第一个参数是 order，第二个是对手价
        called_order, called_price = callback.call_args.args
        assert called_order.order_id == order.order_id
        assert called_price == Decimal("10.10")
        om.create_order.assert_not_called()


# ───────────────────────── PARTIAL 状态 ─────────────────────────


class TestPartialFilled:
    """PARTIAL 部分成交场景。"""

    def test_partial_below_threshold_ignored(self, frozen_clock, trading_now):
        """PARTIAL 剩余 < min_unit（100股）→ 忽略转 CANCELLED。"""
        # 总量 500，已成交 450，剩余 50 < 100
        order = _make_order(
            quantity=Decimal("500"),
            filled_quantity=Decimal("450"),
            status=OrderStatus.PARTIAL,
        )
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(
                make_or_take_timeout_seconds=30.0,
                partial_ignore_threshold=100,
            ),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.LOW)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.IGNORE_PARTIAL
        assert actions[0].success is True
        om.cancel_order.assert_called_once_with(order.order_id)

    def test_partial_high_urgency_make_or_take(self, frozen_clock, trading_now):
        """PARTIAL 剩余 ≥ min_unit + urgency=高 → Make-or-Take 补单。"""
        # 总量 500，已成交 100，剩余 400 ≥ 100，urgency=HIGH
        order = _make_order(
            quantity=Decimal("500"),
            filled_quantity=Decimal("100"),
            status=OrderStatus.PARTIAL,
        )
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(60.0)  # 超时

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.MAKE_OR_TAKE
        # 应以剩余量 400 重挂（非全量 500）
        new_order = om.create_order.return_value
        om.submit_order.assert_called_once_with(new_order.order_id)

    def test_partial_low_urgency_leaves_open(self, frozen_clock, trading_now):
        """PARTIAL 剩余 ≥ min_unit + urgency=低 → LEAVE_OPEN 留单等成交。"""
        order = _make_order(
            quantity=Decimal("500"),
            filled_quantity=Decimal("100"),
            status=OrderStatus.PARTIAL,
        )
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.LOW)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.LEAVE_OPEN
        assert actions[0].success is True
        om.cancel_order.assert_not_called()


# ───────────────────────── 尾盘清退 ─────────────────────────


class TestMarketCloseOut:
    """14:55 尾盘清退。"""

    def test_close_out_cancels_all_active(self, frozen_clock):
        """14:55 后所有非终态订单撤单清退。"""
        order1 = _make_order(order_id="ord-1", status=OrderStatus.SUBMITTED)
        order2 = _make_order(
            order_id="ord-2",
            status=OrderStatus.PARTIAL,
            filled_quantity=Decimal("100"),
        )
        om = _make_mock_order_manager(open_orders=[order1, order2])
        close_now = lambda: datetime(2026, 8, 10, 14, 55, tzinfo=timezone.utc)
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=close_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order("ord-1", urgency=Urgency.HIGH)
        resolver.register_order("ord-2", urgency=Urgency.LOW)

        actions = resolver.scan_and_resolve()

        assert len(actions) == 2
        assert all(a.action_type is ResolveActionType.CLOSE_OUT for a in actions)
        assert all(a.success for a in actions)
        om.cancel_order.assert_any_call("ord-1")
        om.cancel_order.assert_any_call("ord-2")

    def test_close_out_cancel_fail_marks_unsuccessful(self, frozen_clock):
        """尾盘清退撤单失败 → success=False 但不报错。"""
        order = _make_order(status=OrderStatus.SUBMITTED)
        om = _make_mock_order_manager(open_orders=[order], cancel_returns=False)
        close_now = lambda: datetime(2026, 8, 10, 14, 56, tzinfo=timezone.utc)
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(),
            clock=frozen_clock,
            now_provider=close_now,
        )

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.CLOSE_OUT
        assert actions[0].success is False

    def test_close_out_overrides_make_or_take(self, frozen_clock):
        """14:55 优先于 Make-or-Take：即使超时也走清退。"""
        order = _make_order(status=OrderStatus.SUBMITTED)
        om = _make_mock_order_manager(open_orders=[order])
        close_now = lambda: datetime(2026, 8, 10, 14, 55, tzinfo=timezone.utc)
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=close_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        frozen_clock.set(60.0)  # 已超时

        actions = resolver.scan_and_resolve()

        # 走 CLOSE_OUT 而非 MAKE_OR_TAKE
        assert actions[0].action_type is ResolveActionType.CLOSE_OUT


# ───────────────────────── 幂等性 ─────────────────────────


class TestIdempotency:
    """终态订单跳过 + 未注册订单跳过。"""

    def test_terminal_status_not_in_open_orders(self, frozen_clock, trading_now):
        """终态订单不在 get_open_orders 返回中（OrderManager 保证），scan 不处理。"""
        # get_open_orders 本就只返回 PENDING/SUBMITTED/PARTIAL
        om = _make_mock_order_manager(open_orders=[])
        resolver = OpenOrderResolver(
            order_manager=om,
            clock=frozen_clock,
            now_provider=trading_now,
        )

        actions = resolver.scan_and_resolve()

        assert actions == []

    def test_unregistered_order_skipped(self, frozen_clock, trading_now):
        """未注册到续接跟踪的订单 → SKIP_NOT_REGISTERED。"""
        order = _make_order(status=OrderStatus.SUBMITTED)
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            clock=frozen_clock,
            now_provider=trading_now,
        )
        # 故意不调用 register_order

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.SKIP_NOT_REGISTERED
        assert actions[0].success is False
        om.cancel_order.assert_not_called()


# ───────────────────────── 异常鲁棒 ─────────────────────────


class TestExceptionRobustness:
    """单笔异常不阻断其他订单。"""

    def test_one_order_exception_doesnt_block_others(self, frozen_clock, trading_now):
        """第一笔订单处理抛异常，第二笔仍正常处理。"""
        order1 = _make_order(order_id="ord-1", status=OrderStatus.SUBMITTED)
        order2 = _make_order(order_id="ord-2", status=OrderStatus.SUBMITTED)
        om = _make_mock_order_manager(open_orders=[order1, order2])
        # 第一次 cancel 抛异常，第二次正常
        om.cancel_order.side_effect = [Exception("network error"), True]
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(make_or_take_timeout_seconds=30.0),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order("ord-1", urgency=Urgency.HIGH)
        resolver.register_order("ord-2", urgency=Urgency.HIGH)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()

        assert len(actions) == 2
        # 第一笔异常被捕获，转为 WAIT(success=False)
        assert actions[0].success is False
        # 第二笔仍被处理
        assert actions[1].action_type is ResolveActionType.MAKE_OR_TAKE


# ───────────────────────── 跟踪记录管理 ─────────────────────────


class TestTrackingLifecycle:
    """跟踪记录 register/unregister 生命周期。"""

    def test_unregister_prevents_tracking(self, frozen_clock, trading_now):
        """unregister 后订单变为 SKIP_NOT_REGISTERED。"""
        order = _make_order(status=OrderStatus.SUBMITTED)
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            clock=frozen_clock,
            now_provider=trading_now,
        )
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)
        resolver.unregister_order(order.order_id)

        actions = resolver.scan_and_resolve()

        assert actions[0].action_type is ResolveActionType.SKIP_NOT_REGISTERED

    def test_close_out_unregisters_order(self, frozen_clock):
        """CLOSE_OUT 成功后自动 unregister 跟踪记录。"""
        order = _make_order(status=OrderStatus.SUBMITTED)
        om = _make_mock_order_manager(open_orders=[order])
        close_now = lambda: datetime(2026, 8, 10, 14, 55, tzinfo=timezone.utc)
        resolver = OpenOrderResolver(
            order_manager=om,
            clock=frozen_clock,
            now_provider=close_now,
        )
        resolver.register_order(order.order_id, urgency=Urgency.HIGH)

        # CLOSE_OUT 优先级最高，成功后应自动 unregister 跟踪记录
        actions1 = resolver.scan_and_resolve()
        assert actions1[0].action_type is ResolveActionType.CLOSE_OUT
        assert actions1[0].success is True
        # 验证跟踪记录已被自动清理
        assert order.order_id not in resolver._tracking

    def test_ignore_partial_unregisters_order(self, frozen_clock, trading_now):
        """IGNORE_PARTIAL 成功后自动 unregister 跟踪记录。"""
        order = _make_order(
            quantity=Decimal("500"),
            filled_quantity=Decimal("450"),  # 剩余 50 < 100
            status=OrderStatus.PARTIAL,
        )
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(partial_ignore_threshold=100),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=Urgency.LOW)
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()
        assert actions[0].action_type is ResolveActionType.IGNORE_PARTIAL
        assert actions[0].success is True
        # 验证跟踪记录已被自动清理
        assert order.order_id not in resolver._tracking


# ───────────────────────── 配置 ─────────────────────────


class TestConfig:
    """配置默认值与自定义。"""

    def test_default_config(self):
        cfg = OpenOrderResolverConfig()
        assert cfg.make_or_take_timeout_seconds == 30.0
        assert cfg.partial_ignore_threshold == 100
        assert cfg.market_close_minutes == 895  # 14:55
        assert cfg.default_urgency == Urgency.LOW

    def test_custom_config(self):
        cfg = OpenOrderResolverConfig(
            make_or_take_timeout_seconds=10.0,
            partial_ignore_threshold=200,
            market_close_minutes=14 * 60 + 50,  # 14:50
            default_urgency=Urgency.HIGH,
        )
        assert cfg.make_or_take_timeout_seconds == 10.0
        assert cfg.partial_ignore_threshold == 200
        assert cfg.market_close_minutes == 890
        assert cfg.default_urgency == Urgency.HIGH

    def test_default_urgency_used_when_none(self, frozen_clock, trading_now):
        """register_order 传 None → 使用 config.default_urgency。"""
        order = _make_order(status=OrderStatus.PARTIAL, filled_quantity=Decimal("100"))
        om = _make_mock_order_manager(open_orders=[order])
        resolver = OpenOrderResolver(
            order_manager=om,
            config=OpenOrderResolverConfig(default_urgency=Urgency.HIGH),
            opponent_price_provider=lambda s, sd: Decimal("10.10"),
            clock=frozen_clock,
            now_provider=trading_now,
        )
        frozen_clock.set(0.0)
        resolver.register_order(order.order_id, urgency=None)  # 用默认 HIGH
        frozen_clock.set(60.0)

        actions = resolver.scan_and_resolve()
        # HIGH + PARTIAL ≥ 100 → MAKE_OR_TAKE
        assert actions[0].action_type is ResolveActionType.MAKE_OR_TAKE
