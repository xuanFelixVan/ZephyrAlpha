---
title: 数据目录
doc_type: architecture_view
status: Active
ttl: permanent
generated_at: "2026-07-06 05:23:34"
generator: tmp/generate_data_catalog.py
language: zh
description: 数据目录唯一真源——含4视角章节（总览/回测/实盘/能力矩阵）
---

# 数据目录

> 自动生成时间：**2026-07-06 05:23:34**
> 真源：`data_acquisition_plan.md`（需求清单，人类维护）+ ClickHouse 实时扫描（现状字段）
> 减法逻辑：需求清单（人类想要什么）- ClickHouse现状（已有什么）= 缺口 × 可获取性 = 4态分类
> 专业实践：**一个目录 + 多视角章节**（非多份独立文档，避免漂移）

## 顶部总览

- **数据项总数**：97 项
- **已有数据**：73 项（自动更新 0，手动触发 73）
- **数据缺口**：24 项（可接入 23，无法获取 1）
- **有实时能力**：3 项
- **有历史数据**：69 项

| 状态 | 含义 | 数量 | 占比 |
|------|------|------|------|
| ✅ **稳定获取** | 有数据 + 已配置自动每日更新 | 0 | 0% |
| ⚠️ **手动触发** | 有数据 + 需手动运行脚本 | 73 | 75% |
| 🔵 **待接入** | 无数据 + 数据源支持但表为空 | 23 | 23% |
| ❌ **无法获取** | 无数据 + 试用账号不支持 | 1 | 1% |

## §1 数据目录总览（真源视图）

> 全量数据项，按库分组，含所有字段。这是唯一真源，其他章节都是对此数据的过滤/排序。

### C1 市场数据（`c1_market`）

| 表名 | 中文名 | 起始 | 截止 | 标的数 | 行数 | 数据源字段 | 更新方式 | 可获取性 | 自动更新 | 状态 |
|------|--------|------|------|--------|--------|-----------|----------|---------|---------|------|
| `c1_market.kline_daily` | 日K线(前复权) | 1990-12-19 | 2026-07-03 | 5895 | 18,124,798 | bdpan_qfq | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.adj_factor` | 复权因子 | 1990-12-19 | 2026-07-03 | 5876 | 18,797,511 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_weekly` | 周K线 | 1990-12-20 | 2026-06-26 | 5856 | 3,769,062 | bdpan_qfq | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_monthly` | 月K线 | 1990-12-25 | 2026-06-30 | 5854 | 898,736 | bdpan_qfq | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_index` | 指数K线 | 1990-12-19 | 2026-07-03 | 1031 | 3,066,374 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_1min` | 1分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 3,830,588,993 | local_intraday | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_15min` | 15分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 254,313,641 | local_intraday | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_30min` | 30分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 127,156,825 | local_intraday | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_60min` | 60分钟K线 | 2000-06-09 | 2026-07-02 | 5480 | 63,578,425 | local_intraday | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_5min` | 5分钟K线 | 2000-06-09 | 2026-07-02 | 5238 | 975,946,697 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.daily_valuation` | 估值数据 | 1990-12-19 | 2026-07-03 | 5708 | 8,787,985 | local_valuation | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.money_flow` | 资金流向 | 2025-04-25 | 2026-07-03 | 5632 | 494,658 | local_moneyflow | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.tick_data` | 3秒Tick逐笔 | — | — | 0 | 0 | — | 实时 | ✅已验证 | 未接入 | 🔵 待接入 |
| `c1_market.auction_snapshot` | 集合竞价快照 | — | — | 0 | 0 | — | 实时 | ✅API可用 | 未接入 | 🔵 待接入 |
| `c1_market.index_quote` | 指数3秒行情 | — | — | 0 | 0 | — | 实时 | ✅已验证 | 未接入 | 🔵 待接入 |
| `c1_market.option_iv_surface` | 期权IV曲面 | — | — | 0 | 0 | — | 每日 | 🔶需计算 | 未接入 | 🔵 待接入 |
| `c1_market.convertible_bond_iv` | 可转债隐含波动率 | — | — | 0 | 0 | — | 每日 | 🔶需计算 | 未接入 | 🔵 待接入 |
| `c1_market.futures_position` | 期货持仓 | — | — | 0 | 0 | — | 每日 | ✅已验证 | 未接入 | 🔵 待接入 |
| `c1_market.futures_term_structure` | 期货期限结构 | — | — | 0 | 0 | — | 每日 | 🔶需计算 | 未接入 | 🔵 待接入 |
| `c1_market._pepb_staging` | PE/PB暂存表 | 2025-11-12 | 2026-07-03 | 5533 | 839,473 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.analyst_forecast` | 分析师预测 | 2026-07-04 | 2026-07-04 | 2857 | 8,373 | akshare | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.block_trade` | 大宗交易 | 2010-01-31 | 2026-06-30 | 4963 | 161,708 | ifind | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.convertible_bond_list` | 可转债列表 | 1996-01-01 | 2026-07-06 | — | 1,142 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.daily_kline` | A股日K线(原始) | 1990-12-19 | 2026-07-02 | 5898 | 18,122,192 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.dragon_tiger` | 龙虎榜 | 2006-07-17 | 2026-07-03 | 5047 | 167,961 | ifind | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.etf_benchmark` | ETF基准 | 1991-04-04 | 2025-07-21 | — | 732 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_etf_15min` | kline_etf_15min | 2005-02-23 | 2026-07-03 | 1581 | 22,813,741 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_etf_1min` | kline_etf_1min | 2005-02-23 | 2026-07-03 | 1581 | 343,553,536 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_etf_30min` | kline_etf_30min | 2005-02-23 | 2026-07-03 | 1581 | 11,398,303 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_etf_5min` | ETF K线(多周期) | 2005-02-23 | 2026-07-03 | 1581 | 68,389,859 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_etf_60min` | kline_etf_60min | 2005-02-23 | 2026-07-03 | 1581 | 5,699,152 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.etf_list` | ETF列表 | 2005-02-23 | 2026-07-06 | — | 1,764 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.futures_kline` | 期货K线 | 2010-01-04 | 2026-07-03 | 17592 | 3,067,213 | qmt | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.hk_daily_kline` | 港股日K线 | 2015-05-29 | 2026-07-03 | 923 | 1,459,915 | qmt | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.hk_stock_list` | 港股股票列表 | — | — | — | 4,688 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.hk_trade_calendar` | 港股交易日历 | 1980-01-01 | 2026-07-06 | — | 17,167 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.index_constituent` | 指数成分股 | 2009-12-31 | 2026-06-30 | 3551 | 59,583 | ifind | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.index_list` | 指数列表 | 1991-04-04 | 2025-07-21 | 732 | 732 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.industry_class` | 行业分类 | — | — | 5534 | 16,600 | ifind | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_daily_hfq` | A股日K线(后复权) | 1990-12-19 | 2026-07-02 | 5895 | 18,119,282 | bdpan_hfq | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_daily_none` | A股日K线(不复权) | 1990-12-19 | 2026-07-02 | 5893 | 18,118,948 | bdpan_none | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_monthly_hfq` | A股月K线(后复权) | 1990-12-25 | 2026-06-30 | 5854 | 898,736 | bdpan_hfq | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_monthly_none` | A股月K线(不复权) | 1990-12-25 | 2026-06-30 | 5854 | 904,274 | bdpan_none | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_weekly_hfq` | A股周K线(后复权) | 1990-12-20 | 2026-06-26 | 5853 | 3,768,249 | bdpan_hfq | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_weekly_none` | A股周K线(不复权) | 1990-12-20 | 2026-06-26 | 5856 | 3,769,209 | bdpan_none | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_lof_15min` | kline_lof_15min | 2010-08-16 | 2026-07-03 | 2750 | 12,064,844 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_lof_1min` | kline_lof_1min | 2010-08-16 | 2026-07-03 | 2750 | 181,720,142 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_lof_30min` | kline_lof_30min | 2010-08-16 | 2026-07-03 | 2750 | 6,032,451 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_lof_5min` | LOF K线(多周期) | 2010-08-16 | 2026-07-03 | 2750 | 36,194,482 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.kline_lof_60min` | kline_lof_60min | 2010-08-16 | 2026-07-03 | 2750 | 3,016,252 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.lof_list` | LOF列表 | — | — | — | 361 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.macro_data` | 宏观经济数据 | 2006-03-31 | 2026-06-30 | 27 | 5,853 | akshare | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.margin_trading` | 融资融券 | 2010-01-31 | 2026-06-30 | 5534 | 1,095,732 | ifind | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.stock_list` | A股股票列表 | 1990-12-01 | 2026-07-02 | 5534 | 5,534 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.tdx_market_index` | 通达信板块指数 | — | — | 50 | 50 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.tdx_sector_info` | 通达信板块信息 | 2026-07-03 | 2026-07-03 | 90 | 90 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.tick_data` | Tick数据(历史) | 2000-07-14 | 2026-07-02 | 8740 | 7,143,133,916 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.trade_calendar` | 交易日历 | 1990-12-19 | 2026-07-06 | — | 13,162 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.us_daily_kline` | 美股日K线 | 2006-08-15 | 2026-07-01 | 34 | 167,175 | tickflow | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c1_market.us_index` | 美股指数 | 1993-01-29 | 2026-07-02 | 3 | 22,441 | tickflow | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |

