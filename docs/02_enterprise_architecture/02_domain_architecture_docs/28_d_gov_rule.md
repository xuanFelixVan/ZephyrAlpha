---
doc_type: domain_architecture_doc
title: D-GOV_RULE 规则治理架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 28_d_gov_rule 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 28 | Number | 28 |
| 域ID | D-GOV_RULE | Domain ID | D-GOV_RULE |
| 域名称 | 规则治理 | Domain Name | 规则治理 |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 178 | Module Count | 178 |
| 域内依赖 | 21 | Internal Dependencies | 21 |
| 跨域入边 | 283 | Cross-domain Incoming | 283 |
| 跨域出边 | 29 | Cross-domain Outgoing | 29 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 1 | Prototype Modules | 1 |
| 生产态模块 | 177 | Production Modules | 177 |
| 容量 | 178/200 (正常) | Capacity | 178/200 (正常) |
| 描述 | 规则执行、注册表管理、策略同步、标准定义。从 D-GOVERNANCE 拆分。 | Description | 规则执行、注册表管理、策略同步、标准定义。从 D-GOVERNANCE 拆分。 |

## 模块清单 / Module List

共 178 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| config/alert_rules.yaml |  | production | orphan | config/alert_rules.yaml |  | production | orphan |
| config/budget_policy.yaml |  | production | orphan | config/budget_policy.yaml |  | production | orphan |
| config/capacity/ai_context_policy.yaml |  | production | orphan | config/capacity/ai_context_policy.yaml |  | production | orphan |
| config/capacity/sandbox_policy.yaml |  | production | orphan | config/capacity/sandbox_policy.yaml |  | production | orphan |
| config/compression/policy.yaml |  | production | orphan | config/compression/policy.yaml |  | production | orphan |
| config/context_rules.yaml |  | production | orphan | config/context_rules.yaml |  | production | orphan |
| config/context_rules_v1.yaml |  | production | orphan | config/context_rules_v1.yaml |  | production | orphan |
| config/data/survivorship_policy.yaml |  | production | orphan | config/data/survivorship_policy.yaml |  | production | orphan |
| config/embedding_model_registry.yaml |  | production | orphan | config/embedding_model_registry.yaml |  | production | orphan |
| config/feature_activation_policy.yaml |  | production | orphan | config/feature_activation_policy.yaml |  | production | orphan |
| config/sli_registry.yaml |  | production | orphan | config/sli_registry.yaml |  | production | orphan |
| data/asset_index/archive/migration_registry.yaml |  | production | orphan | data/asset_index/archive/migration_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/ai_risk_register.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/ai_risk_register.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/ai_session_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/ai_session_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/business_streams_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/business_streams_registry.yaml |  | production | orphan |
| ...licies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml |  | production | orphan | ...licies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml |  | production | orphan |
| ...s_and_standards/_registry/catalogs/declarative_contract_tracker_registry.yaml |  | production | orphan | ...s_and_standards/_registry/catalogs/declarative_contract_tracker_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml |  | production | orphan |
| ...licies_and_standards/_registry/catalogs/document_metadata_index_registry.yaml |  | production | orphan | ...licies_and_standards/_registry/catalogs/document_metadata_index_registry.yaml |  | production | orphan |
| .../01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml |  | production | orphan | .../01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml |  | production | orphan |
| .../01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml |  | production | orphan | .../01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/hard_boundaries_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/hard_boundaries_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml |  | production | orphan |
| .../01_policies_and_standards/_registry/catalogs/knowledge_article_registry.yaml |  | production | orphan | .../01_policies_and_standards/_registry/catalogs/knowledge_article_registry.yaml |  | production | orphan |
| ...cies_and_standards/_registry/catalogs/master_document_inventory_registry.yaml |  | production | orphan | ...cies_and_standards/_registry/catalogs/master_document_inventory_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/project_path_tree.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/project_path_tree.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/registry_of_registries.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/registry_of_registries.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/catalogs/task_card_meta_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/task_card_meta_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/contracts/contract_mapping_table.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/contracts/contract_mapping_table.yaml |  | production | orphan |
| .../01_policies_and_standards/_registry/contracts/model_capability_contract.yaml |  | production | orphan | .../01_policies_and_standards/_registry/contracts/model_capability_contract.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/schemas/frontmatter_schema.json |  | production | orphan | docs/01_policies_and_standards/_registry/schemas/frontmatter_schema.json |  | production | orphan |
| docs/01_policies_and_standards/_registry/schemas/index.md |  | production | orphan | docs/01_policies_and_standards/_registry/schemas/index.md |  | production | orphan |
| docs/01_policies_and_standards/_registry/schemas/session_log_schema.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/schemas/session_log_schema.yaml |  | production | orphan |
| ...nd_standards/_registry/vocabularies/ai_autonomy_level_planned_vocabulary.yaml |  | production | orphan | ...nd_standards/_registry/vocabularies/ai_autonomy_level_planned_vocabulary.yaml |  | production | orphan |
| .../01_policies_and_standards/_registry/vocabularies/ai_autonomy_vocabulary.yaml |  | production | orphan | .../01_policies_and_standards/_registry/vocabularies/ai_autonomy_vocabulary.yaml |  | production | orphan |
| ...icies_and_standards/_registry/vocabularies/ai_capability_slot_vocabulary.yaml |  | production | orphan | ...icies_and_standards/_registry/vocabularies/ai_capability_slot_vocabulary.yaml |  | production | orphan |
| ...es_and_standards/_registry/vocabularies/blueprint_refs_status_vocabulary.yaml |  | production | orphan | ...es_and_standards/_registry/vocabularies/blueprint_refs_status_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/category_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/category_vocabulary.yaml |  | production | orphan |
| ..._policies_and_standards/_registry/vocabularies/classification_vocabulary.yaml |  | production | orphan | ..._policies_and_standards/_registry/vocabularies/classification_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/created_by_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/created_by_vocabulary.yaml |  | production | orphan |
| ...nd_standards/_registry/vocabularies/derived_from_relationship_vocabulary.yaml |  | production | orphan | ...nd_standards/_registry/vocabularies/derived_from_relationship_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/domain_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/domain_vocabulary.yaml |  | production | orphan |
| ...olicies_and_standards/_registry/vocabularies/evolution_policy_vocabulary.yaml |  | production | orphan | ...olicies_and_standards/_registry/vocabularies/evolution_policy_vocabulary.yaml |  | production | orphan |
| ...licies_and_standards/_registry/vocabularies/governance_family_vocabulary.yaml |  | production | orphan | ...licies_and_standards/_registry/vocabularies/governance_family_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/language_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/language_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml |  | production | orphan |
| ...1_policies_and_standards/_registry/vocabularies/review_status_vocabulary.yaml |  | production | orphan | ...1_policies_and_standards/_registry/vocabularies/review_status_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/rule_form_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/rule_form_vocabulary.yaml |  | production | orphan |
| ...01_policies_and_standards/_registry/vocabularies/safety_level_vocabulary.yaml |  | production | orphan | ...01_policies_and_standards/_registry/vocabularies/safety_level_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/scope_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/scope_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/stability_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/stability_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/status_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/status_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml |  | production | orphan |
| ...1_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml |  | production | orphan | ...1_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/_index.yaml |  | production | orphan | docs/01_policies_and_standards/rules/_index.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_002_anti_orphan_search_first.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_002_anti_orphan_search_first.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_003_task_granularity_threshold.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_003_task_granularity_threshold.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_004_parallel_atomic_transaction.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_004_parallel_atomic_transaction.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_005_modification_governance.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_005_modification_governance.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_006_anti_hallucination_structure.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_006_anti_hallucination_structure.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_007_anti_hallucination_behavior.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_007_anti_hallucination_behavior.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_008_anti_hallucination_output.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_008_anti_hallucination_output.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_009_anti_hallucination_safety.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_009_anti_hallucination_safety.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_011_code_type_import.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_011_code_type_import.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_012_code_test_security.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_012_code_test_security.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_013_arch_cross_package_dep.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_013_arch_cross_package_dep.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_018_behavior_code_prohibition.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_018_behavior_code_prohibition.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_019_behavior_security_prohibition.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_019_behavior_security_prohibition.yaml |  | production | orphan |
| ...01_policies_and_standards/rules/trae_020_behavior_governance_prohibition.yaml |  | production | orphan | ...01_policies_and_standards/rules/trae_020_behavior_governance_prohibition.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_021_behavior_other_prohibition.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_021_behavior_other_prohibition.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_022_behavior_conditional_code.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_022_behavior_conditional_code.yaml |  | production | orphan |
| ...01_policies_and_standards/rules/trae_023_behavior_conditional_governance.yaml |  | production | orphan | ...01_policies_and_standards/rules/trae_023_behavior_conditional_governance.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_025_methodology_decision.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_025_methodology_decision.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_026_methodology_quality.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_026_methodology_quality.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_027_methodology_collaboration.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_027_methodology_collaboration.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_031_security_key_access.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_031_security_key_access.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_032_module_lifecycle.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_032_module_lifecycle.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_036_arch_gate_transition.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_036_arch_gate_transition.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_037_arch_qualification_versioning.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_037_arch_qualification_versioning.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_038_arch_ctr_injection.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_038_arch_ctr_injection.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_040_ai_model_routing.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_040_ai_model_routing.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_042_meta_rule_standard.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_042_meta_rule_standard.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_045_data_quality_lineage.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_045_data_quality_lineage.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_046_engineering_code_restructure.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_046_engineering_code_restructure.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_048_ops_vibe_coding_session.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_048_ops_vibe_coding_session.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_049_ops_domain_manual.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_049_ops_domain_manual.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_050_domain_policy_data_factor.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_050_domain_policy_data_factor.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_051_domain_policy_risk_backtest.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_051_domain_policy_risk_backtest.yaml |  | production | orphan |
| .../01_policies_and_standards/rules/trae_052_cross_blueprint_change_cleanup.yaml |  | production | orphan | .../01_policies_and_standards/rules/trae_052_cross_blueprint_change_cleanup.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml |  | production | orphan |
| docs/02_enterprise_architecture/migration_registry.yaml |  | production | orphan | docs/02_enterprise_architecture/migration_registry.yaml |  | production | orphan |
| ...cture/target_architecture/architecture_model/contracts/consumer_registry.yaml |  | production | orphan | ...cture/target_architecture/architecture_model/contracts/consumer_registry.yaml |  | production | orphan |
| ...e_architecture/target_architecture/architecture_model/module_id_registry.yaml |  | production | orphan | ...e_architecture/target_architecture/architecture_model/module_id_registry.yaml |  | production | orphan |
| docs/03_modules/_domain_infra_ops/a2a_protocol/arbitration_rules.yaml |  | production | orphan | docs/03_modules/_domain_infra_ops/a2a_protocol/arbitration_rules.yaml |  | production | orphan |
| docs/03_modules/blueprint_registry.yaml |  | production | orphan | docs/03_modules/blueprint_registry.yaml |  | production | orphan |
| docs/03_modules/module_registry.yaml |  | production | orphan | docs/03_modules/module_registry.yaml |  | production | orphan |
| docs/03_modules/system_pathway_registry.yaml |  | production | orphan | docs/03_modules/system_pathway_registry.yaml |  | production | orphan |
| docs/03_modules/template_registry.yaml |  | production | orphan | docs/03_modules/template_registry.yaml |  | production | orphan |
| scripts/governance/generators/generate_script_manifest.py |  | prototype | draft | scripts/governance/generators/generate_script_manifest.py |  | prototype | draft |
| scripts/governance/meta/trust_tier_policy.yaml |  | production | orphan | scripts/governance/meta/trust_tier_policy.yaml |  | production | orphan |
| scripts/governance/script_manifest.yaml |  | production | orphan | scripts/governance/script_manifest.yaml |  | production | orphan |
| scripts/registry_scope.yaml |  | production | orphan | scripts/registry_scope.yaml |  | production | orphan |
| scripts/script_manifest.yaml |  | production | orphan | scripts/script_manifest.yaml |  | production | orphan |
| src/zephyr/governance/constitutional_update/constitutional_update.py |  | production | draft | src/zephyr/governance/constitutional_update/constitutional_update.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/__init__.py |  | production | draft | src/zephyr/governance/rule_enforcement/__init__.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/_registry.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/_registry.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/_template.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/_template.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/adaptive_threshold.py |  | production | draft | src/zephyr/governance/rule_enforcement/adaptive_threshold.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/adversarial_strategies.py |  | production | draft | src/zephyr/governance/rule_enforcement/adversarial_strategies.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/adversarial_validation.py |  | production | draft | src/zephyr/governance/rule_enforcement/adversarial_validation.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/ai_capability_guard.py |  | production | draft | src/zephyr/governance/rule_enforcement/ai_capability_guard.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/anti_pattern_guard.py |  | production | draft | src/zephyr/governance/rule_enforcement/anti_pattern_guard.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/can_i_deploy.py |  | production | draft | src/zephyr/governance/rule_enforcement/can_i_deploy.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/capability_checker.py |  | production | draft | src/zephyr/governance/rule_enforcement/capability_checker.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/cbac_matrix.py |  | production | draft | src/zephyr/governance/rule_enforcement/cbac_matrix.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/cdc_broker.py |  | production | draft | src/zephyr/governance/rule_enforcement/cdc_broker.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/check_types/check_type_registry.py |  | production | draft | src/zephyr/governance/rule_enforcement/check_types/check_type_registry.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/circuit_breaker.py |  | production | draft | src/zephyr/governance/rule_enforcement/circuit_breaker.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/contract_template_manager.py |  | production | draft | src/zephyr/governance/rule_enforcement/contract_template_manager.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/end_to_end_walkthrough.py |  | production | draft | src/zephyr/governance/rule_enforcement/end_to_end_walkthrough.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/g1_ingest.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g1_ingest.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g2_triage.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g2_triage.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g3_evaluate.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g3_evaluate.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g4_activate.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g4_activate.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g5_extract.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g5_extract.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g6_path_tree_freshness.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g6_path_tree_freshness.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g7_position_limits.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g7_position_limits.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g8.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g8.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g8_leverage.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g8_leverage.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g9.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g9.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g9_strategy_correlation.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g9_strategy_correlation.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/g_asset_inventory.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/g_asset_inventory.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/gate_context.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_context.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/gate_dedup.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/gate_dedup.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/gate_engine.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_engine.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/gate_override.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_override.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/gate_pipeline.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_pipeline.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/gate_simulator.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_simulator.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/gate_types.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_types.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/gct_024_budget_enforcer.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/gct_024_budget_enforcer.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/integration_test_runner.py |  | production | draft | src/zephyr/governance/rule_enforcement/integration_test_runner.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/invariants/en_001_circular_dependency.py |  | production | draft | src/zephyr/governance/rule_enforcement/invariants/en_001_circular_dependency.py |  | production | draft |
| ...zephyr/governance/rule_enforcement/invariants/en_001_circular_dependency.yaml |  | production | draft | ...zephyr/governance/rule_enforcement/invariants/en_001_circular_dependency.yaml |  | production | draft |
| ...ephyr/governance/rule_enforcement/invariants/en_003_contract_compatibility.py |  | production | draft | ...ephyr/governance/rule_enforcement/invariants/en_003_contract_compatibility.py |  | production | draft |
| ...hyr/governance/rule_enforcement/invariants/en_003_contract_compatibility.yaml |  | production | orphan | ...hyr/governance/rule_enforcement/invariants/en_003_contract_compatibility.yaml |  | production | orphan |
| ...zephyr/governance/rule_enforcement/invariants/en_process_lifecycle_gateway.py |  | production | draft | ...zephyr/governance/rule_enforcement/invariants/en_process_lifecycle_gateway.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/invariants/zero_residue_check.py |  | production | draft | src/zephyr/governance/rule_enforcement/invariants/zero_residue_check.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/kiss_enforcer.py |  | production | draft | src/zephyr/governance/rule_enforcement/kiss_enforcer.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/observability_baseline.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/observability_baseline.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/risk_ssot.py |  | production | draft | src/zephyr/governance/rule_enforcement/risk_ssot.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/secrets_guard.py |  | production | draft | src/zephyr/governance/rule_enforcement/secrets_guard.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/task/g0_entry.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/task/g0_entry.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/task/g0_orc_gate_engine.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/task/g0_orc_gate_engine.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/task/g7_orc_gate_engine.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/task/g7_orc_gate_engine.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/task_completion_gate.py |  | production | draft | src/zephyr/governance/rule_enforcement/task_completion_gate.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/task_types.py |  | production | draft | src/zephyr/governance/rule_enforcement/task_types.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/triple_alignment.py |  | production | draft | src/zephyr/governance/rule_enforcement/triple_alignment.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/zero_residue.yaml |  | production | orphan | src/zephyr/governance/rule_enforcement/zero_residue.yaml |  | production | orphan |
| src/zephyr/governance/rule_engine.py |  | production | draft | src/zephyr/governance/rule_engine.py |  | production | draft |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_GOV_RULE["D-GOV_RULE 规则治理"]
        config_alert_rules_yaml["config/alert_rules.yaml production"]
        config_budget_policy_yaml["config/budget_policy.yaml production"]
        config_capacity_ai_context_policy_yaml["config/capacity/ai_context_policy.yaml production"]
        config_capacity_sandbox_policy_yaml["config/capacity/sandbox_policy.yaml production"]
        config_compression_policy_yaml["config/compression/policy.yaml production"]
        config_context_rules_yaml["config/context_rules.yaml production"]
        config_context_rules_v1_yaml["config/context_rules_v1.yaml production"]
        config_data_survivorship_policy_yaml["config/data/survivorship_policy.yaml production"]
        config_embedding_model_registry_yaml["config/embedding_model_registry.yaml production"]
        config_feature_activation_policy_yaml["config/feature_activation_policy.yaml production"]
        config_sli_registry_yaml["config/sli_registry.yaml production"]
        data_asset_index_archive_migration_registry_yaml["data/asset_index/archive/migration_registry.yaml production"]
        docs_01_policies_and_standards_registry_catalogs_ai_risk_register_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_ai_session_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_business_streams_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_cross_module_dependency_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_declarative_contract_tracker_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_directory_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_document_metadata_index_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_frontmatter_field_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_functional_domain_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_gate_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_hard_boundaries_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_knowledge_article_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_master_document_inventory_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_project_path_tree_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_registry_master_index_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_registry_of_registries_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_registry_catalogs_rule_catalog_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class config_alert_rules_yaml,config_budget_policy_yaml,config_capacity_ai_context_policy_yaml,config_capacity_sandbox_policy_yaml,config_compression_policy_yaml,config_context_rules_yaml,config_context_rules_v1_yaml,config_data_survivorship_policy_yaml,config_embedding_model_registry_yaml,config_feature_activation_policy_yaml,config_sli_registry_yaml,data_asset_index_archive_migration_registry_yaml,docs_01_policies_and_standards_registry_catalogs_ai_risk_register_yaml,docs_01_policies_and_standards_registry_catalogs_ai_session_registry_yaml,docs_01_policies_and_standards_registry_catalogs_business_streams_yaml,docs_01_policies_and_standards_registry_catalogs_cross_module_dependency_registry_yaml,docs_01_policies_and_standards_registry_catalogs_declarative_contract_tracker_registry_yaml,docs_01_policies_and_standards_registry_catalogs_directory_registry_yaml,docs_01_policies_and_standards_registry_catalogs_document_metadata_index_registry_yaml,docs_01_policies_and_standards_registry_catalogs_frontmatter_field_registry_yaml,docs_01_policies_and_standards_registry_catalogs_functional_domain_registry_yaml,docs_01_policies_and_standards_registry_catalogs_gate_registry_yaml,docs_01_policies_and_standards_registry_catalogs_hard_boundaries_yaml,docs_01_policies_and_standards_registry_catalogs_infrastructure_registry_yaml,docs_01_policies_and_standards_registry_catalogs_knowledge_article_registry_yaml,docs_01_policies_and_standards_registry_catalogs_master_document_inventory_registry_yaml,docs_01_policies_and_standards_registry_catalogs_project_path_tree_yaml,docs_01_policies_and_standards_registry_catalogs_registry_master_index_yaml,docs_01_policies_and_standards_registry_catalogs_registry_of_registries_yaml,docs_01_policies_and_standards_registry_catalogs_rule_catalog_registry_yaml production
