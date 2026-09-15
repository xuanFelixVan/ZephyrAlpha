# [BLUEPRINT] MOD-BT-151 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_compute_window_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-151 compute_window_gate 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯函数测试零 IO 零网络（不触 CH）；时序用例覆盖盘中/盘后/周末/naive 拒收
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-151 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E0 算力闸门纯函数核单测——窗档分类/判决理由码/权重映射，零 IO 零网络。"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from scripts.backtest.compute_window_gate import (
    NODE_CLASS_WEIGHT,
    REASON_ALLOW_LIGHT,
    REASON_ALLOW_OFFHOURS,
    REASON_DENY_CALENDAR_UNKNOWN,
    REASON_DENY_TRADING_HOURS,
    WINDOW_HEAVY_OK,
    WINDOW_LIGHT_ONLY,
    classify_window,
    gate_decision,
    needs_heavy_window,
)

_TZ = ZoneInfo("Asia/Shanghai")


def _dt(h: int, m: int = 0, weekday: int = 2) -> datetime:
    """构造 2026-09 基准周（9/2 周三）的 aware 时刻。"""
    return datetime(2026, 9, 2 + weekday if weekday < 5 else weekday + 2, h, m, tzinfo=_TZ)


class TestClassifyWindow:
    def test_trading_day_intraday_band_is_light_only(self):
        # 09:00-15:30 保守带（开盘前缓冲到收盘后缓冲）=light_only
        assert classify_window(_dt(10), True) == WINDOW_LIGHT_ONLY
        assert classify_window(_dt(15, 29), True) == WINDOW_LIGHT_ONLY
        assert classify_window(_dt(9, 0), True) == WINDOW_LIGHT_ONLY

    def test_after_close_buffer_is_heavy_ok(self):
        assert classify_window(_dt(15, 30), True) == WINDOW_HEAVY_OK
        assert classify_window(_dt(23, 0), True) == WINDOW_HEAVY_OK

    def test_premarket_dawn_is_heavy_ok(self):
        # 2026-09-16 治本：交易日凌晨 00:00-09:00 为盘外黄金窗（重算力主窗口），
        # 原实现误判 light_only（09-14 07:10/07:11 与 09-16 00:21 三次误拒实证）
        for h in (0, 2, 6, 7, 8):
            assert classify_window(_dt(h), True) == WINDOW_HEAVY_OK
        assert classify_window(_dt(8, 59), True) == WINDOW_HEAVY_OK

    def test_non_trading_day_always_heavy_ok(self):
        for h in (9, 12, 15, 20):
            assert classify_window(_dt(h), False) == WINDOW_HEAVY_OK

    def test_naive_datetime_rejected(self):
        with pytest.raises(ValueError):
            classify_window(datetime(2026, 9, 2, 10), True)

    def test_other_tz_normalized(self):
        utc_noon = datetime(2026, 9, 2, 2, 0, tzinfo=ZoneInfo("UTC"))  # 北京 10:00
        assert classify_window(utc_noon, True) == WINDOW_LIGHT_ONLY


class TestGateDecision:
    def test_light_always_allowed_even_unknown_calendar(self):
        d = gate_decision("monitor", False, _dt(10), None)
        assert d["allowed"] and d["reason_code"] == REASON_ALLOW_LIGHT

    def test_heavy_denied_in_trading_hours(self):
        d = gate_decision("c4_batch", True, _dt(10), True)
        assert not d["allowed"] and d["reason_code"] == REASON_DENY_TRADING_HOURS
        assert d["window"] == WINDOW_LIGHT_ONLY

    def test_heavy_allowed_after_close(self):
        d = gate_decision("c4_batch", True, _dt(16), True)
        assert d["allowed"] and d["reason_code"] == REASON_ALLOW_OFFHOURS

    def test_heavy_allowed_holiday(self):
        d = gate_decision("gp_mine", True, _dt(10), False)
        assert d["allowed"] and d["reason_code"] == REASON_ALLOW_OFFHOURS

    def test_heavy_fail_closed_on_unknown_calendar(self):
        d = gate_decision("c4_batch", True, _dt(10), None)
        assert not d["allowed"] and d["reason_code"] == REASON_DENY_CALENDAR_UNKNOWN

    def test_reason_codes_closed_set(self):
        codes = {REASON_ALLOW_LIGHT, REASON_ALLOW_OFFHOURS,
                 REASON_DENY_TRADING_HOURS, REASON_DENY_CALENDAR_UNKNOWN}
        assert len(codes) == 4


class TestNodeClassWeight:
    def test_map_matches_factory_map_compute_classes(self):
        assert set(NODE_CLASS_WEIGHT) == {"local", "api", "local_gpu", "mixed"}
        assert not needs_heavy_window("local") and not needs_heavy_window("api")
        assert needs_heavy_window("local_gpu") and needs_heavy_window("mixed")

    def test_unknown_class_fails_closed_to_heavy(self):
        assert needs_heavy_window("quantum") is True


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
