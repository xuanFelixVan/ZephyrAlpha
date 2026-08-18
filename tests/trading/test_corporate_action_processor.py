# [BLUEPRINT] MOD-TRADING-004 | docs/03_modules/_domain_trading/corporate_action_processor/blueprint.md
# [MODULE] tests.trading.test_corporate_action_processor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.corporate_action_processor
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-TRADING-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-TRADING-004 Corporate Action Processor 单元测试.

覆盖: 现金分红/送股/配股/拆股/除权除息复合/零持仓/负成本保护/
批量处理/回调触发/回调异常不阻断/Decimal精度/输入校验.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.trading.corporate_action_processor import (
    CorporateAction,
    CorporateActionProcessor,
    CorporateActionResult,
    CorporateActionType,
    InvalidCorporateActionError,
    PositionAdjustment,
)

EX_DATE = "2026-08-01"


# ── 辅助工厂 ──


def make_action(
    action_id: str = "CA001",
    symbol: str = "600000.SH",
    action_type: CorporateActionType = CorporateActionType.CASH_DIVIDEND,
    dividend_per_share: str | None = None,
    stock_dividend_ratio: str | None = None,
    rights_ratio: str | None = None,
    rights_price: str | None = None,
    split_ratio: str | None = None,
    ex_date: str = EX_DATE,
) -> CorporateAction:
    return CorporateAction(
        action_id=action_id,
        symbol=symbol,
        action_type=action_type,
        ex_date=ex_date,
        dividend_per_share=(
            Decimal(dividend_per_share) if dividend_per_share is not None else None
        ),
        stock_dividend_ratio=(
            Decimal(stock_dividend_ratio)
            if stock_dividend_ratio is not None
            else None
        ),
        rights_ratio=(
            Decimal(rights_ratio) if rights_ratio is not None else None
        ),
        rights_price=(
            Decimal(rights_price) if rights_price is not None else None
        ),
        split_ratio=(
            Decimal(split_ratio) if split_ratio is not None else None
        ),
    )


# ── 现金分红 ──


class TestCashDividend:
    def test_basic_cash_dividend(self):
        """现金分红: avg_cost 下降, qty 不变, 现金流入。"""
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="0.50",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_quantity == Decimal("100")  # qty 不变
        assert adj.adjusted_avg_cost == Decimal("9.50")  # 10 - 0.5
        assert adj.cash_delta == Decimal("50.00")  # 0.5 × 100

    def test_dividend_exceeds_cost_floor_zero(self):
        """分红超过成本——avg_cost 归零(max(0,...)保护)。"""
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="15.00",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_avg_cost == Decimal("0")
        assert adj.cash_delta == Decimal("1500.00")

    def test_zero_dividend(self):
        """零分红——无变化。"""
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="0",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_quantity == Decimal("100")
        assert adj.adjusted_avg_cost == Decimal("10")
        assert adj.cash_delta == Decimal("0")


# ── 送股 ──


