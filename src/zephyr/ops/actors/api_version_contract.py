# [A_module] module_id=MOD-UNK_api_version_contract | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.actors.api_version_contract

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""API Version Contract — v0.14.0 R188

Blindspot: API version contracts invisible to consuming agents; sunset dates unenforced.
Risk: R188 — Agent calls deprecated API version; silent failure or wrong behavior.

Mitigation: Agent-readable API version contracts with sunset date enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


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
            today = datetime.now().strftime("%Y-%m-%d")
        sunset = datetime.strptime(self.sunset_date, "%Y-%m-%d")
        now = datetime.strptime(today, "%Y-%m-%d")
        return now >= sunset

    def days_until_sunset(self) -> int:
        sunset = datetime.strptime(self.sunset_date, "%Y-%m-%d")
        return (sunset - datetime.now()).days
