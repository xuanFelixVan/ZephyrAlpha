---
task_id: "TASK-INF-0207"
source_blueprint: "MOD-INF-014"
source_section: "§7 L4 + §52 金融特化 + §56 长时域 + §25.2 盲点二 + §47 Agent冒充人"
title: "L4 Agent安全层完整实现——权限最小化+HITL审批+工具参数注入防护+金融合规+长时域防御+冒充防御"
description: |
  实现 AgentSecurityLayer: 工具调用授权检查(AgentPermission枚举)+ 工具参数注入防护(Pydantic验证)
  + HITL审批(RiskLevel三级)+ 操作审计日志 + 金融合规六类威胁门禁(FJ1-FJ6)
  + 长时期Agent攻击防御(intent一致性+工具链异常+目标漂移+安全衰减曲线)
  + Agent-to-Human冒充防御(不可伪造标识+用户验证确认层)。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\behavior_audit_logger.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l4_agent.py"
    description: "L4 AgentSecurityLayer——权限+HITL+工具注入+审计+金融合规+长时域+冒充防御"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_l4_agent_security.py"
    description: "L4 Agent安全单元测试——15条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l4_agent.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_l4_agent_security.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
    reason: "§7+§52+§56+§25.2+§47完整接口"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 15000
timeout_minutes: 90
acceptance_criteria:
  - "AgentSecurityLayer 含 authorize_tool_call/validate_tool_params/request_human_approval/audit_tool_execution 4个方法"
  - "AgentPermission 枚举 READ_ONLY/WRITE_SAFE/WRITE_CRITICAL/ADMIN + RiskLevel 枚举 HIGH/MEDIUM/LOW"
  - "_TOOL_RISK_MAP 含10+工具风险评估"
  - "FinancialComplianceGate 含 FJ1-FJ6 六类威胁: insider trading/confirmation bias/market hallucination/market injection/market timing/cascading error"
  - "LongHorizonAgentDefender: intent_consistency/tool_chaining_anomaly/objective_drift/safety_decay_curve 4项"
  - "AgentImpersonationDefender: unforgeable_marker + user_verification_layer"
  - "Pydantic V2 ToolCallAuthorization/ApprovalRequest 模型"
  - "15条单元测试全部通过"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\llm_security\layers\l4_agent.py
  2. 删除 D:\ZephyrAlpha\tests\llm_security\test_l4_agent_security.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security","agent"]
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

实现 L4 Agent 安全层——Agent 工具调用全生命周期保护。权限检查、参数注入防护、HITL 审批、操作审计、金融领域特化威胁、长时期攻击防御、Agent-to-Human 冒充防御的完整能力。

## 触发条件
- TASK-INF-0201 已通过

## 执行步骤

### 读
- `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm-security\blueprint.md` §7+§52+§56+§25.2+§47
- `D:\ZephyrAlpha\src\zephyr\llm_security\behavior_audit_logger.py`

### 做
1. 实现 `AgentSecurityLayer` 核心4方法
2. 实现 `FinancialComplianceGate` ——6类金融威胁门禁
3. 实现 `LongHorizonAgentDefender` ——4项长时域检测
4. 实现 `AgentImpersonationDefender` ——不可伪造标记+用户验证
5. 编写 15 条单元测试

### 产
- `l4_agent.py` / `test_l4_agent_security.py`

### 检
```bash
pytest tests/llm_security/test_l4_agent_security.py -v
```
