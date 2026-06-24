---
doc_type: domain_architecture_diagram
title: D-GOVERNANCE 生命周期管理架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 25_d_governance / 生命周期管理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示生命周期管理（D-GOVERNANCE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 生命周期管理（D-GOVERNANCE）的模块分布。共 3860 个模块 / 3860 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│           L1 基础层 / Foundation Layer (3312 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   §8.1  [design]                                                 │
│   architecture_model/architecture_lock.yaml  [production]        │
│   architecture_model/index.yaml  [production]                    │
│   architecture_model/layers/b_context_engine.yaml  [production]  │
│   architecture_model/layers/b_core.yaml  [production]            │
│   architecture_model/layers/b_db.yaml  [production]              │
│   architecture_model/layers/b_execution_model.yaml  [production] │
│   architecture_model/layers/b_feedback_loop.yaml  [production]   │
│   architecture_model/layers/b_gates.yaml  [production]           │
│   architecture_model/layers/b_kb.yaml  [production]              │
│   architecture_model/layers/b_llm_security.yaml  [production]    │
│   architecture_model/layers/b_mcp.yaml  [production]             │
│   architecture_model/layers/b_orchestrator.yaml  [production]    │
│   architecture_model/layers/b_pipeline.yaml  [production]        │
│   architecture_model/layers/b_shared.yaml  [production]          │
│   architecture_model/layers/schema.yaml  [production]            │
│   architecture_model/scope.yaml  [production]                    │
│   architecture_model/technology_landscape.yaml  [production]     │
│   ...还有 3294 个模块 / 3294 more modules                        │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/data_governance/__init__.py  [prototype]            │
│   src/zephyr/data_governance/_extensions/__init__.py  [scaffo... │
│   src/zephyr/data_governance/api/__init__.py  [scaffold_place... │
│   src/zephyr/data_governance/core/__init__.py  [scaffold_plac... │
│   src/zephyr/data_governance/infrastructure/__init__.py  [sca... │
│   src/zephyr/data_governance/models/__init__.py  [scaffold_pl... │
│   src/zephyr/data_governance/services/__init__.py  [scaffold_... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (541 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   45 Capability List 45项能力清单  [design]                      │
│   5 Drift Detection 5类漂移检测  [design]                        │
│   A2A Failure Escalation A2A失败升级  [design]                   │
│   A2A Gateway Policy Engine A2A检查网关策略引擎  [design]        │
│   A2A Iron Law A2A铁律  [design]                                 │
│   A2A Protocol Governance Auditor A2A协议治理审计器  [design]    │
│   A2A Protocol Governance Contracts A2A协议治理契约  [design]    │
│   A2A Protocol Phase Hold A2A协议阶段保持  [design]              │
│   ACO多路径依赖搜索器 ACOMultiPathDependencySearcher  [design]   │
│   ADR Decision Tracking ADR决策追踪  [design]                    │
│   ADR Generation ADR架构决策记录自动生成  [design]               │
│   ADR Generation ADR生成  [design]                               │
│   ADR Simulation ADR仿真  [design]                               │
│   ADR传播/多ADR交互/回溯/变更仿真等  [design]                    │
│   ADR解析/约束提取/双向关联/校验/推演等  [design]                │
│   AI Autonomy Boundary AI自治边界  [design]                      │
│   AI Autonomy Boundary Manager AI自治边界管理器  [design]        │
│   AI Code Review AI代码审查  [design]                            │
│   ...还有 523 个模块 / 523 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 3860 个模块 / 3860 modules）。

### L1 基础层 / Foundation Layer (3312 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 01-跨域交叉点 vs 29-D-GOVERNANCE/D-GOV-11 | §8.1 | design | design_only |
| 2 | architecture_model/architecture_lock.yaml | architecture_model/architecture_lock.... | production | orphan |
| 3 | architecture_model/index.yaml | architecture_model/index.yaml | production | orphan |
| 4 | architecture_model/layers/b_context_engine.yaml | architecture_model/layers/b_context_e... | production | orphan |
| 5 | architecture_model/layers/b_core.yaml | architecture_model/layers/b_core.yaml | production | orphan |
| 6 | architecture_model/layers/b_db.yaml | architecture_model/layers/b_db.yaml | production | orphan |
| 7 | architecture_model/layers/b_execution_model.yaml | architecture_model/layers/b_execution... | production | orphan |
| 8 | architecture_model/layers/b_feedback_loop.yaml | architecture_model/layers/b_feedback_... | production | orphan |
| 9 | architecture_model/layers/b_gates.yaml | architecture_model/layers/b_gates.yaml | production | orphan |
| 10 | architecture_model/layers/b_kb.yaml | architecture_model/layers/b_kb.yaml | production | orphan |
| 11 | architecture_model/layers/b_llm_security.yaml | architecture_model/layers/b_llm_secur... | production | orphan |
| 12 | architecture_model/layers/b_mcp.yaml | architecture_model/layers/b_mcp.yaml | production | orphan |
| 13 | architecture_model/layers/b_orchestrator.yaml | architecture_model/layers/b_orchestra... | production | orphan |
| 14 | architecture_model/layers/b_pipeline.yaml | architecture_model/layers/b_pipeline.... | production | orphan |
| 15 | architecture_model/layers/b_shared.yaml | architecture_model/layers/b_shared.yaml | production | orphan |
| 16 | architecture_model/layers/schema.yaml | architecture_model/layers/schema.yaml | production | orphan |
| 17 | architecture_model/scope.yaml | architecture_model/scope.yaml | production | orphan |
| 18 | architecture_model/technology_landscape.yaml | architecture_model/technology_landsca... | production | orphan |
| 19 | config/ai_capability_matrix.yaml | config/ai_capability_matrix.yaml | production | orphan |
| 20 | config/blueprint_routing.yaml | config/blueprint_routing.yaml | production | orphan |
| 21 | config/capabilities.yaml | config/capabilities.yaml | production | orphan |
| 22 | config/capacity/asset_inventory.yaml | config/capacity/asset_inventory.yaml | production | orphan |
| 23 | config/capacity/capacity_slo.yaml | config/capacity/capacity_slo.yaml | production | orphan |
| 24 | config/capacity/degradation_chain.yaml | config/capacity/degradation_chain.yaml | production | orphan |
| 25 | config/capacity/error_budget_config.yaml | config/capacity/error_budget_config.yaml | production | orphan |
| 26 | config/capacity/external_watchdog.yaml | config/capacity/external_watchdog.yaml | production | orphan |
| 27 | config/capacity/owner_offline_protocol.yaml | config/capacity/owner_offline_protoco... | production | orphan |
| 28 | config/capacity/risk_register.yaml | config/capacity/risk_register.yaml | production | orphan |
| 29 | config/capacity/tech_stack_manifest.yaml | config/capacity/tech_stack_manifest.yaml | production | orphan |
| 30 | config/capacity_params.yaml | config/capacity_params.yaml | production | orphan |
| 31 | config/flags.yaml | config/flags.yaml | production | orphan |
| 32 | config/kb_parameters.yaml | config/kb_parameters.yaml | production | orphan |
| 33 | config/metrics_schema.yaml | config/metrics_schema.yaml | production | orphan |
| 34 | config/model_pricing.yaml | config/model_pricing.yaml | production | orphan |
| 35 | config/nav_table_mapping.yaml | config/nav_table_mapping.yaml | production | orphan |
| 36 | config/rbac_roles.yaml | config/rbac_roles.yaml | production | orphan |
| 37 | config/resource_optimization.yaml | config/resource_optimization.yaml | production | orphan |
| 38 | config/risk_params.yaml | config/risk_params.yaml | production | orphan |
| 39 | config/runtime/burn_rate_acceleration.yaml | config/runtime/burn_rate_acceleration... | production | orphan |
| 40 | config/runtime/error_budget_state.yaml | config/runtime/error_budget_state.yaml | production | orphan |
| 41 | config/runtime/script_retirement_state.yaml | config/runtime/script_retirement_stat... | production | orphan |
| 42 | config/runtime/shadow_mode_state.yaml | config/runtime/shadow_mode_state.yaml | production | orphan |
| 43 | config/session_state_machine.yaml | config/session_state_machine.yaml | production | orphan |
| 44 | config/skill_cbac_mapping.yaml | config/skill_cbac_mapping.yaml | production | orphan |
| 45 | config/trigger_router.yaml | config/trigger_router.yaml | production | orphan |
| 46 | data/asset_index/archive/import_update_manifest.yaml | data/asset_index/archive/import_updat... | production | orphan |
| 47 | data/asset_index/archive/migration_scripts/_migration_sha... | data/asset_index/archive/migration_sc... | prototype | draft |
| 48 | data/asset_index/archive/migration_scripts/_verify_manife... | data/asset_index/archive/migration_sc... | prototype | draft |
| 49 | data/asset_index/archive/migration_scripts/_verify_step4.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 50 | data/asset_index/archive/migration_scripts/apply_rulings.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 51 | data/asset_index/archive/migration_scripts/check_coverage.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 52 | data/asset_index/archive/migration_scripts/comprehensive_... | data/asset_index/archive/migration_sc... | prototype | draft |
| 53 | data/asset_index/archive/migration_scripts/create_target_... | data/asset_index/archive/migration_sc... | prototype | draft |
| 54 | data/asset_index/archive/migration_scripts/cross_domain_i... | data/asset_index/archive/migration_sc... | prototype | draft |
| 55 | data/asset_index/archive/migration_scripts/domain_prefix_... | data/asset_index/archive/migration_sc... | prototype | draft |
| 56 | data/asset_index/archive/migration_scripts/execute_move.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 57 | data/asset_index/archive/migration_scripts/generate_migra... | data/asset_index/archive/migration_sc... | prototype | draft |
| 58 | data/asset_index/archive/migration_scripts/generate_path_... | data/asset_index/archive/migration_sc... | prototype | draft |
| 59 | data/asset_index/archive/migration_scripts/inject_domain_... | data/asset_index/archive/migration_sc... | prototype | draft |
| 60 | data/asset_index/archive/migration_scripts/lock_batch.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 61 | data/asset_index/archive/migration_scripts/preflight_chec... | data/asset_index/archive/migration_sc... | prototype | draft |
| 62 | data/asset_index/archive/migration_scripts/rollback_batch.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 63 | data/asset_index/archive/migration_scripts/scan_import_im... | data/asset_index/archive/migration_sc... | prototype | draft |
| 64 | data/asset_index/archive/migration_scripts/shared_import_... | data/asset_index/archive/migration_sc... | prototype | draft |
| 65 | data/asset_index/archive/migration_scripts/test_import_fi... | data/asset_index/archive/migration_sc... | prototype | draft |
| 66 | data/asset_index/archive/migration_scripts/unnest_from_mc... | data/asset_index/archive/migration_sc... | prototype | draft |
| 67 | data/asset_index/archive/migration_scripts/update_imports.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 68 | data/asset_index/archive/migration_scripts/update_non_imp... | data/asset_index/archive/migration_sc... | prototype | draft |
| 69 | data/asset_index/archive/migration_scripts/verify_batch.py | data/asset_index/archive/migration_sc... | prototype | draft |
| 70 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 71 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 72 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 73 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 74 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 75 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 76 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 77 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 78 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 79 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 80 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 81 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 82 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 83 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 84 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 85 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 86 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 87 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 88 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 89 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 90 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 91 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 92 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 93 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 94 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 95 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 96 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 97 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 98 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 99 | docs/03_modules/_alpha_signal_domain/blueprint.md | docs__03_modules___alpha_signal_domai... | design | design_only |
| 100 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | docs__03_modules___cross_layer__agent... | design | design_only |
| 101 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | docs__03_modules___cross_layer__auto_... | design | design_only |
| 102 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | docs__03_modules___cross_layer__auto_... | design | design_only |
| 103 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | docs__03_modules___cross_layer__behav... | design | design_only |
| 104 | docs/03_modules/_cross_layer/context_engine/blueprint.md | docs__03_modules___cross_layer__conte... | design | design_only |
| 105 | docs/03_modules/_cross_layer/database/blueprint.md | docs__03_modules___cross_layer__datab... | design | design_only |
| 106 | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | docs__03_modules___cross_layer__feedb... | design | design_only |
| 107 | docs/03_modules/_cross_layer/feedback_loop/capacity_upgra... | docs__03_modules___cross_layer__feedb... | design | design_only |
| 108 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | docs__03_modules___cross_layer__gate_... | design | design_only |
| 109 | docs/03_modules/_cross_layer/llm_security/blueprint.md | docs__03_modules___cross_layer__llm_s... | design | design_only |
| 110 | docs/03_modules/_cross_layer/mcp_servers/blueprint.md | docs__03_modules___cross_layer__mcp_s... | design | design_only |
| 111 | docs/03_modules/_cross_layer/mcp_servers/changes/MOD_INF_... | docs/03_modules/_cross_layer/mcp_serv... | production | orphan |
| 112 | docs/03_modules/_cross_layer/model_capability_exam/bluepr... | docs__03_modules___cross_layer__model... | design | design_only |
| 113 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | docs__03_modules___cross_layer__orpha... | design | design_only |
| 114 | docs/03_modules/_cross_layer/pipeline/blueprint.md | docs__03_modules___cross_layer__pipel... | design | design_only |
| 115 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | docs__03_modules___cross_layer__red_b... | design | design_only |
| 116 | docs/03_modules/_cross_layer/resource_optimization_engine... | docs__03_modules___cross_layer__resou... | design | design_only |
| 117 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | docs__03_modules___cross_layer__seman... | design | design_only |
| 118 | docs/03_modules/_cross_layer/shared_core/blueprint.md | docs__03_modules___cross_layer__share... | design | design_only |
| 119 | docs/03_modules/_domain_autonomy_core/agent_spec/blind_sp... | docs/03_modules/_domain_autonomy_core... | production | orphan |
| 120 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprin... | docs__03_modules___domain_autonomy_co... | design | design_only |
| 121 | docs/03_modules/_domain_autonomy_core/agent_spec/decision... | docs/03_modules/_domain_autonomy_core... | production | orphan |
| 122 | docs/03_modules/_domain_autonomy_core/agent_spec/phase_tr... | docs/03_modules/_domain_autonomy_core... | production | orphan |
| 123 | docs/03_modules/_domain_autonomy_core/agent_spec/risk_tra... | docs/03_modules/_domain_autonomy_core... | production | orphan |
| 124 | docs/03_modules/_domain_autonomy_core/rollback_system/blu... | docs__03_modules___domain_autonomy_co... | design | design_only |
| 125 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blu... | docs__03_modules___domain_autonomy_pe... | design | design_only |
| 126 | docs/03_modules/_domain_autonomy_perm/escalation_protocol... | docs__03_modules___domain_autonomy_pe... | design | design_only |
| 127 | docs/03_modules/_domain_compliance/compliance_core/bluepr... | docs__03_modules___domain_compliance_... | design | design_only |
| 128 | docs/03_modules/_domain_data/datasource_core/blueprint.md | docs__03_modules___domain_data__datas... | design | design_only |
| 129 | docs/03_modules/_domain_ex_core/ex_core/blueprint.md | docs__03_modules___domain_ex_core__ex... | design | design_only |
| 130 | docs/03_modules/_domain_factor/alpha_factor_core/blueprin... | docs__03_modules___domain_factor__alp... | design | design_only |
| 131 | docs/03_modules/_domain_frontend/hmi_core/blueprint.md | docs__03_modules___domain_frontend__h... | design | design_only |
| 132 | docs/03_modules/_domain_governance/blueprint.md | docs__03_modules___domain_governance_... | design | design_only |
| 133 | docs/03_modules/_domain_governance/capacity_upgrade/bluep... | docs__03_modules___domain_governance_... | design | design_only |
| 134 | docs/03_modules/_domain_governance/code_dedup_engine/blue... | docs__03_modules___domain_governance_... | design | design_only |
| 135 | docs/03_modules/_domain_governance/governance_automation/... | docs__03_modules___domain_governance_... | design | design_only |
| 136 | docs/03_modules/_domain_governance/registry_governance/bl... | docs__03_modules___domain_governance_... | design | design_only |
| 137 | docs/03_modules/_domain_infra_ops/a2a_protocol/a2a_anomal... | docs/03_modules/_domain_infra_ops/a2a... | production | orphan |
| 138 | docs/03_modules/_domain_infra_ops/a2a_protocol/blind_spot... | docs/03_modules/_domain_infra_ops/a2a... | production | orphan |
| 139 | docs/03_modules/_domain_infra_ops/a2a_protocol/blueprint.md | docs__03_modules___domain_infra_ops__... | design | design_only |
| 140 | docs/03_modules/_domain_infra_ops/a2a_protocol/phase_plan... | docs/03_modules/_domain_infra_ops/a2a... | production | orphan |
| 141 | docs/03_modules/_domain_infra_ops/a2a_protocol/pre_mortem... | docs/03_modules/_domain_infra_ops/a2a... | production | orphan |
| 142 | docs/03_modules/_domain_infra_ops/a2a_protocol/trigger_co... | docs/03_modules/_domain_infra_ops/a2a... | production | orphan |
| 143 | docs/03_modules/_domain_infra_ops/a2a_protocol/version_tr... | docs/03_modules/_domain_infra_ops/a2a... | production | orphan |
| 144 | docs/03_modules/_domain_infra_ops/asset_inventory/bluepri... | docs__03_modules___domain_infra_ops__... | design | design_only |
| 145 | docs/03_modules/_domain_infra_ops/capacity_assurance/blue... | docs__03_modules___domain_infra_ops__... | design | design_only |
| 146 | docs/03_modules/_domain_infra_runtime/runtime_integration... | docs__03_modules___domain_infra_runti... | design | design_only |
| 147 | docs/03_modules/_domain_infra_runtime/state_machine_engin... | docs__03_modules___domain_infra_runti... | design | design_only |
| 148 | docs/03_modules/_domain_infra_runtime/task_system/bluepri... | docs__03_modules___domain_infra_runti... | design | design_only |
| 149 | docs/03_modules/_domain_integration/local_model/blueprint.md | docs__03_modules___domain_integration... | design | design_only |
| 150 | docs/03_modules/_domain_ml_train/ml_core/blueprint.md | docs__03_modules___domain_ml_train__m... | design | design_only |
| 151 | docs/03_modules/_domain_pf_core/pf_core/blueprint.md | docs__03_modules___domain_pf_core__po... | design | design_only |
| 152 | docs/03_modules/_domain_reporting/analytics_core/blueprin... | docs__03_modules___domain_reporting__... | design | design_only |
| 153 | docs/03_modules/_domain_research/research_core/blueprint.md | docs__03_modules___domain_research__r... | design | design_only |
| 154 | docs/03_modules/_domain_risk/risk_management_core/bluepri... | docs__03_modules___domain_risk__risk_... | design | design_only |
| 155 | docs/03_modules/_domain_signal/signal_generation_core/blu... | docs__03_modules___domain_signal__sig... | design | design_only |
| 156 | docs/03_modules/_domain_simulation/experiment_core/bluepr... | docs__03_modules___domain_simulation_... | design | design_only |
| 157 | docs/03_modules/_master_blueprint/blueprint.md | docs__03_modules___master_blueprint__... | design | design_only |
| 158 | docs/03_modules/_master_blueprint/blueprint_agent_spec.md | agent_spec_md | design | design_only |
| 159 | docs/03_modules/_ml_experiment_domain/blueprint.md | docs__03_modules___ml_experiment_doma... | design | design_only |
| 160 | docs/03_modules/_restructuring/blueprint.md | docs__03_modules___restructuring__blu... | design | design_only |
| 161 | docs/03_modules/_sys_master/blueprint.md | docs__03_modules___sys_master__bluepr... | design | design_only |
| 162 | docs/03_modules/path_ownership_map.yaml | docs/03_modules/path_ownership_map.yaml | production | orphan |
| 163 | scripts/__init__.py | scripts/__init__.py | prototype | draft |
| 164 | scripts/_archive/construction/create_db_alignment_tasks.py | scripts/_archive/construction/create_... | prototype | draft |
| 165 | scripts/_archive/construction/create_dm_phase9_tasks.py | scripts/_archive/construction/create_... | prototype | draft |
| 166 | scripts/_archive/construction/dm014_orphan_edge_repair.py | scripts/_archive/construction/dm014_o... | prototype | draft |
| 167 | scripts/_archive/governance/create_depgraph_task_cards.py | scripts/_archive/governance/create_de... | prototype | draft |
| 168 | scripts/_archive/governance/d3_metadata/assign_module_id.py | scripts/_archive/governance/d3_metada... | prototype | draft |
| 169 | scripts/_archive/governance/d3_metadata/check_frontmatter... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 170 | scripts/_archive/governance/d3_metadata/check_template_co... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 171 | scripts/_archive/governance/d3_metadata/detect_deprecated... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 172 | scripts/_archive/governance/d3_metadata/detect_skip_activ... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 173 | scripts/_archive/governance/d3_metadata/detect_stale_vers... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 174 | scripts/_archive/governance/d3_metadata/fix_dm411_bare_re... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 175 | scripts/_archive/governance/d3_metadata/fix_dm413_duplica... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 176 | scripts/_archive/governance/d3_metadata/fix_n06_module_id... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 177 | scripts/_archive/governance/d3_metadata/generate_rule_cat... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 178 | scripts/_archive/governance/d3_metadata/scan_deep_content.py | scripts/_archive/governance/d3_metada... | prototype | draft |
| 179 | scripts/_archive/governance/d3_metadata/validate_blueprin... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 180 | scripts/_archive/governance/d3_metadata/validate_cross_mo... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 181 | scripts/_archive/governance/d3_metadata/validate_derived_... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 182 | scripts/_archive/governance/d3_metadata/validate_enum_con... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 183 | scripts/_archive/governance/d3_metadata/validate_frontmat... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 184 | scripts/_archive/governance/d3_metadata/validate_no_dupli... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 185 | scripts/_archive/governance/d3_metadata/validate_ssot_sta... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 186 | scripts/_archive/governance/d3_metadata/validate_supersed... | scripts/_archive/governance/d3_metada... | prototype | draft |
| 187 | scripts/_archive/governance/dm101_blueprint_domain_mappin... | scripts/_archive/governance/dm101_blu... | prototype | draft |
| 188 | scripts/_archive/governance/merge_domain_nodes.py | scripts/_archive/governance/merge_dom... | prototype | draft |
| 189 | scripts/_archive/migration/_migration_shared.py | scripts/_archive/migration/_migration... | prototype | draft |
| 190 | scripts/_archive/migration/_verify_manifest.py | scripts/_archive/migration/_verify_ma... | prototype | draft |
| 191 | scripts/_archive/migration/_verify_step4.py | scripts/_archive/migration/_verify_st... | prototype | draft |
| 192 | scripts/_archive/migration/apply_rulings.py | scripts/_archive/migration/apply_ruli... | prototype | draft |
| 193 | scripts/_archive/migration/check_coverage.py | scripts/_archive/migration/check_cove... | prototype | draft |
| 194 | scripts/_archive/migration/comprehensive_import_fix.py | scripts/_archive/migration/comprehens... | prototype | draft |
| 195 | scripts/_archive/migration/create_target_dirs.py | scripts/_archive/migration/create_tar... | prototype | draft |
| 196 | scripts/_archive/migration/cross_domain_import_fix.py | scripts/_archive/migration/cross_doma... | prototype | draft |
| 197 | scripts/_archive/migration/domain_prefix_import_fix.py | scripts/_archive/migration/domain_pre... | prototype | draft |
| 198 | scripts/_archive/migration/execute_move.py | scripts/_archive/migration/execute_mo... | prototype | draft |
| 199 | scripts/_archive/migration/generate_migration_registry.py | scripts/_archive/migration/generate_m... | prototype | draft |
| 200 | scripts/_archive/migration/generate_path_migration_mappin... | scripts/_archive/migration/generate_p... | prototype | draft |

> (仅显示前 200 个模块，共 3312 个)

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/data_governance/__init__.py | src/zephyr/data_governance/__init__.py | prototype | draft |
| 2 | src/zephyr/data_governance/_extensions/__init__.py | src/zephyr/data_governance/_extension... | scaffold_placeholder | orphan |
| 3 | src/zephyr/data_governance/api/__init__.py | src/zephyr/data_governance/api/__init... | scaffold_placeholder | orphan |
| 4 | src/zephyr/data_governance/core/__init__.py | src/zephyr/data_governance/core/__ini... | scaffold_placeholder | orphan |
| 5 | src/zephyr/data_governance/infrastructure/__init__.py | src/zephyr/data_governance/infrastruc... | scaffold_placeholder | orphan |
| 6 | src/zephyr/data_governance/models/__init__.py | src/zephyr/data_governance/models/__i... | scaffold_placeholder | orphan |
| 7 | src/zephyr/data_governance/services/__init__.py | src/zephyr/data_governance/services/_... | scaffold_placeholder | orphan |

### 未分类 / Unclassified (541 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-GOVERNANCE/45 Capability List 45项能力清单 | 45 Capability List 45项能力清单 | design | design_only |
| 2 | D-GOVERNANCE/5 Drift Detection 5类漂移检测 | 5 Drift Detection 5类漂移检测 | design | design_only |
| 3 | D-GOVERNANCE/A2A Failure Escalation A2A失败升级 | A2A Failure Escalation A2A失败升级 | design | design_only |
| 4 | D-GOVERNANCE/A2A Gateway Policy Engine A2A检查网关策略引擎 | A2A Gateway Policy Engine A2A检查网关... | design | design_only |
| 5 | D-GOVERNANCE/A2A Iron Law A2A铁律 | A2A Iron Law A2A铁律 | design | design_only |
| 6 | D-GOVERNANCE/A2A Protocol Governance Auditor A2A协议治理... | A2A Protocol Governance Auditor A2A协... | design | design_only |
| 7 | D-GOVERNANCE/A2A Protocol Governance Contracts A2A协议治... | A2A Protocol Governance Contracts A2A... | design | design_only |
| 8 | D-GOVERNANCE/A2A Protocol Phase Hold A2A协议阶段保持 | A2A Protocol Phase Hold A2A协议阶段保持 | design | design_only |
| 9 | D-GOVERNANCE/ACO多路径依赖搜索器 ACOMultiPathDependencySe... | ACO多路径依赖搜索器 ACOMultiPathDepen... | design | design_only |
| 10 | D-GOVERNANCE/ADR Decision Tracking ADR决策追踪 | ADR Decision Tracking ADR决策追踪 | design | design_only |
| 11 | D-GOVERNANCE/ADR Generation ADR架构决策记录自动生成 | ADR Generation ADR架构决策记录自动生成 | design | design_only |
| 12 | D-GOVERNANCE/ADR Generation ADR生成 | ADR Generation ADR生成 | design | design_only |
| 13 | D-GOVERNANCE/ADR Simulation ADR仿真 | ADR Simulation ADR仿真 | design | design_only |
| 14 | D-GOVERNANCE/ADR传播/多ADR交互/回溯/变更仿真等 | ADR传播/多ADR交互/回溯/变更仿真等 | design | design_only |
| 15 | D-GOVERNANCE/ADR解析/约束提取/双向关联/校验/推演等 | ADR解析/约束提取/双向关联/校验/推演等 | design | design_only |
| 16 | D-GOVERNANCE/AI Autonomy Boundary AI自治边界 | AI Autonomy Boundary AI自治边界 | design | design_only |
| 17 | D-GOVERNANCE/AI Autonomy Boundary Manager AI自治边界管理器 | AI Autonomy Boundary Manager AI自治边... | design | design_only |
| 18 | D-GOVERNANCE/AI Code Review AI代码审查 | AI Code Review AI代码审查 | design | design_only |
| 19 | D-GOVERNANCE/AI Code Standards AI代码标准 | AI Code Standards AI代码标准 | design | design_only |
| 20 | D-GOVERNANCE/AI Construction Governor AI施工治理器 | AI Construction Governor AI施工治理器 | design | design_only |
| 21 | D-GOVERNANCE/AI Ethics Statement AI伦理声明 | AI Ethics Statement AI伦理声明 | design | design_only |
| 22 | D-GOVERNANCE/AI Hallucination Detection AI幻觉检测 | AI Hallucination Detection AI幻觉检测 | design | design_only |
| 23 | D-GOVERNANCE/AI Self Diagnosis AI自诊断监督 | AI Self Diagnosis AI自诊断监督 | design | design_only |
| 24 | D-GOVERNANCE/AIConstructionGovernor AI建设治理器 | AIConstructionGovernor AI建设治理器 | design | design_only |
| 25 | D-GOVERNANCE/AI模型能力持续提升 | AI模型能力持续提升 | design | design_only |
| 26 | D-GOVERNANCE/AI治理框架 AI Governance Framework | AI治理框架 AI Governance Framework | design | design_only |
| 27 | D-GOVERNANCE/AI生成策略合规 | AI生成策略合规 | design | design_only |
| 28 | D-GOVERNANCE/ALPHA-SIGNAL-DOMAIN-001 Alpha信号域标识 | ALPHA-SIGNAL-DOMAIN-001 Alpha信号域标识 | design | design_only |
| 29 | D-GOVERNANCE/API Dependency API依赖 | API Dependency API依赖 | design | design_only |
| 30 | D-GOVERNANCE/AST Call Graph AST调用图 | AST Call Graph AST调用图 | design | design_only |
| 31 | D-GOVERNANCE/AST Call Graph Generator AST调用图生成器 | AST Call Graph Generator AST调用图生成器 | design | design_only |
| 32 | D-GOVERNANCE/AST解析/调用图/膨胀检测/清理/可视化等 | AST解析/调用图/膨胀检测/清理/可视化等 | design | design_only |
| 33 | D-GOVERNANCE/AaC Compiler AaC编译器 | AaC Compiler AaC编译器 | design | design_only |
| 34 | D-GOVERNANCE/AaC DSL/约束定义/漂移检测/修复/CI集成等 | AaC DSL/约束定义/漂移检测/修复/CI集成等 | design | design_only |
| 35 | D-GOVERNANCE/AaC DSL编译/CI门禁/漂移/修复/报告等 | AaC DSL编译/CI门禁/漂移/修复/报告等 | design | design_only |
| 36 | D-GOVERNANCE/Activation Phase Set 激活阶段集 | Activation Phase Set 激活阶段集 | design | design_only |
| 37 | D-GOVERNANCE/Administrator 管理员角色 | Administrator 管理员角色 | design | design_only |
| 38 | D-GOVERNANCE/Admission Response 准入响应 | Admission Response 准入响应 | design | design_only |
| 39 | D-GOVERNANCE/Adoption Curve Modeler 采纳曲线建模器 | Adoption Curve Modeler 采纳曲线建模器 | design | design_only |
| 40 | D-GOVERNANCE/Agent Debate Agent辩论机制 | Agent Debate Agent辩论机制 | design | design_only |
| 41 | D-GOVERNANCE/Agent Hard Boundary Agent硬边界 | Agent Hard Boundary Agent硬边界 | design | design_only |
| 42 | D-GOVERNANCE/Agent OS Policy Engine Agent OS策略引擎 | Agent OS Policy Engine Agent OS策略引擎 | design | design_only |
| 43 | D-GOVERNANCE/Agentic Drift Protection Agentic Drift防护 | Agentic Drift Protection Agentic Drif... | design | design_only |
| 44 | D-GOVERNANCE/Agentic Regulator四层治理框架 | Agentic Regulator四层治理框架 | design | design_only |
| 45 | D-GOVERNANCE/Agent架构 Agent Architecture | Agent架构 Agent Architecture | design | design_only |
| 46 | D-GOVERNANCE/Agent集群 Agent Cluster MARL | Agent集群 Agent Cluster MARL | design | design_only |
| 47 | D-GOVERNANCE/Approval Escalation 审批升级 | Approval Escalation 审批升级 | design | design_only |
| 48 | D-GOVERNANCE/Architecture Contracts 架构契约 | Architecture Contracts 架构契约 | design | design_only |
| 49 | D-GOVERNANCE/Architecture Drift Detection 架构漂移检测与... | Architecture Drift Detection 架构漂移... | design | design_only |
| 50 | D-GOVERNANCE/Architecture Principles 架构原则定义 | Architecture Principles 架构原则定义 | design | design_only |
| 51 | D-GOVERNANCE/Architecture Tech Debt Tracker 架构技术债追踪器 | Architecture Tech Debt Tracker 架构技... | design | design_only |
| 52 | D-GOVERNANCE/Architecture Test Suite 架构测试套件 | Architecture Test Suite 架构测试套件 | design | design_only |
| 53 | D-GOVERNANCE/Architecture as Code Engine 架构即代码引擎 | Architecture as Code Engine 架构即代... | design | design_only |
| 54 | D-GOVERNANCE/Architecture as Code 架构即代码 | Architecture as Code 架构即代码 | design | design_only |
| 55 | D-GOVERNANCE/ArchitectureGovernance 架构治理 | ArchitectureGovernance 架构治理 | design | design_only |
| 56 | D-GOVERNANCE/Audit & Compliance Traceability 审计与合规追溯 | Audit & Compliance Traceability 审计... | design | design_only |
| 57 | D-GOVERNANCE/Audit Engine 审计引擎 | Audit Engine 审计引擎 | design | design_only |
| 58 | D-GOVERNANCE/Audit Integrity Verifier 审计完整性验证器 | Audit Integrity Verifier 审计完整性验... | design | design_only |
| 59 | D-GOVERNANCE/Audit Log Immutable 审计日志不可篡改 | Audit Log Immutable 审计日志不可篡改 | design | design_only |
| 60 | D-GOVERNANCE/Audit Log Non-Tamperable 审计日志不可篡改 | Audit Log Non-Tamperable 审计日志不可... | design | design_only |
| 61 | D-GOVERNANCE/Audit Log Non-Tamperable 审计日志不可篡改删除 | Audit Log Non-Tamperable 审计日志不可... | design | design_only |
| 62 | D-GOVERNANCE/AuditContext Consumer Interface AuditContext... | AuditContext Consumer Interface Audit... | design | design_only |
| 63 | D-GOVERNANCE/AuditContext 审计上下文接口 | AuditContext 审计上下文接口 | design | design_only |
| 64 | D-GOVERNANCE/AuditContextUpdate 审计上下文更新 | AuditContextUpdate 审计上下文更新 | design | design_only |
| 65 | D-GOVERNANCE/AuditLedger 审计账本 | AuditLedger 审计账本 | design | design_only |
| 66 | D-GOVERNANCE/AuditQuery 审计查询 | AuditQuery 审计查询 | design | design_only |
| 67 | D-GOVERNANCE/A股T+1制度不变 | A股T+1制度不变 | design | design_only |
| 68 | D-GOVERNANCE/Behavioral Auditor 行为审计器 | Behavioral Auditor 行为审计器 | design | design_only |
| 69 | D-GOVERNANCE/Benchmark Integrity 基准完整性 | Benchmark Integrity 基准完整性 | design | design_only |
| 70 | D-GOVERNANCE/Blueprint Code Document Three Way Alignment ... | Blueprint Code Document Three Way Ali... | design | design_only |
| 71 | D-GOVERNANCE/Blueprint Code Document Three Way Alignment ... | Blueprint Code Document Three Way Ali... | design | design_only |
| 72 | D-GOVERNANCE/Blueprint-Code Traceability 蓝图-代码追溯 | Blueprint-Code Traceability 蓝图-代码... | design | design_only |
| 73 | D-GOVERNANCE/Blueprint-Code-Doc Three-Way Alignment 蓝图-... | Blueprint-Code-Doc Three-Way Alignmen... | design | design_only |
| 74 | D-GOVERNANCE/Broker Resilience Broker韧性 | Broker Resilience Broker韧性 | design | design_only |
| 75 | D-GOVERNANCE/Budget Handler 预算处理 | Budget Handler 预算处理 | design | design_only |
| 76 | D-GOVERNANCE/Budget Tracker 预算追踪 | Budget Tracker 预算追踪 | design | design_only |
| 77 | D-GOVERNANCE/Business Capability-Module Mapper 业务能力-... | Business Capability-Module Mapper 业... | design | design_only |
| 78 | D-GOVERNANCE/BusinessCapabilityMapper 业务能力映射器 | BusinessCapabilityMapper 业务能力映射器 | design | design_only |
| 79 | D-GOVERNANCE/CFA Institute两层治理框架 | CFA Institute两层治理框架 | design | design_only |
| 80 | D-GOVERNANCE/CQRS/ES Modeling CQRS/ES建模 | CQRS/ES Modeling CQRS/ES建模 | design | design_only |
| 81 | D-GOVERNANCE/CTR-P1-009 Governance Contract CTR-P1-009治... | CTR-P1-009 Governance Contract CTR-P1... | design | design_only |
| 82 | D-GOVERNANCE/CTR-P1-012 ComplianceRule 合规规则 | CTR-P1-012 ComplianceRule 合规规则 | design | design_only |
| 83 | D-GOVERNANCE/Captide 对冲基金AI平台 | Captide 对冲基金AI平台 | design | design_only |
| 84 | D-GOVERNANCE/Causal Conflict Detector 因果冲突检测器 | Causal Conflict Detector 因果冲突检测器 | design | design_only |
| 85 | D-GOVERNANCE/Cedar Cedar策略语言 | Cedar Cedar策略语言 | design | design_only |
| 86 | D-GOVERNANCE/Change Approval Chain Not Bypassable 变更审... | Change Approval Chain Not Bypassable ... | design | design_only |
| 87 | D-GOVERNANCE/Change Approval Flow 变更审批流 | Change Approval Flow 变更审批流 | design | design_only |
| 88 | D-GOVERNANCE/Change Impact Analyzer 变更影响分析器 | Change Impact Analyzer 变更影响分析器 | design | design_only |
| 89 | D-GOVERNANCE/Change Shock Radius Predictor 变更冲击半径预... | Change Shock Radius Predictor 变更冲... | design | design_only |
| 90 | D-GOVERNANCE/Check Threeway Alignment 检查三对齐 | Check Threeway Alignment 检查三对齐 | design | design_only |
| 91 | D-GOVERNANCE/Closed-Loop Rule 闭环规则 | Closed-Loop Rule 闭环规则 | design | design_only |
| 92 | D-GOVERNANCE/Code Dedup Engine 代码去重引擎 | Code Dedup Engine 代码去重引擎 | design | design_only |
| 93 | D-GOVERNANCE/CogAlpha | CogAlpha | design | design_only |
| 94 | D-GOVERNANCE/Compliance Scripts 合规脚本 | Compliance Scripts 合规脚本 | design | design_only |
| 95 | D-GOVERNANCE/ComplianceAudit 合规审计 | ComplianceAudit 合规审计 | design | design_only |
| 96 | D-GOVERNANCE/ComplianceAuditCompleted 合规审计完成 | ComplianceAuditCompleted 合规审计完成 | design | design_only |
| 97 | D-GOVERNANCE/ComplianceAuditor 合规审计器 | ComplianceAuditor 合规审计器 | design | design_only |
| 98 | D-GOVERNANCE/ComplianceChecker 合规检查器 | ComplianceChecker 合规检查器 | design | design_only |
| 99 | D-GOVERNANCE/ComplianceRule Consumer Interface Compliance... | ComplianceRule Consumer Interface Com... | design | design_only |
| 100 | D-GOVERNANCE/ComplianceRuleUpdated 合规规则更新 | ComplianceRuleUpdated 合规规则更新 | design | design_only |
| 101 | D-GOVERNANCE/Conditional Gate Extension 条件门禁扩展 | Conditional Gate Extension 条件门禁扩展 | design | design_only |
| 102 | D-GOVERNANCE/ConfigChanged 参数变更事件 | ConfigChanged 参数变更事件 | design | design_only |
| 103 | D-GOVERNANCE/Consequence Manager 后果管理器 | Consequence Manager 后果管理器 | design | design_only |
| 104 | D-GOVERNANCE/Constitutional Update 宪法更新 | Constitutional Update 宪法更新 | design | design_only |
| 105 | D-GOVERNANCE/ConstitutionalGuard 宪法守卫 | ConstitutionalGuard 宪法守卫 | design | design_only |
| 106 | D-GOVERNANCE/Construction Gate 施工门禁 | Construction Gate 施工门禁 | design | design_only |
| 107 | D-GOVERNANCE/Consume Event Set 消费事件集 | Consume Event Set 消费事件集 | design | design_only |
| 108 | D-GOVERNANCE/Consumer Interface Set 消费接口集 | Consumer Interface Set 消费接口集 | design | design_only |
| 109 | D-GOVERNANCE/Contract Version Management 契约版本管理 | Contract Version Management 契约版本管理 | design | design_only |
| 110 | D-GOVERNANCE/ContractRegistered 契约注册 | ContractRegistered 契约注册 | design | design_only |
| 111 | D-GOVERNANCE/ContractRegistry Consumer Interface Contract... | ContractRegistry Consumer Interface C... | design | design_only |
| 112 | D-GOVERNANCE/Coupling Metrics 耦合度量 | Coupling Metrics 耦合度量 | design | design_only |
| 113 | D-GOVERNANCE/Coupling Strength Metrics 耦合度量计算器 | Coupling Strength Metrics 耦合度量计算器 | design | design_only |
| 114 | D-GOVERNANCE/CouplingStrengthMetrics 耦合度量 | CouplingStrengthMetrics 耦合度量 | design | design_only |
| 115 | D-GOVERNANCE/Critical Path Analyzer 关键路径分析器 | Critical Path Analyzer 关键路径分析器 | design | design_only |
| 116 | D-GOVERNANCE/Cross Cutting Triangle 横切三角 | Cross Cutting Triangle 横切三角 | design | design_only |
| 117 | D-GOVERNANCE/Cross Environment Consistency 跨环境一致性校验 | Cross Environment Consistency 跨环境... | design | design_only |
| 118 | D-GOVERNANCE/Cross-Domain Intersection 跨域交叉点 | Cross-Domain Intersection 跨域交叉点 | design | design_only |
| 119 | D-GOVERNANCE/Cycle Detection 环路检测 | Cycle Detection 环路检测 | design | design_only |
| 120 | D-GOVERNANCE/D-GOV-16~26 Dependency Semantic Series 依赖... | D-GOV-16~26 Dependency Semantic Serie... | design | design_only |
| 121 | D-GOVERNANCE/D-GOVERNANCE 治理 | D-GOVERNANCE 治理 | design | design_only |
| 122 | D-GOVERNANCE/D1~D84 独立研究模块 | D1~D84 独立研究模块 | design | design_only |
| 123 | D-GOVERNANCE/D5 Architecture Validators D5架构验证器 | D5 Architecture Validators D5架构验证器 | design | design_only |
| 124 | D-GOVERNANCE/DDD Iron Law Three Stage Execution DDD铁律三... | DDD Iron Law Three Stage Execution DD... | design | design_only |
| 125 | D-GOVERNANCE/DDDRuleCheck DDD铁律检查 | DDDRuleCheck DDD铁律检查 | design | design_only |
| 126 | D-GOVERNANCE/DDDRuleEnforcer DDD铁律执行器 | DDDRuleEnforcer DDD铁律执行器 | design | design_only |
| 127 | D-GOVERNANCE/DDDViolationDetected DDD违规检出 | DDDViolationDetected DDD违规检出 | design | design_only |
| 128 | D-GOVERNANCE/DOM-GOV-CAP-001 容量升级 | DOM-GOV-CAP-001 容量升级 | design | design_only |
| 129 | D-GOVERNANCE/Data Classification 数据分类 | Data Classification 数据分类 | design | design_only |
| 130 | D-GOVERNANCE/Data Lifecycle 数据生命周期 | Data Lifecycle 数据生命周期 | design | design_only |
| 131 | D-GOVERNANCE/Data Quality 数据质量 | Data Quality 数据质量 | design | design_only |
| 132 | D-GOVERNANCE/Data Source Reliability 数据源可靠性 | Data Source Reliability 数据源可靠性 | design | design_only |
| 133 | D-GOVERNANCE/Decision Fatigue CLI 决策疲劳CLI | Decision Fatigue CLI 决策疲劳CLI | design | design_only |
| 134 | D-GOVERNANCE/Decision Fatigue Detector 决策疲劳检测器 | Decision Fatigue Detector 决策疲劳检测器 | design | design_only |
| 135 | D-GOVERNANCE/DecisionArchived 决策归档 | DecisionArchived 决策归档 | design | design_only |
| 136 | D-GOVERNANCE/DecisionProvenance 决策溯源链 | DecisionProvenance 决策溯源链 | design | design_only |
| 137 | D-GOVERNANCE/DecisionTrace 决策溯源 | DecisionTrace 决策溯源 | design | design_only |
| 138 | D-GOVERNANCE/DepMap Engine 分层存储AST依赖扫描引擎 | DepMap Engine 分层存储AST依赖扫描引擎 | design | design_only |
| 139 | D-GOVERNANCE/Dependency Adoption Pattern Analyzer 依赖采... | Dependency Adoption Pattern Analyzer ... | design | design_only |
| 140 | D-GOVERNANCE/Dependency Amplification Analyzer 依赖放大效... | Dependency Amplification Analyzer 依... | design | design_only |
| 141 | D-GOVERNANCE/Dependency Amplification Mitigation 依赖放大... | Dependency Amplification Mitigation ... | design | design_only |
| 142 | D-GOVERNANCE/Dependency Analysis Domain 依赖分析域 | Dependency Analysis Domain 依赖分析域 | design | design_only |
| 143 | D-GOVERNANCE/Dependency Bloat Meter 依赖膨胀度量器 | Dependency Bloat Meter 依赖膨胀度量器 | design | design_only |
| 144 | D-GOVERNANCE/Dependency Change Log 依赖变更日志 | Dependency Change Log 依赖变更日志 | design | design_only |
| 145 | D-GOVERNANCE/Dependency Change Log 模块依赖变更日志 | Dependency Change Log 模块依赖变更日志 | design | design_only |
| 146 | D-GOVERNANCE/Dependency Deduplication Advisor 依赖去重顾问 | Dependency Deduplication Advisor 依赖... | design | design_only |
| 147 | D-GOVERNANCE/Dependency Entropy Calculator 依赖熵计算器 | Dependency Entropy Calculator 依赖熵... | design | design_only |
| 148 | D-GOVERNANCE/Dependency Health Scorecard 依赖健康评分卡 | Dependency Health Scorecard 依赖健康... | design | design_only |
| 149 | D-GOVERNANCE/Dependency Manager 依赖管理 | Dependency Manager 依赖管理 | design | design_only |
| 150 | D-GOVERNANCE/Dependency Semantics Layer 依赖语义层 | Dependency Semantics Layer 依赖语义层 | design | design_only |
| 151 | D-GOVERNANCE/Dependency Temporal Evolution Analyzer 依赖... | Dependency Temporal Evolution Analyze... | design | design_only |
| 152 | D-GOVERNANCE/Dependency Update Latency Predictor 依赖更新... | Dependency Update Latency Predictor ... | design | design_only |
| 153 | D-GOVERNANCE/DependencyAmplification 依赖放大效应 | DependencyAmplification 依赖放大效应 | design | design_only |
| 154 | D-GOVERNANCE/DependencySemantics 依赖语义 | DependencySemantics 依赖语义 | design | design_only |
| 155 | D-GOVERNANCE/Dependent Type Verifier 依赖类型验证器 | Dependent Type Verifier 依赖类型验证器 | design | design_only |
| 156 | D-GOVERNANCE/Developer Portal 开发者门户 | Developer Portal 开发者门户 | design | design_only |
| 157 | D-GOVERNANCE/Dnalyaw | Dnalyaw | design | design_only |
| 158 | D-GOVERNANCE/Downstream Anchors Verifier 下游锚点验证器 | Downstream Anchors Verifier 下游锚点... | design | design_only |
| 159 | D-GOVERNANCE/Drift Fix 漂移修复 | Drift Fix 漂移修复 | design | design_only |
| 160 | D-GOVERNANCE/DriftGovernance 漂移治理 | DriftGovernance 漂移治理 | design | design_only |
| 161 | D-GOVERNANCE/Dual-Layer Gate Model 双层门控架构 | Dual-Layer Gate Model 双层门控架构 | design | design_only |
| 162 | D-GOVERNANCE/Durable Execution 持久化执行 | Durable Execution 持久化执行 | design | design_only |
| 163 | D-GOVERNANCE/Dw150 Update Blueprints dw150更新入 | Dw150 Update Blueprints dw150更新入 | design | design_only |
| 164 | D-GOVERNANCE/Dw151 Full Verify dw151满验证 | Dw151 Full Verify dw151满验证 | design | design_only |
| 165 | D-GOVERNANCE/E-0046 执行核心→治理域依赖 | E-0046 执行核心→治理域依赖 | design | design_only |
| 166 | D-GOVERNANCE/E-0093 合规域→治理域依赖 | E-0093 合规域→治理域依赖 | design | design_only |
| 167 | D-GOVERNANCE/E-0123 前端域→治理域依赖 | E-0123 前端域→治理域依赖 | design | design_only |
| 168 | D-GOVERNANCE/E-0124 治理域→自治核心依赖 | E-0124 治理域→自治核心依赖 | design | design_only |
| 169 | D-GOVERNANCE/E-0125 治理域→集成域依赖 | E-0125 治理域→集成域依赖 | design | design_only |
| 170 | D-GOVERNANCE/E-0126 治理域→运行时基础设施依赖 | E-0126 治理域→运行时基础设施依赖 | design | design_only |
| 171 | D-GOVERNANCE/E-GV-01 GatePassed E-GV-01门禁通过 | E-GV-01 GatePassed E-GV-01门禁通过 | design | design_only |
| 172 | D-GOVERNANCE/E-GV-02 GateFailed E-GV-02门禁失败 | E-GV-02 GateFailed E-GV-02门禁失败 | design | design_only |
| 173 | D-GOVERNANCE/E-GV-03 PolicyUpdated 策略 | E-GV-03 PolicyUpdated 策略 | design | design_only |
| 174 | D-GOVERNANCE/E-GV-04 AuditAnomalyDetected 审计 | E-GV-04 AuditAnomalyDetected 审计 | design | design_only |
| 175 | D-GOVERNANCE/EU AI Act Article 14 Compliance Mapping EU A... | EU AI Act Article 14 Compliance Mappi... | design | design_only |
| 176 | D-GOVERNANCE/EU AI Act字面合规 EU AI Act Literal Compliance | EU AI Act字面合规 EU AI Act Literal C... | design | design_only |
| 177 | D-GOVERNANCE/EVT-AUT-AUDIT Consume Event EVT-AUT-AUDIT消... | EVT-AUT-AUDIT Consume Event EVT-AUT-A... | design | design_only |
| 178 | D-GOVERNANCE/EVT-AUT-PERM Consume Event EVT-AUT-PERM消费事件 | EVT-AUT-PERM Consume Event EVT-AUT-PE... | design | design_only |
| 179 | D-GOVERNANCE/EVT-CMP-RULE Consume Event EVT-CMP-RULE消费事件 | EVT-CMP-RULE Consume Event EVT-CMP-RU... | design | design_only |
| 180 | D-GOVERNANCE/EVT-DE-LINEAGE Consume Event EVT-DE-LINEAGE... | EVT-DE-LINEAGE Consume Event EVT-DE-L... | design | design_only |
| 181 | D-GOVERNANCE/EVT-EX-AUDIT Consume Event EVT-EX-AUDIT消费事件 | EVT-EX-AUDIT Consume Event EVT-EX-AUD... | design | design_only |
| 182 | D-GOVERNANCE/EVT-FE-GOV Consume Event EVT-FE-GOV消费事件 | EVT-FE-GOV Consume Event EVT-FE-GOV消... | design | design_only |
| 183 | D-GOVERNANCE/EVT-INT-CONTRACT Consume Event EVT-INT-CONTR... | EVT-INT-CONTRACT Consume Event EVT-IN... | design | design_only |
| 184 | D-GOVERNANCE/EVT-OPS-ALERT Consume Event EVT-OPS-ALERT消... | EVT-OPS-ALERT Consume Event EVT-OPS-A... | design | design_only |
| 185 | D-GOVERNANCE/EVT-SEC-SCAN Consume Event EVT-SEC-SCAN消费事件 | EVT-SEC-SCAN Consume Event EVT-SEC-SC... | design | design_only |
| 186 | D-GOVERNANCE/Ecosystem Risk Diversification Analyzer 生态... | Ecosystem Risk Diversification Analyz... | design | design_only |
| 187 | D-GOVERNANCE/Entanglement-Aware Scheduler 纠缠感知调度器 | Entanglement-Aware Scheduler 纠缠感知... | design | design_only |
| 188 | D-GOVERNANCE/Escalation Governance Contracts 升级治理契约 | Escalation Governance Contracts 升级... | design | design_only |
| 189 | D-GOVERNANCE/Evals Evaluation Framework 评估框架 | Evals Evaluation Framework 评估框架 | design | design_only |
| 190 | D-GOVERNANCE/Event-Driven Dependency Tracer 事件驱动依赖... | Event-Driven Dependency Tracer 事件驱... | design | design_only |
| 191 | D-GOVERNANCE/EventBus Consumer Interface EventBus消费接口 | EventBus Consumer Interface EventBus... | design | design_only |
| 192 | D-GOVERNANCE/EventBus 事件总线接口 | EventBus 事件总线接口 | design | design_only |
| 193 | D-GOVERNANCE/ExecutionAudit Consumer Interface ExecutionA... | ExecutionAudit Consumer Interface Exe... | design | design_only |
| 194 | D-GOVERNANCE/ExecutionAudit 执行审计接口 | ExecutionAudit 执行审计接口 | design | design_only |
| 195 | D-GOVERNANCE/ExecutionAuditEvent 执行审计事件 | ExecutionAuditEvent 执行审计事件 | design | design_only |
| 196 | D-GOVERNANCE/FactorMAD 因子 | FactorMAD 因子 | design | design_only |
| 197 | D-GOVERNANCE/FactorMiner 因子 | FactorMiner 因子 | design | design_only |
| 198 | D-GOVERNANCE/Factory层 Factory Layer | Factory层 Factory Layer | design | design_only |
| 199 | D-GOVERNANCE/Fan-In/Fan-Out Analyzer 扇入扇出分析器 | Fan-In/Fan-Out Analyzer 扇入扇出分析器 | design | design_only |
| 200 | D-GOVERNANCE/Fault Tolerance 容错 | Fault Tolerance 容错 | design | design_only |

> (仅显示前 200 个模块，共 541 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 2158 条 / 2158 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│     依赖关系图 / Dependency Graph (共 2158 条 / 2158 edges)      │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 9                               │
│   [config_depends]: 797 条 / edges                               │
│   [import_depends]: 730 条 / edges                               │
│   [test_depends]: 489 条 / edges                                 │
│   [contract]: 52 条 / edges                                      │
│   [event]: 44 条 / edges                                         │
│   [runtime]: 30 条 / edges                                       │
│   [data]: 14 条 / edges                                          │
│   [invoke]: 1 条 / edges                                         │
│   [import]: 1 条 / edges                                         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [config_depends] (797 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   account_isolator.py → __init__.py                              │
│   action_history.py → __init__.py                                │
│   agent_cooldown.py → __init__.py                                │
│   anti_automation_bias.py → __init__.py                          │
│   annotations.py → __init__.py                                   │
│   api_lifecycle.py → __init__.py                                 │
│   alternative_path_blocker.py → __init__.py                      │
│   api_response_sanitizer.py → __init__.py                        │
│   ast_comparator.py → __init__.py                                │
│   arbitrage_asymmetry_detec... → __init__.py                     │
│   atomic_fixer.py → __init__.py                                  │
│   auditor.py → __init__.py                                       │
│   autonomy_dashboard.py → __init__.py                            │
│   autonomy_regressor.py → __init__.py                            │
│   auto_fixer.py → __init__.py                                    │
│   base.py → __init__.py                                          │
│   bandwidth_optimizer.py → __init__.py                           │
│   bare_repo_scanner.py → __init__.py                             │
│   auto_test_generator.py → __init__.py                           │
│   backtest_engine.py → __init__.py                               │
│   behavioral_trust_checker.py → __init__.py                      │
│   behavioral_sampler.py → __init__.py                            │
│   blast_radius.py → __init__.py                                  │
│   blueprint_reconciler.py → __init__.py                          │
│   blueprint_bloat_monitor.py → __init__.py                       │
│   blind_spot_tracker.py → __init__.py                            │
│   blueprint_code_consistenc... → __init__.py                     │
│   bootstrapping_calibrator.py → __init__.py                      │
│   broker_resilience.py → __init__.py                             │
│   cache_manager.py → __init__.py                                 │
│   canary_register.py → __init__.py                               │
│   canary_manager.py → __init__.py                                │
│   changelog_manager.py → __init__.py                             │
│   checkpoint_gc.py → __init__.py                                 │
│   code_analyzer_runner.py → __init__.py                          │
│   code_simulator.py → __init__.py                                │
│   code_archaeology.py → __init__.py                              │
│   clock_guard.py → __init__.py                                   │
│   coldstart_manager.py → __init__.py                             │
│   command_chain_length_gate.py → __init__.py                     │
│   commit_quality_gate.py → __init__.py                           │
│   complexity_budget.py → __init__.py                             │
│   config.py → __init__.py                                        │
│   consequence_tracker.py → __init__.py                           │
│   compositional_safety_test... → __init__.py                     │
│   confidence_quantifier.py → __init__.py                         │
│   confidence_estimator.py → __init__.py                          │
│   compliance_mapper.py → __init__.py                             │
│   config_scanner.py → __init__.py                                │
│   ...还有 748 条 / 748 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[import_depends]** (730 条 / edges) — 已达显示上限，省略 / limit reached

**[test_depends]** (489 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (52 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (44 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (30 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (14 条 / edges) — 已达显示上限，省略 / limit reached

**[invoke]** (1 条 / edges) — 已达显示上限，省略 / limit reached

**[import]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 2158 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `25_d_governance_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
