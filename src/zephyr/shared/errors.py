# [A_module] module_id=MOD-SHR_errors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.errors

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
errors.py —— Re-export wrapper → canonical: zephyr.shared.foundation.errors

本文件是向后兼容的顶层别名。规范实现位于 foundation/errors.py。
修改异常层次请编辑 foundation/errors.py，不要编辑本文件。
"""

from zephyr.shared.foundation.errors import *  # noqa: F401, F403
