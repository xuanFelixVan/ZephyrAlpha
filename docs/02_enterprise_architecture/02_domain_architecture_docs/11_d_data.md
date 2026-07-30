---
doc_type: architecture_view
title: D_DATA 数据接入层架构文档
version: "1.0"
status: active
date: 2026-07-30
owner: auto-generator
ttl: permanent
---

# 11_d_data / 数据接入层 / Data Access Layer

> **功能简介 / Overview**: 数据接入层，负责数据源接入、数据集成和数据标准化

> **文档作用 / Purpose**: 展示 数据接入层（D_DATA）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 11 | Number | 11 |
| 域ID | D_DATA | Domain ID | D_DATA |
| 域名称 | 数据接入层 | Domain Name | Data Access Layer |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 168 | Module Count | 168 |
| 域内依赖 | 264 | Internal Dependencies | 264 |
| 跨域入边 | 27 | Cross-domain Incoming | 27 |
| 跨域出边 | 22 | Cross-domain Outgoing | 22 |
| 设计态模块 | 6 | Design Modules | 6 |
| 生产态模块 | 162 | Production Modules | 162 |
| 容量 | 162/150 (超容) | Capacity | 162/150 (超容) |
| 描述 | 数据源集成器 | Description | 数据源集成器 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 168 个模块 / 168 modules）。

### L0 基础设施层 / Infrastructure Layer (159 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | schemas/categories/cross_validation_log.py | cross_validation_log 表 DDL-as-Code（P1-4 多源... | 生产态 / production |  |
| 2 | schemas/categories/fundamental_analyst_forecast.py | analyst_forecast（分析师预测）DDL-as-Code（cate... | 生产态 / production |  |
| 3 | schemas/categories/fundamental_balance_sheet.py | balance_sheet（资产负债表）DDL-as-Code（categor... | 生产态 / production |  |
| 4 | schemas/categories/fundamental_cashflow_statement.py | cashflow_statement（现金流量表）DDL-as-Code（ca... | 生产态 / production |  |
| 5 | schemas/categories/fundamental_disclosure_plan.py | disclosure_plan（披露计划）DDL-as-Code（categor... | 生产态 / production |  |
| 6 | schemas/categories/fundamental_equity_pledge_detail.py | equity_pledge_detail（股权质押明细）DDL-as-Code... | 生产态 / production |  |
| 7 | schemas/categories/fundamental_income_statement.py | income_statement（利润表）DDL-as-Code（category... | 生产态 / production |  |
| 8 | schemas/categories/fundamental_industry_class.py | industry_class 表 DDL-as-Code（category_id: fun... | 生产态 / production |  |
| 9 | schemas/categories/fundamental_industry_class_suppl.py | industry_class_suppl（补充行业分类）DDL-as-Code... | 生产态 / production |  |
| 10 | schemas/categories/fundamental_restricted_shares.py | restricted_shares（限售股明细）DDL-as-Code（cat... | 生产态 / production |  |
| 11 | schemas/categories/fundamental_rights_issue.py | rights_issue（分红配股）DDL-as-Code（category_i... | 生产态 / production |  |
| 12 | schemas/categories/fundamental_share_change.py | share_change（股本变动）DDL-as-Code（category_i... | 生产态 / production |  |
| 13 | schemas/categories/fundamental_share_unlock.py | share_unlock（解除限售）DDL-as-Code（category_i... | 生产态 / production |  |
| 14 | schemas/categories/macro_edb_data.py | edb_data 表 DDL-as-Code（category_id: macro_edb... | 生产态 / production |  |
| 15 | schemas/categories/macro_macro_data.py | macro_data 表 DDL-as-Code（category_id: macro_m... | 生产态 / production |  |
| 16 | schemas/categories/market_adj_factor.py | adj_factor 表 DDL-as-Code（category_id: market_... | 生产态 / production |  |
| 17 | schemas/categories/market_auction.py | auction_snapshot 表 DDL-as-Code（category_id: m... | 生产态 / production |  |
| 18 | schemas/categories/market_auction_book.py | auction_book 表 DDL-as-Code（category_id: marke... | 生产态 / production |  |
| 19 | schemas/categories/market_block_trade.py | block_trade 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 20 | schemas/categories/market_block_trade_detail.py | block_trade_detail 表 DDL-as-Code（category_id:... | 生产态 / production |  |
| 21 | schemas/categories/market_cb_iv.py | convertible_bond_iv 表 DDL-as-Code（category_id... | 生产态 / production |  |
| 22 | schemas/categories/market_concept_board.py | concept_board 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 23 | schemas/categories/market_concept_board_constituent.py | concept_board_constituent 表 DDL-as-Code（categ... | 生产态 / production |  |
| 24 | schemas/categories/market_concept_sector.py | concept_sector 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 25 | schemas/categories/market_convertible_bond_list.py | convertible_bond_list 表 DDL-as-Code（category_... | 生产态 / production |  |
| 26 | schemas/categories/market_daily_valuation.py | daily_valuation 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 27 | schemas/categories/market_dragon_tiger.py | dragon_tiger 表 DDL-as-Code（category_id: marke... | 生产态 / production |  |
| 28 | schemas/categories/market_dragon_tiger_seat.py | dragon_tiger_seat 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 29 | schemas/categories/market_etf_benchmark.py | etf_benchmark 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 30 | schemas/categories/market_etf_list.py | etf_list 表 DDL-as-Code（category_id: market_et... | 生产态 / production |  |
| 31 | schemas/categories/market_etf_nav.py | etf_nav 表 DDL-as-Code（category_id: market_etf... | 生产态 / production |  |
| 32 | schemas/categories/market_futures_kline_qmt.py | futures_kline_qmt 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 33 | schemas/categories/market_futures_position.py | futures_position 表 DDL-as-Code（category_id: m... | 生产态 / production |  |
| 34 | schemas/categories/market_futures_term.py | futures_term_structure 表 DDL-as-Code（category... | 生产态 / production |  |
| 35 | schemas/categories/market_hk_connect_flow.py | hk_connect_flow 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 36 | schemas/categories/market_hk_kline.py | hk_kline 表 DDL-as-Code（category_id: market_hk... | 生产态 / production |  |
| 37 | schemas/categories/market_hk_stock_list.py | hk_stock_list 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 38 | schemas/categories/market_hk_trade_calendar.py | hk_trade_calendar 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 39 | schemas/categories/market_index.py | index_quote 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 40 | schemas/categories/market_index_constituent.py | index_constituent 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 41 | schemas/categories/market_index_list.py | index_list 表 DDL-as-Code（category_id: market_... | 生产态 / production |  |
| 42 | schemas/categories/market_index_meta.py | market_index_meta 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 43 | schemas/categories/market_index_weight.py | index_weight 表 DDL-as-Code（category_id: marke... | 生产态 / production |  |
| 44 | schemas/categories/market_kline_15min.py | kline_15min 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 45 | schemas/categories/market_kline_1min.py | kline_1min 表 DDL-as-Code（category_id: market_... | 生产态 / production |  |
| 46 | schemas/categories/market_kline_30min.py | kline_30min 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 47 | schemas/categories/market_kline_5min.py | kline_5min 表 DDL-as-Code（category_id: market_... | 生产态 / production |  |
| 48 | schemas/categories/market_kline_60min.py | kline_60min 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 49 | schemas/categories/market_kline_cb.py | kline_cb 表 DDL-as-Code（category_id: market_kl... | 生产态 / production |  |
| 50 | schemas/categories/market_kline_daily.py | kline_daily 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 51 | schemas/categories/market_kline_daily_hfq.py | kline_daily_hfq 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 52 | schemas/categories/market_kline_etf_15min.py | kline_etf_15min 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 53 | schemas/categories/market_kline_etf_1min.py | kline_etf_1min 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 54 | schemas/categories/market_kline_etf_30min.py | kline_etf_30min 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 55 | schemas/categories/market_kline_etf_5min.py | kline_etf_5min 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 56 | schemas/categories/market_kline_etf_60min.py | kline_etf_60min 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 57 | schemas/categories/market_kline_futures.py | kline_futures 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 58 | schemas/categories/market_kline_hk_daily.py | kline_hk_daily 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 59 | schemas/categories/market_kline_index.py | kline_index 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 60 | schemas/categories/market_kline_lof_15min.py | kline_lof_15min 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 61 | schemas/categories/market_kline_lof_1min.py | kline_lof_1min 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 62 | schemas/categories/market_kline_lof_30min.py | kline_lof_30min 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 63 | schemas/categories/market_kline_lof_5min.py | kline_lof_5min 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 64 | schemas/categories/market_kline_lof_60min.py | kline_lof_60min 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 65 | schemas/categories/market_kline_monthly.py | kline_monthly 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 66 | schemas/categories/market_kline_monthly_hfq.py | kline_monthly_hfq 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 67 | schemas/categories/market_kline_sector.py | kline_sector 表 DDL-as-Code（category_id: marke... | 生产态 / production |  |
| 68 | schemas/categories/market_kline_sector_880.py | kline_sector_880 表 DDL-as-Code（category_id: m... | 生产态 / production |  |
| 69 | schemas/categories/market_kline_sector_intraday.py | kline_sector_intraday 表 DDL-as-Code（category_... | 生产态 / production |  |
| 70 | schemas/categories/market_kline_us_daily.py | kline_us_daily 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 71 | schemas/categories/market_kline_weekly.py | kline_weekly 表 DDL-as-Code（category_id: marke... | 生产态 / production |  |
| 72 | schemas/categories/market_kline_weekly_hfq.py | kline_weekly_hfq 表 DDL-as-Code（category_id: m... | 生产态 / production |  |
| 73 | schemas/categories/market_l2_tick.py | l2_tick 表 DDL-as-Code（category_id: market_l2_... | 生产态 / production |  |
| 74 | schemas/categories/market_limit_up_down.py | limit_up_down 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 75 | schemas/categories/market_lof_list.py | lof_list 表 DDL-as-Code（category_id: market_lo... | 生产态 / production |  |
| 76 | schemas/categories/market_margin_trading.py | margin_trading 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 77 | schemas/categories/market_money_flow.py | money_flow 表 DDL-as-Code（category_id: market_... | 生产态 / production |  |
| 78 | schemas/categories/market_option_greeks.py | option_greeks 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 79 | schemas/categories/market_option_iv.py | option_iv_surface 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 80 | schemas/categories/market_option_kline.py | option_kline 表 DDL-as-Code（category_id: marke... | 生产态 / production |  |
| 81 | schemas/categories/market_realtime_snapshot.py | realtime_snapshot 表 DDL-as-Code（category_id: ... | 生产态 / production |  |
| 82 | schemas/categories/market_sector_constituent.py | sector_constituent 表 DDL-as-Code（category_id:... | 生产态 / production |  |
| 83 | schemas/categories/market_sector_list.py | sector_list 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 84 | schemas/categories/market_sector_meta.py | sector_meta 表 DDL-as-Code（category_id: market... | 生产态 / production |  |
| 85 | schemas/categories/market_sector_snapshot.py | sector_snapshot 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 86 | schemas/categories/market_st_stock_list.py | st_stock_list 表 DDL-as-Code（category_id: mark... | 生产态 / production |  |
| 87 | schemas/categories/market_stock_indicator.py | stock_indicator 表 DDL-as-Code（category_id: ma... | 生产态 / production |  |
| 88 | schemas/categories/market_stock_list.py | stock_list 表 DDL-as-Code（category_id: market_... | 生产态 / production |  |
| 89 | schemas/categories/market_tick.py | tick_data 表 DDL-as-Code（category_id: market_t... | 生产态 / production |  |
| 90 | schemas/categories/market_trade_calendar.py | trade_calendar 表 DDL-as-Code（category_id: mar... | 生产态 / production |  |
| 91 | schemas/categories/market_us_index.py | us_index 表 DDL-as-Code（category_id: market_us... | 生产态 / production |  |
| 92 | scripts/ch/_data_inventory.py | 全库数据盘点：逐表审计行数/日期范围/空表/缺失日... | 生产态 / production |  |
| 93 | scripts/ch/apply_exchange_columns.py | ClickHouse exchange+symbol_canonical 列部署脚本... | 生产态 / production |  |
| 94 | scripts/ch/apply_fundamental_tables_ddl.py | ClickHouse c3_fundamental 财务三表 DDL 部署 + ... | 生产态 / production |  |
| 95 | scripts/ch/apply_market_tables_ddl.py | ClickHouse c1_market 建表 DDL 部署 + 引擎验证脚... | 生产态 / production |  |
| 96 | scripts/ch/apply_rbac.py | ClickHouse RBAC 账号分级部署 + 验证脚本（audit ... | 生产态 / production |  |
| 97 | scripts/ch/apply_timezone_migration.py | ClickHouse 时区防线迁移脚本（audit A组 Schema ... | 生产态 / production |  |
| 98 | scripts/ch/lint_symbol_convention.py | Symbol 约定 lint 门禁（TRAE-082 GATE-SYMBOL-CON... | 生产态 / production |  |
| 99 | scripts/ch/verify_exchange_coverage.py | exchange+symbol_canonical 数据覆盖率校验器（TRA... | 生产态 / production |  |
| 100 | scripts/ch/verify_schema_truth.py | DDL-as-Code 真源 vs ClickHouse 实际表结构 漂移... | 生产态 / production |  |
| 101 | scripts/ops/verify_alert_channels.py | 告警通道端到端验证（B2，#ARCH-CH-023，2026-07-2... | 生产态 / production |  |
| 102 | scripts/register_aux_tasks.ps1 | register_aux_tasks.ps1 | 生产态 / production |  |
| 103 | scripts/register_guard_tasks.ps1 | register_guard_tasks.ps1 | 生产态 / production |  |
| 104 | scripts/start_scheduler.ps1 | start_scheduler.ps1 | 生产态 / production |  |
| 105 | scripts/start_tick_subscriber.ps1 | start_tick_subscriber.ps1 | 生产态 / production |  |
| 106 | src/zephyr/data/__init__.py | zephyr.data — 数据源集成器（MOD-L00-004）。 | 生产态 / production |  |
| 107 | src/zephyr/data/__main__.py | python -m zephyr.data — 数据源集成器 CLI 入口。 | 生产态 / production |  |
| 108 | src/zephyr/data/alerter.py | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §... | 生产态 / production |  |
| 109 | src/zephyr/data/backfill_checker.py | L10 周末补下载检测器——检测过去N天缺失数据并精... | 生产态 / production |  |
| 110 | src/zephyr/data/buffered_writer.py | 批量聚合写入器（MOD-L00-004 §18.3 裁定... | 生产态 / production |  |
| 111 | src/zephyr/data/capability_validator.py | Provider Capability 行为契约校验器（裁定... | 生产态 / production |  |
| 112 | src/zephyr/data/ch_config.py | ClickHouse 连接配置单真源加载器（裁定... | 生产态 / production |  |
| 113 | src/zephyr/data/ch_reader.py | ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 | 生产态 / production |  |
| 114 | src/zephyr/data/ch_writer.py | ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6... | 生产态 / production |  |
| 115 | src/zephyr/data/cli.py | 数据源集成器 CLI（MOD-L00-004 §8.4）。 | 生产态 / production |  |
| 116 | src/zephyr/data/cross_source_validator.py | 多源交叉校验器——比较 QMT 主源与 TDX 备源 tick... | 生产态 / production |  |
| 117 | src/zephyr/data/error_classifier.py | 数据源错误分类器——根据错误字符串判断可恢复性。 | 生产态 / production |  |
| 118 | src/zephyr/data/implementations/__init__.py | 数据源 Provider 实现集合（MOD-L00-004 §4.3）。 | 生产态 / production |  |
| 119 | src/zephyr/data/implementations/akshare_provider.py | AKShare 数据源 Provider 实现（MOD-L00-004 §4.3）。 | 生产态 / production |  |
| 120 | src/zephyr/data/implementations/baostock_provider.py | Baostock 数据源 Provider 实现（MOD-L00-004 §4.... | 生产态 / production |  |
| 121 | src/zephyr/data/implementations/cls_provider.py | 财联社电报数据源 Provider 实现（MOD-L00-004 §4... | 生产态 / production |  |
| 122 | src/zephyr/data/implementations/eastmoney_news_provider.py | 东方财富新闻数据源 Provider 实现（MOD-L00-004 ... | 生产态 / production |  |
| 123 | src/zephyr/data/implementations/ifind_provider.py | IFindProvider 实现（MOD-L00-004 §4.3 数据源集... | 生产态 / production |  |
| 124 | src/zephyr/data/implementations/miniqmt_provider.py | MOD-L00-004 数据源集成器 · MiniQmtIngestProvid... | 生产态 / production |  |
| 125 | src/zephyr/data/implementations/rss_provider.py | RSS 财经新闻数据源 Provider 实现（MOD-L00-004 ... | 生产态 / production |  |
| 126 | src/zephyr/data/implementations/tdx_provider.py | 通达信数据源 Provider 实现（MOD-L00-004 §4.3）。 | 生产态 / production |  |
| 127 | src/zephyr/data/implementations/tickflow_provider.py | TickFlow 数据源 Provider 实现（MOD-L00-004 §4.... | 生产态 / production |  |
| 128 | src/zephyr/data/implementations/tqcenter_provider.py | tqcenter 数据源 Provider 实现。 | 生产态 / production |  |
| 129 | src/zephyr/data/implementations/tushare_provider.py | Tushare 数据源 Provider 实现（MOD-L00-004 §4.3）。 | 生产态 / production |  |
| 130 | src/zephyr/data/integrity_checker.py | 数据完整性巡检器——每天盘后检测全表当日数据是... | 生产态 / production |  |
| 131 | src/zephyr/data/kline_resampler.py | 880xxx 板块K线合成器——从 1m/5m 合成 15m/30m/6... | 生产态 / production |  |
| 132 | src/zephyr/data/local_replay.py | 本地落盘兜底 + 自动回灌（裁定 #ARCH-CH-013 Phas... | 生产态 / production |  |
| 133 | src/zephyr/data/metrics.py | 可观测性指标采集（MOD-L00-004 §11）。 | 生产态 / production |  |
| 134 | src/zephyr/data/news_dedup.py | 新闻数据去重模块（MOD-L00-004 §4.3）。 | 生产态 / production |  |
| 135 | src/zephyr/data/pit_query.py | 财报 Point-In-Time (PIT) 查询能力（#ARCH-CH-021... | 生产态 / production |  |
| 136 | src/zephyr/data/pit_query.py/ |  | 设计态 / design |  |
| 137 | src/zephyr/data/policy_registry.py | per-source 调用策略注册表（MOD-L00-004 §5）。 | 生产态 / production |  |
| 138 | src/zephyr/data/progress_store.py | 统一进度存储（MOD-L00-004 §7）。 | 生产态 / production |  |
| 139 | src/zephyr/data/provider_base.py | 数据源 Provider 抽象基类（MOD-L00-004 §4）。 | 生产态 / production |  |
| 140 | src/zephyr/data/quality_gate.py | Re-export wrapper: QualityReport 真源在 zephyr.... | 生产态 / production |  |
| 141 | src/zephyr/data/redundant_source/__init__.py | 数据源冗余与热切换模块（MOD-L00-005）。 | 生产态 / production |  |
| 142 | src/zephyr/data/satellite_geospatial_engine/__init__.py | D_DATA Data Source | 生产态 / production |  |
| 143 | src/zephyr/data/scheduler.py | 数据源调度编排层（MOD-L00-004 §6）。 | 生产态 / production |  |
| 144 | src/zephyr/data/sector_kline_downloader.py | 880xxx 板块指数K线下载器——盘后从 tqcenter 下... | 生产态 / production |  |
| 145 | src/zephyr/data/sector_ranking_engine.py | 880xxx 板块动态排名引擎——5因子复合排名调整99... | 生产态 / production |  |
| 146 | src/zephyr/data/sector_snapshot_collector.py | 880xxx 板块实时快照采集器（tqcenter → ClickHou... | 生产态 / production |  |
| 147 | src/zephyr/data/speed_tester.py | 数据源测速器（MOD-L00-004 §8.5）。 | 生产态 / production |  |
| 148 | src/zephyr/data/symbol_normalizer/__init__.py | Symbol 标准化模块——TRAE-082 symbol 约定铁律的... | 生产态 / production |  |
| 149 | src/zephyr/data/symbol_normalizer/normalizer.py | symbol 标准化核心实现——TRAE-082 symbol 约定铁律。 | 生产态 / production |  |
| 150 | src/zephyr/data/table_registry.py | 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | 生产态 / production |  |
| 151 | src/zephyr/data/task_queue.py | 任务依赖图 + 优先级队列（MOD-L00-004 §6.3 任务... | 生产态 / production |  |
| 152 | src/zephyr/data/tick_subscriber.py | QMT 实时 Tick 订阅服务——subscribe_quote 实时... | 生产态 / production |  |
| 153 | src/zephyr/data/trading_calendar.py | A 股交易日历守卫（MOD-L00-004）。 | 生产态 / production |  |
| 154 | src/zephyr/data/wal_codec/__init__.py | WAL 段编解码模块（MOD-L00-006）。 | 生产态 / production |  |
| 155 | src/zephyr/data/wal_writer.py | 主动 WAL 写入器（P0-1 Phase A）。 | 生产态 / production |  |
| 156 | tests/data/test_market_quality_validator.py | #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测... | 生产态 / production |  |
| 157 | tests/data/test_pit_query.py | #ARCH-CH-021 P0-5: 财报 PIT 查询能力测试。 | 生产态 / production |  |
| 158 | tests/zephyr/data/test_cross_source_validator.py | cross_source_validator 单元测试（P1-4 多源交叉... | 生产态 / production |  |
| 159 | tests/zephyr/data/test_tick_subscriber.py | tick_subscriber 单元测试（含 Phase C: WalWriter... | 生产态 / production |  |

