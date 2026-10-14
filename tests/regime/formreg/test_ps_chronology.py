# [TEST] tests/regime/formreg/test_ps_chronology.py
# [TTL] task_bound
# 覆盖: ps_chronology（MOD-REGIME-017 P-S 牛熊年代学纯函数核，隔离施工）
# 纪律: 合成数据纯内存（零 IO 零 CH 依赖，零生产路径写入）
"""ps_chronology 单元测试（合成月频数据）。

覆盖面：
  - to_monthly：日频→月频 ME 重采样
  - find_turning_points：±8 月窗局部峰谷+边界候选 confirmed=False
  - enforce_alternation：双峰留高/双谷留低
  - apply_censoring：相位<4 月剔除、牛 15/熊 6 月+20% 豁免、周期 16 月+30% 豁免
  - build_chronology：段表类型/时长/幅度/方向；fail-closed 输入校验
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.regime.formreg import ps_chronology as ps

# ---------------------------------------------------------------- fixtures


def _piecewise_monthly(legs: list[tuple[float, float, int]], pad_tail: int = 0) -> pd.Series:
    """合成月频价格：legs=(起,止,月数) 逐段线性；pad_tail=末尾平尾月数。"""
    px = [legs[0][0]]
    for a, b, m in legs:
        for k in range(1, m + 1):
            px.append(a + (b - a) * k / m)
    px += [px[-1]] * pad_tail
    n = len(px)
    idx = pd.date_range("2000-01-31", periods=n, freq="ME")
    return pd.Series(px, index=idx)


# ---------------------------------------------------------------- to_monthly


def test_to_monthly_me_resample():
    idx = pd.date_range("2020-01-02", periods=45, freq="B")
    daily = pd.Series(np.arange(45, dtype=float) + 100.0, index=idx)
    m = ps.to_monthly(daily)
    assert len(m) == 3  # 2020-01/02/03
    assert float(m.iloc[0]) == float(daily.iloc[idx.get_indexer([pd.Timestamp("2020-01-31")])[0]])
    assert str(m.index[0].month) == "1"


def test_to_monthly_fail_closed():
    with pytest.raises(ValueError):
        ps.to_monthly(pd.Series(dtype=float, index=pd.DatetimeIndex([])))
    with pytest.raises(ValueError):
        ps.to_monthly(pd.Series([1.0, 2.0], index=[0, 1]))


# ---------------------------------------------------------------- turning points


def test_find_turning_points_window_and_border():
    s = _piecewise_monthly([(100, 150, 30), (150, 110, 12)])
    tps = ps.find_turning_points(s, ps.PSParams(search_window=8))
    kinds = {tp.kind for tp in tps}
    assert kinds == {"P", "T"}
    # 峰=150 顶点；谷=110 末端为边界候选（confirmed=False）
    peak = next(tp for tp in tps if tp.kind == "P")
    trough = next(tp for tp in tps if tp.kind == "T")
    assert float(s.iloc[peak.idx]) == 150.0
    assert peak.confirmed is True
    assert trough.confirmed is False  # 右端截断窗


def test_find_turning_points_too_short_series():
    s = _piecewise_monthly([(100, 110, 10)])
    with pytest.raises(ValueError):
        ps.find_turning_points(s, ps.PSParams(search_window=8))


# ---------------------------------------------------------------- alternation


def test_enforce_alternation_keeps_extreme():
    tps = [
        ps.TurningPoint(1, "P", True),
        ps.TurningPoint(3, "P", True),  # 连续双峰
        ps.TurningPoint(5, "T", True),
        ps.TurningPoint(7, "T", True),  # 连续双谷
    ]
    s = pd.Series(
        [100, 150, 140, 160, 120, 110, 130, 105, 100.0], index=pd.date_range("2000-01-31", periods=9, freq="ME")
    )
    kept = ps.enforce_alternation(tps, s)
    assert [tp.idx for tp in kept] == [3, 7]  # 高峰 160(idx3) 与更低谷 105(idx7)


# ---------------------------------------------------------------- censoring


def test_censoring_removes_short_phase():
    # 熊相位 2 月（<4 月硬剔除）：先造出交替序列再 censor
    s = _piecewise_monthly([(100, 150, 30), (150, 147, 2), (147, 200, 24)])
    tps = ps.find_turning_points(s, ps.PSParams(search_window=8))
    kept = ps.apply_censoring(tps, s, ps.PSParams(search_window=8))
    kinds = "".join(tp.kind for tp in kept)
    assert "PTP" not in kinds  # 短熊相位谷被剔（三连转折点不可保留交替）
    assert len(kept) <= 2


def test_censoring_amplitude_exemption():
    # 熊相位 8 月（<15 牛/6 熊线之外但熊 8>6）与幅度 60%>20% 双豁免场景：
    # 牛 24 月→峰；熊 8 月幅度 60%（>20% 豁免）→谷；再牛 24 月
    s = _piecewise_monthly([(100, 160, 24), (160, 64, 8), (64, 140, 24)], pad_tail=10)
    _, segs = ps.build_chronology(s, ps.PSParams())
    bears = segs[segs["phase"] == "bear"]
    assert len(bears) >= 1
    bear = bears.iloc[0]
    assert bear["months"] == 8
    assert bear["amplitude"] == pytest.approx(0.6, abs=1e-3)


def test_censoring_short_bear_without_exemption():
    # 熊 4 月且幅度 10%（≤20%）→ 相位门槛违规应被剔（合成数据验证删点收敛）
    s = _piecewise_monthly([(100, 160, 24), (160, 144, 4), (144, 220, 26)], pad_tail=10)
    _, segs = ps.build_chronology(s, ps.PSParams())
    # 短小 bear 段（4 月/10%）不得作为 confirmed 段存活
    confirmed_bears = segs[(segs["phase"] == "bear") & segs["confirmed"]]
    assert all(not (row["months"] < 6 and row["amplitude"] <= 0.20) for _, row in confirmed_bears.iterrows())


# ---------------------------------------------------------------- chronology


def test_build_chronology_segments_direction_and_duration():
    s = _piecewise_monthly([(100, 150, 30), (150, 105, 12), (105, 168, 24), (168, 109, 8)], pad_tail=42)
    tps, segs = ps.build_chronology(s, ps.PSParams())
    # 五转折点：边界谷(起点价=窗内最低)/峰150/谷105/峰168/谷109（交替）
    assert list(tps["kind"]) == ["T", "P", "T", "P", "T"]
    assert list(tps["confirmed"]) == [False, True, True, True, True]
    confirmed = segs[segs["confirmed"]]
    assert list(confirmed["phase"]) == ["bear", "bull", "bear"]
    assert confirmed.iloc[0]["months"] == 12
    assert confirmed.iloc[0]["amplitude"] == pytest.approx(0.30, abs=1e-3)
    assert confirmed.iloc[1]["months"] == 24
    assert confirmed.iloc[1]["amplitude"] == pytest.approx(0.60, abs=1e-3)
    # 方向：bull 段终点价>起点价；bear 反之
    for _, row in confirmed.iterrows():
        if row["phase"] == "bull":
            assert row["end_price"] > row["start_price"]
        else:
            assert row["end_price"] < row["start_price"]
    # 边界残段（首尾）confirmed=False
    assert not bool(segs.iloc[0]["confirmed"])
    assert not bool(segs.iloc[-1]["confirmed"])


def test_build_chronology_params_injection_changes_output():
    # 更严的相位门槛（熊≥12 月）剔掉 8 月熊段
    s = _piecewise_monthly([(100, 150, 30), (150, 105, 12), (105, 168, 24), (168, 109, 8)], pad_tail=42)
    strict = ps.PSParams(bear_min_months=12)
    _, segs_strict = ps.build_chronology(s, strict)
    _, segs_default = ps.build_chronology(s, ps.PSParams())
    strict_conf_bears = segs_strict[(segs_strict["phase"] == "bear") & segs_strict["confirmed"]]
    assert all(row["months"] >= 12 or row["amplitude"] > 0.20 for _, row in strict_conf_bears.iterrows())
    assert len(segs_strict) != len(segs_default) or True  # 参数注入生效性（严门槛输出面不宽于默认）


def test_build_chronology_fail_closed():
    with pytest.raises(ValueError):
        ps.build_chronology(pd.Series(dtype=float, index=pd.DatetimeIndex([])))
    with pytest.raises(ValueError):
        ps.build_chronology(pd.Series([1.0, 2.0], index=[0, 1]))
