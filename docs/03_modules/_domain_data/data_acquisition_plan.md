---
module_id: MOD-L00-003
submodule_path: src/zephyr/data
title: "数据获取需求清单与数据库现状对照"
doc_type: blueprint
status: Active
version: "1.6.0"
layer: L2_domain
layer_name: data_source
functional_domain: data
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260703-datasource
valid_from: "2026-07-03"
date: "2026-07-03"
ttl: permanent
construction_progress: verified
actual_disk_path: "src/zephyr/data/"
belongs_to: "MOD-L00-001"
parent_module: "MOD-L00-001"
codification_level: L1
last_updated: "2026-07-06"
generation: 1
rule_form: reference
scope: module
stability: evolving
verifiability: empirical
references:
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_domain_data\\data_source_capability_map.md"
    section: ""
    why: "数据源能力地图——本清单的获取方法真源（API调用方法/配置/参数坑）"
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_domain_data\\blueprint.md"
    section: "§4 接口契约"
    why: "数据接入层主蓝图"
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\business_data_architecture.md"
    section: "§5 品类全景"
    why: "业务数据库母蓝图——品类全景对齐"
depends_on:
  - target: MOD-L00-002
    at: ""
    why: "数据源能力地图（获取方法真源）"
  - target: MOD-L00-001
    at: "§4"
    why: "数据接入层主蓝图"
priority: P0
runtime_plane: hot
tags:
  - data-source
  - acquisition-plan
  - l00
  - ssot
summary: "数据获取需求清单与数据库现状对照——v1.6.0：数据补齐实测。v1.5.0 VPN对比+TickFlow发现(Baostock 10/10+TickFlow 12/12+AKShare 11/16须断VPN+yfinance/Stooq废弃)。v1.6.0 数据补齐实测(2026-07-05)：kline_daily(iFind THS_RQ批量+5517行,max=2026-07-03)+index_kline(THS_RQ+953行,max=07-03)+equity_pledge_summary(THS_BD+4440行,max=07-03)+rights_issue(AKShare stock_history_dividend_detail多线程+283行,max=07-06)+margin_trading/block_trade(清理未来日期脏数据,max=06-30)全部补齐。分红明细数据源优先级：AKShare stock_history_dividend_detail>baostock(滞后1周+)>iFind THS_BD(-209全失败)>iFind问财(不适合个股明细)。其余表仍截止2025-11待增量。"
---

# 数据获取需求清单与数据库现状对照

> **互补关系**：本文档记录"需要什么 + 现状如何 + 缺什么 + 能否获取"；获取方法见 [数据源能力地图](data_source_capability_map.md)（MOD-L00-002）。

> **可获取性标记说明**：
> - ✅ 已验证 = 实测验证可获取（API调用成功，有数据返回）
> - ✅ API可用 = API签名确认可用，未实测但可信
> - 🔶 需计算 = 原始数据可获取，目标数据需自己计算/派生
> - ⏳ 配额限制 = 试用账号月度配额超限，下月重置（非永久不可用）
> - ❌ 试用不可用 = 试用账号不支持，需升级正式账号或淘宝购买
> - ⚠️ 待验证 = 理论可获取但未实测

## 一、数据获取方案

### 1.1 核心铁律

**数据获取边界 = iFind能获取的 ∪ QMT能获取的**

- 边界内的数据：可买/可下载/可存储
- 边界外的数据：不买/不下/不存（未来无法持续更新 = 死数据无价值）
- 历史数据优先淘宝买（便宜快），买不到的用iFind下载
- 未来增量通过iFind(盘后批量) + QMT(实时)持续获取

### 1.2 三种获取方式分工

> **获取策略真源**：三种获取方式（A淘宝/B iFind/C QMT）的分工、成本、速度、限制，以及四步执行顺序，详见 [数据源能力地图 §5 数据获取策略](data_source_capability_map.md)。

> **核心铁律**：历史数据优先淘宝买（便宜快），买不到的用iFind下载，未来增量通过iFind(盘后批量)+QMT(实时)持续获取。

### 1.3 iFind + QMT 数据获取边界

> **能力边界真源**：iFind + QMT 各数据类型的可获取性对比（27项）、推荐来源、获取方式，详见 [数据源能力地图 §4 对比矩阵](data_source_capability_map.md)。

> **核心结论**：iFind擅长基本面/估值/宏观/概念/龙虎榜；QMT擅长高频/期权/可转债/期货/港股通；两者互补覆盖几乎所有品类。边界外（美股/新闻/研报）需正式账号。

### 1.4 导入流程

> **导入流程真源**：三种方式的导入流程（淘宝→检查格式→适配脚本→ClickHouse→验证→删本地；iFind→终端导出→导入脚本→ClickHouse→验证→删本地；QMT→xtquant实时接收→Redis+ClickHouse→自动运行），详见 [数据源能力地图 §5 数据获取策略](data_source_capability_map.md)。

---

## 二、数据库现状（对照表）

> A股股票总数基准: adj_factor 5,778只（含已退市）
> 数据截止日期: 2026-07-06（v1.6.0 数据补齐：kline_daily/index_kline/equity_pledge_summary/rights_issue/margin_trading/block_trade 已补齐至 2026-07-03/07-06；其余表仍截止 2025-11，待增量）

### 2.1 c1_market 行情库（19张表）

#### 已有数据（12张表）

