# Worktree 内未跟踪 `docs/_working` 成果 · 抢救清单（v2 全量）

> 生成时间：2026-10-14 　session：st-docconsol-20261014　**copy2，未删源**

## 为什么有这个目录

1. `git status --porcelain`（不带 `-uno`）**默认只报主工作区**；worktree 内部的 `??` 文件在主区命令里**完全看不见**。
2. 本轮「把 `docs/_working` 整合归档」若只扫主工作区，这 **292 个文件 / 3.65 MiB** 会系统性漏网。
3. 而这些 worktree 后续若被 prune，`git worktree remove` 会**连带删除 untracked 文件** ⇒ 归档漏 + prune 删 = 内容归零。
4. **这不是理论风险**：`finalclean2_campaign/00_ledger.md:79` 记录了**已发生**的同类事故——主区 `00_ledger.md` 于 12:31→13:08 间从盘面消失，全程 untracked，git 侧零痕迹，**唯一存活处是车道快照**。

## 归档扫描面口径（应固化为纪律）

> **归档扫描面 = 主工作区 `docs/_working` ＋ 64 个 worktree 内的 `docs/_working` 未跟踪文件**

## 清单

| 来源 | 类型 | 复制文件数 |
|---|---|---|
| `./docs/_working/condaxis/07_sharpe2_reality_verdict.md` | FILE | 1 |
| `./docs/_working/rule_library_survey/02_裁定书与规则纵向地图方案.md` | FILE | 1 |
| `.aidrafts/st-deadmass3-20261014/docs/_working/deadmass_campaign/99_delivery_shift3.md` | FILE | 1 |
| `.aidrafts/st-fclean4-20261012/docs/_working/finalclean2_campaign/wave4/` | DIR | 17 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/10_exam_recast_quintile.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/12_gcal1_reconciliation.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/13_exam_run_limit_up.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/15_work_orders_engine_and_vocab.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/16_pillar_vocab_census.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/17_sector_line_closeout.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/18_route_audit_replay.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/19_route_audit_reconciliation.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/20_reverse_triage.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/21_exam_run_event_switch.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/22_reverse_audit_result.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/23_exploration_digest.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/24_exploration_recalc_order_receipt.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/25_exploration_price_correction_and_blockers.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/26_v3_breadth_scan_prep.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/27_five_card_freeze_protocol.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/28_ruling_execution_and_impl_fork.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/30_chwindow_hold_and_unfreeze.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/32_breadth_scan_result.yaml` | FILE | 1 |
| `.aidrafts/st-mineloop-20261010/docs/_working/mineloop_campaign/draft_TDM-X-R1-01__comparison__06_基线出生件与r位声明版.yaml` | FILE | 1 |
| `.worktrees/st-bakdr-20261013/docs/_working/infoaxis/` | DIR | 2 |
| `.worktrees/st-finalclean2-20261010/docs/_working/finalclean2_campaign/` | DIR | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/01_anchor_reverify_lanec.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/02_gpu03_dataset_and_f1_evidence.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/03_gpu01_gpu02_construction.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/04_gpu04_b007_material.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/05_lanec_fakegreen_fix.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/06_llama_cpp_install.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/07_gpu04_correction_and_blockers.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/08_gpu03b_p0_p2_pipeline.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/09_r3_shard_and_projection_lag_block.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/10_gpu04_shadow_leg.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/11_resource_declaration_and_overlap_precheck.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/12_post_window_measurements_and_premises.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/13_gold_owner_corrections_v1.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/14_gold_freeze_v1_record.yaml` | FILE | 1 |
| `.worktrees/st-gpuwo-20261011/docs/_working/gpuwo_campaign/gold_expansion_spotcheck_pack.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-24-aiarch-construction-list.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-24-designmemos-construction-list.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-25-page-by-page-review.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-28-d-disk-cleanup-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-28-remaining-construction-roadmap.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-30-b16-feed-exploration.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-30-b4-six-factor-construction-breakdown.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-30-b7-batch-bc-doc-supplement-checklist.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-31-frontend-gap-views-derived.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-08-31-frontend-governance-four-piece-drafts.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-01-stockq-component-split-inventory-v2.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-04-trading-decision-map-discussion.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-05-audit-greatwall-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-05-steward-b-class-owner-book.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-06-flash-execution-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-07-tdm-backtest-protocol.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-07-tdm-internal-factpack.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-07-tdm-pre-backtest-review-checklist.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-07-tdm-review-round-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-08-qmt-bridge-migration-ledger.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-clearance-night-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-greatwall-quality-task-brief.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-news-industry-wiring-directive.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-node-backtest-governance.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-node-template-draft.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-tdm-field-upgrade-discussion.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-tdm-growth-blueprint.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-tdm-missing-modules-construction.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-09-tdm-night-greatwall-directive.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-10-chainmap-frontend-batch-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-10-commit-pipeline-perf-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-10-legacy-clear-night-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-10-nodebt-night-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-10-xflow-batch-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-10-xflow-followup-design.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-backtest-evidence-log-discussion.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-backtest-system-sop-discussion.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-chainmap-final-batch-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-commit-queue-dead-zero-closure.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-crypto-shadow-mvp.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-g07-sentiment-validation.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-l308-aggregator-construction.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-news-chain-wiring-spec-cards.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-11-tdm-morning-review-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-alt-data-batch1-construction-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-alt-data-construction-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-alt-data-handoff.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-data-layer-gap-analysis.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-expectation-consumption-design.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-fundamental-consumption-design.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-handoff-c3-zcode.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-igfact-ckg2021-data-asset-analysis.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-research-report-data-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-research-report-handoff.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-12-work-roadmap.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-c5-cluster-differentiation-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-dedup-analysis.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-factory-gate-review.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-io-structure-anchor-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-knowledge-reserve-nonpipeline.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-p002-semantic-review.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-panic-rebound-sim-paper.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-strategy-factory-pipeline-discussion.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-tdm-upgrade-blueprint.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-xtreme-redblue-retest.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-xtreme-redblue-v3-log.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-xtreme-redblue-v3-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-13-xtreme-redblue-v3-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-agg-switch-design.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-auto-mount-research.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-c4-history-repair-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-ch-connection-handoff.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-chart-pattern-mining-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-combination-layer-exhaustive-charter.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-dsr-enable-impact-assessment.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-fac-e1c-formula-mining-design.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-full-chain-factory-blueprint.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-handoff-market-data-repair.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-indicator-mining-batch4.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-lane-c-agentic-mining-charter.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-market-data-gap-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-p0-syntax-gate.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-p002-reprint-result.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-pattern-consumer-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-sim-partition-discussion.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-supply483-verification-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-tdm-consumption-sop-draft.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-tilib-batch6-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-tilib-batch7-wiring-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-typhoon-bdi-factor-mining-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-14-xtreme-redblue-v4-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-c4-acceptance-interim.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-c5-cluster-refresh.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-four-big-items-blueprint.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-full-automation-night-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-governance-module-mining-sop-map.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-gutters-eoc3-verification-deadend.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-handoff-factory-docs-discussion.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-neff-estimator-preregistration.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-szopen-pipeline-handoff.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-15-tilib-handoff.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-18-gate-identity-root-fix-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-18-rule-audit-master-construction-plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-19-overnight-handover-max-shift.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/2026-09-19-overnight-scope-lock-report.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/alt_data_consumption_plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/auction_bridge_switch_mining_2026_09_17.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/construction_backlog.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/infoaxis/11_equity_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/infoaxis/12_research_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/infoaxis/13_earnings_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/infoaxis/14_retail_ir_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/infoaxis/15_intraday_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/infoaxis/99_delivery.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/p21_contract_header_slimming_proposal.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/pipeline-research/promotion-reports/` | DIR | 96 |
| `.worktrees/st-infoaxis-20261013/docs/_working/pipeline-research/sim-memos/sim-memo-202610.json` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/pipeline-research/sim-memos/sim-memo-202610.md` | FILE | 1 |
| `.worktrees/st-infoaxis-20261013/docs/_working/qcure_commit_queue_plan.md` | FILE | 1 |
| `.worktrees/st-infoaxis-land-20261014/docs/_working/infoaxis/11_equity_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-land-20261014/docs/_working/infoaxis/12_research_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-land-20261014/docs/_working/infoaxis/13_earnings_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-land-20261014/docs/_working/infoaxis/14_retail_ir_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-land-20261014/docs/_working/infoaxis/15_intraday_workbook.md` | FILE | 1 |
| `.worktrees/st-infoaxis-land-20261014/docs/_working/infoaxis/99_delivery.md` | FILE | 1 |
| `.worktrees/st-libstale-20261013/docs/_working/libghost_campaign/` | DIR | 2 |
| `.worktrees/st-maint5-20261013/docs/_working/maint5_campaign/` | DIR | 1 |
| `.worktrees/st-maint6-20261013/docs/_working/maint4_campaign/` | DIR | 1 |
| `.worktrees/st-maint6-20261013/docs/_working/maint6_campaign/` | DIR | 1 |
| `.worktrees/st-minedig2-20261012/docs/_working/disk_reorg_campaign/vhdx_precheck_20261013.md` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/10_ruler_calibration_preregistration_v1.md` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/11_ruler_calibration_report_v1.md` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/11_ruler_calibration_v1.yaml` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/12_ruler_calibration_verdict_v1.yaml` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/13_ruler_calibration_size_control_v1.yaml` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/21_negative_results_family_v1.md` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/22_f06_archive_ruling2_v1.md` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/23_evening_pack_v1.md` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/24_positive_control_backfill_spec_v1.md` | FILE | 1 |
| `.worktrees/st-statsgov-20261012/docs/_working/statsgov_campaign/90_calibration_runners_source.md` | FILE | 1 |

合计：**294 个文件 / 3764.3 KiB**
