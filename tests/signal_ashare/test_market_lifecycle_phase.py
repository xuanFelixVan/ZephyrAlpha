"""市场生命周期相位 单元测试（90 号 §22.4 BM-SEL-10 春夏秋冬 4 阶段，MOD-SIG-041）"""

import pytest

from zephyr.signal_ashare.market_lifecycle_phase import (
    LifecyclePhaseConfig,
    LifecycleSeason,
    MarketLifecycleDataError,
    MarketLifecyclePhaseSensor,
    classify_season,
    compute_nh_ratio_series,
    detect_lifecycle_phase,
    moving_average,
    season_constraint,
)


def _linear_series(start: float, end: float, n: int = 30) -> list[float]:
    return [start + (end - start) * i / (n - 1) for i in range(n)]


class TestMovingAverage:
    def test_basic(self):
        assert moving_average([1.0, 2.0, 3.0, 4.0], 2) == pytest.approx(3.5)

    def test_window_covers_all(self):
        assert moving_average([1.0, 2.0, 3.0], 5) == pytest.approx(2.0)


class TestClassifySeason:
    def test_four_combinations(self):
        """2×2（新高占比水位 × 趋势）→ 春夏秋冬"""
        assert classify_season(is_high=False, is_rising=True) == LifecycleSeason.SPRING
        assert classify_season(is_high=True, is_rising=True) == LifecycleSeason.SUMMER
        assert classify_season(is_high=True, is_rising=False) == LifecycleSeason.AUTUMN
        assert classify_season(is_high=False, is_rising=False) == LifecycleSeason.WINTER


class TestSeasonConstraint:
    def test_winter_forbids_bottom_fishing(self):
        c = season_constraint(LifecycleSeason.WINTER)
        assert c.forbid_bottom_fishing is True
        assert c.force_exit is False

    def test_autumn_forces_exit(self):
        c = season_constraint(LifecycleSeason.AUTUMN)
        assert c.forbid_bottom_fishing is False
        assert c.force_exit is True

    def test_spring_summer_no_constraint(self):
        for season in (LifecycleSeason.SPRING, LifecycleSeason.SUMMER):
            c = season_constraint(season)
            assert c.forbid_bottom_fishing is False
            assert c.force_exit is False


class TestComputeNhRatioSeries:
    def test_two_codes_ratio(self):
        """A 连创新高 / B 连跌 → 首日 2/2（单点窗口恒新高），其后 1/2"""
        rows = [
            ("A", "2026-08-01", 10.0),
            ("A", "2026-08-02", 11.0),
            ("A", "2026-08-03", 12.0),
            ("B", "2026-08-01", 12.0),
            ("B", "2026-08-02", 11.0),
            ("B", "2026-08-03", 10.0),
        ]
        series = compute_nh_ratio_series(rows, high_window=250)
        assert [d for d, _ in series] == ["2026-08-01", "2026-08-02", "2026-08-03"]
        assert [r for _, r in series] == [pytest.approx(1.0), pytest.approx(0.5), pytest.approx(0.5)]

    def test_empty_rows(self):
        assert compute_nh_ratio_series([]) == []


class TestDetectLifecyclePhase:
    def test_spring_low_rising(self):
        """低位回升（0.02→0.06，慢线 <0.10 且快线上穿）→ SPRING"""
        snap = detect_lifecycle_phase(_linear_series(0.02, 0.06))
        assert snap.season == LifecycleSeason.SPRING
        assert snap.nh_slow < 0.10
        assert snap.nh_fast > snap.nh_slow
        assert 0.0 <= snap.confidence <= 1.0

    def test_summer_high_rising(self):
        snap = detect_lifecycle_phase(_linear_series(0.12, 0.20))
        assert snap.season == LifecycleSeason.SUMMER

    def test_autumn_high_falling(self):
        snap = detect_lifecycle_phase(_linear_series(0.20, 0.12))
        assert snap.season == LifecycleSeason.AUTUMN
        assert snap.constraint.force_exit is True

    def test_winter_low_falling(self):
        snap = detect_lifecycle_phase(_linear_series(0.08, 0.02))
        assert snap.season == LifecycleSeason.WINTER
        assert snap.constraint.forbid_bottom_fishing is True

    def test_days_in_season_tail_run(self):
        """恒定高位 0.20 → 高位滞涨判 AUTUMN（不升即滞涨），30 输入 − 19 暖机 = 11 天"""
        snap = detect_lifecycle_phase([0.20] * 30)
        assert snap.season == LifecycleSeason.AUTUMN
        assert snap.days_in_season == 11

    def test_index_agreement_adjusts_confidence(self):
        """指数趋势与季节一致 → 置信度上调；背离 → 下调"""
        nh = _linear_series(0.12, 0.20)  # SUMMER（多方季）
        closes_up = _linear_series(100.0, 120.0, 30)
        closes_down = _linear_series(120.0, 100.0, 30)
        agree = detect_lifecycle_phase(nh, closes_up)
        disagree = detect_lifecycle_phase(nh, closes_down)
        assert agree.confidence > disagree.confidence

    def test_insufficient_history_raises(self):
        with pytest.raises(ValueError):
            detect_lifecycle_phase([0.1] * 20)


class TestMarketLifecyclePhaseSensorLoader:
    @staticmethod
    def _fake_registry():
        class _R:
            def table(self, category_id):
                return {
                    "market_sector_kline": "c1_market.kline_sector",
                    "market_index_kline": "c1_market.kline_index",
                }[category_id]

        return _R()

    def test_sense_end_to_end_with_fake_query(self):
        """板块新高占比阶梯式崩塌（1.0→2/3→1/3→0）→ WINTER（冬季禁抄底约束生效）"""
        codes = {
            # A 前 10 日连创新高后转跌；B 前 5 日；C 前 2 日（high_window=250 下 NH=收盘超全部历史）
            "8801": [100.0 + i for i in range(1, 11)] + [110.0 - (i - 10) for i in range(11, 31)],
            "8802": [100.0 + i for i in range(1, 6)] + [105.0 - (i - 5) for i in range(6, 31)],
            "8803": [100.0 + i for i in range(1, 3)] + [102.0 - (i - 2) for i in range(3, 31)],
        }
        sector_rows = "\n".join(
            f"{code}\t2026-07-{i:02d}\t{closes[i - 1]:.4f}" for code, closes in codes.items() for i in range(1, 31)
        )
        index_rows = "\n".join(f"2026-07-{i:02d}\t{120.0 - i}" for i in range(1, 31))

        def fake_query(sql, timeout=30):
            if "kline_sector" in sql:
                return sector_rows
            return index_rows

        sensor = MarketLifecyclePhaseSensor(registry=self._fake_registry(), query_fn=fake_query)
        snap = sensor.sense("000300", "2026-07-01", "2026-07-31")
        assert snap.season == LifecycleSeason.WINTER
        assert snap.constraint.forbid_bottom_fishing is True
        assert 0.0 <= snap.confidence <= 1.0

    def test_empty_sector_query_raises(self):
        sensor = MarketLifecyclePhaseSensor(registry=self._fake_registry(), query_fn=lambda sql, timeout=30: "")
        with pytest.raises(MarketLifecycleDataError):
            sensor.sense("000300", "2026-07-01", "2026-07-31")
