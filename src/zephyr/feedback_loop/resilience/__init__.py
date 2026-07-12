# [A_module] module_id=MOD-RES_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.resilience
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""feedback-loop.resilience — auto-generated package init."""

from . import (
    config_hot_reload_guard,
    deadman_switch,
    dr_automation,
    graceful_degradation_planner,
    multi_instance_coord,
    oscillation_damping,
    resource_starvation_aware,
    self_api_throttle_defense,
    split_brain_quorum,
)

__all__ = [
    "config_hot_reload_guard",
    "deadman_switch",
    "dr_automation",
    "graceful_degradation_planner",
    "multi_instance_coord",
    "oscillation_damping",
    "resource_starvation_aware",
    "self_api_throttle_defense",
    "split_brain_quorum",
]
