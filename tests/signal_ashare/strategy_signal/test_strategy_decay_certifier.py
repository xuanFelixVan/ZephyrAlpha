# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-SIG-150 | tests/signal_ashare/strategy_signal/test_strategy_decay_certifier.py
# [TTL] permanent
"""strategy_decay_certifier 单测（W-R 三域落地）——三态+退役/复活建议。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.strategy_signal.strategy_decay_certifier import (
    run_strategy_decay_certify,
)


class _FakeClient:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, sql, params=None):
        # 模拟 load_latest_metrics 的内存 last-wins 去重（表非 Replacing 无 FINAL）
        dedup = {}
        for r in self._rows:
            dedup[r[0]] = r
        return list(dedup.values())


def test_decay_three_states(tmp_path):
    rows = [
        ("STR-A", 0.8, 1.2, 0.1),   # certified
        ("STR-B", 0.3, 0.9, 0.2),   # probation
        ("STR-C", -0.2, 0.8, 0.3),  # failed
        ("STR-D", None, None, None), # 无 DS→probation
    ]
    r = run_strategy_decay_certify(
        client=_FakeClient(rows), ledger_path=tmp_path / "led.json", today="D1"
    )
    assert r["counts"] == {"probation": 2, "failed": 1, "certified": 1}
    doc = __import__("json").loads((tmp_path / "led.json").read_text(encoding="utf-8"))
    assert doc["strategies"]["STR-A"]["state"] == "certified"


def test_decay_failed_streak_retires(tmp_path):
    rows = [("STR-C", -0.2, 0.8, 0.3)]
    ledger = tmp_path / "led.json"
    for i in range(8):
        r = run_strategy_decay_certify(
            client=_FakeClient(rows), ledger_path=ledger, today=f"D{i}"
        )
    assert r["counts"].get("retired") == 1
    doc = __import__("json").loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["STR-C"]["state"] == "retired"


def test_decay_resurrect_after_retire(tmp_path):
    ledger = tmp_path / "led.json"
    for i in range(8):
        run_strategy_decay_certify(
            client=_FakeClient([("STR-C", -0.2, 0.8, 0.3)]), ledger_path=ledger, today=f"D{i}"
        )
    r = run_strategy_decay_certify(
        client=_FakeClient([("STR-C", 0.8, 1.2, 0.1)]), ledger_path=ledger, today="D99"
    )
    doc = __import__("json").loads(ledger.read_text(encoding="utf-8"))
    assert doc["strategies"]["STR-C"]["state"] == "resurrected"
    assert r["counts"].get("resurrected") == 1
