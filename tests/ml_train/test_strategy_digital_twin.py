# [BLUEPRINT] MOD-ML-006 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] tests.ml_train.test_strategy_digital_twin
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/ml_train/test_strategy_digital_twin.py -q
# [TTL] permanent

"""策略数字孪生（MOD-ML-006）单元测试——T+1 无未来函数仿真/绩效指标。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.strategy_digital_twin import (
    DigitalTwinError,
    StrategyDigitalTwin,
    TwinSimulationResult,
)


def _twin() -> StrategyDigitalTwin:
    return StrategyDigitalTwin()


class TestInputValidation:
    def test_length_mismatch_rejected(self):
        with pytest.raises(DigitalTwinError):
            _twin().simulate(np.ones(5), np.ones(4))

    def test_too_short_rejected(self):
        with pytest.raises(DigitalTwinError):
            _twin().simulate(np.ones(1), np.ones(1))

    def test_non_positive_price_rejected(self):
        with pytest.raises(DigitalTwinError):
            _twin().simulate(np.zeros(5), np.array([1.0, -1.0, 1.0, 1.0, 1.0]))

    def test_signal_out_of_range_rejected(self):
        with pytest.raises(DigitalTwinError):
            _twin().simulate(np.full(5, 2.0), np.ones(5) * 10)

    def test_non_finite_rejected(self):
        with pytest.raises(DigitalTwinError):
            _twin().simulate(np.array([0.0, np.nan, 0.0]), np.ones(3))


class TestSimulation:
    def test_flat_signal_zero_return(self):
        prices = np.linspace(10, 20, 30)
        result = _twin().simulate(np.zeros(30), prices)
        assert isinstance(result, TwinSimulationResult)
        assert result.total_return == pytest.approx(0.0)
        assert result.n_trades == 0

    def test_full_long_uptrend_positive(self):
        prices = np.linspace(10, 20, 30)
        result = _twin().simulate(np.ones(30), prices)
        assert result.total_return > 0.9  # 约翻倍
        assert result.max_drawdown <= 0.0

    def test_t_plus_1_no_lookahead(self):
        # 第 t 日信号吃 t→t+1 收益：末日信号不产生收益
        prices = np.array([10.0, 10.0, 20.0])
        signals = np.array([0.0, 1.0, 1.0])
        result = _twin().simulate(signals, prices)
        assert result.total_return == pytest.approx(1.0)
        # 若存在未来函数（当日信号当日生效），total_return 会 > 1.0
        result2 = _twin().simulate(np.array([1.0, 0.0, 0.0]), prices)
        assert result2.total_return == pytest.approx(0.0)

    def test_max_drawdown_negative_in_crash(self):
        prices = np.array([10.0, 12.0, 6.0, 6.0])
        result = _twin().simulate(np.ones(4), prices)
        assert result.max_drawdown == pytest.approx(-0.5)

    def test_n_trades_counts_position_changes(self):
        prices = np.linspace(10, 11, 6)
        signals = np.array([0.0, 1.0, 1.0, 0.0, -1.0, 0.0])
        result = _twin().simulate(signals, prices)
        assert result.n_trades == 4  # 0→1, 1→0, 0→-1, -1→0

    def test_equity_curve_length(self):
        prices = np.linspace(10, 12, 10)
        result = _twin().simulate(np.ones(10) * 0.5, prices)
        assert len(result.equity_curve) == 10
        assert result.equity_curve[0] == pytest.approx(1.0)

    def test_sharpe_finite_for_volatile_series(self):
        rng = np.random.default_rng(0)
        prices = 10 * np.exp(np.cumsum(rng.normal(0.001, 0.02, 60)))
        result = _twin().simulate(np.ones(60), prices)
        assert np.isfinite(result.sharpe)

    def test_error_code(self):
        assert DigitalTwinError.error_code == "ZA-MLT-0010"
