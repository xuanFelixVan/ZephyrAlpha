---
task_id: "DB-025-0022"
namespace: "OPS"
seq: 22
title: "数据目录清单验证——§6.3 数据与备份目录存在性确认"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_directory"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
depends_on: ["DB-025-0011"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\09_audit\\state\\"
  - "D:\\ZephyrAlpha\\data\\backups\\"
  - "D:\\ZephyrAlpha\\data\\warehouse\\"
acceptance_criteria:
  - "docs/09_audit/state/zalpha_metadata.db → 运行时可生成—确认路径合法"
  - "data/backups/ → 备份目录可创建/已存在"
  - "data/warehouse/ → 冷数据归档目录可创建/已存在"
rollback_instructions: "目录不可创建 → §20 R12 P2 磁盘空间"
context_assembly_manifest: []
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
effective_priority: "P2"
diff_plan_required: false
estimated_context_tokens: 3000
context_window_limit: 128000
---

# DB-025-0022：数据目录清单验证——§6.3

§6.3 路径: docs/09_audit/state/zalpha_metadata.db, data/backups/, data/warehouse/。确认可创建/已存在。
