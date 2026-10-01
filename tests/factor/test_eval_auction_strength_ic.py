# [TTL] permanent
"""eval_auction_strength_ic 证尺（CNS-11 取证面，SW14）——合成帧端到端零 CH。

- 逐日截面 IC 计算：单调因子×单调收益=IC±1；短截面日如实弃；
- 汇总：mean/ic_ir/t_stat 可复算；有效日<2 披露不凑数。
"""

from __future__ import annotations

import importlib.util
import math
import pathlib

import pandas as pd
import pytest

_SPEC = importlib.util.spec_from_file_location(
    "eval_auction_strength_ic",
    pathlib.Path(__file__).resolve().parents[2] / "scripts" / "backtest" / "eval_auction_strength_ic.py",
)
MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(MOD)


def _scored_frame(n_days: int = 6, n_syms: int = 40):
    """合成帧：score 与未来收益完全同序（预期 IC≈+1）。"""
    rows = []
    fwd = {}
    days = pd.bdate_range("2026-08-03", periods=n_days)
    for i, d in enumerate(days[:-1]):
        day = d.date().isoformat()
        nxt = days[i + 1].date().isoformat()
        for k in range(n_syms):
            sym = f"S{k:03d}"
            score = float(k)  # 截面内递增
            rows.append({"trade_date": day, "symbol": sym, "auction_strength_score": score})
            fwd[(sym, day)] = 0.01 * (k + 1) / n_syms  # 与 score 同序
        # 末一日无前视（未成熟）
        rows.append({"trade_date": nxt, "symbol": "S000", "auction_strength_score": 0.0})
    df = pd.DataFrame(rows)
    df = df[~((df["trade_date"] == days[-1].date().isoformat()) & (df["symbol"] != "S000"))]
    return df, fwd


def test_daily_ic_monotone_perfect_rank():
    df, fwd = _scored_frame()
    ic = MOD.daily_cross_section_ic(df, fwd)
    eff = ic.dropna(subset=["ic"])
    assert len(eff) == 5  # 6 日窗口：末日无前视弃，days[0..4] 各 40 票全有效
    assert all(v == pytest.approx(1.0) for v in eff["ic"])


def test_short_cross_section_days_disclosed_not_pooled():
    df, fwd = _scored_frame()
    ic = MOD.daily_cross_section_ic(df, fwd)
    short = ic[ic["ic"].isna()]
    assert len(short) >= 1 and (short["n"] < MOD._MIN_CROSS_SECTION).all()  # 弃日有计数


def test_summary_stats_recomputable():
    df, fwd = _scored_frame()
    ic = MOD.daily_cross_section_ic(df, fwd)
    s = MOD.summarize(ic)
    assert s["n_days_effective"] == 5
    assert s["ic_mean"] == pytest.approx(1.0)
    # 全 1.0 恒 IC → 零方差 → icir/t 如实 None（零方差非可报统计，禁除零假数）
    assert s["ic_ir"] is None and s["t_stat"] is None
    assert s["n_days_dropped_short"] == len(ic) - 5


def test_summary_with_varying_ic():
    df, fwd = _scored_frame()
    # 打乱一日内部分排名 → IC 日间有方差 → icir/t 可算
    day2 = df["trade_date"].unique()[1]
    mask = (df["trade_date"] == day2) & (df["symbol"] == "S000")
    df.loc[mask, "auction_strength_score"] = 99.0
    ic = MOD.daily_cross_section_ic(df, fwd)
    s = MOD.summarize(ic)
    assert s["ic_ir"] is not None and s["t_stat"] is not None


def test_summary_too_few_days_discloses():
    ic = pd.DataFrame({"trade_date": ["d1"], "n": [5], "ic": [None]})
    s = MOD.summarize(ic)
    assert s["ic_mean"] is None and "不凑数" in s["disclosure"]
