# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.lifecycle_governance.api_lifecycle
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_api_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel


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
            remaining = (removal_dt - datetime.now(UTC)).days
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
    deprecation: DeprecationNotice | None = None
    sunset_date: str | None = None


def deprecate_api(
    endpoint: APIEndpoint,
    migration_guide: str = "",
    grace_period_days: int = 90,
) -> DeprecationNotice:
    notice = DeprecationNotice(
        api_name=endpoint.name,
        deprecated_at=datetime.now(UTC).isoformat(),
        removal_at=(datetime.now(UTC) + timedelta(days=grace_period_days)).isoformat(),
        migration_guide=migration_guide,
        grace_period_days=grace_period_days,
    )
    endpoint.state = APIState.DEPRECATED
    endpoint.deprecation = notice
    return notice


def remove_api(endpoint: APIEndpoint) -> None:
    endpoint.state = APIState.REMOVED
    endpoint.sunset_date = datetime.now(UTC).isoformat()
