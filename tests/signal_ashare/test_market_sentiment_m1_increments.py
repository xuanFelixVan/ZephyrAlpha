"""MOD-SIG-025 M1 情绪增量包（44 号 §9.1/§9.2/§9.4 + 92 号 §6.1）单元测试

6 增量已知答案合成用例 + 缺数据全降级 + 既有 7 维零破坏回归 + 灰度链兼容：
  M1-① 涨跌加速度三件套（breadth_vel_5m/breadth_acc_15m/lu_net_rate_5m/break_rate_5m）
        + 拐点信号（修复中/恶化中）+ 20 日 z-score + 快照缺失>2min 置 NaN 不外推
  M1-②a/b 护盘/风格失真检测（维度⑧：触发与不误触 + 权重归一 + distortion×0.7）
  M1-⑤ 量能盘中预测（ŷ_full=cum_vol/p̄(t)；缩量警示/放量确认）
  M1-⑥ 大幅回撤个股数（追涨被埋警示）
  M1-⑦ 昨日破板今表现（炸板判定 high≥limit_up 且 close<limit_up + 承接力分档）
"""

from datetime import datetime, timedelta, timezone

import pytest

from zephyr.signal_ashare.market_sentiment_analyzer import (
    BreadthAccelerationResult,
    BreadthSnapshot,
    BreadthTimeSeries,
    BrokenBoardResult,
    BrokenBoardStock,
    DistortionDetectionResult,
    DrawdownRiskResult,
    FeatureZScoreStats,
    IndexContributionInput,
    IndexPerformanceData,
    LimitUpDownData,
    MarketBreadthData,
    MarketSentimentAnalyzer,
    MarketSentimentConfig,
    MarketSentimentInput,
    MarketSentimentResult,
    SpreadSeriesInput,
    StockIntradayGain,
    VolumeForecastInput,
    VolumeForecastResult,
    YesterdayLimitUpPerformance,
)

_BASE_TS = datetime(2026, 8, 3, 9, 30, tzinfo=timezone.utc)


@pytest.fixture
def analyzer() -> MarketSentimentAnalyzer:
    return MarketSentimentAnalyzer()


def make_input(
    advancing: int = 3000,
    declining: int = 1500,
    flat: int = 500,
    limit_up: int = 60,
    limit_down: int = 5,
    sealed: int = 50,
    attempted: int = 70,
    index_change: float = 0.01,
    **m1_kwargs,
) -> MarketSentimentInput:
    """与既有测试同口径的基础输入，附加 M1 增量 Optional 字段。"""
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
            count=30,
            avg_return_today=0.02,
            positive_ratio=0.6,
        ),
        **m1_kwargs,
    )


def make_time_series(
    adv: list[int],
    lu: list[int],
    sealed: list[int],
    att: list[int],
    total: int = 5000,
    minutes: list[int] | None = None,
    stats: dict | None = None,
) -> BreadthTimeSeries:
    """构造分钟级快照序列；minutes 缺省为 0..n-1 连续分钟。"""
    n = len(adv)
    minute_offsets = minutes if minutes is not None else list(range(n))
    assert len(minute_offsets) == n
    snaps = tuple(
        BreadthSnapshot(
            timestamp=_BASE_TS + timedelta(minutes=minute_offsets[i]),
            advancing_count=adv[i],
            declining_count=1000,
            limit_up_count=lu[i],
            sealed_limit_up_count=sealed[i],
            attempted_limit_up_count=att[i],
        )
        for i in range(n)
    )
    return BreadthTimeSeries(snapshots=snaps, total_count=total, zscore_stats=stats)


def legacy_overall(analyzer: MarketSentimentAnalyzer, inp: MarketSentimentInput) -> float:
    """既有 6 分数加权公式（零破坏回归的锚）。"""
    _, limit_s = analyzer.analyze_limit_activity(inp.limit_data)
    _, profit_s = analyzer.evaluate_profit_effect(inp.breadth)
    _, morale_s = analyzer.evaluate_morale(inp.breadth)
    _, seal_s, _ = analyzer.analyze_seal_rate(inp.limit_data)
    _, breadth_s = analyzer.analyze_breadth(inp.breadth)
    _, risk_s = analyzer.warn_next_day_risk(inp.breadth, inp.index_performance)
    raw = limit_s * 0.20 + profit_s * 0.20 + morale_s * 0.15 + seal_s * 0.15 + breadth_s * 0.15 + risk_s * 0.15
    return max(0.0, min(100.0, raw))


