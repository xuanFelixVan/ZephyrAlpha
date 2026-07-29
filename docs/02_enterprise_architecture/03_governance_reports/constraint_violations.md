---
doc_type: audit_report
title: 架构约束违规报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 架构约束违规报告

> **文档作用 / Purpose**: 展示架构约束违规情况，包括跨层依赖、循环依赖、命名违规等，为架构治理提供修复清单。

> 本文档由 generate_constraint_violations.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) arch_constraints表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 约束总数 | 67 |
| Open（未解决） | 67 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 60 |
| hard | 7 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_exceeded | 7 |
| cross_domain_violation | 43 |
| hard_limit_exceeded | 7 |
| layer_violation | 9 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| V-CAP-D_DATA | 容量超限: D_DATA | capacity_exceeded | D_DATA |  | hard | gate | 域 D_DATA(数据接入层) production 节点 155 超过上限 150，需拆分或提升上限 (ARCH-CA... |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | gate | 域 D_GOVERNANCE(生命周期管理) production 节点 220 超过上限 150，需拆分或提升上限 (... |
| V-CAP-D_GOV_CODE_QUALITY | 容量超限: D_GOV_CODE_QUALITY | capacity_exceeded | D_GOV_CODE_QUALITY |  | hard | gate | 域 D_GOV_CODE_QUALITY(代码质量治理) production 节点 168 超过上限 150，需拆分或... |
| V-CAP-D_GOV_SCRIPTS | 容量超限: D_GOV_SCRIPTS | capacity_exceeded | D_GOV_SCRIPTS |  | hard | gate | 域 D_GOV_SCRIPTS(脚本治理) production 节点 378 超过上限 150，需拆分或提升上限 (A... |
| V-CAP-D_INFRA_RUNTIME | 容量超限: D_INFRA_RUNTIME | capacity_exceeded | D_INFRA_RUNTIME |  | hard | gate | 域 D_INFRA_RUNTIME(运行时集成) production 节点 160 超过上限 150，需拆分或提升上限... |
| V-CAP-D_SECURITY | 容量超限: D_SECURITY | capacity_exceeded | D_SECURITY |  | hard | gate | 域 D_SECURITY(对抗验证) production 节点 166 超过上限 150，需拆分或提升上限 (ARCH... |
| V-CAP-D_SHARED | 容量超限: D_SHARED | capacity_exceeded | D_SHARED |  | hard | gate | 域 D_SHARED(共享服务) production 节点 184 超过上限 150，需拆分或提升上限 (ARCH-C... |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY | error | gate | 跨域依赖未声明: D_AUTONOMY_CORE -> D_SECURITY |
| V-CROSS-D_BACKTEST-D_INFRA_RUNTIME | 跨域违规: D_BACKTEST -> D_INFRA_RUNTIME | cross_domain_violation | D_BACKTEST | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_BACKTEST -> D_INFRA_RUNTIME |
| V-CROSS-D_COMPLIANCE-D_SECURITY | 跨域违规: D_COMPLIANCE -> D_SECURITY | cross_domain_violation | D_COMPLIANCE | D_SECURITY | error | gate | 跨域依赖未声明: D_COMPLIANCE -> D_SECURITY |
| V-CROSS-D_FACTOR-D_SHARED | 跨域违规: D_FACTOR -> D_SHARED | cross_domain_violation | D_FACTOR | D_SHARED | error | gate | 跨域依赖未声明: D_FACTOR -> D_SHARED |
| V-CROSS-D_FEEDBACK_LOOP-D_SECURITY | 跨域违规: D_FEEDBACK_LOOP -> D_SECURITY | cross_domain_violation | D_FEEDBACK_LOOP | D_SECURITY | error | gate | 跨域依赖未声明: D_FEEDBACK_LOOP -> D_SECURITY |
| V-CROSS-D_GOVERNANCE-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_GOVERNANCE -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_GOVERNANCE | D_FUNDAMENTAL_SIGNAL | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_FUNDAMENTAL_SIGNAL |
| V-CROSS-D_GOVERNANCE-D_GOV_DRIFT | 跨域违规: D_GOVERNANCE -> D_GOV_DRIFT | cross_domain_violation | D_GOVERNANCE | D_GOV_DRIFT | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_GOV_DRIFT |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_A2A |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_INFRA_RECOVERY |
| V-CROSS-D_GOVERNANCE-D_RISK | 跨域违规: D_GOVERNANCE -> D_RISK | cross_domain_violation | D_GOVERNANCE | D_RISK | error | gate | 跨域依赖未声明: D_GOVERNANCE -> D_RISK |
| V-CROSS-D_GOV_AUDIT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_AUDIT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_AUDIT | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOV_AUDIT -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOV_CODE_QUALITY-D_DATA | 跨域违规: D_GOV_CODE_QUALITY -> D_DATA | cross_domain_violation | D_GOV_CODE_QUALITY | D_DATA | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_DATA |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_AUDIT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_AUDIT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_AUDIT | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_GOV_AUDIT |
| V-CROSS-D_GOV_CODE_QUALITY-D_SECURITY | 跨域违规: D_GOV_CODE_QUALITY -> D_SECURITY | cross_domain_violation | D_GOV_CODE_QUALITY | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_CODE_QUALITY -> D_SECURITY |
| V-CROSS-D_GOV_DRIFT-D_SECURITY | 跨域违规: D_GOV_DRIFT -> D_SECURITY | cross_domain_violation | D_GOV_DRIFT | D_SECURITY | error | gate | 跨域依赖未声明: D_GOV_DRIFT -> D_SECURITY |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_SCRIPTS -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_CODE_QUALITY | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_CODE_QUALITY |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_OPS_RESILIENCE | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_OPS_RESILIENCE |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_REPAIR | 跨域违规: D_GOV_SCRIPTS -> D_GOV_REPAIR | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_REPAIR | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_REPAIR |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_RULE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_RULE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_RULE | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_GOV_RULE |
| V-CROSS-D_GOV_SCRIPTS-D_ORCHESTRATOR | 跨域违规: D_GOV_SCRIPTS -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_SCRIPTS | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_GOV_SCRIPTS -> D_ORCHESTRATOR |
| V-CROSS-D_INFRASTRUCTURE-D_SHARED | 跨域违规: D_INFRASTRUCTURE -> D_SHARED | cross_domain_violation | D_INFRASTRUCTURE | D_SHARED | error | gate | 跨域依赖未声明: D_INFRASTRUCTURE -> D_SHARED |
| V-CROSS-D_INFRA_RECOVERY-D_SECURITY | 跨域违规: D_INFRA_RECOVERY -> D_SECURITY | cross_domain_violation | D_INFRA_RECOVERY | D_SECURITY | error | gate | 跨域依赖未声明: D_INFRA_RECOVERY -> D_SECURITY |
| V-CROSS-D_INFRA_RUNTIME-D_AUTONOMY_CORE | 跨域违规: D_INFRA_RUNTIME -> D_AUTONOMY_CORE | cross_domain_violation | D_INFRA_RUNTIME | D_AUTONOMY_CORE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_AUTONOMY_CORE |
| V-CROSS-D_INFRA_RUNTIME-D_DATA | 跨域违规: D_INFRA_RUNTIME -> D_DATA | cross_domain_violation | D_INFRA_RUNTIME | D_DATA | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_DATA |
| V-CROSS-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 跨域违规: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP | cross_domain_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_REPAIR | 跨域违规: D_INFRA_RUNTIME -> D_GOV_REPAIR | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_GOV_REPAIR |
| V-CROSS-D_INFRA_RUNTIME-D_INFRASTRUCTURE | 跨域违规: D_INFRA_RUNTIME -> D_INFRASTRUCTURE | cross_domain_violation | D_INFRA_RUNTIME | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INFRASTRUCTURE |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_RECOVERY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_RECOVERY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_RECOVERY | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INFRA_RECOVERY |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTEGRATION |
| V-CROSS-D_INFRA_RUNTIME-D_INTELLIGENCE | 跨域违规: D_INFRA_RUNTIME -> D_INTELLIGENCE | cross_domain_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_INTELLIGENCE |
| V-CROSS-D_INFRA_RUNTIME-D_OPS | 跨域违规: D_INFRA_RUNTIME -> D_OPS | cross_domain_violation | D_INFRA_RUNTIME | D_OPS | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_OPS |
| V-CROSS-D_INFRA_RUNTIME-D_ORCHESTRATOR | 跨域违规: D_INFRA_RUNTIME -> D_ORCHESTRATOR | cross_domain_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_ORCHESTRATOR |
| V-CROSS-D_INFRA_RUNTIME-D_SECURITY | 跨域违规: D_INFRA_RUNTIME -> D_SECURITY | cross_domain_violation | D_INFRA_RUNTIME | D_SECURITY | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_SECURITY |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 跨域依赖未声明: D_INFRA_RUNTIME -> D_TRADING |
| V-CROSS-D_INTEGRATION-D_TRADING | 跨域违规: D_INTEGRATION -> D_TRADING | cross_domain_violation | D_INTEGRATION | D_TRADING | error | gate | 跨域依赖未声明: D_INTEGRATION -> D_TRADING |
| V-CROSS-D_MKT_DATA-D_DATA | 跨域违规: D_MKT_DATA -> D_DATA | cross_domain_violation | D_MKT_DATA | D_DATA | error | gate | 跨域依赖未声明: D_MKT_DATA -> D_DATA |
| V-CROSS-D_ORCHESTRATOR-D_SECURITY | 跨域违规: D_ORCHESTRATOR -> D_SECURITY | cross_domain_violation | D_ORCHESTRATOR | D_SECURITY | error | gate | 跨域依赖未声明: D_ORCHESTRATOR -> D_SECURITY |
| V-CROSS-D_PF_ALLOC-D_SHARED | 跨域违规: D_PF_ALLOC -> D_SHARED | cross_domain_violation | D_PF_ALLOC | D_SHARED | error | gate | 跨域依赖未声明: D_PF_ALLOC -> D_SHARED |
| V-CROSS-D_RISK-D_SHARED | 跨域违规: D_RISK -> D_SHARED | cross_domain_violation | D_RISK | D_SHARED | error | gate | 跨域依赖未声明: D_RISK -> D_SHARED |
| V-CROSS-D_SHARED-D_INFRASTRUCTURE | 跨域违规: D_SHARED -> D_INFRASTRUCTURE | cross_domain_violation | D_SHARED | D_INFRASTRUCTURE | error | gate | 跨域依赖未声明: D_SHARED -> D_INFRASTRUCTURE |
| V-CROSS-D_SHARED-D_INFRA_RUNTIME | 跨域违规: D_SHARED -> D_INFRA_RUNTIME | cross_domain_violation | D_SHARED | D_INFRA_RUNTIME | error | gate | 跨域依赖未声明: D_SHARED -> D_INFRA_RUNTIME |
| V-CROSS-D_SHARED-D_ML_TRAIN | 跨域违规: D_SHARED -> D_ML_TRAIN | cross_domain_violation | D_SHARED | D_ML_TRAIN | error | gate | 跨域依赖未声明: D_SHARED -> D_ML_TRAIN |
| V-HARD150-D_DATA | 硬上限违规: D_DATA | hard_limit_exceeded | D_DATA |  | error | gate | 域 D_DATA(数据接入层) production 节点 155 超过硬上限 150 (ARCH-CAP-002 v1... |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | gate | 域 D_GOVERNANCE(生命周期管理) production 节点 220 超过硬上限 150 (ARCH-CAP... |
| V-HARD150-D_GOV_CODE_QUALITY | 硬上限违规: D_GOV_CODE_QUALITY | hard_limit_exceeded | D_GOV_CODE_QUALITY |  | error | gate | 域 D_GOV_CODE_QUALITY(代码质量治理) production 节点 168 超过硬上限 150 (AR... |
| V-HARD150-D_GOV_SCRIPTS | 硬上限违规: D_GOV_SCRIPTS | hard_limit_exceeded | D_GOV_SCRIPTS |  | error | gate | 域 D_GOV_SCRIPTS(脚本治理) production 节点 378 超过硬上限 150 (ARCH-CAP-... |
| V-HARD150-D_INFRA_RUNTIME | 硬上限违规: D_INFRA_RUNTIME | hard_limit_exceeded | D_INFRA_RUNTIME |  | error | gate | 域 D_INFRA_RUNTIME(运行时集成) production 节点 160 超过硬上限 150 (ARCH-C... |
| V-HARD150-D_SECURITY | 硬上限违规: D_SECURITY | hard_limit_exceeded | D_SECURITY |  | error | gate | 域 D_SECURITY(对抗验证) production 节点 166 超过硬上限 150 (ARCH-CAP-002... |
| V-HARD150-D_SHARED | 硬上限违规: D_SHARED | hard_limit_exceeded | D_SHARED |  | error | gate | 域 D_SHARED(共享服务) production 节点 184 超过硬上限 150 (ARCH-CAP-002 v... |
| V-LAYER-D_INFRA_RUNTIME-D_AUTONOMY_CORE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_AUTONOMY_CORE | error | gate | 层级违规: 7312192 -> 7309852 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_DATA | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_DATA | error | gate | 层级违规: 7311102 -> 7309915 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_REPAIR | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | gate | 层级违规: 7311251 -> 7310535 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | gate | 层级违规: 7312208 -> 7311932 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_OPS | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_OPS | error | gate | 层级违规: 7312192 -> 7310589 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | gate | 层级违规: 7312192 -> 7311579 (L0_infrastructure -> L1_foundation... |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | gate | 层级违规: 7312211 -> 7312204 (L0_infrastructure -> L2_domain) |
| V-LAYER-D_INTEGRATION-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_TRADING | error | gate | 层级违规: 7311418 -> 7312185 (L1_foundation -> L2_domain) |
| V-LAYER-D_SHARED-D_ML_TRAIN | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_SHARED | D_ML_TRAIN | error | gate | 层级违规: 7312133 -> 7311543 (L0_infrastructure -> L2_domain) |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| V-CAP-D_DATA | 容量超限: D_DATA | capacity_exceeded | D_DATA |  | hard | open |
| V-CAP-D_GOVERNANCE | 容量超限: D_GOVERNANCE | capacity_exceeded | D_GOVERNANCE |  | hard | open |
| V-CAP-D_GOV_CODE_QUALITY | 容量超限: D_GOV_CODE_QUALITY | capacity_exceeded | D_GOV_CODE_QUALITY |  | hard | open |
| V-CAP-D_GOV_SCRIPTS | 容量超限: D_GOV_SCRIPTS | capacity_exceeded | D_GOV_SCRIPTS |  | hard | open |
| V-CAP-D_INFRA_RUNTIME | 容量超限: D_INFRA_RUNTIME | capacity_exceeded | D_INFRA_RUNTIME |  | hard | open |
| V-CAP-D_SECURITY | 容量超限: D_SECURITY | capacity_exceeded | D_SECURITY |  | hard | open |
| V-CAP-D_SHARED | 容量超限: D_SHARED | capacity_exceeded | D_SHARED |  | hard | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
| V-CROSS-D_AUTONOMY_CORE-D_SECURITY | 跨域违规: D_AUTONOMY_CORE -> D_SECURITY | cross_domain_violation | D_AUTONOMY_CORE | D_SECURITY | error | open |
| V-CROSS-D_BACKTEST-D_INFRA_RUNTIME | 跨域违规: D_BACKTEST -> D_INFRA_RUNTIME | cross_domain_violation | D_BACKTEST | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_COMPLIANCE-D_SECURITY | 跨域违规: D_COMPLIANCE -> D_SECURITY | cross_domain_violation | D_COMPLIANCE | D_SECURITY | error | open |
| V-CROSS-D_FACTOR-D_SHARED | 跨域违规: D_FACTOR -> D_SHARED | cross_domain_violation | D_FACTOR | D_SHARED | error | open |
| V-CROSS-D_FEEDBACK_LOOP-D_SECURITY | 跨域违规: D_FEEDBACK_LOOP -> D_SECURITY | cross_domain_violation | D_FEEDBACK_LOOP | D_SECURITY | error | open |
| V-CROSS-D_GOVERNANCE-D_FUNDAMENTAL_SIGNAL | 跨域违规: D_GOVERNANCE -> D_FUNDAMENTAL_SIGNAL | cross_domain_violation | D_GOVERNANCE | D_FUNDAMENTAL_SIGNAL | error | open |
| V-CROSS-D_GOVERNANCE-D_GOV_DRIFT | 跨域违规: D_GOVERNANCE -> D_GOV_DRIFT | cross_domain_violation | D_GOVERNANCE | D_GOV_DRIFT | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_A2A | 跨域违规: D_GOVERNANCE -> D_INFRA_A2A | cross_domain_violation | D_GOVERNANCE | D_INFRA_A2A | error | open |
| V-CROSS-D_GOVERNANCE-D_INFRA_RECOVERY | 跨域违规: D_GOVERNANCE -> D_INFRA_RECOVERY | cross_domain_violation | D_GOVERNANCE | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_GOVERNANCE-D_RISK | 跨域违规: D_GOVERNANCE -> D_RISK | cross_domain_violation | D_GOVERNANCE | D_RISK | error | open |
| V-CROSS-D_GOV_AUDIT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_AUDIT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_AUDIT | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_DATA | 跨域违规: D_GOV_CODE_QUALITY -> D_DATA | cross_domain_violation | D_GOV_CODE_QUALITY | D_DATA | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_GOV_AUDIT | 跨域违规: D_GOV_CODE_QUALITY -> D_GOV_AUDIT | cross_domain_violation | D_GOV_CODE_QUALITY | D_GOV_AUDIT | error | open |
| V-CROSS-D_GOV_CODE_QUALITY-D_SECURITY | 跨域违规: D_GOV_CODE_QUALITY -> D_SECURITY | cross_domain_violation | D_GOV_CODE_QUALITY | D_SECURITY | error | open |
| V-CROSS-D_GOV_DRIFT-D_SECURITY | 跨域违规: D_GOV_DRIFT -> D_SECURITY | cross_domain_violation | D_GOV_DRIFT | D_SECURITY | error | open |
| V-CROSS-D_GOV_ENFORCEMENT-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_ENFORCEMENT -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_ENFORCEMENT | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_CODE_QUALITY | 跨域违规: D_GOV_SCRIPTS -> D_GOV_CODE_QUALITY | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_CODE_QUALITY | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_OPS_RESILIENCE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_OPS_RESILIENCE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_OPS_RESILIENCE | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_REPAIR | 跨域违规: D_GOV_SCRIPTS -> D_GOV_REPAIR | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_REPAIR | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_GOV_RULE | 跨域违规: D_GOV_SCRIPTS -> D_GOV_RULE | cross_domain_violation | D_GOV_SCRIPTS | D_GOV_RULE | error | open |
| V-CROSS-D_GOV_SCRIPTS-D_ORCHESTRATOR | 跨域违规: D_GOV_SCRIPTS -> D_ORCHESTRATOR | cross_domain_violation | D_GOV_SCRIPTS | D_ORCHESTRATOR | error | open |
| V-CROSS-D_INFRASTRUCTURE-D_SHARED | 跨域违规: D_INFRASTRUCTURE -> D_SHARED | cross_domain_violation | D_INFRASTRUCTURE | D_SHARED | error | open |
| V-CROSS-D_INFRA_RECOVERY-D_SECURITY | 跨域违规: D_INFRA_RECOVERY -> D_SECURITY | cross_domain_violation | D_INFRA_RECOVERY | D_SECURITY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_AUTONOMY_CORE | 跨域违规: D_INFRA_RUNTIME -> D_AUTONOMY_CORE | cross_domain_violation | D_INFRA_RUNTIME | D_AUTONOMY_CORE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_DATA | 跨域违规: D_INFRA_RUNTIME -> D_DATA | cross_domain_violation | D_INFRA_RUNTIME | D_DATA | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_FEEDBACK_LOOP | 跨域违规: D_INFRA_RUNTIME -> D_FEEDBACK_LOOP | cross_domain_violation | D_INFRA_RUNTIME | D_FEEDBACK_LOOP | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_GOV_REPAIR | 跨域违规: D_INFRA_RUNTIME -> D_GOV_REPAIR | cross_domain_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INFRASTRUCTURE | 跨域违规: D_INFRA_RUNTIME -> D_INFRASTRUCTURE | cross_domain_violation | D_INFRA_RUNTIME | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INFRA_RECOVERY | 跨域违规: D_INFRA_RUNTIME -> D_INFRA_RECOVERY | cross_domain_violation | D_INFRA_RUNTIME | D_INFRA_RECOVERY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INTEGRATION | 跨域违规: D_INFRA_RUNTIME -> D_INTEGRATION | cross_domain_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_INTELLIGENCE | 跨域违规: D_INFRA_RUNTIME -> D_INTELLIGENCE | cross_domain_violation | D_INFRA_RUNTIME | D_INTELLIGENCE | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_OPS | 跨域违规: D_INFRA_RUNTIME -> D_OPS | cross_domain_violation | D_INFRA_RUNTIME | D_OPS | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_ORCHESTRATOR | 跨域违规: D_INFRA_RUNTIME -> D_ORCHESTRATOR | cross_domain_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_SECURITY | 跨域违规: D_INFRA_RUNTIME -> D_SECURITY | cross_domain_violation | D_INFRA_RUNTIME | D_SECURITY | error | open |
| V-CROSS-D_INFRA_RUNTIME-D_TRADING | 跨域违规: D_INFRA_RUNTIME -> D_TRADING | cross_domain_violation | D_INFRA_RUNTIME | D_TRADING | error | open |
| V-CROSS-D_INTEGRATION-D_TRADING | 跨域违规: D_INTEGRATION -> D_TRADING | cross_domain_violation | D_INTEGRATION | D_TRADING | error | open |
| V-CROSS-D_MKT_DATA-D_DATA | 跨域违规: D_MKT_DATA -> D_DATA | cross_domain_violation | D_MKT_DATA | D_DATA | error | open |
| V-CROSS-D_ORCHESTRATOR-D_SECURITY | 跨域违规: D_ORCHESTRATOR -> D_SECURITY | cross_domain_violation | D_ORCHESTRATOR | D_SECURITY | error | open |
| V-CROSS-D_PF_ALLOC-D_SHARED | 跨域违规: D_PF_ALLOC -> D_SHARED | cross_domain_violation | D_PF_ALLOC | D_SHARED | error | open |
| V-CROSS-D_RISK-D_SHARED | 跨域违规: D_RISK -> D_SHARED | cross_domain_violation | D_RISK | D_SHARED | error | open |
| V-CROSS-D_SHARED-D_INFRASTRUCTURE | 跨域违规: D_SHARED -> D_INFRASTRUCTURE | cross_domain_violation | D_SHARED | D_INFRASTRUCTURE | error | open |
| V-CROSS-D_SHARED-D_INFRA_RUNTIME | 跨域违规: D_SHARED -> D_INFRA_RUNTIME | cross_domain_violation | D_SHARED | D_INFRA_RUNTIME | error | open |
| V-CROSS-D_SHARED-D_ML_TRAIN | 跨域违规: D_SHARED -> D_ML_TRAIN | cross_domain_violation | D_SHARED | D_ML_TRAIN | error | open |
| V-HARD150-D_DATA | 硬上限违规: D_DATA | hard_limit_exceeded | D_DATA |  | error | open |
| V-HARD150-D_GOVERNANCE | 硬上限违规: D_GOVERNANCE | hard_limit_exceeded | D_GOVERNANCE |  | error | open |
| V-HARD150-D_GOV_CODE_QUALITY | 硬上限违规: D_GOV_CODE_QUALITY | hard_limit_exceeded | D_GOV_CODE_QUALITY |  | error | open |
| V-HARD150-D_GOV_SCRIPTS | 硬上限违规: D_GOV_SCRIPTS | hard_limit_exceeded | D_GOV_SCRIPTS |  | error | open |
| V-HARD150-D_INFRA_RUNTIME | 硬上限违规: D_INFRA_RUNTIME | hard_limit_exceeded | D_INFRA_RUNTIME |  | error | open |
| V-HARD150-D_SECURITY | 硬上限违规: D_SECURITY | hard_limit_exceeded | D_SECURITY |  | error | open |
| V-HARD150-D_SHARED | 硬上限违规: D_SHARED | hard_limit_exceeded | D_SHARED |  | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_AUTONOMY_CORE | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_AUTONOMY_CORE | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_DATA | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_DATA | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_GOV_REPAIR | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_GOV_REPAIR | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_INTEGRATION | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_INTEGRATION | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_OPS | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_OPS | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_ORCHESTRATOR | 层级违规: L0_infrastructure -> L1_foundation | layer_violation | D_INFRA_RUNTIME | D_ORCHESTRATOR | error | open |
| V-LAYER-D_INFRA_RUNTIME-D_TRADING | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_INFRA_RUNTIME | D_TRADING | error | open |
| V-LAYER-D_INTEGRATION-D_TRADING | 层级违规: L1_foundation -> L2_domain | layer_violation | D_INTEGRATION | D_TRADING | error | open |
| V-LAYER-D_SHARED-D_ML_TRAIN | 层级违规: L0_infrastructure -> L2_domain | layer_violation | D_SHARED | D_ML_TRAIN | error | open |
