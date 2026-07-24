# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-07-25 00:14:55
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=683 / dataflow=89 / decision=802 / blueprint=78
- 问题总数: 258
  - 孤儿（仅一图）: 236
  - 状态漂移（blueprint 缺 design_maturity）: 4
  - 域不一致（domain_id 不一致）: 0
  - 设计态孤立（design 仅一图）: 18

## 1. 孤儿节点（仅一图存在）

| module_id | graph | entity_name |
|---|---|---|
| MOD-GOV-HEARTBEAT | dataflow | MOD-GOV-HEARTBEAT |
| MOD-GOV-blueprint_status_transition_reconciler | dataflow | MOD-GOV-blueprint_status_transition_reconciler |
| MOD-GOV-cross_layer_contract_signature_reconciler | dataflow | MOD-GOV-cross_layer_contract_signature_reconciler |
| MOD-GOV-depgraph_pre_registration_gate | dataflow | MOD-GOV-depgraph_pre_registration_gate |
| MOD-GOV-derivation_annotation_gate | dataflow | MOD-GOV-derivation_annotation_gate |
| MOD-GOV-folder_capacity_hard_limit_gate | dataflow | MOD-GOV-folder_capacity_hard_limit_gate |
| MOD-GOV-heartbeat_daemon | dataflow | MOD-GOV-heartbeat_daemon |
| MOD-GOV-relative_path_literal_gate | dataflow | MOD-GOV-relative_path_literal_gate |
| MOD-GOV-runtime_violation_snapshot | dataflow | MOD-GOV-runtime_violation_snapshot |
| MOD-GOV-runtime_violation_snapshot_reconciler | dataflow | MOD-GOV-runtime_violation_snapshot_reconciler |
| MOD-GOV-stash_accumulation_gate | dataflow | MOD-GOV-stash_accumulation_gate |
| MOD-GOV-worktree_lifecycle | dataflow | MOD-GOV-worktree_lifecycle |
| MOD-GOV_blueprint_status_transition_reconciler | dataflow | MOD-GOV_blueprint_status_transition_reconciler |
| MOD-GOV_cross_layer_contract_signature_reconciler | dataflow | MOD-GOV_cross_layer_contract_signature_reconciler |
| MOD-D5-ARCH-TOOLS | decision | layer:MOD-D5-ARCH-TOOLS |
| MOD-GOV-REPAIR | decision | layer:MOD-GOV-REPAIR |
| MOD-GOV-SCRIPTS | decision | layer:MOD-GOV-SCRIPTS |
| MOD-GOV-SCRIPTS-ARCH | decision | layer:MOD-GOV-SCRIPTS-ARCH |
| MOD-GOV-arch_reference_gate | decision | layer:MOD-GOV-arch_reference_gate |
| MOD-GOV-audit_return_contract_usage | decision | layer:MOD-GOV-audit_return_contract_usage |
| MOD-GOV-audit_worktree_ops_telemetry | decision | layer:MOD-GOV-audit_worktree_ops_telemetry |
| MOD-GOV-bare_getenv_gate | decision | layer:MOD-GOV-bare_getenv_gate |
| MOD-GOV-bare_sql_gate | decision | layer:MOD-GOV-bare_sql_gate |
| MOD-GOV-batched_auto_committer | decision | layer:MOD-GOV-batched_auto_committer |
| MOD-GOV-blueprint_amodule_consistency_gate | decision | layer:MOD-GOV-blueprint_amodule_consistency_gate |
| MOD-GOV-capability_overlap_gate | decision | layer:MOD-GOV-capability_overlap_gate |
| MOD-GOV-check_vocab_hardcode | decision | layer:MOD-GOV-check_vocab_hardcode |
| MOD-GOV-claim_required_gate | decision | layer:MOD-GOV-claim_required_gate |
| MOD-GOV-commit_gate_registry | decision | layer:MOD-GOV-commit_gate_registry |
| MOD-GOV-commit_gates | decision | layer:MOD-GOV-commit_gates |
| MOD-GOV-create_guard | decision | layer:MOD-GOV-create_guard |
| MOD-GOV-dangling_reference_gate | decision | layer:MOD-GOV-dangling_reference_gate |
| MOD-GOV-diff_helpers | decision | layer:MOD-GOV-diff_helpers |
| MOD-GOV-doc_ref_broken_gate | decision | layer:MOD-GOV-doc_ref_broken_gate |
| MOD-GOV-domain_fk_gate | decision | layer:MOD-GOV-domain_fk_gate |
| MOD-GOV-emergency_commit | decision | layer:MOD-GOV-emergency_commit |
| MOD-GOV-empty_handler_gate | decision | layer:MOD-GOV-empty_handler_gate |
| MOD-GOV-exempt_zone_frontmatter_gate | decision | layer:MOD-GOV-exempt_zone_frontmatter_gate |
| MOD-GOV-file_copy_gate | decision | layer:MOD-GOV-file_copy_gate |
| MOD-GOV-function_dup_gate | decision | layer:MOD-GOV-function_dup_gate |
| MOD-GOV-god_class_gate | decision | layer:MOD-GOV-god_class_gate |
| MOD-GOV-hardcoded_url_gate | decision | layer:MOD-GOV-hardcoded_url_gate |
| MOD-GOV-held_overlap_gate | decision | layer:MOD-GOV-held_overlap_gate |
| MOD-GOV-high_complexity_gate | decision | layer:MOD-GOV-high_complexity_gate |
| MOD-GOV-id_uniqueness_gate | decision | layer:MOD-GOV-id_uniqueness_gate |
| MOD-GOV-import_direction_gate | decision | layer:MOD-GOV-import_direction_gate |
| MOD-GOV-long_param_list_gate | decision | layer:MOD-GOV-long_param_list_gate |
| MOD-GOV-manual_only_permanent_gate | decision | layer:MOD-GOV-manual_only_permanent_gate |
| MOD-GOV-migrate_metadata | decision | layer:MOD-GOV-migrate_metadata |
| MOD-GOV-module_id_consistency_gate | decision | layer:MOD-GOV-module_id_consistency_gate |
| MOD-GOV-no_import_side_effect_gate | decision | layer:MOD-GOV-no_import_side_effect_gate |
| MOD-GOV-orphan_module_gate | decision | layer:MOD-GOV-orphan_module_gate |
| MOD-GOV-panorama_alignment_gate | decision | layer:MOD-GOV-panorama_alignment_gate |
| MOD-GOV-perm_trigger_gate | decision | layer:MOD-GOV-perm_trigger_gate |
| MOD-GOV-pre_write_gate | decision | layer:MOD-GOV-pre_write_gate |
| MOD-GOV-r5_digit_suffix_gate | decision | layer:MOD-GOV-r5_digit_suffix_gate |
| MOD-GOV-reconcile_runner | decision | layer:MOD-GOV-reconcile_runner |
| MOD-GOV-reconcile_worker | decision | layer:MOD-GOV-reconcile_worker |
| MOD-GOV-reconciliation_registry | decision | layer:MOD-GOV-reconciliation_registry |
| MOD-GOV-rename_depgraph_sync_gate | decision | layer:MOD-GOV-rename_depgraph_sync_gate |
| MOD-GOV-rule_four_way_alignment_gate | decision | layer:MOD-GOV-rule_four_way_alignment_gate |
| MOD-GOV-rule_patterns | decision | layer:MOD-GOV-rule_patterns |
| MOD-GOV-ruling_reference_gate | decision | layer:MOD-GOV-ruling_reference_gate |
| MOD-GOV-run_silent_failure_regression | decision | layer:MOD-GOV-run_silent_failure_regression |
| MOD-GOV-session_claim | decision | layer:MOD-GOV-session_claim |
| MOD-GOV-session_required_gate | decision | layer:MOD-GOV-session_required_gate |
| MOD-GOV-session_worktree | decision | layer:MOD-GOV-session_worktree |
| MOD-GOV-ssot_redefinition_gate | decision | layer:MOD-GOV-ssot_redefinition_gate |
| MOD-GOV-test_claim_files_for_edit | decision | layer:MOD-GOV-test_claim_files_for_edit |
| MOD-GOV-test_emergency_commit | decision | layer:MOD-GOV-test_emergency_commit |
| MOD-GOV-test_reconcile_async | decision | layer:MOD-GOV-test_reconcile_async |
| MOD-GOV-test_source_consistency_gate | decision | layer:MOD-GOV-test_source_consistency_gate |
| MOD-GOV-vocab_hardcode_gate | decision | layer:MOD-GOV-vocab_hardcode_gate |
| MOD-GOV-worktree_manager | decision | layer:MOD-GOV-worktree_manager |
| MOD-GOV_behavioral_admission | decision | layer:MOD-GOV_behavioral_admission |
| MOD-GOV_code_quality_domain | decision | layer:MOD-GOV_code_quality_domain |
| MOD-GOV_commit_gates | decision | layer:MOD-GOV_commit_gates |
| MOD-GOV_commit_gateway_abuse_monitor | decision | layer:MOD-GOV_commit_gateway_abuse_monitor |
| MOD-GOV_git_performance_monitor | decision | layer:MOD-GOV_git_performance_monitor |
| MOD-GOV_guc_trigger_fix | decision | layer:MOD-GOV_guc_trigger_fix |
| MOD-GOV_resilience_governance | decision | layer:MOD-GOV_resilience_governance |
| MOD-GOV_rule_domain | decision | layer:MOD-GOV_rule_domain |
| MOD-GOV_rule_execution_pairing_gate | decision | layer:MOD-GOV_rule_execution_pairing_gate |
| MOD-GOV_runtime_violation_snapshot | decision | layer:MOD-GOV_runtime_violation_snapshot |
| MOD-GOV_runtime_violation_snapshot_reconciler | decision | layer:MOD-GOV_runtime_violation_snapshot_reconciler |
| MOD-GOV_security_governance | decision | layer:MOD-GOV_security_governance |
| MOD-GOV_sync_savepoint_test | decision | layer:MOD-GOV_sync_savepoint_test |
| MOD-GOV_yaml_sync_error_class | decision | layer:MOD-GOV_yaml_sync_error_class |
| MOD-INF-GOV | decision | layer:MOD-INF-GOV |
| MOD-KB-001 | decision | layer:L2D |
| MOD-KB-001 | decision | layer:MOD-KB-001 |
| MOD-ORC-trigger_router | decision | layer:MOD-ORC-trigger_router |
| MOD-PFC-001 | decision | layer:MOD-PFC-001 |
| MOD-SEC-immutable_core | decision | layer:MOD-SEC-immutable_core |
| MOD-SHR-io-yaml | decision | layer:MOD-SHR-io-yaml |
| MOD-SHR-workspace_telemetry | decision | layer:MOD-SHR-workspace_telemetry |
| MOD-SHR_converters | decision | layer:MOD-SHR_converters |
| MOD-TEST-259 | decision | layer:MOD-TEST-259 |
| MOD-TEST-267 | decision | layer:MOD-TEST-267 |
| MOD-TEST-apply_depgraph_smoke | decision | layer:MOD-TEST-apply_depgraph_smoke |
| MOD-TEST_apply_depgraph_smoke | decision | layer:MOD-TEST_apply_depgraph_smoke |
| MOD-D5_ARCH_TOOLS | depgraph | scripts/governance/query_module_panorama.py |
| MOD-D_GOV_SCRIPTS | depgraph | scripts/governance/d5_architecture/generators/generate_code_wiki_stats.py |
| MOD-GOV-008 | depgraph | scripts/governance/d7_code/any_type_inferrer.py |
| MOD-GOV-backfill_checker | depgraph | src/zephyr/data/config/known_data_gaps.yaml |
| MOD-GOV_AGENT_RBAC | depgraph | src/zephyr/governance/agent-rbac/__init__.py |
| MOD-GOV_ALIGN_PANORAMAS | depgraph | scripts/governance/d5_architecture/generators/align_panoramas.py |
| MOD-GOV_ANALYZE_CHANGE_IMPACT | depgraph | scripts/governance/d5_architecture/analyze_change_impact.py |
| MOD-GOV_ANALYZE_ORPHAN_CONSUMERS | depgraph | scripts/governance/_archive/one_off/analyze_orphan_consumers.py |
| MOD-GOV_ARCH_REFERENCE_GATE | depgraph | tests/governance/commit_gates/test_arch_reference_gate.py |
| MOD-GOV_ASYNC_RUNTIME | depgraph | tests/trading/runtime/test_async_runtime.py |
| MOD-GOV_AUDIT | depgraph | tests/governance/audit/test_reconcile_worker_selfheal.py |
| MOD-GOV_AUDIT_RETURN_CONTRACT_USAGE | depgraph | scripts/governance/audit_return_contract_usage.py |
| MOD-GOV_AUDIT_TRAIL | depgraph | src/zephyr/governance/audit-trail/__init__.py |
| MOD-GOV_AUDIT_WORKTREE_OPS_TELEMETRY | depgraph | scripts/governance/audit_worktree_ops_telemetry.py |
| MOD-GOV_BARE_GETENV_GATE | depgraph | tests/governance/commit_gates/test_bare_getenv_gate.py |
| MOD-GOV_BARE_SQL_GATE | depgraph | tests/governance/commit_gates/test_bare_sql_gate.py |
| MOD-GOV_BATCHED_AUTO_COMMITTER | depgraph | src/zephyr/gov_enforcement/rule_bridge/batched_auto_committer.py |
| MOD-GOV_BEHAVIORAL_ADMISSION | depgraph | src/zephyr/gov_enforcement/behavioral_admission/__init__.py |
| MOD-GOV_BLUEPRINT_AMODULE_CONSISTENCY_GATE | depgraph | tests/governance/commit_gates/test_blueprint_amodule_consistency_gate.py |
| MOD-GOV_BLUEPRINT_STATUS_TRANSITION_RECONCILER | depgraph | src/zephyr/governance/audit/blueprint_status_transition_reconciler.py |
| MOD-GOV_CAPABILITY_OVERLAP_GATE | depgraph | tests/governance/commit_gates/test_capability_overlap_gate.py |
| MOD-GOV_CHECK_ANY_ABUSE | depgraph | scripts/governance/d7_code/check_any_abuse.py |
| MOD-GOV_CHECK_CANONICAL_YAML_DRIFT | depgraph | tests/governance/scripts_governance/test_check_canonical_yaml_drift.py |
| MOD-GOV_CHECK_RULE_COVERAGE | depgraph | scripts/governance/_archive/one_off/check_rule_coverage.py |
| MOD-GOV_CHECK_VOCAB_HARDCODE | depgraph | tests/governance/scripts_governance/test_check_vocab_hardcode.py |
| MOD-GOV_CH_BATCH_SIZE_GATE | depgraph | tests/governance/commit_gates/test_ch_batch_size_gate.py |
| MOD-GOV_CH_VERSION_COL_GATE | depgraph | tests/governance/commit_gates/test_ch_version_col_gate.py |
| MOD-GOV_CLAIM_REQUIRED_GATE | depgraph | tests/governance/commit_gates/test_claim_required_gate.py |
| MOD-GOV_CODE_QUALITY_DOMAIN | depgraph | src/zephyr/gov_code_quality/__init__.py |
| MOD-GOV_COMMIT_GATES | depgraph | src/zephyr/gov_enforcement/commit_gates/__init__.py |
| MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR | depgraph | src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py |
| MOD-GOV_COMMIT_GATE_REGISTRY | depgraph | src/zephyr/gov_enforcement/rule_bridge/__init__.py |
| MOD-GOV_CONCURRENT_WRITE_TEST | depgraph | scripts/governance/repair/apply_verification_results.py |
| MOD-GOV_CREATE_GUARD | depgraph | tests/governance/commit_gates/test_create_guard.py |
| MOD-GOV_CROSS_LAYER_CONTRACT_SIGNATURE_RECONCILER | depgraph | src/zephyr/governance/audit/cross_layer_contract_signature_reconciler.py |
| MOD-GOV_DANGLING_REFERENCE_GATE | depgraph | tests/governance/commit_gates/test_dangling_reference_gate.py |
| MOD-GOV_DATABASE_SERVICE | depgraph | tests/governance/data_layer/test_database_service.py |
| MOD-GOV_DEEPSEEK_API | depgraph | scripts/construction/test_deepseek_api.py |
| MOD-GOV_DEMO_EE_PIPELINE | depgraph | scripts/demos/demo_e2e_pipeline.py |
| MOD-GOV_DETECT_CAUSAL_CONFLICTS | depgraph | scripts/governance/d5_architecture/detect_causal_conflicts.py |
| MOD-GOV_DIFF_HELPERS | depgraph | tests/governance/commit_gates/test_diff_helpers.py |
| MOD-GOV_DM200912_QUERY_DOMAINS | depgraph | scripts/governance/d5_architecture/dm200912_query_domains.py |
| MOD-GOV_DM200916_WRITE_DIRECT | depgraph | scripts/governance/d5_architecture/dm200916_write_direct.py |
| MOD-GOV_DOC_REF_BROKEN_GATE | depgraph | tests/governance/commit_gates/test_doc_ref_broken_gate.py |
| MOD-GOV_DOMAIN_FK_GATE | depgraph | tests/governance/commit_gates/test_domain_fk_gate.py |
| MOD-GOV_EMERGENCY_COMMIT | depgraph | src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py |
| MOD-GOV_EMPTY_HANDLER_GATE | depgraph | tests/governance/commit_gates/test_empty_handler_gate.py |
| MOD-GOV_ENFORCEMENT_worktree_lifecycle | depgraph | config/worktree_state_machine.yaml |
| MOD-GOV_ERROR_PATTERN_CONSUMER | depgraph | src/zephyr/governance/audit/error_pattern_consumer_reconciler.py |
| MOD-GOV_ERROR_PATTERN_LIBRARY | depgraph | src/zephyr/governance/audit/ai_error_pattern_library.py |
| MOD-GOV_EXEMPT_ZONE_FRONTMATTER_GATE | depgraph | tests/governance/commit_gates/test_exempt_zone_frontmatter_gate.py |
| MOD-GOV_F3_AUTO_INTEGRATION | depgraph | tests/infrastructure/test_f3_auto_integration.py |
| MOD-GOV_F3_EXTREME | depgraph | tests/infrastructure/test_f3_extreme.py |
| MOD-GOV_FILE_COPY_GATE | depgraph | tests/governance/commit_gates/test_file_copy_gate.py |
| MOD-GOV_FUNCTION_DUP_GATE | depgraph | tests/governance/commit_gates/test_function_dup_gate.py |
| MOD-GOV_GENERATE_ASSET_CATALOG | depgraph | scripts/governance/d5_architecture/generators/generate_asset_catalog.py |
| MOD-GOV_GENERATE_CAPABILITY_HEATMAP | depgraph | scripts/governance/d5_architecture/generators/generate_capability_heatmap.py |
| MOD-GOV_GENERATE_CAPACITY_REPORT | depgraph | scripts/governance/d5_architecture/generators/generate_capacity_report.py |
| MOD-GOV_GENERATE_CONSTRAINT_VIOLATIONS | depgraph | scripts/governance/d5_architecture/generators/generate_constraint_violations.py |
| MOD-GOV_GENERATE_CONTRACT_CATALOG | depgraph | scripts/governance/d5_architecture/generators/generate_contract_catalog.py |
| MOD-GOV_GENERATE_CROSS_DOMAIN_MATRIX | depgraph | scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py |
| MOD-GOV_GENERATE_DATAFLOW_DIAGRAM | depgraph | tests/test_generate_dataflow_diagram.py |
| MOD-GOV_GENERATE_DESIGN_VS_PRODUCTION | depgraph | scripts/governance/d5_architecture/generators/generate_design_vs_production.py |
| MOD-GOV_GENERATE_DOMAIN_DEPENDENCY_DIAGRAM | depgraph | scripts/governance/d5_architecture/generators/generate_domain_dependency_diagram.py |
| MOD-GOV_GENERATE_DOMAIN_DOC | depgraph | scripts/governance/d5_architecture/generators/generate_domain_doc.py |
| MOD-GOV_GENERATE_DOMAIN_INDEX | depgraph | scripts/governance/d5_architecture/generators/generate_domain_index.py |
| MOD-GOV_GENERATE_INTEGRATION_TOPOLOGY | depgraph | scripts/governance/d5_architecture/generators/generate_integration_topology.py |
| MOD-GOV_GENERATE_NAVIGATION_INDEX | depgraph | scripts/governance/d5_architecture/generators/generate_navigation_index.py |
| MOD-GOV_GENERATE_PATH_TREE | depgraph | scripts/governance/d5_architecture/generators/generate_path_tree.py |
| MOD-GOV_GIT_HELPERS | depgraph | src/zephyr/governance/audit/_git_helpers.py |
| MOD-GOV_GIT_PERFORMANCE_MONITOR | depgraph | src/zephyr/governance/audit/git_performance_monitor_reconciler.py |
| MOD-GOV_GOD_CLASS_GATE | depgraph | tests/governance/commit_gates/test_god_class_gate.py |
| MOD-GOV_GROUP_ORPHAN_MODULES | depgraph | scripts/governance/_archive/one_off/group_orphan_modules.py |
| MOD-GOV_GUC_TRIGGER_FIX | depgraph | tests/governance/d8_doc_sync/test_guc_trigger_fix.py |
| MOD-GOV_HARDCODED_URL_GATE | depgraph | tests/governance/commit_gates/test_hardcoded_url_gate.py |
| MOD-GOV_HEALTH_SCORE_CALCULATOR | depgraph | src/zephyr/governance/audit/health_score_calculator.py |
| MOD-GOV_HEARTBEAT_DAEMON | depgraph | src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py |
| MOD-GOV_HEARTBEAT_DAEMON_TEST | depgraph | tests/governance/rule_bridge/test_heartbeat_daemon.py |
| MOD-GOV_HELD_OVERLAP_GATE | depgraph | tests/governance/commit_gates/test_held_overlap_gate.py |
| MOD-GOV_HIGH_COMPLEXITY_GATE | depgraph | tests/governance/commit_gates/test_high_complexity_gate.py |
| MOD-GOV_ID_UNIQUENESS_GATE | depgraph | tests/governance/commit_gates/test_id_uniqueness_gate.py |
| MOD-GOV_IMPORT_DIRECTION_GATE | depgraph | tests/governance/commit_gates/test_import_direction_gate.py |
| MOD-GOV_LONG_PARAM_LIST_GATE | depgraph | tests/governance/commit_gates/_gate_test_helpers.py |
| MOD-GOV_MIGRATE_METADATA | depgraph | scripts/governance/migrate_to_metadata_tables.py |
| MOD-GOV_MODULE_ID_CONSISTENCY_GATE | depgraph | tests/governance/commit_gates/test_module_id_consistency_gate.py |
| MOD-GOV_NO_IMPORT_SIDE_EFFECT_GATE | depgraph | tests/governance/commit_gates/test_no_import_side_effect_gate.py |
| MOD-GOV_ORPHAN_MODULE_GATE | depgraph | tests/governance/commit_gates/test_orphan_module_gate.py |
| MOD-GOV_PANORAMA_ALIGNMENT_GATE | depgraph | tests/governance/commit_gates/test_panorama_alignment_gate.py |
| MOD-GOV_PERF_DEPGRAPH_BASELINE | depgraph | scripts/governance/_archive/one_off/perf_depgraph_baseline.py |
| MOD-GOV_PERM_TRIGGER_GATE | depgraph | tests/governance/commit_gates/test_perm_trigger_gate.py |
| MOD-GOV_PRE_WRITE_GATE | depgraph | tests/governance/scripts_governance/test_pre_write_gate.py |
| MOD-GOV_R5_DIGIT_SUFFIX_GATE | depgraph | tests/governance/commit_gates/test_r5_digit_suffix_gate.py |
| MOD-GOV_RECONCILE_RUNNER | depgraph | src/zephyr/governance/audit/reconcile_runner.py |
| MOD-GOV_RECONCILE_WORKER | depgraph | src/zephyr/governance/audit/reconcile_worker.py |
| MOD-GOV_RECONCILIATION_REGISTRY | depgraph | src/zephyr/governance/audit/reconciliation_registry.py |
| MOD-GOV_RENAME_DEPGRAPH_SYNC_GATE | depgraph | tests/governance/commit_gates/test_rename_depgraph_sync_gate.py |
| MOD-GOV_REPAIR | depgraph | scripts/governance/repair/audit_design_completeness.py |
| MOD-GOV_RESILIENCE_GOVERNANCE | depgraph | src/zephyr/governance/resilience_governance/__init__.py |
| MOD-GOV_ROLLBACK | depgraph | src/zephyr/governance/rollback/__init__.py |
... 共 236 行（仅展示前 200 行）

