"""D-SIGNAL-25 市场情绪分析引擎 单元测试"""

from datetime import datetime, timezone

import pytest

from zephyr.signal_ashare.market_sentiment_analyzer import (
    IndexPerformanceData,
    LimitUpDownData,
    MarketBreadthData,
    MarketSentimentAnalyzer,
    MarketSentimentConfig,
    MarketSentimentInput,
    MarketSentimentResult,
    SentimentPhase,
    YesterdayLimitUpPerformance,
)


@pytest.fixture
def analyzer() -> MarketSentimentAnalyzer:
    return MarketSentimentAnalyzer()


@pytest.fixture
def config() -> MarketSentimentConfig:
    return MarketSentimentConfig()


def make_input(
    advancing: int = 3000,
    declining: int = 1500,
    flat: int = 500,
    limit_up: int = 60,
    limit_down: int = 5,
    sealed: int = 50,
    attempted: int = 70,
    index_change: float = 0.01,
    yesterday_lu_count: int = 30,
    yesterday_lu_avg_ret: float = 0.02,
) -> MarketSentimentInput:
    return MarketSentimentInput(
        timestamp=datetime(2026, 8, 3, 15, 0, tzinfo=timezone.utc),
        breadth=MarketBreadthData(
            advancing_count=advancing,
            declining_count=declining,
            flat_count=flat,
            total_count=advancing + declining + flat,
        ),
        limit_data=LimitUpDownData(
            limit_up_count=limit_up,
            limit_down_count=limit_down,
            near_limit_up_count=limit_up + 10,
            sealed_limit_up_count=sealed,
            attempted_limit_up_count=attempted,
        ),
        index_performance=IndexPerformanceData(
            index_name="上证指数",
            index_change_pct=index_change,
        ),
        yesterday_limit_up=YesterdayLimitUpPerformance(
            count=yesterday_lu_count,
            avg_return_today=yesterday_lu_avg_ret,
            positive_ratio=0.6,
        ),
    )


