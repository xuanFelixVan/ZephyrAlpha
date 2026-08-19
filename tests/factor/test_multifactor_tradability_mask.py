# [BLUEPRINT] MOD-E2E-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""25号memo Phase 4.1 Mask-First tradability mask 测试。

覆盖：mask 构造（停牌/涨跌停/流动性各通道+组合）/ masked_rank_ic
（掩码过滤效果/标的不足 NaN/常数列 NaN/上游污染实证——不掩码 IC 虚高）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

mod = pytest.importorskip("zephyr.factor.analysis.multifactor_tradability_mask")

build_tradability_mask = mod.build_tradability_mask
masked_rank_ic = mod.masked_rank_ic


def _frames(n_days: int = 2, names: tuple = ("A", "B", "C")):
    idx = pd.date_range("2026-08-18", periods=n_days)
    z = pd.DataFrame(False, index=idx, columns=list(names))
    return z.copy(), z.copy(), z.copy()


class TestBuildMask:
    def test_all_tradable(self):
        s, u, d = _frames()
        m = build_tradability_mask(s, u, d)
        assert m.all().all()

    def test_suspended_excluded(self):
        s, u, d = _frames()
        s.iloc[0, 0] = True
        m = build_tradability_mask(s, u, d)
        assert not m.iloc[0, 0]
        assert m.iloc[1, 0]

    def test_limit_up_down_excluded(self):
        s, u, d = _frames()
        u.iloc[0, 1] = True
        d.iloc[1, 2] = True
        m = build_tradability_mask(s, u, d)
        assert not m.iloc[0, 1]
        assert not m.iloc[1, 2]

    def test_liquidity_filter(self):
        s, u, d = _frames()
        amount = pd.DataFrame(2e7, index=s.index, columns=s.columns)
        amount.iloc[0, 0] = 5e6  # <1000 万
        m = build_tradability_mask(s, u, d, daily_amount=amount)
        assert not m.iloc[0, 0]
        assert m.iloc[0, 1]

    def test_no_amount_skips_liquidity(self):
        s, u, d = _frames()
        m = build_tradability_mask(s, u, d, daily_amount=None)
        assert m.all().all()


class TestMaskedRankIC:
    def test_perfect_rank_ic(self):
        names = [f"S{i}" for i in range(10)]
        f = pd.Series(np.arange(10.0), index=names)
        r = pd.Series(np.arange(10.0), index=names)
        mask = pd.Series(True, index=names)
        assert masked_rank_ic(f, r, mask) == pytest.approx(1.0)

    def test_mask_excludes_polluted_names(self):
        # 停牌标的因子值与收益随机（污染），掩码后 IC 反映可交易池真实排序
        names = [f"S{i}" for i in range(8)] + ["SUS1", "SUS2"]
        f = pd.Series([float(i) for i in range(8)] + [100.0, 99.0], index=names)
        r = pd.Series([float(i) for i in range(8)] + [-5.0, -6.0], index=names)
        mask = pd.Series([True] * 8 + [False, False], index=names)
        assert masked_rank_ic(f, r, mask) == pytest.approx(1.0)

    def test_too_few_tradable_nan(self):
        names = list("ABCD")
        f = pd.Series([1.0, 2.0, 3.0, 4.0], index=names)
        r = pd.Series([1.0, 2.0, 3.0, 4.0], index=names)
        mask = pd.Series([True, True, True, False], index=names)
        assert np.isnan(masked_rank_ic(f, r, mask))  # 3 < min_names=5

    def test_constant_factor_nan(self):
        names = [f"S{i}" for i in range(6)]
        f = pd.Series(1.0, index=names)
        r = pd.Series(np.arange(6.0), index=names)
        mask = pd.Series(True, index=names)
        assert np.isnan(masked_rank_ic(f, r, mask))

    def test_all_masked_out_nan(self):
        names = [f"S{i}" for i in range(6)]
        f = pd.Series(np.arange(6.0), index=names)
        r = pd.Series(np.arange(6.0), index=names)
        mask = pd.Series(False, index=names)
        assert np.isnan(masked_rank_ic(f, r, mask))
