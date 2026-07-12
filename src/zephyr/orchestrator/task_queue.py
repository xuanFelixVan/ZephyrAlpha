# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.task_queue
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.__init__
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
# [A_module] module_id=MOD-ORC_task_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ActiveTaskQueue — 后台任务轮询与自动分发
==========================================
Blueprint: MOD-TASK_SYSTEM 盲点#9

线程安全的后台调度器：定期扫描 READY 任务，自动 dispatch。

NOTE: 此模块已迁移至 zephyr.trading.orchestrator.core.task_queue，
      本文件仅保留向后兼容的 re-export。
      修复: 消除双重 TaskQueue 实例导致的重复轮询问题。
"""

from __future__ import annotations

from zephyr.orchestrator.core.task_queue import (  # noqa: F401
    ActiveTaskQueue,
    PipelineDispatcher,
    get_queue,
)

# 向后兼容别名（P9 重命名：避免与 infrastructure.queue.TaskQueue 同名冲突）
TaskQueue = ActiveTaskQueue
