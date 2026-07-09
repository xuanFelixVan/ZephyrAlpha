---
doc_type: architecture_view
title: 业务数据采集流图 / Data Acquisition Flow
version: "1.0"
status: active
date: 2026-07-10
owner: auto-generator
ttl: permanent
---

# 业务数据采集流图 / Data Acquisition Flow

> 生成时间: 2026-07-06T09:59:11
> 运行日期: 2026-07-10
> 输入真源: `docs/03_modules/_domain_data/data_acquisition_matrix.md`（人类+扫描器维护）
> 输出: 本文档（自动派生产物，禁止手工编辑）

## 概述 / Overview

本文档展示**业务数据库表的数据采集流**——即外部数据源通过哪个采集 Job 把数据灌进哪张业务表。

This document presents the **data acquisition flow of business database tables** — i.e., which external data source feeds which business table through which acquisition Job.

**与 [dataflow_index.md](dataflow_index.md) 的关系 / Relationship with dataflow_index.md**：
- `dataflow_index.md` 画**运行时业务系统流**（tick → K线 → 因子 → 信号 → 订单 → 成交 → 持仓） / draws the **runtime business system flow** (tick → K-line → factor → signal → order → trade → position)
- 本文档画**数据采集流**（iFind/QMT/AKShare 等 → 采集 Job → ClickHouse 业务表） / this document draws the **data acquisition flow** (iFind/QMT/AKShare etc. → acquisition Job → ClickHouse business tables)
- 两者正交互补，共同构成数据全景。 / The two are orthogonal and complementary, together forming the full data landscape.

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 采集任务总数 / Total Tasks | 61 |
| 唯一业务表数 / Unique Tables | 54 |
| 数据源数 / Data Sources | 8 |
| 调度时段数 / Schedule Slots | 5 |
| 数据库数 / Databases | 2 |

### 按状态统计 / By Status

| 状态 / Status | 任务数 / Tasks | 占比 / Ratio |
|------|--------|------|
| 已配置定时 / Scheduled | 44 | 72.1% |
| 已禁用 / Disabled | 2 | 3.3% |
| 待接入(空表) / Pending | 15 | 24.6% |

### 按数据源统计 / By Data Source

| 数据源 / Source | 任务数 / Tasks | 占比 / Ratio |
|--------|--------|------|
| AKShare | 4 | 6.6% |
| BaoStock | 3 | 4.9% |
| 同花顺iFind | 19 | 31.1% |
| 迅投QMT | 25 | 41.0% |
| RSS | 1 | 1.6% |
| 通达信 | 3 | 4.9% |
| TickFlow | 4 | 6.6% |
| Tushare | 2 | 3.3% |

### 按调度时段统计 / By Schedule Slot

| 调度时段 / Slot | 任务数 / Tasks | 占比 / Ratio |
|----------|--------|------|
| 周末财务 / 10:00 周六 (Weekend Financial) | 13 | 21.3% |
| 盘后事件 / 18:00 周一-五 (Post-close Event) | 13 | 21.3% |
| 盘后日K / 16:30 周一-五 (Post-close Daily K) | 12 | 19.7% |
| 盘后资金 / 17:00 周一-五 (Post-close Capital) | 11 | 18.0% |
| 静态数据 / 09:00 月初 (Static Data) | 12 | 19.7% |

### 按数据库统计 / By Database

| 数据库 / DB | 任务数 / Tasks | 唯一表数 / Unique Tables |
|--------|--------|----------|
| c1_market | 40 | 33 |
| c3_fundamental | 21 | 21 |

### 数据新鲜度统计 / Data Freshness Statistics（基于最新日期 vs 运行日期 / Based on latest date vs run date）

| 新鲜度 / Freshness | 任务数 / Tasks | 说明 / Note |
|--------|--------|------|
| 🟢 当日 / Today | 0 | 滞后 ≤1 天 / Lag ≤1d |
| 🟡 滞后1-3天 / Lag 1-3d | 0 | 滞后 2-3 天 / Lag 2-3d |
| 🟠 滞后4-7天 / Lag 4-7d | 12 | 滞后 4-7 天 / Lag 4-7d |
| 🔴 滞后>7天 / Lag >7d | 16 | 滞后 >7 天 / Lag >7d |
| ⚫ 未知 / Unknown | 33 | 无最新日期 / No latest date |

## Mermaid 图表 / Charts

> **图例说明 / Legend**：
> - **绿色圆角矩形 / Green rounded rect** = 采集 Job / Acquisition Job（jobNode）
> - **蓝色矩形 / Blue rect** = 业务表 Dataset / Business Table（dsNode）
> - **粉色圆角矩形 / Pink rounded rect** = 外部数据源 / External Source（srcNode）
> - **黄色圆角矩形 / Yellow rounded rect** = 调度时段内的 Job / Job in schedule slot（按时段图 / by-slot chart）
> - 表节点前缀图标 / Table node prefix icon 🟢/🟡/🟠/🔴/⚫ = 数据新鲜度 / Data freshness

### 图1：按数据源分组 / By Data Source（外部源 → 采集Job → 业务表 / Source → Job → Table）

> 8 数据源 / Sources / 54 业务表 / Tables / 61 采集边 / Edges

