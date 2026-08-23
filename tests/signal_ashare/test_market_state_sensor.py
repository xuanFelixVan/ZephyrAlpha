"""市场状态传感器 单元测试（10 号 regime spec §2.1 结构探测器，MOD-SIG-036）"""

import pytest

from zephyr.signal_ashare.market_state_sensor import (
    MarketGridState,
    MarketStateConfig,
    MarketStateDataError,
    MarketStateSensor,
    TrendDirection,
    VolatilityLevel,
    classify_market_state,
    classify_trend,
    classify_volatility,
    compute_trend_score,
    compute_vol_percentile,
    sense_market_state,
)


def _uptrend_closes(n: int = 120, start: float = 100.0, daily: float = 0.01) -> list[float]:
    """线性指数增长序列（每日 +1%），用于制造明确上涨趋势。"""
    return [start * (1.0 + daily) ** i for i in range(n)]


def _downtrend_closes(n: int = 120, start: float = 100.0, daily: float = 0.01) -> list[float]:
    return [start * (1.0 - daily) ** i for i in range(n)]


class TestComputeTrendScore:
    def test_flat_closes_score_zero(self):
        assert compute_trend_score([100.0] * 80) == pytest.approx(0.0)

    def test_uptrend_score_positive_bull_zone(self):
        score = compute_trend_score(_uptrend_closes())
        assert score > 0.2

    def test_downtrend_score_negative_bear_zone(self):
        score = compute_trend_score(_downtrend_closes())
        assert score < -0.2

    def test_score_bounded(self):
        assert -1.0 <= compute_trend_score(_uptrend_closes(daily=0.05)) <= 1.0
        assert -1.0 <= compute_trend_score(_downtrend_closes(daily=0.05)) <= 1.0

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            compute_trend_score([100.0] * 30)


class TestComputeVolPercentile:
    def test_increasing_amplitude_percentile_one(self):
        """振幅单调放大 → 当前波动率创窗口新高 → 分位 1.0"""
        returns = [0.0001 * i * (1 if i % 2 == 0 else -1) for i in range(1, 40)]
        pct = compute_vol_percentile(returns, vol_window=5, lookback=20)
        assert pct == pytest.approx(1.0)

    def test_decreasing_amplitude_percentile_low(self):
        """振幅单调收窄 → 当前波动率处于窗口低分位（≤0.2）"""
        returns = [0.5 / i * (1 if i % 2 == 0 else -1) for i in range(1, 40)]
        pct = compute_vol_percentile(returns, vol_window=5, lookback=20)
        assert pct <= 0.2

    def test_percentile_in_unit_interval(self):
        returns = [0.003 * (1 if i % 3 else -1) for i in range(60)]
        pct = compute_vol_percentile(returns, vol_window=10, lookback=30)
        assert 0.0 < pct <= 1.0

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            compute_vol_percentile([0.01, -0.01], vol_window=5)


class TestClassify:
    @pytest.mark.parametrize(
        ("score", "expected"),
        [
            (0.2, TrendDirection.BULL),
            (0.35, TrendDirection.BULL),
            (-0.2, TrendDirection.BEAR),
            (-0.5, TrendDirection.BEAR),
            (0.19, TrendDirection.NEUTRAL),
            (-0.19, TrendDirection.NEUTRAL),
            (0.0, TrendDirection.NEUTRAL),
        ],
    )
    def test_classify_trend(self, score, expected):
        assert classify_trend(score) == expected

    @pytest.mark.parametrize(
        ("pct", "expected"),
        [
            (0.30, VolatilityLevel.LOW),
            (1.0 / 3.0, VolatilityLevel.MEDIUM),  # 边界等值落 MEDIUM
            (0.5, VolatilityLevel.MEDIUM),
            (2.0 / 3.0, VolatilityLevel.MEDIUM),  # 边界等值落 MEDIUM
            (0.7, VolatilityLevel.HIGH),
        ],
    )
    def test_classify_volatility(self, pct, expected):
        assert classify_volatility(pct) == expected

    def test_grid_state_nine_combinations(self):
        assert classify_market_state(TrendDirection.BULL, VolatilityLevel.LOW) == MarketGridState.BULL_LOW
        assert classify_market_state(TrendDirection.BULL, VolatilityLevel.MEDIUM) == MarketGridState.BULL_MEDIUM
        assert classify_market_state(TrendDirection.BULL, VolatilityLevel.HIGH) == MarketGridState.BULL_HIGH
        assert classify_market_state(TrendDirection.NEUTRAL, VolatilityLevel.LOW) == MarketGridState.NEUTRAL_LOW
        assert classify_market_state(TrendDirection.NEUTRAL, VolatilityLevel.MEDIUM) == MarketGridState.NEUTRAL_MEDIUM
        assert classify_market_state(TrendDirection.NEUTRAL, VolatilityLevel.HIGH) == MarketGridState.NEUTRAL_HIGH
        assert classify_market_state(TrendDirection.BEAR, VolatilityLevel.LOW) == MarketGridState.BEAR_LOW
        assert classify_market_state(TrendDirection.BEAR, VolatilityLevel.MEDIUM) == MarketGridState.BEAR_MEDIUM
        assert classify_market_state(TrendDirection.BEAR, VolatilityLevel.HIGH) == MarketGridState.BEAR_HIGH


