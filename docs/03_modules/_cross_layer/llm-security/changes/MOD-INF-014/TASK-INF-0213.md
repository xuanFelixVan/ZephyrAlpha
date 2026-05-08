---
task_id: "TASK-INF-0213"
source_blueprint: "MOD-INF-014"
source_section: "§12 fail-closed + §19 不实施LSG的后果"
title: "LSG fail-closed安全默认原则实现——全部九层默认阻断+可重写fail-open白名单"
description: |
  在 LLMSecurityProtocol 抽象基类及所有九层实现类中强制 fail-closed 原则：
  安全判断不确定时默认阻断，仅通过显式白名单允许放行。
  同时实现 §19 描述的未部署LSG七项后果的防护验证测试。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l0_supply_chain.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
    description: "LLMSecurityProtocol 添加 fail_closed DEFAULT_BLOCK 注解"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_fail_closed.py"
    description: "fail-closed 原则验证测试+不部署LSG后果防护测试"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\protocol.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_fail_closed.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l0_supply_chain.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§12+§19"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 6000
timeout_minutes: 30
acceptance_criteria:
  - "protocol.py 含 SecurityDecision Enum: BLOCK/PASS_ERROR_MAYBE_ALLOW 并标注 BLOCK 为默认值"
  - "LLMSecurityProtocol 抽象基类含 DEFAULT_BLOCK=True 类级常量"
  - "test_fail_closed.py 含4条测试: default_block/uncertain_block/whitelist_allow/七项后果反向验证"
rollback_instructions: |
  1. 回退 protocol.py 到添加 fail-closed 前的版本
  2. 删除 test_fail_closed.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "done"
tags_fn: ["security","fail-safe"]
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

在 LSG 全链路强制 fail-closed 原则——安全判定不确定时默认阻断而非放行。这是安全网关的生命线设计决策。

## 执行步骤

### 做
1. 在 protocol.py 中添加 SecurityDecision Enum + DEFAULT_BLOCK 常量
2. 验证所有九层实现遵循 fail-closed
3. 实现七项不部署后果的防护验证测试
