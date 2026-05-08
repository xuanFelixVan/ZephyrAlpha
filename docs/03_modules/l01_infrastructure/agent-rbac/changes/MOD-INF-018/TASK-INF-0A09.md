---
task_id: "TASK-INF-0A09"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.8 L5 — Output Guard 输出护栏 + §2.28 权限决策自解释 + D-018-10/D-018-26"

title: "实现L5 OutputGuard — 输出护栏(PII脱敏/凭证检测/截断) + DecisionExplainer"
description: |
  实现output_guard.py和decision_explainer.py。
  OutputGuard：PII脱敏(含中文身份证18位/手机号11位/统一社会信用代码18位)、凭证检测(token/key/secret模式)、输出截断(>1MB自动截断+警告)。
  中文PII模式(身份证/手机/信用代码——B107)。
  Synthesis Leakage Detection——跨读链的合成输出检测。
  DecisionExplainer：结构化拒绝原因+规则溯源+自校正建议+因果链——D-018-26。
priority: "P3"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\output_guard.py"
    description: "OutputGuard——PII_detection/credential_detection/size_truncation/synthesis_leakage_detection"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\decision_explainer.py"
    description: "DecisionExplainer——结构化拒绝原因/规则溯源/自校正建议/因果链"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_output_guard.py"
    description: "测试——中文PII/凭证检测/截断/合成泄漏检测"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_decision_explainer.py"
    description: "测试——拒绝原因结构/溯源/自校正建议"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\output_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\decision_explainer.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_output_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_decision_explainer.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.8 L5 Output Guard+中文PII模式+凭证检测+截断+synthesis leakage+§2.28 D-018-26自解释"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "中文身份证110101199001011234模式被检测并脱敏"
  - "中文手机号1[3-9]\\d{9}模式被检测并脱敏"
  - "AWS/Azure/GCP/OpenAI API key模式被检测→输出中mask"
  - "输出>1MB自动截断+发出[SIZE_TRUNCATED]警告"
  - "Synthesis Leakage:3个不同源读取→输出含组合敏感信息→标记AUTO_GUARD"
  - "DecisionExplainer.structured_rejection()返回(blocked_layer, rule_id, correction_suggestion, causal_chain)"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\output_guard.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\decision_explainer.py
  3. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_output_guard.py
  4. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_decision_explainer.py

depends_on:
  - "TASK-INF-0A02"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-018"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