### C3 基本面数据（`c3_fundamental`）

| 表名 | 中文名 | 起始 | 截止 | 标的数 | 行数 | 数据源字段 | 更新方式 | 可获取性 | 自动更新 | 状态 |
|------|--------|------|------|--------|--------|-----------|----------|---------|---------|------|
| `c3_fundamental.balance_sheet` | 资产负债表 | 1990-03-21 | 2026-06-04 | 5857 | 334,521 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.income_statement` | 利润表 | 1995-01-05 | 2026-06-04 | 5857 | 340,959 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.cashflow_statement` | 现金流量表 | 1999-01-30 | 2026-06-04 | 5848 | 305,230 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.financial_indicator` | 财务指标 | 1990-03-21 | 2026-06-04 | 5860 | 347,984 | bdpan | 每日 | ✅API可用 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.main_business` | 主营业务 | 2000-12-31 | 2026-03-31 | 5850 | 2,090,334 | bdpan | 每日 | ✅API可用 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.dividend` | 分红送股 | 1991-03-17 | 2026-07-01 | 5823 | 115,351 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.earnings_forecast` | 盈利预测 | 1999-01-08 | 2026-07-03 | 5707 | 125,582 | bdpan | 每日 | ✅API可用 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.audit_opinion` | 审计意见 | 1998-02-21 | 2026-05-29 | 5852 | 96,010 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.express_report` | 业绩快报 | 2005-01-08 | 2026-07-02 | 4395 | 29,627 | bdpan | 每日 | ✅API可用 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.rights_issue` | 分红配股 | 1991-03-03 | 2026-07-06 | 5823 | 81,028 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.equity_pledge_summary` | 股权质押 | 2014-03-07 | 2026-07-03 | 4440 | 1,723,182 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.disclosure_plan` | 财报披露计划 | 2001-02-06 | 2026-07-02 | 5858 | 305,711 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.equity_pledge_detail` | 股权质押明细 | 2003-06-10 | 2026-07-03 | 3572 | 297,056 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.news_data` | 新闻数据(爬虫) | 2026-06-07 | 2026-07-03 | 287 | 287 | wallstreetcn | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.news_news_info` | 新闻信息(tushare) | 2000-01-01 | 2024-07-07 | 9608745 | 9,609,089 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.news_security` | 新闻-股票关联 | 1997-04-30 | 2024-08-22 | 12590 | 3,728,723 | — | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.restricted_shares` | 限售解禁 | 2005-01-10 | 2026-07-02 | 5747 | 11,359,865 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.shareholder_count` | 股东户数 | 1993-01-12 | 2026-07-02 | 5840 | 501,972 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.top10_circulating_shareholders` | 十大流通股东 | 2005-01-29 | 2026-05-15 | 5768 | 2,145,705 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |
| `c3_fundamental.top10_shareholders` | 十大股东 | 2005-01-29 | 2026-05-15 | 5789 | 1,447,675 | bdpan | 每日 | ✅已验证 | 手动触发 | ⚠️ 手动触发 |

