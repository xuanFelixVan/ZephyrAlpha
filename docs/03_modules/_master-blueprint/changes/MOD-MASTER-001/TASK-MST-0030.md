---
task_id: "TASK-MST-0030"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §三十五 系统移交与恢复——CT-TRANSFER-001/CT-RECOVERY-001 + §三十六 知识质量评分——CT-KE-QUALITY-001"

title: "实现系统移交恢复 + 知识质量评分契约"
description: |
  实现 §三十五 CT-TRANSFER-001/CT-RECOVERY-001 + §三十六 CT-KE-QUALITY-001。
  系统移交：(1)transfer_manifest 数据结构——current_state/progress_report/known_issues/CT-*_contract_status/ai_quality_scores/handoff_instructions；
  (2)destructive_transfer——Phase1(12系统probe)→Phase2(shutdown→backup)→Phase3(archive)→Phase4(unlockztop)。
  CT-TRANSFER-001 触发: system_recovery / port_to_new_machine / new_owner / L1 disaster。
  系统恢复：(1)Phase1——.env + config + secrets restore→presync→12 system probe→restore→health scan→sync→status OK?→Phase2；
  (2)Phase2——数据库、SQLite .db (BACKUP_DISASTER_R) + ChromaDB .zip restore + VMS index rebuild + MCP .exe rebuild→Phase3；
  (3)Phase3——db schema migration verify→DLQ drain stale→capac双检查→12 system probe→phase final→FULL OPERATIONAL；
  (4)RTO: graceful=20min(healthy→backup shards) / catastrophic=40min(backup restore+index rebuild) / force=60min。
  知识质量：(1)3维评分——accuracy_score(是否可复现→1-10)+freshness_score(数据多久前的→1-10)+utility_score(被引用多少+fulfilled预期→1-10)→aggregate anchored weight；
  (2)GATE-KB-QUALITY-1 废弃知识自动审——score<4→auto create Finding→生成改进TaskCard→CE auto_re_ref。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\system_transfer.py"
    description: "系统移交管理器——CT-TRANSFER-001——transfer_manifest读写+destructive_transfer"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\system_recovery.py"
    description: "系统恢复管理器——CT-RECOVERY-001——3Phase恢复+RTO:20/40/60min"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\knowledge_base\\knowledge_quality.py"
    description: "知识质量评分器——CT-KE-QUALITY-001——3维评分+auto_re_ref"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_system_transfer.py"
    description: "系统移交单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_knowledge_quality.py"
    description: "知识质量评分器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\system_transfer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\system_recovery.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\knowledge_base\\knowledge_quality.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_system_transfer.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_knowledge_quality.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

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
    reason: "§三十五——CT-TRANSFER-001/CT-RECOVERY-001 + §三十六——CT-KE-QUALITY-001 完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 90

acceptance_criteria:
  - "system_transfer.py 实现 transfer_manifest(current_state/progress/known_issues/contract_status/ai_scores/handoff_instructions)"
  - "destructive_transfer 4 Phase——ensure backup done→verify→archive→unlock"
  - "system_recovery.py 实现 3 Phase recovery + RTO 20/40/60"
  - "recovery precheck: env+config+secrets valid→SQLite BACKUP validation→ChromaDB 解压验证"
  - "knowledge_quality.py 实现 3 维评分(accuracy/freshness/utility)→aggregated→anchor_weight=acc*0.4+fresh*0.3+util*0.3"
  - "GATE-KB-QUALITY-1: score<4→auto Finding→生成TaskCard→CE auto_re_ref→audit score improvement"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 3 个源码文件
  2. 删除新增的测试文件
  3. 如有创建的 transfer_manifest 或 recovery snapshots → 删除

depends_on: ["TASK-MST-0017"]
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
