# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.dry_run
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_dry_run_agent_rbac.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] DryRunResult.would_succeed defaults True when no guard; simulate never raises
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] simulate()/impact_analysis() never raise; return DryRunResult/ImpactAnalysis
# [TESTS] tests/agent_rbac/test_dry_run_agent_rbac.py
# [A_module] module_id=MOD-SEC_dry_run | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DryRun — 权限模拟与影响分析.

依据蓝图 MOD-INF-018 §3:
- 模拟权限检查结果（不实际执行）
- 分析变更对多个 agent 的影响
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DryRunResult:
    """权限模拟结果.

    Attributes:
        operation: 模拟的操作
        would_be_decision: 模拟决策（ALLOW/BLOCKED/AUTO_GUARD）
        would_be_layer: 检查层
        would_be_reason: 决策原因
        would_succeed: 是否会成功
    """

    operation: str = ""
    would_be_decision: str = "ALLOW"
    would_be_layer: str = ""
    would_be_reason: str = ""
    would_succeed: bool = True


@dataclass
class ImpactAnalysis:
    """影响分析结果.

    Attributes:
        change_description: 变更描述
        affected_agents: 受影响的 agent 列表
        affected_operations: 受影响的操作列表
    """

    change_description: str = ""
    affected_agents: list[Any] = field(default_factory=list)
    affected_operations: list[str] = field(default_factory=list)


class DryRunSimulator:
    """权限模拟器 — 模拟权限检查而不实际执行."""

    def __init__(self) -> None:
        self._guard: Any = None

    def set_guard(self, guard: Any) -> None:
        """设置权限守卫.

        Args:
            guard: 权限守卫实例（需有 check(agent, operation) 方法）
        """
        self._guard = guard

    def simulate(self, agent: Any, operation: str, target: str = "") -> DryRunResult:
        """模拟权限检查.

        Args:
            agent: AgentIdentity 实例
            operation: 操作名称
            target: 目标路径（可选）

        Returns:
            DryRunResult 包含模拟结果
        """
        if self._guard is None:
            return DryRunResult(
                operation=operation,
                would_be_decision="ALLOW",
                would_be_layer="default",
                would_be_reason="no guard configured, default allow",
                would_succeed=True,
            )

        if hasattr(self._guard, "check"):
            try:
                result = self._guard.check(agent, operation, target)
            except TypeError:
                result = self._guard.check(agent, operation)
        else:
            result = self._guard.check(agent, operation)
        decision = getattr(result, "decision", "ALLOW")
        decision_str = decision.value if hasattr(decision, "value") else str(decision)
        would_succeed = decision_str != "BLOCKED"

        return DryRunResult(
            operation=operation,
            would_be_decision=decision_str,
            would_be_layer=getattr(result, "layer", ""),
            would_be_reason=getattr(result, "reason", ""),
            would_succeed=would_succeed,
        )

    def impact_analysis(
        self,
        agents: list[Any],
        operations: list[str],
        change: dict[str, Any],
    ) -> ImpactAnalysis:
        """分析变更对多个 agent 的影响.

        Args:
            agents: agent 列表
            operations: 操作列表
            change: 变更描述字典

        Returns:
            ImpactAnalysis 包含影响分析结果
        """
        change_desc = f"Change: {change}"
        affected_agents: list[Any] = []
        affected_operations: list[str] = []

        for agent in agents:
            for op in operations:
                if self._guard is not None:
                    result = self._guard.check(agent, op)
                    decision = getattr(result, "decision", "ALLOW")
                    decision_str = decision.value if hasattr(decision, "value") else str(decision)
                    if decision_str == "BLOCKED":
                        if agent not in affected_agents:
                            affected_agents.append(agent)
                        if op not in affected_operations:
                            affected_operations.append(op)
                else:
                    if agent not in affected_agents:
                        affected_agents.append(agent)
                    if op not in affected_operations:
                        affected_operations.append(op)

        return ImpactAnalysis(
            change_description=change_desc,
            affected_agents=affected_agents,
            affected_operations=affected_operations,
        )


__all__ = [
    "DryRunResult",
    "DryRunSimulator",
    "ImpactAnalysis",
]