# ------------------------------------------------------------------
# 1. 涨跌家数分析
# ------------------------------------------------------------------
class TestBreadthAnalysis:
    def test_divergence_when_advancing_dominant(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(4000, 500, 500, 5000)
        status, score = analyzer.analyze_breadth(breadth)
        assert status == "二八分化"
        assert score >= 80.0

    def test_divergence_when_declining_dominant(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(500, 4000, 500, 5000)
        status, score = analyzer.analyze_breadth(breadth)
        assert status == "二八分化"
        assert score <= 20.0

    def test_bullish_market(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(3500, 1000, 500, 5000)
        status, score = analyzer.analyze_breadth(breadth)
        assert status == "普涨"
        assert score > 60.0

    def test_balanced_market(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(2500, 2400, 100, 5000)
        status, score = analyzer.analyze_breadth(breadth)
        assert status == "均衡"
        assert 40.0 <= score <= 60.0

    def test_empty_data(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(0, 0, 0, 0)
        status, score = analyzer.analyze_breadth(breadth)
        assert status == "无数据"
        assert score == 50.0


# ------------------------------------------------------------------
# 2. 涨跌停分析
# ------------------------------------------------------------------
class TestLimitActivity:
    def test_zeal_when_many_limit_ups(self, analyzer: MarketSentimentAnalyzer):
        data = LimitUpDownData(80, 2, 90, 70, 85)
        status, score = analyzer.analyze_limit_activity(data)
        assert status == "做多热情"
        assert score >= 70.0

    def test_panic_when_many_limit_downs(self, analyzer: MarketSentimentAnalyzer):
        data = LimitUpDownData(5, 30, 10, 5, 10)
        status, score = analyzer.analyze_limit_activity(data)
        assert status == "恐慌蔓延"
        assert score <= 30.0

    def test_normal_activity(self, analyzer: MarketSentimentAnalyzer):
        data = LimitUpDownData(20, 5, 25, 18, 22)
        status, score = analyzer.analyze_limit_activity(data)
        assert status == "正常"


# ------------------------------------------------------------------
# 3. 赚钱效应
# ------------------------------------------------------------------
class TestProfitEffect:
    def test_strong_profit_effect(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(4000, 800, 200, 5000)
        status, score = analyzer.evaluate_profit_effect(breadth)
        assert status == "强"
        assert score > 60.0

    def test_weak_profit_effect(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(800, 4000, 200, 5000)
        status, score = analyzer.evaluate_profit_effect(breadth)
        assert status == "弱"
        assert score < 40.0


# ------------------------------------------------------------------
# 4. 次日回调风险
# ------------------------------------------------------------------
class TestNextDayRisk:
    def test_high_risk_when_index_up_but_stocks_down(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(1500, 3500, 0, 5000)
        index = IndexPerformanceData("上证", 0.02)
        status, score = analyzer.warn_next_day_risk(breadth, index)
        assert status == "高风险"
        assert score >= 80.0

    def test_low_risk_normal_market(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(3500, 1000, 500, 5000)
        index = IndexPerformanceData("上证", 0.01)
        status, score = analyzer.warn_next_day_risk(breadth, index)
        assert status == "低风险"


# ------------------------------------------------------------------
# 5. 市场士气
# ------------------------------------------------------------------
class TestMorale:
    def test_high_morale(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(3500, 1000, 500, 5000)
        status, score = analyzer.evaluate_morale(breadth)
        assert status == "高涨"
        assert score > 60.0

    def test_low_morale(self, analyzer: MarketSentimentAnalyzer):
        breadth = MarketBreadthData(1000, 3500, 500, 5000)
        status, score = analyzer.evaluate_morale(breadth)
        assert status == "低迷"
        assert score < 40.0


# ------------------------------------------------------------------
# 6. 封板率分析
# ------------------------------------------------------------------
class TestSealRate:
    def test_good_seal_rate(self, analyzer: MarketSentimentAnalyzer):
        data = LimitUpDownData(60, 2, 70, 55, 65)
        status, score, rate = analyzer.analyze_seal_rate(data)
        assert status == "好"
        assert rate >= 0.7

    def test_bad_seal_rate(self, analyzer: MarketSentimentAnalyzer):
        data = LimitUpDownData(60, 2, 70, 20, 65)
        status, score, rate = analyzer.analyze_seal_rate(data)
        assert status == "差"
        assert rate <= 0.4

    def test_no_attempted_limit_ups(self, analyzer: MarketSentimentAnalyzer):
        data = LimitUpDownData(0, 0, 0, 0, 0)
        status, score, rate = analyzer.analyze_seal_rate(data)
        assert status == "无数据"


# ------------------------------------------------------------------
# 7. 昨日涨停表现
# ------------------------------------------------------------------
class TestYesterdayLimitUp:
    def test_good_performance(self, analyzer: MarketSentimentAnalyzer):
        lu = YesterdayLimitUpPerformance(30, 0.05, 0.7)
        assert analyzer.track_yesterday_limit_up(lu) == "好"

    def test_bad_performance(self, analyzer: MarketSentimentAnalyzer):
        lu = YesterdayLimitUpPerformance(30, -0.03, 0.3)
        assert analyzer.track_yesterday_limit_up(lu) == "差"

    def test_no_data(self, analyzer: MarketSentimentAnalyzer):
        assert analyzer.track_yesterday_limit_up(None) == "无数据"


# ------------------------------------------------------------------
# 综合7维度分析
# ------------------------------------------------------------------
class TestOverallAnalysis:
    def test_full_analysis_returns_result(self, analyzer: MarketSentimentAnalyzer):
        result = analyzer.analyze(make_input())
        assert isinstance(result, MarketSentimentResult)
        assert 0 <= result.overall_score <= 100
        assert result.sentiment_phase in [p.value for p in SentimentPhase]

    def test_bullish_market_high_score(self, analyzer: MarketSentimentAnalyzer):
        result = analyzer.analyze(make_input(
            advancing=4000, declining=500, flat=500,
            limit_up=80, limit_down=2, sealed=75, attempted=85,
        ))
        assert result.overall_score > 60

    def test_bearish_market_low_score(self, analyzer: MarketSentimentAnalyzer):
        result = analyzer.analyze(make_input(
            advancing=500, declining=4000, flat=500,
            limit_up=2, limit_down=30, sealed=2, attempted=5,
            index_change=-0.02,
        ))
        assert result.overall_score < 40


# ------------------------------------------------------------------
# 可配置性
# ------------------------------------------------------------------
class TestConfigurable:
    def test_custom_config_changes_thresholds(self):
        config = MarketSentimentConfig(limit_up_zeal_threshold=100)
        analyzer = MarketSentimentAnalyzer(config)
        data = LimitUpDownData(80, 2, 90, 70, 85)
        status, _ = analyzer.analyze_limit_activity(data)
        # 80 < 100 threshold → not 做多热情
        assert status != "做多热情"

    def test_default_config_used_when_none(self):
        analyzer = MarketSentimentAnalyzer()
        assert analyzer._config.limit_up_zeal_threshold == 50