### L1 基础层 / Foundation Layer (9 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | schemas/categories/market_hog_futures_core.py | hog_futures_core 表 DDL-as-Code（category_id: m... | 设计态 / design |  |
| 2 | schemas/categories/market_hog_province_spot.py | hog_province_spot 表 DDL-as-Code（category_id: ... | 设计态 / design |  |
| 3 | schemas/categories/market_hog_spot_index.py | hog_spot_index 表 DDL-as-Code（category_id: mar... | 设计态 / design |  |
| 4 | schemas/categories/market_kline_etf_daily.py | kline_etf_daily 表 DDL-as-Code（category_id: ma... | 设计态 / design |  |
| 5 | scripts/ch/_recovery_drill.py | 恢复演练：轮询备份完成 → 恢复小表到临时库 → ... | 生产态 / production |  |
| 6 | src/zephyr/data/config/policies.yaml | policies.yaml | 生产态 / production |  |
| 7 | src/zephyr/data/config/schedule.yaml | schedule.yaml | 生产态 / production |  |
| 8 | src/zephyr/data/config/tasks.yaml | tasks.yaml | 生产态 / production |  |
| 9 | src/zephyr/data/symbol_normalizer/ |  | 设计态 / design |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分三个视图：合并全景图、运营态子图、设计态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 168 个模块（生产态 162 + 设计态 6），标签标注成熟度。

#### 第 1 页 / 共 6 页

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        schemas_categories_cross_validation_log_py["(生产态 / production) cross_validation_log 表 DDL-as-Code（P1-4 多源...<br/>文件: cross_validation_log.py"]
        schemas_categories_fundamental_analyst_forecast_py["(生产态 / production) analyst_forecast（分析师预测）DDL-as-Code（cate...<br/>文件: fundamental_analyst_forecast.py"]
        schemas_categories_fundamental_balance_sheet_py["(生产态 / production) balance_sheet（资产负债表）DDL-as-Code（categor...<br/>文件: fundamental_balance_sheet.py"]
        schemas_categories_fundamental_cashflow_statement_py["(生产态 / production) cashflow_statement（现金流量表）DDL-as-Code（ca...<br/>文件: fundamental_cashflow_statement.py"]
        schemas_categories_fundamental_disclosure_plan_py["(生产态 / production) disclosure_plan（披露计划）DDL-as-Code（categor...<br/>文件: fundamental_disclosure_plan.py"]
        schemas_categories_fundamental_equity_pledge_detail_py["(生产态 / production) equity_pledge_detail（股权质押明细）DDL-as-Code...<br/>文件: fundamental_equity_pledge_detail.py"]
        schemas_categories_fundamental_income_statement_py["(生产态 / production) income_statement（利润表）DDL-as-Code（category...<br/>文件: fundamental_income_statement.py"]
        schemas_categories_fundamental_industry_class_py["(生产态 / production) industry_class 表 DDL-as-Code（category_id: fun...<br/>文件: fundamental_industry_class.py"]
        schemas_categories_fundamental_industry_class_suppl_py["(生产态 / production) industry_class_suppl（补充行业分类）DDL-as-Code...<br/>文件: fundamental_industry_class_suppl.py"]
        schemas_categories_fundamental_restricted_shares_py["(生产态 / production) restricted_shares（限售股明细）DDL-as-Code（cat...<br/>文件: fundamental_restricted_shares.py"]
        schemas_categories_fundamental_rights_issue_py["(生产态 / production) rights_issue（分红配股）DDL-as-Code（category_i...<br/>文件: fundamental_rights_issue.py"]
        schemas_categories_fundamental_share_change_py["(生产态 / production) share_change（股本变动）DDL-as-Code（category_i...<br/>文件: fundamental_share_change.py"]
        schemas_categories_fundamental_share_unlock_py["(生产态 / production) share_unlock（解除限售）DDL-as-Code（category_i...<br/>文件: fundamental_share_unlock.py"]
        schemas_categories_macro_edb_data_py["(生产态 / production) edb_data 表 DDL-as-Code（category_id: macro_edb...<br/>文件: macro_edb_data.py"]
        schemas_categories_macro_macro_data_py["(生产态 / production) macro_data 表 DDL-as-Code（category_id: macro_m...<br/>文件: macro_macro_data.py"]
        schemas_categories_market_adj_factor_py["(生产态 / production) adj_factor 表 DDL-as-Code（category_id: market_...<br/>文件: market_adj_factor.py"]
        schemas_categories_market_auction_py["(生产态 / production) auction_snapshot 表 DDL-as-Code（category_id: m...<br/>文件: market_auction.py"]
        schemas_categories_market_auction_book_py["(生产态 / production) auction_book 表 DDL-as-Code（category_id: marke...<br/>文件: market_auction_book.py"]
        schemas_categories_market_block_trade_py["(生产态 / production) block_trade 表 DDL-as-Code（category_id: market...<br/>文件: market_block_trade.py"]
        schemas_categories_market_block_trade_detail_py["(生产态 / production) block_trade_detail 表 DDL-as-Code（category_id:...<br/>文件: market_block_trade_detail.py"]
        schemas_categories_market_cb_iv_py["(生产态 / production) convertible_bond_iv 表 DDL-as-Code（category_id...<br/>文件: market_cb_iv.py"]
        schemas_categories_market_concept_board_py["(生产态 / production) concept_board 表 DDL-as-Code（category_id: mark...<br/>文件: market_concept_board.py"]
        schemas_categories_market_concept_board_constituent_py["(生产态 / production) concept_board_constituent 表 DDL-as-Code（categ...<br/>文件: market_concept_board_constituent.py"]
        schemas_categories_market_concept_sector_py["(生产态 / production) concept_sector 表 DDL-as-Code（category_id: mar...<br/>文件: market_concept_sector.py"]
        schemas_categories_market_convertible_bond_list_py["(生产态 / production) convertible_bond_list 表 DDL-as-Code（category_...<br/>文件: market_convertible_bond_list.py"]
        schemas_categories_market_daily_valuation_py["(生产态 / production) daily_valuation 表 DDL-as-Code（category_id: ma...<br/>文件: market_daily_valuation.py"]
        schemas_categories_market_dragon_tiger_py["(生产态 / production) dragon_tiger 表 DDL-as-Code（category_id: marke...<br/>文件: market_dragon_tiger.py"]
        schemas_categories_market_dragon_tiger_seat_py["(生产态 / production) dragon_tiger_seat 表 DDL-as-Code（category_id: ...<br/>文件: market_dragon_tiger_seat.py"]
        schemas_categories_market_etf_benchmark_py["(生产态 / production) etf_benchmark 表 DDL-as-Code（category_id: mark...<br/>文件: market_etf_benchmark.py"]
        schemas_categories_market_etf_list_py["(生产态 / production) etf_list 表 DDL-as-Code（category_id: market_et...<br/>文件: market_etf_list.py"]
    end
    schemas_categories_fundamental_analyst_forecast_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_equity_pledge_detail_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_balance_sheet_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_cashflow_statement_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_income_statement_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_disclosure_plan_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_industry_class_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_rights_issue_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_restricted_shares_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_industry_class_suppl_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_macro_macro_data_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_share_change_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_adj_factor_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_macro_edb_data_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_share_unlock_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_auction_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_block_trade_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_auction_book_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_block_trade_detail_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_concept_board_constituent_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_concept_sector_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_cb_iv_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_concept_board_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_convertible_bond_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_dragon_tiger_seat_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_dragon_tiger_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_daily_valuation_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_etf_benchmark_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_etf_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_cross_validation_log_py,schemas_categories_fundamental_analyst_forecast_py,schemas_categories_fundamental_balance_sheet_py,schemas_categories_fundamental_cashflow_statement_py,schemas_categories_fundamental_disclosure_plan_py,schemas_categories_fundamental_equity_pledge_detail_py,schemas_categories_fundamental_income_statement_py,schemas_categories_fundamental_industry_class_py,schemas_categories_fundamental_industry_class_suppl_py,schemas_categories_fundamental_restricted_shares_py,schemas_categories_fundamental_rights_issue_py,schemas_categories_fundamental_share_change_py,schemas_categories_fundamental_share_unlock_py,schemas_categories_macro_edb_data_py,schemas_categories_macro_macro_data_py,schemas_categories_market_adj_factor_py,schemas_categories_market_auction_py,schemas_categories_market_auction_book_py,schemas_categories_market_block_trade_py,schemas_categories_market_block_trade_detail_py,schemas_categories_market_cb_iv_py,schemas_categories_market_concept_board_py,schemas_categories_market_concept_board_constituent_py,schemas_categories_market_concept_sector_py,schemas_categories_market_convertible_bond_list_py,schemas_categories_market_daily_valuation_py,schemas_categories_market_dragon_tiger_py,schemas_categories_market_dragon_tiger_seat_py,schemas_categories_market_etf_benchmark_py,schemas_categories_market_etf_list_py production