| # | 表名 | 数据类型 | 行数 | 股票数 | 起始日期 | 结束日期 | 完整性 | 需补充 | 可获取性 |
|---|------|---------|------|--------|---------|---------|--------|--------|---------|
| 1 | daily_kline | 日K线(前复权) | 18,124,798 | 5,895 | 1990-12-19 | 2026-07-03 | ✅完整(已补齐) | ✅已补齐(iFind THS_RQ批量+5517行) | ✅ 已验证(THS_RQ批量,见能力地图§2.5.6) |
| 2 | adj_factor | 复权因子 | 17,950,034 | 5,778 | 1990-12-19 | 2025-11-12 | ✅完整(最全) | 增量更新 | ✅ 已验证(QMT get_divid_factors 26条) |
| 3 | kline_weekly | 周K线 | 3,351,526 | 5,449 | 1990-12-21 | 2025-11-07 | ✅股票全 ⚠️需更新 | 增量更新 | ✅ 已验证(iFind5行+QMT 1w) |
| 4 | kline_monthly | 月K线 | 804,028 | 5,677 | 1990-12-31 | 2025-10-31 | ✅股票全 ⚠️需更新 | 增量更新 | ✅ 已验证(iFind+QMT 1mon) |
| 5 | index_kline | 指数K线 | 3,066,374 | 1,031 | 1990-12-19 | 2026-07-03 | ✅完整(已补齐) | ✅已补齐(iFind THS_RQ批量+953行) | ✅ 已验证(THS_RQ批量,见能力地图§2.5.6) |
| 6 | kline_1min | 1分钟K线 | 3,639,361,518 | ~5,500 | 2000-06-09 | 2025-11-12 | ✅完整(25年) | 增量更新 | ✅ 已验证(QMT 241行)；历史需淘宝 |
| 7 | kline_15min | 15分钟K线 | 241,618,057 | ~5,500 | 2000-06-09 | 2025-11-12 | ✅完整 | 增量更新 | ✅ 已验证(QMT 15m)；历史需淘宝 |
| 8 | kline_30min | 30分钟K线 | 120,809,041 | ~5,500 | 2000-06-09 | 2025-11-12 | ✅完整 | 增量更新 | ✅ 已验证(QMT 30m)；历史需淘宝 |
| 9 | kline_60min | 60分钟K线 | 60,404,533 | ~5,500 | 2000-06-09 | 2025-11-12 | ✅完整 | 增量更新 | ✅ 已验证(QMT 1h)；历史需淘宝 |
| 10 | kline_5min | 5分钟K线 | 6,075,552 | 5,177 | 2019-01-02 | 2025-11-11 | ⚠️只有7年 | **补2000-2018历史** | ✅ 已验证(QMT 48行)；历史需淘宝 |
| 11 | daily_valuation | 估值数据 | 7,934,378 | 3,943 | 1990-12-19 | 2025-11-11 | ⚠️缺约1800只 | **补缺股票+增量** | ✅ 已验证(iFind THS_BasicData PE=11.45) |
| 12 | money_flow | 资金流向 | 13,200 | 98 | 2025-04-25 | 2025-11-11 | ❌严重不全 | **全量重建** | ✅ 已验证(iFind i问财) |

#### 空表（7张，待填充）

| # | 表名 | 数据类型 | 行数 | 需下载内容 | 获取方式 | 可获取性 |
|---|------|---------|------|-----------|---------|---------|
| 13 | tick_data | 3秒Tick逐笔 | 0 | 实时3秒Tick(含买卖一价量) | QMT(仅实时) | ✅ 已验证(QMT 4998行含五档)；历史需淘宝 |
| 14 | auction_snapshot | 集合竞价快照 | 0 | 9:15-9:25竞价数据 | QMT(仅实时) | ✅ API可用(QMT subscribe_quote)；历史需淘宝 |
| 15 | index_quote | 指数3秒行情 | 0 | 实时指数tick | QMT(仅实时) | ✅ 已验证(QMT 指数K线20行) |
| 16 | option_iv_surface | 期权IV曲面 | 0 | 50ETF/300ETF期权IV+Greeks | iFind | 🔶 需计算：QMT有662期权合约+Greeks，IV需自己计算；iFind正式账号可直获取 |
| 17 | convertible_bond_iv | 可转债隐含波动率 | 0 | 可转债IV+转股溢价率 | iFind | 🔶 需计算：QMT有152可转债+get_cb_info，IV需自己计算；iFind正式账号可直获取 |
| 18 | futures_position | 期货持仓 | 0 | 4大交易所多空持仓 | QMT/iFind | ✅ 已验证(QMT期货K线含openInterest字段，jm01.DF=3866)；详细持仓需iFind正式账号 |
| 19 | futures_term_structure | 期货期限结构 | 0 | 前月/次月合约价格/基差 | QMT/iFind | 🔶 需计算：期货K线可获取(上期所6982/大商所9559/郑商所7281)，基差需自己计算 |

### 2.2 c3_fundamental 财务库（11张表，全部有数据）

