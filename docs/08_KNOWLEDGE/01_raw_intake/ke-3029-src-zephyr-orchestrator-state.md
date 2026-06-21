---
module_id: KE-2929
status: active
title: src/zephyr/orchestrator/state.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/orchestrator/state.py (experimental 产出)

src/zephyr/orchestrator/state.py (experimental 产出)

from enum import Enum

class TaskState(str, Enum):
    DRAFT      = "draft"       # 已创建未提交
    QUEUED     = "queued"      # 已入队等待 Agent 认领
    ASSIGNED   = "assigned"    # 被 Agent claim 未开始
    RUNNING    = "running"     # 执行中
    BLOCKED    = "blocked"     # 被依赖阻塞
    REVIEWING  = "reviewing"   # 等待 LSG 审查输出
    COMPLETED  = "completed"   # 成功完成
    FAILED     = "failed"      # 失败
    CANCELLED  = "cancelled"   # 主动取消
    HALLUCINATING = "hallucinating"  # 幻觉检测触发，隔离待清理
