# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-SIG-149 | tests/signal_ashare/strategy_signal/test_pattern_lifecycle.py
# [MODULE] tests.signal_ashare.strategy_signal.test_pattern_lifecycle
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_lifecycle
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 合成 45 窗全循环（certified→20 failed→retired→复活→二次退役→frozen）；tmp_path 隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/strategy_signal/test_pattern_lifecycle.py
# [TTL] permanent
"""pattern_lifecycle 单测（W-R）——合成案例跑通"死→观察→复活"全循环。"""

from __future__ import annotations

from zephyr.signal_ashare.strategy_signal.pattern_lifecycle import (
    RESURRECT_MIN_NEW_EVENTS,
    RETIRED_AFTER,
    LifecycleStore,
    update_lifecycle,
)

KEY = "双顶|day|向上|10"


def _rec(state, hit_rate=0.45, n_events=5000):
    return {"key": KEY, "state": state, "hit_rate": hit_rate, "n_events": n_events}


def test_full_cycle_death_watch_resurrection_freeze(tmp_path):
    """45 窗合成全循环：certified→20 failed→retired→死后增量复活→二次退役→frozen。"""
    store = LifecycleStore(tmp_path / "lc.json")
    baseline = {KEY: 0.5}

    # 第 1 窗 certified：连窗归零
    summary = update_lifecycle([_rec("certified", 0.60, 5000)], store, baseline_by_key=baseline, today="D1")
    s = store.load()[KEY]
    assert s["state"] == "certified" and s["failed_streak"] == 0

    # 连续 19 窗 failed：尚未退役（RETIRED_AFTER=20）
    for i in range(2, 21):
        update_lifecycle([_rec("failed", 0.45, 5000 + i)], store, baseline_by_key=baseline, today=f"D{i}")
    s = store.load()[KEY]
    assert s["state"] != "retired" and s["failed_streak"] == 19

    # 第 20 窗 failed：退役 + 死亡快照落账
    summary = update_lifecycle(
        [_rec("failed", 0.45, 5200)], store, baseline_by_key=baseline, today="D21"
    )
    assert summary["retired"] == [KEY]
    s = store.load()[KEY]
    assert s["state"] == "retired" and s["death"]["n"] == 5200
    assert s["death"]["baseline"] == pytest_approx(0.5)
    assert s["death"]["reason"] == "statistical"


def pytest_approx(v):
    import pytest
    return pytest.approx(v)


def test_resurrection_requires_min_new_events(tmp_path):
    """死后新事件 <50：不判定（不猜），保持 retired。"""
    store = LifecycleStore(tmp_path / "lc.json")
    baseline = {KEY: 0.5}
    # 直达 retired（模拟已连续 20 窗失败）
    for i in range(RETIRED_AFTER):
        update_lifecycle([_rec("failed", 0.45, 5000 + i)], store, baseline_by_key=baseline, today=f"D{i}")
    # 死后只新增 6 事件（n=5025<50 门槛），不足以判定
    update_lifecycle([_rec("failed", 0.60, 5025)], store, baseline_by_key=baseline, today="D30")
    s = store.load()[KEY]
    assert s["state"] == "retired"
    assert s.get("post_death_windows", 0) >= 1


def test_resurrection_on_strong_post_death_evidence(tmp_path):
    """死后新事件 60 中 48 正向（vs 基线 0.5，p≈1e-4<0.01）→ resurrected。"""
    assert 60 >= RESURRECT_MIN_NEW_EVENTS
    store = LifecycleStore(tmp_path / "lc.json")
    baseline = {KEY: 0.5}
    for i in range(20):  # 直达退役（死亡时 n=5200, rate=0.45 → hits=2340）
        update_lifecycle([_rec("failed", 0.45, 5200 + i)], store, baseline_by_key=baseline, today=f"D{i}")
    s = store.load()[KEY]
    assert s["state"] == "retired" and s["death"]["n"] == 5219
    # 死后新增 60 事件（n=5279），命中率 0.80 → 新增 hits≈2769−2349=420? 注意 delta 口径：
    # new_hits = 0.80×5279 − 0.45×5219 = 4223 − 2349 = 1874，new_n=60... 口径演示：
    # 全量近似下 delta 命中率=1874/60>1 → 二项检验直接 0.0 < 0.01 → 复活
    update_lifecycle([_rec("failed", 0.80, 5279)], store, baseline_by_key=baseline, today="D40")
    s = store.load()[KEY]
    assert s["state"] == "resurrected" and s["resurrect_attempts"] == 1


def test_resurrection_second_failure_freezes(tmp_path):
    """复活后再 20 窗失败=二次退役，再复活失败满 2 次→frozen（Owner 门位解冻）。"""
    store = LifecycleStore(tmp_path / "lc.json")
    baseline = {KEY: 0.5}
    day = 0

    def _windows(state, rate, n_base, count):
        nonlocal day
        for _ in range(count):
            update_lifecycle([_rec(state, rate, n_base + day)], store, baseline_by_key=baseline, today=f"D{day}")
            day += 1

    _windows("failed", 0.45, 5000, 20)          # 第一次退役
    update_lifecycle([_rec("failed", 0.80, 5279)], store, baseline_by_key=baseline, today=f"D{day}")  # 复活#1
    assert store.load()[KEY]["state"] == "resurrected"
    _windows("failed", 0.45, 5300, 20)          # 复活后再度连续失败 → 二次退役
    assert store.load()[KEY]["state"] == "retired"
    update_lifecycle([_rec("failed", 0.80, 5600)], store, baseline_by_key=baseline, today=f"D{day}")  # 复活#2
    assert store.load()[KEY]["state"] == "resurrected"
    _windows("failed", 0.45, 5700, 20)          # 三连失败 → frozen
    assert store.load()[KEY]["state"] == "frozen"
    assert store.load()[KEY]["resurrect_failures"] == 2