```mermaid
flowchart LR
    subgraph S_akshare["AKShare（4 任务 / 4 tasks）"]
        J10["macro_data_incremental<br/>宏观数据增量"]:::jobNode
        J29["analyst_forecast_incremental<br/>分析师一致预期增量"]:::jobNode
        J34["rights_issue_incremental<br/>分红配股增量"]:::jobNode
        J56["macro_data_full_refresh<br/>宏观数据全量刷新"]:::jobNode
    end
    subgraph S_baostock["BaoStock（3 任务 / 3 tasks）"]
        J50["trade_calendar_refresh<br/>交易日历全量刷新"]:::jobNode
        J52["index_constituent_refresh<br/>沪深300成分股全量刷新"]:::jobNode
        J55["kline_daily_full_refresh<br/>日K线全量刷新"]:::jobNode
    end
    subgraph S_ifind["同花顺iFind（19 任务 / 19 tasks）"]
        J1["adj_factor_incremental<br/>复权因子增量"]:::jobNode
        J2["kline_daily_hfq_incremental<br/>后复权日K线增量"]:::jobNode
        J3["kline_daily_incremental<br/>不复权日K线增量"]:::jobNode
        J4["daily_valuation_incremental<br/>每日估值（PE/PB）增量"]:::jobNode
        J5["index_kline_incremental<br/>指数日K线增量"]:::jobNode
        J6["margin_trading_incremental<br/>融资融券增量"]:::jobNode
        J7["block_trade_incremental<br/>大宗交易增量"]:::jobNode
        J8["dragon_tiger_incremental<br/>龙虎榜增量"]:::jobNode
        J11["money_flow_incremental<br/>资金流向增量"]:::jobNode
        J12["hk_connect_flow_incremental<br/>沪深港通资金增量"]:::jobNode
        J17["kline_weekly_incremental<br/>周K线增量"]:::jobNode
        J18["kline_monthly_incremental<br/>月K线增量"]:::jobNode
        J27["share_unlock_incremental<br/>限售解禁增量"]:::jobNode
        J32["audit_opinion_incremental<br/>审计意见增量"]:::jobNode
        J35["equity_pledge_incremental<br/>股权质押增量"]:::jobNode
        J36["equity_pledge_summary_incremental<br/>股权质押摘要增量"]:::jobNode
        J53["industry_class_ifind_refresh<br/>申万/中证行业分类全量刷新"]:::jobNode
        J59["money_flow_full_refresh<br/>资金流向全量刷新"]:::jobNode
        J60["daily_valuation_full_refresh<br/>估值数据全量刷新"]:::jobNode
    end
    subgraph S_miniqmt["迅投QMT（25 任务 / 25 tasks）"]
        J9["hk_daily_kline_incremental<br/>港股日K线增量"]:::jobNode
        J13["futures_kline_incremental<br/>期货行情K线增量"]:::jobNode
        J14["futures_position_incremental<br/>期货持仓增量"]:::jobNode
        J19["kline_1min_incremental<br/>1分钟K线增量"]:::jobNode
        J20["kline_5min_incremental<br/>5分钟K线增量"]:::jobNode
        J21["kline_15min_incremental<br/>15分钟K线增量"]:::jobNode
        J22["kline_30min_incremental<br/>30分钟K线增量"]:::jobNode
        J23["kline_60min_incremental<br/>60分钟K线增量"]:::jobNode
        J28["shareholder_incremental<br/>股东数据增量"]:::jobNode
        J30["earnings_forecast_incremental<br/>盈利预测增量"]:::jobNode
        J31["express_report_incremental<br/>业绩快报增量"]:::jobNode
        J33["dividend_incremental<br/>分红送股增量"]:::jobNode
        J37["balance_sheet_incremental<br/>资产负债表增量"]:::jobNode
        J38["income_statement_incremental<br/>利润表增量"]:::jobNode
        J39["cashflow_statement_incremental<br/>现金流量表增量"]:::jobNode
        J40["financial_indicator_incremental<br/>财务指标增量"]:::jobNode
        J41["main_business_incremental<br/>主营业务增量"]:::jobNode
        J44["option_iv_surface_incremental<br/>期权IV曲面增量"]:::jobNode
        J45["convertible_bond_iv_incremental<br/>可转债IV增量"]:::jobNode
        J46["futures_term_structure_incremental<br/>期货期限结构增量"]:::jobNode
        J47["tick_data_snapshot<br/>3秒Tick快照"]:::jobNode
        J48["auction_snapshot<br/>集合竞价快照"]:::jobNode
        J49["index_quote_snapshot<br/>指数3秒实时行情快照"]:::jobNode
        J51["stock_list_refresh<br/>股票列表全量刷新"]:::jobNode
        J61["kline_5min_history_backfill<br/>5分钟K线历史回补"]:::jobNode
    end
    subgraph S_rss["RSS（1 任务 / 1 tasks）"]
        J24["news_data_incremental<br/>财经新闻增量"]:::jobNode
    end
    subgraph S_tdx["通达信（3 任务 / 3 tasks）"]
        J42["industry_class_refresh<br/>板块分类全量刷新"]:::jobNode
        J43["sector_kline_incremental<br/>板块指数K线增量"]:::jobNode
        J54["sector_constituent_refresh<br/>板块成分股全量刷新"]:::jobNode
    end
    subgraph S_tickflow["TickFlow（4 任务 / 4 tasks）"]
        J15["us_daily_kline_incremental<br/>美股日K线增量"]:::jobNode
        J16["us_index_incremental<br/>美股指数增量"]:::jobNode
        J57["us_daily_kline_full_refresh<br/>美股日K线全量刷新"]:::jobNode
        J58["us_index_full_refresh<br/>美股指数全量刷新"]:::jobNode
    end
    subgraph S_tushare["Tushare（2 任务 / 2 tasks）"]
        J25["news_news_info_incremental<br/>新闻快讯增量"]:::jobNode
        J26["news_security_incremental<br/>证券新闻增量"]:::jobNode
    end
    subgraph DB_c1_market["c1_market（33 表 / 33 tables）"]
        T_c1_market_adj_factor["🟠 c1_market.adj_factor<br/>1879.8万行 / 18.798M rows<br/>2026-07-03"]:::dsNode
        T_c1_market_auction_snapshot["⚫ c1_market.auction_snapshot<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_block_trade["🔴 c1_market.block_trade<br/>16.2万行 / 161.71K rows<br/>2026-06-30"]:::dsNode
        T_c1_market_convertible_bond_iv["⚫ c1_market.convertible_bond_iv<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_daily_valuation["🟠 c1_market.daily_valuation<br/>878.8万行 / 8.788M rows<br/>2026-07-03"]:::dsNode
        T_c1_market_dragon_tiger["🟠 c1_market.dragon_tiger<br/>16.8万行 / 167.96K rows<br/>2026-07-03"]:::dsNode
        T_c1_market_futures_kline["🟠 c1_market.futures_kline<br/>306.7万行 / 3.067M rows<br/>2026-07-03"]:::dsNode
        T_c1_market_futures_position["⚫ c1_market.futures_position<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_futures_term_structure["⚫ c1_market.futures_term_structure<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_hk_connect_flow["⚫ c1_market.hk_connect_flow<br/>-行 / -"]:::dsNode
        T_c1_market_hk_daily_kline["🟠 c1_market.hk_daily_kline<br/>146.0万行 / 1.460M rows<br/>2026-07-03"]:::dsNode
        T_c1_market_index_constituent["🔴 c1_market.index_constituent<br/>6.0万行 / 59.58K rows<br/>2026-06-30"]:::dsNode
        T_c1_market_index_kline["🟠 c1_market.index_kline<br/>306.6万行 / 3.066M rows<br/>2026-07-03"]:::dsNode
        T_c1_market_index_quote["⚫ c1_market.index_quote<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_kline_15min["🔴 c1_market.kline_15min<br/>2.54亿行 / 254.314M rows<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_1min["🔴 c1_market.kline_1min<br/>38.31亿行 / 3830.589M rows<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_30min["🔴 c1_market.kline_30min<br/>1.27亿行 / 127.157M rows<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_5min["⚫ c1_market.kline_5min<br/>9.76亿行 / 975.947M rows"]:::dsNode
        T_c1_market_kline_60min["🔴 c1_market.kline_60min<br/>6357.8万行 / 63.578M rows<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_daily["🟠 c1_market.kline_daily<br/>1812.5万行 / 18.125M rows<br/>2026-07-03"]:::dsNode
        T_c1_market_kline_daily_hfq["🔴 c1_market.kline_daily_hfq<br/>1811.9万行 / 18.119M rows<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_monthly["🔴 c1_market.kline_monthly<br/>89.9万行 / 898.74K rows<br/>2026-06-30"]:::dsNode
        T_c1_market_kline_weekly["🔴 c1_market.kline_weekly<br/>376.9万行 / 3.769M rows<br/>2026-06-26"]:::dsNode
        T_c1_market_macro_data["🔴 c1_market.macro_data<br/>5853行 / 5853 rows<br/>2026-06-30"]:::dsNode
        T_c1_market_margin_trading["🔴 c1_market.margin_trading<br/>109.6万行 / 1.096M rows<br/>2026-06-30"]:::dsNode
        T_c1_market_money_flow["🟠 c1_market.money_flow<br/>49.5万行 / 494.66K rows<br/>2026-07-03"]:::dsNode
        T_c1_market_option_iv_surface["⚫ c1_market.option_iv_surface<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_sector_kline["⚫ c1_market.sector_kline<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_stock_list["⚫ c1_market.stock_list<br/>5534行 / 5534 rows"]:::dsNode
        T_c1_market_tick_data["⚫ c1_market.tick_data<br/>0行 / 0 rows"]:::dsNode
        T_c1_market_trade_calendar["⚫ c1_market.trade_calendar<br/>1.3万行 / 13.16K rows"]:::dsNode
        T_c1_market_us_daily_kline["🔴 c1_market.us_daily_kline<br/>16.7万行 / 167.18K rows<br/>2026-07-01"]:::dsNode
        T_c1_market_us_index["🔴 c1_market.us_index<br/>2.2万行 / 22.44K rows<br/>2026-07-02"]:::dsNode
    end
    subgraph DB_c3_fundamental["c3_fundamental（21 表 / 21 tables）"]
        T_c3_fundamental_analyst_forecast["⚫ c3_fundamental.analyst_forecast<br/>0行 / 0 rows"]:::dsNode
        T_c3_fundamental_audit_opinion["⚫ c3_fundamental.audit_opinion<br/>9.6万行 / 96.01K rows"]:::dsNode
        T_c3_fundamental_balance_sheet["⚫ c3_fundamental.balance_sheet<br/>33.5万行 / 334.52K rows"]:::dsNode
        T_c3_fundamental_cashflow_statement["⚫ c3_fundamental.cashflow_statement<br/>30.5万行 / 305.23K rows"]:::dsNode
        T_c3_fundamental_dividend["⚫ c3_fundamental.dividend<br/>11.5万行 / 115.35K rows"]:::dsNode
        T_c3_fundamental_earnings_forecast["⚫ c3_fundamental.earnings_forecast<br/>12.6万行 / 125.58K rows"]:::dsNode
        T_c3_fundamental_equity_pledge["⚫ c3_fundamental.equity_pledge<br/>0行 / 0 rows"]:::dsNode
        T_c3_fundamental_equity_pledge_summary["🟠 c3_fundamental.equity_pledge_summary<br/>172.3万行 / 1.723M rows<br/>2026-07-03"]:::dsNode
        T_c3_fundamental_express_report["⚫ c3_fundamental.express_report<br/>3.0万行 / 29.63K rows"]:::dsNode
        T_c3_fundamental_financial_indicator["⚫ c3_fundamental.financial_indicator<br/>34.8万行 / 347.98K rows"]:::dsNode
        T_c3_fundamental_income_statement["⚫ c3_fundamental.income_statement<br/>34.1万行 / 340.96K rows"]:::dsNode
        T_c3_fundamental_industry_class["⚫ c3_fundamental.industry_class<br/>0行 / 0 rows"]:::dsNode
        T_c3_fundamental_industry_class_ifind["⚫ c3_fundamental.industry_class_ifind<br/>0行 / 0 rows"]:::dsNode
        T_c3_fundamental_main_business["⚫ c3_fundamental.main_business<br/>209.0万行 / 2.090M rows"]:::dsNode
        T_c3_fundamental_news_data["⚫ c3_fundamental.news_data<br/>287行 / 287 rows"]:::dsNode
        T_c3_fundamental_news_news_info["⚫ c3_fundamental.news_news_info<br/>960.9万行 / 9.609M rows"]:::dsNode
        T_c3_fundamental_news_security["⚫ c3_fundamental.news_security<br/>372.9万行 / 3.729M rows"]:::dsNode
        T_c3_fundamental_rights_issue["⚫ c3_fundamental.rights_issue<br/>8.1万行 / 81.03K rows"]:::dsNode
        T_c3_fundamental_sector_constituent["⚫ c3_fundamental.sector_constituent<br/>0行 / 0 rows"]:::dsNode
        T_c3_fundamental_share_unlock["⚫ c3_fundamental.share_unlock<br/>0行 / 0 rows"]:::dsNode
        T_c3_fundamental_shareholder["⚫ c3_fundamental.shareholder<br/>0行 / 0 rows"]:::dsNode
    end
    J1 --> T_c1_market_adj_factor
    J2 --> T_c1_market_kline_daily_hfq
    J3 --> T_c1_market_kline_daily
    J4 --> T_c1_market_daily_valuation
    J5 --> T_c1_market_index_kline
    J6 --> T_c1_market_margin_trading
    J7 --> T_c1_market_block_trade
    J8 --> T_c1_market_dragon_tiger
    J9 --> T_c1_market_hk_daily_kline
    J10 --> T_c1_market_macro_data
    J11 --> T_c1_market_money_flow
    J12 --> T_c1_market_hk_connect_flow
    J13 --> T_c1_market_futures_kline
    J14 --> T_c1_market_futures_position
    J15 --> T_c1_market_us_daily_kline
    J16 --> T_c1_market_us_index
    J17 --> T_c1_market_kline_weekly
    J18 --> T_c1_market_kline_monthly
    J19 --> T_c1_market_kline_1min
    J20 --> T_c1_market_kline_5min
    J21 --> T_c1_market_kline_15min
    J22 --> T_c1_market_kline_30min
    J23 --> T_c1_market_kline_60min
    J24 --> T_c3_fundamental_news_data
    J25 --> T_c3_fundamental_news_news_info
    J26 --> T_c3_fundamental_news_security
    J27 --> T_c3_fundamental_share_unlock
    J28 --> T_c3_fundamental_shareholder
    J29 --> T_c3_fundamental_analyst_forecast
    J30 --> T_c3_fundamental_earnings_forecast
    J31 --> T_c3_fundamental_express_report
    J32 --> T_c3_fundamental_audit_opinion
    J33 --> T_c3_fundamental_dividend
    J34 --> T_c3_fundamental_rights_issue
    J35 --> T_c3_fundamental_equity_pledge
    J36 --> T_c3_fundamental_equity_pledge_summary
    J37 --> T_c3_fundamental_balance_sheet
    J38 --> T_c3_fundamental_income_statement
    J39 --> T_c3_fundamental_cashflow_statement
    J40 --> T_c3_fundamental_financial_indicator
    J41 --> T_c3_fundamental_main_business
    J42 --> T_c3_fundamental_industry_class
    J43 --> T_c1_market_sector_kline
    J44 --> T_c1_market_option_iv_surface
    J45 --> T_c1_market_convertible_bond_iv
    J46 --> T_c1_market_futures_term_structure
    J47 --> T_c1_market_tick_data
    J48 --> T_c1_market_auction_snapshot
    J49 --> T_c1_market_index_quote
    J50 --> T_c1_market_trade_calendar
    J51 --> T_c1_market_stock_list
    J52 --> T_c1_market_index_constituent
    J53 --> T_c3_fundamental_industry_class_ifind
    J54 --> T_c3_fundamental_sector_constituent
    J55 --> T_c1_market_kline_daily
    J56 --> T_c1_market_macro_data
    J57 --> T_c1_market_us_daily_kline
    J58 --> T_c1_market_us_index
    J59 --> T_c1_market_money_flow
    J60 --> T_c1_market_daily_valuation
    J61 --> T_c1_market_kline_5min

    classDef jobNode fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20
    classDef dsNode fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
```

