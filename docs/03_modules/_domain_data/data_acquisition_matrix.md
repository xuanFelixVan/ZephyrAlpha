---
module_id: MOD-L00-004
date: "2026-07-14"
ttl: permanent
stability: evolving
last_updated: "2026-07-14"
generated_by: tmp/generate_acquisition_matrix.py
responsibility_domain: 
design_maturity: prototype
build_status: generated
---

# 数据获取能力矩阵

> **生成时间**: 2026-07-14 17:19:38
> **数据源**: tasks.yaml（117 个任务）+ ClickHouse 行数扫描
> **生成器**: `tmp/generate_acquisition_matrix.py`（task_bound，阶段4 重建）
> **集成器蓝图**: [data_source_integrator_blueprint.md](data_source_integrator_blueprint.md)（MOD-L00-004）

## 4 态统计

- ✅ 已配置定时: 103
- ❌ 表不存在: 5
- 🔴 已禁用: 6
- 🔵 待接入(空表): 3

## 调度时段覆盖

| 调度时段 | 任务数 | 已配置定时 |
|---------|--------|-----------|
| 盘后日K(16:30) | 15 | 13 |
| 夜间财务(22:00) | 8 | 8 |
| 盘后资金(17:00) | 16 | 11 |
| L1实时(*/5 9-15) | 12 | 10 |
| L3事件(*/15 * * * *) | 13 | 11 |
| 周末校准(周六02:00) | 12 | 12 |
| L2分钟(*/5 9-15) | 15 | 13 |
| 盘后事件(18:00) | 11 | 11 |
| 静态数据(月初09:00) | 15 | 14 |

## 矩阵明细

