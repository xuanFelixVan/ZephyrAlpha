# [A_module] module_id=MOD-INF-reliability | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.reliability
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
core.reliability — auto-generated package init.

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/reliability/reliability__init__.yaml
"""

# WO-12/C7：circuit_breaker.py 已于 1ddcd089cf 作为死模块删除（ARCH-032 迁 governance 后
# 无存续引用），但本 __init__ 残留幽灵引用致整包不可导入（ImportError: partially
# initialized）。清残留引用，非结构变更。
from typing import Final

from . import context_guard

__all__: Final = ["context_guard"]
