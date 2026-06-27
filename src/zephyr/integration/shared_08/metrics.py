# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared_08.metrics
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.shared.shared_services.observability_02.metrics
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
# [A_module] module_id=MOD-INT_metrics | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
metrics.py —— Re-export wrapper → canonical: zephyr.infrastructure.shared_services.observability_02.metrics

本文件是向后兼容的顶层别名。规范实现位于 observability/metrics.py。
修改指标收集逻辑请编辑 observability/metrics.py，不要编辑本文件。
"""

from zephyr.shared.shared_services.observability_02.metrics import *  # noqa: F403
