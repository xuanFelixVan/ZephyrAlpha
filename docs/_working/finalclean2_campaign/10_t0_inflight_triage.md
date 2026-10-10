---
ttl: task_bound
completes_when: 793 件逐属主认领完成且两枚锚可安全释放后转归档
---
# T0 在飞面分流案卷（终清二期·波二前置件 T0）

- 袋＝`c2de2face68db9e019ba0d9cf4cde6417643158b`（`On dev: st-constland-20261010-T2-merge-transit`，12:34:13）
- 锚＝`refs/quarantine/st-govjudge-20261010-20261010`（原锚，名指 govjudge 实为 constland transit）＋本班新锚 `refs/recover/inflight-20261010`（同 commit，additive，禁 drop/禁 clear）
- 全集 1,444 件（主 diff 1,266 ∪ index 态 1,298；该 stash 只有 2 父＝未带 -u，故未跟踪树 0 件）；已回归盘面 651 件；**仍在袋内 793 件**

## 一、按 dev 身位三分（决定谁该紧张）

| 类 | 件数 | 含义 | 属主动作（本班未代做） |
|---|---:|---|---|
| 甲：dev 有此路径、盘面缺 | 0 | 盘面缺件，dev 有身位 | `git checkout dev -- <path>` |
| 乙：dev 无此路径 | 793 | **袋内字节是唯一版** | `git checkout c2de2fac -- <path>` 后走正门 |
| 丙：分类矛盾件 | 0 | 对账器口径复核面 | 见文末 |

## 二、乙类（唯一版）按属主分流

| 属主面 | 件数 | 认领状态 |
|---|---:|---|
| domain:tests | 274 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:decision_map_campaign_20260924 | 91 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:total_command_closeout | 30 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:pipeline-research | 20 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:fms_overhaul | 19 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:circulation_chief | 16 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:fullcirculation_campaign_20261008 | 16 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:master_tc_night | 16 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:three_piece_infra | 16 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:commit_speedup_campaign | 12 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:decision_map_campaign | 12 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:qcure_campaign | 11 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:archive | 10 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:fullcirculation_campaign | 10 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:audit_cure_night | 9 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:chain_fullflow_closeout | 9 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:matrix_campaign | 9 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:meta_question_answers | 9 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:audit_fix | 8 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:lib_ram_campaign | 8 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:map_build | 8 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:question_mining_campaign | 8 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:qmine_campaign | 7 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| domain:scripts | 7 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| domain:src | 7 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:l5_lanes | 6 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:tail3 | 6 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:commitmap_cure | 5 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:industry_chain_alpha | 5 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:night_sweep | 5 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| domain:modules_doc | 4 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:dexp_campaign | 4 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:fullscore_night | 4 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:map_census | 4 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:wave13_chief3 | 4 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:chain_piling_campaign | 3 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:chiefc_campaign | 3 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:fullflow_chief_20261001 | 3 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:master_tc_20261006 | 3 | 待认领（本班已登记；属主活性由 §三 三源表判） |
| campaign:night_totalflow_chief | 3 | 待认领（本班已登记；属主活性由 §三 三源表判） |

### 乙类内容构成（不自判退役）

- docs/_working 案卷：501 件
- 其它（代码/配置/数据面）：292 件

## 三、甲类（dev 有身位）按属主分流

| 属主面 | 件数 |
|---|---:|

## 四、乙类逐件清单（前 200 件，全量见 inflight_recon.jsonl 里 `current` 以"仍在袋内"开头者）

