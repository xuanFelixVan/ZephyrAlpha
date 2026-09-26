# [A_test] module_id: MOD-TEST-RB14-BASE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | docs/_working/commit_speedup_campaign/90_verification/red_blue_pkg14_report.md | §
# [MODULE] governance.red_blue_pkg14.conftest
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; governance.red_blue_pkg14._common
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/
# [MATURITY] testing
# [INVARIANTS] fixture 只做转发；实现真源=_common.py（全 tmp 沙盒，绝不触生产活体）
# [MODIFY-GUARD] 包14 红蓝极限对抗 7 场景（st-commitspeed-tbl-20260924）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本目录
# [TTL] task_bound
"""red_blue_pkg14 conftest — pytest fixture 转发层（实现真源=_common.py）。"""

from __future__ import annotations

from governance.red_blue_pkg14._common import sb_queue, sb_repo  # noqa: F401 — fixture 转发
