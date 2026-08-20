# [A_test] module_id: MOD-GOV_test_market_cap_tier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.signal_ashare.test_market_cap_tier
# [TESTS] src/zephyr/signal_ashare/market_cap_tier.py
# [TTL] task_bound
"""90 号 Phase2 项（#15 资产分级）：流通市值 6 级分层已知答案 toy 断言。

裁定真源：90_methodology_open_questions.md §15（v2.0.0 裁定④）——
  流通市值 6 级分层采纳为交易准入内的子维度（"市值定调子"）：
  1000亿+ / 300-1000 / 100-300 / 50-100 / 20-50 / <20亿。
"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.market_cap_tier import MarketCapTier, float_mcap_tier


class TestKnownTiers:
    @pytest.mark.parametrize(
        "mcap_yi,expected",
        [
            (1500.0, MarketCapTier.MEGA),  # 1000亿+ 超级大蓝筹
            (1000.0, MarketCapTier.MEGA),  # 边界含下限
            (500.0, MarketCapTier.LARGE),  # 300-1000 行业头部/白马
            (300.0, MarketCapTier.LARGE),
            (200.0, MarketCapTier.MID),  # 100-300 成长股/二线龙头
            (100.0, MarketCapTier.MID),
            (75.0, MarketCapTier.SMALL_MID),  # 50-100 中小盘
            (50.0, MarketCapTier.SMALL_MID),
            (30.0, MarketCapTier.SMALL),  # 20-50 小盘（游资主场）
            (20.0, MarketCapTier.SMALL),
            (10.0, MarketCapTier.MICRO),  # <20亿 超小盘
            (0.5, MarketCapTier.MICRO),
        ],
    )
    def test_tier_assignment(self, mcap_yi, expected):
        assert float_mcap_tier(mcap_yi) is expected

    def test_six_tiers_complete(self):
        """裁定 6 级分层完整。"""
        assert len(MarketCapTier) == 6


class TestValidation:
    def test_negative_raises(self):
        with pytest.raises(ValueError):
            float_mcap_tier(-1.0)

    def test_zero_is_micro(self):
        assert float_mcap_tier(0.0) is MarketCapTier.MICRO
