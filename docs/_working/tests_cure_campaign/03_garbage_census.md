---
ttl: task_bound
completes_when: tests 治理战役收官随批归档
---
# tests/ 清理分档战役 · 03 垃圾判据普查（L1/L2/L3/L4）

> 生成: 2026-10-04 · 方法: 只读静态扫描 + pytest --collect-only 分块普查（132 顶块 + 60 下钻块） · 判据脚本/中间数据: `.runtime/tmp/census_*.json`（会话临时区，24h TTL）
> 路径约定：本文所有测试文件路径均相对 `tests/` 根（如 `a2a/test_a2a_check.py` = `tests/a2a/test_a2a_check.py`）。

## 0. 全量数字

| 指标 | 值 |
|---|---|
| tests/ 下 .py 总数 | 4046 |
| pytest collection 总 items | 74784（74784 = 56776 + 18008） |
| collection error 文件数 | 8（其中 L1 断链 7 个） |
| 含 skip 痕迹文件数 | 212（212） |
| — L2 真永久 skip（无复活条件） | 4 |
| — 运行时可用性守卫 skip（有复活条件） | 123 |
| — skipif 语法条件 skip | 85 |
| L3 同名对撞对 | 3（均为同音异义，非双树重复） |
| L3 import 强对撞对（真候选） | 7 |
| L4 一次性验证线索文件 | 184（原始 187，剔除 wave_generator 生产模块误报 3） |

## 1. L1 collection 错误（8 文件，断链 7 + 环境 1）

静态全量预检：6557 条 `zephyr.*` import 语句的模块路径 0 断链——断链全部发生在**符号级 / 被测文件级 / 迁移未跟上**，单看模块路径发现不了，必须 collection 实跑。

| 测试文件 | 错误 | 断链类型 | L1 判定 |
|---|---|---|---|
| tests/backtest/test_n_trial_ledger_t0_family.py | ImportError: cannot import name 'T0_BATCH_KIND' from 'zephyr.backtest.core.n_trial_ledger' | 符号级断链（符号已删） | L1 |
| tests/strategy_pipeline/test_daily_gate_snapshot_l5.py | ImportError: cannot import name '_read_external_kill_switch_state' from 'zephyr.strategy_p | 符号级断链（符号已删） | L1 |
| tests/model/test_qwen3_baseline_profile.py | FileNotFoundError: scripts/tasks/run/run_qwen3_baseline_exam.py（全仓仅 .aidrafts 存档+.pyc 残留） | 被测脚本已删 | L1 |
| tests/scripts/test_run_post_settlement.py | FileNotFoundError: scripts/tasks/run/run_post_settlement.py（真源已迁 scripts/run_post_settleme | 被测脚本迁移未跟上 | L1 |
| tests/governance/commit_gates/test_data_supply_chain_map_gate.py | ModuleNotFoundError: zephyr.gov_enforcement.commit_gates.data_supply_chain_map_gate（已迁 reg | 模块迁移未跟上 | L1 |
| tests/governance/commit_gates/test_trading_day_cycle_map_gate.py | ModuleNotFoundError: zephyr.gov_enforcement.commit_gates.trading_day_cycle_map_gate（已迁 reg | 模块迁移未跟上 | L1 |
| tests/zephyr/data/test_sector_eqw_from_constituents.py | ModuleNotFoundError: 'kline_sector_intraday_from_constituents'（脚本在 scripts/，测试顶层 import 依赖 | 路径断链（弱 L1，可修复复活） | L1? |
| tests/clone_guard/test_relate_adapter.py | UserWarning: CUDA path could not be detected 被 filterwarnings 升级为 error（CuPy/torch 导入链） | 环境型（CUDA 在场即可收集） | 非 L1 |

处置建议：前 6 个为确定性 L1（改被测对象已删/已迁，测试未跟上）；`test_sector_eqw_from_constituents.py` 属路径断链（脚本活着，sys.path 问题），修复 import 即复活，建议归「可修复」而非删除；`test_relate_adapter.py` 在有 CUDA 环境机器可正常收集，非 L1。

## 2. L2 永久 skip 清单（4 文件，无复活条件）

| 测试文件 | 痕迹构成 | reason（截断） |
|---|---|---|
| f_lifecycle/test_f18_automation.py | {'DEPRECATION': 11, 'AVAILABILITY': 2} | ARCH-034: PhaseManager 类已删除/拆分为函数式 API ; ARCH-034: GOVERNANCE_GATE_DIMENSIONS 已删除，维度分组被阶段分组替代 |
| gate/test_gate_e2e.py | {'STATIC_PERM': 1} | RULE-THIRTEEN R1: deliverables ≤ 1，多 deliverables 场景已不合法 |
| governance/conftest.py | {'DEPRECATION': 1} | Phase 1 legacy gate: governance architecture evolved beyond 8-module layout |
| io/test_verify_schema_health.py | {'STATIC_PERM': 4} | P2迁移：依赖 SQLite 临时库 + init_db 创建 SQLite 文件，不适用 PG ; P2迁移：依赖 SQLite 临时库 + sqlite_master 触发器检查，不适用 PG |

- `f_lifecycle/test_f18_automation.py`：13 条 skip 全因 ARCH-034 PhaseManager 类已删除——被测对象已死，整文件 L1/L2 双重命中，**首选删除**。
- `gate/test_gate_e2e.py`：RULE-THIRTEEN R1 后多 deliverables 场景已不合法——场景永久非法，删除。
- `io/test_verify_schema_health.py`：P2 迁移 PG 后 SQLite 临时库依赖永久不适用——随 P2 迁移收尾处置。
- `governance/conftest.py`：模块级 skip 一条（legacy 8-module layout 已超越）——需看该 conftest 挡住的子树是否整体过时。

