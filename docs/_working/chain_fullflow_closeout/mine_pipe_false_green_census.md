---
ttl: task_bound
---

# M3 · 假绿灯全量普查清单（270 任务全扫 · 2026-09-26）

- 判据：任务态=task_runs 最近一次记录（SQLite mode=ro）；落库真值=CH 实测 count()/max(date_col)（DatabaseService reader Client，抛错单列 PROBE_INCONCLUSIVE，禁与 0 行混读）。
- 复现命令：`python .runtime/tmp/mine_dossiers_20260926/false_green_census.py`（全只读；原始机读件 census.json 同目录）。
- 新鲜度基准实测：trade_calendar max(is_open=1, <=today) = 2026-09-24（09-25 中秋休市，缺席≠断更）。
- 近 30h 全库状态分布（task_runs, started_at>=2026-09-25）：{"FAILED": 36, "RUNNING": 4, "STALE": 1, "SUCCESS": 1859}
- 判定分布：{"GREEN_WITH_DATA": 226, "NOT_GREEN": 25, "NO_TARGET_TABLE": 4, "FALSE_GREEN": 5, "NEVER_RUN": 10}

## 0. 命中摘要

- **FALSE_GREEN（SUCCESS 但目标表 0 行）= 5**：realtime_snapshot_incremental / etf_benchmark_refresh / suspend_status_premarket / suspend_status_postclose / suspend_status_derive_weekend。
- **不可分辨集合（SUCCESS+0 行+fetched=0+written=0，与"合法 no-op/从没跑成"同读数）= 4**：etf_benchmark_refresh / suspend 三腿。
- NEVER_RUN=10、NO_TARGET_TABLE=4、NOT_GREEN=25、GREEN_WITH_DATA=226、PROBE_INCONCLUSIVE=0。
- 值级假绿补充（表非空但内容冻结/异常，行数判不出）：news_sentiment_score（打分腿无排产面，见主案卷 #28）、restricted_shares max=2035-10-29（前瞻数据污染新鲜度尺）、consensus_daily / financial_derived / market_pattern_win_rate（FAILED 面已入 NOT_GREEN）。

## 1. 全量清单（270 行）

| task_id | 最近态@UTC | 目标表 | 实测行数 | 最新数据日 | 判定 | 备注(last_error 截断) |
|---|---|---|---|---|---|---|

