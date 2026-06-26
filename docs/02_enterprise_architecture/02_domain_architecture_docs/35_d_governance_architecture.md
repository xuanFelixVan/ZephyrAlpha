---
doc_type: architecture_view
title: D-GOVERNANCE 生命周期管理架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 35_d_governance / 生命周期管理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示生命周期管理（D-GOVERNANCE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 生命周期管理（D-GOVERNANCE）的模块分布。共 2843 个模块 / 2843 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│           L1 基础层 / Foundation Layer (2775 modules)            │
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
│   ...还有 2757 个模块 / 2757 more modules                        │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/data_governance/__init__.py  [prototype]            │
│   src/zephyr/data_governance/_extensions/__init__.py  [protot... │
│   src/zephyr/data_governance/api/__init__.py  [prototype]        │
│   src/zephyr/data_governance/core/__init__.py  [prototype]       │
│   src/zephyr/data_governance/infrastructure/__init__.py  [pro... │
│   src/zephyr/data_governance/models/__init__.py  [prototype]     │
│   src/zephyr/data_governance/services/__init__.py  [prototype]   │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (61 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   F18-governance-scripts/  [design]                              │
│   F28-asset-inventory/  [design]                                 │
│   F29-semantic-audit/  [design]                                  │
│   F3-task-system/  [design]                                      │
│   F31-registry-gov/  [design]                                    │
│   F34-code-dedup/  [design]                                      │
│   F35-file-structure/  [design]                                  │
│   F5-escalation/  [design]                                       │
│   scripts/governance/_audit_gate_registry.py  [production]       │
│   scripts/governance/_check_all_status.py  [production]          │
│   scripts/governance/_check_task.py  [production]                │
│   scripts/governance/_check_vs.py  [production]                  │
│   scripts/governance/_list_gate_ids.py  [production]             │
│   scripts/governance/_verify_gate_loading.py  [production]       │
│   scripts/governance/analyze_orphan_consumers.py  [production]   │
│   scripts/governance/check_rule_coverage.py  [production]        │
│   scripts/governance/d3_metadata/validate_rule_frontmatter.py... │
│   scripts/governance/d5_architecture/dm200912_query_domains.p... │
│   ...还有 43 个模块 / 43 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 2843 个模块 / 2843 modules）。

### L1 基础层 / Foundation Layer (2775 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 01-跨域交叉点 vs 29-D-GOVERNANCE/D-GOV-11 | §8.1 | design | planned |
| 2 | architecture_model/architecture_lock.yaml | architecture_model/architecture_lock.... | production | deprecated |
| 3 | architecture_model/index.yaml | architecture_model/index.yaml | production | deprecated |
| 4 | architecture_model/layers/b_context_engine.yaml | architecture_model/layers/b_context_e... | production | deprecated |
| 5 | architecture_model/layers/b_core.yaml | architecture_model/layers/b_core.yaml | production | deprecated |
| 6 | architecture_model/layers/b_db.yaml | architecture_model/layers/b_db.yaml | production | deprecated |
| 7 | architecture_model/layers/b_execution_model.yaml | architecture_model/layers/b_execution... | production | deprecated |
| 8 | architecture_model/layers/b_feedback_loop.yaml | architecture_model/layers/b_feedback_... | production | deprecated |
| 9 | architecture_model/layers/b_gates.yaml | architecture_model/layers/b_gates.yaml | production | deprecated |
| 10 | architecture_model/layers/b_kb.yaml | architecture_model/layers/b_kb.yaml | production | deprecated |
| 11 | architecture_model/layers/b_llm_security.yaml | architecture_model/layers/b_llm_secur... | production | deprecated |
| 12 | architecture_model/layers/b_mcp.yaml | architecture_model/layers/b_mcp.yaml | production | deprecated |
| 13 | architecture_model/layers/b_orchestrator.yaml | architecture_model/layers/b_orchestra... | production | deprecated |
| 14 | architecture_model/layers/b_pipeline.yaml | architecture_model/layers/b_pipeline.... | production | deprecated |
| 15 | architecture_model/layers/b_shared.yaml | architecture_model/layers/b_shared.yaml | production | deprecated |
| 16 | architecture_model/layers/schema.yaml | architecture_model/layers/schema.yaml | production | deprecated |
| 17 | architecture_model/scope.yaml | architecture_model/scope.yaml | production | deprecated |
| 18 | architecture_model/technology_landscape.yaml | architecture_model/technology_landsca... | production | deprecated |
| 19 | config/ai_capability_matrix.yaml | config/ai_capability_matrix.yaml | production | deprecated |
| 20 | config/blueprint_routing.yaml | config/blueprint_routing.yaml | production | deprecated |
| 21 | config/capabilities.yaml | config/capabilities.yaml | production | deprecated |
| 22 | config/capacity/asset_inventory.yaml | config/capacity/asset_inventory.yaml | production | deprecated |
| 23 | config/capacity/capacity_slo.yaml | config/capacity/capacity_slo.yaml | production | deprecated |
| 24 | config/capacity/degradation_chain.yaml | config/capacity/degradation_chain.yaml | production | deprecated |
| 25 | config/capacity/error_budget_config.yaml | config/capacity/error_budget_config.yaml | production | deprecated |
| 26 | config/capacity/external_watchdog.yaml | config/capacity/external_watchdog.yaml | production | deprecated |
| 27 | config/capacity/owner_offline_protocol.yaml | config/capacity/owner_offline_protoco... | production | deprecated |
| 28 | config/capacity/risk_register.yaml | config/capacity/risk_register.yaml | production | deprecated |
| 29 | config/capacity_params.yaml | config/capacity_params.yaml | production | deprecated |
| 30 | config/flags.yaml | config/flags.yaml | production | deprecated |
| 31 | config/kb_parameters.yaml | config/kb_parameters.yaml | production | deprecated |
| 32 | config/metrics_schema.yaml | config/metrics_schema.yaml | production | deprecated |
| 33 | config/model_pricing.yaml | config/model_pricing.yaml | production | deprecated |
| 34 | config/nav_table_mapping.yaml | config/nav_table_mapping.yaml | production | deprecated |
| 35 | config/rbac_roles.yaml | config/rbac_roles.yaml | production | deprecated |
| 36 | config/resource_optimization.yaml | config/resource_optimization.yaml | production | deprecated |
| 37 | config/risk_params.yaml | config/risk_params.yaml | production | deprecated |
| 38 | config/runtime/burn_rate_acceleration.yaml | config/runtime/burn_rate_acceleration... | production | deprecated |
| 39 | config/runtime/error_budget_state.yaml | config/runtime/error_budget_state.yaml | production | deprecated |
| 40 | config/runtime/script_retirement_state.yaml | config/runtime/script_retirement_stat... | production | deprecated |
| 41 | config/runtime/shadow_mode_state.yaml | config/runtime/shadow_mode_state.yaml | production | deprecated |
| 42 | config/session_state_machine.yaml | config/session_state_machine.yaml | production | deprecated |
| 43 | config/skill_cbac_mapping.yaml | config/skill_cbac_mapping.yaml | production | deprecated |
| 44 | config/trigger_router.yaml | config/trigger_router.yaml | production | deprecated |
| 45 | data/asset_index/archive/migration_scripts/_migration_sha... | data/asset_index/archive/migration_sc... | prototype | generated |
| 46 | data/asset_index/archive/migration_scripts/_verify_manife... | data/asset_index/archive/migration_sc... | prototype | generated |
| 47 | data/asset_index/archive/migration_scripts/_verify_step4.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 48 | data/asset_index/archive/migration_scripts/apply_rulings.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 49 | data/asset_index/archive/migration_scripts/check_coverage.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 50 | data/asset_index/archive/migration_scripts/comprehensive_... | data/asset_index/archive/migration_sc... | prototype | generated |
| 51 | data/asset_index/archive/migration_scripts/create_target_... | data/asset_index/archive/migration_sc... | prototype | generated |
| 52 | data/asset_index/archive/migration_scripts/cross_domain_i... | data/asset_index/archive/migration_sc... | prototype | generated |
| 53 | data/asset_index/archive/migration_scripts/domain_prefix_... | data/asset_index/archive/migration_sc... | prototype | generated |
| 54 | data/asset_index/archive/migration_scripts/execute_move.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 55 | data/asset_index/archive/migration_scripts/generate_migra... | data/asset_index/archive/migration_sc... | prototype | generated |
| 56 | data/asset_index/archive/migration_scripts/generate_path_... | data/asset_index/archive/migration_sc... | prototype | generated |
| 57 | data/asset_index/archive/migration_scripts/inject_domain_... | data/asset_index/archive/migration_sc... | prototype | generated |
| 58 | data/asset_index/archive/migration_scripts/lock_batch.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 59 | data/asset_index/archive/migration_scripts/preflight_chec... | data/asset_index/archive/migration_sc... | prototype | generated |
| 60 | data/asset_index/archive/migration_scripts/rollback_batch.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 61 | data/asset_index/archive/migration_scripts/scan_import_im... | data/asset_index/archive/migration_sc... | prototype | generated |
| 62 | data/asset_index/archive/migration_scripts/shared_import_... | data/asset_index/archive/migration_sc... | prototype | generated |
| 63 | data/asset_index/archive/migration_scripts/test_import_fi... | data/asset_index/archive/migration_sc... | prototype | generated |
| 64 | data/asset_index/archive/migration_scripts/unnest_from_mc... | data/asset_index/archive/migration_sc... | prototype | generated |
| 65 | data/asset_index/archive/migration_scripts/update_imports.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 66 | data/asset_index/archive/migration_scripts/update_non_imp... | data/asset_index/archive/migration_sc... | prototype | generated |
| 67 | data/asset_index/archive/migration_scripts/verify_batch.py | data/asset_index/archive/migration_sc... | prototype | generated |
| 68 | docs/03_modules/_alpha_signal_domain/blueprint.md | docs__03_modules___alpha_signal_domai... | design | planned |
| 69 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | docs__03_modules___cross_layer__agent... | design | planned |
| 70 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | docs__03_modules___cross_layer__auto_... | design | planned |
| 71 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | docs__03_modules___cross_layer__auto_... | design | planned |
| 72 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | docs__03_modules___cross_layer__behav... | design | planned |
| 73 | docs/03_modules/_cross_layer/context_engine/blueprint.md | docs__03_modules___cross_layer__conte... | design | planned |
| 74 | docs/03_modules/_cross_layer/database/blueprint.md | docs__03_modules___cross_layer__datab... | design | planned |
| 75 | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | docs__03_modules___cross_layer__feedb... | design | planned |
| 76 | docs/03_modules/_cross_layer/feedback_loop/capacity_upgra... | docs__03_modules___cross_layer__feedb... | design | planned |
| 77 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | docs__03_modules___cross_layer__gate_... | design | planned |
| 78 | docs/03_modules/_cross_layer/llm_security/blueprint.md | docs__03_modules___cross_layer__llm_s... | design | planned |
| 79 | docs/03_modules/_cross_layer/mcp_servers/blueprint.md | docs__03_modules___cross_layer__mcp_s... | design | planned |
| 80 | docs/03_modules/_cross_layer/model_capability_exam/bluepr... | docs__03_modules___cross_layer__model... | design | planned |
| 81 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | docs__03_modules___cross_layer__orpha... | design | planned |
| 82 | docs/03_modules/_cross_layer/pipeline/blueprint.md | docs__03_modules___cross_layer__pipel... | design | planned |
| 83 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | docs__03_modules___cross_layer__red_b... | design | planned |
| 84 | docs/03_modules/_cross_layer/resource_optimization_engine... | docs__03_modules___cross_layer__resou... | design | planned |
| 85 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | docs__03_modules___cross_layer__seman... | design | planned |
| 86 | docs/03_modules/_cross_layer/shared_core/blueprint.md | docs__03_modules___cross_layer__share... | design | planned |
| 87 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprin... | docs__03_modules___domain_autonomy_co... | design | planned |
| 88 | docs/03_modules/_domain_autonomy_core/rollback_system/blu... | docs__03_modules___domain_autonomy_co... | design | planned |
| 89 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blu... | docs__03_modules___domain_autonomy_pe... | design | planned |
| 90 | docs/03_modules/_domain_autonomy_perm/escalation_protocol... | docs__03_modules___domain_autonomy_pe... | design | planned |
| 91 | docs/03_modules/_domain_compliance/compliance_core/bluepr... | docs__03_modules___domain_compliance_... | design | planned |
| 92 | docs/03_modules/_domain_data/datasource_core/blueprint.md | docs__03_modules___domain_data__datas... | design | planned |
| 93 | docs/03_modules/_domain_ex_core/ex_core/blueprint.md | docs__03_modules___domain_ex_core__ex... | design | planned |
| 94 | docs/03_modules/_domain_factor/alpha_factor_core/blueprin... | docs__03_modules___domain_factor__alp... | design | planned |
| 95 | docs/03_modules/_domain_frontend/hmi_core/blueprint.md | docs__03_modules___domain_frontend__h... | design | planned |
| 96 | docs/03_modules/_domain_governance/blueprint.md | docs__03_modules___domain_governance_... | design | planned |
| 97 | docs/03_modules/_domain_governance/capacity_upgrade/bluep... | docs__03_modules___domain_governance_... | design | planned |
| 98 | docs/03_modules/_domain_governance/code_dedup_engine/blue... | docs__03_modules___domain_governance_... | design | planned |
| 99 | docs/03_modules/_domain_governance/governance_automation/... | docs__03_modules___domain_governance_... | design | planned |
| 100 | docs/03_modules/_domain_governance/registry_governance/bl... | docs__03_modules___domain_governance_... | design | planned |
| 101 | docs/03_modules/_domain_infra_ops/a2a_protocol/blueprint.md | docs__03_modules___domain_infra_ops__... | design | planned |
| 102 | docs/03_modules/_domain_infra_ops/asset_inventory/bluepri... | docs__03_modules___domain_infra_ops__... | design | planned |
| 103 | docs/03_modules/_domain_infra_ops/capacity_assurance/blue... | docs__03_modules___domain_infra_ops__... | design | planned |
| 104 | docs/03_modules/_domain_infra_runtime/runtime_integration... | docs__03_modules___domain_infra_runti... | design | planned |
| 105 | docs/03_modules/_domain_infra_runtime/state_machine_engin... | docs__03_modules___domain_infra_runti... | design | planned |
| 106 | docs/03_modules/_domain_infra_runtime/task_system/bluepri... | docs__03_modules___domain_infra_runti... | design | planned |
| 107 | docs/03_modules/_domain_integration/local_model/blueprint.md | docs__03_modules___domain_integration... | design | planned |
| 108 | docs/03_modules/_domain_ml_train/ml_core/blueprint.md | docs__03_modules___domain_ml_train__m... | design | planned |
| 109 | docs/03_modules/_domain_pf_core/pf_core/blueprint.md | docs__03_modules___domain_pf_core__po... | design | planned |
| 110 | docs/03_modules/_domain_reporting/analytics_core/blueprin... | docs__03_modules___domain_reporting__... | design | planned |
| 111 | docs/03_modules/_domain_research/research_core/blueprint.md | docs__03_modules___domain_research__r... | design | planned |
| 112 | docs/03_modules/_domain_risk/risk_management_core/bluepri... | docs__03_modules___domain_risk__risk_... | design | planned |
| 113 | docs/03_modules/_domain_signal/signal_generation_core/blu... | docs__03_modules___domain_signal__sig... | design | planned |
| 114 | docs/03_modules/_domain_simulation/experiment_core/bluepr... | docs__03_modules___domain_simulation_... | design | planned |
| 115 | docs/03_modules/_master_blueprint/blueprint.md | docs__03_modules___master_blueprint__... | design | planned |
| 116 | docs/03_modules/_master_blueprint/blueprint_agent_spec.md | agent_spec_md | design | planned |
| 117 | docs/03_modules/_ml_experiment_domain/blueprint.md | docs__03_modules___ml_experiment_doma... | design | planned |
| 118 | docs/03_modules/_restructuring/blueprint.md | docs__03_modules___restructuring__blu... | design | planned |
| 119 | docs/03_modules/_sys_master/blueprint.md | docs__03_modules___sys_master__bluepr... | design | planned |
| 120 | scripts/governance/d5_architecture/__init__.py | scripts/governance/d5_architecture/__... | prototype | generated |
| 121 | scripts/governance/d5_architecture/analyzers/__init__.py | scripts/governance/d5_architecture/an... | prototype | generated |
| 122 | scripts/governance/d5_architecture/analyzers/analyze_cont... | scripts/governance/d5_architecture/an... | prototype | generated |
| 123 | scripts/governance/d5_architecture/analyzers/audit_depend... | scripts/governance/d5_architecture/an... | prototype | generated |
| 124 | scripts/governance/d5_architecture/analyzers/measure_depr... | scripts/governance/d5_architecture/an... | prototype | generated |
| 125 | scripts/governance/d5_architecture/audit_agent_spec.py | scripts/governance/d5_architecture/au... | prototype | generated |
| 126 | scripts/governance/d5_architecture/check_blueprint_code_a... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 127 | scripts/governance/d5_architecture/check_budget_health.py | scripts/governance/d5_architecture/ch... | prototype | generated |
| 128 | scripts/governance/d5_architecture/check_drift_e2e.py | scripts/governance/d5_architecture/ch... | prototype | generated |
| 129 | scripts/governance/d5_architecture/checkers/__init__.py | scripts/governance/d5_architecture/ch... | prototype | generated |
| 130 | scripts/governance/d5_architecture/checkers/check_archite... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 131 | scripts/governance/d5_architecture/checkers/check_bluepri... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 132 | scripts/governance/d5_architecture/checkers/check_bluepri... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 133 | scripts/governance/d5_architecture/checkers/check_bluepri... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 134 | scripts/governance/d5_architecture/checkers/check_bvb_com... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 135 | scripts/governance/d5_architecture/checkers/check_code_du... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 136 | scripts/governance/d5_architecture/checkers/check_contrac... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 137 | scripts/governance/d5_architecture/checkers/check_depende... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 138 | scripts/governance/d5_architecture/checkers/check_dual_tr... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 139 | scripts/governance/d5_architecture/checkers/check_g6_ctr_... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 140 | scripts/governance/d5_architecture/checkers/check_orphan_... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 141 | scripts/governance/d5_architecture/checkers/check_ssot_un... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 142 | scripts/governance/d5_architecture/checkers/check_trace_c... | scripts/governance/d5_architecture/ch... | prototype | generated |
| 143 | scripts/governance/d5_architecture/detectors/__init__.py | scripts/governance/d5_architecture/de... | prototype | generated |
| 144 | scripts/governance/d5_architecture/detectors/detect_depen... | scripts/governance/d5_architecture/de... | prototype | generated |
| 145 | scripts/governance/d5_architecture/detectors/detect_depre... | scripts/governance/d5_architecture/de... | prototype | generated |
| 146 | scripts/governance/d5_architecture/detectors/detect_dupli... | scripts/governance/d5_architecture/de... | prototype | generated |
| 147 | scripts/governance/d5_architecture/generators/__init__.py | scripts/governance/d5_architecture/ge... | prototype | generated |
| 148 | scripts/governance/d5_architecture/generators/auto_genera... | scripts/governance/d5_architecture/ge... | prototype | generated |
| 149 | scripts/governance/d5_architecture/generators/generate_co... | scripts/governance/d5_architecture/ge... | prototype | generated |
| 150 | scripts/governance/d5_architecture/generators/generate_tr... | scripts/governance/d5_architecture/ge... | prototype | generated |
| 151 | scripts/governance/d5_architecture/pre_commit_hook.ps1 | scripts/governance/d5_architecture/pr... | prototype | generated |
| 152 | scripts/governance/d5_architecture/syncers/__init__.py | scripts/governance/d5_architecture/sy... | prototype | generated |
| 153 | scripts/governance/d5_architecture/syncers/archive_ration... | scripts/governance/d5_architecture/sy... | prototype | generated |
| 154 | scripts/governance/d5_architecture/syncers/merge_readme_t... | scripts/governance/d5_architecture/sy... | prototype | generated |
| 155 | scripts/governance/d5_architecture/syncers/sync_blueprint... | scripts/governance/d5_architecture/sy... | prototype | generated |
| 156 | scripts/governance/d5_architecture/syncers/sync_registry_... | scripts/governance/d5_architecture/sy... | prototype | generated |
| 157 | scripts/governance/d5_architecture/validators/__init__.py | scripts/governance/d5_architecture/va... | prototype | generated |
| 158 | scripts/governance/d5_architecture/validators/blueprint/_... | scripts/governance/d5_architecture/va... | prototype | generated |
| 159 | scripts/governance/d5_architecture/validators/blueprint/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 160 | scripts/governance/d5_architecture/validators/blueprint/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 161 | scripts/governance/d5_architecture/validators/blueprint/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 162 | scripts/governance/d5_architecture/validators/blueprint/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 163 | scripts/governance/d5_architecture/validators/blueprint/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 164 | scripts/governance/d5_architecture/validators/lifecycle/_... | scripts/governance/d5_architecture/va... | prototype | generated |
| 165 | scripts/governance/d5_architecture/validators/lifecycle/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 166 | scripts/governance/d5_architecture/validators/lifecycle/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 167 | scripts/governance/d5_architecture/validators/lifecycle/v... | scripts/governance/d5_architecture/va... | prototype | generated |
| 168 | scripts/governance/d5_architecture/validators/session/__i... | scripts/governance/d5_architecture/va... | prototype | generated |
| 169 | scripts/governance/d5_architecture/validators/session/val... | scripts/governance/d5_architecture/va... | prototype | generated |
| 170 | scripts/governance/d5_architecture/validators/session/val... | scripts/governance/d5_architecture/va... | prototype | generated |
| 171 | scripts/governance/d5_architecture/validators/validate_ad... | scripts/governance/d5_architecture/va... | prototype | generated |
| 172 | scripts/governance/d5_architecture/validators/validate_ar... | scripts/governance/d5_architecture/va... | prototype | generated |
| 173 | scripts/governance/d5_architecture/validators/validate_ar... | scripts/governance/d5_architecture/va... | prototype | generated |
| 174 | scripts/governance/d5_architecture/validators/validate_au... | scripts/governance/d5_architecture/va... | prototype | generated |
| 175 | scripts/governance/d5_architecture/validators/validate_b_... | scripts/governance/d5_architecture/va... | prototype | generated |
| 176 | scripts/governance/d5_architecture/validators/validate_bl... | scripts/governance/d5_architecture/va... | prototype | generated |
| 177 | scripts/governance/d5_architecture/validators/validate_co... | scripts/governance/d5_architecture/va... | prototype | generated |
| 178 | scripts/governance/d5_architecture/validators/validate_cr... | scripts/governance/d5_architecture/va... | prototype | generated |
| 179 | scripts/governance/d5_architecture/validators/validate_da... | scripts/governance/d5_architecture/va... | prototype | generated |
| 180 | scripts/governance/d5_architecture/validators/validate_de... | scripts/governance/d5_architecture/va... | prototype | generated |
| 181 | scripts/governance/d5_architecture/validators/validate_de... | scripts/governance/d5_architecture/va... | prototype | generated |
| 182 | scripts/governance/d5_architecture/validators/validate_de... | scripts/governance/d5_architecture/va... | prototype | generated |
| 183 | scripts/governance/d5_architecture/validators/validate_di... | scripts/governance/d5_architecture/va... | prototype | generated |
| 184 | scripts/governance/d5_architecture/validators/validate_fi... | scripts/governance/d5_architecture/va... | prototype | generated |
| 185 | scripts/governance/d5_architecture/validators/validate_ga... | scripts/governance/d5_architecture/va... | prototype | generated |
| 186 | scripts/governance/d5_architecture/validators/validate_ha... | scripts/governance/d5_architecture/va... | prototype | generated |
| 187 | scripts/governance/d5_architecture/validators/validate_in... | scripts/governance/d5_architecture/va... | prototype | generated |
| 188 | scripts/governance/d5_architecture/validators/validate_la... | scripts/governance/d5_architecture/va... | prototype | generated |
| 189 | scripts/governance/d5_architecture/validators/validate_la... | scripts/governance/d5_architecture/va... | prototype | generated |
| 190 | scripts/governance/d5_architecture/validators/validate_lo... | scripts/governance/d5_architecture/va... | prototype | generated |
| 191 | scripts/governance/d5_architecture/validators/validate_mo... | scripts/governance/d5_architecture/va... | prototype | generated |
| 192 | scripts/governance/d5_architecture/validators/validate_ne... | scripts/governance/d5_architecture/va... | prototype | generated |
| 193 | scripts/governance/d5_architecture/validators/validate_p0... | scripts/governance/d5_architecture/va... | prototype | generated |
| 194 | scripts/governance/d5_architecture/validators/validate_ss... | scripts/governance/d5_architecture/va... | prototype | generated |
| 195 | scripts/governance/d5_architecture/validators/validate_st... | scripts/governance/d5_architecture/va... | prototype | generated |
| 196 | scripts/governance/d5_architecture/validators/validate_te... | scripts/governance/d5_architecture/va... | prototype | generated |
| 197 | scripts/governance/d5_architecture/validators/validate_th... | scripts/governance/d5_architecture/va... | prototype | generated |
| 198 | scripts/governance/d5_architecture/validators/yaml_md/__i... | scripts/governance/d5_architecture/va... | prototype | generated |
| 199 | scripts/governance/d5_architecture/validators/yaml_md/val... | scripts/governance/d5_architecture/va... | prototype | generated |
| 200 | scripts/governance/d5_architecture/validators/yaml_md/val... | scripts/governance/d5_architecture/va... | prototype | generated |

> (仅显示前 200 个模块，共 2775 个)

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/data_governance/__init__.py | src/zephyr/data_governance/__init__.py | prototype | generated |
| 2 | src/zephyr/data_governance/_extensions/__init__.py | src/zephyr/data_governance/_extension... | prototype | deprecated |
| 3 | src/zephyr/data_governance/api/__init__.py | src/zephyr/data_governance/api/__init... | prototype | deprecated |
| 4 | src/zephyr/data_governance/core/__init__.py | src/zephyr/data_governance/core/__ini... | prototype | deprecated |
| 5 | src/zephyr/data_governance/infrastructure/__init__.py | src/zephyr/data_governance/infrastruc... | prototype | deprecated |
| 6 | src/zephyr/data_governance/models/__init__.py | src/zephyr/data_governance/models/__i... | prototype | deprecated |
| 7 | src/zephyr/data_governance/services/__init__.py | src/zephyr/data_governance/services/_... | prototype | deprecated |

### 未分类 / Unclassified (61 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F18-governance-scripts/ | F18-governance-scripts/ | design | stable |
| 2 | F28-asset-inventory/ | F28-asset-inventory/ | design | stable |
| 3 | F29-semantic-audit/ | F29-semantic-audit/ | design | stable |
| 4 | F3-task-system/ | F3-task-system/ | design | stable |
| 5 | F31-registry-gov/ | F31-registry-gov/ | design | stable |
| 6 | F34-code-dedup/ | F34-code-dedup/ | design | planned |
| 7 | F35-file-structure/ | F35-file-structure/ | design | planned |
| 8 | F5-escalation/ | F5-escalation/ | design | stable |
| 9 | scripts/governance/_audit_gate_registry.py | scripts/governance/_audit_gate_regist... | production | generated |
| 10 | scripts/governance/_check_all_status.py | scripts/governance/_check_all_status.py | production | generated |
| 11 | scripts/governance/_check_task.py | scripts/governance/_check_task.py | production | generated |
| 12 | scripts/governance/_check_vs.py | scripts/governance/_check_vs.py | production | generated |
| 13 | scripts/governance/_list_gate_ids.py | scripts/governance/_list_gate_ids.py | production | generated |
| 14 | scripts/governance/_verify_gate_loading.py | scripts/governance/_verify_gate_loadi... | production | generated |
| 15 | scripts/governance/analyze_orphan_consumers.py | scripts/governance/analyze_orphan_con... | production | generated |
| 16 | scripts/governance/check_rule_coverage.py | scripts/governance/check_rule_coverag... | production | generated |
| 17 | scripts/governance/d3_metadata/validate_rule_frontmatter.py | scripts/governance/d3_metadata/valida... | production | generated |
| 18 | scripts/governance/d5_architecture/dm200912_query_domains.py | scripts/governance/d5_architecture/dm... | production | generated |
| 19 | scripts/governance/d5_architecture/dm200912_rewrite_views.py | scripts/governance/d5_architecture/dm... | production | generated |
| 20 | scripts/governance/d5_architecture/dm200913_rewrite_diagr... | scripts/governance/d5_architecture/dm... | production | generated |
| 21 | scripts/governance/d5_architecture/dm200916_write_direct.py | scripts/governance/d5_architecture/dm... | production | generated |
| 22 | scripts/governance/d5_architecture/generators/domain_name... | scripts/governance/d5_architecture/ge... | production | generated |
| 23 | scripts/governance/d5_architecture/generators/generate_ca... | scripts/governance/d5_architecture/ge... | production | generated |
| 24 | scripts/governance/d5_architecture/generators/generate_ca... | scripts/governance/d5_architecture/ge... | production | generated |
| 25 | scripts/governance/d5_architecture/generators/generate_co... | scripts/governance/d5_architecture/ge... | production | generated |
| 26 | scripts/governance/d5_architecture/generators/generate_cr... | scripts/governance/d5_architecture/ge... | production | generated |
| 27 | scripts/governance/d5_architecture/generators/generate_de... | scripts/governance/d5_architecture/ge... | production | generated |
| 28 | scripts/governance/d5_architecture/generators/generate_do... | scripts/governance/d5_architecture/ge... | production | generated |
| 29 | scripts/governance/d5_architecture/generators/generate_do... | scripts/governance/d5_architecture/ge... | production | generated |
| 30 | scripts/governance/d5_architecture/generators/generate_do... | scripts/governance/d5_architecture/ge... | production | generated |
| 31 | scripts/governance/d5_architecture/generators/generate_do... | scripts/governance/d5_architecture/ge... | production | generated |
| 32 | scripts/governance/d5_architecture/generators/generate_in... | scripts/governance/d5_architecture/ge... | production | generated |
| 33 | scripts/governance/d5_architecture/generators/generate_na... | scripts/governance/d5_architecture/ge... | production | generated |
| 34 | scripts/governance/d5_architecture/generators/generate_pa... | scripts/governance/d5_architecture/ge... | production | generated |
| 35 | scripts/governance/d5_architecture/generators/generate_ru... | scripts/governance/d5_architecture/ge... | production | generated |
| 36 | scripts/governance/d7_code/fix_n06_scope.py | scripts/governance/d7_code/fix_n06_sc... | production | generated |
| 37 | scripts/governance/d7_code/fix_n12_ke_naming.py | scripts/governance/d7_code/fix_n12_ke... | production | generated |
| 38 | scripts/governance/d7_code/fix_n13_snake_case.py | scripts/governance/d7_code/fix_n13_sn... | production | generated |
| 39 | scripts/governance/d7_code/fix_n14_init_all.py | scripts/governance/d7_code/fix_n14_in... | production | generated |
| 40 | scripts/governance/d7_code/fix_n15_blueprint_path.py | scripts/governance/d7_code/fix_n15_bl... | production | generated |
| 41 | scripts/governance/d7_code/fix_naming_manual.py | scripts/governance/d7_code/fix_naming... | production | generated |
| 42 | scripts/governance/group_orphan_modules.py | scripts/governance/group_orphan_modul... | production | generated |
| 43 | scripts/governance/iterative_cleanup_imports.py | scripts/governance/iterative_cleanup_... | production | generated |
| 44 | scripts/governance/perf_depgraph_baseline.py | scripts/governance/perf_depgraph_base... | production | generated |
| 45 | scripts/governance/register_orphan_modules.py | scripts/governance/register_orphan_mo... | production | generated |
| 46 | scripts/governance/rename_whitelist_cleanup.py | scripts/governance/rename_whitelist_c... | production | generated |
| 47 | scripts/governance/repair/concurrent_write_test.py | scripts/governance/repair/concurrent_... | production | generated |
| 48 | scripts/governance/task_show.py | scripts/governance/task_show.py | production | generated |
| 49 | scripts/governance/verify_key_imports.py | scripts/governance/verify_key_imports.py | production | generated |
| 50 | scripts/record_session_start_commit.py | scripts/record_session_start_commit.py | production | generated |
| 51 | src/zephyr/governance/auto_runner.py | src/zephyr/governance/auto_runner.py | production | generated |
| 52 | src/zephyr/governance/behavioral_auditor/__init__.py | src/zephyr/governance/behavioral_audi... | production | generated |
| 53 | src/zephyr/governance/budget_enforcement.py | src/zephyr/governance/budget_enforcem... | production | generated |
| 54 | src/zephyr/governance/escalation/__init__.py | src/zephyr/governance/escalation/__in... | production | generated |
| 55 | src/zephyr/governance/f5_boot_integration.py | src/zephyr/governance/f5_boot_integra... | production | generated |
| 56 | src/zephyr/governance/f5_event_subscriber.py | src/zephyr/governance/f5_event_subscr... | production | generated |
| 57 | src/zephyr/governance/f5_shutdown_manager.py | src/zephyr/governance/f5_shutdown_man... | production | generated |
| 58 | src/zephyr/governance/rule_enforcement/invariants/post_do... | src/zephyr/governance/rule_enforcemen... | production | generated |
| 59 | src/zephyr/governance/rule_enforcement/phase_executor.py | src/zephyr/governance/rule_enforcemen... | production | generated |
| 60 | src/zephyr/governance/semantic_audit/orchestrator.py | src/zephyr/governance/semantic_audit/... | production | generated |
| 61 | tests/governance/test_database_service.py | tests/governance/test_database_servic... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 1183 条 / 1183 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│     依赖关系图 / Dependency Graph (共 1183 条 / 1183 edges)      │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [test_depends]: 481 条 / edges                                 │
│   [config_depends]: 438 条 / edges                               │
│   [import_depends]: 230 条 / edges                               │
│   [runtime]: 19 条 / edges                                       │
│   [data]: 8 条 / edges                                           │
│   [contract]: 7 条 / edges                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [test_depends] (481 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   conftest.py → sqlite_schema.py                                 │
│   test_a2a_failure.py → __init__.py                              │
│   test_a2a_layer1_discovery.py → __init__.py                     │
│   test_account_isolator.py → __init__.py                         │
│   test_action_history.py → __init__.py                           │
│   test_adversarial_tester.py → __init__.py                       │
│   test_agent_debate.py → agent_debate.py                         │
│   test_agent_cooldown.py → __init__.py                           │
│   test_agent_dispatch.py → agent_dispatch.py                     │
│   test_alerts_bridge.py → __init__.py                            │
│   test_alerts.py → __init__.py                                   │
│   test_alternative_path_blo... → __init__.py                     │
│   test_annotations.py → __init__.py                              │
│   test_anti_automation_bias.py → __init__.py                     │
│   test_api_lifecycle.py → api_lifecycle.py                       │
│   test_approval.py → __init__.py                                 │
│   test_api_response_sanitiz... → __init__.py                     │
│   test_arbitrage_asymmetry_... → __init__.py                     │
│   test_atomic_fixer.py → __init__.py                             │
│   test_ast_comparator.py → __init__.py                           │
│   test_auditor.py → __init__.py                                  │
│   test_audit_write_failure_... → __init__.py                     │
│   test_autonomy_dashboard.py → __init__.py                       │
│   test_autopilot.py → task_repo.py                               │
│   test_autonomy_regressor.py → __init__.py                       │
│   test_auto_fixer.py → __init__.py                               │
│   test_auto_test_generator.py → __init__.py                      │
│   test_auto_split.py → task_repo.py                              │
│   test_bandwidth_optimizer.py → __init__.py                      │
│   test_bare_repo_scanner.py → __init__.py                        │
│   test_backtest_engine.py → __init__.py                          │
│   test_behavioral_sampler.py → __init__.py                       │
│   test_behavioral_trust_che... → __init__.py                     │
│   test_blueprint_code_consi... → __init__.py                     │
│   test_blueprint_bloat_moni... → __init__.py                     │
│   test_blueprint_reconciler.py → __init__.py                     │
│   test_bootstrapping_calibr... → __init__.py                     │
│   test_boot_hooks_unlock.py → task_repo.py                       │
│   test_budget_enforcer_rbac... → __init__.py                     │
│   test_broker_resilience.py → __init__.py                        │
│   test_budget_models.py → __init__.py                            │
│   test_budget_handler.py → __init__.py                           │
│   test_budget_tracker.py → __init__.py                           │
│   test_budget_profile_manag... → __init__.py                     │
│   test_bus_factor_defense.py → __init__.py                       │
│   test_burn_rate_monitor.py → __init__.py                        │
│   test_canary_register.py → __init__.py                          │
│   test_cache_manager.py → __init__.py                            │
│   test_checkpoint_gc.py → __init__.py                            │
│   ...还有 432 条 / 432 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (438 条 / edges) — 已达显示上限，省略 / limit reached

**[import_depends]** (230 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (19 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (8 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (7 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 1183 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `35_d_governance_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
