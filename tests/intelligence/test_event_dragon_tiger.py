# [MODULE] tests.intelligence.test_event_dragon_tiger
# [DOMAIN] D_INTELLIGENCE
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/intelligence/test_event_dragon_tiger.py -q
"""test_event_dragon_tiger.py — 龙虎榜佐证修正因子单元测试（26 号 §2.5 v1.8.0）。

覆盖：
  1. 无数据 → 1.0
  2. 净买率硬阈值（≥12%→1.2 / <12%→1.0 / 边界恰好 12% / 零成交降级）
  3. 量化席位过滤（hard ×0.7 / soft ×0.85 / 不足 3 席不过滤 / 零买入基线）
  4. 组合场景（强佐证×量化 hard/soft）与值域 [0.7, 1.2]
"""
from __future__ import annotations

import pytest

from zephyr.intelligence.event_dragon_tiger import (
    DragonTigerData,
    DragonTigerSeat,
    dragon_tiger_corroboration_modifier,
)


def _dt(net=130.0, turnover=1000.0, total_buy=500.0, seats=()) -> DragonTigerData:
    return DragonTigerData(
        net_buy_amount=net, total_turnover=turnover, total_buy=total_buy, buyer_seats=tuple(seats),
    )


def _quant_seats(n: int, each: float) -> list[DragonTigerSeat]:
    return [DragonTigerSeat(type="quant_inst", buy_amount=each) for _ in range(n)]


# ============ 1-2. 净买率门控 ============


class TestNetBuyRatioGate:
    def test_none_data_neutral(self):
        assert dragon_tiger_corroboration_modifier(None) == 1.0

    def test_strong_net_buy_ratio_boosts(self):
        assert dragon_tiger_corroboration_modifier(_dt(net=130.0, turnover=1000.0)) == 1.2

    def test_boundary_exactly_12pct_boosts(self):
        assert dragon_tiger_corroboration_modifier(_dt(net=120.0, turnover=1000.0)) == 1.2

    def test_below_threshold_no_boost(self):
        # 机构净买入方向性失效（45.7%<随机）→ 不加分
        assert dragon_tiger_corroboration_modifier(_dt(net=119.0, turnover=1000.0)) == 1.0

    def test_zero_turnover_degrades_no_boost(self):
        assert dragon_tiger_corroboration_modifier(_dt(net=999.0, turnover=0.0)) == 1.0


# ============ 3. 量化席位过滤 ============


class TestQuantSeatFilter:
    def test_hard_filter_when_dominant(self):
        # 3 量化席买入 200/500 = 40% > 30% → hard ×0.7（净买率 5% → base 1.0）
        data = _dt(net=50.0, seats=_quant_seats(3, 200.0 / 3))
        assert dragon_tiger_corroboration_modifier(data) == pytest.approx(1.0 * 0.7)

    def test_soft_filter_when_present_not_dominant(self):
        # 3 量化席买入 100/500 = 20% ≤ 30% → soft ×0.85
        data = _dt(net=50.0, seats=_quant_seats(3, 100.0 / 3))
        assert dragon_tiger_corroboration_modifier(data) == pytest.approx(1.0 * 0.85)

    def test_two_quant_seats_no_filter(self):
        data = _dt(net=50.0, seats=_quant_seats(2, 200.0))
        assert dragon_tiger_corroboration_modifier(data) == 1.0

    def test_non_quant_seats_ignored(self):
        seats = [DragonTigerSeat(type="hot_money", buy_amount=200.0) for _ in range(4)]
        assert dragon_tiger_corroboration_modifier(_dt(net=50.0, seats=seats)) == 1.0

    def test_zero_total_buy_quant_ratio_zero(self):
        data = _dt(net=50.0, total_buy=0.0, seats=_quant_seats(3, 100.0))
        # quant_buy_ratio=0 → 不触发 hard，但 quant_count>=3 → soft
        assert dragon_tiger_corroboration_modifier(data) == pytest.approx(1.0 * 0.85)


# ============ 4. 组合场景与值域 ============


class TestCombined:
    def test_strong_boost_with_hard_filter(self):
        # 1.2 × 0.7 = 0.84
        data = _dt(net=200.0, seats=_quant_seats(3, 200.0 / 3))
        assert dragon_tiger_corroboration_modifier(data) == pytest.approx(1.2 * 0.7)

    def test_strong_boost_with_soft_filter(self):
        # 1.2 × 0.85 = 1.02
        data = _dt(net=200.0, seats=_quant_seats(3, 100.0 / 3))
        assert dragon_tiger_corroboration_modifier(data) == pytest.approx(1.2 * 0.85)

    def test_value_range_bounded(self):
        cases = [
            None,
            _dt(net=0.0),
            _dt(net=1000.0, turnover=1000.0),
            _dt(net=1000.0, turnover=1000.0, seats=_quant_seats(5, 150.0)),
            _dt(net=1000.0, turnover=1000.0, seats=_quant_seats(5, 50.0)),
        ]
        for data in cases:
            m = dragon_tiger_corroboration_modifier(data)
            assert 0.7 <= m <= 1.2, data
