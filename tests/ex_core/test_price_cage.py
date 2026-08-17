# [A_test] module_id: MOD-EXE-price_cage_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_price_cage
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""价格笼子校验单元测试（40_execution_broker §决策⑭ gap 11 施工）。

覆盖：
  - 基准价方向：买入基准=卖一(ask1)，卖出基准=买一(bid1)
  - 板块差异：主板/创业板 ±2%+0.1兜底 / 科创板严格±2% / 北交所±5%
  - 0.1元兜底：低价股按兜底放宽（主板/创业板有，科创板无）
  - 回退链：无盘口→最新成交价→前收盘价
  - 在笼子内不变，超限夹到边界（向下取整到 tick）
  - 无任何基准价可用时返回 UNKNOWN（交由调用方决定）

依据：40_execution_broker.md v2.3.0 §决策⑭（v1.3.0 订正基准价方向）
      上交所 2026 修订交易规则 §3.3.14 / 深交所 §3.1.16
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_core.price_cage import (
    CageStatus,
    PriceCageResult,
    check_price_cage,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide

# ---------------------------------------------------------------------
# 买入基准价 = 卖一价（ask1）
# ---------------------------------------------------------------------


def test_buy_base_is_ask1() -> None:
    """买入基准价取对手方最优价=卖一价（ask1），非买一价。"""
    # ask1=10.00, 2% 笼子 → 上限 10.20；委托 10.10 在笼子内
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.10"),
        symbol="600000.SH",
        ask1=Decimal("10.00"),
        bid1=Decimal("9.99"),
    )
    assert r.status is CageStatus.IN_CAGE
    assert r.base_price == Decimal("10.00")
    assert r.upper_bound == Decimal("10.20")
    assert not r.was_clamped


def test_buy_above_cage_clamped_to_upper() -> None:
    """买入价超笼子上限 → 夹到上限。"""
    # ask1=10.00, 主板 ±2%+0.1兜底 → 上限 max(10.20, 10.10)=10.20
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.50"),
        symbol="600000.SH",
        ask1=Decimal("10.00"),
    )
    assert r.status is CageStatus.CLAMPED
    assert r.clamped_price == Decimal("10.20")
    assert r.was_clamped is True


def test_buy_at_upper_bound_in_cage() -> None:
    """买入价恰好等于笼子上限 → 在笼子内（边界含）。"""
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.20"),
        symbol="600000.SH",
        ask1=Decimal("10.00"),
    )
    assert r.status is CageStatus.IN_CAGE
    assert not r.was_clamped


# ---------------------------------------------------------------------
# 卖出基准价 = 买一价（bid1）
# ---------------------------------------------------------------------


def test_sell_base_is_bid1() -> None:
    """卖出基准价取对手方最优价=买一价（bid1），非卖一价。"""
    # bid1=10.00, 2% 笼子 → 下限 9.80；委托 9.90 在笼子内
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("9.90"),
        symbol="600000.SH",
        ask1=Decimal("10.01"),
        bid1=Decimal("10.00"),
    )
    assert r.status is CageStatus.IN_CAGE
    assert r.base_price == Decimal("10.00")
    assert r.lower_bound == Decimal("9.80")


def test_sell_below_cage_clamped_to_lower() -> None:
    """卖出价低于笼子下限 → 夹到下限。"""
    # bid1=10.00, 主板 → 下限 min(9.80, 9.90)=9.80
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("9.50"),
        symbol="600000.SH",
        bid1=Decimal("10.00"),
    )
    assert r.status is CageStatus.CLAMPED
    assert r.clamped_price == Decimal("9.80")
    assert r.was_clamped is True


def test_sell_at_lower_bound_in_cage() -> None:
    """卖出价恰好等于笼子下限 → 在笼子内（边界含）。"""
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("9.80"),
        symbol="600000.SH",
        bid1=Decimal("10.00"),
    )
    assert r.status is CageStatus.IN_CAGE


# ---------------------------------------------------------------------
# 板块差异：0.1元兜底
# ---------------------------------------------------------------------


