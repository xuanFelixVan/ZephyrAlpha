---
task_id: "TASK-MST-0011"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十一 风险与后果——R1~R7 + §十二 集成冲突裁决程序"

title: "实现风险注册表(R1~R7)缓解与集成冲突裁决引擎"
description: |
  实现 §十一 风险注册表的 7 条风险(R1~R7)的缓解策略及 §十二 集成冲突裁决程序。
  风险覆盖：(R1)任务卡SQLite同步不一致、(R2)AI执行并行文件冲突、(R3)SQLite Schema演化破坏、
  (R4)契约爆炸管理、(R5)Telemetry数据丢失、(R6)Panic Mode误触发、(R7)Owner缺位时系统腐化。
  冲突裁决：(1)4种触发条件——蓝图vs代码不一致/模块蓝图vs总蓝图矛盾/跨CT-*Schema冲突/双系统声明分歧；
  (2)3级裁决优先级——Tier 0(总蓝图)>Tier 1(architecture-model)>Tier 2(模块蓝图)；
  (3)5步冲突修复流程——检测→记录Finding→按优先级裁决→修复→verify。
  每条风险含：probability/impact/RPN/缓解措施/对应盲点编号。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\truth_source_validator.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\risk_registry.py"
    description: "风险注册表——R1~R7 风险项注册 + 缓解策略 + 监控触发器"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\conflict_arbitrator.py"
    description: "冲突裁决引擎——4触发条件 + 3级优先级 + 5步修复流程"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_risk_registry.py"
    description: "风险注册表单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_conflict_arbitrator.py"
    description: "冲突裁决引擎单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\risk_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\conflict_arbitrator.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_risk_registry.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_conflict_arbitrator.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\truth_source_validator.py"

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
    reason: "§十一风险表(R1~R7) + §十二冲突裁决程序 + validate_integration_consistency.py"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "risk_registry.py 注册全部 7 条风险(R1~R7)，每条含 probability/impact/RPN/缓解措施/盲点编号"
  - "conflict_arbitrator.py 检测 4 种冲突触发条件并执行 5 步修复流程"
  - "冲突裁决严格按 Tier 0(总蓝图)>Tier 1(architecture-model)>Tier 2(模块蓝图) 优先级"
  - "每次检测到冲突→自动创建 DOC_INCONSISTENCY Finding → 不得静默修复"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\risk_registry.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\conflict_arbitrator.py
  3. 删除新增的测试文件

depends_on: ["TASK-MST-0001"]
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
