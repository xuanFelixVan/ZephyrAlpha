# [A_module] module_id=MOD-RES_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.ops.resilience
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""feedback-loop.resilience — auto-generated package init."""
from . import config_hot_reload_guard
from . import deadman_switch
from . import dr_automation
from . import graceful_degradation_planner
from . import multi_instance_coord
from . import oscillation_damping
from . import resource_starvation_aware
from . import self_api_throttle_defense
from . import split_brain_quorum

__all__ = ['config_hot_reload_guard', 'deadman_switch', 'dr_automation', 'graceful_degradation_planner', 'multi_instance_coord', 'oscillation_damping', 'resource_starvation_aware', 'self_api_throttle_defense', 'split_brain_quorum']

