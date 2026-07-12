# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.api_version_contract
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_api_version_contract | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""API Version Contract — v0.14.0 R188

Blindspot: API version contracts invisible to consuming agents; sunset dates unenforced.
Risk: R188 — Agent calls deprecated API version; silent failure or wrong behavior.

Mitigation: Agent-readable API version contracts with sunset date enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from zephyr.shared.utils.time_utils import now_utc


class VersionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    SUNSET = "SUNSET"


@dataclass
class APIVersionContract:
    api_name: str
    version: str
    sunset_date: str
    replacement_version: str = ""
    status: VersionStatus = VersionStatus.ACTIVE
    deprecation_notice_days: int = 90

    def check_sunset(self, today: str | None = None) -> bool:
        if today is None:
            today = now_utc().strftime("%Y-%m-%d")
        sunset = datetime.strptime(self.sunset_date, "%Y-%m-%d")
        now = datetime.strptime(today, "%Y-%m-%d")
        return now >= sunset

    def days_until_sunset(self) -> int:
        sunset = datetime.strptime(self.sunset_date, "%Y-%m-%d")
        return (sunset - now_utc()).days
