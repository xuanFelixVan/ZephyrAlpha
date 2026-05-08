---
task_id: "DB-025-0061"
namespace: "OPS"
seq: 61
title: "容量估算——§13.1 存储容量需验证"
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
depends_on: ["DB-025-0026"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"]
acceptance_criteria:
  - "单条TaskCard约10KB → 10年100万任务约10GB（不含审计）——DB文件本地磁盘"
rollback_instructions: "超标 → §20 R12"
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

# DB-025-0061：容量估算——§13.1 存储

§13.1: 单卡10KB × 100万 ≈ 10GB。本地磁盘单机。
