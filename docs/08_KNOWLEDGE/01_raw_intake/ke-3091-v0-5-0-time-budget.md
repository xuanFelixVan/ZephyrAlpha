---
module_id: KE-2990----time-budget-000
status: active
title: ── v0.5.0 新增：Time Budget 三维预算体系 ──
category: module_blueprint
---

# ── v0.5.0 新增：Time Budget 三维预算体系 ──

── v0.5.0 新增：Time Budget 三维预算体系 ──
time_budget:
  description: "Wall-clock 时间预算——token 消耗少但耗时极长的任务（死循环/慢模型/网络抖动）是三维预算必须独立追踪的原因"
  # Stanford 论文数据：相同任务在不同模型间执行时间差异可达 10x，与 token 消耗无关
  dimensions:
    request_timeout: 120           # 单次 API 调用 2 分钟超时
    turn_timeout: 300              # 单轮 ReAct 循环 5 分钟超时
    task_timeout: 3600             # 单个施工任务 1 小时超时
    session_timeout: 28800         # 单个 Session 8 小时超时
  enforcement: "Timeout Guard（§2.20）——硬超时即刻 abort + 保存 partial state + Action History checkpoint"
  visualization: "终端显示 '⏱ 任务: 23min/60min (38%) | 💰 Token: 42K/100K (42%)'"
```
