---
task_id: "TASK-MST-0007"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §六 施工 Phase 规划——Phase 0~Phase D"

title: "实现施工 Phase 规划——Phase 0 管控契约优先 + Phase A→D 四级施工序列"
description: |
  实现 §六 定义的四级施工 Phase 规划的执行引擎：
  Phase 0(管控契约优先)——17 条管控契约(§14-§20)+ Phase 0 context check；
  Phase A(核心集成)——13 条核心 CT-* + 3 个共享 Schema；
  Phase B(治理补齐)——Anti-Patterns + 集成测试 + 门禁；
  Phase C(运行保障)——CDC + DLQ + 动态调参 + 健康探针 + CBAC；
  Phase D(1人+AI维护)——冷启动分派 + SLO + Bulkhead + Watchdog + Backup + 场景走查。
  核心：(1)Phase 0 context check——每次施工前先跑 phase_e_context_check.py；
  (2)Phase 间依赖关系——Phase B 依赖 Phase A 完成；
  (3)construction_progress 字段自动更新。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\phase_executor.py"
    description: "Phase 执行引擎——Phase 0→D 四级施工序列 + Phase 间依赖检查"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_phase_executor.py"
    description: "Phase 执行引擎单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\phase_executor.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_phase_executor.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

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
    reason: "§六——Phase 0~Phase D 施工序列 + construction_progress 字段定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 45

acceptance_criteria:
  - "phase_executor.py 实现 Phase 0→A→B→C→D 四级施工序列及 Phase 间依赖检查"
  - "Phase 0 context check——施工前自动运行 context 完整性检查"
  - "construction_progress 字段在 Phase 完成后自动更新"
  - "当前 Phase 未完成 → 阻止下一 Phase 的任务卡创建"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\phase_executor.py
  2. 删除新增的测试文件

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
