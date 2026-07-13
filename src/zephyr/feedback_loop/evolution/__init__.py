# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-UNK_evolution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.evolution
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""feedback-loop.evolution — auto-generated package init."""

from . import (
    auto_reward,
    conformal_prediction,
    cross_gen_validation,
    dynamic_threshold,
    ewc_kb_review,
    failure_replay,
    graduated_activation_protocol,
    hypernetwork,
    knowledge_distillation,
    online_feature_importance,
    prompt_factory_governance,
    prompt_optimization_regression_detector,
    prompt_self_optimization_loop,
    self_modification_rate_limiter,
    self_reflection,
    self_upgrade_canary,
    semantic_intent_preservation_guard,
    teacher_transfer,
    training_data_gov,
)

__all__ = [
    "auto_reward",
    "conformal_prediction",
    "cross_gen_validation",
    "dynamic_threshold",
    "ewc_kb_review",
    "failure_replay",
    "graduated_activation_protocol",
    "hypernetwork",
    "knowledge_distillation",
    "online_feature_importance",
    "prompt_factory_governance",
    "prompt_optimization_regression_detector",
    "prompt_self_optimization_loop",
    "self_modification_rate_limiter",
    "self_reflection",
    "self_upgrade_canary",
    "semantic_intent_preservation_guard",
    "teacher_transfer",
    "training_data_gov",
]
