---
ttl: task_bound
date: 2026-09-17
generated_at: 2026-09-17T03:49:08
generated_by: scripts/governance/d5_architecture/generators/report_algo_flow_author_debt.py
---

<!-- GENERATED — do not hand-edit -->

# ALGO_FLOW 出仓作者欠账台账（P2-1 尾池）

> 本文由 `scripts/governance/d5_architecture/generators/report_algo_flow_author_debt.py` 生成，勿手改（AGENTS.md §9 第 5 条：静态清单必由生成器产出）。
> 时间源：`idempotent_timestamp`（本脚本最近 git commit 时间，相同 commit→相同输出）。
> 池来源：`--scan-pool`（现扫 src/zephyr 内联块，无手工清单）；判据：`externalize(dry_run=True)`（零写入）的 skipped 报因。
> 欠账=补节点/补边即臆造算法语义，禁工具代做（伪造边会把错图渲染成「已验证」全景图）。

## 统计

| 类 | 件数 | 报因真源（出仓器常量，勿改写） | 后续派工口径 |
|------|:---:|------|------|
| 五段式散文（欠机器块行） | 47 | `legacy 五段式 prose (no - id: rows)` | 按五段式口径补 `- id:` 机器块行后重跑本批 |
| 零边图（欠边） | 17 | `graph has no edges (validate_graph would block)` | 补边须作者裁定语义，禁工具臆造（伪造边=错图冒充已验证） |
| 块不可解析（零节点） | 5 | `block unparsable (no nodes)` | 逐件诊断块形，能补则补、该删则删（须作者确认） |
| **作者欠账合计** | **69** | — | 本台账的账 |
| 可机械出仓（dry-run 判可动） | 0 | — | 归出仓批，非欠账 |
| 其他（须逐件看报因） | 0 | — | 几何/定位类，非内容欠账 |
| 池总数 | 69 | — | 恒等式：欠账+可机械+其他=池总数 |

状态分布：skipped=69

## 五段式散文（欠机器块行）（47 件）

报因：`legacy 五段式 prose (no - id: rows)`
派工：按五段式口径补 `- id:` 机器块行后重跑本批

### signal_ashare（23 件）

- `src/zephyr/signal_ashare/auction_microstructure_analyzer.py`
- `src/zephyr/signal_ashare/bottom_confirmation_entry.py`
- `src/zephyr/signal_ashare/capital_behavior_orchestrator.py`
- `src/zephyr/signal_ashare/chanlun_structure.py`
- `src/zephyr/signal_ashare/cross_asset_ratio_monitor.py`
- `src/zephyr/signal_ashare/false_breakout_trap_detector.py`
- `src/zephyr/signal_ashare/intraday_t0/intraday_volume_orderflow.py`
- `src/zephyr/signal_ashare/intraday_t0/t0_trading_pipeline.py`
- `src/zephyr/signal_ashare/limit_up/limit_up_ecosystem_leadership.py`
- `src/zephyr/signal_ashare/limit_up/limit_up_potential_scorer.py`
- `src/zephyr/signal_ashare/ml_forecast/gap_fill_model.py`
- `src/zephyr/signal_ashare/ml_forecast/mc_path_simulator.py`
- `src/zephyr/signal_ashare/ml_forecast/next_day_probability_gate.py`
- `src/zephyr/signal_ashare/multi_indicator_divergence.py`
- `src/zephyr/signal_ashare/screening/relative_strength_screener.py`
- `src/zephyr/signal_ashare/screening/screening_funnel_report.py`
- `src/zephyr/signal_ashare/sector/sector_momentum_persistence.py`
- `src/zephyr/signal_ashare/sentiment/extreme_sentiment_reversal_detector.py`
- `src/zephyr/signal_ashare/sentiment/sentiment_price_divergence.py`
- `src/zephyr/signal_ashare/stock_signal_strength.py`
- `src/zephyr/signal_ashare/strategy_signal/signal_factory.py`
- `src/zephyr/signal_ashare/strategy_signal/unified_pattern_engine.py`
- `src/zephyr/signal_ashare/wyckoff_accumulation_signal.py`

### plan_engine（19 件）