# ------------------------------------------------------------------
# M1-① 涨跌加速度三件套（44 号 §9.1）
# ------------------------------------------------------------------
class TestBreadthAcceleration:
    def test_known_answer_four_features(self, analyzer: MarketSentimentAnalyzer):
        # 21 分钟快照：前 20 分钟平稳，最后一分钟 adv/lu/att/sealed 同步跳变
        ts = make_time_series(
            adv=[3000] * 20 + [3050],
            lu=[50] * 20 + [56],
            sealed=[80] * 20 + [85],
            att=[100] * 20 + [110],
        )
        result = analyzer.analyze(make_input(time_series=ts))
        accel = result.breadth_acceleration
        assert isinstance(accel, BreadthAccelerationResult)
        # breadth_vel_5m = (3050-3000)/5000 = 0.01
        assert accel.breadth_vel_5m == pytest.approx(0.01)
        # breadth_acc_15m = vel(t) - vel(t-15) = 0.01 - 0.0 = 0.01
        assert accel.breadth_acc_15m == pytest.approx(0.01)
        # lu_net_rate_5m = 56-50 = 6
        assert accel.lu_net_rate_5m == pytest.approx(6.0)
        # break_rate_5m = 10 / max(10, 5+10) = 10/15
        assert accel.break_rate_5m == pytest.approx(10.0 / 15.0)
        assert accel.repairing is False
        assert accel.deteriorating is False

    def test_repairing_inflection(self, analyzer: MarketSentimentAnalyzer):
        # lu 先 20 分钟每分钟 -1（净增为负），随后每分钟 +2 → 由负转正且持续 ≥10min
        lu = [100 - i for i in range(20)] + [81 + 2 * (i - 19) for i in range(20, 40)]
        ts = make_time_series(
            adv=[3000] * 40,
            lu=lu,
            sealed=[80] * 40,
            att=[100] * 40,
        )
        result = analyzer.analyze(make_input(time_series=ts))
        assert result.breadth_acceleration.repairing is True
        assert result.breadth_acceleration.lu_net_rate_5m == pytest.approx(10.0)

    def test_repairing_requires_10min_persistence(self, analyzer: MarketSentimentAnalyzer):
        # 同样由负转正但只持续 9 分钟 → 不判修复中
        lu = [100 - i for i in range(20)] + [81 + 2 * (i - 19) for i in range(20, 30)]
        ts = make_time_series(
            adv=[3000] * 30,
            lu=lu,
            sealed=[80] * 30,
            att=[100] * 30,
        )
        result = analyzer.analyze(make_input(time_series=ts))
        assert result.breadth_acceleration.repairing is False

    def test_deteriorating_inflection(self, analyzer: MarketSentimentAnalyzer):
        # 末段 adv 5 分钟下滑 → vel<0；指数涨 → 恶化中；指数跌 → 不判
        adv = [3000] * 16 + [2990, 2980, 2970, 2960, 2950]
        ts = make_time_series(adv=adv, lu=[50] * 21, sealed=[80] * 21, att=[100] * 21)
        up = analyzer.analyze(make_input(time_series=ts, index_change=0.01))
        assert up.breadth_acceleration.breadth_vel_5m == pytest.approx(-0.01)
        assert up.breadth_acceleration.deteriorating is True
        down = analyzer.analyze(make_input(time_series=ts, index_change=-0.01))
        assert down.breadth_acceleration.deteriorating is False

    def test_snapshot_gap_sets_nan_no_extrapolation(self, analyzer: MarketSentimentAnalyzer):
        # 缺失第 13/14/15 分钟（>2min）→ 最后一分钟各特征全部 NaN→None，不外推
        minutes = list(range(13)) + list(range(16, 21))
        ts = make_time_series(
            adv=[3000] * 18,
            lu=[50] * 18,
            sealed=[80] * 18,
            att=[100] * 18,
            minutes=minutes,
        )
        result = analyzer.analyze(make_input(time_series=ts))
        accel = result.breadth_acceleration
        assert accel is not None
        assert accel.breadth_vel_5m is None
        assert accel.breadth_acc_15m is None
        assert accel.lu_net_rate_5m is None
        assert accel.break_rate_5m is None
        assert accel.repairing is False

    def test_zscore_normalization(self, analyzer: MarketSentimentAnalyzer):
        ts = make_time_series(
            adv=[3000] * 20 + [3050],
            lu=[50] * 20 + [56],
            sealed=[80] * 20 + [85],
            att=[100] * 20 + [110],
            stats={
                "breadth_vel_5m": FeatureZScoreStats(mean=0.0, std=0.005),
                "lu_net_rate_5m": FeatureZScoreStats(mean=1.0, std=2.5),
            },
        )
        accel = analyzer.analyze(make_input(time_series=ts)).breadth_acceleration
        assert accel.breadth_vel_5m_z == pytest.approx(2.0)
        assert accel.lu_net_rate_5m_z == pytest.approx(2.0)
        # 未供给统计的特征 z 字段为 None
        assert accel.break_rate_5m_z is None

    def test_time_series_none_skips_whole_group(self, analyzer: MarketSentimentAnalyzer):
        result = analyzer.analyze(make_input(time_series=None))
        assert result.breadth_acceleration is None
        # 整组跳过 → 综合分与既有公式完全一致
        assert result.overall_score == pytest.approx(legacy_overall(analyzer, make_input()))

    def test_insufficient_snapshots_returns_none(self, analyzer: MarketSentimentAnalyzer):
        ts = make_time_series(adv=[3000, 3010], lu=[50, 51], sealed=[80, 80], att=[100, 100])
        assert analyzer.analyze(make_input(time_series=ts)).breadth_acceleration is None