### 图2：按调度时段分组 / By Schedule Slot（5档时段 → 采集Job → 业务表 / Slots → Job → Table）

> 5 调度时段 / Slots / 61 采集边 / Edges

```mermaid
flowchart LR
    subgraph SL________10_00_["周末财务 / 10:00 周六 (Weekend Financial)（13 任务 / 13 tasks）"]
        J37["balance_sheet_incremental<br/>资产负债表增量"]:::jobNode
        J38["income_statement_incremental<br/>利润表增量"]:::jobNode
        J39["cashflow_statement_incremental<br/>现金流量表增量"]:::jobNode
        J40["financial_indicator_incremental<br/>财务指标增量"]:::jobNode
        J41["main_business_incremental<br/>主营业务增量"]:::jobNode
        J42["industry_class_refresh<br/>板块分类全量刷新"]:::jobNode
        J43["sector_kline_incremental<br/>板块指数K线增量"]:::jobNode
        J44["option_iv_surface_incremental<br/>期权IV曲面增量"]:::jobNode
        J45["convertible_bond_iv_incremental<br/>可转债IV增量"]:::jobNode
        J46["futures_term_structure_incremental<br/>期货期限结构增量"]:::jobNode
        J47["tick_data_snapshot<br/>3秒Tick快照"]:::jobNode
        J48["auction_snapshot<br/>集合竞价快照"]:::jobNode
        J49["index_quote_snapshot<br/>指数3秒实时行情快照"]:::jobNode
    end
    subgraph SL______18_00_["盘后事件 / 18:00 周一-五 (Post-close Event)（13 任务 / 13 tasks）"]
        J24["news_data_incremental<br/>财经新闻增量"]:::jobNode
        J25["news_news_info_incremental<br/>新闻快讯增量"]:::jobNode
        J26["news_security_incremental<br/>证券新闻增量"]:::jobNode
        J27["share_unlock_incremental<br/>限售解禁增量"]:::jobNode
        J28["shareholder_incremental<br/>股东数据增量"]:::jobNode
        J29["analyst_forecast_incremental<br/>分析师一致预期增量"]:::jobNode
        J30["earnings_forecast_incremental<br/>盈利预测增量"]:::jobNode
        J31["express_report_incremental<br/>业绩快报增量"]:::jobNode
        J32["audit_opinion_incremental<br/>审计意见增量"]:::jobNode
        J33["dividend_incremental<br/>分红送股增量"]:::jobNode
        J34["rights_issue_incremental<br/>分红配股增量"]:::jobNode
        J35["equity_pledge_incremental<br/>股权质押增量"]:::jobNode
        J36["equity_pledge_summary_incremental<br/>股权质押摘要增量"]:::jobNode
    end
    subgraph SL____K_16_30_["盘后日K / 16:30 周一-五 (Post-close Daily K)（12 任务 / 12 tasks）"]
        J1["adj_factor_incremental<br/>复权因子增量"]:::jobNode
        J2["kline_daily_hfq_incremental<br/>后复权日K线增量"]:::jobNode
        J3["kline_daily_incremental<br/>不复权日K线增量"]:::jobNode
        J4["daily_valuation_incremental<br/>每日估值（PE/PB）增量"]:::jobNode
        J5["index_kline_incremental<br/>指数日K线增量"]:::jobNode
        J17["kline_weekly_incremental<br/>周K线增量"]:::jobNode
        J18["kline_monthly_incremental<br/>月K线增量"]:::jobNode
        J19["kline_1min_incremental<br/>1分钟K线增量"]:::jobNode
        J20["kline_5min_incremental<br/>5分钟K线增量"]:::jobNode
        J21["kline_15min_incremental<br/>15分钟K线增量"]:::jobNode
        J22["kline_30min_incremental<br/>30分钟K线增量"]:::jobNode
        J23["kline_60min_incremental<br/>60分钟K线增量"]:::jobNode
    end
    subgraph SL______17_00_["盘后资金 / 17:00 周一-五 (Post-close Capital)（11 任务 / 11 tasks）"]
        J6["margin_trading_incremental<br/>融资融券增量"]:::jobNode
        J7["block_trade_incremental<br/>大宗交易增量"]:::jobNode
        J8["dragon_tiger_incremental<br/>龙虎榜增量"]:::jobNode
        J9["hk_daily_kline_incremental<br/>港股日K线增量"]:::jobNode
        J10["macro_data_incremental<br/>宏观数据增量"]:::jobNode
        J11["money_flow_incremental<br/>资金流向增量"]:::jobNode
        J12["hk_connect_flow_incremental<br/>沪深港通资金增量"]:::jobNode
        J13["futures_kline_incremental<br/>期货行情K线增量"]:::jobNode
        J14["futures_position_incremental<br/>期货持仓增量"]:::jobNode
        J15["us_daily_kline_incremental<br/>美股日K线增量"]:::jobNode
        J16["us_index_incremental<br/>美股指数增量"]:::jobNode
    end
    subgraph SL________09_00_["静态数据 / 09:00 月初 (Static Data)（12 任务 / 12 tasks）"]
        J50["trade_calendar_refresh<br/>交易日历全量刷新"]:::jobNode
        J51["stock_list_refresh<br/>股票列表全量刷新"]:::jobNode
        J52["index_constituent_refresh<br/>沪深300成分股全量刷新"]:::jobNode
        J53["industry_class_ifind_refresh<br/>申万/中证行业分类全量刷新"]:::jobNode
        J54["sector_constituent_refresh<br/>板块成分股全量刷新"]:::jobNode
        J55["kline_daily_full_refresh<br/>日K线全量刷新"]:::jobNode
        J56["macro_data_full_refresh<br/>宏观数据全量刷新"]:::jobNode
        J57["us_daily_kline_full_refresh<br/>美股日K线全量刷新"]:::jobNode
        J58["us_index_full_refresh<br/>美股指数全量刷新"]:::jobNode
        J59["money_flow_full_refresh<br/>资金流向全量刷新"]:::jobNode
        J60["daily_valuation_full_refresh<br/>估值数据全量刷新"]:::jobNode
        J61["kline_5min_history_backfill<br/>5分钟K线历史回补"]:::jobNode
    end
    T_c1_market_adj_factor["🟠 c1_market.adj_factor<br/>1879.8万行 / 18.798M rows<br/>2026-07-03"]:::dsNode
    T_c1_market_kline_daily_hfq["🔴 c1_market.kline_daily_hfq<br/>1811.9万行 / 18.119M rows<br/>2026-07-02"]:::dsNode
    T_c1_market_kline_daily["🟠 c1_market.kline_daily<br/>1812.5万行 / 18.125M rows<br/>2026-07-03"]:::dsNode
    T_c1_market_daily_valuation["🟠 c1_market.daily_valuation<br/>878.8万行 / 8.788M rows<br/>2026-07-03"]:::dsNode
    T_c1_market_index_kline["🟠 c1_market.index_kline<br/>306.6万行 / 3.066M rows<br/>2026-07-03"]:::dsNode
    T_c1_market_margin_trading["🔴 c1_market.margin_trading<br/>109.6万行 / 1.096M rows<br/>2026-06-30"]:::dsNode
    T_c1_market_block_trade["🔴 c1_market.block_trade<br/>16.2万行 / 161.71K rows<br/>2026-06-30"]:::dsNode
    T_c1_market_dragon_tiger["🟠 c1_market.dragon_tiger<br/>16.8万行 / 167.96K rows<br/>2026-07-03"]:::dsNode
    T_c1_market_hk_daily_kline["🟠 c1_market.hk_daily_kline<br/>146.0万行 / 1.460M rows<br/>2026-07-03"]:::dsNode
    T_c1_market_macro_data["🔴 c1_market.macro_data<br/>5853行 / 5853 rows<br/>2026-06-30"]:::dsNode
    T_c1_market_money_flow["🟠 c1_market.money_flow<br/>49.5万行 / 494.66K rows<br/>2026-07-03"]:::dsNode
    T_c1_market_hk_connect_flow["⚫ c1_market.hk_connect_flow<br/>-行 / -"]:::dsNode
    T_c1_market_futures_kline["🟠 c1_market.futures_kline<br/>306.7万行 / 3.067M rows<br/>2026-07-03"]:::dsNode
    T_c1_market_futures_position["⚫ c1_market.futures_position<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_us_daily_kline["🔴 c1_market.us_daily_kline<br/>16.7万行 / 167.18K rows<br/>2026-07-01"]:::dsNode
    T_c1_market_us_index["🔴 c1_market.us_index<br/>2.2万行 / 22.44K rows<br/>2026-07-02"]:::dsNode
    T_c1_market_kline_weekly["🔴 c1_market.kline_weekly<br/>376.9万行 / 3.769M rows<br/>2026-06-26"]:::dsNode
    T_c1_market_kline_monthly["🔴 c1_market.kline_monthly<br/>89.9万行 / 898.74K rows<br/>2026-06-30"]:::dsNode
    T_c1_market_kline_1min["🔴 c1_market.kline_1min<br/>38.31亿行 / 3830.589M rows<br/>2026-07-02"]:::dsNode
    T_c1_market_kline_5min["⚫ c1_market.kline_5min<br/>9.76亿行 / 975.947M rows"]:::dsNode
    T_c1_market_kline_15min["🔴 c1_market.kline_15min<br/>2.54亿行 / 254.314M rows<br/>2026-07-02"]:::dsNode
    T_c1_market_kline_30min["🔴 c1_market.kline_30min<br/>1.27亿行 / 127.157M rows<br/>2026-07-02"]:::dsNode
    T_c1_market_kline_60min["🔴 c1_market.kline_60min<br/>6357.8万行 / 63.578M rows<br/>2026-07-02"]:::dsNode
    T_c3_fundamental_news_data["⚫ c3_fundamental.news_data<br/>287行 / 287 rows"]:::dsNode
    T_c3_fundamental_news_news_info["⚫ c3_fundamental.news_news_info<br/>960.9万行 / 9.609M rows"]:::dsNode
    T_c3_fundamental_news_security["⚫ c3_fundamental.news_security<br/>372.9万行 / 3.729M rows"]:::dsNode
    T_c3_fundamental_share_unlock["⚫ c3_fundamental.share_unlock<br/>0行 / 0 rows"]:::dsNode
    T_c3_fundamental_shareholder["⚫ c3_fundamental.shareholder<br/>0行 / 0 rows"]:::dsNode
    T_c3_fundamental_analyst_forecast["⚫ c3_fundamental.analyst_forecast<br/>0行 / 0 rows"]:::dsNode
    T_c3_fundamental_earnings_forecast["⚫ c3_fundamental.earnings_forecast<br/>12.6万行 / 125.58K rows"]:::dsNode
    T_c3_fundamental_express_report["⚫ c3_fundamental.express_report<br/>3.0万行 / 29.63K rows"]:::dsNode
    T_c3_fundamental_audit_opinion["⚫ c3_fundamental.audit_opinion<br/>9.6万行 / 96.01K rows"]:::dsNode
    T_c3_fundamental_dividend["⚫ c3_fundamental.dividend<br/>11.5万行 / 115.35K rows"]:::dsNode
    T_c3_fundamental_rights_issue["⚫ c3_fundamental.rights_issue<br/>8.1万行 / 81.03K rows"]:::dsNode
    T_c3_fundamental_equity_pledge["⚫ c3_fundamental.equity_pledge<br/>0行 / 0 rows"]:::dsNode
    T_c3_fundamental_equity_pledge_summary["🟠 c3_fundamental.equity_pledge_summary<br/>172.3万行 / 1.723M rows<br/>2026-07-03"]:::dsNode
    T_c3_fundamental_balance_sheet["⚫ c3_fundamental.balance_sheet<br/>33.5万行 / 334.52K rows"]:::dsNode
    T_c3_fundamental_income_statement["⚫ c3_fundamental.income_statement<br/>34.1万行 / 340.96K rows"]:::dsNode
    T_c3_fundamental_cashflow_statement["⚫ c3_fundamental.cashflow_statement<br/>30.5万行 / 305.23K rows"]:::dsNode
    T_c3_fundamental_financial_indicator["⚫ c3_fundamental.financial_indicator<br/>34.8万行 / 347.98K rows"]:::dsNode
    T_c3_fundamental_main_business["⚫ c3_fundamental.main_business<br/>209.0万行 / 2.090M rows"]:::dsNode
    T_c3_fundamental_industry_class["⚫ c3_fundamental.industry_class<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_sector_kline["⚫ c1_market.sector_kline<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_option_iv_surface["⚫ c1_market.option_iv_surface<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_convertible_bond_iv["⚫ c1_market.convertible_bond_iv<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_futures_term_structure["⚫ c1_market.futures_term_structure<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_tick_data["⚫ c1_market.tick_data<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_auction_snapshot["⚫ c1_market.auction_snapshot<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_index_quote["⚫ c1_market.index_quote<br/>0行 / 0 rows"]:::dsNode
    T_c1_market_trade_calendar["⚫ c1_market.trade_calendar<br/>1.3万行 / 13.16K rows"]:::dsNode
    T_c1_market_stock_list["⚫ c1_market.stock_list<br/>5534行 / 5534 rows"]:::dsNode
    T_c1_market_index_constituent["🔴 c1_market.index_constituent<br/>6.0万行 / 59.58K rows<br/>2026-06-30"]:::dsNode
    T_c3_fundamental_industry_class_ifind["⚫ c3_fundamental.industry_class_ifind<br/>0行 / 0 rows"]:::dsNode
    T_c3_fundamental_sector_constituent["⚫ c3_fundamental.sector_constituent<br/>0行 / 0 rows"]:::dsNode
    J1 --> T_c1_market_adj_factor
    J2 --> T_c1_market_kline_daily_hfq
    J3 --> T_c1_market_kline_daily
    J4 --> T_c1_market_daily_valuation
    J5 --> T_c1_market_index_kline
    J6 --> T_c1_market_margin_trading
    J7 --> T_c1_market_block_trade
    J8 --> T_c1_market_dragon_tiger
    J9 --> T_c1_market_hk_daily_kline
    J10 --> T_c1_market_macro_data
    J11 --> T_c1_market_money_flow
    J12 --> T_c1_market_hk_connect_flow
    J13 --> T_c1_market_futures_kline
    J14 --> T_c1_market_futures_position
    J15 --> T_c1_market_us_daily_kline
    J16 --> T_c1_market_us_index
    J17 --> T_c1_market_kline_weekly
    J18 --> T_c1_market_kline_monthly
    J19 --> T_c1_market_kline_1min
    J20 --> T_c1_market_kline_5min
    J21 --> T_c1_market_kline_15min
    J22 --> T_c1_market_kline_30min
    J23 --> T_c1_market_kline_60min
    J24 --> T_c3_fundamental_news_data
    J25 --> T_c3_fundamental_news_news_info
    J26 --> T_c3_fundamental_news_security
    J27 --> T_c3_fundamental_share_unlock
    J28 --> T_c3_fundamental_shareholder
    J29 --> T_c3_fundamental_analyst_forecast
    J30 --> T_c3_fundamental_earnings_forecast
    J31 --> T_c3_fundamental_express_report
    J32 --> T_c3_fundamental_audit_opinion
    J33 --> T_c3_fundamental_dividend
    J34 --> T_c3_fundamental_rights_issue
    J35 --> T_c3_fundamental_equity_pledge
    J36 --> T_c3_fundamental_equity_pledge_summary
    J37 --> T_c3_fundamental_balance_sheet
    J38 --> T_c3_fundamental_income_statement
    J39 --> T_c3_fundamental_cashflow_statement
    J40 --> T_c3_fundamental_financial_indicator
    J41 --> T_c3_fundamental_main_business
    J42 --> T_c3_fundamental_industry_class
    J43 --> T_c1_market_sector_kline
    J44 --> T_c1_market_option_iv_surface
    J45 --> T_c1_market_convertible_bond_iv
    J46 --> T_c1_market_futures_term_structure
    J47 --> T_c1_market_tick_data
    J48 --> T_c1_market_auction_snapshot
    J49 --> T_c1_market_index_quote
    J50 --> T_c1_market_trade_calendar
    J51 --> T_c1_market_stock_list
    J52 --> T_c1_market_index_constituent
    J53 --> T_c3_fundamental_industry_class_ifind
    J54 --> T_c3_fundamental_sector_constituent
    J55 --> T_c1_market_kline_daily
    J56 --> T_c1_market_macro_data
    J57 --> T_c1_market_us_daily_kline
    J58 --> T_c1_market_us_index
    J59 --> T_c1_market_money_flow
    J60 --> T_c1_market_daily_valuation
    J61 --> T_c1_market_kline_5min

    classDef jobNode fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#f57f17
    classDef dsNode fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
```