- `src/zephyr/plan_engine/auction_hit_recorder.py`
- `src/zephyr/plan_engine/batch_boundary_runner.py`
- `src/zephyr/plan_engine/boundary_revision_engine.py`
- `src/zephyr/plan_engine/brier_calibration.py`
- `src/zephyr/plan_engine/closing_session_decision.py`
- `src/zephyr/plan_engine/daily_trade_plan.py`
- `src/zephyr/plan_engine/daily_warroom_pipeline.py`
- `src/zephyr/plan_engine/evidence_chain_decision.py`
- `src/zephyr/plan_engine/llm_premarket_analysis.py`
- `src/zephyr/plan_engine/overnight_boundary_reviser.py`
- `src/zephyr/plan_engine/premarket_constraint_loader.py`
- `src/zephyr/plan_engine/scenario_attribution_stats.py`
- `src/zephyr/plan_engine/scenario_plan_recorder.py`
- `src/zephyr/plan_engine/scenario_planner.py`
- `src/zephyr/plan_engine/scenario_probability_model.py`
- `src/zephyr/plan_engine/sit_out_list.py`
- `src/zephyr/plan_engine/tomorrow_boundary_planner.py`
- `src/zephyr/plan_engine/trading_analyst_agents.py`
- `src/zephyr/plan_engine/trading_debate.py`

### factor（1 件）

- `src/zephyr/factor/analysis/factor_similarity_cluster.py`

### pf_alloc（1 件）

- `src/zephyr/pf_alloc/batched_position_builder.py`

### reporting（1 件）

- `src/zephyr/reporting/ai_review_summary.py`

### research（1 件）

- `src/zephyr/research/factor_mining_pipeline.py`

### trading（1 件）

- `src/zephyr/trading/trigger_registry.py`

## 零边图（欠边）（17 件）

报因：`graph has no edges (validate_graph would block)`
派工：补边须作者裁定语义，禁工具臆造（伪造边=错图冒充已验证）

### signal_ashare（4 件）

- `src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py`
- `src/zephyr/signal_ashare/strategy_signal/pattern_lifecycle.py`
- `src/zephyr/signal_ashare/strategy_signal/pattern_signal_runtime.py`
- `src/zephyr/signal_ashare/strategy_signal/strategy_decay_certifier.py`

### intelligence（3 件）

- `src/zephyr/intelligence/chain_impact_resolver.py`
- `src/zephyr/intelligence/chain_impact_stream.py`
- `src/zephyr/intelligence/news_chain_node_linker.py`

### trading（3 件）

- `src/zephyr/trading/action_dispatcher/_audit_log_writer.py`
- `src/zephyr/trading/action_dispatcher/_file_lifecycle_manager.py`
- `src/zephyr/trading/action_dispatcher/_search_replace_engine.py`

### gov_enforcement（2 件）

- `src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py`
- `src/zephyr/gov_enforcement/rule_enforcement/gate_engine/__init__.py`

### governance（2 件）

- `src/zephyr/governance/audit/pg_probe.py`
- `src/zephyr/governance/persistence/base_repo.py`

### factor（1 件）

- `src/zephyr/factor/analysis/factor_lifecycle_runner.py`

### pf_alloc（1 件）

- `src/zephyr/pf_alloc/core/maxdd_limit_allocator.py`

### shared（1 件）

- `src/zephyr/shared/io/paths.py`

## 块不可解析（零节点）（5 件）

报因：`block unparsable (no nodes)`
派工：逐件诊断块形，能补则补、该删则删（须作者确认）

### ex_core（2 件）

- `src/zephyr/ex_core/risk_layer_orchestrator.py`
- `src/zephyr/ex_core/trading_session.py`

### governance（1 件）

- `src/zephyr/governance/lifecycle_governance/drift_observatory_orchestrator.py`

### regime（1 件）

- `src/zephyr/regime/validation/wyckoff_walkforward.py`

### risk（1 件）

- `src/zephyr/risk/core/drawdown_tracker.py`

## 可机械出仓（0 件，非欠账，登记防漏）

（无）

## 其他报因（0 件，逐件诊断）

（无）
