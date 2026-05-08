---
task_id: "TASK-INF-0212"
source_blueprint: "MOD-INF-014"
source_section: "§23 L8 多Agent安全"
title: "L8 多Agent安全层完整实现——跨Agent权限继承+多Agent权限泄漏防护+Agent信任链验证"
description: |
  实现 MultiAgentSecurityLayer: 跨Agent调用权限继承检查(被调用Agent≤调用者权限)、
  Agent信任等级枚举(TRUSTED/SEMI_TRUSTED/UNTRUSTED)、
  工具调用风险评估(风险传播矩阵+链路风险评估)、Agent身份验证+调用签名。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l8_multi_agent.py"
    description: "L8 MultiAgentSecurityLayer——权限继承+多Agent信息泄漏防护+信任链验证"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l8_multi_agent.py"
    description: "L8 多Agent安全单元测试——10条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l8_multi_agent.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l8_multi_agent.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§23 完整定义"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 10000
timeout_minutes: 60
acceptance_criteria:
  - "MultiAgentSecurityLayer 含 check_permission_inheritance/validate_tool_call_chain/check_information_leak/validate_agent_identity 4个方法"
  - "AgentTrustLevel 枚举 TRUSTED/SEMI_TRUSTED/UNTRUSTED"
  - "RiskPropagationMatrix: 风险等级传播规则"
  - "AgentCallChain Pydantic V2: caller_agent_id/callee_agent_id/tool_requested/caller_trust/caller_permission"
  - "10条单元测试全部通过"
rollback_instructions: |
  1. 删除 l8_multi_agent.py
  2. 删除 test_l8_multi_agent.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security","multi-agent"]
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

实现 L8 多 Agent 安全层——多 Agent 间调用的权限继承、信息泄漏防护、信任链验证。防止权限提升和信息跨 Agent 泄漏。

## 执行步骤

### 做
1. 实现 MultiAgentSecurityLayer 4个核心方法
2. 实现信任等级枚举+风险传播矩阵
3. 编写 10 条单元测试