### 未建表（有需求）（`—`）

| 表名 | 中文名 | 起始 | 截止 | 标的数 | 行数 | 数据源字段 | 更新方式 | 可获取性 | 自动更新 | 状态 |
|------|--------|------|------|--------|--------|-----------|----------|---------|---------|------|
| — | 龙虎榜 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 融资融券 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 大宗交易 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 沪深港通资金 | — | — | — | — | — | 静态 | ❌试用不可用 | 未接入 | ❌ 无法获取 |
| — | 股东数据 | — | — | — | — | — | 静态 | ✅API可用 | 未接入 | 🔵 待接入 |
| — | 限售解禁 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 交易日历 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 股票列表 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 行业分类 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 指数成分股 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 期货行情K线 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 美股日K线 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 美股指数 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 港股日K线 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 宏观经济 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |
| — | 新闻舆情 | — | — | — | — | — | 静态 | ✅API可用 | 未接入 | 🔵 待接入 |
| — | 分析师预期 | — | — | — | — | — | 静态 | ✅已验证 | 未接入 | 🔵 待接入 |

## §2 回测视角（历史数据覆盖）

> 关注历史覆盖范围。筛选：有历史数据的项。排序：按行数降序。

共 **69** 项有历史数据。

| 数据项 | 表 | 起始 | 截止 | 标的数 | 行数 | 数据源 | 更新方式 |
|--------|-----|------|------|--------|------|--------|----------|
| Tick数据(历史) | `c1_market.tick_data` | 2000-07-14 | 2026-07-02 | 8740 | 7,143,133,916 | bdpan | 每日 |
| 1分钟K线 | `c1_market.kline_1min` | 2000-06-09 | 2026-07-02 | 5480 | 3,830,588,993 | local_intraday | 每日 |
| 5分钟K线 | `c1_market.kline_5min` | 2000-06-09 | 2026-07-02 | 5238 | 975,946,697 | bdpan | 每日 |
| kline_etf_1min | `c1_market.kline_etf_1min` | 2005-02-23 | 2026-07-03 | 1581 | 343,553,536 | bdpan | 每日 |
| 15分钟K线 | `c1_market.kline_15min` | 2000-06-09 | 2026-07-02 | 5480 | 254,313,641 | local_intraday | 每日 |
| kline_lof_1min | `c1_market.kline_lof_1min` | 2010-08-16 | 2026-07-03 | 2750 | 181,720,142 | bdpan | 每日 |
| 30分钟K线 | `c1_market.kline_30min` | 2000-06-09 | 2026-07-02 | 5480 | 127,156,825 | local_intraday | 每日 |
| ETF K线(多周期) | `c1_market.kline_etf_5min` | 2005-02-23 | 2026-07-03 | 1581 | 68,389,859 | bdpan | 每日 |
| 60分钟K线 | `c1_market.kline_60min` | 2000-06-09 | 2026-07-02 | 5480 | 63,578,425 | local_intraday | 每日 |
| LOF K线(多周期) | `c1_market.kline_lof_5min` | 2010-08-16 | 2026-07-03 | 2750 | 36,194,482 | bdpan | 每日 |
| kline_etf_15min | `c1_market.kline_etf_15min` | 2005-02-23 | 2026-07-03 | 1581 | 22,813,741 | bdpan | 每日 |
| 复权因子 | `c1_market.adj_factor` | 1990-12-19 | 2026-07-03 | 5876 | 18,797,511 | bdpan | 每日 |
| 日K线(前复权) | `c1_market.kline_daily` | 1990-12-19 | 2026-07-03 | 5895 | 18,124,798 | bdpan_qfq | 每日 |
| A股日K线(原始) | `c1_market.daily_kline` | 1990-12-19 | 2026-07-02 | 5898 | 18,122,192 | bdpan | 每日 |
| A股日K线(后复权) | `c1_market.kline_daily_hfq` | 1990-12-19 | 2026-07-02 | 5895 | 18,119,282 | bdpan_hfq | 每日 |
| A股日K线(不复权) | `c1_market.kline_daily_none` | 1990-12-19 | 2026-07-02 | 5893 | 18,118,948 | bdpan_none | 每日 |
| kline_lof_15min | `c1_market.kline_lof_15min` | 2010-08-16 | 2026-07-03 | 2750 | 12,064,844 | bdpan | 每日 |
| kline_etf_30min | `c1_market.kline_etf_30min` | 2005-02-23 | 2026-07-03 | 1581 | 11,398,303 | bdpan | 每日 |
| 限售解禁 | `c3_fundamental.restricted_shares` | 2005-01-10 | 2026-07-02 | 5747 | 11,359,865 | bdpan | 每日 |
| 新闻信息(tushare) | `c3_fundamental.news_news_info` | 2000-01-01 | 2024-07-07 | 9608745 | 9,609,089 | — | 每日 |
| 估值数据 | `c1_market.daily_valuation` | 1990-12-19 | 2026-07-03 | 5708 | 8,787,985 | local_valuation | 每日 |
| kline_lof_30min | `c1_market.kline_lof_30min` | 2010-08-16 | 2026-07-03 | 2750 | 6,032,451 | bdpan | 每日 |
| kline_etf_60min | `c1_market.kline_etf_60min` | 2005-02-23 | 2026-07-03 | 1581 | 5,699,152 | bdpan | 每日 |
| A股周K线(不复权) | `c1_market.kline_weekly_none` | 1990-12-20 | 2026-06-26 | 5856 | 3,769,209 | bdpan_none | 每日 |
| 周K线 | `c1_market.kline_weekly` | 1990-12-20 | 2026-06-26 | 5856 | 3,769,062 | bdpan_qfq | 每日 |
| A股周K线(后复权) | `c1_market.kline_weekly_hfq` | 1990-12-20 | 2026-06-26 | 5853 | 3,768,249 | bdpan_hfq | 每日 |
| 新闻-股票关联 | `c3_fundamental.news_security` | 1997-04-30 | 2024-08-22 | 12590 | 3,728,723 | — | 每日 |
| 期货K线 | `c1_market.futures_kline` | 2010-01-04 | 2026-07-03 | 17592 | 3,067,213 | qmt | 每日 |
| 指数K线 | `c1_market.kline_index` | 1990-12-19 | 2026-07-03 | 1031 | 3,066,374 | bdpan | 每日 |
| kline_lof_60min | `c1_market.kline_lof_60min` | 2010-08-16 | 2026-07-03 | 2750 | 3,016,252 | bdpan | 每日 |
| 十大流通股东 | `c3_fundamental.top10_circulating_shareholders` | 2005-01-29 | 2026-05-15 | 5768 | 2,145,705 | bdpan | 每日 |
| 主营业务 | `c3_fundamental.main_business` | 2000-12-31 | 2026-03-31 | 5850 | 2,090,334 | bdpan | 每日 |
| 股权质押 | `c3_fundamental.equity_pledge_summary` | 2014-03-07 | 2026-07-03 | 4440 | 1,723,182 | bdpan | 每日 |
| 港股日K线 | `c1_market.hk_daily_kline` | 2015-05-29 | 2026-07-03 | 923 | 1,459,915 | qmt | 每日 |
| 十大股东 | `c3_fundamental.top10_shareholders` | 2005-01-29 | 2026-05-15 | 5789 | 1,447,675 | bdpan | 每日 |
| 融资融券 | `c1_market.margin_trading` | 2010-01-31 | 2026-06-30 | 5534 | 1,095,732 | ifind | 每日 |
| A股月K线(不复权) | `c1_market.kline_monthly_none` | 1990-12-25 | 2026-06-30 | 5854 | 904,274 | bdpan_none | 每日 |
| 月K线 | `c1_market.kline_monthly` | 1990-12-25 | 2026-06-30 | 5854 | 898,736 | bdpan_qfq | 每日 |
| A股月K线(后复权) | `c1_market.kline_monthly_hfq` | 1990-12-25 | 2026-06-30 | 5854 | 898,736 | bdpan_hfq | 每日 |
| PE/PB暂存表 | `c1_market._pepb_staging` | 2025-11-12 | 2026-07-03 | 5533 | 839,473 | — | 每日 |
| 股东户数 | `c3_fundamental.shareholder_count` | 1993-01-12 | 2026-07-02 | 5840 | 501,972 | bdpan | 每日 |
| 资金流向 | `c1_market.money_flow` | 2025-04-25 | 2026-07-03 | 5632 | 494,658 | local_moneyflow | 每日 |
| 财务指标 | `c3_fundamental.financial_indicator` | 1990-03-21 | 2026-06-04 | 5860 | 347,984 | bdpan | 每日 |
| 利润表 | `c3_fundamental.income_statement` | 1995-01-05 | 2026-06-04 | 5857 | 340,959 | bdpan | 每日 |
| 资产负债表 | `c3_fundamental.balance_sheet` | 1990-03-21 | 2026-06-04 | 5857 | 334,521 | bdpan | 每日 |
| 财报披露计划 | `c3_fundamental.disclosure_plan` | 2001-02-06 | 2026-07-02 | 5858 | 305,711 | bdpan | 每日 |
| 现金流量表 | `c3_fundamental.cashflow_statement` | 1999-01-30 | 2026-06-04 | 5848 | 305,230 | bdpan | 每日 |
| 股权质押明细 | `c3_fundamental.equity_pledge_detail` | 2003-06-10 | 2026-07-03 | 3572 | 297,056 | bdpan | 每日 |
| 龙虎榜 | `c1_market.dragon_tiger` | 2006-07-17 | 2026-07-03 | 5047 | 167,961 | ifind | 每日 |
| 美股日K线 | `c1_market.us_daily_kline` | 2006-08-15 | 2026-07-01 | 34 | 167,175 | tickflow | 每日 |
| 大宗交易 | `c1_market.block_trade` | 2010-01-31 | 2026-06-30 | 4963 | 161,708 | ifind | 每日 |
| 盈利预测 | `c3_fundamental.earnings_forecast` | 1999-01-08 | 2026-07-03 | 5707 | 125,582 | bdpan | 每日 |
| 分红送股 | `c3_fundamental.dividend` | 1991-03-17 | 2026-07-01 | 5823 | 115,351 | bdpan | 每日 |
| 审计意见 | `c3_fundamental.audit_opinion` | 1998-02-21 | 2026-05-29 | 5852 | 96,010 | bdpan | 每日 |
| 分红配股 | `c3_fundamental.rights_issue` | 1991-03-03 | 2026-07-06 | 5823 | 81,028 | bdpan | 每日 |
| 指数成分股 | `c1_market.index_constituent` | 2009-12-31 | 2026-06-30 | 3551 | 59,583 | ifind | 每日 |
| 业绩快报 | `c3_fundamental.express_report` | 2005-01-08 | 2026-07-02 | 4395 | 29,627 | bdpan | 每日 |
| 美股指数 | `c1_market.us_index` | 1993-01-29 | 2026-07-02 | 3 | 22,441 | tickflow | 每日 |
| 港股交易日历 | `c1_market.hk_trade_calendar` | 1980-01-01 | 2026-07-06 | — | 17,167 | — | 每日 |
| 交易日历 | `c1_market.trade_calendar` | 1990-12-19 | 2026-07-06 | — | 13,162 | — | 每日 |
| 分析师预测 | `c1_market.analyst_forecast` | 2026-07-04 | 2026-07-04 | 2857 | 8,373 | akshare | 每日 |
| 宏观经济数据 | `c1_market.macro_data` | 2006-03-31 | 2026-06-30 | 27 | 5,853 | akshare | 每日 |
| A股股票列表 | `c1_market.stock_list` | 1990-12-01 | 2026-07-02 | 5534 | 5,534 | — | 每日 |
| ETF列表 | `c1_market.etf_list` | 2005-02-23 | 2026-07-06 | — | 1,764 | — | 每日 |
| 可转债列表 | `c1_market.convertible_bond_list` | 1996-01-01 | 2026-07-06 | — | 1,142 | — | 每日 |
| ETF基准 | `c1_market.etf_benchmark` | 1991-04-04 | 2025-07-21 | — | 732 | — | 每日 |
| 指数列表 | `c1_market.index_list` | 1991-04-04 | 2025-07-21 | 732 | 732 | — | 每日 |
| 新闻数据(爬虫) | `c3_fundamental.news_data` | 2026-06-07 | 2026-07-03 | 287 | 287 | wallstreetcn | 每日 |
| 通达信板块信息 | `c1_market.tdx_sector_info` | 2026-07-03 | 2026-07-03 | 90 | 90 | — | 每日 |

