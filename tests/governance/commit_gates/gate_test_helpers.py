# [BLUEPRINT] MOD-GATE_ENGINE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test_helpers] module_id=SH-TEST-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""公共模块别名（R5 公共化）— 从 _gate_test_helpers 重新导出。

测试通过 ``from tests.governance.commit_gates.gate_test_helpers import ...`` 导入，
本模块提供公共路径，实际实现在 ``_gate_test_helpers.py``。
"""

# 同目录直导：repo tests 命名空间被 site-packages 同名 regular 包遮蔽（import tests
# 解析到 site-packages/tests，tests.governance 不存在），绝对导入转发不可用
from _gate_test_helpers import *  # noqa: F401,F403
from _gate_test_helpers import (  # noqa: F401
    make_mock_gateway,
)
