---
module_id: KE-1780
status: active
title: 2.20 Timeout Guard（并行监控线程）
category: module_blueprint
---

# 2.20 Timeout Guard（并行监控线程）

2.20 Timeout Guard（并行监控线程）

> **决策 D-024-18（🆕 v0.5.0）**：AgentGuard (2026.4) 三大 guard 之一——Timeout Guard = wall-clock kill switch。这是一个独立于预算链的并行线程——不依赖 L0-L6 降级或 Pre-flight Gate，一旦触发即强行 abort。

```yaml
timeout_guard:
  description: "独立并行线程——wall-clock 超时即 abort，不经过降级协商流程"
  lifecycle_position: "in_flight（与 Stream Abort Guard 并行运行）"
  implementation: "asyncio 独立 task → 每个 Session 启动一个 daemon timer"

  session_timer:
    countdown: 28800              # 8 小时（来自 §2.1 time_budget）
    on_expiry:
      action: "FORCE_ABORT——所有活跃请求立即终止"
      pre_action: "保存 Action History + 生成 resume checkpoint + 写入 audit trail"
      message: "⏰ Session 时间预算已耗尽（8h）——当前进度已保存。下次启动自动恢复。"

  task_timer:
    countdown: 3600               # 1 小时
    on_expiry:
      action: "FORCE_ABORT 当前 Task + 自动委托到新 Task"
      message: "⏰ 任务超时（1h）——已自动拆分并委托剩余工作到新任务"

  request_timer:
    countdown: 120                # 2 分钟
    on_expiry:
      action: "CANCEL streaming SSE + ABORT"
      auto_retry: true            # 自动重试一次（不同 Provider 或模型）
```
