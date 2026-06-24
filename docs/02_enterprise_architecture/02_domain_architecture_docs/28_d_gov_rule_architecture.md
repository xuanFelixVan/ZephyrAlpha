---
doc_type: domain_architecture_diagram
title: D-GOV_RULE 规则治理架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 28_d_gov_rule / 规则治理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示规则治理（D-GOV_RULE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 规则治理（D-GOV_RULE）的模块分布。共 179 个模块 / 179 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (178 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   config/alert_rules.yaml  [production]                          │
│   config/budget_policy.yaml  [production]                        │
│   config/capacity/ai_context_policy.yaml  [production]           │
│   config/capacity/sandbox_policy.yaml  [production]              │
│   config/compression/policy.yaml  [production]                   │
│   config/context_rules.yaml  [production]                        │
│   config/context_rules_v1.yaml  [production]                     │
│   config/data/survivorship_policy.yaml  [production]             │
│   config/embedding_model_registry.yaml  [production]             │
│   config/feature_activation_policy.yaml  [production]            │
│   config/sli_registry.yaml  [production]                         │
│   data/asset_index/archive/migration_registry.yaml  [production] │
│   docs/01_policies_and_standards/_registry/catalogs/ai_risk_r... │
│   docs/01_policies_and_standards/_registry/catalogs/ai_sessio... │
│   docs/01_policies_and_standards/_registry/catalogs/business_... │
│   docs/01_policies_and_standards/_registry/catalogs/cross_mod... │
│   docs/01_policies_and_standards/_registry/catalogs/declarati... │
│   docs/01_policies_and_standards/_registry/catalogs/directory... │
│   ...还有 160 个模块 / 160 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (1 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   F2-gate-engine/  [design]                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 179 个模块 / 179 modules）。

### L1 基础层 / Foundation Layer (178 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | config/alert_rules.yaml | config/alert_rules.yaml | production | orphan |
| 2 | config/budget_policy.yaml | config/budget_policy.yaml | production | orphan |
| 3 | config/capacity/ai_context_policy.yaml | config/capacity/ai_context_policy.yaml | production | orphan |
| 4 | config/capacity/sandbox_policy.yaml | config/capacity/sandbox_policy.yaml | production | orphan |
| 5 | config/compression/policy.yaml | config/compression/policy.yaml | production | orphan |
| 6 | config/context_rules.yaml | config/context_rules.yaml | production | orphan |
| 7 | config/context_rules_v1.yaml | config/context_rules_v1.yaml | production | orphan |
| 8 | config/data/survivorship_policy.yaml | config/data/survivorship_policy.yaml | production | orphan |
| 9 | config/embedding_model_registry.yaml | config/embedding_model_registry.yaml | production | orphan |
| 10 | config/feature_activation_policy.yaml | config/feature_activation_policy.yaml | production | orphan |
| 11 | config/sli_registry.yaml | config/sli_registry.yaml | production | orphan |
| 12 | data/asset_index/archive/migration_registry.yaml | data/asset_index/archive/migration_re... | production | orphan |
| 13 | docs/01_policies_and_standards/_registry/catalogs/ai_risk... | docs/01_policies_and_standards/_regis... | production | orphan |
| 14 | docs/01_policies_and_standards/_registry/catalogs/ai_sess... | docs/01_policies_and_standards/_regis... | production | orphan |
| 15 | docs/01_policies_and_standards/_registry/catalogs/busines... | docs/01_policies_and_standards/_regis... | production | orphan |
| 16 | docs/01_policies_and_standards/_registry/catalogs/cross_m... | docs/01_policies_and_standards/_regis... | production | orphan |
| 17 | docs/01_policies_and_standards/_registry/catalogs/declara... | docs/01_policies_and_standards/_regis... | production | orphan |
| 18 | docs/01_policies_and_standards/_registry/catalogs/directo... | docs/01_policies_and_standards/_regis... | production | orphan |
| 19 | docs/01_policies_and_standards/_registry/catalogs/documen... | docs/01_policies_and_standards/_regis... | production | orphan |
| 20 | docs/01_policies_and_standards/_registry/catalogs/frontma... | docs/01_policies_and_standards/_regis... | production | orphan |
| 21 | docs/01_policies_and_standards/_registry/catalogs/functio... | docs/01_policies_and_standards/_regis... | production | orphan |
| 22 | docs/01_policies_and_standards/_registry/catalogs/gate_re... | docs/01_policies_and_standards/_regis... | production | orphan |
| 23 | docs/01_policies_and_standards/_registry/catalogs/hard_bo... | docs/01_policies_and_standards/_regis... | production | orphan |
| 24 | docs/01_policies_and_standards/_registry/catalogs/infrast... | docs/01_policies_and_standards/_regis... | production | orphan |
| 25 | docs/01_policies_and_standards/_registry/catalogs/knowled... | docs/01_policies_and_standards/_regis... | production | orphan |
| 26 | docs/01_policies_and_standards/_registry/catalogs/master_... | docs/01_policies_and_standards/_regis... | production | orphan |
| 27 | docs/01_policies_and_standards/_registry/catalogs/project... | docs/01_policies_and_standards/_regis... | production | orphan |
| 28 | docs/01_policies_and_standards/_registry/catalogs/registr... | docs/01_policies_and_standards/_regis... | production | orphan |
| 29 | docs/01_policies_and_standards/_registry/catalogs/registr... | docs/01_policies_and_standards/_regis... | production | orphan |
| 30 | docs/01_policies_and_standards/_registry/catalogs/rule_ca... | docs/01_policies_and_standards/_regis... | production | orphan |
| 31 | docs/01_policies_and_standards/_registry/catalogs/task_ca... | docs/01_policies_and_standards/_regis... | production | orphan |
| 32 | docs/01_policies_and_standards/_registry/contracts/archit... | docs/01_policies_and_standards/_regis... | production | orphan |
| 33 | docs/01_policies_and_standards/_registry/contracts/contra... | docs/01_policies_and_standards/_regis... | production | orphan |
| 34 | docs/01_policies_and_standards/_registry/contracts/model_... | docs/01_policies_and_standards/_regis... | production | orphan |
| 35 | docs/01_policies_and_standards/_registry/schemas/frontmat... | docs/01_policies_and_standards/_regis... | production | orphan |
| 36 | docs/01_policies_and_standards/_registry/schemas/index.md | docs/01_policies_and_standards/_regis... | production | orphan |
| 37 | docs/01_policies_and_standards/_registry/schemas/session_... | docs/01_policies_and_standards/_regis... | production | orphan |
| 38 | docs/01_policies_and_standards/_registry/vocabularies/ai_... | docs/01_policies_and_standards/_regis... | production | orphan |
| 39 | docs/01_policies_and_standards/_registry/vocabularies/ai_... | docs/01_policies_and_standards/_regis... | production | orphan |
| 40 | docs/01_policies_and_standards/_registry/vocabularies/ai_... | docs/01_policies_and_standards/_regis... | production | orphan |
| 41 | docs/01_policies_and_standards/_registry/vocabularies/blu... | docs/01_policies_and_standards/_regis... | production | orphan |
| 42 | docs/01_policies_and_standards/_registry/vocabularies/cat... | docs/01_policies_and_standards/_regis... | production | orphan |
| 43 | docs/01_policies_and_standards/_registry/vocabularies/cla... | docs/01_policies_and_standards/_regis... | production | orphan |
| 44 | docs/01_policies_and_standards/_registry/vocabularies/cre... | docs/01_policies_and_standards/_regis... | production | orphan |
| 45 | docs/01_policies_and_standards/_registry/vocabularies/der... | docs/01_policies_and_standards/_regis... | production | orphan |
| 46 | docs/01_policies_and_standards/_registry/vocabularies/doc... | docs/01_policies_and_standards/_regis... | production | orphan |
| 47 | docs/01_policies_and_standards/_registry/vocabularies/dom... | docs/01_policies_and_standards/_regis... | production | orphan |
| 48 | docs/01_policies_and_standards/_registry/vocabularies/evo... | docs/01_policies_and_standards/_regis... | production | orphan |
| 49 | docs/01_policies_and_standards/_registry/vocabularies/gov... | docs/01_policies_and_standards/_regis... | production | orphan |
| 50 | docs/01_policies_and_standards/_registry/vocabularies/lan... | docs/01_policies_and_standards/_regis... | production | orphan |
| 51 | docs/01_policies_and_standards/_registry/vocabularies/lay... | docs/01_policies_and_standards/_regis... | production | orphan |
| 52 | docs/01_policies_and_standards/_registry/vocabularies/rev... | docs/01_policies_and_standards/_regis... | production | orphan |
| 53 | docs/01_policies_and_standards/_registry/vocabularies/rul... | docs/01_policies_and_standards/_regis... | production | orphan |
| 54 | docs/01_policies_and_standards/_registry/vocabularies/saf... | docs/01_policies_and_standards/_regis... | production | orphan |
| 55 | docs/01_policies_and_standards/_registry/vocabularies/sco... | docs/01_policies_and_standards/_regis... | production | orphan |
| 56 | docs/01_policies_and_standards/_registry/vocabularies/sta... | docs/01_policies_and_standards/_regis... | production | orphan |
| 57 | docs/01_policies_and_standards/_registry/vocabularies/sta... | docs/01_policies_and_standards/_regis... | production | orphan |
| 58 | docs/01_policies_and_standards/_registry/vocabularies/ttl... | docs/01_policies_and_standards/_regis... | production | orphan |
| 59 | docs/01_policies_and_standards/_registry/vocabularies/ver... | docs/01_policies_and_standards/_regis... | production | orphan |
| 60 | docs/01_policies_and_standards/rules/_index.yaml | docs/01_policies_and_standards/rules/... | production | orphan |
| 61 | docs/01_policies_and_standards/rules/trae_001_file_operat... | docs/01_policies_and_standards/rules/... | production | orphan |
| 62 | docs/01_policies_and_standards/rules/trae_002_anti_orphan... | docs/01_policies_and_standards/rules/... | production | orphan |
| 63 | docs/01_policies_and_standards/rules/trae_003_task_granul... | docs/01_policies_and_standards/rules/... | production | orphan |
| 64 | docs/01_policies_and_standards/rules/trae_004_parallel_at... | docs/01_policies_and_standards/rules/... | production | orphan |
| 65 | docs/01_policies_and_standards/rules/trae_005_modificatio... | docs/01_policies_and_standards/rules/... | production | orphan |
| 66 | docs/01_policies_and_standards/rules/trae_006_anti_halluc... | docs/01_policies_and_standards/rules/... | production | orphan |
| 67 | docs/01_policies_and_standards/rules/trae_007_anti_halluc... | docs/01_policies_and_standards/rules/... | production | orphan |
| 68 | docs/01_policies_and_standards/rules/trae_008_anti_halluc... | docs/01_policies_and_standards/rules/... | production | orphan |
| 69 | docs/01_policies_and_standards/rules/trae_009_anti_halluc... | docs/01_policies_and_standards/rules/... | production | orphan |
| 70 | docs/01_policies_and_standards/rules/trae_010_code_naming... | docs/01_policies_and_standards/rules/... | production | orphan |
| 71 | docs/01_policies_and_standards/rules/trae_011_code_type_i... | docs/01_policies_and_standards/rules/... | production | orphan |
| 72 | docs/01_policies_and_standards/rules/trae_012_code_test_s... | docs/01_policies_and_standards/rules/... | production | orphan |
| 73 | docs/01_policies_and_standards/rules/trae_013_arch_cross_... | docs/01_policies_and_standards/rules/... | production | orphan |
| 74 | docs/01_policies_and_standards/rules/trae_014_arch_bluepr... | docs/01_policies_and_standards/rules/... | production | orphan |
| 75 | docs/01_policies_and_standards/rules/trae_015_arch_path_r... | docs/01_policies_and_standards/rules/... | production | orphan |
| 76 | docs/01_policies_and_standards/rules/trae_017_arch_govern... | docs/01_policies_and_standards/rules/... | production | orphan |
| 77 | docs/01_policies_and_standards/rules/trae_018_behavior_co... | docs/01_policies_and_standards/rules/... | production | orphan |
| 78 | docs/01_policies_and_standards/rules/trae_019_behavior_se... | docs/01_policies_and_standards/rules/... | production | orphan |
| 79 | docs/01_policies_and_standards/rules/trae_020_behavior_go... | docs/01_policies_and_standards/rules/... | production | orphan |
| 80 | docs/01_policies_and_standards/rules/trae_021_behavior_ot... | docs/01_policies_and_standards/rules/... | production | orphan |
| 81 | docs/01_policies_and_standards/rules/trae_022_behavior_co... | docs/01_policies_and_standards/rules/... | production | orphan |
| 82 | docs/01_policies_and_standards/rules/trae_023_behavior_co... | docs/01_policies_and_standards/rules/... | production | orphan |
| 83 | docs/01_policies_and_standards/rules/trae_024_methodology... | docs/01_policies_and_standards/rules/... | production | orphan |
| 84 | docs/01_policies_and_standards/rules/trae_025_methodology... | docs/01_policies_and_standards/rules/... | production | orphan |
| 85 | docs/01_policies_and_standards/rules/trae_026_methodology... | docs/01_policies_and_standards/rules/... | production | orphan |
| 86 | docs/01_policies_and_standards/rules/trae_027_methodology... | docs/01_policies_and_standards/rules/... | production | orphan |
| 87 | docs/01_policies_and_standards/rules/trae_028_doc_structu... | docs/01_policies_and_standards/rules/... | production | orphan |
| 88 | docs/01_policies_and_standards/rules/trae_029_doc_operati... | docs/01_policies_and_standards/rules/... | production | orphan |
| 89 | docs/01_policies_and_standards/rules/trae_030_doc_numberi... | docs/01_policies_and_standards/rules/... | production | orphan |
| 90 | docs/01_policies_and_standards/rules/trae_031_security_ke... | docs/01_policies_and_standards/rules/... | production | orphan |
| 91 | docs/01_policies_and_standards/rules/trae_032_module_life... | docs/01_policies_and_standards/rules/... | production | orphan |
| 92 | docs/01_policies_and_standards/rules/trae_033_module_regi... | docs/01_policies_and_standards/rules/... | production | orphan |
| 93 | docs/01_policies_and_standards/rules/trae_034_task_card_s... | docs/01_policies_and_standards/rules/... | production | orphan |
| 94 | docs/01_policies_and_standards/rules/trae_036_arch_gate_t... | docs/01_policies_and_standards/rules/... | production | orphan |
| 95 | docs/01_policies_and_standards/rules/trae_037_arch_qualif... | docs/01_policies_and_standards/rules/... | production | orphan |
| 96 | docs/01_policies_and_standards/rules/trae_038_arch_ctr_in... | docs/01_policies_and_standards/rules/... | production | orphan |
| 97 | docs/01_policies_and_standards/rules/trae_040_ai_model_ro... | docs/01_policies_and_standards/rules/... | production | orphan |
| 98 | docs/01_policies_and_standards/rules/trae_041_meta_rule_c... | docs/01_policies_and_standards/rules/... | production | orphan |
| 99 | docs/01_policies_and_standards/rules/trae_042_meta_rule_s... | docs/01_policies_and_standards/rules/... | production | orphan |
| 100 | docs/01_policies_and_standards/rules/trae_043_meta_rule_m... | docs/01_policies_and_standards/rules/... | production | orphan |
| 101 | docs/01_policies_and_standards/rules/trae_045_data_qualit... | docs/01_policies_and_standards/rules/... | production | orphan |
| 102 | docs/01_policies_and_standards/rules/trae_046_engineering... | docs/01_policies_and_standards/rules/... | production | orphan |
| 103 | docs/01_policies_and_standards/rules/trae_047_engineering... | docs/01_policies_and_standards/rules/... | production | orphan |
| 104 | docs/01_policies_and_standards/rules/trae_048_ops_vibe_co... | docs/01_policies_and_standards/rules/... | production | orphan |
| 105 | docs/01_policies_and_standards/rules/trae_049_ops_domain_... | docs/01_policies_and_standards/rules/... | production | orphan |
| 106 | docs/01_policies_and_standards/rules/trae_050_domain_poli... | docs/01_policies_and_standards/rules/... | production | orphan |
| 107 | docs/01_policies_and_standards/rules/trae_051_domain_poli... | docs/01_policies_and_standards/rules/... | production | orphan |
| 108 | docs/01_policies_and_standards/rules/trae_052_cross_bluep... | docs/01_policies_and_standards/rules/... | production | orphan |
| 109 | docs/01_policies_and_standards/rules/trae_053_automation_... | docs/01_policies_and_standards/rules/... | production | orphan |
| 110 | docs/02_enterprise_architecture/migration_registry.yaml | docs/02_enterprise_architecture/migra... | production | orphan |
| 111 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 112 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 113 | docs/03_modules/_domain_infra_ops/a2a_protocol/arbitratio... | docs/03_modules/_domain_infra_ops/a2a... | production | orphan |
| 114 | docs/03_modules/blueprint_registry.yaml | docs/03_modules/blueprint_registry.yaml | production | orphan |
| 115 | docs/03_modules/module_registry.yaml | docs/03_modules/module_registry.yaml | production | orphan |
| 116 | docs/03_modules/system_pathway_registry.yaml | docs/03_modules/system_pathway_regist... | production | orphan |
| 117 | docs/03_modules/template_registry.yaml | docs/03_modules/template_registry.yaml | production | orphan |
| 118 | scripts/governance/generators/generate_script_manifest.py | scripts/governance/generators/generat... | prototype | draft |
| 119 | scripts/governance/meta/trust_tier_policy.yaml | scripts/governance/meta/trust_tier_po... | production | orphan |
| 120 | scripts/governance/script_manifest.yaml | scripts/governance/script_manifest.yaml | production | orphan |
| 121 | scripts/registry_scope.yaml | scripts/registry_scope.yaml | production | orphan |
| 122 | scripts/script_manifest.yaml | scripts/script_manifest.yaml | production | orphan |
| 123 | src/zephyr/governance/constitutional_update/constitutiona... | src/zephyr/governance/constitutional_... | production | draft |
| 124 | src/zephyr/governance/rule_enforcement/__init__.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 125 | src/zephyr/governance/rule_enforcement/_registry.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 126 | src/zephyr/governance/rule_enforcement/_template.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 127 | src/zephyr/governance/rule_enforcement/adaptive_threshold.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 128 | src/zephyr/governance/rule_enforcement/adversarial_strate... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 129 | src/zephyr/governance/rule_enforcement/adversarial_valida... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 130 | src/zephyr/governance/rule_enforcement/ai_capability_guar... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 131 | src/zephyr/governance/rule_enforcement/anti_pattern_guard.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 132 | src/zephyr/governance/rule_enforcement/can_i_deploy.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 133 | src/zephyr/governance/rule_enforcement/capability_checker.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 134 | src/zephyr/governance/rule_enforcement/cbac_matrix.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 135 | src/zephyr/governance/rule_enforcement/cdc_broker.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 136 | src/zephyr/governance/rule_enforcement/check_types/check_... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 137 | src/zephyr/governance/rule_enforcement/circuit_breaker.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 138 | src/zephyr/governance/rule_enforcement/contract_template_... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 139 | src/zephyr/governance/rule_enforcement/end_to_end_walkthr... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 140 | src/zephyr/governance/rule_enforcement/g1_ingest.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 141 | src/zephyr/governance/rule_enforcement/g2_triage.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 142 | src/zephyr/governance/rule_enforcement/g3_evaluate.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 143 | src/zephyr/governance/rule_enforcement/g4_activate.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 144 | src/zephyr/governance/rule_enforcement/g5_extract.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 145 | src/zephyr/governance/rule_enforcement/g6_path_tree_fresh... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 146 | src/zephyr/governance/rule_enforcement/g7_position_limits... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 147 | src/zephyr/governance/rule_enforcement/g8.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 148 | src/zephyr/governance/rule_enforcement/g8_leverage.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 149 | src/zephyr/governance/rule_enforcement/g9.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 150 | src/zephyr/governance/rule_enforcement/g9_strategy_correl... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 151 | src/zephyr/governance/rule_enforcement/g_asset_inventory.... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 152 | src/zephyr/governance/rule_enforcement/gate_context.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 153 | src/zephyr/governance/rule_enforcement/gate_dedup.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 154 | src/zephyr/governance/rule_enforcement/gate_engine.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 155 | src/zephyr/governance/rule_enforcement/gate_override.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 156 | src/zephyr/governance/rule_enforcement/gate_pipeline.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 157 | src/zephyr/governance/rule_enforcement/gate_simulator.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 158 | src/zephyr/governance/rule_enforcement/gate_types.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 159 | src/zephyr/governance/rule_enforcement/gct_024_budget_enf... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 160 | src/zephyr/governance/rule_enforcement/integration_test_r... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 161 | src/zephyr/governance/rule_enforcement/invariants/en_001_... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 162 | src/zephyr/governance/rule_enforcement/invariants/en_001_... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 163 | src/zephyr/governance/rule_enforcement/invariants/en_003_... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 164 | src/zephyr/governance/rule_enforcement/invariants/en_003_... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 165 | src/zephyr/governance/rule_enforcement/invariants/en_proc... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 166 | src/zephyr/governance/rule_enforcement/invariants/zero_re... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 167 | src/zephyr/governance/rule_enforcement/kiss_enforcer.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 168 | src/zephyr/governance/rule_enforcement/observability_base... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 169 | src/zephyr/governance/rule_enforcement/risk_ssot.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 170 | src/zephyr/governance/rule_enforcement/secrets_guard.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 171 | src/zephyr/governance/rule_enforcement/task/g0_entry.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 172 | src/zephyr/governance/rule_enforcement/task/g0_orc_gate_e... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 173 | src/zephyr/governance/rule_enforcement/task/g7_orc_gate_e... | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 174 | src/zephyr/governance/rule_enforcement/task_completion_ga... | src/zephyr/governance/rule_enforcemen... | production | draft |
| 175 | src/zephyr/governance/rule_enforcement/task_types.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 176 | src/zephyr/governance/rule_enforcement/triple_alignment.py | src/zephyr/governance/rule_enforcemen... | production | draft |
| 177 | src/zephyr/governance/rule_enforcement/zero_residue.yaml | src/zephyr/governance/rule_enforcemen... | production | orphan |
| 178 | src/zephyr/governance/rule_engine.py | src/zephyr/governance/rule_engine.py | production | draft |

### 未分类 / Unclassified (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F2-gate-engine/ | F2-gate-engine/ | design | stable |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 21 条 / 21 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 21 条 / 21 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [import_depends]: 21 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (21 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   capability_checker.py → cbac_matrix.py                         │
│   gate_engine.py → circuit_breaker.py                            │
│   gate_engine.py → gate_types.py                                 │
│   gate_engine.py → risk_ssot.py                                  │
│   gate_engine.py → task_types.py                                 │
│   gate_engine.py → zero_residue_check.py                         │
│   gate_engine.py → en_003_contract_compatibi...                  │
│   gate_engine.py → en_001_circular_dependenc...                  │
│   gate_pipeline.py → gate_context.py                             │
│   gate_simulator.py → gate_context.py                            │
│   gate_simulator.py → gate_pipeline.py                           │
│   __init__.py → adaptive_threshold.py                            │
│   __init__.py → ai_capability_guard.py                           │
│   __init__.py → end_to_end_walkthrough.py                        │
│   __init__.py → gate_override.py                                 │
│   __init__.py → gate_simulator.py                                │
│   __init__.py → kiss_enforcer.py                                 │
│   __init__.py → integration_test_runner.py                       │
│   __init__.py → secrets_guard.py                                 │
│   check_type_registry.py → task_types.py                         │
│   check_type_registry.py → __init__.py                           │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `28_d_gov_rule_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
