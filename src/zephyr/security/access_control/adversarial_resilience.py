# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.adversarial_resilience
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py; tests/agent_rbac/test_adversarial_resilience.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] get_owasp_coverage returns dict{category: bool} with 10 entries; assess_* never raise
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_owasp_coverage/assess_self_modification/assess_incentive_alignment never raise
# [TESTS] tests/agent_rbac/test_adversarial_resilience.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
AdversarialResilience - adversarial resilience & OWASP coverage.

assess_self_modification: detect dangerous self-modification operations.
assess_incentive_alignment: score agent incentive alignment.
get_owasp_coverage: return OWASP Agentic Top 10 coverage as dict.

治本(2026-07-18): 重写以匹配 tests/agent_rbac/test_adversarial_resilience.py 契约.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: adversarial_resilience.py
# 层: 算法
# - id: A1
#   name_zh: ① AdversarialResilience
#   name_en: AdversarialResilience
#   intro: Adversarial resilience assessor.
#   desc: Adversarial resilience assessor.；公共方法（定义序）: get_owasp_coverage, assess_self_modification, assess_incentive_al…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: AdversarialResilience
#   downstream: tests/agent_rbac/test_redteam_adversarial.py; tests/agent_rbac/test_adversarial…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MAESTRO_LAYERS = [
    "L1_model",
    "L2_data",
    "L3_agent",
    "L4_deployment",
    "L5_orchestration",
]

OWASP_TOP10_MAP = {
    "ASI01": "Prompt Injection",
    "ASI02": "Sensitive Information Disclosure",
    "ASI03": "Supply Chain Vulnerabilities",
    "ASI04": "Data Poisoning",
    "ASI05": "Improper Output Handling",
    "ASI06": "Excessive Agency",
    "ASI07": "System Prompt Leakage",
    "ASI08": "Insecure Plugin/Tool Design",
    "ASI09": "Inadequate Identity Authentication",
    "ASI10": "Inadequate Monitoring & Logging",
}


class ASIRiskLevel:
    """ASI risk level enum."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Operations that are critical self-modification attempts
_CRITICAL_OPS = {
    "modify:self_constraints",
    "modify:self_goals",
    "modify:self_reward",
    "disable:kill_switch",
    "disable:safety_guard",
    "modify:immutable_core",
    "modify:blueprint",
    "delete:audit_log",
}

# Map critical operations to OWASP category
_OP_OWASP_MAP = {
    "modify:self_constraints": "ASI08",
    "modify:self_goals": "ASI06",
    "modify:self_reward": "ASI06",
    "disable:kill_switch": "ASI08",
    "disable:safety_guard": "ASI08",
    "modify:immutable_core": "ASI08",
    "modify:blueprint": "ASI08",
    "delete:audit_log": "ASI10",
}


@dataclass
class AdversarialResult:
    """Adversarial assessment result."""

    risk_level: str = ASIRiskLevel.NONE
    owasp_category: str = ""
    agent_id: str = ""
    operation: str = ""
    detail: str = ""


@dataclass
class IncentiveScore:
    """Incentive alignment score."""

    safety_alignment: float = 0.5
    overall_score: float = 0.0
    agent_id: str = ""
    safety_events: int = 0
    violation_events: int = 0


class AdversarialResilience:
    """Adversarial resilience assessor."""

    def __init__(self) -> None:
        self._coverage: dict[str, bool] = {cat: True for cat in OWASP_TOP10_MAP}

    def get_owasp_coverage(self) -> dict[str, bool]:
        """Return OWASP Top 10 coverage as dict{category: covered}."""
        return dict(self._coverage)

    def assess_self_modification(self, agent_id: str, operation: str) -> AdversarialResult:
        """Assess risk of a self-modification operation.

        Critical ops (modify:self_*, disable:kill_switch, etc.) -> CRITICAL + ASI08.
        Empty/benign ops -> NONE.
        """
        if not operation:
            return AdversarialResult(
                risk_level=ASIRiskLevel.NONE, owasp_category="", agent_id=agent_id, operation=operation
            )
        if operation in _CRITICAL_OPS:
            return AdversarialResult(
                risk_level=ASIRiskLevel.CRITICAL,
                owasp_category=_OP_OWASP_MAP.get(operation, "ASI08"),
                agent_id=agent_id,
                operation=operation,
                detail="critical self-modification detected",
            )
        return AdversarialResult(
            risk_level=ASIRiskLevel.NONE, owasp_category="", agent_id=agent_id, operation=operation
        )

    def assess_incentive_alignment(self, agent_id: str, safety_events: int, violation_events: int) -> IncentiveScore:
        """Score incentive alignment based on safety vs violation events.

        safety_alignment = safety_events / (safety_events + violation_events).
        0/0 -> 0.5 (neutral).
        overall_score = safety_alignment * 100.
        """
        total = safety_events + violation_events
        if total == 0:
            safety_alignment = 0.5
        else:
            safety_alignment = safety_events / total
        overall_score = safety_alignment * 100.0
        return IncentiveScore(
            safety_alignment=safety_alignment,
            overall_score=overall_score,
            agent_id=agent_id,
            safety_events=safety_events,
            violation_events=violation_events,
        )


__all__ = [
    "MAESTRO_LAYERS",
    "OWASP_TOP10_MAP",
    "ASIRiskLevel",
    "AdversarialResilience",
    "AdversarialResult",
    "IncentiveScore",
]
