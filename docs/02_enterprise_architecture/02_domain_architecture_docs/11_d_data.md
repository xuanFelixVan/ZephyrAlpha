---
doc_type: architecture_view
title: D_DATA 数据接入层架构文档
version: "1.0"
status: active
date: 2026-08-05
owner: auto-generator
ttl: permanent
---

# 11_d_data / 数据接入层域 / Data Access Layer

> **功能简介 / Overview**: 数据接入层，负责数据源接入、数据集成和数据标准化

> **文档作用 / Purpose**: 展示 数据接入层（D_DATA）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/11_d_data.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 11 | Number | 11 |
| 域ID | D_DATA | Domain ID | D_DATA |
| 域名称 | 数据接入层 | Domain Name | Data Access Layer |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 176 | Module Count | 176 |
| 域内依赖 | 275 | Internal Dependencies | 275 |
| 跨域入边 | 33 | Cross-domain Incoming | 33 |
| 跨域出边 | 32 | Cross-domain Outgoing | 32 |
| 设计态模块 | 5 | Design Modules | 5 |
| 生产态模块 | 171 | Production Modules | 171 |
| 容量 | 172/150 (超容) | Capacity | 172/150 (超容) |
| 描述 | 数据源集成器 | Description | 数据源集成器 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 176 个模块（生产态 171 + 设计态 5），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    schemas_categories_fundamental_balance_sheet_py["fundamental余额sheet<br/>本文件是 c3_fundamental.balance_sheet<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_balance_sheet<br/>文件: categories/fundamental_balance_sheet.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_cashflow_statement_py["fundamentalcashflow报表<br/>本文件是 c3_fundamental.cashflow_statement<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_cashflow_statement<br/>文件: categories<br/>/fundamental_cashflow_statement.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_disclosure_plan_py["fundamentaldisclosure计划<br/>本文件是 c3_fundamental.disclosure_plan<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_disclosure_plan<br/>文件: categories/fundamental_disclosure_plan.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_equity_pledge_detail_py["fundamentalequitypledge详情<br/>（股权质押明细）DDL-as-Code（category_id:<br/>fundamental_equity_pledge_detail）<br/>文件: categories<br/>/fundamental_equity_pledge_detail.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_income_statement_py["fundamentalincome报表<br/>本文件是 c3_fundamental.income_statement<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_income_statement<br/>文件: categories/fundamental_income_statement.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_industry_class_py["fundamentalindustry类<br/>本文件是 c1_market.industry_class<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_industry_class<br/>文件: categories/fundamental_industry_class.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_industry_class_suppl_py["fundamentalindustry类suppl<br/>补充行业分类 DDL，定义<br/>fundamental_industry_class_suppl 分类表结构。<br/>文件: categories<br/>/fundamental_industry_class_suppl.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_restricted_shares_py["restrictedshares（限售股明细）DDL-as-Code（cate<br/>（限售股明细）DDL-as-Code（cate<br/>（限售股明细）DDL-as-Code（category_id:<br/>fundamental_restricted_shares）<br/>文件: categories<br/>/fundamental_restricted_shares.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_rights_issue_py["rightsissue（分红配股）DDL-as-Code（categoryi<br/>（分红配股）DDL-as-Code（categoryi<br/>（分红配股）DDL-as-Code（category_id:<br/>fundamental_rights_issue）<br/>文件: categories/fundamental_rights_issue.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_share_change_py["fundamental股票变更<br/>（股本变动）DDL-as-Code（category_id:<br/>fundamental_share_change）<br/>文件: categories/fundamental_share_change.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_share_unlock_py["fundamental股票unlock<br/>本文件是 c3_fundamental.share_unlock<br/>表结构的唯一真源。<br/>fundamental_share_unlock<br/>文件: categories/fundamental_share_unlock.py<br/>(生产态 / production)"]
    schemas_categories_macro_edb_data_py["macroedb数据<br/>本文件是 c1_market.edb_data 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>macro_edb_data<br/>文件: categories/macro_edb_data.py<br/>(生产态 / production)"]
    schemas_categories_macro_macro_data_py["macromacro数据<br/>本文件是 c1_market.macro_data 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>macro_macro_data<br/>文件: categories/macro_macro_data.py<br/>(生产态 / production)"]
    schemas_categories_market_adj_factor_py["行情adj因子<br/>本文件是 c1_market.adj_factor 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_adj_factor<br/>文件: categories/market_adj_factor.py<br/>(生产态 / production)"]
    schemas_categories_market_auction_py["行情拍卖<br/>本文件是 c1_market.auction_snapshot<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_auction<br/>文件: categories/market_auction.py<br/>(生产态 / production)"]
    schemas_categories_market_auction_book_py["行情拍卖book<br/>本文件是 c1_market.auction_book<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_auction_book<br/>文件: categories/market_auction_book.py<br/>(生产态 / production)"]
    schemas_categories_market_block_trade_py["行情块交易<br/>本文件是 c1_market.block_trade<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_block_trade<br/>文件: categories/market_block_trade.py<br/>(生产态 / production)"]
    schemas_categories_market_block_trade_detail_py["行情block成交详情<br/>本文件是 c1_market.block_trade_detail<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_block_trade_detail<br/>文件: categories/market_block_trade_detail.py<br/>(生产态 / production)"]
    schemas_categories_market_cb_iv_py["行情cb隐含波动率<br/>本文件是 c1_market.convertible_bond_iv<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_cb_iv<br/>文件: categories/market_cb_iv.py<br/>(生产态 / production)"]
    schemas_categories_market_concept_board_py["行情conceptboard<br/>实现业务功能（market concept board）<br/>market_concept_board<br/>文件: categories/market_concept_board.py<br/>(生产态 / production)"]
    schemas_categories_market_concept_board_constituent_py["行情conceptboardconstituent<br/>实现业务功能（market concept board constituent）<br/>market_concept_board_constituent<br/>文件: categories<br/>/market_concept_board_constituent.py<br/>(生产态 / production)"]
    schemas_categories_market_concept_sector_py["行情conceptsector<br/>实现业务功能（market concept sector）<br/>market_concept_sector<br/>文件: categories/market_concept_sector.py<br/>(生产态 / production)"]
    schemas_categories_market_convertible_bond_list_py["行情convertiblebondlist<br/>实现业务功能（market convertible bond list）<br/>market_convertible_bond_list<br/>文件: categories/market_convertible_bond_list.py<br/>(生产态 / production)"]
    schemas_categories_market_daily_valuation_py["行情dailyvaluation<br/>本文件是 c1_market.daily_valuation<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_daily_valuation<br/>文件: categories/market_daily_valuation.py<br/>(生产态 / production)"]
    schemas_categories_market_dragon_tiger_py["行情dragontiger<br/>本文件是 c1_market.dragon_tiger<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_dragon_tiger<br/>文件: categories/market_dragon_tiger.py<br/>(生产态 / production)"]
    schemas_categories_market_dragon_tiger_seat_py["行情dragontigerseat<br/>龙虎榜席位明细：存储个股龙虎榜 Top5 买入<br/>/卖出营业部席位买卖额明细。<br/>market_dragon_tiger_seat<br/>文件: categories/market_dragon_tiger_seat.py<br/>(生产态 / production)"]
    schemas_categories_market_etf_benchmark_py["行情etf基准<br/>categories相关功能（market etf benchmark）<br/>market_etf_benchmark<br/>文件: categories/market_etf_benchmark.py<br/>(生产态 / production)"]
    schemas_categories_market_etf_list_py["行情etf列表<br/>categories相关功能（market etf list）<br/>market_etf_list<br/>文件: categories/market_etf_list.py<br/>(生产态 / production)"]
    schemas_categories_market_etf_nav_py["行情etfnav<br/>本文件是 c1_market.etf_nav 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_etf_nav<br/>文件: categories/market_etf_nav.py<br/>(生产态 / production)"]
    schemas_categories_market_futures_kline_qmt_py["行情futuresklineqmt<br/>本文件是 c1_market.futures_kline_qmt<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_futures_kline_qmt<br/>文件: categories/market_futures_kline_qmt.py<br/>(生产态 / production)"]
    schemas_categories_market_futures_position_py["行情futures持仓<br/>本文件是 c1_market.futures_position<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_futures_position<br/>文件: categories/market_futures_position.py<br/>(生产态 / production)"]
    schemas_categories_market_futures_term_py["行情futures期限<br/>本文件是 c1_market.futures_term_structure<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_futures_term<br/>文件: categories/market_futures_term.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_connect_flow_py["行情hkconnect流程<br/>本文件是 c1_market.hk_connect_flow<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_hk_connect_flow<br/>文件: categories/market_hk_connect_flow.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_kline_py["行情hkkline<br/>本文件是 c1_market.hk_kline 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_hk_kline<br/>文件: categories/market_hk_kline.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_stock_list_py["行情hk股票列表<br/>categories相关功能（market hk stock list）<br/>market_hk_stock_list<br/>文件: categories/market_hk_stock_list.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_trade_calendar_py["行情hk成交日历<br/>categories相关功能（market hk trade calendar）<br/>market_hk_trade_calendar<br/>文件: categories/market_hk_trade_calendar.py<br/>(生产态 / production)"]
    schemas_categories_market_hog_futures_core_py["市场生猪Futures核心<br/>hog_futures_core 表 DDL-as-Code（category_id:<br/>market_hog_futures_core, calc_m...<br/>Market Hog Futures Core<br/>文件: categories/market_hog_futures_core.py<br/>(生产态 / production)"]
    schemas_categories_market_hog_province_spot_py["市场生猪Province现货<br/>hog_province_spot 表 DDL-as-Code（category_id:<br/>market_hog_province_spot, calc...<br/>Market Hog Province Spot<br/>文件: categories/market_hog_province_spot.py<br/>(生产态 / production)"]
    schemas_categories_market_hog_spot_index_py["市场生猪现货索引<br/>hog_spot_index 表 DDL-as-Code（category_id:<br/>market_hog_spot_index, calc_mode:...<br/>Market Hog Spot Index<br/>文件: categories/market_hog_spot_index.py<br/>(生产态 / production)"]
    schemas_categories_market_index_py["行情索引<br/>本文件是 c1_market.index_quote<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_index<br/>文件: categories/market_index.py<br/>(生产态 / production)"]
    schemas_categories_market_index_constituent_py["行情索引constituent<br/>categories相关功能（market index constituent）<br/>market_index_constituent<br/>文件: categories/market_index_constituent.py<br/>(生产态 / production)"]
    schemas_categories_market_index_list_py["行情索引列表<br/>categories相关功能（market index list）<br/>market_index_list<br/>文件: categories/market_index_list.py<br/>(生产态 / production)"]
    schemas_categories_market_index_meta_py["行情索引元<br/>本文件是 c1_market.market_index_meta<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>文件: categories/market_index_meta.py<br/>(生产态 / production)"]
    schemas_categories_market_index_weight_py["行情索引weight<br/>本文件是 c1_market.index_weight<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_index_weight<br/>文件: categories/market_index_weight.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_15min_py["行情kline15min<br/>本文件是 c1_market.kline_15min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_15min<br/>文件: categories/market_kline_15min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_1min_py["行情kline1min<br/>本文件是 c1_market.kline_1min 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_kline_1min<br/>文件: categories/market_kline_1min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_30min_py["行情kline30min<br/>本文件是 c1_market.kline_30min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_30min<br/>文件: categories/market_kline_30min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_5min_py["行情kline5min<br/>本文件是 c1_market.kline_5min 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_kline_5min<br/>文件: categories/market_kline_5min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_60min_py["行情kline60min<br/>本文件是 c1_market.kline_60min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_60min<br/>文件: categories/market_kline_60min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_cb_py["行情klinecb<br/>本文件是 c1_market.kline_cb 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_kline_cb<br/>文件: categories/market_kline_cb.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_daily_py["行情klinedaily<br/>本文件是 c1_market.kline_daily<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_daily<br/>文件: categories/market_kline_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_daily_hfq_py["行情klinedailyhfq<br/>本文件是 c1_market.kline_daily_hfq<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_daily_hfq<br/>文件: categories/market_kline_daily_hfq.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_15min_py["行情klineetf15min<br/>本文件是 c1_market.kline_etf_15min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_15min<br/>文件: categories/market_kline_etf_15min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_1min_py["行情klineetf1min<br/>本文件是 c1_market.kline_etf_1min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_1min<br/>文件: categories/market_kline_etf_1min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_30min_py["行情klineetf30min<br/>本文件是 c1_market.kline_etf_30min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_30min<br/>文件: categories/market_kline_etf_30min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_5min_py["行情klineetf5min<br/>本文件是 c1_market.kline_etf_5min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_5min<br/>文件: categories/market_kline_etf_5min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_60min_py["行情klineetf60min<br/>本文件是 c1_market.kline_etf_60min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_60min<br/>文件: categories/market_kline_etf_60min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_daily_py["市场K线EtfDaily<br/>kline_etf_daily 表 DDL-as-Code（category_id:<br/>market_kline_etf_daily, calc_mod...<br/>Market Kline Etf Daily<br/>文件: categories/market_kline_etf_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_futures_py["行情klinefutures<br/>本文件是 c1_market.kline_futures<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_futures<br/>文件: categories/market_kline_futures.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_hk_daily_py["行情klinehkdaily<br/>本文件是 c1_market.kline_hk_daily<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_hk_daily<br/>文件: categories/market_kline_hk_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_index_py["行情kline索引<br/>本文件是 c1_market.kline_index<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_index<br/>文件: categories/market_kline_index.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_15min_py["行情klinelof15min<br/>本文件是 c1_market.kline_lof_15min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_15min<br/>文件: categories/market_kline_lof_15min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_1min_py["行情klinelof1min<br/>本文件是 c1_market.kline_lof_1min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_1min<br/>文件: categories/market_kline_lof_1min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_30min_py["行情klinelof30min<br/>本文件是 c1_market.kline_lof_30min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_30min<br/>文件: categories/market_kline_lof_30min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_5min_py["行情klinelof5min<br/>本文件是 c1_market.kline_lof_5min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_5min<br/>文件: categories/market_kline_lof_5min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_60min_py["行情klinelof60min<br/>本文件是 c1_market.kline_lof_60min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_60min<br/>文件: categories/market_kline_lof_60min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_monthly_py["行情klinemonthly<br/>本文件是 c1_market.kline_monthly<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_monthly<br/>文件: categories/market_kline_monthly.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_monthly_hfq_py["行情klinemonthlyhfq<br/>本文件是 c1_market.kline_monthly_hfq<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_monthly_hfq<br/>文件: categories/market_kline_monthly_hfq.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_sector_py["行情klinesector<br/>本文件是 c1_market.kline_sector<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_sector<br/>文件: categories/market_kline_sector.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_sector_880_py["行情klinesector880<br/>本文件是 c1_market.kline_sector_880<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_sector_880<br/>文件: categories/market_kline_sector_880.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_sector_intraday_py["行情klinesectorintraday<br/>本文件是 c1_market.kline_sector_intraday<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_sector_intraday<br/>文件: categories/market_kline_sector_intraday.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_us_daily_py["行情klineusdaily<br/>本文件是 c1_market.kline_us_daily<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_us_daily<br/>文件: categories/market_kline_us_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_weekly_py["行情klineweekly<br/>本文件是 c1_market.kline_weekly<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_weekly<br/>文件: categories/market_kline_weekly.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_weekly_hfq_py["行情klineweeklyhfq<br/>本文件是 c1_market.kline_weekly_hfq<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_weekly_hfq<br/>文件: categories/market_kline_weekly_hfq.py<br/>(生产态 / production)"]
    schemas_categories_market_l2_tick_py["行情l2逐笔<br/>本文件是 c1_market.l2_tick 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_l2_tick<br/>文件: categories/market_l2_tick.py<br/>(生产态 / production)"]
    schemas_categories_market_limit_up_down_py["行情限制上下<br/>本文件是 c1_market.limit_up_down<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_limit_up_down<br/>文件: categories/market_limit_up_down.py<br/>(生产态 / production)"]
    schemas_categories_market_lof_list_py["行情lof列表<br/>categories相关功能（market lof list）<br/>market_lof_list<br/>文件: categories/market_lof_list.py<br/>(生产态 / production)"]
    schemas_categories_market_margin_trading_py["行情保证金交易<br/>本文件是 c1_market.margin_trading<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_margin_trading<br/>文件: categories/market_margin_trading.py<br/>(生产态 / production)"]
    schemas_categories_market_money_flow_py["行情money流程<br/>本文件是 c1_market.money_flow 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_money_flow<br/>文件: categories/market_money_flow.py<br/>(生产态 / production)"]
    schemas_categories_market_option_greeks_py["行情选项greeks<br/>本文件是 c1_market.option_greeks<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_option_greeks<br/>文件: categories/market_option_greeks.py<br/>(生产态 / production)"]
    schemas_categories_market_option_iv_py["行情选项隐含波动率<br/>本文件是 c1_market.option_iv_surface<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_option_iv<br/>文件: categories/market_option_iv.py<br/>(生产态 / production)"]
    schemas_categories_market_option_kline_py["行情选项kline<br/>本文件是 c1_market.option_kline<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_option_kline<br/>文件: categories/market_option_kline.py<br/>(生产态 / production)"]
    schemas_categories_market_realtime_snapshot_py["行情实时快照<br/>本文件是 c1_market.realtime_snapshot<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_realtime_snapshot<br/>文件: categories/market_realtime_snapshot.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_constituent_py["行情sectorconstituent<br/>实现业务功能（market sector constituent）<br/>market_sector_constituent<br/>文件: categories/market_sector_constituent.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_list_py["行情板块列表<br/>本文件是 c1_market.sector_list<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_sector_list<br/>文件: categories/market_sector_list.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_meta_py["行情板块元<br/>本文件是 c1_market.sector_meta<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_sector_meta<br/>文件: categories/market_sector_meta.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_snapshot_py["行情板块快照<br/>本文件是 c1_market.sector_snapshot<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_sector_snapshot<br/>文件: categories/market_sector_snapshot.py<br/>(生产态 / production)"]
    schemas_categories_market_st_stock_list_py["行情st股票列表<br/>categories相关功能（market st stock list）<br/>market_st_stock_list<br/>文件: categories/market_st_stock_list.py<br/>(生产态 / production)"]
    schemas_categories_market_stock_indicator_py["行情股票指标<br/>本文件是 c1_market.stock_indicator<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_stock_indicator<br/>文件: categories/market_stock_indicator.py<br/>(生产态 / production)"]
    schemas_categories_market_stock_list_py["行情股票列表<br/>本文件是 c1_market.stock_list 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_stock_list<br/>文件: categories/market_stock_list.py<br/>(生产态 / production)"]
    schemas_categories_market_tick_py["行情逐笔<br/>本文件是 c1_market.tick_data 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_tick<br/>文件: categories/market_tick.py<br/>(生产态 / production)"]
    schemas_categories_market_trade_calendar_py["行情成交日历<br/>categories相关功能（market trade calendar）<br/>market_trade_calendar<br/>文件: categories/market_trade_calendar.py<br/>(生产态 / production)"]
    schemas_categories_market_us_index_py["行情us索引<br/>本文件是 c1_market.us_index 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_us_index<br/>文件: categories/market_us_index.py<br/>(生产态 / production)"]
    scripts_ch_data_inventory_py["全库数据盘点：逐表审计行数/日期范围/空表<br/>/缺失日期/引擎/大小。<br/>输出完整数据资产清单，用于'收口'——确认数据完整性<br/>+ 识别缺口。<br/>_data_inventory<br/>文件: ch/_data_inventory.py<br/>(生产态 / production)"]
    scripts_ch_recovery_drill_py["恢复演练：轮询备份完成 → 恢复小表到临时库 →<br/>行数校验 → 清理。<br/>非破坏性：不碰 live 表，恢复到 _restore_drill<br/>临时库。<br/>_recovery_drill<br/>文件: ch/_recovery_drill.py<br/>(生产态 / production)"]
    scripts_ch_apply_fundamental_tables_ddl_py["应用fundamentaltablesddl<br/>ClickHouse c3_fundamental 财务三表 DDL 部署 +<br/>精度验证脚本（audit 1.2 治本）。<br/>apply_fundamental_tables_ddl<br/>文件: ch/apply_fundamental_tables_ddl.py<br/>(生产态 / production)"]
    scripts_ch_apply_market_tables_ddl_py["apply行情tablesddl<br/>ClickHouse c1_market 建表 DDL 部署 +<br/>引擎验证脚本（Phase F）。<br/>apply_market_tables_ddl<br/>文件: ch/apply_market_tables_ddl.py<br/>(生产态 / production)"]
    scripts_ch_apply_rbac_py["应用rbac<br/>ClickHouse RBAC 账号分级部署 + 验证脚本（audit<br/>9.4 治本 #ARCH-CH-027）。<br/>apply_rbac<br/>文件: ch/apply_rbac.py<br/>(生产态 / production)"]
    scripts_ch_lint_symbol_convention_py["Symbol 约定 lint 门禁（TRAE-082 GATE-SYMBOL-C<br/>静态 lint 校验（无 DB 连接，快速 pre-commit<br/>适用）：<br/>lint_symbol_convention<br/>文件: ch/lint_symbol_convention.py<br/>(生产态 / production)"]
    scripts_ch_verify_exchange_coverage_py["verify交易所coverage<br/>exchange+symbol_canonical 数据覆盖率校验器<br/>（TRAE-082 1.1.0 阶段2 配套）。<br/>verify_exchange_coverage<br/>文件: ch/verify_exchange_coverage.py<br/>(生产态 / production)"]
    scripts_ch_verify_schema_truth_py["verify结构truth<br/>DDL-as-Code 真源 vs ClickHouse 实际表结构<br/>漂移校验器（治本工具）。<br/>verify_schema_truth<br/>文件: ch/verify_schema_truth.py<br/>(生产态 / production)"]
    scripts_ops_ch_health_probe_py["7×24 CH 健康探针守护进程<br/>（R4b，#ARCH-DR-CH-RESTART-001）<br/>Ch Health Probe<br/>文件: ops/ch_health_probe.py<br/>(生产态 / production)"]
    scripts_ops_verify_alert_channels_py["告警通道端到端验证<br/>（B2，#ARCH-CH-023，2026-07-25）。<br/>告警通道端到端验证，#，2026-07-25）。<br/>verify_alert_channels<br/>文件: ops/verify_alert_channels.py<br/>(生产态 / production)"]
    scripts_register_aux_tasks_ps1["注册aux任务<br/>register_aux_tasks.ps1的注册表，登记和查询已注册<br/>的条目<br/>文件: scripts/register_aux_tasks.ps1<br/>(生产态 / production)"]
    scripts_register_guard_tasks_ps1["注册守卫任务<br/>守卫的注册表，登记和查询已注册的条目<br/>register_guard_tasks<br/>文件: scripts/register_guard_tasks.ps1<br/>(生产态 / production)"]
    scripts_start_ch_health_probe_ps1["启动ChHealthProbe<br/>脚本包的start_ch_health_probe模块<br/>Start Ch Health Probe<br/>文件: scripts/start_ch_health_probe.ps1<br/>(生产态 / production)"]
    scripts_start_scheduler_ps1["启动调度器<br/>调度器的调度器，按时间或优先级安排任务执行<br/>start_scheduler<br/>文件: scripts/start_scheduler.ps1<br/>(生产态 / production)"]
    scripts_start_tick_subscriber_ps1["启动逐笔订阅器<br/>start_tick_subscriber.ps1的订阅器，订阅接收数据<br/>文件: scripts/start_tick_subscriber.ps1<br/>(生产态 / production)"]
    src_zephyr_data_main_py["主入口<br/>data — 数据源集成器 CLI 入口<br/>__main__<br/>文件: data/__main__.py<br/>(生产态 / production)"]
    src_zephyr_data_config_policies_yaml["策略<br/>数据采集策略配置（派生物），由<br/>generate_policies.py 从<br/>data_sources_registry.yaml<br/>派生，禁止手工修改，mtime 变化时热更新。<br/>文件: config/policies.yaml<br/>(生产态 / production)"]
    src_zephyr_data_config_schedule_yaml["调度计划<br/>机器学习的调度器，按时间或优先级安排任务执行<br/>schedule<br/>文件: config/schedule.yaml<br/>(生产态 / production)"]
    src_zephyr_data_config_tasks_yaml["任务<br/>数据采集任务清单配置，定义首批 10<br/>个任务的调度计划、DAG 依赖与数据源映射，覆盖<br/>iFind/QMT/AKShare 三个 Provider。<br/>tasks<br/>文件: config/tasks.yaml<br/>(生产态 / production)"]
    src_zephyr_data_connectors["data/connectors<br/>数据连接器包，适配外部数据源连接与数据采集<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: connectors/<br/>(设计态 / design)"]
    src_zephyr_data_implementations_init_py["data/implementations 包入口<br/>每个 Provider 封装一个数据源 SDK，继承<br/>IngestProviderBase。<br/>文件: implementations/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_fred_provider_py["FRED宏观数据获取器<br/>从美联储经济数据库<br/>(FRED)和世界银行API免费获取国际宏观经济指标，包<br/>括美国GDP/CPI/失业率/国债收益率/汇率<br/>/大宗商品，以及各国GDP/人口<br/>/进出口等，补充国内数据源覆盖不到的国际对比数据<br/>文件: implementations/fred_provider.py<br/>(设计态 / design)"]
    src_zephyr_data_kline_resampler_py["880xxx 板块K线合成器——从 1m/5m 合成 15m/30m/60m<br/>写<br/>入 ClickHouse<br/>kline_resampler<br/>文件: data/kline_resampler.py<br/>(生产态 / production)"]
    src_zephyr_data_redundant_source_init_py["数据源冗余与热切换模块（MOD-L00-005）。<br/>P2-8：主备数据源热切换 + CH 冗余降级。<br/>文件: redundant_source/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_satellite_geospatial_engine_init_py["data/satellite_geospatial_engine 包入口<br/>域量化架构 · D_DATA 数据接入层<br/>D_DATA Data Source<br/>文件: satellite_geospatial_engine/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_sector_kline_downloader_py["板块klinedownloader<br/>880xxx 板块指数K线下载器——盘后从 tqcenter<br/>下载日K/分钟K写入 ClickHouse。<br/>sector_kline_downloader<br/>文件: data/sector_kline_downloader.py<br/>(生产态 / production)"]
    src_zephyr_data_sector_snapshot_collector_py["板块快照收集器<br/>880xxx 板块实时快照采集器（tqcenter →<br/>ClickHouse sector_snapshot 表）。<br/>sector_snapshot_collector<br/>文件: data/sector_snapshot_collector.py<br/>(生产态 / production)"]
    src_zephyr_data_symbol_normalizer_init_py["data/symbol_normalizer 包入口<br/>Symbol 标准化模块——TRAE-082 symbol<br/>约定铁律的实现真源。<br/>文件: symbol_normalizer/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_wal_codec_init_py["WAL 段编解码模块（MOD-L00-006）。<br/>WAL 段编解码模块包入口，TSV 格式向后兼容，用<br/>magic number 区分格式。<br/>文件: wal_codec/__init__.py<br/>(生产态 / production)"]
    tests_data_test_market_quality_validator_py["#ARCH-CH-021 P0-4:<br/>写入路径异常值校验器四门禁测试。<br/># P0-4: 写入路径异常值校验器四门禁测试。<br/>test_market_quality_validator<br/>文件: data/test_market_quality_validator.py<br/>(生产态 / production)"]
    tests_data_test_pit_query_py["#ARCH-CH-021 P0-5: 财报 PIT 查询能力测试。<br/># P0-5: 财报 PIT 查询能力测试。<br/>test_pit_query<br/>文件: data/test_pit_query.py<br/>(生产态 / production)"]
    tests_data_test_source_health_check_py["数据源健康检查测试<br/>test_source_health_check.py —<br/>数据源健康检查模块单测。<br/>Test Source Health Check<br/>文件: data/test_source_health_check.py<br/>(生产态 / production)"]
    tests_zephyr_data_test_cross_source_validator_py["测试跨源校验器<br/>cross_source_validator 单元测试（P1-4<br/>多源交叉校验）。<br/>test_cross_source_validator<br/>文件: data/test_cross_source_validator.py<br/>(生产态 / production)"]
    tests_zephyr_data_test_tick_subscriber_py["测试逐笔订阅器<br/>tick_subscriber 单元测试（含 Phase C: WalWriter<br/>+ 批量出队 + 无锁计数）。<br/>test_tick_subscriber<br/>文件: data/test_tick_subscriber.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_balance_sheet_py ~~~ schemas_categories_fundamental_cashflow_statement_py
    schemas_categories_fundamental_cashflow_statement_py ~~~ schemas_categories_fundamental_disclosure_plan_py
    schemas_categories_fundamental_disclosure_plan_py ~~~ schemas_categories_fundamental_equity_pledge_detail_py
    schemas_categories_fundamental_equity_pledge_detail_py ~~~ schemas_categories_fundamental_income_statement_py
    schemas_categories_fundamental_income_statement_py ~~~ schemas_categories_fundamental_industry_class_py
    schemas_categories_fundamental_industry_class_py ~~~ schemas_categories_fundamental_industry_class_suppl_py
    schemas_categories_fundamental_industry_class_suppl_py ~~~ schemas_categories_fundamental_restricted_shares_py
    schemas_categories_fundamental_restricted_shares_py ~~~ schemas_categories_fundamental_rights_issue_py
    schemas_categories_fundamental_rights_issue_py ~~~ schemas_categories_fundamental_share_change_py
    schemas_categories_fundamental_share_change_py ~~~ schemas_categories_fundamental_share_unlock_py
    schemas_categories_fundamental_share_unlock_py ~~~ schemas_categories_macro_edb_data_py
    schemas_categories_macro_edb_data_py ~~~ schemas_categories_macro_macro_data_py
    schemas_categories_macro_macro_data_py ~~~ schemas_categories_market_adj_factor_py
    schemas_categories_market_adj_factor_py ~~~ schemas_categories_market_auction_py
    schemas_categories_market_auction_py ~~~ schemas_categories_market_auction_book_py
    schemas_categories_market_auction_book_py ~~~ schemas_categories_market_block_trade_py
    schemas_categories_market_block_trade_py ~~~ schemas_categories_market_block_trade_detail_py
    schemas_categories_market_block_trade_detail_py ~~~ schemas_categories_market_cb_iv_py
    schemas_categories_market_cb_iv_py ~~~ schemas_categories_market_concept_board_py
    schemas_categories_market_concept_board_py ~~~ schemas_categories_market_concept_board_constituent_py
    schemas_categories_market_concept_board_constituent_py ~~~ schemas_categories_market_concept_sector_py
    schemas_categories_market_concept_sector_py ~~~ schemas_categories_market_convertible_bond_list_py
    schemas_categories_market_convertible_bond_list_py ~~~ schemas_categories_market_daily_valuation_py
    schemas_categories_market_daily_valuation_py ~~~ schemas_categories_market_dragon_tiger_py
    schemas_categories_market_dragon_tiger_py ~~~ schemas_categories_market_dragon_tiger_seat_py
    schemas_categories_market_dragon_tiger_seat_py ~~~ schemas_categories_market_etf_benchmark_py
    schemas_categories_market_etf_benchmark_py ~~~ schemas_categories_market_etf_list_py
    schemas_categories_market_etf_list_py ~~~ schemas_categories_market_etf_nav_py
    schemas_categories_market_etf_nav_py ~~~ schemas_categories_market_futures_kline_qmt_py
    schemas_categories_market_futures_kline_qmt_py ~~~ schemas_categories_market_futures_position_py
    schemas_categories_market_futures_position_py ~~~ schemas_categories_market_futures_term_py
    schemas_categories_market_futures_term_py ~~~ schemas_categories_market_hk_connect_flow_py
    schemas_categories_market_hk_connect_flow_py ~~~ schemas_categories_market_hk_kline_py
    schemas_categories_market_hk_kline_py ~~~ schemas_categories_market_hk_stock_list_py
    schemas_categories_market_hk_stock_list_py ~~~ schemas_categories_market_hk_trade_calendar_py
    schemas_categories_market_hk_trade_calendar_py ~~~ schemas_categories_market_hog_futures_core_py
    schemas_categories_market_hog_futures_core_py ~~~ schemas_categories_market_hog_province_spot_py
    schemas_categories_market_hog_province_spot_py ~~~ schemas_categories_market_hog_spot_index_py
    schemas_categories_market_hog_spot_index_py ~~~ schemas_categories_market_index_py
    schemas_categories_market_index_py ~~~ schemas_categories_market_index_constituent_py
    schemas_categories_market_index_constituent_py ~~~ schemas_categories_market_index_list_py
    schemas_categories_market_index_list_py ~~~ schemas_categories_market_index_meta_py
    schemas_categories_market_index_meta_py ~~~ schemas_categories_market_index_weight_py
    schemas_categories_market_index_weight_py ~~~ schemas_categories_market_kline_15min_py
    schemas_categories_market_kline_15min_py ~~~ schemas_categories_market_kline_1min_py
    schemas_categories_market_kline_1min_py ~~~ schemas_categories_market_kline_30min_py
    schemas_categories_market_kline_30min_py ~~~ schemas_categories_market_kline_5min_py
    schemas_categories_market_kline_5min_py ~~~ schemas_categories_market_kline_60min_py
    schemas_categories_market_kline_60min_py ~~~ schemas_categories_market_kline_cb_py
    schemas_categories_market_kline_cb_py ~~~ schemas_categories_market_kline_daily_py
    schemas_categories_market_kline_daily_py ~~~ schemas_categories_market_kline_daily_hfq_py
    schemas_categories_market_kline_daily_hfq_py ~~~ schemas_categories_market_kline_etf_15min_py
    schemas_categories_market_kline_etf_15min_py ~~~ schemas_categories_market_kline_etf_1min_py
    schemas_categories_market_kline_etf_1min_py ~~~ schemas_categories_market_kline_etf_30min_py
    schemas_categories_market_kline_etf_30min_py ~~~ schemas_categories_market_kline_etf_5min_py
    schemas_categories_market_kline_etf_5min_py ~~~ schemas_categories_market_kline_etf_60min_py
    schemas_categories_market_kline_etf_60min_py ~~~ schemas_categories_market_kline_etf_daily_py
    schemas_categories_market_kline_etf_daily_py ~~~ schemas_categories_market_kline_futures_py
    schemas_categories_market_kline_futures_py ~~~ schemas_categories_market_kline_hk_daily_py
    schemas_categories_market_kline_hk_daily_py ~~~ schemas_categories_market_kline_index_py
    schemas_categories_market_kline_index_py ~~~ schemas_categories_market_kline_lof_15min_py
    schemas_categories_market_kline_lof_15min_py ~~~ schemas_categories_market_kline_lof_1min_py
    schemas_categories_market_kline_lof_1min_py ~~~ schemas_categories_market_kline_lof_30min_py
    schemas_categories_market_kline_lof_30min_py ~~~ schemas_categories_market_kline_lof_5min_py
    schemas_categories_market_kline_lof_5min_py ~~~ schemas_categories_market_kline_lof_60min_py
    schemas_categories_market_kline_lof_60min_py ~~~ schemas_categories_market_kline_monthly_py
    schemas_categories_market_kline_monthly_py ~~~ schemas_categories_market_kline_monthly_hfq_py
    schemas_categories_market_kline_monthly_hfq_py ~~~ schemas_categories_market_kline_sector_py
    schemas_categories_market_kline_sector_py ~~~ schemas_categories_market_kline_sector_880_py
    schemas_categories_market_kline_sector_880_py ~~~ schemas_categories_market_kline_sector_intraday_py
    schemas_categories_market_kline_sector_intraday_py ~~~ schemas_categories_market_kline_us_daily_py
    schemas_categories_market_kline_us_daily_py ~~~ schemas_categories_market_kline_weekly_py
    schemas_categories_market_kline_weekly_py ~~~ schemas_categories_market_kline_weekly_hfq_py
    schemas_categories_market_kline_weekly_hfq_py ~~~ schemas_categories_market_l2_tick_py
    schemas_categories_market_l2_tick_py ~~~ schemas_categories_market_limit_up_down_py
    schemas_categories_market_limit_up_down_py ~~~ schemas_categories_market_lof_list_py
    schemas_categories_market_lof_list_py ~~~ schemas_categories_market_margin_trading_py
    schemas_categories_market_margin_trading_py ~~~ schemas_categories_market_money_flow_py
    schemas_categories_market_money_flow_py ~~~ schemas_categories_market_option_greeks_py
    schemas_categories_market_option_greeks_py ~~~ schemas_categories_market_option_iv_py
    schemas_categories_market_option_iv_py ~~~ schemas_categories_market_option_kline_py
    schemas_categories_market_option_kline_py ~~~ schemas_categories_market_realtime_snapshot_py
    schemas_categories_market_realtime_snapshot_py ~~~ schemas_categories_market_sector_constituent_py
    schemas_categories_market_sector_constituent_py ~~~ schemas_categories_market_sector_list_py
    schemas_categories_market_sector_list_py ~~~ schemas_categories_market_sector_meta_py
    schemas_categories_market_sector_meta_py ~~~ schemas_categories_market_sector_snapshot_py
    schemas_categories_market_sector_snapshot_py ~~~ schemas_categories_market_st_stock_list_py
    schemas_categories_market_st_stock_list_py ~~~ schemas_categories_market_stock_indicator_py
    schemas_categories_market_stock_indicator_py ~~~ schemas_categories_market_stock_list_py
    schemas_categories_market_stock_list_py ~~~ schemas_categories_market_tick_py
    schemas_categories_market_tick_py ~~~ schemas_categories_market_trade_calendar_py
    schemas_categories_market_trade_calendar_py ~~~ schemas_categories_market_us_index_py
    schemas_categories_market_us_index_py ~~~ scripts_ch_data_inventory_py
    scripts_ch_data_inventory_py ~~~ scripts_ch_recovery_drill_py
    scripts_ch_recovery_drill_py ~~~ scripts_ch_apply_fundamental_tables_ddl_py
    scripts_ch_apply_fundamental_tables_ddl_py ~~~ scripts_ch_apply_market_tables_ddl_py
    scripts_ch_apply_market_tables_ddl_py ~~~ scripts_ch_apply_rbac_py
    scripts_ch_apply_rbac_py ~~~ scripts_ch_lint_symbol_convention_py
    scripts_ch_lint_symbol_convention_py ~~~ scripts_ch_verify_exchange_coverage_py
    scripts_ch_verify_exchange_coverage_py ~~~ scripts_ch_verify_schema_truth_py
    scripts_ch_verify_schema_truth_py ~~~ scripts_ops_ch_health_probe_py
    scripts_ops_ch_health_probe_py ~~~ scripts_ops_verify_alert_channels_py
    scripts_ops_verify_alert_channels_py ~~~ scripts_register_aux_tasks_ps1
    scripts_register_aux_tasks_ps1 ~~~ scripts_register_guard_tasks_ps1
    scripts_register_guard_tasks_ps1 ~~~ scripts_start_ch_health_probe_ps1
    scripts_start_ch_health_probe_ps1 ~~~ scripts_start_scheduler_ps1
    scripts_start_scheduler_ps1 ~~~ scripts_start_tick_subscriber_ps1
    scripts_start_tick_subscriber_ps1 ~~~ src_zephyr_data_main_py
    src_zephyr_data_main_py ~~~ src_zephyr_data_config_policies_yaml
    src_zephyr_data_config_policies_yaml ~~~ src_zephyr_data_config_schedule_yaml
    src_zephyr_data_config_schedule_yaml ~~~ src_zephyr_data_config_tasks_yaml
    src_zephyr_data_config_tasks_yaml ~~~ src_zephyr_data_connectors
    src_zephyr_data_connectors ~~~ src_zephyr_data_implementations_init_py
    src_zephyr_data_implementations_init_py ~~~ src_zephyr_data_implementations_fred_provider_py
    src_zephyr_data_implementations_fred_provider_py ~~~ src_zephyr_data_kline_resampler_py
    src_zephyr_data_kline_resampler_py ~~~ src_zephyr_data_redundant_source_init_py
    src_zephyr_data_redundant_source_init_py ~~~ src_zephyr_data_satellite_geospatial_engine_init_py
    src_zephyr_data_satellite_geospatial_engine_init_py ~~~ src_zephyr_data_sector_kline_downloader_py
    src_zephyr_data_sector_kline_downloader_py ~~~ src_zephyr_data_sector_snapshot_collector_py
    src_zephyr_data_sector_snapshot_collector_py ~~~ src_zephyr_data_symbol_normalizer_init_py
    src_zephyr_data_symbol_normalizer_init_py ~~~ src_zephyr_data_wal_codec_init_py
    src_zephyr_data_wal_codec_init_py ~~~ tests_data_test_market_quality_validator_py
    tests_data_test_market_quality_validator_py ~~~ tests_data_test_pit_query_py
    tests_data_test_pit_query_py ~~~ tests_data_test_source_health_check_py
    tests_data_test_source_health_check_py ~~~ tests_zephyr_data_test_cross_source_validator_py
    tests_zephyr_data_test_cross_source_validator_py ~~~ tests_zephyr_data_test_tick_subscriber_py
    schemas_categories_cross_validation_log_py["跨验证日志<br/>存储 QMT 主源 vs TDX 备源的 tick<br/>数据交叉校验结果，<br/>cross_validation_log<br/>文件: categories/cross_validation_log.py<br/>(生产态 / production)"]
    scripts_ch_apply_exchange_columns_py["apply交易所columns<br/>处理数据读写与转换（apply exchange columns）<br/>apply_exchange_columns<br/>文件: ch/apply_exchange_columns.py<br/>(生产态 / production)"]
    scripts_ch_apply_timezone_migration_py["应用timezone迁移<br/>ClickHouse 时区防线迁移脚本（audit A组 Schema<br/>治理 - 时区防线，#ARCH-CH-022）。<br/>apply_timezone_migration<br/>文件: ch/apply_timezone_migration.py<br/>(生产态 / production)"]
    src_zephyr_data_alerter_py["告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8<br/>可观测性）<br/>告警触发条件（蓝图 §6.5）：<br/>alerter<br/>文件: data/alerter.py<br/>(生产态 / production)"]
    src_zephyr_data_cli_py["数据源集成器 CLI（MOD-L00-004 §8.4）。<br/>数据源集成器命令行入口，用 argparse 加<br/>subparsers 实现 8 个子命令。<br/>文件: data/cli.py<br/>(生产态 / production)"]
    src_zephyr_data_cross_source_validator_py["跨源校验器<br/>多源交叉校验器——比较 QMT 主源与 TDX 备源 tick<br/>数据一致性（P1-4）。<br/>cross_source_validator<br/>文件: data/cross_source_validator.py<br/>(生产态 / production)"]
    src_zephyr_data_normalizers["归一化器<br/>归一化的子目录，归集相关子模块<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: normalizers/<br/>(设计态 / design)"]
    src_zephyr_data_pit_query_py["pit查询<br/>处理数据读写与转换（pit query）<br/>pit_query<br/>文件: data/pit_query.py<br/>(生产态 / production)"]
    src_zephyr_data_sector_ranking_engine_py["880xxx 板块动态排名引擎——5因子复合排名调整99只推<br/>送池。<br/>5因子复合排名（权重之和=1.0）：<br/>sector_ranking_engine<br/>文件: data/sector_ranking_engine.py<br/>(生产态 / production)"]
    src_zephyr_data_source_health_check_py["数据源健康检查<br/>调度器每天启动时给所有数据源做体检——挨个测连接和<br/>拉数据，记录哪个通哪个不通并写日志。查出毛病的源<br/>只记录不自动停，留给人工或备用源处理，绝不让体检<br/>本身卡住调度器启动。<br/>文件: data/source_health_check.py<br/>(生产态 / production)"]
    src_zephyr_data_tick_subscriber_py["逐笔订阅器<br/>QMT 实时 Tick 订阅服务——subscribe_quote<br/>实时推送，写入 ClickHouse tick_data。<br/>tick_subscriber<br/>文件: data/tick_subscriber.py<br/>(生产态 / production)"]
    schemas_categories_cross_validation_log_py ~~~ scripts_ch_apply_exchange_columns_py
    scripts_ch_apply_exchange_columns_py ~~~ scripts_ch_apply_timezone_migration_py
    scripts_ch_apply_timezone_migration_py ~~~ src_zephyr_data_alerter_py
    src_zephyr_data_alerter_py ~~~ src_zephyr_data_cli_py
    src_zephyr_data_cli_py ~~~ src_zephyr_data_cross_source_validator_py
    src_zephyr_data_cross_source_validator_py ~~~ src_zephyr_data_normalizers
    src_zephyr_data_normalizers ~~~ src_zephyr_data_pit_query_py
    src_zephyr_data_pit_query_py ~~~ src_zephyr_data_sector_ranking_engine_py
    src_zephyr_data_sector_ranking_engine_py ~~~ src_zephyr_data_source_health_check_py
    src_zephyr_data_source_health_check_py ~~~ src_zephyr_data_tick_subscriber_py
    schemas_categories_fundamental_analyst_forecast_py["fundamentalanalyst预测<br/>本文件是 c3_fundamental.analyst_forecast<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_analyst_forecast<br/>文件: categories/fundamental_analyst_forecast.py<br/>(生产态 / production)"]
    src_zephyr_data_ch_config_py["ch配置<br/>ClickHouse 连接配置单真源加载器（裁定<br/>#ARCH-CH-017 / #ARCH-CH-019）。<br/>ch_config<br/>文件: data/ch_config.py<br/>(生产态 / production)"]
    src_zephyr_data_ch_reader_py["ch读取器<br/>处理数据读写与转换（ch reader）<br/>ch_reader<br/>文件: data/ch_reader.py<br/>(生产态 / production)"]
    src_zephyr_data_progress_store_py["统一进度存储（MOD-L00-004 §7）。<br/>统一进度存储，SQLite<br/>单文件存储数据集成进度，支持断点续传。<br/>progress_store<br/>文件: data/progress_store.py<br/>(生产态 / production)"]
    src_zephyr_data_scheduler_py["数据源调度编排层（MOD-L00-004 §6）。<br/>APScheduler 常驻进程，按 cron<br/>时段触发任务批次，管理 DAG 依赖，<br/>文件: data/scheduler.py<br/>(生产态 / production)"]
    src_zephyr_data_speed_tester_py["数据源测速器（MOD-L00-004 §8.5）。<br/>对每个数据能力×每个可用数据源做小样本测速，记录<br/>rows/sec、symbols/sec、错误率，<br/>speed_tester<br/>文件: data/speed_tester.py<br/>(生产态 / production)"]
    src_zephyr_data_storage["存储<br/>存储的子目录，归集相关子模块<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: storage/<br/>(设计态 / design)"]
    src_zephyr_data_symbol_normalizer_normalizer_py["归一化器<br/>symbol 标准化核心实现——TRAE-082 symbol<br/>约定铁律。<br/>normalizer<br/>文件: symbol_normalizer/normalizer.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_analyst_forecast_py ~~~ src_zephyr_data_ch_config_py
    src_zephyr_data_ch_config_py ~~~ src_zephyr_data_ch_reader_py
    src_zephyr_data_ch_reader_py ~~~ src_zephyr_data_progress_store_py
    src_zephyr_data_progress_store_py ~~~ src_zephyr_data_scheduler_py
    src_zephyr_data_scheduler_py ~~~ src_zephyr_data_speed_tester_py
    src_zephyr_data_speed_tester_py ~~~ src_zephyr_data_storage
    src_zephyr_data_storage ~~~ src_zephyr_data_symbol_normalizer_normalizer_py
    src_zephyr_data_init_py["zephyr/data 包入口<br/>包入口.data — 数据源集成器（MOD-L00-004）。<br/>文件: data/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_cache["缓存<br/>缓存的子目录，归集相关子模块<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: cache/<br/>(设计态 / design)"]
    src_zephyr_data_ch_writer_py["ch写入器<br/>ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6步<br/>+ §7.3 幂等性）。<br/>ch_writer<br/>文件: data/ch_writer.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_akshare_provider_py["akshare提供器<br/>封装 AKShare 开源金融数据 SDK，继承<br/>IngestProviderBase。<br/>akshare_provider<br/>文件: implementations/akshare_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_baostock_provider_py["baostock提供器<br/>匿名访问（bs.login() 无需<br/>token，处理数据读写与转换<br/>baostock_provider<br/>文件: implementations/baostock_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_cls_provider_py["cls提供器<br/>财联社电报数据源 Provider 实现（MOD-L00-004<br/>§4.3）。<br/>cls_provider<br/>文件: implementations/cls_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_eastmoney_news_provider_py["eastmoney新闻提供器<br/>东方财富新闻数据源 Provider 实现（MOD-L00-004<br/>§4.3）。<br/>eastmoney_news_provider<br/>文件: implementations/eastmoney_news_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_miniqmt_provider_py["miniqmt提供器<br/>MOD-L00-004 数据源集成器 ·<br/>MiniQmtIngestProvider 实现。<br/>miniqmt_provider<br/>文件: implementations/miniqmt_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_rss_provider_py["rss提供器<br/>RSS 财经新闻数据源 Provider 实现（MOD-L00-004<br/>§4.3）。<br/>rss_provider<br/>文件: implementations/rss_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tdx_provider_py["tdx提供器<br/>通达信数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>tdx_provider<br/>文件: implementations/tdx_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tickflow_provider_py["tickflow提供器<br/>60 次/分钟限流（必须 _call_with_policy<br/>包裹以触发 RPM 限流）<br/>tickflow_provider<br/>文件: implementations/tickflow_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tushare_provider_py["tushare提供器<br/>token认证（环境变量TUSHARE_TOKEN）；历史数据截止<br/>2024-08；积分不足触发重试<br/>tushare_provider<br/>文件: implementations/tushare_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_policy_registry_py["策略注册表<br/>每个数据源有自己的限流/重试/反爬<br/>/登录刷新策略，集中管理、yaml 热更新。<br/>policy_registry<br/>文件: data/policy_registry.py<br/>(生产态 / production)"]
    src_zephyr_data_provider_base_py["提供器基类<br/>定义所有数据源封装的统一接口：<br/>provider_base<br/>文件: data/provider_base.py<br/>(生产态 / production)"]
    src_zephyr_data_table_registry_py["table注册表<br/>表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase<br/>2）。<br/>table_registry<br/>文件: data/table_registry.py<br/>(生产态 / production)"]
    src_zephyr_data_init_py ~~~ src_zephyr_data_cache
    src_zephyr_data_cache ~~~ src_zephyr_data_ch_writer_py
    src_zephyr_data_ch_writer_py ~~~ src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_implementations_akshare_provider_py ~~~ src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_implementations_baostock_provider_py ~~~ src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_implementations_cls_provider_py ~~~ src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_implementations_eastmoney_news_provider_py ~~~ src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_implementations_miniqmt_provider_py ~~~ src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_implementations_rss_provider_py ~~~ src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_implementations_tdx_provider_py ~~~ src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_implementations_tickflow_provider_py ~~~ src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_implementations_tushare_provider_py ~~~ src_zephyr_data_policy_registry_py
    src_zephyr_data_policy_registry_py ~~~ src_zephyr_data_provider_base_py
    src_zephyr_data_provider_base_py ~~~ src_zephyr_data_table_registry_py
    src_zephyr_data_backfill_checker_py["L10 周末补下载检测器——检测过去N天缺失数据并精准<br/>补下载。<br/>backfill_checker<br/>文件: data/backfill_checker.py<br/>(生产态 / production)"]
    src_zephyr_data_buffered_writer_py["批量聚合写入器（MOD-L00-004 §18.3 裁定<br/>#ARCH-CH-003<br/>批量聚合写入器（MOD-L00-004 §18.3 裁定 #。<br/>buffered_writer<br/>文件: data/buffered_writer.py<br/>(生产态 / production)"]
    src_zephyr_data_capability_validator_py["能力校验器<br/>Provider Capability 行为契约校验器（裁定<br/>#ARCH-CH-022）。<br/>capability_validator<br/>文件: data/capability_validator.py<br/>(生产态 / production)"]
    src_zephyr_data_error_classifier_py["数据源错误分类器——根据错误字符串判断可恢复性。<br/>设计理念（数据韧性三层机制 §2）：<br/>error_classifier<br/>文件: data/error_classifier.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_eia_provider_py["implementations/eia_provider<br/>EiaProvider 实现（MOD-L00-004 §4.3<br/>数据源集成器）。<br/>文件: implementations/eia_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_qweather_provider_py["implementations/qweather_provider<br/>QWeatherProvider 实现（MOD-L00-004 §4.3<br/>数据源集成器）。<br/>文件: implementations/qweather_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tqcenter_provider_py["TQCenter提供器<br/>封装 tqcenter SDK（通达信插件），继承<br/>IngestProviderBase。<br/>tqcenter_provider<br/>文件: implementations/tqcenter_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_integrity_checker_py["数据完整性巡检器——每天盘后检测全表当日数据是否达<br/>标。<br/>设计理念（数据韧性三层机制 §3）：<br/>integrity_checker<br/>文件: data/integrity_checker.py<br/>(生产态 / production)"]
    src_zephyr_data_local_replay_py["本地replay<br/>本地落盘兜底 + 自动回灌（裁定 #ARCH-CH-013<br/>Phase 1）。<br/>local_replay<br/>文件: data/local_replay.py<br/>(生产态 / production)"]
    src_zephyr_data_metrics_py["可观测性指标采集（MOD-L00-004 §11）。<br/>不依赖 prometheus_client 库，直接按 Prometheus<br/>文本格式写入 data/metrics.prom。<br/>文件: data/metrics.py<br/>(生产态 / production)"]
    src_zephyr_data_news_dedup_py["新闻数据去重模块（MOD-L00-004 §4.3）。<br/>基于标题 MD5 哈希对新闻数据进行查重去重。<br/>news_dedup<br/>文件: data/news_dedup.py<br/>(生产态 / production)"]
    src_zephyr_data_quality_gate_py["质量门禁<br/>治本修复: 测试通过 zephyr.data.quality_gate<br/>导入 QualityReport，但真源在<br/>文件: data/quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_data_task_queue_py["任务依赖图 + 优先级队列（MOD-L00-004 §6.3<br/>任务依赖图 + §<br/>6.4 并发控制）<br/>task_queue<br/>文件: data/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_data_trading_calendar_py["A 股交易日历守卫（MOD-L00-004）。<br/>基于 exchange_calendars 包的 XSHG<br/>（上海证券交易所）日历，<br/>trading_calendar<br/>文件: data/trading_calendar.py<br/>(生产态 / production)"]
    src_zephyr_data_wal_writer_py["wal写入器<br/>数据先落本地 WAL 段文件，再由后台 drain<br/>线程异步排空到 ClickHouse。<br/>wal_writer<br/>文件: data/wal_writer.py<br/>(生产态 / production)"]
    src_zephyr_data_backfill_checker_py ~~~ src_zephyr_data_buffered_writer_py
    src_zephyr_data_buffered_writer_py ~~~ src_zephyr_data_capability_validator_py
    src_zephyr_data_capability_validator_py ~~~ src_zephyr_data_error_classifier_py
    src_zephyr_data_error_classifier_py ~~~ src_zephyr_data_implementations_eia_provider_py
    src_zephyr_data_implementations_eia_provider_py ~~~ src_zephyr_data_implementations_qweather_provider_py
    src_zephyr_data_implementations_qweather_provider_py ~~~ src_zephyr_data_implementations_tqcenter_provider_py
    src_zephyr_data_implementations_tqcenter_provider_py ~~~ src_zephyr_data_integrity_checker_py
    src_zephyr_data_integrity_checker_py ~~~ src_zephyr_data_local_replay_py
    src_zephyr_data_local_replay_py ~~~ src_zephyr_data_metrics_py
    src_zephyr_data_metrics_py ~~~ src_zephyr_data_news_dedup_py
    src_zephyr_data_news_dedup_py ~~~ src_zephyr_data_quality_gate_py
    src_zephyr_data_quality_gate_py ~~~ src_zephyr_data_task_queue_py
    src_zephyr_data_task_queue_py ~~~ src_zephyr_data_trading_calendar_py
    src_zephyr_data_trading_calendar_py ~~~ src_zephyr_data_wal_writer_py
    src_zephyr_data_connectors -.->|data / data| src_zephyr_data_normalizers
    src_zephyr_data_normalizers -.->|data / data| src_zephyr_data_storage
    src_zephyr_data_storage -.->|data / data| src_zephyr_data_cache
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_tick_subscriber_py
    src_zephyr_data_buffered_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_buffered_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_progress_store_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_speed_tester_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_scheduler_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_quality_gate_py
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_capability_validator_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_backfill_checker_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_local_replay_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_kline_resampler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_provider_base_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_sector_snapshot_collector_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_sector_snapshot_collector_py -->|导入依赖 / import_depends| src_zephyr_data_sector_ranking_engine_py
    src_zephyr_data_source_health_check_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_source_health_check_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_scheduler_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_wal_writer_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_main_py -->|导入依赖 / import_depends| src_zephyr_data_cli_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_satellite_geospatial_engine_init_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_symbol_normalizer_init_py -->|导入依赖 / import_depends| src_zephyr_data_symbol_normalizer_normalizer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_backfill_checker_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_buffered_writer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_capability_validator_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_integrity_checker_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_error_classifier_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_progress_store_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_metrics_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_source_health_check_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_task_queue_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_trading_calendar_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eia_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_qweather_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tqcenter_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    scripts_ch_lint_symbol_convention_py -->|config_depends / config_depends| scripts_ch_apply_timezone_migration_py
    scripts_ch_apply_timezone_migration_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| scripts_ch_apply_exchange_columns_py
    scripts_ch_apply_rbac_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_symbol_normalizer_normalizer_py
    scripts_ch_verify_schema_truth_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_data_inventory_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_recovery_drill_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ops_verify_alert_channels_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    tests_data_test_source_health_check_py -->|测试依赖 / test_depends| src_zephyr_data_source_health_check_py
    tests_data_test_pit_query_py -->|测试依赖 / test_depends| src_zephyr_data_pit_query_py
    tests_data_test_pit_query_py -->|测试依赖 / test_depends| src_zephyr_data_init_py
    tests_zephyr_data_test_cross_source_validator_py -->|测试依赖 / test_depends| src_zephyr_data_cross_source_validator_py
    tests_zephyr_data_test_tick_subscriber_py -->|测试依赖 / test_depends| src_zephyr_data_tick_subscriber_py
    schemas_categories_cross_validation_log_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_balance_sheet_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_disclosure_plan_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_cashflow_statement_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_income_statement_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_industry_class_suppl_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_restricted_shares_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_rights_issue_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_equity_pledge_detail_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_industry_class_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_macro_macro_data_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_macro_edb_data_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_share_unlock_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_share_change_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_adj_factor_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_auction_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_auction_book_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_block_trade_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_convertible_bond_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_concept_board_constituent_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_block_trade_detail_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_concept_sector_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_cb_iv_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_daily_valuation_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_concept_board_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_dragon_tiger_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_dragon_tiger_seat_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_etf_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_etf_benchmark_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_etf_nav_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_futures_kline_qmt_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_futures_position_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_connect_flow_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_futures_term_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_kline_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_trade_calendar_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hog_futures_core_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_stock_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hog_province_spot_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_constituent_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_weight_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hog_spot_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_meta_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_15min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_30min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_5min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_1min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_15min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_cb_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_daily_hfq_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_60min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_60min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_1min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_5min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_30min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_futures_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_hk_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_60min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_1min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_monthly_hfq_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_5min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_30min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_monthly_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_sector_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_15min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_sector_880_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_lof_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_weekly_hfq_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_sector_intraday_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_us_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_l2_tick_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_limit_up_down_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_margin_trading_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_weekly_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_option_kline_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_money_flow_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_constituent_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_meta_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_option_iv_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_option_greeks_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_stock_indicator_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_realtime_snapshot_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_stock_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_snapshot_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_us_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_tick_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_trade_calendar_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_st_stock_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    D_SHARED["共享服务<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>Shared Services<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_source_health_check_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_source_health_check_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_alerter_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["规则执行<br/>规则执行，负责治理规则执行和门禁拦截<br/>Rule Enforcement<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    src_zephyr_data_quality_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_data_ch_config_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| D_SHARED
    tests_data_test_market_quality_validator_py -->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| D_SHARED
    D_MKT_DATA["行情数据<br/>行情数据，负责市场行情数据的采集、分发和订阅管理<br/>Market Data<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_MKT_DATA -->|runtime / runtime| src_zephyr_data_table_registry_py
    D_ML_TRAIN["训练<br/>训练，负责模型训练、特征工程和模型评估<br/>Training<br/>跨域节点 / cross-domain<br/>(设计态 / design)"]
    D_ML_TRAIN -.->|data / data| src_zephyr_data_pit_query_py
    D_ML_TRAIN -.->|data / data| src_zephyr_data_pit_query_py
    D_ML_TRAIN -.->|data / data| src_zephyr_data_table_registry_py
    D_INFRA_OPS["基础设施运维<br/>资产清单与运维扫描，负责运行时资产盘点、基础设施<br/>配置管理和运维自动化<br/>Asset Inventory<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INFRA_OPS -->|config_depends / config_depends| scripts_ops_ch_health_probe_py
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_BACKTEST["回测<br/>回测，负责历史数据回测、回测引擎和回测报告<br/>Backtest<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_BACKTEST -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_GOV_CODE_QUALITY["代码质量治理<br/>代码质量治理，负责代码去重引擎、函数重复检测、AS<br/>T语义分析和提交门禁引擎<br/>Code Quality Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_data_capability_validator_py
    D_FACTOR["因子<br/>因子，负责因子计算、因子库管理和因子评价<br/>Factor<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_GOVERNANCE["生命周期管理<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>Lifecycle Management<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_GOVERNANCE -->|测试依赖 / test_depends| src_zephyr_data_quality_gate_py
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_INFRA_RUNTIME["运行时集成<br/>运行时集成，负责组件生命周期编排、启动钩子和运行<br/>时上下文管理<br/>Runtime Integration<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_data_tick_subscriber_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_cross_validation_log_py,schemas_categories_fundamental_analyst_forecast_py,schemas_categories_fundamental_balance_sheet_py,schemas_categories_fundamental_cashflow_statement_py,schemas_categories_fundamental_disclosure_plan_py,schemas_categories_fundamental_equity_pledge_detail_py,schemas_categories_fundamental_income_statement_py,schemas_categories_fundamental_industry_class_py,schemas_categories_fundamental_industry_class_suppl_py,schemas_categories_fundamental_restricted_shares_py,schemas_categories_fundamental_rights_issue_py,schemas_categories_fundamental_share_change_py,schemas_categories_fundamental_share_unlock_py,schemas_categories_macro_edb_data_py,schemas_categories_macro_macro_data_py,schemas_categories_market_adj_factor_py,schemas_categories_market_auction_py,schemas_categories_market_auction_book_py,schemas_categories_market_block_trade_py,schemas_categories_market_block_trade_detail_py,schemas_categories_market_cb_iv_py,schemas_categories_market_concept_board_py,schemas_categories_market_concept_board_constituent_py,schemas_categories_market_concept_sector_py,schemas_categories_market_convertible_bond_list_py,schemas_categories_market_daily_valuation_py,schemas_categories_market_dragon_tiger_py,schemas_categories_market_dragon_tiger_seat_py,schemas_categories_market_etf_benchmark_py,schemas_categories_market_etf_list_py,schemas_categories_market_etf_nav_py,schemas_categories_market_futures_kline_qmt_py,schemas_categories_market_futures_position_py,schemas_categories_market_futures_term_py,schemas_categories_market_hk_connect_flow_py,schemas_categories_market_hk_kline_py,schemas_categories_market_hk_stock_list_py,schemas_categories_market_hk_trade_calendar_py,schemas_categories_market_hog_futures_core_py,schemas_categories_market_hog_province_spot_py,schemas_categories_market_hog_spot_index_py,schemas_categories_market_index_py,schemas_categories_market_index_constituent_py,schemas_categories_market_index_list_py,schemas_categories_market_index_meta_py,schemas_categories_market_index_weight_py,schemas_categories_market_kline_15min_py,schemas_categories_market_kline_1min_py,schemas_categories_market_kline_30min_py,schemas_categories_market_kline_5min_py,schemas_categories_market_kline_60min_py,schemas_categories_market_kline_cb_py,schemas_categories_market_kline_daily_py,schemas_categories_market_kline_daily_hfq_py,schemas_categories_market_kline_etf_15min_py,schemas_categories_market_kline_etf_1min_py,schemas_categories_market_kline_etf_30min_py,schemas_categories_market_kline_etf_5min_py,schemas_categories_market_kline_etf_60min_py,schemas_categories_market_kline_etf_daily_py,schemas_categories_market_kline_futures_py,schemas_categories_market_kline_hk_daily_py,schemas_categories_market_kline_index_py,schemas_categories_market_kline_lof_15min_py,schemas_categories_market_kline_lof_1min_py,schemas_categories_market_kline_lof_30min_py,schemas_categories_market_kline_lof_5min_py,schemas_categories_market_kline_lof_60min_py,schemas_categories_market_kline_monthly_py,schemas_categories_market_kline_monthly_hfq_py,schemas_categories_market_kline_sector_py,schemas_categories_market_kline_sector_880_py,schemas_categories_market_kline_sector_intraday_py,schemas_categories_market_kline_us_daily_py,schemas_categories_market_kline_weekly_py,schemas_categories_market_kline_weekly_hfq_py,schemas_categories_market_l2_tick_py,schemas_categories_market_limit_up_down_py,schemas_categories_market_lof_list_py,schemas_categories_market_margin_trading_py,schemas_categories_market_money_flow_py,schemas_categories_market_option_greeks_py,schemas_categories_market_option_iv_py,schemas_categories_market_option_kline_py,schemas_categories_market_realtime_snapshot_py,schemas_categories_market_sector_constituent_py,schemas_categories_market_sector_list_py,schemas_categories_market_sector_meta_py,schemas_categories_market_sector_snapshot_py,schemas_categories_market_st_stock_list_py,schemas_categories_market_stock_indicator_py,schemas_categories_market_stock_list_py,schemas_categories_market_tick_py,schemas_categories_market_trade_calendar_py,schemas_categories_market_us_index_py,scripts_ch_data_inventory_py,scripts_ch_recovery_drill_py,scripts_ch_apply_exchange_columns_py,scripts_ch_apply_fundamental_tables_ddl_py,scripts_ch_apply_market_tables_ddl_py,scripts_ch_apply_rbac_py,scripts_ch_apply_timezone_migration_py,scripts_ch_lint_symbol_convention_py,scripts_ch_verify_exchange_coverage_py,scripts_ch_verify_schema_truth_py,scripts_ops_ch_health_probe_py,scripts_ops_verify_alert_channels_py,scripts_register_aux_tasks_ps1,scripts_register_guard_tasks_ps1,scripts_start_ch_health_probe_ps1,scripts_start_scheduler_ps1,scripts_start_tick_subscriber_ps1,src_zephyr_data_init_py,src_zephyr_data_main_py,src_zephyr_data_alerter_py,src_zephyr_data_backfill_checker_py,src_zephyr_data_buffered_writer_py,src_zephyr_data_capability_validator_py,src_zephyr_data_ch_config_py,src_zephyr_data_ch_reader_py,src_zephyr_data_ch_writer_py,src_zephyr_data_cli_py,src_zephyr_data_config_policies_yaml,src_zephyr_data_config_schedule_yaml,src_zephyr_data_config_tasks_yaml,src_zephyr_data_cross_source_validator_py,src_zephyr_data_error_classifier_py,src_zephyr_data_implementations_init_py,src_zephyr_data_implementations_akshare_provider_py,src_zephyr_data_implementations_baostock_provider_py,src_zephyr_data_implementations_cls_provider_py,src_zephyr_data_implementations_eastmoney_news_provider_py,src_zephyr_data_implementations_eia_provider_py,src_zephyr_data_implementations_miniqmt_provider_py,src_zephyr_data_implementations_qweather_provider_py,src_zephyr_data_implementations_rss_provider_py,src_zephyr_data_implementations_tdx_provider_py,src_zephyr_data_implementations_tickflow_provider_py,src_zephyr_data_implementations_tqcenter_provider_py,src_zephyr_data_implementations_tushare_provider_py,src_zephyr_data_integrity_checker_py,src_zephyr_data_kline_resampler_py,src_zephyr_data_local_replay_py,src_zephyr_data_metrics_py,src_zephyr_data_news_dedup_py,src_zephyr_data_pit_query_py,src_zephyr_data_policy_registry_py,src_zephyr_data_progress_store_py,src_zephyr_data_provider_base_py,src_zephyr_data_quality_gate_py,src_zephyr_data_redundant_source_init_py,src_zephyr_data_satellite_geospatial_engine_init_py,src_zephyr_data_scheduler_py,src_zephyr_data_sector_kline_downloader_py,src_zephyr_data_sector_ranking_engine_py,src_zephyr_data_sector_snapshot_collector_py,src_zephyr_data_source_health_check_py,src_zephyr_data_speed_tester_py,src_zephyr_data_symbol_normalizer_init_py,src_zephyr_data_symbol_normalizer_normalizer_py,src_zephyr_data_table_registry_py,src_zephyr_data_task_queue_py,src_zephyr_data_tick_subscriber_py,src_zephyr_data_trading_calendar_py,src_zephyr_data_wal_codec_init_py,src_zephyr_data_wal_writer_py,tests_data_test_market_quality_validator_py,tests_data_test_pit_query_py,tests_data_test_source_health_check_py,tests_zephyr_data_test_cross_source_validator_py,tests_zephyr_data_test_tick_subscriber_py production
    class src_zephyr_data_cache,src_zephyr_data_connectors,src_zephyr_data_implementations_fred_provider_py,src_zephyr_data_normalizers,src_zephyr_data_storage design
    class D_SHARED,D_GOV_ENFORCEMENT,D_MKT_DATA,D_INFRA_OPS,D_GOV_SCRIPTS,D_BACKTEST,D_GOV_CODE_QUALITY,D_FACTOR,D_GOVERNANCE,D_INFRA_RUNTIME external_prod
    class D_ML_TRAIN external_design
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 171 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    schemas_categories_fundamental_balance_sheet_py["fundamental余额sheet<br/>本文件是 c3_fundamental.balance_sheet<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_balance_sheet<br/>文件: categories/fundamental_balance_sheet.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_cashflow_statement_py["fundamentalcashflow报表<br/>本文件是 c3_fundamental.cashflow_statement<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_cashflow_statement<br/>文件: categories<br/>/fundamental_cashflow_statement.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_disclosure_plan_py["fundamentaldisclosure计划<br/>本文件是 c3_fundamental.disclosure_plan<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_disclosure_plan<br/>文件: categories/fundamental_disclosure_plan.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_equity_pledge_detail_py["fundamentalequitypledge详情<br/>（股权质押明细）DDL-as-Code（category_id:<br/>fundamental_equity_pledge_detail）<br/>文件: categories<br/>/fundamental_equity_pledge_detail.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_income_statement_py["fundamentalincome报表<br/>本文件是 c3_fundamental.income_statement<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_income_statement<br/>文件: categories/fundamental_income_statement.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_industry_class_py["fundamentalindustry类<br/>本文件是 c1_market.industry_class<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_industry_class<br/>文件: categories/fundamental_industry_class.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_industry_class_suppl_py["fundamentalindustry类suppl<br/>补充行业分类 DDL，定义<br/>fundamental_industry_class_suppl 分类表结构。<br/>文件: categories<br/>/fundamental_industry_class_suppl.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_restricted_shares_py["restrictedshares（限售股明细）DDL-as-Code（cate<br/>（限售股明细）DDL-as-Code（cate<br/>（限售股明细）DDL-as-Code（category_id:<br/>fundamental_restricted_shares）<br/>文件: categories<br/>/fundamental_restricted_shares.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_rights_issue_py["rightsissue（分红配股）DDL-as-Code（categoryi<br/>（分红配股）DDL-as-Code（categoryi<br/>（分红配股）DDL-as-Code（category_id:<br/>fundamental_rights_issue）<br/>文件: categories/fundamental_rights_issue.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_share_change_py["fundamental股票变更<br/>（股本变动）DDL-as-Code（category_id:<br/>fundamental_share_change）<br/>文件: categories/fundamental_share_change.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_share_unlock_py["fundamental股票unlock<br/>本文件是 c3_fundamental.share_unlock<br/>表结构的唯一真源。<br/>fundamental_share_unlock<br/>文件: categories/fundamental_share_unlock.py<br/>(生产态 / production)"]
    schemas_categories_macro_edb_data_py["macroedb数据<br/>本文件是 c1_market.edb_data 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>macro_edb_data<br/>文件: categories/macro_edb_data.py<br/>(生产态 / production)"]
    schemas_categories_macro_macro_data_py["macromacro数据<br/>本文件是 c1_market.macro_data 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>macro_macro_data<br/>文件: categories/macro_macro_data.py<br/>(生产态 / production)"]
    schemas_categories_market_adj_factor_py["行情adj因子<br/>本文件是 c1_market.adj_factor 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_adj_factor<br/>文件: categories/market_adj_factor.py<br/>(生产态 / production)"]
    schemas_categories_market_auction_py["行情拍卖<br/>本文件是 c1_market.auction_snapshot<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_auction<br/>文件: categories/market_auction.py<br/>(生产态 / production)"]
    schemas_categories_market_auction_book_py["行情拍卖book<br/>本文件是 c1_market.auction_book<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_auction_book<br/>文件: categories/market_auction_book.py<br/>(生产态 / production)"]
    schemas_categories_market_block_trade_py["行情块交易<br/>本文件是 c1_market.block_trade<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_block_trade<br/>文件: categories/market_block_trade.py<br/>(生产态 / production)"]
    schemas_categories_market_block_trade_detail_py["行情block成交详情<br/>本文件是 c1_market.block_trade_detail<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_block_trade_detail<br/>文件: categories/market_block_trade_detail.py<br/>(生产态 / production)"]
    schemas_categories_market_cb_iv_py["行情cb隐含波动率<br/>本文件是 c1_market.convertible_bond_iv<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_cb_iv<br/>文件: categories/market_cb_iv.py<br/>(生产态 / production)"]
    schemas_categories_market_concept_board_py["行情conceptboard<br/>实现业务功能（market concept board）<br/>market_concept_board<br/>文件: categories/market_concept_board.py<br/>(生产态 / production)"]
    schemas_categories_market_concept_board_constituent_py["行情conceptboardconstituent<br/>实现业务功能（market concept board constituent）<br/>market_concept_board_constituent<br/>文件: categories<br/>/market_concept_board_constituent.py<br/>(生产态 / production)"]
    schemas_categories_market_concept_sector_py["行情conceptsector<br/>实现业务功能（market concept sector）<br/>market_concept_sector<br/>文件: categories/market_concept_sector.py<br/>(生产态 / production)"]
    schemas_categories_market_convertible_bond_list_py["行情convertiblebondlist<br/>实现业务功能（market convertible bond list）<br/>market_convertible_bond_list<br/>文件: categories/market_convertible_bond_list.py<br/>(生产态 / production)"]
    schemas_categories_market_daily_valuation_py["行情dailyvaluation<br/>本文件是 c1_market.daily_valuation<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_daily_valuation<br/>文件: categories/market_daily_valuation.py<br/>(生产态 / production)"]
    schemas_categories_market_dragon_tiger_py["行情dragontiger<br/>本文件是 c1_market.dragon_tiger<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_dragon_tiger<br/>文件: categories/market_dragon_tiger.py<br/>(生产态 / production)"]
    schemas_categories_market_dragon_tiger_seat_py["行情dragontigerseat<br/>龙虎榜席位明细：存储个股龙虎榜 Top5 买入<br/>/卖出营业部席位买卖额明细。<br/>market_dragon_tiger_seat<br/>文件: categories/market_dragon_tiger_seat.py<br/>(生产态 / production)"]
    schemas_categories_market_etf_benchmark_py["行情etf基准<br/>categories相关功能（market etf benchmark）<br/>market_etf_benchmark<br/>文件: categories/market_etf_benchmark.py<br/>(生产态 / production)"]
    schemas_categories_market_etf_list_py["行情etf列表<br/>categories相关功能（market etf list）<br/>market_etf_list<br/>文件: categories/market_etf_list.py<br/>(生产态 / production)"]
    schemas_categories_market_etf_nav_py["行情etfnav<br/>本文件是 c1_market.etf_nav 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_etf_nav<br/>文件: categories/market_etf_nav.py<br/>(生产态 / production)"]
    schemas_categories_market_futures_kline_qmt_py["行情futuresklineqmt<br/>本文件是 c1_market.futures_kline_qmt<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_futures_kline_qmt<br/>文件: categories/market_futures_kline_qmt.py<br/>(生产态 / production)"]
    schemas_categories_market_futures_position_py["行情futures持仓<br/>本文件是 c1_market.futures_position<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_futures_position<br/>文件: categories/market_futures_position.py<br/>(生产态 / production)"]
    schemas_categories_market_futures_term_py["行情futures期限<br/>本文件是 c1_market.futures_term_structure<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_futures_term<br/>文件: categories/market_futures_term.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_connect_flow_py["行情hkconnect流程<br/>本文件是 c1_market.hk_connect_flow<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_hk_connect_flow<br/>文件: categories/market_hk_connect_flow.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_kline_py["行情hkkline<br/>本文件是 c1_market.hk_kline 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_hk_kline<br/>文件: categories/market_hk_kline.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_stock_list_py["行情hk股票列表<br/>categories相关功能（market hk stock list）<br/>market_hk_stock_list<br/>文件: categories/market_hk_stock_list.py<br/>(生产态 / production)"]
    schemas_categories_market_hk_trade_calendar_py["行情hk成交日历<br/>categories相关功能（market hk trade calendar）<br/>market_hk_trade_calendar<br/>文件: categories/market_hk_trade_calendar.py<br/>(生产态 / production)"]
    schemas_categories_market_hog_futures_core_py["市场生猪Futures核心<br/>hog_futures_core 表 DDL-as-Code（category_id:<br/>market_hog_futures_core, calc_m...<br/>Market Hog Futures Core<br/>文件: categories/market_hog_futures_core.py<br/>(生产态 / production)"]
    schemas_categories_market_hog_province_spot_py["市场生猪Province现货<br/>hog_province_spot 表 DDL-as-Code（category_id:<br/>market_hog_province_spot, calc...<br/>Market Hog Province Spot<br/>文件: categories/market_hog_province_spot.py<br/>(生产态 / production)"]
    schemas_categories_market_hog_spot_index_py["市场生猪现货索引<br/>hog_spot_index 表 DDL-as-Code（category_id:<br/>market_hog_spot_index, calc_mode:...<br/>Market Hog Spot Index<br/>文件: categories/market_hog_spot_index.py<br/>(生产态 / production)"]
    schemas_categories_market_index_py["行情索引<br/>本文件是 c1_market.index_quote<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_index<br/>文件: categories/market_index.py<br/>(生产态 / production)"]
    schemas_categories_market_index_constituent_py["行情索引constituent<br/>categories相关功能（market index constituent）<br/>market_index_constituent<br/>文件: categories/market_index_constituent.py<br/>(生产态 / production)"]
    schemas_categories_market_index_list_py["行情索引列表<br/>categories相关功能（market index list）<br/>market_index_list<br/>文件: categories/market_index_list.py<br/>(生产态 / production)"]
    schemas_categories_market_index_meta_py["行情索引元<br/>本文件是 c1_market.market_index_meta<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>文件: categories/market_index_meta.py<br/>(生产态 / production)"]
    schemas_categories_market_index_weight_py["行情索引weight<br/>本文件是 c1_market.index_weight<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_index_weight<br/>文件: categories/market_index_weight.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_15min_py["行情kline15min<br/>本文件是 c1_market.kline_15min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_15min<br/>文件: categories/market_kline_15min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_1min_py["行情kline1min<br/>本文件是 c1_market.kline_1min 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_kline_1min<br/>文件: categories/market_kline_1min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_30min_py["行情kline30min<br/>本文件是 c1_market.kline_30min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_30min<br/>文件: categories/market_kline_30min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_5min_py["行情kline5min<br/>本文件是 c1_market.kline_5min 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_kline_5min<br/>文件: categories/market_kline_5min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_60min_py["行情kline60min<br/>本文件是 c1_market.kline_60min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_60min<br/>文件: categories/market_kline_60min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_cb_py["行情klinecb<br/>本文件是 c1_market.kline_cb 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_kline_cb<br/>文件: categories/market_kline_cb.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_daily_py["行情klinedaily<br/>本文件是 c1_market.kline_daily<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_daily<br/>文件: categories/market_kline_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_daily_hfq_py["行情klinedailyhfq<br/>本文件是 c1_market.kline_daily_hfq<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_daily_hfq<br/>文件: categories/market_kline_daily_hfq.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_15min_py["行情klineetf15min<br/>本文件是 c1_market.kline_etf_15min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_15min<br/>文件: categories/market_kline_etf_15min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_1min_py["行情klineetf1min<br/>本文件是 c1_market.kline_etf_1min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_1min<br/>文件: categories/market_kline_etf_1min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_30min_py["行情klineetf30min<br/>本文件是 c1_market.kline_etf_30min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_30min<br/>文件: categories/market_kline_etf_30min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_5min_py["行情klineetf5min<br/>本文件是 c1_market.kline_etf_5min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_5min<br/>文件: categories/market_kline_etf_5min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_60min_py["行情klineetf60min<br/>本文件是 c1_market.kline_etf_60min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_etf_60min<br/>文件: categories/market_kline_etf_60min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_etf_daily_py["市场K线EtfDaily<br/>kline_etf_daily 表 DDL-as-Code（category_id:<br/>market_kline_etf_daily, calc_mod...<br/>Market Kline Etf Daily<br/>文件: categories/market_kline_etf_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_futures_py["行情klinefutures<br/>本文件是 c1_market.kline_futures<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_futures<br/>文件: categories/market_kline_futures.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_hk_daily_py["行情klinehkdaily<br/>本文件是 c1_market.kline_hk_daily<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_hk_daily<br/>文件: categories/market_kline_hk_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_index_py["行情kline索引<br/>本文件是 c1_market.kline_index<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_index<br/>文件: categories/market_kline_index.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_15min_py["行情klinelof15min<br/>本文件是 c1_market.kline_lof_15min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_15min<br/>文件: categories/market_kline_lof_15min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_1min_py["行情klinelof1min<br/>本文件是 c1_market.kline_lof_1min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_1min<br/>文件: categories/market_kline_lof_1min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_30min_py["行情klinelof30min<br/>本文件是 c1_market.kline_lof_30min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_30min<br/>文件: categories/market_kline_lof_30min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_5min_py["行情klinelof5min<br/>本文件是 c1_market.kline_lof_5min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_5min<br/>文件: categories/market_kline_lof_5min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_lof_60min_py["行情klinelof60min<br/>本文件是 c1_market.kline_lof_60min<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_lof_60min<br/>文件: categories/market_kline_lof_60min.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_monthly_py["行情klinemonthly<br/>本文件是 c1_market.kline_monthly<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_monthly<br/>文件: categories/market_kline_monthly.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_monthly_hfq_py["行情klinemonthlyhfq<br/>本文件是 c1_market.kline_monthly_hfq<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_monthly_hfq<br/>文件: categories/market_kline_monthly_hfq.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_sector_py["行情klinesector<br/>本文件是 c1_market.kline_sector<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_sector<br/>文件: categories/market_kline_sector.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_sector_880_py["行情klinesector880<br/>本文件是 c1_market.kline_sector_880<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_sector_880<br/>文件: categories/market_kline_sector_880.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_sector_intraday_py["行情klinesectorintraday<br/>本文件是 c1_market.kline_sector_intraday<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_sector_intraday<br/>文件: categories/market_kline_sector_intraday.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_us_daily_py["行情klineusdaily<br/>本文件是 c1_market.kline_us_daily<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_us_daily<br/>文件: categories/market_kline_us_daily.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_weekly_py["行情klineweekly<br/>本文件是 c1_market.kline_weekly<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_weekly<br/>文件: categories/market_kline_weekly.py<br/>(生产态 / production)"]
    schemas_categories_market_kline_weekly_hfq_py["行情klineweeklyhfq<br/>本文件是 c1_market.kline_weekly_hfq<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_kline_weekly_hfq<br/>文件: categories/market_kline_weekly_hfq.py<br/>(生产态 / production)"]
    schemas_categories_market_l2_tick_py["行情l2逐笔<br/>本文件是 c1_market.l2_tick 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_l2_tick<br/>文件: categories/market_l2_tick.py<br/>(生产态 / production)"]
    schemas_categories_market_limit_up_down_py["行情限制上下<br/>本文件是 c1_market.limit_up_down<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_limit_up_down<br/>文件: categories/market_limit_up_down.py<br/>(生产态 / production)"]
    schemas_categories_market_lof_list_py["行情lof列表<br/>categories相关功能（market lof list）<br/>market_lof_list<br/>文件: categories/market_lof_list.py<br/>(生产态 / production)"]
    schemas_categories_market_margin_trading_py["行情保证金交易<br/>本文件是 c1_market.margin_trading<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_margin_trading<br/>文件: categories/market_margin_trading.py<br/>(生产态 / production)"]
    schemas_categories_market_money_flow_py["行情money流程<br/>本文件是 c1_market.money_flow 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_money_flow<br/>文件: categories/market_money_flow.py<br/>(生产态 / production)"]
    schemas_categories_market_option_greeks_py["行情选项greeks<br/>本文件是 c1_market.option_greeks<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_option_greeks<br/>文件: categories/market_option_greeks.py<br/>(生产态 / production)"]
    schemas_categories_market_option_iv_py["行情选项隐含波动率<br/>本文件是 c1_market.option_iv_surface<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_option_iv<br/>文件: categories/market_option_iv.py<br/>(生产态 / production)"]
    schemas_categories_market_option_kline_py["行情选项kline<br/>本文件是 c1_market.option_kline<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_option_kline<br/>文件: categories/market_option_kline.py<br/>(生产态 / production)"]
    schemas_categories_market_realtime_snapshot_py["行情实时快照<br/>本文件是 c1_market.realtime_snapshot<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_realtime_snapshot<br/>文件: categories/market_realtime_snapshot.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_constituent_py["行情sectorconstituent<br/>实现业务功能（market sector constituent）<br/>market_sector_constituent<br/>文件: categories/market_sector_constituent.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_list_py["行情板块列表<br/>本文件是 c1_market.sector_list<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_sector_list<br/>文件: categories/market_sector_list.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_meta_py["行情板块元<br/>本文件是 c1_market.sector_meta<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_sector_meta<br/>文件: categories/market_sector_meta.py<br/>(生产态 / production)"]
    schemas_categories_market_sector_snapshot_py["行情板块快照<br/>本文件是 c1_market.sector_snapshot<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_sector_snapshot<br/>文件: categories/market_sector_snapshot.py<br/>(生产态 / production)"]
    schemas_categories_market_st_stock_list_py["行情st股票列表<br/>categories相关功能（market st stock list）<br/>market_st_stock_list<br/>文件: categories/market_st_stock_list.py<br/>(生产态 / production)"]
    schemas_categories_market_stock_indicator_py["行情股票指标<br/>本文件是 c1_market.stock_indicator<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>market_stock_indicator<br/>文件: categories/market_stock_indicator.py<br/>(生产态 / production)"]
    schemas_categories_market_stock_list_py["行情股票列表<br/>本文件是 c1_market.stock_list 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_stock_list<br/>文件: categories/market_stock_list.py<br/>(生产态 / production)"]
    schemas_categories_market_tick_py["行情逐笔<br/>本文件是 c1_market.tick_data 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_tick<br/>文件: categories/market_tick.py<br/>(生产态 / production)"]
    schemas_categories_market_trade_calendar_py["行情成交日历<br/>categories相关功能（market trade calendar）<br/>market_trade_calendar<br/>文件: categories/market_trade_calendar.py<br/>(生产态 / production)"]
    schemas_categories_market_us_index_py["行情us索引<br/>本文件是 c1_market.us_index 表结构的唯一真源<br/>（DDL-as-Code 模式）。<br/>market_us_index<br/>文件: categories/market_us_index.py<br/>(生产态 / production)"]
    scripts_ch_data_inventory_py["全库数据盘点：逐表审计行数/日期范围/空表<br/>/缺失日期/引擎/大小。<br/>输出完整数据资产清单，用于'收口'——确认数据完整性<br/>+ 识别缺口。<br/>_data_inventory<br/>文件: ch/_data_inventory.py<br/>(生产态 / production)"]
    scripts_ch_recovery_drill_py["恢复演练：轮询备份完成 → 恢复小表到临时库 →<br/>行数校验 → 清理。<br/>非破坏性：不碰 live 表，恢复到 _restore_drill<br/>临时库。<br/>_recovery_drill<br/>文件: ch/_recovery_drill.py<br/>(生产态 / production)"]
    scripts_ch_apply_fundamental_tables_ddl_py["应用fundamentaltablesddl<br/>ClickHouse c3_fundamental 财务三表 DDL 部署 +<br/>精度验证脚本（audit 1.2 治本）。<br/>apply_fundamental_tables_ddl<br/>文件: ch/apply_fundamental_tables_ddl.py<br/>(生产态 / production)"]
    scripts_ch_apply_market_tables_ddl_py["apply行情tablesddl<br/>ClickHouse c1_market 建表 DDL 部署 +<br/>引擎验证脚本（Phase F）。<br/>apply_market_tables_ddl<br/>文件: ch/apply_market_tables_ddl.py<br/>(生产态 / production)"]
    scripts_ch_apply_rbac_py["应用rbac<br/>ClickHouse RBAC 账号分级部署 + 验证脚本（audit<br/>9.4 治本 #ARCH-CH-027）。<br/>apply_rbac<br/>文件: ch/apply_rbac.py<br/>(生产态 / production)"]
    scripts_ch_lint_symbol_convention_py["Symbol 约定 lint 门禁（TRAE-082 GATE-SYMBOL-C<br/>静态 lint 校验（无 DB 连接，快速 pre-commit<br/>适用）：<br/>lint_symbol_convention<br/>文件: ch/lint_symbol_convention.py<br/>(生产态 / production)"]
    scripts_ch_verify_exchange_coverage_py["verify交易所coverage<br/>exchange+symbol_canonical 数据覆盖率校验器<br/>（TRAE-082 1.1.0 阶段2 配套）。<br/>verify_exchange_coverage<br/>文件: ch/verify_exchange_coverage.py<br/>(生产态 / production)"]
    scripts_ch_verify_schema_truth_py["verify结构truth<br/>DDL-as-Code 真源 vs ClickHouse 实际表结构<br/>漂移校验器（治本工具）。<br/>verify_schema_truth<br/>文件: ch/verify_schema_truth.py<br/>(生产态 / production)"]
    scripts_ops_ch_health_probe_py["7×24 CH 健康探针守护进程<br/>（R4b，#ARCH-DR-CH-RESTART-001）<br/>Ch Health Probe<br/>文件: ops/ch_health_probe.py<br/>(生产态 / production)"]
    scripts_ops_verify_alert_channels_py["告警通道端到端验证<br/>（B2，#ARCH-CH-023，2026-07-25）。<br/>告警通道端到端验证，#，2026-07-25）。<br/>verify_alert_channels<br/>文件: ops/verify_alert_channels.py<br/>(生产态 / production)"]
    scripts_register_aux_tasks_ps1["注册aux任务<br/>register_aux_tasks.ps1的注册表，登记和查询已注册<br/>的条目<br/>文件: scripts/register_aux_tasks.ps1<br/>(生产态 / production)"]
    scripts_register_guard_tasks_ps1["注册守卫任务<br/>守卫的注册表，登记和查询已注册的条目<br/>register_guard_tasks<br/>文件: scripts/register_guard_tasks.ps1<br/>(生产态 / production)"]
    scripts_start_ch_health_probe_ps1["启动ChHealthProbe<br/>脚本包的start_ch_health_probe模块<br/>Start Ch Health Probe<br/>文件: scripts/start_ch_health_probe.ps1<br/>(生产态 / production)"]
    scripts_start_scheduler_ps1["启动调度器<br/>调度器的调度器，按时间或优先级安排任务执行<br/>start_scheduler<br/>文件: scripts/start_scheduler.ps1<br/>(生产态 / production)"]
    scripts_start_tick_subscriber_ps1["启动逐笔订阅器<br/>start_tick_subscriber.ps1的订阅器，订阅接收数据<br/>文件: scripts/start_tick_subscriber.ps1<br/>(生产态 / production)"]
    src_zephyr_data_main_py["主入口<br/>data — 数据源集成器 CLI 入口<br/>__main__<br/>文件: data/__main__.py<br/>(生产态 / production)"]
    src_zephyr_data_config_policies_yaml["策略<br/>数据采集策略配置（派生物），由<br/>generate_policies.py 从<br/>data_sources_registry.yaml<br/>派生，禁止手工修改，mtime 变化时热更新。<br/>文件: config/policies.yaml<br/>(生产态 / production)"]
    src_zephyr_data_config_schedule_yaml["调度计划<br/>机器学习的调度器，按时间或优先级安排任务执行<br/>schedule<br/>文件: config/schedule.yaml<br/>(生产态 / production)"]
    src_zephyr_data_config_tasks_yaml["任务<br/>数据采集任务清单配置，定义首批 10<br/>个任务的调度计划、DAG 依赖与数据源映射，覆盖<br/>iFind/QMT/AKShare 三个 Provider。<br/>tasks<br/>文件: config/tasks.yaml<br/>(生产态 / production)"]
    src_zephyr_data_implementations_init_py["data/implementations 包入口<br/>每个 Provider 封装一个数据源 SDK，继承<br/>IngestProviderBase。<br/>文件: implementations/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_kline_resampler_py["880xxx 板块K线合成器——从 1m/5m 合成 15m/30m/60m<br/>写<br/>入 ClickHouse<br/>kline_resampler<br/>文件: data/kline_resampler.py<br/>(生产态 / production)"]
    src_zephyr_data_redundant_source_init_py["数据源冗余与热切换模块（MOD-L00-005）。<br/>P2-8：主备数据源热切换 + CH 冗余降级。<br/>文件: redundant_source/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_satellite_geospatial_engine_init_py["data/satellite_geospatial_engine 包入口<br/>域量化架构 · D_DATA 数据接入层<br/>D_DATA Data Source<br/>文件: satellite_geospatial_engine/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_sector_kline_downloader_py["板块klinedownloader<br/>880xxx 板块指数K线下载器——盘后从 tqcenter<br/>下载日K/分钟K写入 ClickHouse。<br/>sector_kline_downloader<br/>文件: data/sector_kline_downloader.py<br/>(生产态 / production)"]
    src_zephyr_data_sector_snapshot_collector_py["板块快照收集器<br/>880xxx 板块实时快照采集器（tqcenter →<br/>ClickHouse sector_snapshot 表）。<br/>sector_snapshot_collector<br/>文件: data/sector_snapshot_collector.py<br/>(生产态 / production)"]
    src_zephyr_data_symbol_normalizer_init_py["data/symbol_normalizer 包入口<br/>Symbol 标准化模块——TRAE-082 symbol<br/>约定铁律的实现真源。<br/>文件: symbol_normalizer/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_wal_codec_init_py["WAL 段编解码模块（MOD-L00-006）。<br/>WAL 段编解码模块包入口，TSV 格式向后兼容，用<br/>magic number 区分格式。<br/>文件: wal_codec/__init__.py<br/>(生产态 / production)"]
    tests_data_test_market_quality_validator_py["#ARCH-CH-021 P0-4:<br/>写入路径异常值校验器四门禁测试。<br/># P0-4: 写入路径异常值校验器四门禁测试。<br/>test_market_quality_validator<br/>文件: data/test_market_quality_validator.py<br/>(生产态 / production)"]
    tests_data_test_pit_query_py["#ARCH-CH-021 P0-5: 财报 PIT 查询能力测试。<br/># P0-5: 财报 PIT 查询能力测试。<br/>test_pit_query<br/>文件: data/test_pit_query.py<br/>(生产态 / production)"]
    tests_data_test_source_health_check_py["数据源健康检查测试<br/>test_source_health_check.py —<br/>数据源健康检查模块单测。<br/>Test Source Health Check<br/>文件: data/test_source_health_check.py<br/>(生产态 / production)"]
    tests_zephyr_data_test_cross_source_validator_py["测试跨源校验器<br/>cross_source_validator 单元测试（P1-4<br/>多源交叉校验）。<br/>test_cross_source_validator<br/>文件: data/test_cross_source_validator.py<br/>(生产态 / production)"]
    tests_zephyr_data_test_tick_subscriber_py["测试逐笔订阅器<br/>tick_subscriber 单元测试（含 Phase C: WalWriter<br/>+ 批量出队 + 无锁计数）。<br/>test_tick_subscriber<br/>文件: data/test_tick_subscriber.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_balance_sheet_py ~~~ schemas_categories_fundamental_cashflow_statement_py
    schemas_categories_fundamental_cashflow_statement_py ~~~ schemas_categories_fundamental_disclosure_plan_py
    schemas_categories_fundamental_disclosure_plan_py ~~~ schemas_categories_fundamental_equity_pledge_detail_py
    schemas_categories_fundamental_equity_pledge_detail_py ~~~ schemas_categories_fundamental_income_statement_py
    schemas_categories_fundamental_income_statement_py ~~~ schemas_categories_fundamental_industry_class_py
    schemas_categories_fundamental_industry_class_py ~~~ schemas_categories_fundamental_industry_class_suppl_py
    schemas_categories_fundamental_industry_class_suppl_py ~~~ schemas_categories_fundamental_restricted_shares_py
    schemas_categories_fundamental_restricted_shares_py ~~~ schemas_categories_fundamental_rights_issue_py
    schemas_categories_fundamental_rights_issue_py ~~~ schemas_categories_fundamental_share_change_py
    schemas_categories_fundamental_share_change_py ~~~ schemas_categories_fundamental_share_unlock_py
    schemas_categories_fundamental_share_unlock_py ~~~ schemas_categories_macro_edb_data_py
    schemas_categories_macro_edb_data_py ~~~ schemas_categories_macro_macro_data_py
    schemas_categories_macro_macro_data_py ~~~ schemas_categories_market_adj_factor_py
    schemas_categories_market_adj_factor_py ~~~ schemas_categories_market_auction_py
    schemas_categories_market_auction_py ~~~ schemas_categories_market_auction_book_py
    schemas_categories_market_auction_book_py ~~~ schemas_categories_market_block_trade_py
    schemas_categories_market_block_trade_py ~~~ schemas_categories_market_block_trade_detail_py
    schemas_categories_market_block_trade_detail_py ~~~ schemas_categories_market_cb_iv_py
    schemas_categories_market_cb_iv_py ~~~ schemas_categories_market_concept_board_py
    schemas_categories_market_concept_board_py ~~~ schemas_categories_market_concept_board_constituent_py
    schemas_categories_market_concept_board_constituent_py ~~~ schemas_categories_market_concept_sector_py
    schemas_categories_market_concept_sector_py ~~~ schemas_categories_market_convertible_bond_list_py
    schemas_categories_market_convertible_bond_list_py ~~~ schemas_categories_market_daily_valuation_py
    schemas_categories_market_daily_valuation_py ~~~ schemas_categories_market_dragon_tiger_py
    schemas_categories_market_dragon_tiger_py ~~~ schemas_categories_market_dragon_tiger_seat_py
    schemas_categories_market_dragon_tiger_seat_py ~~~ schemas_categories_market_etf_benchmark_py
    schemas_categories_market_etf_benchmark_py ~~~ schemas_categories_market_etf_list_py
    schemas_categories_market_etf_list_py ~~~ schemas_categories_market_etf_nav_py
    schemas_categories_market_etf_nav_py ~~~ schemas_categories_market_futures_kline_qmt_py
    schemas_categories_market_futures_kline_qmt_py ~~~ schemas_categories_market_futures_position_py
    schemas_categories_market_futures_position_py ~~~ schemas_categories_market_futures_term_py
    schemas_categories_market_futures_term_py ~~~ schemas_categories_market_hk_connect_flow_py
    schemas_categories_market_hk_connect_flow_py ~~~ schemas_categories_market_hk_kline_py
    schemas_categories_market_hk_kline_py ~~~ schemas_categories_market_hk_stock_list_py
    schemas_categories_market_hk_stock_list_py ~~~ schemas_categories_market_hk_trade_calendar_py
    schemas_categories_market_hk_trade_calendar_py ~~~ schemas_categories_market_hog_futures_core_py
    schemas_categories_market_hog_futures_core_py ~~~ schemas_categories_market_hog_province_spot_py
    schemas_categories_market_hog_province_spot_py ~~~ schemas_categories_market_hog_spot_index_py
    schemas_categories_market_hog_spot_index_py ~~~ schemas_categories_market_index_py
    schemas_categories_market_index_py ~~~ schemas_categories_market_index_constituent_py
    schemas_categories_market_index_constituent_py ~~~ schemas_categories_market_index_list_py
    schemas_categories_market_index_list_py ~~~ schemas_categories_market_index_meta_py
    schemas_categories_market_index_meta_py ~~~ schemas_categories_market_index_weight_py
    schemas_categories_market_index_weight_py ~~~ schemas_categories_market_kline_15min_py
    schemas_categories_market_kline_15min_py ~~~ schemas_categories_market_kline_1min_py
    schemas_categories_market_kline_1min_py ~~~ schemas_categories_market_kline_30min_py
    schemas_categories_market_kline_30min_py ~~~ schemas_categories_market_kline_5min_py
    schemas_categories_market_kline_5min_py ~~~ schemas_categories_market_kline_60min_py
    schemas_categories_market_kline_60min_py ~~~ schemas_categories_market_kline_cb_py
    schemas_categories_market_kline_cb_py ~~~ schemas_categories_market_kline_daily_py
    schemas_categories_market_kline_daily_py ~~~ schemas_categories_market_kline_daily_hfq_py
    schemas_categories_market_kline_daily_hfq_py ~~~ schemas_categories_market_kline_etf_15min_py
    schemas_categories_market_kline_etf_15min_py ~~~ schemas_categories_market_kline_etf_1min_py
    schemas_categories_market_kline_etf_1min_py ~~~ schemas_categories_market_kline_etf_30min_py
    schemas_categories_market_kline_etf_30min_py ~~~ schemas_categories_market_kline_etf_5min_py
    schemas_categories_market_kline_etf_5min_py ~~~ schemas_categories_market_kline_etf_60min_py
    schemas_categories_market_kline_etf_60min_py ~~~ schemas_categories_market_kline_etf_daily_py
    schemas_categories_market_kline_etf_daily_py ~~~ schemas_categories_market_kline_futures_py
    schemas_categories_market_kline_futures_py ~~~ schemas_categories_market_kline_hk_daily_py
    schemas_categories_market_kline_hk_daily_py ~~~ schemas_categories_market_kline_index_py
    schemas_categories_market_kline_index_py ~~~ schemas_categories_market_kline_lof_15min_py
    schemas_categories_market_kline_lof_15min_py ~~~ schemas_categories_market_kline_lof_1min_py
    schemas_categories_market_kline_lof_1min_py ~~~ schemas_categories_market_kline_lof_30min_py
    schemas_categories_market_kline_lof_30min_py ~~~ schemas_categories_market_kline_lof_5min_py
    schemas_categories_market_kline_lof_5min_py ~~~ schemas_categories_market_kline_lof_60min_py
    schemas_categories_market_kline_lof_60min_py ~~~ schemas_categories_market_kline_monthly_py
    schemas_categories_market_kline_monthly_py ~~~ schemas_categories_market_kline_monthly_hfq_py
    schemas_categories_market_kline_monthly_hfq_py ~~~ schemas_categories_market_kline_sector_py
    schemas_categories_market_kline_sector_py ~~~ schemas_categories_market_kline_sector_880_py
    schemas_categories_market_kline_sector_880_py ~~~ schemas_categories_market_kline_sector_intraday_py
    schemas_categories_market_kline_sector_intraday_py ~~~ schemas_categories_market_kline_us_daily_py
    schemas_categories_market_kline_us_daily_py ~~~ schemas_categories_market_kline_weekly_py
    schemas_categories_market_kline_weekly_py ~~~ schemas_categories_market_kline_weekly_hfq_py
    schemas_categories_market_kline_weekly_hfq_py ~~~ schemas_categories_market_l2_tick_py
    schemas_categories_market_l2_tick_py ~~~ schemas_categories_market_limit_up_down_py
    schemas_categories_market_limit_up_down_py ~~~ schemas_categories_market_lof_list_py
    schemas_categories_market_lof_list_py ~~~ schemas_categories_market_margin_trading_py
    schemas_categories_market_margin_trading_py ~~~ schemas_categories_market_money_flow_py
    schemas_categories_market_money_flow_py ~~~ schemas_categories_market_option_greeks_py
    schemas_categories_market_option_greeks_py ~~~ schemas_categories_market_option_iv_py
    schemas_categories_market_option_iv_py ~~~ schemas_categories_market_option_kline_py
    schemas_categories_market_option_kline_py ~~~ schemas_categories_market_realtime_snapshot_py
    schemas_categories_market_realtime_snapshot_py ~~~ schemas_categories_market_sector_constituent_py
    schemas_categories_market_sector_constituent_py ~~~ schemas_categories_market_sector_list_py
    schemas_categories_market_sector_list_py ~~~ schemas_categories_market_sector_meta_py
    schemas_categories_market_sector_meta_py ~~~ schemas_categories_market_sector_snapshot_py
    schemas_categories_market_sector_snapshot_py ~~~ schemas_categories_market_st_stock_list_py
    schemas_categories_market_st_stock_list_py ~~~ schemas_categories_market_stock_indicator_py
    schemas_categories_market_stock_indicator_py ~~~ schemas_categories_market_stock_list_py
    schemas_categories_market_stock_list_py ~~~ schemas_categories_market_tick_py
    schemas_categories_market_tick_py ~~~ schemas_categories_market_trade_calendar_py
    schemas_categories_market_trade_calendar_py ~~~ schemas_categories_market_us_index_py
    schemas_categories_market_us_index_py ~~~ scripts_ch_data_inventory_py
    scripts_ch_data_inventory_py ~~~ scripts_ch_recovery_drill_py
    scripts_ch_recovery_drill_py ~~~ scripts_ch_apply_fundamental_tables_ddl_py
    scripts_ch_apply_fundamental_tables_ddl_py ~~~ scripts_ch_apply_market_tables_ddl_py
    scripts_ch_apply_market_tables_ddl_py ~~~ scripts_ch_apply_rbac_py
    scripts_ch_apply_rbac_py ~~~ scripts_ch_lint_symbol_convention_py
    scripts_ch_lint_symbol_convention_py ~~~ scripts_ch_verify_exchange_coverage_py
    scripts_ch_verify_exchange_coverage_py ~~~ scripts_ch_verify_schema_truth_py
    scripts_ch_verify_schema_truth_py ~~~ scripts_ops_ch_health_probe_py
    scripts_ops_ch_health_probe_py ~~~ scripts_ops_verify_alert_channels_py
    scripts_ops_verify_alert_channels_py ~~~ scripts_register_aux_tasks_ps1
    scripts_register_aux_tasks_ps1 ~~~ scripts_register_guard_tasks_ps1
    scripts_register_guard_tasks_ps1 ~~~ scripts_start_ch_health_probe_ps1
    scripts_start_ch_health_probe_ps1 ~~~ scripts_start_scheduler_ps1
    scripts_start_scheduler_ps1 ~~~ scripts_start_tick_subscriber_ps1
    scripts_start_tick_subscriber_ps1 ~~~ src_zephyr_data_main_py
    src_zephyr_data_main_py ~~~ src_zephyr_data_config_policies_yaml
    src_zephyr_data_config_policies_yaml ~~~ src_zephyr_data_config_schedule_yaml
    src_zephyr_data_config_schedule_yaml ~~~ src_zephyr_data_config_tasks_yaml
    src_zephyr_data_config_tasks_yaml ~~~ src_zephyr_data_implementations_init_py
    src_zephyr_data_implementations_init_py ~~~ src_zephyr_data_kline_resampler_py
    src_zephyr_data_kline_resampler_py ~~~ src_zephyr_data_redundant_source_init_py
    src_zephyr_data_redundant_source_init_py ~~~ src_zephyr_data_satellite_geospatial_engine_init_py
    src_zephyr_data_satellite_geospatial_engine_init_py ~~~ src_zephyr_data_sector_kline_downloader_py
    src_zephyr_data_sector_kline_downloader_py ~~~ src_zephyr_data_sector_snapshot_collector_py
    src_zephyr_data_sector_snapshot_collector_py ~~~ src_zephyr_data_symbol_normalizer_init_py
    src_zephyr_data_symbol_normalizer_init_py ~~~ src_zephyr_data_wal_codec_init_py
    src_zephyr_data_wal_codec_init_py ~~~ tests_data_test_market_quality_validator_py
    tests_data_test_market_quality_validator_py ~~~ tests_data_test_pit_query_py
    tests_data_test_pit_query_py ~~~ tests_data_test_source_health_check_py
    tests_data_test_source_health_check_py ~~~ tests_zephyr_data_test_cross_source_validator_py
    tests_zephyr_data_test_cross_source_validator_py ~~~ tests_zephyr_data_test_tick_subscriber_py
    schemas_categories_cross_validation_log_py["跨验证日志<br/>存储 QMT 主源 vs TDX 备源的 tick<br/>数据交叉校验结果，<br/>cross_validation_log<br/>文件: categories/cross_validation_log.py<br/>(生产态 / production)"]
    scripts_ch_apply_exchange_columns_py["apply交易所columns<br/>处理数据读写与转换（apply exchange columns）<br/>apply_exchange_columns<br/>文件: ch/apply_exchange_columns.py<br/>(生产态 / production)"]
    scripts_ch_apply_timezone_migration_py["应用timezone迁移<br/>ClickHouse 时区防线迁移脚本（audit A组 Schema<br/>治理 - 时区防线，#ARCH-CH-022）。<br/>apply_timezone_migration<br/>文件: ch/apply_timezone_migration.py<br/>(生产态 / production)"]
    src_zephyr_data_alerter_py["告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8<br/>可观测性）<br/>告警触发条件（蓝图 §6.5）：<br/>alerter<br/>文件: data/alerter.py<br/>(生产态 / production)"]
    src_zephyr_data_cli_py["数据源集成器 CLI（MOD-L00-004 §8.4）。<br/>数据源集成器命令行入口，用 argparse 加<br/>subparsers 实现 8 个子命令。<br/>文件: data/cli.py<br/>(生产态 / production)"]
    src_zephyr_data_cross_source_validator_py["跨源校验器<br/>多源交叉校验器——比较 QMT 主源与 TDX 备源 tick<br/>数据一致性（P1-4）。<br/>cross_source_validator<br/>文件: data/cross_source_validator.py<br/>(生产态 / production)"]
    src_zephyr_data_pit_query_py["pit查询<br/>处理数据读写与转换（pit query）<br/>pit_query<br/>文件: data/pit_query.py<br/>(生产态 / production)"]
    src_zephyr_data_sector_ranking_engine_py["880xxx 板块动态排名引擎——5因子复合排名调整99只推<br/>送池。<br/>5因子复合排名（权重之和=1.0）：<br/>sector_ranking_engine<br/>文件: data/sector_ranking_engine.py<br/>(生产态 / production)"]
    src_zephyr_data_source_health_check_py["数据源健康检查<br/>调度器每天启动时给所有数据源做体检——挨个测连接和<br/>拉数据，记录哪个通哪个不通并写日志。查出毛病的源<br/>只记录不自动停，留给人工或备用源处理，绝不让体检<br/>本身卡住调度器启动。<br/>文件: data/source_health_check.py<br/>(生产态 / production)"]
    src_zephyr_data_tick_subscriber_py["逐笔订阅器<br/>QMT 实时 Tick 订阅服务——subscribe_quote<br/>实时推送，写入 ClickHouse tick_data。<br/>tick_subscriber<br/>文件: data/tick_subscriber.py<br/>(生产态 / production)"]
    schemas_categories_cross_validation_log_py ~~~ scripts_ch_apply_exchange_columns_py
    scripts_ch_apply_exchange_columns_py ~~~ scripts_ch_apply_timezone_migration_py
    scripts_ch_apply_timezone_migration_py ~~~ src_zephyr_data_alerter_py
    src_zephyr_data_alerter_py ~~~ src_zephyr_data_cli_py
    src_zephyr_data_cli_py ~~~ src_zephyr_data_cross_source_validator_py
    src_zephyr_data_cross_source_validator_py ~~~ src_zephyr_data_pit_query_py
    src_zephyr_data_pit_query_py ~~~ src_zephyr_data_sector_ranking_engine_py
    src_zephyr_data_sector_ranking_engine_py ~~~ src_zephyr_data_source_health_check_py
    src_zephyr_data_source_health_check_py ~~~ src_zephyr_data_tick_subscriber_py
    schemas_categories_fundamental_analyst_forecast_py["fundamentalanalyst预测<br/>本文件是 c3_fundamental.analyst_forecast<br/>表结构的唯一真源（DDL-as-Code 模式）。<br/>fundamental_analyst_forecast<br/>文件: categories/fundamental_analyst_forecast.py<br/>(生产态 / production)"]
    src_zephyr_data_ch_config_py["ch配置<br/>ClickHouse 连接配置单真源加载器（裁定<br/>#ARCH-CH-017 / #ARCH-CH-019）。<br/>ch_config<br/>文件: data/ch_config.py<br/>(生产态 / production)"]
    src_zephyr_data_ch_reader_py["ch读取器<br/>处理数据读写与转换（ch reader）<br/>ch_reader<br/>文件: data/ch_reader.py<br/>(生产态 / production)"]
    src_zephyr_data_progress_store_py["统一进度存储（MOD-L00-004 §7）。<br/>统一进度存储，SQLite<br/>单文件存储数据集成进度，支持断点续传。<br/>progress_store<br/>文件: data/progress_store.py<br/>(生产态 / production)"]
    src_zephyr_data_scheduler_py["数据源调度编排层（MOD-L00-004 §6）。<br/>APScheduler 常驻进程，按 cron<br/>时段触发任务批次，管理 DAG 依赖，<br/>文件: data/scheduler.py<br/>(生产态 / production)"]
    src_zephyr_data_speed_tester_py["数据源测速器（MOD-L00-004 §8.5）。<br/>对每个数据能力×每个可用数据源做小样本测速，记录<br/>rows/sec、symbols/sec、错误率，<br/>speed_tester<br/>文件: data/speed_tester.py<br/>(生产态 / production)"]
    src_zephyr_data_symbol_normalizer_normalizer_py["归一化器<br/>symbol 标准化核心实现——TRAE-082 symbol<br/>约定铁律。<br/>normalizer<br/>文件: symbol_normalizer/normalizer.py<br/>(生产态 / production)"]
    schemas_categories_fundamental_analyst_forecast_py ~~~ src_zephyr_data_ch_config_py
    src_zephyr_data_ch_config_py ~~~ src_zephyr_data_ch_reader_py
    src_zephyr_data_ch_reader_py ~~~ src_zephyr_data_progress_store_py
    src_zephyr_data_progress_store_py ~~~ src_zephyr_data_scheduler_py
    src_zephyr_data_scheduler_py ~~~ src_zephyr_data_speed_tester_py
    src_zephyr_data_speed_tester_py ~~~ src_zephyr_data_symbol_normalizer_normalizer_py
    src_zephyr_data_init_py["zephyr/data 包入口<br/>包入口.data — 数据源集成器（MOD-L00-004）。<br/>文件: data/__init__.py<br/>(生产态 / production)"]
    src_zephyr_data_ch_writer_py["ch写入器<br/>ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6步<br/>+ §7.3 幂等性）。<br/>ch_writer<br/>文件: data/ch_writer.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_akshare_provider_py["akshare提供器<br/>封装 AKShare 开源金融数据 SDK，继承<br/>IngestProviderBase。<br/>akshare_provider<br/>文件: implementations/akshare_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_baostock_provider_py["baostock提供器<br/>匿名访问（bs.login() 无需<br/>token，处理数据读写与转换<br/>baostock_provider<br/>文件: implementations/baostock_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_cls_provider_py["cls提供器<br/>财联社电报数据源 Provider 实现（MOD-L00-004<br/>§4.3）。<br/>cls_provider<br/>文件: implementations/cls_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_eastmoney_news_provider_py["eastmoney新闻提供器<br/>东方财富新闻数据源 Provider 实现（MOD-L00-004<br/>§4.3）。<br/>eastmoney_news_provider<br/>文件: implementations/eastmoney_news_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_miniqmt_provider_py["miniqmt提供器<br/>MOD-L00-004 数据源集成器 ·<br/>MiniQmtIngestProvider 实现。<br/>miniqmt_provider<br/>文件: implementations/miniqmt_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_rss_provider_py["rss提供器<br/>RSS 财经新闻数据源 Provider 实现（MOD-L00-004<br/>§4.3）。<br/>rss_provider<br/>文件: implementations/rss_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tdx_provider_py["tdx提供器<br/>通达信数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>tdx_provider<br/>文件: implementations/tdx_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tickflow_provider_py["tickflow提供器<br/>60 次/分钟限流（必须 _call_with_policy<br/>包裹以触发 RPM 限流）<br/>tickflow_provider<br/>文件: implementations/tickflow_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tushare_provider_py["tushare提供器<br/>token认证（环境变量TUSHARE_TOKEN）；历史数据截止<br/>2024-08；积分不足触发重试<br/>tushare_provider<br/>文件: implementations/tushare_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_policy_registry_py["策略注册表<br/>每个数据源有自己的限流/重试/反爬<br/>/登录刷新策略，集中管理、yaml 热更新。<br/>policy_registry<br/>文件: data/policy_registry.py<br/>(生产态 / production)"]
    src_zephyr_data_provider_base_py["提供器基类<br/>定义所有数据源封装的统一接口：<br/>provider_base<br/>文件: data/provider_base.py<br/>(生产态 / production)"]
    src_zephyr_data_table_registry_py["table注册表<br/>表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase<br/>2）。<br/>table_registry<br/>文件: data/table_registry.py<br/>(生产态 / production)"]
    src_zephyr_data_init_py ~~~ src_zephyr_data_ch_writer_py
    src_zephyr_data_ch_writer_py ~~~ src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_implementations_akshare_provider_py ~~~ src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_implementations_baostock_provider_py ~~~ src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_implementations_cls_provider_py ~~~ src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_implementations_eastmoney_news_provider_py ~~~ src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_implementations_miniqmt_provider_py ~~~ src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_implementations_rss_provider_py ~~~ src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_implementations_tdx_provider_py ~~~ src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_implementations_tickflow_provider_py ~~~ src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_implementations_tushare_provider_py ~~~ src_zephyr_data_policy_registry_py
    src_zephyr_data_policy_registry_py ~~~ src_zephyr_data_provider_base_py
    src_zephyr_data_provider_base_py ~~~ src_zephyr_data_table_registry_py
    src_zephyr_data_backfill_checker_py["L10 周末补下载检测器——检测过去N天缺失数据并精准<br/>补下载。<br/>backfill_checker<br/>文件: data/backfill_checker.py<br/>(生产态 / production)"]
    src_zephyr_data_buffered_writer_py["批量聚合写入器（MOD-L00-004 §18.3 裁定<br/>#ARCH-CH-003<br/>批量聚合写入器（MOD-L00-004 §18.3 裁定 #。<br/>buffered_writer<br/>文件: data/buffered_writer.py<br/>(生产态 / production)"]
    src_zephyr_data_capability_validator_py["能力校验器<br/>Provider Capability 行为契约校验器（裁定<br/>#ARCH-CH-022）。<br/>capability_validator<br/>文件: data/capability_validator.py<br/>(生产态 / production)"]
    src_zephyr_data_error_classifier_py["数据源错误分类器——根据错误字符串判断可恢复性。<br/>设计理念（数据韧性三层机制 §2）：<br/>error_classifier<br/>文件: data/error_classifier.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_eia_provider_py["implementations/eia_provider<br/>EiaProvider 实现（MOD-L00-004 §4.3<br/>数据源集成器）。<br/>文件: implementations/eia_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_qweather_provider_py["implementations/qweather_provider<br/>QWeatherProvider 实现（MOD-L00-004 §4.3<br/>数据源集成器）。<br/>文件: implementations/qweather_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_implementations_tqcenter_provider_py["TQCenter提供器<br/>封装 tqcenter SDK（通达信插件），继承<br/>IngestProviderBase。<br/>tqcenter_provider<br/>文件: implementations/tqcenter_provider.py<br/>(生产态 / production)"]
    src_zephyr_data_integrity_checker_py["数据完整性巡检器——每天盘后检测全表当日数据是否达<br/>标。<br/>设计理念（数据韧性三层机制 §3）：<br/>integrity_checker<br/>文件: data/integrity_checker.py<br/>(生产态 / production)"]
    src_zephyr_data_local_replay_py["本地replay<br/>本地落盘兜底 + 自动回灌（裁定 #ARCH-CH-013<br/>Phase 1）。<br/>local_replay<br/>文件: data/local_replay.py<br/>(生产态 / production)"]
    src_zephyr_data_metrics_py["可观测性指标采集（MOD-L00-004 §11）。<br/>不依赖 prometheus_client 库，直接按 Prometheus<br/>文本格式写入 data/metrics.prom。<br/>文件: data/metrics.py<br/>(生产态 / production)"]
    src_zephyr_data_news_dedup_py["新闻数据去重模块（MOD-L00-004 §4.3）。<br/>基于标题 MD5 哈希对新闻数据进行查重去重。<br/>news_dedup<br/>文件: data/news_dedup.py<br/>(生产态 / production)"]
    src_zephyr_data_quality_gate_py["质量门禁<br/>治本修复: 测试通过 zephyr.data.quality_gate<br/>导入 QualityReport，但真源在<br/>文件: data/quality_gate.py<br/>(生产态 / production)"]
    src_zephyr_data_task_queue_py["任务依赖图 + 优先级队列（MOD-L00-004 §6.3<br/>任务依赖图 + §<br/>6.4 并发控制）<br/>task_queue<br/>文件: data/task_queue.py<br/>(生产态 / production)"]
    src_zephyr_data_trading_calendar_py["A 股交易日历守卫（MOD-L00-004）。<br/>基于 exchange_calendars 包的 XSHG<br/>（上海证券交易所）日历，<br/>trading_calendar<br/>文件: data/trading_calendar.py<br/>(生产态 / production)"]
    src_zephyr_data_wal_writer_py["wal写入器<br/>数据先落本地 WAL 段文件，再由后台 drain<br/>线程异步排空到 ClickHouse。<br/>wal_writer<br/>文件: data/wal_writer.py<br/>(生产态 / production)"]
    src_zephyr_data_backfill_checker_py ~~~ src_zephyr_data_buffered_writer_py
    src_zephyr_data_buffered_writer_py ~~~ src_zephyr_data_capability_validator_py
    src_zephyr_data_capability_validator_py ~~~ src_zephyr_data_error_classifier_py
    src_zephyr_data_error_classifier_py ~~~ src_zephyr_data_implementations_eia_provider_py
    src_zephyr_data_implementations_eia_provider_py ~~~ src_zephyr_data_implementations_qweather_provider_py
    src_zephyr_data_implementations_qweather_provider_py ~~~ src_zephyr_data_implementations_tqcenter_provider_py
    src_zephyr_data_implementations_tqcenter_provider_py ~~~ src_zephyr_data_integrity_checker_py
    src_zephyr_data_integrity_checker_py ~~~ src_zephyr_data_local_replay_py
    src_zephyr_data_local_replay_py ~~~ src_zephyr_data_metrics_py
    src_zephyr_data_metrics_py ~~~ src_zephyr_data_news_dedup_py
    src_zephyr_data_news_dedup_py ~~~ src_zephyr_data_quality_gate_py
    src_zephyr_data_quality_gate_py ~~~ src_zephyr_data_task_queue_py
    src_zephyr_data_task_queue_py ~~~ src_zephyr_data_trading_calendar_py
    src_zephyr_data_trading_calendar_py ~~~ src_zephyr_data_wal_writer_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_tick_subscriber_py
    src_zephyr_data_buffered_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_buffered_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_progress_store_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_speed_tester_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_scheduler_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_quality_gate_py
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_capability_validator_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_backfill_checker_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_local_replay_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_kline_resampler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_provider_base_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_sector_snapshot_collector_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_sector_snapshot_collector_py -->|导入依赖 / import_depends| src_zephyr_data_sector_ranking_engine_py
    src_zephyr_data_source_health_check_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_source_health_check_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_scheduler_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_wal_writer_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_main_py -->|导入依赖 / import_depends| src_zephyr_data_cli_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_eia_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_qweather_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_satellite_geospatial_engine_init_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_symbol_normalizer_init_py -->|导入依赖 / import_depends| src_zephyr_data_symbol_normalizer_normalizer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_backfill_checker_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_buffered_writer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_capability_validator_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_integrity_checker_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_error_classifier_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_progress_store_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_metrics_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_source_health_check_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_task_queue_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_trading_calendar_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eia_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_qweather_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tqcenter_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    scripts_ch_lint_symbol_convention_py -->|config_depends / config_depends| scripts_ch_apply_timezone_migration_py
    scripts_ch_apply_timezone_migration_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| scripts_ch_apply_exchange_columns_py
    scripts_ch_apply_rbac_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_symbol_normalizer_normalizer_py
    scripts_ch_verify_schema_truth_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_data_inventory_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_recovery_drill_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ops_ch_health_probe_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ops_verify_alert_channels_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    tests_data_test_source_health_check_py -->|测试依赖 / test_depends| src_zephyr_data_source_health_check_py
    tests_data_test_pit_query_py -->|测试依赖 / test_depends| src_zephyr_data_pit_query_py
    tests_data_test_pit_query_py -->|测试依赖 / test_depends| src_zephyr_data_init_py
    tests_zephyr_data_test_cross_source_validator_py -->|测试依赖 / test_depends| src_zephyr_data_cross_source_validator_py
    tests_zephyr_data_test_tick_subscriber_py -->|测试依赖 / test_depends| src_zephyr_data_tick_subscriber_py
    schemas_categories_cross_validation_log_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_balance_sheet_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_disclosure_plan_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_cashflow_statement_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_income_statement_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_industry_class_suppl_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_restricted_shares_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_rights_issue_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_equity_pledge_detail_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_industry_class_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_macro_macro_data_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_macro_edb_data_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_share_unlock_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_share_change_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_adj_factor_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_auction_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_auction_book_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_block_trade_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_convertible_bond_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_concept_board_constituent_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_block_trade_detail_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_concept_sector_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_cb_iv_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_daily_valuation_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_concept_board_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_dragon_tiger_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_dragon_tiger_seat_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_etf_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_etf_benchmark_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_etf_nav_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_futures_kline_qmt_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_futures_position_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_connect_flow_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_futures_term_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_kline_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_trade_calendar_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hog_futures_core_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hk_stock_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hog_province_spot_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_constituent_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_weight_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_hog_spot_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_index_meta_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_15min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_30min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_5min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_1min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_15min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_cb_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_daily_hfq_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_60min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_60min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_1min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_5min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_30min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_futures_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_etf_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_hk_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_60min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_1min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_monthly_hfq_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_5min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_30min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_monthly_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_sector_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_lof_15min_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_sector_880_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_lof_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_weekly_hfq_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_sector_intraday_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_us_daily_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_l2_tick_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_limit_up_down_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_margin_trading_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_kline_weekly_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_option_kline_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_money_flow_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_constituent_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_meta_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_option_iv_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_option_greeks_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_stock_indicator_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_realtime_snapshot_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_stock_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_sector_snapshot_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_us_index_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_tick_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_trade_calendar_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_market_st_stock_list_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_cross_validation_log_py,schemas_categories_fundamental_analyst_forecast_py,schemas_categories_fundamental_balance_sheet_py,schemas_categories_fundamental_cashflow_statement_py,schemas_categories_fundamental_disclosure_plan_py,schemas_categories_fundamental_equity_pledge_detail_py,schemas_categories_fundamental_income_statement_py,schemas_categories_fundamental_industry_class_py,schemas_categories_fundamental_industry_class_suppl_py,schemas_categories_fundamental_restricted_shares_py,schemas_categories_fundamental_rights_issue_py,schemas_categories_fundamental_share_change_py,schemas_categories_fundamental_share_unlock_py,schemas_categories_macro_edb_data_py,schemas_categories_macro_macro_data_py,schemas_categories_market_adj_factor_py,schemas_categories_market_auction_py,schemas_categories_market_auction_book_py,schemas_categories_market_block_trade_py,schemas_categories_market_block_trade_detail_py,schemas_categories_market_cb_iv_py,schemas_categories_market_concept_board_py,schemas_categories_market_concept_board_constituent_py,schemas_categories_market_concept_sector_py,schemas_categories_market_convertible_bond_list_py,schemas_categories_market_daily_valuation_py,schemas_categories_market_dragon_tiger_py,schemas_categories_market_dragon_tiger_seat_py,schemas_categories_market_etf_benchmark_py,schemas_categories_market_etf_list_py,schemas_categories_market_etf_nav_py,schemas_categories_market_futures_kline_qmt_py,schemas_categories_market_futures_position_py,schemas_categories_market_futures_term_py,schemas_categories_market_hk_connect_flow_py,schemas_categories_market_hk_kline_py,schemas_categories_market_hk_stock_list_py,schemas_categories_market_hk_trade_calendar_py,schemas_categories_market_hog_futures_core_py,schemas_categories_market_hog_province_spot_py,schemas_categories_market_hog_spot_index_py,schemas_categories_market_index_py,schemas_categories_market_index_constituent_py,schemas_categories_market_index_list_py,schemas_categories_market_index_meta_py,schemas_categories_market_index_weight_py,schemas_categories_market_kline_15min_py,schemas_categories_market_kline_1min_py,schemas_categories_market_kline_30min_py,schemas_categories_market_kline_5min_py,schemas_categories_market_kline_60min_py,schemas_categories_market_kline_cb_py,schemas_categories_market_kline_daily_py,schemas_categories_market_kline_daily_hfq_py,schemas_categories_market_kline_etf_15min_py,schemas_categories_market_kline_etf_1min_py,schemas_categories_market_kline_etf_30min_py,schemas_categories_market_kline_etf_5min_py,schemas_categories_market_kline_etf_60min_py,schemas_categories_market_kline_etf_daily_py,schemas_categories_market_kline_futures_py,schemas_categories_market_kline_hk_daily_py,schemas_categories_market_kline_index_py,schemas_categories_market_kline_lof_15min_py,schemas_categories_market_kline_lof_1min_py,schemas_categories_market_kline_lof_30min_py,schemas_categories_market_kline_lof_5min_py,schemas_categories_market_kline_lof_60min_py,schemas_categories_market_kline_monthly_py,schemas_categories_market_kline_monthly_hfq_py,schemas_categories_market_kline_sector_py,schemas_categories_market_kline_sector_880_py,schemas_categories_market_kline_sector_intraday_py,schemas_categories_market_kline_us_daily_py,schemas_categories_market_kline_weekly_py,schemas_categories_market_kline_weekly_hfq_py,schemas_categories_market_l2_tick_py,schemas_categories_market_limit_up_down_py,schemas_categories_market_lof_list_py,schemas_categories_market_margin_trading_py,schemas_categories_market_money_flow_py,schemas_categories_market_option_greeks_py,schemas_categories_market_option_iv_py,schemas_categories_market_option_kline_py,schemas_categories_market_realtime_snapshot_py,schemas_categories_market_sector_constituent_py,schemas_categories_market_sector_list_py,schemas_categories_market_sector_meta_py,schemas_categories_market_sector_snapshot_py,schemas_categories_market_st_stock_list_py,schemas_categories_market_stock_indicator_py,schemas_categories_market_stock_list_py,schemas_categories_market_tick_py,schemas_categories_market_trade_calendar_py,schemas_categories_market_us_index_py,scripts_ch_data_inventory_py,scripts_ch_recovery_drill_py,scripts_ch_apply_exchange_columns_py,scripts_ch_apply_fundamental_tables_ddl_py,scripts_ch_apply_market_tables_ddl_py,scripts_ch_apply_rbac_py,scripts_ch_apply_timezone_migration_py,scripts_ch_lint_symbol_convention_py,scripts_ch_verify_exchange_coverage_py,scripts_ch_verify_schema_truth_py,scripts_ops_ch_health_probe_py,scripts_ops_verify_alert_channels_py,scripts_register_aux_tasks_ps1,scripts_register_guard_tasks_ps1,scripts_start_ch_health_probe_ps1,scripts_start_scheduler_ps1,scripts_start_tick_subscriber_ps1,src_zephyr_data_init_py,src_zephyr_data_main_py,src_zephyr_data_alerter_py,src_zephyr_data_backfill_checker_py,src_zephyr_data_buffered_writer_py,src_zephyr_data_capability_validator_py,src_zephyr_data_ch_config_py,src_zephyr_data_ch_reader_py,src_zephyr_data_ch_writer_py,src_zephyr_data_cli_py,src_zephyr_data_config_policies_yaml,src_zephyr_data_config_schedule_yaml,src_zephyr_data_config_tasks_yaml,src_zephyr_data_cross_source_validator_py,src_zephyr_data_error_classifier_py,src_zephyr_data_implementations_init_py,src_zephyr_data_implementations_akshare_provider_py,src_zephyr_data_implementations_baostock_provider_py,src_zephyr_data_implementations_cls_provider_py,src_zephyr_data_implementations_eastmoney_news_provider_py,src_zephyr_data_implementations_eia_provider_py,src_zephyr_data_implementations_miniqmt_provider_py,src_zephyr_data_implementations_qweather_provider_py,src_zephyr_data_implementations_rss_provider_py,src_zephyr_data_implementations_tdx_provider_py,src_zephyr_data_implementations_tickflow_provider_py,src_zephyr_data_implementations_tqcenter_provider_py,src_zephyr_data_implementations_tushare_provider_py,src_zephyr_data_integrity_checker_py,src_zephyr_data_kline_resampler_py,src_zephyr_data_local_replay_py,src_zephyr_data_metrics_py,src_zephyr_data_news_dedup_py,src_zephyr_data_pit_query_py,src_zephyr_data_policy_registry_py,src_zephyr_data_progress_store_py,src_zephyr_data_provider_base_py,src_zephyr_data_quality_gate_py,src_zephyr_data_redundant_source_init_py,src_zephyr_data_satellite_geospatial_engine_init_py,src_zephyr_data_scheduler_py,src_zephyr_data_sector_kline_downloader_py,src_zephyr_data_sector_ranking_engine_py,src_zephyr_data_sector_snapshot_collector_py,src_zephyr_data_source_health_check_py,src_zephyr_data_speed_tester_py,src_zephyr_data_symbol_normalizer_init_py,src_zephyr_data_symbol_normalizer_normalizer_py,src_zephyr_data_table_registry_py,src_zephyr_data_task_queue_py,src_zephyr_data_tick_subscriber_py,src_zephyr_data_trading_calendar_py,src_zephyr_data_wal_codec_init_py,src_zephyr_data_wal_writer_py,tests_data_test_market_quality_validator_py,tests_data_test_pit_query_py,tests_data_test_source_health_check_py,tests_zephyr_data_test_cross_source_validator_py,tests_zephyr_data_test_tick_subscriber_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 5 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_data_connectors["data/connectors<br/>数据连接器包，适配外部数据源连接与数据采集<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: connectors/<br/>(设计态 / design)"]
    src_zephyr_data_implementations_fred_provider_py["FRED宏观数据获取器<br/>从美联储经济数据库<br/>(FRED)和世界银行API免费获取国际宏观经济指标，包<br/>括美国GDP/CPI/失业率/国债收益率/汇率<br/>/大宗商品，以及各国GDP/人口<br/>/进出口等，补充国内数据源覆盖不到的国际对比数据<br/>文件: implementations/fred_provider.py<br/>(设计态 / design)"]
    src_zephyr_data_connectors ~~~ src_zephyr_data_implementations_fred_provider_py
    src_zephyr_data_normalizers["归一化器<br/>归一化的子目录，归集相关子模块<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: normalizers/<br/>(设计态 / design)"]
    src_zephyr_data_storage["存储<br/>存储的子目录，归集相关子模块<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: storage/<br/>(设计态 / design)"]
    src_zephyr_data_cache["缓存<br/>缓存的子目录，归集相关子模块<br/>⛔ 该域，设计已就绪，等待开发排期<br/>文件: cache/<br/>(设计态 / design)"]
    src_zephyr_data_connectors -.->|data / data| src_zephyr_data_normalizers
    src_zephyr_data_normalizers -.->|data / data| src_zephyr_data_storage
    src_zephyr_data_storage -.->|data / data| src_zephyr_data_cache
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_data_cache,src_zephyr_data_connectors,src_zephyr_data_implementations_fred_provider_py,src_zephyr_data_normalizers,src_zephyr_data_storage design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 质量门禁 / quality_gate (data/quality_gate.py) | → | D_GOV_ENFORCEMENT 规则执行: Quality门禁 / Quality Gate (rule_enforcement/quality_gate... | 导入依赖 / import_depends |
| 2 | 包入口 / D_DATA Data Source (satellite_geospatial_engine/... | → | D_GOV_ENFORCEMENT 规则执行: Quality门禁 / Quality Gate (rule_enforcement/quality_gate... | 导入依赖 / import_depends |
| 3 | #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测试。 / tes... | → | D_GOV_ENFORCEMENT 规则执行: Quality门禁 / Quality Gate (rule_enforcement/quality_gate... | 测试依赖 / test_depends |
| 4 | 7×24 CH 健康探针守护进程 / Ch Health Probe (ops/ch_healt... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 5 | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 6 | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性... | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 7 | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 8 | ch配置 / ch_config (data/ch_config.py) | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 9 | ch配置 / ch_config (data/ch_config.py) | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 10 | ch写入器 / ch_writer (data/ch_writer.py) | → | D_SHARED 共享服务: 线程安全的轻量级 Metrics 注册表 / Metrics (observability/... | 导入依赖 / import_depends |
| 11 | ch写入器 / ch_writer (data/ch_writer.py) | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 12 | akshare提供器 / akshare_provider (implementations/akshare... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 13 | cls提供器 / cls_provider (implementations/cls_provider.py) | → | D_SHARED 共享服务: 常量 / Constants (foundation/constants.py) | 导入依赖 / import_depends |
| 14 | EiaProvider 实现（MOD-L00-004 §4.3 数据源集成器）。 (imp... | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 15 | EiaProvider 实现（MOD-L00-004 §4.3 数据源集成器）。 (imp... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 16 | QWeatherProvider 实现（MOD-L00-004 §4.3 数据源集成器）。... | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 17 | QWeatherProvider 实现（MOD-L00-004 §4.3 数据源集成器）。... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 18 | rss提供器 / rss_provider (implementations/rss_provider.py) | → | D_SHARED 共享服务: 常量 / Constants (foundation/constants.py) | 导入依赖 / import_depends |
| 19 | tushare提供器 / tushare_provider (implementations/tushare... | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 20 | tushare提供器 / tushare_provider (implementations/tushare... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 21 | 本地replay / local_replay (data/local_replay.py) | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 22 | 可观测性指标采集（MOD-L00-004 §11）。 / metrics (data/me... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 23 | 统一进度存储（MOD-L00-004 §7）。 / progress_store (data/... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 24 | 统一进度存储（MOD-L00-004 §7）。 / progress_store (data/... | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 25 | 数据源调度编排层（MOD-L00-004 §6）。 / scheduler (data/s... | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 26 | 数据源健康检查 (data/source_health_check.py) | → | D_SHARED 共享服务: 常量 / Constants (foundation/constants.py) | 导入依赖 / import_depends |
| 27 | 数据源健康检查 (data/source_health_check.py) | → | D_SHARED 共享服务: 注册 datetime/date→sqlite3 str 适配器 / Time Utils (util... | 导入依赖 / import_depends |
| 28 | 数据源测速器（MOD-L00-004 §8.5）。 / speed_tester (data/... | → | D_SHARED 共享服务: 常量 / Constants (foundation/constants.py) | 导入依赖 / import_depends |
| 29 | table注册表 / table_registry (data/table_registry.py) | → | D_SHARED 共享服务: 从当前文件向上查找项目根目录 / Paths (io/paths.py) | 导入依赖 / import_depends |
| 30 | 逐笔订阅器 / tick_subscriber (data/tick_subscriber.py) | → | D_SHARED 共享服务: 线程安全的轻量级 Metrics 注册表 / Metrics (observability/... | 导入依赖 / import_depends |
| 31 | 逐笔订阅器 / tick_subscriber (data/tick_subscriber.py) | → | D_SHARED 共享服务: Prometheus /metrics HTTP 端点 / Metrics Server (observabi... | 导入依赖 / import_depends |
| 32 | wal写入器 / wal_writer (data/wal_writer.py) | → | D_SHARED 共享服务: 线程安全的轻量级 Metrics 注册表 / Metrics (observability/... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_BACKTEST 回测: 数据处理器 / data_handler (core/data_handler.py) | → | 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 2 | D_BACKTEST 回测: 数据处理器 / data_handler (core/data_handler.py) | → | ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 3 | D_BACKTEST 回测: 数据处理器 / data_handler (core/data_handler.py) | → | pit查询 / pit_query (data/pit_query.py) | 导入依赖 / import_depends |
| 4 | D_FACTOR 因子: FactorSignal 批量缓冲写入器 / Buffer (batch_output/buffer... | → | 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 5 | D_FACTOR 因子: FactorSignal 批量缓冲写入器 / Buffer (batch_output/buffer... | → | ch写入器 / ch_writer (data/ch_writer.py) | 导入依赖 / import_depends |
| 6 | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评估。 / back... | → | 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 7 | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评估。 / back... | → | ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 8 | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评估。 / back... | → | table注册表 / table_registry (data/table_registry.py) | 导入依赖 / import_depends |
| 9 | D_GOVERNANCE 生命周期管理: demoe2e管线 / demo_e2e_pipeline (construction/demo_e2e_pi... | → | 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 10 | D_GOVERNANCE 生命周期管理: 记忆提供器 / D_DATA — Memory Provider (intelligence_gove... | → | 策略注册表 / policy_registry (data/policy_registry.py) | 导入依赖 / import_depends |
| 11 | D_GOVERNANCE 生命周期管理: 记忆提供器 / D_DATA — Memory Provider (intelligence_gove... | → | 提供器基类 / provider_base (data/provider_base.py) | 导入依赖 / import_depends |
| 12 | D_GOVERNANCE 生命周期管理: 端到端管道测试 / Test E2e Pipeline (trading/test_e2e_pipe... | → | 质量门禁 / quality_gate (data/quality_gate.py) | 测试依赖 / test_depends |
| 13 | D_GOV_CODE_QUALITY 代码质量治理: 能力一致性门禁 / capability_consistency_gate (commit_gate... | → | 能力校验器 / capability_validator (data/capability_valida... | 导入依赖 / import_depends |
| 14 | D_GOV_CODE_QUALITY 代码质量治理: TABLE-NAME-REGISTRY block 门禁 / Table Name Registry Gate... | → | table注册表 / table_registry (data/table_registry.py) | 导入依赖 / import_depends |
| 15 | D_GOV_CODE_QUALITY 代码质量治理: TRAE-082 symbol 标准化模块测试 / Test Symbol Normalizer (... | → | 包入口 / __init__ (symbol_normalizer/__init__.py) | 测试依赖 / test_depends |
| 16 | D_GOV_SCRIPTS 脚本治理: Code Wiki 统计数据生成器 / Generate Code Wiki Stats (gene... | → | table注册表 / table_registry (data/table_registry.py) | 导入依赖 / import_depends |
| 17 | D_GOV_SCRIPTS 脚本治理: 扫描 ClickHouse 生成业务数据清单 MD / Generate Data Inven... | → | 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 18 | D_GOV_SCRIPTS 脚本治理: 扫描 ClickHouse 生成业务数据清单 MD / Generate Data Inven... | → | ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 19 | D_GOV_SCRIPTS 脚本治理: tick_data 表真重复检查工具 / Check Tick Duplication (data... | → | 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 20 | D_GOV_SCRIPTS 脚本治理: tick_data 表真重复检查工具 / Check Tick Duplication (data... | → | ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 21 | D_INFRA_OPS 基础设施运维: Download模型 / Download Models (ops/download_models.py) | → | 7×24 CH 健康探针守护进程 / Ch Health Probe (ops/ch_healt... | config_depends / config_depends |
| 22 | D_INFRA_RUNTIME 运行时集成: 从 config/.env.clickhouse 加载 ClickHouse 只读连接参数 / ... | → | ch配置 / ch_config (data/ch_config.py) | 导入依赖 / import_depends |
| 23 | D_INFRA_RUNTIME 运行时集成: 单进程串起 tick_subscriber + IntradayFactorLoop / Intrada... | → | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性... | 导入依赖 / import_depends |
| 24 | D_INFRA_RUNTIME 运行时集成: 单进程串起 tick_subscriber + IntradayFactorLoop / Intrada... | → | 逐笔订阅器 / tick_subscriber (data/tick_subscriber.py) | 导入依赖 / import_depends |
| 25 | D_INFRA_RUNTIME 运行时集成: 单进程串起 tick_subscriber + IntradayFactorLoop / Intrada... | → | A 股交易日历守卫（MOD-L00-004）。 / trading_calendar (dat... | 导入依赖 / import_depends |
| 26 | D_INFRA_RUNTIME 运行时集成: tick→Redis tick:{symbol}:latest 双写器 / Test Tick Redis... | → | 逐笔订阅器 / tick_subscriber (data/tick_subscriber.py) | 测试依赖 / test_depends |
| 27 | D_MKT_DATA 行情数据: Autoload (market_data/autoload.py) | → | table注册表 / table_registry (data/table_registry.py) | runtime / runtime |
| 28 | D_MKT_DATA 行情数据: D_MKT_DATA→D_FACTOR 数据供给 / Producer (normalized_mark... | → | 包入口 / __init__ (data/__init__.py) | 导入依赖 / import_depends |
| 29 | D_MKT_DATA 行情数据: D_MKT_DATA→D_FACTOR 数据供给 / Producer (normalized_mark... | → | ch读取器 / ch_reader (data/ch_reader.py) | 导入依赖 / import_depends |
| 30 | D_MKT_DATA 行情数据: D_MKT_DATA→D_FACTOR 数据供给 / Producer (normalized_mark... | → | table注册表 / table_registry (data/table_registry.py) | 导入依赖 / import_depends |
| 31 | D_ML_TRAIN 训练: 训练数据集管理器 / Training Dataset Manager (training_dat... | → | pit查询 / pit_query (data/pit_query.py) | data / data |
| 32 | D_ML_TRAIN 训练: 训练数据集管理器 / Training Dataset Manager (training_dat... | → | table注册表 / table_registry (data/table_registry.py) | data / data |
| 33 | D_ML_TRAIN 训练: 训练管道 / Training Pipeline (training_pipeline/) | → | pit查询 / pit_query (data/pit_query.py) | data / data |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 11 个外部域直接连接（出边 32 条 + 入边 33 条 = 65 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_DATA["D_DATA<br/>数据接入层"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_MKT_DATA["D_MKT_DATA<br/>行情数据"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_ML_TRAIN["D_ML_TRAIN<br/>训练"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_INFRA_OPS["D_INFRA_OPS<br/>基础设施运维"]
    D_DATA -->|29条 导入依赖 / import_depends| D_SHARED
    D_DATA -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_INFRA_RUNTIME -->|5条 导入依赖 / import_depends, 测试依赖 / test_depends| D_DATA
    D_FACTOR -->|5条 导入依赖 / import_depends| D_DATA
    D_GOV_SCRIPTS -->|5条 导入依赖 / import_depends| D_DATA
    D_MKT_DATA -->|4条 导入依赖 / import_depends, runtime / runtime| D_DATA
    D_GOVERNANCE -->|4条 导入依赖 / import_depends, 测试依赖 / test_depends| D_DATA
    D_ML_TRAIN -->|3条 data / data| D_DATA
    D_GOV_CODE_QUALITY -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_DATA
    D_BACKTEST -->|3条 导入依赖 / import_depends| D_DATA
    D_INFRA_OPS -->|1条 config_depends / config_depends| D_DATA
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
