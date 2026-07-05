---
module_id: MOD-L00-001
title: 业务数据清单
doc_type: data_inventory
status: Active
generated_at: "2026-07-06 03:50:17"
generator: tmp/generate_data_inventory.py
language: zh
description: ClickHouse 业务数据库实时扫描结果
---

# 业务数据清单

> 自动生成时间：**2026-07-06 03:50:17**
> 数据库：ClickHouse（c1_market / c2_factor / c3_fundamental / c4_reference）
> 生成器：`tmp/generate_data_inventory.py`（可随时运行刷新）

## 总览

- 业务表总数：**80**
- 非空表数：**73**
- 数据总行数：**13,245,344,613**

## C1 市场数据（`c1_market`）

| 表名 | 中文名 | 起始时间 | 截止时间 | 标的数 | 总行数 | 数据源 | 更新方式 |
|------|--------|----------|----------|--------|--------|--------|----------|
| `_pepb_staging` | PE/PB暂存表 | 2025-11-12 | 2026-07-03 | 5533 | 839,473 | — | 每日 |
| `adj_factor` | 复权因子 | 1990-12-19 | 2026-07-03 | 5876 | 18,797,511 | bdpan | 每日 |
| `analyst_forecast` | 分析师预测 | 2026-07-04 | 2026-07-04 | 2857 | 8,373 | akshare | 事件驱动 |
| `auction_snapshot` | 集合竞价快照 | — | — | 0 | 0 | — | 实时 |
| `block_trade` | 大宗交易 | 2010-01-31 | 2026-06-30 | 4963 | 161,708 | ifind | 每日 |
| `convertible_bond_iv` | 可转债隐含波动率 | — | — | 0 | 0 | — | 每日 |
| `convertible_bond_list` | 可转债列表 | 1996-01-01 | 2026-07-06 | — | 1,142 | — | 静态 |
| `daily_kline` | A股日K线（原始） | 1990-12-19 | 2026-07-02 | 5898 | 18,122,192 | bdpan | 每日 |
| `daily_valuation` | 每日估值 | 1990-12-19 | 2026-07-03 | 5708 | 8,787,985 | local_valuation | 每日 |
| `dragon_tiger` | 龙虎榜 | 2006-07-17 | 2026-07-03 | 5047 | 167,961 | ifind | 每日 |
| `etf_benchmark` | ETF基准 | 1991-04-04 | 2025-07-21 | — | 732 | — | 静态 |
| `etf_kline_15min` | ETF15分钟K线 | 2005-02-23 | 2026-07-03 | 1581 | 22,813,741 | bdpan | 实时 |
| `etf_kline_1min` | ETF1分钟K线 | 2005-02-23 | 2026-07-03 | 1581 | 343,553,536 | bdpan | 实时 |
| `etf_kline_30min` | ETF30分钟K线 | 2005-02-23 | 2026-07-03 | 1581 | 11,398,303 | bdpan | 实时 |
| `etf_kline_5min` | ETF5分钟K线 | 2005-02-23 | 2026-07-03 | 1581 | 68,389,859 | bdpan | 实时 |
| `etf_kline_60min` | ETF60分钟K线 | 2005-02-23 | 2026-07-03 | 1581 | 5,699,152 | bdpan | 实时 |
| `etf_list` | ETF列表 | 2005-02-23 | 2026-07-06 | — | 1,764 | — | 静态 |
| `futures_kline` | 期货K线 | 2010-01-04 | 2026-07-03 | 17592 | 3,067,213 | qmt | 每日 |
| `futures_position` | 期货持仓 | — | — | 0 | 0 | — | 每日 |
| `futures_term_structure` | 期货期限结构 | — | — | 0 | 0 | — | 每日 |
| `hk_daily_kline` | 港股日K线 | 2015-05-29 | 2026-07-03 | 923 | 1,459,915 | qmt | 每日 |
| `hk_stock_list` | 港股股票列表 | — | — | — | 4,688 | — | 静态 |
| `hk_trade_calendar` | 港股交易日历 | 1980-01-01 | 2026-07-06 | — | 17,167 | — | 静态 |
| `index_constituent` | 指数成分股 | 2009-12-31 | 2026-06-30 | 3551 | 59,583 | ifind | 静态 |
| `index_kline` | 指数日K线 | 1990-12-19 | 2026-07-03 | 1031 | 3,066,374 | bdpan | 每日 |
| `index_list` | 指数列表 | 1991-04-04 | 2025-07-21 | 732 | 732 | — | 静态 |
| `index_quote` | 指数报价 | — | — | 0 | 0 | — | 每日 |
| `industry_class` | 行业分类 | — | — | 5534 | 16,600 | ifind | 静态 |
| `kline_15min` | A股15分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 254,313,641 | local_intraday | 实时 |
| `kline_1min` | A股1分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 3,830,588,993 | local_intraday | 实时 |
| `kline_30min` | A股30分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 127,156,825 | local_intraday | 实时 |
| `kline_5min` | A股5分钟K线 | 2000-06-09 | 2026-07-02 | 5238 | 975,946,697 | bdpan | 实时 |
| `kline_60min` | A股60分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 63,578,425 | local_intraday | 实时 |
| `kline_daily` | A股日K线（前复权） | 1990-12-19 | 2026-07-03 | 5895 | 18,124,798 | bdpan_qfq | 每日 |
| `kline_daily_hfq` | A股日K线（后复权） | 1990-12-19 | 2026-07-02 | 5895 | 18,119,282 | bdpan_hfq | 每日 |
| `kline_daily_none` | A股日K线（不复权） | 1990-12-19 | 2026-07-02 | 5893 | 18,118,948 | bdpan_none | 每日 |
| `kline_monthly` | A股月K线（前复权） | 1990-12-25 | 2026-06-30 | 5854 | 898,736 | bdpan_qfq | 每月 |
| `kline_monthly_hfq` | A股月K线（后复权） | 1990-12-25 | 2026-06-30 | 5854 | 898,736 | bdpan_hfq | 每月 |
| `kline_monthly_none` | A股月K线（不复权） | 1990-12-25 | 2026-06-30 | 5854 | 904,274 | bdpan_none | 每月 |
| `kline_weekly` | A股周K线（前复权） | 1990-12-20 | 2026-06-26 | 5856 | 3,769,062 | bdpan_qfq | 每周 |
| `kline_weekly_hfq` | A股周K线（后复权） | 1990-12-20 | 2026-06-26 | 5853 | 3,768,249 | bdpan_hfq | 每周 |
| `kline_weekly_none` | A股周K线（不复权） | 1990-12-20 | 2026-06-26 | 5856 | 3,769,209 | bdpan_none | 每周 |
| `lof_kline_15min` | LOF15分钟K线 | 2010-08-16 | 2026-07-03 | 2750 | 12,064,844 | bdpan | 实时 |
| `lof_kline_1min` | LOF1分钟K线 | 2010-08-16 | 2026-07-03 | 2750 | 181,720,142 | bdpan | 实时 |
| `lof_kline_30min` | LOF30分钟K线 | 2010-08-16 | 2026-07-03 | 2750 | 6,032,451 | bdpan | 实时 |
| `lof_kline_5min` | LOF5分钟K线 | 2010-08-16 | 2026-07-03 | 2750 | 36,194,482 | bdpan | 实时 |
| `lof_kline_60min` | LOF60分钟K线 | 2010-08-16 | 2026-07-03 | 2750 | 3,016,252 | bdpan | 实时 |
| `lof_list` | LOF列表 | — | — | — | 361 | — | 静态 |
| `macro_data` | 宏观经济数据 | 2006-03-31 | 2026-06-30 | 27 | 5,853 | akshare | 静态 |
| `margin_trading` | 融资融券 | 2010-01-31 | 2026-06-30 | 5534 | 1,095,732 | ifind | 每日 |
| `money_flow` | 资金流向 | 2025-04-25 | 2026-07-03 | 5632 | 494,658 | local_moneyflow | 每日 |
| `option_iv_surface` | 期权波动率曲面 | — | — | 0 | 0 | — | 每日 |
| `stock_list` | A股股票列表 | 1990-12-01 | 2026-07-02 | 5534 | 5,534 | — | 静态 |
| `tdx_market_index` | 通达信板块指数 | — | — | 50 | 50 | — | 每日 |
| `tdx_sector_info` | 通达信板块信息 | 2026-07-03 | 2026-07-03 | 90 | 90 | — | 每日 |
| `tick_data` | Tick数据（实时） | — | — | 0 | 0 | — | 实时 |
| `tick_history` | Tick数据（历史） | 2000-07-14 | 2026-07-02 | 8740 | 7,143,133,916 | bdpan | 每日 |
| `trade_calendar` | 交易日历 | 1990-12-19 | 2026-07-06 | — | 13,162 | — | 静态 |
| `us_daily_kline` | 美股日K线 | 2006-08-15 | 2026-07-01 | 34 | 167,175 | tickflow | 每日 |
| `us_index` | 美股指数 | 1993-01-29 | 2026-07-02 | 3 | 22,441 | tickflow | 每日 |

