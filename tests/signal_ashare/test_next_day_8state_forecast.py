"""次日 8 状态预测 单元测试（交易决策架构 9.2 八态模型，MOD-SIG-037）"""

import pytest

from zephyr.signal_ashare.next_day_8state_forecast import (
    DailyBar,
    ForecastConfig,
    NextDay8StateForecaster,
    NextDayForecastDataError,
    NextDayState,
    build_state_series,
    classify_daily_state,
    estimate_transition_matrix,
    forecast_next_day,
    stationary_distribution,
)

S = NextDayState  # 简写


class TestClassifyDailyState:
    """8 态分类（前收 100 基准；默认阈值：平开 ±0.5% / 收平 ±0.3% / 剧烈震荡振幅 ≥3%）"""

    def test_gap_up_up(self):
        assert classify_daily_state(DailyBar(101.0, 102.0, 100.5, 101.8), 100.0) == S.GAP_UP_UP

    def test_gap_up_down(self):
        assert classify_daily_state(DailyBar(101.0, 101.5, 100.4, 100.6), 100.0) == S.GAP_UP_DOWN

    def test_gap_down_up(self):
        assert classify_daily_state(DailyBar(99.0, 100.0, 98.8, 99.6), 100.0) == S.GAP_DOWN_UP

    def test_gap_down_down(self):
        assert classify_daily_state(DailyBar(99.0, 99.5, 98.2, 98.5), 100.0) == S.GAP_DOWN_DOWN

    def test_flat_up(self):
        assert classify_daily_state(DailyBar(100.2, 101.0, 100.0, 100.8), 100.0) == S.FLAT_UP

    def test_flat_down(self):
        assert classify_daily_state(DailyBar(100.2, 100.4, 99.3, 99.5), 100.0) == S.FLAT_DOWN

    def test_flat_close(self):
        """|收盘涨跌| ≤ 0.3% → 震荡收平（覆盖开收方向）"""
        assert classify_daily_state(DailyBar(100.2, 100.6, 99.8, 100.1), 100.0) == S.FLAT_CLOSE
        assert classify_daily_state(DailyBar(101.0, 101.4, 99.9, 100.05), 100.0) == S.FLAT_CLOSE

    def test_violent_overrides_grid(self):
        """振幅 ≥3% → 剧烈震荡（优先级最高，覆盖高开高走网格）"""
        assert classify_daily_state(DailyBar(101.0, 104.0, 97.0, 102.0), 100.0) == S.VIOLENT

    def test_violent_boundary_and_gap_boundary(self):
        """振幅恰好 3% 触发剧烈震荡；缺口恰好 ±0.5% 算平开"""
        assert classify_daily_state(DailyBar(100.0, 101.6, 98.6, 101.0), 100.0) == S.VIOLENT  # amp=3.0%
        assert classify_daily_state(DailyBar(100.5, 101.2, 100.3, 101.0), 100.0) == S.FLAT_UP  # gap=+0.5%

    def test_invalid_prev_close_raises(self):
        with pytest.raises(ValueError):
            classify_daily_state(DailyBar(100.0, 101.0, 99.0, 100.5), 0.0)


class TestBuildStateSeries:
    def test_series_length_and_values(self):
        bars = [
            DailyBar(100.0, 101.0, 99.5, 100.5),  # 首日无前收，跳过
            DailyBar(101.2, 102.0, 100.5, 101.8),  # 缺口 +0.70% → GAP_UP_UP
            DailyBar(99.0, 99.5, 98.2, 98.5),  # 缺口 -2.75% → GAP_DOWN_DOWN
        ]
        states = build_state_series(bars)
        assert states == [S.GAP_UP_UP, S.GAP_DOWN_DOWN]

    def test_too_few_bars_returns_empty(self):
        assert build_state_series([DailyBar(100.0, 101.0, 99.0, 100.5)]) == []


class TestEstimateTransitionMatrix:
    def test_laplace_smoothing_row_values(self):
        """[A,A,B,B] + laplace=1：A 行 = [2,2,1,1,1,1,1,1]/10"""
        matrix = estimate_transition_matrix([S.FLAT_UP, S.FLAT_UP, S.FLAT_DOWN, S.FLAT_DOWN])
        i_a, i_b = list(S).index(S.FLAT_UP), list(S).index(S.FLAT_DOWN)
        row_a = matrix[i_a]
        assert row_a[i_a] == pytest.approx(0.2)
        assert row_a[i_b] == pytest.approx(0.2)
        assert sum(row_a) == pytest.approx(1.0)

    def test_no_smoothing_exact_counts(self):
        matrix = estimate_transition_matrix(
            [S.FLAT_UP, S.FLAT_UP, S.FLAT_DOWN, S.FLAT_DOWN], laplace_alpha=0.0
        )
        i_a, i_b = list(S).index(S.FLAT_UP), list(S).index(S.FLAT_DOWN)
        assert matrix[i_a][i_a] == pytest.approx(0.5)
        assert matrix[i_a][i_b] == pytest.approx(0.5)
        assert matrix[i_b][i_b] == pytest.approx(1.0)

    def test_all_rows_normalized_with_smoothing(self):
        states = [list(S)[i % 8] for i in range(50)]
        matrix = estimate_transition_matrix(states)
        for row in matrix:
            assert sum(row) == pytest.approx(1.0)