# ------------------------------------------------------------------
# M1-②a/b 护盘/风格失真检测（44 号 §9.2，维度⑧）
# ------------------------------------------------------------------
class TestDistortionDetection:
    def test_guard_illusion_triggers(self, analyzer: MarketSentimentAnalyzer):
        # 固定权重股全涨 3%：Σcontrib=0.245×0.03=0.00735，指数 +1% → guard_ratio=0.735>0.6
        # 上涨占比 1500/5000=0.3 <0.4 → 护盘假象触发
        contrib = IndexContributionInput(
            constituent_returns={code: 0.03 for code in MarketSentimentConfig().guard_weights}
        )
        inp = make_input(advancing=1500, declining=3000, flat=500, index_contrib=contrib)
        result = analyzer.analyze(inp)
        dist = result.distortion
        assert isinstance(dist, DistortionDetectionResult)
        assert dist.guard_ratio == pytest.approx(0.735)
        assert dist.guard_illusion is True
        assert dist.distortion_flag is True
        assert dist.distortion_score == pytest.approx(0.0)
        # 综合分 = (base×0.92 + 0×0.08) × 0.7
        base = legacy_overall(analyzer, make_input(advancing=1500, declining=3000, flat=500))
        assert result.overall_score == pytest.approx(base * 0.92 * 0.7)

    def test_guard_illusion_not_triggered_when_breadth_broad(self, analyzer: MarketSentimentAnalyzer):
        # 同样权重贡献但上涨占比 0.6 ≥0.4 → 不误触
        contrib = IndexContributionInput(
            constituent_returns={code: 0.03 for code in MarketSentimentConfig().guard_weights}
        )
        inp = make_input(index_contrib=contrib)
        result = analyzer.analyze(inp)
        assert result.distortion.guard_illusion is False
        assert result.distortion.distortion_flag is False
        assert result.distortion.distortion_score == pytest.approx(100.0)
        # 维度⑧参与加权但未触发降权：overall = base×0.92 + 100×0.08
        base = legacy_overall(analyzer, make_input())
        assert result.overall_score == pytest.approx(base * 0.92 + 8.0)

    def test_guard_illusion_not_triggered_when_ratio_low(self, analyzer: MarketSentimentAnalyzer):
        # 权重股仅 +1%：guard_ratio=0.245 <0.6 → 不触发；score=100×(1-0.245/0.6)
        contrib = IndexContributionInput(
            constituent_returns={code: 0.01 for code in MarketSentimentConfig().guard_weights}
        )
        inp = make_input(advancing=1500, declining=3000, flat=500, index_contrib=contrib)
        result = analyzer.analyze(inp)
        assert result.distortion.guard_illusion is False
        assert result.distortion.distortion_score == pytest.approx(100.0 * (1.0 - 0.245 / 0.6))

    def test_weight_cover_triggers(self, analyzer: MarketSentimentAnalyzer):
        # 黄白线 spread 末值 0.004，hist(0, 0.002) → z=2>1；且较 30 分钟前 0.001 走扩 → 权重掩护
        spreads = tuple([0.001] * 39 + [0.004])
        inp = make_input(spread_series=SpreadSeriesInput(spreads=spreads, hist_mean=0.0, hist_std=0.002))
        result = analyzer.analyze(inp)
        dist = result.distortion
        assert dist.spread_zscore == pytest.approx(2.0)
        assert dist.spread_widening_30m is True
        assert dist.weight_cover is True
        assert dist.distortion_flag is True
        base = legacy_overall(analyzer, make_input())
        assert result.overall_score == pytest.approx(base * 0.92 * 0.7)

    def test_weight_cover_requires_widening(self, analyzer: MarketSentimentAnalyzer):
        # z=2 但 30 分钟前 spread 更高（未走扩）→ 不触发
        spreads = [0.001] * 40
        spreads[9] = 0.005  # spreads[-31]：30 分钟前更高
        spreads[-1] = 0.004
        inp = make_input(spread_series=SpreadSeriesInput(spreads=tuple(spreads), hist_mean=0.0, hist_std=0.002))
        result = analyzer.analyze(inp)
        assert result.distortion.spread_widening_30m is False
        assert result.distortion.weight_cover is False
        assert result.distortion.distortion_flag is False
        assert result.distortion.distortion_score == pytest.approx(100.0)

    def test_weight_cover_below_sigma_scores_partial(self, analyzer: MarketSentimentAnalyzer):
        # z=0.75<1 且走扩 → 不触发；score=100×(1-0.75)=25
        spreads = tuple([0.001] * 39 + [0.0015])
        inp = make_input(spread_series=SpreadSeriesInput(spreads=spreads, hist_mean=0.0, hist_std=0.002))
        result = analyzer.analyze(inp)
        assert result.distortion.weight_cover is False
        assert result.distortion.distortion_score == pytest.approx(25.0)

    def test_dimension8_absent_renormalizes_to_legacy(self, analyzer: MarketSentimentAnalyzer):
        # 两通道输入均缺 → 维度⑧跳过，权重自动归一回既有 6 分数（行为与现状一致）
        result = analyzer.analyze(make_input())
        assert result.distortion is None
        assert result.overall_score == pytest.approx(legacy_overall(analyzer, make_input()))

    def test_guard_threshold_configurable(self):
        config = MarketSentimentConfig(guard_ratio_threshold=0.8)
        analyzer = MarketSentimentAnalyzer(config)
        contrib = IndexContributionInput(constituent_returns={code: 0.03 for code in config.guard_weights})
        inp = make_input(advancing=1500, declining=3000, flat=500, index_contrib=contrib)
        result = analyzer.analyze(inp)
        # 0.735 < 0.8 自定义阈值 → 不触发
        assert result.distortion.guard_illusion is False


