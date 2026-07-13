# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.operational_seasonality
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_operational_seasonality | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Operational Seasonality — v0.16.0 R228

Blindspot: FLE operates same way weekends/weekdays/EOQ/EOY; seasonal patterns invisible.
Risk: R228 — Weekend low-staff mode uses same thresholds as peak; false negatives pile up.

Mitigation: Time-based operational mode switching (weekend/month-end/quarter-end/year-end).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from zephyr.shared.utils.time_utils import now_utc


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
    threshold_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            "WEEKEND": 0.7,
            "MONTH_END": 0.5,
            "QUARTER_END": 0.3,
            "YEAR_END": 0.2,
        }
    )

    def auto_mode(self) -> OpMode:
        now = now_utc()
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
