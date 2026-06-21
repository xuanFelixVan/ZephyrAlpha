# [A_module] module_id=MOD-SHR_context | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.context

# [INVARIANTS] re-export shim only; canonical source is zephyr.shared.utils.context

# [MODIFY-GUARD] do not add logic here; modify zephyr.shared.utils.context instead

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
context.py —— Re-export wrapper → canonical: zephyr.shared.utils.context

本文件是向后兼容的顶层别名。规范实现位于 utils/context.py。
修改上下文逻辑请编辑 utils/context.py，不要编辑本文件。
"""

from zephyr.shared.utils.context import *  # noqa: F401, F403
from zephyr.shared.utils.context import __all__