# ------------------------------------------------------------------
# M1-⑤ 量能盘中预测（44 号 §9.4 上半）
# ------------------------------------------------------------------
def make_pct_curve() -> tuple[float, ...]:
    return tuple((i + 1) / 240.0 for i in range(240))


class TestVolumeForecast:
    def test_shrink_warning(self, analyzer: MarketSentimentAnalyzer):
        # 午间 p̄=0.5，cum=4000 → ŷ=8000，20 日均量 10000 → 0.8<0.85 缩量警示
        vol = VolumeForecastInput(
            cum_volume=4000.0,
            minute_index=119,
            pct_curve=make_pct_curve(),
            avg_full_volume_20d=10000.0,
        )
        result = analyzer.analyze(make_input(volume_series=vol))
        vf = result.volume_forecast
        assert isinstance(vf, VolumeForecastResult)
        assert vf.predicted_full_volume == pytest.approx(8000.0)
        assert vf.volume_ratio == pytest.approx(0.8)
        assert vf.shrink_warning is True
        assert vf.volume_confirm is False

    def test_volume_confirm_requires_positive_breadth_vel(self, analyzer: MarketSentimentAnalyzer):
        # cum=7000 → ŷ=14000 → 1.4>1.2；breadth_vel>0 → 放量确认
        vol = VolumeForecastInput(
            cum_volume=7000.0,
            minute_index=119,
            pct_curve=make_pct_curve(),
            avg_full_volume_20d=10000.0,
        )
        ts = make_time_series(
            adv=[3000 + 10 * i for i in range(10)],
            lu=[50] * 10,
            sealed=[80] * 10,
            att=[100] * 10,
        )
        with_ts = analyzer.analyze(make_input(volume_series=vol, time_series=ts))
        assert with_ts.volume_forecast.volume_ratio == pytest.approx(1.4)
        assert with_ts.volume_forecast.volume_confirm is True
        assert with_ts.volume_forecast.shrink_warning is False
        # 缺 time_series（vel 未知）→ 放量确认不成立
        without_ts = analyzer.analyze(make_input(volume_series=vol))
        assert without_ts.volume_forecast.volume_confirm is False

    def test_volume_input_none_skips(self, analyzer: MarketSentimentAnalyzer):
        assert analyzer.analyze(make_input()).volume_forecast is None

    def test_invalid_inputs_skip_gracefully(self, analyzer: MarketSentimentAnalyzer):
        curve = make_pct_curve()
        # 分钟序号越界
        bad_idx = VolumeForecastInput(100.0, 500, curve, 10000.0)
        assert analyzer.analyze(make_input(volume_series=bad_idx)).volume_forecast is None
        # 20 日均量非正
        bad_avg = VolumeForecastInput(100.0, 119, curve, 0.0)
        assert analyzer.analyze(make_input(volume_series=bad_avg)).volume_forecast is None


