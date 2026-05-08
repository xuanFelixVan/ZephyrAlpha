---
task_id: "DB-025-0066"
namespace: "OPS"
seq: 66
title: "施工指引 §16.1-§16.8 全量——AI施工检查表+策略+前置+后置验证"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_construction_guide"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 1.0
tags: ["fn:construction", "ly:cross_layer"]
depends_on: ["DB-025-0018"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"]
acceptance_criteria:
  - "§16.1 AI施工检查表(6行)全部对应代码状态"
  - "§16.2施工策略：时间分配/方法/信息流/好循环启动已验证"
  - "§16.3施工前置条件：#1-#4全部满足"
  - "§16.5施工顺序：Phase scaffold→experimental→beta→stable 流程图验证"
  - "§16.6回滚策略：T-DB-001~006+011共6条回滚方案可执行"
  - "§16.7施工完成标准：10项all ✓"
  - "§16.8施工完成状态记录已填写"
rollback_instructions: "如施工未达标准→回退至前Phase重做"
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
estimated_context_tokens: 4000
context_window_limit: 128000
---

# DB-025-0066：施工指引 §16.1-§16.8 全量

§16: 检查表6行+策略+前置4项(#1-#4)+施工顺序流程图+回滚6条+完成标准10项+状态记录。
