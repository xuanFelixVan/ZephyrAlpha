# -*- coding: utf-8 -*-
"""边界单测：除权除息处理（GAP-010）

测试除权除息日的持仓数量/成本价调整。
"""

from datetime import date
from decimal import Decimal

from zephyr.ex_core.corporate_action_adjuster import (
    CorporateAction,
    CorporateActionAdjuster,
)


def _action(
    symbol: str = "600000.SH",
    cash: str = "0",
    ratio: str = "0",
    record_close: str = "10.00",
) -> CorporateAction:
    return CorporateAction(
        symbol=symbol,
        ex_date=date(2026, 8, 10),
        record_date=date(2026, 8, 7),
        cash_dividend_per_share=Decimal(cash),
        stock_dividend_ratio=Decimal(ratio),
        record_close=Decimal(record_close),
    )


class TestExDividend:
    """除权除息边界测试。"""

    def test_cash_dividend_cost_adjust(self):
        """现金分红后成本价下调（分红视为成本回收），股数不变。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_action(cash="0.50", record_close="10.00"))

        result = adjuster.adjust_position(
            "600000.SH",
            current_qty=Decimal("1000"),
            current_avg_cost=Decimal("10.00"),
        )
        assert result is not None
        # 总成本 10000 - 红利 500 = 9500，股数不变 → 成本 9.50
        assert result.new_position_qty == Decimal("1000")
        assert result.new_avg_cost == Decimal("9.5000")
        assert result.cash_dividend_received == Decimal("500.00")
        # 除息参考价 = 10.00 - 0.50 = 9.50
        assert result.new_prev_close == Decimal("9.50")

    def test_stock_dividend_qty_increase(self):
        """送股后持仓数量增加，成本摊薄。"""
        adjuster = CorporateActionAdjuster()
        adjuster.register_action(_action(ratio="0.1", record_close="10.00"))  # 10送1

        result = adjuster.adjust_position(
            "600000.SH",
            current_qty=Decimal("1000"),
            current_avg_cost=Decimal("10.00"),
        )
        assert result is not None
        # 1000 × 1.1 = 1100 股；总成本 10000 不变 → 10000/1100 = 9.0909
        assert result.new_position_qty == Decimal("1100")
        assert result.new_avg_cost == Decimal("9.0909")
        assert result.cash_dividend_received == Decimal("0")
        # 除权参考价 = 10.00 / 1.1 = 9.09
        assert result.new_prev_close == Decimal("9.09")

    def test_limit_price_recalc_after_ex_div(self):
        """除权后涨跌停价必须基于调整后前收盘价重算，不得沿用原昨收。"""
        adjuster = CorporateActionAdjuster()
        # 现金 0.50 + 10送1：参考价 = (11.00 - 0.50) / 1.1 = 9.55
        adjuster.register_action(_action(cash="0.50", ratio="0.1", record_close="11.00"))

        limit_up, limit_down = adjuster.get_adjusted_limit_prices(
            "600000.SH",
            Decimal("11.00"),
            Decimal("0.10"),
        )
        # 基于新前收 9.55：涨停 9.55×1.1=10.51，跌停 9.55×0.9=8.60
        assert limit_up == Decimal("10.51")
        assert limit_down == Decimal("8.60")
        # 若沿用原昨收 11.00 会是 12.10/9.90——挂单价直接超笼子废单
        assert limit_up != Decimal("12.10")

    def test_backtest_adjusted_vs_live_raw_consistency(self):
        """回测复权价 vs 实盘原始价映射一致性（GAP-011/G-11 防幽灵仓位）。

        不变量：除权日总市值连续——回测后复权价倍数 == 实盘持仓数量倍数，
        且 新持仓市值 + 现金红利 == 原持仓市值。
        （用例数字刻意取整，避免 Decimal 28 位舍入噪声干扰恒等断言）
        """
        adjuster = CorporateActionAdjuster()
        # 每 10 送 2.5（ratio=0.25）：除权参考价 10.00/1.25=8.00 整除
        action = _action(ratio="0.25", record_close="10.00")
        adjuster.register_action(action)

        result = adjuster.adjust_position(
            "600000.SH",
            current_qty=Decimal("1000"),
            current_avg_cost=Decimal("10.00"),
        )
        assert result is not None

        # 回测侧：后复权价倍数 = 登记日收盘价 / 除权参考价（未量化原值）
        hfq_factor = action.record_close / action.ex_dividend_price
        # 实盘侧：持仓数量倍数 = 新股数 / 旧股数
        qty_factor = result.new_position_qty / Decimal("1000")
        # 两倍数必须相等，否则除权日出现"幽灵仓位"（对账差异高发源）
        assert hfq_factor == qty_factor == Decimal("1.25")

        # 含现金分红时市值连续性：新市值 + 现金红利 == 原市值
        # 登记日收盘 12.00、每股派 1.00、10送1：参考价 (12-1)/1.1=10.00 整除
        adjuster2 = CorporateActionAdjuster()
        action2 = _action(cash="1.00", ratio="0.1", record_close="12.00")
        adjuster2.register_action(action2)
        result2 = adjuster2.adjust_position(
            "600000.SH",
            current_qty=Decimal("1000"),
            current_avg_cost=Decimal("12.00"),
        )
        assert result2 is not None
        new_mv = result2.new_position_qty * action2.ex_dividend_price
        old_mv = Decimal("1000") * action2.record_close
        assert new_mv + result2.cash_dividend_received == old_mv