# ------------------------------------------------------------------
# M1-⑥ 大幅回撤个股数（44 号 §9.4 下半）
# ------------------------------------------------------------------
class TestDrawdownRisk:
    def test_count_and_max_drawdown_no_warning(self, analyzer: MarketSentimentAnalyzer):
        # 7 只：冲高 12% 回落至 5%（回吐 58%≥50%，回撤 7 个百分点）→ 计数够但最大回撤 ≤10
        stocks = tuple(StockIntradayGain(high_gain_pct=12.0, current_gain_pct=5.0) for _ in range(7))
        result = analyzer.analyze(make_input(drawdown_stocks=stocks))
        dd = result.drawdown_risk
        assert isinstance(dd, DrawdownRiskResult)
        assert dd.drawdown_count == 7
        assert dd.max_drawdown_pct == pytest.approx(7.0)
        assert dd.chase_buried_warning is False

    def test_chase_buried_warning(self, analyzer: MarketSentimentAnalyzer):
        # 7 只达标 + 1 只冲高 15% 回落至 4%（回撤 11>10）→ 追涨被埋警示
        stocks = tuple(StockIntradayGain(12.0, 5.0) for _ in range(7)) + (StockIntradayGain(15.0, 4.0),)
        result = analyzer.analyze(make_input(drawdown_stocks=stocks))
        assert result.drawdown_risk.drawdown_count == 8
        assert result.drawdown_risk.max_drawdown_pct == pytest.approx(11.0)
        assert result.drawdown_risk.chase_buried_warning is True

    def test_below_count_threshold_no_warning(self, analyzer: MarketSentimentAnalyzer):
        stocks = tuple(StockIntradayGain(15.0, 4.0) for _ in range(6))
        result = analyzer.analyze(make_input(drawdown_stocks=stocks))
        assert result.drawdown_risk.drawdown_count == 6
        assert result.drawdown_risk.chase_buried_warning is False

    def test_non_qualifying_stocks_excluded(self, analyzer: MarketSentimentAnalyzer):
        stocks = (
            StockIntradayGain(4.9, 1.0),  # 冲高不足 5%
            StockIntradayGain(10.0, 6.0),  # 回吐仅 40%
            StockIntradayGain(10.0, -2.0),  # 回吐 120% 且回撤 12 → 计入
        )
        result = analyzer.analyze(make_input(drawdown_stocks=stocks))
        assert result.drawdown_risk.drawdown_count == 1
        assert result.drawdown_risk.max_drawdown_pct == pytest.approx(12.0)

    def test_drawdown_input_none_skips(self, analyzer: MarketSentimentAnalyzer):
        assert analyzer.analyze(make_input()).drawdown_risk is None


