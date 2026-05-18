# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.rbac_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
L1 RBAC Guard — 三层权限模型 (always_allow / auto_guard / blocked)

MOD-INF-018 §2.4  D-018-01

分层信任策略: 95% always_allow + 4% auto_guard + 1% blocked
取消 needs_approval 层——改为 auto_guard（先干后验）
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from zephyr.shared.contracts.identity.agent_identity import AgentIdentity, AgentRole, MaturityLevel, MATURITY_AUTO_GUARD_TIMEOUT
from zephyr.agent_rbac.immutable_core import ImmutableCore


class PermissionDecision(str, Enum):
    ALLOW = "ALLOW"
    AUTO_GUARD = "AUTO_GUARD"
    BLOCKED = "BLOCKED"


@dataclass
class PermissionResult:
    decision: PermissionDecision
    reason: str = ""
    requires_owner_review: bool = False
    auto_guard_timeout: int = 300
    audit_context: dict = field(default_factory=dict)


ALWAYS_ALLOW_OPERATIONS = [
    "read:docs",
    "read:src",
    "read:tests",
    "read:config",
    "read:logs",
    "read:data",
    "write:tests",
    "execute:tests",
    "run_scripts:governance",
    "run_scripts:pre-commit",
    "file_search",
    "code_search",
    "list_directory",
    "read_file",
    "generate_report",
    "update_journal",
    "update_checkpoint",
]

AUTO_GUARD_OPERATIONS = [
    "write:src",
    "modify:config",
    "execute:scripts",
    "create:file",
    "delete:file",
    "rename:file",
    "modify:manifest",
    "modify:index",
    "create:directory",
    "modify:blueprint",
    "modify:document",
]

ALWAYS_BLOCKED_OPERATIONS = [
    "delete:audit_logs",
    "modify:immutable_core",
    "disable:kill_switch",
    "modify:rbac_roles",
    "delete:permanent_files",
    "shell:true_execution",
    "modify:environment_variables",
    "circumvent:gate_engine",
]


class RBACGuard:
    def __init__(self, immutable_core: Optional[ImmutableCore] = None) -> None:
        self._immutable_core = immutable_core or ImmutableCore()

    def check(
        self,
        agent: AgentIdentity,
        operation: str,
        target_path: str = "",
    ) -> PermissionResult:
        if self._immutable_core.is_always_blocked(operation):
            return PermissionResult(
                decision=PermissionDecision.BLOCKED,
                reason=f"Operation '{operation}' is always blocked (L0 Immutable Core)",
                audit_context={"blocked_by": "L0", "operation": operation},
            )

        if target_path and self._immutable_core.is_protected_path(target_path):
            if agent.role not in (AgentRole.ADMIN, AgentRole.AUDITOR):
                return PermissionResult(
                    decision=PermissionDecision.BLOCKED,
                    reason=f"Target path '{target_path}' is protected (L0 Immutable Core)",
                    audit_context={"blocked_by": "L0:protected_path", "path": target_path},
                )

        if operation in ALWAYS_BLOCKED_OPERATIONS:
            return PermissionResult(
                decision=PermissionDecision.BLOCKED,
                reason=f"Operation '{operation}' is always blocked",
            )

        if operation in ALWAYS_ALLOW_OPERATIONS:
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason=f"Operation '{operation}' is always allowed",
            )

        auto_guard_result = self._check_auto_guard(agent, operation)
        if auto_guard_result is not None:
            return auto_guard_result

        role_permissions = self._get_role_permissions(agent)
        if agent.has_permission(operation) or operation in role_permissions:
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason=f"Explicit permission granted for '{operation}'",
            )

        if not agent.owner_approved:
            if not agent.auto_guard_eligible:
                return PermissionResult(
                    decision=PermissionDecision.BLOCKED,
                    reason=f"Agent not owner-approved and not auto_guard eligible",
                )

        if agent.owner_approved:
            return PermissionResult(
                decision=PermissionDecision.ALLOW,
                reason="Owner-approved agent: allow by default",
            )

        return PermissionResult(
            decision=PermissionDecision.BLOCKED,
            reason=f"Operation '{operation}' not explicitly allowed for agent role {agent.role.value}",
            audit_context={"agent_role": agent.role.value, "operation": operation},
        )

    def _check_auto_guard(self, agent: AgentIdentity, operation: str) -> Optional[PermissionResult]:
        if operation in AUTO_GUARD_OPERATIONS:
            if agent.owner_approved:
                return PermissionResult(
                    decision=PermissionDecision.ALLOW,
                    reason=f"Owner-approved: auto_guard operation '{operation}' allowed",
                )
            if not agent.auto_guard_eligible:
                return PermissionResult(
                    decision=PermissionDecision.BLOCKED,
                    reason=f"Agent not auto_guard eligible for '{operation}'",
                )
            timeout = agent.get_auto_guard_timeout()
            return PermissionResult(
                decision=PermissionDecision.AUTO_GUARD,
                reason=f"Operation '{operation}' allowed with auto_guard",
                auto_guard_timeout=timeout,
                audit_context={"guard_mode": "auto_guard", "timeout": timeout},
            )

        for op_prefix in AUTO_GUARD_OPERATIONS:
            if operation.startswith(op_prefix.split(":")[0] + ":"):
                if not agent.auto_guard_eligible:
                    return PermissionResult(
                        decision=PermissionDecision.BLOCKED,
                        reason=f"Agent not auto_guard eligible for '{operation}'",
                    )
                return PermissionResult(
                    decision=PermissionDecision.AUTO_GUARD,
                    reason=f"Operation '{operation}' matched auto_guard prefix '{op_prefix}'",
                    auto_guard_timeout=agent.get_auto_guard_timeout(),
                )

        return None

    def _get_role_permissions(self, agent: AgentIdentity) -> list[str]:
        from zephyr.shared.contracts.identity.agent_identity import ROLE_DEFAULT_PERMISSIONS
        return ROLE_DEFAULT_PERMISSIONS.get(agent.role, [])

    def is_blocked(self, result: PermissionResult) -> bool:
        return result.decision == PermissionDecision.BLOCKED

    def is_auto_guard(self, result: PermissionResult) -> bool:
        return result.decision == PermissionDecision.AUTO_GUARD


PermissionVerdict = PermissionDecision
PermissionRequest = PermissionResult