### 图3：按数据库分组 / By Database（外部源 → ClickHouse 库 → 业务表 / Source → DB → Table）

> 2 数据库 / DBs / 55 源→表 边（去重）/ Source→Table edges (deduped)

```mermaid
flowchart LR
    SRC_akshare[("AKShare")]:::srcNode
    SRC_baostock[("BaoStock")]:::srcNode
    SRC_ifind[("同花顺iFind")]:::srcNode
    SRC_miniqmt[("迅投QMT")]:::srcNode
    SRC_rss[("RSS")]:::srcNode
    SRC_tdx[("通达信")]:::srcNode
    SRC_tickflow[("TickFlow")]:::srcNode
    SRC_tushare[("Tushare")]:::srcNode
    subgraph DB_c1_market["c1_market（33 表 / 33 tables）"]
        T_c1_market_adj_factor["🟠 c1_market.adj_factor<br/>1879.8万行 / 18.798M rows<br/>源: ifind<br/>2026-07-03"]:::dsNode
        T_c1_market_auction_snapshot["⚫ c1_market.auction_snapshot<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_block_trade["🔴 c1_market.block_trade<br/>16.2万行 / 161.71K rows<br/>源: ifind<br/>2026-06-30"]:::dsNode
        T_c1_market_convertible_bond_iv["⚫ c1_market.convertible_bond_iv<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_daily_valuation["🟠 c1_market.daily_valuation<br/>878.8万行 / 8.788M rows<br/>源: ifind<br/>2026-07-03"]:::dsNode
        T_c1_market_dragon_tiger["🟠 c1_market.dragon_tiger<br/>16.8万行 / 167.96K rows<br/>源: ifind<br/>2026-07-03"]:::dsNode
        T_c1_market_futures_kline["🟠 c1_market.futures_kline<br/>306.7万行 / 3.067M rows<br/>源: miniqmt<br/>2026-07-03"]:::dsNode
        T_c1_market_futures_position["⚫ c1_market.futures_position<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_futures_term_structure["⚫ c1_market.futures_term_structure<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_hk_connect_flow["⚫ c1_market.hk_connect_flow<br/>-行 / -<br/>源: ifind"]:::dsNode
        T_c1_market_hk_daily_kline["🟠 c1_market.hk_daily_kline<br/>146.0万行 / 1.460M rows<br/>源: miniqmt<br/>2026-07-03"]:::dsNode
        T_c1_market_index_constituent["🔴 c1_market.index_constituent<br/>6.0万行 / 59.58K rows<br/>源: baostock<br/>2026-06-30"]:::dsNode
        T_c1_market_index_kline["🟠 c1_market.index_kline<br/>306.6万行 / 3.066M rows<br/>源: ifind<br/>2026-07-03"]:::dsNode
        T_c1_market_index_quote["⚫ c1_market.index_quote<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_kline_15min["🔴 c1_market.kline_15min<br/>2.54亿行 / 254.314M rows<br/>源: miniqmt<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_1min["🔴 c1_market.kline_1min<br/>38.31亿行 / 3830.589M rows<br/>源: miniqmt<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_30min["🔴 c1_market.kline_30min<br/>1.27亿行 / 127.157M rows<br/>源: miniqmt<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_5min["⚫ c1_market.kline_5min<br/>9.76亿行 / 975.947M rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_kline_60min["🔴 c1_market.kline_60min<br/>6357.8万行 / 63.578M rows<br/>源: miniqmt<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_daily["🟠 c1_market.kline_daily<br/>1812.5万行 / 18.125M rows<br/>源: baostock/ifind<br/>2026-07-03"]:::dsNode
        T_c1_market_kline_daily_hfq["🔴 c1_market.kline_daily_hfq<br/>1811.9万行 / 18.119M rows<br/>源: ifind<br/>2026-07-02"]:::dsNode
        T_c1_market_kline_monthly["🔴 c1_market.kline_monthly<br/>89.9万行 / 898.74K rows<br/>源: ifind<br/>2026-06-30"]:::dsNode
        T_c1_market_kline_weekly["🔴 c1_market.kline_weekly<br/>376.9万行 / 3.769M rows<br/>源: ifind<br/>2026-06-26"]:::dsNode
        T_c1_market_macro_data["🔴 c1_market.macro_data<br/>5853行 / 5853 rows<br/>源: akshare<br/>2026-06-30"]:::dsNode
        T_c1_market_margin_trading["🔴 c1_market.margin_trading<br/>109.6万行 / 1.096M rows<br/>源: ifind<br/>2026-06-30"]:::dsNode
        T_c1_market_money_flow["🟠 c1_market.money_flow<br/>49.5万行 / 494.66K rows<br/>源: ifind<br/>2026-07-03"]:::dsNode
        T_c1_market_option_iv_surface["⚫ c1_market.option_iv_surface<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_sector_kline["⚫ c1_market.sector_kline<br/>0行 / 0 rows<br/>源: tdx"]:::dsNode
        T_c1_market_stock_list["⚫ c1_market.stock_list<br/>5534行 / 5534 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_tick_data["⚫ c1_market.tick_data<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
        T_c1_market_trade_calendar["⚫ c1_market.trade_calendar<br/>1.3万行 / 13.16K rows<br/>源: baostock"]:::dsNode
        T_c1_market_us_daily_kline["🔴 c1_market.us_daily_kline<br/>16.7万行 / 167.18K rows<br/>源: tickflow<br/>2026-07-01"]:::dsNode
        T_c1_market_us_index["🔴 c1_market.us_index<br/>2.2万行 / 22.44K rows<br/>源: tickflow<br/>2026-07-02"]:::dsNode
    end
    subgraph DB_c3_fundamental["c3_fundamental（21 表 / 21 tables）"]
        T_c3_fundamental_analyst_forecast["⚫ c3_fundamental.analyst_forecast<br/>0行 / 0 rows<br/>源: akshare"]:::dsNode
        T_c3_fundamental_audit_opinion["⚫ c3_fundamental.audit_opinion<br/>9.6万行 / 96.01K rows<br/>源: ifind"]:::dsNode
        T_c3_fundamental_balance_sheet["⚫ c3_fundamental.balance_sheet<br/>33.5万行 / 334.52K rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_cashflow_statement["⚫ c3_fundamental.cashflow_statement<br/>30.5万行 / 305.23K rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_dividend["⚫ c3_fundamental.dividend<br/>11.5万行 / 115.35K rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_earnings_forecast["⚫ c3_fundamental.earnings_forecast<br/>12.6万行 / 125.58K rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_equity_pledge["⚫ c3_fundamental.equity_pledge<br/>0行 / 0 rows<br/>源: ifind"]:::dsNode
        T_c3_fundamental_equity_pledge_summary["🟠 c3_fundamental.equity_pledge_summary<br/>172.3万行 / 1.723M rows<br/>源: ifind<br/>2026-07-03"]:::dsNode
        T_c3_fundamental_express_report["⚫ c3_fundamental.express_report<br/>3.0万行 / 29.63K rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_financial_indicator["⚫ c3_fundamental.financial_indicator<br/>34.8万行 / 347.98K rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_income_statement["⚫ c3_fundamental.income_statement<br/>34.1万行 / 340.96K rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_industry_class["⚫ c3_fundamental.industry_class<br/>0行 / 0 rows<br/>源: tdx"]:::dsNode
        T_c3_fundamental_industry_class_ifind["⚫ c3_fundamental.industry_class_ifind<br/>0行 / 0 rows<br/>源: ifind"]:::dsNode
        T_c3_fundamental_main_business["⚫ c3_fundamental.main_business<br/>209.0万行 / 2.090M rows<br/>源: miniqmt"]:::dsNode
        T_c3_fundamental_news_data["⚫ c3_fundamental.news_data<br/>287行 / 287 rows<br/>源: rss"]:::dsNode
        T_c3_fundamental_news_news_info["⚫ c3_fundamental.news_news_info<br/>960.9万行 / 9.609M rows<br/>源: tushare"]:::dsNode
        T_c3_fundamental_news_security["⚫ c3_fundamental.news_security<br/>372.9万行 / 3.729M rows<br/>源: tushare"]:::dsNode
        T_c3_fundamental_rights_issue["⚫ c3_fundamental.rights_issue<br/>8.1万行 / 81.03K rows<br/>源: akshare"]:::dsNode
        T_c3_fundamental_sector_constituent["⚫ c3_fundamental.sector_constituent<br/>0行 / 0 rows<br/>源: tdx"]:::dsNode
        T_c3_fundamental_share_unlock["⚫ c3_fundamental.share_unlock<br/>0行 / 0 rows<br/>源: ifind"]:::dsNode
        T_c3_fundamental_shareholder["⚫ c3_fundamental.shareholder<br/>0行 / 0 rows<br/>源: miniqmt"]:::dsNode
    end
    SRC_ifind --> T_c1_market_adj_factor
    SRC_ifind --> T_c1_market_kline_daily_hfq
    SRC_ifind --> T_c1_market_kline_daily
    SRC_ifind --> T_c1_market_daily_valuation
    SRC_ifind --> T_c1_market_index_kline
    SRC_ifind --> T_c1_market_margin_trading
    SRC_ifind --> T_c1_market_block_trade
    SRC_ifind --> T_c1_market_dragon_tiger
    SRC_miniqmt --> T_c1_market_hk_daily_kline
    SRC_akshare --> T_c1_market_macro_data
    SRC_ifind --> T_c1_market_money_flow
    SRC_ifind --> T_c1_market_hk_connect_flow
    SRC_miniqmt --> T_c1_market_futures_kline
    SRC_miniqmt --> T_c1_market_futures_position
    SRC_tickflow --> T_c1_market_us_daily_kline
    SRC_tickflow --> T_c1_market_us_index
    SRC_ifind --> T_c1_market_kline_weekly
    SRC_ifind --> T_c1_market_kline_monthly
    SRC_miniqmt --> T_c1_market_kline_1min
    SRC_miniqmt --> T_c1_market_kline_5min
    SRC_miniqmt --> T_c1_market_kline_15min
    SRC_miniqmt --> T_c1_market_kline_30min
    SRC_miniqmt --> T_c1_market_kline_60min
    SRC_rss --> T_c3_fundamental_news_data
    SRC_tushare --> T_c3_fundamental_news_news_info
    SRC_tushare --> T_c3_fundamental_news_security
    SRC_ifind --> T_c3_fundamental_share_unlock
    SRC_miniqmt --> T_c3_fundamental_shareholder
    SRC_akshare --> T_c3_fundamental_analyst_forecast
    SRC_miniqmt --> T_c3_fundamental_earnings_forecast
    SRC_miniqmt --> T_c3_fundamental_express_report
    SRC_ifind --> T_c3_fundamental_audit_opinion
    SRC_miniqmt --> T_c3_fundamental_dividend
    SRC_akshare --> T_c3_fundamental_rights_issue
    SRC_ifind --> T_c3_fundamental_equity_pledge
    SRC_ifind --> T_c3_fundamental_equity_pledge_summary
    SRC_miniqmt --> T_c3_fundamental_balance_sheet
    SRC_miniqmt --> T_c3_fundamental_income_statement
    SRC_miniqmt --> T_c3_fundamental_cashflow_statement
    SRC_miniqmt --> T_c3_fundamental_financial_indicator
    SRC_miniqmt --> T_c3_fundamental_main_business
    SRC_tdx --> T_c3_fundamental_industry_class
    SRC_tdx --> T_c1_market_sector_kline
    SRC_miniqmt --> T_c1_market_option_iv_surface
    SRC_miniqmt --> T_c1_market_convertible_bond_iv
    SRC_miniqmt --> T_c1_market_futures_term_structure
    SRC_miniqmt --> T_c1_market_tick_data
    SRC_miniqmt --> T_c1_market_auction_snapshot
    SRC_miniqmt --> T_c1_market_index_quote
    SRC_baostock --> T_c1_market_trade_calendar
    SRC_miniqmt --> T_c1_market_stock_list
    SRC_baostock --> T_c1_market_index_constituent
    SRC_ifind --> T_c3_fundamental_industry_class_ifind
    SRC_tdx --> T_c3_fundamental_sector_constituent
    SRC_baostock --> T_c1_market_kline_daily

    classDef srcNode fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c
    classDef dsNode fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1
```

