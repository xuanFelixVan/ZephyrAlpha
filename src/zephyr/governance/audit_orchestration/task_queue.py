# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] zephyr.governance.audit_orchestration.task_queue
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_orchestration.core.task_queue
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_task_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
ActiveTaskQueue — 后台任务轮询与自动分发
==========================================
Blueprint: MOD-TASK_SYSTEM 盲点#9

线程安全的后台调度器：定期扫描 READY 任务，自动 dispatch。

NOTE: 此模块已迁移至 zephyr.governance.audit_orchestration.core.task_queue，
      本文件仅保留向后兼容的 re-export。
      修复: 消除双重 TaskQueue 实例导致的重复轮询问题。
"""

from __future__ import annotations

from zephyr.governance.audit_orchestration.core.task_queue import (  # noqa: F401
    PipelineDispatcher,
    TaskQueue,
    get_queue,
)
