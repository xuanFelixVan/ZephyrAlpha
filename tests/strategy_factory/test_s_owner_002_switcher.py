# [TEST] tests/strategy_factory/test_s_owner_002_switcher.py
# [COVERS] zephyr.strategy_factory.owner_regime_switcher.switcher
# [TTL] permanent
"""切换器核心单测：状态映射/滞后带/置信门/失败安全/PIT 语义/参数校验（合成数据，禁触生产库）。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from zephyr.strategy_factory.owner_regime_switcher.switcher import (
    DEFAULT_FAIL_SAFE_CAPS,
    DEFAULT_RANGE_CAPS,
    DEFAULT_TREND_DOWN_CAPS,
    DEFAULT_TREND_UP_CAPS,
    STATE_FAIL_SAFE,
    STATE_RANGE,
    STATE_TREND_DOWN,
    STATE_TREND_UP,
    SwitcherConfig,
    baseline_schedule,
    build_schedule,
    count_state_transitions,
    scaled_schedule,
)

D = pd.bdate_range("2024-01-01", periods=60)


def _snap(dates: list[str], dominants: list[str], confs: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {"trade_date": pd.to_datetime(dates), "dominant": dominants, "confidence": confs}
    )


def _caps_of(out: pd.DataFrame, day: int) -> tuple[float, float]:
    return float(out.iloc[day]["cap_A"]), float(out.iloc[day]["cap_B"])


def test_state_mapping_and_caps() -> None:
    cfg = SwitcherConfig()
    # 快照流覆盖整窗（每日 r3、conf 0.9；另加窗前一行）——否则陈旧度>M 进失败安全（语义使然）
    dates = ["2023-12-15"] + [str(d.date()) for d in D]
    snap = _snap(dates, ["r3"] * len(dates), [0.9] * len(dates))
    out = build_schedule(D, snap, cfg)
    # 起点热启动=取可见快照映射态（r3）；滞后带只门控后续翻转
    assert out.iloc[0]["state"] == STATE_TREND_UP
    # 第 30 日应为 trend_up、上限 {B:1.0}
    row30 = out.iloc[30]
    assert row30["state"] == STATE_TREND_UP
    assert _caps_of(out, 30) == (0.0, 1.0)  # {B:1.0}


def test_hysteresis_requires_n_consecutive_days() -> None:
    cfg = SwitcherConfig(hysteresis_days=5)
    # 第一天起就是 r1（range）；第 20 个交易日起 dominant 换 r3
    dates = [D[0] - pd.Timedelta(days=1)]
    doms = ["r1"]
    confs = [0.9]
    for i, d in enumerate(D):
        dates.append(d)
        doms.append("r3" if i >= 20 else "r1")
        confs.append(0.9)
    out = build_schedule(D, _snap([str(x) for x in dates], doms, confs), cfg)
    # 第 20 日（index 20）dominant 变 r3，PIT 下 index 21 才是第一个受影响执行日；
    # 连续 5 日候选 → 翻转最早发生在 index 21+5-1=25 的行（第 26 个交易日）
    states = out["state"].tolist()
    flipped_idx = next(i for i, s in enumerate(states) if s == STATE_TREND_UP)
    assert flipped_idx == 25
    for i in range(21, 25):
        assert states[i] == STATE_RANGE


def test_confidence_gate_low_conf_holds_state() -> None:
    cfg = SwitcherConfig(hysteresis_days=1)  # 关滞后带，隔离置信门语义
    # 快照流每日更新：窗前+全窗；D[30] 起 dominant=r3 但 conf=0.2（低置信=不确定）
    dates = ["2023-12-15"] + [str(d.date()) for d in D]
    doms = ["r1"] * (len(D) + 1)
    confs = [0.9] * (len(D) + 1)
    for i, d in enumerate(D):
        if i >= 30:
            doms[i + 1] = "r3"
            confs[i + 1] = 0.2
    out = build_schedule(D, _snap(dates, doms, confs), cfg)
    # 全程维持 range（不确定不构成翻转证据）
    assert (out["state"] == STATE_RANGE).all()


def test_fail_safe_on_missing_snapshots() -> None:
    cfg = SwitcherConfig(hysteresis_days=1, fail_safe_missing_days=5)
    # 只有窗口第一天之前一条快照：PIT 缺失累计 >5 日 → 失败安全
    out = build_schedule(D, _snap([str(D[0] - pd.Timedelta(days=3))], ["r1"], [0.9]), cfg)
    row = out.iloc[10]
    assert row["state"] == STATE_FAIL_SAFE
    assert _caps_of(out, 10) == (
        DEFAULT_FAIL_SAFE_CAPS["A"],
        DEFAULT_FAIL_SAFE_CAPS["B"],
    )
    assert bool(row["fail_safe"]) is True


def test_fail_safe_at_window_start() -> None:
    out = build_schedule(D, _snap([str(D[-1])], ["r1"], [0.9]), SwitcherConfig())
    assert out.iloc[0]["state"] == STATE_FAIL_SAFE


def test_trend_down_full_cash() -> None:
    cfg = SwitcherConfig(hysteresis_days=1)
    out = build_schedule(
        D,
        _snap([str(D[0] - pd.Timedelta(days=1))], ["r4"], [0.9]),
        cfg,
    )
    # 起点失败安全 → r4 滞后带（N=1）后进入 trend_down=全现金
    assert (out["state"] == STATE_TREND_DOWN).iloc[5]
    assert _caps_of(out, 5) == (
        DEFAULT_TREND_DOWN_CAPS.get("A", 0.0),
        DEFAULT_TREND_DOWN_CAPS.get("B", 0.0),
    )


def test_unknown_state_and_nan_are_uncertain() -> None:
    cfg = SwitcherConfig(hysteresis_days=1)
    # 快照流每日更新：窗前 r1 0.9；D[20] 起 dominant=r99（未知）与 NaN 置信交替
    dates = ["2023-12-15"] + [str(d.date()) for d in D]
    doms: list[object] = ["r1"] * (len(D) + 1)
    confs: list[object] = [0.9] * (len(D) + 1)
    for i, d in enumerate(D):
        if i >= 20:
            doms[i + 1] = "r99" if i % 2 == 0 else "r1"
            confs[i + 1] = np.nan
    snap = pd.DataFrame({"trade_date": pd.to_datetime(dates), "dominant": doms, "confidence": confs})
    out = build_schedule(D, snap, cfg)
    # 未知态 + NaN 置信 = 不确定 = 维持 range
    assert (out["state"] == STATE_RANGE).all()


def test_validate_rejects_bad_configs() -> None:
    with pytest.raises(ValueError):
        SwitcherConfig(trend_up_states=frozenset({"r1", "r3"})).validate()
    with pytest.raises(ValueError):
        SwitcherConfig(trend_up_caps={"B": 1.5}).validate()
    with pytest.raises(ValueError):
        SwitcherConfig(hysteresis_days=0).validate()


def test_pit_strictly_before() -> None:
    """快照日期当日的调度不得包含该快照（严格 <t）。"""
    cfg = SwitcherConfig(hysteresis_days=1)
    # 唯一快照=D[10]：D[10] 当日仍不可见（须 D[11] 起生效）
    out = build_schedule(D, _snap([str(D[10])], ["r3"], [0.9]), cfg)
    assert out.iloc[10]["state"] != STATE_TREND_UP
    assert out.iloc[min(11 + 0, len(D) - 1)]["state"] == STATE_TREND_UP  # N=1 → 次日翻转


def test_baseline_and_scaling() -> None:
    base = baseline_schedule(D)
    assert (base["cap_A"] == 1.0).all() and (base["cap_B"] == 1.0).all()
    scaled = scaled_schedule(base, 0.4)
    assert np.allclose(scaled["cap_A"], 0.4)
    with pytest.raises(ValueError):
        scaled_schedule(base, 1.5)


def test_transition_counter() -> None:
    cfg = SwitcherConfig(hysteresis_days=5)
    doms = ["r1", "r3", "r1", "r4"]
    dates = []
    confs = []
    for i, d in enumerate(D):
        dates.append(str(d))
        doms.append(doms[i % 4] if i < 8 else doms[min(i // 20, 3)])
        confs.append(0.9)
    snap = _snap(dates, [doms[i] for i in range(len(D))], confs)
    out = build_schedule(D, snap, cfg)
    assert count_state_transitions(out) >= 1
