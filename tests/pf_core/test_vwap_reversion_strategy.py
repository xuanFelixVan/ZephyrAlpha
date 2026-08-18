# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L05-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODULE] tests.pf_core.test_vwap_reversion_strategy
# [DOMAIN] D_PF_CORE
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""VWAPReversionStrategy 单元测试（路径 B 均值回归策略）。

覆盖做 T 状态机的核心决策点：
  - 无效价格（<=0）跳过
  - volume/amount<=0（VWAP 未定义）跳过
  - flat 态：价格未低于 VWAP 足够幅度 → 持仓不变
  - flat 态：价格低于 VWAP >= entry_threshold → 买入（target_weight=base_weight）
  - flat 态：价格低于 VWAP 但卖盘压力大（ob<block_threshold）→ 滤子拦截不买
  - flat 态：关闭盘口滤子 → 仅凭偏离买入
  - long 态：价格未回归 VWAP → 持仓不变
  - long 态：价格回归到 VWAP（deviation>=exit_threshold）→ 卖出（target_weight=0）
  - 完整 round-trip：flat→买入→卖出→flat→再买入
  - 盘口失衡计算 + 构造参数校验
  - 注册表发现（strategy_id="vwap-reversion"）
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from zephyr.backtest.core.matching_logic import TickSnapshot
from zephyr.pf_core.strategy_engine.tick_strategy_base import (
    TickStrategyBase,
    autodiscover_tick_strategies,
)
from zephyr.pf_core.vwap_reversion_strategy import VWAPReversionStrategy

# ------------------------------------------------------------------
# 测试辅助
# ------------------------------------------------------------------


def _make_tick(
    last_price: float,
    *,
    vwap: float = 10.0,
    volume: float = 10000.0,
    bid_vol_1: float = 100.0,
    ask_vol_1: float = 100.0,
    ts: datetime | None = None,
    symbol: str = "600000.SH",
) -> TickSnapshot:
    """构造 TickSnapshot。

    通过 vwap*volume 反推 amount，使 VWAP=amount/volume 恰为指定 vwap，
    便于独立控制每个 tick 的 VWAP 基准（单 tick 决策测试无需模拟累计）。
    """
    amount = float(vwap) * float(volume)
    bid_vols = tuple(Decimal(str(v)) for v in [bid_vol_1, 0, 0, 0, 0])
    ask_vols = tuple(Decimal(str(v)) for v in [ask_vol_1, 0, 0, 0, 0])
    prices = tuple(Decimal(str(last_price)) for _ in range(5))
    return TickSnapshot(
        symbol=symbol,
        timestamp=ts or datetime(2026, 7, 31, 10, 0, 0),
        last_price=Decimal(str(last_price)),
        open=Decimal(str(last_price)),
        high=Decimal(str(last_price)),
        low=Decimal(str(last_price)),
        prev_close=Decimal(str(last_price)),
        amount=Decimal(str(amount)),
        volume=Decimal(str(volume)),
        ask_price=prices,
        bid_price=prices,
        ask_vol=ask_vols,
        bid_vol=bid_vols,
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
    strategy: VWAPReversionStrategy,
    series: list[tuple[float, float]],
    *,
    start: datetime | None = None,
    bid_vol_1: float = 100.0,
    ask_vol_1: float = 100.0,
    volume: float = 10000.0,
    symbol: str = "600000.SH",
) -> list[dict[str, float]]:
    """按 1 秒间隔喂入 (price, vwap) 序列，收集每次返回的权重 dict。"""
    base = start or datetime(2026, 7, 31, 10, 0, 0)
    results: list[dict[str, float]] = []
    for i, (p, vwap) in enumerate(series):
        ts = base + timedelta(seconds=i)
        tick = _make_tick(
            p, vwap=vwap, volume=volume,
            bid_vol_1=bid_vol_1, ask_vol_1=ask_vol_1, ts=ts, symbol=symbol,
        )
        results.append(strategy.on_tick(_FakeEvent(timestamp=ts, symbol=symbol, tick_data=tick)))
    return results


# ------------------------------------------------------------------
# 构造与注册
# ------------------------------------------------------------------


class TestConstruction:
    def test_invalid_entry_threshold_raises(self) -> None:
        with pytest.raises(ValueError, match="entry_threshold"):
            VWAPReversionStrategy(entry_threshold=0.0)
        with pytest.raises(ValueError, match="entry_threshold"):
            VWAPReversionStrategy(entry_threshold=-0.001)

    def test_invalid_base_weight_raises(self) -> None:
        with pytest.raises(ValueError, match="base_weight"):
            VWAPReversionStrategy(base_weight=0.0)
        with pytest.raises(ValueError, match="base_weight"):
            VWAPReversionStrategy(base_weight=1.5)

    def test_registered_in_tick_registry(self) -> None:
        """导入即注册（@register 装饰器在类定义时执行）；autodiscover 幂等可发现。"""
        assert TickStrategyBase.get("vwap-reversion") is VWAPReversionStrategy
        autodiscover_tick_strategies("zephyr.pf_core")
        assert TickStrategyBase.get("vwap-reversion") is VWAPReversionStrategy


