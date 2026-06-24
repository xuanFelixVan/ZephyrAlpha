---
doc_type: domain_architecture_diagram
title: D-AUTONOMY_PERM 自治保护架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 16_d_autonomy_perm / 自治保护 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示自治保护（D-AUTONOMY_PERM）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 自治保护（D-AUTONOMY_PERM）的模块分布。共 270 个模块 / 270 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (74 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   config/runtime/kill_switch_state.yaml  [production]            │
│   docs/03_modules/_domain_autonomy_core/agent_rbac/adversaria... │
│   docs__03_modules___domain_autonomy_core__agent_rbac__bluepr... │
│   scripts/arch_guard/fitness_functions/check_kill_switch_late... │
│   scripts/governance/meta/kill_switch_state.yaml  [production]   │
│   scripts/governance/meta/manage_kill_switch.py  [prototype]     │
│   src/zephyr/autonomy_perm/__init__.py  [prototype]              │
│   src/zephyr/autonomy_perm/_extensions/__init__.py  [scaffold... │
│   src/zephyr/autonomy_perm/api/__init__.py  [scaffold_placeho... │
│   src/zephyr/autonomy_perm/core/__init__.py  [scaffold_placeh... │
│   src/zephyr/autonomy_perm/infrastructure/__init__.py  [scaff... │
│   src/zephyr/autonomy_perm/models/__init__.py  [scaffold_plac... │
│   src/zephyr/autonomy_perm/red_blue_validator/__init__.py  [p... │
│   src/zephyr/autonomy_perm/red_blue_validator/attack_registry... │
│   src/zephyr/autonomy_perm/red_blue_validator/bypass_recorder... │
│   src/zephyr/autonomy_perm/red_blue_validator/constitution_gu... │
│   src/zephyr/autonomy_perm/red_blue_validator/convergence_che... │
│   src/zephyr/autonomy_perm/red_blue_validator/defense_runner.... │
│   ...还有 56 个模块 / 56 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (18 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   Audit-Persistence Dual-Write Coordinator  [design]             │
│   Feedback Loop Three-Layer Escalation Trigger  [design]         │
│   Vector Index Health Monitor  [design]                          │
│   Dual-Storage Rollback Coordinator  [design]                    │
│   M10 Audit Report Finding Format Generator  [design]            │
│   Cost Optimizer  [design]                                       │
│   Governance Phase Check Slimmer  [design]                       │
│   AI Comprehension Cost Dynamic Estimator  [design]              │
│   System Health Five-Star Scorer  [design]                       │
│   Core Chain E2E Health Monitor  [design]                        │
│   Risk Alert Notification Dispatcher  [design]                   │
│   密钥管理器(自治版)  [design]                                   │
│   MCP网关限流审计管理器  [design]                                │
│   Auto-Guard异步审批管理器  [design]                             │
│   TaskCard六维防漂移校验器  [design]                             │
│   非AI模块边界守卫器  [design]                                   │
│   知识快照回滚管理器  [design]                                   │
│   Token预算管理器  [design]                                      │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (178 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   AI Autonomy Boundary Not Self-Extendable AI自治边界不可被AI... │
│   AI Comprehension Cost Dynamic Estimator AI理解成本动态估算...  │
│   AI Governance Framework Compliance Assessor AI治理框架合规...  │
│   AI Risk Assessor AI风险评估器  [design]                        │
│   AI Risk Classifier AI风险分类器  [design]                      │
│   AI Risk Dependency Mapper AI风险依赖映射器  [design]           │
│   AI-Driven Saga Orchestrator AI驱动Saga编排器  [design]         │
│   APPROVE 通过  [design]                                         │
│   ARS Dual-Track Settlement ARS双轨结算模型  [design]            │
│   AWS Agentic AI Security Scoping Matrix AWS Agent AI安全范围... │
│   Agent Cannot Auto-Execute Large Order Agent不可自动执行大额... │
│   Agent Cannot Auto-Online Strategy Agent不可自动上线新策略  ... │
│   Agent Cannot Autonomously Modify Boundary Agent不可自主修改... │
│   Audit Trail 审计链  [design]                                   │
│   Audit-Persistence Dual-Write Coordinator 审计-持久化双写协...  │
│   AuditLogWrite 审计日志写入  [design]                           │
│   AuditRecord 审计记录  [design]                                 │
│   Auto Fix Engine 自动修复引擎  [design]                         │
│   ...还有 160 个模块 / 160 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 270 个模块 / 270 modules）。

### L1 基础层 / Foundation Layer (74 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | config/runtime/kill_switch_state.yaml | config/runtime/kill_switch_state.yaml | production | orphan |
| 2 | docs/03_modules/_domain_autonomy_core/agent_rbac/adversar... | docs/03_modules/_domain_autonomy_core... | production | orphan |
| 3 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprin... | docs__03_modules___domain_autonomy_co... | design | design_only |
| 4 | scripts/arch_guard/fitness_functions/check_kill_switch_la... | scripts/arch_guard/fitness_functions/... | prototype | draft |
| 5 | scripts/governance/meta/kill_switch_state.yaml | scripts/governance/meta/kill_switch_s... | production | orphan |
| 6 | scripts/governance/meta/manage_kill_switch.py | scripts/governance/meta/manage_kill_s... | prototype | draft |
| 7 | src/zephyr/autonomy_perm/__init__.py | src/zephyr/autonomy_perm/__init__.py | prototype | orphan |
| 8 | src/zephyr/autonomy_perm/_extensions/__init__.py | src/zephyr/autonomy_perm/_extensions/... | scaffold_placeholder | orphan |
| 9 | src/zephyr/autonomy_perm/api/__init__.py | src/zephyr/autonomy_perm/api/__init__.py | scaffold_placeholder | orphan |
| 10 | src/zephyr/autonomy_perm/core/__init__.py | src/zephyr/autonomy_perm/core/__init_... | scaffold_placeholder | orphan |
| 11 | src/zephyr/autonomy_perm/infrastructure/__init__.py | src/zephyr/autonomy_perm/infrastructu... | scaffold_placeholder | orphan |
| 12 | src/zephyr/autonomy_perm/models/__init__.py | src/zephyr/autonomy_perm/models/__ini... | scaffold_placeholder | orphan |
| 13 | src/zephyr/autonomy_perm/red_blue_validator/__init__.py | src/zephyr/autonomy_perm/red_blue_val... | prototype | draft |
| 14 | src/zephyr/autonomy_perm/red_blue_validator/attack_regist... | src/zephyr/autonomy_perm/red_blue_val... | prototype | draft |
| 15 | src/zephyr/autonomy_perm/red_blue_validator/bypass_record... | src/zephyr/autonomy_perm/red_blue_val... | prototype | draft |
| 16 | src/zephyr/autonomy_perm/red_blue_validator/constitution_... | src/zephyr/autonomy_perm/red_blue_val... | prototype | draft |
| 17 | src/zephyr/autonomy_perm/red_blue_validator/convergence_c... | src/zephyr/autonomy_perm/red_blue_val... | prototype | draft |
| 18 | src/zephyr/autonomy_perm/red_blue_validator/defense_runne... | src/zephyr/autonomy_perm/red_blue_val... | prototype | draft |
| 19 | src/zephyr/autonomy_perm/red_blue_validator/game_day_runn... | src/zephyr/autonomy_perm/red_blue_val... | prototype | draft |
| 20 | src/zephyr/autonomy_perm/services/__init__.py | src/zephyr/autonomy_perm/services/__i... | scaffold_placeholder | orphan |
| 21 | src/zephyr/governance/agent_signer.py | src/zephyr/governance/agent_signer.py | prototype | draft |
| 22 | src/zephyr/security/access_control/governance_bridges/__i... | src/zephyr/security/access_control/go... | prototype | production |
| 23 | src/zephyr/security/access_control/governance_bridges/a2a... | src/zephyr/security/access_control/go... | prototype | production |
| 24 | src/zephyr/security/access_control/governance_bridges/app... | src/zephyr/security/access_control/go... | prototype | production |
| 25 | src/zephyr/security/access_control/governance_bridges/boo... | src/zephyr/security/access_control/go... | production | production |
| 26 | src/zephyr/security/access_control/governance_bridges/cap... | src/zephyr/security/access_control/go... | prototype | production |
| 27 | src/zephyr/security/access_control/governance_bridges/con... | src/zephyr/security/access_control/go... | prototype | production |
| 28 | tests/agent_rbac/__init__.py | tests/agent_rbac/__init__.py | prototype | draft |
| 29 | tests/agent_rbac/conftest.py | tests/agent_rbac/conftest.py | prototype | draft |
| 30 | tests/agent_rbac/test_abac_guard_agent_rbac.py | tests/agent_rbac/test_abac_guard_agen... | prototype | draft |
| 31 | tests/agent_rbac/test_adversarial_agent_rbac.py | tests/agent_rbac/test_adversarial_age... | prototype | draft |
| 32 | tests/agent_rbac/test_blind_spot_coverage.py | tests/agent_rbac/test_blind_spot_cove... | prototype | draft |
| 33 | tests/agent_rbac/test_cross_model_consistency.py | tests/agent_rbac/test_cross_model_con... | prototype | draft |
| 34 | tests/agent_rbac/test_crosscut_d.py | tests/agent_rbac/test_crosscut_d.py | prototype | draft |
| 35 | tests/agent_rbac/test_cybersec_2026.py | tests/agent_rbac/test_cybersec_2026.py | prototype | draft |
| 36 | tests/agent_rbac/test_decision_explainer_agent_rbac.py | tests/agent_rbac/test_decision_explai... | prototype | draft |
| 37 | tests/agent_rbac/test_decisions.py | tests/agent_rbac/test_decisions.py | prototype | draft |
| 38 | tests/agent_rbac/test_derive_rbac.py | tests/agent_rbac/test_derive_rbac.py | prototype | draft |
| 39 | tests/agent_rbac/test_dry_run_agent_rbac.py | tests/agent_rbac/test_dry_run_agent_r... | prototype | draft |
| 40 | tests/agent_rbac/test_engine_degradation_agent_rbac.py | tests/agent_rbac/test_engine_degradat... | prototype | draft |
| 41 | tests/agent_rbac/test_enhanced_security.py | tests/agent_rbac/test_enhanced_securi... | prototype | draft |
| 42 | tests/agent_rbac/test_exceptions_agent_rbac.py | tests/agent_rbac/test_exceptions_agen... | prototype | draft |
| 43 | tests/agent_rbac/test_forensic_a.py | tests/agent_rbac/test_forensic_a.py | prototype | draft |
| 44 | tests/agent_rbac/test_forensic_b.py | tests/agent_rbac/test_forensic_b.py | prototype | draft |
| 45 | tests/agent_rbac/test_forensic_c.py | tests/agent_rbac/test_forensic_c.py | prototype | draft |
| 46 | tests/agent_rbac/test_guard_layers_agent_rbac.py | tests/agent_rbac/test_guard_layers_ag... | prototype | draft |
| 47 | tests/agent_rbac/test_identity.py | tests/agent_rbac/test_identity.py | prototype | draft |
| 48 | tests/agent_rbac/test_immutable_core_agent_rbac.py | tests/agent_rbac/test_immutable_core_... | prototype | draft |
| 49 | tests/agent_rbac/test_input_guard_agent_rbac.py | tests/agent_rbac/test_input_guard_age... | prototype | draft |
| 50 | tests/agent_rbac/test_integration_agent_rbac.py | tests/agent_rbac/test_integration_age... | prototype | draft |
| 51 | tests/agent_rbac/test_integrity_agent_rbac.py | tests/agent_rbac/test_integrity_agent... | prototype | draft |
| 52 | tests/agent_rbac/test_intent_binder_agent_rbac.py | tests/agent_rbac/test_intent_binder_a... | prototype | draft |
| 53 | tests/agent_rbac/test_kill_switch_agent_rbac.py | tests/agent_rbac/test_kill_switch_age... | prototype | draft |
| 54 | tests/agent_rbac/test_novel_attack.py | tests/agent_rbac/test_novel_attack.py | prototype | draft |
| 55 | tests/agent_rbac/test_observability_agent_rbac.py | tests/agent_rbac/test_observability_a... | prototype | draft |
| 56 | tests/agent_rbac/test_output_guard_agent_rbac.py | tests/agent_rbac/test_output_guard_ag... | prototype | draft |
| 57 | tests/agent_rbac/test_permission_guard.py | tests/agent_rbac/test_permission_guar... | prototype | draft |
| 58 | tests/agent_rbac/test_permissions.py | tests/agent_rbac/test_permissions.py | prototype | draft |
| 59 | tests/agent_rbac/test_post_action.py | tests/agent_rbac/test_post_action.py | prototype | draft |
| 60 | tests/agent_rbac/test_rbac_guard_agent_rbac.py | tests/agent_rbac/test_rbac_guard_agen... | prototype | draft |
| 61 | tests/agent_rbac/test_redteam_adversarial.py | tests/agent_rbac/test_redteam_adversa... | prototype | draft |
| 62 | tests/agent_rbac/test_risk_mitigation_agent_rbac.py | tests/agent_rbac/test_risk_mitigation... | prototype | draft |
| 63 | tests/agent_rbac/test_sequence_guard_agent_rbac.py | tests/agent_rbac/test_sequence_guard_... | prototype | draft |
| 64 | tests/agent_rbac/test_toctou_guard_agent_rbac.py | tests/agent_rbac/test_toctou_guard_ag... | prototype | draft |
| 65 | tests/agent_rbac/test_vibe_coding.py | tests/agent_rbac/test_vibe_coding.py | prototype | draft |
| 66 | tests/test_agent_signer.py | tests/test_agent_signer.py | prototype | draft |
| 67 | tests/test_ce_kill_switch.py | tests/test_ce_kill_switch.py | prototype | draft |
| 68 | tests/test_kill_switch_root.py | tests/test_kill_switch_root.py | prototype | draft |
| 69 | tests/test_kill_switch_sim.py | tests/test_kill_switch_sim.py | prototype | draft |
| 70 | tests/test_skill_kill_switch.py | tests/test_skill_kill_switch.py | prototype | draft |
| 71 | tests/test_trading_kill_switch.py | tests/test_trading_kill_switch.py | prototype | draft |
| 72 | tests/unit/agent_rbac/__init__.py | tests/unit/agent_rbac/__init__.py | prototype | draft |
| 73 | tests/unit/agent_rbac/conftest.py | tests/unit/agent_rbac/conftest.py | prototype | draft |
| 74 | tests/unit/agent_rbac/test_rbac_core.py | tests/unit/agent_rbac/test_rbac_core.py | prototype | draft |

### L2 领域层 / Domain Layer (18 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 自治保护域-双写协调/D-AUTONOMY-166 | Audit-Persistence Dual-Write Coordinator | design | design_only |
| 2 | 自治保护域-反馈升级/D-AUTONOMY-184 | Feedback Loop Three-Layer Escalation ... | design | design_only |
| 3 | 自治保护域-向量索引/D-AUTONOMY-74 | Vector Index Health Monitor | design | design_only |
| 4 | 自治保护域-回滚协调/D-AUTONOMY-106 | Dual-Storage Rollback Coordinator | design | design_only |
| 5 | 自治保护域-审计报告/D-AUTONOMY-203 | M10 Audit Report Finding Format Gener... | design | design_only |
| 6 | 自治保护域-成本/D-AUTONOMY-16 | Cost Optimizer | design | design_only |
| 7 | 自治保护域-治理精简/D-AUTONOMY-128 | Governance Phase Check Slimmer | design | design_only |
| 8 | 自治保护域-理解成本/D-AUTONOMY-145 | AI Comprehension Cost Dynamic Estimator | design | design_only |
| 9 | 自治保护域-系统评分/D-AUTONOMY-151 | System Health Five-Star Scorer | design | design_only |
| 10 | 自治保护域-链路监控/D-AUTONOMY-120 | Core Chain E2E Health Monitor | design | design_only |
| 11 | 自治保护域-风控通知/D-AUTONOMY-52 | Risk Alert Notification Dispatcher | design | design_only |
| 12 | 自治保护域/D-AUTONOMY-10 | 密钥管理器(自治版) | design | design_only |
| 13 | 自治保护域/D-AUTONOMY-104 | MCP网关限流审计管理器 | design | design_only |
| 14 | 自治保护域/D-AUTONOMY-108 | Auto-Guard异步审批管理器 | design | design_only |
| 15 | 自治保护域/D-AUTONOMY-161 | TaskCard六维防漂移校验器 | design | design_only |
| 16 | 自治保护域/D-AUTONOMY-33 | 非AI模块边界守卫器 | design | design_only |
| 17 | 自治保护域/D-AUTONOMY-47 | 知识快照回滚管理器 | design | design_only |
| 18 | 自治保护域/D-AUTONOMY-83 | Token预算管理器 | design | design_only |

### 未分类 / Unclassified (178 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-AUTONOMY-PERM/AI Autonomy Boundary Not Self-Extendable ... | AI Autonomy Boundary Not Self-Extenda... | design | design_only |
| 2 | D-AUTONOMY-PERM/AI Comprehension Cost Dynamic Estimator A... | AI Comprehension Cost Dynamic Estimat... | design | design_only |
| 3 | D-AUTONOMY-PERM/AI Governance Framework Compliance Assess... | AI Governance Framework Compliance As... | design | design_only |
| 4 | D-AUTONOMY-PERM/AI Risk Assessor AI风险评估器 | AI Risk Assessor AI风险评估器 | design | design_only |
| 5 | D-AUTONOMY-PERM/AI Risk Classifier AI风险分类器 | AI Risk Classifier AI风险分类器 | design | design_only |
| 6 | D-AUTONOMY-PERM/AI Risk Dependency Mapper AI风险依赖映射器 | AI Risk Dependency Mapper AI风险依赖... | design | design_only |
| 7 | D-AUTONOMY-PERM/AI-Driven Saga Orchestrator AI驱动Saga编排器 | AI-Driven Saga Orchestrator AI驱动Sag... | design | design_only |
| 8 | D-AUTONOMY-PERM/APPROVE 通过 | APPROVE 通过 | design | design_only |
| 9 | D-AUTONOMY-PERM/ARS Dual-Track Settlement ARS双轨结算模型 | ARS Dual-Track Settlement ARS双轨结算... | design | design_only |
| 10 | D-AUTONOMY-PERM/AWS Agentic AI Security Scoping Matrix AW... | AWS Agentic AI Security Scoping Matri... | design | design_only |
| 11 | D-AUTONOMY-PERM/Agent Cannot Auto-Execute Large Order Age... | Agent Cannot Auto-Execute Large Order... | design | design_only |
| 12 | D-AUTONOMY-PERM/Agent Cannot Auto-Online Strategy Agent不... | Agent Cannot Auto-Online Strategy Age... | design | design_only |
| 13 | D-AUTONOMY-PERM/Agent Cannot Autonomously Modify Boundary... | Agent Cannot Autonomously Modify Boun... | design | design_only |
| 14 | D-AUTONOMY-PERM/Audit Trail 审计链 | Audit Trail 审计链 | design | design_only |
| 15 | D-AUTONOMY-PERM/Audit-Persistence Dual-Write Coordinator ... | Audit-Persistence Dual-Write Coordina... | design | design_only |
| 16 | D-AUTONOMY-PERM/AuditLogWrite 审计日志写入 | AuditLogWrite 审计日志写入 | design | design_only |
| 17 | D-AUTONOMY-PERM/AuditRecord 审计记录 | AuditRecord 审计记录 | design | design_only |
| 18 | D-AUTONOMY-PERM/Auto Fix Engine 自动修复引擎 | Auto Fix Engine 自动修复引擎 | design | design_only |
| 19 | D-AUTONOMY-PERM/Auto-Guard Async Approval Manager Auto-Gu... | Auto-Guard Async Approval Manager Aut... | design | design_only |
| 20 | D-AUTONOMY-PERM/Autonomy Boundary Change Process 自治边界... | Autonomy Boundary Change Process 自治... | design | design_only |
| 21 | D-AUTONOMY-PERM/Autonomy Fuse 自治熔断器 | Autonomy Fuse 自治熔断器 | design | design_only |
| 22 | D-AUTONOMY-PERM/Backtest-Live Deviation Monitor 回测-实盘... | Backtest-Live Deviation Monitor 回测-... | design | design_only |
| 23 | D-AUTONOMY-PERM/BacktestRealtimeDeviation 回测-实盘偏差 | BacktestRealtimeDeviation 回测-实盘偏差 | design | design_only |
| 24 | D-AUTONOMY-PERM/BacktestRealtimeDeviationAlert 回测实盘偏... | BacktestRealtimeDeviationAlert 回测实... | design | design_only |
| 25 | D-AUTONOMY-PERM/BlockCommand 阻止指令 | BlockCommand 阻止指令 | design | design_only |
| 26 | D-AUTONOMY-PERM/Budget Enforcer On-Demand Activator Budge... | Budget Enforcer On-Demand Activator B... | design | design_only |
| 27 | D-AUTONOMY-PERM/BudgetExemption 预算豁免 | BudgetExemption 预算豁免 | design | design_only |
| 28 | D-AUTONOMY-PERM/Choreography Saga Engine 协调式Saga引擎 | Choreography Saga Engine 协调式Saga引擎 | design | design_only |
| 29 | D-AUTONOMY-PERM/Circuit Breaker State Machine 熔断器状态机 | Circuit Breaker State Machine 熔断器... | design | design_only |
| 30 | D-AUTONOMY-PERM/Cluster Behavior Risk Protection 群集行为... | Cluster Behavior Risk Protection 群集... | design | design_only |
| 31 | D-AUTONOMY-PERM/Code Health Assessor 代码健康度评估器 | Code Health Assessor 代码健康度评估器 | design | design_only |
| 32 | D-AUTONOMY-PERM/Compensation Action Manager 补偿动作管理器 | Compensation Action Manager 补偿动作... | design | design_only |
| 33 | D-AUTONOMY-PERM/Compensation Dependency Graph Analyzer 补... | Compensation Dependency Graph Analyze... | design | design_only |
| 34 | D-AUTONOMY-PERM/Core Chain E2E Health Monitor 核心链路端... | Core Chain E2E Health Monitor 核心链... | design | design_only |
| 35 | D-AUTONOMY-PERM/CoreReadOnlyState CORE只读状态 | CoreReadOnlyState CORE只读状态 | design | design_only |
| 36 | D-AUTONOMY-PERM/Cross-Saga Transaction Coordinator 跨Saga... | Cross-Saga Transaction Coordinator 跨... | design | design_only |
| 37 | D-AUTONOMY-PERM/D-AUT-PERM | D-AUT-PERM | design | design_only |
| 38 | D-AUTONOMY-PERM/D-AUTONOMY-PERM | D-AUTONOMY-PERM | design | design_only |
| 39 | D-AUTONOMY-PERM/Dependency Upgrade Sandbox Approval Gatew... | Dependency Upgrade Sandbox Approval G... | design | design_only |
| 40 | D-AUTONOMY-PERM/DependencyUpgradeApproval 依赖升级审批 | DependencyUpgradeApproval 依赖升级审批 | design | design_only |
| 41 | D-AUTONOMY-PERM/DependencyUpgradeCompleted 依赖库升级完成 | DependencyUpgradeCompleted 依赖库升级... | design | design_only |
| 42 | D-AUTONOMY-PERM/Drift Detector Statistical Drift Checker ... | Drift Detector Statistical Drift Chec... | design | design_only |
| 43 | D-AUTONOMY-PERM/Drift Guard 漂移守卫 | Drift Guard 漂移守卫 | design | design_only |
| 44 | D-AUTONOMY-PERM/DriftDetected 漂移检测 | DriftDetected 漂移检测 | design | design_only |
| 45 | D-AUTONOMY-PERM/Dual-Storage Rollback Coordinator 双存储... | Dual-Storage Rollback Coordinator 双... | design | design_only |
| 46 | D-AUTONOMY-PERM/Enhanced Confidence Cascade Mapper 增强置... | Enhanced Confidence Cascade Mapper 增... | design | design_only |
| 47 | D-AUTONOMY-PERM/Escalation Protocol 升级协议 | Escalation Protocol 升级协议 | design | design_only |
| 48 | D-AUTONOMY-PERM/FLATTEN 紧急平仓 | FLATTEN 紧急平仓 | design | design_only |
| 49 | D-AUTONOMY-PERM/Feedback Loop Three-Layer Escalation Trig... | Feedback Loop Three-Layer Escalation ... | design | design_only |
| 50 | D-AUTONOMY-PERM/Four-Level Autonomy Boundary Agent自治边... | Four-Level Autonomy Boundary Agent自... | design | design_only |
| 51 | D-AUTONOMY-PERM/Four-Level Autonomy Model 四级自治模型 | Four-Level Autonomy Model 四级自治模型 | design | design_only |
| 52 | D-AUTONOMY-PERM/Governance Dashboard 治理仪表盘 | Governance Dashboard 治理仪表盘 | design | design_only |
| 53 | D-AUTONOMY-PERM/Governance Phase Check Slimmer Governance... | Governance Phase Check Slimmer Govern... | design | design_only |
| 54 | D-AUTONOMY-PERM/Governance Policy Engine 治理策略引擎 | Governance Policy Engine 治理策略引擎 | design | design_only |
| 55 | D-AUTONOMY-PERM/HITL Confidence Upgrade HITL置信度升级 | HITL Confidence Upgrade HITL置信度升级 | design | design_only |
| 56 | D-AUTONOMY-PERM/HITL Human-in-the-Loop 人在闭环机制 | HITL Human-in-the-Loop 人在闭环机制 | design | design_only |
| 57 | D-AUTONOMY-PERM/HITL Mechanism HITL人在闭环机制 | HITL Mechanism HITL人在闭环机制 | design | design_only |
| 58 | D-AUTONOMY-PERM/Half-Open Probe 熔断器半开试探 | Half-Open Probe 熔断器半开试探 | design | design_only |
| 59 | D-AUTONOMY-PERM/Hard Block 硬阻断 | Hard Block 硬阻断 | design | design_only |
| 60 | D-AUTONOMY-PERM/Hard Reset Permission Gate Hard Reset权限... | Hard Reset Permission Gate Hard Reset... | design | design_only |
| 61 | D-AUTONOMY-PERM/Hard-Gate 硬门禁架构 | Hard-Gate 硬门禁架构 | design | design_only |
| 62 | D-AUTONOMY-PERM/Health Check Service 健康检查服务 | Health Check Service 健康检查服务 | design | design_only |
| 63 | D-AUTONOMY-PERM/HealthReport 健康报告 | HealthReport 健康报告 | design | design_only |
| 64 | D-AUTONOMY-PERM/Immutable Audit Log Writer 不可变审计日志... | Immutable Audit Log Writer 不可变审计... | design | design_only |
| 65 | D-AUTONOMY-PERM/KILLSWITCH.md AI Agent Emergency Stop Pro... | KILLSWITCH.md AI Agent Emergency Stop... | design | design_only |
| 66 | D-AUTONOMY-PERM/Kill Switch Controlled Reentry Kill Switc... | Kill Switch Controlled Reentry Kill S... | design | design_only |
| 67 | D-AUTONOMY-PERM/Kill Switch Direct Path Kill Switch直通路径 | Kill Switch Direct Path Kill Switch直... | design | design_only |
| 68 | D-AUTONOMY-PERM/Kill Switch Layered & Local Evaluated Kil... | Kill Switch Layered & Local Evaluated... | design | design_only |
| 69 | D-AUTONOMY-PERM/Kill Switch 紧急制动开关 | Kill Switch 紧急制动开关 | design | design_only |
| 70 | D-AUTONOMY-PERM/KillSwitchDirect Kill Switch直通 | KillSwitchDirect Kill Switch直通 | design | design_only |
| 71 | D-AUTONOMY-PERM/KillSwitchDirectActivated Kill Switch直通... | KillSwitchDirectActivated Kill Switch... | design | design_only |
| 72 | D-AUTONOMY-PERM/KillSwitch直通路径 KillSwitch Direct Path | KillSwitch直通路径 KillSwitch Direct ... | design | design_only |
| 73 | D-AUTONOMY-PERM/Knowledge Snapshot Rollback Manager 知识... | Knowledge Snapshot Rollback Manager ... | design | design_only |
| 74 | D-AUTONOMY-PERM/Knowledge Write Guard Protector 知识Write... | Knowledge Write Guard Protector 知识W... | design | design_only |
| 75 | D-AUTONOMY-PERM/LLM Cost Guard LLM成本守卫 | LLM Cost Guard LLM成本守卫 | design | design_only |
| 76 | D-AUTONOMY-PERM/Large Order Requires Approval 大额下单需... | Large Order Requires Approval 大额下... | design | design_only |
| 77 | D-AUTONOMY-PERM/Learning System Kill Switch 学习系统Kill ... | Learning System Kill Switch 学习系统K... | design | design_only |
| 78 | D-AUTONOMY-PERM/Level 0-3 Autonomy Levels 0-3自治级别 | Level 0-3 Autonomy Levels 0-3自治级别 | design | design_only |
| 79 | D-AUTONOMY-PERM/Local Model 本地推理模型 | Local Model 本地推理模型 | design | design_only |
| 80 | D-AUTONOMY-PERM/M10 Audit Report Finding Format Generator... | M10 Audit Report Finding Format Gener... | design | design_only |
| 81 | D-AUTONOMY-PERM/MCP Gateway Rate-Limit Audit Manager MCP... | MCP Gateway Rate-Limit Audit Manager ... | design | design_only |
| 82 | D-AUTONOMY-PERM/Model Drift Dependency Propagator 模型漂... | Model Drift Dependency Propagator 模... | design | design_only |
| 83 | D-AUTONOMY-PERM/Model Drift Detector 模型漂移检测器 | Model Drift Detector 模型漂移检测器 | design | design_only |
| 84 | D-AUTONOMY-PERM/Model Inventory Dependency Graph Builder ... | Model Inventory Dependency Graph Buil... | design | design_only |
| 85 | D-AUTONOMY-PERM/Model Monitoring Dependency Tracker 模型... | Model Monitoring Dependency Tracker ... | design | design_only |
| 86 | D-AUTONOMY-PERM/Model Override Dependency Impact Analyzer... | Model Override Dependency Impact Anal... | design | design_only |
| 87 | D-AUTONOMY-PERM/Model Override Impact Analyzer 模型覆盖影... | Model Override Impact Analyzer 模型覆... | design | design_only |
| 88 | D-AUTONOMY-PERM/Model Registry 模型注册表 | Model Registry 模型注册表 | design | design_only |
| 89 | D-AUTONOMY-PERM/Model Risk Tier Classifier 模型风险分级器 | Model Risk Tier Classifier 模型风险分... | design | design_only |
| 90 | D-AUTONOMY-PERM/Model Risk Tier Dependency Classifier 模... | Model Risk Tier Dependency Classifier... | design | design_only |
| 91 | D-AUTONOMY-PERM/Model Validation Dependency Orchestrator ... | Model Validation Dependency Orchestra... | design | design_only |
| 92 | D-AUTONOMY-PERM/Model Validation Dependency Orchestrator ... | Model Validation Dependency Orchestra... | design | design_only |
| 93 | D-AUTONOMY-PERM/NIST AI 100-5 Three-Layer Security NIST A... | NIST AI 100-5 Three-Layer Security NI... | design | design_only |
| 94 | D-AUTONOMY-PERM/NVIDIA Agentic Autonomy Levels NVIDIA Age... | NVIDIA Agentic Autonomy Levels NVIDIA... | design | design_only |
| 95 | D-AUTONOMY-PERM/Non-AI Boundary Guard 非AI边界守卫 | Non-AI Boundary Guard 非AI边界守卫 | design | design_only |
| 96 | D-AUTONOMY-PERM/Non-worsening 不恶化性 | Non-worsening 不恶化性 | design | design_only |
| 97 | D-AUTONOMY-PERM/Orchestrated Saga Engine 编排式Saga引擎 | Orchestrated Saga Engine 编排式Saga引擎 | design | design_only |
| 98 | D-AUTONOMY-PERM/PERM Budget Exempt Executor PERM预算豁免... | PERM Budget Exempt Executor PERM预算... | design | design_only |
| 99 | D-AUTONOMY-PERM/PERM Independent Health Checker PERM独立... | PERM Independent Health Checker PERM... | design | design_only |
| 100 | D-AUTONOMY-PERM/PERM-CORE Read-Only Interface Contract PE... | PERM-CORE Read-Only Interface Contrac... | design | design_only |
| 101 | D-AUTONOMY-PERM/PERMBlockCommand PERM阻止命令 | PERMBlockCommand PERM阻止命令 | design | design_only |
| 102 | D-AUTONOMY-PERM/PERMBlockExecuted PERM阻止指令执行 | PERMBlockExecuted PERM阻止指令执行 | design | design_only |
| 103 | D-AUTONOMY-PERM/PERMBudgetExemption PERM预算豁免 | PERMBudgetExemption PERM预算豁免 | design | design_only |
| 104 | D-AUTONOMY-PERM/PERMBudgetExemptionUsed PERM预算豁免被使用 | PERMBudgetExemptionUsed PERM预算豁免... | design | design_only |
| 105 | D-AUTONOMY-PERM/PERMIndependentHealthCheck PERM独立健康检查 | PERMIndependentHealthCheck PERM独立健... | design | design_only |
| 106 | D-AUTONOMY-PERM/PERM不修改CORE状态 PERM No Modify CORE State | PERM不修改CORE状态 PERM No Modify COR... | design | design_only |
| 107 | D-AUTONOMY-PERM/PERM预算豁免 PERM Budget Exemption | PERM预算豁免 PERM Budget Exemption | design | design_only |
| 108 | D-AUTONOMY-PERM/Parameter Optimizer 参数优化器 | Parameter Optimizer 参数优化器 | design | design_only |
| 109 | D-AUTONOMY-PERM/PermissionCheck 权限检查 | PermissionCheck 权限检查 | design | design_only |
| 110 | D-AUTONOMY-PERM/PermissionDenied 权限拒绝 | PermissionDenied 权限拒绝 | design | design_only |
| 111 | D-AUTONOMY-PERM/PipelineOrchestrator CostTracker Componen... | PipelineOrchestrator CostTracker Comp... | design | design_only |
| 112 | D-AUTONOMY-PERM/RBAC Permission Check Embedded Bridge RBA... | RBAC Permission Check Embedded Bridge... | design | design_only |
| 113 | D-AUTONOMY-PERM/RBACDecision RBAC决策 | RBACDecision RBAC决策 | design | design_only |
| 114 | D-AUTONOMY-PERM/REDUCE 缩量保留方向 | REDUCE 缩量保留方向 | design | design_only |
| 115 | D-AUTONOMY-PERM/REJECT 完全阻断 | REJECT 完全阻断 | design | design_only |
| 116 | D-AUTONOMY-PERM/Red-Blue Validator 红蓝对抗验证器 | Red-Blue Validator 红蓝对抗验证器 | design | design_only |
| 117 | D-AUTONOMY-PERM/Responsible AI Dependency Auditor 负责任A... | Responsible AI Dependency Auditor 负... | design | design_only |
| 118 | D-AUTONOMY-PERM/Reversibility 可撤销性 | Reversibility 可撤销性 | design | design_only |
| 119 | D-AUTONOMY-PERM/Risk Alert Notification Dispatcher 风控告... | Risk Alert Notification Dispatcher 风... | design | design_only |
| 120 | D-AUTONOMY-PERM/Risk Check RBAC Permission Controller 风... | Risk Check RBAC Permission Controller... | design | design_only |
| 121 | D-AUTONOMY-PERM/Role and Interaction Journey 角色与交互旅程 | Role and Interaction Journey 角色与交... | design | design_only |
| 122 | D-AUTONOMY-PERM/Rollback Four-Tier Strategy Selector 回滚... | Rollback Four-Tier Strategy Selector ... | design | design_only |
| 123 | D-AUTONOMY-PERM/Rollback Operation Visual Tracker 回滚操... | Rollback Operation Visual Tracker 回... | design | design_only |
| 124 | D-AUTONOMY-PERM/Rollback System 回滚系统 | Rollback System 回滚系统 | design | design_only |
| 125 | D-AUTONOMY-PERM/Saga Deadlock Detector Saga死锁检测器 | Saga Deadlock Detector Saga死锁检测器 | design | design_only |
| 126 | D-AUTONOMY-PERM/Saga Definition Saga定义器 | Saga Definition Saga定义器 | design | design_only |
| 127 | D-AUTONOMY-PERM/Saga Observability Tracer Saga可观测性追踪器 | Saga Observability Tracer Saga可观测... | design | design_only |
| 128 | D-AUTONOMY-PERM/Saga State Tracker Saga状态追踪器 | Saga State Tracker Saga状态追踪器 | design | design_only |
| 129 | D-AUTONOMY-PERM/Saga Version Compatibility Manager Saga版... | Saga Version Compatibility Manager Sa... | design | design_only |
| 130 | D-AUTONOMY-PERM/Saga/Process Manager Dependency Orchestra... | Saga/Process Manager Dependency Orche... | design | design_only |
| 131 | D-AUTONOMY-PERM/Soft Block 软阻断 | Soft Block 软阻断 | design | design_only |
| 132 | D-AUTONOMY-PERM/System Health Five-Star Scorer 系统健康度... | System Health Five-Star Scorer 系统健... | design | design_only |
| 133 | D-AUTONOMY-PERM/System Version Upgrade Path Manager 系统... | System Version Upgrade Path Manager ... | design | design_only |
| 134 | D-AUTONOMY-PERM/Szpruch Conditional Gate Szpruch条件门禁 | Szpruch Conditional Gate Szpruch条件门禁 | design | design_only |
| 135 | D-AUTONOMY-PERM/TNR Safety Specification TNR安全规范 | TNR Safety Specification TNR安全规范 | design | design_only |
| 136 | D-AUTONOMY-PERM/TaskCard Six-Dimension Anti-Drift Validat... | TaskCard Six-Dimension Anti-Drift Val... | design | design_only |
| 137 | D-AUTONOMY-PERM/Temporal GNN Dependency Drift Predictor ... | Temporal GNN Dependency Drift Predict... | design | design_only |
| 138 | D-AUTONOMY-PERM/Token Budget Coordinator Token预算协调器 | Token Budget Coordinator Token预算协调器 | design | design_only |
| 139 | D-AUTONOMY-PERM/Token Budget Manager Token预算管理器 | Token Budget Manager Token预算管理器 | design | design_only |
| 140 | D-AUTONOMY-PERM/Trading Session Aware Ops Scheduler 交易... | Trading Session Aware Ops Scheduler ... | design | design_only |
| 141 | D-AUTONOMY-PERM/TradingSessionSchedule 交易时段调度 | TradingSessionSchedule 交易时段调度 | design | design_only |
| 142 | D-AUTONOMY-PERM/TradingSessionSwitch 交易时段切换 | TradingSessionSwitch 交易时段切换 | design | design_only |
| 143 | D-AUTONOMY-PERM/Transactionality 事务性 | Transactionality 事务性 | design | design_only |
| 144 | D-AUTONOMY-PERM/Vector Index Health Monitor 向量索引健康... | Vector Index Health Monitor 向量索引... | design | design_only |
| 145 | D-AUTONOMY-PERM/Zone Crossing Boundary Validator Zone Cro... | Zone Crossing Boundary Validator Zone... | design | design_only |
| 146 | D-AUTONOMY-PERM/agent_creation_policy.py Agent创建策略 | agent_creation_policy.py Agent创建策略 | design | design_only |
| 147 | D-AUTONOMY-PERM/ai_modifiable 自治区 | ai_modifiable 自治区 | design | design_only |
| 148 | D-AUTONOMY-PERM/anomaly_detector.py 异常检测器 | anomaly_detector.py 异常检测器 | design | design_only |
| 149 | D-AUTONOMY-PERM/anti_pattern_guard.py 反模式守卫 | anti_pattern_guard.py 反模式守卫 | design | design_only |
| 150 | D-AUTONOMY-PERM/asymmetric_audit.py 非对称审计 | asymmetric_audit.py 非对称审计 | design | design_only |
| 151 | D-AUTONOMY-PERM/auto_maintenance.py 自动维护 | auto_maintenance.py 自动维护 | design | design_only |
| 152 | D-AUTONOMY-PERM/bootstrap_verifier.py 引导验证器 | bootstrap_verifier.py 引导验证器 | design | design_only |
| 153 | D-AUTONOMY-PERM/build_sanitizer.py 构建清洗器 | build_sanitizer.py 构建清洗器 | design | design_only |
| 154 | D-AUTONOMY-PERM/cache_invalidation.py 缓存失效器 | cache_invalidation.py 缓存失效器 | design | design_only |
| 155 | D-AUTONOMY-PERM/contract_verifier.py 契约验证器 | contract_verifier.py 契约验证器 | design | design_only |
| 156 | D-AUTONOMY-PERM/cross_cutting.py 横切关注点 | cross_cutting.py 横切关注点 | design | design_only |
| 157 | D-AUTONOMY-PERM/dependency_auditor.py 依赖审计器 | dependency_auditor.py 依赖审计器 | design | design_only |
| 158 | D-AUTONOMY-PERM/environment_manager.py 环境管理器 | environment_manager.py 环境管理器 | design | design_only |
| 159 | D-AUTONOMY-PERM/exceptions.py 异常定义 | exceptions.py 异常定义 | design | design_only |
| 160 | D-AUTONOMY-PERM/genesis_bootstrap.py 创世引导 | genesis_bootstrap.py 创世引导 | design | design_only |
| 161 | D-AUTONOMY-PERM/human_gated 门控区 | human_gated 门控区 | design | design_only |
| 162 | D-AUTONOMY-PERM/immutable 禁区 | immutable 禁区 | design | design_only |
| 163 | D-AUTONOMY-PERM/串谋/策略同质化 Collusion/Strategy Homoge... | 串谋/策略同质化 Collusion/Strategy Ho... | design | design_only |
| 164 | D-AUTONOMY-PERM/交易时段仅监控 Trading Session Monitor Only | 交易时段仅监控 Trading Session Monito... | design | design_only |
| 165 | D-AUTONOMY-PERM/决策一致性 Decision Consistency | 决策一致性 Decision Consistency | design | design_only |
| 166 | D-AUTONOMY-PERM/权限边界偏离 Permission Boundary Deviation | 权限边界偏离 Permission Boundary Devi... | design | design_only |
| 167 | D-AUTONOMY-PERM/涌现行为 Emergent Behavior | 涌现行为 Emergent Behavior | design | design_only |
| 168 | D-AUTONOMY-PERM/禁止AI自动升级交易时段依赖库 | 禁止AI自动升级交易时段依赖库 | design | design_only |
| 169 | D-AUTONOMY-PERM/禁止AI自动清理未归档交易日志和审计记录 | 禁止AI自动清理未归档交易日志和审计记录 | design | design_only |
| 170 | D-AUTONOMY-PERM/禁止AI自动订阅付费数据源 | 禁止AI自动订阅付费数据源 | design | design_only |
| 171 | D-AUTONOMY-PERM/禁止AI自动重启交易时段核心进程 | 禁止AI自动重启交易时段核心进程 | design | design_only |
| 172 | D-AUTONOMY-PERM/资源消耗异常 Resource Consumption Anomaly | 资源消耗异常 Resource Consumption Ano... | design | design_only |
| 173 | D-AUTONOMY-PERM/通信异常 Communication Anomaly | 通信异常 Communication Anomaly | design | design_only |
| 174 | D-AUTONOMY-PERM/隐性串谋 Implicit Collusion | 隐性串谋 Implicit Collusion | design | design_only |
| 175 | D-GOVERNANCE/Agent RBAC Approver Check Agent RBAC审批人检查 | Agent RBAC Approver Check Agent RBAC... | design | design_only |
| 176 | D-GOVERNANCE/Agent RBAC Governance Bridges Contracts Agen... | Agent RBAC Governance Bridges Contrac... | design | design_only |
| 177 | D-GOVERNANCE/Kill Switch (Governance Layer) 治理层Kill Sw... | Kill Switch (Governance Layer) 治理层... | design | design_only |
| 178 | D-GOVERNANCE/Kill Switch Layered Kill Switch分层 | Kill Switch Layered Kill Switch分层 | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 181 条 / 181 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 181 条 / 181 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 127 条 / edges                               │
│   [config_depends]: 22 条 / edges                                │
│   [contract]: 18 条 / edges                                      │
│   [event]: 9 条 / edges                                          │
│   [runtime]: 5 条 / edges                                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (127 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   D-AUTONOMY-PERM → Non-AI Boundary Guard 非A...                 │
│   Non-AI Boundary Guard 非A... → Model Registry 模型注册表       │
│   D-AUT-PERM → Compensation Dependency G...                      │
│   Model Registry 模型注册表 → Model Drift Detector 模型...       │
│   Model Drift Detector 模型... → Kill Switch 紧急制动开关        │
│   Kill Switch 紧急制动开关 → Autonomy Fuse 自治熔断器            │
│   Autonomy Fuse 自治熔断器 → Drift Guard 漂移守卫                │
│   Drift Guard 漂移守卫 → Audit Trail 审计链                      │
│   Audit Trail 审计链 → Rollback System 回滚系统                  │
│   Rollback System 回滚系统 → Escalation Protocol 升级协议        │
│   Escalation Protocol 升级协议 → Red-Blue Validator 红蓝对...    │
│   Red-Blue Validator 红蓝对... → Auto Fix Engine 自动修复引擎    │
│   Auto Fix Engine 自动修复引擎 → Local Model 本地推理模型        │
│   Local Model 本地推理模型 → Knowledge Write Guard Pro...        │
│   Local Model 本地推理模型 → KILLSWITCH.md AI Agent Em...        │
│   Knowledge Write Guard Pro... → Knowledge Snapshot Rollba...    │
│   Knowledge Snapshot Rollba... → LLM Cost Guard LLM成本守卫      │
│   LLM Cost Guard LLM成本守卫 → Token Budget Manager Toke...      │
│   Token Budget Manager Toke... → Zone Crossing Boundary Va...    │
│   Zone Crossing Boundary Va... → MCP Gateway Rate-Limit Au...    │
│   Zone Crossing Boundary Va... → PERM预算豁免 PERM Budget ...    │
│   MCP Gateway Rate-Limit Au... → Auto-Guard Async Approval...    │
│   Auto-Guard Async Approval... → Immutable Audit Log Write...    │
│   Immutable Audit Log Write... → TaskCard Six-Dimension An...    │
│   TaskCard Six-Dimension An... → Audit-Persistence Dual-Wr...    │
│   Audit-Persistence Dual-Wr... → Parameter Optimizer 参数...     │
│   Parameter Optimizer 参数... → Risk Check RBAC Permissio...     │
│   Risk Check RBAC Permissio... → Risk Alert Notification D...    │
│   Risk Alert Notification D... → Health Check Service 健康...    │
│   Health Check Service 健康... → Vector Index Health Monit...    │
│   Vector Index Health Monit... → Rollback Four-Tier Strate...    │
│   Rollback Four-Tier Strate... → Dual-Storage Rollback Coo...    │
│   Dual-Storage Rollback Coo... → Core Chain E2E Health Mon...    │
│   Core Chain E2E Health Mon... → Code Health Assessor 代码...    │
│   Code Health Assessor 代码... → Governance Phase Check Sl...    │
│   Governance Phase Check Sl... → Budget Enforcer On-Demand...    │
│   Budget Enforcer On-Demand... → AI Comprehension Cost Dyn...    │
│   AI Comprehension Cost Dyn... → PipelineOrchestrator Cost...    │
│   PipelineOrchestrator Cost... → System Health Five-Star S...    │
│   System Health Five-Star S... → AI Governance Framework C...    │
│   AI Governance Framework C... → RBAC Permission Check Emb...    │
│   RBAC Permission Check Emb... → Rollback Operation Visual...    │
│   Rollback Operation Visual... → Feedback Loop Three-Layer...    │
│   Feedback Loop Three-Layer... → Token Budget Coordinator ...    │
│   Token Budget Coordinator ... → M10 Audit Report Finding ...    │
│   M10 Audit Report Finding ... → Drift Detector Statistica...    │
│   Drift Detector Statistica... → System Version Upgrade Pa...    │
│   Drift Detector Statistica... → AWS Agentic AI Security S...    │
│   System Version Upgrade Pa... → Saga Definition Saga定义器      │
│   ...还有 78 条 / 78 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (22 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (18 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (9 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (5 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 181 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `16_d_autonomy_perm_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
