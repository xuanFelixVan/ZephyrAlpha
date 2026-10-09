---
ttl: task_bound
completes_when: 复活工单全部落地或销案
---
# 死信清偿专案 · 复活工单登记册（机读 YAML 载荷，生成器产出，禁手工维护）

```yaml
# 死信清偿专案 · 复活工单登记册（生成器产出，禁手工维护）
generated_at: '2026-10-09T05:32:38+08:00'
source_of_truth: .runtime/tmp/st-deadcure-20261009/common/action_plan.json
cluster_total: 221
bag_total: 1289
---
clusters:
  - id: chief_revive_additive_new/None
    bags: 89
    families: ["chaos2-st-06", "st-closeout-basereq-20261006", "st-cmd-20260924", "st-cure-p01-20261006", "st-cure-p02-20261006", "st-cure-p05-20261006"]
    flags: {"P0_tests_hole": 6}
    adjudication: "bag only adds brand-new paths (no HEAD line destroyed), but new files need creation_token/translation/14-field"
    qids_sample: ["mine-20260927-0003", "hief-20261004-0018", "n-w2-20261006-0001", "-p01-20261006-0029", "-p01-20261006-0066"]
    missing_paths_sample: ["docs/_working/question_mining_20260927/00_charter.md", "tests/governance/commit_gates/test_tdm_mount_coverage_gate.py", "docs/_working/handoff_ownscope_expansion_m2.md", "docs/_working/fullflow_chief_20261001/skeleton/F_risk_compliance/F62.md", "docs/_working/sector_line/statreplay/freeze_baseline.py", "docs/_working/circulation_chief/logs/wave4d.md", "docs/_working/decision_map_campaign_20260924/links/L08_risk/arbitration_order_v1_draft.md", "docs/_working/tests_cure_campaign/01_structure_census.md"]
  - id: lane1/l1-tests_01
    bags: 76
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 76, "P0_tests_hole": 75}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0002", "hief-20261004-0019", "hief-20261004-0020", "hief-20261004-0031", "hief-20261004-0032"]
    missing_paths_sample: ["tests/ai/ai/test_ai_comment_veracity.py", "tests/ai/ai/test_ai_construction_detectors.py", "tests/ai/ai/test_ai_context_injector.py", "tests/ai/ai/test_ai_self_diagnosis.py", "tests/ai/ai/test_l08_human_ai_interface.py", "tests/ai/ai_layer/redline/test_annual_review.py", "tests/ai/ai_layer/redline/test_negative_list.py", "tests/ai/ai_layer/redline/test_session_env_guard.py"]
  - id: lane6/l6-c01
    bags: 54
    families: ["st-cure-p08b-20261006"]
    flags: {"P0_tests_hole": 54}
    adjudication: "重投班会话自己先死：存活闸按属主 heartbeat 判活，st-cure-p08b 等 exited→一律拒（裁定#459）。非内容坏，属设施性可修因致死，同签名上一轮已误伤 124 袋。"
    qids_sample: ["p08b-20261006-0002", "p08b-20261006-0003", "p08b-20261006-0004", "p08b-20261006-0005", "p08b-20261006-0007"]
    missing_paths_sample: ["tests/ai/intelligence/switch_engine/conftest.py", "tests/ai/intelligence/switch_engine/test_criteria.py", "tests/ai/intelligence/switch_engine/test_shadow_runner.py", "tests/ai/intelligence/switch_engine/test_switch_criteria_ssot.py", "tests/ai/intelligence/switch_engine/test_switch_engine.py", "tests/ai/intelligence/switch_engine/test_switch_registry.py", "tests/ai/intelligence/test_agent_memory_architecture.py", "tests/ai/intelligence/test_api_llm_pool.py"]
  - id: lane4/l4-01
    bags: 37
    families: ["st-f15-frombag-20261005"]
    flags: {"lane_claim_overridden": 37, "P0_tests_hole": 12}
    adjudication: "重投班 st-f15 死于重投机制本身（cascade_stale 基底重校验不适用 / 快照基底与 dev 冲突 / 三向合并失败）。44 袋 1248 件：HEAD 全缺 100（路径今不在 HEAD 98、他径亦无"
    qids_sample: ["mbag-20261005-0011", "mbag-20261005-0012", "mbag-20261005-0015", "mbag-20261005-0018", "mbag-20261005-0019"]
    missing_paths_sample: ["docs/_working/ai_layer_vision/P1_resume_files_v1.txt", "docs/_working/ai_layer_vision/P1_resume_files_v2.txt", "tests/ai_layer/redline/test_annual_review.py", "tests/ai_layer/redline/test_negative_list.py", "tests/ai_layer/redline/test_negative_list_gates.py", "tests/ai_layer/redline/test_session_env_guard.py", "tests/ai_layer/redline/test_sev_router.py", "docs/_working/align_dirty/LEDGER.md"]
  - id: lane7/l7-c16
    bags: 36
    families: ["st-cmd-20260924", "st-cure-p02-20261006", "st-cure-p03-20261006", "st-cure-p06-20261006", "st-f11-requeue-20261005", "st-final-build-20260926"]
    flags: {"P0_tests_hole": 8}
    adjudication: "regression_risk（rule R-4）：HEAD 已演进过快照，盲重投会删掉最多 max_only_head 条更新行——只能行级摘取（line-level cherry pick），禁 requeue --"
    qids_sample: ["-cmd-20260924-0033", "uild-20260926-0012", "uild-20260926-0015", "uild-20260926-0022", "uild-20260926-0027"]
    missing_paths_sample: ["tests/backtest/test_factory_grid_stage_cost_tiers.py", "scripts/signals/chart_condition_package.py", "src/zephyr/gov_enforcement/rule_bridge/union_priority_ruler.py", "src/zephyr/shared/foundation/flag_read_state.py", "scripts/governance/meta/rules_integrity_db.json", "scripts/signals/chart_condition_package.py", "scripts/governance/meta/rules_integrity_db.json", "scripts/signals/chart_condition_package.py"]
  - id: lane6/l6-c02
    bags: 33
    families: ["st-cure-p12a-20261006", "st-cure-p12b-20261006"]
    flags: {"P0_tests_hole": 11}
    adjudication: "袋侧与 dev 侧同文件皆改，落地侧整文件三方判真冲突→按设计死信回人工。欠账真实存在（多数件仍在树），只能逐行判侧。"
    qids_sample: ["p12a-20261006-0005", "p12a-20261006-0009", "p12a-20261006-0011", "p12a-20261006-0012", "p12a-20261006-0013"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py", "docs/_working/ai_layer_vision/closure_wave2/AI1_routing_and_caliber.md", "docs/_working/ai_layer_vision/closure_wave2/AI2_scheduling_host_confirm.md", "docs/_working/ai_layer_vision/closure_wave2/AI3_design_flips_and_filings.md", "docs/_working/ai_layer_vision/closure_wave2/AI4_ratification_secrets_vocab.md", "docs/_working/ai_layer_vision/closure_wave2/l6_tombstone_ttl_cleanup_proposal.yaml", "docs/_working/ai_layer_vision/OBJ_T_tools/sandbox_profile_v0.yaml", "docs/_working/ai_layer_vision/OBJ_T_tools/tool_trial_card_template_v0.yaml"]
  - id: lane7/l7-c11
    bags: 30
    families: ["st-cmd-20260924", "st-cure-p03-20261006", "st-cure-p05-20261006", "st-datasop-20260930", "st-f11-requeue-20261005", "st-final-build-20260926"]
    flags: {"P0_tests_hole": 5}
    adjudication: "hot-registry 整档快照（rule R-3）：盲 requeue --from-bag 会蒸发他队已落地条目（capability 册 62k 行事故在案），禁重投；未落地 delta 走正道（PG token"
    qids_sample: ["-cmd-20260924-0016", "uild-20260926-0002", "uild-20260926-0003", "uild-20260926-0004", "uild-20260926-0007"]
    missing_paths_sample: ["docs/_working/decision_map_campaign_20260924/01_goal_and_architecture.md", "docs/_working/decision_map_campaign_20260924/02_rulings_and_calibers.md", "tests/governance/test_enforcement_surface_reconcile_canary.py", "tests/governance/test_delivery_card_canary.py", "tests/governance/test_enforcement_surface_reconcile_canary.py", "tests/governance/test_delivery_card_canary.py", "tests/governance/test_enforcement_surface_reconcile_canary.py", "tests/governance/test_delivery_card_canary.py"]
  - id: lane2/l2-c17
    bags: 24
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 5}
    adjudication: "F123 迁移通道三件套里只有台账册 REG-SCHEMA-MIG-001 落了 HEAD，runner/CLI/DatabaseService.migrate() 代码面全仓零命中（工作树亦无）⇒ 通道真没落、仍要；死"
    qids_sample: ["-p01-20261006-0006", "-p01-20261006-0007", "-p01-20261006-0015", "-p01-20261006-0024", "-p01-20261006-0034"]
    missing_paths_sample: ["src/zephyr/infrastructure/schema_migrations.py", "scripts/governance/apply_schema_migrations.py", "tests/infrastructure/test_schema_migrations.py", "src/zephyr/governance/meta_question/vocab_loader.py", "src/zephyr/governance/reuse_scan.py", "tests/alt_data/test_emotion_index_replay.py", "docs/_working/emotion_line/index.md", "src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py"]
  - id: lane7/l7-c12
    bags: 24
    families: ["st-cure-p06-20261006", "st-datasop-20260930", "st-f11-requeue-20261005", "st-final-build-20260926", "st-govfix-g4-20261007", "st-mastertc-l7"]
    flags: {"P0_tests_hole": 1}
    adjudication: "hot-registry 整档快照（rule R-3）：盲 requeue --from-bag 会蒸发他队已落地条目（capability 册 62k 行事故在案），禁重投；未落地 delta 走正道（PG token"
    qids_sample: ["uild-20260926-0008", "uild-20260926-0009", "uild-20260926-0014", "uild-20260926-0019", "work-20260928-0001"]
    missing_paths_sample: ["scripts/signals/chart_condition_package.py", "scripts/signals/chart_condition_package.py", "scripts/governance/meta/rules_integrity_db.json", "scripts/signals/chart_condition_package.py", "tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py"]
  - id: lane5/l5-c01
    bags: 23
    families: ["st-chief7-20260928"]
    flags: {"lane_claim_overridden": 23, "P0_tests_hole": 23}
    adjudication: "38 袋=同批治理生成器的反复重投快照。本体全部在 HEAD，行差源于 10-01 总包按 CLONEGUARD 单源化合并重构=被取代；真缺只剩 4 把证尺，走行级摘取。"
    qids_sample: ["ief7-20260928-0095", "ief7-20260928-0173", "ief7-20260928-0253", "ief7-20260928-0329", "ief7-20260928-0405"]
    missing_paths_sample: ["tests/data/test_wave3_date_normalize.py", "tests/data/test_wave3_dual_source_guard.py", "tests/data/test_wave3_miniqmt_caliber.py", "tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/data_supply/__init__.py", "tests/governance/data_supply/test_false_green_crosscheck.py", "tests/data/test_wave3_date_normalize.py"]
  - id: lane6/l6-c03
    bags: 22
    families: ["st-cure-p08b-20261006", "st-cure-p10-20261006", "st-cure-p12b-20261006", "st-sP-bottleneck-20261005"]
    flags: {"P0_tests_hole": 18}
    adjudication: "own-scope 临时索引重跑 pre-commit hook（ruff/ruff-format/gate-naming）拦本袋文件。搬家与陈旧快照把存量违规当新增行二次拦——同签名必复发。"
    qids_sample: ["neck-20261005-0116", "p08b-20261006-0001", "-p10-20261006-0003", "-p10-20261006-0010", "-p10-20261006-0012"]
    missing_paths_sample: ["tests/ai/intelligence/model_routing/test_runtime_assembly.py", "tests/ai/intelligence/switch_engine/conftest.py", "tests/ai/intelligence/switch_engine/test_criteria.py", "tests/ai/intelligence/switch_engine/test_shadow_runner.py", "tests/ai/intelligence/switch_engine/test_switch_criteria_ssot.py", "tests/ai/intelligence/switch_engine/test_switch_engine.py", "tests/ai/intelligence/switch_engine/test_switch_registry.py", "tests/ai/intelligence/test_agent_memory_architecture.py"]
  - id: lane2/l2-c24
    bags: 20
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 3}
    adjudication: "缺面逐件复查：8 件已按新家落位（tests 八域归位），15 件同名同父目录零命中=真没落（reuse_scan.yaml、lane_alive.md、apply_meta_question_ddl.py）⇒ 主体②归"
    qids_sample: ["-p01-20261006-0004", "-p01-20261006-0005", "-p01-20261006-0008", "-p01-20261006-0011", "-p01-20261006-0022"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/rule_bridge/union_priority_ruler.py", "src/zephyr/shared/foundation/flag_read_state.py", "src/zephyr/governance/registry_projection/generator.py", "tests/ex_core/test_qmt_trading_session.py", "tests/zephyr/data/quality/test_sla_breach_predictor.py", "tests/ai_layer/scheduling/test_confirm_gate.py", "tests/ai_layer/redline/test_ai_secret_exposure.py", "src/zephyr/governance/meta_question/registry.py"]
  - id: lane3/l3-c00
    bags: 20
    families: ["st-closeout-basereq-20261006", "st-combine-20260923"]
    flags: {"P0_tests_hole": 18}
    adjudication: "组合层接电批部分已由他道落地（082d4591e79 的 L9 就绪度闸接线），但本批核心面——REGIME_TO_SEGMENT SSOT 下移、config/pf_alloc.yaml、tests/pf_alloc "
    qids_sample: ["bine-20260923-0001", "bine-20260923-0002", "bine-20260923-0003", "bine-20260923-0004", "bine-20260923-0005"]
    missing_paths_sample: ["config/pf_alloc.yaml", "tests/pf_alloc/test_allocation_team_wiring.py", "tests/pf_alloc/test_allocation_chain.py", "docs/_working/pf_alloc_wiring/delivery_report_pf_alloc_wiring.md", "config/pf_alloc.yaml", "tests/pf_alloc/test_allocation_team_wiring.py", "tests/pf_alloc/test_allocation_chain.py", "docs/_working/pf_alloc_wiring/delivery_report_pf_alloc_wiring.md"]
  - id: lane2/l2-c25
    bags: 19
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 2}
    adjudication: "缺面逐件复查：7 件已按新家落位（tests 八域归位），14 件同名同父目录零命中=真没落（data_supply_chain_map_gate.yaml、dead_letter_surgery_ledger.md、i"
    qids_sample: ["-p01-20261006-0001", "-p01-20261006-0010", "-p01-20261006-0012", "-p01-20261006-0013", "-p01-20261006-0026"]
    missing_paths_sample: ["tests/scripts/test_generate_resource_profile_registry.py", "tests/backtest/test_f06_e4_wfa_exam.py", "tests/scripts/test_generate_resource_profile_registry.py", "tests/backtest/test_f06_e4_wfa_exam.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py"]
  - id: lane1/l1-tests_02
    bags: 17
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 17, "P0_tests_hole": 17}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0014", "hief-20261004-0016", "hief-20261004-0033", "hief-20261004-0034", "hief-20261004-0036"]
    missing_paths_sample: ["tests/gov/feedback/learning_evolution/test_evolution_engine_root.py", "tests/gov/feedback/learning_evolution/test_evolution_init.py", "tests/gov/feedback/learning_evolution/test_graduated_activation_protocol.py", "tests/gov/feedback/learning_evolution/test_hypernetwork.py", "tests/gov/feedback/learning_evolution/test_nonstationary_effectiveness.py", "tests/gov/feedback/learning_evolution/test_online_feature_importance.py", "tests/gov/feedback/learning_evolution/test_teacher_transfer.py", "tests/gov/feedback/learning_evolution/test_training_data_gov.py"]
  - id: lane2/l2-c26
    bags: 17
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 5}
    adjudication: "缺面逐件复查：2 件已按新家落位（tests 八域归位），15 件同名同父目录零命中=真没落（P1_resume_files_v1.txt、P1_resume_files_v2.txt、LEDGER.md）⇒ 主体②归档"
    qids_sample: ["-p01-20261006-0020", "-p01-20261006-0031", "-p01-20261006-0061", "-p01-20261006-0063", "-p01-20261006-0068"]
    missing_paths_sample: ["docs/_working/wave13_chief3/inbox/merger_identity/01_case_file.md", "docs/_working/deadletter_cure_20261003/20_design/commit_map_and_slimming_plan.md", "docs/_working/align_dirty/LEDGER.md", "docs/_working/decision_map_campaign_20260924/01_goal_and_architecture.md", "docs/_working/decision_map_campaign_20260924/02_rulings_and_calibers.md", "docs/_working/decision_map_campaign_20260924/12_data_universe_census.md", "docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/allocation_rule_v1_draft.md", "docs/_working/decision_map_campaign_20260924/links/L08_risk/arbitration_order_v1_draft.md"]
  - id: lane7/l7-c20
    bags: 17
    families: ["st-cure-p05-20261006", "st-cure-p09-20261006"]
    flags: {"P0_tests_hole": 14}
    adjudication: "tests 域搬家批未落地快照（rule R-5）：重投旧 tests 树违反 tests 新家权威（docs/_working/tests_cure_campaign/99_delivery.md 8 域切法），重建归"
    qids_sample: ["-p05-20261006-0005", "-p05-20261006-0030", "-p05-20261006-0034", "-p05-20261006-0037", "-p05-20261006-0040"]
    missing_paths_sample: ["tests/data/alt_data/test_filing_nlp_engine.py", "tests/data/alt_data/test_geopolitical_risk_analyzer.py", "tests/data/alt_data/test_policy_expectation_analyzer.py", "tests/data/alt_data/test_policy_theme_mapper.py", "tests/data/alt_data/test_research_report_collector.py", "tests/data/alt_data/test_sentiment_engine.py", "tests/data/alt_data/test_social_sentiment_collector.py", "tests/data/alt_data/test_web_scraper_engine.py"]
  - id: lane4/l4-02
    bags: 16
    families: ["st-f15-frombag-20261005", "st-fr-resurrect", "st-menu-w3h-20260930", "st-qmine-20260925"]
    flags: {"lane_claim_overridden": 16, "P0_tests_hole": 3}
    adjudication: "module_translation_registry.yaml（68098 行热册）整档快照袋。39 袋 357 件：HEAD 全缺 45（路径今不在 HEAD 31、他径亦无同名件 6）、行级漂移 143。判据[al"
    qids_sample: ["mine-20260925-0042", "mine-20260925-0043", "mine-20260925-0044", "-w3h-20260930-0003", "-w3h-20260930-0011"]
    missing_paths_sample: ["scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py", "tests/scripts/test_audit_news_publish_time.py", "scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py", "tests/scripts/test_audit_news_publish_time.py", "scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py"]
  - id: lane6/l6-c04
    bags: 16
    families: ["st-cure-p12a-20261006", "st-sP-bottleneck-20261005"]
    flags: {"lane_claim_overridden": 16, "P0_tests_hole": 5}
    adjudication: "袋被后继袋顶替（reason 内 stale_by=q-… 点名）或基底重校验不适用：同波内容已由后继袋携带，本袋属结构性陈袋——归档零丢失，复活责任在 successor 袋所属车道。"
    qids_sample: ["neck-20261005-0013", "neck-20261005-0024", "neck-20261005-0027", "neck-20261005-0044", "neck-20261005-0076"]
    missing_paths_sample: ["tests/governance/test_derived_books_parity.py", "tests/governance/test_commit_door_provenance.py", "tests/governance/registry_projection/test_fidelity_gate.py", "tests/alt_data/test_emotion_index_replay.py", "docs/_working/emotion_line/index.md", "docs/_working/registry_incident_20260922/night_surgery_report.md", "docs/_working/registry_incident_20260922/overnight_decisions_20260923.md", "docs/_working/night_totalflow_20261001/99_delivery.md"]
  - id: lane7/l7-c17
    bags: 16
    families: ["st-cure-p05-20261006", "st-cure-p09-20261006", "st-f11-requeue-20261005", "st-sJ-doctorb2-20261004"]
    flags: {"P0_tests_hole": 13}
    adjudication: "regression_risk（rule R-4）：HEAD 已演进过快照，盲重投会删掉最多 max_only_head 条更新行——只能行级摘取（line-level cherry pick），禁 requeue --"
    qids_sample: ["orb2-20261004-0017", "ueue-20261005-0079", "-p05-20261006-0014", "-p05-20261006-0015", "-p05-20261006-0017"]
    missing_paths_sample: ["tests/backtest/test_n_trial_ledger.py", "tests/ex_core/test_qmt_trading_session.py", "tests/governance/commit_gates/test_arch_reference_gate.py", "tests/governance/scripts_governance/test_detect_git_dangerous_selfdoc.py", "tests/trade/trading/test_reference_data_manager.py", "tests/trade/trading/test_reference_data_manager.py", "tests/gov/governance/resilience/test_emergency_track_guardian.py", "tests/gov/governance/resilience/test_fail_mode_manager.py"]
  - id: lane7/l7-c18
    bags: 15
    families: ["st-ailayer-final-20260924", "st-cmd-20260924", "st-cure-p03-20261006", "st-f11-requeue-20261005", "st-final-build-20260926", "st-sD-liquidation-20261004"]
    flags: {"P0_tests_hole": 2}
    adjudication: "regression_risk（rule R-4）：HEAD 已演进过快照，盲重投会删掉最多 max_only_head 条更新行——只能行级摘取（line-level cherry pick），禁 requeue --"
    qids_sample: ["inal-20260924-0001", "-cmd-20260924-0040", "-cmd-20260924-0068", "-cmd-20260924-0079", "-cmd-20260924-0089"]
    missing_paths_sample: ["docs/_working/ai_layer_vision/P1_resume_files_v1.txt", "docs/_working/ai_layer_vision/P1_resume_files_v2.txt", "tests/ai_layer/redline/test_annual_review.py", "tests/ai_layer/redline/test_negative_list.py", "tests/ai_layer/redline/test_negative_list_gates.py", "tests/ai_layer/redline/test_session_env_guard.py", "tests/ai_layer/redline/test_sev_router.py", "docs/_working/decision_map_campaign_20260924/12_data_universe_census.md"]
  - id: lane1/l1-tests_03
    bags: 14
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 14, "P0_tests_hole": 14}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["hief-20261004-0015", "hief-20261004-0017", "hief-20261004-0035", "hief-20261004-0037", "hief-20261004-0053"]
    missing_paths_sample: ["tests/gov/governance/code_quality/test_code_analyzer_runner.py", "tests/gov/governance/code_quality/test_code_dedup_engine.py", "tests/gov/governance/code_quality/test_code_dedup_engine_red_team.py", "tests/gov/governance/code_quality/test_code_simulator.py", "tests/gov/governance/code_quality/test_detect_forward_reference.py", "tests/gov/governance/code_quality/test_evals_unit.py", "tests/gov/governance/code_quality/test_formal_verifier.py", "tests/gov/governance/code_quality/test_fsm_verifier.py"]
  - id: chief_revive_requeue/None
    bags: 14
    families: ["st-cure-p12b-20261006", "st-docs-e13-20261009", "st-mastertc-l0", "st-mastertc-l7", "st-mastertc-mini", "st-sK-orphanarch-20261004"]
    flags: {}
    adjudication: "replay adds lines only, destroys none (lines_only_in_head=0) — mechanical requeue --from-bag"
    qids_sample: ["n-w2-20261006-0002", "arch-20261004-0001", "lose-20261004-0005", "ave0-20260924-0045", "ave0-20260924-0046"]
    missing_paths_sample: ["config/data_masking_policy.yaml", "docs/_working/commitmap_cure/f11_orphan_test_verdict.md", "src/zephyr/data_security/wiring/__init__.py", "src/zephyr/data_security/wiring/audit_sink.py", "src/zephyr/data_security/wiring/data_exit_guard.py", "src/zephyr/data_security/wiring/lsg_masking_front.py", "tests/data/data_security/test_wiring_audit_sink.py", "tests/data/data_security/test_wiring_data_exit_guard.py"]
  - id: lane2/l2-c08
    bags: 14
    families: ["st-chainpile-20260922"]
    flags: {"lane_claim_overridden": 14}
    adjudication: "死袋主体=meta_question 基建四件套；HEAD 实测同一能力以改名姿势在树（meta_question_registry.py 含 register() API、snapshot.py/exam_ops.py"
    qids_sample: ["pile-20260922-0031", "pile-20260922-0055", "pile-20260922-0058", "pile-20260922-0059", "pile-20260922-0060"]
    missing_paths_sample: ["src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py"]
  - id: lane5/l5-c10
    bags: 14
    families: ["st-ffchief-20261001"]
    flags: {}
    adjudication: "14 袋挟两份热册整档快照（差 7649/2944 行），重投必蒸发他队条目→册面只能归档走 token 正道；但 F128 脱敏 wiring 三件+策略册+CNS-01 daily_job 从未入库而 token 在"
    qids_sample: ["hief-20261001-0003", "hief-20261001-0006", "hief-20261001-0034", "hief-20261001-0040", "hief-20261001-0076"]
    missing_paths_sample: ["src/zephyr/data_security/wiring/__init__.py", "src/zephyr/data_security/wiring/audit_sink.py", "src/zephyr/data_security/wiring/lsg_masking_front.py", "src/zephyr/data_security/wiring/data_exit_guard.py", "config/data_masking_policy.yaml", "tests/data_security/test_wiring_lsg_masking_front.py", "tests/data_security/test_wiring_data_exit_guard.py", "tests/data_security/test_wiring_audit_sink.py"]
  - id: lane7/l7-c13
    bags: 14
    families: ["st-circ-a2-20260930", "st-f11-requeue-20261005", "st-mastertc-l5b", "st-mastertc-l6", "st-sD-liquidation-20261004", "st-sJ-doctorb2-20261004"]
    flags: {"P0_tests_hole": 3}
    adjudication: "hot-registry 整档快照（rule R-3）：盲 requeue --from-bag 会蒸发他队已落地条目（capability 册 62k 行事故在案），禁重投；未落地 delta 走正道（PG token"
    qids_sample: ["ildA-20260923-0001", "c-a2-20260930-0008", "c-a2-20260930-0010", "tion-20261004-0015", "orb2-20261004-0003"]
    missing_paths_sample: ["src/zephyr/governance/registry_ledger/schema.py", "src/zephyr/governance/registry_ledger/identity.py", "tests/governance/test_registry_ledger.py", "tests/git/test_precommit_debt_ratchet.py", "tests/git/test_git_commit_gateway.py", "tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py", "tests/git/test_precommit_debt_ratchet.py", "tests/git/test_git_commit_gateway.py"]
  - id: lane6/l6-c05
    bags: 13
    families: ["st-sP-bottleneck-20261005"]
    flags: {"P0_tests_hole": 5}
    adjudication: "快照基底之后 dev 又推进并触及同路径=基底漂移死信；多数件已在树，剩未落余量需以新基底重做，盲重投必删现役。"
    qids_sample: ["neck-20261005-0006", "neck-20261005-0032", "neck-20261005-0033", "neck-20261005-0035", "neck-20261005-0041"]
    missing_paths_sample: ["tests/backtest/test_lane_c_formula_miner.py", "tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py", "tests/governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py", "tests/governance/test_next_ruling_id.py", "tests/ai_layer/scheduling/test_confirm_gate.py", "tests/ai_layer/redline/test_ai_secret_exposure.py", "scripts/governance/meta/rules_integrity_db.json", "scripts/signals/chart_condition_package.py"]
  - id: lane5/l5-c07
    bags: 12
    families: ["st-ffchief-20261001"]
    flags: {"lane_claim_overridden": 12, "P0_tests_hole": 12}
    adjudication: "16 袋 backtest 重投：reexam 本体在 HEAD，t0 族尺随搬家改名入库，sim_daily 仅 116 行差；真缺 2 把尺走行级摘取。战役已自出终报收口。"
    qids_sample: ["hief-20261001-0062", "hief-20261001-0077", "hief-20261001-0082", "hief-20261001-0090", "hief-20261001-0093"]
    missing_paths_sample: ["tests/infrastructure/test_resource_sampler.py", "tests/backtest/test_reexam_cpcv_harness.py", "tests/infrastructure/test_resource_sampler.py", "tests/backtest/test_reexam_cpcv_harness.py", "tests/backtest/test_reexam_cpcv_harness.py", "tests/backtest/test_reexam_cpcv_harness.py", "tests/backtest/test_reexam_cpcv_harness.py", "tests/backtest/test_reexam_cpcv_harness.py"]
  - id: lane7/l7-c19
    bags: 12
    families: ["st-cmd-20260924", "st-gpu-conv4-20260928", "st-mastertc-l6", "st-matrix-20261006", "st-poscap-fix-20261008", "st-sD-liquidation-20261004"]
    flags: {"P0_tests_hole": 2}
    adjudication: "regression_risk（rule R-4）：HEAD 已演进过快照，盲重投会删掉最多 max_only_head 条更新行——只能行级摘取（line-level cherry pick），禁 requeue --"
    qids_sample: ["-cmd-20260924-0145", "-cmd-20260924-0149", "eout-20260928-0029", "onv4-20260928-0001", "tion-20261004-0012"]
    missing_paths_sample: ["tests/signal_ashare/test_candidate_pool_snapshot.py", "tests/strategy_pipeline/test_pipeline_events.py", "tests/signal_ashare/test_candidate_pool_snapshot.py", "tests/strategy_pipeline/test_pipeline_events.py", "src/zephyr/governance/registry_projection/generator.py", "tests/governance/registry_projection/test_projection_model_renderer.py", "tests/governance/registry_projection/test_projection_generator.py"]
  - id: lane2/l2-c27
    bags: 11
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 3}
    adjudication: "缺面逐件复查：4 件已按新家落位（tests 八域归位），6 件同名同父目录零命中=真没落（lane_b_ledger_reconcile.py、test_f06_e5_synergy_wiring.py、test_la"
    qids_sample: ["-p01-20261006-0014", "-p01-20261006-0017", "-p01-20261006-0018", "-p01-20261006-0021", "-p01-20261006-0083"]
    missing_paths_sample: ["tests/backtest/test_reexam_cpcv_harness.py", "tests/backtest/test_lane_c_formula_miner.py", "tests/backtest/test_factory_intake_pipeline.py", "scripts/backtest/lane_b_ledger_reconcile.py", "tests/backtest/test_hypothesis_precheck.py", "tests/backtest/test_hypothesis_translator.py", "tests/backtest/test_lane_b_ledger_reconcile.py", "tests/backtest/test_f06_e5_synergy_wiring.py"]
  - id: lane3/l3-c01
    bags: 11
    families: ["st-closeout-basereq-20261006", "st-tclose-integ-20261004"]
    flags: {}
    adjudication: "门册在册、测试在树、实现文件不在 HEAD：STRATEGY-CARD-LIFECYCLE-MAP 属空转门（真缺口仍要）。袋同时带 panorama/map_family 面已被后续班推进，禁整档重投，只摘该门实现与其"
    qids_sample: ["nteg-20261004-0005", "nteg-20261004-0007", "nteg-20261004-0010", "nteg-20261004-0011", "nteg-20261004-0003"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py", "tests/governance/commit_gates/test_construction_workflow_map_gate.py", "tests/governance/commit_gates/test_strategy_card_lifecycle_map_gate.py", "docs/_working/fullcirc_closeout_chief/integ_workorder.md", "src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py", "tests/governance/commit_gates/test_construction_workflow_map_gate.py", "tests/governance/commit_gates/test_strategy_card_lifecycle_map_gate.py", "docs/_working/fullcirc_closeout_chief/integ_workorder.md"]
  - id: lane4/l4-08
    bags: 11
    families: ["st-cure-p05b-20261006", "st-f14-final-sweep-20261005", "st-f15-frombag-20261005"]
    flags: {"P0_tests_hole": 11}
    adjudication: "死于 GATE-PRECOMMIT-RUN：reason 自述 staged 面检出未解决冲突标记/gate-naming 违规。11 袋 2844 件：HEAD 全缺 1470（路径今不在 HEAD 1470、他径亦无"
    qids_sample: ["p05b-20261006-0001", "p05b-20261006-0005", "weep-20261005-0047", "mbag-20261005-0205", "p05b-20261006-0009"]
    missing_paths_sample: ["tests/ai/intelligence/model_routing/test_runtime_assembly.py", "tests/ai/intelligence/switch_engine/conftest.py", "tests/ai/intelligence/switch_engine/test_criteria.py", "tests/ai/intelligence/switch_engine/test_shadow_runner.py", "tests/ai/intelligence/switch_engine/test_switch_criteria_ssot.py", "tests/ai/intelligence/switch_engine/test_switch_engine.py", "tests/ai/intelligence/switch_engine/test_switch_registry.py", "tests/ai/intelligence/test_agent_memory_architecture.py"]
  - id: lane1/l1-tests_04
    bags: 10
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 10, "P0_tests_hole": 10}
    adjudication: "tests 搬家快照;99_delivery+收官 commit 证 8域切法已落 HEAD(差集清零),死袋=被后续落地取代"
    qids_sample: ["hief-20261004-0132", "hief-20261004-0133", "hief-20261004-0134", "hief-20261004-0142", "hief-20261004-0193"]
    missing_paths_sample: ["tests/ai/ai_layer/redline/test_annual_review.py", "tests/ai/ai_layer/redline/test_negative_list.py", "tests/ai/ai_layer/redline/test_session_env_guard.py", "tests/ai/intelligence/switch_engine/test_switch_engine.py", "tests/ai/ai_layer/redline/test_annual_review.py", "tests/ai/ai_layer/redline/test_negative_list.py", "tests/ai/ai_layer/redline/test_session_env_guard.py", "tests/ai/ai_layer/redline/test_sev_router.py"]
  - id: lane1/l1-tests_05
    bags: 9
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 9, "P0_tests_hole": 9}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0023", "hief-20261004-0024", "hief-20261004-0042", "hief-20261004-0043", "hief-20261004-0078"]
    missing_paths_sample: ["tests/research/ba/test_ba_events.py", "tests/research/ba/test_ba_handoff_manager.py", "tests/research/ba/test_ba_integration_test_runner.py", "tests/research/ba/test_ba_main.py", "tests/research/ba/test_ba_state_machine.py", "tests/research/backtest/test_anomaly_diagnoser.py", "tests/research/backtest/test_auto_mount.py", "tests/research/backtest/test_auto_mount_sle3.py"]
  - id: lane4/l4-09
    bags: 9
    families: ["st-cure-p05b-20261006", "st-f15-frombag-20261005"]
    flags: {"P0_tests_hole": 8}
    adjudication: "死于业务对齐闸（MAP-ALIGNMENT/TABLE-NAME-REGISTRY/ALGO-FLOW-LINK/TEST-SOURCE-CONSISTENCY 等）。9 袋 2200 件：HEAD 全缺 1427（路径"
    qids_sample: ["p05b-20261006-0003", "p05b-20261006-0004", "mbag-20261005-0082", "mbag-20261005-0206", "mbag-20261005-0207"]
    missing_paths_sample: ["tests/gov/governance/access_control/test_approval.py", "tests/gov/governance/access_control/test_cbac_matrix.py", "tests/gov/governance/access_control/test_credential_guard.py", "tests/gov/governance/access_control/test_rbac_bridge.py", "tests/gov/governance/access_control/test_rbac_bridge_bridge.py", "tests/gov/governance/access_control/test_secret_rotation_aware.py", "tests/gov/governance/adversarial/test_adversarial_tester.py", "tests/gov/governance/adversarial/test_anti_automation_bias.py"]
  - id: lane2/l2-c53
    bags: 8
    families: ["st-map9-f4-20261003"]
    flags: {"lane_claim_overridden": 8}
    adjudication: "重投链父子实测：本簇 1/8 袋的 requeue 后继已 done（qid q-20261004-st-map9-f4-20261003-0020）——同一批字节随后继袋落进 dev；簇内各袋 open_paths 签"
    qids_sample: ["9-f4-20261003-0011", "9-f4-20261003-0013", "9-f4-20261003-0014", "9-f4-20261003-0015", "9-f4-20261003-0017"]
    missing_paths_sample: ["tests/strategy_pipeline/test_intake.py", "tests/strategy_pipeline/test_intake.py", "tests/strategy_pipeline/test_intake.py", "tests/strategy_pipeline/test_intake.py", "tests/strategy_pipeline/test_intake.py", "tests/strategy_pipeline/test_intake.py", "tests/strategy_pipeline/test_intake.py", "tests/strategy_pipeline/test_intake.py"]
  - id: lane4/l4-10
    bags: 8
    families: ["st-c9-f4647", "st-f15-frombag-20261005", "st-tdm-mountgate-20261005"]
    flags: {}
    adjudication: "module_translation_registry.yaml（68098 行热册）整档快照袋。8 袋 74 件：HEAD 全缺 39（路径今不在 HEAD 39、他径亦无同名件 37）、行级漂移 27。判据[mate"
    qids_sample: ["9-st-c9-f4647-0002", "gate-20261005-0016", "gate-20261005-0032", "gate-20261005-0033", "gate-20261005-0034"]
    missing_paths_sample: ["src/zephyr/sell_decision/services/exit_execution_orchestrator.py", "tests/sell_decision/test_exit_execution_orchestrator.py", "docs/03_modules/MOD-SELL-020/blueprint.md", "docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tdm_mount_coverage_gate.yaml", "docs/03_modules/_domain_governance/algo_flow/audit/tdm_mount_coverage_reconciler.yaml", "tests/governance/commit_gates/test_tdm_mount_coverage_gate.py", "tests/governance/audit/test_tdm_mount_coverage_reconciler.py", "docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tdm_mount_coverage_gate.yaml"]
  - id: lane4/l4-11
    bags: 8
    families: ["st-f15-frombag-20261005"]
    flags: {"P0_tests_hole": 6}
    adjudication: "重投班 st-f15 死于重投机制本身（cascade_stale 基底重校验不适用 / 快照基底与 dev 冲突 / 三向合并失败）。8 袋 597 件：HEAD 全缺 317（路径今不在 HEAD 317、他径亦无同"
    qids_sample: ["mbag-20261005-0006", "mbag-20261005-0010", "mbag-20261005-0042", "mbag-20261005-0085", "mbag-20261005-0095"]
    missing_paths_sample: ["tests/governance/test_commit_queue_pool.py", "tests/governance/test_preflight_bare_sql_alignment.py", "schemas/categories/market/market_option_daily_stats.py", "scripts/backfill_option_daily_stats.py", "scripts/audit/pcr_e4_exam.py", "scripts/patrol/zcode_workspace_patrol.ps1", "tests/signal_ashare/sentiment/test_option_sentiment.py", "tests/governance/rule_bridge/test_commit_belt_daemon.py"]
  - id: lane7/l7-c23
    bags: 8
    families: ["st-cure-p05-20261006", "st-cure-p09-20261006"]
    flags: {"P0_tests_hole": 8}
    adjudication: "F-1 十二把回归尺清单件（rule R-7）：本专案只归档不重建，让给施工总队车道F 按尺规格重建；本簇只出源材料指路（袋内 blob_sha + 死信 qid），禁自行复活。｜clone_guard 尺（tests/"
    qids_sample: ["-p05-20261006-0016", "-p05-20261006-0020", "-p05-20261006-0021", "-p05-20261006-0036", "-p05-20261006-0038"]
    missing_paths_sample: ["tests/gov/clone_guard/fixtures/__init__.py", "tests/gov/clone_guard/fixtures/redup_sample.json", "tests/gov/clone_guard/fixtures/relate_corpus/different.py", "tests/gov/clone_guard/fixtures/relate_corpus/near_dup_a.py", "tests/gov/clone_guard/fixtures/relate_corpus/near_dup_b.py", "tests/gov/clone_guard/fixtures/relate_sample.json", "tests/gov/clone_guard/fixtures/vendetect_sample.txt", "tests/gov/clone_guard/test_aggregator.py"]
  - id: lane1/l1-tests_06
    bags: 7
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 7, "P0_tests_hole": 7}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0022", "hief-20261004-0040", "hief-20261004-0041", "hief-20261004-0076", "hief-20261004-0077"]
    missing_paths_sample: ["tests/meta/pipeline/test_pipeline_orchestrator_root.py", "tests/research/alpha_signal/__init__.py", "tests/research/alpha_signal/test_adversarial_alpha_signal.py", "tests/research/alpha_signal/test_l02_alpha_factor.py", "tests/research/ba/test_ba_canary_controller.py", "tests/research/ba/test_ba_chaos_injector.py", "tests/research/ba/test_ba_dashboard.py", "tests/research/ba/test_ba_data_lifecycle.py"]
  - id: lane3/l3-c05
    bags: 7
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 7, "P0_tests_hole": 6}
    adjudication: "tests 搬家袋：8 域归位已由 st-tests-chief-20261004 主批落地（129 目录中 116 归位），袋内旧路径在 HEAD 判 relocated/演进→②归档；gov 域残余见姊妹簇工单。"
    qids_sample: ["ereq-20261006-0134", "ereq-20261006-0228", "ereq-20261006-0239", "ereq-20261006-0238", "ereq-20261006-0260"]
    missing_paths_sample: ["tests/gov/gov_code_dedup/test_config_test_code_dedup_engine.py", "tests/gov/gov_code_dedup/test_degradation_edge.py", "tests/gov/gov_code_dedup/test_micro_clone.py", "tests/gov/gov_code_dedup/test_scanner_cross.py", "tests/gov/gov_code_dedup/test_scanner_raw.py", "tests/gov/gov_code_dedup/test_self_scan_integrity.py", "tests/gov/gov_drift/test_agent_stability_index.py", "tests/gov/gov_enforcement/create_guard_batch_replay.py"]
  - id: lane4/l4-05
    bags: 7
    families: ["st-commitmap-chief-20261003", "st-f15-frombag-20261005", "st-fig13-bone-20261004"]
    flags: {"lane_claim_overridden": 7, "P0_tests_hole": 1}
    adjudication: "死于业务对齐闸（MAP-ALIGNMENT/TABLE-NAME-REGISTRY/ALGO-FLOW-LINK/TEST-SOURCE-CONSISTENCY 等）。16 袋 134 件：HEAD 全缺 8（路径今不在"
    qids_sample: ["bone-20261004-0001", "bone-20261004-0004", "hief-20261003-0030", "bone-20261004-0005", "bone-20261004-0014"]
    missing_paths_sample: ["tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/rule_bridge/test_commit_belt_daemon.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "docs/_working/commitmap_cure/a2_ledger_census.md", "docs/_working/commitmap_cure/a2_gap_list.yaml"]
  - id: lane5/l5-c06
    bags: 7
    families: ["st-chief7-20260928"]
    flags: {"P0_tests_hole": 5}
    adjudication: "7 袋只搬 3 件 wave3 测试：dual_source_guard 已入新家，另两件全库零命中。被测本体已由收官手术落地=缺尺不缺能力，交 tests 施工队补位。"
    qids_sample: ["ief7-20260928-2081", "ief7-20260928-2128", "ief7-20260928-2129", "ief7-20260928-2130", "ief7-20260928-2147"]
    missing_paths_sample: ["tests/data/test_wave3_dual_source_guard.py", "tests/data/test_wave3_miniqmt_caliber.py", "tests/data/test_wave3_date_normalize.py", "tests/data/test_wave3_dual_source_guard.py", "tests/data/test_wave3_miniqmt_caliber.py", "tests/data/test_wave3_date_normalize.py", "tests/data/test_wave3_dual_source_guard.py", "tests/data/test_wave3_miniqmt_caliber.py"]
  - id: lane5/l5-c08
    bags: 7
    families: ["st-ffchief-20261001"]
    flags: {"lane_claim_overridden": 7}
    adjudication: "18 袋 src 代码重投：27 路径仅 1 件缺席且为旧家测试，其余皆已落后演化差。终报明载 13 车道施工落地——判被取代。"
    qids_sample: ["hief-20261001-0020", "hief-20261001-0033", "hief-20261001-0041", "hief-20261001-0049", "hief-20261001-0065"]
    missing_paths_sample: ["tests/ai_layer/comparator/test_compare_events.py", "tests/ai_layer/comparator/test_compare_events.py", "tests/data/test_wave3_dual_source_guard.py", "tests/ai_layer/comparator/test_compare_events.py", "tests/backtest/test_chart_cell_materializer.py", "tests/backtest/test_chart_cell_materializer.py", "tests/backtest/test_chart_cell_materializer.py"]
  - id: lane1/l1-st-map01
    bags: 6
    families: ["st-map9-chief-20261008", "st-mapbuild-20260924"]
    flags: {"lane_claim_overridden": 6, "P0_tests_hole": 2}
    adjudication: "st-map9-chief-20261008 施工快照:主件已在 HEAD 存在且演进(或改名入新路径),盲投毁新行=不可重投;内容被后续战役取代,归档②"
    qids_sample: ["hief-20261008-0001", "hief-20261008-0003", "hief-20261008-0007", "hief-20261008-0008", "uild-20260924-0007"]
    missing_paths_sample: ["tests/research/strategy_pipeline/test_registry_writer_verify.py", "tests/research/strategy_pipeline/test_registry_writer_verify.py", "tests/research/strategy_pipeline/test_registry_writer_verify.py", "tests/research/strategy_pipeline/test_registry_writer_verify.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py"]
  - id: lane2/l2-c18
    bags: 6
    families: ["st-cure-p01-20261006"]
    flags: {}
    adjudication: "缺面逐件复查：1 件已按新家落位（tests 八域归位），5 件同名同父目录零命中=真没落（lost_file_recovery_channels.md、offrepo_secret_inventory.md、test_"
    qids_sample: ["-p01-20261006-0019", "-p01-20261006-0023", "-p01-20261006-0126", "-p01-20261006-0131", "-p01-20261006-0134"]
    missing_paths_sample: ["tests/governance/test_derived_books_parity.py", "tests/governance/test_commit_door_provenance.py", "tests/governance/registry_projection/test_fidelity_gate.py", "docs/_working/wave13_chief3/offrepo_secret_inventory.md", "docs/_working/wave13_chief3/lost_file_recovery_channels.md", "tests/trading/test_decision_map.py"]
  - id: lane3/l3-c02
    bags: 6
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 6, "P0_tests_hole": 2}
    adjudication: "本批治理脚本主件（d8_doc_sync 反向孤儿对账器、meta/enforcement_surface_reconcile、wave1a/cross_session_view、data_supply 尺件）逐件 gi"
    qids_sample: ["ereq-20261006-0011", "ereq-20261006-0066", "ereq-20261006-0146", "ereq-20261006-0162", "ereq-20261006-0113"]
    missing_paths_sample: ["tests/scripts/test_generate_resource_profile_registry.py", "tests/backtest/test_f06_e4_wfa_exam.py", "tests/scripts/test_generate_resource_profile_registry.py", "tests/backtest/test_f06_e4_wfa_exam.py", "tests/scripts/test_generate_resource_profile_registry.py", "tests/backtest/test_f06_e4_wfa_exam.py", "tests/scripts/test_generate_resource_profile_registry.py", "tests/backtest/test_f06_e4_wfa_exam.py"]
  - id: lane3/l3-c03
    bags: 6
    families: ["st-deadletter-cure-20261003"]
    flags: {"lane_claim_overridden": 6, "P0_tests_hole": 6}
    adjudication: "本专案工具链自身的历史袋：dead_letter_doctor.py 已由 2b28c6fbf1 落地、又被 st-govfix-g2-20261007 的 895b535843 继续改进→②归档；唯其自家测试件从未进 "
    qids_sample: ["cure-20261003-0004", "cure-20261003-0005", "cure-20261003-0006", "cure-20261003-0007", "cure-20261003-0008"]
    missing_paths_sample: ["tests/governance/test_dead_letter_doctor.py", "tests/governance/test_dead_letter_doctor.py", "tests/governance/test_dead_letter_doctor.py", "tests/governance/test_dead_letter_doctor.py", "tests/governance/test_dead_letter_doctor.py", "tests/governance/test_dead_letter_doctor.py"]
  - id: lane3/l3-c06
    bags: 6
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "热册整档禁盲重投，且册外仍有件确实不在 HEAD（真缺口）→①复活走行级摘取+正道补登，开工单。"
    qids_sample: ["ereq-20261006-0130", "ereq-20261006-0131", "ereq-20261006-0132", "ereq-20261006-0224", "ereq-20261006-0225"]
    missing_paths_sample: ["docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tdm_mount_coverage_gate.yaml", "docs/03_modules/_domain_governance/algo_flow/audit/tdm_mount_coverage_reconciler.yaml", "tests/governance/commit_gates/test_tdm_mount_coverage_gate.py", "tests/governance/audit/test_tdm_mount_coverage_reconciler.py", "docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tdm_mount_coverage_gate.yaml", "docs/03_modules/_domain_governance/algo_flow/audit/tdm_mount_coverage_reconciler.yaml", "tests/governance/commit_gates/test_tdm_mount_coverage_gate.py", "tests/governance/audit/test_tdm_mount_coverage_reconciler.py"]
  - id: lane5/l5-c02
    bags: 6
    families: ["st-chief7-20260928"]
    flags: {"lane_claim_overridden": 6, "P0_tests_hole": 6}
    adjudication: "30 袋同 data_supply 供给件重投。本体经总包 L07批A/收官手术两度落地并做过克隆合并，HEAD 已更新；残余 7 把尺是真缺，但只能摘取不可重投。"
    qids_sample: ["ief7-20260928-0029", "ief7-20260928-0603", "ief7-20260928-1331", "ief7-20260928-1927", "ief7-20260928-2047"]
    missing_paths_sample: ["tests/data/test_wave3_date_normalize.py", "tests/data/test_wave3_dual_source_guard.py", "tests/data/test_wave3_miniqmt_caliber.py", "tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/data_supply/__init__.py", "tests/governance/data_supply/test_false_green_crosscheck.py", "tests/governance/data_supply/test_no_cache_and_cli_rc.py"]
  - id: lane5/l5-c23
    bags: 6
    families: ["st-mastertc-l1", "st-mastertc-recover"]
    flags: {}
    adjudication: "6 袋 17 路径 8 已落、残余仅 76 行，但 check_registry_field_legality 门本体全库零命中而其尺已入库（有尺无体）；报文引 Owner #488 批建，裁定册未见专条→授权面待核。真"
    qids_sample: ["t-mastertc-l1-0004", "t-mastertc-l1-0006", "tertc-recover-0002", "tertc-recover-0003", "tertc-recover-0004"]
    missing_paths_sample: ["tests/library/test_library_hygiene.py", "tests/library/test_library_hygiene.py", "scripts/governance/check_registry_field_legality.py", "tests/governance/test_check_registry_field_legality.py", "docs/_working/total_command_closeout/final_review_chartlib/ext_05_minute_k_persistence_design.md"]
  - id: lane6/l6-c06
    bags: 6
    families: ["st-cure-p12a-20261006", "st-sP-bottleneck-20261005"]
    flags: {"lane_claim_overridden": 6}
    adjudication: "袋被后继袋顶替（reason 内 stale_by=q-… 点名）或基底重校验不适用：同波内容已由后继袋携带，本袋属结构性陈袋——归档零丢失，复活责任在 successor 袋所属车道。"
    qids_sample: ["neck-20261005-0007", "neck-20261005-0016", "neck-20261005-0017", "neck-20261005-0022", "neck-20261005-0108"]
    missing_paths_sample: ["tests/backtest/test_factory_intake_pipeline.py", "docs/_working/wave13_chief3/inbox/merger_identity/01_case_file.md", "scripts/backtest/lane_b_ledger_reconcile.py", "tests/backtest/test_hypothesis_precheck.py", "tests/backtest/test_hypothesis_translator.py", "tests/backtest/test_lane_b_ledger_reconcile.py", "tests/zephyr/data/quality/test_sla_breach_predictor.py", "tests/governance/generators/test_map_coverage_attribution.py"]
  - id: lane6/l6-c07
    bags: 6
    families: ["st-cure-p12a-20261006", "st-cure-p12b-20261006"]
    flags: {"P0_tests_hole": 3}
    adjudication: "热册袋带整档快照：重投会蒸发他队条目（capability 册 62k 行损坏事故在案，终报 §3.1），禁重投。实测 51.6% 在 HEAD，余量走条目级册正道。"
    qids_sample: ["p12a-20261006-0001", "p12a-20261006-0015", "p12a-20261006-0016", "p12b-20261006-0015", "p12b-20261006-0030"]
    missing_paths_sample: ["config/pf_alloc.yaml", "tests/pf_alloc/test_allocation_team_wiring.py", "tests/pf_alloc/test_allocation_chain.py", "docs/_working/pf_alloc_wiring/delivery_report_pf_alloc_wiring.md", "tests/governance/test_scan_scope_convergence_equivalence.py", "tests/governance/test_consumption_census_redproof.py", "tests/governance/test_library_reconcilers_red_blue.py", "docs/_working/three_piece_infra/integration_fix/CASE.md"]
  - id: lane6/l6-c08
    bags: 6
    families: ["st-cure-p12a-20261006"]
    flags: {"P0_tests_hole": 1}
    adjudication: "袋搬的正是 dev 已删/已搬走的旧路径：基底有、dev 已删→拒陈旧快照整文件写回。tests/ 件也被称注册表族，因合并仲裁面 Owner 终裁已扩至全路径。"
    qids_sample: ["p12a-20261006-0010", "p12a-20261006-0020", "p12a-20261006-0024", "p12a-20261006-0025", "p12a-20261006-0026"]
    missing_paths_sample: ["tests/governance/test_probe_failure_must_report_red.py", "tests/governance/commit_gates/test_ch_final_gate_no_final_reads.py", "tests/zephyr/data/test_ch_parts_monitor.py", "scripts/governance/backfill_registry_consumption.py", "tests/governance/test_backfill_registry_consumption.py", "scripts/backtest/eval_tech_indicator_ic.py", "tests/backtest/test_eval_tech_indicator_ic.py", "tests/backtest/test_chart_condition_package.py"]
  - id: lane6/l6-c09
    bags: 6
    families: ["st-cure-p12b-20261006"]
    flags: {"P0_tests_hole": 6}
    adjudication: "tests/ 搬家批 6 袋：新家权威=99_delivery.md:12（8 域切法 7/8 域已落，116/129 目录归位）+§七:61（gov 批7=唯一未完成环）。陈旧整树快照禁重投；实测本簇 75.9% 路径"
    qids_sample: ["p12b-20261006-0041", "p12b-20261006-0042", "p12b-20261006-0043", "p12b-20261006-0044", "p12b-20261006-0045"]
    missing_paths_sample: ["tests/ai/ai_layer/redline/test_annual_review.py", "tests/ai/ai_layer/redline/test_negative_list.py", "tests/ai/ai_layer/redline/test_session_env_guard.py", "tests/ai/ai_layer/redline/test_annual_review.py", "tests/ai/ai_layer/redline/test_negative_list.py", "tests/ai/ai_layer/redline/test_session_env_guard.py", "tests/ai/ai_layer/redline/test_sev_router.py", "tests/ai/ai_layer/redline/test_annual_review.py"]
  - id: lane1/l1-tests_07
    bags: 5
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 5, "P0_tests_hole": 5}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0038", "hief-20261004-0074", "hief-20261004-0089", "hief-20261004-0110", "hief-20261004-0127"]
    missing_paths_sample: ["tests/infra/infra_ops/test_config_effect_checker.py", "tests/infra/infra_ops/test_loki_log_pipeline.py", "tests/infra/infra_ops/test_runtime_topology_visualizer.py", "tests/infra/infra_ops/test_storage_cost_calculator.py", "tests/infra/infra_ops/test_wal_checkpoint_monitor.py", "tests/infra/infra_runtime/test_cold_plane_isolation.py", "tests/infra/infra_runtime/test_database_layer.py", "tests/infra/infra_runtime/test_ha_sla_framework.py"]
  - id: lane3/l3-c08
    bags: 5
    families: ["st-audit-fix-20260924", "st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "热册整档禁盲重投，且册外仍有件确实不在 HEAD（真缺口）→①复活走行级摘取+正道补登，开工单。"
    qids_sample: ["-fix-20260924-0034", "-fix-20260924-0038", "-fix-20260924-0039", "ereq-20261006-0083", "ereq-20261006-0178"]
    missing_paths_sample: ["tests/governance/test_derived_books_parity.py", "tests/governance/test_commit_door_provenance.py", "tests/governance/test_commit_door_provenance.py", "tests/governance/test_derived_books_parity.py", "tests/governance/test_commit_door_provenance.py", "tests/governance/test_derived_books_parity.py", "tests/governance/test_derived_books_parity.py", "tests/governance/test_commit_door_provenance.py"]
  - id: lane3/l3-c09
    bags: 5
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "热册整档禁盲重投，且册外仍有件确实不在 HEAD（真缺口）→①复活走行级摘取+正道补登，开工单。"
    qids_sample: ["ereq-20261006-0265", "ereq-20261006-0267", "ereq-20261006-0089", "ereq-20261006-0184", "ereq-20261006-0264"]
    missing_paths_sample: ["docs/03_modules/_domain_gov_enforcement/algo_flow/construction_workflow_map_gate.yaml", "docs/03_modules/_domain_gov_enforcement/algo_flow/construction_workflow_map_gate.yaml", "tests/governance/registry_projection/test_fidelity_gate.py", "tests/governance/registry_projection/test_fidelity_gate.py"]
  - id: lane3/l3-c10
    bags: 5
    families: ["st-closeout-basereq-20261006", "st-nightfix-20260923"]
    flags: {"lane_claim_overridden": 5, "P0_tests_hole": 3}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["tfix-20260923-0006", "tfix-20260923-0007", "tfix-20260923-0008", "ereq-20261006-0124", "ereq-20261006-0218"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py", "tests/governance/commit_gates/test_registry_mass_deletion_gate.py", "tests/governance/commit_gates/test_registry_batch_edit_and_mass_deletion_gate.py", "src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py", "tests/governance/commit_gates/test_registry_mass_deletion_gate.py", "tests/governance/commit_gates/test_registry_batch_edit_and_mass_deletion_gate.py", "src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py", "tests/governance/commit_gates/test_registry_mass_deletion_gate.py"]
  - id: lane3/l3-c11
    bags: 5
    families: ["st-closeout-basereq-20261006"]
    flags: {"P0_tests_hole": 3}
    adjudication: "tests/gov 面确有缺口：HEAD 实测 tests/gov/governance/commit_gates 仅 4 件，袋内 import_direction/import_integrity/long_para"
    qids_sample: ["ereq-20261006-0135", "ereq-20261006-0229", "ereq-20261006-0243", "ereq-20261006-0133", "ereq-20261006-0227"]
    missing_paths_sample: ["tests/gov/governance/commit_gates/test_import_direction_gate.py", "tests/gov/governance/commit_gates/test_import_integrity_gate.py", "tests/gov/governance/commit_gates/test_long_param_list_gate.py", "tests/gov/governance/commit_gates/test_m21_phase3_6_gates.py", "tests/gov/governance/commit_gates/test_manual_only_permanent_gate_noqa.py", "tests/gov/governance/commit_gates/test_mcp_version_field_gate.py", "tests/gov/governance/commit_gates/test_module_id_consistency_gate.py", "tests/gov/governance/commit_gates/test_msg_exposure_gate.py"]
  - id: lane3/l3-c12
    bags: 5
    families: ["st-wm1-wave0-20260924"]
    flags: {"P0_tests_hole": 4}
    adjudication: "registry_ledger 子系统（identity.py/schema.py/台账测试）三件全不在 HEAD，而案卷 docs/_working/registry_migration/LEDGER_wave0.md"
    qids_sample: ["ave0-20260924-0004", "ave0-20260924-0005", "ave0-20260924-0018", "ave0-20260924-0027", "ave0-20260924-0031"]
    missing_paths_sample: ["src/zephyr/governance/registry_projection/generator.py", "tests/governance/registry_projection/test_projection_model_renderer.py", "tests/governance/registry_projection/test_projection_generator.py", "src/zephyr/governance/registry_ledger/identity.py", "src/zephyr/governance/registry_ledger/schema.py", "tests/governance/test_registry_ledger.py", "src/zephyr/governance/registry_ledger/identity.py", "src/zephyr/governance/registry_ledger/schema.py"]
  - id: lane4/l4-13
    bags: 5
    families: ["st-cure-p05b-20261006", "st-f14-final-sweep-20261005", "st-f15-frombag-20261005"]
    flags: {"P0_tests_hole": 5}
    adjudication: "F-1 回归尺（tests/gov clone_guard·escalation 等）源材料袋，禁重建，只指路给车道F。5 袋 1210 件：HEAD 全缺 1139（路径今不在 HEAD 1139、他径亦无同名件 11"
    qids_sample: ["p05b-20261006-0002", "weep-20261005-0052", "mbag-20261005-0208", "p05b-20261006-0012", "p05b-20261006-0023"]
    missing_paths_sample: ["tests/gov/clone_guard/fixtures/relate_corpus/near_dup_b.py", "tests/gov/clone_guard/fixtures/relate_sample.json", "tests/gov/clone_guard/fixtures/vendetect_sample.txt", "tests/gov/clone_guard/test_aggregator.py", "tests/gov/clone_guard/test_ast_grep_adapter.py", "tests/gov/clone_guard/test_config.py", "tests/gov/clone_guard/test_echo_guard_adapter.py", "tests/gov/clone_guard/test_mcp_server.py"]
  - id: lane5/l5-c19
    bags: 5
    families: ["st-joinchk-20261004"]
    flags: {"lane_claim_overridden": 5}
    adjudication: "5 袋 7 路径零真缺：唯一缺席尺已按新家 tests/gov/ 入库，归因分析册也搬家；残余 616 行含 545 行热册快照——判被取代。"
    qids_sample: ["nchk-20261004-0013", "nchk-20261004-0014", "nchk-20261004-0015", "nchk-20261004-0016", "nchk-20261004-0021"]
    missing_paths_sample: ["tests/governance/generators/test_map_coverage_attribution.py", "tests/governance/generators/test_map_coverage_attribution.py", "tests/governance/generators/test_map_coverage_attribution.py", "tests/governance/generators/test_map_coverage_attribution.py", "tests/governance/generators/test_map_coverage_attribution.py"]
  - id: lane6/l6-c10
    bags: 5
    families: ["st-cure-p10-20261006", "st-gpu-conv3-20260928", "st-sP-bottleneck-20261005"]
    flags: {"P0_tests_hole": 3}
    adjudication: "文档/蓝图头不合规（BLUEPRINT module_id 格式，裁定#214 Phase 0 防蔓延）＝内容级欠账：不改头重投必撞同一门（上一轮终报 12 败主项即此类）。"
    qids_sample: ["onv3-20260928-0001", "neck-20261005-0065", "neck-20261005-0067", "neck-20261005-0072", "-p10-20261006-0031"]
    missing_paths_sample: ["tests/backtest/test_gpu_core_parity.py", "tests/gov/architecture/__init__.py", "tests/gov/architecture/test_contract_consistency.py", "tests/gov/architecture/test_cross_module_contracts.py", "tests/gov/architecture/test_layer_isolation.py", "tests/gov/architecture/test_money_and_docs.py", "tests/gov/architecture/test_single_order_exit.py", "tests/gov/audit/audit_core/test_audit_adversarial.py"]
  - id: lane1/l1-tests_08
    bags: 4
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 4}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0044", "hief-20261004-0080", "hief-20261004-0095", "hief-20261004-0114"]
    missing_paths_sample: ["tests/trade/trading/test_reference_data_manager.py", "tests/trade/trading/test_reference_data_manager.py", "tests/trade/trading/test_reference_data_manager.py", "tests/trade/trading/test_reference_data_manager.py"]
  - id: lane2/l2-c19
    bags: 4
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 1}
    adjudication: "缺面逐件复查：5 件已按新家落位（tests 八域归位），15 件同名同父目录零命中=真没落（00_campaign_brief.md、01_skeleton_environments.md、02_gap_ledger."
    qids_sample: ["-p01-20261006-0030", "-p01-20261006-0092", "-p01-20261006-0143", "-p01-20261006-0152"]
    missing_paths_sample: ["docs/_working/night_totalflow_20261001/99_delivery.md", "docs/_working/t0_matrix/FINAL_REPORT_t0_matrix_reexam.md", "docs/_working/t0_matrix/six_phase_history_v1.meta.yaml", "docs/_working/t0_matrix/t0_ceiling_daily.csv", "docs/_working/t0_matrix/t0_ceiling_result.yaml", "docs/_working/t0_matrix/t0_conditional_e4_v3_result.yaml", "tests/audit/test_t0_ceiling_capacity_exam.py", "tests/audit/test_t0_conditional_e4_v3_exam.py"]
  - id: lane2/l2-c20
    bags: 4
    families: ["st-cure-p01-20261006"]
    flags: {}
    adjudication: "缺面逐件复查：1 件已按新家落位（tests 八域归位），3 件同名同父目录零命中=真没落（audit_news_publish_time.py、audit_technical_indicator_columns.py、"
    qids_sample: ["-p01-20261006-0041", "-p01-20261006-0042", "-p01-20261006-0123", "-p01-20261006-0138"]
    missing_paths_sample: ["scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py", "tests/scripts/test_audit_news_publish_time.py", "scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py", "tests/scripts/test_audit_news_publish_time.py", "scripts/data/kline_sector_intraday_from_constituents.py", "scripts/data/kline_sector_intraday_from_constituents.py"]
  - id: lane2/l2-c28
    bags: 4
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 4}
    adjudication: "缺面逐件复查：1 件已按新家落位（tests 八域归位），13 件同名同父目录零命中=真没落（test_ai_comment_veracity.py、test_ai_construction_detectors.py、t"
    qids_sample: ["-p01-20261006-0050", "-p01-20261006-0053", "-p01-20261006-0132", "-p01-20261006-0146"]
    missing_paths_sample: ["tests/ai/intelligence/model_routing/test_runtime_assembly.py", "tests/ai/intelligence/switch_engine/conftest.py", "tests/ai/intelligence/switch_engine/test_criteria.py", "tests/ai/intelligence/switch_engine/test_shadow_runner.py", "tests/ai/intelligence/switch_engine/test_switch_criteria_ssot.py", "tests/ai/intelligence/switch_engine/test_switch_engine.py", "tests/ai/intelligence/switch_engine/test_switch_registry.py", "tests/ai/intelligence/test_agent_memory_architecture.py"]
  - id: lane2/l2-c59
    bags: 4
    families: ["st-menu-t1b1-20260930"]
    flags: {"lane_claim_overridden": 4}
    adjudication: "缺面逐件按“同名+同父目录”复查 HEAD：全部命中新家（tests 八域归位/模块改名落位），零件真失踪（1 件全命中）⇒ 内容被别处取代，②归档；按旧路径复活=造双真源，禁。"
    qids_sample: ["t1b1-20260930-0001", "t1b1-20260930-0003", "t1b1-20260930-0006", "t1b1-20260930-0009"]
    missing_paths_sample: ["tests/zephyr/data/quality/test_sla_breach_predictor.py", "tests/zephyr/data/quality/test_sla_breach_predictor.py", "tests/zephyr/data/quality/test_sla_breach_predictor.py", "tests/zephyr/data/quality/test_sla_breach_predictor.py"]
  - id: lane2/l2-c60
    bags: 4
    families: ["st-pipeline-final-20260924"]
    flags: {"lane_claim_overridden": 4}
    adjudication: "死袋主体=meta_question 基建四件套；HEAD 实测同一能力以改名姿势在树（meta_question_registry.py 含 register() API、snapshot.py/exam_ops.py"
    qids_sample: ["inal-20260924-0003", "inal-20260924-0007", "inal-20260924-0008", "inal-20260924-0012"]
    missing_paths_sample: ["src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py"]
  - id: lane3/l3-c14
    bags: 4
    families: ["st-audit-fix-20260924"]
    flags: {"P0_tests_hole": 1}
    adjudication: "审计修复案的 d11_compliance/gate_replay_selfproof.py 与其测试不在 HEAD（门自证面缺口），同批热册/案卷件已在树→行级摘取重落，勿碰册面。"
    qids_sample: ["-fix-20260924-0007", "-fix-20260924-0017", "-fix-20260924-0036", "-fix-20260924-0037"]
    missing_paths_sample: ["tests/governance/test_commit_queue_base_head.py", "scripts/governance/d11_compliance/gate_replay_selfproof.py", "tests/governance/test_gate_replay_selfproof.py", "docs/_working/chain_fullflow_20260925/chain_fullflow_skeleton.md", "docs/_working/chain_fullflow_20260925/lane_gate_liveness.md", "docs/_working/chain_fullflow_20260925/lane_gate_autofix.md", "docs/_working/chain_fullflow_20260925/lane_gate_business_flowthrough.md", "docs/_working/chain_fullflow_20260925/lane_gate_door_provenance.md"]
  - id: lane3/l3-c15
    bags: 4
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "热册整档禁盲重投，且册外仍有件确实不在 HEAD（真缺口）→①复活走行级摘取+正道补登，开工单。"
    qids_sample: ["ereq-20261006-0128", "ereq-20261006-0222", "ereq-20261006-0077", "ereq-20261006-0172"]
    missing_paths_sample: ["docs/03_modules/_domain_governance/algo_flow/reuse_scan.yaml", "docs/03_modules/_domain_governance/algo_flow/reuse_scan.yaml", "src/zephyr/governance/reuse_scan.py", "src/zephyr/governance/reuse_scan.py"]
  - id: lane3/l3-c17
    bags: 4
    families: ["st-closeout-basereq-20261006", "st-metaq-20260923"]
    flags: {}
    adjudication: "meta_question 只落了 __init__/exam_loop（HEAD 实测），registry.py/vocab_loader.py/apply_meta_question_ddl.py 全缺=题录闭环断在"
    qids_sample: ["etaq-20260923-0002", "etaq-20260923-0003", "ereq-20261006-0062", "ereq-20261006-0159"]
    missing_paths_sample: ["src/zephyr/governance/meta_question/registry.py", "src/zephyr/governance/meta_question/vocab_loader.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "src/zephyr/governance/meta_question/vocab_loader.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py"]
  - id: lane3/l3-c18
    bags: 4
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "scripts/data 审计件不在 HEAD；HEAD 另有同域后继件 audit_technical_indicator_coverage.py，是否已被其取代需二判，故只开指路工单不判废。"
    qids_sample: ["ereq-20261006-0126", "ereq-20261006-0127", "ereq-20261006-0220", "ereq-20261006-0221"]
    missing_paths_sample: ["scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py", "tests/scripts/test_audit_news_publish_time.py", "scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py", "tests/scripts/test_audit_news_publish_time.py", "scripts/data/audit_news_publish_time.py", "scripts/data/audit_technical_indicator_columns.py"]
  - id: lane3/l3-c19
    bags: 4
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "registry_projection/generator.py 实测不在 HEAD（投影生成器缺体），同批主册件在树且已被他队推进→①复活走行级摘取，册面经生成器 render 回写，禁重投。"
    qids_sample: ["ereq-20261006-0063", "ereq-20261006-0118", "ereq-20261006-0160", "ereq-20261006-0212"]
    missing_paths_sample: ["src/zephyr/governance/registry_projection/generator.py", "src/zephyr/governance/registry_ledger/identity.py", "src/zephyr/governance/registry_ledger/schema.py", "src/zephyr/governance/registry_projection/generator.py", "src/zephyr/governance/registry_ledger/identity.py", "src/zephyr/governance/registry_ledger/schema.py"]
  - id: lane3/l3-c20
    bags: 4
    families: ["st-closeout-basereq-20261006"]
    flags: {"P0_tests_hole": 2}
    adjudication: "回测脚本面 lane_b_ledger_reconcile.py 与 hypothesis/cpcv 复验测试不在 HEAD（同批 harness 主件在树）→行级摘取补件，禁整批重投。"
    qids_sample: ["ereq-20261006-0085", "ereq-20261006-0180", "ereq-20261006-0075", "ereq-20261006-0170"]
    missing_paths_sample: ["scripts/backtest/lane_b_ledger_reconcile.py", "tests/backtest/test_hypothesis_precheck.py", "tests/backtest/test_hypothesis_translator.py", "tests/backtest/test_lane_b_ledger_reconcile.py", "scripts/backtest/lane_b_ledger_reconcile.py", "tests/backtest/test_hypothesis_precheck.py", "tests/backtest/test_hypothesis_translator.py", "tests/backtest/test_lane_b_ledger_reconcile.py"]
  - id: lane3/l3-c21
    bags: 4
    families: ["st-closeout-basereq-20261006", "st-e2e-20260924"]
    flags: {}
    adjudication: "E2E 集成案的 cost_qualified_list_reexam yaml 不在 HEAD，exam_cost_gate 代码与其余案卷在树→残口一处，行级补。"
    qids_sample: ["-e2e-20260924-0008", "-e2e-20260924-0009", "ereq-20261006-0052", "ereq-20261006-0151"]
    missing_paths_sample: ["docs/_working/e2e_integration/cost_qualified_list_reexam_20260923.yaml", "docs/_working/e2e_integration/cost_qualified_list_reexam_20260923.yaml", "docs/_working/e2e_integration/cost_qualified_list_reexam_20260923.yaml", "docs/_working/e2e_integration/cost_qualified_list_reexam_20260923.yaml"]
  - id: lane3/l3-c22
    bags: 4
    families: ["st-metaq-20260923"]
    flags: {}
    adjudication: "题录治理链的 DDL/registry 件缺位（apply_meta_question_ddl.py 实测 NOT-IN-HEAD），死因 COMPLEXITY/翻译门属施工欠账，非判死。"
    qids_sample: ["etaq-20260923-0004", "etaq-20260923-0011", "etaq-20260923-0016", "etaq-20260923-0020"]
    missing_paths_sample: ["src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py"]
  - id: lane4/l4-03
    bags: 4
    families: ["st-f14-final-sweep-20261005", "st-f15-frombag-20261005", "st-mastertc-l5c", "st-tailwork5-20260928"]
    flags: {"lane_claim_overridden": 4, "P0_tests_hole": 2}
    adjudication: "纯文书缺票被拦（CREATE-GUARD/TRANSLATION-COVERAGE/DOC-HEADER-SUITE），无毁 HEAD 行。22 袋 640 件：HEAD 全缺 48（路径今不在 HEAD 27、他径亦无"
    qids_sample: ["ork5-20260928-0001", "weep-20261005-0057", "mbag-20261005-0216", "-mastertc-l5c-0001"]
    missing_paths_sample: ["tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py"]
  - id: lane4/l4-06
    bags: 4
    families: ["st-chief-mount-20261003", "st-ff-chfail-20260926", "st-regfix-lane0b-20260923", "st-storageswap-20260930"]
    flags: {"lane_claim_overridden": 4, "P0_tests_hole": 2}
    adjudication: "capability_canonical_file_registry.yaml（64506 行热册）整档快照袋。14 袋 68 件：HEAD 全缺 7（路径今不在 HEAD 7、他径亦无同名件 2）、行级漂移 37。判据"
    qids_sample: ["ne0b-20260923-0015", "fail-20260926-0002", "swap-20260930-0013", "ount-20261003-0002"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py", "src/zephyr/gov_enforcement/commit_gates/registry_family/__init__.py", "tests/governance/test_probe_failure_must_report_red.py", "tests/governance/commit_gates/test_ch_final_gate_no_final_reads.py", "tests/zephyr/data/test_ch_parts_monitor.py", "docs/_working/night_totalflow_20261001/99_delivery.md", "tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py"]
  - id: lane4/l4-07
    bags: 4
    families: ["st-f15-frombag-20261005", "st-tdm-mountgate-20261005"]
    flags: {"P0_tests_hole": 3}
    adjudication: "纯文书缺票被拦（CREATE-GUARD/TRANSLATION-COVERAGE/DOC-HEADER-SUITE），无毁 HEAD 行。11 袋 869 件：HEAD 全缺 830（路径今不在 HEAD 830、他径"
    qids_sample: ["gate-20261005-0015", "mbag-20261005-0210", "mbag-20261005-0211", "mbag-20261005-0212"]
    missing_paths_sample: ["scripts/governance/_shared/mount_obligation.py", "config/tdm_mount_exemption_registry.yaml", "scripts/generate_mount_obligation_manifest.py", "tests/governance/test_generate_mount_obligation_manifest.py", "tests/gov/clone_guard/fixtures/__init__.py", "tests/gov/clone_guard/fixtures/redup_sample.json", "tests/gov/clone_guard/fixtures/relate_corpus/different.py", "tests/gov/clone_guard/fixtures/relate_corpus/near_dup_a.py"]
  - id: lane4/l4-14
    bags: 4
    families: ["chiefzc-surgeon-20260928", "st-f15-frombag-20261005"]
    flags: {"lane_claim_overridden": 4, "P0_tests_hole": 1}
    adjudication: "docs/_working 战役台账册快照袋（非注册表本体）。4 袋 159 件：HEAD 全缺 36（路径今不在 HEAD 35、他径亦无同名件 31）、行级漂移 21。判据[registered-since×4]→②"
    qids_sample: ["geon-20260928-0002", "geon-20260928-0004", "mbag-20261005-0029", "mbag-20261005-0182"]
    missing_paths_sample: ["scripts/governance/d11_compliance/gate_replay_selfproof.py", "tests/governance/test_gate_replay_selfproof.py", "docs/_working/chain_fullflow_20260925/chain_fullflow_skeleton.md", "docs/_working/chain_fullflow_20260925/lane_gate_liveness.md", "docs/_working/chain_fullflow_20260925/lane_gate_autofix.md", "docs/_working/chain_fullflow_20260925/lane_gate_business_flowthrough.md", "docs/_working/chain_fullflow_20260925/lane_gate_door_provenance.md", "docs/_working/chain_fullflow_20260925/lane_gate_derived_books.md"]
  - id: lane4/l4-15
    bags: 4
    families: ["st-f15-frombag-20261005", "st-nightsweep-sw14-20260929", "st-nightsweep2-nf2-20260930"]
    flags: {"P0_tests_hole": 2}
    adjudication: "capability_canonical_file_registry.yaml（64506 行热册）整档快照袋。4 袋 21 件：HEAD 全缺 10（路径今不在 HEAD 10、他径亦无同名件 10）、行级漂移 11。"
    qids_sample: ["sw14-20260929-0004", "-nf2-20260930-0006", "mbag-20261005-0003", "mbag-20261005-0004"]
    missing_paths_sample: ["docs/_working/night_sweep/cns_closeout_ledger.md", "docs/_working/night_sweep/e6_vm_assessment.md", "config/pf_alloc.yaml", "tests/pf_alloc/test_allocation_team_wiring.py", "tests/pf_alloc/test_allocation_chain.py", "docs/_working/pf_alloc_wiring/delivery_report_pf_alloc_wiring.md", "config/pf_alloc.yaml", "tests/pf_alloc/test_allocation_team_wiring.py"]
  - id: lane4/l4-16
    bags: 4
    families: ["st-chief-mount-20261003", "st-f15-frombag-20261005", "st-fig13-bone-20261004", "st-mastertc-l0"]
    flags: {"lane_claim_overridden": 4}
    adjudication: "死于 GATE-PRECOMMIT-RUN：reason 自述 staged 面检出未解决冲突标记/gate-naming 违规。4 袋 119 件：HEAD 全缺 5（路径今不在 HEAD 3、他径亦无同名件 0）、行"
    qids_sample: ["bone-20261004-0002", "ount-20261003-0008", "mbag-20261005-0218", "t-mastertc-l0-0002"]
    missing_paths_sample: ["tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "docs/_working/commitmap_cure/a2_ledger_census.md", "docs/_working/commitmap_cure/a2_gap_list.yaml", "tests/trade/trading/test_reference_data_manager.py", "tests/ex_core/test_fill_jsonl_single_writer.py"]
  - id: lane4/l4-17
    bags: 4
    families: ["st-f14-final-sweep-20261005", "st-f15-frombag-20261005"]
    flags: {"P0_tests_hole": 4}
    adjudication: "docs/_working 战役台账册快照袋（非注册表本体）。4 袋 1165 件：HEAD 全缺 827（路径今不在 HEAD 825、他径亦无同名件 799）、行级漂移 50。判据[materially-missin"
    qids_sample: ["weep-20261005-0054", "weep-20261005-0099", "mbag-20261005-0159", "mbag-20261005-0213"]
    missing_paths_sample: ["tests/gov/governance/test_scheduled_task_reconcile.py", "tests/gov/governance/test_sel_unreachable_5_linkage.py", "tests/gov/governance/test_session_closeout_reconciler.py", "tests/gov/governance/test_session_reincarnation_guard.py", "tests/gov/governance/test_session_startup_health_check.py", "tests/gov/governance/test_session_takeover_ledger.py", "tests/gov/governance/test_shared_yaml_utils_reexport.py", "tests/gov/governance/test_split_coordination.py"]
  - id: lane5/l5-c04
    bags: 4
    families: ["st-chief7-20260928"]
    flags: {"lane_claim_overridden": 4, "P0_tests_hole": 4}
    adjudication: "8 袋跨波次治理脚本重投，HEAD 均有同名本体；10 件缺席路径全是旧家测试，已按 tests 8 域新家入库=搬家非丢失。"
    qids_sample: ["ief7-20260928-0861", "ief7-20260928-0932", "ief7-20260928-1416", "ief7-20260928-2086"]
    missing_paths_sample: ["tests/data/test_wave3_date_normalize.py", "tests/data/test_wave3_dual_source_guard.py", "tests/data/test_wave3_miniqmt_caliber.py", "tests/governance/data_supply/__init__.py", "tests/governance/data_supply/test_false_green_crosscheck.py", "tests/governance/data_supply/test_no_cache_and_cli_rc.py", "tests/governance/data_supply/test_supply_conservation.py", "tests/governance/test_enforcement_surface_reconcile_canary.py"]
  - id: lane6/l6-c12
    bags: 4
    families: ["st-cure-p12b-20261006", "st-sP-bottleneck-20261005"]
    flags: {}
    adjudication: "热册袋带整档快照：重投会蒸发他队条目（capability 册 62k 行损坏事故在案，终报 §3.1），禁重投。实测 40.5% 在 HEAD，余量走条目级册正道。"
    qids_sample: ["neck-20261005-0057", "neck-20261005-0133", "neck-20261005-0143", "p12b-20261006-0031"]
    missing_paths_sample: ["scripts/governance/d11_compliance/gate_replay_selfproof.py", "tests/governance/test_gate_replay_selfproof.py", "docs/_working/chain_fullflow_20260925/chain_fullflow_skeleton.md", "docs/_working/chain_fullflow_20260925/lane_gate_liveness.md", "docs/_working/chain_fullflow_20260925/lane_gate_autofix.md", "docs/_working/chain_fullflow_20260925/lane_gate_business_flowthrough.md", "docs/_working/chain_fullflow_20260925/lane_gate_door_provenance.md", "docs/_working/chain_fullflow_20260925/lane_gate_derived_books.md"]
  - id: lane6/l6-c13
    bags: 4
    families: ["st-sP-bottleneck-20261005"]
    flags: {}
    adjudication: "热册袋带整档快照：重投会蒸发他队条目（capability 册 62k 行损坏事故在案，终报 §3.1），禁重投。实测 80.0% 在 HEAD，余量走条目级册正道。"
    qids_sample: ["neck-20261005-0140", "neck-20261005-0148", "neck-20261005-0149", "neck-20261005-0150"]
    missing_paths_sample: ["docs/_working/commit_speedup_campaign/00_HANDOFF.md", "docs/_working/commit_speedup_campaign/00_MASTER_PLAN.md", "docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tdm_mount_coverage_gate.yaml", "docs/03_modules/_domain_governance/algo_flow/audit/tdm_mount_coverage_reconciler.yaml", "tests/governance/commit_gates/test_tdm_mount_coverage_gate.py", "tests/governance/audit/test_tdm_mount_coverage_reconciler.py", "docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/t/tdm_mount_coverage_gate.yaml", "docs/03_modules/_domain_governance/algo_flow/audit/tdm_mount_coverage_reconciler.yaml"]
  - id: lane6/l6-c14
    bags: 4
    families: ["st-cure-p10-20261006"]
    flags: {"P0_tests_hole": 2}
    adjudication: "tests/ 搬家批 4 袋：新家权威=99_delivery.md:12（8 域切法 7/8 域已落，116/129 目录归位）+§七:61（gov 批7=唯一未完成环）。陈旧整树快照禁重投；实测本簇 52.1% 路径"
    qids_sample: ["-p10-20261006-0009", "-p10-20261006-0013", "-p10-20261006-0015", "-p10-20261006-0026"]
    missing_paths_sample: ["tests/ai/test_ai_audit_logger.py", "tests/ai/test_ai_capability_guard.py", "tests/ai/test_ai_code_standards.py", "tests/data/alt_data/test_research_report_collector.py", "tests/data/alt_data/test_sentiment_engine.py", "tests/data/alt_data/test_social_sentiment_collector.py", "tests/data/alt_data/test_web_scraper_engine.py", "tests/data/backup/test_restore_drill.py"]
  - id: lane7/l7-c14
    bags: 4
    families: ["st-cure-p05-20261006", "st-f11-requeue-20261005", "st-mastertc-l7"]
    flags: {"P0_tests_hole": 3}
    adjudication: "hot-registry 整档快照（rule R-3）：盲 requeue --from-bag 会蒸发他队已落地条目（capability 册 62k 行事故在案），禁重投；未落地 delta 走正道（PG token"
    qids_sample: ["ueue-20261005-0075", "-p05-20261006-0004", "-p05-20261006-0029", "t-mastertc-l7-0004"]
    missing_paths_sample: ["tests/gov/governance/code_quality/test_code_analyzer_runner.py", "tests/gov/governance/code_quality/test_code_dedup_engine.py", "tests/gov/governance/code_quality/test_code_dedup_engine_red_team.py", "tests/gov/governance/code_quality/test_code_simulator.py", "tests/gov/governance/code_quality/test_detect_forward_reference.py", "tests/gov/governance/code_quality/test_evals_unit.py", "tests/gov/governance/code_quality/test_formal_verifier.py", "tests/gov/governance/code_quality/test_fsm_verifier.py"]
  - id: lane1/l1-st-c9-01
    bags: 3
    families: ["st-c9-f43"]
    flags: {"lane_claim_overridden": 3}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["929-st-c9-f43-0002", "930-st-c9-f43-0001", "930-st-c9-f43-0002"]
    missing_paths_sample: ["src/zephyr/strategy_pipeline/t0_condition_pack.py", "tests/strategy_pipeline/test_t0_condition_pack.py", "src/zephyr/strategy_pipeline/t0_condition_pack.py", "tests/strategy_pipeline/test_t0_condition_pack.py", "src/zephyr/strategy_pipeline/t0_condition_pack.py", "tests/strategy_pipeline/test_t0_condition_pack.py"]
  - id: lane1/l1-tests_09
    bags: 3
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 3, "P0_tests_hole": 3}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0050", "hief-20261004-0068", "hief-20261004-0083"]
    missing_paths_sample: ["tests/data/alt_data/test_filing_nlp_engine.py", "tests/data/alt_data/test_geopolitical_risk_analyzer.py", "tests/data/alt_data/test_policy_expectation_analyzer.py", "tests/data/alt_data/test_policy_theme_mapper.py", "tests/data/alt_data/test_research_report_collector.py", "tests/data/alt_data/test_sentiment_engine.py", "tests/data/alt_data/test_social_sentiment_collector.py", "tests/data/alt_data/test_web_scraper_engine.py"]
  - id: lane1/l1-tests_10
    bags: 3
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 3, "P0_tests_hole": 3}
    adjudication: "F-1 十二把回归尺件,让给施工总队车道F重建(本专案只归档不重建);指路=路径+死袋 qid(blobs/ 快照据此定位)"
    qids_sample: ["hief-20261004-0051", "hief-20261004-0084", "hief-20261004-0122"]
    missing_paths_sample: ["tests/gov/audit/test_tone_adapter.py", "tests/gov/audit/test_tone_adapter_v2.py", "tests/gov/audit/test_traffic_replay_validator.py", "tests/gov/audit/test_trend_analyzer.py", "tests/gov/audit/test_verification_engine.py", "tests/gov/autonomy_core/test_agentic_drift_guard.py", "tests/gov/autonomy_core/test_killswitch_response_levels.py", "tests/gov/boundary/__init__.py"]
  - id: lane1/l1-st-map03
    bags: 3
    families: ["st-map9-chief-20261008", "st-mapbuild-20260924"]
    flags: {"lane_claim_overridden": 3}
    adjudication: "六图战役(mapbuild)施工快照:三图生成器/config 图在 HEAD 演进;map 校验门被后继战役改名迁入 map_family/ 目录落地,袋快照=被取代,归档②"
    qids_sample: ["uild-20260924-0009", "uild-20260924-0014", "hief-20261008-0005"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py", "docs/_working/factory_flow_20261007/00_施工方案与环节骨架.md", "docs/_working/factory_flow_20261007/E0_算力调度.md"]
  - id: lane2/l2-c57
    bags: 3
    families: ["st-matrix-final-20260930"]
    flags: {"lane_claim_overridden": 3}
    adjudication: "死袋投的是 commit_gates/ 平铺独立 gate 文件；HEAD 实测三门以 map_family/ 聚合台子台在树且 gate_registry 三条 status: active（algo_flow 外源首"
    qids_sample: ["inal-20260930-0021", "inal-20260930-0024", "inal-20260930-0026"]
    missing_paths_sample: ["tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py"]
  - id: lane2/l2-c72
    bags: 3
    families: ["st-tdm-chief-20261004"]
    flags: {"lane_claim_overridden": 3}
    adjudication: "缺面逐件按“同名+同父目录”复查 HEAD：全部命中新家（tests 八域归位/模块改名落位），零件真失踪（1 件全命中）⇒ 内容被别处取代，②归档；按旧路径复活=造双真源，禁。"
    qids_sample: ["hief-20261004-0012", "hief-20261004-0014", "hief-20261004-0015"]
    missing_paths_sample: ["tests/trading/test_decision_map.py", "tests/trading/test_decision_map.py", "tests/trading/test_decision_map.py"]
  - id: lane2/l2-c74
    bags: 3
    families: ["st-workingchief-20261006"]
    flags: {}
    adjudication: "docs/_working/chief_fullchain_20261006/ 在 HEAD 零命中=整战役区文档真没落；死因 R5-DIGIT-SUFFIX 目录命名门禁⇒ 仍要但必须先改目录名去数字后缀，属施工动作，"
    qids_sample: ["hief-20261006-0006", "hief-20261006-0007", "hief-20261006-0010"]
    missing_paths_sample: ["docs/_working/chief_fullchain_20261006/00_campaign_brief.md", "docs/_working/chief_fullchain_20261006/01_skeleton_environments.md", "docs/_working/chief_fullchain_20261006/02_gap_ledger.md", "docs/_working/chief_fullchain_20261006/05_folder_verdicts.md", "docs/_working/chief_fullchain_20261006/06_root_sweep_ledger.md", "docs/_working/chief_fullchain_20261006/90_chief_runlog.md", "docs/_working/chief_fullchain_20261006/99_final_delivery.md", "docs/_working/chief_fullchain_20261006/env_mining/env_01_collect.md"]
  - id: lane3/l3-c25
    bags: 3
    families: ["st-closeout-basereq-20261006", "st-nightfix-20260923"]
    flags: {"lane_claim_overridden": 3}
    adjudication: "registry_incident_20260922 夜诊案卷不在 HEAD，死因是 R5 数字后缀目录禁令（路径本身非法）+战役早已收官：判③留痕；若 Owner 仍要留存，按 TRAE-028 改名后行级重落。"
    qids_sample: ["tfix-20260923-0009", "ereq-20261006-0101", "ereq-20261006-0196"]
    missing_paths_sample: ["docs/_working/registry_incident_20260922/night_surgery_report.md", "docs/_working/registry_incident_20260922/overnight_decisions_20260923.md", "docs/_working/registry_incident_20260922/night_surgery_report.md", "docs/_working/registry_incident_20260922/overnight_decisions_20260923.md", "docs/_working/registry_incident_20260922/night_surgery_report.md", "docs/_working/registry_incident_20260922/overnight_decisions_20260923.md"]
  - id: lane3/l3-c26
    bags: 3
    families: ["st-closeout-basereq-20261006", "st-tclose-integ-20261004"]
    flags: {}
    adjudication: "与 c01 同族（缺体门 strategy_card_lifecycle_map_gate + 挂图测试旧路径），门册在册而实现不在树=真缺口仍要；并入 c01 工单排队。"
    qids_sample: ["nteg-20261004-0012", "ereq-20261006-0116", "ereq-20261006-0210"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py", "tests/governance/commit_gates/test_construction_workflow_map_gate.py", "tests/governance/commit_gates/test_strategy_card_lifecycle_map_gate.py", "docs/_working/fullcirc_closeout_chief/integ_workorder.md", "src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py", "tests/governance/commit_gates/test_construction_workflow_map_gate.py", "tests/governance/commit_gates/test_strategy_card_lifecycle_map_gate.py", "docs/_working/fullcirc_closeout_chief/integ_workorder.md"]
  - id: lane3/l3-c27
    bags: 3
    families: ["st-bcure-20261008"]
    flags: {}
    adjudication: "bcure（2026-10-08 新袋）数据链主件已在 HEAD，唯 tests/legacy_zephyr 交易日历内建测试不在树；残口小，随 tests 新家一批处理。"
    qids_sample: ["cure-20261008-0002", "cure-20261008-0003", "cure-20261008-0004"]
    missing_paths_sample: ["tests/legacy_zephyr/data/test_ashare_trade_calendar_internal.py", "tests/legacy_zephyr/data/test_ashare_trade_calendar_internal.py"]
  - id: lane4/l4-19
    bags: 3
    families: ["st-cure-p05b-20261006", "st-f14-final-sweep-20261005", "st-f15-frombag-20261005"]
    flags: {"P0_tests_hole": 2}
    adjudication: "tests 搬家批（新家=tests_cure_campaign 8 域切法），未落地面归施工队排队。3 袋 568 件：HEAD 全缺 554（路径今不在 HEAD 554、他径亦无同名件 536）、行级漂移 0。判据"
    qids_sample: ["weep-20261005-0058", "mbag-20261005-0204", "p05b-20261006-0013"]
    missing_paths_sample: ["tests/data/alt_data/test_filing_nlp_engine.py", "tests/data/alt_data/test_geopolitical_risk_analyzer.py", "tests/data/alt_data/test_policy_expectation_analyzer.py", "tests/data/alt_data/test_policy_theme_mapper.py", "tests/data/alt_data/test_research_report_collector.py", "tests/data/alt_data/test_sentiment_engine.py", "tests/data/alt_data/test_social_sentiment_collector.py", "tests/data/alt_data/test_web_scraper_engine.py"]
  - id: lane4/l4-20
    bags: 3
    families: ["st-f14-final-sweep-20261005"]
    flags: {"P0_tests_hole": 3}
    adjudication: "死于存活闸（裁定#459）：属主会话 heartbeat=exited，自动重投被拒。3 袋 824 件：HEAD 全缺 576（路径今不在 HEAD 576、他径亦无同名件 565）、行级漂移 59。判据[materi"
    qids_sample: ["weep-20261005-0086", "weep-20261005-0120", "weep-20261005-0121"]
    missing_paths_sample: ["tests/ai/intelligence/model_routing/test_runtime_assembly.py", "tests/ai/intelligence/switch_engine/conftest.py", "tests/ai/intelligence/switch_engine/test_criteria.py", "tests/ai/intelligence/switch_engine/test_shadow_runner.py", "tests/ai/intelligence/switch_engine/test_switch_criteria_ssot.py", "tests/ai/intelligence/switch_engine/test_switch_engine.py", "tests/ai/intelligence/switch_engine/test_switch_registry.py", "tests/ai/intelligence/test_agent_memory_architecture.py"]
  - id: lane5/l5-c05
    bags: 3
    families: ["st-chief7-20260928"]
    flags: {"lane_claim_overridden": 3, "P0_tests_hole": 3}
    adjudication: "4 袋代码件：validator/generator 本体在 HEAD，n_trial_ledger 尺改名入库；其余旧家测试缺席属搬家批，判被取代。"
    qids_sample: ["ief7-20260928-0901", "ief7-20260928-1800", "ief7-20260928-2076"]
    missing_paths_sample: ["tests/backtest/test_n_trial_ledger.py", "tests/ex_core/test_qmt_trading_session.py", "tests/governance/commit_gates/test_arch_reference_gate.py", "tests/governance/scripts_governance/test_detect_git_dangerous_selfdoc.py", "tests/data/test_wave3_date_normalize.py", "tests/data/test_wave3_dual_source_guard.py", "tests/data/test_wave3_miniqmt_caliber.py", "tests/data/test_wave3_date_normalize.py"]
  - id: lane5/l5-c11
    bags: 3
    families: ["st-ffchief-20261001"]
    flags: {}
    adjudication: "3 袋残余 11926 行里热册占 10593（禁重投），真缺仅 f06 协同尺与健康探针尺 2 件——出工单，置信度低待复核。"
    qids_sample: ["hief-20261001-0019", "hief-20261001-0048", "hief-20261001-0132"]
    missing_paths_sample: ["tests/backtest/test_f06_e5_synergy_wiring.py", "tests/trading/test_health_monitor_probe.py"]
  - id: lane5/l5-c20
    bags: 3
    families: ["st-align-dirty-20260924"]
    flags: {"lane_claim_overridden": 3}
    adjudication: "3 袋仅 3 路径：LEDGER.md 改名落为 align_dirty_ledger.md、R2 交付件直接入库，剩 2921 行是 capability 册整档差（禁重投）。内容全在=归档。"
    qids_sample: ["irty-20260924-0041", "irty-20260924-0045", "irty-20260924-0048"]
    missing_paths_sample: ["docs/_working/align_dirty/LEDGER.md", "docs/_working/align_dirty/LEDGER.md", "docs/_working/align_dirty/LEDGER.md"]
  - id: lane5/l5-c24
    bags: 3
    families: ["st-chief3b-20260926"]
    flags: {}
    adjudication: "3 袋 14 路径全未落（已落 0、缺席 5）：仓外明文登记、回收通道、merger 案卷三件 HEAD 与 worktree 双零命中。报文自称 Owner 令但裁定册查无→授权面 pending_owner，内容面按"
    qids_sample: ["ef3b-20260926-0007", "ef3b-20260926-0008", "ef3b-20260926-0010"]
    missing_paths_sample: ["docs/_working/wave13_chief3/inbox/merger_identity/01_case_file.md", "docs/_working/wave13_chief3/offrepo_secret_inventory.md", "docs/_working/wave13_chief3/lost_file_recovery_channels.md", "tests/ai_layer/scheduling/test_confirm_gate.py", "tests/ai_layer/redline/test_ai_secret_exposure.py", "docs/_working/wave13_chief3/offrepo_secret_inventory.md", "docs/_working/wave13_chief3/lost_file_recovery_channels.md"]
  - id: lane5/l5-c27
    bags: 3
    families: ["st-nightsweep-sw10-20260929", "st-nightsweep-sw17-20260929"]
    flags: {}
    adjudication: "3 袋 13 路径仅 1 已落、缺席 7：回补消耗登记器与 tech_indicator IC 评价尺两件本体+两把尺全库零命中，两篇夜战册未落且后继报告不承接一波——真缺口须摘取重建。"
    qids_sample: ["sw10-20260929-0001", "sw10-20260929-0002", "sw17-20260929-0001"]
    missing_paths_sample: ["scripts/governance/backfill_registry_consumption.py", "tests/governance/test_backfill_registry_consumption.py", "scripts/backtest/eval_tech_indicator_ic.py", "tests/backtest/test_eval_tech_indicator_ic.py", "tests/backtest/test_chart_condition_package.py", "docs/_working/night_sweep/SW10_cns_chart_wiring.md", "scripts/governance/backfill_registry_consumption.py", "tests/governance/test_backfill_registry_consumption.py"]
  - id: lane5/l5-c28
    bags: 3
    families: ["st-sI-identity-20261004"]
    flags: {"lane_claim_overridden": 3}
    adjudication: "3 袋 16 路径 8 已落：治本本体 registry_ledger/baseline.py 在 HEAD，残余 9110 行里热册占 8213（禁重投），唯一真缺是保真门尺——能力已被他道完成=归档+尺件工单。"
    qids_sample: ["tity-20261004-0001", "tity-20261004-0002", "tity-20261004-0003"]
    missing_paths_sample: ["tests/governance/registry_projection/test_fidelity_gate.py", "tests/governance/registry_projection/test_fidelity_gate.py", "tests/governance/registry_projection/test_fidelity_gate.py"]
  - id: lane6/l6-c18
    bags: 3
    families: ["st-cure-p10-20261006"]
    flags: {"P0_tests_hole": 3}
    adjudication: "热册袋带整档快照：重投会蒸发他队条目（capability 册 62k 行损坏事故在案，终报 §3.1），禁重投。实测 0.0% 在 HEAD，余量走条目级册正道。"
    qids_sample: ["-p10-20261006-0011", "-p10-20261006-0014", "-p10-20261006-0024"]
    missing_paths_sample: ["tests/gov/guard/test_guard_interaction_topology_mapper.py", "tests/gov/guard/test_guard_layers_root.py", "tests/gov/guard/test_guard_oscillation_detector.py", "tests/gov/guard/test_guard_self_consistency_auditor.py", "tests/gov/risk/core/test_agent_risk_monitor.py", "tests/gov/risk/core/test_ai_agent_monitor.py", "tests/gov/risk/core/test_alert_generator.py", "tests/gov/risk/core/test_copula_garch_joint.py"]
  - id: lane1/l1-st-gov01
    bags: 2
    families: ["st-govfix-g3-20261007"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["x-g3-20261007-0001", "x-g3-20261007-0002"]
    missing_paths_sample: ["scripts/matrix_rescued_tmp/rowvec/bench_scaling.py", "scripts/matrix_rescued_tmp/rowvec/panelized_indicators.py", "scripts/matrix_rescued_tmp/rowvec/parity_check.py", "scripts/matrix_rescued_tmp/rowvec/bench_scaling.py", "scripts/matrix_rescued_tmp/rowvec/panelized_indicators.py", "scripts/matrix_rescued_tmp/rowvec/parity_check.py"]
  - id: lane1/l1-st-map02
    bags: 2
    families: ["st-mapbuild-20260924"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "六图战役(mapbuild)施工快照:三图生成器/config 图在 HEAD 演进;map 校验门被后继战役改名迁入 map_family/ 目录落地,袋快照=被取代,归档②"
    qids_sample: ["uild-20260924-0008", "uild-20260924-0013"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py"]
  - id: lane1/l1-st-map04
    bags: 2
    families: ["st-mapbuild-20260924"]
    flags: {"lane_claim_overridden": 2, "P0_tests_hole": 2}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["uild-20260924-0018", "uild-20260924-0022"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py", "tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py"]
  - id: lane1/l1-st-map05
    bags: 2
    families: ["st-mapbuild-20260924"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "六图战役(mapbuild)施工快照:三图生成器/config 图在 HEAD 演进;map 校验门被后继战役改名迁入 map_family/ 目录落地,袋快照=被取代,归档②"
    qids_sample: ["uild-20260924-0030", "uild-20260924-0037"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/construction_workflow_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/strategy_card_lifecycle_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/construction_workflow_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py"]
  - id: lane1/l1-st-map06
    bags: 2
    families: ["st-mapbuild-20260924"]
    flags: {"lane_claim_overridden": 2, "P0_tests_hole": 2}
    adjudication: "六图战役(mapbuild)施工快照:三图生成器/config 图在 HEAD 演进;map 校验门被后继战役改名迁入 map_family/ 目录落地,袋快照=被取代,归档②"
    qids_sample: ["uild-20260924-0031", "uild-20260924-0038"]
    missing_paths_sample: ["tests/governance/commit_gates/test_construction_workflow_map_gate.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_strategy_card_lifecycle_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py", "tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py", "tests/governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py", "tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py"]
  - id: lane1/l1-st-cir01
    bags: 2
    families: ["st-circ-a8-20260930"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["c-a8-20260930-0001", "c-a8-20260930-0003"]
    missing_paths_sample: ["tests/backtest/test_lane_c_formula_miner.py", "tests/backtest/test_lane_c_formula_miner.py"]
  - id: lane1/l1-tests_11
    bags: 2
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 2, "P0_tests_hole": 2}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0001", "hief-20261004-0030"]
    missing_paths_sample: ["docs/_working/tests_cure_campaign/01_structure_census.md", "docs/_working/tests_cure_campaign/02_reference_census.md", "docs/_working/tests_cure_campaign/03_garbage_census.md", "tests/data/alt_data/test_filing_nlp_engine.py", "tests/data/alt_data/test_geopolitical_risk_analyzer.py", "tests/data/alt_data/test_policy_expectation_analyzer.py", "tests/data/alt_data/test_policy_theme_mapper.py", "tests/data/alt_data/test_research_report_collector.py"]
  - id: lane1/l1-tests_12
    bags: 2
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 2, "P0_tests_hole": 2}
    adjudication: "tests 搬家快照;99_delivery+收官 commit 证 8域切法已落 HEAD(差集清零),死袋=被后续落地取代"
    qids_sample: ["hief-20261004-0104", "hief-20261004-0121"]
    missing_paths_sample: ["tests/data/alt_data/test_filing_nlp_engine.py", "tests/data/alt_data/test_geopolitical_risk_analyzer.py", "tests/data/alt_data/test_policy_expectation_analyzer.py", "tests/data/alt_data/test_policy_theme_mapper.py", "tests/data/alt_data/test_research_report_collector.py", "tests/data/alt_data/test_sentiment_engine.py", "tests/data/alt_data/test_social_sentiment_collector.py", "tests/data/alt_data/test_web_scraper_engine.py"]
  - id: lane1/l1-st-tai01
    bags: 2
    families: ["st-tailwork2-20260928", "st-tailwork9-20260928"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "st-tailwork2-20260928 施工快照:主件已在 HEAD 存在且演进(或改名入新路径),盲投毁新行=不可重投;内容被后续战役取代,归档②"
    qids_sample: ["ork2-20260928-0001", "ork9-20260928-0001"]
    missing_paths_sample: ["tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py"]
  - id: lane2/l2-c06
    bags: 2
    families: ["st-c7-f56-20260927"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺面逐件按“同名+同父目录”复查 HEAD：全部命中新家（tests 八域归位/模块改名落位），零件真失踪（2 件全命中）⇒ 内容被别处取代，②归档；按旧路径复活=造双真源，禁。"
    qids_sample: ["-f56-20260927-0001", "-f56-20260927-0004"]
    missing_paths_sample: ["tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/ex_core/adapters/test_qmt_file_bridge_broker.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py"]
  - id: lane2/l2-c21
    bags: 2
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 2}
    adjudication: "整档快照型热册袋（capability/gate/translation/registry 册）——重投=蒸发他队条目（62k 行并发写损坏事故在案）且 HEAD 已演进（max_only_head 最高 59 行）⇒ "
    qids_sample: ["-p01-20261006-0049", "-p01-20261006-0051"]
    missing_paths_sample: ["tests/gov/governance/commit_gates/test_import_direction_gate.py", "tests/gov/governance/commit_gates/test_import_integrity_gate.py", "tests/gov/governance/commit_gates/test_long_param_list_gate.py", "tests/gov/governance/commit_gates/test_m21_phase3_6_gates.py", "tests/gov/governance/commit_gates/test_manual_only_permanent_gate_noqa.py", "tests/gov/governance/commit_gates/test_mcp_version_field_gate.py", "tests/gov/governance/commit_gates/test_module_id_consistency_gate.py", "tests/gov/governance/commit_gates/test_msg_exposure_gate.py"]
  - id: lane2/l2-c22
    bags: 2
    families: ["st-cure-p01-20261006"]
    flags: {}
    adjudication: "整档快照型热册袋（capability/gate/translation/registry 册）——重投=蒸发他队条目（62k 行并发写损坏事故在案）且 HEAD 已演进（max_only_head 最高 5010 行）"
    qids_sample: ["-p01-20261006-0067", "-p01-20261006-0122"]
    missing_paths_sample: ["scripts/governance/d11_compliance/gate_replay_selfproof.py", "tests/governance/test_gate_replay_selfproof.py", "docs/_working/chain_fullflow_campaign/chain_fullflow_skeleton.md", "docs/_working/chain_fullflow_campaign/lane_gate_liveness.md", "docs/_working/chain_fullflow_campaign/lane_gate_autofix.md", "docs/_working/chain_fullflow_campaign/lane_gate_business_flowthrough.md", "docs/_working/chain_fullflow_campaign/lane_gate_door_provenance.md", "docs/_working/chain_fullflow_campaign/lane_gate_derived_books.md"]
  - id: lane2/l2-c29
    bags: 2
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 2}
    adjudication: "缺件确在 HEAD 零命中（真失踪 12 件），但同簇混跨战役欠账、死因以基底冲突为主（final_closeout §5③：重投后仍漂=人工清偿域）⇒ 不复活整袋，按行级摘取建单；本簇未逐件补实证据，标 needs_s"
    qids_sample: ["-p01-20261006-0054", "-p01-20261006-0133"]
    missing_paths_sample: ["tests/infra/infra_ops/test_config_effect_checker.py", "tests/infra/infra_ops/test_loki_log_pipeline.py", "tests/infra/infra_ops/test_runtime_topology_visualizer.py", "tests/infra/infra_ops/test_storage_cost_calculator.py", "tests/infra/infra_ops/test_wal_checkpoint_monitor.py", "tests/infra/infra_runtime/test_cold_plane_isolation.py", "tests/infra/infra_runtime/test_database_layer.py", "tests/infra/infra_runtime/test_ha_sla_framework.py"]
  - id: lane2/l2-c30
    bags: 2
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 2}
    adjudication: "缺件确在 HEAD 零命中（真失踪 3 件），但同簇混跨战役欠账、死因以基底冲突为主（final_closeout §5③：重投后仍漂=人工清偿域）⇒ 不复活整袋，按行级摘取建单；本簇未逐件补实证据，标 needs_se"
    qids_sample: ["-p01-20261006-0057", "-p01-20261006-0076"]
    missing_paths_sample: ["tests/governance/test_commit_queue_pool.py", "tests/governance/test_preflight_bare_sql_alignment.py", "tests/governance/test_commit_queue_base_head.py"]
  - id: lane2/l2-c31
    bags: 2
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 1}
    adjudication: "缺面逐件复查：2 件已按新家落位（tests 八域归位），1 件同名同父目录零命中=真没落（test_resource_schedule_regen_check.py）⇒ 主体②归档，仅对真失踪件挂新建工单；整袋不复活（"
    qids_sample: ["-p01-20261006-0101", "-p01-20261006-0124"]
    missing_paths_sample: ["tests/infrastructure/test_resource_schedule_regen_check.py", "tests/scripts/test_apply_resource_plan.py", "tests/trading/test_register_post_settlement_task_form.py"]
  - id: lane2/l2-c44
    bags: 2
    families: ["st-emoreplay-20260923"]
    flags: {}
    adjudication: "缺面逐件复查：1 件已按新家落位（tests 八域归位），2 件同名同父目录零命中=真没落（gpu_emotion_condition_matrix_v1.meta.json、index.md）⇒ 主体②归档，仅对真失踪"
    qids_sample: ["play-20260923-0001", "play-20260923-0002"]
    missing_paths_sample: ["tests/alt_data/test_emotion_index_replay.py", "docs/_working/emotion_line/gpu_emotion_condition_matrix_v1.meta.json", "docs/_working/emotion_line/index.md", "tests/alt_data/test_emotion_index_replay.py", "docs/_working/emotion_line/index.md"]
  - id: lane2/l2-c51
    bags: 2
    families: ["st-fullscore-20260930"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺面逐件按“同名+同父目录”复查 HEAD：全部命中新家（tests 八域归位/模块改名落位），零件真失踪（1 件全命中）⇒ 内容被别处取代，②归档；按旧路径复活=造双真源，禁。"
    qids_sample: ["core-20260930-0020", "core-20260930-0023"]
    missing_paths_sample: ["tests/backtest/test_factory_intake_pipeline.py", "tests/backtest/test_factory_intake_pipeline.py"]
  - id: lane2/l2-c55
    bags: 2
    families: ["st-matrix-final-20260930"]
    flags: {}
    adjudication: "缺面逐件复查：1 件已按新家落位（tests 八域归位），1 件同名同父目录零命中=真没落（identifier_masking.py）⇒ 主体②归档，仅对真失踪件挂新建工单；整袋不复活（袋带已演进主件与热册快照）。"
    qids_sample: ["inal-20260930-0023", "inal-20260930-0027"]
    missing_paths_sample: ["src/zephyr/shared/security/identifier_masking.py", "tests/scripts/test_run_post_settlement_disclosure.py", "src/zephyr/shared/security/identifier_masking.py"]
  - id: lane2/l2-c56
    bags: 2
    families: ["st-matrix-final-20260930"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "死袋投的是 commit_gates/ 平铺独立 gate 文件；HEAD 实测三门以 map_family/ 聚合台子台在树且 gate_registry 三条 status: active（algo_flow 外源首"
    qids_sample: ["inal-20260930-0028", "inal-20260930-0029"]
    missing_paths_sample: ["tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py"]
  - id: lane3/l3-c07
    bags: 2
    families: ["st-audit-fix-20260924"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口只在 docs/_working/ 战役案卷（ttl=task_bound，收官未 promote、无在册消费方），代码与主册件均在 HEAD→③判废留痕；若 Owner 判仍要，按 TRAE-028 改名后行级重落"
    qids_sample: ["-fix-20260924-0018", "-fix-20260924-0049"]
    missing_paths_sample: ["docs/_working/audit_fix/AUDIT_FIX_LEDGER.md", "docs/_working/audit_fix/AUDIT_FIX_LEDGER.md"]
  - id: lane3/l3-c32
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "schema_migrations 三件（src infrastructure / scripts apply / 测试）实测全 NOT-IN-HEAD=数据库迁移正门缺位，属仍要；与热册 hea 演进无关，禁重投。"
    qids_sample: ["ereq-20261006-0058", "ereq-20261006-0157"]
    missing_paths_sample: ["src/zephyr/infrastructure/schema_migrations.py", "scripts/governance/apply_schema_migrations.py", "tests/infrastructure/test_schema_migrations.py", "src/zephyr/infrastructure/schema_migrations.py", "scripts/governance/apply_schema_migrations.py", "tests/infrastructure/test_schema_migrations.py"]
  - id: lane3/l3-c33
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "提交提速战役的 MASTER_PLAN/HANDOFF 未 promote，而同题已由后班以更优姿势落地（7e737d7af6 commitmap-cure P0 治本三向合并扩面、895b535843 G2 队列基建三"
    qids_sample: ["ereq-20261006-0125", "ereq-20261006-0219"]
    missing_paths_sample: ["docs/_working/commit_speedup_campaign/00_HANDOFF.md", "docs/_working/commit_speedup_campaign/00_MASTER_PLAN.md", "docs/_working/commit_speedup_campaign/00_HANDOFF.md", "docs/_working/commit_speedup_campaign/00_MASTER_PLAN.md"]
  - id: lane3/l3-c34
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0091", "ereq-20261006-0186"]
    missing_paths_sample: ["tests/alt_data/test_emotion_index_replay.py", "docs/_working/emotion_line/index.md", "tests/alt_data/test_emotion_index_replay.py", "docs/_working/emotion_line/index.md"]
  - id: lane3/l3-c36
    bags: 2
    families: ["st-sC-surgery-20261003"]
    flags: {}
    adjudication: "热册整档禁盲重投，且册外仍有件确实不在 HEAD（真缺口）→①复活走行级摘取+正道补登，开工单。"
    qids_sample: ["gery-20261003-0014", "gery-20261003-0015"]
    missing_paths_sample: ["docs/03_modules/_domain_governance/algo_flow/reuse_scan.yaml", "docs/03_modules/_domain_governance/algo_flow/reuse_scan.yaml"]
  - id: lane3/l3-c38
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "night_totalflow_20261001/99_delivery.md 不在 HEAD：本批实际死因是收官会话 ghost 闸（裁定#459），且数字后缀路径族受 R5-DIGIT-SUFFIX 禁令；案卷 tt"
    qids_sample: ["ereq-20261006-0108", "ereq-20261006-0203"]
    missing_paths_sample: ["docs/_working/night_totalflow_20261001/99_delivery.md", "docs/_working/night_totalflow_20261001/99_delivery.md"]
  - id: lane3/l3-c40
    bags: 2
    families: ["st-audit-fix-20260924"]
    flags: {"P0_tests_hole": 2}
    adjudication: "确有件不在 HEAD（真实缺口），且同批热册/在树件已被他队推进→①复活走行级摘取，开工单排队。"
    qids_sample: ["-fix-20260924-0016", "-fix-20260924-0052"]
    missing_paths_sample: ["tests/governance/test_commit_queue_base_head.py", "tests/governance/test_commit_queue_base_head.py"]
  - id: lane3/l3-c41
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0096", "ereq-20261006-0191"]
    missing_paths_sample: ["tests/ai_layer/scheduling/test_confirm_gate.py", "tests/ai_layer/redline/test_ai_secret_exposure.py", "tests/ai_layer/scheduling/test_confirm_gate.py", "tests/ai_layer/redline/test_ai_secret_exposure.py"]
  - id: lane3/l3-c42
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0084", "ereq-20261006-0179"]
    missing_paths_sample: ["docs/_working/wave13_chief3/inbox/merger_identity/01_case_file.md", "docs/_working/wave13_chief3/inbox/merger_identity/01_case_file.md"]
  - id: lane3/l3-c43
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0067", "ereq-20261006-0163"]
    missing_paths_sample: ["tests/ex_core/test_qmt_trading_session.py", "tests/ex_core/test_qmt_trading_session.py"]
  - id: lane3/l3-c44
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0081", "ereq-20261006-0176"]
    missing_paths_sample: ["tests/backtest/test_lane_c_formula_miner.py", "tests/backtest/test_lane_c_formula_miner.py"]
  - id: lane3/l3-c45
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0087", "ereq-20261006-0182"]
    missing_paths_sample: ["tests/zephyr/data/quality/test_sla_breach_predictor.py", "tests/zephyr/data/quality/test_sla_breach_predictor.py"]
  - id: lane3/l3-c46
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"P0_tests_hole": 2}
    adjudication: "确有件不在 HEAD（真实缺口），且同批热册/在树件已被他队推进→①复活走行级摘取，开工单排队。"
    qids_sample: ["ereq-20261006-0117", "ereq-20261006-0211"]
    missing_paths_sample: ["tests/signal_ashare/test_candidate_pool_snapshot.py", "tests/strategy_pipeline/test_pipeline_events.py", "tests/signal_ashare/test_candidate_pool_snapshot.py", "tests/strategy_pipeline/test_pipeline_events.py"]
  - id: lane3/l3-c48
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "件在 HEAD 但袋侧仍有大批独有行未吸收（能力欠账在行级不在文件级）→只能行级摘取，开工单。"
    qids_sample: ["ereq-20261006-0082", "ereq-20261006-0177"]
    missing_paths_sample: ["tests/backtest/test_factory_intake_pipeline.py", "tests/backtest/test_factory_intake_pipeline.py"]
  - id: lane3/l3-c49
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口只在 docs/_working/ 战役案卷（ttl=task_bound，收官未 promote、无在册消费方），代码与主册件均在 HEAD→③判废留痕；若 Owner 判仍要，按 TRAE-028 改名后行级重落"
    qids_sample: ["ereq-20261006-0109", "ereq-20261006-0204"]
    missing_paths_sample: ["docs/_working/deadletter_cure_20261003/20_design/commit_map_and_slimming_plan.md", "docs/_working/deadletter_cure_20261003/20_design/commit_map_and_slimming_plan.md"]
  - id: lane3/l3-c50
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "union_priority_ruler.py 与 flag_read_state.py 实测不在 HEAD 且全仓 grep 零命中=无后继同能力件；若属 F-1 十二把回归尺家族，让给施工总队车道F，本车道只指路（袋"
    qids_sample: ["ereq-20261006-0054", "ereq-20261006-0153"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/rule_bridge/union_priority_ruler.py", "src/zephyr/shared/foundation/flag_read_state.py", "src/zephyr/gov_enforcement/rule_bridge/union_priority_ruler.py", "src/zephyr/shared/foundation/flag_read_state.py"]
  - id: lane3/l3-c51
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "确有件不在 HEAD（真实缺口），且同批热册/在树件已被他队推进→①复活走行级摘取，开工单排队。"
    qids_sample: ["ereq-20261006-0098", "ereq-20261006-0193"]
    missing_paths_sample: ["scripts/governance/meta/rules_integrity_db.json", "scripts/signals/chart_condition_package.py", "scripts/governance/meta/rules_integrity_db.json", "scripts/signals/chart_condition_package.py"]
  - id: lane3/l3-c53
    bags: 2
    families: ["st-k4-20260923"]
    flags: {"lane_claim_overridden": 2, "P0_tests_hole": 1}
    adjudication: "袋要的 registry_family/registry_mass_deletion_gate.py 在 HEAD 以平路径在册（registry_family 目录 HEAD 实测为空）=同件改道落地→②归档。"
    qids_sample: ["t-k4-20260923-0006", "t-k4-20260923-0007"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py", "tests/governance/test_commit_queue_pool.py", "tests/governance/test_preflight_bare_sql_alignment.py", "src/zephyr/gov_enforcement/commit_gates/registry_family/registry_mass_deletion_gate.py"]
  - id: lane3/l3-c54
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {}
    adjudication: "与 c17/c22 同族：题录 registry/snapshot/DDL 缺体，__init__ 与 exam_loop 在树→行级摘取补件，勿重投热册。"
    qids_sample: ["ereq-20261006-0111", "ereq-20261006-0206"]
    missing_paths_sample: ["src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py", "src/zephyr/governance/meta_question/registry.py", "scripts/governance/apply_meta_question_ddl.py", "tests/governance/meta_question/test_registry.py"]
  - id: lane3/l3-c56
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0106", "ereq-20261006-0201"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py", "docs/_working/fullflow_chief_20260928/dead_letter_surgery_ledger.md", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py"]
  - id: lane3/l3-c57
    bags: 2
    families: ["st-closeout-basereq-20261006"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "缺口全是旧路径：同名件已在册于新家（git ls-files 实测逐件命中），属改道/搬家非蒸发→②归档，内容以新家现面为准。"
    qids_sample: ["ereq-20261006-0070", "ereq-20261006-0165"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py"]
  - id: lane4/l4-18
    bags: 2
    families: ["st-storageswap-20260930"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "快照路径被 .gitignore 判为再生产物区，prestage 依法拒收——产物本就不该入 git。3 袋 23 件：HEAD 全缺 2（路径今不在 HEAD 2、他径亦无同名件 0）、行级漂移 10。判据[path"
    qids_sample: ["swap-20260930-0003", "swap-20260930-0005"]
    missing_paths_sample: ["scripts/data/kline_sector_intraday_from_constituents.py", "scripts/data/kline_sector_intraday_from_constituents.py"]
  - id: lane4/l4-21
    bags: 2
    families: ["st-f14-final-sweep-20261005"]
    flags: {"lane_claim_overridden": 2, "P0_tests_hole": 1}
    adjudication: "死于存活闸（裁定#459）：属主会话 heartbeat=exited，自动重投被拒。3 袋 493 件：HEAD 全缺 5（路径今不在 HEAD 5、他径亦无同名件 4）、行级漂移 59。判据[mostly-lande"
    qids_sample: ["weep-20261005-0087", "weep-20261005-0103"]
    missing_paths_sample: ["tests/ai/ai_layer/redline/test_annual_review.py", "tests/ai/ai_layer/redline/test_negative_list.py", "tests/ai/ai_layer/redline/test_session_env_guard.py", "tests/ai/ai_layer/redline/test_sev_router.py", "tests/trade/trading/test_reference_data_manager.py"]
  - id: lane5/l5-c26
    bags: 2
    families: ["st-xhs-full-20260922"]
    flags: {"P0_tests_hole": 2}
    adjudication: "2 袋 16 文件：期权日线统计品类整链未落——同族 greeks/iv/kline 都在库唯 daily_stats 无，回补件与 E4 考试件零命中。确属缺口，但袋挟热册又是 16 文件混批，只能摘取重建。"
    qids_sample: ["full-20260922-0043", "full-20260922-0053"]
    missing_paths_sample: ["schemas/categories/market/market_option_daily_stats.py", "scripts/backfill_option_daily_stats.py", "scripts/audit/pcr_e4_exam.py", "scripts/patrol/zcode_workspace_patrol.ps1", "tests/signal_ashare/sentiment/test_option_sentiment.py", "schemas/categories/market/market_option_daily_stats.py", "scripts/backfill_option_daily_stats.py", "scripts/audit/pcr_e4_exam.py"]
  - id: lane5/l5-c30
    bags: 2
    families: ["st-mx07-chief"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "4 袋仅 3 路径且全部已由他道入库（L8 verdict 证据 archive+经典指标疑点调查 v1 双命中），残余 164 行含热册 36 行。证据抢救目的已达成——纯归档。"
    qids_sample: ["st-mx07-chief-0002", "st-mx07-chief-0006"]
    missing_paths_sample: ["docs/_working/matrix_campaign/mining/emotion_linkage_exam_v1_results.archive.json", "docs/_working/matrix_campaign/mining/emotion_linkage_exam_v1_results.archive.json"]
  - id: lane5/l5-c34
    bags: 2
    families: ["st-tailwork10-20260928", "st-tailwork6-20260928"]
    flags: {"lane_claim_overridden": 2}
    adjudication: "2 袋 v14/v18 长链重投：三张地图门『缺席』实为整族迁入 commit_gates/map_family/ 子包（逐件核到同名本体在库），尺随 tests 新家、gate_registry 9 条在册。结构性搬家"
    qids_sample: ["ork6-20260928-0001", "rk10-20260928-0001"]
    missing_paths_sample: ["tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py"]
  - id: lane6/l6-c20
    bags: 2
    families: ["st-p1b-libr", "st-sP-bottleneck-20261005"]
    flags: {"P0_tests_hole": 2}
    adjudication: "热册袋带整档快照：重投会蒸发他队条目（capability 册 62k 行损坏事故在案，终报 §3.1），禁重投。实测 21.4% 在 HEAD，余量走条目级册正道。"
    qids_sample: ["6-st-p1b-libr-0001", "neck-20261005-0069"]
    missing_paths_sample: ["tests/governance/test_library_reconcilers_red_blue.py", "docs/_working/three_piece_infra/piece1b_library/CASE.md", "docs/_working/three_piece_infra/piece1b_library/register_manifest.md", "tests/gov/governance/test_ops_guard_red_team.py", "tests/gov/governance/test_panorama_common.py", "tests/gov/governance/test_pg_dsn_utf8_guard.py", "tests/gov/governance/test_pool_dead_letter_seal.py", "tests/gov/governance/test_post_commit_guard_no_verify_threshold.py"]
  - id: lane6/l6-c21
    bags: 2
    families: ["st-sP-bottleneck-20261005", "st-tailwork7-20260928"]
    flags: {}
    adjudication: "袋内新建件缺 creation_token：token 是一次性账本物，陈袋重投时已失效/册面已变→必复发（热册损坏期曾全系 fail-closed）。"
    qids_sample: ["ork7-20260928-0001", "neck-20261005-0008"]
    missing_paths_sample: ["tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py"]
  - id: lane6/l6-c22
    bags: 2
    families: ["st-cure-p12b-20261006", "st-sP-bottleneck-20261005"]
    flags: {"P0_tests_hole": 2}
    adjudication: "陈旧测试快照 import 的符号在 HEAD 源码已改名/删除（§5.178 测试-源码漂移）＝内容级漂移；实测本簇 head_pct 极低，测试件确未落。"
    qids_sample: ["neck-20261005-0066", "p12b-20261006-0037"]
    missing_paths_sample: ["tests/gov/feedback/learning_evolution/test_evolution_engine_root.py", "tests/gov/feedback/learning_evolution/test_evolution_init.py", "tests/gov/feedback/learning_evolution/test_graduated_activation_protocol.py", "tests/gov/feedback/learning_evolution/test_hypernetwork.py", "tests/gov/feedback/learning_evolution/test_nonstationary_effectiveness.py", "tests/gov/feedback/learning_evolution/test_online_feature_importance.py", "tests/gov/feedback/learning_evolution/test_teacher_transfer.py", "tests/gov/feedback/learning_evolution/test_training_data_gov.py"]
  - id: lane6/l6-c24
    bags: 2
    families: ["st-cure-p12a-20261006", "st-cure-p12b-20261006"]
    flags: {}
    adjudication: "热册袋带整档快照：重投会蒸发他队条目（capability 册 62k 行损坏事故在案，终报 §3.1），禁重投。实测 62.5% 在 HEAD，余量走条目级册正道。"
    qids_sample: ["p12a-20261006-0023", "p12b-20261006-0021"]
    missing_paths_sample: ["tests/governance/lifecycle/test_retire_module.py", "src/zephyr/gov_enforcement/commit_gates/data_supply_chain_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/dev_delivery_map_gate.py", "src/zephyr/gov_enforcement/commit_gates/trading_day_cycle_map_gate.py", "tests/ex_core/test_bridge_instruction_kernel_trd_a10.py", "tests/governance/commit_gates/test_data_supply_chain_map_gate.py", "tests/governance/commit_gates/test_dev_delivery_map_gate.py", "tests/governance/commit_gates/test_trading_day_cycle_map_gate.py"]
  - id: lane1/l1-st-wm101
    bags: 1
    families: ["st-wm1-buildB-20260923"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["ildB-20260923-0001"]
    missing_paths_sample: ["src/zephyr/governance/registry_projection/generator.py", "tests/governance/registry_projection/test_projection_model_renderer.py", "tests/governance/registry_projection/test_projection_generator.py"]
  - id: lane1/l1-st-mas01
    bags: 1
    families: ["st-mastermap-20261004"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["rmap-20261004-0006"]
    missing_paths_sample: ["tests/governance/generators/test_panorama_master_map.py"]
  - id: lane1/l1-st-sH-02
    bags: 1
    families: ["st-sH-f8family-20261004"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "st-sH-f8family-20261004 施工快照:主件已在 HEAD 存在且演进(或改名入新路径),盲投毁新行=不可重投;内容被后续战役取代,归档②"
    qids_sample: ["mily-20261004-0006"]
    missing_paths_sample: ["docs/_working/deadletter_cure_20261003/20_design/commit_map_and_slimming_plan.md"]
  - id: lane1/l1-tests_13
    bags: 1
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 1, "P0_tests_hole": 1}
    adjudication: "tests 搬家快照;99_delivery+收官 commit 证 8域切法已落 HEAD(差集清零),死袋=被后续落地取代"
    qids_sample: ["hief-20261004-0003"]
    missing_paths_sample: ["tests/meta/scripts/test_run_post_settlement.py"]
  - id: lane1/l1-tests_14
    bags: 1
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 1, "P0_tests_hole": 1}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["hief-20261004-0004"]
    missing_paths_sample: ["docs/_working/tests_cure_campaign/03_garbage_census.md", "tests/gov/architecture/__init__.py", "tests/gov/architecture/test_contract_consistency.py", "tests/gov/architecture/test_cross_module_contracts.py", "tests/gov/architecture/test_layer_isolation.py", "tests/gov/architecture/test_money_and_docs.py", "tests/gov/architecture/test_single_order_exit.py", "tests/gov/audit/audit_core/test_audit_adversarial.py"]
  - id: lane1/l1-tests_15
    bags: 1
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 1, "P0_tests_hole": 1}
    adjudication: "tests 治理战役施工快照,战役已直连收官(129目录对HEAD差集清零)+P09按 sha256 补投 missing 件,内容已在 HEAD"
    qids_sample: ["hief-20261004-0013"]
    missing_paths_sample: ["tests/gov/architecture/__init__.py", "tests/gov/architecture/test_contract_consistency.py", "tests/gov/architecture/test_cross_module_contracts.py", "tests/gov/architecture/test_layer_isolation.py", "tests/gov/architecture/test_money_and_docs.py", "tests/gov/architecture/test_single_order_exit.py", "tests/gov/audit/audit_core/test_audit_adversarial.py", "tests/gov/audit/audit_core/test_audit_anomaly.py"]
  - id: lane1/l1-st-cur01
    bags: 1
    families: ["st-cure-p11-20261006"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["-p11-20261006-0002"]
    missing_paths_sample: ["docs/_working/commit_speedup_campaign/00_HANDOFF.md", "docs/_working/commit_speedup_campaign/00_MASTER_PLAN.md"]
  - id: lane1/l1-tests_18
    bags: 1
    families: ["st-tests-chief-20261004"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "tests 搬家快照;99_delivery+收官 commit 证 8域切法已落 HEAD(差集清零),死袋=被后续落地取代"
    qids_sample: ["hief-20261004-0131"]
    missing_paths_sample: ["tests/trade/trading/test_reference_data_manager.py"]
  - id: lane1/l1-st-acu01
    bags: 1
    families: ["st-acure-e1"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["8-st-acure-e1-0001"]
    missing_paths_sample: ["docs/_working/audit_cure_night/02_lanes/E_erratum_workbook.md"]
  - id: lane1/l1-st-acu03
    bags: 1
    families: ["st-acure-r1"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "st-acure-r1 施工快照:主件已在 HEAD 存在且演进(或改名入新路径),盲投毁新行=不可重投;内容被后续战役取代,归档②"
    qids_sample: ["8-st-acure-r1-0004"]
    missing_paths_sample: ["scripts/governance/check_registry_field_legality.py", "tests/governance/test_check_registry_field_legality.py", "tests/trading/test_process_reaper_status.py"]
  - id: lane1/l1-st-gov03
    bags: 1
    families: ["st-govfix-g3-20261007"]
    flags: {"lane_claim_overridden": 1}
    adjudication: "热册整档快照袋:禁盲投(重投蒸发他队条目,capability 册 62k 行事故在案);死袋本身归档②,未落条目走正道(账本 token+持窗者 render 投影)由工单补,禁 requeue"
    qids_sample: ["x-g3-20261007-0009"]
    missing_paths_sample: ["scripts/matrix_rescued_tmp/rowvec/bench_scaling.py", "scripts/matrix_rescued_tmp/rowvec/panelized_indicators.py", "scripts/matrix_rescued_tmp/rowvec/parity_check.py"]
  - id: lane2/l2-c04
    bags: 1
    families: ["st-bt-fast-w5-20261006"]
    flags: {}
    adjudication: "整档快照型热册袋（capability/gate/translation/registry 册）——重投=蒸发他队条目（62k 行并发写损坏事故在案）且 HEAD 已演进（max_only_head 最高 821 行）⇒"
    qids_sample: ["t-w5-20261006-0002"]
    missing_paths_sample: ["src/zephyr/gov_enforcement/rule_bridge/gate_blob_cache.py", "docs/_working/w5_bt_fast_20261006/baseline.md", "docs/_working/w5_bt_fast_20261006/step3_narrowing_list.md", "docs/_working/w5_bt_fast_20261006/receipts/W5.json", "tests/git/test_w5_blob_cache.py", "tests/git/test_w5_gate_chain_parallel.py"]
  - id: lane2/l2-c05
    bags: 1
    families: ["st-bt-fast-w5-20261006"]
    flags: {}
    adjudication: "整档快照型热册袋（capability/gate/translation/registry 册）——重投=蒸发他队条目（62k 行并发写损坏事故在案）且 HEAD 已演进（max_only_head 最高 821 行）⇒"
    qids_sample: ["t-w5-20261006-0003"]
    missing_paths_sample: ["docs/_working/w5_bt_fast_20261006/receipts/W5.json"]
  - id: lane2/l2-c07
    bags: 1
    families: ["st-c8-s4"]
    flags: {}
    adjudication: "缺面逐件复查：2 件已按新家落位（tests 八域归位），2 件同名同父目录零命中=真没落（lane_b_ledger_reconcile.py、test_lane_b_ledger_reconcile.py）⇒ 主体②"
    qids_sample: ["0928-st-c8-s4-0001"]
    missing_paths_sample: ["scripts/backtest/lane_b_ledger_reconcile.py", "tests/backtest/test_hypothesis_precheck.py", "tests/backtest/test_hypothesis_translator.py", "tests/backtest/test_lane_b_ledger_reconcile.py"]
  - id: lane2/l2-c09
    bags: 1
    families: ["st-commitspeed-tbl-20260924"]
    flags: {}
    adjudication: "战役卷宗/案卷首册在 HEAD 实测零命中（如 00_HANDOFF.md、00_MASTER_PLAN.md、reaudit_20261007.md），同战役其余册页已在树 ⇒ 内容没落且仍要（“落库防蒸发”就是本袋使"
    qids_sample: ["-tbl-20260924-0002"]
    missing_paths_sample: ["docs/_working/commit_speedup_campaign/00_HANDOFF.md", "docs/_working/commit_speedup_campaign/00_MASTER_PLAN.md"]
  - id: lane2/l2-c10
    bags: 1
    families: ["st-commitspeed-tbl-20260924"]
    flags: {}
    adjudication: "战役卷宗/案卷首册在 HEAD 实测零命中（如 00_HANDOFF.md、00_MASTER_PLAN.md、reaudit_20261007.md），同战役其余册页已在树 ⇒ 内容没落且仍要（“落库防蒸发”就是本袋使"
    qids_sample: ["-tbl-20260924-0006"]
    missing_paths_sample: ["docs/_working/commit_speedup_campaign/00_HANDOFF.md", "docs/_working/commit_speedup_campaign/00_MASTER_PLAN.md"]
  - id: lane2/l2-c11
    bags: 1
    families: ["st-commitspeed-tbl-20260924"]
    flags: {}
    adjudication: "缺件确在 HEAD 零命中（真失踪 1 件），但同簇混跨战役欠账、死因以基底冲突为主（final_closeout §5③：重投后仍漂=人工清偿域）⇒ 不复活整袋，按行级摘取建单；本簇未逐件补实证据，标 needs_se"
    qids_sample: ["-tbl-20260924-0120"]
    missing_paths_sample: ["tests/governance/test_d2_w1_env_retirement.py"]
  - id: lane2/l2-c12
    bags: 1
    families: ["st-construct-20261002"]
    flags: {"lane_claim_overridden": 1, "P0_tests_hole": 1}
    adjudication: "袋内文件全部已在 HEAD 树，差异=落地后又被别道演进（本簇 max_only_head 最高 4771 行）；死因是基底冲突/漂移（final_closeout §5③：重投后仍漂，属人工清偿域，机器重投已到极限）⇒"
    qids_sample: ["ruct-20261002-0002"]
    missing_paths_sample: ["tests/infrastructure/test_resource_schedule_regen_check.py", "tests/scripts/test_apply_resource_plan.py", "tests/trading/test_register_post_settlement_task_form.py"]
  - id: lane2/l2-c23
    bags: 1
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 1}
    adjudication: "tests 治理战役 8 域切法经收官册实测已落 7/8 域，本簇是 blob 恢复后的 280 文件复投袋⇒ 搬家批未落地=施工队欠账（任务书 §1 明判归施工队不归本车道），本车道只指路+挂单，不建议 requeue"
    qids_sample: ["-p01-20261006-0107"]
    missing_paths_sample: ["docs/_working/tests_cure_campaign/03_garbage_census.md", "tests/gov/autonomy_core/test_killswitch_response_levels.py", "tests/gov/boundary/__init__.py", "tests/gov/boundary/test_ex_dividend.py", "tests/gov/boundary/test_limit_up_down.py", "tests/gov/boundary/test_reconnect.py", "tests/gov/boundary/test_suspension.py", "tests/gov/boundary/test_t_plus_1.py"]
  - id: lane2/l2-c32
    bags: 1
    families: ["st-cure-p01-20261006"]
    flags: {}
    adjudication: "缺件确在 HEAD 零命中（真失踪 1 件），但同簇混跨战役欠账、死因以基底冲突为主（final_closeout §5③：重投后仍漂=人工清偿域）⇒ 不复活整袋，按行级摘取建单；本簇未逐件补实证据，标 needs_se"
    qids_sample: ["-p01-20261006-0003"]
    missing_paths_sample: ["docs/_working/e2e_integration/cost_qualified_list_reexam_20260923.yaml"]
  - id: lane2/l2-c33
    bags: 1
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 1}
    adjudication: "缺件确在 HEAD 零命中（真失踪 7 件），但同簇混跨战役欠账、死因以基底冲突为主（final_closeout §5③：重投后仍漂=人工清偿域）⇒ 不复活整袋，按行级摘取建单；本簇未逐件补实证据，标 needs_se"
    qids_sample: ["-p01-20261006-0045"]
    missing_paths_sample: ["tests/gov/gov_code_dedup/test_config_test_code_dedup_engine.py", "tests/gov/gov_code_dedup/test_degradation_edge.py", "tests/gov/gov_code_dedup/test_micro_clone.py", "tests/gov/gov_code_dedup/test_scanner_cross.py", "tests/gov/gov_code_dedup/test_scanner_raw.py", "tests/gov/gov_code_dedup/test_self_scan_integrity.py", "tests/gov/gov_drift/test_agent_stability_index.py", "tests/gov/gov_enforcement/create_guard_batch_replay.py"]
  - id: lane2/l2-c34
    bags: 1
    families: ["st-cure-p01-20261006"]
    flags: {"P0_tests_hole": 1}
    adjudication: "缺件确在 HEAD 零命中（真失踪 5 件），但同簇混跨战役欠账、死因以基底冲突为主（final_closeout §5③：重投后仍漂=人工清偿域）⇒ 不复活整袋，按行级摘取建单；本簇未逐件补实证据，标 needs_se"
    qids_sample: ["-p01-20261006-0060"]
    missing_paths_sample: ["schemas/categories/market/market_option_daily_stats.py", "scripts/backfill_option_daily_stats.py", "scripts/audit/pcr_e4_exam.py", "scripts/patrol/zcode_workspace_patrol.ps1", "tests/signal_ashare/sentiment/test_option_sentiment.py"]
```
