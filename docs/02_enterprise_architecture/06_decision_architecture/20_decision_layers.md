# 决策流图 · 层级详情图

> 生成时间: 2026-07-30T01:41:53
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 辅助图

L0-L6 层级卡片 + 频率/成熟度/状态 + 流向箭头 + 学习闭环反馈边。

```mermaid
flowchart LR
    LCFG_rule_enforcement_registry["[production] CFG-rule-enforcement-registry<br/>蓝图: 门禁规则集 / Gate Rule Set — ARCH-052 聚合节点 production<br/>成熟度: production<br/>build: stable"]:::bsStable
    LCFG_rule_registry_collection["[production] CFG-rule-registry-collection<br/>蓝图: 规则注册表集 / Rule Registry Collection — ARCH-052 聚合节点 production<br/>成熟度: production<br/>build: stable"]:::bsStable
    LCFG_scripts_registry["[production] CFG-scripts-registry<br/>蓝图: 脚本集 / Script Collection — ARCH-052 聚合节点 production<br/>成熟度: production<br/>build: stable"]:::bsStable
    LCFG_test_suite_registry["[production] CFG-test-suite-registry<br/>蓝图: 测试集 / Test Suite — ARCH-052 聚合节点 production<br/>成熟度: production<br/>build: stable"]:::bsStable
    LINFRA_DB_001["[production] INFRA-DB-001<br/>蓝图: zephyr-sqlite-task-db — database 节点 (ARCH-053)<br/>成熟度: production<br/>build: stable"]:::bsStable
    LINFRA_DB_002["[production] INFRA-DB-002<br/>蓝图: zephyr-chroma-vector-db — database 节点 (ARCH-053)<br/>成熟度: production<br/>build: stable"]:::bsStable
    LINFRA_DB_003["[production] INFRA-DB-003<br/>蓝图: zephyr-depgraph-db — database 节点 (ARCH-053)<br/>成熟度: production<br/>build: stable"]:::bsStable
    LINFRA_DB_006["[production] INFRA-DB-006<br/>蓝图: zephyr-clickhouse-c1-market — database 节点 (ARCH-053)<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL0["[production] L0 数据接入与预处理层<br/>Data Ingestion & Preprocessing<br/>蓝图: MOD-MKT_DATA<br/>功能: miniQMT + iFind + t…<br/>频率: tick<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL1["[production] L1 因子计算层<br/>Factor Calculation<br/>蓝图: MOD-L02-001<br/>功能: 因子工厂全生命周期管理 → 盘前全量/…<br/>频率: daily<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL2A["[design] L2A 信号层<br/>Signal Generation<br/>功能: 信号工厂 → 多策略投票 → 收益率条…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2B["[design] L2B 主力行为层<br/>Main Force Behavior Analysis<br/>功能: 六阶段识别 + 自迭代推演 + 庄家专…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2C["[design] L2C 市场状态与大盘预测层<br/>Market State & Index Prediction<br/>功能: 3×3矩阵 + 2叠加态 + 三层大盘…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL2D["[design] L2D 知识图谱与因果推演层<br/>Knowledge Graph & Causal Inference<br/>功能: 六类知识图谱 → 事件影响链分析 → …<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL3["[design] L3 策略组合层<br/>Strategy & Portfolio Combination<br/>功能: 多策略信号合成 → 资本分配 → 元策…<br/>频率: daily<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL4["[production] L4 风控层<br/>Risk Control<br/>蓝图: MOD-L04-001<br/>功能: Pre/Post-Trade 风控校验…<br/>频率: realtime<br/>成熟度: production<br/>build: stable"]:::bsStable
    LL5["[design] L5 学习层<br/>Learning & Optimization<br/>功能: 7阶段学习流水线 → 模块工厂 → 知…<br/>频率: weekly<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LL6["[design] L6 自评估层<br/>Self Evaluation<br/>功能: LLM 自评估(Judge+交叉验证)…<br/>频率: weekly<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_ALT_DATA["[production] MOD-ALT_DATA<br/>蓝图: MOD-ALT_DATA<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_ARCH_BIZDB["[design] MOD-ARCH-BIZDB<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_AUTONOMY_CORE["[production] MOD-AUTONOMY_CORE<br/>蓝图: MOD-AUTONOMY_CORE<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_BT_001["[design] MOD-BT-001<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_C1_MARKETCH["[design] MOD-C1-MARKETCH<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_CONTEXT_ENGINE["[design] MOD-CONTEXT_ENGINE<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_CROSS_ASSET["[design] MOD-CROSS_ASSET<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_D5_ARCH_TOOLS["[production] MOD-D5-ARCH-TOOLS<br/>蓝图: MOD-D5-ARCH-TOOLS<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_DATABASE["[production] MOD-DATABASE<br/>蓝图: MOD-DATABASE<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_DATA_ENG["[production] MOD-DATA_ENG<br/>蓝图: MOD-DATA_ENG<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_DATA_GOV["[production] MOD-DATA_GOV<br/>蓝图: MOD-DATA_GOV<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_DATA_SEC["[production] MOD-DATA_SEC<br/>蓝图: MOD-DATA_SEC<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_DIGITAL_TWIN["[design] MOD-DIGITAL_TWIN<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_EXEC_SIM["[production] MOD-EXEC_SIM<br/>蓝图: MOD-EXEC_SIM<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_EX_SOR["[production] MOD-EX_SOR<br/>蓝图: MOD-EX_SOR<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_FEEDBACK_LOOP["[design] MOD-FEEDBACK_LOOP<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_GATE_ENGINE["[design] MOD-GATE_ENGINE<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_GOV_019["[production] MOD-GOV-019<br/>蓝图: MOD-GOV-019<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_029["[production] MOD-GOV-029<br/>蓝图: MOD-GOV-029<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_041["[production] MOD-GOV-041<br/>蓝图: MOD-GOV-041<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_ALIGN_PANORAMAS["[design] MOD-GOV-ALIGN-PANORAMAS<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_GOV_DOCS["[production] MOD-GOV-DOCS<br/>蓝图: MOD-GOV-DOCS<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_REPAIR["[production] MOD-GOV-REPAIR<br/>蓝图: MOD-GOV-REPAIR<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_SCRIPTS["[production] MOD-GOV-SCRIPTS<br/>蓝图: MOD-GOV-SCRIPTS<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_SCRIPTS_ARCH["[production] MOD-GOV-SCRIPTS-ARCH<br/>蓝图: MOD-GOV-SCRIPTS-ARCH<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_SYNC_PANORAMA["[production] MOD-GOV-SYNC-PANORAMA<br/>蓝图: MOD-GOV-SYNC-PANORAMA<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_arch_reference_gate["[production] MOD-GOV-arch_reference_gate<br/>蓝图: MOD-GOV-arch_reference_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_audit_return_contract_usage["[production] MOD-GOV-audit_return_contract_usage<br/>蓝图: MOD-GOV-audit_return_contract_usage<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_audit_worktree_ops_telemetry["[production] MOD-GOV-audit_worktree_ops_telemetry<br/>蓝图: MOD-GOV-audit_worktree_ops_telemetry<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_bare_getenv_gate["[production] MOD-GOV-bare_getenv_gate<br/>蓝图: MOD-GOV-bare_getenv_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_bare_sql_gate["[production] MOD-GOV-bare_sql_gate<br/>蓝图: MOD-GOV-bare_sql_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_batched_auto_committer["[production] MOD-GOV-batched_auto_committer<br/>蓝图: MOD-GOV-batched_auto_committer<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_blueprint_amodule_consistency_gate["[production] MOD-GOV-blueprint_amodule_consistency_gate<br/>蓝图: MOD-GOV-blueprint_amodule_consistency_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_capability_overlap_gate["[production] MOD-GOV-capability_overlap_gate<br/>蓝图: MOD-GOV-capability_overlap_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_check_vocab_hardcode["[production] MOD-GOV-check_vocab_hardcode<br/>蓝图: MOD-GOV-check_vocab_hardcode<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_claim_required_gate["[production] MOD-GOV-claim_required_gate<br/>蓝图: MOD-GOV-claim_required_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_commit_gate_registry["[production] MOD-GOV-commit_gate_registry<br/>蓝图: MOD-GOV-commit_gate_registry<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_commit_gates["[production] MOD-GOV-commit_gates<br/>蓝图: MOD-GOV-commit_gates<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_create_guard["[production] MOD-GOV-create_guard<br/>蓝图: MOD-GOV-create_guard<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_dangling_reference_gate["[production] MOD-GOV-dangling_reference_gate<br/>蓝图: MOD-GOV-dangling_reference_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_diff_helpers["[production] MOD-GOV-diff_helpers<br/>蓝图: MOD-GOV-diff_helpers<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_doc_ref_broken_gate["[production] MOD-GOV-doc_ref_broken_gate<br/>蓝图: MOD-GOV-doc_ref_broken_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_domain_fk_gate["[production] MOD-GOV-domain_fk_gate<br/>蓝图: MOD-GOV-domain_fk_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_emergency_commit["[production] MOD-GOV-emergency_commit<br/>蓝图: MOD-GOV-emergency_commit<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_empty_handler_gate["[production] MOD-GOV-empty_handler_gate<br/>蓝图: MOD-GOV-empty_handler_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_exempt_zone_frontmatter_gate["[production] MOD-GOV-exempt_zone_frontmatter_gate<br/>蓝图: MOD-GOV-exempt_zone_frontmatter_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_file_copy_gate["[production] MOD-GOV-file_copy_gate<br/>蓝图: MOD-GOV-file_copy_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_function_dup_gate["[production] MOD-GOV-function_dup_gate<br/>蓝图: MOD-GOV-function_dup_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_god_class_gate["[production] MOD-GOV-god_class_gate<br/>蓝图: MOD-GOV-god_class_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_hardcoded_url_gate["[production] MOD-GOV-hardcoded_url_gate<br/>蓝图: MOD-GOV-hardcoded_url_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_held_overlap_gate["[production] MOD-GOV-held_overlap_gate<br/>蓝图: MOD-GOV-held_overlap_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_high_complexity_gate["[production] MOD-GOV-high_complexity_gate<br/>蓝图: MOD-GOV-high_complexity_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_id_uniqueness_gate["[production] MOD-GOV-id_uniqueness_gate<br/>蓝图: MOD-GOV-id_uniqueness_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_import_direction_gate["[production] MOD-GOV-import_direction_gate<br/>蓝图: MOD-GOV-import_direction_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_long_param_list_gate["[production] MOD-GOV-long_param_list_gate<br/>蓝图: MOD-GOV-long_param_list_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_manual_only_permanent_gate["[production] MOD-GOV-manual_only_permanent_gate<br/>蓝图: MOD-GOV-manual_only_permanent_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_migrate_metadata["[production] MOD-GOV-migrate_metadata<br/>蓝图: MOD-GOV-migrate_metadata<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_module_id_consistency_gate["[production] MOD-GOV-module_id_consistency_gate<br/>蓝图: MOD-GOV-module_id_consistency_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_no_import_side_effect_gate["[production] MOD-GOV-no_import_side_effect_gate<br/>蓝图: MOD-GOV-no_import_side_effect_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_orphan_module_gate["[production] MOD-GOV-orphan_module_gate<br/>蓝图: MOD-GOV-orphan_module_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_panorama_alignment_gate["[production] MOD-GOV-panorama_alignment_gate<br/>蓝图: MOD-GOV-panorama_alignment_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_perm_trigger_gate["[production] MOD-GOV-perm_trigger_gate<br/>蓝图: MOD-GOV-perm_trigger_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_pre_write_gate["[production] MOD-GOV-pre_write_gate<br/>蓝图: MOD-GOV-pre_write_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_r5_digit_suffix_gate["[production] MOD-GOV-r5_digit_suffix_gate<br/>蓝图: MOD-GOV-r5_digit_suffix_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_reconcile_runner["[production] MOD-GOV-reconcile_runner<br/>蓝图: MOD-GOV-reconcile_runner<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_reconcile_worker["[production] MOD-GOV-reconcile_worker<br/>蓝图: MOD-GOV-reconcile_worker<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_reconciliation_registry["[production] MOD-GOV-reconciliation_registry<br/>蓝图: MOD-GOV-reconciliation_registry<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_rename_depgraph_sync_gate["[production] MOD-GOV-rename_depgraph_sync_gate<br/>蓝图: MOD-GOV-rename_depgraph_sync_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_rule_execution_pairing_gate["[design] MOD-GOV-rule_execution_pairing_gate<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_GOV_rule_four_way_alignment_gate["[production] MOD-GOV-rule_four_way_alignment_gate<br/>蓝图: MOD-GOV-rule_four_way_alignment_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_rule_patterns["[production] MOD-GOV-rule_patterns<br/>蓝图: MOD-GOV-rule_patterns<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_ruling_reference_gate["[production] MOD-GOV-ruling_reference_gate<br/>蓝图: MOD-GOV-ruling_reference_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_run_silent_failure_regression["[production] MOD-GOV-run_silent_failure_regression<br/>蓝图: MOD-GOV-run_silent_failure_regression<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_session_claim["[production] MOD-GOV-session_claim<br/>蓝图: MOD-GOV-session_claim<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_session_required_gate["[production] MOD-GOV-session_required_gate<br/>蓝图: MOD-GOV-session_required_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_session_startup_health_check["[design] MOD-GOV-session_startup_health_check<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_GOV_session_worktree["[production] MOD-GOV-session_worktree<br/>蓝图: MOD-GOV-session_worktree<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_ssot_redefinition_gate["[production] MOD-GOV-ssot_redefinition_gate<br/>蓝图: MOD-GOV-ssot_redefinition_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_test_claim_files_for_edit["[production] MOD-GOV-test_claim_files_for_edit<br/>蓝图: MOD-GOV-test_claim_files_for_edit<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_test_emergency_commit["[production] MOD-GOV-test_emergency_commit<br/>蓝图: MOD-GOV-test_emergency_commit<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_test_reconcile_async["[production] MOD-GOV-test_reconcile_async<br/>蓝图: MOD-GOV-test_reconcile_async<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_test_source_consistency_gate["[production] MOD-GOV-test_source_consistency_gate<br/>蓝图: MOD-GOV-test_source_consistency_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_vocab_hardcode_gate["[production] MOD-GOV-vocab_hardcode_gate<br/>蓝图: MOD-GOV-vocab_hardcode_gate<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_workspace_hygiene_reconciler["[design] MOD-GOV-workspace_hygiene_reconciler<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_GOV_worktree_manager["[production] MOD-GOV-worktree_manager<br/>蓝图: MOD-GOV-worktree_manager<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOVERNANCE["[design] MOD-GOVERNANCE<br/>成熟度: design<br/>build: generated"]:::bsGenerated
    LMOD_GOV_COMMON["[production] MOD-GOV_COMMON<br/>蓝图: MOD-GOV_COMMON<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_DATAFLOW_DIAGRAM["[production] MOD-GOV_DATAFLOW_DIAGRAM<br/>蓝图: MOD-GOV_DATAFLOW_DIAGRAM<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_DQ["[production] MOD-GOV_DQ<br/>蓝图: MOD-GOV_DQ<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_ENFORCEMENT["[production] MOD-GOV_ENFORCEMENT<br/>蓝图: MOD-GOV_ENFORCEMENT<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_ENFORCEMENT_worktree_pool["[design] MOD-GOV_ENFORCEMENT_worktree_pool<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_GOV_GATE_CACHE["[production] MOD-GOV_GATE_CACHE<br/>蓝图: MOD-GOV_GATE_CACHE<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_HEALTH_SMOKE["[production] MOD-GOV_HEALTH_SMOKE<br/>蓝图: MOD-GOV_HEALTH_SMOKE<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_SILENT_FAILURE_REGRESSION["[production] MOD-GOV_SILENT_FAILURE_REGRESSION<br/>蓝图: MOD-GOV_SILENT_FAILURE_REGRESSION<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_behavioral_admission["[production] MOD-GOV_behavioral_admission<br/>蓝图: MOD-GOV_behavioral_admission<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_code_quality_domain["[production] MOD-GOV_code_quality_domain<br/>蓝图: MOD-GOV_code_quality_domain<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_commit_gates["[production] MOD-GOV_commit_gates<br/>蓝图: MOD-GOV_commit_gates<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_commit_gateway_abuse_monitor["[production] MOD-GOV_commit_gateway_abuse_monitor<br/>蓝图: MOD-GOV_commit_gateway_abuse_monitor<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_git_performance_monitor["[production] MOD-GOV_git_performance_monitor<br/>蓝图: MOD-GOV_git_performance_monitor<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_GOV_guc_trigger_fix["[production] MOD-GOV_guc_trigger_fix<br/>蓝图: MOD-GOV_guc_trigger_fix<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_resilience_governance["[production] MOD-GOV_resilience_governance<br/>蓝图: MOD-GOV_resilience_governance<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_rule_domain["[production] MOD-GOV_rule_domain<br/>蓝图: MOD-GOV_rule_domain<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_rule_execution_pairing_gate["[design] MOD-GOV_rule_execution_pairing_gate<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_GOV_runtime_violation_snapshot["[design] MOD-GOV_runtime_violation_snapshot<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_GOV_runtime_violation_snapshot_reconciler["[design] MOD-GOV_runtime_violation_snapshot_reconciler<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_GOV_security_governance["[production] MOD-GOV_security_governance<br/>蓝图: MOD-GOV_security_governance<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_sync_savepoint_test["[production] MOD-GOV_sync_savepoint_test<br/>蓝图: MOD-GOV_sync_savepoint_test<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_GOV_yaml_sync_error_class["[production] MOD-GOV_yaml_sync_error_class<br/>蓝图: MOD-GOV_yaml_sync_error_class<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_001["[production] MOD-INF-001<br/>蓝图: MOD-INF-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_002["[production] MOD-INF-002<br/>蓝图: MOD-INF-002<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_003["[production] MOD-INF-003<br/>蓝图: MOD-INF-003<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_005["[design] MOD-INF-005<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_009["[design] MOD-INF-009<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_011["[design] MOD-INF-011<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_013["[production] MOD-INF-013<br/>蓝图: MOD-INF-013<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_014["[production] MOD-INF-014<br/>蓝图: MOD-INF-014<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_INF_015["[production] MOD-INF-015<br/>蓝图: MOD-INF-015<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_INF_016["[design] MOD-INF-016<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_017["[design] MOD-INF-017<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_018["[production] MOD-INF-018<br/>蓝图: MOD-INF-018<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_019["[design] MOD-INF-019<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_020["[design] MOD-INF-020<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_021["[design] MOD-INF-021<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_022["[design] MOD-INF-022<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_023["[design] MOD-INF-023<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_024["[design] MOD-INF-024<br/>成熟度: design<br/>build: generated"]:::bsGenerated
    LMOD_INF_025["[production] MOD-INF-025<br/>蓝图: MOD-INF-025<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_026["[production] MOD-INF-026<br/>蓝图: MOD-INF-026<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_INF_027["[design] MOD-INF-027<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_028["[design] MOD-INF-028<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_029["[design] MOD-INF-029<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_030["[design] MOD-INF-030<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_031["[design] MOD-INF-031<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_033["[design] MOD-INF-033<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_034["[design] MOD-INF-034<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_035["[production] MOD-INF-035<br/>蓝图: MOD-INF-035<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_036["[design] MOD-INF-036<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_037["[design] MOD-INF-037<br/>成熟度: design<br/>build: generated"]:::bsGenerated
    LMOD_INF_038["[production] MOD-INF-038<br/>蓝图: MOD-INF-038<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_039["[design] MOD-INF-039<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INF_040["[production] MOD-INF-040<br/>蓝图: MOD-INF-040<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_042["[production] MOD-INF-042<br/>蓝图: MOD-INF-042<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_043["[production] MOD-INF-043<br/>蓝图: MOD-INF-043<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INF_GOV["[production] MOD-INF-GOV<br/>蓝图: MOD-INF-GOV<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INFRA_OPS["[design] MOD-INFRA_OPS<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_INFRA_RUNTIME["[production] MOD-INFRA_RUNTIME<br/>蓝图: MOD-INFRA_RUNTIME<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_INTEGRATION["[production] MOD-INTEGRATION<br/>蓝图: MOD-INTEGRATION<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_KB_001["[production] MOD-KB-001<br/>蓝图: MOD-KB-001<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_L00_001["[design] MOD-L00-001<br/>成熟度: design<br/>build: generated"]:::bsGenerated
    LMOD_L00_002["[design] MOD-L00-002<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_L00_003["[design] MOD-L00-003<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_L00_004["[production] MOD-L00-004<br/>蓝图: MOD-L00-004<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_L02_001["[production] MOD-L02-001<br/>蓝图: MOD-L02-001<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_L03_001["[production] MOD-L03-001<br/>蓝图: MOD-L03-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_L04_001["[production] MOD-L04-001<br/>蓝图: MOD-L04-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_L05_001["[production] MOD-L05-001<br/>蓝图: MOD-L05-001<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_L06_001["[design] MOD-L06-001<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_L07_001["[production] MOD-L07-001<br/>蓝图: MOD-L07-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_L08_001["[design] MOD-L08-001<br/>成熟度: design<br/>build: generated"]:::bsGenerated
    LMOD_L09_001["[production] MOD-L09-001<br/>蓝图: MOD-L09-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_L10_001["[production] MOD-L10-001<br/>蓝图: MOD-L10-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_L11_001["[production] MOD-L11-001<br/>蓝图: MOD-L11-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_L13_001["[production] MOD-L13-001<br/>蓝图: MOD-L13-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_LLM_SECURITY["[production] MOD-LLM_SECURITY<br/>蓝图: MOD-LLM_SECURITY<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_MASTER_001["[design] MOD-MASTER-001<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_MASTER_002["[design] MOD-MASTER-002<br/>成熟度: design<br/>build: stable"]:::bsStable
    LMOD_MASTER_003["[design] MOD-MASTER-003<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_MASTER_BLUEPRINT["[design] MOD-MASTER_BLUEPRINT<br/>成熟度: design<br/>build: deprecated"]:::bsDeprecated
    LMOD_MKT_DATA["[production] MOD-MKT_DATA<br/>蓝图: MOD-MKT_DATA<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_ML_SERVE["[production] MOD-ML_SERVE<br/>蓝图: MOD-ML_SERVE<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_OPS_018["[production] MOD-OPS-018<br/>蓝图: MOD-OPS-018<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_ORC_trigger_router["[production] MOD-ORC-trigger_router<br/>蓝图: MOD-ORC-trigger_router<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_PFC_001["[production] MOD-PFC-001<br/>蓝图: MOD-PFC-001<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_PF_ALLOC["[design] MOD-PF_ALLOC<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_REMEDIATION_PROGRESS["[production] MOD-REMEDIATION_PROGRESS<br/>蓝图: MOD-REMEDIATION_PROGRESS<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_REMEDIATION_PROGRESS_SMOKE["[production] MOD-REMEDIATION_PROGRESS_SMOKE<br/>蓝图: MOD-REMEDIATION_PROGRESS_SMOKE<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_RESOURCE_OPTIMIZATION_ENGINE["[design] MOD-RESOURCE_OPTIMIZATION_ENGINE<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_RULE_ENGINE["[production] MOD-RULE_ENGINE<br/>蓝图: MOD-RULE_ENGINE<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SEC_030["[production] MOD-SEC-030<br/>蓝图: MOD-SEC-030<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SEC_immutable_core["[production] MOD-SEC-immutable_core<br/>蓝图: MOD-SEC-immutable_core<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SELL_DECISION["[production] MOD-SELL_DECISION<br/>蓝图: MOD-SELL_DECISION<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SHARED_001["[production] MOD-SHARED-001<br/>蓝图: MOD-SHARED-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SHARED_002["[production] MOD-SHARED-002<br/>蓝图: MOD-SHARED-002<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SHR_io_yaml["[production] MOD-SHR-io-yaml<br/>蓝图: MOD-SHR-io-yaml<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SHR_workspace_telemetry["[production] MOD-SHR-workspace_telemetry<br/>蓝图: MOD-SHR-workspace_telemetry<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_SHR_converters["[production] MOD-SHR_converters<br/>蓝图: MOD-SHR_converters<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_SIGNAL_ASHARE["[production] MOD-SIGNAL_ASHARE<br/>蓝图: MOD-SIGNAL_ASHARE<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SIGQC_001["[production] MOD-SIGQC-001<br/>蓝图: MOD-SIGQC-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_SIMULATION["[design] MOD-SIMULATION<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_SMOKE_TEST["[design] MOD-SMOKE-TEST<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_TASK_SYSTEM["[production] MOD-TASK_SYSTEM<br/>蓝图: MOD-TASK_SYSTEM<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST["[design] MOD-TEST<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LMOD_TEST_202["[production] MOD-TEST-202<br/>蓝图: MOD-TEST-202<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_203["[production] MOD-TEST-203<br/>蓝图: MOD-TEST-203<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_204["[production] MOD-TEST-204<br/>蓝图: MOD-TEST-204<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_205["[production] MOD-TEST-205<br/>蓝图: MOD-TEST-205<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_206["[production] MOD-TEST-206<br/>蓝图: MOD-TEST-206<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_210["[production] MOD-TEST-210<br/>蓝图: MOD-TEST-210<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_211["[production] MOD-TEST-211<br/>蓝图: MOD-TEST-211<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_212["[production] MOD-TEST-212<br/>蓝图: MOD-TEST-212<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_213["[production] MOD-TEST-213<br/>蓝图: MOD-TEST-213<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_215["[production] MOD-TEST-215<br/>蓝图: MOD-TEST-215<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_216["[production] MOD-TEST-216<br/>蓝图: MOD-TEST-216<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_217["[production] MOD-TEST-217<br/>蓝图: MOD-TEST-217<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_218["[production] MOD-TEST-218<br/>蓝图: MOD-TEST-218<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_219["[production] MOD-TEST-219<br/>蓝图: MOD-TEST-219<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_220["[production] MOD-TEST-220<br/>蓝图: MOD-TEST-220<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_221["[production] MOD-TEST-221<br/>蓝图: MOD-TEST-221<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_222["[production] MOD-TEST-222<br/>蓝图: MOD-TEST-222<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_223["[production] MOD-TEST-223<br/>蓝图: MOD-TEST-223<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_224["[production] MOD-TEST-224<br/>蓝图: MOD-TEST-224<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_225["[production] MOD-TEST-225<br/>蓝图: MOD-TEST-225<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_226["[production] MOD-TEST-226<br/>蓝图: MOD-TEST-226<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_227["[production] MOD-TEST-227<br/>蓝图: MOD-TEST-227<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_228["[production] MOD-TEST-228<br/>蓝图: MOD-TEST-228<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_229["[production] MOD-TEST-229<br/>蓝图: MOD-TEST-229<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_230["[production] MOD-TEST-230<br/>蓝图: MOD-TEST-230<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_231["[production] MOD-TEST-231<br/>蓝图: MOD-TEST-231<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_232["[production] MOD-TEST-232<br/>蓝图: MOD-TEST-232<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_233["[production] MOD-TEST-233<br/>蓝图: MOD-TEST-233<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_234["[production] MOD-TEST-234<br/>蓝图: MOD-TEST-234<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_235["[production] MOD-TEST-235<br/>蓝图: MOD-TEST-235<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_236["[production] MOD-TEST-236<br/>蓝图: MOD-TEST-236<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_237["[production] MOD-TEST-237<br/>蓝图: MOD-TEST-237<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_238["[production] MOD-TEST-238<br/>蓝图: MOD-TEST-238<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_239["[production] MOD-TEST-239<br/>蓝图: MOD-TEST-239<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_240["[production] MOD-TEST-240<br/>蓝图: MOD-TEST-240<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_241["[production] MOD-TEST-241<br/>蓝图: MOD-TEST-241<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_242["[production] MOD-TEST-242<br/>蓝图: MOD-TEST-242<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_246["[production] MOD-TEST-246<br/>蓝图: MOD-TEST-246<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_247["[production] MOD-TEST-247<br/>蓝图: MOD-TEST-247<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_248["[production] MOD-TEST-248<br/>蓝图: MOD-TEST-248<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_250["[production] MOD-TEST-250<br/>蓝图: MOD-TEST-250<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_251["[production] MOD-TEST-251<br/>蓝图: MOD-TEST-251<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_252["[production] MOD-TEST-252<br/>蓝图: MOD-TEST-252<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_253["[production] MOD-TEST-253<br/>蓝图: MOD-TEST-253<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_254["[production] MOD-TEST-254<br/>蓝图: MOD-TEST-254<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_255["[production] MOD-TEST-255<br/>蓝图: MOD-TEST-255<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_256["[production] MOD-TEST-256<br/>蓝图: MOD-TEST-256<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_257["[production] MOD-TEST-257<br/>蓝图: MOD-TEST-257<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_258["[production] MOD-TEST-258<br/>蓝图: MOD-TEST-258<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_259["[production] MOD-TEST-259<br/>蓝图: MOD-TEST-259<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_260["[production] MOD-TEST-260<br/>蓝图: MOD-TEST-260<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_261["[production] MOD-TEST-261<br/>蓝图: MOD-TEST-261<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_262["[production] MOD-TEST-262<br/>蓝图: MOD-TEST-262<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_263["[production] MOD-TEST-263<br/>蓝图: MOD-TEST-263<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_264["[production] MOD-TEST-264<br/>蓝图: MOD-TEST-264<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_265["[production] MOD-TEST-265<br/>蓝图: MOD-TEST-265<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_266["[production] MOD-TEST-266<br/>蓝图: MOD-TEST-266<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_267["[production] MOD-TEST-267<br/>蓝图: MOD-TEST-267<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_268["[production] MOD-TEST-268<br/>蓝图: MOD-TEST-268<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_272["[production] MOD-TEST-272<br/>蓝图: MOD-TEST-272<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_273["[production] MOD-TEST-273<br/>蓝图: MOD-TEST-273<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_274["[production] MOD-TEST-274<br/>蓝图: MOD-TEST-274<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_275["[production] MOD-TEST-275<br/>蓝图: MOD-TEST-275<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_276["[production] MOD-TEST-276<br/>蓝图: MOD-TEST-276<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_277["[production] MOD-TEST-277<br/>蓝图: MOD-TEST-277<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_278["[production] MOD-TEST-278<br/>蓝图: MOD-TEST-278<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_279["[production] MOD-TEST-279<br/>蓝图: MOD-TEST-279<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_280["[production] MOD-TEST-280<br/>蓝图: MOD-TEST-280<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_281["[production] MOD-TEST-281<br/>蓝图: MOD-TEST-281<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_282["[production] MOD-TEST-282<br/>蓝图: MOD-TEST-282<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_283["[production] MOD-TEST-283<br/>蓝图: MOD-TEST-283<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_284["[production] MOD-TEST-284<br/>蓝图: MOD-TEST-284<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_285["[production] MOD-TEST-285<br/>蓝图: MOD-TEST-285<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_286["[production] MOD-TEST-286<br/>蓝图: MOD-TEST-286<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_287["[production] MOD-TEST-287<br/>蓝图: MOD-TEST-287<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_288["[production] MOD-TEST-288<br/>蓝图: MOD-TEST-288<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_289["[production] MOD-TEST-289<br/>蓝图: MOD-TEST-289<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_290["[production] MOD-TEST-290<br/>蓝图: MOD-TEST-290<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_291["[production] MOD-TEST-291<br/>蓝图: MOD-TEST-291<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_292["[production] MOD-TEST-292<br/>蓝图: MOD-TEST-292<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_293["[production] MOD-TEST-293<br/>蓝图: MOD-TEST-293<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_294["[production] MOD-TEST-294<br/>蓝图: MOD-TEST-294<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_295["[production] MOD-TEST-295<br/>蓝图: MOD-TEST-295<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_296["[production] MOD-TEST-296<br/>蓝图: MOD-TEST-296<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_297["[production] MOD-TEST-297<br/>蓝图: MOD-TEST-297<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_298["[production] MOD-TEST-298<br/>蓝图: MOD-TEST-298<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_299["[production] MOD-TEST-299<br/>蓝图: MOD-TEST-299<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_300["[production] MOD-TEST-300<br/>蓝图: MOD-TEST-300<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_301["[production] MOD-TEST-301<br/>蓝图: MOD-TEST-301<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_302["[production] MOD-TEST-302<br/>蓝图: MOD-TEST-302<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_303["[production] MOD-TEST-303<br/>蓝图: MOD-TEST-303<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_304["[production] MOD-TEST-304<br/>蓝图: MOD-TEST-304<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_305["[production] MOD-TEST-305<br/>蓝图: MOD-TEST-305<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_306["[production] MOD-TEST-306<br/>蓝图: MOD-TEST-306<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_307["[production] MOD-TEST-307<br/>蓝图: MOD-TEST-307<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_308["[production] MOD-TEST-308<br/>蓝图: MOD-TEST-308<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_309["[production] MOD-TEST-309<br/>蓝图: MOD-TEST-309<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_310["[production] MOD-TEST-310<br/>蓝图: MOD-TEST-310<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_311["[production] MOD-TEST-311<br/>蓝图: MOD-TEST-311<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_312["[production] MOD-TEST-312<br/>蓝图: MOD-TEST-312<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_313["[production] MOD-TEST-313<br/>蓝图: MOD-TEST-313<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_314["[production] MOD-TEST-314<br/>蓝图: MOD-TEST-314<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_315["[production] MOD-TEST-315<br/>蓝图: MOD-TEST-315<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_316["[production] MOD-TEST-316<br/>蓝图: MOD-TEST-316<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_319["[production] MOD-TEST-319<br/>蓝图: MOD-TEST-319<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_320["[production] MOD-TEST-320<br/>蓝图: MOD-TEST-320<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_322["[production] MOD-TEST-322<br/>蓝图: MOD-TEST-322<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_323["[production] MOD-TEST-323<br/>蓝图: MOD-TEST-323<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_324["[production] MOD-TEST-324<br/>蓝图: MOD-TEST-324<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_325["[production] MOD-TEST-325<br/>蓝图: MOD-TEST-325<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_326["[production] MOD-TEST-326<br/>蓝图: MOD-TEST-326<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_328["[production] MOD-TEST-328<br/>蓝图: MOD-TEST-328<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_329["[production] MOD-TEST-329<br/>蓝图: MOD-TEST-329<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_330["[production] MOD-TEST-330<br/>蓝图: MOD-TEST-330<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_331["[production] MOD-TEST-331<br/>蓝图: MOD-TEST-331<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_332["[production] MOD-TEST-332<br/>蓝图: MOD-TEST-332<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_333["[production] MOD-TEST-333<br/>蓝图: MOD-TEST-333<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_334["[production] MOD-TEST-334<br/>蓝图: MOD-TEST-334<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_335["[production] MOD-TEST-335<br/>蓝图: MOD-TEST-335<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_336["[production] MOD-TEST-336<br/>蓝图: MOD-TEST-336<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_337["[production] MOD-TEST-337<br/>蓝图: MOD-TEST-337<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_338["[production] MOD-TEST-338<br/>蓝图: MOD-TEST-338<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_339["[production] MOD-TEST-339<br/>蓝图: MOD-TEST-339<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_340["[production] MOD-TEST-340<br/>蓝图: MOD-TEST-340<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_342["[production] MOD-TEST-342<br/>蓝图: MOD-TEST-342<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_343["[production] MOD-TEST-343<br/>蓝图: MOD-TEST-343<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_344["[production] MOD-TEST-344<br/>蓝图: MOD-TEST-344<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_345["[production] MOD-TEST-345<br/>蓝图: MOD-TEST-345<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_346["[production] MOD-TEST-346<br/>蓝图: MOD-TEST-346<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_347["[production] MOD-TEST-347<br/>蓝图: MOD-TEST-347<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_348["[production] MOD-TEST-348<br/>蓝图: MOD-TEST-348<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_349["[production] MOD-TEST-349<br/>蓝图: MOD-TEST-349<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_350["[production] MOD-TEST-350<br/>蓝图: MOD-TEST-350<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_351["[production] MOD-TEST-351<br/>蓝图: MOD-TEST-351<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_354["[production] MOD-TEST-354<br/>蓝图: MOD-TEST-354<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_355["[production] MOD-TEST-355<br/>蓝图: MOD-TEST-355<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_356["[production] MOD-TEST-356<br/>蓝图: MOD-TEST-356<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_357["[production] MOD-TEST-357<br/>蓝图: MOD-TEST-357<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_358["[production] MOD-TEST-358<br/>蓝图: MOD-TEST-358<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_359["[production] MOD-TEST-359<br/>蓝图: MOD-TEST-359<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_360["[production] MOD-TEST-360<br/>蓝图: MOD-TEST-360<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_361["[production] MOD-TEST-361<br/>蓝图: MOD-TEST-361<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_362["[production] MOD-TEST-362<br/>蓝图: MOD-TEST-362<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_363["[production] MOD-TEST-363<br/>蓝图: MOD-TEST-363<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_364["[production] MOD-TEST-364<br/>蓝图: MOD-TEST-364<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_365["[production] MOD-TEST-365<br/>蓝图: MOD-TEST-365<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_366["[production] MOD-TEST-366<br/>蓝图: MOD-TEST-366<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_367["[production] MOD-TEST-367<br/>蓝图: MOD-TEST-367<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_368["[production] MOD-TEST-368<br/>蓝图: MOD-TEST-368<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_369["[production] MOD-TEST-369<br/>蓝图: MOD-TEST-369<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_370["[production] MOD-TEST-370<br/>蓝图: MOD-TEST-370<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_371["[production] MOD-TEST-371<br/>蓝图: MOD-TEST-371<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_372["[production] MOD-TEST-372<br/>蓝图: MOD-TEST-372<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_373["[production] MOD-TEST-373<br/>蓝图: MOD-TEST-373<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_374["[production] MOD-TEST-374<br/>蓝图: MOD-TEST-374<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_375["[production] MOD-TEST-375<br/>蓝图: MOD-TEST-375<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_376["[production] MOD-TEST-376<br/>蓝图: MOD-TEST-376<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_377["[production] MOD-TEST-377<br/>蓝图: MOD-TEST-377<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_378["[production] MOD-TEST-378<br/>蓝图: MOD-TEST-378<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_379["[production] MOD-TEST-379<br/>蓝图: MOD-TEST-379<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_380["[production] MOD-TEST-380<br/>蓝图: MOD-TEST-380<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_381["[production] MOD-TEST-381<br/>蓝图: MOD-TEST-381<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_382["[production] MOD-TEST-382<br/>蓝图: MOD-TEST-382<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_383["[production] MOD-TEST-383<br/>蓝图: MOD-TEST-383<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_384["[production] MOD-TEST-384<br/>蓝图: MOD-TEST-384<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_385["[production] MOD-TEST-385<br/>蓝图: MOD-TEST-385<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_386["[production] MOD-TEST-386<br/>蓝图: MOD-TEST-386<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_387["[production] MOD-TEST-387<br/>蓝图: MOD-TEST-387<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_388["[production] MOD-TEST-388<br/>蓝图: MOD-TEST-388<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_389["[production] MOD-TEST-389<br/>蓝图: MOD-TEST-389<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_390["[production] MOD-TEST-390<br/>蓝图: MOD-TEST-390<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_391["[production] MOD-TEST-391<br/>蓝图: MOD-TEST-391<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_392["[production] MOD-TEST-392<br/>蓝图: MOD-TEST-392<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_393["[production] MOD-TEST-393<br/>蓝图: MOD-TEST-393<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_394["[production] MOD-TEST-394<br/>蓝图: MOD-TEST-394<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_395["[production] MOD-TEST-395<br/>蓝图: MOD-TEST-395<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_396["[production] MOD-TEST-396<br/>蓝图: MOD-TEST-396<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_397["[production] MOD-TEST-397<br/>蓝图: MOD-TEST-397<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_402["[production] MOD-TEST-402<br/>蓝图: MOD-TEST-402<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_403["[production] MOD-TEST-403<br/>蓝图: MOD-TEST-403<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_404["[production] MOD-TEST-404<br/>蓝图: MOD-TEST-404<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_406["[production] MOD-TEST-406<br/>蓝图: MOD-TEST-406<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_407["[production] MOD-TEST-407<br/>蓝图: MOD-TEST-407<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_408["[production] MOD-TEST-408<br/>蓝图: MOD-TEST-408<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_409["[production] MOD-TEST-409<br/>蓝图: MOD-TEST-409<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_410["[production] MOD-TEST-410<br/>蓝图: MOD-TEST-410<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_411["[production] MOD-TEST-411<br/>蓝图: MOD-TEST-411<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_412["[production] MOD-TEST-412<br/>蓝图: MOD-TEST-412<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_413["[production] MOD-TEST-413<br/>蓝图: MOD-TEST-413<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_414["[production] MOD-TEST-414<br/>蓝图: MOD-TEST-414<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_415["[production] MOD-TEST-415<br/>蓝图: MOD-TEST-415<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_416["[production] MOD-TEST-416<br/>蓝图: MOD-TEST-416<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_417["[production] MOD-TEST-417<br/>蓝图: MOD-TEST-417<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_418["[production] MOD-TEST-418<br/>蓝图: MOD-TEST-418<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_419["[production] MOD-TEST-419<br/>蓝图: MOD-TEST-419<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_420["[production] MOD-TEST-420<br/>蓝图: MOD-TEST-420<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_421["[production] MOD-TEST-421<br/>蓝图: MOD-TEST-421<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_422["[production] MOD-TEST-422<br/>蓝图: MOD-TEST-422<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_423["[production] MOD-TEST-423<br/>蓝图: MOD-TEST-423<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_424["[production] MOD-TEST-424<br/>蓝图: MOD-TEST-424<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_425["[production] MOD-TEST-425<br/>蓝图: MOD-TEST-425<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_426["[production] MOD-TEST-426<br/>蓝图: MOD-TEST-426<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_427["[production] MOD-TEST-427<br/>蓝图: MOD-TEST-427<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_428["[production] MOD-TEST-428<br/>蓝图: MOD-TEST-428<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_429["[production] MOD-TEST-429<br/>蓝图: MOD-TEST-429<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_430["[production] MOD-TEST-430<br/>蓝图: MOD-TEST-430<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_431["[production] MOD-TEST-431<br/>蓝图: MOD-TEST-431<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_432["[production] MOD-TEST-432<br/>蓝图: MOD-TEST-432<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_433["[production] MOD-TEST-433<br/>蓝图: MOD-TEST-433<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_434["[production] MOD-TEST-434<br/>蓝图: MOD-TEST-434<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_435["[production] MOD-TEST-435<br/>蓝图: MOD-TEST-435<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_436["[production] MOD-TEST-436<br/>蓝图: MOD-TEST-436<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_437["[production] MOD-TEST-437<br/>蓝图: MOD-TEST-437<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_438["[production] MOD-TEST-438<br/>蓝图: MOD-TEST-438<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_439["[production] MOD-TEST-439<br/>蓝图: MOD-TEST-439<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_440["[production] MOD-TEST-440<br/>蓝图: MOD-TEST-440<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_441["[production] MOD-TEST-441<br/>蓝图: MOD-TEST-441<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_444["[production] MOD-TEST-444<br/>蓝图: MOD-TEST-444<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_447["[production] MOD-TEST-447<br/>蓝图: MOD-TEST-447<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_449["[production] MOD-TEST-449<br/>蓝图: MOD-TEST-449<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_450["[production] MOD-TEST-450<br/>蓝图: MOD-TEST-450<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_452["[production] MOD-TEST-452<br/>蓝图: MOD-TEST-452<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_454["[production] MOD-TEST-454<br/>蓝图: MOD-TEST-454<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_455["[production] MOD-TEST-455<br/>蓝图: MOD-TEST-455<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_456["[production] MOD-TEST-456<br/>蓝图: MOD-TEST-456<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_457["[production] MOD-TEST-457<br/>蓝图: MOD-TEST-457<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_459["[production] MOD-TEST-459<br/>蓝图: MOD-TEST-459<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_460["[production] MOD-TEST-460<br/>蓝图: MOD-TEST-460<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_461["[production] MOD-TEST-461<br/>蓝图: MOD-TEST-461<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_462["[production] MOD-TEST-462<br/>蓝图: MOD-TEST-462<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_463["[production] MOD-TEST-463<br/>蓝图: MOD-TEST-463<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_464["[production] MOD-TEST-464<br/>蓝图: MOD-TEST-464<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_466["[production] MOD-TEST-466<br/>蓝图: MOD-TEST-466<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_467["[production] MOD-TEST-467<br/>蓝图: MOD-TEST-467<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_468["[production] MOD-TEST-468<br/>蓝图: MOD-TEST-468<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_469["[production] MOD-TEST-469<br/>蓝图: MOD-TEST-469<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_470["[production] MOD-TEST-470<br/>蓝图: MOD-TEST-470<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_471["[production] MOD-TEST-471<br/>蓝图: MOD-TEST-471<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_472["[production] MOD-TEST-472<br/>蓝图: MOD-TEST-472<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_473["[production] MOD-TEST-473<br/>蓝图: MOD-TEST-473<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_475["[production] MOD-TEST-475<br/>蓝图: MOD-TEST-475<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_476["[production] MOD-TEST-476<br/>蓝图: MOD-TEST-476<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_477["[production] MOD-TEST-477<br/>蓝图: MOD-TEST-477<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_479["[production] MOD-TEST-479<br/>蓝图: MOD-TEST-479<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_481["[production] MOD-TEST-481<br/>蓝图: MOD-TEST-481<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_482["[production] MOD-TEST-482<br/>蓝图: MOD-TEST-482<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_484["[production] MOD-TEST-484<br/>蓝图: MOD-TEST-484<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_485["[production] MOD-TEST-485<br/>蓝图: MOD-TEST-485<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_487["[production] MOD-TEST-487<br/>蓝图: MOD-TEST-487<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_488["[production] MOD-TEST-488<br/>蓝图: MOD-TEST-488<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_489["[production] MOD-TEST-489<br/>蓝图: MOD-TEST-489<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_490["[production] MOD-TEST-490<br/>蓝图: MOD-TEST-490<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_491["[production] MOD-TEST-491<br/>蓝图: MOD-TEST-491<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_492["[production] MOD-TEST-492<br/>蓝图: MOD-TEST-492<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_494["[production] MOD-TEST-494<br/>蓝图: MOD-TEST-494<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_495["[production] MOD-TEST-495<br/>蓝图: MOD-TEST-495<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_496["[production] MOD-TEST-496<br/>蓝图: MOD-TEST-496<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_497["[production] MOD-TEST-497<br/>蓝图: MOD-TEST-497<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_498["[production] MOD-TEST-498<br/>蓝图: MOD-TEST-498<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_499["[production] MOD-TEST-499<br/>蓝图: MOD-TEST-499<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_501["[production] MOD-TEST-501<br/>蓝图: MOD-TEST-501<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_502["[production] MOD-TEST-502<br/>蓝图: MOD-TEST-502<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_504["[production] MOD-TEST-504<br/>蓝图: MOD-TEST-504<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_505["[production] MOD-TEST-505<br/>蓝图: MOD-TEST-505<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_506["[production] MOD-TEST-506<br/>蓝图: MOD-TEST-506<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_508["[production] MOD-TEST-508<br/>蓝图: MOD-TEST-508<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_509["[production] MOD-TEST-509<br/>蓝图: MOD-TEST-509<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_510["[production] MOD-TEST-510<br/>蓝图: MOD-TEST-510<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_511["[production] MOD-TEST-511<br/>蓝图: MOD-TEST-511<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_512["[production] MOD-TEST-512<br/>蓝图: MOD-TEST-512<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_513["[production] MOD-TEST-513<br/>蓝图: MOD-TEST-513<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_514["[production] MOD-TEST-514<br/>蓝图: MOD-TEST-514<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_528["[production] MOD-TEST-528<br/>蓝图: MOD-TEST-528<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_529["[production] MOD-TEST-529<br/>蓝图: MOD-TEST-529<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_530["[production] MOD-TEST-530<br/>蓝图: MOD-TEST-530<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_532["[production] MOD-TEST-532<br/>蓝图: MOD-TEST-532<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_533["[production] MOD-TEST-533<br/>蓝图: MOD-TEST-533<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_534["[production] MOD-TEST-534<br/>蓝图: MOD-TEST-534<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_535["[production] MOD-TEST-535<br/>蓝图: MOD-TEST-535<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_536["[production] MOD-TEST-536<br/>蓝图: MOD-TEST-536<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_537["[production] MOD-TEST-537<br/>蓝图: MOD-TEST-537<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_538["[production] MOD-TEST-538<br/>蓝图: MOD-TEST-538<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_539["[production] MOD-TEST-539<br/>蓝图: MOD-TEST-539<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_540["[production] MOD-TEST-540<br/>蓝图: MOD-TEST-540<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_541["[production] MOD-TEST-541<br/>蓝图: MOD-TEST-541<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_543["[production] MOD-TEST-543<br/>蓝图: MOD-TEST-543<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_544["[production] MOD-TEST-544<br/>蓝图: MOD-TEST-544<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_545["[production] MOD-TEST-545<br/>蓝图: MOD-TEST-545<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_547["[production] MOD-TEST-547<br/>蓝图: MOD-TEST-547<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_548["[production] MOD-TEST-548<br/>蓝图: MOD-TEST-548<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_549["[production] MOD-TEST-549<br/>蓝图: MOD-TEST-549<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_550["[production] MOD-TEST-550<br/>蓝图: MOD-TEST-550<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_551["[production] MOD-TEST-551<br/>蓝图: MOD-TEST-551<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_552["[production] MOD-TEST-552<br/>蓝图: MOD-TEST-552<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_553["[production] MOD-TEST-553<br/>蓝图: MOD-TEST-553<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_554["[production] MOD-TEST-554<br/>蓝图: MOD-TEST-554<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_555["[production] MOD-TEST-555<br/>蓝图: MOD-TEST-555<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_557["[production] MOD-TEST-557<br/>蓝图: MOD-TEST-557<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_558["[production] MOD-TEST-558<br/>蓝图: MOD-TEST-558<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_559["[production] MOD-TEST-559<br/>蓝图: MOD-TEST-559<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_560["[production] MOD-TEST-560<br/>蓝图: MOD-TEST-560<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_561["[production] MOD-TEST-561<br/>蓝图: MOD-TEST-561<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_562["[production] MOD-TEST-562<br/>蓝图: MOD-TEST-562<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_563["[production] MOD-TEST-563<br/>蓝图: MOD-TEST-563<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_564["[production] MOD-TEST-564<br/>蓝图: MOD-TEST-564<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_565["[production] MOD-TEST-565<br/>蓝图: MOD-TEST-565<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_566["[production] MOD-TEST-566<br/>蓝图: MOD-TEST-566<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_567["[production] MOD-TEST-567<br/>蓝图: MOD-TEST-567<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_568["[production] MOD-TEST-568<br/>蓝图: MOD-TEST-568<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_569["[production] MOD-TEST-569<br/>蓝图: MOD-TEST-569<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_570["[production] MOD-TEST-570<br/>蓝图: MOD-TEST-570<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_571["[production] MOD-TEST-571<br/>蓝图: MOD-TEST-571<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_572["[production] MOD-TEST-572<br/>蓝图: MOD-TEST-572<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_573["[production] MOD-TEST-573<br/>蓝图: MOD-TEST-573<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_574["[production] MOD-TEST-574<br/>蓝图: MOD-TEST-574<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_575["[production] MOD-TEST-575<br/>蓝图: MOD-TEST-575<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_576["[production] MOD-TEST-576<br/>蓝图: MOD-TEST-576<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_577["[production] MOD-TEST-577<br/>蓝图: MOD-TEST-577<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_579["[production] MOD-TEST-579<br/>蓝图: MOD-TEST-579<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_580["[production] MOD-TEST-580<br/>蓝图: MOD-TEST-580<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_582["[production] MOD-TEST-582<br/>蓝图: MOD-TEST-582<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_583["[production] MOD-TEST-583<br/>蓝图: MOD-TEST-583<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_584["[production] MOD-TEST-584<br/>蓝图: MOD-TEST-584<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_585["[production] MOD-TEST-585<br/>蓝图: MOD-TEST-585<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_586["[production] MOD-TEST-586<br/>蓝图: MOD-TEST-586<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_587["[production] MOD-TEST-587<br/>蓝图: MOD-TEST-587<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_588["[production] MOD-TEST-588<br/>蓝图: MOD-TEST-588<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_590["[production] MOD-TEST-590<br/>蓝图: MOD-TEST-590<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_591["[production] MOD-TEST-591<br/>蓝图: MOD-TEST-591<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_592["[production] MOD-TEST-592<br/>蓝图: MOD-TEST-592<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_593["[production] MOD-TEST-593<br/>蓝图: MOD-TEST-593<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_594["[production] MOD-TEST-594<br/>蓝图: MOD-TEST-594<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_595["[production] MOD-TEST-595<br/>蓝图: MOD-TEST-595<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_597["[production] MOD-TEST-597<br/>蓝图: MOD-TEST-597<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_598["[production] MOD-TEST-598<br/>蓝图: MOD-TEST-598<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_599["[production] MOD-TEST-599<br/>蓝图: MOD-TEST-599<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_600["[production] MOD-TEST-600<br/>蓝图: MOD-TEST-600<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_601["[production] MOD-TEST-601<br/>蓝图: MOD-TEST-601<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_602["[production] MOD-TEST-602<br/>蓝图: MOD-TEST-602<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_603["[production] MOD-TEST-603<br/>蓝图: MOD-TEST-603<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_604["[production] MOD-TEST-604<br/>蓝图: MOD-TEST-604<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_605["[production] MOD-TEST-605<br/>蓝图: MOD-TEST-605<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_606["[production] MOD-TEST-606<br/>蓝图: MOD-TEST-606<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_607["[production] MOD-TEST-607<br/>蓝图: MOD-TEST-607<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_608["[production] MOD-TEST-608<br/>蓝图: MOD-TEST-608<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_609["[production] MOD-TEST-609<br/>蓝图: MOD-TEST-609<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_610["[production] MOD-TEST-610<br/>蓝图: MOD-TEST-610<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_611["[production] MOD-TEST-611<br/>蓝图: MOD-TEST-611<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_612["[production] MOD-TEST-612<br/>蓝图: MOD-TEST-612<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_613["[production] MOD-TEST-613<br/>蓝图: MOD-TEST-613<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_614["[production] MOD-TEST-614<br/>蓝图: MOD-TEST-614<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_616["[production] MOD-TEST-616<br/>蓝图: MOD-TEST-616<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_617["[production] MOD-TEST-617<br/>蓝图: MOD-TEST-617<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_618["[production] MOD-TEST-618<br/>蓝图: MOD-TEST-618<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_619["[production] MOD-TEST-619<br/>蓝图: MOD-TEST-619<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_620["[production] MOD-TEST-620<br/>蓝图: MOD-TEST-620<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_621["[production] MOD-TEST-621<br/>蓝图: MOD-TEST-621<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_622["[production] MOD-TEST-622<br/>蓝图: MOD-TEST-622<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_623["[production] MOD-TEST-623<br/>蓝图: MOD-TEST-623<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_624["[production] MOD-TEST-624<br/>蓝图: MOD-TEST-624<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_625["[production] MOD-TEST-625<br/>蓝图: MOD-TEST-625<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_626["[production] MOD-TEST-626<br/>蓝图: MOD-TEST-626<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_627["[production] MOD-TEST-627<br/>蓝图: MOD-TEST-627<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_628["[production] MOD-TEST-628<br/>蓝图: MOD-TEST-628<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_629["[production] MOD-TEST-629<br/>蓝图: MOD-TEST-629<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_630["[production] MOD-TEST-630<br/>蓝图: MOD-TEST-630<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_631["[production] MOD-TEST-631<br/>蓝图: MOD-TEST-631<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_633["[production] MOD-TEST-633<br/>蓝图: MOD-TEST-633<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_634["[production] MOD-TEST-634<br/>蓝图: MOD-TEST-634<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_635["[production] MOD-TEST-635<br/>蓝图: MOD-TEST-635<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_636["[production] MOD-TEST-636<br/>蓝图: MOD-TEST-636<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_637["[production] MOD-TEST-637<br/>蓝图: MOD-TEST-637<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_639["[production] MOD-TEST-639<br/>蓝图: MOD-TEST-639<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_640["[production] MOD-TEST-640<br/>蓝图: MOD-TEST-640<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_641["[production] MOD-TEST-641<br/>蓝图: MOD-TEST-641<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_642["[production] MOD-TEST-642<br/>蓝图: MOD-TEST-642<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_643["[production] MOD-TEST-643<br/>蓝图: MOD-TEST-643<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_644["[production] MOD-TEST-644<br/>蓝图: MOD-TEST-644<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_646["[production] MOD-TEST-646<br/>蓝图: MOD-TEST-646<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_647["[production] MOD-TEST-647<br/>蓝图: MOD-TEST-647<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_648["[production] MOD-TEST-648<br/>蓝图: MOD-TEST-648<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_649["[production] MOD-TEST-649<br/>蓝图: MOD-TEST-649<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_651["[production] MOD-TEST-651<br/>蓝图: MOD-TEST-651<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_652["[production] MOD-TEST-652<br/>蓝图: MOD-TEST-652<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_653["[production] MOD-TEST-653<br/>蓝图: MOD-TEST-653<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_654["[production] MOD-TEST-654<br/>蓝图: MOD-TEST-654<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_655["[production] MOD-TEST-655<br/>蓝图: MOD-TEST-655<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_660["[production] MOD-TEST-660<br/>蓝图: MOD-TEST-660<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_661["[production] MOD-TEST-661<br/>蓝图: MOD-TEST-661<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_662["[production] MOD-TEST-662<br/>蓝图: MOD-TEST-662<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_663["[production] MOD-TEST-663<br/>蓝图: MOD-TEST-663<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_664["[production] MOD-TEST-664<br/>蓝图: MOD-TEST-664<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_665["[production] MOD-TEST-665<br/>蓝图: MOD-TEST-665<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_668["[production] MOD-TEST-668<br/>蓝图: MOD-TEST-668<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_669["[production] MOD-TEST-669<br/>蓝图: MOD-TEST-669<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_670["[production] MOD-TEST-670<br/>蓝图: MOD-TEST-670<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_671["[production] MOD-TEST-671<br/>蓝图: MOD-TEST-671<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_672["[production] MOD-TEST-672<br/>蓝图: MOD-TEST-672<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_673["[production] MOD-TEST-673<br/>蓝图: MOD-TEST-673<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_674["[production] MOD-TEST-674<br/>蓝图: MOD-TEST-674<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_675["[production] MOD-TEST-675<br/>蓝图: MOD-TEST-675<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_676["[production] MOD-TEST-676<br/>蓝图: MOD-TEST-676<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_677["[production] MOD-TEST-677<br/>蓝图: MOD-TEST-677<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_678["[production] MOD-TEST-678<br/>蓝图: MOD-TEST-678<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_679["[production] MOD-TEST-679<br/>蓝图: MOD-TEST-679<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_680["[production] MOD-TEST-680<br/>蓝图: MOD-TEST-680<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_681["[production] MOD-TEST-681<br/>蓝图: MOD-TEST-681<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_682["[production] MOD-TEST-682<br/>蓝图: MOD-TEST-682<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_683["[production] MOD-TEST-683<br/>蓝图: MOD-TEST-683<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_684["[production] MOD-TEST-684<br/>蓝图: MOD-TEST-684<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_685["[production] MOD-TEST-685<br/>蓝图: MOD-TEST-685<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_686["[production] MOD-TEST-686<br/>蓝图: MOD-TEST-686<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_687["[production] MOD-TEST-687<br/>蓝图: MOD-TEST-687<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_688["[production] MOD-TEST-688<br/>蓝图: MOD-TEST-688<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_689["[production] MOD-TEST-689<br/>蓝图: MOD-TEST-689<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_690["[production] MOD-TEST-690<br/>蓝图: MOD-TEST-690<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_691["[production] MOD-TEST-691<br/>蓝图: MOD-TEST-691<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_692["[production] MOD-TEST-692<br/>蓝图: MOD-TEST-692<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_693["[production] MOD-TEST-693<br/>蓝图: MOD-TEST-693<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_694["[production] MOD-TEST-694<br/>蓝图: MOD-TEST-694<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_695["[production] MOD-TEST-695<br/>蓝图: MOD-TEST-695<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_696["[production] MOD-TEST-696<br/>蓝图: MOD-TEST-696<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_697["[production] MOD-TEST-697<br/>蓝图: MOD-TEST-697<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_698["[production] MOD-TEST-698<br/>蓝图: MOD-TEST-698<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_699["[production] MOD-TEST-699<br/>蓝图: MOD-TEST-699<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_700["[production] MOD-TEST-700<br/>蓝图: MOD-TEST-700<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_701["[production] MOD-TEST-701<br/>蓝图: MOD-TEST-701<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_702["[production] MOD-TEST-702<br/>蓝图: MOD-TEST-702<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_703["[production] MOD-TEST-703<br/>蓝图: MOD-TEST-703<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_704["[production] MOD-TEST-704<br/>蓝图: MOD-TEST-704<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_705["[production] MOD-TEST-705<br/>蓝图: MOD-TEST-705<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_706["[production] MOD-TEST-706<br/>蓝图: MOD-TEST-706<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_708["[production] MOD-TEST-708<br/>蓝图: MOD-TEST-708<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_710["[production] MOD-TEST-710<br/>蓝图: MOD-TEST-710<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_apply_depgraph_smoke["[production] MOD-TEST-apply_depgraph_smoke<br/>蓝图: MOD-TEST-apply_depgraph_smoke<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TEST_apply_depgraph_smoke["[production] MOD-TEST_apply_depgraph_smoke<br/>蓝图: MOD-TEST_apply_depgraph_smoke<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_TRADING_001["[production] MOD-TRADING-001<br/>蓝图: MOD-TRADING-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_WORKSPACE_TELEMETRY["[production] MOD-WORKSPACE_TELEMETRY<br/>蓝图: MOD-WORKSPACE_TELEMETRY<br/>成熟度: production<br/>build: stable"]:::bsStable
    LMOD_XLR_003["[production] MOD-XLR-003<br/>蓝图: MOD-XLR-003<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_migrate_sqlite_to_pg["[production] MOD-migrate_sqlite_to_pg<br/>蓝图: MOD-migrate_sqlite_to_pg<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LMOD_readme_version_sync["[production] MOD-readme_version_sync<br/>蓝图: MOD-readme_version_sync<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LPLACEHOLDER_MOD_GOV_SYNC_PANORAMA["[design] PLACEHOLDER-MOD-GOV-SYNC-PANORAMA<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LSH_DB_001["[design] SH-DB-001<br/>成熟度: design<br/>build: planned"]:::bsPlanned
    LSH_DB_002["[production] SH-DB-002<br/>蓝图: SH-DB-002<br/>成熟度: production<br/>build: stable"]:::bsStable
    LSH_GOV_003["[production] SH-GOV-003<br/>蓝图: SH-GOV-003<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LSH_GOV_004["[production] SH-GOV-004<br/>蓝图: SH-GOV-004<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LSH_MAIN_001["[production] SH-MAIN-001<br/>蓝图: SH-MAIN-001<br/>成熟度: production<br/>build: generated"]:::bsGenerated
    LSYS_MASTER_001["[design] SYS-MASTER-001<br/>成熟度: design<br/>build: stable"]:::bsStable
    LCFG_rule_enforcement_registry -->|triggering| LCFG_rule_registry_collection
    LCFG_rule_registry_collection -->|triggering| LCFG_scripts_registry
    LCFG_scripts_registry -->|triggering| LCFG_test_suite_registry
    LCFG_test_suite_registry -->|triggering| LINFRA_DB_001
    LINFRA_DB_001 -->|triggering| LINFRA_DB_002
    LINFRA_DB_002 -->|triggering| LINFRA_DB_003
    LINFRA_DB_003 -->|triggering| LINFRA_DB_006
    LINFRA_DB_006 -->|triggering| LL0
    LL0 -->|triggering| LL1
    LL1 -->|triggering| LL2A
    LL2A -->|triggering| LL2B
    LL2B -->|triggering| LL2C
    LL2C -->|triggering| LL2D
    LL2D -->|triggering| LL3
    LL3 -->|triggering| LL4
    LL4 -->|triggering| LL5
    LL5 -->|triggering| LL6
    LL6 -->|triggering| LMOD_ALT_DATA
    LMOD_ALT_DATA -->|triggering| LMOD_ARCH_BIZDB
    LMOD_ARCH_BIZDB -->|triggering| LMOD_AUTONOMY_CORE
    LMOD_AUTONOMY_CORE -->|triggering| LMOD_BT_001
    LMOD_BT_001 -->|triggering| LMOD_C1_MARKETCH
    LMOD_C1_MARKETCH -->|triggering| LMOD_CONTEXT_ENGINE
    LMOD_CONTEXT_ENGINE -->|triggering| LMOD_CROSS_ASSET
    LMOD_CROSS_ASSET -->|triggering| LMOD_D5_ARCH_TOOLS
    LMOD_D5_ARCH_TOOLS -->|triggering| LMOD_DATABASE
    LMOD_DATABASE -->|triggering| LMOD_DATA_ENG
    LMOD_DATA_ENG -->|triggering| LMOD_DATA_GOV
    LMOD_DATA_GOV -->|triggering| LMOD_DATA_SEC
    LMOD_DATA_SEC -->|triggering| LMOD_DIGITAL_TWIN
    LMOD_DIGITAL_TWIN -->|triggering| LMOD_EXEC_SIM
    LMOD_EXEC_SIM -->|triggering| LMOD_EX_SOR
    LMOD_EX_SOR -->|triggering| LMOD_FEEDBACK_LOOP
    LMOD_FEEDBACK_LOOP -->|triggering| LMOD_GATE_ENGINE
    LMOD_GATE_ENGINE -->|triggering| LMOD_GOV_019
    LMOD_GOV_019 -->|triggering| LMOD_GOV_029
    LMOD_GOV_029 -->|triggering| LMOD_GOV_041
    LMOD_GOV_041 -->|triggering| LMOD_GOV_ALIGN_PANORAMAS
    LMOD_GOV_ALIGN_PANORAMAS -->|triggering| LMOD_GOV_DOCS
    LMOD_GOV_DOCS -->|triggering| LMOD_GOV_REPAIR
    LMOD_GOV_REPAIR -->|triggering| LMOD_GOV_SCRIPTS
    LMOD_GOV_SCRIPTS -->|triggering| LMOD_GOV_SCRIPTS_ARCH
    LMOD_GOV_SCRIPTS_ARCH -->|triggering| LMOD_GOV_SYNC_PANORAMA
    LMOD_GOV_SYNC_PANORAMA -->|triggering| LMOD_GOV_arch_reference_gate
    LMOD_GOV_arch_reference_gate -->|triggering| LMOD_GOV_audit_return_contract_usage
    LMOD_GOV_audit_return_contract_usage -->|triggering| LMOD_GOV_audit_worktree_ops_telemetry
    LMOD_GOV_audit_worktree_ops_telemetry -->|triggering| LMOD_GOV_bare_getenv_gate
    LMOD_GOV_bare_getenv_gate -->|triggering| LMOD_GOV_bare_sql_gate
    LMOD_GOV_bare_sql_gate -->|triggering| LMOD_GOV_batched_auto_committer
    LMOD_GOV_batched_auto_committer -->|triggering| LMOD_GOV_blueprint_amodule_consistency_gate
    LMOD_GOV_blueprint_amodule_consistency_gate -->|triggering| LMOD_GOV_capability_overlap_gate
    LMOD_GOV_capability_overlap_gate -->|triggering| LMOD_GOV_check_vocab_hardcode
    LMOD_GOV_check_vocab_hardcode -->|triggering| LMOD_GOV_claim_required_gate
    LMOD_GOV_claim_required_gate -->|triggering| LMOD_GOV_commit_gate_registry
    LMOD_GOV_commit_gate_registry -->|triggering| LMOD_GOV_commit_gates
    LMOD_GOV_commit_gates -->|triggering| LMOD_GOV_create_guard
    LMOD_GOV_create_guard -->|triggering| LMOD_GOV_dangling_reference_gate
    LMOD_GOV_dangling_reference_gate -->|triggering| LMOD_GOV_diff_helpers
    LMOD_GOV_diff_helpers -->|triggering| LMOD_GOV_doc_ref_broken_gate
    LMOD_GOV_doc_ref_broken_gate -->|triggering| LMOD_GOV_domain_fk_gate
    LMOD_GOV_domain_fk_gate -->|triggering| LMOD_GOV_emergency_commit
    LMOD_GOV_emergency_commit -->|triggering| LMOD_GOV_empty_handler_gate
    LMOD_GOV_empty_handler_gate -->|triggering| LMOD_GOV_exempt_zone_frontmatter_gate
    LMOD_GOV_exempt_zone_frontmatter_gate -->|triggering| LMOD_GOV_file_copy_gate
    LMOD_GOV_file_copy_gate -->|triggering| LMOD_GOV_function_dup_gate
    LMOD_GOV_function_dup_gate -->|triggering| LMOD_GOV_god_class_gate
    LMOD_GOV_god_class_gate -->|triggering| LMOD_GOV_hardcoded_url_gate
    LMOD_GOV_hardcoded_url_gate -->|triggering| LMOD_GOV_held_overlap_gate
    LMOD_GOV_held_overlap_gate -->|triggering| LMOD_GOV_high_complexity_gate
    LMOD_GOV_high_complexity_gate -->|triggering| LMOD_GOV_id_uniqueness_gate
    LMOD_GOV_id_uniqueness_gate -->|triggering| LMOD_GOV_import_direction_gate
    LMOD_GOV_import_direction_gate -->|triggering| LMOD_GOV_long_param_list_gate
    LMOD_GOV_long_param_list_gate -->|triggering| LMOD_GOV_manual_only_permanent_gate
    LMOD_GOV_manual_only_permanent_gate -->|triggering| LMOD_GOV_migrate_metadata
    LMOD_GOV_migrate_metadata -->|triggering| LMOD_GOV_module_id_consistency_gate
    LMOD_GOV_module_id_consistency_gate -->|triggering| LMOD_GOV_no_import_side_effect_gate
    LMOD_GOV_no_import_side_effect_gate -->|triggering| LMOD_GOV_orphan_module_gate
    LMOD_GOV_orphan_module_gate -->|triggering| LMOD_GOV_panorama_alignment_gate
    LMOD_GOV_panorama_alignment_gate -->|triggering| LMOD_GOV_perm_trigger_gate
    LMOD_GOV_perm_trigger_gate -->|triggering| LMOD_GOV_pre_write_gate
    LMOD_GOV_pre_write_gate -->|triggering| LMOD_GOV_r5_digit_suffix_gate
    LMOD_GOV_r5_digit_suffix_gate -->|triggering| LMOD_GOV_reconcile_runner
    LMOD_GOV_reconcile_runner -->|triggering| LMOD_GOV_reconcile_worker
    LMOD_GOV_reconcile_worker -->|triggering| LMOD_GOV_reconciliation_registry
    LMOD_GOV_reconciliation_registry -->|triggering| LMOD_GOV_rename_depgraph_sync_gate
    LMOD_GOV_rename_depgraph_sync_gate -->|triggering| LMOD_GOV_rule_execution_pairing_gate
    LMOD_GOV_rule_execution_pairing_gate -->|triggering| LMOD_GOV_rule_four_way_alignment_gate
    LMOD_GOV_rule_four_way_alignment_gate -->|triggering| LMOD_GOV_rule_patterns
    LMOD_GOV_rule_patterns -->|triggering| LMOD_GOV_ruling_reference_gate
    LMOD_GOV_ruling_reference_gate -->|triggering| LMOD_GOV_run_silent_failure_regression
    LMOD_GOV_run_silent_failure_regression -->|triggering| LMOD_GOV_session_claim
    LMOD_GOV_session_claim -->|triggering| LMOD_GOV_session_required_gate
    LMOD_GOV_session_required_gate -->|triggering| LMOD_GOV_session_startup_health_check
    LMOD_GOV_session_startup_health_check -->|triggering| LMOD_GOV_session_worktree
    LMOD_GOV_session_worktree -->|triggering| LMOD_GOV_ssot_redefinition_gate
    LMOD_GOV_ssot_redefinition_gate -->|triggering| LMOD_GOV_test_claim_files_for_edit
    LMOD_GOV_test_claim_files_for_edit -->|triggering| LMOD_GOV_test_emergency_commit
    LMOD_GOV_test_emergency_commit -->|triggering| LMOD_GOV_test_reconcile_async
    LMOD_GOV_test_reconcile_async -->|triggering| LMOD_GOV_test_source_consistency_gate
    LMOD_GOV_test_source_consistency_gate -->|triggering| LMOD_GOV_vocab_hardcode_gate
    LMOD_GOV_vocab_hardcode_gate -->|triggering| LMOD_GOV_workspace_hygiene_reconciler
    LMOD_GOV_workspace_hygiene_reconciler -->|triggering| LMOD_GOV_worktree_manager
    LMOD_GOV_worktree_manager -->|triggering| LMOD_GOVERNANCE
    LMOD_GOVERNANCE -->|triggering| LMOD_GOV_COMMON
    LMOD_GOV_COMMON -->|triggering| LMOD_GOV_DATAFLOW_DIAGRAM
    LMOD_GOV_DATAFLOW_DIAGRAM -->|triggering| LMOD_GOV_DQ
    LMOD_GOV_DQ -->|triggering| LMOD_GOV_ENFORCEMENT
    LMOD_GOV_ENFORCEMENT -->|triggering| LMOD_GOV_ENFORCEMENT_worktree_pool
    LMOD_GOV_ENFORCEMENT_worktree_pool -->|triggering| LMOD_GOV_GATE_CACHE
    LMOD_GOV_GATE_CACHE -->|triggering| LMOD_GOV_HEALTH_SMOKE
    LMOD_GOV_HEALTH_SMOKE -->|triggering| LMOD_GOV_SILENT_FAILURE_REGRESSION
    LMOD_GOV_SILENT_FAILURE_REGRESSION -->|triggering| LMOD_GOV_behavioral_admission
    LMOD_GOV_behavioral_admission -->|triggering| LMOD_GOV_code_quality_domain
    LMOD_GOV_code_quality_domain -->|triggering| LMOD_GOV_commit_gates
    LMOD_GOV_commit_gates -->|triggering| LMOD_GOV_commit_gateway_abuse_monitor
    LMOD_GOV_commit_gateway_abuse_monitor -->|triggering| LMOD_GOV_git_performance_monitor
    LMOD_GOV_git_performance_monitor -->|triggering| LMOD_GOV_guc_trigger_fix
    LMOD_GOV_guc_trigger_fix -->|triggering| LMOD_GOV_resilience_governance
    LMOD_GOV_resilience_governance -->|triggering| LMOD_GOV_rule_domain
    LMOD_GOV_rule_domain -->|triggering| LMOD_GOV_rule_execution_pairing_gate
    LMOD_GOV_rule_execution_pairing_gate -->|triggering| LMOD_GOV_runtime_violation_snapshot
    LMOD_GOV_runtime_violation_snapshot -->|triggering| LMOD_GOV_runtime_violation_snapshot_reconciler
    LMOD_GOV_runtime_violation_snapshot_reconciler -->|triggering| LMOD_GOV_security_governance
    LMOD_GOV_security_governance -->|triggering| LMOD_GOV_sync_savepoint_test
    LMOD_GOV_sync_savepoint_test -->|triggering| LMOD_GOV_yaml_sync_error_class
    LMOD_GOV_yaml_sync_error_class -->|triggering| LMOD_INF_001
    LMOD_INF_001 -->|triggering| LMOD_INF_002
    LMOD_INF_002 -->|triggering| LMOD_INF_003
    LMOD_INF_003 -->|triggering| LMOD_INF_005
    LMOD_INF_005 -->|triggering| LMOD_INF_009
    LMOD_INF_009 -->|triggering| LMOD_INF_011
    LMOD_INF_011 -->|triggering| LMOD_INF_013
    LMOD_INF_013 -->|triggering| LMOD_INF_014
    LMOD_INF_014 -->|triggering| LMOD_INF_015
    LMOD_INF_015 -->|triggering| LMOD_INF_016
    LMOD_INF_016 -->|triggering| LMOD_INF_017
    LMOD_INF_017 -->|triggering| LMOD_INF_018
    LMOD_INF_018 -->|triggering| LMOD_INF_019
    LMOD_INF_019 -->|triggering| LMOD_INF_020
    LMOD_INF_020 -->|triggering| LMOD_INF_021
    LMOD_INF_021 -->|triggering| LMOD_INF_022
    LMOD_INF_022 -->|triggering| LMOD_INF_023
    LMOD_INF_023 -->|triggering| LMOD_INF_024
    LMOD_INF_024 -->|triggering| LMOD_INF_025
    LMOD_INF_025 -->|triggering| LMOD_INF_026
    LMOD_INF_026 -->|triggering| LMOD_INF_027
    LMOD_INF_027 -->|triggering| LMOD_INF_028
    LMOD_INF_028 -->|triggering| LMOD_INF_029
    LMOD_INF_029 -->|triggering| LMOD_INF_030
    LMOD_INF_030 -->|triggering| LMOD_INF_031
    LMOD_INF_031 -->|triggering| LMOD_INF_033
    LMOD_INF_033 -->|triggering| LMOD_INF_034
    LMOD_INF_034 -->|triggering| LMOD_INF_035
    LMOD_INF_035 -->|triggering| LMOD_INF_036
    LMOD_INF_036 -->|triggering| LMOD_INF_037
    LMOD_INF_037 -->|triggering| LMOD_INF_038
    LMOD_INF_038 -->|triggering| LMOD_INF_039
    LMOD_INF_039 -->|triggering| LMOD_INF_040
    LMOD_INF_040 -->|triggering| LMOD_INF_042
    LMOD_INF_042 -->|triggering| LMOD_INF_043
    LMOD_INF_043 -->|triggering| LMOD_INF_GOV
    LMOD_INF_GOV -->|triggering| LMOD_INFRA_OPS
    LMOD_INFRA_OPS -->|triggering| LMOD_INFRA_RUNTIME
    LMOD_INFRA_RUNTIME -->|triggering| LMOD_INTEGRATION
    LMOD_INTEGRATION -->|triggering| LMOD_KB_001
    LMOD_KB_001 -->|triggering| LMOD_L00_001
    LMOD_L00_001 -->|triggering| LMOD_L00_002
    LMOD_L00_002 -->|triggering| LMOD_L00_003
    LMOD_L00_003 -->|triggering| LMOD_L00_004
    LMOD_L00_004 -->|triggering| LMOD_L02_001
    LMOD_L02_001 -->|triggering| LMOD_L03_001
    LMOD_L03_001 -->|triggering| LMOD_L04_001
    LMOD_L04_001 -->|triggering| LMOD_L05_001
    LMOD_L05_001 -->|triggering| LMOD_L06_001
    LMOD_L06_001 -->|triggering| LMOD_L07_001
    LMOD_L07_001 -->|triggering| LMOD_L08_001
    LMOD_L08_001 -->|triggering| LMOD_L09_001
    LMOD_L09_001 -->|triggering| LMOD_L10_001
    LMOD_L10_001 -->|triggering| LMOD_L11_001
    LMOD_L11_001 -->|triggering| LMOD_L13_001
    LMOD_L13_001 -->|triggering| LMOD_LLM_SECURITY
    LMOD_LLM_SECURITY -->|triggering| LMOD_MASTER_001
    LMOD_MASTER_001 -->|triggering| LMOD_MASTER_002
    LMOD_MASTER_002 -->|triggering| LMOD_MASTER_003
    LMOD_MASTER_003 -->|triggering| LMOD_MASTER_BLUEPRINT
    LMOD_MASTER_BLUEPRINT -->|triggering| LMOD_MKT_DATA
    LMOD_MKT_DATA -->|triggering| LMOD_ML_SERVE
    LMOD_ML_SERVE -->|triggering| LMOD_OPS_018
    LMOD_OPS_018 -->|triggering| LMOD_ORC_trigger_router
    LMOD_ORC_trigger_router -->|triggering| LMOD_PFC_001
    LMOD_PFC_001 -->|triggering| LMOD_PF_ALLOC
    LMOD_PF_ALLOC -->|triggering| LMOD_REMEDIATION_PROGRESS
    LMOD_REMEDIATION_PROGRESS -->|triggering| LMOD_REMEDIATION_PROGRESS_SMOKE
    LMOD_REMEDIATION_PROGRESS_SMOKE -->|triggering| LMOD_RESOURCE_OPTIMIZATION_ENGINE
    LMOD_RESOURCE_OPTIMIZATION_ENGINE -->|triggering| LMOD_RULE_ENGINE
    LMOD_RULE_ENGINE -->|triggering| LMOD_SEC_030
    LMOD_SEC_030 -->|triggering| LMOD_SEC_immutable_core
    LMOD_SEC_immutable_core -->|triggering| LMOD_SELL_DECISION
    LMOD_SELL_DECISION -->|triggering| LMOD_SHARED_001
    LMOD_SHARED_001 -->|triggering| LMOD_SHARED_002
    LMOD_SHARED_002 -->|triggering| LMOD_SHR_io_yaml
    LMOD_SHR_io_yaml -->|triggering| LMOD_SHR_workspace_telemetry
    LMOD_SHR_workspace_telemetry -->|triggering| LMOD_SHR_converters
    LMOD_SHR_converters -->|triggering| LMOD_SIGNAL_ASHARE
    LMOD_SIGNAL_ASHARE -->|triggering| LMOD_SIGQC_001
    LMOD_SIGQC_001 -->|triggering| LMOD_SIMULATION
    LMOD_SIMULATION -->|triggering| LMOD_SMOKE_TEST
    LMOD_SMOKE_TEST -->|triggering| LMOD_TASK_SYSTEM
    LMOD_TASK_SYSTEM -->|triggering| LMOD_TEST
    LMOD_TEST -->|triggering| LMOD_TEST_202
    LMOD_TEST_202 -->|triggering| LMOD_TEST_203
    LMOD_TEST_203 -->|triggering| LMOD_TEST_204
    LMOD_TEST_204 -->|triggering| LMOD_TEST_205
    LMOD_TEST_205 -->|triggering| LMOD_TEST_206
    LMOD_TEST_206 -->|triggering| LMOD_TEST_210
    LMOD_TEST_210 -->|triggering| LMOD_TEST_211
    LMOD_TEST_211 -->|triggering| LMOD_TEST_212
    LMOD_TEST_212 -->|triggering| LMOD_TEST_213
    LMOD_TEST_213 -->|triggering| LMOD_TEST_215
    LMOD_TEST_215 -->|triggering| LMOD_TEST_216
    LMOD_TEST_216 -->|triggering| LMOD_TEST_217
    LMOD_TEST_217 -->|triggering| LMOD_TEST_218
    LMOD_TEST_218 -->|triggering| LMOD_TEST_219
    LMOD_TEST_219 -->|triggering| LMOD_TEST_220
    LMOD_TEST_220 -->|triggering| LMOD_TEST_221
    LMOD_TEST_221 -->|triggering| LMOD_TEST_222
    LMOD_TEST_222 -->|triggering| LMOD_TEST_223
    LMOD_TEST_223 -->|triggering| LMOD_TEST_224
    LMOD_TEST_224 -->|triggering| LMOD_TEST_225
    LMOD_TEST_225 -->|triggering| LMOD_TEST_226
    LMOD_TEST_226 -->|triggering| LMOD_TEST_227
    LMOD_TEST_227 -->|triggering| LMOD_TEST_228
    LMOD_TEST_228 -->|triggering| LMOD_TEST_229
    LMOD_TEST_229 -->|triggering| LMOD_TEST_230
    LMOD_TEST_230 -->|triggering| LMOD_TEST_231
    LMOD_TEST_231 -->|triggering| LMOD_TEST_232
    LMOD_TEST_232 -->|triggering| LMOD_TEST_233
    LMOD_TEST_233 -->|triggering| LMOD_TEST_234
    LMOD_TEST_234 -->|triggering| LMOD_TEST_235
    LMOD_TEST_235 -->|triggering| LMOD_TEST_236
    LMOD_TEST_236 -->|triggering| LMOD_TEST_237
    LMOD_TEST_237 -->|triggering| LMOD_TEST_238
    LMOD_TEST_238 -->|triggering| LMOD_TEST_239
    LMOD_TEST_239 -->|triggering| LMOD_TEST_240
    LMOD_TEST_240 -->|triggering| LMOD_TEST_241
    LMOD_TEST_241 -->|triggering| LMOD_TEST_242
    LMOD_TEST_242 -->|triggering| LMOD_TEST_246
    LMOD_TEST_246 -->|triggering| LMOD_TEST_247
    LMOD_TEST_247 -->|triggering| LMOD_TEST_248
    LMOD_TEST_248 -->|triggering| LMOD_TEST_250
    LMOD_TEST_250 -->|triggering| LMOD_TEST_251
    LMOD_TEST_251 -->|triggering| LMOD_TEST_252
    LMOD_TEST_252 -->|triggering| LMOD_TEST_253
    LMOD_TEST_253 -->|triggering| LMOD_TEST_254
    LMOD_TEST_254 -->|triggering| LMOD_TEST_255
    LMOD_TEST_255 -->|triggering| LMOD_TEST_256
    LMOD_TEST_256 -->|triggering| LMOD_TEST_257
    LMOD_TEST_257 -->|triggering| LMOD_TEST_258
    LMOD_TEST_258 -->|triggering| LMOD_TEST_259
    LMOD_TEST_259 -->|triggering| LMOD_TEST_260
    LMOD_TEST_260 -->|triggering| LMOD_TEST_261
    LMOD_TEST_261 -->|triggering| LMOD_TEST_262
    LMOD_TEST_262 -->|triggering| LMOD_TEST_263
    LMOD_TEST_263 -->|triggering| LMOD_TEST_264
    LMOD_TEST_264 -->|triggering| LMOD_TEST_265
    LMOD_TEST_265 -->|triggering| LMOD_TEST_266
    LMOD_TEST_266 -->|triggering| LMOD_TEST_267
    LMOD_TEST_267 -->|triggering| LMOD_TEST_268
    LMOD_TEST_268 -->|triggering| LMOD_TEST_272
    LMOD_TEST_272 -->|triggering| LMOD_TEST_273
    LMOD_TEST_273 -->|triggering| LMOD_TEST_274
    LMOD_TEST_274 -->|triggering| LMOD_TEST_275
    LMOD_TEST_275 -->|triggering| LMOD_TEST_276
    LMOD_TEST_276 -->|triggering| LMOD_TEST_277
    LMOD_TEST_277 -->|triggering| LMOD_TEST_278
    LMOD_TEST_278 -->|triggering| LMOD_TEST_279
    LMOD_TEST_279 -->|triggering| LMOD_TEST_280
    LMOD_TEST_280 -->|triggering| LMOD_TEST_281
    LMOD_TEST_281 -->|triggering| LMOD_TEST_282
    LMOD_TEST_282 -->|triggering| LMOD_TEST_283
    LMOD_TEST_283 -->|triggering| LMOD_TEST_284
    LMOD_TEST_284 -->|triggering| LMOD_TEST_285
    LMOD_TEST_285 -->|triggering| LMOD_TEST_286
    LMOD_TEST_286 -->|triggering| LMOD_TEST_287
    LMOD_TEST_287 -->|triggering| LMOD_TEST_288
    LMOD_TEST_288 -->|triggering| LMOD_TEST_289
    LMOD_TEST_289 -->|triggering| LMOD_TEST_290
    LMOD_TEST_290 -->|triggering| LMOD_TEST_291
    LMOD_TEST_291 -->|triggering| LMOD_TEST_292
    LMOD_TEST_292 -->|triggering| LMOD_TEST_293
    LMOD_TEST_293 -->|triggering| LMOD_TEST_294
    LMOD_TEST_294 -->|triggering| LMOD_TEST_295
    LMOD_TEST_295 -->|triggering| LMOD_TEST_296
    LMOD_TEST_296 -->|triggering| LMOD_TEST_297
    LMOD_TEST_297 -->|triggering| LMOD_TEST_298
    LMOD_TEST_298 -->|triggering| LMOD_TEST_299
    LMOD_TEST_299 -->|triggering| LMOD_TEST_300
    LMOD_TEST_300 -->|triggering| LMOD_TEST_301
    LMOD_TEST_301 -->|triggering| LMOD_TEST_302
    LMOD_TEST_302 -->|triggering| LMOD_TEST_303
    LMOD_TEST_303 -->|triggering| LMOD_TEST_304
    LMOD_TEST_304 -->|triggering| LMOD_TEST_305
    LMOD_TEST_305 -->|triggering| LMOD_TEST_306
    LMOD_TEST_306 -->|triggering| LMOD_TEST_307
    LMOD_TEST_307 -->|triggering| LMOD_TEST_308
    LMOD_TEST_308 -->|triggering| LMOD_TEST_309
    LMOD_TEST_309 -->|triggering| LMOD_TEST_310
    LMOD_TEST_310 -->|triggering| LMOD_TEST_311
    LMOD_TEST_311 -->|triggering| LMOD_TEST_312
    LMOD_TEST_312 -->|triggering| LMOD_TEST_313
    LMOD_TEST_313 -->|triggering| LMOD_TEST_314
    LMOD_TEST_314 -->|triggering| LMOD_TEST_315
    LMOD_TEST_315 -->|triggering| LMOD_TEST_316
    LMOD_TEST_316 -->|triggering| LMOD_TEST_319
    LMOD_TEST_319 -->|triggering| LMOD_TEST_320
    LMOD_TEST_320 -->|triggering| LMOD_TEST_322
    LMOD_TEST_322 -->|triggering| LMOD_TEST_323
    LMOD_TEST_323 -->|triggering| LMOD_TEST_324
    LMOD_TEST_324 -->|triggering| LMOD_TEST_325
    LMOD_TEST_325 -->|triggering| LMOD_TEST_326
    LMOD_TEST_326 -->|triggering| LMOD_TEST_328
    LMOD_TEST_328 -->|triggering| LMOD_TEST_329
    LMOD_TEST_329 -->|triggering| LMOD_TEST_330
    LMOD_TEST_330 -->|triggering| LMOD_TEST_331
    LMOD_TEST_331 -->|triggering| LMOD_TEST_332
    LMOD_TEST_332 -->|triggering| LMOD_TEST_333
    LMOD_TEST_333 -->|triggering| LMOD_TEST_334
    LMOD_TEST_334 -->|triggering| LMOD_TEST_335
    LMOD_TEST_335 -->|triggering| LMOD_TEST_336
    LMOD_TEST_336 -->|triggering| LMOD_TEST_337
    LMOD_TEST_337 -->|triggering| LMOD_TEST_338
    LMOD_TEST_338 -->|triggering| LMOD_TEST_339
    LMOD_TEST_339 -->|triggering| LMOD_TEST_340
    LMOD_TEST_340 -->|triggering| LMOD_TEST_342
    LMOD_TEST_342 -->|triggering| LMOD_TEST_343
    LMOD_TEST_343 -->|triggering| LMOD_TEST_344
    LMOD_TEST_344 -->|triggering| LMOD_TEST_345
    LMOD_TEST_345 -->|triggering| LMOD_TEST_346
    LMOD_TEST_346 -->|triggering| LMOD_TEST_347
    LMOD_TEST_347 -->|triggering| LMOD_TEST_348
    LMOD_TEST_348 -->|triggering| LMOD_TEST_349
    LMOD_TEST_349 -->|triggering| LMOD_TEST_350
    LMOD_TEST_350 -->|triggering| LMOD_TEST_351
    LMOD_TEST_351 -->|triggering| LMOD_TEST_354
    LMOD_TEST_354 -->|triggering| LMOD_TEST_355
    LMOD_TEST_355 -->|triggering| LMOD_TEST_356
    LMOD_TEST_356 -->|triggering| LMOD_TEST_357
    LMOD_TEST_357 -->|triggering| LMOD_TEST_358
    LMOD_TEST_358 -->|triggering| LMOD_TEST_359
    LMOD_TEST_359 -->|triggering| LMOD_TEST_360
    LMOD_TEST_360 -->|triggering| LMOD_TEST_361
    LMOD_TEST_361 -->|triggering| LMOD_TEST_362
    LMOD_TEST_362 -->|triggering| LMOD_TEST_363
    LMOD_TEST_363 -->|triggering| LMOD_TEST_364
    LMOD_TEST_364 -->|triggering| LMOD_TEST_365
    LMOD_TEST_365 -->|triggering| LMOD_TEST_366
    LMOD_TEST_366 -->|triggering| LMOD_TEST_367
    LMOD_TEST_367 -->|triggering| LMOD_TEST_368
    LMOD_TEST_368 -->|triggering| LMOD_TEST_369
    LMOD_TEST_369 -->|triggering| LMOD_TEST_370
    LMOD_TEST_370 -->|triggering| LMOD_TEST_371
    LMOD_TEST_371 -->|triggering| LMOD_TEST_372
    LMOD_TEST_372 -->|triggering| LMOD_TEST_373
    LMOD_TEST_373 -->|triggering| LMOD_TEST_374
    LMOD_TEST_374 -->|triggering| LMOD_TEST_375
    LMOD_TEST_375 -->|triggering| LMOD_TEST_376
    LMOD_TEST_376 -->|triggering| LMOD_TEST_377
    LMOD_TEST_377 -->|triggering| LMOD_TEST_378
    LMOD_TEST_378 -->|triggering| LMOD_TEST_379
    LMOD_TEST_379 -->|triggering| LMOD_TEST_380
    LMOD_TEST_380 -->|triggering| LMOD_TEST_381
    LMOD_TEST_381 -->|triggering| LMOD_TEST_382
    LMOD_TEST_382 -->|triggering| LMOD_TEST_383
    LMOD_TEST_383 -->|triggering| LMOD_TEST_384
    LMOD_TEST_384 -->|triggering| LMOD_TEST_385
    LMOD_TEST_385 -->|triggering| LMOD_TEST_386
    LMOD_TEST_386 -->|triggering| LMOD_TEST_387
    LMOD_TEST_387 -->|triggering| LMOD_TEST_388
    LMOD_TEST_388 -->|triggering| LMOD_TEST_389
    LMOD_TEST_389 -->|triggering| LMOD_TEST_390
    LMOD_TEST_390 -->|triggering| LMOD_TEST_391
    LMOD_TEST_391 -->|triggering| LMOD_TEST_392
    LMOD_TEST_392 -->|triggering| LMOD_TEST_393
    LMOD_TEST_393 -->|triggering| LMOD_TEST_394
    LMOD_TEST_394 -->|triggering| LMOD_TEST_395
    LMOD_TEST_395 -->|triggering| LMOD_TEST_396
    LMOD_TEST_396 -->|triggering| LMOD_TEST_397
    LMOD_TEST_397 -->|triggering| LMOD_TEST_402
    LMOD_TEST_402 -->|triggering| LMOD_TEST_403
    LMOD_TEST_403 -->|triggering| LMOD_TEST_404
    LMOD_TEST_404 -->|triggering| LMOD_TEST_406
    LMOD_TEST_406 -->|triggering| LMOD_TEST_407
    LMOD_TEST_407 -->|triggering| LMOD_TEST_408
    LMOD_TEST_408 -->|triggering| LMOD_TEST_409
    LMOD_TEST_409 -->|triggering| LMOD_TEST_410
    LMOD_TEST_410 -->|triggering| LMOD_TEST_411
    LMOD_TEST_411 -->|triggering| LMOD_TEST_412
    LMOD_TEST_412 -->|triggering| LMOD_TEST_413
    LMOD_TEST_413 -->|triggering| LMOD_TEST_414
    LMOD_TEST_414 -->|triggering| LMOD_TEST_415
    LMOD_TEST_415 -->|triggering| LMOD_TEST_416
    LMOD_TEST_416 -->|triggering| LMOD_TEST_417
    LMOD_TEST_417 -->|triggering| LMOD_TEST_418
    LMOD_TEST_418 -->|triggering| LMOD_TEST_419
    LMOD_TEST_419 -->|triggering| LMOD_TEST_420
    LMOD_TEST_420 -->|triggering| LMOD_TEST_421
    LMOD_TEST_421 -->|triggering| LMOD_TEST_422
    LMOD_TEST_422 -->|triggering| LMOD_TEST_423
    LMOD_TEST_423 -->|triggering| LMOD_TEST_424
    LMOD_TEST_424 -->|triggering| LMOD_TEST_425
    LMOD_TEST_425 -->|triggering| LMOD_TEST_426
    LMOD_TEST_426 -->|triggering| LMOD_TEST_427
    LMOD_TEST_427 -->|triggering| LMOD_TEST_428
    LMOD_TEST_428 -->|triggering| LMOD_TEST_429
    LMOD_TEST_429 -->|triggering| LMOD_TEST_430
    LMOD_TEST_430 -->|triggering| LMOD_TEST_431
    LMOD_TEST_431 -->|triggering| LMOD_TEST_432
    LMOD_TEST_432 -->|triggering| LMOD_TEST_433
    LMOD_TEST_433 -->|triggering| LMOD_TEST_434
    LMOD_TEST_434 -->|triggering| LMOD_TEST_435
    LMOD_TEST_435 -->|triggering| LMOD_TEST_436
    LMOD_TEST_436 -->|triggering| LMOD_TEST_437
    LMOD_TEST_437 -->|triggering| LMOD_TEST_438
    LMOD_TEST_438 -->|triggering| LMOD_TEST_439
    LMOD_TEST_439 -->|triggering| LMOD_TEST_440
    LMOD_TEST_440 -->|triggering| LMOD_TEST_441
    LMOD_TEST_441 -->|triggering| LMOD_TEST_444
    LMOD_TEST_444 -->|triggering| LMOD_TEST_447
    LMOD_TEST_447 -->|triggering| LMOD_TEST_449
    LMOD_TEST_449 -->|triggering| LMOD_TEST_450
    LMOD_TEST_450 -->|triggering| LMOD_TEST_452
    LMOD_TEST_452 -->|triggering| LMOD_TEST_454
    LMOD_TEST_454 -->|triggering| LMOD_TEST_455
    LMOD_TEST_455 -->|triggering| LMOD_TEST_456
    LMOD_TEST_456 -->|triggering| LMOD_TEST_457
    LMOD_TEST_457 -->|triggering| LMOD_TEST_459
    LMOD_TEST_459 -->|triggering| LMOD_TEST_460
    LMOD_TEST_460 -->|triggering| LMOD_TEST_461
    LMOD_TEST_461 -->|triggering| LMOD_TEST_462
    LMOD_TEST_462 -->|triggering| LMOD_TEST_463
    LMOD_TEST_463 -->|triggering| LMOD_TEST_464
    LMOD_TEST_464 -->|triggering| LMOD_TEST_466
    LMOD_TEST_466 -->|triggering| LMOD_TEST_467
    LMOD_TEST_467 -->|triggering| LMOD_TEST_468
    LMOD_TEST_468 -->|triggering| LMOD_TEST_469
    LMOD_TEST_469 -->|triggering| LMOD_TEST_470
    LMOD_TEST_470 -->|triggering| LMOD_TEST_471
    LMOD_TEST_471 -->|triggering| LMOD_TEST_472
    LMOD_TEST_472 -->|triggering| LMOD_TEST_473
    LMOD_TEST_473 -->|triggering| LMOD_TEST_475
    LMOD_TEST_475 -->|triggering| LMOD_TEST_476
    LMOD_TEST_476 -->|triggering| LMOD_TEST_477
    LMOD_TEST_477 -->|triggering| LMOD_TEST_479
    LMOD_TEST_479 -->|triggering| LMOD_TEST_481
    LMOD_TEST_481 -->|triggering| LMOD_TEST_482
    LMOD_TEST_482 -->|triggering| LMOD_TEST_484
    LMOD_TEST_484 -->|triggering| LMOD_TEST_485
    LMOD_TEST_485 -->|triggering| LMOD_TEST_487
    LMOD_TEST_487 -->|triggering| LMOD_TEST_488
    LMOD_TEST_488 -->|triggering| LMOD_TEST_489
    LMOD_TEST_489 -->|triggering| LMOD_TEST_490
    LMOD_TEST_490 -->|triggering| LMOD_TEST_491
    LMOD_TEST_491 -->|triggering| LMOD_TEST_492
    LMOD_TEST_492 -->|triggering| LMOD_TEST_494
    LMOD_TEST_494 -->|triggering| LMOD_TEST_495
    LMOD_TEST_495 -->|triggering| LMOD_TEST_496
    LMOD_TEST_496 -->|triggering| LMOD_TEST_497
    LMOD_TEST_497 -->|triggering| LMOD_TEST_498
    LMOD_TEST_498 -->|triggering| LMOD_TEST_499
    LMOD_TEST_499 -->|triggering| LMOD_TEST_501
    LMOD_TEST_501 -->|triggering| LMOD_TEST_502
    LMOD_TEST_502 -->|triggering| LMOD_TEST_504
    LMOD_TEST_504 -->|triggering| LMOD_TEST_505
    LMOD_TEST_505 -->|triggering| LMOD_TEST_506
    LMOD_TEST_506 -->|triggering| LMOD_TEST_508
    LMOD_TEST_508 -->|triggering| LMOD_TEST_509
    LMOD_TEST_509 -->|triggering| LMOD_TEST_510
    LMOD_TEST_510 -->|triggering| LMOD_TEST_511
    LMOD_TEST_511 -->|triggering| LMOD_TEST_512
    LMOD_TEST_512 -->|triggering| LMOD_TEST_513
    LMOD_TEST_513 -->|triggering| LMOD_TEST_514
    LMOD_TEST_514 -->|triggering| LMOD_TEST_528
    LMOD_TEST_528 -->|triggering| LMOD_TEST_529
    LMOD_TEST_529 -->|triggering| LMOD_TEST_530
    LMOD_TEST_530 -->|triggering| LMOD_TEST_532
    LMOD_TEST_532 -->|triggering| LMOD_TEST_533
    LMOD_TEST_533 -->|triggering| LMOD_TEST_534
    LMOD_TEST_534 -->|triggering| LMOD_TEST_535
    LMOD_TEST_535 -->|triggering| LMOD_TEST_536
    LMOD_TEST_536 -->|triggering| LMOD_TEST_537
    LMOD_TEST_537 -->|triggering| LMOD_TEST_538
    LMOD_TEST_538 -->|triggering| LMOD_TEST_539
    LMOD_TEST_539 -->|triggering| LMOD_TEST_540
    LMOD_TEST_540 -->|triggering| LMOD_TEST_541
    LMOD_TEST_541 -->|triggering| LMOD_TEST_543
    LMOD_TEST_543 -->|triggering| LMOD_TEST_544
    LMOD_TEST_544 -->|triggering| LMOD_TEST_545
    LMOD_TEST_545 -->|triggering| LMOD_TEST_547
    LMOD_TEST_547 -->|triggering| LMOD_TEST_548
    LMOD_TEST_548 -->|triggering| LMOD_TEST_549
    LMOD_TEST_549 -->|triggering| LMOD_TEST_550
    LMOD_TEST_550 -->|triggering| LMOD_TEST_551
    LMOD_TEST_551 -->|triggering| LMOD_TEST_552
    LMOD_TEST_552 -->|triggering| LMOD_TEST_553
    LMOD_TEST_553 -->|triggering| LMOD_TEST_554
    LMOD_TEST_554 -->|triggering| LMOD_TEST_555
    LMOD_TEST_555 -->|triggering| LMOD_TEST_557
    LMOD_TEST_557 -->|triggering| LMOD_TEST_558
    LMOD_TEST_558 -->|triggering| LMOD_TEST_559
    LMOD_TEST_559 -->|triggering| LMOD_TEST_560
    LMOD_TEST_560 -->|triggering| LMOD_TEST_561
    LMOD_TEST_561 -->|triggering| LMOD_TEST_562
    LMOD_TEST_562 -->|triggering| LMOD_TEST_563
    LMOD_TEST_563 -->|triggering| LMOD_TEST_564
    LMOD_TEST_564 -->|triggering| LMOD_TEST_565
    LMOD_TEST_565 -->|triggering| LMOD_TEST_566
    LMOD_TEST_566 -->|triggering| LMOD_TEST_567
    LMOD_TEST_567 -->|triggering| LMOD_TEST_568
    LMOD_TEST_568 -->|triggering| LMOD_TEST_569
    LMOD_TEST_569 -->|triggering| LMOD_TEST_570
    LMOD_TEST_570 -->|triggering| LMOD_TEST_571
    LMOD_TEST_571 -->|triggering| LMOD_TEST_572
    LMOD_TEST_572 -->|triggering| LMOD_TEST_573
    LMOD_TEST_573 -->|triggering| LMOD_TEST_574
    LMOD_TEST_574 -->|triggering| LMOD_TEST_575
    LMOD_TEST_575 -->|triggering| LMOD_TEST_576
    LMOD_TEST_576 -->|triggering| LMOD_TEST_577
    LMOD_TEST_577 -->|triggering| LMOD_TEST_579
    LMOD_TEST_579 -->|triggering| LMOD_TEST_580
    LMOD_TEST_580 -->|triggering| LMOD_TEST_582
    LMOD_TEST_582 -->|triggering| LMOD_TEST_583
    LMOD_TEST_583 -->|triggering| LMOD_TEST_584
    LMOD_TEST_584 -->|triggering| LMOD_TEST_585
    LMOD_TEST_585 -->|triggering| LMOD_TEST_586
    LMOD_TEST_586 -->|triggering| LMOD_TEST_587
    LMOD_TEST_587 -->|triggering| LMOD_TEST_588
    LMOD_TEST_588 -->|triggering| LMOD_TEST_590
    LMOD_TEST_590 -->|triggering| LMOD_TEST_591
    LMOD_TEST_591 -->|triggering| LMOD_TEST_592
    LMOD_TEST_592 -->|triggering| LMOD_TEST_593
    LMOD_TEST_593 -->|triggering| LMOD_TEST_594
    LMOD_TEST_594 -->|triggering| LMOD_TEST_595
    LMOD_TEST_595 -->|triggering| LMOD_TEST_597
    LMOD_TEST_597 -->|triggering| LMOD_TEST_598
    LMOD_TEST_598 -->|triggering| LMOD_TEST_599
    LMOD_TEST_599 -->|triggering| LMOD_TEST_600
    LMOD_TEST_600 -->|triggering| LMOD_TEST_601
    LMOD_TEST_601 -->|triggering| LMOD_TEST_602
    LMOD_TEST_602 -->|triggering| LMOD_TEST_603
    LMOD_TEST_603 -->|triggering| LMOD_TEST_604
    LMOD_TEST_604 -->|triggering| LMOD_TEST_605
    LMOD_TEST_605 -->|triggering| LMOD_TEST_606
    LMOD_TEST_606 -->|triggering| LMOD_TEST_607
    LMOD_TEST_607 -->|triggering| LMOD_TEST_608
    LMOD_TEST_608 -->|triggering| LMOD_TEST_609
    LMOD_TEST_609 -->|triggering| LMOD_TEST_610
    LMOD_TEST_610 -->|triggering| LMOD_TEST_611
    LMOD_TEST_611 -->|triggering| LMOD_TEST_612
    LMOD_TEST_612 -->|triggering| LMOD_TEST_613
    LMOD_TEST_613 -->|triggering| LMOD_TEST_614
    LMOD_TEST_614 -->|triggering| LMOD_TEST_616
    LMOD_TEST_616 -->|triggering| LMOD_TEST_617
    LMOD_TEST_617 -->|triggering| LMOD_TEST_618
    LMOD_TEST_618 -->|triggering| LMOD_TEST_619
    LMOD_TEST_619 -->|triggering| LMOD_TEST_620
    LMOD_TEST_620 -->|triggering| LMOD_TEST_621
    LMOD_TEST_621 -->|triggering| LMOD_TEST_622
    LMOD_TEST_622 -->|triggering| LMOD_TEST_623
    LMOD_TEST_623 -->|triggering| LMOD_TEST_624
    LMOD_TEST_624 -->|triggering| LMOD_TEST_625
    LMOD_TEST_625 -->|triggering| LMOD_TEST_626
    LMOD_TEST_626 -->|triggering| LMOD_TEST_627
    LMOD_TEST_627 -->|triggering| LMOD_TEST_628
    LMOD_TEST_628 -->|triggering| LMOD_TEST_629
    LMOD_TEST_629 -->|triggering| LMOD_TEST_630
    LMOD_TEST_630 -->|triggering| LMOD_TEST_631
    LMOD_TEST_631 -->|triggering| LMOD_TEST_633
    LMOD_TEST_633 -->|triggering| LMOD_TEST_634
    LMOD_TEST_634 -->|triggering| LMOD_TEST_635
    LMOD_TEST_635 -->|triggering| LMOD_TEST_636
    LMOD_TEST_636 -->|triggering| LMOD_TEST_637
    LMOD_TEST_637 -->|triggering| LMOD_TEST_639
    LMOD_TEST_639 -->|triggering| LMOD_TEST_640
    LMOD_TEST_640 -->|triggering| LMOD_TEST_641
    LMOD_TEST_641 -->|triggering| LMOD_TEST_642
    LMOD_TEST_642 -->|triggering| LMOD_TEST_643
    LMOD_TEST_643 -->|triggering| LMOD_TEST_644
    LMOD_TEST_644 -->|triggering| LMOD_TEST_646
    LMOD_TEST_646 -->|triggering| LMOD_TEST_647
    LMOD_TEST_647 -->|triggering| LMOD_TEST_648
    LMOD_TEST_648 -->|triggering| LMOD_TEST_649
    LMOD_TEST_649 -->|triggering| LMOD_TEST_651
    LMOD_TEST_651 -->|triggering| LMOD_TEST_652
    LMOD_TEST_652 -->|triggering| LMOD_TEST_653
    LMOD_TEST_653 -->|triggering| LMOD_TEST_654
    LMOD_TEST_654 -->|triggering| LMOD_TEST_655
    LMOD_TEST_655 -->|triggering| LMOD_TEST_660
    LMOD_TEST_660 -->|triggering| LMOD_TEST_661
    LMOD_TEST_661 -->|triggering| LMOD_TEST_662
    LMOD_TEST_662 -->|triggering| LMOD_TEST_663
    LMOD_TEST_663 -->|triggering| LMOD_TEST_664
    LMOD_TEST_664 -->|triggering| LMOD_TEST_665
    LMOD_TEST_665 -->|triggering| LMOD_TEST_668
    LMOD_TEST_668 -->|triggering| LMOD_TEST_669
    LMOD_TEST_669 -->|triggering| LMOD_TEST_670
    LMOD_TEST_670 -->|triggering| LMOD_TEST_671
    LMOD_TEST_671 -->|triggering| LMOD_TEST_672
    LMOD_TEST_672 -->|triggering| LMOD_TEST_673
    LMOD_TEST_673 -->|triggering| LMOD_TEST_674
    LMOD_TEST_674 -->|triggering| LMOD_TEST_675
    LMOD_TEST_675 -->|triggering| LMOD_TEST_676
    LMOD_TEST_676 -->|triggering| LMOD_TEST_677
    LMOD_TEST_677 -->|triggering| LMOD_TEST_678
    LMOD_TEST_678 -->|triggering| LMOD_TEST_679
    LMOD_TEST_679 -->|triggering| LMOD_TEST_680
    LMOD_TEST_680 -->|triggering| LMOD_TEST_681
    LMOD_TEST_681 -->|triggering| LMOD_TEST_682
    LMOD_TEST_682 -->|triggering| LMOD_TEST_683
    LMOD_TEST_683 -->|triggering| LMOD_TEST_684
    LMOD_TEST_684 -->|triggering| LMOD_TEST_685
    LMOD_TEST_685 -->|triggering| LMOD_TEST_686
    LMOD_TEST_686 -->|triggering| LMOD_TEST_687
    LMOD_TEST_687 -->|triggering| LMOD_TEST_688
    LMOD_TEST_688 -->|triggering| LMOD_TEST_689
    LMOD_TEST_689 -->|triggering| LMOD_TEST_690
    LMOD_TEST_690 -->|triggering| LMOD_TEST_691
    LMOD_TEST_691 -->|triggering| LMOD_TEST_692
    LMOD_TEST_692 -->|triggering| LMOD_TEST_693
    LMOD_TEST_693 -->|triggering| LMOD_TEST_694
    LMOD_TEST_694 -->|triggering| LMOD_TEST_695
    LMOD_TEST_695 -->|triggering| LMOD_TEST_696
    LMOD_TEST_696 -->|triggering| LMOD_TEST_697
    LMOD_TEST_697 -->|triggering| LMOD_TEST_698
    LMOD_TEST_698 -->|triggering| LMOD_TEST_699
    LMOD_TEST_699 -->|triggering| LMOD_TEST_700
    LMOD_TEST_700 -->|triggering| LMOD_TEST_701
    LMOD_TEST_701 -->|triggering| LMOD_TEST_702
    LMOD_TEST_702 -->|triggering| LMOD_TEST_703
    LMOD_TEST_703 -->|triggering| LMOD_TEST_704
    LMOD_TEST_704 -->|triggering| LMOD_TEST_705
    LMOD_TEST_705 -->|triggering| LMOD_TEST_706
    LMOD_TEST_706 -->|triggering| LMOD_TEST_708
    LMOD_TEST_708 -->|triggering| LMOD_TEST_710
    LMOD_TEST_710 -->|triggering| LMOD_TEST_apply_depgraph_smoke
    LMOD_TEST_apply_depgraph_smoke -->|triggering| LMOD_TEST_apply_depgraph_smoke
    LMOD_TEST_apply_depgraph_smoke -->|triggering| LMOD_TRADING_001
    LMOD_TRADING_001 -->|triggering| LMOD_WORKSPACE_TELEMETRY
    LMOD_WORKSPACE_TELEMETRY -->|triggering| LMOD_XLR_003
    LMOD_XLR_003 -->|triggering| LMOD_migrate_sqlite_to_pg
    LMOD_migrate_sqlite_to_pg -->|triggering| LMOD_readme_version_sync
    LMOD_readme_version_sync -->|triggering| LPLACEHOLDER_MOD_GOV_SYNC_PANORAMA
    LPLACEHOLDER_MOD_GOV_SYNC_PANORAMA -->|triggering| LSH_DB_001
    LSH_DB_001 -->|triggering| LSH_DB_002
    LSH_DB_002 -->|triggering| LSH_GOV_003
    LSH_GOV_003 -->|triggering| LSH_GOV_004
    LSH_GOV_004 -->|triggering| LSH_MAIN_001
    LSH_MAIN_001 -->|triggering| LSYS_MASTER_001
    L6 -.->|feedback| CFG_rule_registry_collection
    L6 -.->|feedback| L5

    classDef bsStable fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef bsGenerated fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#000
    classDef bsTesting fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef bsPlanned fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef bsDeprecated fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

