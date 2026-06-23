---
doc_type: domain_architecture_doc
title: D-GOV_RULE 规则治理架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-GOV_RULE 规则治理架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-GOV_RULE |
| 域名称 | 规则治理 |
| 架构层 | L2_domain |
| 模块总数 | 175 |
| 设计态模块 | 0 |
| 原型态模块 | 0 |
| 生产态模块 | 175 |
| 容量 | 175/200 (正常) |
| 描述 | 规则执行、注册表管理、策略同步、标准定义。从 D-GOVERNANCE 拆分。 |

## 模块清单

共 175 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| config/alert_rules.yaml | MOD-GOVERNANCE | orphan | production | 0 | 0 |
| config/budget_policy.yaml | MOD-INF-024 | orphan | production | 0 | 0 |
| config/capacity/ai_context_policy.yaml | MOD_INF_001 | orphan | production | 0 | 0 |
| config/capacity/sandbox_policy.yaml | MOD_INF_001 | orphan | production | 0 | 0 |
| config/compression/policy.yaml | GOV-DOC-011 | orphan | production | 0 | 0 |
| config/context_rules.yaml | MOD-INF-002 | orphan | production | 0 | 0 |
| config/context_rules_v1.yaml | MOD-INF-002 | orphan | production | 0 | 0 |
| config/data/survivorship_policy.yaml | MOD_INF_016 | orphan | production | 0 | 0 |
| config/embedding_model_registry.yaml | MOD-INF-002 | orphan | production | 0 | 0 |
| config/feature_activation_policy.yaml | MOD-INF-002 | orphan | production | 0 | 0 |
| config/sli_registry.yaml | MOD-GOVERNANCE | orphan | production | 0 | 0 |
| data/asset_index/archive/migration_registry.yaml | MOD-GOVERNANCE | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/ai_risk_register.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/ai_session_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/business_streams.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...licies_and_standards/_registry/catalogs/cross_module_dependency_registry.yaml | PS-REG-007 | orphan | production | 0 | 0 |
| ...s_and_standards/_registry/catalogs/declarative_contract_tracker_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...licies_and_standards/_registry/catalogs/document_metadata_index_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| .../01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml | PS-REG-012 | orphan | production | 0 | 0 |
| .../01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/hard_boundaries.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| .../01_policies_and_standards/_registry/catalogs/knowledge_article_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...cies_and_standards/_registry/catalogs/master_document_inventory_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/project_path_tree.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/registry_of_registries.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/catalogs/task_card_meta_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/contracts/architecture_contract.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/contracts/contract_mapping_table.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| .../01_policies_and_standards/_registry/contracts/model_capability_contract.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/schemas/frontmatter_schema.json | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/schemas/index.md | GOV-006 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/schemas/session_log_schema.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...nd_standards/_registry/vocabularies/ai_autonomy_level_planned_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| .../01_policies_and_standards/_registry/vocabularies/ai_autonomy_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...icies_and_standards/_registry/vocabularies/ai_capability_slot_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...es_and_standards/_registry/vocabularies/blueprint_refs_status_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/category_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ..._policies_and_standards/_registry/vocabularies/classification_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/created_by_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...nd_standards/_registry/vocabularies/derived_from_relationship_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/doc_type_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/domain_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...olicies_and_standards/_registry/vocabularies/evolution_policy_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...licies_and_standards/_registry/vocabularies/governance_family_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/language_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/layer_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...1_policies_and_standards/_registry/vocabularies/review_status_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/rule_form_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...01_policies_and_standards/_registry/vocabularies/safety_level_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/scope_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/stability_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/status_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...1_policies_and_standards/_registry/vocabularies/verifiability_vocabulary.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/_index.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_002_anti_orphan_search_first.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_003_task_granularity_threshold.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_004_parallel_atomic_transaction.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_005_modification_governance.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_006_anti_hallucination_structure.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_007_anti_hallucination_behavior.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_008_anti_hallucination_output.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_009_anti_hallucination_safety.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_011_code_type_import.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_012_code_test_security.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_013_arch_cross_package_dep.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_017_arch_governance_order.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_018_behavior_code_prohibition.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_019_behavior_security_prohibition.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| ...01_policies_and_standards/rules/trae_020_behavior_governance_prohibition.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_021_behavior_other_prohibition.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_022_behavior_conditional_code.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| ...01_policies_and_standards/rules/trae_023_behavior_conditional_governance.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_025_methodology_decision.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_026_methodology_quality.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_027_methodology_collaboration.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_031_security_key_access.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_032_module_lifecycle.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_033_module_registration_sync.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_036_arch_gate_transition.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_037_arch_qualification_versioning.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_038_arch_ctr_injection.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_040_ai_model_routing.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_041_meta_rule_classification.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_042_meta_rule_standard.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_043_meta_rule_metadata.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_045_data_quality_lineage.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_046_engineering_code_restructure.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_048_ops_vibe_coding_session.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_049_ops_domain_manual.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_050_domain_policy_data_factor.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_051_domain_policy_risk_backtest.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| .../01_policies_and_standards/rules/trae_052_cross_blueprint_change_cleanup.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/02_enterprise_architecture/migration_registry.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| ...cture/target_architecture/architecture_model/contracts/consumer_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| ...e_architecture/target_architecture/architecture_model/module_id_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/03_modules/_domain_infra_ops/a2a_protocol/arbitration_rules.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/03_modules/blueprint_registry.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/03_modules/module_registry.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/03_modules/system_pathway_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/03_modules/template_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| scripts/governance/meta/trust_tier_policy.yaml | MOD-INF-005 | orphan | production | 0 | 0 |
| scripts/registry_scope.yaml | MOD-INF-005 | orphan | production | 0 | 0 |
| src/zephyr/governance/constitutional_update/constitutional_update.py | SRC-025 | draft | production | 4 | 2 |
| src/zephyr/governance/rule_enforcement/__init__.py | MOD-INF-007 | draft | production | 3 | 11 |
| src/zephyr/governance/rule_enforcement/_registry.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/_template.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/adaptive_threshold.py | MOD-INF-007 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/adversarial_strategies.py | MOD-INF-007 | draft | production | 3 | 0 |
| src/zephyr/governance/rule_enforcement/adversarial_validation.py | MOD-INF-007 | draft | production | 5 | 0 |
| src/zephyr/governance/rule_enforcement/ai_capability_guard.py | MOD-INF-007 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/anti_pattern_guard.py | MOD-INF-007 | draft | production | 1 | 0 |
| src/zephyr/governance/rule_enforcement/can_i_deploy.py | MOD-INF-007 | draft | production | 1 | 0 |
| src/zephyr/governance/rule_enforcement/capability_checker.py | MOD-INF-007 | draft | production | 2 | 2 |
| src/zephyr/governance/rule_enforcement/cbac_matrix.py | MOD-INF-007 | draft | production | 3 | 0 |
| src/zephyr/governance/rule_enforcement/cdc_broker.py | MOD-INF-007 | draft | production | 1 | 0 |
| src/zephyr/governance/rule_enforcement/check_types/check_type_registry.py | MOD-INF-007 | draft | production | 69 | 2 |
| src/zephyr/governance/rule_enforcement/circuit_breaker.py | MOD-INF-007 | draft | production | 8 | 2 |
| src/zephyr/governance/rule_enforcement/contract_template_manager.py | MOD-INF-007 | draft | production | 2 | 1 |
| src/zephyr/governance/rule_enforcement/end_to_end_walkthrough.py | MOD-INF-007 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/g1_ingest.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g2_triage.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g3_evaluate.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g4_activate.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g5_extract.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g6_path_tree_freshness.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g7_position_limits.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g8.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g8_leverage.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g9.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g9_strategy_correlation.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/g_asset_inventory.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/gate_context.py | MOD-INF-007 | draft | production | 8 | 0 |
| src/zephyr/governance/rule_enforcement/gate_dedup.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/gate_engine.py | MOD-INF-007 | draft | production | 29 | 18 |
| src/zephyr/governance/rule_enforcement/gate_override.py | MOD-INF-007 | draft | production | 2 | 1 |
| src/zephyr/governance/rule_enforcement/gate_pipeline.py | MOD-INF-007 | draft | production | 3 | 1 |
| src/zephyr/governance/rule_enforcement/gate_simulator.py | MOD-INF-007 | draft | production | 2 | 2 |
| src/zephyr/governance/rule_enforcement/gate_types.py | MOD-INF-007 | draft | production | 8 | 1 |
| src/zephyr/governance/rule_enforcement/gct_024_budget_enforcer.yaml | MOD-GOV-ENFORCEMENT | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/integration_test_runner.py | MOD-INF-007 | draft | production | 3 | 0 |
| src/zephyr/governance/rule_enforcement/invariants/en_001_circular_dependency.py | MOD-INF-007 | draft | production | 3 | 0 |
| ...zephyr/governance/rule_enforcement/invariants/en_001_circular_dependency.yaml | MOD-GOV-ENFORCEMENT | draft | production | 0 | 1 |
| ...ephyr/governance/rule_enforcement/invariants/en_003_contract_compatibility.py | MOD-INF-007 | draft | production | 3 | 1 |
| ...hyr/governance/rule_enforcement/invariants/en_003_contract_compatibility.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| ...zephyr/governance/rule_enforcement/invariants/en_process_lifecycle_gateway.py | MOD-INF-016 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/invariants/zero_residue_check.py | MOD-INF-007 | draft | production | 4 | 0 |
| src/zephyr/governance/rule_enforcement/kiss_enforcer.py | MOD-INF-007 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/observability_baseline.yaml | MOD-GOV-ENFORCEMENT | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/risk_ssot.py | MOD-INF-007 | draft | production | 5 | 0 |
| src/zephyr/governance/rule_enforcement/secrets_guard.py | MOD-INF-007 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/task/g0_entry.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/task/g0_orc_gate_engine.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/task/g7_orc_gate_engine.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/task_completion_gate.py | MOD-INF-007 | draft | production | 3 | 1 |
| src/zephyr/governance/rule_enforcement/task_types.py | MOD-INF-007 | draft | production | 103 | 3 |
| src/zephyr/governance/rule_enforcement/triple_alignment.py | MOD-INF-007 | draft | production | 3 | 0 |
| src/zephyr/governance/rule_enforcement/zero_residue.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_engine.py | MOD-GOV-019 | draft | production | 3 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INTEGRATION | 10 | import_depends |
| D-SHARED | 9 | import_depends |
| D-GOV_DRIFT | 4 | import_depends |
| D-GOV_AUDIT | 2 | import_depends |
| D-GOVERNANCE | 2 | import_depends,config_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 269 | import_depends,test_depends,runtime,config_depends |
| D-TRADING | 4 | contract,import_depends |
| D-SECURITY | 4 | import_depends |
| D-INTELLIGENCE | 2 | contract,import_depends |
| D-INTEGRATION | 2 | import_depends |
| D-GOV_AUDIT | 1 | import_depends |
| D-AUTONOMY_CORE | 1 | import_depends |

## 域内依赖图

详见 [d_gov_rule_dependency.mmd](d_gov_rule_dependency.mmd)