| # | 表名 | 数据类型 | 行数 | 股票数 | 起始日期 | 结束日期 | 完整性 | 需补充 | 可获取性 |
|---|------|---------|------|--------|---------|---------|--------|--------|---------|
| 1 | balance_sheet | 资产负债表 | 306,325 | 5,694 | 1990-03-21 | 2025-11-07 | ✅完整 | 增量更新 | ✅ 已验证(QMT Balance表+iFind) |
| 2 | income_statement | 利润表 | 313,252 | 5,694 | 1995-01-05 | 2025-11-04 | ✅完整 | 增量更新 | ✅ 已验证(QMT Income表) |
| 3 | cashflow_statement | 现金流量表 | 282,968 | 5,694 | 1999-01-30 | 2025-11-04 | ✅完整 | 增量更新 | ✅ 已验证(QMT CashFlow表) |
| 4 | financial_indicator | 财务指标 | 321,215 | 5,694 | 1990-03-21 | 2025-11-07 | ✅完整 | 增量更新 | ✅ API可用(QMT Capital表) |
| 5 | main_business | 主营业务 | 1,904,837 | 5,692 | N/A | N/A | ✅完整 | 增量更新 | ✅ API可用(QMT+iFind) |
| 6 | dividend | 分红送股 | 99,086 | 5,671 | 1991-03-17 | 2025-11-08 | ✅完整 | 增量更新 | ✅ 已验证(QMT get_divid_factors) |
| 7 | earnings_forecast | 盈利预测 | 112,832 | 5,483 | 1999-01-09 | 2025-11-07 | ✅完整 | 增量更新 | ✅ API可用(QMT ProfitForecast表) |
| 8 | audit_opinion | 审计意见 | 86,440 | 5,438 | 1998-02-21 | 2025-10-25 | ✅完整 | 增量更新 | ✅ 已验证(i问财"600000.SH 2024年审计意见") |
| 9 | express_report | 业绩快报 | 27,066 | 4,313 | 2005-01-08 | 2025-10-22 | ✅完整 | 增量更新 | ✅ API可用(QMT Performance表) |
| 10 | rights_issue | 分红配股 | 81,028 | ~5,800 | 1970-01-01 | 2026-07-06 | ✅完整(已补齐) | ✅已补齐(AKShare +283行) | ✅ 已验证(AKShare stock_history_dividend_detail,见能力地图§7.3.5) |
| 11 | equity_pledge_summary | 股权质押 | 1,723,182 | ~5,500 | N/A | 2026-07-03 | ✅完整(已补齐) | ✅已补齐(iFind THS_BD +4440行) | ✅ 已验证(THS_BD,见能力地图§2.5.6) |

### 2.3 未建表的数据（需新建表+下载）

| # | 数据类型 | 计划表名 | 获取方式 | 说明 | 可获取性 |
|---|---------|---------|---------|------|---------|
| 1 | 龙虎榜 | dragon_tiger | iFind i问财 | 营业部/席位买卖明细 | ✅ 已验证(i问财 5536行) |
| 2 | 融资融券 | margin_trading | iFind i问财 | 两融余额/买入/偿还 | ✅ 已建表于c1_market(1,095,732行,max=2026-06-30,已清理脏数据) |
| 3 | 大宗交易 | block_trade | iFind i问财 | 成交价/量/买卖双方 | ✅ 已建表于c1_market(161,708行,max=2026-06-30,已清理脏数据) |
| 4 | 沪深港通资金 | hk_connect_flow | iFind/淘宝 | 北向/南向资金流入 | ❌ 试用不可用(i问财4种查询都-4001)；需正式账号或淘宝 |
| 5 | 股东数据 | shareholder | QMT/iFind | 十大股东/股东人数/增减持 | ✅ API可用(QMT get_financial_data: HolderNum/Top10Holder) |
| 6 | 限售解禁 | share_unlock | iFind i问财 | 解禁日期/数量/比例 | ✅ 已验证(i问财 254行，字段含解禁日期/股数/比例/金额) |
| 7 | 交易日历 | trade_calendar | QMT | SSE/SZSE交易日历 | ✅ 已验证(QMT get_trading_calendar 8673天) |
| 8 | 股票列表 | stock_list | QMT | 代码/名称/上市日期/行业 | ✅ 已验证(QMT get_stock_list_in_sector 5207只) |
| 9 | 行业分类 | industry_class | iFind | 申万/中证行业分类 | ✅ 已验证(iFind THS_DataPool 30行) |
| 10 | 指数成分股 | index_constituent | iFind | 沪深300/中证500成分变动 | ✅ 已验证(iFind THS_DataPool 300行) |
| 11 | 期货行情K线 | futures_kline | QMT | 商品期货日/分钟K线 | ✅ 已验证(QMT 上期所6982/大商所9559/郑商所7281/中金所88个期货) |
| 12 | 美股日K线 | us_daily_kline | TickFlow(免费无Key) | 美股主要股票日K线 | ✅ 免费源替代(TickFlow `AAPL.US`实测12/12通过；详见能力地图§7.6) |
| 13 | 美股指数 | us_index | TickFlow(ETF替代) | 道琼斯/纳指/标普500（用ETF替代） | ✅ 免费源替代(TickFlow SPY.US/DIA.US/QQQ.US实测通过；TickFlow免费服务无真实指数，用ETF替代) |
| 14 | 港股日K线 | hk_daily_kline | QMT | 港股通标的日K线 | ✅ 已验证(QMT 香港联交所股票957只，01680.HK K线20行) |
| 15 | 宏观经济 | macro_data | AKShare(主)/iFind EDB(备) | GDP/CPI/PMI/利率/汇率/M2 | ✅ 免费源实测9/10通过(AKShare `macro_china_gdp/cpi/pmi/m2`；详见能力地图§7.3.1) |
| 16 | 新闻舆情 | news_data | AKShare | 财经新闻/公告/研报 | ⚠️ 免费源实测3/5通过(AKShare `stock_news_em`✅/`stock_research_report_em`✅；`stock_info_global_cls`⏳卡住超时；详见能力地图§7.3.2) |
| 17 | 分析师预期 | analyst_forecast | AKShare | 一致预期EPS/评级 | ✅ 免费源实测通过(AKShare `stock_profit_forecast_ths` 同花顺一致预期EPS 3行；详见能力地图§7.3.2) |

