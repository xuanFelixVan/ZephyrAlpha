# [A_test] module_id: SRC-TST-1816 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-446 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.agent_rbac.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""conftest for tests/unit/agent_rbac/ — 确保 src/ 在 sys.path.

ARCH-035 治本：删除路径劫持（_ensure_stub/spec_from_file_location 从 phantom path
agent-rbac/ 加载），改用 Python 正常包机制解析 zephyr.security.access_control。
测试文件直接 ``from zephyr.security.access_control.guards.X import Y``。
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
