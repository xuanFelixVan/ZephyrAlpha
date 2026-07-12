# [A_module] module_id=MOD-UNK_verifiers | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""feedback-loop.verifiers — auto-generated package init."""

from . import (
    ab_test,
    action_explainability,
    ai_comment_veracity,
    attack_simulator,
    auto_rollback,
    build_reproducibility_verifier,
    canary_repair,
    cascading_rollback_analyzer,
    cross_blueprint_contract_drift,
    cross_module_integration,
    cross_session_knowledge_integrity,
    digital_twin_sandbox,
    dry_run_sandbox,
    federated_protocol,
    golden_test_external,
    no_llm_degradation,
    pre_flight_simulator,
    preventive_repair,
    rollback_integrity,
    sim2real_calibration,
    stochastic_diagnosis_verifier,
    toctou_revalidation,
    verification_engine,
)

__all__ = [
    "ab_test",
    "action_explainability",
    "ai_comment_veracity",
    "attack_simulator",
    "auto_rollback",
    "build_reproducibility_verifier",
    "canary_repair",
    "cascading_rollback_analyzer",
    "cross_blueprint_contract_drift",
    "cross_module_integration",
    "cross_session_knowledge_integrity",
    "digital_twin_sandbox",
    "dry_run_sandbox",
    "federated_protocol",
    "golden_test_external",
    "no_llm_degradation",
    "pre_flight_simulator",
    "preventive_repair",
    "rollback_integrity",
    "sim2real_calibration",
    "stochastic_diagnosis_verifier",
    "toctou_revalidation",
    "verification_engine",
]