class TestStationaryDistribution:
    def test_uniform_matrix_uniform_stationary(self):
        matrix = [[1.0 / 8.0] * 8 for _ in range(8)]
        stat = stationary_distribution(matrix)
        assert stat == pytest.approx([1.0 / 8.0] * 8)

    def test_two_state_embedded_stationary(self):
        """嵌入 2 态链 [[0.9,0.1],[0.5,0.5]] → 平稳分布 (5/6, 1/6)"""
        matrix = [[0.0] * 8 for _ in range(8)]
        matrix[0][0], matrix[0][1] = 0.9, 0.1
        matrix[1][0], matrix[1][1] = 0.5, 0.5
        stat = stationary_distribution(matrix)
        assert stat[0] == pytest.approx(5.0 / 6.0, abs=1e-4)
        assert stat[1] == pytest.approx(1.0 / 6.0, abs=1e-4)
        assert sum(stat) == pytest.approx(1.0)


class TestForecastNextDay:
    def test_probabilities_sum_to_one(self):
        bars = _make_bars(60)
        fc = forecast_next_day(build_state_series(bars))
        assert sum(fc.probabilities.values()) == pytest.approx(1.0)
        assert len(fc.probabilities) == 8
        assert fc.top_state == max(fc.probabilities, key=fc.probabilities.get)
        assert fc.top_probability == fc.probabilities[fc.top_state]
        assert 0.0 <= fc.confidence <= 1.0

    def test_zero_blend_returns_empirical_row(self):
        """stationary_blend=0 → 预测分布 = 经验转移行（含 laplace 平滑）"""
        states = [S.FLAT_UP, S.FLAT_UP, S.FLAT_DOWN]
        cfg = ForecastConfig(stationary_blend=0.0, laplace_alpha=1.0, min_history=2)
        fc = forecast_next_day(states, cfg)
        # 当前态 FLAT_DOWN，历史无 FLAT_DOWN 出发转移 → 行全平滑 1/8
        assert fc.current_state == S.FLAT_DOWN
        assert fc.probabilities[S.FLAT_UP] == pytest.approx(1.0 / 8.0)

    def test_full_blend_returns_stationary(self):
        """stationary_blend=1 → 预测分布 = 平稳分布（与经验行无关）"""
        states = [S.GAP_UP_UP, S.GAP_UP_UP] * 30
        cfg = ForecastConfig(stationary_blend=1.0)
        fc = forecast_next_day(states, cfg)
        stat = stationary_distribution(estimate_transition_matrix(states, cfg.laplace_alpha))
        for s in S:
            assert fc.probabilities[s] == pytest.approx(stat[list(S).index(s)])

    def test_confidence_scales_with_support(self):
        """转移样本越充足置信度越高"""
        few = [S.FLAT_UP, S.FLAT_DOWN] * 2
        many = [S.FLAT_UP, S.FLAT_DOWN] * 60
        cfg = ForecastConfig(stationary_blend=0.0, laplace_alpha=0.0, min_history=2)
        assert forecast_next_day(many, cfg).confidence > forecast_next_day(few, cfg).confidence

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            forecast_next_day([S.FLAT_UP] * 5)


def _make_bars(n: int) -> list[DailyBar]:
    """构造 n 根交替小阴阳 K 线（振幅 <3%，缺口交替）"""
    bars = []
    price = 100.0
    for i in range(n):
        open_ = price * (1.01 if i % 2 == 0 else 0.99)
        close = open_ * (1.005 if i % 3 else 0.995)
        high = max(open_, close) * 1.005
        low = min(open_, close) * 0.995
        bars.append(DailyBar(open_, high, low, close))
        price = close
    return bars


class TestNextDay8StateForecasterLoader:
    def test_forecast_end_to_end_with_fake_query(self):
        bars = _make_bars(80)
        rows = "\n".join(f"2026-01-{i:02d}\t{b.open}\t{b.high}\t{b.low}\t{b.close}" for i, b in enumerate(bars, 1))
        forecaster = NextDay8StateForecaster(query_fn=lambda sql, timeout=30: rows)
        fc = forecaster.forecast("000300", "2025-01-01", "2026-08-31")
        assert sum(fc.probabilities.values()) == pytest.approx(1.0)
        assert fc.n_transitions == 78

    def test_empty_query_raises(self):
        forecaster = NextDay8StateForecaster(query_fn=lambda sql, timeout=30: "")
        with pytest.raises(NextDayForecastDataError):
            forecaster.forecast("000300", "2025-01-01", "2026-08-31")
