---
task_id: TASK-MOD-INF-010-0006
module_id: MOD-INF-010
blueprint_ref: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
blueprint_sections: ["§2 子系统 v0.16.0（第15轮：Vibe Coding Native + 认知运营）", "§5 v0.16.0 New Files (10)", "§7 R221-R230", "§6 Phase52-53"]
status: pending
priority: P0
created_date: 2026-05-06
assigned_to: null
depends_on: ["TASK-MOD-INF-010-0005"]
blocked_by: []
blocks: ["TASK-MOD-INF-010-0007"]
estimated_effort_hours: 18
actual_effort_hours: null
tags: [v0.16.0, vibe-coding, cognitive-ops, 1-person-maintenance, 10-files]
upstream_files:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\mtti_tracker.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\zombie_fle_detector.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\cognitive_load_budget.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\evolution\prompt_factory_governance.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\verifiers\cross_session_knowledge_integrity.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\actors\global_action_scheduler.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\config_complexity_budget.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\operational_seasonality.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\collectors\known_unknown_registry.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\concurrent_change_deconfliction.py
acceptance_criteria:
  - AC-0006-01: 10 个文件全部创建
  - AC-0006-02: mtti_tracker.py 实现 MTTI < 5min 追踪
  - AC-0006-03: zombie_fle_detector.py 实现脑死亡检测（Cognition Smoke Test）
  - AC-0006-04: cognitive_load_budget.py 实现 Owner 决策疲劳度预算
  - AC-0006-05: cross_session_knowledge_integrity.py 实现跨会话KB完整性验证
  - AC-0006-06: R221-R230 缓解措施落位
rollback_instructions: |
  1. 删除本次创建的 10 个文件
  2. 回滚 §10 路径索引
context_assembly_manifest:
  required_contexts:
    - context_id: CTX-BLUEPRINT-v0.16.0
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§变更记录 v0.16.0"]
      description: 十五轮——氛围编程原生+认知运营1人维护
  assembly_notes: |
    v0.16.0 首次引入"氛围编程原生"概念——MTTI追踪、ZombieFLE检测、
    认知负载预算、Prompt工厂治理、跨会话知识完整性。1人+AI维护的核心保障。
---

# TASK-MOD-INF-010-0006: v0.16.0 Vibe Coding Native + 认知运营

## 1. 任务目标
实现 v0.16.0 的 10 个氛围编程原生子系统，覆盖 R221-R230。

## 2. 文件清单
| # | 文件 | 职责 |
|---|------|------|
| 1 | diagnosers/mtti_tracker.py | MTTI追踪+误报时间成本+阈值自适应 |
| 2 | diagnosers/zombie_fle_detector.py | FLE脑死亡检测——心跳正常但认知停摆 |
| 3 | diagnosers/cognitive_load_budget.py | Owner决策疲劳度+通知节奏自适应 |
| 4 | evolution/prompt_factory_governance.py | Prompt模板工厂治理——版本审计+AB测试 |
| 5 | verifiers/cross_session_knowledge_integrity.py | 跨会话KB完整性——散列锚定+连续性审计 |
| 6 | actors/global_action_scheduler.py | 全局Action优先级调度——实时抢占+死锁检测 |
| 7 | gates/config_complexity_budget.py | 1人配置复杂度预算——items上限+交互面度量 |
| 8 | diagnosers/operational_seasonality.py | 周末/月末/季末/年末模式自动切换 |
| 9 | collectors/known_unknown_registry.py | "我知道我不知道什么"注册表 |
| 10 | gates/concurrent_change_deconfliction.py | Owner+FLE并发变更冲突消歧 |
