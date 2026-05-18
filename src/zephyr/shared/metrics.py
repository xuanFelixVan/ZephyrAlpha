# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.metrics

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
metrics.py —— Re-export wrapper → canonical: zephyr.shared.observability.metrics

本文件是向后兼容的顶层别名。规范实现位于 observability/metrics.py。
修改指标收集逻辑请编辑 observability/metrics.py，不要编辑本文件。
"""

from zephyr.shared.observability.metrics import *  # noqa: F401, F403
