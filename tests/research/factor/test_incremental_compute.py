# [BLUEPRINT] MOD-L02-025 | (auto-injected by S4 reconciler) | §D-FACTOR-01
# [A_module] module_id=MOD-L02-025 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-L02-025 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_incremental_compute
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_incremental_compute.py
# [TTL] task_bound
"""D-FACTOR-01 incremental_compute() 滑动窗口测试——纯逻辑模块（无 IO 依赖）。

覆盖：
- FactorBase 默认回退到 compute()
- Momentum20d 增量计算与全量结果一致
- Momentum20d 无缓存时回退到全量
- Momentum20d 无新增数据时返回缓存
- Momentum20d cached 索引不在 data 中时回退全量
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry
from zephyr.factor.momentum_factor import Momentum20d


def _make_close_data(n: int = 50, seed: int = 42) -> pd.DataFrame:
    """生成合成收盘价数据（n 个交易日）。"""
    rng = np.random.RandomState(seed)
    dates = pd.date_range("2026-01-01", periods=n, freq="B")
    close = 100.0 + np.cumsum(rng.randn(n) * 0.5)
    return pd.DataFrame({"close": close}, index=dates)


class TestDefaultFallback:
    """FactorBase 默认 incremental_compute 回退到 compute()。"""

    def test_default_falls_back_to_compute(self):
        """未覆盖 incremental_compute 的因子应回退到 compute()。"""

        @FactorRegistry.register
        class _TestFactor(FactorBase):
            meta = FactorMeta(
                factor_id="_test_inc_default",
                name="测试因子",
                domain="technical",
            )

            def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
                return data["close"] * 2

        try:
            factor = _TestFactor()
            data = _make_close_data(30)
            full = factor.compute(data)
            inc = factor.incremental_compute(data, cached=pd.Series(dtype=float))
            pd.testing.assert_series_equal(inc, full)
        finally:
            FactorRegistry.registry.pop("_test_inc_default", None)


class TestMomentumIncremental:
    """Momentum20d 增量计算测试。"""

    def test_no_cache_falls_back_to_full(self):
        factor = Momentum20d()
        data = _make_close_data(50)
        full = factor.compute(data, window=20)
        inc = factor.incremental_compute(data, window=20, cached=None)
        pd.testing.assert_series_equal(inc, full)

    def test_empty_cache_falls_back_to_full(self):
        factor = Momentum20d()
        data = _make_close_data(50)
        full = factor.compute(data, window=20)
        inc = factor.incremental_compute(data, window=20, cached=pd.Series(dtype=float))
        pd.testing.assert_series_equal(inc, full)

    def test_incremental_matches_full(self):
        """增量计算结果与全量计算完全一致。"""
        factor = Momentum20d()
        full_data = _make_close_data(50)
        # 先用前 40 天做全量计算作为缓存
        cache_data = full_data.iloc[:40]
        cached = factor.compute(cache_data, window=20)
        # 用全部 50 天做增量计算
        incremental = factor.incremental_compute(full_data, window=20, cached=cached)
        # 全量计算作为基准
        full_result = factor.compute(full_data, window=20)
        # 去掉 NaN 后比较（前 20 天是 NaN）
        valid_mask = full_result.notna()
        pd.testing.assert_series_equal(
            incremental[valid_mask],
            full_result[valid_mask],
            check_names=False,
        )

    def test_no_new_data_returns_cached(self):
        factor = Momentum20d()
        data = _make_close_data(50)
        cached = factor.compute(data, window=20)
        # 传入相同数据 → 无新增 → 返回缓存
        result = factor.incremental_compute(data, window=20, cached=cached)
        pd.testing.assert_series_equal(result, cached)

    def test_cached_index_not_in_data_falls_back(self):
        factor = Momentum20d()
        data = _make_close_data(50)
        # 构造一个索引不在 data 中的缓存
        fake_index = pd.date_range("2025-01-01", periods=30, freq="B")
        cached = pd.Series(np.random.randn(30), index=fake_index)
        result = factor.incremental_compute(data, window=20, cached=cached)
        full = factor.compute(data, window=20)
        # 应回退到全量计算
        pd.testing.assert_series_equal(result, full, check_names=False)

    def test_single_new_point(self):
        """只新增一个数据点时，增量计算正确。"""
        factor = Momentum20d()
        full_data = _make_close_data(41)
        cache_data = full_data.iloc[:40]
        cached = factor.compute(cache_data, window=20)
        incremental = factor.incremental_compute(full_data, window=20, cached=cached)
        full_result = factor.compute(full_data, window=20)
        # 最后一个点应该一致
        assert incremental.iloc[-1] == pytest.approx(full_result.iloc[-1], rel=1e-10)

    def test_multiple_new_points(self):
        """新增多个数据点时，增量计算正确。"""
        factor = Momentum20d()
        full_data = _make_close_data(50)
        cache_data = full_data.iloc[:35]
        cached = factor.compute(cache_data, window=20)
        incremental = factor.incremental_compute(full_data, window=20, cached=cached)
        full_result = factor.compute(full_data, window=20)
        # 比较新增部分（第 35 天之后）
        new_part = full_result.iloc[35:]
        inc_new = incremental.iloc[35:]
        pd.testing.assert_series_equal(inc_new, new_part, check_names=False)
