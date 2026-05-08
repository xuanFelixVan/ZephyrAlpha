---
module_id: KE-module_blu-illegalstatetransitionerr-000
title: 合法状态转移（非法转移直接抛 IllegalStateTransitionError）
category: module_blueprint
---

# 合法状态转移（非法转移直接抛 IllegalStateTransitionError）

合法状态转移（非法转移直接抛 IllegalStateTransitionError）
ALLOWED_TRANSITIONS: dict[TaskState, set[TaskState]] = {
    TaskState.DRAFT:      {TaskState.QUEUED, TaskState.CANCELLED},
    TaskState.QUEUED:     {TaskState.ASSIGNED, TaskState.CANCELLED},
    TaskState.ASSIGNED:   {TaskState.RUNNING, TaskState.BLOCKED, TaskState.CANCELLED},
    TaskState.RUNNING:    {TaskState.REVIEWING, TaskState.BLOCKED, TaskState.FAILED,
                           TaskState.HALLUCINATING, TaskState.CANCELLED},
    TaskState.BLOCKED:    {TaskState.RUNNING, TaskState.CANCELLED, TaskState.FAILED},
    TaskState.REVIEWING:  {TaskState.COMPLETED, TaskState.FAILED, TaskState.RUNNING},  # review 挂后退回 RUNNING 允许重试
    TaskState.HALLUCINATING: {TaskState.CANCELLED, TaskState.FAILED},
    TaskState.COMPLETED:  set(),  # 终态
    TaskState.FAILED:     set(),  # 终态
    TaskState.CANCELLED:  set(),  # 终态
}
```
