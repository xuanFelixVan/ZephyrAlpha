---
task_id: "TASK-INF-0104"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 12 + §12 盲点 B29, B32"

title: "Phase 12 施工——AI 质量可控：Evals框架(B29) + Session审计轨迹(B32)"
description: |
  实现 AI 输出质量评估与 Session 完整审计。
  B29：有 contract tests（代码正确性），缺 Agent 输出质量系统评估。
  需实现：结构化 eval 用例定义、评分 rubrics（Relevance/Accuracy/Completeness）、回归检测。
  B32：每次 AI session 的记录——prompts/decisions/tool_calls/costs/errors/outcomes。
  1人+AI 维护下唯一的学习来源。
  需实现：SessionAuditTrail——JSONL 格式审计日志、与 Session Log schema 对齐。
  专业对标：PydanticAI Evals / LangChain eval harness / PydanticAI Logfire audit。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\schemas\\session-log-schema.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\evals.py"
    description: "Evals 框架——EvalCase / EvalRubric / EvalResult Pydantic模型 + EvalRunner"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\session_audit.py"
    description: "SessionAuditTrail——SessionRecord 模型 + JSONL writer + audit query"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_evals.py"
    description: "单元测试——验证评分一致性、回归检测"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_session_audit.py"
    description: "单元测试——验证 JSONL 写入、audit query"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\evals.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\session_audit.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_evals.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_session_audit.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\schemas\\session-log-schema.yaml"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§10.6"
    reason: "Session Log 正文字段——context_budget_used / knowledge_extracted / construction_deviations / next_session_handover"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §12——B29/B32 盲点详情与专业对标"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\schemas\\session-log-schema.yaml"
    reason: "Session Log schema——B32 需与此 schema 对齐"

assigned_model: "claude-sonnet-4.6"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 25000
timeout_minutes: 60

acceptance_criteria:
  - "evals.py: EvalCase 模型含 input/output/expected 字段"
  - "evals.py: EvalRubric 模型含 relevance/accuracy/completeness 三维评分"
  - "evals.py: EvalRunner.run() 方法——批量执行 eval cases 并输出 EvalResult[]"
  - "session_audit.py: SessionRecord 模型含 session_id/prompts/decisions/tool_calls/costs/errors/outcomes"
  - "session_audit.py: SessionAuditTrail 类——append_record() + query() + export_jsonl()"
  - "pytest tests/unit/test_evals.py -v 全部通过"
  - "pytest tests/unit/test_session_audit.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 evals + session_audit 入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\evals.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\session_audit.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_evals.py
  4. 删除 D:\ZephyrAlpha\tests\unit\test_session_audit.py
  5. 还原 __init__.py 中对应导出
  6. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0103"]
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