class TestStockDividend:
    def test_basic_stock_dividend(self):
        """送股: qty 增加, avg_cost 下降, 无现金变动。

        每10股送3股 → ratio=0.3
        qty_new = 100 × 1.3 = 130
        cost_new = 10 / 1.3 ≈ 7.6923...
        """
        action = make_action(
            action_type=CorporateActionType.STOCK_DIVIDEND,
            stock_dividend_ratio="0.3",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_quantity == Decimal("130")
        assert adj.adjusted_avg_cost == Decimal("10") / Decimal("1.3")
        assert adj.cash_delta == Decimal("0")

    def test_stock_dividend_value_preserved(self):
        """送股前后总市值不变(qty×cost 恒等)。"""
        action = make_action(
            action_type=CorporateActionType.STOCK_DIVIDEND,
            stock_dividend_ratio="0.5",
        )
        qty, cost = Decimal("200"), Decimal("8")
        adj = CorporateActionProcessor().process(action, qty, cost)

        original_value = qty * cost
        adjusted_value = adj.adjusted_quantity * adj.adjusted_avg_cost
        assert original_value == adjusted_value


# ── 配股 ──


class TestRightsOffering:
    def test_basic_rights_offering(self):
        """配股: qty 增加, avg_cost 调整, 现金流出。

        每10股配3股 → ratio=0.3, 配股价=5元
        qty_new = 100 × 1.3 = 130
        cost_new = (10 + 5×0.3) / 1.3 = 11.5 / 1.3 ≈ 8.846...
        cash = -5 × 100 × 0.3 = -150
        """
        action = make_action(
            action_type=CorporateActionType.RIGHTS_OFFERING,
            rights_ratio="0.3",
            rights_price="5",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_quantity == Decimal("130")
        expected_cost = (Decimal("10") + Decimal("5") * Decimal("0.3")) / Decimal("1.3")
        assert adj.adjusted_avg_cost == expected_cost
        assert adj.cash_delta == Decimal("-150")

    def test_rights_at_market_price(self):
        """配股价等于市价——avg_cost 不变。"""
        action = make_action(
            action_type=CorporateActionType.RIGHTS_OFFERING,
            rights_ratio="0.5",
            rights_price="10",  # 等于 avg_cost
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_avg_cost == Decimal("10")
        assert adj.cash_delta == Decimal("-500")  # -10 × 100 × 0.5


# ── 拆股 ──


class TestStockSplit:
    def test_forward_split(self):
        """1拆2: qty 翻倍, cost 减半。"""
        action = make_action(
            action_type=CorporateActionType.STOCK_SPLIT,
            split_ratio="2",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_quantity == Decimal("200")
        assert adj.adjusted_avg_cost == Decimal("5")
        assert adj.cash_delta == Decimal("0")

    def test_reverse_split(self):
        """2并1: qty 减半, cost 翻倍。"""
        action = make_action(
            action_type=CorporateActionType.STOCK_SPLIT,
            split_ratio="0.5",
        )
        adj = CorporateActionProcessor().process(action, Decimal("200"), Decimal("5"))

        assert adj.adjusted_quantity == Decimal("100")
        assert adj.adjusted_avg_cost == Decimal("10")

    def test_split_value_preserved(self):
        """拆股前后总市值不变。"""
        action = make_action(
            action_type=CorporateActionType.STOCK_SPLIT,
            split_ratio="3",
        )
        qty, cost = Decimal("100"), Decimal("30")
        adj = CorporateActionProcessor().process(action, qty, cost)

        assert qty * cost == adj.adjusted_quantity * adj.adjusted_avg_cost


# ── 除权除息复合 ──


class TestExRights:
    def test_cash_plus_stock_dividend(self):
        """复合: 现金分红 + 送股。

        分红0.5元 → cost: 10 → 9.5
        送股(每10送3) → qty: 100 → 130, cost: 9.5 → 9.5/1.3
        """
        action = make_action(
            action_type=CorporateActionType.EX_RIGHTS,
            dividend_per_share="0.5",
            stock_dividend_ratio="0.3",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        assert adj.adjusted_quantity == Decimal("130")
        expected_cost = (Decimal("10") - Decimal("0.5")) / Decimal("1.3")
        assert adj.adjusted_avg_cost == expected_cost
        assert adj.cash_delta == Decimal("50")  # 0.5 × 100

    def test_full_ex_rights(self):
        """完整除权除息: 分红 + 送股 + 配股。

        分红0.5 → cost 10→9.5, cash +50
        送股0.3 → qty 100→130, cost 9.5→9.5/1.3
        配股0.2@6 → qty 130→156, cost 调整, cash -6×130×0.2=-156
        """
        action = make_action(
            action_type=CorporateActionType.EX_RIGHTS,
            dividend_per_share="0.5",
            stock_dividend_ratio="0.3",
            rights_ratio="0.2",
            rights_price="6",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

        # qty: 100 → 130 (送股) → 156 (配股)
        assert adj.adjusted_quantity == Decimal("156")

        # cost: 10 → 9.5 (分红) → 9.5/1.3 (送股) → (9.5/1.3 + 6×0.2) / 1.2 (配股)
        cost_after_div = Decimal("10") - Decimal("0.5")
        cost_after_sd = cost_after_div / Decimal("1.3")
        expected_cost = (cost_after_sd + Decimal("6") * Decimal("0.2")) / Decimal("1.2")
        assert adj.adjusted_avg_cost == expected_cost

        # cash: +50 (分红) - 156×... wait, 配股 cash = -6 × 130 × 0.2 = -156
        # total = 50 - 156 = -106
        assert adj.cash_delta == Decimal("50") + Decimal("-156")

    def test_ex_rights_with_split(self):
        """除权除息含拆股: 分红 + 拆股。"""
        action = make_action(
            action_type=CorporateActionType.EX_RIGHTS,
            dividend_per_share="1.0",
            split_ratio="2",
        )
        adj = CorporateActionProcessor().process(action, Decimal("100"), Decimal("20"))

        # 分红: cost 20→19, cash +100
        # 拆股: qty 100→200, cost 19→9.5
        assert adj.adjusted_quantity == Decimal("200")
        assert adj.adjusted_avg_cost == Decimal("19") / Decimal("2")
        assert adj.cash_delta == Decimal("100")


# ── 零持仓 ──


class TestZeroQuantity:
    def test_zero_quantity_cash_dividend(self):
        """零持仓现金分红——无影响。"""
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="0.5",
        )
        adj = CorporateActionProcessor().process(action, Decimal("0"), Decimal("10"))

        assert adj.adjusted_quantity == Decimal("0")
        assert adj.cash_delta == Decimal("0")


# ── 批量处理 ──


class TestBatchApply:
    def test_apply_multiple_actions(self):
        """批量处理: 多标的, 多行动。"""
        actions = [
            make_action(
                action_id="CA1",
                symbol="600000.SH",
                action_type=CorporateActionType.CASH_DIVIDEND,
                dividend_per_share="0.5",
            ),
            make_action(
                action_id="CA2",
                symbol="000001.SZ",
                action_type=CorporateActionType.STOCK_SPLIT,
                split_ratio="2",
            ),
        ]
        positions = {
            "600000.SH": (Decimal("100"), Decimal("10")),
            "000001.SZ": (Decimal("200"), Decimal("20")),
        }
        result = CorporateActionProcessor().apply(actions, positions)

        assert isinstance(result, CorporateActionResult)
        assert len(result.adjustments) == 2
        assert result.total_cash_delta == Decimal("50")  # 仅分红有现金流入

        # 第一项: 分红
        assert result.adjustments[0].symbol == "600000.SH"
        assert result.adjustments[0].adjusted_avg_cost == Decimal("9.5")

        # 第二项: 拆股
        assert result.adjustments[1].symbol == "000001.SZ"
        assert result.adjustments[1].adjusted_quantity == Decimal("400")

    def test_apply_skips_no_position(self):
        """批量处理: 无持仓的标的跳过。"""
        actions = [
            make_action(
                action_id="CA1",
                symbol="600000.SH",
                action_type=CorporateActionType.CASH_DIVIDEND,
                dividend_per_share="0.5",
            ),
            make_action(
                action_id="CA2",
                symbol="999999.SZ",
                action_type=CorporateActionType.CASH_DIVIDEND,
                dividend_per_share="1.0",
            ),
        ]
        positions = {"600000.SH": (Decimal("100"), Decimal("10"))}
        result = CorporateActionProcessor().apply(actions, positions)

        assert len(result.adjustments) == 1
        assert result.adjustments[0].symbol == "600000.SH"

    def test_apply_sequential_same_symbol(self):
        """同一标的多行动顺序应用: 分红 → 拆股。"""
        actions = [
            make_action(
                action_id="CA1",
                symbol="600000.SH",
                action_type=CorporateActionType.CASH_DIVIDEND,
                dividend_per_share="1.0",
            ),
            make_action(
                action_id="CA2",
                symbol="600000.SH",
                action_type=CorporateActionType.STOCK_SPLIT,
                split_ratio="2",
            ),
        ]
        positions = {"600000.SH": (Decimal("100"), Decimal("10"))}
        result = CorporateActionProcessor().apply(actions, positions)

        assert len(result.adjustments) == 2
        # 第一次: 分红 → qty=100, cost=9
        assert result.adjustments[0].adjusted_avg_cost == Decimal("9")
        # 第二次: 拆股(基于第一次结果) → qty=200, cost=4.5
        assert result.adjustments[1].adjusted_quantity == Decimal("200")
        assert result.adjustments[1].adjusted_avg_cost == Decimal("4.5")

    def test_apply_empty(self):
        """空列表——无调整。"""
        result = CorporateActionProcessor().apply([], {})
        assert len(result.adjustments) == 0
        assert result.total_cash_delta == Decimal("0")


# ── 回调 ──


class TestCallback:
    def test_callback_triggered_on_apply(self):
        """apply 有调整时触发 on_adjusted 回调。"""
        triggered: list[CorporateActionResult] = []

        def on_adj(result: CorporateActionResult) -> None:
            triggered.append(result)

        actions = [
            make_action(
                action_type=CorporateActionType.CASH_DIVIDEND,
                dividend_per_share="0.5",
            )
        ]
        positions = {"600000.SH": (Decimal("100"), Decimal("10"))}
        CorporateActionProcessor(on_adjusted=on_adj).apply(actions, positions)

        assert len(triggered) == 1
        assert len(triggered[0].adjustments) == 1

    def test_callback_not_triggered_on_empty(self):
        """无调整时不触发回调。"""
        triggered: list[CorporateActionResult] = []

        def on_adj(result: CorporateActionResult) -> None:
            triggered.append(result)

        CorporateActionProcessor(on_adjusted=on_adj).apply([], {})
        assert len(triggered) == 0

    def test_callback_exception_does_not_block(self):
        """回调抛异常不阻断处理主流程。"""
        def bad_callback(result: CorporateActionResult) -> None:
            raise RuntimeError("通知通道故障")

        actions = [
            make_action(
                action_type=CorporateActionType.CASH_DIVIDEND,
                dividend_per_share="0.5",
            )
        ]
        positions = {"600000.SH": (Decimal("100"), Decimal("10"))}
        result = CorporateActionProcessor(on_adjusted=bad_callback).apply(
            actions, positions
        )
        assert len(result.adjustments) == 1


# ── 输入校验 ──


class TestInputValidation:
    def test_negative_quantity_raises(self):
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="0.5",
        )
        with pytest.raises(InvalidCorporateActionError):
            CorporateActionProcessor().process(action, Decimal("-1"), Decimal("10"))

    def test_negative_avg_cost_raises(self):
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="0.5",
        )
        with pytest.raises(InvalidCorporateActionError):
            CorporateActionProcessor().process(action, Decimal("100"), Decimal("-1"))

    def test_missing_dividend_raises(self):
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share=None,
        )
        with pytest.raises(InvalidCorporateActionError):
            CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

    def test_negative_ratio_raises(self):
        action = make_action(
            action_type=CorporateActionType.STOCK_DIVIDEND,
            stock_dividend_ratio="-0.5",
        )
        with pytest.raises(InvalidCorporateActionError):
            CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

    def test_zero_split_ratio_raises(self):
        action = make_action(
            action_type=CorporateActionType.STOCK_SPLIT,
            split_ratio="0",
        )
        with pytest.raises(InvalidCorporateActionError):
            CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

    def test_empty_action_id_raises(self):
        action = CorporateAction(
            action_id="",
            symbol="600000.SH",
            action_type=CorporateActionType.CASH_DIVIDEND,
            ex_date=EX_DATE,
            dividend_per_share=Decimal("0.5"),
        )
        with pytest.raises(InvalidCorporateActionError):
            CorporateActionProcessor().process(action, Decimal("100"), Decimal("10"))

    def test_error_code(self):
        assert InvalidCorporateActionError.error_code == "ZA-TR-0020"


# ── Decimal 精度 ──


class TestDecimalPrecision:
    def test_decimal_preserved(self):
        """Decimal 精度保持。"""
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="0.123456789",
        )
        adj = CorporateActionProcessor().process(
            action, Decimal("100"), Decimal("10.000000000")
        )
        assert adj.adjusted_avg_cost == Decimal("9.876543211")
        assert adj.cash_delta == Decimal("12.3456789")

    def test_no_float_contamination(self):
        action = make_action(
            action_type=CorporateActionType.STOCK_SPLIT,
            split_ratio="3",
        )
        adj = CorporateActionProcessor().process(
            action, Decimal("100"), Decimal("30")
        )
        assert isinstance(adj.adjusted_quantity, Decimal)
        assert isinstance(adj.adjusted_avg_cost, Decimal)
        assert isinstance(adj.cash_delta, Decimal)


# ── 不可变性 ──


class TestImmutability:
    def test_frozen_dataclasses(self):
        action = make_action(
            action_type=CorporateActionType.CASH_DIVIDEND,
            dividend_per_share="0.5",
        )
        with pytest.raises(Exception):
            action.symbol = "X"  # type: ignore[misc]

        adj = PositionAdjustment(
            action_id="CA1",
            symbol="600000.SH",
            action_type=CorporateActionType.CASH_DIVIDEND,
            original_quantity=Decimal("100"),
            original_avg_cost=Decimal("10"),
            adjusted_quantity=Decimal("100"),
            adjusted_avg_cost=Decimal("9.5"),
            cash_delta=Decimal("50"),
        )
        with pytest.raises(Exception):
            adj.symbol = "X"  # type: ignore[misc]