## §3 实盘视角（实时获取能力）

> 关注实时获取能力。筛选：有实时数据源的项。排序：按延迟等级（Tick>秒>分钟>日>事件）。

共 **3** 项有实时能力。

### 实时数据源能力总览

| 数据源 | 获取方式 | 典型延迟 | 限流 | 稳定性 | 适用场景 |
|--------|----------|----------|------|--------|----------|
| **miniQMT** | 订阅推送 | Tick级(3s) | 无限制 | 高(自动重连) | A股Tick/分钟K线/五档盘口 |
| **iFind THS_RQ/BD** | 批量轮询 | 秒级 | 50代码/次 | 中(重试) | 估值/财务/指数成分 |
| **AKShare** | 单点轮询 | 秒级 | ~1次/秒 | 中(须断VPN) | 资金流/龙虎榜/公告/财务 |
| **TickFlow** | 轮询 | 日级 | 无限制 | 中(无VPN) | 美股/港股K线 |
| **财经RSS** | 订阅/轮询 | 分钟级 | 无限制 | 中(无VPN) | 国外财经新闻 |
| **tushare** | 轮询 | 分钟级 | 限流(积分制) | 中 | 新闻-股票关联 |

### 实时数据项明细

| 数据项 | 实时数据源 | 获取方式 | 延迟 | 限流 | 稳定性 | 时段 | 本地表 | 行数 |
|--------|-----------|----------|------|------|--------|------|--------|------|
| 3秒Tick逐笔 | miniQMT订阅 | 订阅推送 | 分钟级 | 无限制(订阅) | 高(自动重连) | 交易时段 | `c1_market.tick_data` | 0 |
| 集合竞价快照 | miniQMT订阅 | 订阅推送 | 分钟级 | 无限制(订阅) | 高(自动重连) | 交易时段 | `c1_market.auction_snapshot` | 0 |
| 指数3秒行情 | miniQMT订阅 | 订阅推送 | 分钟级 | 无限制(订阅) | 高(自动重连) | 交易时段 | `c1_market.index_quote` | 0 |

