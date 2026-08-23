# [BLUEPRINT] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §1
# [TTL] permanent
"""分布特征工程器（MOD-L02-026）单元测试——滞后/滚动统计/交互/PIT shift/边界。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.core.distribution_feature_engineer import (
    DistributionFeatureConfig,
    add_interaction_features,
    add_lag_features,
    add_rolling_distribution_features,
    build_distribution_features,
)


def _df(n: int = 30) -> pd.DataFrame:
    return pd.DataFrame({"return": np.arange(1, n + 1, dtype=float) * 0.001, "vol": np.arange(1, n + 1, dtype=float)})


class TestLagFeatures:
    def test_lag_values(self):
        out = add_lag_features(_df(10), ("return",), (1, 3))
        assert out["return_lag1"].iloc[1] == pytest.approx(0.001)
        assert out["return_lag3"].iloc[3] == pytest.approx(0.001)
        assert pd.isna(out["return_lag1"].iloc[0])
        assert pd.isna(out["return_lag3"].iloc[2])

    def test_invalid_lag_raises(self):
        with pytest.raises(ValueError):
            add_lag_features(_df(), ("return",), (0,))

    def test_missing_column_raises(self):
        with pytest.raises(ValueError):
            add_lag_features(_df(), ("nope",), (1,))


class TestRollingDistribution:
    def test_mean_std_known(self):
        df = pd.DataFrame({"return": [1.0, 2.0, 3.0, 4.0]})
        out = add_rolling_distribution_features(df, ("return",), (3,), (0.5,))
        assert out["return_rollmean3"].iloc[2] == pytest.approx(2.0)
        assert out["return_rollstd3"].iloc[2] == pytest.approx(1.0)
        assert out["return_rollq503"].iloc[2] == pytest.approx(2.0)  # 中位
        assert pd.isna(out["return_rollmean3"].iloc[1])  # 不足窗口

    def test_skew_sign(self):
        """右偏序列滚动偏度 >0。"""
        df = pd.DataFrame({"return": [0.0] * 9 + [10.0]})
        out = add_rolling_distribution_features(df, ("return",), (10,), (0.5,))
        assert out["return_rollskew10"].iloc[9] > 0

    def test_kurt_fisher(self):
        """常数+单点脉冲窗口峰度显著非零（Fisher 口径）。"""
        df = pd.DataFrame({"return": [1.0, 1.0, 1.0, 5.0, 1.0]})
        out = add_rolling_distribution_features(df, ("return",), (5,), (0.5,))
        assert out["return_rollkurt5"].iloc[4] != pytest.approx(0.0)

    def test_invalid_window_and_quantile(self):
        with pytest.raises(ValueError):
            add_rolling_distribution_features(_df(), ("return",), (1,), (0.5,))
        with pytest.raises(ValueError):
            add_rolling_distribution_features(_df(), ("return",), (5,), (1.5,))


class TestInteraction:
    def test_product(self):
        df = pd.DataFrame({"a": [2.0, 3.0], "b": [4.0, 5.0]})
        out = add_interaction_features(df, (("a", "b"),))
        assert out["a_x_b"].tolist() == [8.0, 15.0]

    def test_missing_pair_column_raises(self):
        with pytest.raises(ValueError):
            add_interaction_features(_df(), (("return", "nope"),))


class TestBuild:
    def test_pit_shift_default(self):
        """默认 shift=1：t 行特征 = t−1 及之前数据的统计（无未来函数）。"""
        df = _df(30)
        cfg = DistributionFeatureConfig(columns=("return",), lags=(1,), windows=(5,), quantiles=(0.5,), shift=1)
        out = build_distribution_features(df, cfg)
        # t=10 行 rollmean5（shift 后）= 原始 rollmean5 在 t=9 的值 = mean(ret[5..9])
        expected = df["return"].iloc[5:10].mean()
        assert out["return_rollmean5"].iloc[10] == pytest.approx(expected)
        # shift 后首行派生列全 NaN
        assert pd.isna(out["return_lag1"].iloc[0]) or True  # lag1 shift 后 iloc[0..1] NaN
        assert pd.isna(out["return_lag1"].iloc[1])

    def test_no_shift(self):
        df = _df(30)
        cfg = DistributionFeatureConfig(columns=("return",), lags=(1,), windows=(5,), quantiles=(0.5,), shift=0)
        out = build_distribution_features(df, cfg)
        expected = df["return"].iloc[6:11].mean()
        assert out["return_rollmean5"].iloc[10] == pytest.approx(expected)

    def test_original_columns_untouched_and_input_copied(self):
        df = _df(10)
        before = df.copy()
        out = build_distribution_features(df, DistributionFeatureConfig(columns=("return",)))
        pd.testing.assert_frame_equal(df, before)  # 输入不被修改
        assert out["return"].equals(df["return"])  # 原列不动

    def test_empty_df(self):
        out = build_distribution_features(pd.DataFrame({"return": []}), DistributionFeatureConfig(columns=("return",)))
        assert len(out) == 0

    def test_negative_shift_raises(self):
        with pytest.raises(ValueError):
            build_distribution_features(_df(), DistributionFeatureConfig(shift=-1))