```
domain:modules_doc                             docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-S1-02__comparison__02_dualwindow.yaml
domain:modules_doc                             docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-S1-03__comparison__02_dualwindow.yaml
domain:modules_doc                             docs/03_modules/_domain_execution_core/algo_flow/phase_discriminator.yaml
domain:modules_doc                             docs/03_modules/_domain_strategy_pipeline/algo_flow/graduated_package_feed.yaml
campaign:2026-09-18-landing-anchor-algo-flow-closeout docs/_working/2026-09-18-landing-anchor-algo-flow-closeout/index.md
campaign:2026-10-09-tdm-exam-card-system-plan.md docs/_working/2026-10-09-tdm-exam-card-system-plan.md
campaign:ai_layer_vision                       docs/_working/ai_layer_vision/closure_wave2/index.md
campaign:align_dirty                           docs/_working/align_dirty/index.md
campaign:altdata_night                         docs/_working/altdata_night/index.md
campaign:archive                               docs/_working/archive/2026-10/index.md
campaign:archive                               docs/_working/archive/2026-10/sector_line/index.md
campaign:archive                               docs/_working/archive/2026-10/sector_line/statreplay/index.md
campaign:archive                               docs/_working/archive/2026-10/sim_launch/index.md
campaign:archive                               docs/_working/archive/2026-10/sweep_tail/index.md
campaign:archive                               docs/_working/archive/2026-10/t0_matrix/index.md
campaign:archive                               docs/_working/archive/2026-10/t0_matrix/rerun_frozen/index.md
campaign:archive                               docs/_working/archive/2026-10/t0_revival/index.md
campaign:archive                               docs/_working/archive/2026-10/vocab_legislation/index.md
campaign:archive                               docs/_working/archive/2026-10/同花顺资料/index.md
campaign:audit_all                             docs/_working/audit_all/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/01_mining/branch_landing/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/01_mining/deadbag_recovery/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/01_mining/desktop_lists/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/01_mining/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/01_mining/ledger_erratum/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/01_mining/open_questions/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/02_lanes/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/99_delivery/index.md
campaign:audit_cure_night                      docs/_working/audit_cure_night/index.md
campaign:audit_fix                             docs/_working/audit_fix/cross/index.md
campaign:audit_fix                             docs/_working/audit_fix/index.md
campaign:audit_fix                             docs/_working/audit_fix/lanes/L1_commit_base/index.md
campaign:audit_fix                             docs/_working/audit_fix/lanes/L2_ruling_resurrection/index.md
campaign:audit_fix                             docs/_working/audit_fix/lanes/L3_dangling_py_gomap/index.md
campaign:audit_fix                             docs/_working/audit_fix/lanes/L4_registry_counts/index.md
campaign:audit_fix                             docs/_working/audit_fix/lanes/L5_align_head_anchor/index.md
campaign:audit_fix                             docs/_working/audit_fix/lanes/index.md
campaign:audit_integrity                       docs/_working/audit_integrity/index.md
campaign:axis_unify                            docs/_working/axis_unify/index.md
campaign:bm_reclass_ruling                     docs/_working/bm_reclass_ruling/index.md
campaign:board_synthesis                       docs/_working/board_synthesis/index.md
campaign:branch_zero_takeover                  docs/_working/branch_zero_takeover/construct/index.md
campaign:branch_zero_takeover                  docs/_working/branch_zero_takeover/index.md
campaign:branch_zero_takeover_20261002         docs/_working/branch_zero_takeover_20261002/index.md
campaign:ch_fail_loud_campaign_20260926        docs/_working/ch_fail_loud_campaign_20260926/index.md
campaign:chain_circulation_campaign            docs/_working/chain_circulation_campaign/index.md
campaign:chain_fullflow_20260926               docs/_working/chain_fullflow_20260926/index.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/index.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_chief_authority.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_empty_tables.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_flag_readfail.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_hfq_lineage.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_queue_liveness.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_queue_liveness.md.tmp.21964.1791474350827
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_scheduled_tasks.md
campaign:chain_fullflow_closeout               docs/_working/chain_fullflow_closeout/ruling_verify_landed.md
campaign:chain_piling_campaign                 docs/_working/chain_piling_campaign/index.md
campaign:chain_piling_campaign                 docs/_working/chain_piling_campaign/infra_mining/index.md
campaign:chain_piling_campaign                 docs/_working/chain_piling_campaign/snapshots/index.md
campaign:chief8_night                          docs/_working/chief8_night/index.md
campaign:chief_fullchain_20261006              docs/_working/chief_fullchain_20261006/env_mining/index.md
campaign:chief_fullchain_20261006              docs/_working/chief_fullchain_20261006/index.md
campaign:chief_fullchain_campaign              docs/_working/chief_fullchain_campaign/env_mining/index.md
campaign:chief_fullchain_campaign              docs/_working/chief_fullchain_campaign/index.md
campaign:chiefc_campaign                       docs/_working/chiefc_campaign/g_lane_r01_r16_ledger.md
campaign:chiefc_campaign                       docs/_working/chiefc_campaign/index.md
campaign:chiefc_campaign                       docs/_working/chiefc_campaign/rb1_eval.md
campaign:circulation_chief                     docs/_working/circulation_chief/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/logs/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/A_data_supply/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/B_strategy_factory/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/C_knowledge/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/D_tdm/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/E_execution/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/F_risk_compliance/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/G_backtest/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/H_promotion/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/I_scheduler/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/J_ai_layer/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/K_governance_gates/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/L_frontend/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/M_crosscut/index.md
campaign:circulation_chief                     docs/_working/circulation_chief/skeleton/index.md
campaign:cleanup_final                         docs/_working/cleanup_final/index.md
campaign:closure_audit_20261008                docs/_working/closure_audit_20261008/00_终审裁定表.md
campaign:closure_audit_20261008                docs/_working/closure_audit_20261008/index.md
campaign:cmd_ledger                            docs/_working/cmd_ledger/index.md
campaign:commit_chain_fullflow                 docs/_working/commit_chain_fullflow/index.md
campaign:commit_chain_mining                   docs/_working/commit_chain_mining/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/00_skeleton/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/10_D1_D2/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/20_target_arch/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/30_gate_census/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/40_B0_derived_offload/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/50_replay_baseline/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/60_deep_dive/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/60_deep_dive/r1_data/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/70_redblue/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/80_hmac_proposal/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/90_verification/index.md
campaign:commit_speedup_campaign               docs/_working/commit_speedup_campaign/index.md
campaign:commit_system_opt                     docs/_working/commit_system_opt/index.md
campaign:commitmap_cure                        docs/_working/commitmap_cure/a2_gap_list.yaml
campaign:commitmap_cure                        docs/_working/commitmap_cure/a2_ledger_census.md
campaign:commitmap_cure                        docs/_working/commitmap_cure/chief_handoff_20261008.md
campaign:commitmap_cure                        docs/_working/commitmap_cure/index.md
campaign:commitmap_cure                        docs/_working/commitmap_cure/t_guardfix_report.md
campaign:commitspeed_audit                     docs/_working/commitspeed_audit/index.md
campaign:constland_campaign                    docs/_working/constland_campaign/00_ledger.md
campaign:datatail                              docs/_working/datatail/index.md
campaign:datavein                              docs/_working/datavein/index.md
campaign:deadcure_campaign                     docs/_working/deadcure_campaign/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L01_regime/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L02_emotion/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L03_sector/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L04_stock_wire/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L05_t0/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L05_t0/rule_cards/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L06_exam_alloc/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L07_exec/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L08_risk/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/L09_review/index.md
campaign:decision_map_campaign                 docs/_working/decision_map_campaign/links/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/adj/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/du881_verdict/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/engine_caliber_map/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/landing/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s10_downstream_consumer_surface/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s11_validation_family/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s12_secondary_model_farm/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s1_hmm_kernel/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s2_overlay_transition_engine/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s3_overlay_signal_suppliers/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s4_feature_pipeline/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s5_shrinkage_risk_signals/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s6_snapshot_production_slot/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s7_anchored_state_track/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s8_six_phase_truth_chain/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L01_regime/s9_alt_regime_channel/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/a_builder_kernel/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/b_history_replay_line/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/c1_limitup_temperature/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/c2_promotion_rate/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/c3_breadth/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/c4_volume_energy/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/c5_leverage_margin/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/c6_news_sentiment/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/d_e_auction_and_rating_candidates/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/f_legacy_emotion_cluster/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/g_tomorrow_emotion_forecast/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/h_consumption_surface/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L02_emotion/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b1_index_data_foundation/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b2_state_aggregation_kernel/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b3_pipeline_slots_preference/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b4_fund_dimension/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b5_rotation_algorithm_family/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b6_l2_gate_wiring/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b7_constituent_and_coordinates/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/b8_p1_conditional_tables/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L03_sector/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s1_conduction_gate/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s2_constituent_mapping/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s3_candidate_pool_chain/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s4_factor_layer_and_news_dim/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s5_tradability_filters/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L04_stock_wire/s6_stock_state_axis/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/etf_t0_cost_and_pool/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/news_dimension_pit/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/period_axis_semantics/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_card_candidate_surface/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/rule_cards/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/state_match_downstream_surface/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L05_t0/tick_imbalance_material/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/exam_result_writeback/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/exam_ruler_holdout/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/onboarding_rules_matrix/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/resonance_friction_assembly/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc/search_executor_prereg/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s1_signal_to_order/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s2_order_pipeline/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s3_qmt_bridge_client/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s4_execution_report_chain/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s5_cost_feedback_loop/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s6_execution_algorithms/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s7_slippage_calibration/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s8_depth_and_imbalance/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L07_exec/s9_sell_and_daban/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L08_risk/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L08_risk/s1_system_killswitch_agent_behavior/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L08_risk/s2_five_level_circuit_breaker/index.md
campaign:decision_map_campaign_20260924        docs/_working/decision_map_campaign_20260924/links/L08_risk/s3_tdm_drawdown_state_machine/index.md
```
