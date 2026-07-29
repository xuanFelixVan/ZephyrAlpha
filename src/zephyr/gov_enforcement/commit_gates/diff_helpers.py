# [A_module] module_id=SH-GOV-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-CG | docs/03_modules/_domain_governance/blueprint.md
# [TTL] permanent
"""公共模块别名（R5 公共化）— 从 _diff_helpers 重新导出所有公共符号。

测试通过 ``from zephyr.gov_enforcement.commit_gates.diff_helpers import ...`` 导入，
本模块提供公共路径，实际实现在 ``_diff_helpers.py``。
"""
from zephyr.gov_enforcement.commit_gates._diff_helpers import (  # noqa: F401
    __all__,
)
from zephyr.gov_enforcement.commit_gates._diff_helpers import *  # noqa: F401,F403
