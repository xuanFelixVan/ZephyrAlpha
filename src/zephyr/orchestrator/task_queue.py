# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.task_queue
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ActiveTaskQueue — 后台任务轮询与自动分发
==========================================
Blueprint: MOD-TASK_SYSTEM 盲点#9

线程安全的后台调度器：定期扫描 READY 任务，自动 dispatch。

NOTE: 此模块已迁移至 zephyr.orchestrator.core.task_queue，
      本文件仅保留向后兼容的 re-export。
      修复: 消除双重 TaskQueue 实例导致的重复轮询问题。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: task_queue.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: task_queue.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L65；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.orchestrator.core.task_queue import (  # noqa: F401
    ActiveTaskQueue,
    PipelineDispatcher,
    get_queue,
)

# 向后兼容别名（P9 重命名：避免与 infrastructure.queue.TaskQueue 同名冲突）
TaskQueue = ActiveTaskQueue