## 交叉矩阵 / Cross Matrix

### 数据源 × 调度时段 / Source × Slot

| 数据源 \ 调度时段 | 周末财务 / 10:00 周六 (Weekend Financial) | 盘后事件 / 18:00 周一-五 (Post-close Event) | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 静态数据 / 09:00 月初 (Static Data) | 合计 |
|---|---|---|---|---|---|---|
| AKShare | - | 2 | - | 1 | 1 | 4 |
| BaoStock | - | - | - | - | 3 | 3 |
| 同花顺iFind | - | 4 | 7 | 5 | 3 | 19 |
| 迅投QMT | 11 | 4 | 5 | 3 | 2 | 25 |
| RSS | - | 1 | - | - | - | 1 |
| 通达信 | 2 | - | - | - | 1 | 3 |
| TickFlow | - | - | - | 2 | 2 | 4 |
| Tushare | - | 2 | - | - | - | 2 |
| **合计** | 13 | 13 | 12 | 11 | 12 | **61** |


### 数据源 × 状态 / Source × Status

| 数据源 / Source | 已配置定时 / Scheduled | 已禁用 / Disabled | 待接入(空表) / Pending | 合计 / Total |
|---|---|---|---|---|
| AKShare | 3 | - | 1 | 4 |
| BaoStock | 3 | - | - | 3 |
| 同花顺iFind | 15 | 1 | 3 | 19 |
| 迅投QMT | 16 | 1 | 8 | 25 |
| RSS | 1 | - | - | 1 |
| 通达信 | - | - | 3 | 3 |
| TickFlow | 4 | - | - | 4 |
| Tushare | 2 | - | - | 2 |