def test_main_board_01_floor_widens_cage_for_low_price() -> None:
    """主板低价股：2% < 0.1元时，按 0.1元兜底放宽笼子。"""
    # ask1=3.00, 2%=0.06 < 0.10 → 上限 max(3.06, 3.10)=3.10（兜底生效）
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("3.08"),
        symbol="600000.SH",  # 沪市主板
        ask1=Decimal("3.00"),
    )
    assert r.upper_bound == Decimal("3.10")
    assert r.status is CageStatus.IN_CAGE


def test_chinext_board_01_floor() -> None:
    """创业板同样有 0.1元兜底。"""
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("3.08"),
        symbol="300001.SZ",  # 创业板
        ask1=Decimal("3.00"),
    )
    assert r.upper_bound == Decimal("3.10")


def test_star_board_no_01_floor_strict_2pct() -> None:
    """科创板严格 ±2%，无 0.1元兜底。"""
    # ask1=3.00, 科创板严格 2% → 上限 3.06（无兜底，不放宽到 3.10）
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("3.06"),
        symbol="688001.SH",  # 科创板
        ask1=Decimal("3.00"),
    )
    assert r.upper_bound == Decimal("3.06")
    # 3.08 超过 3.06 → 夹到 3.06
    r2 = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("3.08"),
        symbol="688001.SH",
        ask1=Decimal("3.00"),
    )
    assert r2.status is CageStatus.CLAMPED
    assert r2.clamped_price == Decimal("3.06")


def test_star_board_sell_strict_2pct() -> None:
    """科创板卖出严格 ±2% 无兜底。"""
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("2.94"),
        symbol="688001.SH",
        bid1=Decimal("3.00"),
    )
    assert r.lower_bound == Decimal("2.94")
    assert r.status is CageStatus.IN_CAGE


def test_bse_board_5pct_cage() -> None:
    """北交所笼子幅度 ±5%。"""
    # ask1=10.00, 北交所 ±5% → 上限 10.50
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.40"),
        symbol="830799.BJ",  # 北交所
        ask1=Decimal("10.00"),
    )
    assert r.upper_bound == Decimal("10.50")
    assert r.status is CageStatus.IN_CAGE


def test_bse_board_sell_5pct() -> None:
    """北交所卖出 ±5%。"""
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("9.60"),
        symbol="830799.BJ",
        bid1=Decimal("10.00"),
    )
    assert r.lower_bound == Decimal("9.50")
    assert r.status is CageStatus.IN_CAGE


# ---------------------------------------------------------------------
# 回退链：无盘口 → 最新成交价 → 前收盘价
# ---------------------------------------------------------------------


def test_fallback_to_last_price_when_no_orderbook() -> None:
    """无盘口（ask1/bid1 缺失）→ 回退到最新成交价。"""
    # 买入无 ask1，用 last_price=10.00 作基准
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.10"),
        symbol="600000.SH",
        last_price=Decimal("10.00"),
    )
    assert r.base_price == Decimal("10.00")
    assert r.upper_bound == Decimal("10.20")
    assert r.status is CageStatus.IN_CAGE


def test_fallback_to_prev_close_when_no_orderbook_no_last() -> None:
    """无盘口且无最新价 → 回退到前收盘价。"""
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("9.90"),
        symbol="600000.SH",
        prev_close=Decimal("10.00"),
    )
    assert r.base_price == Decimal("10.00")
    assert r.lower_bound == Decimal("9.80")
    assert r.status is CageStatus.IN_CAGE


def test_fallback_chain_priority_orderbook_first() -> None:
    """盘口优先于最新价/前收盘价。"""
    # ask1=10.00, last=9.50, prev_close=9.00 → 应优先用 ask1
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.10"),
        symbol="600000.SH",
        ask1=Decimal("10.00"),
        last_price=Decimal("9.50"),
        prev_close=Decimal("9.00"),
    )
    assert r.base_price == Decimal("10.00")  # 优先 ask1


