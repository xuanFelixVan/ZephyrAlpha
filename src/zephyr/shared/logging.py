# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.shared.logging
# [DOMAIN] D-SHARED
# [DEPENDENCIES] zephyr.ops.observability.logging
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_logging | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""
logging.py —— Re-export wrapper → canonical: zephyr.ops.observability.logging

本文件是向后兼容的顶层别名。规范实现位于 observability/logging.py。
修改日志逻辑请编辑 observability/logging.py，不要编辑本文件。
"""

from zephyr.ops.observability.logging import *  # noqa: F403
