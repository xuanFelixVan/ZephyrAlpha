# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.identity.permission
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.access_control.guards.permission_guard;zephyr.infrastructure.escalation;zephyr.governance;zephyr.integration.mcp
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 权限判定枚举不可扩展
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py
# [A_module] module_id=MOD-SHR_permission | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from dataclasses import dataclass, field
from enum import Enum


class GuardDecision(str, Enum):
    ALLOW = "ALLOW"
    AUTO_GUARD = "AUTO_GUARD"
    BLOCKED = "BLOCKED"


@dataclass
class GuardResult:
    decision: GuardDecision = GuardDecision.ALLOW
    layer: str = ""
    reason: str = ""
    rule_id: str = ""
    audit_context: dict = field(default_factory=dict)
    timing_ns: int = 0
