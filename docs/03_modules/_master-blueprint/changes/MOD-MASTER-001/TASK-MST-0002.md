---
task_id: "TASK-MST-0002"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §零 AI Agent 分派与阅读指南 + §0.1 Token 预算"

title: "实现 AI Agent 冷启动分派表与三级 Token 预算管理器"
description: |
  实现 §零 定义的 AI Agent 分派系统：12 系统×各自 CT-* 契约+关联 Schema+tokens 的分派表，
  以及三级 Token 预算（L1 快速定位 500/L2 施工 1500/L3 全量 8000）。
  核心功能：(1) 新 AI session 启动时根据分配的 CT-* 自动定位需要读取的蓝图节段；
  (2) Token 预算管理器监控每次 context build 的 token 数并逐级限制；
  (3) 当 Token 预算超过 7200(90%)时触发 degraded 标记。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\dispatch_table.py"
    description: "AI Agent 分派表——12系统×CT-*契约×Schema×Token 预算映射"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\token_budget.py"
    description: "三级 Token 预算管理器——L1(500)/L2(1500)/L3(8000)分级控制"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_dispatch_table.py"
    description: "分派表单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_token_budget.py"
    description: "Token 预算管理器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\dispatch_table.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\token_budget.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_dispatch_table.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_token_budget.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

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
    reason: "§零——分派表结构 + §0.1 Token 预算三级定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "dispatch_table.py 为 12 个系统提供完整的 CT-*+Schema+tokens 分派映射"
  - "token_budget.py 实现 L1(500)/L2(1500)/L3(8000) 三级预算控制并支持运行时切换"
  - "token_budget 使用超过 7200(90%)时自动标记 degraded=true"
  - "分派表支持按 CT-* 编号查询返回需要读取的蓝图节段"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\context_engine\dispatch_table.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\context_engine\token_budget.py
  3. 删除新增的测试文件

depends_on: []
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
