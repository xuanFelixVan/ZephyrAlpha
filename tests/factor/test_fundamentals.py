# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_fundamentals
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.fundamentals
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数直测零 IO（禁写生产路径，面板全部内存构造）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] 本文件
# [TTL] permanent
"""fundamentals 八因子单测——方向约定/同比移位/边界（消费端 F2，DS-230 面板契约）。

锁定：
    1. 方向约定：值越大预期收益越高（FQ-01 取负、FQ-05 取负）
    2. 报告期移位：MultiIndex(symbol, report_period) 下 shift(4)=上年同期
    3. F-Score 九项齐才出分（缺项→NaN）；完美公司=9、恶化公司=低分
    4. 除法分母零/NaN→NaN 禁 inf
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.factor.fundamentals import (
    accrual_negative_screen,
    fq01_accrual,
    fq02_cash_conversion,
    fq03_gpoa,
    fq04_delta_roe_q,
    fq05_info_quality,
    fq06_fscore,
    gr01_rev_q_yoy,
    gr02_np_q_qoq,
)


def _panel(n_periods: int = 8, symbols: tuple = ("000001",)) -> pd.MultiIndex:
    """构造 (symbol, report_period) 面板索引，季度末升序。"""
    periods = pd.period_range("2024Q1", periods=n_periods, freq="Q").to_timestamp(how="end").normalize()
    idx = pd.MultiIndex.from_product([symbols, periods], names=["symbol", "report_period"])
    return idx.sort_values()


def test_fq01_sign_negated():
    idx = _panel(2)
    acc = pd.Series([0.10, -0.05] * 1, index=idx[:2])
    out = fq01_accrual(acc)
    assert out.iloc[0] == pytest.approx(-0.10)
    assert out.iloc[1] == pytest.approx(0.05)


def test_fq02_stable_converter_beats_volatile():
    # A 股票：转化效率稳定 1.2；B 股票：均值同为 1.2 但剧烈波动
    n = 12
    idx = _panel(n, symbols=("A",))
    np_ttm = pd.Series([10.0] * n, index=idx)
    ocf_a = pd.Series([12.0, 11.5, 12.5, 12.0] * (n // 4), index=idx)
    ta = pd.Series([100.0] * n, index=idx)
    good = fq02_cash_conversion(np_ttm, ocf_a, ta)
    ocf_b = pd.Series([20.0, 4.0, 20.0, 4.0] * (n // 4), index=idx)  # 均值 12 但波动大
    bad = fq02_cash_conversion(np_ttm, ocf_b, ta)
    assert good.iloc[-1] > bad.iloc[-1]


def test_fq03_passthrough():
    idx = _panel(1)
    s = pd.Series([0.31], index=idx)
    assert fq03_gpoa(s).iloc[0] == pytest.approx(0.31)


def test_fq04_delta_roe_uses_year_ago_report():
    # 8 个报告期：前 4 期 np_q=1（roe 年化=4/100），后 4 期 np_q=2（roe 年化=8/100）
    n = 8
    idx = _panel(n, symbols=("A",))
    np_q = pd.Series([1.0] * 4 + [2.0] * 4, index=idx)
    eq = pd.Series([100.0] * n, index=idx)
    out = fq04_delta_roe_q(np_q, eq)
    assert out.iloc[:4].isna().all()          # 上年同期不足 → NaN
    assert out.iloc[4] == pytest.approx(0.08 - 0.04)


def test_gr_passthrough_and_nan_propagation():
    idx = _panel(2)
    up = pd.Series([0.25, np.nan], index=idx)
    assert gr01_rev_q_yoy(up).iloc[0] == pytest.approx(0.25)
    assert gr01_rev_q_yoy(up).iloc[1] is np.nan or np.isnan(gr01_rev_q_yoy(up).iloc[1])
    qoq = pd.Series([-0.4, 0.6], index=idx)
    assert gr02_np_q_qoq(qoq).iloc[1] == pytest.approx(0.6)


def test_fq05_clean_beats_aggressive():
    n = 14
    idx = _panel(n, symbols=("A",))
    rev = pd.Series([100.0] * n, index=idx)
    tax = pd.Series([0.15] * n, index=idx)
    clean_ar = pd.Series([10.0 + (i % 3) * 0.1 for i in range(n)], index=idx)             # 平稳（常数域往复）
    wild_ar = pd.Series([10.0 + (25.0 if i % 2 else 0.0) for i in range(n)], index=idx)  # 锯齿
    clean = fq05_info_quality(clean_ar, rev, tax)
    wild = fq05_info_quality(wild_ar, rev, tax)
    assert clean.iloc[-1] > wild.iloc[-1]


def test_fq06_nine_items_and_strict_nan():
    n = 6
    idx = _panel(n, symbols=("A",))
    # 完美公司：盈利且逐期改善（ΔROA>0 需真增长）、现金足、股本不增
    df = pd.DataFrame({
        "np_ttm": [10.0, 10.0, 10.0, 10.0, 10.5, 11.0],
        "ocf_ttm": [12.0] * n,
        "total_assets": [100.0] * n,
        "total_liabilities": [40.0, 40.0, 40.0, 40.0, 38.0, 36.0],
        "tca": [50.0, 50.0, 50.0, 50.0, 52.0, 54.0],
        "tcl": [30.0, 30.0, 30.0, 30.0, 29.0, 28.0],
        "shares": [10.0] * n,
        "rev_ttm": [200.0, 200.0, 200.0, 200.0, 210.0, 220.0],
        "gm_q": [0.30, 0.30, 0.30, 0.30, 0.32, 0.34],
    }, index=idx)
    score = fq06_fscore(
        df["np_ttm"], df["ocf_ttm"], df["total_assets"], df["total_liabilities"],
        df["tca"], df["tcl"], df["shares"], df["rev_ttm"], df["gm_q"])
    # 首期缺上年同期 5 项（ROA↑/杠杆/流动/周转/毛利率同比）→ NaN
    assert np.isnan(score.iloc[0])
    # 末期：全部 9 项满足 → 9.0
    assert score.iloc[-1] == pytest.approx(9.0)

    # 缺股本（无增发项不可得）→ 整体 NaN（严格语义）
    bad_shares = df["shares"].copy()
    bad_shares.iloc[-1] = np.nan
    score2 = fq06_fscore(
        df["np_ttm"], df["ocf_ttm"], df["total_assets"], df["total_liabilities"],
        df["tca"], df["tcl"], bad_shares, df["rev_ttm"], df["gm_q"])
    assert np.isnan(score2.iloc[-1])


def test_fq06_deteriorating_company_low_score():
    n = 6
    idx = _panel(n, symbols=("A",))
    # 恶化公司：亏损、无现金、杠杆升、股本增发
    df = pd.DataFrame({
        "np_ttm": [-5.0] * n,
        "ocf_ttm": [-8.0] * n,
        "total_assets": [100.0] * n,
        "total_liabilities": [50.0, 52.0, 54.0, 56.0, 58.0, 60.0],
        "tca": [40.0, 38.0, 36.0, 34.0, 32.0, 30.0],
        "tcl": [30.0, 31.0, 32.0, 33.0, 34.0, 35.0],
        "shares": [10.0, 10.0, 11.0, 12.0, 13.0, 14.0],
        "rev_ttm": [200.0, 195.0, 190.0, 185.0, 180.0, 175.0],
        "gm_q": [0.30, 0.29, 0.28, 0.27, 0.26, 0.25],
    }, index=idx)
    score = fq06_fscore(
        df["np_ttm"], df["ocf_ttm"], df["total_assets"], df["total_liabilities"],
        df["tca"], df["tcl"], df["shares"], df["rev_ttm"], df["gm_q"])
    assert score.iloc[-1] <= 1.0


def test_accrual_negative_screen():
    """剔除器：应计>阈值→True（建议剔除）；NaN→False（无证据不剔除）。"""
    idx = _panel(3)
    s = pd.Series([0.05, -0.02, np.nan], index=idx)
    out = accrual_negative_screen(s)
    assert out.iloc[0] is True or out.iloc[0] == True  # noqa: E712 — 高应计剔除
    assert out.iloc[1] == False  # noqa: E712 — 低应计保留
    assert out.iloc[2] == False  # noqa: E712 — NaN 不剔除
    assert accrual_negative_screen(s, threshold=0.1).iloc[0] == False  # noqa: E712
