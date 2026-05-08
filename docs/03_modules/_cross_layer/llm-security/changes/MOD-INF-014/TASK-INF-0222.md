---
task_id: "TASK-INF-0222"
source_blueprint: "MOD-INF-014"
source_section: "§24 AI BOM + §41 数据层安全 + §42 构建产物CI安全"
title: "AI BOM供应链透明度+数据层安全策略+构建产物CI安全门禁"
description: |
  §24 AI-BOM Generator: AI物料清单生成器——模型(provider/version/quantization/enclave) + 
  工具(MCP server lists + manifests) + 插件(MCP skills + AutoGLM consumer) + 
  依赖(dependency trees+CVSS) 四维度AI-BOM → CycloneDX JSON → SBOM格式导出。
  §41 数据层安全: LSG自身数据保护策略——敏感记忆条目→标记加密+KE检索权限分离(用户/会话隔离)、
  memory提示词防泄漏策略、database→REE+物理隔离路径。
  §42 CI安全: LSG CI pipeline→沉浸式测试框架、pre-commit+PR→composer request/recv来源验证、
  独立virtual env、AI-BOM→Dependency Diff review → JSON序列化差异→Analog进化标注。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\ai_bom.py"
    description: "AI-BOM生成器——四维度→CycloneDX JSON"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\data_layer_security.py"
    description: "LSG数据层安全策略——加密+权限分离+防泄漏"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\ci_security.py"
    description: "LSG CI Pipeline安全门禁——composer验证+隔离+diff review"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_ai_bom_and_ci.py"
    description: "AI-BOM+数据层+CI安全测试——10条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\ai_bom.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\data_layer_security.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\ci_security.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_ai_bom_and_ci.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§24+§41+§42"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "AIBOMGenerator.generate(model_mapping, tools, skills, dependencies) → CycloneDX JSON"
  - "DataLayerSecurityPolicy 含 KE_ACL(strict separation by user session) + memory_prompt_leak_protect(prompt injection regex)"
  - "CIPipelineSecurity 含 composer_request_validator + diff_reviewer(JSON序列化差异+progress标注)"
  - "独立virtual env隔离策略(configurable path) + pre-commit receiver验证"
  - "Pydantic V2 AIBOMRecord/CIValidationResult"
  - "10条测试全部通过"
rollback_instructions: |
  1. 删除 ai_bom.py + data_layer_security.py + ci_security.py + test_ai_bom_and_ci.py
depends_on: ["TASK-INF-0201","TASK-INF-0203"]
blocked_by: []
status: "created"
tags_fn: ["security","supply-chain","ci"]
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

实现 AI 物料清单(AI-BOM)生成器、LSG数据层安全策略和CI Pipeline安全门禁——确保供应链和数据层的完整透明。

## 执行步骤

### 做
1. 实现 AIBOMGenerator——四维度AI-BOM→CycloneDX
2. 实现 DataLayerSecurityPolicy——KE ACL+防泄漏
3. 实现 CIPipelineSecurity——composer验证+diff review+虚拟环境隔离
4. 编写 10 条测试