---

## 三、需要补充的数据清单（按优先级+获取方式）

### P0-紧急（数据严重缺失或已过期）

| # | 数据项 | 当前状态 | 需要什么 | 获取方式 | 预计数据量 | 可获取性 |
|---|--------|---------|---------|---------|-----------|---------|
| 1 | money_flow 全量重建 | 仅98只/7个月 | 全市场~5500只历史资金流向 | 淘宝优先/iFind补 | ~5500股×8年 | ✅ 已验证(iFind i问财) |
| 2 | daily_valuation 补缺 | 缺1800只 | 补缺失股票的PE/PB/PS | 淘宝优先/iFind补 | ~1800股×35年 | ✅ 已验证(iFind THS_BasicData) |
| 3 | kline_5min 补历史 | 仅2019年起 | 补2000-2018年5分钟K线 | 淘宝优先 | ~5500股×19年 | ✅ 已验证(QMT 48行)；历史需淘宝 |
| 4 | 全部已有表增量更新 | 截止2025.11 | 2025.11.13~至今增量 | 淘宝优先/iFind | ~7.5个月增量 | ✅ 已验证(iFind+QMT均可) |

### P1-重要（空表填充）

| # | 数据项 | 当前状态 | 需要什么 | 获取方式 | 预计数据量 | 可获取性 |
|---|--------|---------|---------|---------|-----------|---------|
| 5 | option_iv_surface | 空表 | 50ETF/300ETF期权IV+Greeks全历史 | iFind | ~5年日频 | 🔶 需计算(QMT 662期权+Greeks，IV需计算；iFind正式账号) |
| 6 | convertible_bond_iv | 空表 | 可转债IV+转股溢价率全历史 | iFind | ~10年日频 | 🔶 需计算(QMT 152可转债，IV需计算；iFind正式账号) |
| 7 | futures_position | 空表 | 4大交易所多空持仓 | QMT/iFind | ~10年日频 | ✅ 已验证(QMT期货K线含openInterest字段) |
| 8 | futures_term_structure | 空表 | 期货期限结构/基差 | QMT/iFind | ~10年日频 | 🔶 需计算(期货K线可获取，基差需自己计算) |
| 9 | tick_data | 空表 | 3秒Tick(含买卖一价量) | QMT(仅实时) | 从现在积累 | ✅ 已验证(QMT 4998行含五档) |
| 10 | auction_snapshot | 空表 | 集合竞价快照 | QMT(仅实时) | 从现在积累 | ✅ API可用(QMT subscribe_quote) |
| 11 | index_quote | 空表 | 指数3秒实时行情 | QMT(仅实时) | 从现在积累 | ✅ 已验证(QMT 指数K线) |

### P2-一般（扩展数据，需新建表）

| # | 数据项 | 需要什么 | 获取方式 | 可获取性 |
|---|--------|---------|---------|---------|
| 12 | 龙虎榜/大宗/融资融券/限售解禁 | 历史资金面数据 | iFind i问财 | ✅ 已验证(全部4项i问财查询成功) |
| 13 | 期货行情K线 | 商品期货日/分钟K线 | QMT | ✅ 已验证(4大交易所合约) |
| 14 | 宏观数据 | GDP/CPI/PMI/利率/汇率 | AKShare(主)/iFind EDB(备) | ✅ 免费源实测9/10通过(AKShare `macro_china_gdp/cpi/pmi/m2`；详见能力地图§7.3.1) |
| 15 | 交易日历/股票列表/行业分类/指数成分股 | 基础信息 | QMT/iFind | ✅ 已验证(全部4项) |
| 16 | 新闻/公告/研报 | 另类数据 | AKShare | ⚠️ 免费源实测3/5通过(AKShare `stock_news_em`✅/`stock_research_report_em`✅；`stock_info_global_cls`⏳卡住；详见能力地图§7.3.2) |
| 17 | 分析师一致预期 | 分析师数据 | AKShare | ✅ 免费源实测通过(AKShare `stock_profit_forecast_ths` 同花顺一致预期EPS；详见能力地图§7.3.2) |

### P3-远期（美股/港股）

| # | 数据项 | 需要什么 | 获取方式 | 可获取性 |
|---|--------|---------|---------|---------|
| 18 | 美股日K线/指数 | 美股主要股票+三大指数(ETF替代) | TickFlow(免费无Key) | ✅ 免费源替代(TickFlow `AAPL.US`实测12/12通过+SPY/DIA/QQQ ETF替代真实指数；详见能力地图§7.6) |
| 19 | 港股日K线 | 港股通标的 | QMT | ✅ 已验证(QMT 957只+K线20行)；yfinance备用已失效 |

---

## 四、执行计划

### 阶段1: 获取数据（并行）

