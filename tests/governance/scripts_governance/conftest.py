# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-305 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.scripts_governance.conftest
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-305 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""pytest conftest for tests/governance/scripts_governance/ — 修复路径解析.

背景：test_check_vocab_hardcode.py 原位于 tests/（parents[1]=repo root），
后被移动到 tests/governance/scripts_governance/（parents[1]=tests/governance/），
但文件内的 parents[1] 路径设置未同步更新，导致 import check_vocab_hardcode 失败。

本 conftest 在 test collection 前将正确的 d3_metadata 路径加入 sys.path，
使 `import check_vocab_hardcode` 能找到模块（不修改测试文件本身）。
"""

from __future__ import annotations

import sys
from pathlib import Path

# tests/governance/scripts_governance/conftest.py
# parents[0]=scripts_governance/ parents[1]=governance/ parents[2]=tests/ parents[3]=repo root
_REPO_ROOT = Path(__file__).resolve().parents[3]
_D3_META = _REPO_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_D3_META) not in sys.path:
    sys.path.insert(0, str(_D3_META))
