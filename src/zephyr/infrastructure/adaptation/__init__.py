# [A_module] module_id=MOD-INF_adaptation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-082 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.adaptation
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""core.adaptation — auto-generated package init."""
from . import execution_tuner
from . import prompt_version_manager

__all__ = ['execution_tuner', 'prompt_version_manager']

