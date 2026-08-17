# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""fill_id 持久化去重 + rebuild_from_broker 测试（Qwen P0-2 / 裁定书 §六 ②③④）。

红队实证（验收②）：
1. 同一 fill_id 重放不重复记账（FillHandler / PositionTracker，含重启存活）；
2. Saga 补偿 rollback-{fill_id} 确定性 ID 配去重集真幂等（重试不双倍回滚）；
3. rebuild_from_broker 以券商为准覆盖式重建 + today_fills 登记去重。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from zephyr.ex_core.fill_handler import FillHandler
from zephyr.ex_core.position_tracker import PositionTracker
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.state_store import AppendOnlyDedupSet

# ── 工厂 ──


def _make_fill(
    fill_id: str = "fill-001",
    symbol: str = "600000.SH",
    qty: Decimal = Decimal("100"),
    price: Decimal = Decimal("10.00"),
    commission: Decimal = Decimal("3.00"),
    order_id: str = "ord-001",
) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=price,
        fill_timestamp=datetime.now(UTC),
        filled_quantity=qty,
        idempotency_key=f"idem-{fill_id}",
        order_id=order_id,
        strategy_id="test",
        symbol=symbol,
        commission=commission,
    )


def _make_order(order_id: str = "ord-001", quantity: Decimal = Decimal("100")) -> Order:
    now = datetime.now(UTC)
    return Order(
        order_id=order_id,
        symbol="600000.SH",
        strategy_id="test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=quantity,
        limit_price=Decimal("10.00"),
        status=OrderStatus.SUBMITTED,
        created_at=now,
        updated_at=now,
        idempotency_key=f"idem-{order_id}",
    )


# ── 红队 1：同一 fill_id 重放不重复记账 ──