## C3 基本面数据（`c3_fundamental`）

| 表名 | 中文名 | 起始时间 | 截止时间 | 标的数 | 总行数 | 数据源 | 更新方式 |
|------|--------|----------|----------|--------|--------|--------|----------|
| `audit_opinion` | 审计意见 | 1998-02-21 | 2026-05-29 | 5852 | 96,010 | bdpan | 年度 |
| `balance_sheet` | 资产负债表 | 1990-03-21 | 2026-06-04 | 5857 | 334,521 | bdpan | 季度 |
| `cashflow_statement` | 现金流量表 | 1999-01-30 | 2026-06-04 | 5848 | 305,230 | bdpan | 季度 |
| `disclosure_plan` | 财报披露计划 | 2001-02-06 | 2026-07-02 | 5858 | 305,711 | bdpan | 静态 |
| `dividend` | 分红数据 | 1991-03-17 | 2026-07-01 | 5823 | 115,351 | bdpan | 事件驱动 |
| `earnings_forecast` | 业绩预告 | 1999-01-08 | 2026-07-03 | 5707 | 125,582 | bdpan | 事件驱动 |
| `equity_pledge_detail` | 股权质押明细 | 2003-06-10 | 2026-07-03 | 3572 | 297,056 | bdpan | 事件驱动 |
| `equity_pledge_summary` | 股权质押汇总 | 2014-03-07 | 2026-07-03 | 4440 | 1,723,182 | bdpan | 每日 |
| `express_report` | 业绩快报 | 2005-01-08 | 2026-07-02 | 4395 | 29,627 | bdpan | 事件驱动 |
| `financial_indicator` | 财务指标 | 1990-03-21 | 2026-06-04 | 5860 | 347,984 | bdpan | 季度 |
| `income_statement` | 利润表 | 1995-01-05 | 2026-06-04 | 5857 | 340,959 | bdpan | 季度 |
| `main_business` | 主营业务构成 | 2000-12-31 | 2026-03-31 | 5850 | 2,090,334 | bdpan | 季度 |
| `news_data` | 新闻数据（爬虫） | 2026-06-07 | 2026-07-03 | 287 | 287 | wallstreetcn | 实时 |
| `news_news_info` | 新闻信息（tushare） | 2000-01-01 | 2024-07-07 | 9608745 | 9,609,089 | — | 实时 |
| `news_security` | 新闻-股票关联 | 1997-04-30 | 2024-08-22 | 12590 | 3,728,723 | — | 实时 |
| `restricted_shares` | 限售解禁 | 2005-01-10 | 2026-07-02 | 5747 | 11,359,865 | bdpan | 事件驱动 |
| `rights_issue` | 配股/分红方案 | 1991-03-03 | 2026-07-06 | 5823 | 81,028 | bdpan | 事件驱动 |
| `shareholder_count` | 股东户数 | 1993-01-12 | 2026-07-02 | 5840 | 501,972 | bdpan | 季度 |
| `top10_circulating_shareholders` | 十大流通股东 | 2005-01-29 | 2026-05-15 | 5768 | 2,145,705 | bdpan | 季度 |
| `top10_shareholders` | 十大股东 | 2005-01-29 | 2026-05-15 | 5789 | 1,447,675 | bdpan | 季度 |

