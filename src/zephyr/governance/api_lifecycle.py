# [BLUEPRINT] DOM-GOV-001 | 03_modules/_domain-governance/blueprint.md | §

# [MODULE] zephyr.governance.api_lifecycle

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class APIState(str, Enum):
    ACTIVE = "Active"
    DEPRECATED = "Deprecated"
    REMOVED = "Removed"


class DeprecationNotice(BaseModel):
    api_name: str
    deprecated_at: str
    removal_at: str
    migration_guide: str = ""
    deprecation_header: str = "X-API-Deprecated"
    grace_period_days: int = 90

    @property
    def days_until_removal(self) -> int:
        try:
            dep_dt = datetime.fromisoformat(self.deprecated_at.replace("Z", "+00:00"))
            removal_dt = dep_dt + timedelta(days=self.grace_period_days)
            remaining = (removal_dt - datetime.now(timezone.utc)).days
            return max(0, remaining)
        except (ValueError, TypeError):
            return 0

    @property
    def expired(self) -> bool:
        return self.days_until_removal == 0


class APIEndpoint(BaseModel):
    name: str
    version: str
    state: APIState = APIState.ACTIVE
    deprecation: Optional[DeprecationNotice] = None
    sunset_date: Optional[str] = None


def deprecate_api(
    endpoint: APIEndpoint,
    migration_guide: str = "",
    grace_period_days: int = 90,
) -> DeprecationNotice:
    notice = DeprecationNotice(
        api_name=endpoint.name,
        deprecated_at=datetime.now(timezone.utc).isoformat(),
        removal_at=(datetime.now(timezone.utc) + timedelta(days=grace_period_days)).isoformat(),
        migration_guide=migration_guide,
        grace_period_days=grace_period_days,
    )
    endpoint.state = APIState.DEPRECATED
    endpoint.deprecation = notice
    return notice


def remove_api(endpoint: APIEndpoint) -> None:
    endpoint.state = APIState.REMOVED
    endpoint.sunset_date = datetime.now(timezone.utc).isoformat()
