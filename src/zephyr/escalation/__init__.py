"""
Escalation Protocol — MOD-INF-022

Rule-driven escalation with auto-delegation, circuit breaker, and economic guards.
Blueprint: docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md
"""
from zephyr.escalation.escalation_models import (
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
from zephyr.escalation.escalation_engine import EscalationEngine
from zephyr.escalation.delegation_engine import DelegationEngine
from zephyr.escalation.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState
from zephyr.escalation.self_test import run_self_test, SelfTestReport, HealthLevel
from zephyr.escalation.adapter import escalate_if_needed, check_operation, EscalationDecision, OperationType
from zephyr.escalation.blueprint_code_consistency import check_blueprint_consistency

__version__ = "0.14.0"
__all__ = [
    "DelegationRecord",
    "DelegationStrategy",
    "EconomicGuard",
    "EscalationEvent",
    "EscalationLevel",
    "EscalationResult",
    "EscalationRule",
    "EscalationState",
    "RuleCategory",
    "EscalationEngine",
    "DelegationEngine",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "run_self_test",
    "SelfTestReport",
    "HealthLevel",
    "escalate_if_needed",
    "check_operation",
    "EscalationDecision",
    "OperationType",
    "check_blueprint_consistency",
    "escalation_models",
    "self_test",
    "blueprint_code_consistency",
    "adapter",
    "anti_automation_bias",
    "slo_contract",
]