## 3. L2 条件 skip 统计（208 文件，均有复活条件，非 L2 删除对象）

### 3.1 分类统计

- **skipif 语法条件**：85 文件 / 162 条痕迹。top 域: ai_layer=17, governance=17, context=5, autonomy=4, backtest=4, cross=3, dr=3, trading=3
- **运行时可用性守卫**（函数体 `pytest.skip(...)` + try/except，条件=服务/文件在场）：123 文件 / 205 条痕迹。top 域: governance=38, autonomy=19, ai_layer=5, infrastructure=5, memory=4, audit=3, backtest=3, context=3
- 可用性 reason 聚类（按文件计，可多归）：PG/PostgreSQL 34、导入失败(Cannot import) 18、服务不可达(中文"不可达") 18、ClickHouse 3、配置缺失 3、文件 not found 2、Redis 2。

### 3.2 skipif 条件清单（85 文件）

| 测试文件 | skipif | 裸 skip |
|---|---|---|
| a2a/test_a2a_check.py | 1 | 0 |
| agent_rbac/test_adversarial_resilience.py | 1 | 0 |
| ai_layer/cleaning/conftest.py | 1 | 0 |
| ai_layer/cleaning/test_spec_store.py | 1 | 0 |
| ai_layer/heritage/conftest.py | 1 | 0 |
| ai_layer/heritage/test_heritage_events.py | 1 | 0 |
| ai_layer/heritage/test_heritage_forget.py | 1 | 0 |
| ai_layer/heritage/test_heritage_snapshot.py | 1 | 0 |
| ai_layer/heritage/test_heritage_store.py | 1 | 0 |
| ai_layer/intake/conftest.py | 1 | 0 |
| ai_layer/intake/test_card_store.py | 1 | 0 |
| ai_layer/intake/test_dedup.py | 1 | 0 |
| ai_layer/intake/test_gate.py | 1 | 0 |
| ai_layer/intake/test_kpi.py | 1 | 0 |
| ai_layer/intake/test_snapshot_regen.py | 1 | 0 |
| ai_layer/perceive/conftest.py | 1 | 0 |
| ai_layer/perceive/test_quota_sync.py | 1 | 0 |
| ai_layer/test_evolution_chain_e2e.py | 1 | 0 |
| ai_layer/test_model_library_ddl.py | 1 | 0 |
| audit/audit_core/test_audit_log_guard.py | 3 | 0 |
| automation/test_auto_maintenance.py | 1 | 0 |
| autonomy/test_adversarial_robustness.py | 1 | 0 |
| autonomy/test_alignment_scorer.py | 1 | 0 |
| autonomy/test_system_snapshot_root.py | 4 | 0 |
| autonomy/test_token_budget_root.py | 1 | 0 |
| backtest/test_c4_engine_gpu_wiring.py | 2 | 0 |
| backtest/test_gpu_core_parity.py | 2 | 0 |
| backtest/test_l2_gpu_landing.py | 1 | 0 |
| backtest/test_stk_limit_matching.py | 1 | 0 |
| backup/test_stage3_vault_mtime_and_verdict.py | 1 | 0 |
| blueprint/test_blueprint_fidelity.py | 1 | 0 |
| canary/test_canary_rollout_manager.py | 1 | 0 |
| capability/test_capability_check.py | 1 | 0 |
| ce/test_ce_kill_switch.py | 1 | 0 |
| clone_guard/test_relate_adapter.py | 1 | 0 |
| context/test_context_assembler_root.py | 1 | 0 |
| context/test_context_drift_detector.py | 1 | 0 |
| context/test_context_evaluator_root.py | 1 | 0 |
| context/test_context_injector_root.py | 1 | 0 |
| context/test_context_pipeline_root.py | 1 | 0 |
| contracts/test_contract_verifier.py | 2 | 0 |
| cross/test_cross_cutting.py | 4 | 0 |
| cross/test_cross_session_detector.py | 2 | 0 |
| cross/test_e2e_redblue_night001.py | 1 | 0 |
| data/implementations/test_akshare_etf_benchmark.py | 1 | 0 |
| data/implementations/test_realtime_snapshot_tencent.py | 1 | 0 |
| decision/test_decision_explainer_root.py | 2 | 0 |
| decision/test_decision_registry.py | 2 | 0 |
| dependency/test_dependency_auditor.py | 2 | 0 |
| dr/test_backup_ch_vm_autocheck.py | 2 | 0 |
| dr/test_backup_mirror_deletion_cap.py | 1 | 0 |
| dr/test_vm_image_source_choice.py | 1 | 0 |
| frontend/test_dashboard_smoke.py | 1 | 0 |
| governance/meta_question/wo_intake_reconcile/test_registry_real_check.py | 1 | 0 |
| governance/persistence/test_base_repo.py | 4 | 0 |
| governance/red_blue_pkg14/test_rb14_s4_forged_marker.py | 6 | 0 |
| governance/red_blue_pkg14/test_rb14_s5_cache_poison.py | 1 | 0 |
| governance/rule_bridge/test_worktree_drift_watchdog_redteam_daemon.py | 1 | 0 |
| governance/security/test_governance_a2a_check.py | 3 | 0 |
| governance/security/test_governance_approver_check.py | 3 | 0 |
| governance/security/test_governance_bootstrap_superadmin.py | 4 | 0 |
| governance/security/test_governance_capability_check.py | 3 | 0 |
| governance/security/test_governance_contracts.py | 3 | 0 |
| governance/shared/test_post_sync_validation.py | 1 | 0 |
| governance/test_coordination_state_board.py | 1 | 0 |
| governance/test_decision_graph_reader.py | 2 | 0 |
| governance/test_delivery_card_canary.py | 2 | 0 |
| governance/test_extract_decisiongraph.py | 1 | 0 |
| governance/test_redblue_governance.py | 3 | 0 |
| governance/test_registry_dedup_audit.py | 2 | 0 |
| intent/test_intent_keyword_mapper_root.py | 1 | 0 |
| intent/test_intent_parser_root.py | 1 | 0 |
| llm_security/test_db.py | 8 | 0 |
| llm_security/test_runtime_interceptor.py | 2 | 0 |
| multi/test_multi_agent_collusion_detector.py | 1 | 0 |
| observability/test_observability_root.py | 5 | 0 |
| regime/test_regime_detector.py | 1 | 0 |
| rollback/test_rollback_sandbox.py | 1 | 0 |
| rule/test_rule_injection_guard.py | 1 | 0 |
| scripts/backup/test_backup_ps_scripts.py | 1 | 0 |
| scripts/test_websearch_ingest.py | 1 | 0 |
| shared/io/test_file_utils_atomic_retry.py | 2 | 0 |
| trading/pipeline/test_l03_signal_generation.py | 4 | 0 |
| trading/test_decision_map_r9_depgraph_check.py | 1 | 0 |
| trading/test_protection_index.py | 15 | 0 |

