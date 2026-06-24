---
doc_type: domain_architecture_diagram
title: D-MKT_DATA 行情数据架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 08_d_mkt_data / 行情数据 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示行情数据（D-MKT_DATA）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 行情数据（D-MKT_DATA）的模块分布。共 266 个模块 / 266 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (3 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/market_data/market_data.py  [prototype]             │
│   src/zephyr/market_data/market_data_pipeline.py  [prototype]    │
│   Trading Calendar Engine  [design]                              │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/market_data/__init__.py  [production]               │
│   src/zephyr/market_data/_extensions/__init__.py  [scaffold_p... │
│   src/zephyr/market_data/api/__init__.py  [scaffold_placeholder] │
│   src/zephyr/market_data/core/__init__.py  [scaffold_placehol... │
│   src/zephyr/market_data/infrastructure/__init__.py  [scaffol... │
│   src/zephyr/market_data/models/__init__.py  [scaffold_placeh... │
│   src/zephyr/market_data/services/__init__.py  [scaffold_plac... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (256 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   4元组数据映射模型 4-tuple Data Mapping  [design]               │
│   A-Share Alt-Data Source Manager 管理器  [design]               │
│   A-Share Auction Data Manager 管理器  [design]                  │
│   A-Share Intraday Data Manager 管理器  [design]                 │
│   A-Share Order Flow Data Manager 管理器订单  [design]           │
│   A-Share Special A股特色  [design]                              │
│   A3 Data Architecture A3数据架构  [design]                      │
│   ADR记录架构决策 ADR Records  [design]                          │
│   AI驱动异常检测 AI Anomaly Detection  [design]                  │
│   AS OF JOIN实现 AS OF JOIN Implementation  [design]             │
│   AUM>200万后升级ClickHouse ClickHouse Upgrade Gate  [design]    │
│   AUM驱动存储升级 AUM-driven Storage Upgrade  [design]           │
│   AkShare AkShare数据适配器  [design]                            │
│   AkShare Data Source Adapter 适配器  [design]                   │
│   AkShare 免费备用数据源  [design]                               │
│   Apache Doris 4.x量化交易 Apache Doris 4.x  [design]            │
│   AuctionUpdate 集合竞价更新事件  [design]                       │
│   Auto Data Source Switch 数据源自动切换  [design]               │
│   ...还有 238 个模块 / 238 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 266 个模块 / 266 modules）。

### L1 基础层 / Foundation Layer (3 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/market_data/market_data.py | src/zephyr/market_data/market_data.py | prototype | draft |
| 2 | src/zephyr/market_data/market_data_pipeline.py | src/zephyr/market_data/market_data_pi... | prototype | draft |
| 3 | 交易日历引擎(交易所日历/假日管理/T+N计算)/D-TRADING-07 | Trading Calendar Engine | design | design_only |

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/market_data/__init__.py | src/zephyr/market_data/__init__.py | production | draft |
| 2 | src/zephyr/market_data/_extensions/__init__.py | src/zephyr/market_data/_extensions/__... | scaffold_placeholder | orphan |
| 3 | src/zephyr/market_data/api/__init__.py | src/zephyr/market_data/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/market_data/core/__init__.py | src/zephyr/market_data/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/market_data/infrastructure/__init__.py | src/zephyr/market_data/infrastructure... | scaffold_placeholder | orphan |
| 6 | src/zephyr/market_data/models/__init__.py | src/zephyr/market_data/models/__init_... | scaffold_placeholder | orphan |
| 7 | src/zephyr/market_data/services/__init__.py | src/zephyr/market_data/services/__ini... | scaffold_placeholder | orphan |

### 未分类 / Unclassified (256 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-MKT-DATA/4元组数据映射模型 4-tuple Data Mapping | 4元组数据映射模型 4-tuple Data Mapping | design | design_only |
| 2 | D-MKT-DATA/A-Share Alt-Data Source Manager 管理器 | A-Share Alt-Data Source Manager 管理器 | design | design_only |
| 3 | D-MKT-DATA/A-Share Auction Data Manager 管理器 | A-Share Auction Data Manager 管理器 | design | design_only |
| 4 | D-MKT-DATA/A-Share Intraday Data Manager 管理器 | A-Share Intraday Data Manager 管理器 | design | design_only |
| 5 | D-MKT-DATA/A-Share Order Flow Data Manager 管理器订单 | A-Share Order Flow Data Manager 管理... | design | design_only |
| 6 | D-MKT-DATA/A-Share Special A股特色 | A-Share Special A股特色 | design | design_only |
| 7 | D-MKT-DATA/A3 Data Architecture A3数据架构 | A3 Data Architecture A3数据架构 | design | design_only |
| 8 | D-MKT-DATA/ADR记录架构决策 ADR Records | ADR记录架构决策 ADR Records | design | design_only |
| 9 | D-MKT-DATA/AI驱动异常检测 AI Anomaly Detection | AI驱动异常检测 AI Anomaly Detection | design | design_only |
| 10 | D-MKT-DATA/AS OF JOIN实现 AS OF JOIN Implementation | AS OF JOIN实现 AS OF JOIN Implementation | design | design_only |
| 11 | D-MKT-DATA/AUM>200万后升级ClickHouse ClickHouse Upgrade Gate | AUM>200万后升级ClickHouse ClickHouse ... | design | design_only |
| 12 | D-MKT-DATA/AUM驱动存储升级 AUM-driven Storage Upgrade | AUM驱动存储升级 AUM-driven Storage Up... | design | design_only |
| 13 | D-MKT-DATA/AkShare AkShare数据适配器 | AkShare AkShare数据适配器 | design | design_only |
| 14 | D-MKT-DATA/AkShare Data Source Adapter 适配器 | AkShare Data Source Adapter 适配器 | design | design_only |
| 15 | D-MKT-DATA/AkShare 免费备用数据源 | AkShare 免费备用数据源 | design | design_only |
| 16 | D-MKT-DATA/Apache Doris 4.x量化交易 Apache Doris 4.x | Apache Doris 4.x量化交易 Apache Doris... | design | design_only |
| 17 | D-MKT-DATA/AuctionUpdate 集合竞价更新事件 | AuctionUpdate 集合竞价更新事件 | design | design_only |
| 18 | D-MKT-DATA/Auto Data Source Switch 数据源自动切换 | Auto Data Source Switch 数据源自动切换 | design | design_only |
| 19 | D-MKT-DATA/BCBS 239合规框架 BCBS 239 Framework | BCBS 239合规框架 BCBS 239 Framework | design | design_only |
| 20 | D-MKT-DATA/BaoStock 历史数据补充 | BaoStock 历史数据补充 | design | design_only |
| 21 | D-MKT-DATA/Bi-Temporal Modeling 双时态建模 | Bi-Temporal Modeling 双时态建模 | design | design_only |
| 22 | D-MKT-DATA/Bloomberg PiT经济数据 Bloomberg PiT Economic Data | Bloomberg PiT经济数据 Bloomberg PiT E... | design | design_only |
| 23 | D-MKT-DATA/CQRS Command Query Responsibility Segregation ... | CQRS Command Query Responsibility Seg... | design | design_only |
| 24 | D-MKT-DATA/CQRS分离 CQRS Separation | CQRS分离 CQRS Separation | design | design_only |
| 25 | D-MKT-DATA/CQRS读写分离 CQRS Read-Write Split | CQRS读写分离 CQRS Read-Write Split | design | design_only |
| 26 | D-MKT-DATA/CTR-001 NormalizedMarketData 标准化市场数据 | CTR-001 NormalizedMarketData 标准化市... | design | design_only |
| 27 | D-MKT-DATA/ClickHouse Analyzer ClickHouse分析器 | ClickHouse Analyzer ClickHouse分析器 | design | design_only |
| 28 | D-MKT-DATA/ClickHouse 列存时序数据库 | ClickHouse 列存时序数据库 | design | design_only |
| 29 | D-MKT-DATA/Cold 冷存储层 Parquet on SSD | Cold 冷存储层 Parquet on SSD | design | design_only |
| 30 | D-MKT-DATA/Concept Factor Mapping Engine 概念因子映射引擎 | Concept Factor Mapping Engine 概念因... | design | design_only |
| 31 | D-MKT-DATA/Connector 连接器 | Connector 连接器 | design | design_only |
| 32 | D-MKT-DATA/Corporate Actions Processor 公司行为处理 | Corporate Actions Processor 公司行为处理 | design | design_only |
| 33 | D-MKT-DATA/CrossSourceReconciler 跨源对账器 | CrossSourceReconciler 跨源对账器 | design | design_only |
| 34 | D-MKT-DATA/D-ALT-DATA MVP Downgrade D-ALT-DATA MVP降级 | D-ALT-DATA MVP Downgrade D-ALT-DATA M... | design | design_only |
| 35 | D-MKT-DATA/D-CROSS-ASSET MVP Downgrade D-CROSS-ASSET MVP降级 | D-CROSS-ASSET MVP Downgrade D-CROSS-A... | design | design_only |
| 36 | D-MKT-DATA/D-DATA | D-DATA | design | design_only |
| 37 | D-MKT-DATA/D-DATA-ENG | D-DATA-ENG | design | design_only |
| 38 | D-MKT-DATA/DDD Aggregate Root & Lifecycle DDD聚合根与生命... | DDD Aggregate Root & Lifecycle DDD聚... | design | design_only |
| 39 | D-MKT-DATA/DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | DDD Aggregate Root Lifecycle DDD聚合... | design | design_only |
| 40 | D-MKT-DATA/Data Anomaly Alerter 数据异常告警器 | Data Anomaly Alerter 数据异常告警器 | design | design_only |
| 41 | D-MKT-DATA/Data Contract执行策略 Data Contract Execution ... | Data Contract执行策略 Data Contract E... | design | design_only |
| 42 | D-MKT-DATA/Data Contract规范缺失 Data Contract Gap | Data Contract规范缺失 Data Contract Gap | design | design_only |
| 43 | D-MKT-DATA/Data Cost Tracker 数据成本追踪 | Data Cost Tracker 数据成本追踪 | design | design_only |
| 44 | D-MKT-DATA/Data Ingestion & Management 数据接入与管理 | Data Ingestion & Management 数据接入... | design | design_only |
| 45 | D-MKT-DATA/Data Ingestion Process 数据接入进程 | Data Ingestion Process 数据接入进程 | design | design_only |
| 46 | D-MKT-DATA/Data Isolation Manager 数据隔离管理器 | Data Isolation Manager 数据隔离管理器 | design | design_only |
| 47 | D-MKT-DATA/Data Lakehouse架构 Data Lakehouse | Data Lakehouse架构 Data Lakehouse | design | design_only |
| 48 | D-MKT-DATA/Data Mesh+Lakehouse互补架构 Data Mesh+Lakehous... | Data Mesh+Lakehouse互补架构 Data Mesh... | design | design_only |
| 49 | D-MKT-DATA/Data Mesh架构 Data Mesh | Data Mesh架构 Data Mesh | design | design_only |
| 50 | D-MKT-DATA/Data Observability Engine 可观测性引擎 | Data Observability Engine 可观测性引擎 | design | design_only |
| 51 | D-MKT-DATA/Data Observability 数据可观测性 | Data Observability 数据可观测性 | design | design_only |
| 52 | D-MKT-DATA/Data Observability五维度框架 Data Observabilit... | Data Observability五维度框架 Data Obs... | design | design_only |
| 53 | D-MKT-DATA/Data Permission Manager 管理器 | Data Permission Manager 管理器 | design | design_only |
| 54 | D-MKT-DATA/Data Retention Manager 数据保留策略 | Data Retention Manager 数据保留策略 | design | design_only |
| 55 | D-MKT-DATA/Data Schema Registry 数据Schema注册表 | Data Schema Registry 数据Schema注册表 | design | design_only |
| 56 | D-MKT-DATA/Data Source Health Monitor 数据源健康度监控器 | Data Source Health Monitor 数据源健康... | design | design_only |
| 57 | D-MKT-DATA/Data Source Management 数据源管理 | Data Source Management 数据源管理 | design | design_only |
| 58 | D-MKT-DATA/Data Source Panorama 数据源全景 | Data Source Panorama 数据源全景 | design | design_only |
| 59 | D-MKT-DATA/Data Subscription Manager 数据订阅管理器 | Data Subscription Manager 数据订阅管理器 | design | design_only |
| 60 | D-MKT-DATA/Data Version Manager 数据版本管理 | Data Version Manager 数据版本管理 | design | design_only |
| 61 | D-MKT-DATA/DataGapDetected 数据缺口检测事件 | DataGapDetected 数据缺口检测事件 | design | design_only |
| 62 | D-MKT-DATA/DataSchemaChanged 数据Schema变更 | DataSchemaChanged 数据Schema变更 | design | design_only |
| 63 | D-MKT-DATA/Design Decision Summary 设计决策汇总 | Design Decision Summary 设计决策汇总 | design | design_only |
| 64 | D-MKT-DATA/Dragon-Tiger List 龙虎榜 | Dragon-Tiger List 龙虎榜 | design | design_only |
| 65 | D-MKT-DATA/Dual Temporal Modeling 双时态建模 | Dual Temporal Modeling 双时态建模 | design | design_only |
| 66 | D-MKT-DATA/Dual-Mode Push Architecture 双模式推送架构 | Dual-Mode Push Architecture 双模式推... | design | design_only |
| 67 | D-MKT-DATA/DuckDB AS OF JOIN PIT Query Engine PIT查询引擎 | DuckDB AS OF JOIN PIT Query Engine PI... | design | design_only |
| 68 | D-MKT-DATA/DuckDB QUALIFY ROW_NUMBER()实现PIT DuckDB QUAL... | DuckDB QUALIFY ROW_NUMBER()实现PIT Du... | design | design_only |
| 69 | D-MKT-DATA/DuckDB性能四区间 DuckDB Performance Tiers | DuckDB性能四区间 DuckDB Performance T... | design | design_only |
| 70 | D-MKT-DATA/DuckDB性能校准 DuckDB Performance Calibration | DuckDB性能校准 DuckDB Performance Cal... | design | design_only |
| 71 | D-MKT-DATA/DuckDB替代ClickHouse作为温层 DuckDB over Click... | DuckDB替代ClickHouse作为温层 DuckDB o... | design | design_only |
| 72 | D-MKT-DATA/DuckDB温层替代ClickHouse DuckDB over ClickHouse | DuckDB温层替代ClickHouse DuckDB over ... | design | design_only |
| 73 | D-MKT-DATA/Embargo期 Embargo Period | Embargo期 Embargo Period | design | design_only |
| 74 | D-MKT-DATA/Event Sourcing Architecture 事件溯源架构 | Event Sourcing Architecture 事件溯源架构 | design | design_only |
| 75 | D-MKT-DATA/Event Store 事件存储 | Event Store 事件存储 | design | design_only |
| 76 | D-MKT-DATA/Event Store用Parquet Event Store via Parquet | Event Store用Parquet Event Store via ... | design | design_only |
| 77 | D-MKT-DATA/Event Store设计 Event Store Design | Event Store设计 Event Store Design | design | design_only |
| 78 | D-MKT-DATA/Exchange 交易所 | Exchange 交易所 | design | design_only |
| 79 | D-MKT-DATA/FWT Retrieval Augmented Diffusion FWT检索增强扩散 | FWT Retrieval Augmented Diffusion FWT... | design | design_only |
| 80 | D-MKT-DATA/Financial Knowledge Graph 金融知识图谱 | Financial Knowledge Graph 金融知识图谱 | design | design_only |
| 81 | D-MKT-DATA/Financial Parser 财务报告解析器 | Financial Parser 财务报告解析器 | design | design_only |
| 82 | D-MKT-DATA/Five-Layer Funnel Data Support 五层筛选漏斗数... | Five-Layer Funnel Data Support 五层筛... | design | design_only |
| 83 | D-MKT-DATA/Flink 2.x AI Functions Flink AI Functions Flin... | Flink 2.x AI Functions Flink AI Funct... | design | design_only |
| 84 | D-MKT-DATA/Governance Market Data Isolation 治理行情数据隔离 | Governance Market Data Isolation 治理... | design | design_only |
| 85 | D-MKT-DATA/Great Expectations Governance Great Expectatio... | Great Expectations Governance Great E... | design | design_only |
| 86 | D-MKT-DATA/HSTR Snapshot+Delta 历史状态重构 | HSTR Snapshot+Delta 历史状态重构 | design | design_only |
| 87 | D-MKT-DATA/HSTR历史状态重构 Historical State Reconstruction | HSTR历史状态重构 Historical State Rec... | design | design_only |
| 88 | D-MKT-DATA/High-Frequency Signal Enhancer 高频信号增强器 | High-Frequency Signal Enhancer 高频信... | design | design_only |
| 89 | D-MKT-DATA/Hot 热存储层 Redis | Hot 热存储层 Redis | design | design_only |
| 90 | D-MKT-DATA/ISIN 国际证券识别码 | ISIN 国际证券识别码 | design | design_only |
| 91 | D-MKT-DATA/ISO 27001 Benchmark ISO 27001对标 | ISO 27001 Benchmark ISO 27001对标 | design | design_only |
| 92 | D-MKT-DATA/Incremental Update Engine 增量更新引擎 | Incremental Update Engine 增量更新引擎 | design | design_only |
| 93 | D-MKT-DATA/Industry Best Practice Benchmark 行业最佳实践对标 | Industry Best Practice Benchmark 行业... | design | design_only |
| 94 | D-MKT-DATA/InstrumentId 工具ID | InstrumentId 工具ID | design | design_only |
| 95 | D-MKT-DATA/Knowledge Distiller 知识蒸馏器 | Knowledge Distiller 知识蒸馏器 | design | design_only |
| 96 | D-MKT-DATA/Knowledge Intelligence 知识与智能 | Knowledge Intelligence 知识与智能 | design | design_only |
| 97 | D-MKT-DATA/L0 数据接入与预处理层 Data Ingestion & Preproc... | L0 数据接入与预处理层 Data Ingestion ... | design | design_only |
| 98 | D-MKT-DATA/L0→L1 标准化流水线 L0→L1 Normalization Pipeline | L0→L1 标准化流水线 L0→L1 Normalizat... | design | design_only |
| 99 | D-MKT-DATA/L0→L6全链路规格 L0→L6 Full-chain Spec | L0→L6全链路规格 L0→L6 Full-chain Spec | design | design_only |
| 100 | D-MKT-DATA/L0不持久化原始推送 No L0 Persistence | L0不持久化原始推送 No L0 Persistence | design | design_only |
| 101 | D-MKT-DATA/L1 Public Data L1公开数据 | L1 Public Data L1公开数据 | design | design_only |
| 102 | D-MKT-DATA/L2 Internal Data L2内部数据 | L2 Internal Data L2内部数据 | design | design_only |
| 103 | D-MKT-DATA/L3 Confidential Data L3机密数据 | L3 Confidential Data L3机密数据 | design | design_only |
| 104 | D-MKT-DATA/L4 Top Secret Data L4绝密数据 | L4 Top Secret Data L4绝密数据 | design | design_only |
| 105 | D-MKT-DATA/LLM API Unified Integration 集成 | LLM API Unified Integration 集成 | design | design_only |
| 106 | D-MKT-DATA/LimitUp/Down 涨跌停事件 | LimitUp/Down 涨跌停事件 | design | design_only |
| 107 | D-MKT-DATA/Local File Auto-Parser 本地文件自动解析器 | Local File Auto-Parser 本地文件自动解... | design | design_only |
| 108 | D-MKT-DATA/M3 Code Generation Model Adapter 适配器模型 | M3 Code Generation Model Adapter 适配... | design | design_only |
| 109 | D-MKT-DATA/M7 Deep Review Model Adapter 适配器模型视图 | M7 Deep Review Model Adapter 适配器模... | design | design_only |
| 110 | D-MKT-DATA/M8-NEW-01 | M8-NEW-01 | design | design_only |
| 111 | D-MKT-DATA/M8-NEW-02 | M8-NEW-02 | design | design_only |
| 112 | D-MKT-DATA/M8-NEW-03 | M8-NEW-03 | design | design_only |
| 113 | D-MKT-DATA/M8-NEW-04 | M8-NEW-04 | design | design_only |
| 114 | D-MKT-DATA/M8-NEW-05 | M8-NEW-05 | design | design_only |
| 115 | D-MKT-DATA/M8-NEW-06 | M8-NEW-06 | design | design_only |
| 116 | D-MKT-DATA/M8-NEW-07 | M8-NEW-07 | design | design_only |
| 117 | D-MKT-DATA/M8-NEW-08 | M8-NEW-08 | design | design_only |
| 118 | D-MKT-DATA/M8-NEW-09 | M8-NEW-09 | design | design_only |
| 119 | D-MKT-DATA/M8-NEW-10 | M8-NEW-10 | design | design_only |
| 120 | D-MKT-DATA/M8-S01 | M8-S01 | design | design_only |
| 121 | D-MKT-DATA/M8-S02 | M8-S02 | design | design_only |
| 122 | D-MKT-DATA/M8-S03 | M8-S03 | design | design_only |
| 123 | D-MKT-DATA/M8-S04 | M8-S04 | design | design_only |
| 124 | D-MKT-DATA/M8-S05 | M8-S05 | design | design_only |
| 125 | D-MKT-DATA/M8-S06 | M8-S06 | design | design_only |
| 126 | D-MKT-DATA/M8-S07 | M8-S07 | design | design_only |
| 127 | D-MKT-DATA/Macro Data Manager 宏观数据管理器 | Macro Data Manager 宏观数据管理器 | design | design_only |
| 128 | D-MKT-DATA/Market Data Pipeline 行情数据管道 | Market Data Pipeline 行情数据管道 | design | design_only |
| 129 | D-MKT-DATA/Market Data Provider 行情数据提供商 | Market Data Provider 行情数据提供商 | design | design_only |
| 130 | D-MKT-DATA/Medallion架构 Medallion Architecture | Medallion架构 Medallion Architecture | design | design_only |
| 131 | D-MKT-DATA/Microsoft Qlib PIT数据架构 Qlib PIT Architecture | Microsoft Qlib PIT数据架构 Qlib PIT A... | design | design_only |
| 132 | D-MKT-DATA/Microstructure Analyzer 微观结构分析器 | Microstructure Analyzer 微观结构分析器 | design | design_only |
| 133 | D-MKT-DATA/Money 货币 | Money 货币 | design | design_only |
| 134 | D-MKT-DATA/Multi-Source Data Priority Router 多数据源优先... | Multi-Source Data Priority Router 多... | design | design_only |
| 135 | D-MKT-DATA/NIST CSF Benchmark NIST CSF对标 | NIST CSF Benchmark NIST CSF对标 | design | design_only |
| 136 | D-MKT-DATA/NormalizedMarketData Interface 标准化市场数据接口 | NormalizedMarketData Interface 标准化... | design | design_only |
| 137 | D-MKT-DATA/NormalizedMarketData 标准化行情数据 | NormalizedMarketData 标准化行情数据 | design | design_only |
| 138 | D-MKT-DATA/Normalizer 归一化器 | Normalizer 归一化器 | design | design_only |
| 139 | D-MKT-DATA/ODCS标准与工具链 ODCS Standard & Toolchain | ODCS标准与工具链 ODCS Standard & Tool... | design | design_only |
| 140 | D-MKT-DATA/Overseas Market Data Adapter 外盘数据适配器 | Overseas Market Data Adapter 外盘数据... | design | design_only |
| 141 | D-MKT-DATA/P0/P1/P2三级优先级 Three-tier Priority | P0/P1/P2三级优先级 Three-tier Priority | design | design_only |
| 142 | D-MKT-DATA/PIT Consistency Guarantee PIT一致性保证 | PIT Consistency Guarantee PIT一致性保证 | design | design_only |
| 143 | D-MKT-DATA/PIT Consistency Guard PIT一致性守卫 | PIT Consistency Guard PIT一致性守卫 | design | design_only |
| 144 | D-MKT-DATA/PIT Manager 管理器 | PIT Manager 管理器 | design | design_only |
| 145 | D-MKT-DATA/PIT一致性 Point-in-Time Consistency | PIT一致性 Point-in-Time Consistency | design | design_only |
| 146 | D-MKT-DATA/PIT三条公理 PIT Three Axioms | PIT三条公理 PIT Three Axioms | design | design_only |
| 147 | D-MKT-DATA/PIT数据时点标记 PIT Data Point-in-time Marking | PIT数据时点标记 PIT Data Point-in-tim... | design | design_only |
| 148 | D-MKT-DATA/PIT校验规则 PIT Validation Rules | PIT校验规则 PIT Validation Rules | design | design_only |
| 149 | D-MKT-DATA/PIT股票池每日截面快照 PIT Stock Pool Daily Sna... | PIT股票池每日截面快照 PIT Stock Pool ... | design | design_only |
| 150 | D-MKT-DATA/PIT验证与测试框架 PIT Validation Framework | PIT验证与测试框架 PIT Validation Fram... | design | design_only |
| 151 | D-MKT-DATA/Parquet列式存储 Parquet Columnar Storage | Parquet列式存储 Parquet Columnar Storage | design | design_only |
| 152 | D-MKT-DATA/Parquet列式存储替代SQLite行式 Parquet over SQLite | Parquet列式存储替代SQLite行式 Parquet... | design | design_only |
| 153 | D-MKT-DATA/Personal Information Protection Law Benchmark ... | Personal Information Protection Law B... | design | design_only |
| 154 | D-MKT-DATA/Point in Time Consistency Point-in-Time一致性保证 | Point in Time Consistency Point-in-Ti... | design | design_only |
| 155 | D-MKT-DATA/Point-in-Time一致性保证 PIT Consistency | Point-in-Time一致性保证 PIT Consistency | design | design_only |
| 156 | D-MKT-DATA/Policy Event Factor Library 政策事件因子库 | Policy Event Factor Library 政策事件... | design | design_only |
| 157 | D-MKT-DATA/PriceChanged 价格变更事件 | PriceChanged 价格变更事件 | design | design_only |
| 158 | D-MKT-DATA/Pydantic V2 Code Generator Pydantic V2代码生成器 | Pydantic V2 Code Generator Pydantic V... | design | design_only |
| 159 | D-MKT-DATA/Real-time Feed Manager 实时管理器 | Real-time Feed Manager 实时管理器 | design | design_only |
| 160 | D-MKT-DATA/Real-time Quote 实时行情 | Real-time Quote 实时行情 | design | design_only |
| 161 | D-MKT-DATA/Redis RDB+AOF双开 Redis RDB+AOF | Redis RDB+AOF双开 Redis RDB+AOF | design | design_only |
| 162 | D-MKT-DATA/Redis因子值→信号检查点 | Redis因子值→信号检查点 | design | design_only |
| 163 | D-MKT-DATA/Research Report Collector 研究报告采集器 | Research Report Collector 研究报告采集器 | design | design_only |
| 164 | D-MKT-DATA/SLA分级体系 SLA Tiered System | SLA分级体系 SLA Tiered System | design | design_only |
| 165 | D-MKT-DATA/SLA按影响分级而非按数据源 SLA by Impact | SLA按影响分级而非按数据源 SLA by Impact | design | design_only |
| 166 | D-MKT-DATA/SQL AST解析器 SQL AST Parser | SQL AST解析器 SQL AST Parser | design | design_only |
| 167 | D-MKT-DATA/Saga模式 Saga Pattern | Saga模式 Saga Pattern | design | design_only |
| 168 | D-MKT-DATA/Schema演进 Schema Evolution | Schema演进 Schema Evolution | design | design_only |
| 169 | D-MKT-DATA/Schema演进必须向后兼容 Backward Compatible Schema | Schema演进必须向后兼容 Backward Compa... | design | design_only |
| 170 | D-MKT-DATA/Sector Factor Data Manager 板块因子数据管理器 | Sector Factor Data Manager 板块因子数... | design | design_only |
| 171 | D-MKT-DATA/Sina+Tencent Real-Time 新浪+腾讯实时行情 | Sina+Tencent Real-Time 新浪+腾讯实时行情 | design | design_only |
| 172 | D-MKT-DATA/Storage 存储 | Storage 存储 | design | design_only |
| 173 | D-MKT-DATA/Survivorship Bias零容忍 Survivorship Bias Zero... | Survivorship Bias零容忍 Survivorship ... | design | design_only |
| 174 | D-MKT-DATA/Temp Query P5 模板查询p5 | Temp Query P5 模板查询p5 | design | design_only |
| 175 | D-MKT-DATA/Text Sentiment Factor Extractor 文本情感因子提... | Text Sentiment Factor Extractor 文本... | design | design_only |
| 176 | D-MKT-DATA/Tick Data Manager 管理器 | Tick Data Manager 管理器 | design | design_only |
| 177 | D-MKT-DATA/Tick→信号≤15秒延迟预算 Tick→Signal 15s Budget | Tick→信号≤15秒延迟预算 Tick→Signal... | design | design_only |
| 178 | D-MKT-DATA/Tick仅保留3个月 Tick Retain 3 Months | Tick仅保留3个月 Tick Retain 3 Months | design | design_only |
| 179 | D-MKT-DATA/Tick仅保留近3个月 Tick Retain 3 Months | Tick仅保留近3个月 Tick Retain 3 Months | design | design_only |
| 180 | D-MKT-DATA/Tiered Storage Architecture 分层存储架构 | Tiered Storage Architecture 分层存储架构 | design | design_only |
| 181 | D-MKT-DATA/Tiered Storage 分层存储 | Tiered Storage 分层存储 | design | design_only |
| 182 | D-MKT-DATA/TimescaleDB PostgreSQL时序扩展 | TimescaleDB PostgreSQL时序扩展 | design | design_only |
| 183 | D-MKT-DATA/Trading Calendar Manager 交易日历管理 | Trading Calendar Manager 交易日历管理 | design | design_only |
| 184 | D-MKT-DATA/Trading Decision Annotation Dataset 交易决策标... | Trading Decision Annotation Dataset ... | design | design_only |
| 185 | D-MKT-DATA/Training Dataset Manager 训练数据集管理器 | Training Dataset Manager 训练数据集管... | design | design_only |
| 186 | D-MKT-DATA/Unified Data Portal 统一数据门户 | Unified Data Portal 统一数据门户 | design | design_only |
| 187 | D-MKT-DATA/Vector DB Switch Manager 向量数据库切换管理器 | Vector DB Switch Manager 向量数据库切... | design | design_only |
| 188 | D-MKT-DATA/VolumeSurge 成交量突增事件 | VolumeSurge 成交量突增事件 | design | design_only |
| 189 | D-MKT-DATA/WAL Checkpoint Monitor SQLite WAL检查点监控器 | WAL Checkpoint Monitor SQLite WAL检查... | design | design_only |
| 190 | D-MKT-DATA/Warm 温存储层 DuckDB+Parquet | Warm 温存储层 DuckDB+Parquet | design | design_only |
| 191 | D-MKT-DATA/Web Data Crawler 网络数据爬虫 | Web Data Crawler 网络数据爬虫 | design | design_only |
| 192 | D-MKT-DATA/Zero Look-Ahead Bias 零前瞻偏差 | Zero Look-Ahead Bias 零前瞻偏差 | design | design_only |
| 193 | D-MKT-DATA/event_id用SHA-256 SHA-256 event_id | event_id用SHA-256 SHA-256 event_id | design | design_only |
| 194 | D-MKT-DATA/iFind 补充数据源 | iFind 补充数据源 | design | design_only |
| 195 | D-MKT-DATA/iFind 补充数据源 盘后日线 | iFind 补充数据源 盘后日线 | design | design_only |
| 196 | D-MKT-DATA/iFind为基本面主数据源 iFind as Fundamental Source | iFind为基本面主数据源 iFind as Fundam... | design | design_only |
| 197 | D-MKT-DATA/iFind盘后数据→Parquet检查点 | iFind盘后数据→Parquet检查点 | design | design_only |
| 198 | D-MKT-DATA/miniQMT Tick→Redis检查点 | miniQMT Tick→Redis检查点 | design | design_only |
| 199 | D-MKT-DATA/miniQMT 主数据源 | miniQMT 主数据源 | design | design_only |
| 200 | D-MKT-DATA/miniQMT 主数据源 A股全市场 | miniQMT 主数据源 A股全市场 | design | design_only |

> (仅显示前 200 个模块，共 256 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 258 条 / 258 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 258 条 / 258 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 184 条 / edges                               │
│   [runtime]: 44 条 / edges                                       │
│   [event]: 14 条 / edges                                         │
│   [config_depends]: 9 条 / edges                                 │
│   [contract]: 4 条 / edges                                       │
│   [data]: 3 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (184 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   D-DATA → Connector 连接器                                      │
│   D-DATA-ENG → iFind 补充数据源 盘后日线                         │
│   Connector 连接器 → Normalizer 归一化器                         │
│   Normalizer 归一化器 → Storage 存储                             │
│   Storage 存储 → Real-time Feed Manager 实...                    │
│   Real-time Feed Manager 实... → PIT Manager 管理器              │
│   PIT Manager 管理器 → Data Permission Manager ...               │
│   Data Permission Manager ... → Tick Data Manager 管理器         │
│   Tick Data Manager 管理器 → Data Observability Engine...        │
│   Data Observability Engine... → A-Share Intraday Data Man...    │
│   A-Share Intraday Data Man... → A-Share Auction Data Mana...    │
│   A-Share Auction Data Mana... → A-Share Alt-Data Source M...    │
│   A-Share Alt-Data Source M... → A-Share Order Flow Data M...    │
│   A-Share Order Flow Data M... → AkShare Data Source Adapt...    │
│   AkShare Data Source Adapt... → LLM API Unified Integrati...    │
│   AkShare Data Source Adapt... → L3 Confidential Data L3机...    │
│   LLM API Unified Integrati... → M3 Code Generation Model ...    │
│   M3 Code Generation Model ... → M7 Deep Review Model Adap...    │
│   M7 Deep Review Model Adap... → M8-S01                          │
│   M8-S01 → M8-S02                                                │
│   M8-S01 → Data Contract规范缺失 Dat...                          │
│   M8-S01 → Personal Information Prot...                          │
│   M8-S02 → M8-S03                                                │
│   M8-S03 → M8-S04                                                │
│   M8-S04 → M8-S05                                                │
│   M8-S05 → M8-S06                                                │
│   M8-S06 → M8-S07                                                │
│   M8-S07 → M8-NEW-01                                             │
│   M8-NEW-01 → M8-NEW-02                                          │
│   M8-NEW-01 → L4 Top Secret Data L4绝密...                       │
│   M8-NEW-02 → M8-NEW-03                                          │
│   M8-NEW-03 → M8-NEW-04                                          │
│   M8-NEW-04 → M8-NEW-05                                          │
│   M8-NEW-04 → ISIN 国际证券识别码                                │
│   M8-NEW-05 → M8-NEW-06                                          │
│   M8-NEW-06 → M8-NEW-07                                          │
│   M8-NEW-06 → L2 Internal Data L2内部数据                        │
│   M8-NEW-07 → M8-NEW-08                                          │
│   M8-NEW-07 → Real-time Quote 实时行情                           │
│   M8-NEW-08 → M8-NEW-09                                          │
│   M8-NEW-09 → M8-NEW-10                                          │
│   M8-NEW-10 → miniQMT 主数据源                                   │
│   miniQMT 主数据源 → iFind 补充数据源                            │
│   iFind 补充数据源 → AkShare 免费备用数据源                      │
│   AkShare 免费备用数据源 → BaoStock 历史数据补充                 │
│   AkShare 免费备用数据源 → Flink 2.x AI Functions Fl...          │
│   AkShare 免费备用数据源 → Microsoft Qlib PIT数据架...           │
│   AkShare 免费备用数据源 → InstrumentId 工具ID                   │
│   BaoStock 历史数据补充 → tushare 新闻快讯数据源                 │
│   ...还有 135 条 / 135 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[runtime]** (44 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (14 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (9 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (4 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (3 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 258 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `08_d_mkt_data_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