### 本地 ClickHouse 读取速度基准

> 实盘交易时，实时数据从API获取，历史数据从本地ClickHouse读取。

| 表 | 读取速度 | 说明 |
|----|---------|------|
| `tick_data` | ~500万行/秒 | MergeTree, 按 date+symbol 过滤 |
| `kline_1min` | ~200万行/秒 | 分钟线, 按日期范围查询 |
| `kline_daily` | ~10万行/秒 | 全表扫描; 单symbol ~5万行/秒 |
| `kline_5min` | ~100万行/秒 | 5分钟线 |
| `daily_valuation` | ~30万行/秒 | 估值数据 |
| 其他MergeTree表 | ~50万行/秒 | 典型值 |

### 实盘数据流配置建议

#### 低延迟交易（Tick级策略）
- **数据流**：miniQMT订阅 → 内存 → 策略计算 → 下单
- **必需数据**：实时Tick(3秒)、五档盘口、实时1分钟K线
- **延迟预算**：Tick 3s + 网络 10ms + 计算 50ms = < 100ms

#### 分钟级交易（日内策略）
- **数据流**：miniQMT订阅分钟线 → ClickHouse → 策略查询 → 下单
- **必需数据**：实时5/15分钟K线、实时资金流、实时行情快照
- **延迟预算**：分钟线 60s + 查询 100ms + 计算 500ms = < 1s

