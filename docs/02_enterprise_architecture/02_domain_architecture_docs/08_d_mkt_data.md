---
doc_type: domain_architecture_doc
title: D-MKT_DATA 行情数据(接入+存储)架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 08_d_mkt_data 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 08 | Number | 08 |
| 域ID | D-MKT_DATA | Domain ID | D-MKT_DATA |
| 域名称 | 行情数据(接入+存储) | Domain Name | 行情数据(接入+存储) |
| 层级 | L1_foundation | Layer | L1_foundation |
| 模块数 | 266 | Module Count | 266 |
| 域内依赖 | 258 | Internal Dependencies | 258 |
| 跨域入边 | 474 | Cross-domain Incoming | 474 |
| 跨域出边 | 66 | Cross-domain Outgoing | 66 |
| 设计态模块 | 257 | Design Modules | 257 |
| 原型态模块 | 2 | Prototype Modules | 2 |
| 生产态模块 | 1 | Production Modules | 1 |
| 容量 | 266/150 (超容) | Capacity | 266/150 (超容) |
| 描述 | 行情数据接入与存储域。负责市场行情数据的接入、存储与分发，包括实时行情、历史行情、多市场数据源的统一接入层。拆分自原D-DATA域。 | Description | 行情数据接入与存储域。负责市场行情数据的接入、存储与分发，包括实时行情、历史行情、多市场数据源的统一接入层。拆分自原D-DATA域。 |

## 模块清单 / Module List

