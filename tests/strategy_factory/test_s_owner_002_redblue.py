# [TEST] tests/strategy_factory/test_s_owner_002_redblue.py
# [COVERS] zephyr.strategy_factory.owner_regime_switcher.exam（红蓝对抗面）
# [TTL] permanent
"""红蓝对抗（冻结 §7）：regime 乱序注入/状态日频抖动/切换成本极端化/NaN 注入 + bootstrap 自检。

全部合成数据（测试隔离铁律：禁写 data/ 业务目录；本文件零生产库依赖）。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from zephyr.strategy_factory.owner_regime_switcher.engine import EngineConfig, run_leg
from zephyr.strategy_factory.owner_regime_switcher.exam import (
    _run_window,
    bootstrap_sharpe_diff,
)
from zephyr.strategy_factory.owner_regime_switcher.packages import PACKAGE_A_SYMBOL, package_a_targets, package_b_targets
from zephyr.strategy_factory.owner_regime_switcher.switcher import (
    STATE_FAIL_SAFE,
    SwitcherConfig,
    build_schedule,
    count_state_transitions,
)

SYMS = ["510050", "159915", "510300", "510500", "512100"]
N = 300
STATES = ["r1", "r2", "r3", "r4", "r10", "r11", "r12"]


def _make_world(seed: int = 23) -> tuple[pd.DatetimeIndex, dict[str, pd.DataFrame]]:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2023-01-02", periods=N)
    daily: dict[str, pd.DataFrame] = {}
    for k, sym in enumerate(SYMS):
        ret = rng.normal(0.0003 + 0.0001 * k, 0.012, size=N)
        close = 5.0 * np.exp(np.cumsum(ret))
        open_ = np.roll(close, 1)
        open_[0] = close[0]
        daily[sym] = pd.DataFrame(
            {"open": open_, "high": close * 1.01, "low": close * 0.99, "close": close, "amount": np.full(N, 4e8)},
            index=idx,
        )
    return idx, daily


def _snapshot_stream(idx: pd.DatetimeIndex, dominators: list[str], confs: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"trade_date": idx, "dominant": dominators, "confidence": confs})


def _targets(daily: dict[str, pd.DataFrame]) -> tuple[pd.Series, pd.DataFrame]:
    a_t = package_a_targets(daily[PACKAGE_A_SYMBOL]["close"])
    b_t = package_b_targets(pd.DataFrame({s: daily[s]["close"] for s in SYMS}))
    return a_t, b_t


def test_red1_shuffled_regime_sequence() -> None:
    """红蓝①: regime 状态值跨日期乱序注入（置换 dominant 序列）→ 调度器不崩溃且产出显著不同。"""
    idx, daily = _make_world()
    rng = np.random.default_rng(5150)
    # 块状持续态（每 25 日换一态）——滞后带下两版调度都脱离失败安全、有真实状态机运转
    doms = [STATES[i // 25 % 7] for i in range(N)]
    confs = [0.8] * N
    snap_clean = _snapshot_stream(idx, doms, confs)
    doms_shuf = list(np.array(doms)[rng.permutation(N)])  # 值置换：日期不动、状态序列乱序
    snap_shuffled = _snapshot_stream(idx, doms_shuf, confs)
    trade_days = idx[40:]
    out_clean = build_schedule(trade_days, snap_clean, SwitcherConfig())
    out_shuf = build_schedule(trade_days, snap_shuffled, SwitcherConfig())
    assert len(out_clean) == len(out_shuf) > 0
    assert (out_clean["state"] != STATE_FAIL_SAFE).any()  # 块状态流确已驱动状态机
    same = (out_clean["state"].to_numpy() == out_shuf["state"].to_numpy()).mean()
    assert same < 0.99  # 乱序必改变调度（非崩溃、非恒等）
    a_t, b_t = _targets(daily)
    start, end = str(trade_days[0].date()), str(trade_days[-1].date())
    res = run_leg(out_shuf, a_t, b_t, daily, sorted(SYMS), start, end, EngineConfig(), "shuffled")
    assert np.isfinite(res.nav).all()


def test_red2_state_jitter_suppressed_by_hysteresis() -> None:
    """红蓝②: dominant 逐日交替抖动 → 滞后带抑制，翻转次数 ≤ 天数/N+2。"""
    idx = pd.bdate_range("2024-01-02", periods=200)
    doms = [STATES[i % 2] for i in range(200)]  # r1/r3 逐日交替
    snap = _snapshot_stream(idx, doms, [0.9] * 200)
    n = 5
    out = build_schedule(idx, snap, SwitcherConfig(hysteresis_days=n))
    flips = count_state_transitions(out)
    assert flips <= len(idx) // n + 2


def test_red3_extreme_switching_cost() -> None:
    """红蓝③: 滑点×50 极端化 → 两腿照常出数且切换腿退化幅度可观测。"""
    idx, daily = _make_world(seed=31)
    rng = np.random.default_rng(7)
    # 抖动状态流制造高换手场景
    doms = [STATES[int(rng.integers(0, 7))] for _ in range(N)]
    snap = _snapshot_stream(idx, doms, [0.9] * N)
    a_t, b_t = _targets(daily)
    trade_days = idx[40:]
    start, end = str(trade_days[0].date()), str(trade_days[-1].date())
    sched = build_schedule(trade_days, snap, SwitcherConfig(hysteresis_days=3))
    base_cfg = EngineConfig()
    harsh_cfg = EngineConfig(slippage_scale=50.0)
    on_std = run_leg(sched, a_t, b_t, daily, sorted(SYMS), start, end, base_cfg, "std")
    on_harsh = run_leg(sched, a_t, b_t, daily, sorted(SYMS), start, end, harsh_cfg, "harsh")
    assert np.isfinite(on_std.nav).all() and np.isfinite(on_harsh.nav).all()
    assert on_harsh.nav.iloc[-1] < on_std.nav.iloc[-1]  # 成本极端化必拖累


def test_red4_nan_injection_no_crash() -> None:
    """红蓝④: dominant/confidence NaN 注入 → 不确定处理，禁崩溃。"""
    idx = pd.bdate_range("2024-01-02", periods=120)
    doms = [STATES[i % 7] for i in range(120)]
    confs = [0.9] * 120
    snap = _snapshot_stream(idx, doms, confs)
    dirty = snap.copy()
    dirty.loc[10:30, "dominant"] = np.nan
    dirty.loc[40:60, "confidence"] = np.nan
    out = build_schedule(idx, dirty, SwitcherConfig(hysteresis_days=1))
    assert out["state"].notna().all()
    assert out["cap_A"].between(0, 1).all() and out["cap_B"].between(0, 1).all()


def test_bootstrap_ci_sanity() -> None:
    """bootstrap 自检: 恒同序列 CI 含 0；恒正差序列 CI 不含 0。"""
    rng = np.random.default_rng(42)
    n = 300
    r_b = pd.Series(rng.normal(0.0002, 0.01, n))
    r_a_zero = r_b.copy()
    (s_lo, s_hi), (m_lo, m_hi) = bootstrap_sharpe_diff(r_a_zero, r_b, draws=300)
    assert s_lo <= 0.0 <= s_hi
    assert m_lo <= 0.0 <= m_hi
    r_a_pos = r_b + 0.002  # 恒正差
    (s_lo2, s_hi2), (m_lo2, m_hi2) = bootstrap_sharpe_diff(r_a_pos, r_b, draws=300)
    assert s_lo2 > 0.0 and m_lo2 > 0.0


def test_dualrun_window_harness() -> None:
    """_run_window 全链路（合成快照+合成面板）: 三腿产出齐全+CI 元组形状正确。"""
    idx, daily = _make_world(seed=77)
    rng = np.random.default_rng(3)
    doms = [STATES[int(rng.integers(0, 7))] for _ in range(N)]
    snap = _snapshot_stream(idx, doms, [0.9] * N)
    a_t, b_t = _targets(daily)
    trade_days = idx[40:]
    start, end = str(trade_days[0].date()), str(trade_days[-1].date())
    res = _run_window("IS", start, end, snap, daily, a_t, b_t, sorted(SYMS))
    assert res.switcher.metrics["trade_events"] >= 0
    assert res.baseline.metrics["avg_gross_exposure"] > 0
    assert 0.0 < res.matched_scalar <= 1.0
    lo, hi = res.sharpe_diff_ci
    assert lo <= hi
    assert len(res.switcher.nav) == len(res.baseline.nav) == len(res.matched.nav)
