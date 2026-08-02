"""D-SIGNAL-26 板块分析引擎 单元测试"""

from datetime import datetime

import pytest

from zephyr.signal_ashare.sector_analyzer import (
    MarketStyle,
    SectorAnalysisConfig,
    SectorAnalysisResult,
    SectorAnalyzer,
    SectorData,
    SectorStatus,
    SectorTheme,
)


@pytest.fixture
def analyzer() -> SectorAnalyzer:
    return SectorAnalyzer()


def make_sector(
    name: str = "半导体",
    limit_up: int = 8,
    total: int = 200,
    tier2: int = 3,
    tier3: int = 1,
    index_change: float = 0.04,
    vol_change: float = 0.5,
    consec_up: int = 2,
    consec_vol_up: int = 1,
    leader_change: float = 0.06,
    leader_lagging: bool = False,
    net_inflow: float = 15.0,
    policy: bool = True,
    order: bool = False,
    breakout: bool = True,
) -> SectorData:
    return SectorData(
        sector_name=name,
        limit_up_count=limit_up,
        total_stocks=total,
        tier2_count=tier2,
        tier3_count=tier3,
        sector_index_change_pct=index_change,
        sector_index_volume_change_pct=vol_change,
        consecutive_up_days=consec_up,
        consecutive_volume_up_days=consec_vol_up,
        leader_change_pct=leader_change,
        leader_lagging=leader_lagging,
        net_inflow=net_inflow,
        has_policy_support=policy,
        has_order_landing=order,
        technical_breakout=breakout,
    )


# ------------------------------------------------------------------
# 1. 板块强度评估
# ------------------------------------------------------------------
class TestStrength:
    def test_strong_sector(self, analyzer: SectorAnalyzer):
        data = make_sector(limit_up=10, tier3=2, index_change=0.05)
        status, score = analyzer.evaluate_strength(data)
        assert status == "强"
        assert score >= 70

    def test_weak_sector(self, analyzer: SectorAnalyzer):
        data = make_sector(limit_up=0, tier2=0, tier3=0, index_change=-0.03)
        status, score = analyzer.evaluate_strength(data)
        assert status == "弱"
        assert score < 40

    def test_medium_sector(self, analyzer: SectorAnalyzer):
        data = make_sector(limit_up=3, tier2=1, tier3=0, index_change=0.01)
        status, score = analyzer.evaluate_strength(data)
        assert status == "中"


# ------------------------------------------------------------------
# 2. 延续性判断
# ------------------------------------------------------------------
class TestContinuity:
    def test_trend_theme(self, analyzer: SectorAnalyzer):
        data = make_sector(consec_up=7, net_inflow=20)
        theme, score = analyzer.judge_continuity(data)
        assert theme == SectorTheme.TREND.value
        assert score >= 60

    def test_short_term_theme(self, analyzer: SectorAnalyzer):
        data = make_sector(consec_up=1, net_inflow=3)
        theme, score = analyzer.judge_continuity(data)
        assert theme == SectorTheme.SHORT_TERM.value

    def test_deep_inflow_bonus(self, analyzer: SectorAnalyzer):
        data = make_sector(consec_up=1, net_inflow=15)
        _, score = analyzer.judge_continuity(data)
        data2 = make_sector(consec_up=1, net_inflow=2)
        _, score2 = analyzer.judge_continuity(data2)
        assert score > score2  # 深度介入加分


# ------------------------------------------------------------------
# 3. 轮动预警
# ------------------------------------------------------------------
class TestRotation:
    def test_rotation_warning_triggered(self, analyzer: SectorAnalyzer):
        data = make_sector(consec_up=4, consec_vol_up=3, leader_lagging=True)
        warning, score = analyzer.warn_rotation(data)
        assert warning is True
        assert score >= 60

    def test_no_rotation_warning(self, analyzer: SectorAnalyzer):
        data = make_sector(consec_up=1, consec_vol_up=0, leader_lagging=False)
        warning, score = analyzer.warn_rotation(data)
        assert warning is False
        assert score < 60


