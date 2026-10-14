# [TEST] tests/regime/formreg/test_cusum_two_sided.py
# [TTL] task_bound
# 覆盖: cusum_two_sided（MOD-REGIME-017 双边 CUSUM 拐点检测，单边先例对称扩展，隔离施工）
# 纪律: 合成数据纯内存（零 IO 零 CH 依赖，零生产路径写入）
"""cusum_two_sided 单元测试（合成均值漂移数据）。

覆盖面：
  - 双边方向：上行漂移出 up 告警、下行漂移出 down 告警
  - 三元组契约：位置/方向/严重度（severity=越阈侧 CU 累积量>h）
  - 告警后重置：事件流语义（持续漂移段重复告警、间隔有界）
  - σ=0 降级：degraded 显式标记不抛错（挖矿簿 4 坑 1）
  - fail-closed：空序列/非 DatetimeIndex/非升序/非法 baseline
"""

from __future__ import annotations

from itertools import pairwise

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.formreg import cusum_two_sided as cs

# ---------------------------------------------------------------- fixtures


def _shifted_series(seed: int = 7) -> pd.Series:
    rng = np.random.default_rng(seed)
    x = np.concatenate(
        [
            rng.normal(0.0, 0.2, 100),
            rng.normal(1.0, 0.2, 100),
            rng.normal(-1.0, 0.2, 100),
        ]
    )
    idx = pd.date_range("2015-01-02", periods=300, freq="B")
    return pd.Series(x, index=idx)


# ---------------------------------------------------------------- 双边方向


def test_two_sided_directions():
    res = cs.detect_turning_events(_shifted_series(), baseline=0.0)
    assert not res.degraded
    ev = res.events
    assert len(ev) > 0
    up_events = ev[ev["direction"] == "up"]
    down_events = ev[ev["direction"] == "down"]
    assert len(up_events) > 0 and len(down_events) > 0
    # 上行告警集中于第二段（位置 100-200），下行集中于第三段（200-300）
    assert up_events["position"].min() >= 100
    assert up_events["position"].max() < 200
    assert down_events["position"].min() >= 200
    # 基线段（0-100）零告警
    assert ev["position"].min() >= 100


def test_triple_contract_severity_exceeds_h():
    res = cs.detect_turning_events(_shifted_series(), baseline=0.0)
    h = res.h_eff
    assert h > 0
    for _, row in res.events.iterrows():
        assert row["severity"] > h
        if row["direction"] == "up":
            assert row["s_plus"] == row["severity"]
        else:
            assert row["s_minus"] == row["severity"]
        assert row["date"]  # 位置字段（date+position）非空


def test_reset_on_alarm_bounded_event_rate():
    """重置语义：告警后归零→持续漂移段周期性再告警（间隔>1，无每步连发）；
    关重置→统计量饱和后每步都告警（无界洪泛）→事件数多于重置版。"""
    res = cs.detect_turning_events(_shifted_series(), baseline=0.0)
    positions = res.events["position"].tolist()
    assert all(b - a > 1 for a, b in pairwise(positions))
    p = cs.CusumTwoSidedParams(reset_on_alarm=False)
    res2 = cs.detect_turning_events(_shifted_series(), baseline=0.0, params=p)
    assert len(res2.events) > len(res.events)


def test_tracks_nonnegative_and_nan_skip():
    s = _shifted_series()
    s.iloc[50] = np.nan
    res = cs.detect_turning_events(s, baseline=0.0)
    assert bool((res.s_plus.dropna() >= 0).all())
    assert bool((res.s_minus.dropna() >= 0).all())
    assert np.isnan(res.s_plus.iloc[50])


# ---------------------------------------------------------------- 参数与降级


def test_params_injection_scales_threshold():
    s = _shifted_series()
    tight = cs.detect_turning_events(s, baseline=0.0, params=cs.CusumTwoSidedParams(h_sigma=10.0))
    loose = cs.detect_turning_events(s, baseline=0.0, params=cs.CusumTwoSidedParams(h_sigma=1.0))
    assert len(tight.events) < len(loose.events)
    assert tight.h_eff == pytest.approx(10.0 * loose.h_eff, rel=1e-9)


def test_sigma_zero_degraded_not_silent():
    idx = pd.date_range("2015-01-02", periods=50, freq="B")
    flat = pd.Series(3.14, index=idx)  # 常数序列 σ=0
    res = cs.detect_turning_events(flat, baseline=0.0)
    assert res.degraded is True
    assert len(res.events) == 0  # 降级显式：有标记、无告警、不抛错


# ---------------------------------------------------------------- fail-closed


def test_fail_closed_inputs():
    idx = pd.date_range("2015-01-02", periods=10, freq="B")
    s = pd.Series(np.arange(10.0), index=idx)
    with pytest.raises(ValueError):
        cs.detect_turning_events(pd.Series(dtype=float, index=pd.DatetimeIndex([])), baseline=0.0)
    with pytest.raises(ValueError):
        cs.detect_turning_events(pd.Series([1.0, 2.0], index=[0, 1]), baseline=0.0)
    with pytest.raises(ValueError):
        cs.detect_turning_events(s.iloc[::-1], baseline=0.0)  # 非升序
    with pytest.raises(ValueError):
        cs.detect_turning_events(s, baseline=float("nan"))
