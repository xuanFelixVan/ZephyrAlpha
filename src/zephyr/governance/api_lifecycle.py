# [A_module] module_id=MOD-UNK_api_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-INF-010
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/

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
