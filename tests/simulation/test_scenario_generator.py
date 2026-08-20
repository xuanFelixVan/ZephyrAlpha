"""MOD-SIM-005 Scenario Generator — 场景生成器单元测试。

覆盖: 三种生成模式、GBM 可复现性、历史切片正确性、自定义冲击叠加、
参数校验、scenario_id 唯一性、Aggregate frozen、空/越界输入。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.simulation.scenario_generator import (
    CustomParams,
    HistoricalParams,
    MonteCarloParams,
    ScenarioGenerationError,
    ScenarioGenerator,
    ScenarioGeneratorConfig,
    ScenarioType,
    SimulationScenario,
)


def make_source_data(n: int = 100) -> pd.DataFrame:
    """构建真实历史样例数据。"""
    dates = pd.date_range("2026-01-01", periods=n, freq="D")
    prices = np.linspace(10.0, 20.0, n)  # 线性上升
    return pd.DataFrame(
        {
            "open": prices,
            "high": prices * 1.01,
            "low": prices * 0.99,
            "close": prices,
            "volume": [1000] * n,
        },
        index=dates,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 蒙特卡洛
# ──────────────────────────────────────────────────────────────────────────────


class TestMonteCarlo:
    def test_generates_correct_length(self):
        gen = ScenarioGenerator()
        sc = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=252))
        assert sc.scenario_type is ScenarioType.MONTE_CARLO
        assert len(sc.market_data) == 252
        assert sc.n_bars == 252

    def test_start_price_first_close_approx(self):
        gen = ScenarioGenerator()
        sc = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=10, drift=0.0, volatility=0.0, seed=1))
        # vol=0, drift=0 → 价格恒等于 start_price
        assert all(abs(c - 100.0) < 1e-9 for c in sc.market_data["close"])

    def test_reproducible_with_same_seed(self):
        gen = ScenarioGenerator()
        p = MonteCarloParams(start_price=100.0, n_bars=50, drift=0.05, volatility=0.3, seed=42)
        sc1 = gen.generate_monte_carlo(p)
        sc2 = gen.generate_monte_carlo(p)
        pd.testing.assert_series_equal(sc1.market_data["close"], sc2.market_data["close"])

    def test_different_seed_different_path(self):
        gen = ScenarioGenerator()
        sc1 = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=50, seed=1))
        sc2 = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=50, seed=2))
        assert not np.allclose(sc1.market_data["close"], sc2.market_data["close"])

    def test_ohlcv_columns_present(self):
        gen = ScenarioGenerator()
        sc = gen.generate_monte_carlo(MonteCarloParams(start_price=50.0, n_bars=20))
        for col in ["open", "high", "low", "close", "volume"]:
            assert col in sc.market_data.columns

    def test_high_ge_max_open_close(self):
        gen = ScenarioGenerator()
        sc = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=20, seed=3))
        df = sc.market_data
        assert all(df["high"] >= np.maximum(df["open"], df["close"]) - 1e-9)

    def test_invalid_start_price(self):
        with pytest.raises(ScenarioGenerationError):
            MonteCarloParams(start_price=0.0, n_bars=10)
        with pytest.raises(ScenarioGenerationError):
            MonteCarloParams(start_price=-5.0, n_bars=10)

    def test_invalid_n_bars(self):
        with pytest.raises(ScenarioGenerationError):
            MonteCarloParams(start_price=100.0, n_bars=0)
        with pytest.raises(ScenarioGenerationError):
            MonteCarloParams(start_price=100.0, n_bars=-1)

    def test_invalid_volatility(self):
        with pytest.raises(ScenarioGenerationError):
            MonteCarloParams(start_price=100.0, n_bars=10, volatility=-0.1)


# ──────────────────────────────────────────────────────────────────────────────
# 历史场景
# ──────────────────────────────────────────────────────────────────────────────


class TestHistorical:
    def test_slice_correct(self):
        gen = ScenarioGenerator()
        src = make_source_data(100)
        sc = gen.generate_historical(HistoricalParams(source_data=src, start_idx=10, n_bars=20))
        assert sc.scenario_type is ScenarioType.HISTORICAL
        assert len(sc.market_data) == 20
        # 切片内容应与源数据一致
        assert sc.market_data["close"].iloc[0] == pytest.approx(src["close"].iloc[10])

    def test_n_bars_zero_to_end(self):
        gen = ScenarioGenerator()
        src = make_source_data(100)
        sc = gen.generate_historical(HistoricalParams(source_data=src, start_idx=80, n_bars=0))
        assert len(sc.market_data) == 20  # 100-80

    def test_does_not_modify_source(self):
        gen = ScenarioGenerator()
        src = make_source_data(50)
        original = src.copy()
        gen.generate_historical(HistoricalParams(source_data=src, start_idx=0, n_bars=20))
        pd.testing.assert_frame_equal(src, original)

    def test_out_of_range_start(self):
        gen = ScenarioGenerator()
        src = make_source_data(10)
        with pytest.raises(ScenarioGenerationError):
            gen.generate_historical(HistoricalParams(source_data=src, start_idx=10, n_bars=5))

    def test_slice_exceeds_length(self):
        gen = ScenarioGenerator()
        src = make_source_data(10)
        with pytest.raises(ScenarioGenerationError):
            gen.generate_historical(HistoricalParams(source_data=src, start_idx=5, n_bars=20))

    def test_missing_columns(self):
        gen = ScenarioGenerator()
        bad = pd.DataFrame({"open": [1, 2], "close": [1, 2]})
        with pytest.raises(ScenarioGenerationError):
            gen.generate_historical(HistoricalParams(source_data=bad, n_bars=2))

    def test_non_dataframe(self):
        gen = ScenarioGenerator()
        with pytest.raises(ScenarioGenerationError):
            gen.generate_historical(HistoricalParams(source_data=[1, 2, 3]))  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 自定义场景
# ──────────────────────────────────────────────────────────────────────────────


class TestCustom:
    def test_shock_applied(self):
        gen = ScenarioGenerator()
        # bar 5 时 -10% 冲击
        sc = gen.generate_custom(CustomParams(start_price=100.0, n_bars=20, shocks=[(5, -0.10)], trend=0.0, seed=1))
        closes = sc.market_data["close"]
        # bar5 相比 bar4 应明显下跌(约 -10%)
        drop = (closes.iloc[5] - closes.iloc[4]) / closes.iloc[4]
        assert drop < -0.09

    def test_reproducible(self):
        gen = ScenarioGenerator()
        p = CustomParams(start_price=100.0, n_bars=30, shocks=[(10, 0.05)], seed=7)
        sc1 = gen.generate_custom(p)
        sc2 = gen.generate_custom(p)
        pd.testing.assert_series_equal(sc1.market_data["close"], sc2.market_data["close"])

    def test_trend_applied(self):
        gen = ScenarioGenerator()
        # 正趋势 → 价格上升
        sc = gen.generate_custom(CustomParams(start_price=100.0, n_bars=50, trend=0.001, seed=1))
        assert sc.market_data["close"].iloc[-1] > 100.0

    def test_invalid_shock_index(self):
        with pytest.raises(ScenarioGenerationError):
            CustomParams(start_price=100.0, n_bars=10, shocks=[(20, -0.1)])
        with pytest.raises(ScenarioGenerationError):
            CustomParams(start_price=100.0, n_bars=10, shocks=[(-1, -0.1)])

    def test_no_shocks_pure_trend_noise(self):
        gen = ScenarioGenerator()
        sc = gen.generate_custom(CustomParams(start_price=100.0, n_bars=20, seed=1))
        assert len(sc.market_data) == 20
        # 价格应始终为正
        assert (sc.market_data["close"] > 0).all()


# ──────────────────────────────────────────────────────────────────────────────
# 通用分发 + Aggregate
# ──────────────────────────────────────────────────────────────────────────────


class TestDispatchAndAggregate:
    def test_generate_dispatch_monte_carlo(self):
        gen = ScenarioGenerator()
        sc = gen.generate(ScenarioType.MONTE_CARLO, MonteCarloParams(start_price=100.0, n_bars=10))
        assert sc.scenario_type is ScenarioType.MONTE_CARLO

    def test_generate_dispatch_historical(self):
        gen = ScenarioGenerator()
        sc = gen.generate(ScenarioType.HISTORICAL, HistoricalParams(source_data=make_source_data(20), n_bars=10))
        assert sc.scenario_type is ScenarioType.HISTORICAL

    def test_generate_dispatch_custom(self):
        gen = ScenarioGenerator()
        sc = gen.generate(ScenarioType.CUSTOM, CustomParams(start_price=100.0, n_bars=10))
        assert sc.scenario_type is ScenarioType.CUSTOM

    def test_dispatch_type_mismatch(self):
        gen = ScenarioGenerator()
        with pytest.raises(ScenarioGenerationError):
            gen.generate(ScenarioType.MONTE_CARLO, CustomParams(start_price=100.0, n_bars=10))

    def test_scenario_id_unique(self):
        gen = ScenarioGenerator()
        sc1 = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=10, seed=1))
        sc2 = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=10, seed=1))
        assert sc1.scenario_id != sc2.scenario_id  # 不同调用 → 不同 id

    def test_scenario_id_starts_with_type(self):
        gen = ScenarioGenerator()
        sc = gen.generate_custom(CustomParams(start_price=100.0, n_bars=5))
        assert sc.scenario_id.startswith("custom-")

    def test_params_snapshot_present(self):
        gen = ScenarioGenerator()
        sc = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=10, seed=5))
        assert sc.params["seed"] == 5
        assert sc.params["start_price"] == 100.0

    def test_generated_at_is_iso(self):
        gen = ScenarioGenerator()
        sc = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=5))
        assert "T" in sc.generated_at  # ISO8601 含 T

    def test_aggregate_is_frozen(self):
        gen = ScenarioGenerator()
        sc = gen.generate_monte_carlo(MonteCarloParams(start_price=100.0, n_bars=5))
        with pytest.raises(Exception):
            sc.symbol = "X"  # type: ignore[misc]

    def test_error_code(self):
        assert ScenarioGenerationError.error_code == "ZA-SIM-0005"
