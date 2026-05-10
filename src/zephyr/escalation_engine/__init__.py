"""
Escalation Protocol — MOD-INF-022

Rule-driven escalation with auto-delegation, circuit breaker, and economic guards.
Blueprint: docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md
"""

from zephyr.escalation_engine.adapter import EscalationDecision, OperationType, check_operation, escalate_if_needed
from zephyr.escalation_engine.blueprint_code_consistency import check_blueprint_consistency
from zephyr.escalation_engine.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState
from zephyr.escalation_engine.delegation_engine import DelegationEngine
from zephyr.escalation_engine.escalation_engine import EscalationEngine
from zephyr.escalation_engine.escalation_models import (
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
from zephyr.escalation_engine.self_test import HealthLevel, SelfTestReport, run_self_test

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