class TestFillHandlerPersistentDedup:
    def test_replay_same_process_not_double_counted(self, tmp_path):
        handler = FillHandler(dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"))
        order = _make_order()
        fill = _make_fill(qty=Decimal("30"))

        s1 = handler.process_fill(fill, order)
        assert s1.filled_quantity == Decimal("30")
        s2 = handler.process_fill(fill, order)
        assert s2.filled_quantity == Decimal("30")
        assert order.filled_quantity == Decimal("30")

    def test_replay_after_restart_not_double_counted(self, tmp_path):
        """重启存活：新 handler 实例加载同一去重集，重放仍被拦截。"""
        dedup_path = tmp_path / "fills.txt"
        handler1 = FillHandler(dedup_store=AppendOnlyDedupSet(dedup_path))
        order = _make_order()
        fill = _make_fill(qty=Decimal("30"))
        handler1.process_fill(fill, order)

        # 模拟重启：新 handler + 从券商/订单账恢复的 order（已含 30 股成交）
        recovered_order = _make_order()
        recovered_order.filled_quantity = Decimal("30")
        recovered_order.avg_fill_price = Decimal("10.00")
        handler2 = FillHandler(dedup_store=AppendOnlyDedupSet(dedup_path))
        summary = handler2.process_fill(fill, recovered_order)

        assert recovered_order.filled_quantity == Decimal("30")  # 未重复累积
        assert summary.filled_quantity == Decimal("30")

    def test_memory_mode_unchanged(self):
        handler = FillHandler()
        order = _make_order()
        fill = _make_fill(qty=Decimal("30"))
        handler.process_fill(fill, order)
        handler.process_fill(fill, order)
        assert order.filled_quantity == Decimal("30")


class TestPositionTrackerPersistentDedup:
    def test_replay_same_fill_not_double_applied(self, tmp_path):
        tracker = PositionTracker(dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"))
        fill = _make_fill()

        tracker.apply_fill(fill, OrderSide.BUY)
        tracker.apply_fill(fill, OrderSide.BUY)  # 重放

        assert tracker.holdings["600000.SH"] == Decimal("100")
        assert tracker.cash == Decimal("998997")

    def test_replay_after_restart_not_double_applied(self, tmp_path):
        dedup_path = tmp_path / "fills.txt"
        t1 = PositionTracker(dedup_store=AppendOnlyDedupSet(dedup_path))
        fill = _make_fill()
        t1.apply_fill(fill, OrderSide.BUY)

        # 模拟重启：新 tracker（持仓已由 rebuild_from_broker 恢复），重放同一 fill
        t2 = PositionTracker(dedup_store=AppendOnlyDedupSet(dedup_path))
        t2.rebuild_from_broker({"600000.SH": {"qty": "100", "avg_cost": "10.00"}})
        t2.apply_fill(fill, OrderSide.BUY)  # 重放 → 拦截

        assert t2.holdings["600000.SH"] == Decimal("100")

    def test_memory_mode_unchanged(self):
        """无 dedup_store（既有行为）：不去重，重复调用重复入账。"""
        tracker = PositionTracker()
        fill = _make_fill()
        tracker.apply_fill(fill, OrderSide.BUY)
        tracker.apply_fill(fill, OrderSide.BUY)
        assert tracker.holdings["600000.SH"] == Decimal("200")


# ── 红队 2：rollback 补偿重试不双倍回滚 ──


class TestSagaRollbackIdempotency:
    def test_rollback_retry_not_double_rolled_back(self, tmp_path):
        """rollback-{fill_id} 确定性 ID：补偿重试第二次被去重集拦截。"""
        tracker = PositionTracker(
            initial_cash=Decimal("1000000"),
            dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"),
        )
        original = _make_fill(fill_id="fill-A", qty=Decimal("100"))
        tracker.apply_fill(original, OrderSide.BUY)
        assert tracker.holdings["600000.SH"] == Decimal("100")

        # Saga _compensate_position 同款构造：确定性 rollback ID + 反方向
        rollback = _make_fill(fill_id=f"rollback-{original.fill_id}", qty=Decimal("100"))
        tracker.apply_fill(rollback, OrderSide.SELL)
        assert tracker.holdings["600000.SH"] == Decimal("0")

        # 补偿异常重试：同一 rollback fill 再执行 → 去重拦截，不双倍回滚（不变 -100）
        tracker.apply_fill(rollback, OrderSide.SELL)
        assert tracker.holdings["600000.SH"] == Decimal("0")

    def test_original_fill_replay_after_rollback_still_blocked(self, tmp_path):
        """原始 fill 重放同样被拦截（重启后重放路径）。"""
        tracker = PositionTracker(dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"))
        original = _make_fill(fill_id="fill-B", qty=Decimal("100"))
        tracker.apply_fill(original, OrderSide.BUY)
        rollback = _make_fill(fill_id=f"rollback-{original.fill_id}", qty=Decimal("100"))
        tracker.apply_fill(rollback, OrderSide.SELL)

        tracker.apply_fill(original, OrderSide.BUY)  # 重放原始 fill → 拦截
        assert tracker.holdings["600000.SH"] == Decimal("0")


# ── rebuild_from_broker（AI-RWIRE-001 启动流程消费接口）──


class TestRebuildFromBroker:
    def test_rebuild_overwrites_positions(self, tmp_path):
        tracker = PositionTracker(dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"))
        tracker.apply_fill(_make_fill(fill_id="old-1", qty=Decimal("50")), OrderSide.BUY)

        tracker.rebuild_from_broker(
            {
                "600000.SH": {"qty": "300", "avg_cost": "12.50"},
                "000001.SZ": {"qty": 200, "avg_cost": 8.0},
            }
        )
        assert tracker.holdings == {"600000.SH": Decimal("300"), "000001.SZ": Decimal("200")}
        assert tracker.avg_costs["600000.SH"] == Decimal("12.50")

    def test_rebuild_skips_zero_qty(self, tmp_path):
        tracker = PositionTracker(dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"))
        tracker.rebuild_from_broker({"600000.SH": {"qty": 0, "avg_cost": 0}})
        assert tracker.holdings == {}

    def test_rebuild_cash_override_and_default(self, tmp_path):
        tracker = PositionTracker(
            initial_cash=Decimal("1000000"),
            dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"),
        )
        tracker.rebuild_from_broker({}, cash=Decimal("888888"))
        assert tracker.cash == Decimal("888888")
        tracker.rebuild_from_broker({})
        assert tracker.cash == Decimal("888888")  # None=保留当前现金账

    def test_rebuild_registers_today_fills_into_dedup(self, tmp_path):
        """today_fills 只登记去重（防重放），不改持仓（持仓以券商为准）。"""
        dedup_path = tmp_path / "fills.txt"
        tracker = PositionTracker(dedup_store=AppendOnlyDedupSet(dedup_path))
        today_fill = _make_fill(fill_id="today-1", qty=Decimal("100"))

        tracker.rebuild_from_broker(
            {"600000.SH": {"qty": "100", "avg_cost": "10.00"}},
            today_fills=[today_fill],
        )
        assert tracker.holdings["600000.SH"] == Decimal("100")

        # 重启后券商重放当日成交 → 去重拦截，不重复记账
        tracker.apply_fill(today_fill, OrderSide.BUY)
        assert tracker.holdings["600000.SH"] == Decimal("100")

    def test_rebuild_today_fills_generator_accepted(self, tmp_path):
        tracker = PositionTracker(dedup_store=AppendOnlyDedupSet(tmp_path / "fills.txt"))
        fills = (_make_fill(fill_id=f"g-{i}") for i in range(3))
        tracker.rebuild_from_broker({}, today_fills=fills)
        snapshot = tracker.get_positions()
        assert snapshot.holdings == {}
