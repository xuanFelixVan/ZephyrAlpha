# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.risk_mitigation
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_risk_mitigation_agent_rbac.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] assess returns RiskAssessment with risk_level; get_mitigation_playbook returns dict with action key
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] assess/get_mitigation_playbook never raise
# [TESTS] tests/agent_rbac/test_risk_mitigation_agent_rbac.py
# [A_module] module_id=MOD-SEC_risk_mitigation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RiskMitigation — 风险评估与缓解策略.

依据蓝图 MOD-INF-018 §3:
- 评估风险等级（CRITICAL/HIGH/MEDIUM/LOW）
- 提供各等级的缓解策略手册
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RiskAssessment:
    """风险评估结果.

    Attributes:
        scenario: 风险场景
        likelihood: 发生概率 (0.0-1.0)
        impact: 影响程度 (0.0-1.0)
        risk_level: 风险等级 (CRITICAL/HIGH/MEDIUM/LOW)
        score: 综合分数 (likelihood * impact)
    """

    scenario: str
    likelihood: float
    impact: float
    risk_level: str
    score: float


class RiskMitigation:
    """风险缓解 — 静态评估与策略手册."""

    PLAYBOOKS: dict[str, dict[str, Any]] = {
        "CRITICAL": {
            "action": "BLOCK_AND_ESCALATE",
            "notify_owner": True,
            "auto_rollback": True,
        },
        "HIGH": {
            "action": "BLOCK_AND_REVIEW",
            "notify_owner": True,
            "auto_rollback": False,
        },
        "MEDIUM": {
            "action": "ALLOW_WITH_REVIEW",
            "notify_owner": False,
            "auto_rollback": False,
        },
        "LOW": {
            "action": "ALLOW_WITH_METRICS",
            "notify_owner": False,
            "auto_rollback": False,
        },
    }

    @staticmethod
    def assess(scenario: str, likelihood: float, impact: float) -> RiskAssessment:
        """评估风险等级.

        阈值:
            score = likelihood * impact
            score >= 0.5 → CRITICAL
            score >= 0.2 → HIGH
            score >= 0.05 → MEDIUM
            else → LOW

        Args:
            scenario: 风险场景描述
            likelihood: 发生概率 (0.0-1.0)
            impact: 影响程度 (0.0-1.0)

        Returns:
            RiskAssessment 包含 risk_level 和 score
        """
        score = likelihood * impact
        if score >= 0.5:
            level = "CRITICAL"
        elif score >= 0.2:
            level = "HIGH"
        elif score >= 0.05:
            level = "MEDIUM"
        else:
            level = "LOW"
        return RiskAssessment(
            scenario=scenario,
            likelihood=likelihood,
            impact=impact,
            risk_level=level,
            score=score,
        )

    @staticmethod
    def get_mitigation_playbook(level: str) -> dict[str, Any]:
        """获取风险等级对应的缓解策略手册.

        Args:
            level: 风险等级 (CRITICAL/HIGH/MEDIUM/LOW)

        Returns:
            dict 包含 action 字段
        """
        return RiskMitigation.PLAYBOOKS.get(
            level,
            {"action": "ALLOW_WITH_METRICS", "notify_owner": False, "auto_rollback": False},
        )


__all__ = [
    "RiskAssessment",
    "RiskMitigation",
]
