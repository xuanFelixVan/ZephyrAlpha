# [A_module] module_id=MOD-RES__core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.governance._core
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增导出须同步更新__init__.py的__all__
# [CONSUMERS] zephyr.governance.__init__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_escalation_engine_imports.py

from zephyr.governance.escalation_engine import EscalationEngine
from zephyr.governance.escalation_models import (
    EscalationEvent,
    EscalationLevel,
    EscalationResult,
    EscalationRule,
    EscalationState,
    RuleCategory,
)
from zephyr.governance.adapter import (
    EscalationDecision,
    OperationType,
    check_operation,
    escalate_if_needed,
)
from zephyr.governance.blueprint_code_consistency import check_blueprint_consistency

_SUBMODULES = [
    "a2a_failure",
    "account_isolator",
    "consequence_manager",
    "context_package",
    "context_switch_governor",
    "cross_assistant_adapter",
    "cross_session_correlator",
    "escalation_api",
    "escalation_fatigue_manager",
    "escalation_loop_detector",
    "escalation_smoke_tests",
    "interrupt_handler",
    "last_resort_watchdog",
    "memory_provenance",
    "multi_turn_intent_analyzer",
    "mvep_orchestrator",
    "objective_tracker",
    "protocol_self_context",
    "protocol_state_store",
    "strategy_portfolio",
    "strategy_scoper",
    "subagent_hook_propagator",
    "vigil_runtime",
]

__all__ = [
    "EscalationEngine",
    "EscalationEvent",
    "EscalationLevel",
    "EscalationResult",
    "EscalationRule",
    "EscalationState",
    "RuleCategory",
    "EscalationDecision",
    "OperationType",
    "check_operation",
    "escalate_if_needed",
    "check_blueprint_consistency",
]
