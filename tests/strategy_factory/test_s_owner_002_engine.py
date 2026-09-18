# [TEST] tests/strategy_factory/test_s_owner_002_engine.py
# [COVERS] zephyr.strategy_factory.owner_regime_switcher.engine; packages; costs
# [TTL] permanent
"""代理包信号+组合引擎单测（合成价格面板；PIT 时序/整数手/成本记账/敞口边界）。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.strategy_factory.owner_regime_switcher.engine import EngineConfig, run_leg
from zephyr.strategy_factory.owner_regime_switcher.packages import (
    PACKAGE_A_SYMBOL,
    package_a_targets,
    package_b_targets,
)
from zephyr.strategy_factory.owner_regime_switcher.switcher import baseline_schedule

SYMS = ["510050", "159915", "510300", "510500", "512100"]
N = 260


def _make_daily(seed: int = 7) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=N)
    daily: dict[str, pd.DataFrame] = {}
    for k, sym in enumerate(SYMS):
        drift = 0.0002 + 0.0001 * k
        ret = rng.normal(drift, 0.01, size=N)
        close = 5.0 * np.exp(np.cumsum(ret))
        open_ = np.roll(close, 1)
        open_[0] = close[0]
        amount = np.full(N, 5e8)  # 5 亿成交额（PIT 输入）
        daily[sym] = pd.DataFrame(
            {"open": open_, "high": close * 1.01, "low": close * 0.99, "close": close, "amount": amount},
            index=idx,
        )
    return daily


def _warm_panel(daily: dict[str, pd.DataFrame]) -> tuple[pd.Series, pd.DataFrame]:
    a_t = package_a_targets(daily[PACKAGE_A_SYMBOL]["close"])
    b_t = package_b_targets(pd.DataFrame({s: daily[s]["close"] for s in SYMS}))
    return a_t, b_t


def test_package_a_targets_ma_band() -> None:
    idx = pd.bdate_range("2024-01-02", periods=60)
    flat = pd.Series([10.0] * 60, index=idx)
    tgt = package_a_targets(flat)
    # 全平价序列 close==MA → 不严格大于 → 0
    assert (tgt == 0.0).all()
    rising = pd.Series(np.linspace(1.0, 20.0, 60), index=idx)
    tgt_up = package_a_targets(rising)
    assert tgt_up.iloc[-1] == 1.0
    assert tgt_up.iloc[18] == 0.0  # 预热段（MA 首 19 行不足窗口）=0；第 20 行起满窗生效
    assert tgt_up.iloc[19] == 1.0  # 单调升序下满窗首日 close>MA


def test_package_b_targets_top1_and_missing() -> None:
    idx = pd.bdate_range("2024-01-02", periods=40)
    panel = pd.DataFrame({s: np.linspace(1, 2, 40) for s in SYMS}, index=idx)
    panel["512100"] = np.nan  # 全程缺数据=无候选资格
    tgt = package_b_targets(panel, mom_window=5)
    # 上升斜率相同→动量同值；idxmax 取第一个列（确定性）；512100 恒 0
    held = tgt.sum(axis=1)
    assert (held <= 1.0).all()
    assert (tgt["512100"] == 0.0).all()
    # 单一标的强势 → top-1 切换正确
    panel2 = pd.DataFrame({s: np.linspace(1, 2, 40) for s in SYMS}, index=idx)
    panel2["159915"] = np.linspace(1, 4, 40)
    tgt2 = package_b_targets(panel2, mom_window=5)
    late = tgt2.iloc[30]
    assert late["159915"] == 1.0 and late.drop("159915").sum() == 0.0


def test_engine_baseline_runs_and_accounts() -> None:
    daily = _make_daily()
    a_t, b_t = _warm_panel(daily)
    start = str(daily[SYMS[0]].index[40].date())
    end = str(daily[SYMS[0]].index[-1].date())
    sched = baseline_schedule(daily[SYMS[0]].index)
    res = run_leg(sched, a_t, b_t, daily, sorted(SYMS), start, end, EngineConfig(), "base")
    assert res.nav.notna().all()
    assert np.isfinite(res.nav).all()
    assert res.metrics["trade_events"] > 0
    assert res.metrics["avg_gross_exposure"] > 0.5  # 基线满配
    assert res.metrics["avg_gross_exposure"] <= 2.0 + 1e-6  # 两包毛敞口上限
    assert 0.0 <= res.metrics["avg_gross_exposure"]
    # 整数手不变式不在此处检查（原注释声称的"结构性检查"实为 turnover>0，不构成手数判据）
    # → 专用判据见 test_engine_lots_are_integer_multiples_of_100_shares
    assert res.turnover_notional > 0
    # 指标族齐全
    for key in ("sharpe", "maxdd", "ann_return", "ann_turnover", "avg_gross_exposure", "trade_events"):
        assert key in res.metrics
    assert res.metrics["maxdd"] <= 0.0


def test_engine_pit_no_same_day_execution() -> None:
    """信号 t 收盘判定→t+1 开盘成交：构造 D1 收盘后跳空，验证建仓价=次日开盘。"""
    idx = pd.bdate_range("2024-01-02", periods=30)
    close = pd.Series([10.0] * 30, index=idx)
    close.iloc[15:] = 20.0  # D15 收盘暴涨 → MA 上穿信号在 D15 收盘判定
    daily = {
        PACKAGE_A_SYMBOL: pd.DataFrame(
            {"open": close.shift(1).fillna(10.0), "high": close, "low": close, "close": close, "amount": 5e8},
            index=idx,
        )
    }
    a_t = package_a_targets(close)
    assert a_t.iloc[19] == 1.0  # 满窗首日（MA20 需 20 行）即判定
    sched = baseline_schedule(idx)
    sched["cap_B"] = 0.0  # 只跑包 A，隔离时序断言
    res = run_leg(sched, a_t, pd.DataFrame(0.0, index=idx, columns=SYMS), daily, [PACKAGE_A_SYMBOL], str(idx[0].date()), str(idx[-1].date()), EngineConfig(), "pit")
    # 信号 idx19 收盘判定 → 最早 idx20 开盘成交；idx19 收盘前必须仍空仓（nav 平坦）
    nav19 = float(res.nav.iloc[19])
    nav18 = float(res.nav.iloc[18])
    assert abs(nav19 - nav18) < 1e-6  # 信号次日生效（idx19 当日无交易）
    nav20 = float(res.nav.iloc[20])
    assert nav20 != nav19  # idx20 开盘已按信号建仓


def test_engine_lots_are_integer_multiples_of_100_shares() -> None:
    """资金不变式钉：全部成交名义必须是 100 股整数手（补 R-037 在册测试盲区）。

    平价世界 close=open=13.3、100 万初始资金满仓：1e6/13.3=75187.97 股 →
    向下取整到 75100 股，成交名义恒为 100 股的整数倍。把 LOT_SIZE 拆成 1（碎股，
    A 股不可能成交的形态）即红——本钉的意义正在此。
    判据只用成交名义额，不涉及成本模型（对成本口径变更不敏感）。
    """
    px = 13.3
    idx = pd.bdate_range("2024-01-02", periods=30)
    flat = pd.Series([px] * len(idx), index=idx)
    daily = {
        PACKAGE_A_SYMBOL: pd.DataFrame(
            {"open": flat, "high": flat, "low": flat, "close": flat, "amount": 5e8}, index=idx
        )
    }
    a_t = pd.Series(1.0, index=idx)  # 全程满仓包 A（绕开 MA 预热，只看手数约束）
    sched = baseline_schedule(idx)
    sched["cap_A"] = 1.0
    sched["cap_B"] = 0.0
    res = run_leg(
        sched,
        a_t,
        pd.DataFrame(0.0, index=idx, columns=SYMS),
        daily,
        [PACKAGE_A_SYMBOL],
        str(idx[0].date()),
        str(idx[-1].date()),
        EngineConfig(),
        "lots",
    )
    shares_traded = res.turnover_notional / px
    assert shares_traded > 0  # 防空跑假绿（零成交也"整除"）
    assert abs(shares_traded - round(shares_traded)) < 1e-6  # 整数股
    assert round(shares_traded) % 100 == 0  # 整数手（100 股/手，冻结 §5 铁律）


def test_engine_cost_reduces_nav_on_churn() -> None:
    daily = _make_daily(seed=11)
    a_t, b_t = _warm_panel(daily)
    idx = daily[SYMS[0]].index
    start, end = str(idx[40].date()), str(idx[-1].date())
    sched = baseline_schedule(idx)
    base = run_leg(sched, a_t, b_t, daily, sorted(SYMS), start, end, EngineConfig(), "std")
    harsh = run_leg(sched, a_t, b_t, daily, sorted(SYMS), start, end, EngineConfig(slippage_scale=50.0), "harsh")
    assert harsh.nav.iloc[-1] < base.nav.iloc[-1]  # 极端成本必拖累
    assert np.isfinite(harsh.nav).all()


def test_scaled_schedule_rejects_out_of_range() -> None:
    from zephyr.strategy_factory.owner_regime_switcher.switcher import scaled_schedule

    idx = pd.bdate_range("2024-01-02", periods=5)
    base = baseline_schedule(idx)
    with pytest.raises(ValueError):
        scaled_schedule(base, 0.0)
    with pytest.raises(ValueError):
        scaled_schedule(base, 2.0)


def test_engine_rejects_bad_schedule() -> None:
    daily = _make_daily()
    a_t, b_t = _warm_panel(daily)
    idx = daily[SYMS[0]].index
    with pytest.raises(KeyError):
        run_leg(pd.DataFrame(index=idx), a_t, b_t, daily, sorted(SYMS), str(idx[40].date()), str(idx[-1].date()))
    with pytest.raises(ValueError):
        run_leg(baseline_schedule(idx), a_t, b_t, daily, sorted(SYMS), str(idx[40].date()), str(idx[-1].date()), EngineConfig(initial_capital=-1))
