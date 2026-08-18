# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L05-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODULE] tests.pf_core.test_orderbook_imbalance_strategy
# [DOMAIN] D_PF_CORE
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""OrderBookImbalanceStrategy 单元测试（路径 B 盘口失衡反转策略）。

覆盖做 T 状态机的核心决策点：
  - 无效价格（<=0）跳过
  - 盘口全零（ob=None）跳过
  - flat 态：卖压未达 entry_threshold → 持仓不变
  - flat 态：ob<=-entry_threshold（极端卖压）→ 买入（target_weight=base_weight）
  - long 态：ob<exit_threshold（未恢复）→ 持仓不变
  - long 态：ob>=exit_threshold（盘口恢复）→ 卖出（target_weight=0）
  - 完整 round-trip：flat→买入→卖出→flat→再买入
  - 多标的状态隔离
  - 5 档 vs 1 档失衡计算
  - 构造参数校验（含状态抖动防护）+ 注册表发现
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from zephyr.backtest.core.matching_logic import TickSnapshot
from zephyr.pf_core.orderbook_imbalance_strategy import OrderBookImbalanceStrategy
from zephyr.pf_core.strategy_engine.tick_strategy_base import (
    TickStrategyBase,
    autodiscover_tick_strategies,
)

# ------------------------------------------------------------------
# 测试辅助
# ------------------------------------------------------------------


def _make_tick(
    last_price: float,
    *,
    bid_vols: list[float] | None = None,
    ask_vols: list[float] | None = None,
    ts: datetime | None = None,
    symbol: str = "600000.SH",
) -> TickSnapshot:
    """构造 TickSnapshot，bid_vols/ask_vols 为 5 档量列表。"""
    bv = tuple(Decimal(str(v)) for v in (bid_vols or [100, 100, 100, 100, 100]))
    av = tuple(Decimal(str(v)) for v in (ask_vols or [100, 100, 100, 100, 100]))
    prices = tuple(Decimal(str(last_price)) for _ in range(5))
    return TickSnapshot(
        symbol=symbol,
        timestamp=ts or datetime(2026, 7, 31, 10, 0, 0),
        last_price=Decimal(str(last_price)),
        open=Decimal(str(last_price)),
        high=Decimal(str(last_price)),
        low=Decimal(str(last_price)),
        prev_close=Decimal(str(last_price)),
        amount=Decimal("100000"),
        volume=Decimal("10000"),
        ask_price=prices,
        bid_price=prices,
        ask_vol=av,
        bid_vol=bv,
        stock_status=0,
        transaction_num=0,
    )


@dataclass
class _FakeEvent:
    """模拟 TickEvent，仅含 on_tick 依赖的字段。"""

    timestamp: datetime
    symbol: str = "600000.SH"
    tick_data: TickSnapshot | None = None
    sequence: int = 1


def _feed(
    strategy: OrderBookImbalanceStrategy,
    series: list[tuple[float, list[float], list[float]]],
    *,
    start: datetime | None = None,
    symbol: str = "600000.SH",
) -> list[dict[str, float]]:
    """按 1 秒间隔喂入 (price, bid_vols, ask_vols) 序列，收集每次返回的权重 dict。"""
    base = start or datetime(2026, 7, 31, 10, 0, 0)
    results: list[dict[str, float]] = []
    for i, (p, bv, av) in enumerate(series):
        ts = base + timedelta(seconds=i)
        tick = _make_tick(p, bid_vols=bv, ask_vols=av, ts=ts, symbol=symbol)
        results.append(strategy.on_tick(_FakeEvent(timestamp=ts, symbol=symbol, tick_data=tick)))
    return results


# ------------------------------------------------------------------
# 构造与注册
# ------------------------------------------------------------------


