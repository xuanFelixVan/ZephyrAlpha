---
module_id: MOD-L00-004
date: "2026-07-06"
ttl: permanent
stability: evolving
last_updated: "2026-07-06"
generated_by: tmp/generate_acquisition_matrix.py
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

# 数据获取能力矩阵

> **生成时间**: 2026-07-06 09:56:29
> **数据源**: tasks.yaml（61 个任务）+ ClickHouse 行数扫描
> **生成器**: `tmp/generate_acquisition_matrix.py`（task_bound，阶段4 重建）
> **集成器蓝图**: [data_source_integrator_blueprint.md](data_source_integrator_blueprint.md)（MOD-L00-004）

## 4 态统计

- ✅ 已配置定时: 44
- 🔴 已禁用: 2
- 🔵 待接入(空表): 15

## 调度时段覆盖

| 调度时段 | 任务数 | 已配置定时 |
|---------|--------|-----------|
| 盘后日K(16:30) | 12 | 12 |
| 盘后资金(17:00) | 11 | 9 |
| 盘后事件(18:00) | 13 | 9 |
| 周末财务(周六10:00) | 13 | 5 |
| 静态数据(月初09:00) | 12 | 9 |

## 矩阵明细

| # | task_id | 表名 | 数据源 | 调度时段 | 行数 | 最新日期 | 状态 |
|---|---------|------|--------|---------|------|---------|------|
| 1 | adj_factor_incremental | c1_market.adj_factor | ifind | 盘后日K(16:30) | 18,797,511 | 2026-07-03 | ✅ 已配置定时 |
| 2 | kline_daily_hfq_incremental | c1_market.kline_daily_hfq | ifind | 盘后日K(16:30) | 18,119,282 | 2026-07-02 | ✅ 已配置定时 |
| 3 | kline_daily_incremental | c1_market.kline_daily | ifind | 盘后日K(16:30) | 18,124,798 | 2026-07-03 | ✅ 已配置定时 |
| 4 | daily_valuation_incremental | c1_market.daily_valuation | ifind | 盘后日K(16:30) | 8,787,985 | 2026-07-03 | ✅ 已配置定时 |
| 5 | index_kline_incremental | c1_market.index_kline | ifind | 盘后日K(16:30) | 3,066,374 | 2026-07-03 | ✅ 已配置定时 |
| 6 | margin_trading_incremental | c1_market.margin_trading | ifind | 盘后资金(17:00) | 1,095,732 | 2026-06-30 | ✅ 已配置定时 |
| 7 | block_trade_incremental | c1_market.block_trade | ifind | 盘后资金(17:00) | 161,708 | 2026-06-30 | ✅ 已配置定时 |
| 8 | dragon_tiger_incremental | c1_market.dragon_tiger | ifind | 盘后资金(17:00) | 167,961 | 2026-07-03 | ✅ 已配置定时 |
| 9 | hk_daily_kline_incremental | c1_market.hk_daily_kline | miniqmt | 盘后资金(17:00) | 1,459,915 | 2026-07-03 | ✅ 已配置定时 |
| 10 | macro_data_incremental | c1_market.macro_data | akshare | 盘后资金(17:00) | 5,853 | 2026-06-30 | ✅ 已配置定时 |
| 11 | money_flow_incremental | c1_market.money_flow | ifind | 盘后资金(17:00) | 494,658 | 2026-07-03 | ✅ 已配置定时 |
| 12 | hk_connect_flow_incremental | c1_market.hk_connect_flow | ifind | 盘后资金(17:00) | N/A |  | 🔴 已禁用 |
| 13 | futures_kline_incremental | c1_market.futures_kline | miniqmt | 盘后资金(17:00) | 3,067,213 | 2026-07-03 | ✅ 已配置定时 |
| 14 | futures_position_incremental | c1_market.futures_position | miniqmt | 盘后资金(17:00) | 0 |  | 🔵 待接入(空表) |
| 15 | us_daily_kline_incremental | c1_market.us_daily_kline | tickflow | 盘后资金(17:00) | 167,175 | 2026-07-01 | ✅ 已配置定时 |
| 16 | us_index_incremental | c1_market.us_index | tickflow | 盘后资金(17:00) | 22,441 | 2026-07-02 | ✅ 已配置定时 |
| 17 | kline_weekly_incremental | c1_market.kline_weekly | ifind | 盘后日K(16:30) | 3,769,062 | 2026-06-26 | ✅ 已配置定时 |
| 18 | kline_monthly_incremental | c1_market.kline_monthly | ifind | 盘后日K(16:30) | 898,736 | 2026-06-30 | ✅ 已配置定时 |
| 19 | kline_1min_incremental | c1_market.kline_1min | miniqmt | 盘后日K(16:30) | 3,830,588,993 | 2026-07-02 | ✅ 已配置定时 |
| 20 | kline_5min_incremental | c1_market.kline_5min | miniqmt | 盘后日K(16:30) | 975,946,697 |  | ✅ 已配置定时 |
| 21 | kline_15min_incremental | c1_market.kline_15min | miniqmt | 盘后日K(16:30) | 254,313,641 | 2026-07-02 | ✅ 已配置定时 |
| 22 | kline_30min_incremental | c1_market.kline_30min | miniqmt | 盘后日K(16:30) | 127,156,825 | 2026-07-02 | ✅ 已配置定时 |
| 23 | kline_60min_incremental | c1_market.kline_60min | miniqmt | 盘后日K(16:30) | 63,578,425 | 2026-07-02 | ✅ 已配置定时 |
| 24 | news_data_incremental | c3_fundamental.news_data | rss | 盘后事件(18:00) | 287 |  | ✅ 已配置定时 |
| 25 | news_news_info_incremental | c3_fundamental.news_news_info | tushare | 盘后事件(18:00) | 9,609,089 |  | ✅ 已配置定时 |
| 26 | news_security_incremental | c3_fundamental.news_security | tushare | 盘后事件(18:00) | 3,728,723 |  | ✅ 已配置定时 |
| 27 | share_unlock_incremental | c3_fundamental.share_unlock | ifind | 盘后事件(18:00) | 0 |  | 🔵 待接入(空表) |
| 28 | shareholder_incremental | c3_fundamental.shareholder | miniqmt | 盘后事件(18:00) | 0 |  | 🔵 待接入(空表) |
| 29 | analyst_forecast_incremental | c3_fundamental.analyst_forecast | akshare | 盘后事件(18:00) | 0 |  | 🔵 待接入(空表) |
| 30 | earnings_forecast_incremental | c3_fundamental.earnings_forecast | miniqmt | 盘后事件(18:00) | 125,582 |  | ✅ 已配置定时 |
| 31 | express_report_incremental | c3_fundamental.express_report | miniqmt | 盘后事件(18:00) | 29,627 |  | ✅ 已配置定时 |
| 32 | audit_opinion_incremental | c3_fundamental.audit_opinion | ifind | 盘后事件(18:00) | 96,010 |  | ✅ 已配置定时 |
| 33 | dividend_incremental | c3_fundamental.dividend | miniqmt | 盘后事件(18:00) | 115,351 |  | ✅ 已配置定时 |
| 34 | rights_issue_incremental | c3_fundamental.rights_issue | akshare | 盘后事件(18:00) | 81,028 |  | ✅ 已配置定时 |
| 35 | equity_pledge_incremental | c3_fundamental.equity_pledge | ifind | 盘后事件(18:00) | 0 |  | 🔵 待接入(空表) |
| 36 | equity_pledge_summary_incremental | c3_fundamental.equity_pledge_summary | ifind | 盘后事件(18:00) | 1,723,182 | 2026-07-03 | ✅ 已配置定时 |
| 37 | balance_sheet_incremental | c3_fundamental.balance_sheet | miniqmt | 周末财务(周六10:00) | 334,521 |  | ✅ 已配置定时 |
| 38 | income_statement_incremental | c3_fundamental.income_statement | miniqmt | 周末财务(周六10:00) | 340,959 |  | ✅ 已配置定时 |
| 39 | cashflow_statement_incremental | c3_fundamental.cashflow_statement | miniqmt | 周末财务(周六10:00) | 305,230 |  | ✅ 已配置定时 |
| 40 | financial_indicator_incremental | c3_fundamental.financial_indicator | miniqmt | 周末财务(周六10:00) | 347,984 |  | ✅ 已配置定时 |
| 41 | main_business_incremental | c3_fundamental.main_business | miniqmt | 周末财务(周六10:00) | 2,090,334 |  | ✅ 已配置定时 |
| 42 | industry_class_refresh | c3_fundamental.industry_class | tdx | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 43 | sector_kline_incremental | c1_market.sector_kline | tdx | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 44 | option_iv_surface_incremental | c1_market.option_iv_surface | miniqmt | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 45 | convertible_bond_iv_incremental | c1_market.convertible_bond_iv | miniqmt | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 46 | futures_term_structure_incremental | c1_market.futures_term_structure | miniqmt | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 47 | tick_data_snapshot | c1_market.tick_data | miniqmt | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 48 | auction_snapshot | c1_market.auction_snapshot | miniqmt | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 49 | index_quote_snapshot | c1_market.index_quote | miniqmt | 周末财务(周六10:00) | 0 |  | 🔵 待接入(空表) |
| 50 | trade_calendar_refresh | c1_market.trade_calendar | baostock | 静态数据(月初09:00) | 13,162 |  | ✅ 已配置定时 |
| 51 | stock_list_refresh | c1_market.stock_list | miniqmt | 静态数据(月初09:00) | 5,534 |  | ✅ 已配置定时 |
| 52 | index_constituent_refresh | c1_market.index_constituent | baostock | 静态数据(月初09:00) | 59,583 | 2026-06-30 | ✅ 已配置定时 |
| 53 | industry_class_ifind_refresh | c3_fundamental.industry_class_ifind | ifind | 静态数据(月初09:00) | 0 |  | 🔵 待接入(空表) |
| 54 | sector_constituent_refresh | c3_fundamental.sector_constituent | tdx | 静态数据(月初09:00) | 0 |  | 🔵 待接入(空表) |
| 55 | kline_daily_full_refresh | c1_market.kline_daily | baostock | 静态数据(月初09:00) | 18,124,798 | 2026-07-03 | ✅ 已配置定时 |
| 56 | macro_data_full_refresh | c1_market.macro_data | akshare | 静态数据(月初09:00) | 5,853 | 2026-06-30 | ✅ 已配置定时 |
| 57 | us_daily_kline_full_refresh | c1_market.us_daily_kline | tickflow | 静态数据(月初09:00) | 167,175 | 2026-07-01 | ✅ 已配置定时 |
| 58 | us_index_full_refresh | c1_market.us_index | tickflow | 静态数据(月初09:00) | 22,441 | 2026-07-02 | ✅ 已配置定时 |
| 59 | money_flow_full_refresh | c1_market.money_flow | ifind | 静态数据(月初09:00) | 494,658 | 2026-07-03 | ✅ 已配置定时 |
| 60 | daily_valuation_full_refresh | c1_market.daily_valuation | ifind | 静态数据(月初09:00) | 8,787,985 | 2026-07-03 | ✅ 已配置定时 |
| 61 | kline_5min_history_backfill | c1_market.kline_5min | miniqmt | 静态数据(月初09:00) | 975,946,697 |  | 🔴 已禁用 |

---

## 变更历史

- **2026-07-06**: 补建 8 张缺失表（DDL: `tmp/sql/_create_integrator_missing_tables.sql`），"❌ 表不存在" 8 → 0，"🔵 待接入(空表)" 7 → 15
- **2026-07-06**: 阶段4 重建——集成器 61 任务接入调度，"已配置定时" 项数 = 44（原阶段1 短板：0 项自动更新）
- **2026-07-06**: 阶段1 初次生成——暴露"61 项手动触发、0 项自动更新"短板，启动 MOD-L00-004