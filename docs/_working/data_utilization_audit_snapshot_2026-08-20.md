---
ttl: task_bound
---

# Data Utilization Audit Snapshot (memo 63 continuous validation)

- date: 2026-08-20
- script: scripts/audit_data_utilization.ps1
- registry: docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml
- scope: src/zephyr (*.py) + design_memos (*.md, memo 63 self excluded), word-boundary match
- policy: warn-only, exit 0 (memo 63 section 9: no blocking gate)

## Summary

| metric | value |
|---|---|
| dataset entries parsed | 104 |
| unique tables | 104 |
| covered (src>0 and memo>0) | 37 |
| code_only / doc gap (src>0, memo=0) | 7 |
| doc_only / planned only (src=0, memo>0) | 0 |
| zero_ref / idle candidate | 60 |

## Matrix

| dataset_id | entity_name | table | src_refs | memo_refs | status |
|---|---|---|---|---|---|
| DS-001 | market_data.tick | tick | 448 | 105 | covered |
| DS-002 | market_data.ohlc_bar | ohlc_bar | 0 | 0 | zero_ref |
| DS-003 | factor.value_factor | value_factor | 4 | 2 | covered |
| DS-004 | factor.momentum_20d | momentum_20d | 20 | 0 | code_only |
| DS-005 | signal.composite | composite | 36 | 16 | covered |
| DS-006 | risk.limits | limits | 56 | 14 | covered |
| DS-007 | order.target | target | 1634 | 42 | covered |
| DS-008 | fill.executed | executed | 34 | 0 | code_only |
| DS-009 | position.snapshot | snapshot | 496 | 14 | covered |
| DS-010 | backtest.result | result | 5313 | 11 | covered |
| DS-011 | backtest.tick_event | tick_event | 2 | 0 | code_only |
| DS-012 | backtest.target_weights | target_weights | 133 | 0 | code_only |
| DS-013 | backtest.fills | fills | 68 | 23 | covered |
| DS-014 | backtest.nav_series | nav_series | 46 | 0 | code_only |
| DS-015 | factor.ashare_alpha87 | ashare_alpha87 | 0 | 0 | zero_ref |
| DS-016 | factor.ashare_capital_flow | ashare_capital_flow | 0 | 0 | zero_ref |
| DS-017 | factor.ashare_cross_market | ashare_cross_market | 0 | 0 | zero_ref |
| DS-018 | factor.ashare_fundamental | ashare_fundamental | 0 | 0 | zero_ref |
| DS-019 | factor.ashare_institutional | ashare_institutional | 0 | 0 | zero_ref |
| DS-020 | factor.ashare_intraday | ashare_intraday | 0 | 0 | zero_ref |
| DS-021 | factor.ashare_irl | ashare_irl | 0 | 0 | zero_ref |
| DS-022 | factor.ashare_market_structure | ashare_market_structure | 0 | 0 | zero_ref |
| DS-023 | factor.ashare_microstructure | ashare_microstructure | 0 | 0 | zero_ref |
| DS-024 | factor.ashare_pattern_signal | ashare_pattern_signal | 0 | 0 | zero_ref |
| DS-025 | factor.ashare_ps_liquidity | ashare_ps_liquidity | 0 | 0 | zero_ref |
| DS-026 | factor.ashare_sector | ashare_sector | 0 | 0 | zero_ref |
| DS-027 | factor.ashare_smc | ashare_smc | 0 | 0 | zero_ref |
| DS-028 | factor.ashare_technical_indicator | ashare_technical_indicator | 0 | 0 | zero_ref |
| DS-029 | factor_analysis.correlation_analyzer | correlation_analyzer | 4 | 5 | covered |
| DS-030 | factor_analysis.correlation_dedup | correlation_dedup | 3 | 7 | covered |
| DS-031 | factor_analysis.decay_monitor | decay_monitor | 14 | 13 | covered |
| DS-032 | factor_analysis.factor_attribution | factor_attribution | 4 | 6 | covered |
| DS-033 | factor_analysis.factor_optimization | factor_optimization | 9 | 3 | covered |
| DS-034 | factor_analysis.ic_decay | ic_decay | 20 | 8 | covered |
| DS-035 | factor_analysis.ic_ir_calc | ic_ir_calc | 6 | 3 | covered |
| DS-036 | factor_analysis.ic_ir_evaluator | ic_ir_evaluator | 5 | 3 | covered |
| DS-037 | factor_analysis.layered_backtest | layered_backtest | 8 | 3 | covered |
| DS-038 | factor_analysis.multifactor_synthesis | multifactor_synthesis | 18 | 5 | covered |
| DS-039 | factor_analysis.three_level_judgment | three_level_judgment | 5 | 5 | covered |
| DS-040 | factor_analysis.turnover_analyzer | turnover_analyzer | 0 | 0 | zero_ref |
| DS-041 | factor.barra_esg | barra_esg | 0 | 0 | zero_ref |
| DS-042 | factor.barra_exposure_calculator | barra_exposure_calculator | 0 | 0 | zero_ref |
| DS-043 | factor.barra_risk_budget_allocator | barra_risk_budget_allocator | 0 | 0 | zero_ref |
| DS-044 | factor.barra_risk_model | barra_risk_model | 0 | 0 | zero_ref |
| DS-045 | factor_mining.causal_validator | causal_validator | 0 | 0 | zero_ref |
| DS-046 | factor_mining.mining_agent | mining_agent | 0 | 0 | zero_ref |
| DS-047 | backtest.anomaly_diagnoser_result | anomaly_diagnoser_result | 0 | 0 | zero_ref |
| DS-048 | backtest.data_quality_checker_result | data_quality_checker_result | 0 | 0 | zero_ref |
| DS-049 | backtest.decay_monitor_result | decay_monitor_result | 0 | 0 | zero_ref |
| DS-050 | backtest.nan_processor_result | nan_processor_result | 0 | 0 | zero_ref |
| DS-051 | backtest.param_analyzer_result | param_analyzer_result | 0 | 0 | zero_ref |
| DS-052 | backtest.report_generator_result | report_generator_result | 0 | 0 | zero_ref |
| DS-053 | backtest.result_comparator_result | result_comparator_result | 0 | 0 | zero_ref |
| DS-054 | backtest.result_deployer_result | result_deployer_result | 0 | 0 | zero_ref |
| DS-055 | data.feature_store | feature_store | 0 | 0 | zero_ref |
| DS-056 | data.realtime_push_manager | realtime_push_manager | 0 | 0 | zero_ref |
| DS-057 | data.tick_data_manager | tick_data_manager | 0 | 0 | zero_ref |
| DS-058 | data.kline_resampler | kline_resampler | 5 | 6 | covered |
| DS-059 | data.sector_snapshot_collector | sector_snapshot_collector | 5 | 8 | covered |
| DS-060 | data_eng.data_lake_manager | data_lake_manager | 0 | 0 | zero_ref |
| DS-061 | data_eng.knowledge_cleaning | knowledge_cleaning | 0 | 0 | zero_ref |
| DS-062 | data_eng.stream_processing | stream_processing | 0 | 0 | zero_ref |
| DS-063 | data_eng.synthetic_data | synthetic_data | 0 | 0 | zero_ref |
| DS-064 | data_eng.training_data_manager | training_data_manager | 0 | 0 | zero_ref |
| DS-065 | execution.audit_journal | audit_journal | 16 | 2 | covered |
| DS-066 | execution.fill_handler | fill_handler | 12 | 5 | covered |
| DS-067 | execution.position_tracker | position_tracker | 38 | 0 | code_only |
| DS-068 | execution.live_portfolio | live_portfolio | 0 | 0 | zero_ref |
| DS-069 | portfolio.optimizer | optimizer | 13 | 1 | covered |
| DS-070 | portfolio.portfolio_aggregate | portfolio_aggregate | 0 | 0 | zero_ref |
| DS-071 | portfolio.strategy_runner | strategy_runner | 9 | 1 | covered |
| DS-072 | portfolio.topn_momentum_strategy | topn_momentum_strategy | 1 | 1 | covered |
| DS-073 | ml.ai_operator_decisions | ai_operator_decisions | 0 | 0 | zero_ref |
| DS-074 | ml.training_dataset | training_dataset | 0 | 0 | zero_ref |
| DS-075 | risk.drawdown_metric | drawdown_metric | 0 | 0 | zero_ref |
| DS-076 | trading.pnl | pnl | 44 | 28 | covered |
| DS-077 | market_data.renko | renko | 0 | 0 | zero_ref |
| DS-078 | market_data.point_figure | point_figure | 0 | 0 | zero_ref |
| DS-079 | market_data.kagi | kagi | 0 | 0 | zero_ref |
| DS-080 | market_data.lhb_detail | lhb_detail | 0 | 0 | zero_ref |
| DS-081 | meta.stock_basic | stock_basic | 7 | 5 | covered |
| DS-082 | market_data.stk_limit | stk_limit | 10 | 7 | covered |
| DS-083 | market_data.suspend | suspend | 9 | 0 | code_only |
| DS-084 | meta.index_member | index_member | 3 | 1 | covered |
| DS-085 | meta.st_status | st_status | 0 | 0 | zero_ref |
| DS-086 | fundamental.daily_basic | daily_basic | 0 | 0 | zero_ref |
| DS-087 | fundamental.fin_income | fin_income | 0 | 0 | zero_ref |
| DS-088 | fundamental.fin_balancesheet | fin_balancesheet | 0 | 0 | zero_ref |
| DS-089 | fundamental.fin_cashflow | fin_cashflow | 0 | 0 | zero_ref |
| DS-090 | fundamental.fin_indicator | fin_indicator | 0 | 0 | zero_ref |
| DS-091 | event.disclosure_date | disclosure_date | 0 | 0 | zero_ref |
| DS-092 | event.fin_forecast | fin_forecast | 0 | 0 | zero_ref |
| DS-093 | event.fin_express | fin_express | 0 | 0 | zero_ref |
| DS-094 | event.dividend | dividend | 6 | 3 | covered |
| DS-095 | event.share_float | share_float | 0 | 0 | zero_ref |
| DS-096 | event.holder_trade | holder_trade | 0 | 0 | zero_ref |
| DS-097 | event.repurchase | repurchase | 6 | 1 | covered |
| DS-098 | capital.margin | margin | 23 | 6 | covered |
| DS-099 | capital.hk_hold | hk_hold | 8 | 16 | covered |
| DS-100 | capital.moneyflow | moneyflow | 2 | 4 | covered |
| DS-101 | macro.cn_macro | cn_macro | 0 | 0 | zero_ref |
| DS-102 | industry.sw_daily | sw_daily | 0 | 0 | zero_ref |
| DS-103 | market_data.northbound_hold_snapshot | northbound_hold_snapshot | 3 | 6 | covered |
| DS-104 | event.news_data | news_data | 26 | 31 | covered |