## 2. 状态漂移（blueprint 缺 design_maturity 字段）

| module_id | depgraph | dataflow | decision | blueprint |
|---|---|---|---|---|
| GOV-ARCH-DIAGRAM-PLAN | - | - | - | - |
| MOD-006 | - | - | - | - |
| MOD-007 | - | - | - | - |
| STD-SESSION-CARRYOVER-001 | - | - | - | - |

## 3. 域不一致（domain_id 不一致）

> 无域不一致。

## 4. 设计态孤立（design 仅一图）

| module_id | graph | entity_name |
|---|---|---|
| MOD-GOV-HEARTBEAT | dataflow | MOD-GOV-HEARTBEAT |
| MOD-GOV-blueprint_status_transition_reconciler | dataflow | MOD-GOV-blueprint_status_transition_reconciler |
| MOD-GOV-cross_layer_contract_signature_reconciler | dataflow | MOD-GOV-cross_layer_contract_signature_reconciler |
| MOD-GOV-depgraph_pre_registration_gate | dataflow | MOD-GOV-depgraph_pre_registration_gate |
| MOD-GOV-derivation_annotation_gate | dataflow | MOD-GOV-derivation_annotation_gate |
| MOD-GOV-folder_capacity_hard_limit_gate | dataflow | MOD-GOV-folder_capacity_hard_limit_gate |
| MOD-GOV-heartbeat_daemon | dataflow | MOD-GOV-heartbeat_daemon |
| MOD-GOV-relative_path_literal_gate | dataflow | MOD-GOV-relative_path_literal_gate |
| MOD-GOV-runtime_violation_snapshot | dataflow | MOD-GOV-runtime_violation_snapshot |
| MOD-GOV-runtime_violation_snapshot_reconciler | dataflow | MOD-GOV-runtime_violation_snapshot_reconciler |
| MOD-GOV-stash_accumulation_gate | dataflow | MOD-GOV-stash_accumulation_gate |
| MOD-GOV-worktree_lifecycle | dataflow | MOD-GOV-worktree_lifecycle |
| MOD-GOV_blueprint_status_transition_reconciler | dataflow | MOD-GOV_blueprint_status_transition_reconciler |
| MOD-GOV_cross_layer_contract_signature_reconciler | dataflow | MOD-GOV_cross_layer_contract_signature_reconciler |
| MOD-GOV_rule_execution_pairing_gate | decision | layer:MOD-GOV_rule_execution_pairing_gate |
| MOD-GOV_runtime_violation_snapshot | decision | layer:MOD-GOV_runtime_violation_snapshot |
| MOD-GOV_runtime_violation_snapshot_reconciler | decision | layer:MOD-GOV_runtime_violation_snapshot_reconciler |
| MOD-KB-001 | decision | layer:L2D |

## 5. 处置建议

- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除
- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）
- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）
- 设计态孤立：评估设计态是否需要同步到另三图
