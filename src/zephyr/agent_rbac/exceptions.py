# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.exceptions

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Agent RBAC 异常类型定义

MOD-INF-018 base exceptions
"""


class AgentRbacError(Exception):
    def __init__(self, message: str = "Agent RBAC error", layer: str = "", rule_id: str = "") -> None:
        super().__init__(message)
        self.layer = layer
        self.rule_id = rule_id


class PermissionDeniedError(AgentRbacError):
    def __init__(self, message: str = "Permission denied", operation: str = "", layer: str = "", rule_id: str = "") -> None:
        super().__init__(message, layer=layer, rule_id=rule_id)
        self.operation = operation


class ColdStartLockedError(AgentRbacError):
    def __init__(self, message: str = "System is in cold-start lock") -> None:
        super().__init__(message, layer="L1", rule_id="CSL-001")


class OverrideTokenExpiredError(AgentRbacError):
    def __init__(self, message: str = "Override token expired", issued_at: float = 0.0) -> None:
        super().__init__(message, layer="L1", rule_id="OVR-001")
        self.issued_at = issued_at


class KillSwitchTrippedError(AgentRbacError):
    def __init__(self, message: str = "Kill switch tripped", trigger: str = "") -> None:
        super().__init__(message, layer="L0", rule_id="KSW-001")
        self.trigger = trigger


class DegradationBlockedError(AgentRbacError):
    def __init__(self, message: str = "Engine degraded — all operations blocked") -> None:
        super().__init__(message, layer="L0", rule_id="DEG-001")