共 266 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| D-MKT-DATA/4元组数据映射模型 4-tuple Data Mapping | 4元组数据映射模型 4-tuple Data Mapping | design | design_only | D-MKT-DATA/4元组数据映射模型 4-tuple Data Mapping | 4元组数据映射模型 4-tuple Data Mapping | design | design_only |
| D-MKT-DATA/A-Share Alt-Data Source Manager 管理器 | A-Share Alt-Data Source Manager 管理器 | design | design_only | D-MKT-DATA/A-Share Alt-Data Source Manager 管理器 | A-Share Alt-Data Source Manager 管理器 | design | design_only |
| D-MKT-DATA/A-Share Auction Data Manager 管理器 | A-Share Auction Data Manager 管理器 | design | design_only | D-MKT-DATA/A-Share Auction Data Manager 管理器 | A-Share Auction Data Manager 管理器 | design | design_only |
| D-MKT-DATA/A-Share Intraday Data Manager 管理器 | A-Share Intraday Data Manager 管理器 | design | design_only | D-MKT-DATA/A-Share Intraday Data Manager 管理器 | A-Share Intraday Data Manager 管理器 | design | design_only |
| D-MKT-DATA/A-Share Order Flow Data Manager 管理器订单 | A-Share Order Flow Data Manager 管理器订单 | design | design_only | D-MKT-DATA/A-Share Order Flow Data Manager 管理器订单 | A-Share Order Flow Data Manager 管理器订单 | design | design_only |
| D-MKT-DATA/A-Share Special A股特色 | A-Share Special A股特色 | design | design_only | D-MKT-DATA/A-Share Special A股特色 | A-Share Special A股特色 | design | design_only |
| D-MKT-DATA/A3 Data Architecture A3数据架构 | A3 Data Architecture A3数据架构 | design | design_only | D-MKT-DATA/A3 Data Architecture A3数据架构 | A3 Data Architecture A3数据架构 | design | design_only |
| D-MKT-DATA/ADR记录架构决策 ADR Records | ADR记录架构决策 ADR Records | design | design_only | D-MKT-DATA/ADR记录架构决策 ADR Records | ADR记录架构决策 ADR Records | design | design_only |
| D-MKT-DATA/AI驱动异常检测 AI Anomaly Detection | AI驱动异常检测 AI Anomaly Detection | design | design_only | D-MKT-DATA/AI驱动异常检测 AI Anomaly Detection | AI驱动异常检测 AI Anomaly Detection | design | design_only |
| D-MKT-DATA/AS OF JOIN实现 AS OF JOIN Implementation | AS OF JOIN实现 AS OF JOIN Implementation | design | design_only | D-MKT-DATA/AS OF JOIN实现 AS OF JOIN Implementation | AS OF JOIN实现 AS OF JOIN Implementation | design | design_only |
| D-MKT-DATA/AUM>200万后升级ClickHouse ClickHouse Upgrade Gate | AUM>200万后升级ClickHouse ClickHouse Upgr... | design | design_only | D-MKT-DATA/AUM>200万后升级ClickHouse ClickHouse Upgrade Gate | AUM>200万后升级ClickHouse ClickHouse Upgr... | design | design_only |
| D-MKT-DATA/AUM驱动存储升级 AUM-driven Storage Upgrade | AUM驱动存储升级 AUM-driven Storage Upgrade | design | design_only | D-MKT-DATA/AUM驱动存储升级 AUM-driven Storage Upgrade | AUM驱动存储升级 AUM-driven Storage Upgrade | design | design_only |
| D-MKT-DATA/AkShare AkShare数据适配器 | AkShare AkShare数据适配器 | design | design_only | D-MKT-DATA/AkShare AkShare数据适配器 | AkShare AkShare数据适配器 | design | design_only |
| D-MKT-DATA/AkShare Data Source Adapter 适配器 | AkShare Data Source Adapter 适配器 | design | design_only | D-MKT-DATA/AkShare Data Source Adapter 适配器 | AkShare Data Source Adapter 适配器 | design | design_only |
| D-MKT-DATA/AkShare 免费备用数据源 | AkShare 免费备用数据源 | design | design_only | D-MKT-DATA/AkShare 免费备用数据源 | AkShare 免费备用数据源 | design | design_only |
| D-MKT-DATA/Apache Doris 4.x量化交易 Apache Doris 4.x | Apache Doris 4.x量化交易 Apache Doris 4.x | design | design_only | D-MKT-DATA/Apache Doris 4.x量化交易 Apache Doris 4.x | Apache Doris 4.x量化交易 Apache Doris 4.x | design | design_only |
| D-MKT-DATA/AuctionUpdate 集合竞价更新事件 | AuctionUpdate 集合竞价更新事件 | design | design_only | D-MKT-DATA/AuctionUpdate 集合竞价更新事件 | AuctionUpdate 集合竞价更新事件 | design | design_only |
| D-MKT-DATA/Auto Data Source Switch 数据源自动切换 | Auto Data Source Switch 数据源自动切换 | design | design_only | D-MKT-DATA/Auto Data Source Switch 数据源自动切换 | Auto Data Source Switch 数据源自动切换 | design | design_only |
| D-MKT-DATA/BCBS 239合规框架 BCBS 239 Framework | BCBS 239合规框架 BCBS 239 Framework | design | design_only | D-MKT-DATA/BCBS 239合规框架 BCBS 239 Framework | BCBS 239合规框架 BCBS 239 Framework | design | design_only |
| D-MKT-DATA/BaoStock 历史数据补充 | BaoStock 历史数据补充 | design | design_only | D-MKT-DATA/BaoStock 历史数据补充 | BaoStock 历史数据补充 | design | design_only |
| D-MKT-DATA/Bi-Temporal Modeling 双时态建模 | Bi-Temporal Modeling 双时态建模 | design | design_only | D-MKT-DATA/Bi-Temporal Modeling 双时态建模 | Bi-Temporal Modeling 双时态建模 | design | design_only |
| D-MKT-DATA/Bloomberg PiT经济数据 Bloomberg PiT Economic Data | Bloomberg PiT经济数据 Bloomberg PiT Econo... | design | design_only | D-MKT-DATA/Bloomberg PiT经济数据 Bloomberg PiT Economic Data | Bloomberg PiT经济数据 Bloomberg PiT Econo... | design | design_only |
| D-MKT-DATA/CQRS Command Query Responsibility Segregation CQRS命令查询职责分离 | CQRS Command Query Responsibility Seg... | design | design_only | D-MKT-DATA/CQRS Command Query Responsibility Segregation CQRS命令查询职责分离 | CQRS Command Query Responsibility Seg... | design | design_only |
| D-MKT-DATA/CQRS分离 CQRS Separation | CQRS分离 CQRS Separation | design | design_only | D-MKT-DATA/CQRS分离 CQRS Separation | CQRS分离 CQRS Separation | design | design_only |
| D-MKT-DATA/CQRS读写分离 CQRS Read-Write Split | CQRS读写分离 CQRS Read-Write Split | design | design_only | D-MKT-DATA/CQRS读写分离 CQRS Read-Write Split | CQRS读写分离 CQRS Read-Write Split | design | design_only |
| D-MKT-DATA/CTR-001 NormalizedMarketData 标准化市场数据 | CTR-001 NormalizedMarketData 标准化市场数据 | design | design_only | D-MKT-DATA/CTR-001 NormalizedMarketData 标准化市场数据 | CTR-001 NormalizedMarketData 标准化市场数据 | design | design_only |
| D-MKT-DATA/ClickHouse Analyzer ClickHouse分析器 | ClickHouse Analyzer ClickHouse分析器 | design | design_only | D-MKT-DATA/ClickHouse Analyzer ClickHouse分析器 | ClickHouse Analyzer ClickHouse分析器 | design | design_only |
| D-MKT-DATA/ClickHouse 列存时序数据库 | ClickHouse 列存时序数据库 | design | design_only | D-MKT-DATA/ClickHouse 列存时序数据库 | ClickHouse 列存时序数据库 | design | design_only |
| D-MKT-DATA/Cold 冷存储层 Parquet on SSD | Cold 冷存储层 Parquet on SSD | design | design_only | D-MKT-DATA/Cold 冷存储层 Parquet on SSD | Cold 冷存储层 Parquet on SSD | design | design_only |
| D-MKT-DATA/Concept Factor Mapping Engine 概念因子映射引擎 | Concept Factor Mapping Engine 概念因子映射引擎 | design | design_only | D-MKT-DATA/Concept Factor Mapping Engine 概念因子映射引擎 | Concept Factor Mapping Engine 概念因子映射引擎 | design | design_only |
| D-MKT-DATA/Connector 连接器 | Connector 连接器 | design | design_only | D-MKT-DATA/Connector 连接器 | Connector 连接器 | design | design_only |
| D-MKT-DATA/Corporate Actions Processor 公司行为处理 | Corporate Actions Processor 公司行为处理 | design | design_only | D-MKT-DATA/Corporate Actions Processor 公司行为处理 | Corporate Actions Processor 公司行为处理 | design | design_only |
| D-MKT-DATA/CrossSourceReconciler 跨源对账器 | CrossSourceReconciler 跨源对账器 | design | design_only | D-MKT-DATA/CrossSourceReconciler 跨源对账器 | CrossSourceReconciler 跨源对账器 | design | design_only |
| D-MKT-DATA/D-ALT-DATA MVP Downgrade D-ALT-DATA MVP降级 | D-ALT-DATA MVP Downgrade D-ALT-DATA M... | design | design_only | D-MKT-DATA/D-ALT-DATA MVP Downgrade D-ALT-DATA MVP降级 | D-ALT-DATA MVP Downgrade D-ALT-DATA M... | design | design_only |
| D-MKT-DATA/D-CROSS-ASSET MVP Downgrade D-CROSS-ASSET MVP降级 | D-CROSS-ASSET MVP Downgrade D-CROSS-A... | design | design_only | D-MKT-DATA/D-CROSS-ASSET MVP Downgrade D-CROSS-ASSET MVP降级 | D-CROSS-ASSET MVP Downgrade D-CROSS-A... | design | design_only |
| D-MKT-DATA/D-DATA | D-DATA | design | design_only | D-MKT-DATA/D-DATA | D-DATA | design | design_only |
| D-MKT-DATA/D-DATA-ENG | D-DATA-ENG | design | design_only | D-MKT-DATA/D-DATA-ENG | D-DATA-ENG | design | design_only |
| D-MKT-DATA/DDD Aggregate Root & Lifecycle DDD聚合根与生命周期 | DDD Aggregate Root & Lifecycle DDD聚合根... | design | design_only | D-MKT-DATA/DDD Aggregate Root & Lifecycle DDD聚合根与生命周期 | DDD Aggregate Root & Lifecycle DDD聚合根... | design | design_only |
| D-MKT-DATA/DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | design | design_only | D-MKT-DATA/DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | DDD Aggregate Root Lifecycle DDD聚合根与生命周期 | design | design_only |
| D-MKT-DATA/Data Anomaly Alerter 数据异常告警器 | Data Anomaly Alerter 数据异常告警器 | design | design_only | D-MKT-DATA/Data Anomaly Alerter 数据异常告警器 | Data Anomaly Alerter 数据异常告警器 | design | design_only |
| D-MKT-DATA/Data Contract执行策略 Data Contract Execution Strategy | Data Contract执行策略 Data Contract Execu... | design | design_only | D-MKT-DATA/Data Contract执行策略 Data Contract Execution Strategy | Data Contract执行策略 Data Contract Execu... | design | design_only |
| D-MKT-DATA/Data Contract规范缺失 Data Contract Gap | Data Contract规范缺失 Data Contract Gap | design | design_only | D-MKT-DATA/Data Contract规范缺失 Data Contract Gap | Data Contract规范缺失 Data Contract Gap | design | design_only |
| D-MKT-DATA/Data Cost Tracker 数据成本追踪 | Data Cost Tracker 数据成本追踪 | design | design_only | D-MKT-DATA/Data Cost Tracker 数据成本追踪 | Data Cost Tracker 数据成本追踪 | design | design_only |
| D-MKT-DATA/Data Ingestion & Management 数据接入与管理 | Data Ingestion & Management 数据接入与管理 | design | design_only | D-MKT-DATA/Data Ingestion & Management 数据接入与管理 | Data Ingestion & Management 数据接入与管理 | design | design_only |
| D-MKT-DATA/Data Ingestion Process 数据接入进程 | Data Ingestion Process 数据接入进程 | design | design_only | D-MKT-DATA/Data Ingestion Process 数据接入进程 | Data Ingestion Process 数据接入进程 | design | design_only |
| D-MKT-DATA/Data Isolation Manager 数据隔离管理器 | Data Isolation Manager 数据隔离管理器 | design | design_only | D-MKT-DATA/Data Isolation Manager 数据隔离管理器 | Data Isolation Manager 数据隔离管理器 | design | design_only |
| D-MKT-DATA/Data Lakehouse架构 Data Lakehouse | Data Lakehouse架构 Data Lakehouse | design | design_only | D-MKT-DATA/Data Lakehouse架构 Data Lakehouse | Data Lakehouse架构 Data Lakehouse | design | design_only |
| D-MKT-DATA/Data Mesh+Lakehouse互补架构 Data Mesh+Lakehouse Complementary | Data Mesh+Lakehouse互补架构 Data Mesh+Lak... | design | design_only | D-MKT-DATA/Data Mesh+Lakehouse互补架构 Data Mesh+Lakehouse Complementary | Data Mesh+Lakehouse互补架构 Data Mesh+Lak... | design | design_only |
| D-MKT-DATA/Data Mesh架构 Data Mesh | Data Mesh架构 Data Mesh | design | design_only | D-MKT-DATA/Data Mesh架构 Data Mesh | Data Mesh架构 Data Mesh | design | design_only |
| D-MKT-DATA/Data Observability Engine 可观测性引擎 | Data Observability Engine 可观测性引擎 | design | design_only | D-MKT-DATA/Data Observability Engine 可观测性引擎 | Data Observability Engine 可观测性引擎 | design | design_only |
| D-MKT-DATA/Data Observability 数据可观测性 | Data Observability 数据可观测性 | design | design_only | D-MKT-DATA/Data Observability 数据可观测性 | Data Observability 数据可观测性 | design | design_only |
| D-MKT-DATA/Data Observability五维度框架 Data Observability Five Dimensions | Data Observability五维度框架 Data Observab... | design | design_only | D-MKT-DATA/Data Observability五维度框架 Data Observability Five Dimensions | Data Observability五维度框架 Data Observab... | design | design_only |
| D-MKT-DATA/Data Permission Manager 管理器 | Data Permission Manager 管理器 | design | design_only | D-MKT-DATA/Data Permission Manager 管理器 | Data Permission Manager 管理器 | design | design_only |
| D-MKT-DATA/Data Retention Manager 数据保留策略 | Data Retention Manager 数据保留策略 | design | design_only | D-MKT-DATA/Data Retention Manager 数据保留策略 | Data Retention Manager 数据保留策略 | design | design_only |
| D-MKT-DATA/Data Schema Registry 数据Schema注册表 | Data Schema Registry 数据Schema注册表 | design | design_only | D-MKT-DATA/Data Schema Registry 数据Schema注册表 | Data Schema Registry 数据Schema注册表 | design | design_only |
| D-MKT-DATA/Data Source Health Monitor 数据源健康度监控器 | Data Source Health Monitor 数据源健康度监控器 | design | design_only | D-MKT-DATA/Data Source Health Monitor 数据源健康度监控器 | Data Source Health Monitor 数据源健康度监控器 | design | design_only |
| D-MKT-DATA/Data Source Management 数据源管理 | Data Source Management 数据源管理 | design | design_only | D-MKT-DATA/Data Source Management 数据源管理 | Data Source Management 数据源管理 | design | design_only |
| D-MKT-DATA/Data Source Panorama 数据源全景 | Data Source Panorama 数据源全景 | design | design_only | D-MKT-DATA/Data Source Panorama 数据源全景 | Data Source Panorama 数据源全景 | design | design_only |
| D-MKT-DATA/Data Subscription Manager 数据订阅管理器 | Data Subscription Manager 数据订阅管理器 | design | design_only | D-MKT-DATA/Data Subscription Manager 数据订阅管理器 | Data Subscription Manager 数据订阅管理器 | design | design_only |
| D-MKT-DATA/Data Version Manager 数据版本管理 | Data Version Manager 数据版本管理 | design | design_only | D-MKT-DATA/Data Version Manager 数据版本管理 | Data Version Manager 数据版本管理 | design | design_only |
| D-MKT-DATA/DataGapDetected 数据缺口检测事件 | DataGapDetected 数据缺口检测事件 | design | design_only | D-MKT-DATA/DataGapDetected 数据缺口检测事件 | DataGapDetected 数据缺口检测事件 | design | design_only |
| D-MKT-DATA/DataSchemaChanged 数据Schema变更 | DataSchemaChanged 数据Schema变更 | design | design_only | D-MKT-DATA/DataSchemaChanged 数据Schema变更 | DataSchemaChanged 数据Schema变更 | design | design_only |
| D-MKT-DATA/Design Decision Summary 设计决策汇总 | Design Decision Summary 设计决策汇总 | design | design_only | D-MKT-DATA/Design Decision Summary 设计决策汇总 | Design Decision Summary 设计决策汇总 | design | design_only |
| D-MKT-DATA/Dragon-Tiger List 龙虎榜 | Dragon-Tiger List 龙虎榜 | design | design_only | D-MKT-DATA/Dragon-Tiger List 龙虎榜 | Dragon-Tiger List 龙虎榜 | design | design_only |
| D-MKT-DATA/Dual Temporal Modeling 双时态建模 | Dual Temporal Modeling 双时态建模 | design | design_only | D-MKT-DATA/Dual Temporal Modeling 双时态建模 | Dual Temporal Modeling 双时态建模 | design | design_only |
| D-MKT-DATA/Dual-Mode Push Architecture 双模式推送架构 | Dual-Mode Push Architecture 双模式推送架构 | design | design_only | D-MKT-DATA/Dual-Mode Push Architecture 双模式推送架构 | Dual-Mode Push Architecture 双模式推送架构 | design | design_only |
| D-MKT-DATA/DuckDB AS OF JOIN PIT Query Engine PIT查询引擎 | DuckDB AS OF JOIN PIT Query Engine PI... | design | design_only | D-MKT-DATA/DuckDB AS OF JOIN PIT Query Engine PIT查询引擎 | DuckDB AS OF JOIN PIT Query Engine PI... | design | design_only |
| D-MKT-DATA/DuckDB QUALIFY ROW_NUMBER()实现PIT DuckDB QUALIFY PIT | DuckDB QUALIFY ROW_NUMBER()实现PIT Duck... | design | design_only | D-MKT-DATA/DuckDB QUALIFY ROW_NUMBER()实现PIT DuckDB QUALIFY PIT | DuckDB QUALIFY ROW_NUMBER()实现PIT Duck... | design | design_only |
| D-MKT-DATA/DuckDB性能四区间 DuckDB Performance Tiers | DuckDB性能四区间 DuckDB Performance Tiers | design | design_only | D-MKT-DATA/DuckDB性能四区间 DuckDB Performance Tiers | DuckDB性能四区间 DuckDB Performance Tiers | design | design_only |
| D-MKT-DATA/DuckDB性能校准 DuckDB Performance Calibration | DuckDB性能校准 DuckDB Performance Calibra... | design | design_only | D-MKT-DATA/DuckDB性能校准 DuckDB Performance Calibration | DuckDB性能校准 DuckDB Performance Calibra... | design | design_only |
| D-MKT-DATA/DuckDB替代ClickHouse作为温层 DuckDB over ClickHouse | DuckDB替代ClickHouse作为温层 DuckDB over Cl... | design | design_only | D-MKT-DATA/DuckDB替代ClickHouse作为温层 DuckDB over ClickHouse | DuckDB替代ClickHouse作为温层 DuckDB over Cl... | design | design_only |
| D-MKT-DATA/DuckDB温层替代ClickHouse DuckDB over ClickHouse | DuckDB温层替代ClickHouse DuckDB over Clic... | design | design_only | D-MKT-DATA/DuckDB温层替代ClickHouse DuckDB over ClickHouse | DuckDB温层替代ClickHouse DuckDB over Clic... | design | design_only |
| D-MKT-DATA/Embargo期 Embargo Period | Embargo期 Embargo Period | design | design_only | D-MKT-DATA/Embargo期 Embargo Period | Embargo期 Embargo Period | design | design_only |
| D-MKT-DATA/Event Sourcing Architecture 事件溯源架构 | Event Sourcing Architecture 事件溯源架构 | design | design_only | D-MKT-DATA/Event Sourcing Architecture 事件溯源架构 | Event Sourcing Architecture 事件溯源架构 | design | design_only |
| D-MKT-DATA/Event Store 事件存储 | Event Store 事件存储 | design | design_only | D-MKT-DATA/Event Store 事件存储 | Event Store 事件存储 | design | design_only |
| D-MKT-DATA/Event Store用Parquet Event Store via Parquet | Event Store用Parquet Event Store via P... | design | design_only | D-MKT-DATA/Event Store用Parquet Event Store via Parquet | Event Store用Parquet Event Store via P... | design | design_only |
| D-MKT-DATA/Event Store设计 Event Store Design | Event Store设计 Event Store Design | design | design_only | D-MKT-DATA/Event Store设计 Event Store Design | Event Store设计 Event Store Design | design | design_only |
| D-MKT-DATA/Exchange 交易所 | Exchange 交易所 | design | design_only | D-MKT-DATA/Exchange 交易所 | Exchange 交易所 | design | design_only |
| D-MKT-DATA/FWT Retrieval Augmented Diffusion FWT检索增强扩散 | FWT Retrieval Augmented Diffusion FWT... | design | design_only | D-MKT-DATA/FWT Retrieval Augmented Diffusion FWT检索增强扩散 | FWT Retrieval Augmented Diffusion FWT... | design | design_only |
| D-MKT-DATA/Financial Knowledge Graph 金融知识图谱 | Financial Knowledge Graph 金融知识图谱 | design | design_only | D-MKT-DATA/Financial Knowledge Graph 金融知识图谱 | Financial Knowledge Graph 金融知识图谱 | design | design_only |
| D-MKT-DATA/Financial Parser 财务报告解析器 | Financial Parser 财务报告解析器 | design | design_only | D-MKT-DATA/Financial Parser 财务报告解析器 | Financial Parser 财务报告解析器 | design | design_only |
| D-MKT-DATA/Five-Layer Funnel Data Support 五层筛选漏斗数据支撑 | Five-Layer Funnel Data Support 五层筛选漏斗... | design | design_only | D-MKT-DATA/Five-Layer Funnel Data Support 五层筛选漏斗数据支撑 | Five-Layer Funnel Data Support 五层筛选漏斗... | design | design_only |
| D-MKT-DATA/Flink 2.x AI Functions Flink AI Functions Flink 2.x AI函数 | Flink 2.x AI Functions Flink AI Funct... | design | design_only | D-MKT-DATA/Flink 2.x AI Functions Flink AI Functions Flink 2.x AI函数 | Flink 2.x AI Functions Flink AI Funct... | design | design_only |
| D-MKT-DATA/Governance Market Data Isolation 治理行情数据隔离 | Governance Market Data Isolation 治理行情... | design | design_only | D-MKT-DATA/Governance Market Data Isolation 治理行情数据隔离 | Governance Market Data Isolation 治理行情... | design | design_only |
| D-MKT-DATA/Great Expectations Governance Great Expectations治理 | Great Expectations Governance Great E... | design | design_only | D-MKT-DATA/Great Expectations Governance Great Expectations治理 | Great Expectations Governance Great E... | design | design_only |
| D-MKT-DATA/HSTR Snapshot+Delta 历史状态重构 | HSTR Snapshot+Delta 历史状态重构 | design | design_only | D-MKT-DATA/HSTR Snapshot+Delta 历史状态重构 | HSTR Snapshot+Delta 历史状态重构 | design | design_only |
| D-MKT-DATA/HSTR历史状态重构 Historical State Reconstruction | HSTR历史状态重构 Historical State Reconstru... | design | design_only | D-MKT-DATA/HSTR历史状态重构 Historical State Reconstruction | HSTR历史状态重构 Historical State Reconstru... | design | design_only |
| D-MKT-DATA/High-Frequency Signal Enhancer 高频信号增强器 | High-Frequency Signal Enhancer 高频信号增强器 | design | design_only | D-MKT-DATA/High-Frequency Signal Enhancer 高频信号增强器 | High-Frequency Signal Enhancer 高频信号增强器 | design | design_only |
| D-MKT-DATA/Hot 热存储层 Redis | Hot 热存储层 Redis | design | design_only | D-MKT-DATA/Hot 热存储层 Redis | Hot 热存储层 Redis | design | design_only |
| D-MKT-DATA/ISIN 国际证券识别码 | ISIN 国际证券识别码 | design | design_only | D-MKT-DATA/ISIN 国际证券识别码 | ISIN 国际证券识别码 | design | design_only |
| D-MKT-DATA/ISO 27001 Benchmark ISO 27001对标 | ISO 27001 Benchmark ISO 27001对标 | design | design_only | D-MKT-DATA/ISO 27001 Benchmark ISO 27001对标 | ISO 27001 Benchmark ISO 27001对标 | design | design_only |
| D-MKT-DATA/Incremental Update Engine 增量更新引擎 | Incremental Update Engine 增量更新引擎 | design | design_only | D-MKT-DATA/Incremental Update Engine 增量更新引擎 | Incremental Update Engine 增量更新引擎 | design | design_only |
| D-MKT-DATA/Industry Best Practice Benchmark 行业最佳实践对标 | Industry Best Practice Benchmark 行业最佳... | design | design_only | D-MKT-DATA/Industry Best Practice Benchmark 行业最佳实践对标 | Industry Best Practice Benchmark 行业最佳... | design | design_only |
| D-MKT-DATA/InstrumentId 工具ID | InstrumentId 工具ID | design | design_only | D-MKT-DATA/InstrumentId 工具ID | InstrumentId 工具ID | design | design_only |
| D-MKT-DATA/Knowledge Distiller 知识蒸馏器 | Knowledge Distiller 知识蒸馏器 | design | design_only | D-MKT-DATA/Knowledge Distiller 知识蒸馏器 | Knowledge Distiller 知识蒸馏器 | design | design_only |
| D-MKT-DATA/Knowledge Intelligence 知识与智能 | Knowledge Intelligence 知识与智能 | design | design_only | D-MKT-DATA/Knowledge Intelligence 知识与智能 | Knowledge Intelligence 知识与智能 | design | design_only |
| D-MKT-DATA/L0 数据接入与预处理层 Data Ingestion & Preprocessing Layer | L0 数据接入与预处理层 Data Ingestion & Preproc... | design | design_only | D-MKT-DATA/L0 数据接入与预处理层 Data Ingestion & Preprocessing Layer | L0 数据接入与预处理层 Data Ingestion & Preproc... | design | design_only |
| D-MKT-DATA/L0→L1 标准化流水线 L0→L1 Normalization Pipeline | L0→L1 标准化流水线 L0→L1 Normalization Pipe... | design | design_only | D-MKT-DATA/L0→L1 标准化流水线 L0→L1 Normalization Pipeline | L0→L1 标准化流水线 L0→L1 Normalization Pipe... | design | design_only |
| D-MKT-DATA/L0→L6全链路规格 L0→L6 Full-chain Spec | L0→L6全链路规格 L0→L6 Full-chain Spec | design | design_only | D-MKT-DATA/L0→L6全链路规格 L0→L6 Full-chain Spec | L0→L6全链路规格 L0→L6 Full-chain Spec | design | design_only |
| D-MKT-DATA/L0不持久化原始推送 No L0 Persistence | L0不持久化原始推送 No L0 Persistence | design | design_only | D-MKT-DATA/L0不持久化原始推送 No L0 Persistence | L0不持久化原始推送 No L0 Persistence | design | design_only |
| D-MKT-DATA/L1 Public Data L1公开数据 | L1 Public Data L1公开数据 | design | design_only | D-MKT-DATA/L1 Public Data L1公开数据 | L1 Public Data L1公开数据 | design | design_only |
| D-MKT-DATA/L2 Internal Data L2内部数据 | L2 Internal Data L2内部数据 | design | design_only | D-MKT-DATA/L2 Internal Data L2内部数据 | L2 Internal Data L2内部数据 | design | design_only |
| D-MKT-DATA/L3 Confidential Data L3机密数据 | L3 Confidential Data L3机密数据 | design | design_only | D-MKT-DATA/L3 Confidential Data L3机密数据 | L3 Confidential Data L3机密数据 | design | design_only |
| D-MKT-DATA/L4 Top Secret Data L4绝密数据 | L4 Top Secret Data L4绝密数据 | design | design_only | D-MKT-DATA/L4 Top Secret Data L4绝密数据 | L4 Top Secret Data L4绝密数据 | design | design_only |
| D-MKT-DATA/LLM API Unified Integration 集成 | LLM API Unified Integration 集成 | design | design_only | D-MKT-DATA/LLM API Unified Integration 集成 | LLM API Unified Integration 集成 | design | design_only |
| D-MKT-DATA/LimitUp/Down 涨跌停事件 | LimitUp/Down 涨跌停事件 | design | design_only | D-MKT-DATA/LimitUp/Down 涨跌停事件 | LimitUp/Down 涨跌停事件 | design | design_only |
| D-MKT-DATA/Local File Auto-Parser 本地文件自动解析器 | Local File Auto-Parser 本地文件自动解析器 | design | design_only | D-MKT-DATA/Local File Auto-Parser 本地文件自动解析器 | Local File Auto-Parser 本地文件自动解析器 | design | design_only |
| D-MKT-DATA/M3 Code Generation Model Adapter 适配器模型 | M3 Code Generation Model Adapter 适配器模型 | design | design_only | D-MKT-DATA/M3 Code Generation Model Adapter 适配器模型 | M3 Code Generation Model Adapter 适配器模型 | design | design_only |
| D-MKT-DATA/M7 Deep Review Model Adapter 适配器模型视图 | M7 Deep Review Model Adapter 适配器模型视图 | design | design_only | D-MKT-DATA/M7 Deep Review Model Adapter 适配器模型视图 | M7 Deep Review Model Adapter 适配器模型视图 | design | design_only |
| D-MKT-DATA/M8-NEW-01 | M8-NEW-01 | design | design_only | D-MKT-DATA/M8-NEW-01 | M8-NEW-01 | design | design_only |
| D-MKT-DATA/M8-NEW-02 | M8-NEW-02 | design | design_only | D-MKT-DATA/M8-NEW-02 | M8-NEW-02 | design | design_only |
| D-MKT-DATA/M8-NEW-03 | M8-NEW-03 | design | design_only | D-MKT-DATA/M8-NEW-03 | M8-NEW-03 | design | design_only |
| D-MKT-DATA/M8-NEW-04 | M8-NEW-04 | design | design_only | D-MKT-DATA/M8-NEW-04 | M8-NEW-04 | design | design_only |
| D-MKT-DATA/M8-NEW-05 | M8-NEW-05 | design | design_only | D-MKT-DATA/M8-NEW-05 | M8-NEW-05 | design | design_only |
| D-MKT-DATA/M8-NEW-06 | M8-NEW-06 | design | design_only | D-MKT-DATA/M8-NEW-06 | M8-NEW-06 | design | design_only |
| D-MKT-DATA/M8-NEW-07 | M8-NEW-07 | design | design_only | D-MKT-DATA/M8-NEW-07 | M8-NEW-07 | design | design_only |
| D-MKT-DATA/M8-NEW-08 | M8-NEW-08 | design | design_only | D-MKT-DATA/M8-NEW-08 | M8-NEW-08 | design | design_only |
| D-MKT-DATA/M8-NEW-09 | M8-NEW-09 | design | design_only | D-MKT-DATA/M8-NEW-09 | M8-NEW-09 | design | design_only |
| D-MKT-DATA/M8-NEW-10 | M8-NEW-10 | design | design_only | D-MKT-DATA/M8-NEW-10 | M8-NEW-10 | design | design_only |
| D-MKT-DATA/M8-S01 | M8-S01 | design | design_only | D-MKT-DATA/M8-S01 | M8-S01 | design | design_only |
| D-MKT-DATA/M8-S02 | M8-S02 | design | design_only | D-MKT-DATA/M8-S02 | M8-S02 | design | design_only |
| D-MKT-DATA/M8-S03 | M8-S03 | design | design_only | D-MKT-DATA/M8-S03 | M8-S03 | design | design_only |
| D-MKT-DATA/M8-S04 | M8-S04 | design | design_only | D-MKT-DATA/M8-S04 | M8-S04 | design | design_only |
| D-MKT-DATA/M8-S05 | M8-S05 | design | design_only | D-MKT-DATA/M8-S05 | M8-S05 | design | design_only |
| D-MKT-DATA/M8-S06 | M8-S06 | design | design_only | D-MKT-DATA/M8-S06 | M8-S06 | design | design_only |
| D-MKT-DATA/M8-S07 | M8-S07 | design | design_only | D-MKT-DATA/M8-S07 | M8-S07 | design | design_only |
| D-MKT-DATA/Macro Data Manager 宏观数据管理器 | Macro Data Manager 宏观数据管理器 | design | design_only | D-MKT-DATA/Macro Data Manager 宏观数据管理器 | Macro Data Manager 宏观数据管理器 | design | design_only |
| D-MKT-DATA/Market Data Pipeline 行情数据管道 | Market Data Pipeline 行情数据管道 | design | design_only | D-MKT-DATA/Market Data Pipeline 行情数据管道 | Market Data Pipeline 行情数据管道 | design | design_only |
| D-MKT-DATA/Market Data Provider 行情数据提供商 | Market Data Provider 行情数据提供商 | design | design_only | D-MKT-DATA/Market Data Provider 行情数据提供商 | Market Data Provider 行情数据提供商 | design | design_only |
| D-MKT-DATA/Medallion架构 Medallion Architecture | Medallion架构 Medallion Architecture | design | design_only | D-MKT-DATA/Medallion架构 Medallion Architecture | Medallion架构 Medallion Architecture | design | design_only |
| D-MKT-DATA/Microsoft Qlib PIT数据架构 Qlib PIT Architecture | Microsoft Qlib PIT数据架构 Qlib PIT Archi... | design | design_only | D-MKT-DATA/Microsoft Qlib PIT数据架构 Qlib PIT Architecture | Microsoft Qlib PIT数据架构 Qlib PIT Archi... | design | design_only |
| D-MKT-DATA/Microstructure Analyzer 微观结构分析器 | Microstructure Analyzer 微观结构分析器 | design | design_only | D-MKT-DATA/Microstructure Analyzer 微观结构分析器 | Microstructure Analyzer 微观结构分析器 | design | design_only |
| D-MKT-DATA/Money 货币 | Money 货币 | design | design_only | D-MKT-DATA/Money 货币 | Money 货币 | design | design_only |
| D-MKT-DATA/Multi-Source Data Priority Router 多数据源优先级路由器 | Multi-Source Data Priority Router 多数据... | design | design_only | D-MKT-DATA/Multi-Source Data Priority Router 多数据源优先级路由器 | Multi-Source Data Priority Router 多数据... | design | design_only |
| D-MKT-DATA/NIST CSF Benchmark NIST CSF对标 | NIST CSF Benchmark NIST CSF对标 | design | design_only | D-MKT-DATA/NIST CSF Benchmark NIST CSF对标 | NIST CSF Benchmark NIST CSF对标 | design | design_only |
| D-MKT-DATA/NormalizedMarketData Interface 标准化市场数据接口 | NormalizedMarketData Interface 标准化市场数据接口 | design | design_only | D-MKT-DATA/NormalizedMarketData Interface 标准化市场数据接口 | NormalizedMarketData Interface 标准化市场数据接口 | design | design_only |
| D-MKT-DATA/NormalizedMarketData 标准化行情数据 | NormalizedMarketData 标准化行情数据 | design | design_only | D-MKT-DATA/NormalizedMarketData 标准化行情数据 | NormalizedMarketData 标准化行情数据 | design | design_only |
| D-MKT-DATA/Normalizer 归一化器 | Normalizer 归一化器 | design | design_only | D-MKT-DATA/Normalizer 归一化器 | Normalizer 归一化器 | design | design_only |
| D-MKT-DATA/ODCS标准与工具链 ODCS Standard & Toolchain | ODCS标准与工具链 ODCS Standard & Toolchain | design | design_only | D-MKT-DATA/ODCS标准与工具链 ODCS Standard & Toolchain | ODCS标准与工具链 ODCS Standard & Toolchain | design | design_only |
| D-MKT-DATA/Overseas Market Data Adapter 外盘数据适配器 | Overseas Market Data Adapter 外盘数据适配器 | design | design_only | D-MKT-DATA/Overseas Market Data Adapter 外盘数据适配器 | Overseas Market Data Adapter 外盘数据适配器 | design | design_only |
| D-MKT-DATA/P0/P1/P2三级优先级 Three-tier Priority | P0/P1/P2三级优先级 Three-tier Priority | design | design_only | D-MKT-DATA/P0/P1/P2三级优先级 Three-tier Priority | P0/P1/P2三级优先级 Three-tier Priority | design | design_only |
| D-MKT-DATA/PIT Consistency Guarantee PIT一致性保证 | PIT Consistency Guarantee PIT一致性保证 | design | design_only | D-MKT-DATA/PIT Consistency Guarantee PIT一致性保证 | PIT Consistency Guarantee PIT一致性保证 | design | design_only |
| D-MKT-DATA/PIT Consistency Guard PIT一致性守卫 | PIT Consistency Guard PIT一致性守卫 | design | design_only | D-MKT-DATA/PIT Consistency Guard PIT一致性守卫 | PIT Consistency Guard PIT一致性守卫 | design | design_only |
| D-MKT-DATA/PIT Manager 管理器 | PIT Manager 管理器 | design | design_only | D-MKT-DATA/PIT Manager 管理器 | PIT Manager 管理器 | design | design_only |
| D-MKT-DATA/PIT一致性 Point-in-Time Consistency | PIT一致性 Point-in-Time Consistency | design | design_only | D-MKT-DATA/PIT一致性 Point-in-Time Consistency | PIT一致性 Point-in-Time Consistency | design | design_only |
| D-MKT-DATA/PIT三条公理 PIT Three Axioms | PIT三条公理 PIT Three Axioms | design | design_only | D-MKT-DATA/PIT三条公理 PIT Three Axioms | PIT三条公理 PIT Three Axioms | design | design_only |
| D-MKT-DATA/PIT数据时点标记 PIT Data Point-in-time Marking | PIT数据时点标记 PIT Data Point-in-time Marking | design | design_only | D-MKT-DATA/PIT数据时点标记 PIT Data Point-in-time Marking | PIT数据时点标记 PIT Data Point-in-time Marking | design | design_only |
| D-MKT-DATA/PIT校验规则 PIT Validation Rules | PIT校验规则 PIT Validation Rules | design | design_only | D-MKT-DATA/PIT校验规则 PIT Validation Rules | PIT校验规则 PIT Validation Rules | design | design_only |
| D-MKT-DATA/PIT股票池每日截面快照 PIT Stock Pool Daily Snapshot | PIT股票池每日截面快照 PIT Stock Pool Daily Sna... | design | design_only | D-MKT-DATA/PIT股票池每日截面快照 PIT Stock Pool Daily Snapshot | PIT股票池每日截面快照 PIT Stock Pool Daily Sna... | design | design_only |
| D-MKT-DATA/PIT验证与测试框架 PIT Validation Framework | PIT验证与测试框架 PIT Validation Framework | design | design_only | D-MKT-DATA/PIT验证与测试框架 PIT Validation Framework | PIT验证与测试框架 PIT Validation Framework | design | design_only |
| D-MKT-DATA/Parquet列式存储 Parquet Columnar Storage | Parquet列式存储 Parquet Columnar Storage | design | design_only | D-MKT-DATA/Parquet列式存储 Parquet Columnar Storage | Parquet列式存储 Parquet Columnar Storage | design | design_only |
| D-MKT-DATA/Parquet列式存储替代SQLite行式 Parquet over SQLite | Parquet列式存储替代SQLite行式 Parquet over SQ... | design | design_only | D-MKT-DATA/Parquet列式存储替代SQLite行式 Parquet over SQLite | Parquet列式存储替代SQLite行式 Parquet over SQ... | design | design_only |
| D-MKT-DATA/Personal Information Protection Law Benchmark 个人信息保护法对标 | Personal Information Protection Law B... | design | design_only | D-MKT-DATA/Personal Information Protection Law Benchmark 个人信息保护法对标 | Personal Information Protection Law B... | design | design_only |
| D-MKT-DATA/Point in Time Consistency Point-in-Time一致性保证 | Point in Time Consistency Point-in-Ti... | design | design_only | D-MKT-DATA/Point in Time Consistency Point-in-Time一致性保证 | Point in Time Consistency Point-in-Ti... | design | design_only |
| D-MKT-DATA/Point-in-Time一致性保证 PIT Consistency | Point-in-Time一致性保证 PIT Consistency | design | design_only | D-MKT-DATA/Point-in-Time一致性保证 PIT Consistency | Point-in-Time一致性保证 PIT Consistency | design | design_only |
| D-MKT-DATA/Policy Event Factor Library 政策事件因子库 | Policy Event Factor Library 政策事件因子库 | design | design_only | D-MKT-DATA/Policy Event Factor Library 政策事件因子库 | Policy Event Factor Library 政策事件因子库 | design | design_only |
| D-MKT-DATA/PriceChanged 价格变更事件 | PriceChanged 价格变更事件 | design | design_only | D-MKT-DATA/PriceChanged 价格变更事件 | PriceChanged 价格变更事件 | design | design_only |
| D-MKT-DATA/Pydantic V2 Code Generator Pydantic V2代码生成器 | Pydantic V2 Code Generator Pydantic V... | design | design_only | D-MKT-DATA/Pydantic V2 Code Generator Pydantic V2代码生成器 | Pydantic V2 Code Generator Pydantic V... | design | design_only |
| D-MKT-DATA/Real-time Feed Manager 实时管理器 | Real-time Feed Manager 实时管理器 | design | design_only | D-MKT-DATA/Real-time Feed Manager 实时管理器 | Real-time Feed Manager 实时管理器 | design | design_only |
| D-MKT-DATA/Real-time Quote 实时行情 | Real-time Quote 实时行情 | design | design_only | D-MKT-DATA/Real-time Quote 实时行情 | Real-time Quote 实时行情 | design | design_only |
| D-MKT-DATA/Redis RDB+AOF双开 Redis RDB+AOF | Redis RDB+AOF双开 Redis RDB+AOF | design | design_only | D-MKT-DATA/Redis RDB+AOF双开 Redis RDB+AOF | Redis RDB+AOF双开 Redis RDB+AOF | design | design_only |
| D-MKT-DATA/Redis因子值→信号检查点 | Redis因子值→信号检查点 | design | design_only | D-MKT-DATA/Redis因子值→信号检查点 | Redis因子值→信号检查点 | design | design_only |
| D-MKT-DATA/Research Report Collector 研究报告采集器 | Research Report Collector 研究报告采集器 | design | design_only | D-MKT-DATA/Research Report Collector 研究报告采集器 | Research Report Collector 研究报告采集器 | design | design_only |
| D-MKT-DATA/SLA分级体系 SLA Tiered System | SLA分级体系 SLA Tiered System | design | design_only | D-MKT-DATA/SLA分级体系 SLA Tiered System | SLA分级体系 SLA Tiered System | design | design_only |
| D-MKT-DATA/SLA按影响分级而非按数据源 SLA by Impact | SLA按影响分级而非按数据源 SLA by Impact | design | design_only | D-MKT-DATA/SLA按影响分级而非按数据源 SLA by Impact | SLA按影响分级而非按数据源 SLA by Impact | design | design_only |
| D-MKT-DATA/SQL AST解析器 SQL AST Parser | SQL AST解析器 SQL AST Parser | design | design_only | D-MKT-DATA/SQL AST解析器 SQL AST Parser | SQL AST解析器 SQL AST Parser | design | design_only |
| D-MKT-DATA/Saga模式 Saga Pattern | Saga模式 Saga Pattern | design | design_only | D-MKT-DATA/Saga模式 Saga Pattern | Saga模式 Saga Pattern | design | design_only |
| D-MKT-DATA/Schema演进 Schema Evolution | Schema演进 Schema Evolution | design | design_only | D-MKT-DATA/Schema演进 Schema Evolution | Schema演进 Schema Evolution | design | design_only |
| D-MKT-DATA/Schema演进必须向后兼容 Backward Compatible Schema | Schema演进必须向后兼容 Backward Compatible Sc... | design | design_only | D-MKT-DATA/Schema演进必须向后兼容 Backward Compatible Schema | Schema演进必须向后兼容 Backward Compatible Sc... | design | design_only |
| D-MKT-DATA/Sector Factor Data Manager 板块因子数据管理器 | Sector Factor Data Manager 板块因子数据管理器 | design | design_only | D-MKT-DATA/Sector Factor Data Manager 板块因子数据管理器 | Sector Factor Data Manager 板块因子数据管理器 | design | design_only |
| D-MKT-DATA/Sina+Tencent Real-Time 新浪+腾讯实时行情 | Sina+Tencent Real-Time 新浪+腾讯实时行情 | design | design_only | D-MKT-DATA/Sina+Tencent Real-Time 新浪+腾讯实时行情 | Sina+Tencent Real-Time 新浪+腾讯实时行情 | design | design_only |
| D-MKT-DATA/Storage 存储 | Storage 存储 | design | design_only | D-MKT-DATA/Storage 存储 | Storage 存储 | design | design_only |
| D-MKT-DATA/Survivorship Bias零容忍 Survivorship Bias Zero Tolerance | Survivorship Bias零容忍 Survivorship Bia... | design | design_only | D-MKT-DATA/Survivorship Bias零容忍 Survivorship Bias Zero Tolerance | Survivorship Bias零容忍 Survivorship Bia... | design | design_only |
| D-MKT-DATA/Temp Query P5 模板查询p5 | Temp Query P5 模板查询p5 | design | design_only | D-MKT-DATA/Temp Query P5 模板查询p5 | Temp Query P5 模板查询p5 | design | design_only |
| D-MKT-DATA/Text Sentiment Factor Extractor 文本情感因子提取器 | Text Sentiment Factor Extractor 文本情感因... | design | design_only | D-MKT-DATA/Text Sentiment Factor Extractor 文本情感因子提取器 | Text Sentiment Factor Extractor 文本情感因... | design | design_only |
| D-MKT-DATA/Tick Data Manager 管理器 | Tick Data Manager 管理器 | design | design_only | D-MKT-DATA/Tick Data Manager 管理器 | Tick Data Manager 管理器 | design | design_only |
| D-MKT-DATA/Tick→信号≤15秒延迟预算 Tick→Signal 15s Budget | Tick→信号≤15秒延迟预算 Tick→Signal 15s Budget | design | design_only | D-MKT-DATA/Tick→信号≤15秒延迟预算 Tick→Signal 15s Budget | Tick→信号≤15秒延迟预算 Tick→Signal 15s Budget | design | design_only |
| D-MKT-DATA/Tick仅保留3个月 Tick Retain 3 Months | Tick仅保留3个月 Tick Retain 3 Months | design | design_only | D-MKT-DATA/Tick仅保留3个月 Tick Retain 3 Months | Tick仅保留3个月 Tick Retain 3 Months | design | design_only |
| D-MKT-DATA/Tick仅保留近3个月 Tick Retain 3 Months | Tick仅保留近3个月 Tick Retain 3 Months | design | design_only | D-MKT-DATA/Tick仅保留近3个月 Tick Retain 3 Months | Tick仅保留近3个月 Tick Retain 3 Months | design | design_only |
| D-MKT-DATA/Tiered Storage Architecture 分层存储架构 | Tiered Storage Architecture 分层存储架构 | design | design_only | D-MKT-DATA/Tiered Storage Architecture 分层存储架构 | Tiered Storage Architecture 分层存储架构 | design | design_only |
| D-MKT-DATA/Tiered Storage 分层存储 | Tiered Storage 分层存储 | design | design_only | D-MKT-DATA/Tiered Storage 分层存储 | Tiered Storage 分层存储 | design | design_only |
| D-MKT-DATA/TimescaleDB PostgreSQL时序扩展 | TimescaleDB PostgreSQL时序扩展 | design | design_only | D-MKT-DATA/TimescaleDB PostgreSQL时序扩展 | TimescaleDB PostgreSQL时序扩展 | design | design_only |
| D-MKT-DATA/Trading Calendar Manager 交易日历管理 | Trading Calendar Manager 交易日历管理 | design | design_only | D-MKT-DATA/Trading Calendar Manager 交易日历管理 | Trading Calendar Manager 交易日历管理 | design | design_only |
| D-MKT-DATA/Trading Decision Annotation Dataset 交易决策标注数据集 | Trading Decision Annotation Dataset 交... | design | design_only | D-MKT-DATA/Trading Decision Annotation Dataset 交易决策标注数据集 | Trading Decision Annotation Dataset 交... | design | design_only |
| D-MKT-DATA/Training Dataset Manager 训练数据集管理器 | Training Dataset Manager 训练数据集管理器 | design | design_only | D-MKT-DATA/Training Dataset Manager 训练数据集管理器 | Training Dataset Manager 训练数据集管理器 | design | design_only |
| D-MKT-DATA/Unified Data Portal 统一数据门户 | Unified Data Portal 统一数据门户 | design | design_only | D-MKT-DATA/Unified Data Portal 统一数据门户 | Unified Data Portal 统一数据门户 | design | design_only |
| D-MKT-DATA/Vector DB Switch Manager 向量数据库切换管理器 | Vector DB Switch Manager 向量数据库切换管理器 | design | design_only | D-MKT-DATA/Vector DB Switch Manager 向量数据库切换管理器 | Vector DB Switch Manager 向量数据库切换管理器 | design | design_only |
| D-MKT-DATA/VolumeSurge 成交量突增事件 | VolumeSurge 成交量突增事件 | design | design_only | D-MKT-DATA/VolumeSurge 成交量突增事件 | VolumeSurge 成交量突增事件 | design | design_only |
| D-MKT-DATA/WAL Checkpoint Monitor SQLite WAL检查点监控器 | WAL Checkpoint Monitor SQLite WAL检查点监控器 | design | design_only | D-MKT-DATA/WAL Checkpoint Monitor SQLite WAL检查点监控器 | WAL Checkpoint Monitor SQLite WAL检查点监控器 | design | design_only |
| D-MKT-DATA/Warm 温存储层 DuckDB+Parquet | Warm 温存储层 DuckDB+Parquet | design | design_only | D-MKT-DATA/Warm 温存储层 DuckDB+Parquet | Warm 温存储层 DuckDB+Parquet | design | design_only |
| D-MKT-DATA/Web Data Crawler 网络数据爬虫 | Web Data Crawler 网络数据爬虫 | design | design_only | D-MKT-DATA/Web Data Crawler 网络数据爬虫 | Web Data Crawler 网络数据爬虫 | design | design_only |
| D-MKT-DATA/Zero Look-Ahead Bias 零前瞻偏差 | Zero Look-Ahead Bias 零前瞻偏差 | design | design_only | D-MKT-DATA/Zero Look-Ahead Bias 零前瞻偏差 | Zero Look-Ahead Bias 零前瞻偏差 | design | design_only |
| D-MKT-DATA/event_id用SHA-256 SHA-256 event_id | event_id用SHA-256 SHA-256 event_id | design | design_only | D-MKT-DATA/event_id用SHA-256 SHA-256 event_id | event_id用SHA-256 SHA-256 event_id | design | design_only |
| D-MKT-DATA/iFind 补充数据源 | iFind 补充数据源 | design | design_only | D-MKT-DATA/iFind 补充数据源 | iFind 补充数据源 | design | design_only |
| D-MKT-DATA/iFind 补充数据源 盘后日线 | iFind 补充数据源 盘后日线 | design | design_only | D-MKT-DATA/iFind 补充数据源 盘后日线 | iFind 补充数据源 盘后日线 | design | design_only |
| D-MKT-DATA/iFind为基本面主数据源 iFind as Fundamental Source | iFind为基本面主数据源 iFind as Fundamental So... | design | design_only | D-MKT-DATA/iFind为基本面主数据源 iFind as Fundamental Source | iFind为基本面主数据源 iFind as Fundamental So... | design | design_only |
| D-MKT-DATA/iFind盘后数据→Parquet检查点 | iFind盘后数据→Parquet检查点 | design | design_only | D-MKT-DATA/iFind盘后数据→Parquet检查点 | iFind盘后数据→Parquet检查点 | design | design_only |
| D-MKT-DATA/miniQMT Tick→Redis检查点 | miniQMT Tick→Redis检查点 | design | design_only | D-MKT-DATA/miniQMT Tick→Redis检查点 | miniQMT Tick→Redis检查点 | design | design_only |
| D-MKT-DATA/miniQMT 主数据源 | miniQMT 主数据源 | design | design_only | D-MKT-DATA/miniQMT 主数据源 | miniQMT 主数据源 | design | design_only |
| D-MKT-DATA/miniQMT 主数据源 A股全市场 | miniQMT 主数据源 A股全市场 | design | design_only | D-MKT-DATA/miniQMT 主数据源 A股全市场 | miniQMT 主数据源 A股全市场 | design | design_only |

