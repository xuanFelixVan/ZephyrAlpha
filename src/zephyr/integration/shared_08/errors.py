# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.errors
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_errors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
errors.py —— Re-export wrapper → canonical: zephyr.integration.shared_08.foundation.errors

本文件是向后兼容的顶层别名。规范实现位于 foundation/errors.py。
修改异常层次请编辑 foundation/errors.py，不要编辑本文件。
"""

from zephyr.integration.shared_08.foundation.errors import *  # noqa: F403
