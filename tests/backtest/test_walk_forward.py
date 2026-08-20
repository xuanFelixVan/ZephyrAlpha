# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_walk_forward
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_walk_forward.py
# [TTL] task_bound
"""WalkForwardAnalyzer 单元测试(52号 §7 新发现1 测试债清偿).

覆盖: 配置校验、rolling/anchored/expanding 三模式切分正确性、PIT 无泄漏
(train_end <= test_start)、split 分发、退化输入(空/None)、
White's Reality Check 显著/不显著/零方差/样本不足、stationary block bootstrap 长度保持。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.backtest.core.walk_forward import (
    WalkForwardAnalyzer,
    WalkForwardConfig,
    WalkForwardError,
)


def _dates(n: int) -> list[int]:
    return list(range(n))


# ============== 配置校验 ==============


class TestWalkForwardConfig:
    def test_default_config_valid(self):
        cfg = WalkForwardConfig()
        assert cfg.mode == "rolling"
        assert cfg.train_window == 252
        assert cfg.test_window == 63
        assert cfg.step == 63

    def test_train_window_must_positive(self):
        with pytest.raises(WalkForwardError):
            WalkForwardConfig(train_window=0)

    def test_test_window_must_positive(self):
        with pytest.raises(WalkForwardError):
            WalkForwardConfig(test_window=-1)

    def test_step_must_positive(self):
        with pytest.raises(WalkForwardError):
            WalkForwardConfig(step=0)

    def test_invalid_mode_rejected(self):
        with pytest.raises(WalkForwardError):
            WalkForwardConfig(mode="kfold")

    def test_block_size_must_non_negative(self):
        with pytest.raises(WalkForwardError):
            WalkForwardConfig(block_size=-1)

    def test_config_frozen(self):
        cfg = WalkForwardConfig()
        with pytest.raises(AttributeError):
            cfg.mode = "anchored"  # type: ignore[misc]


# ============== rolling 切分 ==============


class TestSplitRolling:
    def test_basic_folds(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="rolling", train_window=4, test_window=2, step=2)
        )
        folds = analyzer.split_rolling(_dates(10))
        # fold0: train[0,4) test[4,6); fold1: train[2,6) test[6,8); fold2: train[4,8) test[8,10)
        assert len(folds) == 3
        train0, test0 = folds[0]
        assert train0 == [0, 1, 2, 3]
        assert test0 == [4, 5]

    def test_no_leakage_all_folds(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="rolling", train_window=5, test_window=3, step=2)
        )
        for train, test in analyzer.split_rolling(_dates(20)):
            assert max(train) < min(test)  # PIT: train_end <= test_start

    def test_insufficient_data_returns_empty(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="rolling", train_window=5, test_window=3)
        )
        assert analyzer.split_rolling(_dates(7)) == []

    def test_exact_fit_single_fold(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="rolling", train_window=5, test_window=3)
        )
        folds = analyzer.split_rolling(_dates(8))
        assert len(folds) == 1

    def test_none_dates_raises(self):
        analyzer = WalkForwardAnalyzer()
        with pytest.raises(WalkForwardError):
            analyzer.split_rolling(None)


# ============== anchored 切分 ==============


class TestSplitAnchored:
    def test_train_starts_at_zero_and_grows_by_step(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="anchored", train_window=4, test_window=2, step=2)
        )
        folds = analyzer.split_anchored(_dates(10))
        assert len(folds) == 3
        for train, _ in folds:
            assert train[0] == 0
        assert len(folds[0][0]) == 4
        assert len(folds[1][0]) == 6
        assert len(folds[2][0]) == 8

    def test_no_leakage(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="anchored", train_window=4, test_window=2, step=1)
        )
        for train, test in analyzer.split_anchored(_dates(12)):
            assert max(train) < min(test)

    def test_insufficient_data_returns_empty(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="anchored", train_window=6, test_window=2)
        )
        assert analyzer.split_anchored(_dates(7)) == []


# ============== expanding 切分 ==============


class TestSplitExpanding:
    def test_train_grows_by_test_window_ignores_step(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="expanding", train_window=4, test_window=2, step=99)
        )
        folds = analyzer.split_expanding(_dates(10))
        # step 被忽略, 以 test_window=2 增长
        assert len(folds) == 3
        assert len(folds[0][0]) == 4
        assert len(folds[1][0]) == 6
        assert len(folds[2][0]) == 8

    def test_no_leakage(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="expanding", train_window=3, test_window=2)
        )
        for train, test in analyzer.split_expanding(_dates(9)):
            assert max(train) < min(test)

    def test_none_dates_raises(self):
        analyzer = WalkForwardAnalyzer()
        with pytest.raises(WalkForwardError):
            analyzer.split_expanding(None)


# ============== split 分发 ==============


class TestSplitDispatch:
    def test_dispatch_rolling(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="rolling", train_window=4, test_window=2, step=2)
        )
        assert analyzer.split(_dates(10)) == analyzer.split_rolling(_dates(10))

    def test_dispatch_anchored(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="anchored", train_window=4, test_window=2, step=2)
        )
        assert analyzer.split(_dates(10)) == analyzer.split_anchored(_dates(10))

    def test_dispatch_expanding(self):
        analyzer = WalkForwardAnalyzer(
            WalkForwardConfig(mode="expanding", train_window=4, test_window=2)
        )
        assert analyzer.split(_dates(10)) == analyzer.split_expanding(_dates(10))


# ============== White's Reality Check ==============


class TestWhitesRealityCheck:
    def _series(self, values, start="2024-01-01"):
        idx = pd.date_range(start, periods=len(values), freq="B")
        return pd.Series(values, index=idx)

    def test_strong_excess_return_is_significant(self):
        rng = np.random.default_rng(42)
        n = 250
        benchmark = rng.normal(0.0, 0.01, n)
        # 策略 = 基准 + 稳定正超额(均值0.005, 噪声远小于均值 → t统计量极大)
        strategy = benchmark + 0.005 + rng.normal(0.0, 0.001, n)
        result = WalkForwardAnalyzer().whites_reality_check(
            self._series(strategy), self._series(benchmark), n_bootstrap=200
        )
        assert result["is_significant"] is True
        assert result["p_value"] < 0.05
        assert result["t_stat"] > 0

    def test_no_excess_return_not_significant(self):
        rng = np.random.default_rng(7)
        n = 250
        benchmark = rng.normal(0.0, 0.01, n)
        noise = rng.normal(0.0, 0.01, n)
        noise = noise - noise.mean()  # 精确零均值超额 → obs_t≈0, p 稳定高位(bootstrap内rng无种子)
        strategy = benchmark + noise
        result = WalkForwardAnalyzer().whites_reality_check(
            self._series(strategy), self._series(benchmark), n_bootstrap=200
        )
        assert result["is_significant"] is False
        assert result["p_value"] >= 0.05

    def test_identical_series_zero_variance_guard(self):
        values = np.full(100, 0.001)
        s = self._series(values)
        result = WalkForwardAnalyzer().whites_reality_check(s, s, n_bootstrap=50)
        assert result == {"p_value": 1.0, "is_significant": False, "t_stat": 0.0}

    def test_insufficient_aligned_samples(self):
        s = self._series([0.01])
        b = self._series([0.005])
        result = WalkForwardAnalyzer().whites_reality_check(s, b, n_bootstrap=50)
        assert result["p_value"] == 1.0
        assert result["is_significant"] is False

    def test_none_input_raises(self):
        s = self._series([0.01, 0.02])
        with pytest.raises(WalkForwardError):
            WalkForwardAnalyzer().whites_reality_check(None, s)
        with pytest.raises(WalkForwardError):
            WalkForwardAnalyzer().whites_reality_check(s, None)

    def test_invalid_n_bootstrap_raises(self):
        s = self._series([0.01, 0.02, 0.0])
        with pytest.raises(WalkForwardError):
            WalkForwardAnalyzer().whites_reality_check(s, s, n_bootstrap=0)

    def test_result_keys(self):
        rng = np.random.default_rng(1)
        s = self._series(rng.normal(0.001, 0.01, 80))
        b = self._series(rng.normal(0.0, 0.01, 80))
        result = WalkForwardAnalyzer().whites_reality_check(s, b, n_bootstrap=50)
        assert set(result) == {"p_value", "is_significant", "t_stat"}


# ============== stationary block bootstrap ==============


class TestStationaryBlockBootstrap:
    def test_length_preserved(self):
        data = np.arange(100, dtype=float)
        rng = np.random.default_rng(0)
        sample = WalkForwardAnalyzer._stationary_block_bootstrap(data, 5, rng)
        assert len(sample) == len(data)

    def test_values_from_original(self):
        data = np.arange(10, dtype=float)
        rng = np.random.default_rng(3)
        sample = WalkForwardAnalyzer._stationary_block_bootstrap(data, 3, rng)
        assert set(sample.tolist()).issubset(set(data.tolist()))

    def test_block_size_one_like_iid(self):
        data = np.arange(50, dtype=float)
        rng = np.random.default_rng(5)
        sample = WalkForwardAnalyzer._stationary_block_bootstrap(data, 1, rng)
        assert len(sample) == 50