> (仅显示前 200 个模块，共 266 个)

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_MKT_DATA["D-MKT_DATA 行情数据(接入+存储)"]
        D_MKT_DATA_4_4_tuple_Data_Mapping["4元组数据映射模型 4-tuple Data Mapping design"]
        D_MKT_DATA_A_Share_Alt_Data_Source_Manager["A-Share Alt-Data Source Manager 管理器 design"]
        D_MKT_DATA_A_Share_Auction_Data_Manager["A-Share Auction Data Manager 管理器 design"]
        D_MKT_DATA_A_Share_Intraday_Data_Manager["A-Share Intraday Data Manager 管理器 design"]
        D_MKT_DATA_A_Share_Order_Flow_Data_Manager["A-Share Order Flow Data Manager 管理器订单 design"]
        D_MKT_DATA_A_Share_Special_A["A-Share Special A股特色 design"]
        D_MKT_DATA_A3_Data_Architecture_A3["A3 Data Architecture A3数据架构 design"]
        D_MKT_DATA_ADR_ADR_Records["ADR记录架构决策 ADR Records design"]
        D_MKT_DATA_AI_AI_Anomaly_Detection["AI驱动异常检测 AI Anomaly Detection design"]
        D_MKT_DATA_AS_OF_JOIN_AS_OF_JOIN_Implementation["AS OF JOIN实现 AS OF JOIN Implementation design"]
        D_MKT_DATA_AUM_200_ClickHouse_ClickHouse_Upgrade_Gate["AUM>200万后升级ClickHouse ClickHouse Upgrade Gate design"]
        D_MKT_DATA_AUM_AUM_driven_Storage_Upgrade["AUM驱动存储升级 AUM-driven Storage Upgrade design"]
        D_MKT_DATA_AkShare_AkShare["AkShare AkShare数据适配器 design"]
        D_MKT_DATA_AkShare_Data_Source_Adapter["AkShare Data Source Adapter 适配器 design"]
        D_MKT_DATA_AkShare["AkShare 免费备用数据源 design"]
        D_MKT_DATA_Apache_Doris_4_x_Apache_Doris_4_x["Apache Doris 4.x量化交易 Apache Doris 4.x design"]
        D_MKT_DATA_AuctionUpdate["AuctionUpdate 集合竞价更新事件 design"]
        D_MKT_DATA_Auto_Data_Source_Switch["Auto Data Source Switch 数据源自动切换 design"]
        D_MKT_DATA_BCBS_239_BCBS_239_Framework["BCBS 239合规框架 BCBS 239 Framework design"]
        D_MKT_DATA_BaoStock["BaoStock 历史数据补充 design"]
        D_MKT_DATA_Bi_Temporal_Modeling["Bi-Temporal Modeling 双时态建模 design"]
        D_MKT_DATA_Bloomberg_PiT_Bloomberg_PiT_Economic_Data["Bloomberg PiT经济数据 Bloomberg PiT Economic Data design"]
        D_MKT_DATA_CQRS_Command_Query_Responsibility_Segregation_CQRS["CQRS Command Query Responsibility Segregation C... design"]
        D_MKT_DATA_CQRS_CQRS_Separation["CQRS分离 CQRS Separation design"]
        D_MKT_DATA_CQRS_CQRS_Read_Write_Split["CQRS读写分离 CQRS Read-Write Split design"]
        D_MKT_DATA_CTR_001_NormalizedMarketData["CTR-001 NormalizedMarketData 标准化市场数据 design"]
        D_MKT_DATA_ClickHouse_Analyzer_ClickHouse["ClickHouse Analyzer ClickHouse分析器 design"]
        D_MKT_DATA_ClickHouse["ClickHouse 列存时序数据库 design"]
        D_MKT_DATA_Cold_Parquet_on_SSD["Cold 冷存储层 Parquet on SSD design"]
        D_MKT_DATA_Concept_Factor_Mapping_Engine["Concept Factor Mapping Engine 概念因子映射引擎 design"]
    end
    D_MKT_DATA_A_Share_Intraday_Data_Manager -.->|import_depends| D_MKT_DATA_A_Share_Auction_Data_Manager
    D_MKT_DATA_A_Share_Auction_Data_Manager -.->|import_depends| D_MKT_DATA_A_Share_Alt_Data_Source_Manager
    D_MKT_DATA_A_Share_Alt_Data_Source_Manager -.->|import_depends| D_MKT_DATA_A_Share_Order_Flow_Data_Manager
    D_MKT_DATA_A_Share_Order_Flow_Data_Manager -.->|import_depends| D_MKT_DATA_AkShare_Data_Source_Adapter
    D_MKT_DATA_AkShare -.->|import_depends| D_MKT_DATA_BaoStock
    D_MKT_DATA_Cold_Parquet_on_SSD -.->|runtime| D_MKT_DATA_AUM_AUM_driven_Storage_Upgrade
    D_MKT_DATA_AI_AI_Anomaly_Detection -.->|runtime| D_MKT_DATA_AUM_200_ClickHouse_ClickHouse_Upgrade_Gate
    D_MKT_DATA_CQRS_CQRS_Read_Write_Split -.->|runtime| D_MKT_DATA_4_4_tuple_Data_Mapping
    D_MKT_DATA_4_4_tuple_Data_Mapping -.->|import_depends| D_MKT_DATA_ClickHouse
    D_TRADING["D-TRADING design"]
    D_MKT_DATA_A_Share_Intraday_Data_Manager -.->|contract| D_TRADING
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_MKT_DATA_BaoStock -.->|config_depends| D_INFRA_RUNTIME
    D_MKT_DATA_Cold_Parquet_on_SSD -.->|contract| D_INFRA_RUNTIME
    D_MKT_DATA_AI_AI_Anomaly_Detection -.->|contract| D_TRADING
    D_EX_SOR["D-EX_SOR design"]
    D_MKT_DATA_AuctionUpdate -.->|event| D_EX_SOR
    D_DATA_ENG["D-DATA_ENG design"]
    D_MKT_DATA_AS_OF_JOIN_AS_OF_JOIN_Implementation -.->|data| D_DATA_ENG
    D_MKT_DATA_AkShare_AkShare -.->|event| D_DATA_ENG
    D_MKT_DATA_A_Share_Special_A -.->|config_depends| D_INFRA_RUNTIME
    D_SECURITY["D-SECURITY design"]
    D_SECURITY -.->|event| D_MKT_DATA_A_Share_Auction_Data_Manager
    D_SECURITY -.->|event| D_MKT_DATA_A_Share_Auction_Data_Manager
    D_RISK["D-RISK design"]
    D_RISK -.->|data| D_MKT_DATA_A_Share_Alt_Data_Source_Manager
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|contract| D_MKT_DATA_A_Share_Alt_Data_Source_Manager
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_KNOWLEDGE -.->|event| D_MKT_DATA_A_Share_Order_Flow_Data_Manager
    D_RISK -.->|contract| D_MKT_DATA_A_Share_Order_Flow_Data_Manager
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_AUTONOMY_CORE -.->|event| D_MKT_DATA_A_Share_Order_Flow_Data_Manager
    D_INTELLIGENCE["D-INTELLIGENCE design"]
    D_INTELLIGENCE -.->|data| D_MKT_DATA_AkShare_Data_Source_Adapter
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_GOVERNANCE -.->|event| D_MKT_DATA_AkShare
    D_RISK -.->|config_depends| D_MKT_DATA_AkShare
    D_DATA_GOV["D-DATA_GOV design"]
    D_DATA_GOV -.->|config_depends| D_MKT_DATA_AkShare
    D_REPORTING["D-REPORTING design"]
    D_REPORTING -.->|contract| D_MKT_DATA_BaoStock
    D_KNOWLEDGE -.->|contract| D_MKT_DATA_BaoStock
    D_GOVERNANCE -.->|event| D_MKT_DATA_BaoStock
    D_AUTONOMY_PERM["D-AUTONOMY_PERM design"]
    D_AUTONOMY_PERM -.->|data| D_MKT_DATA_Cold_Parquet_on_SSD
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_MKT_DATA_4_4_tuple_Data_Mapping,D_MKT_DATA_A_Share_Alt_Data_Source_Manager,D_MKT_DATA_A_Share_Auction_Data_Manager,D_MKT_DATA_A_Share_Intraday_Data_Manager,D_MKT_DATA_A_Share_Order_Flow_Data_Manager,D_MKT_DATA_A_Share_Special_A,D_MKT_DATA_A3_Data_Architecture_A3,D_MKT_DATA_ADR_ADR_Records,D_MKT_DATA_AI_AI_Anomaly_Detection,D_MKT_DATA_AS_OF_JOIN_AS_OF_JOIN_Implementation,D_MKT_DATA_AUM_200_ClickHouse_ClickHouse_Upgrade_Gate,D_MKT_DATA_AUM_AUM_driven_Storage_Upgrade,D_MKT_DATA_AkShare_AkShare,D_MKT_DATA_AkShare_Data_Source_Adapter,D_MKT_DATA_AkShare,D_MKT_DATA_Apache_Doris_4_x_Apache_Doris_4_x,D_MKT_DATA_AuctionUpdate,D_MKT_DATA_Auto_Data_Source_Switch,D_MKT_DATA_BCBS_239_BCBS_239_Framework,D_MKT_DATA_BaoStock,D_MKT_DATA_Bi_Temporal_Modeling,D_MKT_DATA_Bloomberg_PiT_Bloomberg_PiT_Economic_Data,D_MKT_DATA_CQRS_Command_Query_Responsibility_Segregation_CQRS,D_MKT_DATA_CQRS_CQRS_Separation,D_MKT_DATA_CQRS_CQRS_Read_Write_Split,D_MKT_DATA_CTR_001_NormalizedMarketData,D_MKT_DATA_ClickHouse_Analyzer_ClickHouse,D_MKT_DATA_ClickHouse,D_MKT_DATA_Cold_Parquet_on_SSD,D_MKT_DATA_Concept_Factor_Mapping_Engine design
    class D_TRADING,D_INFRA_RUNTIME,D_EX_SOR,D_DATA_ENG,D_SECURITY,D_RISK,D_COMPLIANCE,D_KNOWLEDGE,D_AUTONOMY_CORE,D_INTELLIGENCE,D_GOVERNANCE,D_DATA_GOV,D_REPORTING,D_AUTONOMY_PERM external_design
