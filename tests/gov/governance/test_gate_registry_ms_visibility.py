"""ms 盲区判别测试：<1ms 的 gate 在落盘 jsonl 的 ms 字典必须可见。

治本（T14，st-commitspeed-tbl-20260924）：commit_gate_registry._stat_flush 原对
ms 字典施 ``>= 1.0`` 过滤，实测 n_specs=102 而 ms 可见仅 57-59——近半门禁的
执行计时蒸发，宪法 §4.2"零触发零消费"退役审计对它们不可证（连执行都没记录，
无法区分"跑了但快"与"根本没跑"）。修法：ms 字典全量落盘，total_ms 语义不变。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge import commit_gate_registry as cgr


class _FakeGateway:
    """最小 gateway 替身——_stat_flush 只消费 project_root 属性。"""

    def __init__(self, root: Path) -> None:
        self.project_root = root


def _read_last_record(root: Path) -> dict:
    stats = root / ".runtime" / "audit" / "gate_execution_stats.jsonl"
    lines = stats.read_text(encoding="utf-8").strip().splitlines()
    return json.loads(lines[-1])


@pytest.fixture()
def _clean_acc():
    cgr._STAT_ACC.clear()
    yield
    cgr._STAT_ACC.clear()


def test_sub_ms_gate_visible_in_ms_dict(tmp_path, _clean_acc):
    """判别用例：0.5ms 的门必须在 ms 字典可见（修前必红——被 >=1.0 过滤蒸发）。"""
    cgr._stat_ms("FAKE-SUBMS-GATE", 0.5, True, "ran")
    cgr._stat_ms("FAKE-SUPRA-MS-GATE", 12.3, True, "ran")
    cgr._stat_flush(_FakeGateway(tmp_path))
    rec = _read_last_record(tmp_path)
    assert "FAKE-SUBMS-GATE" in rec["ms"], "0.5ms 门被 >=1.0 过滤蒸发——计时盲区"
    assert rec["ms"]["FAKE-SUBMS-GATE"] == 0.5
    assert rec["ms"]["FAKE-SUPRA-MS-GATE"] == 12.3
    assert rec["n_specs"] == 2
    assert rec["total_ms"] == pytest.approx(12.8)


def test_zero_ms_reused_state_visible(tmp_path, _clean_acc):
    """复用/缓存命中态计时为 0.0ms，同样必须可见（state 字段已证其执行路径）。"""
    cgr._stat_ms("FAKE-ZERO-MS-GATE", 0.0, True, "cache_hit")
    cgr._stat_flush(_FakeGateway(tmp_path))
    rec = _read_last_record(tmp_path)
    assert "FAKE-ZERO-MS-GATE" in rec["ms"]
    assert rec["ms"]["FAKE-ZERO-MS-GATE"] == 0.0
    assert rec["total_ms"] == 0.0
