# [A_module] module_id=MOD-INT_cache | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.integration.shared_08.cache

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
cache.py —— Re-export wrapper → canonical: zephyr.infrastructure.shared_services.infra_06.cache

本文件是向后兼容的顶层别名。规范实现位于 infra/cache.py。
修改缓存逻辑请编辑 infra/cache.py，不要编辑本文件。
"""


# STUB: from .infra.cache import *  # noqa: F401, F403
# Reason: shared_08/infra/ subpackage does not exist; canonical is infrastructure.shared_services.infra_06.cache
from zephyr.shared.shared_services.infra_06.cache import *  # noqa: F401, F403
