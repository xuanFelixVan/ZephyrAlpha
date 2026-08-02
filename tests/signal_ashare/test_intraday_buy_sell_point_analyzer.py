"""D-SIGNAL-24 日内买卖点引擎单元测试。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.intraday_buy_sell_point_analyzer import (
    BuyPointType,
    ConfirmationType,
    IntradayBuySellAnalyzer,
    IntradayBuySellConfig,
    IntradayBuySellInput,
    SellPointType,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def analyzer() -> IntradayBuySellAnalyzer:
    return IntradayBuySellAnalyzer()


@pytest.fixture
def config() -> IntradayBuySellConfig:
    return IntradayBuySellConfig()


def make_input(**kwargs) -> IntradayBuySellInput:
    """构造日内买卖点输入——提供合理默认值（3重确认默认全过）。"""
    defaults = dict(
        symbol="600000",
        current_price=10.0,
        resistance_price=0.0,
        volume_ratio=1.0,
        ma_price=0.0,
        pullback_volume_ratio=1.0,
        price_change_pct=0.0,
        capital_net_inflow=0.0,
        open_pct=0.0,
        auction_volume_ratio=0.0,
        prev_bad_board=False,
        prev_intraday_high=0.0,
        intraday_volume_ratio=1.0,
        opened_board=False,
        re_seal_minutes=0,
        seal_order_amount=0.0,
        float_market_cap=0.0,
        target_price=0.0,
        below_ma_pct=0.0,
        initial_seal_amount=0.0,
        current_seal_amount=0.0,
        is_limit_up=False,
        prev_sector_rank=1,
        current_sector_rank=1,
        open_board_count=0,
        consecutive_limit_ups=0,
        news_realized=False,
        # 3重确认默认全过
        market_sentiment_score=60.0,
        sector_strength_score=70.0,
        capital_flow_inflow=100.0,
    )
    defaults.update(kwargs)
    return IntradayBuySellInput(**defaults)


# ============================================================================
# 维度1: 6种买入模式
# ============================================================================


class TestBuyPoints:
    def test_breakout_buy(self, analyzer: IntradayBuySellAnalyzer):
        """突破买点：价格突破阻力位+放量。"""
        result = analyzer.analyze(
            make_input(
                current_price=10.5,
                resistance_price=10.0,
                volume_ratio=2.0,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.BREAKOUT.value in buy_types
        sig = next(s for s in result.buy_signals if s.point_type == BuyPointType.BREAKOUT.value)
        assert sig.confidence > 50

    def test_breakout_no_volume(self, analyzer: IntradayBuySellAnalyzer):
        """突破但无量 → 不触发。"""
        result = analyzer.analyze(
            make_input(
                current_price=10.5,
                resistance_price=10.0,
                volume_ratio=1.0,  # 量比不足
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.BREAKOUT.value not in buy_types

    def test_pullback_buy(self, analyzer: IntradayBuySellAnalyzer):
        """回调买点：回踩均线+缩量。"""
        result = analyzer.analyze(
            make_input(
                current_price=10.2,
                ma_price=10.0,
                pullback_volume_ratio=0.5,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.PULLBACK.value in buy_types

    def test_pullback_too_far(self, analyzer: IntradayBuySellAnalyzer):
        """偏离均线太远 → 不触发。"""
        result = analyzer.analyze(
            make_input(
                current_price=11.0,
                ma_price=10.0,
                pullback_volume_ratio=0.5,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.PULLBACK.value not in buy_types

    def test_contrarian_capital_buy(self, analyzer: IntradayBuySellAnalyzer):
        """逆向资金买点：价跌+资金流入。"""
        result = analyzer.analyze(
            make_input(
                current_price=9.8,
                price_change_pct=-3.0,
                capital_net_inflow=500.0,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.CONTRARIAN_CAPITAL.value in buy_types

    def test_contrarian_no_capital(self, analyzer: IntradayBuySellAnalyzer):
        """价跌但资金流出 → 不触发。"""
        result = analyzer.analyze(
            make_input(
                current_price=9.8,
                price_change_pct=-3.0,
                capital_net_inflow=-100.0,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.CONTRARIAN_CAPITAL.value not in buy_types

    def test_auction_weak_to_strong(self, analyzer: IntradayBuySellAnalyzer):
        """竞价弱转强：前日烂板+高开+竞价量放大。"""
        result = analyzer.analyze(
            make_input(
                prev_bad_board=True,
                open_pct=5.0,
                auction_volume_ratio=8.0,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.AUCTION_WEAK_TO_STRONG.value in buy_types

    def test_auction_no_prev_bad_board(self, analyzer: IntradayBuySellAnalyzer):
        """前日非烂板 → 不触发。"""
        result = analyzer.analyze(
            make_input(
                prev_bad_board=False,
                open_pct=5.0,
                auction_volume_ratio=8.0,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.AUCTION_WEAK_TO_STRONG.value not in buy_types

    def test_intraday_breakout(self, analyzer: IntradayBuySellAnalyzer):
        """分时突破：突破前高+放量。"""
        result = analyzer.analyze(
            make_input(
                current_price=10.2,
                prev_intraday_high=10.0,
                intraday_volume_ratio=2.5,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.INTRADAY_BREAKOUT.value in buy_types

    def test_re_seal_board(self, analyzer: IntradayBuySellAnalyzer):
        """回封打板：开板后快速回封+封流比够。"""
        result = analyzer.analyze(
            make_input(
                current_price=11.0,
                opened_board=True,
                re_seal_minutes=5,
                seal_order_amount=5000.0,
                float_market_cap=50.0,  # 封流比 5000/(50*10000)=0.01=1%? 需>=5%
            )
        )
        # 封流比 = 5000/(50*10000) = 0.01 = 1%，阈值5% → 不触发
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.RE_SEAL_BOARD.value not in buy_types

    def test_re_seal_board_strong_seal(self, analyzer: IntradayBuySellAnalyzer):
        """回封打板：封流比>=5% → 触发。"""
        result = analyzer.analyze(
            make_input(
                current_price=11.0,
                opened_board=True,
                re_seal_minutes=5,
                seal_order_amount=30000.0,  # 封流比 30000/500000=6%
                float_market_cap=50.0,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.RE_SEAL_BOARD.value in buy_types

    def test_no_buy_signals(self, analyzer: IntradayBuySellAnalyzer):
        """无任何买入条件 → 空列表。"""
        result = analyzer.analyze(make_input())
        assert result.buy_signals == []


# ============================================================================
# 维度2: 6种卖出模式
# ============================================================================


class TestSellPoints:
    def test_target_price_sell(self, analyzer: IntradayBuySellAnalyzer):
        """目标价位止盈：达到目标价98%。"""
        result = analyzer.analyze(
            make_input(
                current_price=9.9,
                target_price=10.0,
            )
        )
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.TARGET_PRICE.value in sell_types

    def test_target_price_not_reached(self, analyzer: IntradayBuySellAnalyzer):
        """未达目标价 → 不触发。"""
        result = analyzer.analyze(
            make_input(
                current_price=9.0,
                target_price=10.0,
            )
        )
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.TARGET_PRICE.value not in sell_types

    def test_trend_break_sell(self, analyzer: IntradayBuySellAnalyzer):
        """趋势破位止盈：跌破均线1%。"""
        result = analyzer.analyze(
            make_input(below_ma_pct=-2.0),
        )
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.TREND_BREAK.value in sell_types

    def test_trend_break_not_triggered(self, analyzer: IntradayBuySellAnalyzer):
        """未跌破 → 不触发。"""
        result = analyzer.analyze(
            make_input(below_ma_pct=1.0),
        )
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.TREND_BREAK.value not in sell_types

    def test_news_realized_sell(self, analyzer: IntradayBuySellAnalyzer):
        """利好兑现止盈。"""
        result = analyzer.analyze(make_input(news_realized=True))
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.NEWS_REALIZED.value in sell_types

    def test_seal_decrease_sell(self, analyzer: IntradayBuySellAnalyzer):
        """封单减少止盈：封单缩减到50%以下。"""
        result = analyzer.analyze(
            make_input(
                is_limit_up=True,
                initial_seal_amount=10000.0,
                current_seal_amount=3000.0,  # 30%
            )
        )
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.SEAL_DECREASE.value in sell_types

    def test_seal_decrease_not_triggered(self, analyzer: IntradayBuySellAnalyzer):
        """封单缩减不够 → 不触发。"""
        result = analyzer.analyze(
            make_input(
                is_limit_up=True,
                initial_seal_amount=10000.0,
                current_seal_amount=8000.0,  # 80%
            )
        )
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.SEAL_DECREASE.value not in sell_types

    def test_leader_loss_sell(self, analyzer: IntradayBuySellAnalyzer):
        """龙头丧失止盈：排名下降3+。"""
        result = analyzer.analyze(make_input(prev_sector_rank=1, current_sector_rank=5))
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.LEADER_LOSS.value in sell_types

    def test_strong_divergence_sell(self, analyzer: IntradayBuySellAnalyzer):
        """强分歧止盈：连板+开板>=2次。"""
        result = analyzer.analyze(make_input(consecutive_limit_ups=3, open_board_count=2))
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.STRONG_DIVERGENCE.value in sell_types

    def test_strong_divergence_no_limit_up(self, analyzer: IntradayBuySellAnalyzer):
        """无连板 → 不触发。"""
        result = analyzer.analyze(make_input(consecutive_limit_ups=0, open_board_count=2))
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.STRONG_DIVERGENCE.value not in sell_types

    def test_no_sell_signals(self, analyzer: IntradayBuySellAnalyzer):
        """无任何卖出条件 → 空列表。"""
        result = analyzer.analyze(make_input())
        assert result.sell_signals == []


# ============================================================================
# 维度3: 3重确认
# ============================================================================


class TestConfirmations:
    def test_all_pass(self, analyzer: IntradayBuySellAnalyzer):
        """3重确认全过。"""
        result = analyzer.analyze(
            make_input(
                market_sentiment_score=60.0,
                sector_strength_score=70.0,
                capital_flow_inflow=100.0,
            )
        )
        assert result.all_confirmations_passed is True
        assert len(result.confirmations) == 3
        assert all(c.passed for c in result.confirmations)

    def test_market_fails(self, analyzer: IntradayBuySellAnalyzer):
        """大盘情绪不足 → 确认未全过。"""
        result = analyzer.analyze(
            make_input(market_sentiment_score=30.0)  # < 40
        )
        assert result.all_confirmations_passed is False
        market = next(
            c for c in result.confirmations if c.confirmation_type == ConfirmationType.MARKET_ENVIRONMENT.value
        )
        assert market.passed is False

    def test_sector_fails(self, analyzer: IntradayBuySellAnalyzer):
        """板块强度不足 → 确认未全过。"""
        result = analyzer.analyze(
            make_input(sector_strength_score=50.0)  # < 60
        )
        assert result.all_confirmations_passed is False

    def test_capital_fails(self, analyzer: IntradayBuySellAnalyzer):
        """资金流出 → 确认未全过。"""
        result = analyzer.analyze(make_input(capital_flow_inflow=-50.0))
        assert result.all_confirmations_passed is False
        capital = next(c for c in result.confirmations if c.confirmation_type == ConfirmationType.CAPITAL_FLOW.value)
        assert capital.passed is False


# ============================================================================
# 综合建议
# ============================================================================


class TestRecommendation:
    def test_buy_with_confirmations(self, analyzer: IntradayBuySellAnalyzer):
        """买入信号+3重确认全过 → buy。"""
        result = analyzer.analyze(
            make_input(
                current_price=10.5,
                resistance_price=10.0,
                volume_ratio=2.0,
                market_sentiment_score=60.0,
                sector_strength_score=70.0,
                capital_flow_inflow=100.0,
            )
        )
        assert result.recommendation == "buy"
        assert result.overall_confidence > 50

    def test_buy_blocked_by_confirmation(self, analyzer: IntradayBuySellAnalyzer):
        """买入信号但确认未过 → wait。"""
        result = analyzer.analyze(
            make_input(
                current_price=10.5,
                resistance_price=10.0,
                volume_ratio=2.0,
                market_sentiment_score=30.0,  # 大盘不足
            )
        )
        assert result.recommendation == "wait"

    def test_sell_overrides_buy(self, analyzer: IntradayBuySellAnalyzer):
        """卖出信号>=60且>=买入 → sell（风控优先）。"""
        result = analyzer.analyze(
            make_input(
                current_price=9.9,
                resistance_price=10.0,
                volume_ratio=2.0,
                target_price=10.0,  # 触发目标价止盈
            )
        )
        # current_price=9.9 既触发目标价止盈(9.9>=9.8)又触发突破(resistance=10.0)?
        # 突破需要 current > resistance，9.9 < 10.0 不触发突破
        # 目标价 9.9/10.0=99% >= 98% → 触发
        assert result.recommendation == "sell"

    def test_hold_when_no_signals(self, analyzer: IntradayBuySellAnalyzer):
        """无买卖信号 → hold。"""
        result = analyzer.analyze(make_input())
        assert result.recommendation == "hold"


# ============================================================================
# 综合
# ============================================================================


class TestOverall:
    def test_audit_trail_populated(self, analyzer: IntradayBuySellAnalyzer):
        result = analyzer.analyze(make_input())
        assert len(result.audit_trail) >= 3
        dims = [e["dimension"] for e in result.audit_trail]
        assert "buy_points" in dims
        assert "sell_points" in dims
        assert "confirmations" in dims

    def test_empty_symbol_degraded(self, analyzer: IntradayBuySellAnalyzer):
        result = analyzer.analyze(make_input(symbol=""))
        assert result.is_degraded is True
        assert result.recommendation == "wait"

    def test_negative_price_degraded(self, analyzer: IntradayBuySellAnalyzer):
        result = analyzer.analyze(make_input(current_price=-5.0))
        assert result.is_degraded is True

    def test_symbol_preserved(self, analyzer: IntradayBuySellAnalyzer):
        result = analyzer.analyze(make_input(symbol="000001"))
        assert result.symbol == "000001"

    def test_overall_confidence_range(self, analyzer: IntradayBuySellAnalyzer):
        result = analyzer.analyze(make_input())
        assert 0.0 <= result.overall_confidence <= 100.0


# ============================================================================
# 配置可定制性
# ============================================================================


class TestConfigCustomization:
    def test_custom_breakout_threshold(self):
        """自定义突破阈值——更宽松。"""
        cfg = IntradayBuySellConfig(
            breakout_volume_ratio_min=1.0,
            breakout_price_pct_min=1.0,
        )
        analyzer = IntradayBuySellAnalyzer(cfg)
        result = analyzer.analyze(
            make_input(
                current_price=10.2,
                resistance_price=10.0,  # 突破2%
                volume_ratio=1.2,
            )
        )
        buy_types = [s.point_type for s in result.buy_signals]
        assert BuyPointType.BREAKOUT.value in buy_types

    def test_custom_market_threshold(self):
        """自定义大盘情绪阈值——更严格。"""
        cfg = IntradayBuySellConfig(market_sentiment_min=70.0)
        analyzer = IntradayBuySellAnalyzer(cfg)
        result = analyzer.analyze(
            make_input(
                market_sentiment_score=60.0,  # 默认阈值40通过，但70不通过
                sector_strength_score=80.0,
                capital_flow_inflow=100.0,
            )
        )
        assert result.all_confirmations_passed is False

    def test_custom_target_price_reach(self):
        """自定义目标价达到阈值——更早止盈。"""
        cfg = IntradayBuySellConfig(target_price_reach_pct=90.0)
        analyzer = IntradayBuySellAnalyzer(cfg)
        result = analyzer.analyze(
            make_input(
                current_price=9.5,
                target_price=10.0,  # 95% >= 90% → 触发
            )
        )
        sell_types = [s.point_type for s in result.sell_signals]
        assert SellPointType.TARGET_PRICE.value in sell_types

    def test_frozen_config(self):
        """配置不可变。"""
        cfg = IntradayBuySellConfig()
        with pytest.raises(AttributeError):
            cfg.breakout_volume_ratio_min = 3.0  # type: ignore[misc]
