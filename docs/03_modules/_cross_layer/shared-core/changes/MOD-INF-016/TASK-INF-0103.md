---
task_id: "TASK-INF-0103"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 11 + §12 盲点 B26, B28"

title: "Phase 11 施工——AI 成本可控：成本预算熔断(B26) + 上下文预算管理(B28)"
description: |
  实现 AI 专用基础设施——成本预算与强制熔断。
  B26：LLM API 调用无硬性成本限制，Agent 异常循环可在 10 分钟内刷光配额。
  需实现：CostBudget 类（provider 定价数据、累计消费追踪、硬性熔断阈值）、
  与 metrics.py 集成（成本指标审计）。
  B28：token_utils.py 已存在但未被 __init__.py 导出。
  需实现：ContextBudget 上下文预算分配器、超预算截断策略、配额追踪器。
  专业对标：AgentBudget / PydanticAI Logfire / OpenAI tiktoken。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\token_utils.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\metrics.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cost_budget.py"
    description: "CostBudget 类——provider 定价数据 + 累计消费追踪 + 硬性熔断阈值 + 配额检查"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\context_budget.py"
    description: "ContextBudget 类——上下文配额分配 + 预算追踪 + 超预算截断策略"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_cost_budget.py"
    description: "单元测试——验证熔断阈值触发、累计消费正确性"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_context_budget.py"
    description: "单元测试——验证配额分配、超预算截断、追踪器"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\cost_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\context_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_cost_budget.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_context_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\token_utils.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\**\\*.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§7.1"
    reason: "Task 31字段定义——新模块不能绕过 schemas.py 模型体系"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——必须被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §12——B26/B28 盲点详情与专业对标"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\token_utils.py"
    reason: "token_utils.py 已实现——B28 需基于此扩展上下文预算"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\metrics.py"
    reason: "metrics.py 已实现——B26 成本预算需集成 cost metrics"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 25000
timeout_minutes: 60

acceptance_criteria:
  - "cost_budget.py: CostBudget 类含 provider_pricing dict、cumulative_cost 追踪、hard_limit 阈值"
  - "cost_budget.py: check_budget() 方法——超出 hard_limit 时抛 CostBudgetExceededError"
  - "cost_budget.py: 与 metrics.py Counter 集成——emit cost_metric per API call"
  - "context_budget.py: ContextBudget 类含 allocation/remaning/tracker"
  - "context_budget.py: truncate() 方法——超预算时按策略截断（最新优先/摘要优先）"
  - "token_utils.py 通过 __init__.py __all__ 导出"
  - "pytest tests/unit/test_cost_budget.py -v 全部通过"
  - "pytest tests/unit/test_context_budget.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 cost_budget + context_budget 入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\cost_budget.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\context_budget.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_cost_budget.py
  4. 删除 D:\ZephyrAlpha\tests\unit\test_context_budget.py
  5. 还原 __init__.py 中 cost_budget/context_budget 相关导出
  6. 还原 SHARED-QUICKREF.yml 中对应条目

depends_on: ["TASK-INF-0101"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-sonnet-4.6"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
