---
task_id: "TASK-INF-0210"
source_blueprint: "MOD-INF-014"
source_section: "§10 L7 + §35 LSG自回归测试 + §39 DeepSeek风险 + §53 Post-LiteLLM自安全"
title: "L7 持续验证层完整实现——单元测试+集成测试+安全回归+DeepSeek风险治理+Post-LiteLLM自安全"
description: |
  实现 ValidationLayer: 单元测试门禁(覆盖率≥80%+pytest hooks)、集成测试安全套件(10场景)、
  安全回归测试(7天/30天自动触发)、LSG代码完整性自检(SHA256哈希基线)、
  DeepSeekSpecialRiskManager(幻觉/审查/地理路由/语义输出篡改/尺度漂移五项风险治理)、
  LSG Self-Security Post-LiteLLM适配(provider isolation + provider fail-closed adapter)。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\l7_validation.py"
    description: "L7 ValidationLayer——测试门禁+安全回归+LSG自检+DeepSeek风险+Post-LiteLLM"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l7_validation.py"
    description: "L7 持续验证单元测试——10条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\l7_validation.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l7_validation.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§10+§35+§39+§53"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "ValidationLayer 含 validate_unit_tests/validate_integration_tests/trigger_security_regression 3个核心方法"
  - "单元测试门禁: pytest hook pre-commit→cov≥80%→block commit if fail"
  - "安全回归测试: 7天自动安全场景测试 + 30天全量安全审计"
  - "CodeIntegrityGuard: 关键文件SHA256基线+启动时自检"
  - "DeepSeekSpecialRiskManager: hallucination_filter + censorship_impact + geo_routing_policy(retry_once_to_US) + semantic_manipulation + temperature_drift 5项"
  - "LiteLLMProviderIsolator: get_provider_security_profile() + run_provider_security_check()"
  - "ProviderFailClosedAdapter: 按provider返回明确策略"
  - "10条单元测试全部通过"
rollback_instructions: |
  1. 删除 self_protection/l7_validation.py
  2. 删除 test_l7_validation.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security","validation"]
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

实现 L7 持续验证层——LSG 自身的安全回归测试与持续验证能力。确保安全功能不被代码变更破坏。

## 执行步骤

### 做
1. 实现 ValidationLayer 核心3方法
2. 实现 CodeIntegrityGuard 代码自检
3. 实现 DeepSeekSpecialRiskManager 五项风险治理
4. 实现 LiteLLMProviderIsolator + ProviderFailClosedAdapter
5. 编写 10 条单元测试