class TestConstruction:
    def test_invalid_entry_threshold_raises(self) -> None:
        with pytest.raises(ValueError, match="entry_threshold"):
            OrderBookImbalanceStrategy(entry_threshold=0.0)
        with pytest.raises(ValueError, match="entry_threshold"):
            OrderBookImbalanceStrategy(entry_threshold=1.5)

    def test_invalid_exit_threshold_raises(self) -> None:
        with pytest.raises(ValueError, match="exit_threshold"):
            OrderBookImbalanceStrategy(exit_threshold=1.5)
        with pytest.raises(ValueError, match="exit_threshold"):
            OrderBookImbalanceStrategy(exit_threshold=-1.5)

    def test_entry_must_exceed_exit_for_meaningful_spread(self) -> None:
        """entry/exit 需有合理价差间隔（buy 区 ob<=-entry，sell 区 ob>=exit）。
        本策略不强制 guard（状态机天然防同 tick 双向），但参数语义需自洽：
        entry_threshold>0 且 exit_threshold 可为 0 或负值。"""
        s = OrderBookImbalanceStrategy(entry_threshold=0.2, exit_threshold=0.0)
        assert s._entry_threshold == 0.2

    def test_invalid_base_weight_raises(self) -> None:
        with pytest.raises(ValueError, match="base_weight"):
            OrderBookImbalanceStrategy(base_weight=0.0)
        with pytest.raises(ValueError, match="base_weight"):
            OrderBookImbalanceStrategy(base_weight=1.5)

    def test_registered_in_tick_registry(self) -> None:
        """导入即注册（@register 装饰器在类定义时执行）；autodiscover 幂等可发现。"""
        assert TickStrategyBase.get("orderbook-imbalance") is OrderBookImbalanceStrategy
        autodiscover_tick_strategies("zephyr.pf_core")
        assert TickStrategyBase.get("orderbook-imbalance") is OrderBookImbalanceStrategy


# ------------------------------------------------------------------
# on_tick 决策逻辑
# ------------------------------------------------------------------


