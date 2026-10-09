"""跨市场传导传感器 单元测试（90 号 §22.3 BM-SEL-06，MOD-SIG-038）"""

import pytest

from zephyr.signal_ashare.cross_market_conduction_sensor import (
    ConductionConfig,
    ConductionSnapshot,
    CrossMarketConductionDataError,
    CrossMarketConductionSensor,
    ForeignMarketSeries,
    ShockLevel,
    align_foreign_to_ashare,
    classify_shock,
    estimate_conduction,
    lead_lag_correlation,
    pearson_corr,
    sense_cross_market_conduction,
)


class TestPearsonCorr:
    def test_perfect_positive(self):
        assert pearson_corr([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)

    def test_perfect_negative(self):
        assert pearson_corr([1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)

    def test_zero_variance_returns_zero(self):
        assert pearson_corr([1, 1, 1], [1, 2, 3]) == 0.0

    def test_too_short_returns_zero(self):
        assert pearson_corr([1], [2]) == 0.0


class TestAlignForeignToAshare:
    def test_aligns_to_latest_prior_foreign_date(self):
        """外盘 t 日收益 → A 股其后首个交易日（隔夜传导口径）"""
        ashare = {"2026-01-05": 0.001, "2026-01-06": 0.002, "2026-01-07": 0.003}
        foreign = {"2026-01-04": 0.01, "2026-01-05": -0.02, "2026-01-06": 0.03}
        f_aligned, a_aligned = align_foreign_to_ashare(ashare, foreign)
        assert f_aligned == [0.01, -0.02, 0.03]
        assert a_aligned == [0.001, 0.002, 0.003]

    def test_drops_ashare_dates_without_prior_foreign(self):
        """严格先前口径：同日历日期的外盘收益不算"隔夜"，无更早外盘数据的 A 股日剔除"""
        ashare = {"2026-01-05": 0.001, "2026-01-06": 0.002}
        foreign = {"2026-01-05": 0.01}
        f_aligned, a_aligned = align_foreign_to_ashare(ashare, foreign)
        assert f_aligned == [0.01]
        assert a_aligned == [0.002]

    def test_empty_inputs(self):
        assert align_foreign_to_ashare({}, {"2026-01-01": 0.01}) == ([], [])


class TestLeadLagCorrelation:
    def test_lag_one_perfect(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [0.0, 1.0, 2.0, 3.0, 4.0]  # y = x 滞后 1
        assert lead_lag_correlation(x, y, lag=1) == pytest.approx(1.0)

    def test_lag_zero(self):
        x = [1.0, 2.0, 3.0, 4.0]
        assert lead_lag_correlation(x, x, lag=0) == pytest.approx(1.0)


class TestEstimateConduction:
    def test_same_day_conduction(self):
        """A股 = 0.5×外盘（同期）→ lead_lag=0, beta=0.5, corr=1"""
        foreign = [0.01, -0.01, 0.0] * 40
        ashare = [0.5 * f for f in foreign]
        est = estimate_conduction(foreign, ashare, symbol="SPX")
        assert est is not None
        assert est.lead_lag == 0
        assert est.beta == pytest.approx(0.5)
        assert est.correlation == pytest.approx(1.0)
        assert est.n_samples == 120
        assert 0.0 < est.confidence <= 1.0

    def test_lagged_conduction(self):
        """A股 = 0.5×外盘滞后 1 天 → lead_lag=1（3-cycle 外盘 lag0 自相关仅 0.5）"""
        foreign = [0.01, -0.01, 0.0] * 40
        ashare = [0.0] + [0.5 * foreign[i - 1] for i in range(1, 120)]
        est = estimate_conduction(foreign, ashare, symbol="IXIC")
        assert est is not None
        assert est.lead_lag == 1
        assert est.beta == pytest.approx(0.5)

    def test_insufficient_samples_returns_none(self):
        foreign = [0.01, -0.01, 0.0] * 10  # 30 < min_samples=60
        ashare = [0.5 * f for f in foreign]
        assert estimate_conduction(foreign, ashare) is None


class TestClassifyShock:
    @pytest.mark.parametrize(
        ("shock", "expected"),
        [
            (0.005, ShockLevel.NONE),
            (-0.009, ShockLevel.NONE),
            (0.01, ShockLevel.MILD),
            (-0.015, ShockLevel.MILD),
            (0.02, ShockLevel.SEVERE),
            (-0.05, ShockLevel.SEVERE),
        ],
    )
    def test_shock_levels(self, shock, expected):
        assert classify_shock(shock) == expected


class TestSenseCrossMarketConduction:
    def test_snapshot_aggregation(self):
        foreign = [0.01, -0.01, 0.0] * 40
        ashare = tuple(0.5 * f for f in foreign)
        series = [
            ForeignMarketSeries(symbol="SPX", returns=tuple(foreign), ashare_returns=ashare, latest_shock=0.02),
            ForeignMarketSeries(symbol="IXIC", returns=tuple(foreign), ashare_returns=ashare, latest_shock=-0.005),
        ]
        snap = sense_cross_market_conduction(series)
        assert isinstance(snap, ConductionSnapshot)
        assert len(snap.markets) == 2
        # total = 0.5×0.02 + 0.5×(−0.005) = 0.0075
        assert snap.total_predicted_impact == pytest.approx(0.0075)
        assert snap.worst_shock_level == ShockLevel.SEVERE  # SPX 0.02 触及 SEVERE
        assert 0.0 < snap.confidence <= 1.0

    def test_total_impact_clipped(self):
        foreign = [0.01, -0.01, 0.0] * 40
        ashare = tuple(0.9 * f for f in foreign)
        series = [ForeignMarketSeries(symbol="SPX", returns=tuple(foreign), ashare_returns=ashare, latest_shock=0.10)]
        cfg = ConductionConfig(impact_clip=0.05)
        snap = sense_cross_market_conduction(series, cfg)
        assert snap.total_predicted_impact == pytest.approx(0.05)

    def test_all_insufficient_gives_empty_markets(self):
        series = [
            ForeignMarketSeries(symbol="SPX", returns=(0.01, -0.01), ashare_returns=(0.005, -0.005), latest_shock=0.01)
        ]
        snap = sense_cross_market_conduction(series)
        assert snap.markets == ()
        assert snap.total_predicted_impact == 0.0
        assert snap.confidence == 0.0


class TestCrossMarketConductionSensorLoader:
    @staticmethod
    def _fake_registry():
        class _R:
            def table(self, category_id):
                return {
                    "market_us_index": "c1_market.us_index",
                    "market_index_kline": "c1_market.kline_index",
                }[category_id]

        return _R()

    def test_sense_end_to_end_with_fake_query(self):
        # 外盘 3-cycle 收益（130 期，末值取 MILD 档内 0.012），IXIC 振幅为 SPX 的 2 倍
        spx_rets = [0.01, -0.01, 0.0] * 43 + [0.012]  # 130 期，spx_rets[j] 是日期 D_{j+2} 的收益
        ixic_rets = [r * 2.0 for r in spx_rets]

        def _closes(rets):
            closes = [100.0]
            for r in rets:
                closes.append(closes[-1] * (1.0 + r))
            return closes

        spx_closes = _closes(spx_rets)
        ixic_closes = _closes(ixic_rets)
        # A 股收益 = 0.5 × SPX 前一日收益（隔夜传导口径）：A[D_i] = 0.5×F_ret[D_{i-1}]
        a_closes = [100.0, 100.0]  # D2 收益设为 0（其前一日无外盘收益）
        for i in range(2, 131):
            a_closes.append(a_closes[-1] * (1.0 + 0.5 * spx_rets[i - 2]))
        dates = [f"2026-01-{i:02d}" for i in range(1, 32)]
        dates += [f"2026-02-{i:02d}" for i in range(1, 29)]
        dates += [f"2026-03-{i:02d}" for i in range(1, 32)]
        dates += [f"2026-04-{i:02d}" for i in range(1, 42)]
        assert len(dates) == 131
        us_rows = (
            "\n".join(f"{dates[j]}\tSPX\t{spx_closes[j]:.6f}" for j in range(131))
            + "\n"
            + "\n".join(f"{dates[j]}\tIXIC\t{ixic_closes[j]:.6f}" for j in range(131))
        )
        a_rows = "\n".join(f"{dates[j]}\t{a_closes[j]:.6f}" for j in range(131))

        def fake_query(sql, timeout=30):
            if "us_index" in sql:
                return us_rows
            return a_rows

        sensor = CrossMarketConductionSensor(registry=self._fake_registry(), query_fn=fake_query)
        snap = sensor.sense("000300", "2026-01-01", "2026-08-31")
        assert len(snap.markets) == 2
        by_symbol = {m.foreign_symbol: m for m in snap.markets}
        assert by_symbol["SPX"].beta == pytest.approx(0.5, abs=1e-3)
        assert by_symbol["IXIC"].beta == pytest.approx(0.25, abs=1e-3)
        assert by_symbol["SPX"].lead_lag == 0
        # 最新外盘收益 SPX 0.012 → MILD / IXIC 0.024 → SEVERE；total = 0.006+0.006 = 0.012
        assert by_symbol["SPX"].shock_level == ShockLevel.MILD
        assert snap.worst_shock_level == ShockLevel.SEVERE
        assert snap.total_predicted_impact == pytest.approx(0.012, abs=1e-3)

    def test_empty_query_raises(self):
        sensor = CrossMarketConductionSensor(registry=self._fake_registry(), query_fn=lambda sql, timeout=30: "")
        with pytest.raises(CrossMarketConductionDataError):
            sensor.sense("000300", "2026-01-01", "2026-08-31")