#### 日级交易（隔夜/波段策略）
- **数据流**：盘后批量下载 → ClickHouse → 策略查询 → 次日开盘下单
- **必需数据**：日K线、估值PE/PB、财务数据、资金流向
- **延迟预算**：无实时要求，盘后全量更新

## §4 获取能力矩阵（4态分类）

> 识别数据缺口与自动化短板。基于「是否有数据」+「是否能稳定获取」4态分类。

### 改进建议

**优先级1：建立自动更新机制（73项）**

当前 73 项数据已有但需手动触发，是最大自动化短板。
建议建立每日定时任务，将 `tmp/_fill_*.py` 配置为自动运行：
- 盘后 16:30：日K线/指数K线/估值等日频数据
- 盘后 17:00：融资融券/大宗交易/龙虎榜等资金面数据
- 盘后 18:00：分红/配股/限售解禁等事件驱动数据
- 周末：财务报表/股东数据等低频数据

**优先级2：接入空表数据（23项）**

当前 23 项数据源支持但表为空，建议按价值排序接入：
- Tick/集合竞价：QMT实时订阅，从现在开始积累
- 期权IV/可转债IV：用QMT数据自行计算
- 期货持仓/期限结构：QMT数据派生
- 股东增减持/高管持股/回购/研报：AKShare待建表

**优先级3：无法获取的数据（1项）**

当前 1 项试用账号无法获取，需：
- 升级 iFind 正式账号（沪深港通资金等）
- 商业API付费（天眼查股权穿透等）
- 自建派生（产业链地图基于申万骨架）

### ✅ 已能稳定获取的数据（自动每日更新）（0项）

（无）

### ⚠️ 有数据但不能稳定获取（需手动触发）（73项）

