# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.auto_maintenance
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] dashboard.active_rules >= 0; dashboard.total_rules >= active_rules; last_check is ISO8601 str
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_dashboard() never raises; returns OwnerDashboard with non-negative counts
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_auto_maintenance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AutoMaintenance — 自动维护与规则健康仪表盘.

依据蓝图 MOD-INF-018 §3:
- 提供 OwnerDashboard 视图，展示活跃规则与总规则数
- 支持自动维护流程的健康检查与复杂度预算跟踪
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class OwnerDashboard:
    """Owner 仪表盘 — 规则健康摘要.

    Attributes:
        active_rules: 活跃规则数
        total_rules: 总规则数
        last_check: 最后检查时间（ISO8601）
        complexity_pct: 复杂度百分比
    """

    active_rules: int = 0
    total_rules: int = 0
    last_check: str = ""
    complexity_pct: float = 0.0


@dataclass
class RuleHealth:
    """规则健康记录."""

    rule_id: str = ""
    healthy: bool = True
    detail: str = ""


class ComplexityBudget:
    """复杂度预算跟踪器 — 限制规则体系复杂度."""

    def __init__(self) -> None:
        self._budget: int = 0
        self._used: int = 0

    def allocate(self, amount: int) -> bool:
        if self._used + amount > self._budget:
            return False
        self._used += amount
        return True


class AutoMaintenance:
    """自动维护器 — 产出 OwnerDashboard 健康视图."""

    def __init__(self) -> None:
        self._rules: list[RuleHealth] = []

    def register_rule(self, rule_id: str, healthy: bool = True, detail: str = "") -> RuleHealth:
        rule = RuleHealth(rule_id=rule_id, healthy=healthy, detail=detail)
        self._rules.append(rule)
        return rule

    def get_dashboard(self, **kwargs: Any) -> OwnerDashboard:
        """生成 Owner 仪表盘.

        Args:
            **kwargs: 可选参数（如 denied_last_24h 等），用于扩展仪表盘信息

        Returns:
            OwnerDashboard 健康摘要
        """
        active = sum(1 for r in self._rules if r.healthy)
        total = len(self._rules)
        complexity_pct = 0.0
        if total > 0:
            complexity_pct = (active / total) * 100.0
        return OwnerDashboard(
            active_rules=active,
            total_rules=total,
            last_check=datetime.now(timezone.utc).isoformat(),
            complexity_pct=complexity_pct,
        )


__all__ = [
    "AutoMaintenance",
    "ComplexityBudget",
    "OwnerDashboard",
    "RuleHealth",
]