class TestSenseMarketState:
    def test_uptrend_low_vol_snapshot(self):
        """平稳慢牛（日涨 0.3%，振幅恒定）→ BULL 趋势 + 状态/置信度字段齐备"""
        closes = _uptrend_closes(n=320, daily=0.003)
        snap = sense_market_state(closes)
        assert snap.trend_direction == TrendDirection.BULL
        assert snap.state in (
            MarketGridState.BULL_LOW,
            MarketGridState.BULL_MEDIUM,
            MarketGridState.BULL_HIGH,
        )
        assert -1.0 <= snap.trend_score <= 1.0
        assert 0.0 <= snap.vol_percentile <= 1.0
        assert 0.0 <= snap.confidence <= 1.0
        assert snap.n_days == 320

    def test_downtrend_snapshot_bear(self):
        snap = sense_market_state(_downtrend_closes(n=320, daily=0.004))
        assert snap.trend_direction == TrendDirection.BEAR
        assert snap.state.value.startswith("BEAR")

    def test_flat_snapshot_neutral(self):
        snap = sense_market_state([100.0] * 320)
        assert snap.trend_direction == TrendDirection.NEUTRAL

    def test_custom_config_thresholds(self):
        """自定义阈值生效：bull_min 抬高后同样的弱上涨落入 NEUTRAL"""
        closes = _uptrend_closes(n=320, daily=0.001)
        strict = MarketStateConfig(trend_bull_min=0.9)
        snap = sense_market_state(closes, strict)
        assert snap.trend_direction == TrendDirection.NEUTRAL

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            sense_market_state([100.0] * 50)


class TestMarketStateSensorLoader:
    def test_load_index_closes_with_fake_query(self):
        """DB 隔离：注入假 query_fn 返回 TSV，loader 解析为收盘序列"""
        rows = "\n".join(f"2026-08-{10 + i:02d}\t{100.0 + i}" for i in range(5))
        sensor = MarketStateSensor(query_fn=lambda sql, timeout=30: rows)
        closes = sensor.load_index_closes("000300", "2026-08-01", "2026-08-31")
        assert closes == [100.0, 101.0, 102.0, 103.0, 104.0]

    def test_load_index_closes_empty_raises(self):
        sensor = MarketStateSensor(query_fn=lambda sql, timeout=30: "")
        with pytest.raises(MarketStateDataError):
            sensor.load_index_closes("000300", "2026-08-01", "2026-08-31")

    def test_sense_end_to_end_with_fake_query(self):
        closes = _uptrend_closes(n=320, daily=0.003)
        start = 734000  # 任意基准序数
        rows = "\n".join(f"{start + i}\t{c:.4f}" for i, c in enumerate(closes))
        sensor = MarketStateSensor(query_fn=lambda sql, timeout=30: rows)
        snap = sensor.sense("000300", "2025-01-01", "2026-08-31")
        assert snap.trend_direction == TrendDirection.BULL
        assert snap.n_days == 320
