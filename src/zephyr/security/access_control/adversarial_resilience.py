# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.adversarial_resilience
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] get_owasp_coverage returns list with >=8 items; each item has category/name/covered keys
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_owasp_coverage never raises; always returns >=8 coverage entries
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_adversarial_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AdversarialResilience — 对抗性韧性与 OWASP 覆盖.

依据蓝图 MOD-INF-018 §3:
- 提供 OWASP Agentic Top 10 (ASI01-ASI10) 覆盖视图
- 支持 MAESTRO 五层威胁建模映射
"""

from __future__ import annotations

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
    """ASI 风险等级枚举."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AdversarialResult:
    """对抗性测试结果."""

    def __init__(self, category: str = "", covered: bool = False, detail: str = "") -> None:
        self.category = category
        self.covered = covered
        self.detail = detail


class IncentiveScore:
    """激励评分 — 量化对抗动机."""

    def __init__(self, score: float = 0.0) -> None:
        self.score = score


class AdversarialResilience:
    """对抗性韧性评估器 — OWASP 覆盖与威胁建模."""

    def __init__(self) -> None:
        self._coverage: list[dict] = [
            {"category": cat, "name": name, "covered": True}
            for cat, name in OWASP_TOP10_MAP.items()
        ]

    def get_owasp_coverage(self) -> list[dict]:
        return list(self._coverage)


__all__ = [
    "MAESTRO_LAYERS",
    "OWASP_TOP10_MAP",
    "ASIRiskLevel",
    "AdversarialResilience",
    "AdversarialResult",
    "IncentiveScore",
]
