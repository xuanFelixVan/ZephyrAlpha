---
task_id: "DB-025-0063"
namespace: "OPS"
seq: 63
title: "容量估算——§13.3 性能基线验证"
status: "PENDING"
priority: "P3"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_capacity"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:capacity", "ly:cross_layer"]
depends_on: ["DB-025-0065"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"]
acceptance_criteria:
  - "task_repo.get(): 目标<5ms，降级>100ms——主键查询"
  - "task_repo.create(): 目标<20ms，降级>500ms——含写事务+events写入"
  - "task_repo.transition(): 目标<50ms，降级>500ms——含门禁评估+events"
  - "ATM transaction(无文件): 目标<50ms，降级>1s——SQL-only"
  - "ATM transaction(+3文件): 目标<200ms，降级>2s——含文件fsync"
  - "OLAP趋势查询: 目标<500ms，降级>5s——聚合查询"
  - "health_check: 目标<100ms，降级>1s——完整性扫描"
  - "backup: 目标<5s，降级>30s——取决于DB大小"
  - "VACUUM: 目标<10s，降级>60s——全表重写"
rollback_instructions: "超标 → §20 R*"
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7"]
ai_autonomy_level: "supervised"
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P3"
diff_plan_required: false
estimated_context_tokens: 2000
context_window_limit: 128000
---

# DB-025-0063：容量估算——§13.3 性能基线

§13.3: 9项操作基线——get<5ms/create<20ms/transition<50ms/ATM<50ms/ATM+3f<200ms/OLAP<500ms/health<100ms/backup<5s/VACUUM<10s。
