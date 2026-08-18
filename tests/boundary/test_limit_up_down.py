# -*- coding: utf-8 -*-
"""边界单测：涨跌停处理（GAP-010）

测试涨跌停板下的订单行为：
- 涨停板买单不提交（排不上）
- 跌停板卖单不提交（卖不出）
- ST 股 ±10%（2026-07-06 后与主板统一）
- 创业板/科创板 ±20%
"""
from decimal import Decimal

import pytest

from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker, MiniQmtBrokerError
from zephyr.trading.trading_contracts.execution.order import OrderSide


class TestLimitUpDown:
    """涨跌停边界测试。"""

    def setup_method(self):
        self.broker = MiniQmtBroker()

    def test_limit_up_buy_rejected(self):
        """涨停板买单应拒绝提交（主板 prev_close=10.00，涨停价=11.00）。"""
        with pytest.raises(MiniQmtBrokerError) as exc:
            self.broker._check_price_limit(
                "600000.SH", Decimal("11.00"), OrderSide.BUY, Decimal("10.00")
            )
        assert exc.value.error_code == 50
        # 涨停价下一档（10.99）允许提交
        self.broker._check_price_limit(
            "600000.SH", Decimal("10.99"), OrderSide.BUY, Decimal("10.00")
        )

    def test_limit_down_sell_rejected(self):
        """跌停板卖单应拒绝提交（主板 prev_close=10.00，跌停价=9.00）。"""
        with pytest.raises(MiniQmtBrokerError) as exc:
            self.broker._check_price_limit(
                "600000.SH", Decimal("9.00"), OrderSide.SELL, Decimal("10.00")
            )
        assert exc.value.error_code == 51
        # 跌停价上一档（9.01）允许提交
        self.broker._check_price_limit(
            "600000.SH", Decimal("9.01"), OrderSide.SELL, Decimal("10.00")
        )

    def test_st_stock_10pct_limit(self):
        """ST 股涨跌停 ±10%（2026-07-06 与主板统一，不再 ±5%）。"""
        # prev_close=9.90 → 涨停价=10.89；10.88（+9.9%）允许——若仍按旧 ±5% 会误拒
        self.broker._check_price_limit(
            "600000.SH", Decimal("10.88"), OrderSide.BUY, Decimal("9.90")
        )
        # 10.89（恰 +10% 涨停价）拒绝
        with pytest.raises(MiniQmtBrokerError) as exc:
            self.broker._check_price_limit(
                "600000.SH", Decimal("10.89"), OrderSide.BUY, Decimal("9.90")
            )
        assert exc.value.error_code == 50

    def test_creative_board_20pct_limit(self):
        """创业板/科创板 ±20%（统一 10% 简化实现会误拒 +15% 合法单）。"""
        # 创业板 300xxx：+15% 合法，应允许提交
        self.broker._check_price_limit(
            "300750.SZ", Decimal("115.00"), OrderSide.BUY, Decimal("100.00")
        )
        # 创业板 +20%（涨停价 120.00）拒绝
        with pytest.raises(MiniQmtBrokerError) as exc:
            self.broker._check_price_limit(
                "300750.SZ", Decimal("120.00"), OrderSide.BUY, Decimal("100.00")
            )
        assert exc.value.error_code == 50

        # 科创板 688xxx：+15% 合法，+20% 拒绝
        self.broker._check_price_limit(
            "688981.SH", Decimal("57.50"), OrderSide.BUY, Decimal("50.00")
        )
        with pytest.raises(MiniQmtBrokerError) as exc2:
            self.broker._check_price_limit(
                "688981.SH", Decimal("60.00"), OrderSide.BUY, Decimal("50.00")
            )
        assert exc2.value.error_code == 50
