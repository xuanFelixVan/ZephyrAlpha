# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.diagnosers.operational_seasonality

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Operational Seasonality — v0.16.0 R228

Blindspot: FLE operates same way weekends/weekdays/EOQ/EOY; seasonal patterns invisible.
Risk: R228 — Weekend low-staff mode uses same thresholds as peak; false negatives pile up.

Mitigation: Time-based operational mode switching (weekend/month-end/quarter-end/year-end).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class OpMode(str, Enum):
    WEEKDAY = "WEEKDAY"
    WEEKEND = "WEEKEND"
    MONTH_END = "MONTH_END"
    QUARTER_END = "QUARTER_END"
    YEAR_END = "YEAR_END"
    HOLIDAY = "HOLIDAY"


@dataclass
class OperationalSeasonality:
    mode: OpMode = OpMode.WEEKDAY
    threshold_multipliers: dict[str, float] = field(default_factory=lambda: {
        "WEEKEND": 0.7, "MONTH_END": 0.5, "QUARTER_END": 0.3, "YEAR_END": 0.2,
    })

    def auto_mode(self) -> OpMode:
        now = datetime.now()
        if now.month == 12 and now.day > 25:
            self.mode = OpMode.YEAR_END
        elif now.day > 25 and now.month in (3, 6, 9, 12):
            self.mode = OpMode.QUARTER_END
        elif now.day > 25:
            self.mode = OpMode.MONTH_END
        elif now.weekday() >= 5:
            self.mode = OpMode.WEEKEND
        else:
            self.mode = OpMode.WEEKDAY
        return self.mode

    @property
    def multiplier(self) -> float:
        return self.threshold_multipliers.get(self.mode.value, 1.0)