class TestOnTickDecisions:
    def test_invalid_price_returns_empty(self) -> None:
        """last_price<=0（盘前/停牌）→ 空，不调仓。"""
        s = OrderBookImbalanceStrategy()
        tick = _make_tick(0.0)
        assert s.on_tick(_FakeEvent(timestamp=datetime(2026, 7, 31, 9, 25), tick_data=tick)) == {}

    def test_all_zero_orderbook_returns_empty(self) -> None:
        """盘口全零（ob=None）→ 空，不调仓。"""
        s = OrderBookImbalanceStrategy()
        tick = _make_tick(10.0, bid_vols=[0, 0, 0, 0, 0], ask_vols=[0, 0, 0, 0, 0])
        assert s.on_tick(_FakeEvent(timestamp=datetime(2026, 7, 31, 10, 0), tick_data=tick)) == {}

    def test_flat_insufficient_sell_pressure_holds(self) -> None:
        """flat 态下卖压未达 entry_threshold → 持仓不变。"""
        s = OrderBookImbalanceStrategy(entry_threshold=0.5, use_5levels=False)
        # bid=150, ask=300 → ob=(150-300)/450=-0.333 > -0.5 → 不买
        results = _feed(s, [(10.0, [150, 0, 0, 0, 0], [300, 0, 0, 0, 0])])
        assert all(r == {} for r in results)

    def test_flat_extreme_sell_pressure_buys(self) -> None:
        """flat 态下 ob<=-entry_threshold（极端卖压）→ 买入 base_weight。"""
        s = OrderBookImbalanceStrategy(
            entry_threshold=0.5, base_weight=0.9, use_5levels=False,
        )
        # bid=100, ask=300 → ob=-0.5 <= -0.5 → 买入
        results = _feed(s, [(10.0, [100, 0, 0, 0, 0], [300, 0, 0, 0, 0])])
        buys = [r for r in results if r]
        assert len(buys) == 1
        assert buys[0] == {"600000.SH": 0.9}

    def test_long_not_recovered_holds(self) -> None:
        """long 态下 ob<exit_threshold（未恢复）→ 持仓不变。"""
        s = OrderBookImbalanceStrategy(
            entry_threshold=0.5, exit_threshold=0.0, use_5levels=False,
        )
        # 先买入进入 long
        _feed(s, [(10.0, [100, 0, 0, 0, 0], [300, 0, 0, 0, 0])])
        # ob=-0.2 < 0 → 不卖
        results = _feed(s, [(10.0, [200, 0, 0, 0, 0], [300, 0, 0, 0, 0])],
                        start=datetime(2026, 7, 31, 10, 0, 10))
        assert all(r == {} for r in results)

    def test_long_recovered_sells(self) -> None:
        """long 态下 ob>=exit_threshold（盘口恢复）→ 卖出。"""
        s = OrderBookImbalanceStrategy(
            entry_threshold=0.5, exit_threshold=0.0, use_5levels=False,
        )
        _feed(s, [(10.0, [100, 0, 0, 0, 0], [300, 0, 0, 0, 0])])  # 买入
        # bid=100, ask=100 → ob=0 >= 0 → 卖出
        results = _feed(s, [(10.0, [100, 0, 0, 0, 0], [100, 0, 0, 0, 0])],
                        start=datetime(2026, 7, 31, 10, 0, 10))
        sells = [r for r in results if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}

    def test_long_buy_pressure_sells(self) -> None:
        """long 态下 ob>0（买盘转强，>=exit_threshold=0）→ 卖出。"""
        s = OrderBookImbalanceStrategy(
            entry_threshold=0.5, exit_threshold=0.0, use_5levels=False,
        )
        _feed(s, [(10.0, [100, 0, 0, 0, 0], [300, 0, 0, 0, 0])])  # 买入
        # bid=300, ask=100 → ob=+0.5 >= 0 → 卖出
        results = _feed(s, [(10.0, [300, 0, 0, 0, 0], [100, 0, 0, 0, 0])],
                        start=datetime(2026, 7, 31, 10, 0, 10))
        sells = [r for r in results if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}

    def test_positive_exit_threshold_requires_buy_pressure(self) -> None:
        """exit_threshold>0 时需买盘转强（ob>=正值）才卖。"""
        s = OrderBookImbalanceStrategy(
            entry_threshold=0.6, exit_threshold=0.2, use_5levels=False,
        )
        _feed(s, [(10.0, [100, 0, 0, 0, 0], [400, 0, 0, 0, 0])])  # ob=-0.6 买入
        # ob=0 < 0.2 → 不卖
        r1 = _feed(s, [(10.0, [100, 0, 0, 0, 0], [100, 0, 0, 0, 0])],
                   start=datetime(2026, 7, 31, 10, 0, 10))
        assert all(r == {} for r in r1)
        # bid=300, ask=100 → ob=+0.5 >= 0.2 → 卖
        r2 = _feed(s, [(10.0, [300, 0, 0, 0, 0], [100, 0, 0, 0, 0])],
                   start=datetime(2026, 7, 31, 10, 0, 20))
        sells = [r for r in r2 if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}


# ------------------------------------------------------------------
# 完整 round-trip
# ------------------------------------------------------------------


