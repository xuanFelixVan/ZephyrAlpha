---
task_id: "TASK-INF-0217"
source_blueprint: "MOD-INF-014"
source_section: "§18 已知风险与缓解措施 (R1-R8)"
title: "LSG八大已知风险缓解实现——逐条R1-R8防御代码+验证测试+文档记录"
description: |
  为已知风险 R1-R8 逐条实现缓解措施：
  R1: L1误拦截→高置信白名单+误拦截报告仪表板
  R2: LSG自身性能瓶颈→各层性能预算P50/P99监控/L5内L6指标→§40 PC SF-①②
  R3: 安全策略被逆向→StrategyObfuscationStrategyDep；LSG内部指标→敏感信息脱敏策略
  R4: 第三方供应链->L3 静态session-bound CodeEmitter替代动态subprocess
  R5: 异常检测阈值漂移→自适应阈值调整+人工审核通道
  R6: 多Agent信任崩溃→L8 AgentTrustStateTimeout(1h) + AgentTrustRepairProtocol
  R7: Gemini Provider特殊合规→ProviderAdapter特殊审计
  R8: LSG自身成为攻击面→self_protection/attack_surface_reduction.py防御措施
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\layers\\l0_supply_chain.py"
downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\risk_mitigator.py"
    description: "R1-R8 八条风险缓解集中实现"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_risk_mitigation.py"
    description: "R1-R8 缓解措施验证测试——8条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\risk_mitigation.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_risk_mitigation.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§18 R1-R8 完整风险清单"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 10000
timeout_minutes: 60
acceptance_criteria:
  - "risk_mitigation.py 含 R1Mitigation-R8Mitigation 八个类各含 mitigations_checklist dict"
  - "R1: L1FalsePositiveManager (high_confidence_whitelist + 误拦截仪表板指标)"
  - "R2: PerimeterCrossCostGuard (P50_P99 BUDGET + L5→L6指标转发)"
  - "R3: StrategyObfuscationGuard (策略衰退检测+内部指标脱敏)"
  - "R4: ThirdPartyDependencyGuard (static CodeEmitter替代subprocess)"
  - "R5: AdaptiveThresholdManager (自适应阈值+EMA decay+alpha调整)"
  - "R6: TrustRepairProtocol (agent_trust_state: 可信/隔离/待修复/重新授权 + 1h超时)"
  - "R7: GeminiComplianceAdapter (Perform basic compliance reachability check only)"
  - "R8: AttackSurfaceReducer (input surface reduction + minimal visibility)"
  - "8条测试全部通过"
rollback_instructions: |
  1. 删除 risk_mitigation.py
  2. 删除 test_risk_mitigation.py
depends_on: ["TASK-INF-0201","TASK-INF-0203","TASK-INF-0204"]
blocked_by: []
status: "done"
tags_fn: ["security","risk"]
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

将蓝图 §18 的八条已知风险逐一转化为缓解代码实现，确保 LSG 在遇到对应场景时有经过测试的防御路径。

## 执行步骤

### 做
1. 实现 R1Mitigation-R8Mitigation 八个类
2. 每条含 mitigations_checklist dict: enabled/schedule/responsible
3. 编写 8 条验证测试
