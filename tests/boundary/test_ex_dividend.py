# -*- coding: utf-8 -*-
"""边界单测：除权除息处理（GAP-010）

测试除权除息日的持仓数量/成本价调整。
"""
import pytest
from decimal import Decimal


class TestExDividend:
    """除权除息边界测试。"""

    def test_cash_dividend_cost_adjust(self):
        """现金分红后成本价下调。"""
        # TODO: 接入 CorporateActionAdjuster 验证
        pass

    def test_stock_dividend_qty_increase(self):
        """送股后持仓数量增加。"""
        pass

    def test_limit_price_recalc_after_ex_div(self):
        """除权后涨跌停价重算。"""
        pass

    def test_backtest_adjusted_vs_live_raw_consistency(self):
        """回测复权价 vs 实盘原始价映射一致性（GAP-011）。"""
        pass
