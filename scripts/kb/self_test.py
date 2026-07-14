# [BLUEPRINT] MOD-INF-005 | scripts/kb/self_test.py | §
# [MODULE] scripts.kb.self_test
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_kb.self_test
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 仅作为CLI入口; 不实现体检逻辑
# [MODIFY-GUARD] 真实实现变更时同步CLI参数
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 透传SelfTest.cli()的退出码
# [TESTS] tests/kb/test_kb_self_test.py
# [TTL] task_bound
"""KB 13项一键体检 — CLI入口薄包装

实际实现位于 zephyr.gov_kb.self_test.SelfTest
用法:
    python scripts/kb/self_test.py        # 全量13项
    python scripts/kb/self_test.py --json # JSON输出
"""

from __future__ import annotations

import sys

from zephyr.gov_kb.self_test import SelfTest


def main() -> None:
    sys.exit(SelfTest().cli())


if __name__ == "__main__":
    main()
