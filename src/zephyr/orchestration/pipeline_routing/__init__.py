# [A_module] module_id=MOD-ORC_proxy_pipeline_routing | layer=package | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] GOV-037-CONVERGENCE | docs/02_enterprise_architecture/governance_convergence_plan.md | P0
# [MODULE] zephyr.orchestration.pipeline_routing
# [INVARIANTS] 代理包——__path__ 重定向到 zephyr.integration；不持有业务逻辑
# [MODIFY-GUARD] OPS-2026062101
# [CONSUMERS] throttle.py; resume.py; trigger_router.py; task_model_learner.py 等 import_module("zephyr.orchestration.pipeline_routing.*")
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModuleNotFoundError if zephyr.integration target missing
# [TESTS] tests/unit/test_orchestration_proxy.py

"""
zephyr.orchestration.pipeline_routing — 代理子包

通过 __path__ 重定向到 zephyr.integration 的物理目录，
使 import_module("zephyr.orchestration.pipeline_routing.X") 能找到
zephyr/integration/X.py。

创建依据：OPS-2026062101（zephyr.orchestration 断裂点修复）
"""

import zephyr.integration as _target

# 将本子包的搜索路径指向 zephyr.integration 的物理目录
# Python 导入系统会据此查找子模块
__path__ = list(_target.__path__)

del _target
