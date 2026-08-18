# [MODULE] tests.pf_core.test_intraday_surge_fall_strategy
# [DOMAIN] D_PF_CORE
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_SURGE_FALL_STRATEGY | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IntradaySurgeFallStrategy 单元测试（路径 B 示例策略）。

覆盖做 T 状态机的核心决策点：
  - 无效价格（<=0）跳过
  - long 态：无冲高 → 持仓不变
  - long 态：冲高+回落+卖盘压力 → 卖出（target_weight=0）
  - long 态：冲高+回落但买盘支撑（ob_imbalance>=0）→ 滤子拦截不卖
  - flat 态：未跌至 dip 阈值 → 持仓不变
  - flat 态：较卖出价回落 >= dip → 买回（target_weight=base_weight）
  - 完整 round-trip：long→卖出→买回
  - 窗口淘汰：30s 旧 tick 淘汰后 baseline 更新
  - 盘口失衡计算 + 构造参数校验
  - 注册表发现（strategy_id="intraday-surge-fall"）
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from zephyr.backtest.core.matching_logic import TickSnapshot
from zephyr.pf_core.intraday_surge_fall_strategy import IntradaySurgeFallStrategy
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
    bid_vol_1: float = 100.0,
    ask_vol_1: float = 100.0,
    ts: datetime | None = None,
    symbol: str = "600000.SH",
) -> TickSnapshot:
    """构造 TickSnapshot（5 档盘口，仅一档量有意义，其余填占位）。"""
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
        amount=Decimal("0"),
        volume=Decimal("0"),
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
    strategy: IntradaySurgeFallStrategy,
    prices: list[float],
    *,
    start: datetime | None = None,
    bid_vol_1: float = 100.0,
    ask_vol_1: float = 100.0,
    symbol: str = "600000.SH",
) -> list[dict[str, float]]:
    """按 1 秒间隔喂入一组 tick 价格，收集每次返回的权重 dict。"""
    base = start or datetime(2026, 7, 31, 10, 0, 0)
    results: list[dict[str, float]] = []
    for i, p in enumerate(prices):
        ts = base + timedelta(seconds=i)
        tick = _make_tick(p, bid_vol_1=bid_vol_1, ask_vol_1=ask_vol_1, ts=ts, symbol=symbol)
        results.append(strategy.on_tick(_FakeEvent(timestamp=ts, symbol=symbol, tick_data=tick)))
    return results


# ------------------------------------------------------------------
# 构造与注册
# ------------------------------------------------------------------


class TestConstruction:
    def test_invalid_window_seconds_raises(self) -> None:
        with pytest.raises(ValueError, match="window_seconds"):
            IntradaySurgeFallStrategy(window_seconds=0)

    def test_invalid_base_weight_raises(self) -> None:
        with pytest.raises(ValueError, match="base_weight"):
            IntradaySurgeFallStrategy(base_weight=0.0)
        with pytest.raises(ValueError, match="base_weight"):
            IntradaySurgeFallStrategy(base_weight=1.5)

    def test_registered_in_tick_registry(self) -> None:
        """导入即注册（@register 装饰器在类定义时执行）；autodiscover 幂等可发现。"""
        # 本测试文件顶部 import 已触发 @register
        assert TickStrategyBase.get("intraday-surge-fall") is IntradaySurgeFallStrategy
        # autodiscover 重复 import 缓存模块，不重复注册、不报错
        autodiscover_tick_strategies("zephyr.pf_core")
        assert TickStrategyBase.get("intraday-surge-fall") is IntradaySurgeFallStrategy


# ------------------------------------------------------------------
# on_tick 决策逻辑
# ------------------------------------------------------------------


class TestOnTickDecisions:
    def test_invalid_price_returns_empty(self) -> None:
        """last_price<=0（盘前/停牌）→ 空，不调仓。"""
        s = IntradaySurgeFallStrategy()
        tick = _make_tick(0.0)
        assert s.on_tick(_FakeEvent(timestamp=datetime(2026, 7, 31, 9, 25), tick_data=tick)) == {}

    def test_long_no_surge_holds(self) -> None:
        """long 态下价格平稳波动（无冲高）→ 全程返回空（持仓不变）。"""
        s = IntradaySurgeFallStrategy(use_order_book=False)
        # 价格在 10.00 附近小幅波动，无冲高
        results = _feed(s, [10.00, 10.01, 10.00, 10.01, 10.00])
        assert all(r == {} for r in results)

    def test_surge_fall_with_sell_pressure_sells(self) -> None:
        """冲高+回落+卖盘压力（ask>bid）→ 卖出 target_weight=0。"""
        # 10.00 → 10.06(+0.6% 冲高) → 10.04(从峰值 10.06 回落 0.198%)
        s = IntradaySurgeFallStrategy(
            surge_threshold=0.003, fall_threshold=0.001, use_order_book=True,
        )
        results = _feed(
            s, [10.00, 10.06, 10.04],
            bid_vol_1=50.0, ask_vol_1=200.0,  # 卖盘压力（ob_imbalance<0）
        )
        sells = [r for r in results if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}

    def test_surge_fall_but_buy_support_blocks_sell(self) -> None:
        """冲高+回落但买盘支撑（ob_imbalance>=0）→ 盘口滤子拦截，不卖。"""
        s = IntradaySurgeFallStrategy(use_order_book=True)
        results = _feed(
            s, [10.00, 10.06, 10.04],
            bid_vol_1=200.0, ask_vol_1=50.0,  # 买盘支撑（ob_imbalance>0）
        )
        assert all(r == {} for r in results)

    def test_order_book_disabled_sells_on_pure_price(self) -> None:
        """关闭盘口滤子后，仅凭冲高回落形态即卖出。"""
        s = IntradaySurgeFallStrategy(use_order_book=False)
        results = _feed(s, [10.00, 10.06, 10.04])
        sells = [r for r in results if r]
        assert len(sells) == 1
        assert sells[0] == {"600000.SH": 0.0}

    def test_flat_insufficient_dip_holds(self) -> None:
        """flat 态下未跌至 dip 阈值 → 持仓不变（不买回）。"""
        s = IntradaySurgeFallStrategy(use_order_book=False, dip_threshold=0.003)
        # 先卖出进入 flat 态（卖出价 10.04）
        _feed(s, [10.00, 10.06, 10.04])
        # dip_threshold=0.3% → 需跌至 ~10.01 才买回；10.03 不够（dip≈0.1%）
        results = _feed(s, [10.03, 10.03], start=datetime(2026, 7, 31, 10, 0, 10))
        assert all(r == {} for r in results)

    def test_flat_sufficient_dip_buys_back(self) -> None:
        """flat 态下较卖出价回落 >= dip → 买回 target_weight=base_weight。"""
        s = IntradaySurgeFallStrategy(
            use_order_book=False, dip_threshold=0.003, base_weight=0.8,
        )
        # 卖出（卖出价 10.04）
        _feed(s, [10.00, 10.06, 10.04])
        # 跌至 10.00（较 10.04 跌 0.4% >= 0.3%）→ 买回
        results = _feed(s, [10.00], start=datetime(2026, 7, 31, 10, 0, 10))
        buys = [r for r in results if r]
        assert len(buys) == 1
        assert buys[0] == {"600000.SH": 0.8}


