# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.foundation.serialization
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.io.serialization
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
# [A_module] module_id=MOD-SHR_serialization | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
serialization.py —— Re-export wrapper → canonical: zephyr.shared.io.serialization

本文件是向后兼容的顶层别名。规范实现位于 io/serialization.py。
修改序列化逻辑请编辑 io/serialization.py，不要编辑本文件。
"""

from zephyr.shared.io.serialization import *  # noqa: F403
