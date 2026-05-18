# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.dry_run

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
L7 Dry-Run — 权限影响分析 / Dry-Run模拟 / 权限变更影响分析

MOD-INF-018 §2.10  D-018-12
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DryRunResult:
    operation: str
    would_be_decision: str
    would_be_layer: str = ""
    would_be_reason: str = ""
    would_succeed: bool = False
    affected_agents: list[str] = field(default_factory=list)
    affected_operations: list[str] = field(default_factory=list)


@dataclass
class ImpactAnalysis:
    change_description: str
    agent_impacts: dict[str, list[str]] = field(default_factory=dict)
    operation_impacts: dict[str, list[str]] = field(default_factory=dict)
    breaking_changes: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)


class DryRunSimulator:
    def __init__(self) -> None:
        self._guard = None

    def set_guard(self, guard) -> None:
        self._guard = guard

    def simulate(
        self,
        agent,
        operation: str,
        target_path: str = "",
    ) -> DryRunResult:
        if self._guard is None:
            return DryRunResult(
                operation=operation,
                would_be_decision="ALLOW",
                would_succeed=True,
                would_be_reason="No guard configured (dry-run only)",
            )

        result = self._guard.check(agent, operation, target_path=target_path)
        return DryRunResult(
            operation=operation,
            would_be_decision=result.decision.value if result.decision else "UNKNOWN",
            would_be_layer=result.reason[:50] if result.reason else "",
            would_be_reason=result.reason if result.reason else "",
            would_succeed=not self._guard.is_blocked(result),
        )

    def impact_analysis(
        self,
        agents: list,
        operations: list[str],
        permission_change: dict,
    ) -> ImpactAnalysis:
        analysis = ImpactAnalysis(
            change_description=f"Analyzing impact of {permission_change}",
        )
        for agent in agents:
            for op in operations:
                if not agent.has_permission(op) if hasattr(agent, "has_permission") else True:
                    analysis.agent_impacts.setdefault(agent.session_id, []).append(op)
        return analysis
