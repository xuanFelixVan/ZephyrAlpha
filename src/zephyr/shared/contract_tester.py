# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.contract_tester

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Re-export wrapper — canonical implementation at zephyr.l01_infrastructure.contract_tester.

TD-SHARED-001: 发散副本统一为 re-export wrapper，消除代码漂移。
"""
from zephyr.l01_infrastructure.contract_tester import *  # noqa: F401,F403
from zephyr.l01_infrastructure.contract_tester import ContractTester, ContractTestResult  # noqa: F401
