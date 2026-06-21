# [A_module] module_id=MOD-INT_serialization | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.integration.shared_08.serialization

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
serialization.py —— Re-export wrapper → canonical: zephyr.integration.shared_08.io.serialization

本文件是向后兼容的顶层别名。规范实现位于 io/serialization.py。
修改序列化逻辑请编辑 io/serialization.py，不要编辑本文件。
"""


from zephyr.integration.shared_08.io.serialization import *  # noqa: F401, F403