## 完整表清单 / Full Table List

| # | task_id | 表名 / Table | 数据库 / DB | 数据源 / Source | 调度时段 / Slot | 行数 / Rows | 最新日期 / Latest | 新鲜度 / Freshness | 状态 / Status |
|---|---------|------|--------|--------|---------|------|---------|--------|------|
| 1 | adj_factor_incremental | c1_market.adj_factor | c1_market | 同花顺iFind | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 1879.8万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 2 | kline_daily_hfq_incremental | c1_market.kline_daily_hfq | c1_market | 同花顺iFind | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 1811.9万 | 2026-07-02 | 🔴 滞后8天 | 已配置定时 / Scheduled |
| 3 | kline_daily_incremental | c1_market.kline_daily | c1_market | 同花顺iFind | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 1812.5万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 4 | daily_valuation_incremental | c1_market.daily_valuation | c1_market | 同花顺iFind | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 878.8万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 5 | index_kline_incremental | c1_market.index_kline | c1_market | 同花顺iFind | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 306.6万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 6 | margin_trading_incremental | c1_market.margin_trading | c1_market | 同花顺iFind | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 109.6万 | 2026-06-30 | 🔴 滞后10天 | 已配置定时 / Scheduled |
| 7 | block_trade_incremental | c1_market.block_trade | c1_market | 同花顺iFind | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 16.2万 | 2026-06-30 | 🔴 滞后10天 | 已配置定时 / Scheduled |
| 8 | dragon_tiger_incremental | c1_market.dragon_tiger | c1_market | 同花顺iFind | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 16.8万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 9 | hk_daily_kline_incremental | c1_market.hk_daily_kline | c1_market | 迅投QMT | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 146.0万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 10 | macro_data_incremental | c1_market.macro_data | c1_market | AKShare | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 5853 | 2026-06-30 | 🔴 滞后10天 | 已配置定时 / Scheduled |
| 11 | money_flow_incremental | c1_market.money_flow | c1_market | 同花顺iFind | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 49.5万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 12 | hk_connect_flow_incremental | c1_market.hk_connect_flow | c1_market | 同花顺iFind | 盘后资金 / 17:00 周一-五 (Post-close Capital) | - | - | ⚫ 未知(无日期) | 已禁用 / Disabled |
| 13 | futures_kline_incremental | c1_market.futures_kline | c1_market | 迅投QMT | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 306.7万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 14 | futures_position_incremental | c1_market.futures_position | c1_market | 迅投QMT | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 15 | us_daily_kline_incremental | c1_market.us_daily_kline | c1_market | TickFlow | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 16.7万 | 2026-07-01 | 🔴 滞后9天 | 已配置定时 / Scheduled |
| 16 | us_index_incremental | c1_market.us_index | c1_market | TickFlow | 盘后资金 / 17:00 周一-五 (Post-close Capital) | 2.2万 | 2026-07-02 | 🔴 滞后8天 | 已配置定时 / Scheduled |
| 17 | kline_weekly_incremental | c1_market.kline_weekly | c1_market | 同花顺iFind | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 376.9万 | 2026-06-26 | 🔴 滞后14天 | 已配置定时 / Scheduled |
| 18 | kline_monthly_incremental | c1_market.kline_monthly | c1_market | 同花顺iFind | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 89.9万 | 2026-06-30 | 🔴 滞后10天 | 已配置定时 / Scheduled |
| 19 | kline_1min_incremental | c1_market.kline_1min | c1_market | 迅投QMT | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 38.31亿 | 2026-07-02 | 🔴 滞后8天 | 已配置定时 / Scheduled |
| 20 | kline_5min_incremental | c1_market.kline_5min | c1_market | 迅投QMT | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 9.76亿 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 21 | kline_15min_incremental | c1_market.kline_15min | c1_market | 迅投QMT | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 2.54亿 | 2026-07-02 | 🔴 滞后8天 | 已配置定时 / Scheduled |
| 22 | kline_30min_incremental | c1_market.kline_30min | c1_market | 迅投QMT | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 1.27亿 | 2026-07-02 | 🔴 滞后8天 | 已配置定时 / Scheduled |
| 23 | kline_60min_incremental | c1_market.kline_60min | c1_market | 迅投QMT | 盘后日K / 16:30 周一-五 (Post-close Daily K) | 6357.8万 | 2026-07-02 | 🔴 滞后8天 | 已配置定时 / Scheduled |
| 24 | news_data_incremental | c3_fundamental.news_data | c3_fundamental | RSS | 盘后事件 / 18:00 周一-五 (Post-close Event) | 287 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 25 | news_news_info_incremental | c3_fundamental.news_news_info | c3_fundamental | Tushare | 盘后事件 / 18:00 周一-五 (Post-close Event) | 960.9万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 26 | news_security_incremental | c3_fundamental.news_security | c3_fundamental | Tushare | 盘后事件 / 18:00 周一-五 (Post-close Event) | 372.9万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 27 | share_unlock_incremental | c3_fundamental.share_unlock | c3_fundamental | 同花顺iFind | 盘后事件 / 18:00 周一-五 (Post-close Event) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 28 | shareholder_incremental | c3_fundamental.shareholder | c3_fundamental | 迅投QMT | 盘后事件 / 18:00 周一-五 (Post-close Event) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 29 | analyst_forecast_incremental | c3_fundamental.analyst_forecast | c3_fundamental | AKShare | 盘后事件 / 18:00 周一-五 (Post-close Event) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 30 | earnings_forecast_incremental | c3_fundamental.earnings_forecast | c3_fundamental | 迅投QMT | 盘后事件 / 18:00 周一-五 (Post-close Event) | 12.6万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 31 | express_report_incremental | c3_fundamental.express_report | c3_fundamental | 迅投QMT | 盘后事件 / 18:00 周一-五 (Post-close Event) | 3.0万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 32 | audit_opinion_incremental | c3_fundamental.audit_opinion | c3_fundamental | 同花顺iFind | 盘后事件 / 18:00 周一-五 (Post-close Event) | 9.6万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 33 | dividend_incremental | c3_fundamental.dividend | c3_fundamental | 迅投QMT | 盘后事件 / 18:00 周一-五 (Post-close Event) | 11.5万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 34 | rights_issue_incremental | c3_fundamental.rights_issue | c3_fundamental | AKShare | 盘后事件 / 18:00 周一-五 (Post-close Event) | 8.1万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 35 | equity_pledge_incremental | c3_fundamental.equity_pledge | c3_fundamental | 同花顺iFind | 盘后事件 / 18:00 周一-五 (Post-close Event) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 36 | equity_pledge_summary_incremental | c3_fundamental.equity_pledge_summary | c3_fundamental | 同花顺iFind | 盘后事件 / 18:00 周一-五 (Post-close Event) | 172.3万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 37 | balance_sheet_incremental | c3_fundamental.balance_sheet | c3_fundamental | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 33.5万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 38 | income_statement_incremental | c3_fundamental.income_statement | c3_fundamental | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 34.1万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 39 | cashflow_statement_incremental | c3_fundamental.cashflow_statement | c3_fundamental | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 30.5万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 40 | financial_indicator_incremental | c3_fundamental.financial_indicator | c3_fundamental | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 34.8万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 41 | main_business_incremental | c3_fundamental.main_business | c3_fundamental | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 209.0万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 42 | industry_class_refresh | c3_fundamental.industry_class | c3_fundamental | 通达信 | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 43 | sector_kline_incremental | c1_market.sector_kline | c1_market | 通达信 | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 44 | option_iv_surface_incremental | c1_market.option_iv_surface | c1_market | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 45 | convertible_bond_iv_incremental | c1_market.convertible_bond_iv | c1_market | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 46 | futures_term_structure_incremental | c1_market.futures_term_structure | c1_market | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 47 | tick_data_snapshot | c1_market.tick_data | c1_market | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 48 | auction_snapshot | c1_market.auction_snapshot | c1_market | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 49 | index_quote_snapshot | c1_market.index_quote | c1_market | 迅投QMT | 周末财务 / 10:00 周六 (Weekend Financial) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 50 | trade_calendar_refresh | c1_market.trade_calendar | c1_market | BaoStock | 静态数据 / 09:00 月初 (Static Data) | 1.3万 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 51 | stock_list_refresh | c1_market.stock_list | c1_market | 迅投QMT | 静态数据 / 09:00 月初 (Static Data) | 5534 | - | ⚫ 未知(无日期) | 已配置定时 / Scheduled |
| 52 | index_constituent_refresh | c1_market.index_constituent | c1_market | BaoStock | 静态数据 / 09:00 月初 (Static Data) | 6.0万 | 2026-06-30 | 🔴 滞后10天 | 已配置定时 / Scheduled |
| 53 | industry_class_ifind_refresh | c3_fundamental.industry_class_ifind | c3_fundamental | 同花顺iFind | 静态数据 / 09:00 月初 (Static Data) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 54 | sector_constituent_refresh | c3_fundamental.sector_constituent | c3_fundamental | 通达信 | 静态数据 / 09:00 月初 (Static Data) | 0 | - | ⚫ 未知(无日期) | 待接入(空表) / Pending |
| 55 | kline_daily_full_refresh | c1_market.kline_daily | c1_market | BaoStock | 静态数据 / 09:00 月初 (Static Data) | 1812.5万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 56 | macro_data_full_refresh | c1_market.macro_data | c1_market | AKShare | 静态数据 / 09:00 月初 (Static Data) | 5853 | 2026-06-30 | 🔴 滞后10天 | 已配置定时 / Scheduled |
| 57 | us_daily_kline_full_refresh | c1_market.us_daily_kline | c1_market | TickFlow | 静态数据 / 09:00 月初 (Static Data) | 16.7万 | 2026-07-01 | 🔴 滞后9天 | 已配置定时 / Scheduled |
| 58 | us_index_full_refresh | c1_market.us_index | c1_market | TickFlow | 静态数据 / 09:00 月初 (Static Data) | 2.2万 | 2026-07-02 | 🔴 滞后8天 | 已配置定时 / Scheduled |
| 59 | money_flow_full_refresh | c1_market.money_flow | c1_market | 同花顺iFind | 静态数据 / 09:00 月初 (Static Data) | 49.5万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 60 | daily_valuation_full_refresh | c1_market.daily_valuation | c1_market | 同花顺iFind | 静态数据 / 09:00 月初 (Static Data) | 878.8万 | 2026-07-03 | 🟠 滞后7天 | 已配置定时 / Scheduled |
| 61 | kline_5min_history_backfill | c1_market.kline_5min | c1_market | 迅投QMT | 静态数据 / 09:00 月初 (Static Data) | 9.76亿 | - | ⚫ 未知(无日期) | 已禁用 / Disabled |

## 变更历史 / Changelog

- **2026-07-10**: 初次生成 / Initial generation（generate_data_acquisition_flow.py）

