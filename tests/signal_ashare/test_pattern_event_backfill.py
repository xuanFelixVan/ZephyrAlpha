# [BLUEPRINT] MOD-SIG-145 | tests/signal_ashare/test_pattern_event_backfill.py
# [MODULE] tests.signal_ashare.test_pattern_event_backfill
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] scripts.data.pattern_event_backfill
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数测试，禁触 CH/生产路径
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/test_pattern_event_backfill.py
# [TTL] permanent
"""pattern_event_backfill 纯函数单测（W2）——事件行转换/窗口过滤/run id 稳定性。"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from data.pattern_event_backfill import event_to_row_dict, scan_run_id, state_file  # noqa: E402

from zephyr.signal_ashare.strategy_signal.unified_pattern_engine import (  # noqa: E402
    KeyPoint,
    PatternClass,
    PatternDirection,
    PatternEvent,
)


def _event(anchor_idx: int = 2) -> PatternEvent:
    return PatternEvent(
        pattern_id="双顶@day",
        pattern_class=PatternClass.REVERSAL,
        name="双顶",
        direction=PatternDirection.DOWN,
        confidence=0.8,
        key_points=(KeyPoint(idx=0, price=10.0, role="顶1"),),
        historical_win_rate=None,
        timeframe="day",
        anchor_idx=anchor_idx,
    )


_TRADE_DATES = [date(2026, 9, 8), date(2026, 9, 9), date(2026, 9, 10)]


def test_event_to_row_dict_maps_anchor_and_close():
    row = event_to_row_dict(
        _event(),
        symbol="600519",
        trade_dates=_TRADE_DATES,
        scan_run="pb-x",
        start="2026-09-01",
        end="2026-09-30",
    )
    assert row is not None
    assert row["anchor_trade_date"] == "2026-09-10"
    assert row["confirmed_at"] == "2026-09-10T07:00:00+00:00"  # A股 15:00 CST
    assert row["pattern_class"] == "反转"
    assert row["direction"] == "向下"
    assert row["timeframe"] == "day"
    assert row["symbol"] == "600519"
    assert row["regime_tag"] == ""  # W2 留空
    assert row["key_points"] == [{"idx": 0, "price": 10.0, "role": "顶1"}]


def test_event_to_row_dict_filters_out_of_window():
    assert (
        event_to_row_dict(
            _event(),
            symbol="600519",
            trade_dates=_TRADE_DATES,
            scan_run="pb-x",
            start="2026-10-01",
            end="2026-10-31",
        )
        is None
    )


def test_scan_run_id_stable_and_state_path_under_tmp():
    assert scan_run_id("2021-09-01", "2026-09-13") == "pb-2021-09-01-2026-09-13"
    p = state_file("pb-x")
    assert ".runtime" in str(p) and "tmp" in str(p) and p.name == "pb-x_done.txt"
