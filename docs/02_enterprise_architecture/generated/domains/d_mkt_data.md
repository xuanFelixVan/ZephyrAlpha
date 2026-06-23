---
doc_type: domain_architecture_doc
title: D-MKT_DATA 行情数据(接入+存储)架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-MKT_DATA 行情数据(接入+存储)架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-MKT_DATA |
| 域名称 | 行情数据(接入+存储) |
| 架构层 | L1_foundation |
| 模块总数 | 266 |
| 设计态模块 | 257 |
| 原型态模块 | 2 |
| 生产态模块 | 1 |
| 容量 | 1/150 (正常) |
| 描述 | 行情数据接入与存储域。负责市场行情数据的接入、存储与分发，包括实时行情、历史行情、多市场数据源的统一接入层。拆分自原D-DATA域。 |

## 模块清单

共 266 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-MKT-DATA/4元组数据映射模型 4-tuple Data Mapping |  | design_only | design | 0 | 0 |
| D-MKT-DATA/A-Share Alt-Data Source Manager 管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/A-Share Auction Data Manager 管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/A-Share Intraday Data Manager 管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/A-Share Order Flow Data Manager 管理器订单 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/A-Share Special A股特色 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/A3 Data Architecture A3数据架构 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/ADR记录架构决策 ADR Records |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AI驱动异常检测 AI Anomaly Detection |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AS OF JOIN实现 AS OF JOIN Implementation |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AUM>200万后升级ClickHouse ClickHouse Upgrade Gate |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AUM驱动存储升级 AUM-driven Storage Upgrade |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AkShare AkShare数据适配器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AkShare Data Source Adapter 适配器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AkShare 免费备用数据源 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Apache Doris 4.x量化交易 Apache Doris 4.x |  | design_only | design | 0 | 0 |
| D-MKT-DATA/AuctionUpdate 集合竞价更新事件 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Auto Data Source Switch 数据源自动切换 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/BCBS 239合规框架 BCBS 239 Framework |  | design_only | design | 0 | 0 |
| D-MKT-DATA/BaoStock 历史数据补充 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Bi-Temporal Modeling 双时态建模 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Bloomberg PiT经济数据 Bloomberg PiT Economic Data |  | design_only | design | 0 | 0 |
| D-MKT-DATA/CQRS Command Query Responsibility Segregation CQRS命令查询职责分离 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/CQRS分离 CQRS Separation |  | design_only | design | 0 | 0 |
| D-MKT-DATA/CQRS读写分离 CQRS Read-Write Split |  | design_only | design | 0 | 0 |
| D-MKT-DATA/CTR-001 NormalizedMarketData 标准化市场数据 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/ClickHouse Analyzer ClickHouse分析器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/ClickHouse 列存时序数据库 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Cold 冷存储层 Parquet on SSD |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Concept Factor Mapping Engine 概念因子映射引擎 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Connector 连接器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Corporate Actions Processor 公司行为处理 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/CrossSourceReconciler 跨源对账器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/D-ALT-DATA MVP Downgrade D-ALT-DATA MVP降级 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/D-CROSS-ASSET MVP Downgrade D-CROSS-ASSET MVP降级 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/D-DATA |  | design_only | design | 0 | 0 |
| D-MKT-DATA/D-DATA-ENG |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DDD Aggregate Root & Lifecycle DDD聚合根与生命周期 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DDD Aggregate Root Lifecycle DDD聚合根与生命周期 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Anomaly Alerter 数据异常告警器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Contract执行策略 Data Contract Execution Strategy |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Contract规范缺失 Data Contract Gap |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Cost Tracker 数据成本追踪 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Ingestion & Management 数据接入与管理 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Ingestion Process 数据接入进程 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Isolation Manager 数据隔离管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Lakehouse架构 Data Lakehouse |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Mesh+Lakehouse互补架构 Data Mesh+Lakehouse Complementary |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Mesh架构 Data Mesh |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Observability Engine 可观测性引擎 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Observability 数据可观测性 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Observability五维度框架 Data Observability Five Dimensions |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Permission Manager 管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Retention Manager 数据保留策略 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Schema Registry 数据Schema注册表 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Source Health Monitor 数据源健康度监控器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Source Management 数据源管理 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Source Panorama 数据源全景 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Subscription Manager 数据订阅管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Data Version Manager 数据版本管理 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DataGapDetected 数据缺口检测事件 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DataSchemaChanged 数据Schema变更 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Design Decision Summary 设计决策汇总 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Dragon-Tiger List 龙虎榜 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Dual Temporal Modeling 双时态建模 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Dual-Mode Push Architecture 双模式推送架构 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DuckDB AS OF JOIN PIT Query Engine PIT查询引擎 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DuckDB QUALIFY ROW_NUMBER()实现PIT DuckDB QUALIFY PIT |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DuckDB性能四区间 DuckDB Performance Tiers |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DuckDB性能校准 DuckDB Performance Calibration |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DuckDB替代ClickHouse作为温层 DuckDB over ClickHouse |  | design_only | design | 0 | 0 |
| D-MKT-DATA/DuckDB温层替代ClickHouse DuckDB over ClickHouse |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Embargo期 Embargo Period |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Event Sourcing Architecture 事件溯源架构 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Event Store 事件存储 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Event Store用Parquet Event Store via Parquet |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Event Store设计 Event Store Design |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Exchange 交易所 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/FWT Retrieval Augmented Diffusion FWT检索增强扩散 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Financial Knowledge Graph 金融知识图谱 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Financial Parser 财务报告解析器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Five-Layer Funnel Data Support 五层筛选漏斗数据支撑 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Flink 2.x AI Functions Flink AI Functions Flink 2.x AI函数 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Governance Market Data Isolation 治理行情数据隔离 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Great Expectations Governance Great Expectations治理 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/HSTR Snapshot+Delta 历史状态重构 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/HSTR历史状态重构 Historical State Reconstruction |  | design_only | design | 0 | 0 |
| D-MKT-DATA/High-Frequency Signal Enhancer 高频信号增强器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Hot 热存储层 Redis |  | design_only | design | 0 | 0 |
| D-MKT-DATA/ISIN 国际证券识别码 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/ISO 27001 Benchmark ISO 27001对标 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Incremental Update Engine 增量更新引擎 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Industry Best Practice Benchmark 行业最佳实践对标 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/InstrumentId 工具ID |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Knowledge Distiller 知识蒸馏器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Knowledge Intelligence 知识与智能 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L0 数据接入与预处理层 Data Ingestion & Preprocessing Layer |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L0→L1 标准化流水线 L0→L1 Normalization Pipeline |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L0→L6全链路规格 L0→L6 Full-chain Spec |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L0不持久化原始推送 No L0 Persistence |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L1 Public Data L1公开数据 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L2 Internal Data L2内部数据 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L3 Confidential Data L3机密数据 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/L4 Top Secret Data L4绝密数据 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/LLM API Unified Integration 集成 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/LimitUp/Down 涨跌停事件 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Local File Auto-Parser 本地文件自动解析器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M3 Code Generation Model Adapter 适配器模型 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M7 Deep Review Model Adapter 适配器模型视图 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-01 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-02 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-03 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-04 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-05 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-06 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-07 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-08 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-09 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-NEW-10 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-S01 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-S02 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-S03 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-S04 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-S05 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-S06 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/M8-S07 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Macro Data Manager 宏观数据管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Market Data Pipeline 行情数据管道 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Market Data Provider 行情数据提供商 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Medallion架构 Medallion Architecture |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Microsoft Qlib PIT数据架构 Qlib PIT Architecture |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Microstructure Analyzer 微观结构分析器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Money 货币 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Multi-Source Data Priority Router 多数据源优先级路由器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/NIST CSF Benchmark NIST CSF对标 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/NormalizedMarketData Interface 标准化市场数据接口 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/NormalizedMarketData 标准化行情数据 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Normalizer 归一化器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/ODCS标准与工具链 ODCS Standard & Toolchain |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Overseas Market Data Adapter 外盘数据适配器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/P0/P1/P2三级优先级 Three-tier Priority |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT Consistency Guarantee PIT一致性保证 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT Consistency Guard PIT一致性守卫 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT Manager 管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT一致性 Point-in-Time Consistency |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT三条公理 PIT Three Axioms |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT数据时点标记 PIT Data Point-in-time Marking |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT校验规则 PIT Validation Rules |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT股票池每日截面快照 PIT Stock Pool Daily Snapshot |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PIT验证与测试框架 PIT Validation Framework |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Parquet列式存储 Parquet Columnar Storage |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Parquet列式存储替代SQLite行式 Parquet over SQLite |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Personal Information Protection Law Benchmark 个人信息保护法对标 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Point in Time Consistency Point-in-Time一致性保证 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Point-in-Time一致性保证 PIT Consistency |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Policy Event Factor Library 政策事件因子库 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/PriceChanged 价格变更事件 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Pydantic V2 Code Generator Pydantic V2代码生成器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Real-time Feed Manager 实时管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Real-time Quote 实时行情 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Redis RDB+AOF双开 Redis RDB+AOF |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Redis因子值→信号检查点 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Research Report Collector 研究报告采集器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/SLA分级体系 SLA Tiered System |  | design_only | design | 0 | 0 |
| D-MKT-DATA/SLA按影响分级而非按数据源 SLA by Impact |  | design_only | design | 0 | 0 |
| D-MKT-DATA/SQL AST解析器 SQL AST Parser |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Saga模式 Saga Pattern |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Schema演进 Schema Evolution |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Schema演进必须向后兼容 Backward Compatible Schema |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Sector Factor Data Manager 板块因子数据管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Sina+Tencent Real-Time 新浪+腾讯实时行情 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Storage 存储 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Survivorship Bias零容忍 Survivorship Bias Zero Tolerance |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Temp Query P5 模板查询p5 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Text Sentiment Factor Extractor 文本情感因子提取器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Tick Data Manager 管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Tick→信号≤15秒延迟预算 Tick→Signal 15s Budget |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Tick仅保留3个月 Tick Retain 3 Months |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Tick仅保留近3个月 Tick Retain 3 Months |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Tiered Storage Architecture 分层存储架构 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Tiered Storage 分层存储 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/TimescaleDB PostgreSQL时序扩展 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Trading Calendar Manager 交易日历管理 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Trading Decision Annotation Dataset 交易决策标注数据集 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Training Dataset Manager 训练数据集管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Unified Data Portal 统一数据门户 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Vector DB Switch Manager 向量数据库切换管理器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/VolumeSurge 成交量突增事件 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/WAL Checkpoint Monitor SQLite WAL检查点监控器 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Warm 温存储层 DuckDB+Parquet |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Web Data Crawler 网络数据爬虫 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/Zero Look-Ahead Bias 零前瞻偏差 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/event_id用SHA-256 SHA-256 event_id |  | design_only | design | 0 | 0 |
| D-MKT-DATA/iFind 补充数据源 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/iFind 补充数据源 盘后日线 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/iFind为基本面主数据源 iFind as Fundamental Source |  | design_only | design | 0 | 0 |
| D-MKT-DATA/iFind盘后数据→Parquet检查点 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/miniQMT Tick→Redis检查点 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/miniQMT 主数据源 |  | design_only | design | 0 | 0 |
| D-MKT-DATA/miniQMT 主数据源 A股全市场 |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 266 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INFRA_RUNTIME | 24 | data,config_depends,contract,event |
| D-DATA_ENG | 21 | contract,event,data,domain_dependency |
| D-TRADING | 8 | contract,config_depends,data |
| D-EX_SOR | 8 | contract,data,event,config_depends |
| D-SHARED | 3 | event,data,contract |
| D-GOVERNANCE | 2 | config_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-RISK | 53 | event,data,contract,config_depends,domain_dependency |
| D-GOVERNANCE | 51 | import_depends,test_depends,event,contract,data,config_depends |
| D-COMPLIANCE | 47 | event,contract,data,config_depends |
| D-SECURITY | 38 | contract,event,data,config_depends |
| D-SIGNAL | 37 | data,config_depends,event,contract,domain_dependency |
| D-INTEGRATION | 34 | data,config_depends,contract,event |
| D-AUTONOMY_CORE | 26 | data,contract,event,config_depends |
| D-FACTOR | 23 | data,contract,config_depends,event,domain_dependency |
| D-INFRA_OPS | 21 | event,contract,config_depends,data |
| D-OPS | 18 | data,config_depends,event,contract |
| D-FRONTEND | 15 | data,contract,event,config_depends |
| D-AUTONOMY_PERM | 15 | event,contract,data,config_depends |
| D-INTELLIGENCE | 13 | contract,data,config_depends,event |
| D-KNOWLEDGE | 11 | data,event,contract |
| D-SIMULATION | 10 | data,event,contract,domain_dependency |
| D-EX_CORE | 9 | contract,data,event |
| D-REPORTING | 8 | contract,data,event |
| D-POSITION | 8 | data,contract,config_depends,event |
| D-PF_CORE | 8 | data,contract,event |
| D-PF_ALLOC | 7 | data,event,contract |
| D-CROSS_ASSET | 5 | config_depends,contract,data,event |
| D-ALT_DATA | 4 | data,config_depends,contract |
| D-ML_TRAIN | 3 | event,contract |
| D-DATA_SEC | 3 | data,event |
| D-DATA_GOV | 3 | event,config_depends,contract |
| D-SELL_DECISION | 2 | event,data |
| D-ML_SERVE | 2 | config_depends,contract |

## 域内依赖图

详见 [d_mkt_data_dependency.mmd](d_mkt_data_dependency.mmd)
