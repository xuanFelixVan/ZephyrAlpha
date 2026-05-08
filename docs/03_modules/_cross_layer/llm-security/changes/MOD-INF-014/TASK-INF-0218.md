---
task_id: "TASK-INF-0218"
source_blueprint: "MOD-INF-014"
source_section: "§20 OWASP Agentic Top10 + §21 OWASP Skills Top10 + §22 MITRE ATLAS v5.4 + §30 OWASP MCP + §31 MCP Sampling"
title: "OWASP Agentic/Skills/MCP Top 10 2026 + MITRE ATLAS v5.4 四大框架覆盖实现与审计器"
description: |
  实现四大安全框架的覆盖矩阵验证器：
  §20 OWASP Agentic Applications Top 10 2026 (AV01-AV10 → LSG 防御层)
  §21 OWASP Agentic Skills Top 10 2026 (SK01-SK10 → LSG)
  §22 MITRE ATLAS v5.4 (22战术/100+技术与子技术 → LSG+Agent+Tactic Matrix)
  §30 OWASP MCP Top 10 2026 (MP01-MP10) + §31 MCP Sampling Attack Vector Defense
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\framework_coverage.py"
    description: "四大安全框架覆盖审计器——Agentic+Skills+MCP+ATLAS"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_framework_coverage.py"
    description: "四大框架覆盖验证测试——40+条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\framework_coverage.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_framework_coverage.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§20+§21+§22+§30+§31"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "AgenticCoverageAuditor 含 ASI01-ASI10 十类风险→LSG防御层映射 (8类有覆盖/2类N/A)"
  - "AIVSS Agentic AI Vulnerability Scoring System: AARS = severity_base_score × execution_autonomy × threat_multiplier + 评级 Critical/High/Medium/Low/Info"
  - "SkillsCoverageAuditor 含 SK01-SK10 十类技能风险→LSG+Agent防御层映射"
  - "ATLASCoverageAuditor 含 22战术覆盖率矩阵+ATLAS_RISK_TO_LSG dict (AA01-AA10)"
  - "2x2 Tactic Matrix 含 skill_destroy/skill_deceive/skill_degrade/skill_disrupt"
  - "MCPCoverageAuditor 含 MP01-MP10 L0/L2/L4七层防御主责任+测试联动"
  - "MCPSamplingDefender 含 MCP Sampling API 缓存投毒防御"
  - "Pydantic V2 framework models"
  - "40+条测试全部通过"
rollback_instructions: |
  1. 删除 framework_coverage.py
  2. 删除 test_framework_coverage.py
depends_on: ["TASK-INF-0201","TASK-INF-0202"]
blocked_by: []
status: "created"
tags_fn: ["security","owasp","mitre"]
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

实现四大安全框架的 LSG 覆盖审计器。确保每类框架风险有对应的 LSG 防御层覆盖策略。

## 执行步骤

### 做
1. 实现 AgenticCoverageAuditor（ASI01-ASI10）+ AIVSS AARS 评分引擎
2. 实现 SkillsCoverageAuditor（SK01-SK10）
3. 实现 ATLASCoverageAuditor（22战术+2x2矩阵）
4. 实现 MCPCoverageAuditor（MP01-MP10）+ MCPSamplingDefender
