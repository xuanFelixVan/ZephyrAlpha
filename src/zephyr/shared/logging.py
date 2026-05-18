# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.logging

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
logging.py —— Re-export wrapper → canonical: zephyr.shared.observability.logging

本文件是向后兼容的顶层别名。规范实现位于 observability/logging.py。
修改日志逻辑请编辑 observability/logging.py，不要编辑本文件。
"""

from zephyr.shared.observability.logging import *  # noqa: F401, F403