## 数据新鲜度提示

（当前日期：2026-07-06）

| 表 | 截止时间 | 距今天数 | 状态 |
|----|----------|----------|------|
| `c1_market._pepb_staging` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.adj_factor` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.analyst_forecast` | 2026-07-04 | 2天 | ℹ️ 事件驱动型 |
| `c1_market.block_trade` | 2026-06-30 | 6天 | 🟠 滞后 |
| `c1_market.convertible_bond_list` | 2026-07-06 | 0天 | ℹ️ 静态型 |
| `c1_market.daily_kline` | 2026-07-02 | 4天 | 🟡 轻微滞后 |
| `c1_market.daily_valuation` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.dragon_tiger` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.etf_benchmark` | 2025-07-21 | 350天 | ℹ️ 静态型 |
| `c1_market.etf_kline_15min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.etf_kline_1min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.etf_kline_30min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.etf_kline_5min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.etf_kline_60min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.etf_list` | 2026-07-06 | 0天 | ℹ️ 静态型 |
| `c1_market.futures_kline` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.hk_daily_kline` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.hk_trade_calendar` | 2026-07-06 | 0天 | ℹ️ 静态型 |
| `c1_market.index_constituent` | 2026-06-30 | 6天 | ℹ️ 静态型 |
| `c1_market.index_kline` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.index_list` | 2025-07-21 | 350天 | ℹ️ 静态型 |
| `c1_market.kline_15min` | 2026-07-02 | 4天 | ℹ️ 实时型 |
| `c1_market.kline_1min` | 2026-07-02 | 4天 | ℹ️ 实时型 |
| `c1_market.kline_30min` | 2026-07-02 | 4天 | ℹ️ 实时型 |
| `c1_market.kline_5min` | 2026-07-02 | 4天 | ℹ️ 实时型 |
| `c1_market.kline_60min` | 2026-07-02 | 4天 | ℹ️ 实时型 |
| `c1_market.kline_daily` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.kline_daily_hfq` | 2026-07-02 | 4天 | 🟡 轻微滞后 |
| `c1_market.kline_daily_none` | 2026-07-02 | 4天 | 🟡 轻微滞后 |
| `c1_market.kline_monthly` | 2026-06-30 | 6天 | 🟠 滞后 |
| `c1_market.kline_monthly_hfq` | 2026-06-30 | 6天 | 🟠 滞后 |
| `c1_market.kline_monthly_none` | 2026-06-30 | 6天 | 🟠 滞后 |
| `c1_market.kline_weekly` | 2026-06-26 | 10天 | 🟠 滞后 |
| `c1_market.kline_weekly_hfq` | 2026-06-26 | 10天 | 🟠 滞后 |
| `c1_market.kline_weekly_none` | 2026-06-26 | 10天 | 🟠 滞后 |
| `c1_market.lof_kline_15min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.lof_kline_1min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.lof_kline_30min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.lof_kline_5min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.lof_kline_60min` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c1_market.macro_data` | 2026-06-30 | 6天 | ℹ️ 静态型 |
| `c1_market.margin_trading` | 2026-06-30 | 6天 | 🟠 滞后 |
| `c1_market.money_flow` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.stock_list` | 2026-07-02 | 4天 | ℹ️ 静态型 |
| `c1_market.tdx_sector_info` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c1_market.tick_history` | 2026-07-02 | 4天 | 🟡 轻微滞后 |
| `c1_market.trade_calendar` | 2026-07-06 | 0天 | ℹ️ 静态型 |
| `c1_market.us_daily_kline` | 2026-07-01 | 5天 | 🟠 滞后 |
| `c1_market.us_index` | 2026-07-02 | 4天 | 🟡 轻微滞后 |

| `c3_fundamental.audit_opinion` | 2026-05-29 | 38天 | ℹ️ 年度型 |
| `c3_fundamental.balance_sheet` | 2026-06-04 | 32天 | ℹ️ 季度型 |
| `c3_fundamental.cashflow_statement` | 2026-06-04 | 32天 | ℹ️ 季度型 |
| `c3_fundamental.disclosure_plan` | 2026-07-02 | 4天 | ℹ️ 静态型 |
| `c3_fundamental.dividend` | 2026-07-01 | 5天 | ℹ️ 事件驱动型 |
| `c3_fundamental.earnings_forecast` | 2026-07-03 | 3天 | ℹ️ 事件驱动型 |
| `c3_fundamental.equity_pledge_detail` | 2026-07-03 | 3天 | ℹ️ 事件驱动型 |
| `c3_fundamental.equity_pledge_summary` | 2026-07-03 | 3天 | 🟡 轻微滞后 |
| `c3_fundamental.express_report` | 2026-07-02 | 4天 | ℹ️ 事件驱动型 |
| `c3_fundamental.financial_indicator` | 2026-06-04 | 32天 | ℹ️ 季度型 |
| `c3_fundamental.income_statement` | 2026-06-04 | 32天 | ℹ️ 季度型 |
| `c3_fundamental.main_business` | 2026-03-31 | 97天 | ℹ️ 季度型 |
| `c3_fundamental.news_data` | 2026-07-03 | 3天 | ℹ️ 实时型 |
| `c3_fundamental.news_news_info` | 2024-07-07 | 729天 | ℹ️ 实时型 |
| `c3_fundamental.news_security` | 2024-08-22 | 683天 | ℹ️ 实时型 |
| `c3_fundamental.restricted_shares` | 2026-07-02 | 4天 | ℹ️ 事件驱动型 |
| `c3_fundamental.rights_issue` | 2026-07-06 | 0天 | ℹ️ 事件驱动型 |
| `c3_fundamental.shareholder_count` | 2026-07-02 | 4天 | ℹ️ 季度型 |
| `c3_fundamental.top10_circulating_shareholders` | 2026-05-15 | 52天 | ℹ️ 季度型 |
| `c3_fundamental.top10_shareholders` | 2026-05-15 | 52天 | ℹ️ 季度型 |

## 字段说明

- **起始时间/截止时间**：自动检测表中的日期字段（优先级：trade_date > announce_date > end_date > report_period > cal_date > ...）
- **标的数**：自动检测标的列（symbol/ts_code/news_id 等）的去重计数
- **数据源**：表中 `data_source` 字段的实际取值（TOP1）
- **更新方式**：元信息标注（每日/实时/事件驱动/季度/年度/静态）
- **新鲜度状态**：基于截止时间与当前日期的差值，静态/事件驱动型表不计滞后
