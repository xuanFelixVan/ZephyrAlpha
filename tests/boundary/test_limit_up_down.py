# -*- coding: utf-8 -*-
"""边界单测：涨跌停处理（GAP-010）

测试涨跌停板下的订单行为：
- 涨停板买单不提交（排不上）
- 跌停板卖单不提交（卖不出）
- ST 股 ±5%（2026-07-06 后统一 ±10%）
- 创业板/科创板 ±20%
"""
import pytest
from decimal import Decimal


class TestLimitUpDown:
    """涨跌停边界测试。"""

    def test_limit_up_buy_rejected(self):
        """涨停板买单应拒绝提交。"""
        # TODO: 接入 MiniQmtBroker._check_price_limit 验证
        pass

    def test_limit_down_sell_rejected(self):
        """跌停板卖单应拒绝提交。"""
        pass

    def test_st_stock_10pct_limit(self):
        """ST 股涨跌停 ±10%（2026-07-06 统一）。"""
        pass

    def test_creative_board_20pct_limit(self):
        """创业板/科创板 ±20%。"""
        pass
