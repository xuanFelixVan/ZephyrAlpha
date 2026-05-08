---
task_id: "TASK-INF-0214"
source_blueprint: "MOD-INF-014"
source_section: "§13 文件组成与代码落位 + §60 产出物存放目录 + §17 需更新的内容"
title: "LSG文件组成全景落地与内容同步——代码文件+测试文件+文档+配置+Payload清单全量创建"
description: |
  按蓝图 §13 文件清单创建所有缺失文件，确保与 §60 产出物目录一致。
  同步更新 §17 所列的全部下游文档：AGENTS.md、root README.md、ADR索引、复合蓝图、OWNERS文件、模块README。
  包含 payloads/ 目录下全部 4 个 .yaml 文件的有效载荷数据落地
  （injection_payloads.yaml/tool_call_payloads.yaml/leak_probe_phrases.yaml/red_team_payloads.yaml——后者含 200+ Red Team 攻击载荷）。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\README.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\code_integrity.py"
    description: "LSG 代码完整性自检"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\isolation.py"
    description: "LSG 自身隔离策略"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\injection_payloads.yaml"
    description: "注入 Payload 数据"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\tool_call_payloads.yaml"
    description: "工具调用 Payload 数据"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\leak_probe_phrases.yaml"
    description: "泄露探测短语数据"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\red_team_payloads.yaml"
    description: "Red Team 攻击载荷库——按 OWASP LLM01-LLM10 分类的 200+ 载荷变体"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\dashboard\\app.py"
    description: "Streamlit 安全仪表板"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\README.md"
    description: "模块 README"
  - path: "D:\\ZephyrAlpha\\docs\\04_decision_records\\adr-0040.md"
    description: "ADR索引更新"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\payloads\\*"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\dashboard\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\README.md"
  - "D:\\ZephyrAlpha\\AGENTS.md"
  - "D:\\ZephyrAlpha\\README.md"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§13+§60+§17"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 8000
timeout_minutes: 45
acceptance_criteria:
  - "§13 文件清单中所有未存在的文件已创建"
  - "§17 列出的6个下游文档均同步更新"
  - "payloads/ 目录下 4 个 .yaml 文件（含 red_team_payloads.yaml 200+载荷）具备有效数据"
  - "dashboard/app.py 可启动 Streamlit（import pass）"
  - "所有路径符合 GOV-DOC-002"
rollback_instructions: |
  1. 删除本次新增的非 layers/ 核心文件
  2. 回退 AGENTS.md/README.md/ADR索引/复合蓝图的修改
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["infra","documentation"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

按蓝图文件清单全量创建缺失文件，同步更新所有下游文档。

## 执行步骤

### 做
1. 创建 self_protection/ 下 code_integrity.py + isolation.py
2. 创建 payloads/ 下 4 个 .yaml 数据文件（含 red_team_payloads.yaml）
3. 创建 dashboard/app.py Streamlit 仪表板
4. 创建模块 README.md
5. 更新 AGENTS.md + root README.md + ADR索引 + 复合蓝图 + OWNERS
