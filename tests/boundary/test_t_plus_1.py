# -*- coding: utf-8 -*-
"""边界单测：T+1 约束（GAP-010）

测试 A 股 T+1 交割规则下的卖出限制。
"""
import pytest


class TestTPlusOne:
    """T+1 边界测试。"""

    def test_same_day_buy_cannot_sell(self):
        """当日买入的股票当天不能卖出。"""
        # TODO: 接入 MiniQmtBroker._check_t_plus_1 验证
        pass

    def test_next_day_buy_can_sell(self):
        """次日可以卖出前一日买入的股票。"""
        pass

    def test_t0_fund_available_for_buy(self):
        """卖出回笼的资金可立即用于买入（T+0 资金）。"""
        pass
