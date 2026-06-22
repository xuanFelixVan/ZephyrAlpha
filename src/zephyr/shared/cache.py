# [A_module] module_id=MOD-SHR_cache | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.cache

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
cache.py —— Re-export wrapper → canonical: zephyr.shared.infra.cache

本文件是向后兼容的顶层别名。规范实现位于 infra/cache.py。
修改缓存逻辑请编辑 infra/cache.py，不要编辑本文件。
"""

from .infra.cache import *  # noqa: F403
