# [A_module] module_id=SH-FB-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK-014 | docs/03_modules/_domain_feedback_loop/blueprint.md
# [TTL] permanent
"""公共模块别名（R5 公共化）— 从 _gen_inherited 重新导出所有公共符号。

测试通过 ``from zephyr.feedback_loop.gen_inherited import BASE, SKELETONS`` 导入，
本模块提供公共路径，实际实现在 ``_gen_inherited.py``。
"""
from zephyr.feedback_loop._gen_inherited import (  # noqa: F401
    BASE,
    SKELETONS,
)
from zephyr.feedback_loop._gen_inherited import *  # noqa: F401,F403
