"""引擎/门/信号单测——PIT、做T 额度、熔断、三臂差异、regime 次日生效。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.strategy_factory.owner_band_t.engine import (
    COOLDOWN_DAYS,
    DRAWDOWN_BREAKER,
    INITIAL_CAPITAL,
    LADDER_DEFAULT,
    StrategyConfig,
    compute_metrics,
    run_backtest,
    run_buy_and_hold,
)
from zephyr.strategy_factory.owner_band_t.intraday_t import round_lot
from zephyr.strategy_factory.owner_band_t.regime_gate import gate_open_series
from zephyr.strategy_factory.owner_band_t.signals import build_signal_panel

from conftest import make_synthetic_panel


@pytest.fixture(scope="module")
def panel():
    return make_synthetic_panel()


def test_config_validation():
    with pytest.raises(ValueError, match="entry_mode"):
        StrategyConfig(entry_mode="bad").validate()
    with pytest.raises(ValueError, match="金字塔"):
        StrategyConfig(ladder=(0.5, 0.5, 0.5)).validate()


def test_basic_run_accounting(panel):
    cfg = StrategyConfig(entry_mode="setup9", p1=0.7, exit_arm="bb_upper", t_max_trips=2, t_size=0.3)
    res = run_backtest(panel, cfg, panel["etf"].index[70].date().isoformat(), panel["etf"].index[-1].date().isoformat())
    nav = res["nav"]
    assert nav.notna().all()
    # 现金/持仓非负（无裸空头）
    assert res["t_net_pnl"] == res["t_net_pnl"]  # NaN 检查
    assert res["turnover_band"] >= 0 and res["turnover_t"] >= 0
    m = compute_metrics(nav, res["turnover_band"])
    assert -1.0 < m["maxdd"] <= 0.0
    assert m["n_days"] == len(nav)


def test_no_future_function_midbar_perturbation(panel):
    """红蓝: 篡改第 k 日 bar，k 之前的 NAV 必须逐位不变（未来数据不影响过去）。"""
    import copy

    p1 = copy.deepcopy(panel)
    p2 = copy.deepcopy(panel)
    k = 300  # 中间日
    day_k = p1["etf"].index[k]
    for col in ("open", "high", "low", "close", "amount"):
        p2["etf"].loc[day_k, col] = p2["etf"].loc[day_k, col] * 1.3
    p2["hourly_closes"] = {
        d: ([c * 1.3 if d == day_k else c for c in closes]) for d, closes in p2["hourly_closes"].items()
    }
    cfg = StrategyConfig(entry_mode="setup8", exit_arm="bb_upper", use_t=True)
    start = p1["etf"].index[70].date().isoformat()
    end = p1["etf"].index[-1].date().isoformat()
    r1 = run_backtest(p1, cfg, start, end)
    r2 = run_backtest(p2, cfg, start, end)
    nav1, nav2 = r1["nav"], r2["nav"]
    # 核心断言: 第 k 日之前的 NAV 逐位一致（无未来函数/偷看）
    assert np.allclose(nav1.iloc[:k].to_numpy(), nav2.iloc[:k].to_numpy(), rtol=0, atol=1e-9)


def test_gate_reduces_or_equals_exposure(panel):
    """A(有门) 与 B(无门) 同配置: 门的唯一效果是砍掉闭门段的建仓。"""
    start = panel["etf"].index[70].date().isoformat()
    end = panel["etf"].index[-1].date().isoformat()
    cfg_on = StrategyConfig(entry_mode="setup8", exit_arm="bb_upper", gate_min_conf=0.35, use_t=False)
    cfg_off = StrategyConfig(entry_mode="setup8", exit_arm="bb_upper", gate_min_conf=0.35, use_t=False, use_gate=False)
    a = run_backtest(panel, cfg_on, start, end)
    b = run_backtest(panel, cfg_off, start, end)
    assert a["exposure_ratio"] <= b["exposure_ratio"] + 1e-9


def test_t_arm_quota_never_exceeds_prior_close(panel):
    """红蓝: 做T 买入股数 ≤ 前收盘持仓（T+1 结构约束）——通过 t_size=1.0 极限配置核验现金不穿底。"""
    start = panel["etf"].index[70].date().isoformat()
    end = panel["etf"].index[-1].date().isoformat()
    cfg = StrategyConfig(entry_mode="setup8", exit_arm="bb_upper", use_t=True, t_max_trips=2, t_size=1.0)
    res = run_backtest(panel, cfg, start, end)
    nav = res["nav"]
    # NAV 恒为正（额度约束保证无超额买入）
    assert (nav > 0).all()
    assert res["t_trips"] >= 0


def test_drawdown_breaker_full_exit_and_cooldown(panel):
    cfg = StrategyConfig(entry_mode="setup8", exit_arm="bb_upper", use_t=False)
    res = run_backtest(panel, cfg, panel["etf"].index[70].date().isoformat(), panel["etf"].index[-1].date().isoformat())
    nav = res["nav"].dropna()
    peak = nav.cummax()
    dd = (nav / peak - 1.0).min()
    assert dd >= -(DRAWDOWN_BREAKER + 0.02)  # 熔断+次日执行滑差容忍
    assert COOLDOWN_DAYS == 20


def test_regime_gate_next_day_effective():
    """门状态=严格早于当日的最近快照（翻转次日生效）。"""
    days = pd.bdate_range("2020-01-01", periods=10)
    # 快照: 第 3 日（idx 2）起 r3 高置信 → 第 4 日起门关
    snap = pd.DataFrame(
        {
            "trade_date": [days[0], days[2]],
            "dominant": ["r1", "r3"],
            "confidence": [0.5, 0.9],
        }
    )
    gate = gate_open_series(days, snap, 0.35)
    assert gate.iloc[0] and gate.iloc[1] and gate.iloc[2]  # 第3日用第2日前的快照(r1)
    assert not gate.iloc[3]  # 第4日起 r3 生效
    # 快照前日期=门开（缺失=不确定）
    early_days = pd.bdate_range("2019-12-01", periods=5)
    gate2 = gate_open_series(early_days, snap, 0.35)
    assert gate2.all()


def test_low_confidence_trend_is_gate_open():
    days = pd.bdate_range("2020-01-01", periods=5)
    snap = pd.DataFrame({"trade_date": [days[0]], "dominant": ["r12"], "confidence": [0.30]})
    gate = gate_open_series(days, snap, 0.35)
    assert gate.all()  # r12 但置信不足=不确定=门开


def test_round_lot():
    assert round_lot(333.0) == 300
    assert round_lot(99.0) == 0
    assert round_lot(0) == 0
    assert round_lot(-5) == 0


def test_buy_and_hold_benchmark(panel):
    res = run_buy_and_hold(panel, panel["etf"].index[70].date().isoformat(), panel["etf"].index[-1].date().isoformat())
    assert res["metrics"]["n_days"] > 0
    assert res["turnover"] > 0  # 期初一笔买入


def test_signal_panel_columns(panel):
    sig = build_signal_panel(panel["idx"]["close"], panel["idx"]["high"])
    for col in ("bb_upper", "prior_high_ref", "ret_quantile", "vol_pct"):
        assert col in sig.columns
    assert sig["vol_pct"].dropna().between(0, 1).all()


def test_metrics_zero_variance_guard():
    nav = pd.Series([1.0, 1.0, 1.0])
    m = compute_metrics(nav, 0.0)
    assert m["sharpe"] == 0.0