def test_fallback_last_priority_over_prev_close() -> None:
    """最新价优先于前收盘价。"""
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.10"),
        symbol="600000.SH",
        last_price=Decimal("10.00"),
        prev_close=Decimal("9.00"),
    )
    assert r.base_price == Decimal("10.00")  # 优先 last_price


def test_no_base_price_returns_unknown() -> None:
    """无任何基准价可用 → 返回 UNKNOWN（调用方决定是否跳过/拒单）。"""
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.00"),
        symbol="600000.SH",
    )
    assert r.status is CageStatus.UNKNOWN
    assert r.upper_bound is None
    assert r.lower_bound is None


# ---------------------------------------------------------------------
# 边界与 tick 取整
# ---------------------------------------------------------------------


def test_clamp_rounds_down_to_tick_for_buy() -> None:
    """买入夹边后向下取整到 tick（0.01），避免超出笼子。"""
    # ask1=10.00, 科创板严格 2% → 上限 10.20（恰在 tick 上）
    # 用一个会产生非 tick 边界的场景：ask1=10.03, 2%=0.2006 → 10.2306 → 夹到 10.23
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.50"),
        symbol="688001.SH",  # 科创板严格2%
        ask1=Decimal("10.03"),
    )
    assert r.status is CageStatus.CLAMPED
    # 10.03 * 1.02 = 10.2306 → 向下取整到 tick 10.23
    assert r.clamped_price == Decimal("10.23")


def test_clamp_rounds_up_to_tick_for_sell() -> None:
    """卖出夹边后向上取整到 tick（0.01），确保 >= 下限。"""
    # bid1=10.03, 科创板 2% → 下限 10.03*0.98=9.8294 → 向上取整到 9.83
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("9.50"),
        symbol="688001.SH",
        bid1=Decimal("10.03"),
    )
    assert r.status is CageStatus.CLAMPED
    # 10.03 * 0.98 = 9.8294 → 向上取整到 tick 9.83
    assert r.clamped_price == Decimal("9.83")


def test_buy_with_negative_or_zero_base_returns_unknown() -> None:
    """基准价 <= 0（异常盘口）→ 返回 UNKNOWN，不误判。"""
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("10.00"),
        symbol="600000.SH",
        ask1=Decimal("0"),
    )
    assert r.status is CageStatus.UNKNOWN


def test_unknown_board_falls_back_to_main_rule() -> None:
    """未知板块回退到主板规则（±2%+0.1兜底），不误用严格规则。"""
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("3.08"),
        symbol="999999.XX",  # 无法识别
        ask1=Decimal("3.00"),
    )
    # 主板兜底：max(3.06, 3.10)=3.10
    assert r.upper_bound == Decimal("3.10")


# ---------------------------------------------------------------------
# 集成场景：涨停/跌停价在笼子内
# ---------------------------------------------------------------------


def test_limit_up_sell_price_in_cage() -> None:
    """涨停板卖单挂涨停价在笼子内（涨停价=前收×110% >= 买一×98%）。"""
    # prev_close=10.00, 涨停=11.00, bid1=10.80 → 下限 min(10.584, 10.70)=10.584
    # 11.00 >= 10.584 → 在笼子内
    r = check_price_cage(
        side=OrderSide.SELL,
        limit_price=Decimal("11.00"),
        symbol="600000.SH",
        bid1=Decimal("10.80"),
    )
    assert r.status is CageStatus.IN_CAGE


def test_limit_down_buy_price_in_cage() -> None:
    """跌停板买单挂跌停价在笼子内（跌停价=前收×90% <= 卖一×102%）。"""
    # ask1=9.20, 跌停=9.00 → 上限 max(9.384, 9.30)=9.384；9.00 <= 9.384 → 在笼子内
    r = check_price_cage(
        side=OrderSide.BUY,
        limit_price=Decimal("9.00"),
        symbol="600000.SH",
        ask1=Decimal("9.20"),
    )
    assert r.status is CageStatus.IN_CAGE
