---
asset_id: "DOC:docs/_working/ultimate_library/COVERAGE.md"
ttl: "task_bound"
doc_type: "audit_report"
---

# 馆藏双向对账报告（盲册+ghost）

- 构建时戳（UTC）：2026-09-25T05:00:07.980494+00:00
- 盘上在扫文件：33437｜馆内在编（file/module）：33573
- **blind（盘有馆无）：1**
- **ghost（馆有盘无）：137**

## blind 样本（前 50）

- FILE:data/red_blue/trigger_queue/1790312391_2a77ad90.json

## ghost 样本（前 50）

- DOC:docs/02_enterprise_architecture/08_algorithm_overview/stages/index.md
- DOC:docs/03_modules/_domain_governance/algo_flow/data_governance/akshare_quote_provider.yaml
- FILE:.runtime/audit/algo_flow_translation_sync_runs.jsonl
- FILE:.runtime/audit/archive_log.jsonl
- FILE:.runtime/audit/feature_flags.jsonl
- FILE:.runtime/audit/hook_tracked_drift.jsonl
- FILE:.runtime/audit/safe_write.jsonl
- FILE:.runtime/audit/skill_factory_cas.jsonl
- FILE:.runtime/audit/worktree_drift_watchdog.jsonl + .runtime/audit/watchdog.jsonl
- FILE:.runtime/fetch_perf/fetch_perf_YYYYMMDD.jsonl
- FILE:.runtime/gate_audit/allow_overlap_usage.jsonl
- FILE:.runtime/gate_audit/commit_lock_fallback.jsonl
- FILE:.runtime/gate_audit/design_node_delete.jsonl + .runtime/gate_audit/depgraph_anchor_cascade.jsonl
- FILE:.runtime/gate_audit/force_merge_usage.jsonl
- FILE:.runtime/gate_audit/gateway_index_hygiene.jsonl
- FILE:.runtime/gate_audit/git_guard_self_harm.jsonl
- FILE:.runtime/gate_audit/ops_guard_delete.jsonl
- FILE:.runtime/gate_audit/post_claim_modifications.jsonl
- FILE:.runtime/gate_audit/protected_paths_bypass.jsonl
- FILE:.runtime/gate_audit/safe_rmtree.jsonl
- FILE:.runtime/gate_audit/worktree_abort.jsonl
- FILE:.runtime/gate_audit/worktree_skip.jsonl
- FILE:.runtime/gate_audit/worktree_status_snapshots.jsonl
- FILE:.runtime/git_performance_log.jsonl
- FILE:.runtime/lookup_audit/bypass_audit.jsonl
- FILE:.runtime/quarantine/branch_refs.log
- FILE:.runtime/workspace_drift_warn.jsonl
- FILE:.runtime/worktree_ops_log.jsonl
- FILE:.zephyr/audit/rollback_discard_audit.jsonl
- FILE:.zephyr/audit/rollback_nexus_audit.jsonl
- FILE:.zephyr/audit/rollback_operations_audit.jsonl
- FILE:.zephyr/intent_archive/manifest.jsonl
- FILE:.zephyr/kill_switches.jsonl
- FILE:.zephyr/knowngoodstate_ledger.jsonl
- FILE:.zephyr/rollback_budget_log.jsonl
- FILE:.zephyr/rollback_lock_queue.jsonl
- FILE:.zephyr/rollback_loop_log.jsonl
- FILE:.zephyr/rollback_wal.jsonl
- FILE:.zephyr/topology_change_log.jsonl
- FILE:data/audit_trail/events.jsonl
- FILE:data/audit_trail/gate_chain.jsonl
- FILE:data/backtest_artifacts/ibt-20260922/W_HOLDOUT/run_summary.json
- FILE:data/backtest_artifacts/ibt-20260922/W_IS/redblue_round2.json
- FILE:data/backtest_artifacts/ibt-20260922/W_IS/redblue_round3.json
- FILE:data/backtest_artifacts/ibt-20260922/W_IS/run_summary.json
- FILE:data/backtest_artifacts/ibt-20260922/W_IS/sensitivity.json
- FILE:data/backtest_artifacts/ibt-20260922/W_OOS/redblue_round1.json
- FILE:data/backtest_artifacts/ibt-20260922/W_OOS/redblue_round4.json
- FILE:data/backtest_artifacts/ibt-20260922/W_OOS/run_summary.json
- FILE:data/backtest_artifacts/ibt-20260922/W_OOS/sensitivity.json
