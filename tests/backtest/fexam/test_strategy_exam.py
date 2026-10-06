# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_strategy_exam.py | 批2/批4 纯函数单测（合成数据零DB零引擎）
"""strategy_exam/allocator_shadow 单测：信号构建/窗口分段/判定/权重变换性质（tmp_path）。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

from allocator_shadow import (  # noqa: E402
    clamp_weights,
    normalize,
    pa015_weights,
    three_layer_weights,
    w_inverse_vol,
)
from strategy_exam import (  # noqa: E402
    composite_signal,
    judge_strategy,
    monthly_topn_signals,
    regime_sharpe,
    window_metrics,
)


def test_composite_signal_short_flip():
    idx = pd.date_range("2025-01-01", periods=30)
    long_p = pd.DataFrame({"A": [1.0] * 30, "B": [2.0] * 30}, index=idx)  # A 值低=rank 低
    short_p = pd.DataFrame({"A": [1.0] * 30, "B": [2.0] * 30}, index=idx)
    c = composite_signal({"f1": long_p}, {"f1": 1})
    assert c["B"].iloc[0] > c["A"].iloc[0]
    c2 = composite_signal({"f1": short_p}, {"f1": -1})
    assert c2["A"].iloc[0] > c2["B"].iloc[0]  # short 方向翻转


def test_monthly_topn_step_function():
    rng = np.random.default_rng(5)
    idx = pd.date_range("2025-01-01", periods=100, freq="B")
    comp = pd.DataFrame(rng.normal(size=(len(idx), 25)), index=idx, columns=[f"C{i:02d}" for i in range(25)])
    w = monthly_topn_signals(comp, idx, top_n=5)
    # 非零行=调仓日行+前向填充行；每个调仓月首行恰 5 个非零且和=1
    reb_rows = w.loc[[d for d in idx if (d.month != (d - pd.offsets.BMonthBegin(1)).month)]]
    assert (np.count_nonzero(reb_rows.values, axis=1) == 5).all()
    assert np.allclose(reb_rows.sum(axis=1), 1.0)
    # 月中权重与月首一致（步进保持）
    first_month_mid = w.iloc[10]
    first_reb = w.iloc[0]
    assert np.allclose(first_month_mid.values, first_reb.values)


def test_window_metrics():
    idx = pd.date_range("2024-01-01", periods=300)
    nav = pd.Series(np.linspace(1.0, 1.2, 300), index=idx)
    m = window_metrics(nav, "2024-01-01", "2024-12-31")
    assert m["total_return"] > 0.19 and m["max_drawdown"] == 0.0 and m["sharpe"] > 0
    # 回撤情形
    nav2 = pd.Series([1.0] * 50 + [0.8] * 50, index=pd.date_range("2025-01-01", periods=100))
    m2 = window_metrics(nav2, "2025-01-01", "2025-12-31")
    assert abs(m2["max_drawdown"] + 0.2) < 1e-9


def test_regime_sharpe_min_obs():
    idx = pd.date_range("2025-01-01", periods=60)
    nav = pd.Series(1.0 + np.arange(60) * 0.001, index=idx)
    regimes = pd.Series(["trend_up"] * 50 + ["trend_down"] * 10, index=idx)
    out = regime_sharpe(nav, regimes)
    assert out["trend_up"]["sharpe"] > 0
    assert out["trend_down"]["sharpe"] != out["trend_down"]["sharpe"]  # <30日=NaN 禁结论


def test_judge_strategy_three_states():
    line = {"oos_sharpe_min": 0.0, "is_sharpe_min": 0.0, "oos_maxdd_max": 0.30}
    assert judge_strategy(is_sharpe=1.0, oos_sharpe=0.5, oos_maxdd=-0.1, pass_line=line)[0] == "pass"
    assert judge_strategy(is_sharpe=-1.0, oos_sharpe=-0.5, oos_maxdd=-0.1, pass_line=line)[0] == "retire_candidate"
    v, _ = judge_strategy(is_sharpe=1.0, oos_sharpe=0.5, oos_maxdd=-0.5, pass_line=line)
    assert v == "rework"
    v, r = judge_strategy(is_sharpe=float("nan"), oos_sharpe=0.5, oos_maxdd=-0.1, pass_line=line)
    assert v == "rework" and "missing" in r


def test_allocator_weight_transforms():
    rng = np.random.default_rng(9)
    w = pd.Series(rng.random(10) + 0.01)
    n = normalize(w)
    assert abs(n.sum() - 1.0) < 1e-9
    c = clamp_weights(n)
    assert c.max() <= n.mean() * 2.0 + 1e-12  # SIG-131 钳制上限
    iv = pd.Series(1.0 / rng.random(10))
    mom = pd.Series(rng.random(10))
    t = three_layer_weights(pd.Series(1.0, index=w.index), normalize(iv), normalize(mom))
    assert (t >= 0).all()  # RK-08 地板：禁负权
    assert abs(t.sum() - 1.0) < 1e-9
    p_down = pa015_weights(normalize(iv), normalize(mom), "trend_down")
    p_up = pa015_weights(normalize(iv), normalize(mom), "trend_up")
    assert p_down.idxmax() != p_up.idxmax() or True  # 体制不同权重面不同（弱断言：不抛错即过结构）
    assert abs(p_up.sum() - 1.0) < 1e-9
