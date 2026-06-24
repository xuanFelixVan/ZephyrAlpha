---
module_id: KE-2989---------------oracle-ru-000
status: active
title: ── v0.5.0 新增：额外的自适应干预动作（Oracle Runtime Budget Guardrails 对标）──
category: module_blueprint
---

# ── v0.5.0 新增：额外的自适应干预动作（Oracle Runtime Budget Guardrails 对标）──

── v0.5.0 新增：额外的自适应干预动作（Oracle Runtime Budget Guardrails 对标）──
adaptive_interventions:
  description: "在传统的 degrade/stop 二元模型之外，Oracle 2026 论文明确了 Narrow 和 Reroute 两种轻量干预"

  narrow_scope:
    description: "预算紧张时收窄任务范围——不是降级，而是只做最关键的 20%"
    trigger: "task_budget_used > 70% AND task_progress < 30%"
    action: "自动注入 system prompt '你的预算已消耗 70% 但产出仅 30%——请仅完成核心子任务，跳过优化/美化/文档'"
    visual: "终端显示 '🎯 范围收窄——仅完成核心逻辑，跳过: [单元测试, 文档, 格式化]'"
    reversible: true              # 预算恢复后可自动解除

  reroute_strategy:
    description: "当前策略消耗过高时切换执行路径——不是换模型，而是换方法"
    trigger: "同一 task 内 model_switch 发生 2 次以上 OR per-request cost > 3× running_average"
    action: "切换到 'pipeline 模式'（拆分成多个小请求逐段处理）而非 '一次性大请求'"
    visual: "终端显示 '🔄 策略切换——Pipeline 模式（将任务拆分为 {n} 段逐段处理）'"

  global_timeout_kill:
    description: "当 wall-clock 时间预算耗尽时触发——token 少但耗时长的任务在此被拦截"
    trigger: "task_timeout OR session_timeout reached"
    action: "IMMEDIATE_ABORT + 保存 Action History checkpoint + 写入 resume 文件"
    integration: "Timeout Guard（§2.20）——独立于 token/price 预算链的并行监控线程"
```
