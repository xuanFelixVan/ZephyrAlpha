# [BLUEPRINT] MOD-POS-015 | docs/03_modules/MOD-POS-015/
# [MODULE] zephyr.position.core.position_time_budget
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/position/test_position_time_budget.py
# [TTL] permanent
"""position_time_budget（持仓时间预算）单元测试。

覆盖：
- 持有天数=as_of−entry_date（自然日口径）
- WITHIN/APPROACHING/EXPIRED 三态按预算与预警比例划分
- 到期持仓汇总 + any_expired 标志
- 非法输入（预算<1/入场晚于基准日/预警比例越界）→ InvalidTimeBudgetInputError
"""

from __future__ import annotations

from datetime import date

import pytest

from zephyr.position.core.position_time_budget import (
    InvalidTimeBudgetInputError,
    TimeBudgetPosition,
    TimeBudgetStatus,
    check_time_budgets,
)


def _pos(entry: str, max_days: int) -> TimeBudgetPosition:
    y, m, d = (int(x) for x in entry.split("-"))
    return TimeBudgetPosition(entry_date=date(y, m, d), max_holding_days=max_days)


class TestTimeBudget:
    def test_days_held_calendar(self) -> None:
        """持有天数按自然日差计算。"""
        r = check_time_budgets({"A": _pos("2026-08-01", 30)}, as_of=date(2026, 8, 11))
        assert r.positions["A"].days_held == 10

    def test_within_status(self) -> None:
        """持有 10/30 天（比例 0.33 < 0.8）→ WITHIN。"""
        r = check_time_budgets({"A": _pos("2026-08-01", 30)}, as_of=date(2026, 8, 11))
        assert r.positions["A"].status is TimeBudgetStatus.WITHIN
        assert r.any_expired is False

    def test_approaching_status(self) -> None:
        """持有 25/30 天（比例 0.83 ≥ 0.8）→ APPROACHING。"""
        r = check_time_budgets({"A": _pos("2026-08-01", 30)}, as_of=date(2026, 8, 26))
        assert r.positions["A"].status is TimeBudgetStatus.APPROACHING
        assert "A" in r.approaching

    def test_expired_status(self) -> None:
        """持有 31/30 天 → EXPIRED + any_expired。"""
        r = check_time_budgets({"A": _pos("2026-08-01", 30)}, as_of=date(2026, 9, 1))
        assert r.positions["A"].status is TimeBudgetStatus.EXPIRED
        assert r.any_expired is True
        assert "A" in r.expired

    def test_exact_budget_day_not_expired(self) -> None:
        """持有=预算当天（30/30，比例 1.0）→ APPROACHING 非 EXPIRED。"""
        r = check_time_budgets({"A": _pos("2026-08-01", 30)}, as_of=date(2026, 8, 31))
        assert r.positions["A"].status is TimeBudgetStatus.APPROACHING
        assert r.any_expired is False

    def test_custom_warn_ratio(self) -> None:
        """warn_ratio=0.5 → 持有 6/10 天（0.6）即 APPROACHING。"""
        r = check_time_budgets(
            {"A": _pos("2026-08-01", 10)}, as_of=date(2026, 8, 7), warn_ratio=0.5
        )
        assert r.positions["A"].status is TimeBudgetStatus.APPROACHING

    def test_multiple_positions_mixed(self) -> None:
        """多持仓混合状态分类正确。"""
        r = check_time_budgets(
            {
                "FRESH": _pos("2026-08-20", 30),
                "OLD": _pos("2026-07-01", 30),
                "MID": _pos("2026-08-01", 30),
            },
            as_of=date(2026, 8, 26),
        )
        assert r.positions["FRESH"].status is TimeBudgetStatus.WITHIN
        assert r.positions["OLD"].status is TimeBudgetStatus.EXPIRED
        assert r.positions["MID"].status is TimeBudgetStatus.APPROACHING

    def test_empty_positions(self) -> None:
        """空仓 → 空报告，any_expired=False。"""
        r = check_time_budgets({}, as_of=date(2026, 8, 23))
        assert r.positions == {}
        assert r.any_expired is False


class TestInvalidInput:
    def test_max_days_below_one(self) -> None:
        with pytest.raises(InvalidTimeBudgetInputError):
            check_time_budgets({"A": _pos("2026-08-01", 0)}, as_of=date(2026, 8, 2))

    def test_entry_after_as_of(self) -> None:
        """入场日晚于基准日（数据异常）→ 拒绝。"""
        with pytest.raises(InvalidTimeBudgetInputError):
            check_time_budgets({"A": _pos("2026-09-01", 30)}, as_of=date(2026, 8, 23))

    def test_warn_ratio_out_of_range(self) -> None:
        with pytest.raises(InvalidTimeBudgetInputError):
            check_time_budgets({"A": _pos("2026-08-01", 30)}, as_of=date(2026, 8, 2), warn_ratio=0.0)
        with pytest.raises(InvalidTimeBudgetInputError):
            check_time_budgets({"A": _pos("2026-08-01", 30)}, as_of=date(2026, 8, 2), warn_ratio=1.5)
