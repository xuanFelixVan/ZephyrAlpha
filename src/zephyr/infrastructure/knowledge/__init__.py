# [A_module] module_id=MOD-INF_knowledge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-103 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.knowledge
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS] 
# [ERROR_CONTRACT] 
# [TESTS] 
"""core.knowledge — auto-generated package init."""
from . import ke_linker
from . import ke_structurer
from . import kms_interface

__all__ = ['ke_linker', 'ke_structurer', 'kms_interface']