```

#### 第 2 页 / 共 6 页

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        schemas_categories_market_etf_nav_py["(生产态 / production) etf_nav 表 DDL-as-Code（category_id: market_etf...<br/>文件: market_etf_nav.py"]
        schemas_categories_market_futures_kline_qmt_py["(生产态 / production) futures_kline_qmt 表 DDL-as-Code（category_id: ...<br/>文件: market_futures_kline_qmt.py"]
        schemas_categories_market_futures_position_py["(生产态 / production) futures_position 表 DDL-as-Code（category_id: m...<br/>文件: market_futures_position.py"]
        schemas_categories_market_futures_term_py["(生产态 / production) futures_term_structure 表 DDL-as-Code（category...<br/>文件: market_futures_term.py"]
        schemas_categories_market_hk_connect_flow_py["(生产态 / production) hk_connect_flow 表 DDL-as-Code（category_id: ma...<br/>文件: market_hk_connect_flow.py"]
        schemas_categories_market_hk_kline_py["(生产态 / production) hk_kline 表 DDL-as-Code（category_id: market_hk...<br/>文件: market_hk_kline.py"]
        schemas_categories_market_hk_stock_list_py["(生产态 / production) hk_stock_list 表 DDL-as-Code（category_id: mark...<br/>文件: market_hk_stock_list.py"]
        schemas_categories_market_hk_trade_calendar_py["(生产态 / production) hk_trade_calendar 表 DDL-as-Code（category_id: ...<br/>文件: market_hk_trade_calendar.py"]
        schemas_categories_market_hog_futures_core_py["(设计态 / design) hog_futures_core 表 DDL-as-Code（category_id: m...<br/>文件: market_hog_futures_core.py"]
        schemas_categories_market_hog_province_spot_py["(设计态 / design) hog_province_spot 表 DDL-as-Code（category_id: ...<br/>文件: market_hog_province_spot.py"]
        schemas_categories_market_hog_spot_index_py["(设计态 / design) hog_spot_index 表 DDL-as-Code（category_id: mar...<br/>文件: market_hog_spot_index.py"]
        schemas_categories_market_index_py["(生产态 / production) index_quote 表 DDL-as-Code（category_id: market...<br/>文件: market_index.py"]
        schemas_categories_market_index_constituent_py["(生产态 / production) index_constituent 表 DDL-as-Code（category_id: ...<br/>文件: market_index_constituent.py"]
        schemas_categories_market_index_list_py["(生产态 / production) index_list 表 DDL-as-Code（category_id: market_...<br/>文件: market_index_list.py"]
        schemas_categories_market_index_meta_py["(生产态 / production) market_index_meta 表 DDL-as-Code（category_id: ...<br/>文件: market_index_meta.py"]
        schemas_categories_market_index_weight_py["(生产态 / production) index_weight 表 DDL-as-Code（category_id: marke...<br/>文件: market_index_weight.py"]
        schemas_categories_market_kline_15min_py["(生产态 / production) kline_15min 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_15min.py"]
        schemas_categories_market_kline_1min_py["(生产态 / production) kline_1min 表 DDL-as-Code（category_id: market_...<br/>文件: market_kline_1min.py"]
        schemas_categories_market_kline_30min_py["(生产态 / production) kline_30min 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_30min.py"]
        schemas_categories_market_kline_5min_py["(生产态 / production) kline_5min 表 DDL-as-Code（category_id: market_...<br/>文件: market_kline_5min.py"]
        schemas_categories_market_kline_60min_py["(生产态 / production) kline_60min 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_60min.py"]
        schemas_categories_market_kline_cb_py["(生产态 / production) kline_cb 表 DDL-as-Code（category_id: market_kl...<br/>文件: market_kline_cb.py"]
        schemas_categories_market_kline_daily_py["(生产态 / production) kline_daily 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_daily.py"]
        schemas_categories_market_kline_daily_hfq_py["(生产态 / production) kline_daily_hfq 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_daily_hfq.py"]
        schemas_categories_market_kline_etf_15min_py["(生产态 / production) kline_etf_15min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_15min.py"]
        schemas_categories_market_kline_etf_1min_py["(生产态 / production) kline_etf_1min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_etf_1min.py"]
        schemas_categories_market_kline_etf_30min_py["(生产态 / production) kline_etf_30min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_30min.py"]
        schemas_categories_market_kline_etf_5min_py["(生产态 / production) kline_etf_5min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_etf_5min.py"]
        schemas_categories_market_kline_etf_60min_py["(生产态 / production) kline_etf_60min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_60min.py"]
        schemas_categories_market_kline_etf_daily_py["(设计态 / design) kline_etf_daily 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_daily.py"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_market_etf_nav_py,schemas_categories_market_futures_kline_qmt_py,schemas_categories_market_futures_position_py,schemas_categories_market_futures_term_py,schemas_categories_market_hk_connect_flow_py,schemas_categories_market_hk_kline_py,schemas_categories_market_hk_stock_list_py,schemas_categories_market_hk_trade_calendar_py,schemas_categories_market_index_py,schemas_categories_market_index_constituent_py,schemas_categories_market_index_list_py,schemas_categories_market_index_meta_py,schemas_categories_market_index_weight_py,schemas_categories_market_kline_15min_py,schemas_categories_market_kline_1min_py,schemas_categories_market_kline_30min_py,schemas_categories_market_kline_5min_py,schemas_categories_market_kline_60min_py,schemas_categories_market_kline_cb_py,schemas_categories_market_kline_daily_py,schemas_categories_market_kline_daily_hfq_py,schemas_categories_market_kline_etf_15min_py,schemas_categories_market_kline_etf_1min_py,schemas_categories_market_kline_etf_30min_py,schemas_categories_market_kline_etf_5min_py,schemas_categories_market_kline_etf_60min_py production
    class schemas_categories_market_hog_futures_core_py,schemas_categories_market_hog_province_spot_py,schemas_categories_market_hog_spot_index_py,schemas_categories_market_kline_etf_daily_py design
```

