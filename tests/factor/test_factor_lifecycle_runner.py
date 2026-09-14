# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L02-LIFECYCLE | tests/factor/test_factor_lifecycle_runner.py
# [TTL] permanent
"""factor_lifecycle_runner 单测（W-R 三域落地）——联合认证+退役/复活迁移。"""

from __future__ import annotations

import pytest

from zephyr.factor.analysis.factor_lifecycle_runner import (
    LifecycleStoreLite,
    _ic_p_value,
    certify_factor_family,
    run_factor_lifecycle,
)


def test_ic_p_value_known_range():
    p = _ic_p_value(0.05, 240)
    assert 0.10 <= p <= 0.25
    assert _ic_p_value(0.0, 240) == 0.5  # 零效应单侧 p=0.5


def test_certify_family_three_states():
    factors = [
        {"factor_id": "F-A", "ic": 0.30, "ir": 0.8, "lookback_period": 240},
        {"factor_id": "F-B", "ic": 0.06, "ir": 0.4, "lookback_period": 240},
        {"factor_id": "F-C", "ic": 0.01, "ir": 0.1, "lookback_period": 240},
        {"factor_id": "F-D", "ic": 0.12, "ir": 0.8},
        {"factor_id": "F-E", "ic": None, "ir": None},
    ]
    out = certify_factor_family(factors, q=0.10)
    by_id = {r["factor_id"]: r for r in out}
    assert by_id["F-A"]["state"] in ("certified", "probation")
    assert by_id["F-C"]["state"] == "failed"
    assert by_id["F-D"]["state"] == "probation"  # 无 lookback：Fail-Closed 封顶
    assert by_id["F-E"]["state"] == "probation"  # 无 ic=未评估封顶 probation（未评估≠淘汰）


def test_bhy_family_rejection_hides_weak():
    factors = [{"factor_id": f"F{i}", "ic": 0.02, "ir": 0.2, "lookback_period": 60}
               for i in range(120)]
    out = certify_factor_family(factors, q=0.10)
    assert all(r["state"] in ("failed", "probation") for r in out)
    assert not any(r["state"] == "certified" for r in out)


REG_V1 = (
    "factors:\n"
    '- factor_id: "F-X"\n'
    "  ic: 0.01\n"
    "  ir: 0.1\n"
    "  lookback_period: 240\n"
    "  decay_state: failed\n"
)
REG_V2 = (
    "factors:\n"
    '- factor_id: "F-X"\n'
    "  ic: 0.12\n"
    "  ir: 0.8\n"
    "  lookback_period: 240\n"
    "  decay_state: retired\n"
)


def test_run_lifecycle_retire_then_resurrect(tmp_path):
    store = tmp_path / "lc.json"
    for i in range(20):
        summary = run_factor_lifecycle(
            registry_text=REG_V1, store_path=store, today=f"W{i:02d}",
        )
    s = LifecycleStoreLite(store).load()
    assert s["F-X|weekly"]["state"] == "retired"
    assert summary["counts"].get("retired") == 1
    summary2 = run_factor_lifecycle(
        registry_text=REG_V2, store_path=store, today="W21",
    )
    s2 = LifecycleStoreLite(store).load()
    assert s2["F-X|weekly"]["state"] == "resurrected"
    assert summary2["counts"].get("resurrected") == 1
