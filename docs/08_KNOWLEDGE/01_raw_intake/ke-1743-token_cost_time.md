---
module_id: KE-1653--------token---cost---time-002
status: active
title: 2.1 五级预算体系（Token + Cost + Time 三维）
category: module_blueprint
ttl: permanent
---

# 2.1 五级预算体系（Token + Cost + Time 三维）

2.1 五级预算体系（Token + Cost + Time 三维）

> **决策 D-024-02（v0.5.0 修订）**：从 Token/Cost 双维升级为 Token/Cost/Time 三维。Stanford Token Economics 论文 (2026.4) 验证——wall-clock 时间和 token 消耗仅呈弱相关，必须独立监控。Oracle Runtime Budget Guardrails 明确提出 "given elapsed time, observed cost, and remaining work estimate, decide to continue/narrow/reroute/escalate/stop"。

```yaml
budget_levels:
  # ── Level 5: 最粗粒度 ──
  global_level:
    description: "全局周预算（solo maintainer 场景 weekly 粒度比 daily 更合理）"
    soft_limit: 500000           # tokens/week，约 $3-5/week（按 GPT-4o 价格）
    hard_limit: 750000
    action_on_soft_exceed: "全局通知 + 建议暂停非关键任务"
    action_on_hard_exceed: "全局只读模式"
    reset: "每周一 00:00 UTC"
    borrow_pool: true            # 允许跨周借用（最多预支下周 20%）

  # ── Level 4 ──
  session_level:
    description: "单次会话预算（一次施工对话的累计消耗）"
    soft_limit: 8000             # tokens，到达触发通知
    hard_limit: 12000            # tokens，到达触发降级
    action_on_soft_exceed: "WARNING 日志 + 建议 /compact"
    action_on_hard_exceed: "降级到最小上下文"
    reset: "会话结束"

  # ── Level 3 ──
  task_level:
    description: "单任务预算（一个蓝图层/一个Phase的施工）"
    soft_limit: 4000
    hard_limit: 6000
    action_on_soft_exceed: "暂停任务 + 建议拆分"
    action_on_hard_exceed: "暂停任务 + 委托给新会话"
    pool_share: true             # 同一 Session 内的 Task 之间弹性共享预算

  # ── Level 2: token spiral 锚点 ──
  turn_level:
    description: "单轮 ReAct 迭代预算（一次 think→act→observe 循环）"
    soft_limit: 1500
    hard_limit: 2500
    action_on_soft_exceed: "检查是否陷入循环 + 建议简化工具调用"
    action_on_hard_exceed: "强制终止本轮 + 返回部分结果 + 循环指纹记录"

  # ── Level 1: 最细粒度 ──
  request_level:
    description: "单次 API 调用预算"
    input_limit: 32000           # max input tokens per request
    output_limit: 4096           # max output tokens per request
    reasoning_limit: 8000        # reasoning tokens 专项预算（reasoning models 的 thinking 不可见但计费）
    tool_calls_limit: 10         # max tool calls per request
    action_on_exceed: "截断输出 + 建议拆分请求"
```

```yaml
