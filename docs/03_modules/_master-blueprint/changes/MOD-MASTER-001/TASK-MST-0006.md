---
task_id: "TASK-MST-0006"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §四 全局状态传播链(CT-ORC-DB) + §五 全局容量预算"

title: "实现全局状态传播链与并发容量预算控制器"
description: |
  实现 §四 全局状态传播链（TaskCard 状态变更→所有关联系统得到通知）
  和 §五 全局容量预算（Orc.active_tasks ≤ Orc.max_concurrent_tasks + WIP Limit 强制执行）。
  核心：(1) TaskCard 状态变更 → Orc 持久化至 db.task_repo(CT-ORC-DB)；
  (2) TaskCard.status→COMPLETED → Orc→VMS(CT-ORC-VMS-001) 向量化输出；
  (3) TaskCard.status→BLOCKED → 通知 Gates 检查阻塞原因 → FLE 记录；
  (4) 全局并发任务上限 max_concurrent_tasks 强制——超限任务自动 QUEUED；
  (5) 各系统独立线程池容量预算。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\state_propagation.py"
    description: "全局状态传播链——TaskCard状态变更→关联系统通知"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\capacity_budget.py"
    description: "全局容量预算控制器——并发上限 + WIP Limit + 线程池配额"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_state_propagation.py"
    description: "状态传播链单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_capacity_budget.py"
    description: "容量预算单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\state_propagation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\capacity_budget.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_state_propagation.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_capacity_budget.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§四——全局状态传播链(CT-ORC-DB) + §五——全局容量预算定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "TaskCard 状态变更 → Orc 通过 CT-ORC-DB 持久化至 db.task_repo"
  - "TaskCard.status→COMPLETED → 自动触发 VMS 向量化(CT-ORC-VMS-001)"
  - "TaskCard.status→BLOCKED → Gates 检查阻塞原因 → FLE 记录 anomaly"
  - "capacity_budget.py 强制 max_concurrent_tasks——超限任务自动 QUEUED"
  - "各系统独立线程池 + SQLite WAL max 5 concurrent writers + ChromaDB max 3 connections"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\state_propagation.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\capacity_budget.py
  3. 删除新增的测试文件

depends_on: ["TASK-MST-0004"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
