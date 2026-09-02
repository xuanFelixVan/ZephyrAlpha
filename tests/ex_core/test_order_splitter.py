# [BLUEPRINT] MOD-EX-014 | docs/03_modules/MOD-EX-014/
# [MODULE] tests.ex_core.test_order_splitter
# [DOMAIN] D_EX_CORE
# [INVARIANTS] 纯函数确定性; Decimal守恒(Σ片=总量); 买入片>=min_unit且increment对齐; 卖出末片可零股; VWAP缺曲线Fail-Closed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSplitRequestError
# [TESTS] self
# [TTL] permanent
"""拆单器 TWAP/VWAP 测试（MOD-EX-014，阶段9 执行链路批）。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_core.order_splitter import (
    InvalidSplitRequestError,
    SplitAlgo,
    SplitRequest,
    split_order,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide

_MAIN = "600000.SH"  # 主板 min_unit=100 increment=100
_STAR = "688001.SH"  # 科创板 min_unit=200 increment=1


def _req(symbol, side, total, n, profile=None):
    return SplitRequest(
        symbol=symbol,
        side=side,
        total_quantity=Decimal(str(total)),
        slice_count=n,
        volume_profile=profile,
    )


class TestValidation:
    def test_non_positive_total_rejected(self):
        with pytest.raises(InvalidSplitRequestError):
            split_order(_req(_MAIN, OrderSide.BUY, 0, 3))

    def test_slice_count_bounds(self):
        with pytest.raises(InvalidSplitRequestError):
            split_order(_req(_MAIN, OrderSide.BUY, 1000, 0))
        with pytest.raises(InvalidSplitRequestError):
            split_order(_req(_MAIN, OrderSide.BUY, 100000, 49))

    def test_vwap_missing_profile_fail_closed(self):
        # 无量能曲线→Fail-Closed，不静默降级 TWAP
        with pytest.raises(InvalidSplitRequestError) as exc_info:
            split_order(
                _req(_MAIN, OrderSide.BUY, 1000, 3, profile=(Decimal("1"),)),
                algo=SplitAlgo.VWAP,
            )
        assert exc_info.value.error_code == "ZA-EX-0018"

    def test_vwap_negative_weight_rejected(self):
        with pytest.raises(InvalidSplitRequestError):
            split_order(
                _req(
                    _MAIN,
                    OrderSide.BUY,
                    1000,
                    2,
                    profile=(Decimal("1"), Decimal("-1")),
                ),
                algo=SplitAlgo.VWAP,
            )

    def test_vwap_all_zero_profile_rejected(self):
        with pytest.raises(InvalidSplitRequestError):
            split_order(
                _req(_MAIN, OrderSide.BUY, 1000, 2, profile=(Decimal("0"), Decimal("0"))),
                algo=SplitAlgo.VWAP,
            )

    def test_buy_illegal_total_rejected(self):
        # 150 股主板买入：非 100 整数倍，须先经 board_lot.round_buy_qty
        with pytest.raises(InvalidSplitRequestError):
            split_order(_req(_MAIN, OrderSide.BUY, 150, 2))


class TestTwap:
    def test_equal_slices_conserve(self):
        # 主板整手对齐：1000/4 → 250 非合法申报，最大余数法落 [300,300,200,200]
        plan = split_order(_req(_MAIN, OrderSide.BUY, 1000, 4), algo=SplitAlgo.TWAP)
        assert [s.quantity for s in plan.slices] == [
            Decimal(300),
            Decimal(300),
            Decimal(200),
            Decimal(200),
        ]
        assert sum(s.quantity for s in plan.slices) == Decimal(1000)
        assert [s.sequence for s in plan.slices] == [1, 2, 3, 4]

    def test_remainder_largest_first(self):
        # 1000/3 片主板：units=10, 余 1 → 首片 +100
        plan = split_order(_req(_MAIN, OrderSide.BUY, 1000, 3), algo=SplitAlgo.TWAP)
        assert [s.quantity for s in plan.slices] == [Decimal(400), Decimal(300), Decimal(300)]
        assert sum(s.quantity for s in plan.slices) == Decimal(1000)

    def test_single_slice_passthrough(self):
        plan = split_order(_req(_MAIN, OrderSide.BUY, 500, 1))
        assert len(plan.slices) == 1
        assert plan.slices[0].quantity == Decimal(500)

    def test_too_many_slices_for_quantity_fail_closed(self):
        # 200 股切 3 片：每片须≥100，不可满足→拒
        with pytest.raises(InvalidSplitRequestError):
            split_order(_req(_MAIN, OrderSide.BUY, 200, 3))

    def test_min_unit_topup_from_largest(self):
        # 主板 1100 切 4 片 TWAP：units=11 → [3,3,3,2] → 300,300,300,200 全≥100
        plan = split_order(_req(_MAIN, OrderSide.BUY, 1100, 4))
        assert all(s.quantity >= Decimal(100) for s in plan.slices)
        assert sum(s.quantity for s in plan.slices) == Decimal(1100)

    def test_star_board_increment_one(self):
        # 科创板 min_unit=200 increment=1：201 股合法
        plan = split_order(_req(_STAR, OrderSide.BUY, 201, 1))
        assert plan.slices[0].quantity == Decimal(201)


class TestVwap:
    def test_weighted_slices_conserve(self):
        # 量能曲线 2:1:1（日内分布注入）
        profile = (Decimal("2"), Decimal("1"), Decimal("1"))
        plan = split_order(_req(_MAIN, OrderSide.BUY, 1000, 3, profile=profile), algo=SplitAlgo.VWAP)
        assert [s.quantity for s in plan.slices] == [Decimal(500), Decimal(300), Decimal(200)]
        assert sum(s.quantity for s in plan.slices) == Decimal(1000)
        assert plan.slices[0].weight == pytest.approx(0.5)

    def test_profile_ordering_preserved(self):
        # A股日内分布：开盘20/上午25/午盘10/尾盘45
        profile = tuple(Decimal(str(w)) for w in (20, 25, 10, 45))
        plan = split_order(_req(_MAIN, OrderSide.BUY, 10000, 4, profile=profile), algo=SplitAlgo.VWAP)
        qtys = [s.quantity for s in plan.slices]
        assert qtys[3] > qtys[1] > qtys[0] > qtys[2]
        assert sum(qtys) == Decimal(10000)


class TestSellOddLot:
    def test_odd_tail_goes_to_last_slice(self):
        # 持仓 250 卖出切 2 片：中间片整手，末片 50 零股一次性申报
        plan = split_order(_req(_MAIN, OrderSide.SELL, 250, 2))
        assert [s.quantity for s in plan.slices] == [Decimal(100), Decimal(150)]
        assert sum(s.quantity for s in plan.slices) == Decimal(250)

    def test_odd_tail_single_slice_legal(self):
        # 整单零股卖出 50 股：单片一次性申报合法，不拦截
        plan = split_order(_req(_MAIN, OrderSide.SELL, 50, 1))
        assert plan.slices[0].quantity == Decimal(50)

    def test_sell_unsplittable_fail_closed(self):
        # 150 切 3 片：中间片无法满足 ≥100 → 拒
        with pytest.raises(InvalidSplitRequestError):
            split_order(_req(_MAIN, OrderSide.SELL, 150, 3))

    def test_sell_conserve_with_odd_tail(self):
        plan = split_order(_req(_MAIN, OrderSide.SELL, 350, 3))
        assert sum(s.quantity for s in plan.slices) == Decimal(350)
        for s in plan.slices[:-1]:
            assert s.quantity % 100 == 0
            assert s.quantity >= Decimal(100)


class TestPurity:
    def test_same_input_same_output(self):
        req = _req(_MAIN, OrderSide.BUY, 1000, 3)
        a = split_order(req, algo=SplitAlgo.TWAP)
        b = split_order(req, algo=SplitAlgo.TWAP)
        assert a == b
