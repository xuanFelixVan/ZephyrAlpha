# [TEST] tests/factor/test_expectations.py
# [DOMAIN] D_FACTOR
# [TARGET] zephyr.factor.expectations（EXP-01~06 纯函数）
# [TTL] permanent
"""一致预期因子族纯函数单元测试（消费端 C2 预备，2026-09-12）。

覆盖：EP 除零防护、修正动量两步公式、Gleason-Lee 上调分类 as-of 对齐、
异常覆盖残差、分歧度除零、评级动量与 MultiIndex 分组移位。零 IO 零生产路径。
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.expectations import (
    exp01_consensus_ep,
    exp02_revision_momentum,
    exp03_revision_breadth,
    exp04_anomaly_coverage,
    exp05_dispersion,
    exp06_rating_momentum,
)


def test_exp01_ep_and_zero_guard():
    eps = pd.Series([1.5, 1.5, -0.5])
    close = pd.Series([10.0, 0.0, 10.0])
    out = exp01_consensus_ep(eps, close)
    assert out.iloc[0] == pytest.approx(0.15)
    assert np.isnan(out.iloc[1]), "close=0 → NaN 禁 inf"
    assert out.iloc[2] == pytest.approx(-0.05), "亏损预期保留负 EP（华泰口径）"


def test_exp02_revision_momentum_formula():
    n = 40
    eps = pd.Series([1.0] * 30 + [2.0] * 10)
    std = pd.Series([0.1] * n)
    mean = pd.Series([1.5] * n)
    out = exp02_revision_momentum(eps, std, mean, k=20)
    # 第 40 日：raw=(2-1)/1=1.0；disp=0.1/1.5=0.0667；adjusted=1.0/0.0667=15.0
    assert out.iloc[39] == pytest.approx(15.0, rel=1e-3)
    assert np.isnan(out.iloc[19]), "k 期之前为 NaN"


def test_exp02_division_by_zero_std_floor():
    n = 25
    eps = pd.Series([1.0] * 20 + [2.0] * 5)
    std = pd.Series([0.0] * n)
    mean = pd.Series([1.5] * n)
    out = exp02_revision_momentum(eps, std, mean, k=20)
    # std=0 → disp=0→clip 至 floor(1e-6) → adjusted=raw/floor=1.0/1e-6=1e6（有界非 inf）
    assert out.iloc[24] == pytest.approx(1.0 / 1e-6, rel=1e-3)


def test_exp03_breadth_asof_classification():
    cons = pd.Series(
        [1.0, 2.0], index=pd.to_datetime(["2026-01-01", "2026-02-01"])
    )
    reports = pd.DataFrame({
        "publish_date": ["2026-01-15", "2026-02-15"],
        "forecast_year": [2026, 2026],
        "eps": [1.5, 1.0],  # 前者 vs consensus_before=1.0 → up；后者 vs 2.0 → down
    })
    out = exp03_revision_breadth(reports, cons, window_days=63)
    out = out.dropna()
    assert out.loc[pd.Timestamp("2026-01-15")] == pytest.approx(1.0)
    assert out.loc[pd.Timestamp("2026-02-15")] == pytest.approx(0.5)


def test_exp04_anomaly_coverage_residual():
    # 线性 y=2*log_mv+3 注入离群点（idx2: +10）——OLS 线会被离群点拉斜，
    # 正确语义=离群点残差显著为正且为全截面最大（而非内点残差为 0）
    log_mv = pd.Series([1.0, 2.0, 3.0, 4.0])
    cov = pd.Series([2 * log_mv[v] + 3 for v in range(4)], dtype=float)
    cov.iloc[2] += 10.0
    chars = pd.DataFrame({"log_mv": log_mv})
    out = exp04_anomaly_coverage(cov, chars, use_log_coverage=False)
    assert out.iloc[2] == pytest.approx(7.0, abs=1e-6), "离群点残差=+7（OLS 精确解）"
    assert out.iloc[2] == out.max(), "离群点=全截面最大正残差"
    # 无特征列 → 残差=去均值（线性口径）
    out2 = exp04_anomaly_coverage(
        pd.Series([1.0, 3.0]), pd.DataFrame(index=pd.Index([0, 1])), use_log_coverage=False
    )
    assert out2.iloc[1] == pytest.approx(1.0)


def test_exp05_dispersion_and_zero_guard():
    out = exp05_dispersion(pd.Series([0.2]), pd.Series([-2.0]))
    assert out.iloc[0] == pytest.approx(0.1)
    out0 = exp05_dispersion(pd.Series([0.2]), pd.Series([0.0]))
    assert np.isnan(out0.iloc[0]), "均值 0 → NaN 禁 inf"


def test_exp06_rating_momentum_and_multiindex_grouping():
    s = pd.Series([3.0] * 10 + [4.5] * 5)
    out = exp06_rating_momentum(s, k=10)
    assert out.iloc[14] == pytest.approx(1.5)

    # MultiIndex：A 恒 1.0（动量恒 0）；B 第 6 日起 2.0（k=5 下第 10 日动量=+1.0）
    # ——逐元组构造，防 date-major 叉排
    idx = pd.MultiIndex.from_tuples(
        [(d, sym) for d in range(12) for sym in ("A", "B")], names=["date", "symbol"]
    )
    vals = [1.0 if sym == "A" else (1.0 if d < 6 else 2.0) for (d, sym) in idx]
    panel = pd.Series(vals, index=idx)
    outp = exp06_rating_momentum(panel, k=5)
    a_last = outp.xs(10, level="date").loc["A"]
    b_last = outp.xs(10, level="date").loc["B"]
    assert a_last == pytest.approx(0.0), "A 无变化→动量 0（groupby shift 不跨标的泄漏）"
    assert b_last == pytest.approx(1.0), "B 上调→动量 +1.0"
