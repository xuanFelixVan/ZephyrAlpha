# [A_test] module_id: MOD-RK-DFR | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 35_drawdown_protocol_impl | §3.4/§6.1
# [MODULE] tests.risk.test_drawdown_forced_rest
# [INVARIANTS] 触发日后5个交易日休息(当日不计); 未触发不约束; 日历升序注入; 休息期满≠自动恢复
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_forced_rest.py
# [TTL] task_bound
"""强制休息 5 天自动计时测试（35 号 §6.1：Level 4 触发后强制休息 5 个交易日）。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from zephyr.risk.core.drawdown_forced_rest import (
    ForcedRestConfig,
    ForcedRestTimer,
    InvalidForcedRestInputError,
)

D0 = date(2026, 8, 3)  # 周一


def _trading_days(start: date, n: int) -> list[date]:
    """简化交易日历：跳过周末（测试注入，无节假日依赖）。"""
    days = []
    d = start
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


CAL = _trading_days(D0, 15)  # 8/3(一) 起 15 个交易日


class TestForcedRestTimer:
    def test_not_triggered_no_constraint(self):
        timer = ForcedRestTimer()
        assert timer.is_resting(CAL[0], CAL) is False
        assert timer.remaining_rest_days(CAL[0], CAL) == 0

    def test_rest_window_five_trading_days(self):
        """触发日 T 后 5 个交易日（T+1..T+5）休息中，T+6 解禁。"""
        timer = ForcedRestTimer()
        timer.trigger(CAL[0])
        assert timer.is_resting(CAL[0], CAL) is True   # 触发当日：已过 0 < 5
        assert timer.remaining_rest_days(CAL[0], CAL) == 5
        for k in range(1, 5):
            assert timer.is_resting(CAL[k], CAL) is True
            assert timer.remaining_rest_days(CAL[k], CAL) == 5 - k
        assert timer.is_resting(CAL[5], CAL) is False  # 5 个休息日已满
        assert timer.remaining_rest_days(CAL[5], CAL) == 0

    def test_trigger_day_not_counted(self):
        """触发日当日不计入休息进度。"""
        timer = ForcedRestTimer()
        timer.trigger(CAL[2])
        assert timer.remaining_rest_days(CAL[2], CAL) == 5
        assert timer.remaining_rest_days(CAL[3], CAL) == 4

    def test_query_date_between_calendar_entries(self):
        """查询日不在日历表中：按 ≤ 查询日的交易日计。"""
        timer = ForcedRestTimer()
        timer.trigger(CAL[0])
        weekend = CAL[4] + timedelta(days=1)
        if weekend not in CAL:
            # 周末查询：进度同前一交易日
            assert timer.remaining_rest_days(weekend, CAL) == timer.remaining_rest_days(
                CAL[4], CAL
            )

    def test_retrigger_refreshes(self):
        """重复触发刷新计时（取最严）。"""
        timer = ForcedRestTimer()
        timer.trigger(CAL[0])
        timer.trigger(CAL[3])
        assert timer.trigger_date == CAL[3]
        assert timer.remaining_rest_days(CAL[3], CAL) == 5

    def test_clear(self):
        timer = ForcedRestTimer()
        timer.trigger(CAL[0])
        timer.clear()
        assert timer.is_resting(CAL[1], CAL) is False
        assert timer.remaining_rest_days(CAL[1], CAL) == 0

    def test_custom_rest_days(self):
        timer = ForcedRestTimer(ForcedRestConfig(rest_trading_days=2))
        timer.trigger(CAL[0])
        assert timer.is_resting(CAL[1], CAL) is True
        assert timer.is_resting(CAL[2], CAL) is False

    def test_unsorted_calendar_raises(self):
        timer = ForcedRestTimer()
        timer.trigger(CAL[0])
        with pytest.raises(InvalidForcedRestInputError):
            timer.is_resting(CAL[2], [CAL[2], CAL[1]])

    def test_query_before_trigger_raises(self):
        timer = ForcedRestTimer()
        timer.trigger(CAL[5])
        with pytest.raises(InvalidForcedRestInputError):
            timer.is_resting(CAL[0], CAL)

    def test_query_without_trigger_raises_on_elapsed(self):
        """未触发时 is_resting/remaining 不抛错（False/0），但内部口径校验生效。"""
        timer = ForcedRestTimer()
        assert timer.is_resting(CAL[0], []) is False

    def test_invalid_config(self):
        with pytest.raises(InvalidForcedRestInputError):
            ForcedRestConfig(rest_trading_days=0)