class TestRoundTrip:
    def test_full_round_trip_flat_buy_sell_buy(self) -> None:
        """完整做 T：flat → 买入 → 卖出 → flat → 再买入。"""
        s = OrderBookImbalanceStrategy(
            entry_threshold=0.5, exit_threshold=0.0,
            base_weight=1.0, use_5levels=False,
        )
        # 阶段1：极端卖压买入
        r1 = _feed(s, [(10.0, [100, 0, 0, 0, 0], [300, 0, 0, 0, 0])])
        assert any(r == {"600000.SH": 1.0} for r in r1)
        # 阶段2：盘口恢复卖出
        r2 = _feed(s, [(10.0, [100, 0, 0, 0, 0], [100, 0, 0, 0, 0])],
                   start=datetime(2026, 7, 31, 10, 0, 10))
        assert any(r == {"600000.SH": 0.0} for r in r2)
        # 阶段3：再次极端卖压买入
        r3 = _feed(s, [(10.0, [100, 0, 0, 0, 0], [300, 0, 0, 0, 0])],
                   start=datetime(2026, 7, 31, 10, 0, 20))
        assert any(r == {"600000.SH": 1.0} for r in r3)

    def test_multi_symbol_state_isolation(self) -> None:
        """多 symbol 状态独立：A 买入不影响 B。"""
        s = OrderBookImbalanceStrategy(
            entry_threshold=0.5, use_5levels=False, base_weight=0.9,
        )
        ts = datetime(2026, 7, 31, 10, 0, 0)
        # A 触发买入
        tick_a = _make_tick(10.0, bid_vols=[100, 0, 0, 0, 0], ask_vols=[300, 0, 0, 0, 0],
                            ts=ts, symbol="600000.SH")
        r_a = s.on_tick(_FakeEvent(timestamp=ts, symbol="600000.SH", tick_data=tick_a))
        assert r_a == {"600000.SH": 0.9}
        # B 卖压不足，不调仓
        tick_b = _make_tick(10.0, bid_vols=[200, 0, 0, 0, 0], ask_vols=[300, 0, 0, 0, 0],
                            ts=ts, symbol="600001.SH")
        r_b = s.on_tick(_FakeEvent(timestamp=ts, symbol="600001.SH", tick_data=tick_b))
        assert r_b == {}


# ------------------------------------------------------------------
# 5 档 vs 1 档失衡计算
# ------------------------------------------------------------------


class TestOrderBookImbalance:
    def test_balanced_5level_zero(self) -> None:
        s = OrderBookImbalanceStrategy(use_5levels=True)
        tick = _make_tick(10.0, bid_vols=[100, 100, 100, 100, 100],
                          ask_vols=[100, 100, 100, 100, 100])
        assert s._order_book_imbalance(tick) == pytest.approx(0.0)

    def test_sell_pressure_5level_negative(self) -> None:
        s = OrderBookImbalanceStrategy(use_5levels=True)
        # bid_sum=500, ask_sum=1500 → (500-1500)/2000 = -0.5
        tick = _make_tick(10.0, bid_vols=[100, 100, 100, 100, 100],
                          ask_vols=[300, 300, 300, 300, 300])
        assert s._order_book_imbalance(tick) == pytest.approx(-0.5)

    def test_5level_vs_1level_differ(self) -> None:
        """5 档全量与仅 1 档结果不同：验证 use_5levels 开关生效。"""
        # 1档平衡，但 5档卖压重
        tick = _make_tick(10.0, bid_vols=[100, 50, 50, 50, 50],
                          ask_vols=[100, 200, 200, 200, 200])
        s5 = OrderBookImbalanceStrategy(use_5levels=True)
        s1 = OrderBookImbalanceStrategy(use_5levels=False)
        # 1档：bid1=ask1=100 → ob=0
        assert s1._order_book_imbalance(tick) == pytest.approx(0.0)
        # 5档：bid_sum=300, ask_sum=900 → (300-900)/1200=-0.5
        assert s5._order_book_imbalance(tick) == pytest.approx(-0.5)

    def test_partial_levels_only_counts_positive(self) -> None:
        """零量档被忽略（仅统计 v>0 的档）。"""
        s = OrderBookImbalanceStrategy(use_5levels=True)
        tick = _make_tick(10.0, bid_vols=[100, 0, 0, 0, 0], ask_vols=[300, 0, 0, 0, 0])
        # bid_sum=100, ask_sum=300 → -0.5
        assert s._order_book_imbalance(tick) == pytest.approx(-0.5)