# ------------------------------------------------------------------
# M1-⑦ 昨日破板今表现（44 号 §2 M1-⑦ + 92 号 §1 D11 实证口径）
# ------------------------------------------------------------------
class TestBrokenBoard:
    def test_broken_filter_and_strong_support(self, analyzer: MarketSentimentAnalyzer):
        stocks = (
            # 炸板：high≥limit_up 且 close<limit_up
            BrokenBoardStock("A", 11.0, 10.5, 11.0, 0.04),
            BrokenBoardStock("B", 11.0, 10.8, 11.0, 0.02),
            # 封板（close==limit_up）非炸板 → 排除
            BrokenBoardStock("C", 11.0, 11.0, 11.0, -0.05),
            # 未触板（high<limit_up）→ 排除
            BrokenBoardStock("D", 10.9, 10.6, 11.0, 0.09),
        )
        result = analyzer.analyze(make_input(broken_board_stocks=stocks))
        bb = result.broken_board
        assert isinstance(bb, BrokenBoardResult)
        assert bb.broken_count == 2
        assert bb.avg_return_today == pytest.approx(0.03)
        assert bb.positive_ratio == pytest.approx(1.0)
        assert bb.support_strength == "强"

    def test_weak_support(self, analyzer: MarketSentimentAnalyzer):
        stocks = (
            BrokenBoardStock("A", 11.0, 10.5, 11.0, -0.04),
            BrokenBoardStock("B", 11.0, 10.8, 11.0, -0.02),
        )
        result = analyzer.analyze(make_input(broken_board_stocks=stocks))
        bb = result.broken_board
        assert bb.avg_return_today == pytest.approx(-0.03)
        assert bb.positive_ratio == pytest.approx(0.0)
        assert bb.support_strength == "弱"

    def test_empty_list_gives_no_data_status(self, analyzer: MarketSentimentAnalyzer):
        result = analyzer.analyze(make_input(broken_board_stocks=()))
        bb = result.broken_board
        assert bb is not None
        assert bb.broken_count == 0
        assert bb.support_strength == "无数据"

    def test_broken_board_none_skips(self, analyzer: MarketSentimentAnalyzer):
        assert analyzer.analyze(make_input()).broken_board is None


# ------------------------------------------------------------------
# 缺数据全降级 + 既有 7 维零破坏回归 + 灰度链兼容
# ------------------------------------------------------------------
class TestGracefulDegradationAndRegression:
    def test_all_m1_fields_none_is_legacy_behavior(self, analyzer: MarketSentimentAnalyzer):
        inp = make_input()
        result = analyzer.analyze(inp)
        assert isinstance(result, MarketSentimentResult)
        assert result.breadth_acceleration is None
        assert result.distortion is None
        assert result.volume_forecast is None
        assert result.drawdown_risk is None
        assert result.broken_board is None
        # 既有契约：综合分=6 分数加权、阶段判定不变
        assert result.overall_score == pytest.approx(legacy_overall(analyzer, inp))
        assert 0.0 <= result.overall_score <= 100.0

    def test_grayscale_compatible_with_dimension8_triggered(self, analyzer: MarketSentimentAnalyzer):
        contrib = IndexContributionInput(
            constituent_returns={code: 0.03 for code in MarketSentimentConfig().guard_weights}
        )
        inp = make_input(advancing=1500, declining=3000, flat=500, index_contrib=contrib)
        hard = analyzer.analyze(inp)
        gray = analyzer.analyze_grayscale(inp)
        # 灰度链复用 analyze() 综合分（含维度⑧加权与 ×0.7 降权）
        assert gray.overall_score == pytest.approx(hard.overall_score)
        assert sum(gray.phase_prob.values()) == pytest.approx(1.0)

    def test_overall_stays_in_bounds_when_distortion(self, analyzer: MarketSentimentAnalyzer):
        # 权重股 +10%：guard_ratio=0.245×0.10/0.03≈0.817>0.6，adv 0.1<0.4 → 触发
        contrib = IndexContributionInput(
            constituent_returns={code: 0.10 for code in MarketSentimentConfig().guard_weights}
        )
        inp = make_input(
            advancing=500,
            declining=4000,
            flat=500,
            index_change=0.03,
            index_contrib=contrib,
        )
        result = analyzer.analyze(inp)
        assert result.distortion.distortion_flag is True
        assert 0.0 <= result.overall_score <= 100.0