# ------------------------------------------------------------------
# on_tick 决策逻辑
# ------------------------------------------------------------------


class TestOnTickDecisions:
    def test_invalid_price_returns_empty(self) -> None:
        """last_price<=0（盘前/停牌）→ 空，不调仓。"""
        s = VWAPReversionStrategy()
        tick = _make_tick(0.0, vwap=10.0)
        assert s.on_tick(_FakeEvent(timestamp=datetime(2026, 7, 31, 9, 25), tick_data=tick)) == {}

    def test_zero_volume_returns_empty(self) -> None:
        """volume=0（VWAP 未定义）→ 空，不调仓。"""
        s = VWAPReversionStrategy()
        tick = _make_tick(9.96, vwap=10.0, volume=0.0)
        assert s.on_tick(_FakeEvent(timestamp=datetime(2026, 7, 31, 10, 0), tick_data=tick)) == {}

    def test_zero_amount_returns_empty(self) -> None:
        """amount=0（VWAP<=0）→ 空，不调仓。"""
        s = VWAPReversionStrategy()
        tick = _make_tick(9.96, vwap=0.0, volume=10000.0)
        assert s.on_tick(_FakeEvent(timestamp=datetime(2026, 7, 31, 10, 0), tick_data=tick)) == {}

    def test_flat_insufficient_deviation_holds(self) -> None:
        """flat 态下价格低于 VWAP 但未达 entry_threshold → 持仓不变。"""
        s = VWAPReversionStrategy(entry_threshold=0.003, use_order_book=False)
        # VWAP=10.00, price=9.98 → deviation=-0.002 > -0.003 → 不买
        results = _feed(s, [(9.98, 10.00)])
        assert all(r == {} for r in results)

    def test_flat_sufficient_deviation_buys(self) -> None:
        """flat 态下价格低于 VWAP >= entry_threshold → 买入 base_weight。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, base_weight=0.9, use_order_book=False,
        )
        # VWAP=10.00, price=9.96 → deviation=-0.004 <= -0.003 → 买入
        results = _feed(s, [(9.96, 10.00)])
        buys = [r for r in results if r]
        assert len(buys) == 1
        assert buys[0] == {"600000.SH": 0.9}

    def test_flat_deviation_but_sell_pressure_blocks_buy(self) -> None:
        """价格低于 VWAP 够多，但卖盘压力 ob<block_threshold → 滤子拦截不买。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, use_order_book=True, ob_block_threshold=-0.3,
        )
        # bid1=100, ask1=300 → ob=(100-300)/400=-0.5 < -0.3 → 阻断
        results = _feed(
            s, [(9.96, 10.00)],
            bid_vol_1=100.0, ask_vol_1=300.0,
        )
        assert all(r == {} for r in results)

    def test_flat_deviation_with_neutral_order_book_buys(self) -> None:
        """价格低于 VWAP 够多，盘口中性（ob=0 >= block_threshold）→ 买入。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, use_order_book=True, ob_block_threshold=-0.3,
        )
        # bid1=100, ask1=100 → ob=0 >= -0.3 → 放行
        results = _feed(
            s, [(9.96, 10.00)],
            bid_vol_1=100.0, ask_vol_1=100.0,
        )
        buys = [r for r in results if r]
        assert len(buys) == 1
        assert buys[0] == {"600000.SH": 0.95}

    def test_order_book_disabled_buys_on_pure_deviation(self) -> None:
        """关闭盘口滤子后，即使卖盘压力极大也凭偏离买入。"""
        s = VWAPReversionStrategy(entry_threshold=0.003, use_order_book=False)
        results = _feed(
            s, [(9.96, 10.00)],
            bid_vol_1=0.0, ask_vol_1=1000.0,  # 极端卖压
        )
        buys = [r for r in results if r]
        assert len(buys) == 1
        assert buys[0] == {"600000.SH": 0.95}

    def test_long_below_vwap_holds(self) -> None:
        """long 态下价格仍低于 VWAP（deviation<exit_threshold）→ 持仓不变。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, exit_threshold=0.0, use_order_book=False,
        )
        # 先买入进入 long 态（卖出价无关，本策略不记卖出价）
        _feed(s, [(9.96, 10.00)])
        # long 态：price=9.98, VWAP=10.00 → deviation=-0.002 < 0 → 不卖
        results = _feed(s, [(9.98, 10.00)], start=datetime(2026, 7, 31, 10, 0, 10))
        assert all(r == {} for r in results)

    def test_long_reverts_to_vwap_sells(self) -> None:
        """long 态下价格回归到 VWAP（deviation>=exit_threshold）→ 卖出。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, exit_threshold=0.0, use_order_book=False,
        )
        _feed(s, [(9.96, 10.00)])  # 买入进入 long
        # price=10.00, VWAP=10.00 → deviation=0.0 >= 0 → 卖出
        results = _feed(s, [(10.00, 10.00)], start=datetime(2026, 7, 31, 10, 0, 10))
        sells = [r for r in results if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}

    def test_long_above_vwap_sells(self) -> None:
        """long 态下价格升破 VWAP（deviation>0 >= exit_threshold=0）→ 卖出。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, exit_threshold=0.0, use_order_book=False,
        )
        _feed(s, [(9.96, 10.00)])  # 买入
        # price=10.02, VWAP=10.00 → deviation=+0.002 >= 0 → 卖出
        results = _feed(s, [(10.02, 10.00)], start=datetime(2026, 7, 31, 10, 0, 10))
        sells = [r for r in results if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}

    def test_positive_exit_threshold_requires_above_vwap(self) -> None:
        """exit_threshold>0 时需价格升破 VWAP 足够幅度才卖。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, exit_threshold=0.002, use_order_book=False,
        )
        _feed(s, [(9.96, 10.00)])  # 买入
        # price=10.01 → deviation=+0.001 < 0.002 → 不卖
        r1 = _feed(s, [(10.01, 10.00)], start=datetime(2026, 7, 31, 10, 0, 10))
        assert all(r == {} for r in r1)
        # price=10.03 → deviation=+0.003 >= 0.002 → 卖
        r2 = _feed(s, [(10.03, 10.00)], start=datetime(2026, 7, 31, 10, 0, 20))
        sells = [r for r in r2 if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}


# ------------------------------------------------------------------
# 完整 round-trip
# ------------------------------------------------------------------


class TestRoundTrip:
    def test_full_round_trip_flat_buy_sell_buy(self) -> None:
        """完整做 T：flat → 买入 → 卖出 → flat → 再买入。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, exit_threshold=0.0,
            base_weight=1.0, use_order_book=False,
        )
        # 阶段1：flat→买入（price 9.96 < VWAP 10.00，dev=-0.4%）
        r1 = _feed(s, [(9.96, 10.00)])
        assert any(r == {"600000.SH": 1.0} for r in r1)
        # 阶段2：long→卖出（price 回归 VWAP 10.00）
        r2 = _feed(s, [(10.00, 10.00)], start=datetime(2026, 7, 31, 10, 0, 10))
        assert any(r == {"600000.SH": 0.0} for r in r2)
        # 阶段3：flat→再买入（price 再次低于 VWAP）
        r3 = _feed(s, [(9.95, 10.00)], start=datetime(2026, 7, 31, 10, 0, 20))
        assert any(r == {"600000.SH": 1.0} for r in r3)

    def test_multi_symbol_state_isolation(self) -> None:
        """多 symbol 状态独立：A 买入不影响 B。"""
        s = VWAPReversionStrategy(
            entry_threshold=0.003, use_order_book=False, base_weight=0.9,
        )
        ts = datetime(2026, 7, 31, 10, 0, 0)
        # A 触发买入
        tick_a = _make_tick(9.96, vwap=10.0, ts=ts, symbol="600000.SH")
        r_a = s.on_tick(_FakeEvent(timestamp=ts, symbol="600000.SH", tick_data=tick_a))
        assert r_a == {"600000.SH": 0.9}
        # B 价格未达阈值，不调仓
        tick_b = _make_tick(9.98, vwap=10.0, ts=ts, symbol="600001.SH")
        r_b = s.on_tick(_FakeEvent(timestamp=ts, symbol="600001.SH", tick_data=tick_b))
        assert r_b == {}


# ------------------------------------------------------------------
# 盘口失衡计算
# ------------------------------------------------------------------


class TestOrderBookImbalance:
    def test_buy_pressure_positive(self) -> None:
        s = VWAPReversionStrategy()
        tick = _make_tick(10.0, bid_vol_1=300.0, ask_vol_1=100.0)
        assert s._order_book_imbalance(tick) == pytest.approx(0.5)

    def test_sell_pressure_negative(self) -> None:
        s = VWAPReversionStrategy()
        tick = _make_tick(10.0, bid_vol_1=100.0, ask_vol_1=300.0)
        assert s._order_book_imbalance(tick) == pytest.approx(-0.5)

    def test_zero_volume_neutral(self) -> None:
        s = VWAPReversionStrategy()
        tick = _make_tick(10.0, bid_vol_1=0.0, ask_vol_1=0.0)
        assert s._order_book_imbalance(tick) == 0.0
