# 四图对齐报告 (Panorama Alignment Report)

- 生成时间: 2026-07-25 01:17:52
- 数据源: depgraph (PostgreSQL)
- 四图节点数: depgraph=683 / dataflow=739 / decision=802 / blueprint=78
- 问题总数: 123
  - 孤儿（仅一图）: 101
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