### 3.3 运行时可用性守卫清单（123 文件，复活条件=环境）

| 测试文件 | 痕迹 | reason 首条（80 字符） |
|---|---|---|
| agent_rbac/test_integration_root.py | 1 | pytest.skip(f"Cannot import integration: {exc}", allow_module_level=True) |
| agent_rbac/test_rbac_auto_lifecycle.py | 1 | pytest.skip("hook_registry not available in test environment") |
| ai_layer/comparator/conftest.py | 1 | pytest.skip("PostgreSQL 不可达（skip 而非假绿）") |
| ai_layer/comparator/test_comparison_ssot.py | 2 | pytest.skip( |
| ai_layer/comparator/test_venues.py | 1 | pytest.skip("考尺未建成（fail-closed 是既定态）") |
| ai_layer/switch_engine/test_rollout_tiers_ssot.py | 2 | pytest.skip( |
| ai_layer/tools/conftest.py | 1 | pytest.skip("PostgreSQL 不可达（skip 而非假绿）") |
| architecture/test_layer_isolation.py | 1 | pytest.skip(f"非层文件: {filepath}") |
| audit/audit_core/test_audit_red_blue_e2e.py | 3 | pytest.skip("GateEngine not available") |
| audit/audit_core/test_audit_registry_gate_e2e.py | 1 | pytest.skip("check_critical_findings not available in phase_check_registry", all |
| audit/drift_integrity/test_symlink_checker.py | 2 | pytest.skip("symlinks not supported on this platform") |
| automation/test_flowthrough_verifier.py | 2 | ClickHouse 证据通道不可用 |
| autonomy/test_agent_spec_e2e.py | 1 | pytest.skip(f"Skill not loadable: {result['error']}") |
| autonomy/test_assembly_context_assembler.py | 1 | pytest.skip(f"cannot import context_assembler: {_exc}", allow_module_level=True) |
| autonomy/test_assembly_context_injector.py | 1 | pytest.skip(f"cannot import context_injector: {_exc}", allow_module_level=True) |
| autonomy/test_assembly_context_pipeline.py | 1 | pytest.skip(f"cannot import context_pipeline: {_exc}", allow_module_level=True) |
| autonomy/test_curation_loop_root.py | 1 | pytest.skip(f"无法导入 curation_loop: {exc}", allow_module_level=True) |
| autonomy/test_dispatch_table_root.py | 1 | pytest.skip(f"无法导入 dispatch_table: {exc}", allow_module_level=True) |
| autonomy/test_doc_compressor_root.py | 1 | pytest.skip(f"无法导入 doc_compressor: {exc}", allow_module_level=True) |
| autonomy/test_host_resource_governor.py | 1 | pytestmark = pytest.mark.skip(reason=f"import failed: {_exc}") |
| autonomy/test_list_ce_files.py | 1 | pytest.skip(f"cannot import list_ce_files: {_exc}", allow_module_level=True) |
| autonomy/test_mgmt_context_budget_tracker.py | 1 | pytest.skip(f"cannot import context_budget_tracker: {_exc}", allow_module_level= |
| autonomy/test_mgmt_context_evictor.py | 1 | pytest.skip(f"cannot import context_evictor: {_exc}", allow_module_level=True) |
| autonomy/test_mgmt_context_rot_model.py | 1 | pytest.skip(f"cannot import context_rot_model: {_exc}", allow_module_level=True) |
| autonomy/test_parsing_intent_keyword_mapper.py | 1 | pytest.skip(f"无法导入 intent_keyword_mapper: {_exc}", allow_module_level=True) |
| autonomy/test_parsing_intent_parser.py | 1 | pytest.skip(f"无法导入 intent_parser: {_exc}", allow_module_level=True) |
| autonomy/test_pipeline_skill_injection.py | 2 | pytest.skip("PipelineOrchestrator not available") |
| autonomy/test_support_architecture_context_loader.py | 1 | pytest.skip(f"cannot import architecture_context_loader: {_exc}", allow_module_l |
| autonomy/test_support_doc_compressor.py | 1 | pytest.skip(f"无法导入 doc_compressor: {_exc}", allow_module_level=True) |
| autonomy/test_support_prompt_registry.py | 1 | pytest.skip(f"cannot import prompt_registry: {_exc}", allow_module_level=True) |
| autonomy/test_support_system_snapshot.py | 1 | pytest.skip(f"无法导入 system_snapshot: {_exc}", allow_module_level=True) |
| backtest/test_collection_hygiene.py | 1 | pytest.skip("tomllib unavailable") |
| backtest/test_n_trial_ledger.py | 1 | pytest.skip("git 不可用，无法构造真 eol=lf 钉定面") |
| backtest/test_t0_state_match_matrix.py | 1 | pytest.skip("six_phase_history_v1.csv 不在当前工作区（worktree 件）") |
| ce/test_ce_cache_invalidation.py | 1 | pytest.skip(f"cannot import cache_invalidation: {_exc}", allow_module_level=True |
| ce/test_ce_integrity_check.py | 1 | pytestmark = pytest.mark.skip(reason=f"import failed: {_exc}") |
| conftest.py | 3 | pytest.skip("ZEPHYR_TEST_PG!=1，跳过 PG 测试轨（默认 SQLite 快速路径）") |
| context/test_context_evictor_root.py | 1 | pytest.skip(f"cannot import context_evictor: {_exc}", allow_module_level=True) |
| context/test_context_injector_real_backend_integration.py | 2 | pytestmark = pytest.mark.skipif( |
| context/test_context_rule_registry_root.py | 1 | pytest.skip(f"cannot import context_rule_registry: {_exc}", allow_module_level=T |
| data/test_source_sla_tracker.py | 2 | pytest.skip( |
| data_governance/test_static_lineage_analyzer.py | 1 | pytest.skip("sqlglot 已安装环境不走降级路径") |
| dr/test_backup_lock_semantics.py | 1 | pytest.skip(f"git show HEAD:{_PS1_REL} 不可用（非 git 环境）") |
| escalation/test_escalation_handler.py | 1 | pytest.skip(f"无法导入 escalation_handler: {_exc}", allow_module_level=True) |
| ex_core/test_price_cage_bf6_wiring.py | 2 | pytest.skip( |
| experiment_tracking/test_experiment_history.py | 1 | pytest.skip("panel 未装") |
| fle/test_fle_regime_detector.py | 2 | pytest.skip( |
| gov_enforcement/test_create_guard_token_sim_shadow.py | 1 | pytest.skip("主仓无历史 warn 账本（空窗期），锚无样本可重放") |
| gov_enforcement/test_state_vocab_registry_gate.py | 2 | pytest.skip( |
| governance/audit/test_sbom_generator.py | 2 | pytest.skip( |
| governance/audit/test_verdict_engine.py | 5 | pytest.skip("AuditEntryV1 not available") |
| governance/commit_gates/test_ch_final_gate_no_final_reads.py | 2 | pytest.skip(f"CH 不可达，引擎面无法真验：{exc}") |
| governance/commit_gates/test_file_copy_gate.py | 2 | pytest.skip("主区原文不在（HEAD 漂移），跳过孪生复刻") |
| governance/commit_gates/test_resource_schedule_gate.py | 2 | pytest.skip("生产注册表未生成") |
| governance/commit_gates/test_schema_file_exists_gate.py | 1 | pytest.skip(f"real YAML not found: {real_yaml_path}") |
| governance/commit_gates/test_test_source_consistency_gate.py | 8 | - pytest.skip(allow_module_level=True) → True |
| governance/d5_architecture/test_rule_store_pointer_liveness.py | 1 | pytest.skip(f"数据卷不可见（{data_dir} 不存在）——死指针尺拒绝把『看不见』当成『通过』") |
| governance/d7_code/test_compare_pytest_configs.py | 1 | pytest.skip("py.ini 缺失=检出破损（根目录既有纳管件）") |
| governance/d8_doc_sync/test_guc_trigger_fix.py | 1 | pytest.skip(f"无法连接 PostgreSQL depgraph DB: {e}") |
| governance/d8_doc_sync/test_sync_savepoint_isolation.py | 2 | pytest.skip(f"无法连接 PostgreSQL depgraph DB: {e}") |
| governance/data_layer/test_akshare_real_data.py | 8 | skip_if_no_network = pytest.mark.skipif( |
| governance/depgraph/test_cross_domain_trigger.py | 9 | pytest.skip("PG 测试库未配置（ZEPHYR_TEST_PG_* 或 config/.env.postgres.test），跳过以防测试写生产表" |
| governance/depgraph/test_depgraph_db.py | 3 | pytest.skip( |
| governance/depgraph/test_depgraph_design_conversion.py | 1 | pytest.skip(f"depgraph PG 不可用: {e}") |
| governance/depgraph/test_depgraph_generator_design_protection.py | 1 | pytest.skip(f"PG depgraph 不可达（真 PG 集成钉，无 PG 环境跳过）: {exc}") |
| governance/meta_question/test_build_closure_ledger.py | 1 | pytest.skip("工单总册不在盘（worktree 环境）") |
| governance/registry_projection/test_fidelity_gate.py | 4 | pytest.skip(f"PG 快照不可达（留痕）: {exc}") |
| governance/rule_bridge/test_ssot_gate.py | 1 | pytest.skip( |
| governance/test_algo_quality.py | 1 | pytest.skip("chip_distribution_engine.py not built yet") |
| governance/test_align_panoramas.py | 2 | pytest.skip( |
| governance/test_apply_dataflowgraph_smoke.py | 2 | pytest.skip(f"PostgreSQL dataflowgraph 不可达（CI 环境？）: {e}") |
| governance/test_apply_decisiongraph_smoke.py | 2 | pytest.skip(f"PostgreSQL decisiongraph 不可达（CI 环境？）: {e}") |
| governance/test_apply_depgraph_smoke.py | 4 | pytest.skip(f"PostgreSQL depgraph 不可达（CI 环境？）: {e}") |
| governance/test_audit_fix_lanes_rulers.py | 1 | pytest.skip( |
| governance/test_battle_map_execution_flow.py | 1 | pytest.skip(f"battle_map PostgreSQL 不可达: {exc}") |
| governance/test_battle_map_research_incubation.py | 4 | pytest.skip(f"battle_map PostgreSQL 不可达: {exc}") |
| governance/test_battle_map_simulation_validation.py | 2 | pytest.skip(f"DB 不可达，跳过 e2e 测试: {e}") |
| governance/test_commit_perf_report_judgment.py | 1 | pytest.skip(f"commit_perf_report 模块加载失败: {e}", allow_module_level=True) |
| governance/test_dataflow_design_layout.py | 2 | pytest.skip( |
| governance/test_generate_dataflow_diagram.py | 2 | pytest.skip( |
| governance/test_generate_decision_diagram.py | 2 | pytest.skip( |
| governance/test_generate_project_depgraph_smoke.py | 6 | pytest.skip(f"PostgreSQL depgraph 不可达（CI 环境？）: {e}") |
| governance/test_reconcile_generators.py | 4 | pytest.skip(f"reconcile('battle_map_db') 抛异常（DB 不可达？）: {e}") |
| governance/test_registry_ledger.py | 5 | pytestmark = pytest.mark.skipif( |
| governance/test_registry_ledger_baseline.py | 2 | pytestmark = pytest.mark.skipif( |
| governance/test_shared_yaml_utils_reexport.py | 1 | pytest.skip(f"{_rel(shim, _REPO_ROOT)} 未声明静态 __all__（不强制，声明后本判据自动生效）") |
| governance/test_sync_yaml_to_depgraph_smoke.py | 10 | pytest.skip(f"get_depgraph_pg_connection 导入失败: {e}") |
| guard/test_guard_layers_root.py | 1 | pytest.skip(f"无法导入 guard_layers: {_exc}", allow_module_level=True) |
| infra_runtime/test_runtime_admission.py | 1 | pytest.skip("real registry missing") |
| infrastructure/test_audit_rename_completeness.py | 1 | pytestmark = pytest.mark.skip( |
| infrastructure/test_beta_e2e.py | 2 | pytest.skip( |
| infrastructure/test_f3_extreme.py | 1 | pytest.skip(f"FeedbackLoop raised expected exception on malformed input: {e}") |
| infrastructure/test_resource_schedule_regen_check.py | 1 | pytest.skip(f"本机 schtasks 探针不可用: {problems}") |
| infrastructure/test_vocab_sync_chain.py | 3 | pytest.skip("depgraph (PostgreSQL) 不可用") |
| intelligence/switch_engine/test_switch_criteria_ssot.py | 2 | pytest.skip( |
| intent/test_intent_binder_root.py | 1 | pytest.skip(f"Cannot import intent_binder: {exc}", allow_module_level=True) |
| io/test_depgraph_schema.py | 1 | pytestmark = pytest.mark.skip( |
| library/test_ledger_cache.py | 2 | pytest.skip(f"depgraph PG 不可达，实弹对拍需真源：{exc}") |
| llm_security/test_microstructure_defense.py | 2 | pytest.skip( |
| memory/test_memory_bank_root.py | 1 | pytestmark = pytest.mark.skip(reason=f"import failed: {_exc}") |
| memory/test_memory_guard.py | 1 | pytest.skip(f"Cannot import memory_guard: {_exc}", allow_module_level=True) |
| memory/test_memory_provenance_guard.py | 1 | pytest.skip(f"Cannot import memory_provenance_guard: {_exc}", allow_module_level |
| memory/test_vms_adversarial_hijack.py | 4 | pytest.skip( |
| ops/test_ollama_version_guard.py | 1 | pytest.skip("ollama 不在本执行环境 PATH（不影响守卫逻辑正确性）") |
| path/test_path_guard.py | 1 | pytest.skip(f"无法导入 path_guard: {_exc}", allow_module_level=True) |
| pipeline/test_pipeline_orchestrator_root.py | 1 | pytest.skip(f"Cannot import pipeline_orchestrator: {exc}", allow_module_level=Tr |
| prompt/test_prompt_registry_root.py | 1 | pytest.skip(f"Cannot import prompt_registry: {exc}", allow_module_level=True) |
| resource/test_process_pool.py | 3 | pytest.skip("shim 仅 Windows 语义") |
| risk/test_pot_failure_counter.py | 2 | pytest.skip(f"Redis 配置缺失，跳过 Redis 后端实测: {exc}") |
| rule/test_rule_integration.py | 4 | pytest.skip("skill_registry.yaml not found") |
| safety/test_event_integration.py | 1 | pytestmark = pytest.mark.skip( |
| safety/test_phase_manager_integration.py | 1 | pytestmark = pytest.mark.skip( |
| scripts/governance/d8_doc_sync/test_algo_flow_reverse_orphan_reconciler.py | 1 | pytest.skip("真仓裁定登记表不在检出内") |
| scripts/test_apply_resource_plan.py | 1 | pytest.skip("生成器尚无 parse_drill_entities（P4-α 未合流）") |
| scripts/test_run_post_settlement_disclosure.py | 2 | pytest.skip( |
| shared/lifecycle/test_registry_state_vocab.py | 2 | pytest.skip( |
| shared/test_safe_write.py | 1 | pytest.skip("无法创建 junction（环境限制）") |
| shared/test_state_store_redis.py | 2 | pytest.skip(f"Redis 配置缺失，跳过 Redis 后端实测: {exc}") |
| signal_ashare/sector/test_sector_attribute_rules.py | 1 | pytest.skip("配置文件不存在（CI 环境差异）") |
| skill/test_agent_spec_adversarial.py | 1 | pytest.skip("No domain+role skills registered") |
| task/test_task_repo_auto_commit.py | 1 | pytest.skip("DM-FAKE-001 任务不存在，transition 未走到 COMPLETED——场景未覆盖") |
| zephyr/data/test_capability_validator.py | 1 | pytest.skip(f"{name} provider 文件不存在: {path}") |
| zephyr/factor/test_indicator_reader.py | 1 | pytest.skip(f"CH 不可达: {e}") |

## 4. L3 双树对撞候选（tests/zephyr vs tests/<域>）

tests/zephyr 规模：150 个 .py（123 个含 `zephyr.*` import）/ 3716 collected items / 1 collection error。

### 4.1 同名对撞（3 对）——全部证伪为同音异义

| basename | tests/zephyr/ 侧 | 非 zephyr 侧 | 被测对象比对 | 判定 |
|---|---|---|---|---|
| test_market_calendar.py | zephyr/data/calendar/ | feedback/scheduling/ | zephyr.data.calendar.* vs zephyr.feedback_loop.collectors.market_calendar | 同名异义，非重复 |
| test_metrics.py | zephyr/data/ | backtest/ | src.zephyr.data.metrics vs zephyr.backtest.core.metrics | 同名异义，非重复 |
| test_reference_data_manager.py | zephyr/data/ | trading/ | zephyr.data.reference_data_manager vs zephyr.trading.reference_data_manager | 同名异义，非重复（生产侧本就两份） |

注：`tests/zephyr/data/test_metrics.py` 使用 `from src.zephyr.data.metrics import ...` 的 `src.` 前缀风格，与其余树 `zephyr.*` 风格不一致（本次 collection 未报错，因根 conftest 把仓库根也插入了 sys.path），属风格债非断链。

### 4.2 import 强对撞（7 对，真候选）——zephyr 树测试的主被测模块同时被非 zephyr 树测试覆盖

| tests/zephyr/ 侧 | 共享被测模块 | 非 zephyr 侧已有测试 |
|---|---|---|
| zephyr/backtest/test_ch_tick_replay.py | zephyr.backtest.implementations.ch_tick_replay | backtest/test_closed_book_tick_gate.py |
| zephyr/data/test_ch_parts_monitor.py | zephyr.data.ch_parts_monitor | governance/test_alert_threshold_consistency.py |
| zephyr/data/test_internal_compute_provider.py | zephyr.data.implementations.internal_compute_provider | data/test_internal_compute_provider_cohort_daily.py; data/test_internal_compute_provider_daban_load.py |
| zephyr/data/test_intraday_sentiment_loop.py | zephyr.data.intraday_sentiment_loop | integration/test_phase2_premarket_intraday_e2e.py |
| zephyr/data/test_sector_report_builder.py | zephyr.data.sector_report_builder | integration/test_phase2_premarket_intraday_e2e.py |
| zephyr/infrastructure/test_redis_config.py | zephyr.infrastructure.redis_config | risk/test_pot_failure_counter.py; shared/test_state_store_redis.py |
| zephyr/shared/infra/test_process_lifecycle_gateway.py | zephyr.shared.infra.process_lifecycle_gateway | infrastructure/mcp/test_mcp_*_*.py ×5 |

### 4.3 弱层共享（参考，非候选）：67 个 zephyr 树测试与非 zephyr 树共享 105 个被测 import，但绝大多数是共享**基础模块**（provider_base / policy_registry / ch_reader / contracts / time_utils 等），即两树都在用公共底座，不构成「同被测对象两份」。逐对明细：`.runtime/tmp/census_l3_import.json`。

## 5. L4 一次性验证线索（184 文件，隔离不删）

原始命中 187：文件名/正文含 redblue / red_blue / adversarial / 对抗 / redteam / surgery / 手术 / wave / 验证批。剔除 3 个 wave_generator 误报（生产模块 `src/zephyr/orchestrator/execution/wave_generator.py` 的正常单测：orchestrator/test_orchestrator_wave_generator.py、orchestrator/test_wave_generator_orchestrator.py、trading/unit/test_wave_generator_unit.py）。

### 5.1 名称强命中（76 文件）

- agent_rbac/test_adversarial_agent_rbac.py
- agent_rbac/test_adversarial_resilience.py
- agent_rbac/test_rbac_adversarial.py
- agent_rbac/test_redteam_adversarial.py
- agent_rbac/test_session_aware_stash_red_blue.py
- alpha_signal/test_adversarial_alpha_signal.py
- audit/audit_core/test_audit_adversarial.py
- audit/audit_core/test_audit_red_blue_e2e.py
- automation/test_auto_fix_red_blue.py
- autonomy/test_adversarial_robustness.py
- autonomy/test_context_pipeline_red_blue.py
- autonomy/test_task_system_red_team.py
- backtest/test_p0_validation_adversarial.py
- backtest/test_strategy_production_map_adversarial.py
- cross/test_e2e_redblue_night001.py
- data/test_wave3_date_normalize.py
- data/test_wave3_dual_source_guard.py
- data/test_wave3_miniqmt_caliber.py
- db/test_db_red_blue.py
- f_lifecycle/test_f10_red_blue.py
- f_lifecycle/test_f18_redblue.py
- f_lifecycle/test_f5_red_team_extreme.py
- factor/test_red_blue_lifecycle.py
- federated_learning/test_fl_adversarial_validation.py
- governance/adversarial/test_adversarial_tester.py
- governance/audit/test_arch_diagram_wave_concurrency.py
- governance/budget/test_adversarial_extreme.py
- governance/code_quality/test_code_dedup_engine_red_team.py
- governance/commit_gates/test_frontend_truth_source_gate_redteam.py
- governance/d5_architecture/test_construction_workflow_map_adversarial.py
- governance/d5_architecture/test_data_supply_chain_map_adversarial.py
- governance/d5_architecture/test_dev_delivery_map_adversarial.py
- governance/d5_architecture/test_fig14_fig15_map_bodies_adversarial.py
- governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py
- governance/d5_architecture/test_trading_day_cycle_map_adversarial.py
- governance/generators/test_externalize_algo_flow_redblue.py
- governance/governance_e2e/test_validate_rule_frontmatter_red_blue.py
- governance/meta_question/test_redblue_metaq_suite.py
- governance/rule_bridge/test_commit_pipeline_redblue.py
- governance/rule_enforcement/gate_engine/test_adversarial_gate_integration.py
- governance/rule_enforcement/gate_engine/test_adversarial_validation.py
- governance/rule_enforcement/gate_engine/test_adversarial_validation_gate.py
- governance/rule_enforcement/test_adversarial_strategies.py
- governance/security/test_adversarial_contract_attacks.py
- governance/test_alignment_gates_red_blue.py
- governance/test_library_reconcilers_red_blue.py
- governance/test_redblue_governance.py
- governance/test_redblue_robust.py
- governance/test_wave1a_query_shape_ruler.py
- governance/test_wave1a_strict_read_canary.py
- infrastructure/adversarial/test_capacity_runtime_red_blue.py
- infrastructure/adversarial/test_escalation_adversarial.py
- infrastructure/adversarial/test_f18_governance_adversarial.py
- infrastructure/drift_red_blue_adversarial.py
- infrastructure/mcp/test_mcp_red_team.py
- infrastructure/observability/test_telemetry_red_team.py
- llm_security/test_adversarial_mutator.py
- llm_security/test_l7_red_team.py
- memory/test_vms_adversarial_hijack.py
- memory/test_vms_adversarial_injection.py
- ml_experiment/test_adversarial_ml.py
- ml_experiment/test_adversarial_ml_experiment.py
- ml_train/test_adversarial_robustness_validator.py
- rollback/test_concurrency_guard_red_blue.py
- rollback/test_rollback_adversarial.py
- rule/test_rule_red_blue.py
- safety/test_red_blue_validator.py
- safety/test_red_blue_validator_tests.py
- semantic_auditor/test_blast_radius_red_team.py
- skill/test_agent_spec_adversarial.py
- strategy_factory/test_s_owner_002_redblue.py
- strategy_pipeline/test_redblue.py
- trading/test_decision_map_adversarial.py
- trading/test_decision_map_d38_adversarial.py
- utils/test_adversarial_shared.py
- zephyr/data/test_hardening_redblue_20260916.py

### 5.2 仅正文命中（108 文件，docstring/注释提及对抗或手术语境）

- agent_rbac/test_novel_attack.py
- agent_rbac/test_permissions.py
- ai_layer/heritage/test_heritage_ddl.py
- audit/audit_core/test_audit_integration_fracture.py
- autonomy/test_agent_spec_e2e.py
- autonomy/test_pipeline_bridge_integration.py
- backtest/test_auto_mount.py
- backtest/test_backtest_result_sink.py
- backtest/test_rb_stats_validator_teeth.py
- backtest/test_run_archive_red.py
- backtest/test_toy_reconciliation_night001.py
- db/test_dm400_stale_task_fix.py
- ex_sor/test_sell_session_router.py
- feedback/anomaly_diagnosis/test_automated_rca_postmortem_generator.py
- git/test_claim_retention_derived_attribution.py
- git/test_dead_session_salvage.py
- git/test_git_commit_concurrent.py
- git/test_lock_files_first_acquire_guide.py
- gov_enforcement/test_create_guard_token_sim_shadow.py
- governance/audit/test_integrity_audit_reconciler.py
- governance/audit/test_integrity_head_baseline.py
- governance/audit/test_module_id_header_injector_rc14.py
- governance/code_quality/test_n16_exemption_loader.py
- governance/commit_gates/test_approval_wiring.py
- governance/commit_gates/test_construction_workflow_map_gate.py
- governance/commit_gates/test_data_supply_chain_map_gate.py
- governance/commit_gates/test_registry_mass_deletion_gate.py
- governance/commit_gates/test_split_coordination_gate.py
- governance/commit_gates/test_strategy_factory_map_gate.py
- governance/commit_gates/test_trading_day_cycle_map_gate.py
- governance/d3_metadata/test_batch_creation_tokens.py
- governance/generators/test_map_coverage_attribution.py
- governance/red_blue_pkg14/_common.py
- governance/red_blue_pkg14/conftest.py
- governance/red_blue_pkg14/test_rb14_s1_worker_revival.py
- governance/red_blue_pkg14/test_rb14_s2_dual_writer.py
- governance/red_blue_pkg14/test_rb14_s3_fault_injection.py
- governance/red_blue_pkg14/test_rb14_s4_forged_marker.py
- governance/red_blue_pkg14/test_rb14_s5_cache_poison.py
- governance/red_blue_pkg14/test_rb14_s6_starvation.py
- governance/red_blue_pkg14/test_rb14_s7_cross_lane.py
- governance/redblue_wave73/test_v1_v3_forged_node_and_domain.py
- governance/redblue_wave73/test_v2_dangling_reference.py
- governance/redblue_wave73/test_v3_real_domain_misattach.py
- governance/redblue_wave73/test_v4_extract_clone_no_escape.py
- governance/redblue_wave73/test_v5_forged_production_status.py
- governance/redblue_wave73/test_v6_forbidden_edge_map_alignment.py
- governance/redblue_wave73/test_v7_pid_reuse.py
- governance/redblue_wave73/test_v8_hot_registry_whole_overwrite.py
- governance/registry_projection/test_fidelity_gate.py
- governance/rule_bridge/test_ssot_gate.py
- governance/test_commit_queue_landing_nightfix.py
- governance/test_git_hooks_marker_forgery.py
- governance/test_merge_domain_fk_scan_guard.py
- governance/test_precommit_channel_out_of_lock.py
- governance/test_register_asset_cli.py
- governance/test_registry_entry_counts.py
- governance/test_registry_entry_counts_reconciler.py
- governance/test_registry_ledger_baseline.py
- governance/test_reuse_scan.py
- governance/test_ruff_preclean_enqueue.py
- infrastructure/drift/test_drift_extended_e2e.py
- infrastructure/mcp/test_mcp_gateway_version_ratelimit.py
- infrastructure/mcp/test_mcp_health_check_recovery.py
- infrastructure/test_audit_rename_completeness.py
- infrastructure/test_f3_extreme.py
- intelligence/test_chain_impact_resolver.py
- intelligence/test_chain_impact_stream.py
- intelligence/test_news_chain_node_linker.py
- io/test_verify_schema_health.py
- library/test_lookup_import_surface.py
- llm_security/__init__.py
- llm_security/test_runtime_interceptor.py
- metamorphic/test_fourgate_metamorphic_invariants.py
- ml_train/test_ml_model_factory.py
- path/test_path_tree_generator_design_protection.py
- plan_engine/test_daily_plan.py
- plan_engine/test_intraday_tomorrow_forecast.py
- plan_engine/test_thesis_survival.py
- position/test_defensive_asset_whitelist.py
- position/test_pyramiding_rules.py
- regime/test_index_sensor.py
- rollback/test_concurrent_mv_guard.py
- rollback/test_rollback_concurrent_extreme.py
- rollback/test_rollback_partial_extreme.py
- rollback/test_rollback_scheduler.py
- safety/test_async_monitor.py
- safety/test_circuit_breaker.py
- safety/test_commit_trigger.py
- safety/test_constitution_engine.py
- safety/test_defense_runner.py
- safety/test_event_integration.py
- safety/test_game_day_scheduler.py
- safety/test_injection_engine.py
- safety/test_phase_manager_integration.py
- scripts/test_algo_flow_translation_sync.py
- security/test_session_registry_chief_form.py
- signal_ashare/sector/test_sector_conduction.py
- signal_ashare/test_daily_condition_sensor.py
- signal_ashare/test_tradability_preflight.py
- signal_fundamental/test_negative_veto.py
- simulation/test_overfitting_protection_gate.py
- skill/test_skill_postmortem.py
- trading/extreme/test_f14_pipeline_extreme.py
- trading/extreme/test_f1_extreme.py
- trading/test_incident_postmortem.py
- trading/test_validation_ablation.py
- zephyr/factor/technical_indicators/test_numeric_guards.py

## 6. 方法论注（复现与坑）

1. **全量单进程 collection 会挂死**：`pytest tests/ --collect-only -q` 单进程 20 分钟 0 进展（CPU 1.25s）。根因链：tests/conftest.py → `import zephyr` → `__init__` 起 auto_bootstrap/secret_rotation/service_registration 三个后台 Timer 线程做全模块 monkey-patch，与 collection 主线程竞争。改用**分块普查**：132 个顶层块（180s 超时）+ context/governance 两块超时后 60 个下钻块（240s 超时），6/5 并行，全部完成、下钻零超时（两域是体量超时非挂死）。
2. **skip 粗分会高估永久数**：一维裸/skipif 分类把 93 个文件判「永久」；引入第三维（函数体 `pytest.skip()` 的可用性守卫文本：不可达/缺失/not found/Cannot import）后，真永久塌缩到 4。凡 reason 带环境词的都不是 L2。
3. 断链检测不能只做模块路径静态解析（6557 条 import 0 断链），必须实跑 collection 抓符号级/文件级错误。
4. 分块命令形态：`python -m pytest tests/<域> --collect-only -q -p no:randomly --no-header -o addopts=`（`-o addopts=` 清掉 pyproject 的 -v/--tb，输出短摘要便于聚合）。
