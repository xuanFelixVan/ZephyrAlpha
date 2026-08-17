# [BLUEPRINT] gap-17 board_lot | (auto-injected) |
# [TTL] permanent
"""board_lot 单元测试（40_execution_broker §决策⑰ gap 17 施工）。

覆盖：板块识别、整手规则、买入取整（科创板 200 起买 1 递增）、
      零股一次性卖出调整。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_core.board_lot import (
    AShareBoard,
    BoardLotRule,
    adjust_sell_for_odd_lot,
    classify_board,
    get_board_lot_rule,
    is_odd_lot,
    round_buy_qty,
)

# ── classify_board 板块识别 ────────────────────────────────────────────────────


class TestClassifyBoard:
    def test_star_688(self):
        assert classify_board("688001.SH") is AShareBoard.STAR

    def test_star_689(self):
        assert classify_board("689009.SH") is AShareBoard.STAR

    def test_chinext_300(self):
        assert classify_board("300750.SZ") is AShareBoard.CHINEXT

    def test_chinext_301(self):
        assert classify_board("301088.SZ") is AShareBoard.CHINEXT

    def test_main_sh_600(self):
        assert classify_board("600519.SH") is AShareBoard.MAIN

    def test_main_sh_601(self):
        assert classify_board("601318.SH") is AShareBoard.MAIN

    def test_main_sh_603(self):
        assert classify_board("603986.SH") is AShareBoard.MAIN

    def test_main_sh_605(self):
        assert classify_board("605166.SH") is AShareBoard.MAIN

    def test_main_sz_000(self):
        assert classify_board("000001.SZ") is AShareBoard.MAIN

    def test_main_sz_001(self):
        assert classify_board("001872.SZ") is AShareBoard.MAIN

    def test_bse_8(self):
        assert classify_board("830799.BJ") is AShareBoard.BSE

    def test_bse_4(self):
        assert classify_board("430047.BJ") is AShareBoard.BSE

    def test_bse_92(self):
        # 920xxx 北交所（必须拦截，否则首位 9→SH 误判）
        assert classify_board("920001.BJ") is AShareBoard.BSE

    def test_unknown_empty(self):
        assert classify_board("") is AShareBoard.UNKNOWN

    def test_unknown_alpha(self):
        assert classify_board("AAPL") is AShareBoard.UNKNOWN

    def test_symbol_without_suffix(self):
        # 裸码格式
        assert classify_board("688001") is AShareBoard.STAR
        assert classify_board("300750") is AShareBoard.CHINEXT
        assert classify_board("600519") is AShareBoard.MAIN

    def test_symbol_with_prefix(self):
        # 前缀式 sh600000 / sz000001 / bj830799
        assert classify_board("sh688001") is AShareBoard.STAR
        assert classify_board("sz300750") is AShareBoard.CHINEXT
        assert classify_board("bj830799") is AShareBoard.BSE


# ── get_board_lot_rule 整手规则表 ──────────────────────────────────────────────


class TestGetBoardLotRule:
    def test_main_rule(self):
        rule = get_board_lot_rule("600519.SH")
        assert rule.lot_size == 100
        assert rule.min_unit == 100
        assert rule.increment == 100

    def test_chinext_rule(self):
        rule = get_board_lot_rule("300750.SZ")
        assert rule.lot_size == 100
        assert rule.min_unit == 100
        assert rule.increment == 100

    def test_star_rule(self):
        rule = get_board_lot_rule("688001.SH")
        assert rule.lot_size == 200
        assert rule.min_unit == 200
        assert rule.increment == 1

    def test_bse_rule(self):
        rule = get_board_lot_rule("830799.BJ")
        assert rule.lot_size == 100
        assert rule.min_unit == 100
        assert rule.increment == 100

    def test_unknown_fallback_to_main(self):
        # 未知板块回退主板规则
        rule = get_board_lot_rule("UNKNOWN")
        assert rule.board is AShareBoard.MAIN
        assert rule.lot_size == 100

    def test_rule_is_frozen(self):
        rule = get_board_lot_rule("688001.SH")
        assert isinstance(rule, BoardLotRule)
        with pytest.raises(AttributeError):
            rule.lot_size = 100  # frozen dataclass


# ── round_buy_qty 买入取整 ─────────────────────────────────────────────────────


class TestRoundBuyQty:
    def test_main_exact_100(self):
        assert round_buy_qty(Decimal("100"), "600519.SH") == Decimal("100")

    def test_main_150_rounds_down_to_100(self):
        # 主板 150 股 → 100 股（向下取整到 100 整数倍）
        assert round_buy_qty(Decimal("150"), "600519.SH") == Decimal("100")

    def test_main_250_rounds_to_200(self):
        assert round_buy_qty(Decimal("250"), "600519.SH") == Decimal("200")

    def test_main_below_100_returns_zero(self):
        assert round_buy_qty(Decimal("50"), "600519.SH") == Decimal("0")

    def test_main_zero(self):
        assert round_buy_qty(Decimal("0"), "600519.SH") == Decimal("0")

    def test_main_negative(self):
        assert round_buy_qty(Decimal("-100"), "600519.SH") == Decimal("0")

    # 科创板是 gap 17 的核心修复点（原 floor(qty,100) 对科创板是废单级错误）
    def test_star_exact_200(self):
        assert round_buy_qty(Decimal("200"), "688001.SH") == Decimal("200")

    def test_star_201_allowed(self):
        # 科创板 201 股合法（200 起 + 1 递增）
        assert round_buy_qty(Decimal("201"), "688001.SH") == Decimal("201")

    def test_star_250_returns_250(self):
        # 科创板 250 股合法（200 + 50×1）
        assert round_buy_qty(Decimal("250"), "688001.SH") == Decimal("250")

    def test_star_199_below_min_returns_zero(self):
        # 科创板 199 < 200 起买量 → 0（不能买 100 股，会 error_code=52）
        assert round_buy_qty(Decimal("199"), "688001.SH") == Decimal("0")

    def test_star_100_below_min_returns_zero(self):
        # 科创板 100 股 < 200 起买量 → 0（关键：原代码 floor(100,100)=100 是废单级错误）
        assert round_buy_qty(Decimal("100"), "688001.SH") == Decimal("0")

    def test_star_350_returns_350(self):
        assert round_buy_qty(Decimal("350"), "688001.SH") == Decimal("350")

    def test_star_large_qty(self):
        assert round_buy_qty(Decimal("12345"), "688001.SH") == Decimal("12345")

    def test_chinext_same_as_main(self):
        # 创业板与主板规则一致（100 整数倍）
        assert round_buy_qty(Decimal("150"), "300750.SZ") == Decimal("100")
        assert round_buy_qty(Decimal("250"), "300750.SZ") == Decimal("200")

    def test_bse_same_as_main(self):
        assert round_buy_qty(Decimal("150"), "830799.BJ") == Decimal("100")


# ── is_odd_lot 零股判断 ────────────────────────────────────────────────────────


class TestIsOddLot:
    def test_main_50_is_odd(self):
        assert is_odd_lot(Decimal("50"), "600519.SH") is True

    def test_main_100_not_odd(self):
        assert is_odd_lot(Decimal("100"), "600519.SH") is False

    def test_main_250_not_odd(self):
        assert is_odd_lot(Decimal("250"), "600519.SH") is False

    def test_star_150_is_odd(self):
        # 科创板 150 < 200 起买量 → 零股
        assert is_odd_lot(Decimal("150"), "688001.SH") is True

    def test_star_200_not_odd(self):
        assert is_odd_lot(Decimal("200"), "688001.SH") is False

    def test_zero_not_odd(self):
        assert is_odd_lot(Decimal("0"), "600519.SH") is False

    def test_negative_not_odd(self):
        assert is_odd_lot(Decimal("-10"), "600519.SH") is False


# ── adjust_sell_for_odd_lot 卖出零股调整 ───────────────────────────────────────


class TestAdjustSellForOddLot:
    def test_no_odd_lot_remaining(self):
        # 卖出后剩余 >= min_unit，不调整
        # current=300, sell=100, remaining=200 >= 100 → sell=100
        assert adjust_sell_for_odd_lot(
            Decimal("100"), Decimal("300"), "600519.SH"
        ) == Decimal("100")

    def test_odd_lot_triggers_sell_all(self):
        # current=150, sell=100, remaining=50 < 100 → 全部卖出 150
        assert adjust_sell_for_odd_lot(
            Decimal("100"), Decimal("150"), "600519.SH"
        ) == Decimal("150")

    def test_sell_all_no_adjustment(self):
        # 清仓卖出：current=150, sell=150, remaining=0 → 不触发（remaining=0 非零股）
        assert adjust_sell_for_odd_lot(
            Decimal("150"), Decimal("150"), "600519.SH"
        ) == Decimal("150")

    def test_star_odd_lot(self):
        # 科创板 current=250, sell=100, remaining=150 < 200 → 全部卖出 250
        assert adjust_sell_for_odd_lot(
            Decimal("100"), Decimal("250"), "688001.SH"
        ) == Decimal("250")

    def test_star_no_odd_lot(self):
        # 科创板 current=400, sell=100, remaining=300 >= 200 → 不调整
        assert adjust_sell_for_odd_lot(
            Decimal("100"), Decimal("400"), "688001.SH"
        ) == Decimal("100")

    def test_exact_boundary_remaining(self):
        # remaining 恰好 = min_unit，不触发（边界：>=min_unit 非零股）
        # current=200, sell=100, remaining=100 = min_unit → 不调整
        assert adjust_sell_for_odd_lot(
            Decimal("100"), Decimal("200"), "600519.SH"
        ) == Decimal("100")

    def test_zero_sell(self):
        assert adjust_sell_for_odd_lot(
            Decimal("0"), Decimal("100"), "600519.SH"
        ) == Decimal("0")

    def test_zero_current(self):
        assert adjust_sell_for_odd_lot(
            Decimal("100"), Decimal("0"), "600519.SH"
        ) == Decimal("0")
