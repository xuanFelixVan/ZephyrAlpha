# -*- coding: utf-8 -*-
"""边界单测：停牌处理（GAP-010）

测试盘中临停/跨日停牌/复牌场景。
"""
import pytest


class TestSuspension:
    """停牌边界测试。"""

    def test_intraday_halt_skip_order(self):
        """盘中临停票从当日目标移除不报单。"""
        # TODO: 接入 TradingHaltResolver 验证
        pass

    def test_cross_day_halt_release_preoccupation(self):
        """跨日停牌票释放资金预占额度。"""
        pass

    def test_resume_reevaluate(self):
        """复牌后标记 RESUMED_REEVALUATE 重新评估。"""
        pass
