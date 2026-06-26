---
doc_type: architecture_view
title: D-GOV_SCRIPTS code_dedup架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 39_d_gov_scripts / code_dedup 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示code_dedup（D-GOV_SCRIPTS）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 03:08:24
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 code_dedup（D-GOV_SCRIPTS）的模块分布。共 413 个模块 / 413 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (413 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   scripts/__init__.py  [prototype]                               │
│   scripts/_archive/construction/create_db_alignment_tasks.py ... │
│   scripts/_archive/construction/create_dm_phase9_tasks.py  [p... │
│   scripts/_archive/construction/dm014_orphan_edge_repair.py  ... │
│   scripts/_archive/governance/create_depgraph_task_cards.py  ... │
│   scripts/_archive/governance/d3_metadata/assign_module_id.py... │
│   scripts/_archive/governance/d3_metadata/check_frontmatter_m... │
│   scripts/_archive/governance/d3_metadata/check_template_comp... │
│   scripts/_archive/governance/d3_metadata/detect_deprecated_o... │
│   scripts/_archive/governance/d3_metadata/detect_skip_active_... │
│   scripts/_archive/governance/d3_metadata/detect_stale_versio... │
│   scripts/_archive/governance/d3_metadata/fix_dm411_bare_rela... │
│   scripts/_archive/governance/d3_metadata/fix_dm413_duplicate... │
│   scripts/_archive/governance/d3_metadata/fix_n06_module_id_p... │
│   scripts/_archive/governance/d3_metadata/generate_rule_catal... │
│   scripts/_archive/governance/d3_metadata/scan_deep_content.p... │
│   scripts/_archive/governance/d3_metadata/validate_blueprint_... │
│   scripts/_archive/governance/d3_metadata/validate_cross_modu... │
│   ...还有 395 个模块 / 395 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 413 个模块 / 413 modules）。

### L1 基础层 / Foundation Layer (413 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | scripts/__init__.py | scripts/__init__.py | prototype | generated |
| 2 | scripts/_archive/construction/create_db_alignment_tasks.py | scripts/_archive/construction/create_... | prototype | generated |
| 3 | scripts/_archive/construction/create_dm_phase9_tasks.py | scripts/_archive/construction/create_... | prototype | generated |
| 4 | scripts/_archive/construction/dm014_orphan_edge_repair.py | scripts/_archive/construction/dm014_o... | prototype | generated |
| 5 | scripts/_archive/governance/create_depgraph_task_cards.py | scripts/_archive/governance/create_de... | prototype | generated |
| 6 | scripts/_archive/governance/d3_metadata/assign_module_id.py | scripts/_archive/governance/d3_metada... | prototype | generated |
| 7 | scripts/_archive/governance/d3_metadata/check_frontmatter... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 8 | scripts/_archive/governance/d3_metadata/check_template_co... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 9 | scripts/_archive/governance/d3_metadata/detect_deprecated... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 10 | scripts/_archive/governance/d3_metadata/detect_skip_activ... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 11 | scripts/_archive/governance/d3_metadata/detect_stale_vers... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 12 | scripts/_archive/governance/d3_metadata/fix_dm411_bare_re... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 13 | scripts/_archive/governance/d3_metadata/fix_dm413_duplica... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 14 | scripts/_archive/governance/d3_metadata/fix_n06_module_id... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 15 | scripts/_archive/governance/d3_metadata/generate_rule_cat... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 16 | scripts/_archive/governance/d3_metadata/scan_deep_content.py | scripts/_archive/governance/d3_metada... | prototype | generated |
| 17 | scripts/_archive/governance/d3_metadata/validate_blueprin... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 18 | scripts/_archive/governance/d3_metadata/validate_cross_mo... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 19 | scripts/_archive/governance/d3_metadata/validate_derived_... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 20 | scripts/_archive/governance/d3_metadata/validate_enum_con... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 21 | scripts/_archive/governance/d3_metadata/validate_frontmat... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 22 | scripts/_archive/governance/d3_metadata/validate_no_dupli... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 23 | scripts/_archive/governance/d3_metadata/validate_ssot_sta... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 24 | scripts/_archive/governance/d3_metadata/validate_supersed... | scripts/_archive/governance/d3_metada... | prototype | generated |
| 25 | scripts/_archive/governance/dm101_blueprint_domain_mappin... | scripts/_archive/governance/dm101_blu... | prototype | generated |
| 26 | scripts/_archive/governance/merge_domain_nodes.py | scripts/_archive/governance/merge_dom... | prototype | generated |
| 27 | scripts/_archive/migration/_migration_shared.py | scripts/_archive/migration/_migration... | prototype | generated |
| 28 | scripts/_archive/migration/_verify_manifest.py | scripts/_archive/migration/_verify_ma... | prototype | generated |
| 29 | scripts/_archive/migration/_verify_step4.py | scripts/_archive/migration/_verify_st... | prototype | generated |
| 30 | scripts/_archive/migration/apply_rulings.py | scripts/_archive/migration/apply_ruli... | prototype | generated |
| 31 | scripts/_archive/migration/check_coverage.py | scripts/_archive/migration/check_cove... | prototype | generated |
| 32 | scripts/_archive/migration/comprehensive_import_fix.py | scripts/_archive/migration/comprehens... | prototype | generated |
| 33 | scripts/_archive/migration/create_target_dirs.py | scripts/_archive/migration/create_tar... | prototype | generated |
| 34 | scripts/_archive/migration/cross_domain_import_fix.py | scripts/_archive/migration/cross_doma... | prototype | generated |
| 35 | scripts/_archive/migration/domain_prefix_import_fix.py | scripts/_archive/migration/domain_pre... | prototype | generated |
| 36 | scripts/_archive/migration/execute_move.py | scripts/_archive/migration/execute_mo... | prototype | generated |
| 37 | scripts/_archive/migration/generate_migration_registry.py | scripts/_archive/migration/generate_m... | prototype | generated |
| 38 | scripts/_archive/migration/generate_path_migration_mappin... | scripts/_archive/migration/generate_p... | prototype | generated |
| 39 | scripts/_archive/migration/inject_domain_fields.py | scripts/_archive/migration/inject_dom... | prototype | generated |
| 40 | scripts/_archive/migration/lock_batch.py | scripts/_archive/migration/lock_batch.py | prototype | generated |
| 41 | scripts/_archive/migration/migrate_security_split.py | scripts/_archive/migration/migrate_se... | prototype | generated |
| 42 | scripts/_archive/migration/preflight_check.py | scripts/_archive/migration/preflight_... | prototype | generated |
| 43 | scripts/_archive/migration/rollback_batch.py | scripts/_archive/migration/rollback_b... | prototype | generated |
| 44 | scripts/_archive/migration/safe_delete_operational.py | scripts/_archive/migration/safe_delet... | prototype | generated |
| 45 | scripts/_archive/migration/scan_import_impact.py | scripts/_archive/migration/scan_impor... | prototype | generated |
| 46 | scripts/_archive/migration/shared_import_fix.py | scripts/_archive/migration/shared_imp... | prototype | generated |
| 47 | scripts/_archive/migration/test_import_fix.py | scripts/_archive/migration/test_impor... | prototype | generated |
| 48 | scripts/_archive/migration/unnest_from_mcp_server.py | scripts/_archive/migration/unnest_fro... | prototype | generated |
| 49 | scripts/_archive/migration/update_imports.py | scripts/_archive/migration/update_imp... | prototype | generated |
| 50 | scripts/_archive/migration/update_non_import_refs.py | scripts/_archive/migration/update_non... | prototype | generated |
| 51 | scripts/_archive/migration/verify_batch.py | scripts/_archive/migration/verify_bat... | prototype | generated |
| 52 | scripts/_archive/migration/verify_migration_alignment.py | scripts/_archive/migration/verify_mig... | prototype | generated |
| 53 | scripts/_archive/ops/fill_blueprint_ids.py | scripts/_archive/ops/fill_blueprint_i... | prototype | generated |
| 54 | scripts/a2a_full_verification.py | scripts/a2a_full_verification.py | prototype | generated |
| 55 | scripts/arch_guard/__init__.py | scripts/arch_guard/__init__.py | prototype | generated |
| 56 | scripts/arch_guard/_arch_ssot.py | scripts/arch_guard/_arch_ssot.py | prototype | generated |
| 57 | scripts/arch_guard/_tools/build_ocp_manifest.py | scripts/arch_guard/_tools/build_ocp_m... | prototype | generated |
| 58 | scripts/arch_guard/_tools/inject_idempotency.py | scripts/arch_guard/_tools/inject_idem... | prototype | generated |
| 59 | scripts/arch_guard/_tools/patch_p1_paths.py | scripts/arch_guard/_tools/patch_p1_pa... | prototype | generated |
| 60 | scripts/arch_guard/check_acl_boundary.py | scripts/arch_guard/check_acl_boundary.py | prototype | generated |
| 61 | scripts/arch_guard/check_cross_plane_communication.py | scripts/arch_guard/check_cross_plane_... | prototype | generated |
| 62 | scripts/arch_guard/check_fe_acl_boundary.py | scripts/arch_guard/check_fe_acl_bound... | prototype | generated |
| 63 | scripts/arch_guard/check_hot_path_purity.py | scripts/arch_guard/check_hot_path_pur... | prototype | generated |
| 64 | scripts/arch_guard/check_scaffold_exit_gates.py | scripts/arch_guard/check_scaffold_exi... | prototype | generated |
| 65 | scripts/arch_guard/check_schema_consistency.py | scripts/arch_guard/check_schema_consi... | prototype | generated |
| 66 | scripts/arch_guard/fitness_functions/__init__.py | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 67 | scripts/arch_guard/fitness_functions/check_aisg_gateway.py | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 68 | scripts/arch_guard/fitness_functions/check_audit_log_immu... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 69 | scripts/arch_guard/fitness_functions/check_bvb_compliance.py | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 70 | scripts/arch_guard/fitness_functions/check_capacity_slo_s... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 71 | scripts/arch_guard/fitness_functions/check_daily_loss_lim... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 72 | scripts/arch_guard/fitness_functions/check_hot_warm_ipc.py | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 73 | scripts/arch_guard/fitness_functions/check_idempotency_ke... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 74 | scripts/arch_guard/fitness_functions/check_kill_switch_la... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 75 | scripts/arch_guard/fitness_functions/check_log_secret_lea... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 76 | scripts/arch_guard/fitness_functions/check_no_cross_plane... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 77 | scripts/arch_guard/fitness_functions/check_ocp_signatures.py | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 78 | scripts/arch_guard/fitness_functions/check_pit_compliance.py | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 79 | scripts/arch_guard/fitness_functions/check_position_limit.py | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 80 | scripts/arch_guard/fitness_functions/check_risk_params_co... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 81 | scripts/arch_guard/fitness_functions/check_survivorship_b... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 82 | scripts/arch_guard/fitness_functions/check_warm_cold_asyn... | scripts/arch_guard/fitness_functions/... | prototype | generated |
| 83 | scripts/arch_guard/import_linter/__init__.py | scripts/arch_guard/import_linter/__in... | prototype | generated |
| 84 | scripts/arch_guard/import_linter/layer_boundary_check.py | scripts/arch_guard/import_linter/laye... | prototype | generated |
| 85 | scripts/arch_guard/run_all.py | scripts/arch_guard/run_all.py | prototype | generated |
| 86 | scripts/construction/_e2e_check.py | scripts/construction/_e2e_check.py | prototype | generated |
| 87 | scripts/construction/_e2e_deep.py | scripts/construction/_e2e_deep.py | prototype | generated |
| 88 | scripts/construction/check_statuses.py | scripts/construction/check_statuses.py | prototype | generated |
| 89 | scripts/construction/check_transition_code.py | scripts/construction/check_transition... | prototype | generated |
| 90 | scripts/construction/d_init_task_system.py | scripts/construction/d_init_task_syst... | prototype | generated |
| 91 | scripts/construction/demo_a2a_chat.py | scripts/construction/demo_a2a_chat.py | prototype | generated |
| 92 | scripts/construction/demo_a2a_coordination.py | scripts/construction/demo_a2a_coordin... | prototype | generated |
| 93 | scripts/construction/demo_e2e_pipeline.py | scripts/construction/demo_e2e_pipelin... | prototype | generated |
| 94 | scripts/construction/finalize_tasks.py | scripts/construction/finalize_tasks.py | prototype | generated |
| 95 | scripts/construction/local_layer_daemon.py | scripts/construction/local_layer_daem... | prototype | generated |
| 96 | scripts/construction/reset_test_task.py | scripts/construction/reset_test_task.py | prototype | generated |
| 97 | scripts/construction/start_brain.py | scripts/construction/start_brain.py | prototype | generated |
| 98 | scripts/construction/test_event_hook.py | scripts/construction/test_event_hook.py | prototype | generated |
| 99 | scripts/context/generate_architecture_context.py | scripts/context/generate_architecture... | prototype | deprecated |
| 100 | scripts/dm90971_add_test_headers.py | scripts/dm90971_add_test_headers.py | prototype | generated |
| 101 | scripts/fix_freeze_manifest.py | scripts/fix_freeze_manifest.py | prototype | generated |
| 102 | scripts/fix_orphan_all.py | scripts/fix_orphan_all.py | prototype | generated |
| 103 | scripts/generate_manifest.py | scripts/generate_manifest.py | prototype | generated |
| 104 | scripts/generate_pathway_registry.py | scripts/generate_pathway_registry.py | prototype | generated |
| 105 | scripts/governance/__init__.py | scripts/governance/__init__.py | prototype | generated |
| 106 | scripts/governance/_concurrency.py | scripts/governance/_concurrency.py | prototype | generated |
| 107 | scripts/governance/_e2e_verify.py | scripts/governance/_e2e_verify.py | prototype | generated |
| 108 | scripts/governance/_finding_lifecycle.py | scripts/governance/_finding_lifecycle.py | prototype | generated |
| 109 | scripts/governance/_resource_guard.py | scripts/governance/_resource_guard.py | prototype | generated |
| 110 | scripts/governance/_shared/__init__.py | scripts/governance/_shared/__init__.py | prototype | generated |
| 111 | scripts/governance/_shared/base.py | scripts/governance/_shared/base.py | prototype | generated |
| 112 | scripts/governance/_shared/constants.py | scripts/governance/_shared/constants.py | prototype | generated |
| 113 | scripts/governance/_shared/deprecated_paths.yaml | scripts/governance/_shared/deprecated... | production | deprecated |
| 114 | scripts/governance/_shared/encoding.py | scripts/governance/_shared/encoding.py | prototype | generated |
| 115 | scripts/governance/_shared/frontmatter.py | scripts/governance/_shared/frontmatte... | production | generated |
| 116 | scripts/governance/_shared/libcst_docstring_adder.py | scripts/governance/_shared/libcst_doc... | prototype | generated |
| 117 | scripts/governance/_shared/plugin_contract_schema.yaml | scripts/governance/_shared/plugin_con... | production | deprecated |
| 118 | scripts/governance/_shared/registry_entry_count.py | scripts/governance/_shared/registry_e... | prototype | generated |
| 119 | scripts/governance/_shared/thresholds.py | scripts/governance/_shared/thresholds.py | prototype | generated |
| 120 | scripts/governance/_shared/thresholds.yaml | scripts/governance/_shared/thresholds... | production | deprecated |
| 121 | scripts/governance/_shared/walk.py | scripts/governance/_shared/walk.py | prototype | generated |
| 122 | scripts/governance/_shared/yaml_utils.py | scripts/governance/_shared/yaml_utils.py | prototype | generated |
| 123 | scripts/governance/_sync/check_p0_status.py | scripts/governance/_sync/check_p0_sta... | prototype | generated |
| 124 | scripts/governance/_sync/cleanup_p0_auto_bridged.py | scripts/governance/_sync/cleanup_p0_a... | prototype | generated |
| 125 | scripts/governance/_sync/cleanup_p0_ops_pending.py | scripts/governance/_sync/cleanup_p0_o... | prototype | generated |
| 126 | scripts/governance/_sync/fix_orphan_deps.py | scripts/governance/_sync/fix_orphan_d... | prototype | generated |
| 127 | scripts/governance/_verify_fle_gates.py | scripts/governance/_verify_fle_gates.py | prototype | generated |
| 128 | scripts/governance/_verify_yaml.py | scripts/governance/_verify_yaml.py | prototype | generated |
| 129 | scripts/governance/add_file_headers.py | scripts/governance/add_file_headers.py | prototype | generated |
| 130 | scripts/governance/adversarial_log.py | scripts/governance/adversarial_log.py | prototype | generated |
| 131 | scripts/governance/adversarial_sys_master_test.py | scripts/governance/adversarial_sys_ma... | prototype | generated |
| 132 | scripts/governance/analyze_change_impact.py | scripts/governance/analyze_change_imp... | prototype | generated |
| 133 | scripts/governance/apply_depgraph.py | scripts/governance/apply_depgraph.py | prototype | generated |
| 134 | scripts/governance/audit_blueprint_alignment.py | scripts/governance/audit_blueprint_al... | prototype | generated |
| 135 | scripts/governance/audit_domain_nodes.py | scripts/governance/audit_domain_nodes.py | prototype | generated |
| 136 | scripts/governance/audit_registration.py | scripts/governance/audit_registration.py | prototype | generated |
| 137 | scripts/governance/audit_session_07.py | scripts/governance/audit_session_07.py | prototype | generated |
| 138 | scripts/governance/auto_sync_all_registries.py | scripts/governance/auto_sync_all_regi... | prototype | generated |
| 139 | scripts/governance/blind_spot_registry.py | scripts/governance/blind_spot_registr... | prototype | generated |
| 140 | scripts/governance/build_script_dep_graph.py | scripts/governance/build_script_dep_g... | prototype | generated |
| 141 | scripts/governance/changelog.py | scripts/governance/changelog.py | prototype | generated |
| 142 | scripts/governance/check_audit_rbac_isolation.py | scripts/governance/check_audit_rbac_i... | prototype | generated |
| 143 | scripts/governance/check_blueprint_compliance.py | scripts/governance/check_blueprint_co... | prototype | generated |
| 144 | scripts/governance/check_handoff_manifests.py | scripts/governance/check_handoff_mani... | prototype | generated |
| 145 | scripts/governance/check_registry_consistency.py | scripts/governance/check_registry_con... | prototype | generated |
| 146 | scripts/governance/check_rule_four_way_alignment.py | scripts/governance/check_rule_four_wa... | prototype | generated |
| 147 | scripts/governance/ci_self_check.py | scripts/governance/ci_self_check.py | prototype | generated |
| 148 | scripts/governance/construction_gate.py | scripts/governance/construction_gate.py | prototype | generated |
| 149 | scripts/governance/create_alignment_tasks.py | scripts/governance/create_alignment_t... | prototype | generated |
| 150 | scripts/governance/crosscheck_sys_master_deps.py | scripts/governance/crosscheck_sys_mas... | prototype | generated |
| 151 | scripts/governance/d10_performance/__init__.py | scripts/governance/d10_performance/__... | prototype | generated |
| 152 | scripts/governance/d10_performance/collect_system_threads.py | scripts/governance/d10_performance/co... | prototype | generated |
| 153 | scripts/governance/d11_compliance/__init__.py | scripts/governance/d11_compliance/__i... | prototype | generated |
| 154 | scripts/governance/d11_compliance/fix_shared_bypass.py | scripts/governance/d11_compliance/fix... | prototype | generated |
| 155 | scripts/governance/d11_compliance/validate_blueprint_over... | scripts/governance/d11_compliance/val... | production | generated |
| 156 | scripts/governance/d11_compliance/validate_commit_message.py | scripts/governance/d11_compliance/val... | prototype | generated |
| 157 | scripts/governance/d11_compliance/validate_exit_codes.py | scripts/governance/d11_compliance/val... | prototype | generated |
| 158 | scripts/governance/d11_compliance/validate_frozen_require... | scripts/governance/d11_compliance/val... | prototype | generated |
| 159 | scripts/governance/d11_compliance/validate_manifest_admis... | scripts/governance/d11_compliance/val... | prototype | generated |
| 160 | scripts/governance/d11_compliance/validate_no_utf8_bom.py | scripts/governance/d11_compliance/val... | prototype | generated |
| 161 | scripts/governance/d11_compliance/validate_script_naming.py | scripts/governance/d11_compliance/val... | prototype | generated |
| 162 | scripts/governance/d11_compliance/validate_script_quality.py | scripts/governance/d11_compliance/val... | prototype | generated |
| 163 | scripts/governance/d11_compliance/validate_task_decomposi... | scripts/governance/d11_compliance/val... | prototype | generated |
| 164 | scripts/governance/d11_compliance/validate_truth_source_c... | scripts/governance/d11_compliance/val... | production | generated |
| 165 | scripts/governance/d11_compliance/validate_vocabulary_cov... | scripts/governance/d11_compliance/val... | prototype | generated |
| 166 | scripts/governance/d12_ai_hallucination/__init__.py | scripts/governance/d12_ai_hallucinati... | prototype | generated |
| 167 | scripts/governance/d12_ai_hallucination/check_logger_kwar... | scripts/governance/d12_ai_hallucinati... | prototype | generated |
| 168 | scripts/governance/d12_ai_hallucination/validate_gate_pro... | scripts/governance/d12_ai_hallucinati... | prototype | generated |
| 169 | scripts/governance/d12_ai_hallucination/validate_session_... | scripts/governance/d12_ai_hallucinati... | prototype | generated |
| 170 | scripts/governance/d12_ai_hallucination/validate_session_... | scripts/governance/d12_ai_hallucinati... | prototype | generated |
| 171 | scripts/governance/d1_structure/__init__.py | scripts/governance/d1_structure/__ini... | prototype | generated |
| 172 | scripts/governance/d1_structure/archive_drafts_zone.py | scripts/governance/d1_structure/archi... | production | generated |
| 173 | scripts/governance/d1_structure/audit_config_format.py | scripts/governance/d1_structure/audit... | prototype | generated |
| 174 | scripts/governance/d1_structure/audit_directory_integrity.py | scripts/governance/d1_structure/audit... | prototype | generated |
| 175 | scripts/governance/d1_structure/audit_directory_scalabili... | scripts/governance/d1_structure/audit... | prototype | generated |
| 176 | scripts/governance/d1_structure/audit_findings_by_scope.py | scripts/governance/d1_structure/audit... | prototype | generated |
| 177 | scripts/governance/d1_structure/batch_create_index_md.py | scripts/governance/d1_structure/batch... | prototype | generated |
| 178 | scripts/governance/d1_structure/cbg_reset.py | scripts/governance/d1_structure/cbg_r... | prototype | generated |
| 179 | scripts/governance/d1_structure/check_index_integrity.py | scripts/governance/d1_structure/check... | prototype | generated |
| 180 | scripts/governance/d1_structure/detect_orphan_py.py | scripts/governance/d1_structure/detec... | prototype | generated |
| 181 | scripts/governance/d1_structure/detect_residual_files.py | scripts/governance/d1_structure/detec... | prototype | generated |
| 182 | scripts/governance/d1_structure/detect_temp_files.py | scripts/governance/d1_structure/detec... | prototype | generated |
| 183 | scripts/governance/d1_structure/drafts_zone_archiver.py | scripts/governance/d1_structure/draft... | prototype | generated |
| 184 | scripts/governance/d1_structure/generate_missing_index_md.py | scripts/governance/d1_structure/gener... | prototype | generated |
| 185 | scripts/governance/d1_structure/reset_cbg.py | scripts/governance/d1_structure/reset... | prototype | generated |
| 186 | scripts/governance/d1_structure/run_script_smoke_test.py | scripts/governance/d1_structure/run_s... | prototype | generated |
| 187 | scripts/governance/d1_structure/sync_index_from_manifest.py | scripts/governance/d1_structure/sync_... | prototype | generated |
| 188 | scripts/governance/d1_structure/sync_policies_index.py | scripts/governance/d1_structure/sync_... | prototype | generated |
| 189 | scripts/governance/d1_structure/validate_config_integrity.py | scripts/governance/d1_structure/valid... | prototype | generated |
| 190 | scripts/governance/d1_structure/validate_d1_output_sanity.py | scripts/governance/d1_structure/valid... | prototype | generated |
| 191 | scripts/governance/d1_structure/validate_immutable_core.py | scripts/governance/d1_structure/valid... | prototype | generated |
| 192 | scripts/governance/d1_structure/validate_index_reality.py | scripts/governance/d1_structure/valid... | prototype | generated |
| 193 | scripts/governance/d1_structure/validate_read_before_writ... | scripts/governance/d1_structure/valid... | prototype | generated |
| 194 | scripts/governance/d2_links/__init__.py | scripts/governance/d2_links/__init__.py | prototype | generated |
| 195 | scripts/governance/d2_links/audit_broken_links.py | scripts/governance/d2_links/audit_bro... | prototype | generated |
| 196 | scripts/governance/d2_links/detect_relative_references.py | scripts/governance/d2_links/detect_re... | prototype | generated |
| 197 | scripts/governance/d2_links/validate_depends_on_format.py | scripts/governance/d2_links/validate_... | prototype | generated |
| 198 | scripts/governance/d3_metadata/__init__.py | scripts/governance/d3_metadata/__init... | prototype | generated |
| 199 | scripts/governance/d3_metadata/check_naming_convention.py | scripts/governance/d3_metadata/check_... | prototype | generated |
| 200 | scripts/governance/d3_metadata/check_registry_consistency.py | scripts/governance/d3_metadata/check_... | prototype | generated |

> (仅显示前 200 个模块，共 413 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 315 条 / 315 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 315 条 / 315 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [config_depends]: 314 条 / edges                               │
│   [import_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [config_depends] (314 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   fix_freeze_manifest.py → __init__.py                           │
│   generate_manifest.py → __init__.py                             │
│   dm90971_add_test_headers.py → __init__.py                      │
│   generate_pathway_registry.py → __init__.py                     │
│   fix_orphan_all.py → __init__.py                                │
│   lock_files.py → __init__.py                                    │
│   check_hot_path_purity.py → __init__.py                         │
│   check_cross_plane_communi... → __init__.py                     │
│   check_scaffold_exit_gates.py → __init__.py                     │
│   check_schema_consistency.py → __init__.py                      │
│   check_acl_boundary.py → __init__.py                            │
│   check_fe_acl_boundary.py → __init__.py                         │
│   run_all.py → __init__.py                                       │
│   _arch_ssot.py → __init__.py                                    │
│   check_daily_loss_limit.py → __init__.py                        │
│   check_bvb_compliance.py → __init__.py                          │
│   check_idempotency_key.py → __init__.py                         │
│   check_audit_log_immutabil... → __init__.py                     │
│   check_aisg_gateway.py → __init__.py                            │
│   check_hot_warm_ipc.py → __init__.py                            │
│   check_capacity_slo_ssot.py → __init__.py                       │
│   check_kill_switch_latency.py → __init__.py                     │
│   check_no_cross_plane_muta... → __init__.py                     │
│   check_log_secret_leak.py → __init__.py                         │
│   check_survivorship_bias.py → __init__.py                       │
│   check_pit_compliance.py → __init__.py                          │
│   check_ocp_signatures.py → __init__.py                          │
│   check_position_limit.py → __init__.py                          │
│   check_risk_params_consist... → __init__.py                     │
│   layer_boundary_check.py → __init__.py                          │
│   check_warm_cold_async.py → __init__.py                         │
│   inject_idempotency.py → build_ocp_manifest.py                  │
│   patch_p1_paths.py → inject_idempotency.py                      │
│   demo_a2a_chat.py → check_statuses.py                           │
│   create_dm_phase9_tasks.py → check_statuses.py                  │
│   create_db_alignment_tasks.py → check_statuses.py               │
│   dm014_orphan_edge_repair.py → check_statuses.py                │
│   _e2e_check.py → check_statuses.py                              │
│   add_file_headers.py → __init__.py                              │
│   _e2e_deep.py → check_statuses.py                               │
│   adversarial_log.py → __init__.py                               │
│   apply_depgraph.py → __init__.py                                │
│   audit_domain_nodes.py → __init__.py                            │
│   audit_blueprint_alignment.py → __init__.py                     │
│   audit_session_07.py → __init__.py                              │
│   audit_registration.py → __init__.py                            │
│   blind_spot_registry.py → __init__.py                           │
│   build_script_dep_graph.py → __init__.py                        │
│   auto_sync_all_registries.py → __init__.py                      │
│   ...还有 265 条 / 265 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[import_depends]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 315 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `39_d_gov_scripts_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