# ------------------------------------------------------------------
# 完整 round-trip
# ------------------------------------------------------------------


class TestRoundTrip:
    def test_full_round_trip_long_sell_buy(self) -> None:
        """完整做 T：long → 卖出 → 买回，最终回到 long 态。"""
        s = IntradaySurgeFallStrategy(use_order_book=False, base_weight=1.0)
        # 阶段1：冲高回落卖出
        r1 = _feed(s, [10.00, 10.06, 10.04])  # 卖出价 10.04
        assert any(r == {"600000.SH": 0.0} for r in r1)
        # 阶段2：较卖出价回落买回
        r2 = _feed(s, [9.99], start=datetime(2026, 7, 31, 10, 0, 10))
        assert any(r == {"600000.SH": 1.0} for r in r2)
        # 此后应回到 long 态：再次冲高回落可卖出
        r3 = _feed(s, [9.99, 10.05, 10.03], start=datetime(2026, 7, 31, 10, 0, 20))
        assert any(r == {"600000.SH": 0.0} for r in r3)


# ------------------------------------------------------------------
# 窗口淘汰
# ------------------------------------------------------------------


class TestWindowEviction:
    def test_old_ticks_evicted_baseline_updates(self) -> None:
        """30s 窗口外的旧 tick 被淘汰，baseline 更新为新窗口最旧价。"""
        s = IntradaySurgeFallStrategy(
            window_seconds=30, use_order_book=False,
            surge_threshold=0.003, fall_threshold=0.001,
        )
        base = datetime(2026, 7, 31, 10, 0, 0)
        # 10.00 起步，10s 后到 10.05，再过 25s（距首 tick 35s）回 10.04
        # 此时 10.00 已淘汰出 30s 窗口，baseline 变为窗口内最旧价
        prices_ts = [
            (10.00, base),
            (10.05, base + timedelta(seconds=10)),
            (10.04, base + timedelta(seconds=35)),
        ]
        results = []
        for p, ts in prices_ts:
            tick = _make_tick(p, ts=ts)
            results.append(s.on_tick(_FakeEvent(timestamp=ts, tick_data=tick)))
        # 窗口淘汰后 baseline≈10.05 区间，10.04 对该 baseline 是下跌而非冲高，
        # 故不应触发卖出——验证窗口淘汰改变了 baseline 语义
        assert all(r == {} for r in results)

    def test_within_window_surge_triggers(self) -> None:
        """对照：冲高回落全在 30s 窗口内 → 正常卖出。"""
        s = IntradaySurgeFallStrategy(use_order_book=False)
        base = datetime(2026, 7, 31, 10, 0, 0)
        prices_ts = [
            (10.00, base),
            (10.06, base + timedelta(seconds=5)),   # +0.6% 冲高
            (10.04, base + timedelta(seconds=10)),  # 从峰值 10.06 回落 0.198%
        ]
        results = []
        for p, ts in prices_ts:
            tick = _make_tick(p, ts=ts)
            results.append(s.on_tick(_FakeEvent(timestamp=ts, tick_data=tick)))
        assert any(r == {"600000.SH": 0.0} for r in results)


# ------------------------------------------------------------------
# 盘口失衡计算
# ------------------------------------------------------------------


class TestOrderBookImbalance:
    def test_buy_pressure_positive(self) -> None:
        s = IntradaySurgeFallStrategy()
        tick = _make_tick(10.0, bid_vol_1=300.0, ask_vol_1=100.0)
        assert s._order_book_imbalance(tick) == pytest.approx(0.5)

    def test_sell_pressure_negative(self) -> None:
        s = IntradaySurgeFallStrategy()
        tick = _make_tick(10.0, bid_vol_1=100.0, ask_vol_1=300.0)
        assert s._order_book_imbalance(tick) == pytest.approx(-0.5)

    def test_zero_volume_neutral(self) -> None:
        s = IntradaySurgeFallStrategy()
        tick = _make_tick(10.0, bid_vol_1=0.0, ask_vol_1=0.0)
        assert s._order_book_imbalance(tick) == 0.0
