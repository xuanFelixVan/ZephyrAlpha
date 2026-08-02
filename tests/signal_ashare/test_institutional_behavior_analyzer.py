"""D-SIGNAL-21 主力行为分析引擎单元测试。"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from zephyr.signal_ashare.institutional_behavior_analyzer import (
    BehaviorPhase,
    ConflictWinner,
    InstitutionalBehaviorAnalyzer,
    InstitutionalBehaviorConfig,
    InstitutionalBehaviorInput,
    WashDistributeVerdict,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def analyzer() -> InstitutionalBehaviorAnalyzer:
    return InstitutionalBehaviorAnalyzer()


@pytest.fixture
def config() -> InstitutionalBehaviorConfig:
    return InstitutionalBehaviorConfig()


def make_timestamps(n: int, start_hour: int = 9, start_min: int = 30) -> list[datetime]:
    """生成 n 个时间戳，间隔 5 分钟。"""
    base = datetime(2026, 8, 1, start_hour, start_min)
    return [base + timedelta(minutes=5 * i) for i in range(n)]


def make_input(
    prices: list[float] | None = None,
    volumes: list[float] | None = None,
    large_order_net: list[float] | None = None,
    timestamps: list[datetime] | None = None,
    market_sentiment: float = 50.0,
) -> InstitutionalBehaviorInput:
    n = len(prices or volumes or [])
    if timestamps is None:
        timestamps = make_timestamps(n)
    if prices is None:
        prices = [10.0] * n
    if volumes is None:
        volumes = [1000.0] * n
    if large_order_net is None:
        large_order_net = [0.0] * n
    return InstitutionalBehaviorInput(
        prices=prices,
        volumes=volumes,
        timestamps=timestamps,
        large_order_net=large_order_net,
        market_sentiment_score=market_sentiment,
    )


# ============================================================================
# 维度1: 6阶段识别
# ============================================================================


class TestPhaseIdentification:
    def test_building_phase(self, analyzer: InstitutionalBehaviorAnalyzer):
        """建仓：量温和放大+价微涨+大单正。"""
        n = 10
        prices = [10.0 + i * 0.05 for i in range(n)]  # 微涨
        volumes = [800, 850, 900, 950, 1000, 1000, 1100, 1150, 1200, 1250]  # 温和放大
        lo = [5e5] * n  # 大单正
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.current_phase == BehaviorPhase.BUILDING.value
        assert result.phase_confidence > 50

    def test_washing_phase(self, analyzer: InstitutionalBehaviorAnalyzer):
        """洗盘：缩量+价跌+大单仍正。"""
        n = 10
        prices = [10.0 - i * 0.03 for i in range(n)]  # 小跌
        volumes = [1500, 1400, 1300, 1200, 1100, 1000, 900, 800, 700, 600]  # 缩量
        lo = [2e5] * n  # 大单仍正
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.current_phase == BehaviorPhase.WASHING.value
        assert result.phase_confidence > 50

    def test_pulling_phase(self, analyzer: InstitutionalBehaviorAnalyzer):
        """拉升：放量+大涨+大单强正。"""
        n = 10
        prices = [10.0 + i * 0.6 for i in range(n)]  # 大涨
        volumes = [500, 600, 800, 1000, 1200, 1500, 1800, 2200, 2500, 3000]  # 放量
        lo = [8e5] * n  # 大单强正
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.current_phase == BehaviorPhase.PULLING.value
        assert result.phase_confidence > 50

    def test_distributing_phase(self, analyzer: InstitutionalBehaviorAnalyzer):
        """出货：放量+滞涨+大单负。"""
        n = 10
        prices = [10.0 + i * 0.01 for i in range(n)]  # 滞涨
        volumes = [500, 700, 900, 1100, 1300, 1500, 1700, 1900, 2100, 2300]  # 放量
        lo = [-5e5] * n  # 大单负
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.current_phase == BehaviorPhase.DISTRIBUTING.value
        assert result.phase_confidence > 50

    def test_testing_phase(self, analyzer: InstitutionalBehaviorAnalyzer):
        """试盘：量短暂放大(量比1.3~2.0)+价小涨(1%~3%)。"""
        n = 10
        prices = [10.0 + i * 0.02 for i in range(n)]  # 小涨1.8%
        # 量比≈1.6（近期均值1440 / 前期均值900）——落在试盘区间(1.3~2.0)且超出建仓上限(1.5)
        volumes = [800, 850, 900, 950, 1000, 1400, 1500, 1450, 1400, 1450]
        lo = [1e5] * n
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.current_phase == BehaviorPhase.TESTING.value

    def test_re_washing_phase(self, analyzer: InstitutionalBehaviorAnalyzer):
        """再洗盘：极度缩量+价小跌+大单小幅净流出（主力更深度的试压）。"""
        n = 10
        prices = [10.0 - i * 0.01 for i in range(n)]  # 小跌0.9%
        volumes = [1000, 800, 600, 500, 400, 350, 300, 250, 200, 150]  # 极度缩量
        # 大单小幅净流出——再洗盘阶段主力可能小幅卖出试压（区别于洗盘的大单仍正）
        lo = [-1e5] * n
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.current_phase == BehaviorPhase.RE_WASHING.value

    def test_unknown_phase_low_confidence(self, analyzer: InstitutionalBehaviorAnalyzer):
        """模糊数据 → 未知阶段。"""
        prices = [10.0] * 6  # 完全横盘
        volumes = [1000] * 6  # 量不变
        result = analyzer.analyze(make_input(prices, volumes))
        assert result.current_phase in (
            BehaviorPhase.UNKNOWN.value,
            BehaviorPhase.BUILDING.value,
        )

    def test_phase_confidence_range(self, analyzer: InstitutionalBehaviorAnalyzer):
        prices = [10.0, 10.5, 11.0, 11.5, 12.0]
        volumes = [1000, 1200, 1500, 1800, 2000]
        result = analyzer.analyze(make_input(prices, volumes, [5e5] * 5))
        assert 0.0 <= result.phase_confidence <= 100.0


# ============================================================================
# 维度2: 洗盘vs出货
# ============================================================================


class TestWashVsDistribute:
    def test_wash_detected(self, analyzer: InstitutionalBehaviorAnalyzer):
        """缩量下跌+大单正 → 洗盘。"""
        prices = [10.0 - i * 0.05 for i in range(8)]
        volumes = [2000, 1800, 1500, 1200, 1000, 800, 600, 500]
        lo = [3e5] * 8
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.wash_distribute == WashDistributeVerdict.WASH.value

    def test_distribute_detected(self, analyzer: InstitutionalBehaviorAnalyzer):
        """放量滞涨+大单负 → 出货。"""
        prices = [10.0 + i * 0.005 for i in range(8)]  # 滞涨
        volumes = [500, 800, 1100, 1400, 1700, 2000, 2300, 2600]  # 放量
        lo = [-4e5] * 8
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.wash_distribute == WashDistributeVerdict.DISTRIBUTE.value

    def test_neutral_when_unclear(self, analyzer: InstitutionalBehaviorAnalyzer):
        """数据不明确（量平/价震荡/大单微正）→ 中性判定。"""
        prices = [10.0, 10.1, 10.0, 10.1, 10.0]
        volumes = [1000] * 5
        # 大单小幅净流入——主力微活跃但无明确方向，避免触发出货的 lo<=0 边界
        lo = [1e4] * 5
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.wash_distribute == WashDistributeVerdict.NEUTRAL.value


# ============================================================================
# 维度3: 诱多行为检测
# ============================================================================


class TestBullTrap:
    def test_bull_trap_detected(self, analyzer: InstitutionalBehaviorAnalyzer):
        """先大涨后大跌 → 诱多。"""
        prices = [10.0, 11.0, 12.0, 13.5, 12.0, 10.5, 9.5]  # 先涨35%后跌30%
        volumes = [1000] * 7
        result = analyzer.analyze(make_input(prices, volumes))
        assert result.bull_trap_detected is True
        assert result.bull_trap_confidence > 50

    def test_no_bull_trap_steady_rise(self, analyzer: InstitutionalBehaviorAnalyzer):
        prices = [10.0, 10.5, 11.0, 11.5, 12.0]
        volumes = [1000] * 5
        result = analyzer.analyze(make_input(prices, volumes))
        assert result.bull_trap_detected is False

    def test_no_bull_trap_short_data(self, analyzer: InstitutionalBehaviorAnalyzer):
        result = analyzer.analyze(make_input([10.0, 10.5], [1000, 1100]))
        assert result.bull_trap_detected is False


# ============================================================================
# 维度4: 主力vs游资打架
# ============================================================================


class TestConflict:
    def test_main_force_wins(self, analyzer: InstitutionalBehaviorAnalyzer):
        """大单持续正+波动低 → 主力胜。"""
        prices = [10.0, 10.1, 10.0, 10.1, 10.0, 10.1, 10.0, 10.1]  # 低波动
        volumes = [1000] * 8
        lo = [5e5, 5e5, 5e5, 5e5, 5e5, 5e5, 5e5, 5e5]  # 持续正
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.conflict_winner == ConflictWinner.MAIN_FORCE_WINS.value

    def test_hot_money_wins(self, analyzer: InstitutionalBehaviorAnalyzer):
        """高波动+大单弱 → 游资胜。"""
        prices = [10.0, 11.0, 9.5, 11.5, 9.0, 12.0, 8.5, 12.5]  # 高波动
        volumes = [2000] * 8
        lo = [-1e5, 2e5, -3e5, 1e5, -2e5, 3e5, -1e5, 2e5]  # 大单弱
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.conflict_winner == ConflictWinner.HOT_MONEY_WINS.value

    def test_stalemate(self, analyzer: InstitutionalBehaviorAnalyzer):
        result = analyzer.analyze(make_input([10.0] * 6, [1000] * 6, [0.0] * 6))
        assert result.conflict_winner == ConflictWinner.STALEMATE.value

    def test_no_large_order_data(self, analyzer: InstitutionalBehaviorAnalyzer):
        result = analyzer.analyze(make_input([10.0, 10.1, 10.2], [1000, 1100, 1200]))
        assert result.conflict_winner == ConflictWinner.STALEMATE.value


# ============================================================================
# 维度5: 分时特征
# ============================================================================


class TestIntradayFeatures:
    def test_features_returned(self, analyzer: InstitutionalBehaviorAnalyzer):
        timestamps = make_timestamps(20)
        prices = [10.0 + i * 0.1 for i in range(20)]
        volumes = [1000.0 + i * 50 for i in range(20)]
        result = analyzer.analyze(make_input(prices, volumes, timestamps=timestamps))
        assert "总成交量" in result.intraday_features
        assert "波动率%" in result.intraday_features
        assert "开盘_成交量占比" in result.intraday_features

    def test_degraded_features_on_mismatch(self, analyzer: InstitutionalBehaviorAnalyzer):
        """timestamps 与 volumes 长度不一致 → 降级。"""
        inp = InstitutionalBehaviorInput(
            prices=[10.0, 10.1, 10.2],
            volumes=[1000, 1100, 1200],
            timestamps=make_timestamps(2),  # 不匹配
        )
        result = analyzer.analyze(inp)
        assert result.is_degraded is True


# ============================================================================
# 综合
# ============================================================================


class TestOverall:
    def test_overall_score_range(self, analyzer: InstitutionalBehaviorAnalyzer):
        result = analyzer.analyze(make_input([10.0, 10.5, 11.0], [1000, 1200, 1500], [5e5] * 3))
        assert 0.0 <= result.overall_score <= 100.0

    def test_audit_trail_populated(self, analyzer: InstitutionalBehaviorAnalyzer):
        result = analyzer.analyze(make_input([10.0, 10.5, 11.0, 11.5], [1000, 1200, 1500, 1800], [5e5] * 4))
        assert len(result.audit_trail) >= 4
        dims = [e["dimension"] for e in result.audit_trail]
        assert "phase_identification" in dims
        assert "wash_vs_distribute" in dims
        assert "bull_trap" in dims
        assert "conflict" in dims

    def test_empty_input_degraded(self, analyzer: InstitutionalBehaviorAnalyzer):
        result = analyzer.analyze(InstitutionalBehaviorInput(prices=[], volumes=[], timestamps=[]))
        assert result.is_degraded is True
        assert result.current_phase == BehaviorPhase.UNKNOWN.value

    def test_single_element_degraded(self, analyzer: InstitutionalBehaviorAnalyzer):
        ts = make_timestamps(1)
        result = analyzer.analyze(InstitutionalBehaviorInput(prices=[10.0], volumes=[1000], timestamps=ts))
        assert result.is_degraded is True


# ============================================================================
# 配置可定制性
# ============================================================================


class TestConfigCustomization:
    def test_custom_pulling_threshold(self):
        """自定义拉升阈值——更敏感。"""
        cfg = InstitutionalBehaviorConfig(
            pulling_volume_min=1.3,  # 更低阈值
            pulling_price_rise_min=3.0,
        )
        analyzer = InstitutionalBehaviorAnalyzer(cfg)
        prices = [10.0 + i * 0.4 for i in range(6)]  # 涨约20%
        volumes = [1000, 1100, 1200, 1400, 1600, 1800]  # 量比1.6
        lo = [3e5] * 6
        result = analyzer.analyze(make_input(prices, volumes, lo))
        assert result.current_phase == BehaviorPhase.PULLING.value

    def test_custom_bull_trap_threshold(self):
        """自定义诱多阈值——更严格。"""
        cfg = InstitutionalBehaviorConfig(
            bull_trap_breakout_pct=10.0,  # 需要10%突破才算诱多
            bull_trap_reversal_pct=-5.0,
        )
        analyzer = InstitutionalBehaviorAnalyzer(cfg)
        prices = [10.0, 11.0, 12.0, 13.0, 12.5, 11.5]  # 涨30%后跌8%
        volumes = [1000] * 6
        result = analyzer.analyze(make_input(prices, volumes))
        # 30%>10% 突破, -11.5% < -5% 反转 → 仍检测到
        assert result.bull_trap_detected is True

    def test_frozen_config(self):
        """配置不可变。"""
        cfg = InstitutionalBehaviorConfig()
        with pytest.raises(AttributeError):
            cfg.building_volume_min = 2.0  # type: ignore[misc]