#### 第 3 页 / 共 6 页

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        schemas_categories_market_kline_futures_py["(生产态 / production) kline_futures 表 DDL-as-Code（category_id: mark...<br/>文件: market_kline_futures.py"]
        schemas_categories_market_kline_hk_daily_py["(生产态 / production) kline_hk_daily 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_hk_daily.py"]
        schemas_categories_market_kline_index_py["(生产态 / production) kline_index 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_index.py"]
        schemas_categories_market_kline_lof_15min_py["(生产态 / production) kline_lof_15min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_lof_15min.py"]
        schemas_categories_market_kline_lof_1min_py["(生产态 / production) kline_lof_1min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_lof_1min.py"]
        schemas_categories_market_kline_lof_30min_py["(生产态 / production) kline_lof_30min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_lof_30min.py"]
        schemas_categories_market_kline_lof_5min_py["(生产态 / production) kline_lof_5min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_lof_5min.py"]
        schemas_categories_market_kline_lof_60min_py["(生产态 / production) kline_lof_60min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_lof_60min.py"]
        schemas_categories_market_kline_monthly_py["(生产态 / production) kline_monthly 表 DDL-as-Code（category_id: mark...<br/>文件: market_kline_monthly.py"]
        schemas_categories_market_kline_monthly_hfq_py["(生产态 / production) kline_monthly_hfq 表 DDL-as-Code（category_id: ...<br/>文件: market_kline_monthly_hfq.py"]
        schemas_categories_market_kline_sector_py["(生产态 / production) kline_sector 表 DDL-as-Code（category_id: marke...<br/>文件: market_kline_sector.py"]
        schemas_categories_market_kline_sector_880_py["(生产态 / production) kline_sector_880 表 DDL-as-Code（category_id: m...<br/>文件: market_kline_sector_880.py"]
        schemas_categories_market_kline_sector_intraday_py["(生产态 / production) kline_sector_intraday 表 DDL-as-Code（category_...<br/>文件: market_kline_sector_intraday.py"]
        schemas_categories_market_kline_us_daily_py["(生产态 / production) kline_us_daily 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_us_daily.py"]
        schemas_categories_market_kline_weekly_py["(生产态 / production) kline_weekly 表 DDL-as-Code（category_id: marke...<br/>文件: market_kline_weekly.py"]
        schemas_categories_market_kline_weekly_hfq_py["(生产态 / production) kline_weekly_hfq 表 DDL-as-Code（category_id: m...<br/>文件: market_kline_weekly_hfq.py"]
        schemas_categories_market_l2_tick_py["(生产态 / production) l2_tick 表 DDL-as-Code（category_id: market_l2_...<br/>文件: market_l2_tick.py"]
        schemas_categories_market_limit_up_down_py["(生产态 / production) limit_up_down 表 DDL-as-Code（category_id: mark...<br/>文件: market_limit_up_down.py"]
        schemas_categories_market_lof_list_py["(生产态 / production) lof_list 表 DDL-as-Code（category_id: market_lo...<br/>文件: market_lof_list.py"]
        schemas_categories_market_margin_trading_py["(生产态 / production) margin_trading 表 DDL-as-Code（category_id: mar...<br/>文件: market_margin_trading.py"]
        schemas_categories_market_money_flow_py["(生产态 / production) money_flow 表 DDL-as-Code（category_id: market_...<br/>文件: market_money_flow.py"]
        schemas_categories_market_option_greeks_py["(生产态 / production) option_greeks 表 DDL-as-Code（category_id: mark...<br/>文件: market_option_greeks.py"]
        schemas_categories_market_option_iv_py["(生产态 / production) option_iv_surface 表 DDL-as-Code（category_id: ...<br/>文件: market_option_iv.py"]
        schemas_categories_market_option_kline_py["(生产态 / production) option_kline 表 DDL-as-Code（category_id: marke...<br/>文件: market_option_kline.py"]
        schemas_categories_market_realtime_snapshot_py["(生产态 / production) realtime_snapshot 表 DDL-as-Code（category_id: ...<br/>文件: market_realtime_snapshot.py"]
        schemas_categories_market_sector_constituent_py["(生产态 / production) sector_constituent 表 DDL-as-Code（category_id:...<br/>文件: market_sector_constituent.py"]
        schemas_categories_market_sector_list_py["(生产态 / production) sector_list 表 DDL-as-Code（category_id: market...<br/>文件: market_sector_list.py"]
        schemas_categories_market_sector_meta_py["(生产态 / production) sector_meta 表 DDL-as-Code（category_id: market...<br/>文件: market_sector_meta.py"]
        schemas_categories_market_sector_snapshot_py["(生产态 / production) sector_snapshot 表 DDL-as-Code（category_id: ma...<br/>文件: market_sector_snapshot.py"]
        schemas_categories_market_st_stock_list_py["(生产态 / production) st_stock_list 表 DDL-as-Code（category_id: mark...<br/>文件: market_st_stock_list.py"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_market_kline_futures_py,schemas_categories_market_kline_hk_daily_py,schemas_categories_market_kline_index_py,schemas_categories_market_kline_lof_15min_py,schemas_categories_market_kline_lof_1min_py,schemas_categories_market_kline_lof_30min_py,schemas_categories_market_kline_lof_5min_py,schemas_categories_market_kline_lof_60min_py,schemas_categories_market_kline_monthly_py,schemas_categories_market_kline_monthly_hfq_py,schemas_categories_market_kline_sector_py,schemas_categories_market_kline_sector_880_py,schemas_categories_market_kline_sector_intraday_py,schemas_categories_market_kline_us_daily_py,schemas_categories_market_kline_weekly_py,schemas_categories_market_kline_weekly_hfq_py,schemas_categories_market_l2_tick_py,schemas_categories_market_limit_up_down_py,schemas_categories_market_lof_list_py,schemas_categories_market_margin_trading_py,schemas_categories_market_money_flow_py,schemas_categories_market_option_greeks_py,schemas_categories_market_option_iv_py,schemas_categories_market_option_kline_py,schemas_categories_market_realtime_snapshot_py,schemas_categories_market_sector_constituent_py,schemas_categories_market_sector_list_py,schemas_categories_market_sector_meta_py,schemas_categories_market_sector_snapshot_py,schemas_categories_market_st_stock_list_py production
```

#### 第 4 页 / 共 6 页

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        schemas_categories_market_stock_indicator_py["(生产态 / production) stock_indicator 表 DDL-as-Code（category_id: ma...<br/>文件: market_stock_indicator.py"]
        schemas_categories_market_stock_list_py["(生产态 / production) stock_list 表 DDL-as-Code（category_id: market_...<br/>文件: market_stock_list.py"]
        schemas_categories_market_tick_py["(生产态 / production) tick_data 表 DDL-as-Code（category_id: market_t...<br/>文件: market_tick.py"]
        schemas_categories_market_trade_calendar_py["(生产态 / production) trade_calendar 表 DDL-as-Code（category_id: mar...<br/>文件: market_trade_calendar.py"]
        schemas_categories_market_us_index_py["(生产态 / production) us_index 表 DDL-as-Code（category_id: market_us...<br/>文件: market_us_index.py"]
        scripts_ch_data_inventory_py["(生产态 / production) 全库数据盘点：逐表审计行数/日期范围/空表/缺失日...<br/>文件: _data_inventory.py"]
        scripts_ch_recovery_drill_py["(生产态 / production) 恢复演练：轮询备份完成 → 恢复小表到临时库 → ...<br/>文件: _recovery_drill.py"]
        scripts_ch_apply_exchange_columns_py["(生产态 / production) ClickHouse exchange+symbol_canonical 列部署脚本...<br/>文件: apply_exchange_columns.py"]
        scripts_ch_apply_fundamental_tables_ddl_py["(生产态 / production) ClickHouse c3_fundamental 财务三表 DDL 部署 + ...<br/>文件: apply_fundamental_tables_ddl.py"]
        scripts_ch_apply_market_tables_ddl_py["(生产态 / production) ClickHouse c1_market 建表 DDL 部署 + 引擎验证脚...<br/>文件: apply_market_tables_ddl.py"]
        scripts_ch_apply_rbac_py["(生产态 / production) ClickHouse RBAC 账号分级部署 + 验证脚本（audit ...<br/>文件: apply_rbac.py"]
        scripts_ch_apply_timezone_migration_py["(生产态 / production) ClickHouse 时区防线迁移脚本（audit A组 Schema ...<br/>文件: apply_timezone_migration.py"]
        scripts_ch_lint_symbol_convention_py["(生产态 / production) Symbol 约定 lint 门禁（TRAE-082 GATE-SYMBOL-CON...<br/>文件: lint_symbol_convention.py"]
        scripts_ch_verify_exchange_coverage_py["(生产态 / production) exchange+symbol_canonical 数据覆盖率校验器（TRA...<br/>文件: verify_exchange_coverage.py"]
        scripts_ch_verify_schema_truth_py["(生产态 / production) DDL-as-Code 真源 vs ClickHouse 实际表结构 漂移...<br/>文件: verify_schema_truth.py"]
        scripts_ops_verify_alert_channels_py["(生产态 / production) 告警通道端到端验证（B2，#ARCH-CH-023，2026-07-2...<br/>文件: verify_alert_channels.py"]
        scripts_register_aux_tasks_ps1["(生产态 / production) register_aux_tasks.ps1"]
        scripts_register_guard_tasks_ps1["(生产态 / production) register_guard_tasks.ps1"]
        scripts_start_scheduler_ps1["(生产态 / production) start_scheduler.ps1"]
        scripts_start_tick_subscriber_ps1["(生产态 / production) start_tick_subscriber.ps1"]
        src_zephyr_data_init_py["(生产态 / production) zephyr.data — 数据源集成器（MOD-L00-004）。<br/>文件: __init__.py"]
        src_zephyr_data_main_py["(生产态 / production) python -m zephyr.data — 数据源集成器 CLI 入口。<br/>文件: __main__.py"]
        src_zephyr_data_alerter_py["(生产态 / production) 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §...<br/>文件: alerter.py"]
        src_zephyr_data_backfill_checker_py["(生产态 / production) L10 周末补下载检测器——检测过去N天缺失数据并精...<br/>文件: backfill_checker.py"]
        src_zephyr_data_buffered_writer_py["(生产态 / production) 批量聚合写入器（MOD-L00-004 §18.3 裁定...<br/>文件: buffered_writer.py"]
        src_zephyr_data_capability_validator_py["(生产态 / production) Provider Capability 行为契约校验器（裁定...<br/>文件: capability_validator.py"]
        src_zephyr_data_ch_config_py["(生产态 / production) ClickHouse 连接配置单真源加载器（裁定...<br/>文件: ch_config.py"]
        src_zephyr_data_ch_reader_py["(生产态 / production) ClickHouse 统一读取层（裁定 #ARCH-CH-007）。<br/>文件: ch_reader.py"]
        src_zephyr_data_ch_writer_py["(生产态 / production) ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6...<br/>文件: ch_writer.py"]
        src_zephyr_data_cli_py["(生产态 / production) 数据源集成器 CLI（MOD-L00-004 §8.4）。<br/>文件: cli.py"]
    end
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_buffered_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_main_py -->|导入依赖 / import_depends| src_zephyr_data_cli_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_lint_symbol_convention_py -->|config_depends / config_depends| scripts_ch_apply_exchange_columns_py
    scripts_ch_apply_rbac_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_apply_timezone_migration_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_verify_schema_truth_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| scripts_ch_apply_exchange_columns_py
    scripts_ch_data_inventory_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_recovery_drill_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ops_verify_alert_channels_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_data_ch_config_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_alerter_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_ch_config_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_alerter_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_alerter_py -->|导入依赖 / import_depends| D_SHARED
    D_FACTOR["(设计态 / design) D_FACTOR"]
    D_FACTOR -.->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    D_GOV_CODE_QUALITY["(生产态 / production) D_GOV_CODE_QUALITY"]
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_data_capability_validator_py
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_MKT_DATA["(生产态 / production) D_MKT_DATA"]
    D_MKT_DATA -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_MKT_DATA -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_BACKTEST["(生产态 / production) D_BACKTEST"]
    D_BACKTEST -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    D_BACKTEST -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_data_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_market_stock_indicator_py,schemas_categories_market_stock_list_py,schemas_categories_market_tick_py,schemas_categories_market_trade_calendar_py,schemas_categories_market_us_index_py,scripts_ch_data_inventory_py,scripts_ch_recovery_drill_py,scripts_ch_apply_exchange_columns_py,scripts_ch_apply_fundamental_tables_ddl_py,scripts_ch_apply_market_tables_ddl_py,scripts_ch_apply_rbac_py,scripts_ch_apply_timezone_migration_py,scripts_ch_lint_symbol_convention_py,scripts_ch_verify_exchange_coverage_py,scripts_ch_verify_schema_truth_py,scripts_ops_verify_alert_channels_py,scripts_register_aux_tasks_ps1,scripts_register_guard_tasks_ps1,scripts_start_scheduler_ps1,scripts_start_tick_subscriber_ps1,src_zephyr_data_init_py,src_zephyr_data_main_py,src_zephyr_data_alerter_py,src_zephyr_data_backfill_checker_py,src_zephyr_data_buffered_writer_py,src_zephyr_data_capability_validator_py,src_zephyr_data_ch_config_py,src_zephyr_data_ch_reader_py,src_zephyr_data_ch_writer_py,src_zephyr_data_cli_py production
    class D_SHARED,D_GOV_CODE_QUALITY,D_MKT_DATA,D_GOV_SCRIPTS,D_BACKTEST,D_INFRA_RUNTIME,D_GOVERNANCE external_prod
    class D_FACTOR external_design
```

#### 第 5 页 / 共 6 页

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        src_zephyr_data_config_policies_yaml["(生产态 / production) policies.yaml"]
        src_zephyr_data_config_schedule_yaml["(生产态 / production) schedule.yaml"]
        src_zephyr_data_config_tasks_yaml["(生产态 / production) tasks.yaml"]
        src_zephyr_data_cross_source_validator_py["(生产态 / production) 多源交叉校验器——比较 QMT 主源与 TDX 备源 tick...<br/>文件: cross_source_validator.py"]
        src_zephyr_data_error_classifier_py["(生产态 / production) 数据源错误分类器——根据错误字符串判断可恢复性。<br/>文件: error_classifier.py"]
        src_zephyr_data_implementations_init_py["(生产态 / production) 数据源 Provider 实现集合（MOD-L00-004 §4.3）。<br/>文件: __init__.py"]
        src_zephyr_data_implementations_akshare_provider_py["(生产态 / production) AKShare 数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>文件: akshare_provider.py"]
        src_zephyr_data_implementations_baostock_provider_py["(生产态 / production) Baostock 数据源 Provider 实现（MOD-L00-004 §4....<br/>文件: baostock_provider.py"]
        src_zephyr_data_implementations_cls_provider_py["(生产态 / production) 财联社电报数据源 Provider 实现（MOD-L00-004 §4...<br/>文件: cls_provider.py"]
        src_zephyr_data_implementations_eastmoney_news_provider_py["(生产态 / production) 东方财富新闻数据源 Provider 实现（MOD-L00-004 ...<br/>文件: eastmoney_news_provider.py"]
        src_zephyr_data_implementations_ifind_provider_py["(生产态 / production) IFindProvider 实现（MOD-L00-004 §4.3 数据源集...<br/>文件: ifind_provider.py"]
        src_zephyr_data_implementations_miniqmt_provider_py["(生产态 / production) MOD-L00-004 数据源集成器 · MiniQmtIngestProvid...<br/>文件: miniqmt_provider.py"]
        src_zephyr_data_implementations_rss_provider_py["(生产态 / production) RSS 财经新闻数据源 Provider 实现（MOD-L00-004 ...<br/>文件: rss_provider.py"]
        src_zephyr_data_implementations_tdx_provider_py["(生产态 / production) 通达信数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>文件: tdx_provider.py"]
        src_zephyr_data_implementations_tickflow_provider_py["(生产态 / production) TickFlow 数据源 Provider 实现（MOD-L00-004 §4....<br/>文件: tickflow_provider.py"]
        src_zephyr_data_implementations_tqcenter_provider_py["(生产态 / production) tqcenter 数据源 Provider 实现。<br/>文件: tqcenter_provider.py"]
        src_zephyr_data_implementations_tushare_provider_py["(生产态 / production) Tushare 数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>文件: tushare_provider.py"]
        src_zephyr_data_integrity_checker_py["(生产态 / production) 数据完整性巡检器——每天盘后检测全表当日数据是...<br/>文件: integrity_checker.py"]
        src_zephyr_data_kline_resampler_py["(生产态 / production) 880xxx 板块K线合成器——从 1m/5m 合成 15m/30m/6...<br/>文件: kline_resampler.py"]
        src_zephyr_data_local_replay_py["(生产态 / production) 本地落盘兜底 + 自动回灌（裁定 #ARCH-CH-013 Phas...<br/>文件: local_replay.py"]
        src_zephyr_data_metrics_py["(生产态 / production) 可观测性指标采集（MOD-L00-004 §11）。<br/>文件: metrics.py"]
        src_zephyr_data_news_dedup_py["(生产态 / production) 新闻数据去重模块（MOD-L00-004 §4.3）。<br/>文件: news_dedup.py"]
        src_zephyr_data_pit_query_py["(生产态 / production) 财报 Point-In-Time (PIT) 查询能力（#ARCH-CH-021...<br/>文件: pit_query.py"]
        src_zephyr_data_pit_query_py_1["(设计态 / design) "]
        src_zephyr_data_policy_registry_py["(生产态 / production) per-source 调用策略注册表（MOD-L00-004 §5）。<br/>文件: policy_registry.py"]
        src_zephyr_data_progress_store_py["(生产态 / production) 统一进度存储（MOD-L00-004 §7）。<br/>文件: progress_store.py"]
        src_zephyr_data_provider_base_py["(生产态 / production) 数据源 Provider 抽象基类（MOD-L00-004 §4）。<br/>文件: provider_base.py"]
        src_zephyr_data_quality_gate_py["(生产态 / production) Re-export wrapper: QualityReport 真源在 zephyr....<br/>文件: quality_gate.py"]
        src_zephyr_data_redundant_source_init_py["(生产态 / production) 数据源冗余与热切换模块（MOD-L00-005）。<br/>文件: __init__.py"]
        src_zephyr_data_satellite_geospatial_engine_init_py["(生产态 / production) D_DATA Data Source<br/>文件: __init__.py"]
    end
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_provider_base_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_ifind_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_ifind_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_ifind_provider_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_satellite_geospatial_engine_init_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_progress_store_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    src_zephyr_data_quality_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_data_local_replay_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_satellite_geospatial_engine_init_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_data_metrics_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_progress_store_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_data_config_policies_yaml,src_zephyr_data_config_schedule_yaml,src_zephyr_data_config_tasks_yaml,src_zephyr_data_cross_source_validator_py,src_zephyr_data_error_classifier_py,src_zephyr_data_implementations_init_py,src_zephyr_data_implementations_akshare_provider_py,src_zephyr_data_implementations_baostock_provider_py,src_zephyr_data_implementations_cls_provider_py,src_zephyr_data_implementations_eastmoney_news_provider_py,src_zephyr_data_implementations_ifind_provider_py,src_zephyr_data_implementations_miniqmt_provider_py,src_zephyr_data_implementations_rss_provider_py,src_zephyr_data_implementations_tdx_provider_py,src_zephyr_data_implementations_tickflow_provider_py,src_zephyr_data_implementations_tqcenter_provider_py,src_zephyr_data_implementations_tushare_provider_py,src_zephyr_data_integrity_checker_py,src_zephyr_data_kline_resampler_py,src_zephyr_data_local_replay_py,src_zephyr_data_metrics_py,src_zephyr_data_news_dedup_py,src_zephyr_data_pit_query_py,src_zephyr_data_policy_registry_py,src_zephyr_data_progress_store_py,src_zephyr_data_provider_base_py,src_zephyr_data_quality_gate_py,src_zephyr_data_redundant_source_init_py,src_zephyr_data_satellite_geospatial_engine_init_py production
    class src_zephyr_data_pit_query_py_1 design
    class D_SHARED,D_GOV_ENFORCEMENT,D_GOVERNANCE external_prod
```

#### 第 6 页 / 共 6 页

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        src_zephyr_data_scheduler_py["(生产态 / production) 数据源调度编排层（MOD-L00-004 §6）。<br/>文件: scheduler.py"]
        src_zephyr_data_sector_kline_downloader_py["(生产态 / production) 880xxx 板块指数K线下载器——盘后从 tqcenter 下...<br/>文件: sector_kline_downloader.py"]
        src_zephyr_data_sector_ranking_engine_py["(生产态 / production) 880xxx 板块动态排名引擎——5因子复合排名调整99...<br/>文件: sector_ranking_engine.py"]
        src_zephyr_data_sector_snapshot_collector_py["(生产态 / production) 880xxx 板块实时快照采集器（tqcenter → ClickHou...<br/>文件: sector_snapshot_collector.py"]
        src_zephyr_data_speed_tester_py["(生产态 / production) 数据源测速器（MOD-L00-004 §8.5）。<br/>文件: speed_tester.py"]
        src_zephyr_data_symbol_normalizer["(设计态 / design) "]
        src_zephyr_data_symbol_normalizer_init_py["(生产态 / production) Symbol 标准化模块——TRAE-082 symbol 约定铁律的...<br/>文件: __init__.py"]
        src_zephyr_data_symbol_normalizer_normalizer_py["(生产态 / production) symbol 标准化核心实现——TRAE-082 symbol 约定铁律。<br/>文件: normalizer.py"]
        src_zephyr_data_table_registry_py["(生产态 / production) 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ...<br/>文件: table_registry.py"]
        src_zephyr_data_task_queue_py["(生产态 / production) 任务依赖图 + 优先级队列（MOD-L00-004 §6.3 任务...<br/>文件: task_queue.py"]
        src_zephyr_data_tick_subscriber_py["(生产态 / production) QMT 实时 Tick 订阅服务——subscribe_quote 实时...<br/>文件: tick_subscriber.py"]
        src_zephyr_data_trading_calendar_py["(生产态 / production) A 股交易日历守卫（MOD-L00-004）。<br/>文件: trading_calendar.py"]
        src_zephyr_data_wal_codec_init_py["(生产态 / production) WAL 段编解码模块（MOD-L00-006）。<br/>文件: __init__.py"]
        src_zephyr_data_wal_writer_py["(生产态 / production) 主动 WAL 写入器（P0-1 Phase A）。<br/>文件: wal_writer.py"]
        tests_data_test_market_quality_validator_py["(生产态 / production) #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测...<br/>文件: test_market_quality_validator.py"]
        tests_data_test_pit_query_py["(生产态 / production) #ARCH-CH-021 P0-5: 财报 PIT 查询能力测试。<br/>文件: test_pit_query.py"]
        tests_zephyr_data_test_cross_source_validator_py["(生产态 / production) cross_source_validator 单元测试（P1-4 多源交叉...<br/>文件: test_cross_source_validator.py"]
        tests_zephyr_data_test_tick_subscriber_py["(生产态 / production) tick_subscriber 单元测试（含 Phase C: WalWriter...<br/>文件: test_tick_subscriber.py"]
    end
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_trading_calendar_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_task_queue_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_sector_snapshot_collector_py -->|导入依赖 / import_depends| src_zephyr_data_sector_ranking_engine_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_wal_writer_py
    src_zephyr_data_symbol_normalizer_init_py -->|导入依赖 / import_depends| src_zephyr_data_symbol_normalizer_normalizer_py
    tests_zephyr_data_test_tick_subscriber_py -->|测试依赖 / test_depends| src_zephyr_data_tick_subscriber_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    tests_data_test_market_quality_validator_py -->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_table_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_CODE_QUALITY["(生产态 / production) D_GOV_CODE_QUALITY"]
    D_GOV_CODE_QUALITY -->|测试依赖 / test_depends| src_zephyr_data_symbol_normalizer_init_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_MKT_DATA["(生产态 / production) D_MKT_DATA"]
    D_MKT_DATA -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_FACTOR["(生产态 / production) D_FACTOR"]
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_data_scheduler_py,src_zephyr_data_sector_kline_downloader_py,src_zephyr_data_sector_ranking_engine_py,src_zephyr_data_sector_snapshot_collector_py,src_zephyr_data_speed_tester_py,src_zephyr_data_symbol_normalizer_init_py,src_zephyr_data_symbol_normalizer_normalizer_py,src_zephyr_data_table_registry_py,src_zephyr_data_task_queue_py,src_zephyr_data_tick_subscriber_py,src_zephyr_data_trading_calendar_py,src_zephyr_data_wal_codec_init_py,src_zephyr_data_wal_writer_py,tests_data_test_market_quality_validator_py,tests_data_test_pit_query_py,tests_zephyr_data_test_cross_source_validator_py,tests_zephyr_data_test_tick_subscriber_py production
    class src_zephyr_data_symbol_normalizer design
    class D_SHARED,D_GOV_ENFORCEMENT,D_GOV_CODE_QUALITY,D_GOV_SCRIPTS,D_MKT_DATA,D_FACTOR external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 162 个，260 条域内依赖）。

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        schemas_categories_cross_validation_log_py["(生产态 / production) cross_validation_log 表 DDL-as-Code（P1-4 多源...<br/>文件: cross_validation_log.py"]
        schemas_categories_fundamental_analyst_forecast_py["(生产态 / production) analyst_forecast（分析师预测）DDL-as-Code（cate...<br/>文件: fundamental_analyst_forecast.py"]
        schemas_categories_fundamental_balance_sheet_py["(生产态 / production) balance_sheet（资产负债表）DDL-as-Code（categor...<br/>文件: fundamental_balance_sheet.py"]
        schemas_categories_fundamental_cashflow_statement_py["(生产态 / production) cashflow_statement（现金流量表）DDL-as-Code（ca...<br/>文件: fundamental_cashflow_statement.py"]
        schemas_categories_fundamental_disclosure_plan_py["(生产态 / production) disclosure_plan（披露计划）DDL-as-Code（categor...<br/>文件: fundamental_disclosure_plan.py"]
        schemas_categories_fundamental_equity_pledge_detail_py["(生产态 / production) equity_pledge_detail（股权质押明细）DDL-as-Code...<br/>文件: fundamental_equity_pledge_detail.py"]
        schemas_categories_fundamental_income_statement_py["(生产态 / production) income_statement（利润表）DDL-as-Code（category...<br/>文件: fundamental_income_statement.py"]
        schemas_categories_fundamental_industry_class_py["(生产态 / production) industry_class 表 DDL-as-Code（category_id: fun...<br/>文件: fundamental_industry_class.py"]
        schemas_categories_fundamental_industry_class_suppl_py["(生产态 / production) industry_class_suppl（补充行业分类）DDL-as-Code...<br/>文件: fundamental_industry_class_suppl.py"]
        schemas_categories_fundamental_restricted_shares_py["(生产态 / production) restricted_shares（限售股明细）DDL-as-Code（cat...<br/>文件: fundamental_restricted_shares.py"]
        schemas_categories_fundamental_rights_issue_py["(生产态 / production) rights_issue（分红配股）DDL-as-Code（category_i...<br/>文件: fundamental_rights_issue.py"]
        schemas_categories_fundamental_share_change_py["(生产态 / production) share_change（股本变动）DDL-as-Code（category_i...<br/>文件: fundamental_share_change.py"]
        schemas_categories_fundamental_share_unlock_py["(生产态 / production) share_unlock（解除限售）DDL-as-Code（category_i...<br/>文件: fundamental_share_unlock.py"]
        schemas_categories_macro_edb_data_py["(生产态 / production) edb_data 表 DDL-as-Code（category_id: macro_edb...<br/>文件: macro_edb_data.py"]
        schemas_categories_macro_macro_data_py["(生产态 / production) macro_data 表 DDL-as-Code（category_id: macro_m...<br/>文件: macro_macro_data.py"]
        schemas_categories_market_adj_factor_py["(生产态 / production) adj_factor 表 DDL-as-Code（category_id: market_...<br/>文件: market_adj_factor.py"]
        schemas_categories_market_auction_py["(生产态 / production) auction_snapshot 表 DDL-as-Code（category_id: m...<br/>文件: market_auction.py"]
        schemas_categories_market_auction_book_py["(生产态 / production) auction_book 表 DDL-as-Code（category_id: marke...<br/>文件: market_auction_book.py"]
        schemas_categories_market_block_trade_py["(生产态 / production) block_trade 表 DDL-as-Code（category_id: market...<br/>文件: market_block_trade.py"]
        schemas_categories_market_block_trade_detail_py["(生产态 / production) block_trade_detail 表 DDL-as-Code（category_id:...<br/>文件: market_block_trade_detail.py"]
        schemas_categories_market_cb_iv_py["(生产态 / production) convertible_bond_iv 表 DDL-as-Code（category_id...<br/>文件: market_cb_iv.py"]
        schemas_categories_market_concept_board_py["(生产态 / production) concept_board 表 DDL-as-Code（category_id: mark...<br/>文件: market_concept_board.py"]
        schemas_categories_market_concept_board_constituent_py["(生产态 / production) concept_board_constituent 表 DDL-as-Code（categ...<br/>文件: market_concept_board_constituent.py"]
        schemas_categories_market_concept_sector_py["(生产态 / production) concept_sector 表 DDL-as-Code（category_id: mar...<br/>文件: market_concept_sector.py"]
        schemas_categories_market_convertible_bond_list_py["(生产态 / production) convertible_bond_list 表 DDL-as-Code（category_...<br/>文件: market_convertible_bond_list.py"]
        schemas_categories_market_daily_valuation_py["(生产态 / production) daily_valuation 表 DDL-as-Code（category_id: ma...<br/>文件: market_daily_valuation.py"]
        schemas_categories_market_dragon_tiger_py["(生产态 / production) dragon_tiger 表 DDL-as-Code（category_id: marke...<br/>文件: market_dragon_tiger.py"]
        schemas_categories_market_dragon_tiger_seat_py["(生产态 / production) dragon_tiger_seat 表 DDL-as-Code（category_id: ...<br/>文件: market_dragon_tiger_seat.py"]
        schemas_categories_market_etf_benchmark_py["(生产态 / production) etf_benchmark 表 DDL-as-Code（category_id: mark...<br/>文件: market_etf_benchmark.py"]
        schemas_categories_market_etf_list_py["(生产态 / production) etf_list 表 DDL-as-Code（category_id: market_et...<br/>文件: market_etf_list.py"]
        schemas_categories_market_etf_nav_py["(生产态 / production) etf_nav 表 DDL-as-Code（category_id: market_etf...<br/>文件: market_etf_nav.py"]
        schemas_categories_market_futures_kline_qmt_py["(生产态 / production) futures_kline_qmt 表 DDL-as-Code（category_id: ...<br/>文件: market_futures_kline_qmt.py"]
        schemas_categories_market_futures_position_py["(生产态 / production) futures_position 表 DDL-as-Code（category_id: m...<br/>文件: market_futures_position.py"]
        schemas_categories_market_futures_term_py["(生产态 / production) futures_term_structure 表 DDL-as-Code（category...<br/>文件: market_futures_term.py"]
        schemas_categories_market_hk_connect_flow_py["(生产态 / production) hk_connect_flow 表 DDL-as-Code（category_id: ma...<br/>文件: market_hk_connect_flow.py"]
        schemas_categories_market_hk_kline_py["(生产态 / production) hk_kline 表 DDL-as-Code（category_id: market_hk...<br/>文件: market_hk_kline.py"]
        schemas_categories_market_hk_stock_list_py["(生产态 / production) hk_stock_list 表 DDL-as-Code（category_id: mark...<br/>文件: market_hk_stock_list.py"]
        schemas_categories_market_hk_trade_calendar_py["(生产态 / production) hk_trade_calendar 表 DDL-as-Code（category_id: ...<br/>文件: market_hk_trade_calendar.py"]
        schemas_categories_market_index_py["(生产态 / production) index_quote 表 DDL-as-Code（category_id: market...<br/>文件: market_index.py"]
        schemas_categories_market_index_constituent_py["(生产态 / production) index_constituent 表 DDL-as-Code（category_id: ...<br/>文件: market_index_constituent.py"]
        schemas_categories_market_index_list_py["(生产态 / production) index_list 表 DDL-as-Code（category_id: market_...<br/>文件: market_index_list.py"]
        schemas_categories_market_index_meta_py["(生产态 / production) market_index_meta 表 DDL-as-Code（category_id: ...<br/>文件: market_index_meta.py"]
        schemas_categories_market_index_weight_py["(生产态 / production) index_weight 表 DDL-as-Code（category_id: marke...<br/>文件: market_index_weight.py"]
        schemas_categories_market_kline_15min_py["(生产态 / production) kline_15min 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_15min.py"]
        schemas_categories_market_kline_1min_py["(生产态 / production) kline_1min 表 DDL-as-Code（category_id: market_...<br/>文件: market_kline_1min.py"]
        schemas_categories_market_kline_30min_py["(生产态 / production) kline_30min 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_30min.py"]
        schemas_categories_market_kline_5min_py["(生产态 / production) kline_5min 表 DDL-as-Code（category_id: market_...<br/>文件: market_kline_5min.py"]
        schemas_categories_market_kline_60min_py["(生产态 / production) kline_60min 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_60min.py"]
        schemas_categories_market_kline_cb_py["(生产态 / production) kline_cb 表 DDL-as-Code（category_id: market_kl...<br/>文件: market_kline_cb.py"]
        schemas_categories_market_kline_daily_py["(生产态 / production) kline_daily 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_daily.py"]
        schemas_categories_market_kline_daily_hfq_py["(生产态 / production) kline_daily_hfq 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_daily_hfq.py"]
        schemas_categories_market_kline_etf_15min_py["(生产态 / production) kline_etf_15min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_15min.py"]
        schemas_categories_market_kline_etf_1min_py["(生产态 / production) kline_etf_1min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_etf_1min.py"]
        schemas_categories_market_kline_etf_30min_py["(生产态 / production) kline_etf_30min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_30min.py"]
        schemas_categories_market_kline_etf_5min_py["(生产态 / production) kline_etf_5min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_etf_5min.py"]
        schemas_categories_market_kline_etf_60min_py["(生产态 / production) kline_etf_60min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_60min.py"]
        schemas_categories_market_kline_futures_py["(生产态 / production) kline_futures 表 DDL-as-Code（category_id: mark...<br/>文件: market_kline_futures.py"]
        schemas_categories_market_kline_hk_daily_py["(生产态 / production) kline_hk_daily 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_hk_daily.py"]
        schemas_categories_market_kline_index_py["(生产态 / production) kline_index 表 DDL-as-Code（category_id: market...<br/>文件: market_kline_index.py"]
        schemas_categories_market_kline_lof_15min_py["(生产态 / production) kline_lof_15min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_lof_15min.py"]
        schemas_categories_market_kline_lof_1min_py["(生产态 / production) kline_lof_1min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_lof_1min.py"]
        schemas_categories_market_kline_lof_30min_py["(生产态 / production) kline_lof_30min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_lof_30min.py"]
        schemas_categories_market_kline_lof_5min_py["(生产态 / production) kline_lof_5min 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_lof_5min.py"]
        schemas_categories_market_kline_lof_60min_py["(生产态 / production) kline_lof_60min 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_lof_60min.py"]
        schemas_categories_market_kline_monthly_py["(生产态 / production) kline_monthly 表 DDL-as-Code（category_id: mark...<br/>文件: market_kline_monthly.py"]
        schemas_categories_market_kline_monthly_hfq_py["(生产态 / production) kline_monthly_hfq 表 DDL-as-Code（category_id: ...<br/>文件: market_kline_monthly_hfq.py"]
        schemas_categories_market_kline_sector_py["(生产态 / production) kline_sector 表 DDL-as-Code（category_id: marke...<br/>文件: market_kline_sector.py"]
        schemas_categories_market_kline_sector_880_py["(生产态 / production) kline_sector_880 表 DDL-as-Code（category_id: m...<br/>文件: market_kline_sector_880.py"]
        schemas_categories_market_kline_sector_intraday_py["(生产态 / production) kline_sector_intraday 表 DDL-as-Code（category_...<br/>文件: market_kline_sector_intraday.py"]
        schemas_categories_market_kline_us_daily_py["(生产态 / production) kline_us_daily 表 DDL-as-Code（category_id: mar...<br/>文件: market_kline_us_daily.py"]
        schemas_categories_market_kline_weekly_py["(生产态 / production) kline_weekly 表 DDL-as-Code（category_id: marke...<br/>文件: market_kline_weekly.py"]
        schemas_categories_market_kline_weekly_hfq_py["(生产态 / production) kline_weekly_hfq 表 DDL-as-Code（category_id: m...<br/>文件: market_kline_weekly_hfq.py"]
        schemas_categories_market_l2_tick_py["(生产态 / production) l2_tick 表 DDL-as-Code（category_id: market_l2_...<br/>文件: market_l2_tick.py"]
        schemas_categories_market_limit_up_down_py["(生产态 / production) limit_up_down 表 DDL-as-Code（category_id: mark...<br/>文件: market_limit_up_down.py"]
        schemas_categories_market_lof_list_py["(生产态 / production) lof_list 表 DDL-as-Code（category_id: market_lo...<br/>文件: market_lof_list.py"]
        schemas_categories_market_margin_trading_py["(生产态 / production) margin_trading 表 DDL-as-Code（category_id: mar...<br/>文件: market_margin_trading.py"]
        schemas_categories_market_money_flow_py["(生产态 / production) money_flow 表 DDL-as-Code（category_id: market_...<br/>文件: market_money_flow.py"]
        schemas_categories_market_option_greeks_py["(生产态 / production) option_greeks 表 DDL-as-Code（category_id: mark...<br/>文件: market_option_greeks.py"]
        schemas_categories_market_option_iv_py["(生产态 / production) option_iv_surface 表 DDL-as-Code（category_id: ...<br/>文件: market_option_iv.py"]
        schemas_categories_market_option_kline_py["(生产态 / production) option_kline 表 DDL-as-Code（category_id: marke...<br/>文件: market_option_kline.py"]
        schemas_categories_market_realtime_snapshot_py["(生产态 / production) realtime_snapshot 表 DDL-as-Code（category_id: ...<br/>文件: market_realtime_snapshot.py"]
        schemas_categories_market_sector_constituent_py["(生产态 / production) sector_constituent 表 DDL-as-Code（category_id:...<br/>文件: market_sector_constituent.py"]
        schemas_categories_market_sector_list_py["(生产态 / production) sector_list 表 DDL-as-Code（category_id: market...<br/>文件: market_sector_list.py"]
        schemas_categories_market_sector_meta_py["(生产态 / production) sector_meta 表 DDL-as-Code（category_id: market...<br/>文件: market_sector_meta.py"]
        schemas_categories_market_sector_snapshot_py["(生产态 / production) sector_snapshot 表 DDL-as-Code（category_id: ma...<br/>文件: market_sector_snapshot.py"]
        schemas_categories_market_st_stock_list_py["(生产态 / production) st_stock_list 表 DDL-as-Code（category_id: mark...<br/>文件: market_st_stock_list.py"]
        schemas_categories_market_stock_indicator_py["(生产态 / production) stock_indicator 表 DDL-as-Code（category_id: ma...<br/>文件: market_stock_indicator.py"]
        schemas_categories_market_stock_list_py["(生产态 / production) stock_list 表 DDL-as-Code（category_id: market_...<br/>文件: market_stock_list.py"]
        schemas_categories_market_tick_py["(生产态 / production) tick_data 表 DDL-as-Code（category_id: market_t...<br/>文件: market_tick.py"]
        schemas_categories_market_trade_calendar_py["(生产态 / production) trade_calendar 表 DDL-as-Code（category_id: mar...<br/>文件: market_trade_calendar.py"]
        schemas_categories_market_us_index_py["(生产态 / production) us_index 表 DDL-as-Code（category_id: market_us...<br/>文件: market_us_index.py"]
        scripts_ch_data_inventory_py["(生产态 / production) 全库数据盘点：逐表审计行数/日期范围/空表/缺失日...<br/>文件: _data_inventory.py"]
        scripts_ch_recovery_drill_py["(生产态 / production) 恢复演练：轮询备份完成 → 恢复小表到临时库 → ...<br/>文件: _recovery_drill.py"]
        scripts_ch_apply_exchange_columns_py["(生产态 / production) ClickHouse exchange+symbol_canonical 列部署脚本...<br/>文件: apply_exchange_columns.py"]
        scripts_ch_apply_fundamental_tables_ddl_py["(生产态 / production) ClickHouse c3_fundamental 财务三表 DDL 部署 + ...<br/>文件: apply_fundamental_tables_ddl.py"]
        scripts_ch_apply_market_tables_ddl_py["(生产态 / production) ClickHouse c1_market 建表 DDL 部署 + 引擎验证脚...<br/>文件: apply_market_tables_ddl.py"]
        scripts_ch_apply_rbac_py["(生产态 / production) ClickHouse RBAC 账号分级部署 + 验证脚本（audit ...<br/>文件: apply_rbac.py"]
        scripts_ch_apply_timezone_migration_py["(生产态 / production) ClickHouse 时区防线迁移脚本（audit A组 Schema ...<br/>文件: apply_timezone_migration.py"]
        scripts_ch_lint_symbol_convention_py["(生产态 / production) Symbol 约定 lint 门禁（TRAE-082 GATE-SYMBOL-CON...<br/>文件: lint_symbol_convention.py"]
        scripts_ch_verify_exchange_coverage_py["(生产态 / production) exchange+symbol_canonical 数据覆盖率校验器（TRA...<br/>文件: verify_exchange_coverage.py"]
        scripts_ch_verify_schema_truth_py["(生产态 / production) DDL-as-Code 真源 vs ClickHouse 实际表结构 漂移...<br/>文件: verify_schema_truth.py"]
        scripts_ops_verify_alert_channels_py["(生产态 / production) 告警通道端到端验证（B2，#ARCH-CH-023，2026-07-2...<br/>文件: verify_alert_channels.py"]
        scripts_register_aux_tasks_ps1["(生产态 / production) register_aux_tasks.ps1"]
        scripts_register_guard_tasks_ps1["(生产态 / production) register_guard_tasks.ps1"]
        scripts_start_scheduler_ps1["(生产态 / production) start_scheduler.ps1"]
        scripts_start_tick_subscriber_ps1["(生产态 / production) start_tick_subscriber.ps1"]
        src_zephyr_data_init_py["(生产态 / production) zephyr.data — 数据源集成器（MOD-L00-004）。<br/>文件: __init__.py"]
        src_zephyr_data_main_py["(生产态 / production) python -m zephyr.data — 数据源集成器 CLI 入口。<br/>文件: __main__.py"]
        src_zephyr_data_alerter_py["(生产态 / production) 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §...<br/>文件: alerter.py"]
        src_zephyr_data_backfill_checker_py["(生产态 / production) L10 周末补下载检测器——检测过去N天缺失数据并精...<br/>文件: backfill_checker.py"]
        src_zephyr_data_buffered_writer_py["(生产态 / production) 批量聚合写入器（MOD-L00-004 §18.3 裁定...<br/>文件: buffered_writer.py"]
        src_zephyr_data_capability_validator_py["(生产态 / production) Provider Capability 行为契约校验器（裁定...<br/>文件: capability_validator.py"]
        src_zephyr_data_ch_config_py["(生产态 / production) ClickHouse 连接配置单真源加载器（裁定...<br/>文件: ch_config.py"]
        src_zephyr_data_ch_reader_py["(生产态 / production) ClickHouse 统一读取层（裁定 #ARCH-CH-007）。<br/>文件: ch_reader.py"]
        src_zephyr_data_ch_writer_py["(生产态 / production) ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6...<br/>文件: ch_writer.py"]
        src_zephyr_data_cli_py["(生产态 / production) 数据源集成器 CLI（MOD-L00-004 §8.4）。<br/>文件: cli.py"]
        src_zephyr_data_config_policies_yaml["(生产态 / production) policies.yaml"]
        src_zephyr_data_config_schedule_yaml["(生产态 / production) schedule.yaml"]
        src_zephyr_data_config_tasks_yaml["(生产态 / production) tasks.yaml"]
        src_zephyr_data_cross_source_validator_py["(生产态 / production) 多源交叉校验器——比较 QMT 主源与 TDX 备源 tick...<br/>文件: cross_source_validator.py"]
        src_zephyr_data_error_classifier_py["(生产态 / production) 数据源错误分类器——根据错误字符串判断可恢复性。<br/>文件: error_classifier.py"]
        src_zephyr_data_implementations_init_py["(生产态 / production) 数据源 Provider 实现集合（MOD-L00-004 §4.3）。<br/>文件: __init__.py"]
        src_zephyr_data_implementations_akshare_provider_py["(生产态 / production) AKShare 数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>文件: akshare_provider.py"]
        src_zephyr_data_implementations_baostock_provider_py["(生产态 / production) Baostock 数据源 Provider 实现（MOD-L00-004 §4....<br/>文件: baostock_provider.py"]
        src_zephyr_data_implementations_cls_provider_py["(生产态 / production) 财联社电报数据源 Provider 实现（MOD-L00-004 §4...<br/>文件: cls_provider.py"]
        src_zephyr_data_implementations_eastmoney_news_provider_py["(生产态 / production) 东方财富新闻数据源 Provider 实现（MOD-L00-004 ...<br/>文件: eastmoney_news_provider.py"]
        src_zephyr_data_implementations_ifind_provider_py["(生产态 / production) IFindProvider 实现（MOD-L00-004 §4.3 数据源集...<br/>文件: ifind_provider.py"]
        src_zephyr_data_implementations_miniqmt_provider_py["(生产态 / production) MOD-L00-004 数据源集成器 · MiniQmtIngestProvid...<br/>文件: miniqmt_provider.py"]
        src_zephyr_data_implementations_rss_provider_py["(生产态 / production) RSS 财经新闻数据源 Provider 实现（MOD-L00-004 ...<br/>文件: rss_provider.py"]
        src_zephyr_data_implementations_tdx_provider_py["(生产态 / production) 通达信数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>文件: tdx_provider.py"]
        src_zephyr_data_implementations_tickflow_provider_py["(生产态 / production) TickFlow 数据源 Provider 实现（MOD-L00-004 §4....<br/>文件: tickflow_provider.py"]
        src_zephyr_data_implementations_tqcenter_provider_py["(生产态 / production) tqcenter 数据源 Provider 实现。<br/>文件: tqcenter_provider.py"]
        src_zephyr_data_implementations_tushare_provider_py["(生产态 / production) Tushare 数据源 Provider 实现（MOD-L00-004 §4.3）。<br/>文件: tushare_provider.py"]
        src_zephyr_data_integrity_checker_py["(生产态 / production) 数据完整性巡检器——每天盘后检测全表当日数据是...<br/>文件: integrity_checker.py"]
        src_zephyr_data_kline_resampler_py["(生产态 / production) 880xxx 板块K线合成器——从 1m/5m 合成 15m/30m/6...<br/>文件: kline_resampler.py"]
        src_zephyr_data_local_replay_py["(生产态 / production) 本地落盘兜底 + 自动回灌（裁定 #ARCH-CH-013 Phas...<br/>文件: local_replay.py"]
        src_zephyr_data_metrics_py["(生产态 / production) 可观测性指标采集（MOD-L00-004 §11）。<br/>文件: metrics.py"]
        src_zephyr_data_news_dedup_py["(生产态 / production) 新闻数据去重模块（MOD-L00-004 §4.3）。<br/>文件: news_dedup.py"]
        src_zephyr_data_pit_query_py["(生产态 / production) 财报 Point-In-Time (PIT) 查询能力（#ARCH-CH-021...<br/>文件: pit_query.py"]
        src_zephyr_data_policy_registry_py["(生产态 / production) per-source 调用策略注册表（MOD-L00-004 §5）。<br/>文件: policy_registry.py"]
        src_zephyr_data_progress_store_py["(生产态 / production) 统一进度存储（MOD-L00-004 §7）。<br/>文件: progress_store.py"]
        src_zephyr_data_provider_base_py["(生产态 / production) 数据源 Provider 抽象基类（MOD-L00-004 §4）。<br/>文件: provider_base.py"]
        src_zephyr_data_quality_gate_py["(生产态 / production) Re-export wrapper: QualityReport 真源在 zephyr....<br/>文件: quality_gate.py"]
        src_zephyr_data_redundant_source_init_py["(生产态 / production) 数据源冗余与热切换模块（MOD-L00-005）。<br/>文件: __init__.py"]
        src_zephyr_data_satellite_geospatial_engine_init_py["(生产态 / production) D_DATA Data Source<br/>文件: __init__.py"]
        src_zephyr_data_scheduler_py["(生产态 / production) 数据源调度编排层（MOD-L00-004 §6）。<br/>文件: scheduler.py"]
        src_zephyr_data_sector_kline_downloader_py["(生产态 / production) 880xxx 板块指数K线下载器——盘后从 tqcenter 下...<br/>文件: sector_kline_downloader.py"]
        src_zephyr_data_sector_ranking_engine_py["(生产态 / production) 880xxx 板块动态排名引擎——5因子复合排名调整99...<br/>文件: sector_ranking_engine.py"]
        src_zephyr_data_sector_snapshot_collector_py["(生产态 / production) 880xxx 板块实时快照采集器（tqcenter → ClickHou...<br/>文件: sector_snapshot_collector.py"]
        src_zephyr_data_speed_tester_py["(生产态 / production) 数据源测速器（MOD-L00-004 §8.5）。<br/>文件: speed_tester.py"]
        src_zephyr_data_symbol_normalizer_init_py["(生产态 / production) Symbol 标准化模块——TRAE-082 symbol 约定铁律的...<br/>文件: __init__.py"]
        src_zephyr_data_symbol_normalizer_normalizer_py["(生产态 / production) symbol 标准化核心实现——TRAE-082 symbol 约定铁律。<br/>文件: normalizer.py"]
        src_zephyr_data_table_registry_py["(生产态 / production) 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ...<br/>文件: table_registry.py"]
        src_zephyr_data_task_queue_py["(生产态 / production) 任务依赖图 + 优先级队列（MOD-L00-004 §6.3 任务...<br/>文件: task_queue.py"]
        src_zephyr_data_tick_subscriber_py["(生产态 / production) QMT 实时 Tick 订阅服务——subscribe_quote 实时...<br/>文件: tick_subscriber.py"]
        src_zephyr_data_trading_calendar_py["(生产态 / production) A 股交易日历守卫（MOD-L00-004）。<br/>文件: trading_calendar.py"]
        src_zephyr_data_wal_codec_init_py["(生产态 / production) WAL 段编解码模块（MOD-L00-006）。<br/>文件: __init__.py"]
        src_zephyr_data_wal_writer_py["(生产态 / production) 主动 WAL 写入器（P0-1 Phase A）。<br/>文件: wal_writer.py"]
        tests_data_test_market_quality_validator_py["(生产态 / production) #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测...<br/>文件: test_market_quality_validator.py"]
        tests_data_test_pit_query_py["(生产态 / production) #ARCH-CH-021 P0-5: 财报 PIT 查询能力测试。<br/>文件: test_pit_query.py"]
        tests_zephyr_data_test_cross_source_validator_py["(生产态 / production) cross_source_validator 单元测试（P1-4 多源交叉...<br/>文件: test_cross_source_validator.py"]
        tests_zephyr_data_test_tick_subscriber_py["(生产态 / production) tick_subscriber 单元测试（含 Phase C: WalWriter...<br/>文件: test_tick_subscriber.py"]
    end
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_ch_reader_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_tick_subscriber_py
    src_zephyr_data_backfill_checker_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_buffered_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_buffered_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_capability_validator_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_backfill_checker_py
    src_zephyr_data_integrity_checker_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| src_zephyr_data_quality_gate_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_progress_store_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_scheduler_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_speed_tester_py
    src_zephyr_data_cli_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_cross_source_validator_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_local_replay_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_kline_resampler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_news_dedup_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_pit_query_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_provider_base_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_backfill_checker_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_buffered_writer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_capability_validator_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_integrity_checker_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_error_classifier_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_metrics_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_progress_store_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_trading_calendar_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_task_queue_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_ifind_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tqcenter_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_scheduler_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_sector_kline_downloader_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_baostock_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_eastmoney_news_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_cls_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tdx_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_rss_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_ifind_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tickflow_provider_py
    src_zephyr_data_speed_tester_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_tushare_provider_py
    src_zephyr_data_sector_snapshot_collector_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_sector_snapshot_collector_py -->|导入依赖 / import_depends| src_zephyr_data_sector_ranking_engine_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_local_replay_py
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| src_zephyr_data_wal_writer_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_init_py -->|导入依赖 / import_depends| src_zephyr_data_scheduler_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_baostock_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_main_py -->|导入依赖 / import_depends| src_zephyr_data_cli_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_eastmoney_news_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tdx_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_akshare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_ifind_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_ifind_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_ifind_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_ifind_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_ifind_provider_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_miniqmt_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tqcenter_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tickflow_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_news_dedup_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_policy_registry_py
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_akshare_provider_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_ifind_provider_py
    src_zephyr_data_implementations_init_py -->|导入依赖 / import_depends| src_zephyr_data_implementations_miniqmt_provider_py
    src_zephyr_data_satellite_geospatial_engine_init_py -->|导入依赖 / import_depends| src_zephyr_data_provider_base_py
    src_zephyr_data_symbol_normalizer_init_py -->|导入依赖 / import_depends| src_zephyr_data_symbol_normalizer_normalizer_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_apply_exchange_columns_py -->|导入依赖 / import_depends| src_zephyr_data_symbol_normalizer_normalizer_py
    scripts_ch_lint_symbol_convention_py -->|config_depends / config_depends| scripts_ch_apply_exchange_columns_py
    scripts_ch_apply_rbac_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_market_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_apply_timezone_migration_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_apply_fundamental_tables_ddl_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_verify_schema_truth_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| src_zephyr_data_init_py
    scripts_ch_verify_exchange_coverage_py -->|导入依赖 / import_depends| scripts_ch_apply_exchange_columns_py
    scripts_ch_data_inventory_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ch_recovery_drill_py -->|导入依赖 / import_depends| src_zephyr_data_ch_config_py
    scripts_ops_verify_alert_channels_py -->|导入依赖 / import_depends| src_zephyr_data_alerter_py
    tests_data_test_pit_query_py -->|测试依赖 / test_depends| src_zephyr_data_pit_query_py
    tests_data_test_pit_query_py -->|测试依赖 / test_depends| src_zephyr_data_init_py
    tests_zephyr_data_test_cross_source_validator_py -->|测试依赖 / test_depends| src_zephyr_data_cross_source_validator_py
    tests_zephyr_data_test_tick_subscriber_py -->|测试依赖 / test_depends| src_zephyr_data_tick_subscriber_py
    schemas_categories_fundamental_analyst_forecast_py -->|config_depends / config_depends| schemas_categories_cross_validation_log_py
    schemas_categories_fundamental_equity_pledge_detail_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_balance_sheet_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_cashflow_statement_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_income_statement_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_disclosure_plan_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_industry_class_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_rights_issue_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_restricted_shares_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_industry_class_suppl_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_macro_macro_data_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_share_change_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_adj_factor_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_macro_edb_data_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_fundamental_share_unlock_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_auction_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_block_trade_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_auction_book_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_block_trade_detail_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_concept_board_constituent_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_concept_sector_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_cb_iv_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_concept_board_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_convertible_bond_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_dragon_tiger_seat_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_dragon_tiger_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_daily_valuation_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_futures_kline_qmt_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_etf_benchmark_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_etf_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_etf_nav_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_hk_connect_flow_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_hk_kline_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_hk_stock_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_futures_position_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_hk_trade_calendar_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_futures_term_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_index_constituent_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_index_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_index_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_index_meta_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_15min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_index_weight_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_60min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_1min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_5min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_30min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_cb_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_daily_hfq_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_etf_5min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_etf_15min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_daily_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_etf_30min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_etf_60min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_futures_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_etf_1min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_lof_30min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_lof_15min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_index_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_hk_daily_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_lof_1min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_sector_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_monthly_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_lof_5min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_lof_60min_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_monthly_hfq_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_us_daily_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_sector_880_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_sector_intraday_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_weekly_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_l2_tick_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_limit_up_down_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_kline_weekly_hfq_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_margin_trading_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_lof_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_money_flow_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_option_greeks_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_option_kline_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_sector_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_realtime_snapshot_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_option_iv_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_stock_indicator_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_sector_constituent_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_st_stock_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_trade_calendar_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_sector_meta_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_stock_list_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_tick_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_sector_snapshot_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    schemas_categories_market_us_index_py -->|config_depends / config_depends| schemas_categories_fundamental_analyst_forecast_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_data_implementations_tushare_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_ch_config_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_progress_store_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_rss_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["(生产态 / production) D_GOV_ENFORCEMENT"]
    tests_data_test_market_quality_validator_py -->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    src_zephyr_data_wal_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_ch_writer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_table_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_quality_gate_py -->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    src_zephyr_data_alerter_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_tick_subscriber_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_local_replay_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_implementations_cls_provider_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_data_ch_config_py -->|导入依赖 / import_depends| D_SHARED
    D_FACTOR["(设计态 / design) D_FACTOR"]
    D_FACTOR -.->|导入依赖 / import_depends| src_zephyr_data_ch_writer_py
    D_GOV_CODE_QUALITY["(生产态 / production) D_GOV_CODE_QUALITY"]
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_data_capability_validator_py
    D_GOV_CODE_QUALITY -->|测试依赖 / test_depends| src_zephyr_data_symbol_normalizer_init_py
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_MKT_DATA["(生产态 / production) D_MKT_DATA"]
    D_MKT_DATA -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_GOV_SCRIPTS["(生产态 / production) D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_MKT_DATA -->|导入依赖 / import_depends| src_zephyr_data_init_py
    D_MKT_DATA -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    D_GOV_SCRIPTS -->|导入依赖 / import_depends| src_zephyr_data_ch_reader_py
    D_FACTOR -->|导入依赖 / import_depends| src_zephyr_data_table_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_cross_validation_log_py,schemas_categories_fundamental_analyst_forecast_py,schemas_categories_fundamental_balance_sheet_py,schemas_categories_fundamental_cashflow_statement_py,schemas_categories_fundamental_disclosure_plan_py,schemas_categories_fundamental_equity_pledge_detail_py,schemas_categories_fundamental_income_statement_py,schemas_categories_fundamental_industry_class_py,schemas_categories_fundamental_industry_class_suppl_py,schemas_categories_fundamental_restricted_shares_py,schemas_categories_fundamental_rights_issue_py,schemas_categories_fundamental_share_change_py,schemas_categories_fundamental_share_unlock_py,schemas_categories_macro_edb_data_py,schemas_categories_macro_macro_data_py,schemas_categories_market_adj_factor_py,schemas_categories_market_auction_py,schemas_categories_market_auction_book_py,schemas_categories_market_block_trade_py,schemas_categories_market_block_trade_detail_py,schemas_categories_market_cb_iv_py,schemas_categories_market_concept_board_py,schemas_categories_market_concept_board_constituent_py,schemas_categories_market_concept_sector_py,schemas_categories_market_convertible_bond_list_py,schemas_categories_market_daily_valuation_py,schemas_categories_market_dragon_tiger_py,schemas_categories_market_dragon_tiger_seat_py,schemas_categories_market_etf_benchmark_py,schemas_categories_market_etf_list_py,schemas_categories_market_etf_nav_py,schemas_categories_market_futures_kline_qmt_py,schemas_categories_market_futures_position_py,schemas_categories_market_futures_term_py,schemas_categories_market_hk_connect_flow_py,schemas_categories_market_hk_kline_py,schemas_categories_market_hk_stock_list_py,schemas_categories_market_hk_trade_calendar_py,schemas_categories_market_index_py,schemas_categories_market_index_constituent_py,schemas_categories_market_index_list_py,schemas_categories_market_index_meta_py,schemas_categories_market_index_weight_py,schemas_categories_market_kline_15min_py,schemas_categories_market_kline_1min_py,schemas_categories_market_kline_30min_py,schemas_categories_market_kline_5min_py,schemas_categories_market_kline_60min_py,schemas_categories_market_kline_cb_py,schemas_categories_market_kline_daily_py,schemas_categories_market_kline_daily_hfq_py,schemas_categories_market_kline_etf_15min_py,schemas_categories_market_kline_etf_1min_py,schemas_categories_market_kline_etf_30min_py,schemas_categories_market_kline_etf_5min_py,schemas_categories_market_kline_etf_60min_py,schemas_categories_market_kline_futures_py,schemas_categories_market_kline_hk_daily_py,schemas_categories_market_kline_index_py,schemas_categories_market_kline_lof_15min_py,schemas_categories_market_kline_lof_1min_py,schemas_categories_market_kline_lof_30min_py,schemas_categories_market_kline_lof_5min_py,schemas_categories_market_kline_lof_60min_py,schemas_categories_market_kline_monthly_py,schemas_categories_market_kline_monthly_hfq_py,schemas_categories_market_kline_sector_py,schemas_categories_market_kline_sector_880_py,schemas_categories_market_kline_sector_intraday_py,schemas_categories_market_kline_us_daily_py,schemas_categories_market_kline_weekly_py,schemas_categories_market_kline_weekly_hfq_py,schemas_categories_market_l2_tick_py,schemas_categories_market_limit_up_down_py,schemas_categories_market_lof_list_py,schemas_categories_market_margin_trading_py,schemas_categories_market_money_flow_py,schemas_categories_market_option_greeks_py,schemas_categories_market_option_iv_py,schemas_categories_market_option_kline_py,schemas_categories_market_realtime_snapshot_py,schemas_categories_market_sector_constituent_py,schemas_categories_market_sector_list_py,schemas_categories_market_sector_meta_py,schemas_categories_market_sector_snapshot_py,schemas_categories_market_st_stock_list_py,schemas_categories_market_stock_indicator_py,schemas_categories_market_stock_list_py,schemas_categories_market_tick_py,schemas_categories_market_trade_calendar_py,schemas_categories_market_us_index_py,scripts_ch_data_inventory_py,scripts_ch_recovery_drill_py,scripts_ch_apply_exchange_columns_py,scripts_ch_apply_fundamental_tables_ddl_py,scripts_ch_apply_market_tables_ddl_py,scripts_ch_apply_rbac_py,scripts_ch_apply_timezone_migration_py,scripts_ch_lint_symbol_convention_py,scripts_ch_verify_exchange_coverage_py,scripts_ch_verify_schema_truth_py,scripts_ops_verify_alert_channels_py,scripts_register_aux_tasks_ps1,scripts_register_guard_tasks_ps1,scripts_start_scheduler_ps1,scripts_start_tick_subscriber_ps1,src_zephyr_data_init_py,src_zephyr_data_main_py,src_zephyr_data_alerter_py,src_zephyr_data_backfill_checker_py,src_zephyr_data_buffered_writer_py,src_zephyr_data_capability_validator_py,src_zephyr_data_ch_config_py,src_zephyr_data_ch_reader_py,src_zephyr_data_ch_writer_py,src_zephyr_data_cli_py,src_zephyr_data_config_policies_yaml,src_zephyr_data_config_schedule_yaml,src_zephyr_data_config_tasks_yaml,src_zephyr_data_cross_source_validator_py,src_zephyr_data_error_classifier_py,src_zephyr_data_implementations_init_py,src_zephyr_data_implementations_akshare_provider_py,src_zephyr_data_implementations_baostock_provider_py,src_zephyr_data_implementations_cls_provider_py,src_zephyr_data_implementations_eastmoney_news_provider_py,src_zephyr_data_implementations_ifind_provider_py,src_zephyr_data_implementations_miniqmt_provider_py,src_zephyr_data_implementations_rss_provider_py,src_zephyr_data_implementations_tdx_provider_py,src_zephyr_data_implementations_tickflow_provider_py,src_zephyr_data_implementations_tqcenter_provider_py,src_zephyr_data_implementations_tushare_provider_py,src_zephyr_data_integrity_checker_py,src_zephyr_data_kline_resampler_py,src_zephyr_data_local_replay_py,src_zephyr_data_metrics_py,src_zephyr_data_news_dedup_py,src_zephyr_data_pit_query_py,src_zephyr_data_policy_registry_py,src_zephyr_data_progress_store_py,src_zephyr_data_provider_base_py,src_zephyr_data_quality_gate_py,src_zephyr_data_redundant_source_init_py,src_zephyr_data_satellite_geospatial_engine_init_py,src_zephyr_data_scheduler_py,src_zephyr_data_sector_kline_downloader_py,src_zephyr_data_sector_ranking_engine_py,src_zephyr_data_sector_snapshot_collector_py,src_zephyr_data_speed_tester_py,src_zephyr_data_symbol_normalizer_init_py,src_zephyr_data_symbol_normalizer_normalizer_py,src_zephyr_data_table_registry_py,src_zephyr_data_task_queue_py,src_zephyr_data_tick_subscriber_py,src_zephyr_data_trading_calendar_py,src_zephyr_data_wal_codec_init_py,src_zephyr_data_wal_writer_py,tests_data_test_market_quality_validator_py,tests_data_test_pit_query_py,tests_zephyr_data_test_cross_source_validator_py,tests_zephyr_data_test_tick_subscriber_py production
    class D_SHARED,D_GOV_ENFORCEMENT,D_GOV_CODE_QUALITY,D_MKT_DATA,D_GOV_SCRIPTS external_prod
    class D_FACTOR external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 6 个，1 条域内依赖）。

```mermaid
graph TD
    subgraph D_DATA["D_DATA 数据接入层"]
        schemas_categories_market_hog_futures_core_py["(设计态 / design) hog_futures_core 表 DDL-as-Code（category_id: m...<br/>文件: market_hog_futures_core.py"]
        schemas_categories_market_hog_province_spot_py["(设计态 / design) hog_province_spot 表 DDL-as-Code（category_id: ...<br/>文件: market_hog_province_spot.py"]
        schemas_categories_market_hog_spot_index_py["(设计态 / design) hog_spot_index 表 DDL-as-Code（category_id: mar...<br/>文件: market_hog_spot_index.py"]
        schemas_categories_market_kline_etf_daily_py["(设计态 / design) kline_etf_daily 表 DDL-as-Code（category_id: ma...<br/>文件: market_kline_etf_daily.py"]
        src_zephyr_data_pit_query_py["(设计态 / design) "]
        src_zephyr_data_symbol_normalizer["(设计态 / design) "]
    end
    src_zephyr_data_symbol_normalizer -.->|import / import| schemas_categories_market_kline_etf_daily_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class schemas_categories_market_hog_futures_core_py,schemas_categories_market_hog_province_spot_py,schemas_categories_market_hog_spot_index_py,schemas_categories_market_kline_etf_daily_py,src_zephyr_data_pit_query_py,src_zephyr_data_symbol_normalizer design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | Re-export wrapper: QualityReport 真源在 zephyr.... | → | D_GOV_ENFORCEMENT 规则执行: D_DATA — Data Quality Gate (quality_gate.py) | 导入依赖 / import_depends |
| 2 | D_DATA Data Source (__init__.py) | → | D_GOV_ENFORCEMENT 规则执行: D_DATA — Data Quality Gate (quality_gate.py) | 导入依赖 / import_depends |
| 3 | #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测... | → | D_GOV_ENFORCEMENT 规则执行: D_DATA — Data Quality Gate (quality_gate.py) | 测试依赖 / test_depends |
| 4 | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 5 | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 6 | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 7 | ClickHouse 连接配置单真源加载器（裁定... (ch_co... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 8 | ClickHouse 连接配置单真源加载器（裁定... (ch_co... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 9 | ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6.... | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 导入依赖 / import_depends |
| 10 | 财联社电报数据源 Provider 实现（MOD-L00-004 §4... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 11 | RSS 财经新闻数据源 Provider 实现（MOD-L00-004 .... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 12 | Tushare 数据源 Provider 实现（MOD-L00-004 §4.3... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 13 | 本地落盘兜底 + 自动回灌（裁定 #ARCH-CH-013 Phas... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 14 | 可观测性指标采集（MOD-L00-004 §11）。 (metrics.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 15 | 统一进度存储（MOD-L00-004 §7）。 (progress_sto... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 16 | 统一进度存储（MOD-L00-004 §7）。 (progress_sto... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 17 | 数据源调度编排层（MOD-L00-004 §6）。 (schedule... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 18 | 数据源测速器（MOD-L00-004 §8.5）。 (speed_test... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 19 | 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 20 | QMT 实时 Tick 订阅服务——subscribe_quote 实时.... | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 导入依赖 / import_depends |
| 21 | QMT 实时 Tick 订阅服务——subscribe_quote 实时.... | → | D_SHARED 共享服务: Prometheus /metrics HTTP 端点（P1-5 可观测性改.... | 导入依赖 / import_depends |
| 22 | 主动 WAL 写入器（P0-1 Phase A）。 (wal_writer.py) | → | D_SHARED 共享服务: metrics.py —— 轻量级 Metrics 收集基础设施（Ph... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_BACKTEST 回测: 回测数据处理器模块（v1.1.0 扩展：多源化 + Click... | → | zephyr.data — 数据源集成器（MOD-L00-004）。 (_... | 导入依赖 / import_depends |
| 2 | D_BACKTEST 回测: 回测数据处理器模块（v1.1.0 扩展：多源化 + Click... | → | ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 (c... | 导入依赖 / import_depends |
| 3 | D_FACTOR 因子: D_FACTOR core batch_output.buffer——FactorSign... | → | ClickHouse 写入器（MOD-L00-004 §3.2 数据流第6.... | 导入依赖 / import_depends |
| 4 | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评... | → | zephyr.data — 数据源集成器（MOD-L00-004）。 (_... | 导入依赖 / import_depends |
| 5 | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评... | → | ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 (c... | 导入依赖 / import_depends |
| 6 | D_FACTOR 因子: D-FACTOR-03 因子评估回测运行器——端到端因子评... | → | 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | 导入依赖 / import_depends |
| 7 | D_GOVERNANCE 生命周期管理: C-track 端到端演示 —— 全流水线一次性运行 (dem... | → | zephyr.data — 数据源集成器（MOD-L00-004）。 (_... | 导入依赖 / import_depends |
| 8 | D_GOVERNANCE 生命周期管理: D_DATA — Memory Provider (memory_provider.py) | → | per-source 调用策略注册表（MOD-L00-004 §5）。 ... | 导入依赖 / import_depends |
| 9 | D_GOVERNANCE 生命周期管理: D_DATA — Memory Provider (memory_provider.py) | → | 数据源 Provider 抽象基类（MOD-L00-004 §4）。 (... | 导入依赖 / import_depends |
| 10 | D_GOV_CODE_QUALITY 代码质量治理: capability_consistency_gate.py — Provider 路由... | → | Provider Capability 行为契约校验器（裁定... (ca... | 导入依赖 / import_depends |
| 11 | D_GOV_CODE_QUALITY 代码质量治理: table_name_registry_gate.py — TABLE-NAME-REGIS... | → | 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | 导入依赖 / import_depends |
| 12 | D_GOV_CODE_QUALITY 代码质量治理: test_symbol_normalizer.py — TRAE-082 symbol 标... | → | Symbol 标准化模块——TRAE-082 symbol 约定铁律的... | 测试依赖 / test_depends |
| 13 | D_GOV_SCRIPTS 脚本治理: Code Wiki 统计数据生成器（半自动维护机制）。 (g... | → | 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | 导入依赖 / import_depends |
| 14 | D_GOV_SCRIPTS 脚本治理: G-inventory: 扫描 ClickHouse 生成业务数据清单 M... | → | zephyr.data — 数据源集成器（MOD-L00-004）。 (_... | 导入依赖 / import_depends |
| 15 | D_GOV_SCRIPTS 脚本治理: G-inventory: 扫描 ClickHouse 生成业务数据清单 M... | → | ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 (c... | 导入依赖 / import_depends |
| 16 | D_GOV_SCRIPTS 脚本治理: tick_data 表真重复检查工具（RULE-DATA-OPS 配套.... | → | zephyr.data — 数据源集成器（MOD-L00-004）。 (_... | 导入依赖 / import_depends |
| 17 | D_GOV_SCRIPTS 脚本治理: tick_data 表真重复检查工具（RULE-DATA-OPS 配套.... | → | ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 (c... | 导入依赖 / import_depends |
| 18 | D_INFRA_RUNTIME 运行时集成: DatabaseService: 统一管理数据库的连接池、生命周... | → | ClickHouse 连接配置单真源加载器（裁定... (ch_co... | 导入依赖 / import_depends |
| 19 | D_MKT_DATA 行情数据: NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | → | zephyr.data — 数据源集成器（MOD-L00-004）。 (_... | 导入依赖 / import_depends |
| 20 | D_MKT_DATA 行情数据: NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | → | ClickHouse 统一读取层（裁定 #ARCH-CH-007）。 (c... | 导入依赖 / import_depends |
| 21 | D_MKT_DATA 行情数据: NormalizedMarketData 生产者——D_MKT_DATA→D_FA... | → | 表名/品类注册表消费层（裁定 #ARCH-CH-024 Phase ... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 11 个外部域直接连接（出边 22 条 + 入边 27 条 = 49 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_DATA["D_DATA<br/>数据接入层"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_MKT_DATA["D_MKT_DATA<br/>行情数据"]
    D_FACTOR["D_FACTOR<br/>因子"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_ML_TRAIN["D_ML_TRAIN<br/>训练"]
    D_DATA_ENG["D_DATA_ENG<br/>数据工程"]
    D_BACKTEST["D_BACKTEST<br/>回测"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_DATA -->|19条 导入依赖 / import_depends| D_SHARED
    D_DATA -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOV_SCRIPTS -->|5条 导入依赖 / import_depends| D_DATA
    D_MKT_DATA -->|5条 data / data, 导入依赖 / import_depends, runtime / runtime| D_DATA
    D_FACTOR -->|4条 导入依赖 / import_depends| D_DATA
    D_GOVERNANCE -->|3条 导入依赖 / import_depends| D_DATA
    D_GOV_CODE_QUALITY -->|3条 导入依赖 / import_depends, 测试依赖 / test_depends| D_DATA
    D_ML_TRAIN -->|2条 data / data| D_DATA
    D_DATA_ENG -->|2条 import / import| D_DATA
    D_BACKTEST -->|2条 导入依赖 / import_depends| D_DATA
    D_INFRA_RUNTIME -->|1条 导入依赖 / import_depends| D_DATA
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
