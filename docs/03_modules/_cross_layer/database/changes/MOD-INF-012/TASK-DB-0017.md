---
task_id: "DB-025-0017"
namespace: "OPS"
seq: 17
title: "task_repo JSON1 查询+upsert 语义——§4 增强功能验证"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_code_contract"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
tags: ["fn:contract", "ly:cross_layer", "st:active", "mo:manual"]
depends_on: ["DB-025-0016"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
acceptance_criteria:
  - "list_by_dependency 使用 JSON1 json_extract 查询 depends_on JSON 数组"
  - "list_by_tag 使用 JSON1 json_each 查询 tags JSON 数组"
  - "list_by_blocked_by 使用 JSON1 json_extract 查询 blocked_by JSON 数组"
  - "upsert 使用 ON CONFLICT(task_id) DO UPDATE——保留 created_at，覆盖其他字段"
  - "delete 软删除——设置 is_deleted=1 + deleted_at=NOW"
  - "所有 list_by_* 自动过滤 is_deleted=0"
rollback_instructions: "不一致 → §20 risk R04 软删除残留"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§4——JSON1 + upsert + 软删除"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py", reason: "实现"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M6", "M7"]
ai_autonomy_level: "supervised"
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P2"
diff_plan_required: false
estimated_context_tokens: 4000
context_window_limit: 128000
---

# DB-025-0017：task_repo JSON1 查询+upsert 语义验证

验证 JSON1 查询使用 SQLite JSON1 扩展（json_extract/json_each），upsert 使用 ON CONFLICT DO UPDATE 保留 created_at，软删除设置 is_deleted=1 + deleted_at。

## 验收标准

- [ ] 3 个 list_by_* JSON1 查询使用正确的 SQLite JSON1 函数
- [ ] upsert ON CONFLICT DO UPDATE 语义正确——created_at 不被覆盖
- [ ] 软删除 + is_deleted 过滤正确