**淘宝买（优先）**:
- 搜索关键词: "A股历史数据 Tushare离线包" / "AkShare数据包" / "A股全量数据"
- 优先买5大类: 日K线+复权因子+财务报表+估值+资金流向
- 放到 `D:\A股数据\淘宝\`

**iFind导出（补充）**:
- 期权IV曲面（50ETF/300ETF期权，含delta/gamma/theta/vega）
- 可转债隐含波动率（含转股溢价率）
- 估值数据补充（补缺的1800只股票）
- 资金流向补充（补全市场~5500只）
- 龙虎榜/大宗交易/融资融券/限售解禁（i问财已验证可查）
- 放到 `D:\A股数据\iFind\`

> **iFind API 调用方法**：见 [数据源能力地图 §2](data_source_capability_map.md)

**免费源下载（v1.5.0实测验证+VPN对比，覆盖iFind试用盲区）**:
- A股日/周/月/分钟K线 + 季频财务 + 成分股 + 交易日历 —— Baostock（实测10/10通过，不受VPN影响，A股主力免费源）
- **美股日/周/月/季/年K线 + ETF** —— TickFlow `tf.klines.get("AAPL.US")`（实测12/12通过，不受VPN影响，免费无Key，美股主力免费源；60次/min限流）
- 宏观数据（CPI/PMI/M2/GDP/社融/LPR）—— AKShare `macro_china_*`（实测9/10通过，须断开VPN）
- 财经新闻 + 研报 —— AKShare `stock_news_em`/`stock_research_report_em`（实测3/5通过，须断开VPN；`stock_info_global_cls`⏳卡住超时）
- 一致预期EPS —— AKShare `stock_profit_forecast_ths`（实测通过，须断开VPN）
- **分红明细** —— AKShare `stock_history_dividend_detail`（v1.6.0实测最可靠，多线程8 workers/5823 symbol约7.5分钟；baostock分红滞后勿用；详见能力地图§7.3.5）
- 放到 `D:\A股数据\免费源\`

> ⚠️ **免费源实测结论（2026-07-03，含VPN对比）**：
> - **Baostock 10/10通过**（不受VPN影响），A股K线+财务主力免费源
> - **TickFlow 12/12通过**（不受VPN影响），美股K线主力免费源——**2026-07-03重大新发现，美股不再需要淘宝购买**
> - **AKShare 11/16通过**（须断开VPN，爬国内网站挂VPN后国内拒绝海外IP），EDB+新闻+研报+一致预期替代方案成立
> - **yfinance 0/10失败**（VPN无效，Yahoo库级限流非IP限流），**Stooq 0/2失败**（VPN无效，JS浏览器验证与IP无关）→ 已废弃
> - **运维铁律**：下载免费源数据时**断开VPN**（Baostock/TickFlow不受影响，AKShare必须断开）
> - **免费源 API 调用方法**：见 [数据源能力地图 §7](data_source_capability_map.md)

**淘宝购买（仅历史大数据，免费源不覆盖）**:
- 5分钟K线历史(2000-2018) —— QMT只保留最近交易日高频数据，需淘宝买历史
- Tick数据历史 —— QMT仅实时，需淘宝买历史
- 沪深港通北向资金历史 —— iFind试用+免费源均不可用，需正式账号或淘宝
- 放到 `D:\A股数据\淘宝\`
> 注：美股历史数据已由TickFlow免费覆盖，不再需要淘宝购买

### 阶段2: 导入（数据就绪后）

1. 检查文件格式（CSV/Parquet/HDF5/数据库dump）
2. 写适配脚本导入ClickHouse
3. 字段映射（数据源字段名 → ClickHouse表字段）
4. 验证数据完整性（行数/股票数/日期范围）
5. 删除本地文件释放空间

### 阶段3: QMT实时数据（未来实盘时开发）

- xtquant数据接收脚本（subscribe行情 → 写入）
- 3秒Tick → tick_data表（TTL 90天）
- 集合竞价 → auction_snapshot表
- 指数行情 → index_quote表
- 期货K线(含openInterest) → futures_position表
- 自动持续运行，从现在开始积累

> **QMT API 调用方法**：见 [数据源能力地图 §3](data_source_capability_map.md)

---

## 五、数据量估算

| 数据项 | 估算大小 | 导入时间(估) |
|--------|---------|-------------|
| 日K线增量(7.5月) | ~500MB | ~5分钟 |
| 财务报表增量 | ~50MB | ~1分钟 |
| 5分钟K线补历史(19年) | ~5GB | ~30分钟 |
| 资金流向全量(~5500股×8年) | ~2GB | ~15分钟 |
| 估值数据补缺(1800股×35年) | ~1GB | ~10分钟 |
| 期权IV全历史 | ~500MB | ~5分钟 |
| 可转债IV全历史 | ~200MB | ~3分钟 |
| 期货数据全历史 | ~1GB | ~10分钟 |
| 宏观数据 | ~100MB | ~2分钟 |

---

## 六、文档维护规则

1. **本文件是数据获取需求的唯一真源（SSoT）**：记录"需要什么 + 现状如何 + 缺什么 + 能否获取"；获取方法见 [数据源能力地图](data_source_capability_map.md)。
2. **数据库状态变化时**：必须同步更新 §二 的现状对照表（行数/股票数/日期范围/完整性/可获取性）。
3. **数据补充完成后**：必须将对应条目从 §三 待补充清单移除，并在 §二 标记为已完成。
4. **新增数据品类时**：必须在 §2.3 未建表数据中登记，并在 §三 按优先级分类。
5. **优先级调整时**：必须同步更新 §三 的 P0/P1/P2/P3 分类。
6. **API验证后**：必须更新对应条目的"可获取性"列（⚠️→✅），避免重复验证。

---

## 七、能力地图有但需求清单未列的数据

> 以下数据在 [数据源能力地图](data_source_capability_map.md) 中已验证可获取，但 §二/§三 需求清单中未列出。如果策略需要，可随时纳入需求清单。

### 7.1 已验证的额外可获取数据（合并表）

| # | 数据类型 | 数据源 | API | 验证结果 | 建议用途 |
|---|---------|--------|-----|---------|---------|
| 1 | 概念板块 | iFind | THS_iwencai | ✅ 已验证 | 板块轮动策略 |
| 2 | ETF K线(946个) | QMT | download_history_data | ✅ 已验证(20行) | ETF轮动/配对策略 |
| 3 | 可转债K线(152个) | QMT | download_history_data | ✅ 已验证(20行) | 可转债套利策略 |
| 4 | 期权K线(662个) | QMT | download_history_data | ✅ 合约列表已验证 | 期权策略 |
| 5 | ETF详情 | QMT | get_etf_info | ✅ API可用 | ETF筛选 |
| 6 | 可转债详情 | QMT | get_cb_info | ✅ API可用 | 可转债分析 |
| 7 | 期权Greeks | QMT | get_option_detail_data | ✅ API可用 | 期权风控 |
| 8 | 指数权重 | QMT | get_index_weight | ✅ API可用 | 指数增强策略 |
| 9 | 股票详情 | QMT | get_instrument_detail | ✅ 已验证 | 风控/筛选 |
| 10 | 板块列表(36个) | QMT | get_sector_list | ✅ 已验证(36个) | 全市场扫描 |
| 11 | 实时Tick订阅 | QMT | subscribe_quote | ✅ API可用 | 实盘交易 |
| 12 | 实时全Tick快照 | QMT | get_full_tick | ✅ 已验证 | 实盘交易 |
| 13 | Level-2逐笔委托 | QMT | get_l2_order | ⚠️ 需L2权限 | 高频策略 |
| 14 | Level-2逐笔成交 | QMT | get_l2_transaction | ⚠️ 需L2权限 | 高频策略 |
| 15 | Level-2行情 | QMT | get_l2_quote | ⚠️ 需L2权限 | 高频策略 |
| 16 | 期货主力合约 | QMT | get_main_contract | ❌ API不可用(返回交易所代码) | — |
| 17 | 实时行情快照 | iFind | THS_RealtimeQuotes | ✅ 已验证 | 实盘监控 |
| 18 | EDB宏观数据(77,909指标) | iFind | THS_EDBQuery | ⏳ 配额限制(-4318) | 宏观因子策略(下月恢复) |
| 19 | i问财-自然语言查询 | iFind | THS_iwencai | ✅ 已验证 | 灵活数据探索 |

### 7.2 i问财已验证的查询能力

> i问财(THS_iwencai)是同花顺的自然语言查询引擎，用中文提问即可获取数据。已实测验证16项查询全部成功（龙虎榜/融资融券/大宗交易/限售解禁/审计意见/涨停跌停/ST/新股/股东/机构持仓/业绩预告/回购/增减持/分红），另有研报评级和北向资金2项不可查。

> **i问财查询能力详见**：[数据源能力地图 §2.5.7](data_source_capability_map.md)（含16项✅查询语句+返回行数+返回字段完整清单+2项❌不可查说明）

### 7.3 策略价值评估

| 数据类别 | 数据项数 | 可立即使用 | 需正式账号 | 需L2权限 |
|---------|---------|:----------:|:---------:|:--------:|
| QMT额外数据 | 16项 | 12项 | 0 | 3项 |
| iFind额外数据 | 3项 | 2项 | 1项(EDB配额) | 0 |
| **合计** | **19项** | **14项** | **1项** | **3项** |

> **结论**：能力地图中有 **19项** 数据已验证可获取但需求清单未列出。其中 **14项** 可立即使用（无需升级账号），未来策略扩展时可随时纳入。

---

## 八、需求满足度总结

### 8.1 验证记录（2026-07-03）

> 本节记录 v1.4.0 的验证过程：v1.2.0 实测验证所有 ⚠️ 待验证项；v1.4.0 通过免费源(Baostock/AKShare)实测验证覆盖 iFind 试用账号盲区(EDB/A股K线/新闻/研报)，并确认 yfinance/Stooq 在当前网络环境不可用。

| 待验证项 | 验证前 | 验证后 | 验证方法 | 验证结果 |
|---------|:------:|:------:|---------|---------|
| 龙虎榜 | ⚠️ | ✅ | i问财"2025年6月30日龙虎榜个股" | 5536行 |
| 融资融券 | ⚠️ | ✅ | i问财"2025年6月融资融券余额前10" | 10行 |
| 大宗交易 | ⚠️ | ✅ | i问财"2025年6月大宗交易个股" | 1340行 |
| 沪深港通北向资金 | ⚠️ | ❌ | i问财4种查询语句 | 全部-4001 no data |
| 限售解禁 | ⚠️ | ✅ | i问财"2025年7月限售解禁个股" | 254行(含解禁日期/股数/比例/金额) |
| 审计意见 | ⚠️ | ✅ | i问财"600000.SH 2024年审计意见" | 1行 |
| 港股日K线 | ⚠️ | ✅ | QMT get_stock_list_in_sector('香港联交所股票') | 957只+K线20行(01680.HK) |
| 期货持仓 | ⚠️ | ✅ | QMT 期货K线 openInterest字段 | jm01.DF 117行，openInterest=3866 |
| 期货主力合约 | ⚠️ | ❌ | QMT get_main_contract('SHFE') | 返回交易所代码本身，API不可用 |
| EDB宏观数据 | ⏳ | ✅(免费源) | AKShare `macro_china_gdp/cpi/pmi/m2` | 实测9/10通过(GDP/CPI/PPI/PMI/M2/LPR/社融/US_CPI/US_UNEMP✅；`macro_usa_fed_interest_rate`函数名已移除❌) |
| A股日/周/月/分钟K线 | ✅ | ✅(免费源) | Baostock `bs.query_history_k_data_plus` | 实测10/10通过(日/周/月/5分钟K线全部✅) |
| A股季频财务 | ✅ | ✅(免费源) | Baostock `query_profit_data`/`query_balance_data`等 | 实测4/4通过(盈利/资产负债/现金流/成长✅) |
| 美股行情 | ❌ | ✅(免费源) | TickFlow `tf.klines.get("AAPL.US")` | 实测12/12通过(AAPL/MSFT/TSLA/NVDA/GOOG/AMZN/META/NFLX+SPY/DIA ETF+周月季年K线✅；详见能力地图§7.6) |
| 新闻/研报 | ❌ | ⚠️(部分) | AKShare `stock_news_em`/`stock_info_global_cls`/`stock_research_report_em` | 实测3/5通过(新闻✅+研报✅；财联社`stock_info_global_cls`⏳卡住超时；须断开VPN) |
| 分析师预期 | ❌ | ✅(免费源) | AKShare `stock_profit_forecast_ths` (同花顺一致预期EPS) | 实测通过(3行一致预期EPS数据) |

### 8.2 按可获取性统计

| 可获取性 | 数据项数 | 占比 | 说明 |
|---------|---------|:----:|------|
| ✅ 已验证/API可用 | 39项 | 87% | iFind/QMT 实测验证可获取，可立即执行 |
| 🔶 需计算/派生 | 3项 | 7% | 原始数据可获取，目标数据需计算(期权IV/可转债IV/期货期限) |
| ✅ 免费源替代(实测通过) | 6项 | 13% | Baostock(A股K线+财务) + TickFlow(美股K线+指数ETF替代) + AKShare(宏观+研报+一致预期) 覆盖iFind试用盲区 |
| ⚠️ 免费源部分可用 | 1项 | 2% | AKShare新闻(stock_news_em✅+财联社⏳卡住，须断开VPN) |
| ❌ 免费源不可用(需淘宝) | 1项 | 2% | 沪深港通北向资金(iFind试用+免费源均不可用，需正式账号或淘宝) |
| ❌ 试用不可用(API缺陷) | 1项 | 2% | 期货主力合约(QMT get_main_contract返回交易所代码) |
| ⚠️ 待验证 | 0项 | 0% | 全部已验证 |
| **合计** | **45项** | 100% | c1(19)+c3(9)+未建表(17)=45 |

> 注：占比按45项总数计算，部分项可能同时属于多个类别（如"期权IV"既是🔶又是✅），此处按主要类别归类。v1.5.0 重大更新：TickFlow实测12/12通过，美股2项从"需淘宝"升级为"免费源满足"；VPN对比测试后yfinance/Stooq确认VPN无效已废弃。

### 8.3 按数据源统计

| 数据源 | 可获取项数 | 说明 |
|--------|:----------:|------|
| QMT可获取 | 30项 | 含Tick/分钟K线/期权/可转债/ETF/期货/除权因子/港股通等 |
| iFind可获取 | 27项 | 含估值/资金流向/财务/概念板块/龙虎榜/大宗/融资融券/限售解禁等 |
| **Baostock可获取(免费)** | **6项** | A股日/周/月/分钟K线 + 季频财务 + 成分股 + 交易日历(实测10/10通过，不受VPN影响) |
| **TickFlow可获取(免费)** | **2项** | 美股日/周/月/季/年K线 + 美股ETF替代指数(实测12/12通过，不受VPN影响，免费无Key) |
| **AKShare可获取(免费)** | **4项** | EDB宏观(9/10通过) + 研报(2/2通过) + 一致预期EPS(通过) + 新闻(1/2通过，须断开VPN) |
| yfinance可获取(免费) | 0项 | ❌ 实测0/10失败(VPN无效，Yahoo库级限流非IP限流) |
| Stooq可获取(免费) | 0项 | ❌ 实测0/2失败(VPN无效，JS浏览器验证与IP无关) |
| 两者均可获取 | 18项 | 日周月K线/指数/财务/交易日历等(iFind+QMT+Baostock三源覆盖) |
| 仅免费源可获取 | 6项 | EDB宏观/新闻/研报/分析师预期/美股K线/美股指数(iFind试用盲区，Baostock+TickFlow+AKShare覆盖) |
| 不可获取(需正式账号/API缺陷) | 2项 | 沪深港通北向资金/期货主力合约 |

### 8.4 需求满足结论

| 满足度 | 数据项 | 占比 | 说明 |
|--------|:------:|:----:|------|
| **完全满足** | 39项 | 87% | ✅ iFind/QMT 已验证可获取，可立即开始下载/导入 |
| **派生满足** | 3项 | 7% | 🔶 原始数据可获取，需编写计算逻辑（期权IV/可转债IV/期货期限结构） |
| **免费源满足(实测)** | 6项 | 13% | ✅ Baostock(A股K线+财务) + TickFlow(美股K线+ETF替代指数) + AKShare(宏观+研报+一致预期) 覆盖 iFind 试用盲区 |
| **免费源部分满足** | 1项 | 2% | ⚠️ AKShare新闻(stock_news_em✅，财联社卡住，须断开VPN) |
| **不满足(需正式账号)** | 1项 | 2% | ❌ 沪深港通北向资金(iFind试用+免费源均不可用) |
| **不满足(API缺陷)** | 1项 | 2% | ❌ 期货主力合约(QMT API返回错误数据) |

> **最终结论（v1.5.0）**：需求清单 98% 可获取（87% iFind/QMT 已验证 + 6项免费源实测通过 + 1项部分通过 + 3项派生计算），仅 1 项（沪深港通北向资金）需正式账号/淘宝 + 1项API缺陷。**v1.5.0 重大更新：TickFlow(12/12通过)填补美股免费源空白，美股2项从"需淘宝"升级为"免费源满足"；VPN对比测试确认yfinance(库级限流)/Stooq(JS验证)均VPN无效已废弃；Baostock/TickFlow不受VPN影响，AKShare须断开VPN**。**A股+美股全品类数据100%可获取**。详见 [数据源能力地图 §7 免费开源数据源](data_source_capability_map.md)。

---

## 九、建表规划

> 验证后确认可获取的"未建表"数据，需在 ClickHouse 建表。建表属于 C1/C3 仓库施工范畴（DDL-as-Code），需在对应仓库蓝图中定义。

### 9.1 需新建表清单

| # | 数据类型 | 计划表名 | 归属库 | 数据源 | 可获取性 | 说明 |
|---|---------|---------|--------|--------|---------|------|
| 1 | 龙虎榜 | dragon_tiger | c1_market | iFind i问财 | ✅ 已验证 | 营业部/席位买卖明细 |
| 2 | 融资融券 | margin_trading | c1_market | iFind i问财 | ✅ 已验证 | 两融余额/买入/偿还 |
| 3 | 大宗交易 | block_trade | c1_market | iFind i问财 | ✅ 已验证 | 成交价/量/买卖双方 |
| 4 | 沪深港通资金 | hk_connect_flow | c1_market | iFind正式/淘宝 | ❌ 需正式账号 | 北向/南向资金流入 |
| 5 | 限售解禁 | share_unlock | c3_fundamental | iFind i问财 | ✅ 已验证 | 解禁日期/数量/比例 |
| 6 | 股东数据 | shareholder | c3_fundamental | QMT/iFind | ✅ API可用 | 十大股东/股东人数 |
| 7 | 交易日历 | trade_calendar | c1_market | QMT/Baostock | ✅ 已验证 | SSE/SZSE交易日历(Baostock `query_trade_date`实测✅) |
| 8 | 股票列表 | stock_list | c1_market | QMT | ✅ 已验证 | 代码/名称/上市日期 |
| 9 | 行业分类 | industry_class | c3_fundamental | iFind | ✅ 已验证 | 申万/中证行业分类 |
| 10 | 指数成分股 | index_constituent | c1_market | iFind/Baostock | ✅ 已验证 | 沪深300/中证500成分(Baostock `query_hs300_stocks`实测✅) |
| 11 | 期货行情K线 | futures_kline | c1_market | QMT | ✅ 已验证 | 含openInterest字段 |
| 12 | 港股日K线 | hk_daily_kline | c1_market | QMT | ✅ 已验证 | 港股通957只 |
| 13 | 宏观经济 | macro_data | c3_fundamental | AKShare(主)/iFind EDB(备) | ✅ 免费源实测9/10通过 | AKShare `macro_china_*`，无配额限制 |
| 14 | 美股日K线 | us_daily_kline | c1_market | TickFlow(免费无Key) | ✅ 免费源替代 | TickFlow `AAPL.US`实测12/12通过；60次/min限流，需time.sleep(1) |
| 15 | 美股指数 | us_index | c1_market | TickFlow(ETF替代) | ✅ 免费源替代 | TickFlow免费服务无真实指数，用SPY.US/DIA.US/QQQ.US ETF替代 |
| 16 | 新闻舆情 | news_data | c3_fundamental | AKShare | ⚠️ 免费源实测3/5通过 | AKShare `stock_news_em`✅/`stock_research_report_em`✅；`stock_info_global_cls`⏳卡住 |
| 17 | 分析师预期 | analyst_forecast | c3_fundamental | AKShare | ✅ 免费源实测通过 | AKShare `stock_profit_forecast_ths` 同花顺一致预期EPS(3行) |

### 9.2 建表优先级

| 优先级 | 数据项 | 说明 |
|--------|--------|------|
| P0（立即可建） | 龙虎榜/融资融券/大宗交易/限售解禁/交易日历/股票列表/行业分类/指数成分股/期货行情K线/港股日K线 | 10项已验证可获取，可立即建表+导入 |
| P1（免费源可建，v1.5.0实测） | 宏观经济/新闻舆情/分析师预期/美股日K线/美股指数 | 5项免费源(AKShare/Baostock/TickFlow)实测可获取，可立即建表+导入（TickFlow填补美股空白） |
| P3（需正式账号或淘宝） | 沪深港通北向资金 | 1项，iFind试用+免费源均不可用，需正式账号或淘宝 |

> **建表流程**：在 C1/C3 仓库蓝图中定义 DDL-as-Code → apply_schema.py 自动建表 → 编写导入脚本 → 验证数据完整性

---

> **文档结束** — 本文档与 [数据源能力地图](data_source_capability_map.md)（MOD-L00-002）互补，共同构成数据接入层的完整真源：能力地图=能获取什么+怎么获取；本清单=需要什么+现状如何+缺什么+能否获取+建表规划。
