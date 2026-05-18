---

task_id: "TASK-INF-0220"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.15 AI 自身安全性——Prompt Injection 防护（决策 D-020-31）"

title: "实现 Prompt Injection 净化管道——trail_for_ai_context() 语义沙箱 + 指令关键词过滤"
description: |
  实现审计数据到 AI 上下文的 prompt injection 净化管道：
  1. `step_1_strip_instructions`: Unicode 转义 AI 指令关键词——ignore/disregard/override/bypass/system:/assistant:/user:
  2. `step_2_semantic_sandbox`: 条目包裹 [AUDIT_ENTRY_START]...[AUDIT_ENTRY_END]
  3. `step_3_length_limit`: 每条 entry 截断至 500 chars
  4. `forbidden_patterns`: 检测并转义
blueprint_id: DOM-GOV-001
---
 / === / ``` / system:/assistant:/user: 前缀 / <function_call> / <invoke>
  5. `audit_self_defense`: injection 检测 → ANM-015 标记 + 自动脱毒
  6. `unicode_normalization`: NFKC 归一化防止同形字绕过（Cyrillic "і" 等）
  在 query.py 的 trail_for_ai_context() 中集成——任何 AI 读取审计数据前强制净化。
  落地决策 D-020-31 + D-020-47。覆盖风险 R23。覆盖盲点 B55 + B80。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
    description: "追加 prompt_injection_sanitize() 函数 + 集成进 trail_for_ai_context()"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_prompt_injection.py"
    description: "注入攻击测试——'ignore all previous instructions' → 净化后无攻击效力"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_prompt_injection.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-AI-001"
    section: "全篇"
    reason: "AI 安全——Prompt Injection 防护"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.15——Prompt Injection 净化管道 + D-020-31 + D-020-47"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 40

acceptance_criteria:
  - "'ignore all previous instructions' → 输出 'i\\u0067nore all previous i\\u006estructions'"
  - "'system: override' → 输出 's\\u0079stem: o\\u0076erride'"
  - "每个条目包裹在 [AUDIT_ENTRY_START]...[AUDIT_ENTRY_END] 中"
  - "条目长度 > 500 chars → 截断至 500 chars + '...'"
  - "Cyrillic 'іgnore' → NFKC 归一化后转为拉丁 'ignore' → 被转义"
  - "注入检测触发 → ANM-015 anomaly 自动写入"
  - "6/6 injection 测试用例通过"

rollback_instructions: |
  1. 从 query.py 中移除 prompt_injection_sanitize() 调用
  2. 删除 test_prompt_injection.py

depends_on:
  - "TASK-INF-0211"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---