| 数据项 | 表 | 行数 | 可获取性 | 自动更新 | 数据源说明 |
|--------|-----|------|---------|---------|-----------|
| 日K线(前复权) | `c1_market.kline_daily` | 18,124,798 | ✅已验证 | 手动触发 | iFind THS_RQ批量补齐至2026-07-03 |
| 复权因子 | `c1_market.adj_factor` | 18,797,511 | ✅已验证 | 手动触发 | 最全5778只 |
| 周K线 | `c1_market.kline_weekly` | 3,769,062 | ✅已验证 | 手动触发 | QMT 1w |
| 月K线 | `c1_market.kline_monthly` | 898,736 | ✅已验证 | 手动触发 | QMT 1mon |
| 指数K线 | `c1_market.kline_index` | 3,066,374 | ✅已验证 | 手动触发 | THS_RQ批量补齐至2026-07-03 |
| 1分钟K线 | `c1_market.kline_1min` | 3,830,588,993 | ✅已验证 | 手动触发 | 历史需淘宝 |
| 15分钟K线 | `c1_market.kline_15min` | 254,313,641 | ✅已验证 | 手动触发 | 历史需淘宝 |
| 30分钟K线 | `c1_market.kline_30min` | 127,156,825 | ✅已验证 | 手动触发 | 历史需淘宝 |
| 60分钟K线 | `c1_market.kline_60min` | 63,578,425 | ✅已验证 | 手动触发 | 历史需淘宝 |
| 5分钟K线 | `c1_market.kline_5min` | 975,946,697 | ✅已验证 | 手动触发 | 仅2019年起，补2000-2018历史需淘宝 |
| 估值数据 | `c1_market.daily_valuation` | 8,787,985 | ✅已验证 | 手动触发 | 缺约1800只 |
| 资金流向 | `c1_market.money_flow` | 494,658 | ✅已验证 | 手动触发 | 仅98只/7个月 |
| 资产负债表 | `c3_fundamental.balance_sheet` | 334,521 | ✅已验证 | 手动触发 | — |
| 利润表 | `c3_fundamental.income_statement` | 340,959 | ✅已验证 | 手动触发 | — |
| 现金流量表 | `c3_fundamental.cashflow_statement` | 305,230 | ✅已验证 | 手动触发 | — |
| 财务指标 | `c3_fundamental.financial_indicator` | 347,984 | ✅API可用 | 手动触发 | — |
| 主营业务 | `c3_fundamental.main_business` | 2,090,334 | ✅API可用 | 手动触发 | — |
| 分红送股 | `c3_fundamental.dividend` | 115,351 | ✅已验证 | 手动触发 | — |
| 盈利预测 | `c3_fundamental.earnings_forecast` | 125,582 | ✅API可用 | 手动触发 | — |
| 审计意见 | `c3_fundamental.audit_opinion` | 96,010 | ✅已验证 | 手动触发 | i问财"600000.SH 2024年审计意见" |
| 业绩快报 | `c3_fundamental.express_report` | 29,627 | ✅API可用 | 手动触发 | — |
| 分红配股 | `c3_fundamental.rights_issue` | 81,028 | ✅已验证 | 手动触发 | AKShare多线程8workers/5823 symbol约7.5分钟；已补齐至2026-07-06 |
| 股权质押 | `c3_fundamental.equity_pledge_summary` | 1,723,182 | ✅已验证 | 手动触发 | 已补齐至2026-07-03 |
| PE/PB暂存表 | `c1_market._pepb_staging` | 839,473 | ✅已验证 | 手动触发 | — |
| 分析师预测 | `c1_market.analyst_forecast` | 8,373 | ✅已验证 | 手动触发 | — |
| 大宗交易 | `c1_market.block_trade` | 161,708 | ✅已验证 | 手动触发 | — |
| 可转债列表 | `c1_market.convertible_bond_list` | 1,142 | ✅已验证 | 手动触发 | — |
| A股日K线(原始) | `c1_market.daily_kline` | 18,122,192 | ✅已验证 | 手动触发 | — |
| 龙虎榜 | `c1_market.dragon_tiger` | 167,961 | ✅已验证 | 手动触发 | — |
| ETF基准 | `c1_market.etf_benchmark` | 732 | ✅已验证 | 手动触发 | — |
| kline_etf_15min | `c1_market.kline_etf_15min` | 22,813,741 | ✅已验证 | 手动触发 | — |
| kline_etf_1min | `c1_market.kline_etf_1min` | 343,553,536 | ✅已验证 | 手动触发 | — |
| kline_etf_30min | `c1_market.kline_etf_30min` | 11,398,303 | ✅已验证 | 手动触发 | — |
| ETF K线(多周期) | `c1_market.kline_etf_5min` | 68,389,859 | ✅已验证 | 手动触发 | — |
| kline_etf_60min | `c1_market.kline_etf_60min` | 5,699,152 | ✅已验证 | 手动触发 | — |
| ETF列表 | `c1_market.etf_list` | 1,764 | ✅已验证 | 手动触发 | — |
| 期货K线 | `c1_market.futures_kline` | 3,067,213 | ✅已验证 | 手动触发 | — |
| 港股日K线 | `c1_market.hk_daily_kline` | 1,459,915 | ✅已验证 | 手动触发 | — |
| 港股股票列表 | `c1_market.hk_stock_list` | 4,688 | ✅已验证 | 手动触发 | — |
| 港股交易日历 | `c1_market.hk_trade_calendar` | 17,167 | ✅已验证 | 手动触发 | — |
| 指数成分股 | `c1_market.index_constituent` | 59,583 | ✅已验证 | 手动触发 | — |
| 指数列表 | `c1_market.index_list` | 732 | ✅已验证 | 手动触发 | — |
| 行业分类 | `c1_market.industry_class` | 16,600 | ✅已验证 | 手动触发 | — |
| A股日K线(后复权) | `c1_market.kline_daily_hfq` | 18,119,282 | ✅已验证 | 手动触发 | — |
| A股日K线(不复权) | `c1_market.kline_daily_none` | 18,118,948 | ✅已验证 | 手动触发 | — |
| A股月K线(后复权) | `c1_market.kline_monthly_hfq` | 898,736 | ✅已验证 | 手动触发 | — |
| A股月K线(不复权) | `c1_market.kline_monthly_none` | 904,274 | ✅已验证 | 手动触发 | — |
| A股周K线(后复权) | `c1_market.kline_weekly_hfq` | 3,768,249 | ✅已验证 | 手动触发 | — |
| A股周K线(不复权) | `c1_market.kline_weekly_none` | 3,769,209 | ✅已验证 | 手动触发 | — |
| kline_lof_15min | `c1_market.kline_lof_15min` | 12,064,844 | ✅已验证 | 手动触发 | — |
| kline_lof_1min | `c1_market.kline_lof_1min` | 181,720,142 | ✅已验证 | 手动触发 | — |
| kline_lof_30min | `c1_market.kline_lof_30min` | 6,032,451 | ✅已验证 | 手动触发 | — |
| LOF K线(多周期) | `c1_market.kline_lof_5min` | 36,194,482 | ✅已验证 | 手动触发 | — |
| kline_lof_60min | `c1_market.kline_lof_60min` | 3,016,252 | ✅已验证 | 手动触发 | — |
| LOF列表 | `c1_market.lof_list` | 361 | ✅已验证 | 手动触发 | — |
| 宏观经济数据 | `c1_market.macro_data` | 5,853 | ✅已验证 | 手动触发 | — |
| 融资融券 | `c1_market.margin_trading` | 1,095,732 | ✅已验证 | 手动触发 | — |
| A股股票列表 | `c1_market.stock_list` | 5,534 | ✅已验证 | 手动触发 | — |
| 通达信板块指数 | `c1_market.tdx_market_index` | 50 | ✅已验证 | 手动触发 | — |
| 通达信板块信息 | `c1_market.tdx_sector_info` | 90 | ✅已验证 | 手动触发 | — |
| Tick数据(历史) | `c1_market.tick_data` | 7,143,133,916 | ✅已验证 | 手动触发 | — |
| 交易日历 | `c1_market.trade_calendar` | 13,162 | ✅已验证 | 手动触发 | — |
| 美股日K线 | `c1_market.us_daily_kline` | 167,175 | ✅已验证 | 手动触发 | — |
| 美股指数 | `c1_market.us_index` | 22,441 | ✅已验证 | 手动触发 | — |
| 财报披露计划 | `c3_fundamental.disclosure_plan` | 305,711 | ✅已验证 | 手动触发 | — |
| 股权质押明细 | `c3_fundamental.equity_pledge_detail` | 297,056 | ✅已验证 | 手动触发 | — |
| 新闻数据(爬虫) | `c3_fundamental.news_data` | 287 | ✅已验证 | 手动触发 | — |
| 新闻信息(tushare) | `c3_fundamental.news_news_info` | 9,609,089 | ✅已验证 | 手动触发 | — |
| 新闻-股票关联 | `c3_fundamental.news_security` | 3,728,723 | ✅已验证 | 手动触发 | — |
| 限售解禁 | `c3_fundamental.restricted_shares` | 11,359,865 | ✅已验证 | 手动触发 | — |
| 股东户数 | `c3_fundamental.shareholder_count` | 501,972 | ✅已验证 | 手动触发 | — |
| 十大流通股东 | `c3_fundamental.top10_circulating_shareholders` | 2,145,705 | ✅已验证 | 手动触发 | — |
| 十大股东 | `c3_fundamental.top10_shareholders` | 1,447,675 | ✅已验证 | 手动触发 | — |