# ------------------------------------------------------------------
# 4. 启动条件评估
# ------------------------------------------------------------------
class TestLaunchConditions:
    def test_launch_ready_all_conditions_met(self, analyzer: SectorAnalyzer):
        data = make_sector(breakout=True, policy=True, order=True)
        ready, score = analyzer.evaluate_launch_conditions(data)
        assert ready is True
        assert score >= 75

    def test_launch_not_ready_missing_policy(self, analyzer: SectorAnalyzer):
        data = make_sector(breakout=True, policy=False, order=True)
        ready, _ = analyzer.evaluate_launch_conditions(data)
        assert ready is False


# ------------------------------------------------------------------
# 5. 风格适配
# ------------------------------------------------------------------
class TestMarketStyle:
    def test_trend_style_high_turnover(self, analyzer: SectorAnalyzer):
        assert analyzer.adapt_market_style(2.0) == MarketStyle.TREND.value

    def test_monster_style_low_turnover(self, analyzer: SectorAnalyzer):
        assert analyzer.adapt_market_style(0.5) == MarketStyle.MONSTER.value

    def test_mixed_style(self, analyzer: SectorAnalyzer):
        assert analyzer.adapt_market_style(1.0) == MarketStyle.MIXED.value


# ------------------------------------------------------------------
# 6. 抱团瓦解检测
# ------------------------------------------------------------------
class TestBreakdown:
    def test_breakdown_detected_leader_drop_with_volume(self, analyzer: SectorAnalyzer):
        data = make_sector(leader_change=-0.06, vol_change=2.5)
        assert analyzer.detect_breakdown(data) is True

    def test_breakdown_detected_index_drop(self, analyzer: SectorAnalyzer):
        data = make_sector(index_change=-0.06, leader_change=0.01)
        assert analyzer.detect_breakdown(data) is True

    def test_no_breakdown(self, analyzer: SectorAnalyzer):
        data = make_sector(leader_change=0.03, index_change=0.02, vol_change=0.5)
        assert analyzer.detect_breakdown(data) is False


# ------------------------------------------------------------------
# 综合6维度分析
# ------------------------------------------------------------------
class TestOverallAnalysis:
    def test_full_analysis_returns_result(self, analyzer: SectorAnalyzer):
        result = analyzer.analyze(make_sector(), market_turnover=1.0)
        assert isinstance(result, SectorAnalysisResult)
        assert 0 <= result.overall_score <= 100
        assert result.sector_status in [s.value for s in SectorStatus]

    def test_collapsing_status_on_breakdown(self, analyzer: SectorAnalyzer):
        data = make_sector(leader_change=-0.08, vol_change=3.0, index_change=-0.06)
        result = analyzer.analyze(data)
        assert result.sector_status == SectorStatus.COLLAPSING.value
        assert result.breakdown_signal is True

    def test_accelerating_status_on_strong(self, analyzer: SectorAnalyzer):
        data = make_sector(limit_up=10, tier3=2, index_change=0.05, consec_up=1)
        result = analyzer.analyze(data)
        assert result.sector_status in [
            SectorStatus.ACCELERATING.value,
            SectorStatus.PEAK.value,
        ]


# ------------------------------------------------------------------
# 可配置性
# ------------------------------------------------------------------
class TestConfigurable:
    def test_custom_config_changes_thresholds(self):
        config = SectorAnalysisConfig(strong_limit_up_count=20)
        analyzer = SectorAnalyzer(config)
        data = make_sector(limit_up=10, tier2=0, tier3=0, index_change=0.01)
        status, score = analyzer.evaluate_strength(data)
        # 10 < 20 threshold, no tiers, weak index → not strong
        assert status != "强"

    def test_default_config(self):
        analyzer = SectorAnalyzer()
        assert analyzer._config.strong_limit_up_count == 5
