---
task_id: "DB-025-0010"
namespace: "OPS"
seq: 10
title: "不包含职责边界验证——§2.2 八项排除项落地任务卡"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "排除项验证——逐项确认 MOD-INF-012 无权管辖的范围"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_exclusions"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0009"]
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
waiting_for: null
ready_at: null
completed_at: null
created_at: "2026-05-06T23:36:00Z"
updated_at: "2026-05-06T23:36:00Z"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
downstream_outputs: []
acceptance_criteria:
  - "排除1：任务调度/分派——由 MOD-INF-006 + MOD-INF-009——db/*.py 中无 scheduler/dispatcher 代码"
  - "排除2：门禁规则定义——由 MOD-INF-007——db/*.py 中无 GateRule 定义代码"
  - "排除3：FLE 时序指标——由 MOD-INF-010——db/*.py 只产出数据不定义指标语义"
  - "排除4：向量化检索——由 MOD-INF-011（ChromaDB）——与 SQLite 互补"
  - "排除5：上下文构建注入——由 MOD-INF-008——db/*.py 无 prompt 构建代码"
  - "排除6：审计事件语义——由 MOD-INF-020——db/*.py 是 events 生产方，audit-trail 是消费方"
  - "排除7：Dashboard 渲染——由 MOD-INF-015——db/*.py 只产出指标数据"
  - "排除8：LLM Prompt/响应——由 MOD-INF-014——db/*.py 管理元数据而非 LLM"
rollback_instructions: "若发现越界职责 → 登记到 §20 风险矩阵——边界渗透。不删除代码"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§2.2——8 项不包含职责"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7"]
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
retry_count: 0
max_retries: 3
retry_backoff_seconds: 60
checkpoint_path: null
estimated_context_tokens: 3000
context_window_limit: 128000
effective_priority: "P2"
diff_plan_required: false
circuit_breaker_open: false
suspend_context_json: null
prompt_version: null
prompt_variant: null
compensation_steps: []
sla_deadline: null
sla_escalation_policy: null
original_priority: null
model_snapshot_pinned: null
thinking_state_json: null
emergency_mode: false
cross_task_learning: false
dependency_fingerprint: null
cancelled_artifacts: []
consumer_impact_report: null
run_consumer_tests: false
replan_proposed: false
modified_files_actual: null
lines_changed_actual: null
context_cache_key: null
---

# DB-025-0010：不包含职责边界验证——§2.2 八项排除项

## 任务来源

蓝图 §2.2 明确 8 项能力不在 MOD-INF-012 职责范围内，由其他模块负责。

| # | 排除项 | 谁负责 |
|---|--------|--------|
| 1 | 任务调度与分派 | MOD-INF-006 + MOD-INF-009 |
| 2 | 门禁规则定义与评估 | MOD-INF-007 |
| 3 | FLE 时序指标定义 | MOD-INF-010 |
| 4 | 向量化检索 | MOD-INF-011 (ChromaDB) |
| 5 | 上下文构建注入 | MOD-INF-008 |
| 6 | 审计事件语义解析 | MOD-INF-020 |
| 7 | 监控 Dashboard 渲染 | MOD-INF-015 |
| 8 | LLM Prompt/响应管理 | MOD-INF-014 |

## 验收标准

- [ ] `src/zephyr/db/*.py` 文件不包含上述 8 项能力的实现
- [ ] 若有越界 → 登记到 §20 风险矩阵追加 R* 条目
- [ ] 上下游接口通过（消费方明确）

## 回滚方案

越界 → 登记 risk，不删除。通知 Owner。
