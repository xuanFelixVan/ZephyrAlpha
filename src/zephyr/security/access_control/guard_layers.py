# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §guard_layers
# [MODULE] zephyr.security.access_control.guard_layers
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_permissions.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ColdStartLock default _locked is True; escalate returns non-None
# [MODIFY-GUARD] blueprint.md §guard_layers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] escalate never raises; returns list of action strings
# [TESTS] tests/agent_rbac/test_permissions.py
# [A_module] module_id=MOD-SEC_guard_layers | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""GuardLayers — 权限守卫层组件.

依据蓝图 MOD-INF-018 §guard_layers:
- EscalationHandler: 升级处理器
- ColdStartLock: 冷启动锁
- AutoGuard: 自动守卫
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


_DEFAULT_AUTO_GUARD_TIMEOUT = 600


class AutoGuardMode(str, Enum):
    """自动守卫模式."""

    DISABLED = "disabled"
    ENABLED = "enabled"
    SHADOW = "shadow"


@dataclass
class AutoGuardResult:
    """自动守卫结果.

    Attributes:
        approved: 是否批准
        reason: 原因
        timeout: 超时时间
        decision: 决策字符串
    """

    approved: bool = False
    reason: str = ""
    timeout: int = 0
    decision: str = ""


@dataclass
class EscalationResult:
    """升级结果.

    Attributes:
        agent_id: agent ID
        violation: 违规描述
        severity: 严重程度
        escalated: 是否已升级
        detail: 详情
    """

    agent_id: str = ""
    violation: str = ""
    severity: str = "LOW"
    escalated: bool = True
    detail: str = ""


class AutoGuard:
    """自动守卫."""

    def __init__(self, mode: AutoGuardMode = AutoGuardMode.DISABLED) -> None:
        self._mode = mode
        self._active_guards: dict[str, list[AutoGuardResult]] = {}

    def evaluate(self, agent: Any, operation: str) -> AutoGuardResult:
        """评估操作是否可自动守卫."""
        return AutoGuardResult(approved=False, reason="auto-guard disabled")

    def allow_with_guard(self, agent: Any, operation: str) -> AutoGuardResult:
        """允许操作并设置自动守卫.

        Args:
            agent: AgentIdentity 实例
            operation: 操作名称

        Returns:
            AutoGuardResult 包含决策和超时
        """
        agent_id = getattr(agent, "session_id", str(id(agent)))
        result = AutoGuardResult(
            approved=True,
            reason=f"auto-guard for {operation}",
            timeout=_DEFAULT_AUTO_GUARD_TIMEOUT,
            decision="AUTO_GUARD",
        )
        if agent_id not in self._active_guards:
            self._active_guards[agent_id] = []
        self._active_guards[agent_id].append(result)
        return result

    def get_active_guards(self, agent_id: str) -> list[AutoGuardResult]:
        """获取指定 agent 的活跃守卫列表.

        Args:
            agent_id: agent ID

        Returns:
            list[AutoGuardResult]: 活跃守卫列表
        """
        return self._active_guards.get(agent_id, [])


class ColdStartLock:
    """冷启动锁 — 系统启动时锁定，防止未授权操作."""

    def __init__(self) -> None:
        self._locked: bool = True

    def unlock(self) -> None:
        """解锁."""
        self._locked = False

    def lock(self) -> None:
        """加锁."""
        self._locked = True

    def owner_bypass(self) -> None:
        """Owner 绕过冷启动锁."""
        self._locked = False

    @property
    def is_locked(self) -> bool:
        """是否锁定."""
        return self._locked


class EscalationHandler:
    """升级处理器."""

    def __init__(self) -> None:
        self._escalations: list[EscalationResult] = []
        self._escalation_counts: dict[str, int] = {}

    def escalate(
        self,
        agent_id: str,
        violation: str,
        severity: str = "MEDIUM",
    ) -> list[str]:
        """升级违规事件.

        Args:
            agent_id: agent ID
            violation: 违规描述（可包含严重级别标记如 P0_OWNER/P1_HIGH 等）
            severity: 严重程度 (P0_OWNER/P1_HIGH/P2_MEDIUM/P3_LOW/P4_LOW)

        Returns:
            list[str]: 升级动作列表（支持 ``in`` 操作符）
        """
        self._escalation_counts[agent_id] = self._escalation_counts.get(agent_id, 0) + 1

        # 严重级别可由 violation 或 severity 参数指定
        level = severity if severity.startswith("P") else violation

        result = EscalationResult(
            agent_id=agent_id,
            violation=violation,
            severity=severity,
            escalated=True,
            detail=f"escalated: {violation} (severity={severity})",
        )
        self._escalations.append(result)

        if level == "P0_OWNER":
            return ["NOTIFY_OWNER", "BLOCK_AGENT", "AUDIT_TRAIL"]
        if level == "P1_HIGH":
            return ["NOTIFY_OWNER", "AUDIT_TRAIL"]
        if level == "P2_MEDIUM":
            return ["LOG", "AUDIT_TRAIL"]
        return ["LOG_ONLY"]

    def should_throttle(self, agent_id: str, max_count: int = 5) -> bool:
        """检查 agent 是否应被限流.

        Args:
            agent_id: agent ID
            max_count: 最大升级次数阈值

        Returns:
            bool: 如果升级次数 >= max_count 则返回 True
        """
        count = self._escalation_counts.get(agent_id, 0)
        return count >= max_count

    def reset_agent(self, agent_id: str) -> None:
        """重置指定 agent 的升级计数.

        Args:
            agent_id: agent ID
        """
        self._escalation_counts.pop(agent_id, None)


__all__ = [
    "AutoGuard",
    "AutoGuardMode",
    "AutoGuardResult",
    "ColdStartLock",
    "EscalationHandler",
    "EscalationResult",
]
