# [A_module] module_id=MOD-INT_schemas | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.integration.shared_08.schemas

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
schemas.py —— Re-export wrapper → canonical: zephyr.integration.shared.schema.schemas

本文件是向后兼容的顶层别名。规范实现位于 schema/schemas.py。
修改数据模型/枚举请编辑 schema/schemas.py，不要编辑本文件。
"""


from zephyr.integration.shared.schema.schemas import *  # noqa: F401, F403