| a50_futures_daily_incremental | SUCCESS@2026-09-25T00:34:00+00:00 | c1_market.a50_futures_daily | 2615 | 2026-09-25 | GREEN_WITH_DATA |  |
| adj_factor_incremental | SUCCESS@2026-09-24T08:30:00+00:00 | c1_market.adj_factor | 21055072 | 2026-09-24 | GREEN_WITH_DATA |  |
| agri_wholesale_index_refresh | SUCCESS@2026-09-24T10:00:02+00:00 | c1_market.agri_wholesale_index | 11616 | 2026-09-24 | GREEN_WITH_DATA |  |
| alt_fx_ecb_daily_incremental | SUCCESS@2026-09-25T15:35:01+00:00 | c1_market.alt_fx_rate_ecb | 84 | 2026-09-25 | GREEN_WITH_DATA |  |
| alt_regime_signal_refresh | SUCCESS@2026-09-24T11:08:17+00:00 | c1_market.alt_regime_signal | 20546 | - | GREEN_WITH_DATA |  |
| alt_shipping_index_full_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_shipping_index | 31992 | - | GREEN_WITH_DATA |  |
| alt_shipping_index_incremental | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_shipping_index | 31992 | 2026-09-24 | GREEN_WITH_DATA |  |
| alt_stock_comment_snapshot | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_stock_comment | 51976 | - | GREEN_WITH_DATA |  |
| alt_sz_air_quality_daily_incremental | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_sz_air_quality_daily | 54244 | 2026-09-22 | GREEN_WITH_DATA |  |
| alt_sz_air_quality_region_incremental | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_sz_air_quality_region | 52730 | 2026-09-23 | GREEN_WITH_DATA |  |
| alt_sz_climate_hist_refresh | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_sz_climate_hist | 878953 | - | GREEN_WITH_DATA |  |
| alt_sz_enterprise_year_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_sz_enterprise_year | 44 | - | GREEN_WITH_DATA |  |
| alt_sz_env_meteor_refresh | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_sz_env_meteor | 27882 | - | GREEN_WITH_DATA |  |
| alt_sz_ground_obs_incremental | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_sz_ground_obs | 790355 | 2026-09-24 | GREEN_WITH_DATA |  |
| alt_sz_house_area_incremental | SUCCESS@2026-09-24T11:00:00+00:00 | c1_market.alt_sz_house_area | 59200 | 2026-09-22 | GREEN_WITH_DATA |  |
| alt_sz_house_daily_incremental | SUCCESS@2026-09-24T11:00:24+00:00 | c1_market.alt_sz_house_daily | 436317 | 2026-09-23 | GREEN_WITH_DATA |  |
| alt_sz_house_listing_refresh | SUCCESS@2026-09-24T11:00:28+00:00 | c1_market.alt_sz_house_listing | 1204291 | - | GREEN_WITH_DATA |  |
| alt_sz_house_presale_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_sz_house_presale | 4314 | - | GREEN_WITH_DATA |  |
| alt_sz_marine_forecast_incremental | SUCCESS@2026-09-24T11:00:47+00:00 | c1_market.alt_sz_marine_forecast | 295887 | 2026-09-24 | GREEN_WITH_DATA |  |
| alt_sz_market_subject_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_sz_market_subject | 22 | - | GREEN_WITH_DATA |  |
| alt_sz_port_monthly_refresh | SUCCESS@2026-09-24T11:00:49+00:00 | c1_market.alt_sz_port_monthly | 1168 | - | GREEN_WITH_DATA |  |
| alt_sz_reservoir_level_incremental | SUCCESS@2026-09-24T11:00:49+00:00 | c1_market.alt_sz_reservoir_level | 75463972 | 2026-07-31 | GREEN_WITH_DATA |  |
| alt_sz_reservoir_rain_day_refresh | SUCCESS@2026-09-24T11:00:56+00:00 | c1_market.alt_sz_reservoir_rain_day | 572158 | - | GREEN_WITH_DATA |  |
| alt_sz_reservoir_rain_month_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_sz_reservoir_rain_month | 27482 | - | GREEN_WITH_DATA |  |
| alt_sz_reservoir_station_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_sz_reservoir_station | 970 | - | GREEN_WITH_DATA |  |
| alt_sz_stat_analysis_refresh | SUCCESS@2026-09-24T11:01:33+00:00 | c1_market.alt_sz_stat_analysis | 7 | - | GREEN_WITH_DATA |  |
| alt_sz_stat_monthly_refresh | SUCCESS@2026-09-24T11:01:40+00:00 | c1_market.alt_sz_stat_monthly | 34064 | - | GREEN_WITH_DATA |  |
| alt_sz_visibility_incremental | SUCCESS@2026-09-24T11:02:18+00:00 | c1_market.alt_sz_visibility | 40857 | 2026-09-24 | GREEN_WITH_DATA |  |
| alt_sz_weather_warning_incremental | SUCCESS@2026-09-24T11:02:48+00:00 | c1_market.alt_sz_weather_warning | 18066 | 2026-09-22 | GREEN_WITH_DATA |  |
| alt_typhoon_landfall_history_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_typhoon_landfall_history | 845 | - | GREEN_WITH_DATA |  |
| alt_typhoon_names_refresh | SUCCESS@2026-09-20T19:00:00+00:00 | c1_market.alt_typhoon_names | 1260 | - | GREEN_WITH_DATA |  |
| alt_typhoon_track_full_refresh | SUCCESS@2026-09-20T19:00:02+00:00 | c1_market.alt_typhoon_track | 282434 | - | GREEN_WITH_DATA |  |
| alt_typhoon_track_incremental | SUCCESS@2026-09-24T11:02:59+00:00 | c1_market.alt_typhoon_track | 282434 | 2026-09-24 | GREEN_WITH_DATA |  |
| analyst_forecast_full_refresh | SUCCESS@2026-09-20T19:00:04+00:00 | c3_fundamental.analyst_forecast | 111543 | - | GREEN_WITH_DATA |  |
| analyst_forecast_incremental | SUCCESS@2026-09-24T11:03:44+00:00 | c3_fundamental.analyst_forecast | 111543 | 2026-09-24 | GREEN_WITH_DATA |  |
| anchored_state_build | SUCCESS@2026-09-24T08:43:18+00:00 | c1_backtest.regime_state_anchored | 4477 | 2026-09-24 | GREEN_WITH_DATA |  |
| auction_book_snapshot | SUCCESS@2026-09-24T01:25:50+00:00 | c1_market.auction_book | 3816492 | 2026-09-24 | GREEN_WITH_DATA |  |
| auction_data_snapshot | SUCCESS@2026-09-24T01:25:50+00:00 | c1_market.auction_snapshot | 272117 | 2026-09-24 | GREEN_WITH_DATA |  |
| audit_opinion_incremental | FAILED@2026-07-23T11:00:02+00:00 | c3_fundamental.audit_opinion | 96010 | 2026-05-29 | NOT_GREEN(FAILED) | AKShare 暂无专用审计意见接口，需通过财报接口间接获取 |
| balance_sheet_incremental | SUCCESS@2026-09-24T21:30:17+00:00 | c3_fundamental.balance_sheet | 339738 | 2026-09-02 | GREEN_WITH_DATA |  |
| block_trade_detail_full_refresh | SUCCESS@2026-09-20T19:00:04+00:00 | c1_market.block_trade_detail | 1629 | - | GREEN_WITH_DATA |  |
| block_trade_detail_incremental | SUCCESS@2026-09-24T10:00:02+00:00 | c1_market.block_trade_detail | 1629 | 2026-09-24 | GREEN_WITH_DATA |  |
| block_trade_incremental | SUCCESS@2026-09-24T10:00:02+00:00 | c1_market.block_trade | 1414 | 2026-09-24 | GREEN_WITH_DATA |  |
| block_trade_qmt_placeholder | FAILED@2026-07-12T10:04:16+00:00 | c1_market.block_trade_qmt | None | - | NO_TARGET_TABLE(table_missing_in_ch) | QMT无大宗交易接口，已由AKShare Provider覆盖（block_trade_incremental） |
| calendar_event_refresh | SUCCESS@2026-09-03T11:35:13+00:00 | c1_market.calendar_event | 797 | - | GREEN_WITH_DATA |  |
| cashflow_statement_incremental | SUCCESS@2026-09-24T22:27:23+00:00 | c3_fundamental.cashflow_statement | 310447 | 2026-09-02 | GREEN_WITH_DATA |  |
| cb_premium_median_daily | SUCCESS@2026-09-24T11:03:48+00:00 | c1_market.sentiment_panel | 31 | 2026-09-24 | GREEN_WITH_DATA |  |
| cffex_member_ranking_refresh | DEFERRED_PERSISTENCE@2026-09-24T23:21:25+00:00 | c1_market.market_cffex_member_ranking | 6369 | 2026-09-18 | NOT_GREEN(DEFERRED_PERSISTENCE) | 数据已本地持久化，待回灌: c1_market.market_cffex_member_ranking |
| china_bond_yield_refresh | SUCCESS@2026-09-24T10:00:02+00:00 | c1_market.market_china_bond_yield | 6024 | 2026-09-24 | GREEN_WITH_DATA |  |
| cohort_ledger_daily | SUCCESS@2026-09-24T23:24:16+00:00 | c1_backtest.cohort_daily_ledger | 180 | 2026-09-24 | GREEN_WITH_DATA |  |
| commodity_futures_main_full_refresh | SUCCESS@2026-09-20T19:00:06+00:00 | c1_market.commodity_futures_main | 171 | - | GREEN_WITH_DATA |  |
| commodity_futures_main_refresh | SUCCESS@2026-09-24T11:03:49+00:00 | c1_market.commodity_futures_main | 171 | 2026-09-24 | GREEN_WITH_DATA |  |
| commodity_spot_price_full_refresh | SUCCESS@2026-09-20T19:00:07+00:00 | c1_market.commodity_spot_price | 1026 | - | GREEN_WITH_DATA |  |
| commodity_spot_price_refresh | SUCCESS@2026-09-24T11:03:51+00:00 | c1_market.commodity_spot_price | 1026 | 2026-09-24 | GREEN_WITH_DATA |  |
| concept_board_refresh | SUCCESS@2026-09-24T10:00:02+00:00 | c1_market.concept_board | 375 | - | GREEN_WITH_DATA |  |
| concept_sector_refresh | SUCCESS@2026-09-02T16:59:31+00:00 | c1_market.concept_sector | 375 | - | GREEN_WITH_DATA |  |
| consensus_daily_build | FAILED@2026-09-18T22:30:20+00:00 | c3_fundamental.consensus_daily | 6797719 | 2026-09-14 | NOT_GREEN(FAILED) | '>' not supported between instances of 'str' and 'datetime.date' |
| convertible_bond_clause_refresh | SUCCESS@2026-09-24T10:00:02+00:00 | c1_market.market_convertible_bond_clause | 1589 | 2026-09-24 | GREEN_WITH_DATA |  |
| convertible_bond_iv_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.convertible_bond_iv | 10549 | 2026-09-24 | GREEN_WITH_DATA |  |
| convertible_bond_list_refresh | SUCCESS@2026-09-02T17:11:35+00:00 | c1_market.convertible_bond_list | 2102 | - | GREEN_WITH_DATA |  |
| crypto_fear_greed_incremental | SUCCESS@2026-09-24T11:04:10+00:00 | c1_market.sentiment_panel | 31 | 2026-09-24 | GREEN_WITH_DATA |  |
| crypto_kline_daily_incremental | SUCCESS@2026-09-25T00:41:00+00:00 | c1_market.crypto_kline_daily | 18570 | 2026-09-24 | GREEN_WITH_DATA |  |
| crypto_shadow_gate_daily | SUCCESS@2026-09-25T00:43:10+00:00 | c1_market.crypto_shadow_gate | 9 | 2026-09-24 | GREEN_WITH_DATA |  |
| daban_board_event_derive | SUCCESS@2026-09-22T11:09:29+00:00 | c1_market.daban_board_event | 2390 | 2026-09-22 | GREEN_WITH_DATA |  |
| daban_engine_load_daily | SUCCESS@2026-09-24T08:43:18+00:00 | c1_market.daban_engine_load | 1547 | 2026-09-22 | GREEN_WITH_DATA |  |
| daily_valuation_full_refresh | SUCCESS@2026-09-20T19:00:11+00:00 | c1_market.daily_valuation | 354679 | - | GREEN_WITH_DATA |  |
| daily_valuation_incremental | STALE@2026-09-24T09:38:29+00:00 | c1_market.daily_valuation | 354679 | 2026-09-24 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| disclosure_plan_incremental | SUCCESS@2026-09-24T11:04:13+00:00 | c3_fundamental.disclosure_plan | 305685 | 2026-08-31 | GREEN_WITH_DATA |  |
| dividend_incremental | SUCCESS@2026-09-09T11:00:00+00:00 | c3_fundamental.dividend | 191633 | 2026-09-22 | GREEN_WITH_DATA |  |
| dividend_incremental_akshare | SUCCESS@2026-09-21T21:30:10+00:00 | c3_fundamental.dividend | 191633 | 2026-09-22 | GREEN_WITH_DATA |  |
| dragon_tiger_incremental | SUCCESS@2026-09-24T10:00:02+00:00 | c1_market.dragon_tiger | 2143 | 2026-09-24 | GREEN_WITH_DATA |  |
| dragon_tiger_qmt_placeholder | FAILED@2026-07-12T10:04:17+00:00 | c1_market.dragon_tiger_qmt | None | - | NO_TARGET_TABLE(table_missing_in_ch) | QMT无龙虎榜接口，已由AKShare Provider覆盖（dragon_tiger_incremental） |
| dragon_tiger_seat_incremental | SUCCESS@2026-09-24T10:00:19+00:00 | c1_market.dragon_tiger_seat | 618963 | 2026-09-24 | GREEN_WITH_DATA |  |
| earnings_forecast_incremental | SUCCESS@2026-09-24T11:04:16+00:00 | c3_fundamental.earnings_forecast | 125582 | 2026-07-03 | GREEN_WITH_DATA |  |
| eia_full_refresh | SUCCESS@2026-09-20T19:00:13+00:00 | c1_market.macro_data | 50467 | - | GREEN_WITH_DATA |  |
| eia_petroleum_incremental | SUCCESS@2026-09-24T10:00:20+00:00 | c1_market.macro_data | 50467 | 2026-09-24 | GREEN_WITH_DATA |  |
| emotion_index_close_final | SUCCESS@2026-09-24T09:20:40+00:00 | c1_market.emotion_index | 8650 | 2026-09-24 | GREEN_WITH_DATA |  |
| emotion_index_pre_open | SUCCESS@2026-09-25T00:34:00+00:00 | c1_market.emotion_index | 8650 | 2026-09-24 | GREEN_WITH_DATA |  |
| equity_pledge_full_refresh | SUCCESS@2026-09-20T19:00:19+00:00 | c3_fundamental.equity_pledge_detail | 122922 | - | GREEN_WITH_DATA |  |
| equity_pledge_incremental | SUCCESS@2026-09-24T11:04:27+00:00 | c3_fundamental.equity_pledge_detail | 122922 | 2026-07-03 | GREEN_WITH_DATA |  |
| equity_pledge_summary_incremental | SUCCESS@2026-09-24T11:04:50+00:00 | c3_fundamental.equity_pledge_summary | 1723194 | 2026-09-18 | GREEN_WITH_DATA |  |
| etf_benchmark_refresh | SUCCESS@2026-09-24T21:30:10+00:00 | c1_market.etf_benchmark | 0 | - | FALSE_GREEN(SUCCESS但表0行) |  |
| etf_list_refresh | SUCCESS@2026-09-10T16:19:10+00:00 | c1_market.etf_list | 2184 | - | GREEN_WITH_DATA |  |
| etf_nav_full_refresh | SUCCESS@2026-09-20T19:00:24+00:00 | c1_market.etf_nav | 90389 | - | GREEN_WITH_DATA |  |
| etf_nav_refresh | SUCCESS@2026-09-24T08:30:00+00:00 | c1_market.etf_nav | 90389 | 2026-09-23 | GREEN_WITH_DATA |  |
| etf_share_snapshot_refresh | FAILED@2026-09-24T23:24:18+00:00 | c1_market.market_etf_share_snapshot | 1621 | 2026-09-18 | NOT_GREEN(FAILED) | fund_etf_spot_em 失败: ('Connection aborted.', RemoteDisconnected('Remot |
| ex_dividend_event_incremental | SUCCESS@2026-09-24T11:04:58+00:00 | c3_fundamental.ex_dividend_event | 57866 | 2026-09-24 | GREEN_WITH_DATA |  |
| express_report_incremental | SUCCESS@2026-09-24T11:05:18+00:00 | c3_fundamental.express_report | 28708 | 2026-07-02 | GREEN_WITH_DATA |  |
| factor_decay_monitor_weekly | None@None | - | None | - | NEVER_RUN(无task_runs记录) |  |
| financial_derived_build | FAILED@2026-09-24T23:26:42+00:00 | c3_fundamental.financial_derived | 306526 | 2026-09-02 | NOT_GREEN(FAILED) | '<' not supported between instances of 'str' and 'datetime.date' |
| financial_indicator_incremental | SUCCESS@2026-09-24T23:27:35+00:00 | c3_fundamental.financial_indicator | 386431 | 2026-09-12 | GREEN_WITH_DATA |  |
| futures_kline_qmt_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.futures_kline_qmt | 906 | 2026-09-16 | GREEN_WITH_DATA |  |
| futures_position_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.futures_position | 3458 | 2026-09-23 | GREEN_WITH_DATA |  |
| futures_term_structure_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.futures_term_structure | 3404 | 2026-09-23 | GREEN_WITH_DATA |  |
| futures_tick_intraday | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.tick_data | 8953170951 | 2026-09-24 | GREEN_WITH_DATA |  |
| futures_warehouse_receipt_backfill_czce | SUCCESS@2026-09-18T00:34:24+00:00 | c1_market.futures_warehouse_receipt | 2887725 | 2026-09-24 | GREEN_WITH_DATA |  |
| futures_warehouse_receipt_backfill_shfe | SUCCESS@2026-09-18T03:04:12+00:00 | c1_market.futures_warehouse_receipt | 2887725 | 2026-09-24 | GREEN_WITH_DATA |  |
| futures_warehouse_receipt_incremental | SUCCESS@2026-09-24T10:00:28+00:00 | c1_market.futures_warehouse_receipt | 2887725 | 2026-09-24 | GREEN_WITH_DATA |  |
| global_gold_daily_incremental | SUCCESS@2026-09-25T00:34:00+00:00 | c1_market.kline_global | 10007 | 2026-09-25 | GREEN_WITH_DATA |  |
| global_hsi_daily_incremental | None@None | c1_market.kline_global | 10007 | 2026-09-25 | NEVER_RUN(无task_runs记录) |  |
| global_kospi_daily_incremental | None@None | c1_market.kline_global | 10007 | 2026-09-25 | NEVER_RUN(无task_runs记录) |  |
| global_nikkei_daily_incremental | None@None | c1_market.kline_global | 10007 | 2026-09-25 | NEVER_RUN(无task_runs记录) |  |
| global_usdcnh_daily_incremental | None@None | c1_market.kline_global | 10007 | 2026-09-25 | NEVER_RUN(无task_runs记录) |  |
| global_wti_daily_incremental | SUCCESS@2026-09-25T00:34:00+00:00 | c1_market.kline_global | 10007 | 2026-09-25 | GREEN_WITH_DATA |  |
| hk_connect_flow_full | SUCCESS@2026-09-15T10:00:02+00:00 | c1_market.hk_connect_flow | 4052 | 2024-08-16 | GREEN_WITH_DATA |  |
| hk_connect_flow_incremental | SUCCESS@2026-09-15T10:00:02+00:00 | c1_market.hk_connect_flow | 4052 | - | GREEN_WITH_DATA |  |
| hk_kline_full_refresh | SUCCESS@2026-09-20T19:00:31+00:00 | c1_market.hk_kline | 6298 | - | GREEN_WITH_DATA |  |
| hk_kline_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.hk_kline | 6298 | 2026-09-16 | GREEN_WITH_DATA |  |
| hk_stock_list_refresh | SUCCESS@2026-09-02T16:59:41+00:00 | c1_market.hk_stock_list | 2798 | - | GREEN_WITH_DATA |  |
| hk_trade_calendar_refresh | SUCCESS@2026-09-16T21:30:44+00:00 | c1_market.hk_trade_calendar | 4607 | - | GREEN_WITH_DATA |  |
| hl_funding_history_incremental | SUCCESS@2026-09-25T00:41:00+00:00 | c1_market.hl_funding_history | 4705147 | 2026-09-25 | GREEN_WITH_DATA |  |
| hl_liquidation_capture | SUCCESS@2026-09-25T00:41:00+00:00 | c1_market.hl_liquidation_raw | 7 | 2026-09-25 | GREEN_WITH_DATA |  |
| hl_oi_snapshot_daily_refresh | SUCCESS@2026-09-25T00:41:00+00:00 | c1_market.hl_oi_snapshot_daily | 1638 | 2026-09-25 | GREEN_WITH_DATA |  |
| hl_perp_snapshot_daily_refresh | SUCCESS@2026-09-25T00:41:00+00:00 | c1_market.hl_perp_snapshot_daily | 1638 | 2026-09-25 | GREEN_WITH_DATA |  |
| hog_futures_core_full_refresh | SUCCESS@2026-09-20T19:00:31+00:00 | c1_market.hog_futures_core | 424 | - | GREEN_WITH_DATA |  |
| hog_futures_core_refresh | SUCCESS@2026-09-24T11:05:41+00:00 | c1_market.hog_futures_core | 424 | 2026-09-24 | GREEN_WITH_DATA |  |
| hog_province_spot_refresh | SUCCESS@2026-09-24T11:05:55+00:00 | c1_market.hog_province_spot | 1148 | - | GREEN_WITH_DATA |  |
| hog_spot_index_full_refresh | SUCCESS@2026-09-20T19:00:37+00:00 | c1_market.hog_spot_index | 585 | - | GREEN_WITH_DATA |  |
| hog_spot_index_refresh | SUCCESS@2026-09-24T11:06:03+00:00 | c1_market.hog_spot_index | 585 | 2026-09-21 | GREEN_WITH_DATA |  |
| income_statement_incremental | SUCCESS@2026-09-25T00:07:21+00:00 | c3_fundamental.income_statement | 346176 | 2026-09-02 | GREEN_WITH_DATA |  |
| index_adjustment_derive | SUCCESS@2026-09-17T21:47:13+00:00 | c1_market.index_adjustment | 14763 | 2026-09-14 | GREEN_WITH_DATA |  |
| index_constituent_refresh | SUCCESS@2026-09-03T11:35:14+00:00 | c1_market.index_constituent | 674232 | - | GREEN_WITH_DATA |  |
| index_list_refresh | SUCCESS@2026-09-10T15:05:25+00:00 | c1_market.index_list | 9700 | - | GREEN_WITH_DATA |  |
| index_member_postclose | STALE@2026-09-24T10:00:53+00:00 | c1_market.index_constituent | 674232 | 2026-09-23 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| index_member_premarket | SUCCESS@2026-09-24T00:34:00+00:00 | c1_market.index_constituent | 674232 | 2026-09-23 | GREEN_WITH_DATA |  |
| index_quote_snapshot | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.index_quote | 238951 | 2026-09-24 | GREEN_WITH_DATA |  |
| index_valuation_daily_backfill | SUCCESS@2026-09-20T19:00:38+00:00 | c1_market.index_valuation_daily | 8126 | - | GREEN_WITH_DATA |  |
| index_valuation_daily_compute_after_ingest | SUCCESS@2026-09-20T19:10:14+00:00 | c1_market.index_valuation_daily | 8126 | 2026-09-23 | GREEN_WITH_DATA |  |
| index_valuation_daily_compute_daily | SUCCESS@2026-09-24T08:43:42+00:00 | c1_market.index_valuation_daily | 8126 | 2026-09-23 | GREEN_WITH_DATA |  |
| index_valuation_daily_incremental | SUCCESS@2026-09-24T08:43:26+00:00 | c1_market.index_valuation_daily | 8126 | 2026-09-23 | GREEN_WITH_DATA |  |
| index_weight_refresh | SUCCESS@2026-09-02T17:02:43+00:00 | c1_market.index_weight | 1850 | - | GREEN_WITH_DATA |  |
| industry_class_refresh | SUCCESS@2026-09-20T19:00:44+00:00 | c1_market.industry_class | 46228 | - | GREEN_WITH_DATA |  |
| industry_class_suppl_refresh | SUCCESS@2026-09-03T11:35:15+00:00 | c3_fundamental.industry_class_suppl | 10141 | - | GREEN_WITH_DATA |  |
| ipo_calendar_daily | SUCCESS@2026-09-24T10:01:13+00:00 | c1_market.ipo_calendar | 9202 | 2026-09-24 | GREEN_WITH_DATA |  |
| ir_activity_record_refresh | None@None | c3_fundamental.ir_activity_record | 30 | 2026-09-18 | NEVER_RUN(无task_runs记录) |  |
| irm_interactive_qa_refresh | None@None | c3_fundamental.irm_interactive_qa | 500 | 2026-09-16 | NEVER_RUN(无task_runs记录) |  |
| kline_15min_incremental | SUCCESS@2026-09-24T07:40:01+00:00 | c1_market.kline_15min | 98554570 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_1min_incremental | SUCCESS@2026-09-24T07:40:01+00:00 | c1_market.kline_1min | 1486013551 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_30min_incremental | SUCCESS@2026-09-24T07:40:01+00:00 | c1_market.kline_30min | 49162491 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_5min_history_backfill | None@None | c1_market.kline_5min | 294949599 | - | NEVER_RUN(无task_runs记录) |  |
| kline_5min_incremental | SUCCESS@2026-09-24T07:40:02+00:00 | c1_market.kline_5min | 294949599 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_60min_incremental | SUCCESS@2026-09-24T07:40:02+00:00 | c1_market.kline_60min | 24637280 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_cb_full_refresh | SUCCESS@2026-09-20T19:00:46+00:00 | c1_market.kline_cb | 245849 | - | GREEN_WITH_DATA |  |
| kline_cb_incremental | SUCCESS@2026-09-24T08:30:00+00:00 | c1_market.kline_cb | 245849 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_daily_delisted_backfill | SUCCESS@2026-09-03T11:38:04+00:00 | c1_market.kline_daily | 10108162 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_daily_full_refresh | SUCCESS@2026-09-20T19:01:06+00:00 | c1_market.kline_daily | 10108162 | - | GREEN_WITH_DATA |  |
| kline_daily_hfq_incremental | SUCCESS@2026-09-24T09:01:25+00:00 | c1_market.kline_daily_hfq | 10079242 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_daily_incremental | SUCCESS@2026-09-24T08:30:00+00:00 | c1_market.kline_daily | 10108162 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_etf_15min_incremental | SUCCESS@2026-09-24T07:40:02+00:00 | c1_market.kline_etf_15min | 18964518 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_etf_1min_incremental | SUCCESS@2026-09-24T07:40:03+00:00 | c1_market.kline_etf_1min | 290394600 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_etf_30min_incremental | SUCCESS@2026-09-24T07:40:03+00:00 | c1_market.kline_etf_30min | 11971700 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_etf_5min_incremental | SUCCESS@2026-09-24T08:05:06+00:00 | c1_market.kline_etf_5min | 72475381 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_etf_60min_incremental | SUCCESS@2026-09-24T08:08:33+00:00 | c1_market.kline_etf_60min | 6093724 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_etf_daily_incremental | SUCCESS@2026-09-24T08:30:01+00:00 | c1_market.kline_etf_daily | 103831 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_futures_full | SUCCESS@2026-09-20T19:01:13+00:00 | c1_market.kline_futures | 8274 | 2026-09-18 | GREEN_WITH_DATA |  |
| kline_futures_incremental | SUCCESS@2026-09-24T10:01:40+00:00 | c1_market.kline_futures | 8274 | 2026-09-18 | GREEN_WITH_DATA |  |
| kline_hk_daily_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.kline_hk_daily | 200768 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_index_calc_refresh | SUCCESS@2026-09-24T09:20:40+00:00 | c1_market.kline_index_calc | 3669 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_index_incremental | SUCCESS@2026-09-24T08:30:03+00:00 | c1_market.kline_index | 3101186 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_lof_15min_incremental | SUCCESS@2026-09-24T08:08:34+00:00 | c1_market.kline_lof_15min | 12461208 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_lof_1min_incremental | SUCCESS@2026-09-24T08:20:13+00:00 | c1_market.kline_lof_1min | 139240903 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_lof_30min_incremental | SUCCESS@2026-09-24T08:25:02+00:00 | c1_market.kline_lof_30min | 6198722 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_lof_5min_incremental | SUCCESS@2026-09-24T08:29:42+00:00 | c1_market.kline_lof_5min | 37423834 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_lof_60min_incremental | SUCCESS@2026-09-24T08:30:02+00:00 | c1_market.kline_lof_60min | 3117350 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_monthly_hfq_incremental | SUCCESS@2026-09-24T08:45:33+00:00 | c1_market.kline_monthly_hfq | 502496 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_monthly_incremental | SUCCESS@2026-09-08T19:46:15+00:00 | c1_market.kline_monthly | 470601 | 2026-09-15 | GREEN_WITH_DATA |  |
| kline_sector_15min_incremental | STALE@2026-09-10T07:15:00+00:00 | c1_market.kline_sector_intraday | 10436356 | 2026-09-22 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| kline_sector_1min_incremental | STALE@2026-09-10T07:15:00+00:00 | c1_market.kline_sector_intraday | 10436356 | 2026-09-22 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| kline_sector_30min_incremental | STALE@2026-09-10T07:15:00+00:00 | c1_market.kline_sector_intraday | 10436356 | 2026-09-22 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| kline_sector_5min_incremental | STALE@2026-09-10T07:15:00+00:00 | c1_market.kline_sector_intraday | 10436356 | 2026-09-22 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| kline_sector_60min_incremental | STALE@2026-09-10T07:15:00+00:00 | c1_market.kline_sector_intraday | 10436356 | 2026-09-22 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| kline_sector_880_incremental | SUCCESS@2026-09-24T08:30:03+00:00 | c1_market.kline_sector_880 | 761860 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_sector_880_resample | SUCCESS@2026-09-24T08:35:33+00:00 | c1_market.kline_sector_880 | 761860 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_sector_incremental | SUCCESS@2026-09-24T08:35:36+00:00 | c1_market.kline_sector | 97574 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_us_daily_full_refresh | SUCCESS@2026-09-20T19:01:22+00:00 | c1_market.kline_us_daily | 594 | - | GREEN_WITH_DATA |  |
| kline_us_daily_incremental | SUCCESS@2026-09-24T10:01:46+00:00 | c1_market.kline_us_daily | 594 | 2026-09-23 | GREEN_WITH_DATA |  |
| kline_us_daily_qmt_incremental | None@None | c1_market.kline_us_daily | 594 | 2026-09-23 | NEVER_RUN(无task_runs记录) |  |
| kline_weekly_hfq_incremental | SUCCESS@2026-09-24T08:45:33+00:00 | c1_market.kline_weekly_hfq | 2127400 | 2026-09-24 | GREEN_WITH_DATA |  |
| kline_weekly_incremental | SUCCESS@2026-09-08T19:51:25+00:00 | c1_market.kline_weekly | 1814491 | 2026-09-15 | GREEN_WITH_DATA |  |
| l2_tick_snapshot | FAILED@2026-07-22T07:55:00+00:00 | c1_market.l2_tick | 0 | ALL_NULL | NOT_GREEN(FAILED) | 未知 capability: tick_snapshot |
| limit_up_down_full_refresh | SUCCESS@2026-09-20T19:01:32+00:00 | c1_market.limit_up_down | 4991 | - | GREEN_WITH_DATA |  |
| limit_up_down_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.limit_up_down | 4991 | 2026-09-24 | GREEN_WITH_DATA |  |
| limit_up_pool_incremental | SUCCESS@2026-09-24T10:01:59+00:00 | c1_market.limit_up_pool | 1077 | 2026-09-24 | GREEN_WITH_DATA |  |
| lof_list_refresh | SUCCESS@2026-09-03T11:38:34+00:00 | c1_market.lof_list | 371 | - | GREEN_WITH_DATA |  |
| macro_activity_gauge_refresh | SUCCESS@2026-09-24T11:06:21+00:00 | c1_market.macro_activity_gauge | 433 | 2026-08-31 | GREEN_WITH_DATA |  |
| macro_credit_money_refresh | SUCCESS@2026-09-24T11:06:29+00:00 | c1_market.macro_credit_money | 584 | 2026-08-31 | GREEN_WITH_DATA |  |
| macro_daily_gauge_refresh | SUCCESS@2026-09-24T10:02:07+00:00 | c1_market.macro_daily_gauge | 4674 | 2026-09-24 | GREEN_WITH_DATA |  |
| macro_data_full_refresh | SUCCESS@2026-09-20T19:01:33+00:00 | c1_market.macro_data | 50467 | - | GREEN_WITH_DATA |  |
| macro_data_incremental | RUNNING@2026-09-25T18:21:00+00:00 | c1_market.macro_data | 50467 | 2026-09-24 | NOT_GREEN(RUNNING) |  |
| macro_fred_full_refresh | SUCCESS@2026-09-20T19:02:00+00:00 | c1_market.macro_data | 50467 | 2026-09-24 | GREEN_WITH_DATA |  |
| macro_fred_incremental | SUCCESS@2026-09-25T18:21:01+00:00 | c1_market.macro_data | 50467 | 2026-09-24 | GREEN_WITH_DATA |  |
| macro_pmi_gauge_refresh | SUCCESS@2026-09-24T11:07:26+00:00 | c1_market.macro_pmi_gauge | 224 | 2026-08-31 | GREEN_WITH_DATA |  |
| macro_price_gauge_refresh | SUCCESS@2026-09-24T11:07:38+00:00 | c1_market.macro_price_gauge | 493 | 2026-08-31 | GREEN_WITH_DATA |  |
| macro_trade_gauge_refresh | SUCCESS@2026-09-24T11:07:51+00:00 | c1_market.macro_trade_gauge | 224 | 2026-08-31 | GREEN_WITH_DATA |  |
| macro_worldbank_full_refresh | SUCCESS@2026-09-20T19:02:37+00:00 | c1_market.macro_data | 50467 | 2026-09-24 | GREEN_WITH_DATA |  |
| main_business_incremental | SUCCESS@2026-09-25T00:45:40+00:00 | c3_fundamental.main_business | 2094453 | 2026-03-31 | GREEN_WITH_DATA |  |
| margin_trading_incremental | SUCCESS@2026-09-24T19:56:15+00:00 | c1_market.margin_trading | 2082279 | 2026-09-23 | GREEN_WITH_DATA |  |
| margin_trading_qmt_placeholder | FAILED@2026-07-12T10:05:20+00:00 | c1_market.margin_trading_qmt | None | - | NO_TARGET_TABLE(table_missing_in_ch) | QMT无融资融券接口，已由AKShare Provider覆盖（margin_trading_incremental） |
| market_breadth_snapshot_minute | SUCCESS@2026-09-24T08:36:07+00:00 | c1_market.market_breadth_snapshot | 151 | 2026-09-24 | GREEN_WITH_DATA |  |
| market_fund_flow_refresh | SUCCESS@2026-09-24T10:02:11+00:00 | c1_market.market_fund_flow_daily | 125 | 2026-09-24 | GREEN_WITH_DATA |  |
| money_flow_full_refresh | SUCCESS@2026-09-20T19:03:15+00:00 | c1_market.money_flow | 6043127 | - | GREEN_WITH_DATA |  |
| money_flow_incremental | SUCCESS@2026-09-24T10:02:18+00:00 | c1_market.money_flow | 6043127 | 2026-09-24 | GREEN_WITH_DATA |  |
| ndrc_fuel_price_refresh | SUCCESS@2026-09-24T10:02:44+00:00 | c1_market.ndrc_fuel_price | 330 | 2026-09-25 | GREEN_WITH_DATA |  |
| news_baidu_incremental | SUCCESS@2026-09-25T18:21:01+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_cctv_incremental | SUCCESS@2026-09-25T18:21:01+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_cls_incremental | SUCCESS@2026-09-25T18:21:02+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_data_incremental | SUCCESS@2026-09-25T18:21:03+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_eastmoney_incremental | SUCCESS@2026-09-25T18:21:03+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_economic_baidu_incremental | SUCCESS@2026-09-25T18:21:03+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_rss_incremental | SUCCESS@2026-09-25T18:21:06+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_stock_em_incremental | SUCCESS@2026-09-25T14:17:00+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_stock_incremental | SUCCESS@2026-09-25T18:21:07+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | GREEN_WITH_DATA |  |
| news_tushare_incremental | FAILED@2026-07-13T02:07:25+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | NOT_GREEN(FAILED) | 请指定正确的接口名 |
| northbound_hold_snapshot_refresh | SUCCESS@2026-09-25T01:24:11+00:00 | c1_market.northbound_hold_snapshot | 57083 | - | GREEN_WITH_DATA |  |
| option_daily_stats_daily | SUCCESS@2026-09-23T08:30:06+00:00 | c1_market.option_daily_stats | 11688 | 2026-09-22 | GREEN_WITH_DATA |  |
| option_greeks_incremental | SUCCESS@2026-09-24T07:40:00+00:00 | c1_market.option_greeks | 4706 | 2026-09-23 | GREEN_WITH_DATA |  |
| option_iv_surface_incremental | SUCCESS@2026-09-24T07:40:01+00:00 | c1_market.option_iv_surface | 30296 | 2026-09-23 | GREEN_WITH_DATA |  |
| option_kline_full_refresh | SUCCESS@2026-09-20T19:03:43+00:00 | c1_market.option_kline | 7734 | - | GREEN_WITH_DATA |  |
| option_kline_incremental | SUCCESS@2026-09-24T08:30:09+00:00 | c1_market.option_kline | 7734 | 2026-09-24 | GREEN_WITH_DATA |  |
| pattern_event_incremental | SUCCESS@2026-09-24T09:20:40+00:00 | c1_market.market_pattern_event | 34451531 | 2026-09-24 | GREEN_WITH_DATA |  |
| pattern_evidence_certify | SUCCESS@2026-09-23T10:09:10+00:00 | c1_market.market_pattern_certification | 68 | 2026-09-23 | GREEN_WITH_DATA |  |
| pattern_weight_sync | SUCCESS@2026-09-23T10:09:28+00:00 | c1_market.market_pattern_win_rate | 4239 | 2026-09-23 | GREEN_WITH_DATA |  |
| pattern_win_rate_materialize | FAILED@2026-09-24T09:43:13+00:00 | c1_market.market_pattern_win_rate | 4239 | 2026-09-23 | NOT_GREEN(FAILED) | pattern_win_rate_materialize 退出码 1（物化失败，透传） |
| qweather_forecast_incremental | SUCCESS@2026-09-24T10:02:53+00:00 | c1_market.weather_data | 10353 | - | GREEN_WITH_DATA |  |
| qweather_now_incremental | SUCCESS@2026-09-24T10:03:15+00:00 | c1_market.weather_data | 10353 | - | GREEN_WITH_DATA |  |
| rate_decision_calendar_refresh | SUCCESS@2026-09-24T10:04:15+00:00 | c1_market.rate_decision_calendar | 3086 | 2025-10-30 | GREEN_WITH_DATA |  |
| realtime_snapshot_incremental | SUCCESS@2026-09-24T07:40:06+00:00 | c1_market.realtime_snapshot | 0 | ALL_NULL | FALSE_GREEN(SUCCESS但表0行) |  |
| repurchase_full_refresh | SUCCESS@2026-09-20T19:03:45+00:00 | c3_fundamental.repurchase | 6666 | - | GREEN_WITH_DATA |  |
| repurchase_refresh | SUCCESS@2026-09-24T11:08:01+00:00 | c3_fundamental.repurchase | 6666 | - | GREEN_WITH_DATA |  |
| research_report_detail_incremental | RUNNING@2026-09-25T12:30:00+00:00 | c3_fundamental.research_report | 146769 | 2026-09-18 | NOT_GREEN(RUNNING) |  |
| research_report_incremental | RUNNING@2026-09-25T14:17:06+00:00 | c3_fundamental.news_data | 8192439 | 2026-09-26 | NOT_GREEN(RUNNING) |  |
| restricted_shares_incremental | STALE@2026-09-24T10:05:01+00:00 | c3_fundamental.restricted_shares | 10197952 | 2035-10-29 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| rights_issue_incremental | FAILED@2026-07-23T11:00:28+00:00 | c3_fundamental.rights_issue | 80803 | 2026-06-30 | NOT_GREEN(FAILED) | module 'akshare' has no attribute 'stock_rights_issue_detail_sina' |
| road_freight_index_full_refresh | SUCCESS@2026-09-18T00:18:12+00:00 | c1_market.road_freight_index | 86 | 2026-08-21 | GREEN_WITH_DATA |  |
| road_freight_index_refresh | SUCCESS@2026-09-20T19:04:06+00:00 | c1_market.road_freight_index | 86 | 2026-08-21 | GREEN_WITH_DATA |  |
| sector_constituent_refresh | SUCCESS@2026-09-03T11:38:35+00:00 | c1_market.sector_constituent | 236836 | - | GREEN_WITH_DATA |  |
| sector_list_refresh | SUCCESS@2026-09-02T17:02:12+00:00 | c1_market.sector_list | 5217 | - | GREEN_WITH_DATA |  |
| sector_meta_refresh | SUCCESS@2026-09-24T08:30:42+00:00 | c1_market.sector_meta | 2430 | 2026-09-24 | GREEN_WITH_DATA |  |
| sector_snapshot_incremental | SUCCESS@2026-09-24T07:40:06+00:00 | c1_market.sector_snapshot | 117130 | 2026-09-24 | GREEN_WITH_DATA |  |
| share_change_incremental | STALE@2026-09-24T10:05:01+00:00 | c3_fundamental.share_change | 190501 | 2026-09-23 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| share_unlock_forward_refresh | SUCCESS@2026-09-20T19:04:11+00:00 | c3_fundamental.share_unlock | 31323 | 2027-09-21 | GREEN_WITH_DATA |  |
| share_unlock_incremental | SUCCESS@2026-09-24T10:05:07+00:00 | c3_fundamental.share_unlock | 31323 | 2027-09-21 | GREEN_WITH_DATA |  |
| shareholder_incremental | SUCCESS@2026-09-24T10:05:20+00:00 | c3_fundamental.shareholder_count | 514368 | 2026-09-24 | GREEN_WITH_DATA |  |
| st_namechange_backfill | SUCCESS@2026-09-03T11:39:26+00:00 | c1_market.st_stock_list | 423703 | 2026-09-24 | GREEN_WITH_DATA |  |
| st_status_premarket | SUCCESS@2026-09-24T00:34:00+00:00 | c1_market.st_stock_list | 423703 | 2026-09-24 | GREEN_WITH_DATA |  |
| st_stock_list_refresh | SUCCESS@2026-09-24T10:05:25+00:00 | c1_market.st_stock_list | 423703 | - | GREEN_WITH_DATA |  |
| stk_limit_postclose | SUCCESS@2026-09-24T10:05:38+00:00 | c1_market.stk_limit | 9226503 | 2026-09-24 | GREEN_WITH_DATA |  |
| stk_limit_premarket | SUCCESS@2026-09-24T00:34:18+00:00 | c1_market.stk_limit | 9226503 | 2026-09-24 | GREEN_WITH_DATA |  |
| stock_basic_postclose | STALE@2026-09-24T10:05:54+00:00 | c1_market.stock_basic | 9036265 | 2026-09-23 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| stock_basic_premarket | STALE@2026-09-24T00:34:00+00:00 | c1_market.stock_basic | 9036265 | 2026-09-23 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| stock_daily_basic_incremental | SUCCESS@2026-09-24T08:30:51+00:00 | c1_market.stock_daily_basic | 7079611 | 2026-09-24 | GREEN_WITH_DATA |  |
| stock_hot_rank_incremental | SUCCESS@2026-09-24T10:06:15+00:00 | c1_market.stock_hot_rank | 6793 | - | GREEN_WITH_DATA |  |
| stock_indicator_full_refresh | SUCCESS@2026-09-20T19:04:24+00:00 | c1_market.stock_indicator | 11685777 | - | GREEN_WITH_DATA |  |
| stock_indicator_incremental | SUCCESS@2026-09-24T08:30:59+00:00 | c1_market.stock_indicator | 11685777 | 2026-09-24 | GREEN_WITH_DATA |  |
| stock_list_delisted_refresh | SUCCESS@2026-09-03T11:39:26+00:00 | c1_market.stock_list | 5921 | - | GREEN_WITH_DATA |  |
| stock_list_refresh | SUCCESS@2026-09-03T11:39:29+00:00 | c1_market.stock_list | 5921 | - | GREEN_WITH_DATA |  |
| suspend_status_derive_weekend | SUCCESS@2026-09-24T21:30:16+00:00 | c1_market.suspend | 0 | ALL_NULL | FALSE_GREEN(SUCCESS但表0行) |  |
| suspend_status_postclose | SUCCESS@2026-09-24T10:12:48+00:00 | c1_market.suspend | 0 | ALL_NULL | FALSE_GREEN(SUCCESS但表0行) |  |
| suspend_status_premarket | SUCCESS@2026-09-24T00:34:00+00:00 | c1_market.suspend | 0 | ALL_NULL | FALSE_GREEN(SUCCESS但表0行) |  |
| technical_indicator_full_refresh | STALE@2026-09-22T21:30:18+00:00 | c1_market.technical_indicator | 362215198 | 2026-09-24 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| technical_indicator_incremental | SUCCESS@2026-09-24T09:32:01+00:00 | c1_market.technical_indicator | 362215198 | 2026-09-24 | GREEN_WITH_DATA |  |
| tick_backfill_weekly | None@None | c1_market.tick_data | 8953170951 | - | NEVER_RUN(无task_runs记录) |  |
| tick_data_snapshot | SUCCESS@2026-09-24T07:40:30+00:00 | c1_market.tick_data | 8953170951 | 2026-09-24 | GREEN_WITH_DATA |  |
| top10_circulating_shareholders_incremental | STALE@2026-09-21T14:00:00+00:00 | c3_fundamental.top10_circulating_shareholders | 2138764 | 2026-05-15 | NOT_GREEN(STALE) | Reaped: stale RUNNING > 6h (auto-reap) |
| top10_shareholders_incremental | SUCCESS@2026-09-21T14:00:14+00:00 | c3_fundamental.top10_shareholders | 1500427 | 2026-06-30 | GREEN_WITH_DATA |  |
| trade_calendar_refresh | SUCCESS@2026-09-03T11:39:32+00:00 | c1_market.trade_calendar | 8803 | - | GREEN_WITH_DATA |  |
| trading_lifecycle_weekly | SUCCESS@2026-09-20T19:08:20+00:00 | - | None | - | NO_TARGET_TABLE(no_table_declared) |  |
| us_futures_intraday_snapshot | SUCCESS@2026-09-24T07:40:30+00:00 | c1_market.us_futures_intraday | 671 | 2026-09-24 | GREEN_WITH_DATA |  |
| us_index_full_refresh | SUCCESS@2026-09-20T19:10:11+00:00 | c1_market.us_index | 22633 | - | GREEN_WITH_DATA |  |
| us_index_incremental | SUCCESS@2026-09-24T10:15:16+00:00 | c1_market.us_index | 22633 | 2026-09-23 | GREEN_WITH_DATA |  |
