---
task_id: "TASK-INF-0223"
source_blueprint: "MOD-INF-014"
source_section: "§44 凭据轮换安全网 + §45 级联提示注入 + §46 Few-Shot/Prompt模板投毒"
title: "凭据轮换安全网+级联提示注入+少样本Prompt模板投毒——三层高级注入防御"
description: |
  §44 CredentialRotationSafetyNet: 记录旋转动作→verify旋转有效性→监测旋转后异常调用→自动fallback(流量隔离)
  §45 CascadingPromptInjection: Agent链传播检测器——AgentCallPropagationGraph + Base→Trigger→Amplify Chain Score Checks
  §46 FewShotPromptPoisoning: Few-shot样本劫持→样本接入点注入防护(EXT→EXT:INCOMING_SAMPLE/SYS→CTX:BOUNDARY/FEW的枚举验证)
  + PromptTemplateInjectionDetector(变量注入+markdown/HTML/sh/tool标签注入+嵌入反转)
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\credential_rotation_safety.py"
    description: "凭据轮换安全网"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\advanced_injection_defense.py"
    description: "级联+少样本+Prompt模板三层防御"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_advanced_injection.py"
    description: "级联+少样本+Prompt模板测试——10条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\credential_rotation_safety.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\advanced_injection_defense.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_advanced_injection.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§44+§45+§46"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "CredentialRotationSafety: rotate→verify(success?)→monitor post-rotate anomalies→fallback strategy 8项"
  - "CascadingInjectionDetector: AgentCallPropagationGraph + 2h propagation window + cascade_score 21分威胁评估"
  - "FewShotPoisoningDefender: no_hide + default_safe + poison_mode enum + sample桩→token→max(10x original) cap"
  - "PromptTemplateInjectionDetector: variable_injection/markdown_injection/html_injection/shell_injection/tool_tag_injection/template_silent_capture/embedding_inversion 7个检测器"
  - "Pydantic V2: RotationRecord/CascadingThreatReport"
  - "10条测试全部通过"
rollback_instructions: |
  1. 删除credential_rotation_safety.py + advanced_injection_defense.py + test_advanced_injection.py
depends_on: ["TASK-INF-0201","TASK-INF-0204","TASK-INF-0207"]
blocked_by: []
status: "created"
tags_fn: ["security","injection","credential"]
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

实现凭据轮换安全网和三种高级注入攻击的防护：级联提示注入、少样本Prompt模板投毒和模板间接注入。

## 执行步骤

### 做
1. 实现 CredentialRotationSafetyNet——记录→验证→监测→fallback
2. 实现 CascadingInjectionDetector——Ag传播图+3h窗口+21分评估
3. 实现 FewShotPoisoningDefender+PofTemplateInjectionDetector——7个检测器
4. 编写 10 条测试