| # | task_id | 表名 | 数据源 | 调度时段 | 行数 | 最新日期 | 状态 |
|---|---------|------|--------|---------|------|---------|------|
| 1 | adj_factor_incremental | c1_market.adj_factor | miniqmt | 盘后日K(16:30) | N/A |  | ❌ 表不存在 |
| 2 | kline_daily_hfq_incremental | c1_market.kline_daily_hfq | miniqmt | 盘后日K(16:30) | 18,179,504 | 2026-07-14 | ✅ 已配置定时 |
| 3 | kline_daily_incremental | c1_market.kline_daily | miniqmt | 盘后日K(16:30) | 36,311,578 | 2026-07-14 | ✅ 已配置定时 |
| 4 | daily_valuation_incremental | c1_market.daily_valuation | ifind | 盘后日K(16:30) | 8,789,989 | 2026-07-09 | ✅ 已配置定时 |
| 5 | kline_index_incremental | c1_market.kline_index | miniqmt | 盘后日K(16:30) | 3,069,944 | 2026-07-14 | ✅ 已配置定时 |
| 6 | margin_trading_incremental | c1_market.margin_trading | akshare | 夜间财务(22:00) | 1,134,192 | 2026-07-10 | ✅ 已配置定时 |
| 7 | block_trade_incremental | c1_market.block_trade | akshare | 盘后资金(17:00) | 162,830 | 2026-07-10 | ✅ 已配置定时 |
| 8 | dragon_tiger_incremental | c1_market.dragon_tiger | akshare | 盘后资金(17:00) | 169,180 | 2026-07-10 | ✅ 已配置定时 |
| 9 | kline_hk_daily_incremental | c1_market.kline_hk_daily | miniqmt | L1实时(*/5 9-15) | 1,555,895 | 2026-07-14 | ✅ 已配置定时 |
| 10 | macro_data_incremental | c1_market.macro_data | akshare | L3事件(*/15 * * * *) | 279,597 | 2026-06-30 | ✅ 已配置定时 |
| 11 | money_flow_incremental | c1_market.money_flow | ifind | 盘后资金(17:00) | 594,300 | 2026-07-12 | ✅ 已配置定时 |
| 12 | hk_connect_flow_incremental | c1_market.hk_connect_flow | akshare | 盘后资金(17:00) | 4,052 | 2024-08-16 | ✅ 已配置定时 |
| 13 | kline_futures_incremental | c1_market.kline_futures | miniqmt | 盘后资金(17:00) | 3,108,757 | 2026-07-10 | ✅ 已配置定时 |
| 14 | futures_position_incremental | c1_market.futures_position | miniqmt | L1实时(*/5 9-15) | 292 | 2026-07-13 | ✅ 已配置定时 |
| 15 | kline_us_daily_incremental | c1_market.kline_us_daily | tickflow | 周末校准(周六02:00) | 167,175 | 2026-07-01 | ✅ 已配置定时 |
| 16 | us_index_incremental | c1_market.us_index | tickflow | 周末校准(周六02:00) | 22,441 | 2026-07-02 | ✅ 已配置定时 |
| 17 | kline_weekly_incremental | c1_market.kline_weekly | miniqmt | 盘后日K(16:30) | 3,784,650 | 2026-07-10 | ✅ 已配置定时 |
| 18 | kline_monthly_incremental | c1_market.kline_monthly | miniqmt | 盘后日K(16:30) | 906,990 | 2026-07-14 | ✅ 已配置定时 |
| 19 | kline_1min_incremental | c1_market.kline_1min | miniqmt | L2分钟(*/5 9-15) | 3,843,259,462 | 2026-07-14 | ✅ 已配置定时 |
| 20 | kline_5min_incremental | c1_market.kline_5min | miniqmt | L2分钟(*/5 9-15) | 978,564,641 | 2026-07-13 11:30:00 | ✅ 已配置定时 |
| 21 | kline_15min_incremental | c1_market.kline_15min | miniqmt | L2分钟(*/5 9-15) | 254,880,617 | 2026-07-13 | ✅ 已配置定时 |
| 22 | kline_30min_incremental | c1_market.kline_30min | miniqmt | L2分钟(*/5 9-15) | N/A |  | ❌ 表不存在 |
| 23 | kline_60min_incremental | c1_market.kline_60min | miniqmt | L2分钟(*/5 9-15) | 63,578,425 | 2026-07-02 | ✅ 已配置定时 |
| 24 | kline_etf_1min_incremental | c1_market.kline_etf_1min | miniqmt | L2分钟(*/5 9-15) | 343,553,536 | 2026-07-03 | ✅ 已配置定时 |
| 25 | kline_etf_5min_incremental | c1_market.kline_etf_5min | miniqmt | L2分钟(*/5 9-15) | 68,389,859 | 2026-07-03 | ✅ 已配置定时 |
| 26 | kline_etf_15min_incremental | c1_market.kline_etf_15min | miniqmt | L2分钟(*/5 9-15) | N/A |  | ❌ 表不存在 |
| 27 | kline_etf_30min_incremental | c1_market.kline_etf_30min | miniqmt | L2分钟(*/5 9-15) | 11,398,303 | 2026-07-03 | ✅ 已配置定时 |
| 28 | kline_etf_60min_incremental | c1_market.kline_etf_60min | miniqmt | L2分钟(*/5 9-15) | 5,699,152 | 2026-07-03 | ✅ 已配置定时 |
| 29 | kline_lof_1min_incremental | c1_market.kline_lof_1min | miniqmt | L2分钟(*/5 9-15) | 181,720,142 | 2026-07-03 | ✅ 已配置定时 |
| 30 | kline_lof_5min_incremental | c1_market.kline_lof_5min | miniqmt | L2分钟(*/5 9-15) | 36,194,482 | 2026-07-03 | ✅ 已配置定时 |
| 31 | kline_lof_15min_incremental | c1_market.kline_lof_15min | miniqmt | L2分钟(*/5 9-15) | 12,064,844 | 2026-07-03 | ✅ 已配置定时 |
| 32 | kline_lof_30min_incremental | c1_market.kline_lof_30min | miniqmt | L2分钟(*/5 9-15) | 6,032,451 | 2026-07-03 | ✅ 已配置定时 |
| 33 | kline_lof_60min_incremental | c1_market.kline_lof_60min | miniqmt | L2分钟(*/5 9-15) | 3,016,252 | 2026-07-03 | ✅ 已配置定时 |
| 34 | kline_weekly_hfq_incremental | c1_market.kline_weekly_hfq | miniqmt | 盘后日K(16:30) | 3,778,641 | 2026-07-10 | ✅ 已配置定时 |
| 35 | kline_monthly_hfq_incremental | c1_market.kline_monthly_hfq | miniqmt | 盘后日K(16:30) | 903,936 | 2026-07-10 | ✅ 已配置定时 |
| 36 | news_data_incremental | c3_fundamental.news_data | rss | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 37 | share_unlock_incremental | c3_fundamental.share_unlock | akshare | 盘后资金(17:00) | 71 |  | ✅ 已配置定时 |
| 38 | shareholder_incremental | c3_fundamental.shareholder_count | miniqmt | 盘后事件(18:00) | 1,003,944 | 2026-07-02 | ✅ 已配置定时 |
| 39 | analyst_forecast_incremental | c3_fundamental.analyst_forecast | akshare | 盘后事件(18:00) | 11,176 | 2026-07-13 | ✅ 已配置定时 |
| 40 | earnings_forecast_incremental | c3_fundamental.earnings_forecast | miniqmt | 盘后事件(18:00) | 251,164 |  | ✅ 已配置定时 |
| 41 | express_report_incremental | c3_fundamental.express_report | miniqmt | 盘后事件(18:00) | 57,313 |  | ✅ 已配置定时 |
| 42 | audit_opinion_incremental | c3_fundamental.audit_opinion | akshare | 盘后事件(18:00) | 192,020 |  | ✅ 已配置定时 |
| 43 | dividend_incremental | c3_fundamental.dividend | miniqmt | 盘后事件(18:00) | 231,086 |  | ✅ 已配置定时 |
| 44 | rights_issue_incremental | c3_fundamental.rights_issue | akshare | 盘后事件(18:00) | 161,773 |  | ✅ 已配置定时 |
| 45 | equity_pledge_incremental | c3_fundamental.equity_pledge_detail | akshare | 盘后事件(18:00) | 600,994 |  | ✅ 已配置定时 |
| 46 | equity_pledge_summary_incremental | c3_fundamental.equity_pledge_summary | akshare | 盘后事件(18:00) | 1,723,182 | 2026-07-03 | ✅ 已配置定时 |
| 47 | balance_sheet_incremental | c3_fundamental.balance_sheet | miniqmt | 夜间财务(22:00) | 669,045 |  | ✅ 已配置定时 |
| 48 | income_statement_incremental | c3_fundamental.income_statement | miniqmt | 夜间财务(22:00) | 681,918 |  | ✅ 已配置定时 |
| 49 | cashflow_statement_incremental | c3_fundamental.cashflow_statement | miniqmt | 夜间财务(22:00) | 610,460 |  | ✅ 已配置定时 |
| 50 | financial_indicator_incremental | c3_fundamental.financial_indicator | miniqmt | 夜间财务(22:00) | 696,283 |  | ✅ 已配置定时 |
| 51 | main_business_incremental | c3_fundamental.main_business | miniqmt | 夜间财务(22:00) | 2,763,040 |  | ✅ 已配置定时 |
| 52 | industry_class_refresh | c1_market.industry_class | tdx | 周末校准(周六02:00) | 16,600 |  | ✅ 已配置定时 |
| 53 | kline_sector_incremental | c1_market.kline_sector | tdx | 周末校准(周六02:00) | 8,600 | 2026-07-10 | ✅ 已配置定时 |
| 54 | option_iv_surface_incremental | c1_market.option_iv_surface | miniqmt | L1实时(*/5 9-15) | 8,876 | 2026-07-10 | ✅ 已配置定时 |
| 55 | convertible_bond_iv_incremental | c1_market.convertible_bond_iv | miniqmt | L1实时(*/5 9-15) | 101,457 | 2026-07-13 | ✅ 已配置定时 |
| 56 | futures_term_structure_incremental | c1_market.futures_term_structure | miniqmt | L1实时(*/5 9-15) | 2,525 | 2026-07-13 | ✅ 已配置定时 |
| 57 | tick_data_snapshot | c1_market.tick_data | miniqmt | L1实时(*/5 9-15) | 20,449,044,159 | 2026-07-14 | ✅ 已配置定时 |
| 58 | index_quote_snapshot | c1_market.index_quote | miniqmt | L1实时(*/5 9-15) | 0 |  | 🔵 待接入(空表) |
| 59 | edb_data_incremental | c1_market.edb_data | ifind | L3事件(*/15 * * * *) | 0 |  | 🔴 已禁用 |
| 60 | concept_sector_refresh | c1_market.concept_sector | ifind | 静态数据(月初09:00) | 388 |  | ✅ 已配置定时 |
| 61 | realtime_snapshot_incremental | c1_market.realtime_snapshot | ifind | 盘后日K(16:30) | 0 |  | 🔵 待接入(空表) |
| 62 | trade_calendar_refresh | c1_market.trade_calendar | baostock | 静态数据(月初09:00) | 13,162 |  | ✅ 已配置定时 |
| 63 | stock_list_refresh | c1_market.stock_list | miniqmt | 静态数据(月初09:00) | 5,534 |  | ✅ 已配置定时 |
| 64 | index_constituent_refresh | c1_market.index_constituent | baostock | 静态数据(月初09:00) | 59,583 | 2026-06-30 | ✅ 已配置定时 |
| 65 | industry_class_suppl_refresh | c3_fundamental.industry_class_suppl | ifind | 静态数据(月初09:00) | 5,203 |  | ✅ 已配置定时 |
| 66 | kline_daily_full_refresh | c1_market.kline_daily | miniqmt | 周末校准(周六02:00) | 36,311,578 | 2026-07-14 | ✅ 已配置定时 |
| 67 | macro_data_full_refresh | c1_market.macro_data | akshare | 周末校准(周六02:00) | 279,597 | 2026-06-30 | ✅ 已配置定时 |
| 68 | kline_us_daily_full_refresh | c1_market.kline_us_daily | tickflow | 周末校准(周六02:00) | 167,175 | 2026-07-01 | ✅ 已配置定时 |
| 69 | us_index_full_refresh | c1_market.us_index | tickflow | 周末校准(周六02:00) | 22,441 | 2026-07-02 | ✅ 已配置定时 |
| 70 | money_flow_full_refresh | c1_market.money_flow | ifind | 周末校准(周六02:00) | 594,300 | 2026-07-12 | ✅ 已配置定时 |
| 71 | daily_valuation_full_refresh | c1_market.daily_valuation | akshare | 周末校准(周六02:00) | 8,789,989 | 2026-07-09 | ✅ 已配置定时 |
| 72 | kline_5min_history_backfill | c1_market.kline_5min | miniqmt | 静态数据(月初09:00) | 978,564,641 | 2026-07-13 11:30:00 | 🔴 已禁用 |
| 73 | news_cls_incremental | c3_fundamental.news_data | cls | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 74 | news_eastmoney_incremental | c3_fundamental.news_data | eastmoney_news | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 75 | news_rss_incremental | c3_fundamental.news_data | rss | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 76 | news_stock_em_incremental | c3_fundamental.news_data | akshare | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 77 | news_cctv_incremental | c3_fundamental.news_data | akshare | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 78 | news_economic_baidu_incremental | c3_fundamental.news_data | akshare | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 79 | news_baidu_incremental | c3_fundamental.news_data | akshare | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 80 | news_stock_incremental | c3_fundamental.news_data | akshare | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 81 | news_tushare_incremental | c3_fundamental.news_data | tushare | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | 🔴 已禁用 |
| 82 | restricted_shares_incremental | c3_fundamental.restricted_shares | akshare | 盘后资金(17:00) | 22,719,730 |  | ✅ 已配置定时 |
| 83 | research_report_incremental | c3_fundamental.news_data | akshare | L3事件(*/15 * * * *) | 9,611,190 | 2026-07-14 23:00:00 | ✅ 已配置定时 |
| 84 | hk_connect_flow_full | c1_market.hk_connect_flow | akshare | 盘后资金(17:00) | 4,052 | 2024-08-16 | ✅ 已配置定时 |
| 85 | kline_futures_full | c1_market.kline_futures | akshare | 周末校准(周六02:00) | 3,108,757 | 2026-07-10 | ✅ 已配置定时 |
| 86 | limit_up_down_incremental | c1_market.limit_up_down | akshare | L1实时(*/5 9-15) | 288 | 2026-07-12 | ✅ 已配置定时 |
| 87 | share_change_incremental | c3_fundamental.share_change | akshare | 盘后资金(17:00) | 169,757 |  | ✅ 已配置定时 |
| 88 | st_stock_list_refresh | c1_market.st_stock_list | akshare | 盘后资金(17:00) | 1,365 | 2026-07-12 | ✅ 已配置定时 |
| 89 | concept_board_refresh | c1_market.concept_board | akshare | 周末校准(周六02:00) | 371 |  | ✅ 已配置定时 |
| 90 | stock_indicator_incremental | c1_market.stock_indicator | akshare | 盘后日K(16:30) | 24,617 | 2026-07-10 | ✅ 已配置定时 |
| 91 | block_trade_detail_incremental | c1_market.block_trade_detail | akshare | 盘后资金(17:00) | 441 | 2026-07-10 | ✅ 已配置定时 |
| 92 | kline_cb_incremental | c1_market.kline_cb | miniqmt | 盘后日K(16:30) | 3,056 | 2026-07-14 | ✅ 已配置定时 |
| 93 | option_kline_incremental | c1_market.option_kline | miniqmt | 盘后日K(16:30) | 600 | 2026-07-10 | ✅ 已配置定时 |
| 94 | option_greeks_incremental | c1_market.option_greeks | miniqmt | L1实时(*/5 9-15) | 8,876 | 2026-07-10 | ✅ 已配置定时 |
| 95 | index_weight_refresh | c1_market.index_weight | miniqmt | 静态数据(月初09:00) | 3,700 | 2026-07-12 | ✅ 已配置定时 |
| 96 | sector_list_refresh | c1_market.sector_list | miniqmt | 静态数据(月初09:00) | 15,609 | 2026-07-12 | ✅ 已配置定时 |
| 97 | l2_tick_snapshot | c1_market.l2_tick | miniqmt | L1实时(*/5 9-15) | 0 |  | 🔵 待接入(空表) |
| 98 | auction_data_snapshot | c1_market.auction_snapshot | miniqmt | L1实时(*/5 9-15) | 109,261 | 2026-07-14 | ✅ 已配置定时 |
| 99 | kline_futures_qmt_incremental | c1_market.kline_futures_qmt | miniqmt | 盘后资金(17:00) | N/A |  | ❌ 表不存在 |
| 100 | hk_kline_incremental | c1_market.hk_kline | miniqmt | L1实时(*/5 9-15) | 760 | 2026-07-10 | ✅ 已配置定时 |
| 101 | us_kline_incremental | c1_market.us_kline | miniqmt | 盘后资金(17:00) | N/A |  | ❌ 表不存在 |
| 102 | etf_nav_refresh | c1_market.etf_nav | miniqmt | 盘后日K(16:30) | 400 | 2026-07-12 | ✅ 已配置定时 |
| 103 | repurchase_refresh | c3_fundamental.repurchase | akshare | 盘后事件(18:00) | 5,209 |  | ✅ 已配置定时 |
| 104 | margin_trading_qmt_placeholder | c1_market.margin_trading_qmt | miniqmt | 盘后资金(17:00) | N/A |  | 🔴 已禁用 |
| 105 | dragon_tiger_qmt_placeholder | c1_market.dragon_tiger_qmt | miniqmt | 盘后资金(17:00) | N/A |  | 🔴 已禁用 |
| 106 | block_trade_qmt_placeholder | c1_market.block_trade_qmt | miniqmt | 盘后资金(17:00) | N/A |  | 🔴 已禁用 |
| 107 | top10_shareholders_incremental | c3_fundamental.top10_shareholders | akshare | 夜间财务(22:00) | 1,881,299 |  | ✅ 已配置定时 |
| 108 | top10_circulating_shareholders_incremental | c3_fundamental.top10_circulating_shareholders | akshare | 夜间财务(22:00) | 2,244,440 |  | ✅ 已配置定时 |
| 109 | disclosure_plan_incremental | c3_fundamental.disclosure_plan | akshare | 盘后事件(18:00) | 611,422 |  | ✅ 已配置定时 |
| 110 | convertible_bond_list_refresh | c1_market.convertible_bond_list | akshare | 静态数据(月初09:00) | 1,142 | 2032-07-03 | ✅ 已配置定时 |
| 111 | etf_list_refresh | c1_market.etf_list | akshare | 静态数据(月初09:00) | 1,764 |  | ✅ 已配置定时 |
| 112 | lof_list_refresh | c1_market.lof_list | akshare | 静态数据(月初09:00) | 361 |  | ✅ 已配置定时 |
| 113 | hk_stock_list_refresh | c1_market.hk_stock_list | akshare | 静态数据(月初09:00) | 4,688 |  | ✅ 已配置定时 |
| 114 | hk_trade_calendar_refresh | c1_market.hk_trade_calendar | akshare | 静态数据(月初09:00) | 17,167 |  | ✅ 已配置定时 |
| 115 | index_list_refresh | c1_market.index_list | akshare | 静态数据(月初09:00) | 732 |  | ✅ 已配置定时 |
| 116 | etf_benchmark_refresh | c1_market.etf_benchmark | akshare | 静态数据(月初09:00) | 732 |  | ✅ 已配置定时 |
| 117 | sector_meta_refresh | c1_market.sector_meta | ifind | 盘后日K(16:30) | 90 | 2026-07-03 | ✅ 已配置定时 |

---

## 变更历史

- **2026-07-14**: 阶段4 重建——集成器 61 任务接入调度，"已配置定时" 项数 = 103（原阶段1 短板：0 项自动更新）
- **2026-07-06**: 阶段1 初次生成——暴露"61 项手动触发、0 项自动更新"短板，启动 MOD-L00-004