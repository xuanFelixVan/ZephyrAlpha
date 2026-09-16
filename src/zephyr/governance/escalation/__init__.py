# [BLUEPRINT] MOD-INF-021 | (auto-injected by S4 reconciler) | §
# [TESTS] tests/infrastructure/test_delegation_safety.py; tests/infrastructure/adversarial/test_escalation_adversarial.py; tests/infrastructure/escalation/test_escalation_e2e.py; tests/infrastructure/escalation/test_escalation_engine.py; tests/infrastructure/escalation/test_escalation_hooks.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 5 个测试）
# [TTL] permanent
# [TTL] permanent
# 代理包：将 zephyr.governance.escalation 重定向到实际模块
# 测试文件导入 from zephyr.governance.escalation import EscalationEngine, RuleCategory, ...
# 实际定义在 escalation_engine.py 和 escalation_models.py

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/escalation/escalation__init__.yaml
"""

from zephyr.governance.escalation.escalation_engine import (
    EscalationEngine,
)
from zephyr.governance.escalation.escalation_models import (
    DelegationRecord,
    DelegationStrategy,
    EconomicGuard,
    EscalationEvent,
    EscalationLevel,
    EscalationResult,
    EscalationRule,
    EscalationState,
    RuleCategory,
)
from zephyr.governance.intelligence_governance.delegation_engine import (
    DelegationEngine,
)
from zephyr.governance.resilience_governance.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "DelegationEngine",
    "DelegationRecord",
    "DelegationStrategy",
    "EconomicGuard",
    "EscalationEngine",
    "EscalationEvent",
    "EscalationLevel",
    "EscalationResult",
    "EscalationRule",
    "EscalationState",
    "RuleCategory",
    "alternative_path_blocker",
    "consequence_manager",
    "contracts",
    "escalation_api",
    "escalation_fatigue_manager",
    "escalation_loop_detector",
    "escalation_metrics",
    "escalation_models",
    "escalation_smoke_tests",
    "git_hook_pre_scanner",
    "human_factors",
    "identity_verifier",
    "incident_response",
    "order_state_escalator",
    "result_types",
    "spof_checker",
    "triage",
]