```

> (依赖图最多显示前 30 个节点，共 266 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-INFRA_RUNTIME | 24 | data,config_depends,contract,event | D-INFRA_RUNTIME | 24 | data,config_depends,contract,event |
| D-DATA_ENG | 21 | contract,event,data,domain_dependency | D-DATA_ENG | 21 | contract,event,data,domain_dependency |
| D-TRADING | 8 | contract,config_depends,data | D-TRADING | 8 | contract,config_depends,data |
| D-EX_SOR | 8 | contract,data,event,config_depends | D-EX_SOR | 8 | contract,data,event,config_depends |
| D-SHARED | 3 | event,data,contract | D-SHARED | 3 | event,data,contract |
| D-GOVERNANCE | 2 | config_depends | D-GOVERNANCE | 2 | config_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-RISK | 53 | event,data,contract,config_depends,domain_dependency | D-RISK | 53 | event,data,contract,config_depends,domain_dependency |
| D-GOVERNANCE | 49 | import_depends,test_depends,event,contract,data,config_depends | D-GOVERNANCE | 49 | import_depends,test_depends,event,contract,data,config_depends |
| D-COMPLIANCE | 47 | event,contract,data,config_depends | D-COMPLIANCE | 47 | event,contract,data,config_depends |
| D-SECURITY | 38 | contract,event,data,config_depends | D-SECURITY | 38 | contract,event,data,config_depends |
| D-SIGNAL | 37 | data,config_depends,event,contract,domain_dependency | D-SIGNAL | 37 | data,config_depends,event,contract,domain_dependency |
| D-INTEGRATION | 34 | data,config_depends,contract,event | D-INTEGRATION | 34 | data,config_depends,contract,event |
| D-AUTONOMY_CORE | 26 | data,contract,event,config_depends | D-AUTONOMY_CORE | 26 | data,contract,event,config_depends |
| D-FACTOR | 23 | data,contract,config_depends,event,domain_dependency | D-FACTOR | 23 | data,contract,config_depends,event,domain_dependency |
| D-INFRA_OPS | 21 | event,contract,config_depends,data | D-INFRA_OPS | 21 | event,contract,config_depends,data |
| D-OPS | 19 | data,config_depends,event,contract | D-OPS | 19 | data,config_depends,event,contract |
| D-FRONTEND | 15 | data,contract,event,config_depends | D-FRONTEND | 15 | data,contract,event,config_depends |
| D-AUTONOMY_PERM | 15 | event,contract,data,config_depends | D-AUTONOMY_PERM | 15 | event,contract,data,config_depends |
| D-INTELLIGENCE | 13 | contract,data,config_depends,event | D-INTELLIGENCE | 13 | contract,data,config_depends,event |
| D-KNOWLEDGE | 11 | data,event,contract | D-KNOWLEDGE | 11 | data,event,contract |
| D-SIMULATION | 10 | data,event,contract,domain_dependency | D-SIMULATION | 10 | data,event,contract,domain_dependency |
| D-EX_CORE | 9 | contract,data,event | D-EX_CORE | 9 | contract,data,event |
| D-REPORTING | 8 | contract,data,event | D-REPORTING | 8 | contract,data,event |
| D-POSITION | 8 | data,contract,config_depends,event | D-POSITION | 8 | data,contract,config_depends,event |
| D-PF_CORE | 8 | data,contract,event | D-PF_CORE | 8 | data,contract,event |
| D-PF_ALLOC | 7 | data,event,contract | D-PF_ALLOC | 7 | data,event,contract |
| D-CROSS_ASSET | 5 | config_depends,contract,data,event | D-CROSS_ASSET | 5 | config_depends,contract,data,event |
| D-ALT_DATA | 4 | data,config_depends,contract | D-ALT_DATA | 4 | data,config_depends,contract |
| D-ML_TRAIN | 3 | event,contract | D-ML_TRAIN | 3 | event,contract |
| D-DATA_SEC | 3 | data,event | D-DATA_SEC | 3 | data,event |
| D-DATA_GOV | 3 | event,config_depends,contract | D-DATA_GOV | 3 | event,config_depends,contract |
| D-SELL_DECISION | 2 | event,data | D-SELL_DECISION | 2 | event,data |
| D-ML_SERVE | 2 | config_depends,contract | D-ML_SERVE | 2 | config_depends,contract |
| D-GOV_AUDIT | 1 | data | D-GOV_AUDIT | 1 | data |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