```

> (依赖图最多显示前 30 个节点，共 178 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-INTEGRATION | 10 | import_depends | D-INTEGRATION | 10 | import_depends |
| D-SHARED | 9 | import_depends | D-SHARED | 9 | import_depends |
| D-GOV_DRIFT | 4 | import_depends | D-GOV_DRIFT | 4 | import_depends |
| D-GOVERNANCE | 3 | import_depends,config_depends | D-GOVERNANCE | 3 | import_depends,config_depends |
| D-GOV_AUDIT | 2 | import_depends | D-GOV_AUDIT | 2 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends | D-BEHAVIORAL_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 264 | import_depends,test_depends,runtime,config_depends | D-GOVERNANCE | 264 | import_depends,test_depends,runtime,config_depends |
| D-GOV_AUDIT | 5 | runtime,import_depends,test_depends | D-GOV_AUDIT | 5 | runtime,import_depends,test_depends |
| D-TRADING | 4 | contract,import_depends | D-TRADING | 4 | contract,import_depends |
| D-SECURITY | 4 | import_depends | D-SECURITY | 4 | import_depends |
| D-INTELLIGENCE | 2 | contract,import_depends | D-INTELLIGENCE | 2 | contract,import_depends |
| D-INTEGRATION | 2 | import_depends | D-INTEGRATION | 2 | import_depends |
| D-GOV_DRIFT | 1 | runtime | D-GOV_DRIFT | 1 | runtime |
| D-AUTONOMY_CORE | 1 | import_depends | D-AUTONOMY_CORE | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