### 🔵 无数据但可以获取（待接入）（23项）

| 数据项 | 表 | 行数 | 可获取性 | 自动更新 | 数据源说明 |
|--------|-----|------|---------|---------|-----------|
| 3秒Tick逐笔 | `c1_market.tick_data` | 0 | ✅已验证 | 未接入 | QMT 4998行含五档；历史需淘宝 |
| 集合竞价快照 | `c1_market.auction_snapshot` | 0 | ✅API可用 | 未接入 | 9:15-9:25竞价；历史需淘宝 |
| 指数3秒行情 | `c1_market.index_quote` | 0 | ✅已验证 | 未接入 | 实时指数tick |
| 期权IV曲面 | `c1_market.option_iv_surface` | 0 | 🔶需计算 | 未接入 | QMT 662期权+Greeks，IV需自己计算；iFind正式账号可直获取 |
| 可转债隐含波动率 | `c1_market.convertible_bond_iv` | 0 | 🔶需计算 | 未接入 | QMT 152可转债+get_cb_info，IV需自己计算；iFind正式账号可直获取 |
| 期货持仓 | `c1_market.futures_position` | 0 | ✅已验证 | 未接入 | QMT期货K线含openInterest字段(jm01.DF=3866)；详细持仓需iFind正式账号 |
| 期货期限结构 | `c1_market.futures_term_structure` | 0 | 🔶需计算 | 未接入 | 期货K线可获取(上期所6982/大商所9559/郑商所7281)，基差需自己计算 |
| 龙虎榜 | — | — | ✅已验证 | 未接入 | 计划表名 dragon_tiger；营业部/席位买卖明细；i问财5536行 |
| 融资融券 | — | — | ✅已验证 | 未接入 | 计划表名 margin_trading；两融余额/买入/偿还；已建表于c1_market |
| 大宗交易 | — | — | ✅已验证 | 未接入 | 计划表名 block_trade；成交价/量/买卖双方；已建表于c1_market |
| 股东数据 | — | — | ✅API可用 | 未接入 | 计划表名 shareholder；QMT get_financial_data: HolderNum/Top10Holder |
| 限售解禁 | — | — | ✅已验证 | 未接入 | 计划表名 share_unlock；解禁日期/数量/比例；i问财254行 |
| 交易日历 | — | — | ✅已验证 | 未接入 | 计划表名 trade_calendar；SSE/SZSE交易日历；QMT 8673天 |
| 股票列表 | — | — | ✅已验证 | 未接入 | 计划表名 stock_list；代码/名称/上市日期/行业；QMT 5207只 |
| 行业分类 | — | — | ✅已验证 | 未接入 | 计划表名 industry_class；申万/中证行业分类；iFind THS_DataPool 30行 |
| 指数成分股 | — | — | ✅已验证 | 未接入 | 计划表名 index_constituent；沪深300/中证500成分变动；iFind THS_DataPool 300行 |
| 期货行情K线 | — | — | ✅已验证 | 未接入 | 计划表名 futures_kline；商品期货日/分钟K线；4大交易所合约 |
| 美股日K线 | — | — | ✅已验证 | 未接入 | 计划表名 us_daily_kline；TickFlow AAPL.US实测12/12通过；60次/min限流 |
| 美股指数 | — | — | ✅已验证 | 未接入 | 计划表名 us_index；用SPY.US/DIA.US/QQQ.US ETF替代真实指数 |
| 港股日K线 | — | — | ✅已验证 | 未接入 | 计划表名 hk_daily_kline；港股通标的；QMT 957只 |
| 宏观经济 | — | — | ✅已验证 | 未接入 | 计划表名 macro_data；GDP/CPI/PMI/利率/汇率/M2；AKShare 9/10通过 |
| 新闻舆情 | — | — | ✅API可用 | 未接入 | 计划表名 news_data；AKShare stock_news_em✅/stock_research_report_em✅；stock_info_global_cls⏳卡住 |
| 分析师预期 | — | — | ✅已验证 | 未接入 | 计划表名 analyst_forecast；AKShare stock_profit_forecast_ths 同花顺一致预期EPS |

### ❌ 无数据且无法获取（需正式账号/商业API）（1项）

| 数据项 | 表 | 行数 | 可获取性 | 自动更新 | 数据源说明 |
|--------|-----|------|---------|---------|-----------|
| 沪深港通资金 | — | — | ❌试用不可用 | 未接入 | 计划表名 hk_connect_flow；北向/南向资金流入；i问财4种查询都-4001 |

## 字段说明

- **update_mode**：每日/实时/事件驱动/季度/年度/静态
- **fetch_cap**：✅已验证/✅API可用/🔶需计算/❌试用不可用/⚠️待验证
- **auto_update**：已配置定时(自动每日)/手动触发(需手动运行脚本)/未接入(空表)/不适用(静态)
- **status**：4态分类 = classify(has_data, can_fetch, auto_update)
- **rows/min_date/max_date/symbol_count/data_source**：ClickHouse实时扫描
- **rt_***：实时数据能力字段（rt_source=—表示无实时能力）
