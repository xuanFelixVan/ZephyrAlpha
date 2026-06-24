---
doc_type: domain_architecture_diagram
title: D-DATA_ENG 数据工程架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 05_d_data_eng / 数据工程 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示数据工程（D-DATA_ENG）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 数据工程（D-DATA_ENG）的模块分布。共 147 个模块 / 147 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (4 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   AkShare Data Source Adapter  [design]                          │
│   Data Source Health Monitor  [design]                           │
│   Smart Scheduler  [design]                                      │
│   Market Regime Reference Data  [design]                         │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/data_eng/__init__.py  [prototype]                   │
│   src/zephyr/data_eng/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/data_eng/api/__init__.py  [scaffold_placeholder]    │
│   src/zephyr/data_eng/core/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/data_eng/infrastructure/__init__.py  [scaffold_p... │
│   src/zephyr/data_eng/models/__init__.py  [scaffold_placeholder] │
│   src/zephyr/data_eng/services/__init__.py  [scaffold_placeho... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (136 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   ADWIN Drift Detection ADWIN漂移检测  [design]                  │
│   AI Auto Feature Discoverer AI自动特征发现器  [design]          │
│   Airflow Pipeline Airflow流水线  [design]                       │
│   Alternative Data 另类数据  [design]                            │
│   Apache Beam  [design]                                          │
│   Apache Iceberg v3特性 Iceberg v3 Features  [design]            │
│   CI/CD门禁集成 CI/CD Gate Integration  [design]                 │
│   CQRS Dependency Node CQRS依赖图节点  [design]                  │
│   CQRS Event Sourcing CQRS事件溯源  [design]                     │
│   CTR-TRACE-001 Data Lineage Chain CTR-TRACE-001数据血缘链契...  │
│   Cleaning & Anomaly Engine 清洗与异常引擎  [design]             │
│   Column-Level Lineage 列级血缘  [design]                        │
│   Core Pipeline 核心管线  [design]                               │
│   DDM Drift Detection DDM漂移检测  [design]                      │
│   Data Fusion 数据融合  [design]                                 │
│   Data Lifecycle Management 数据生命周期管理  [design]           │
│   Data Lineage & Traceability 数据血缘与可追溯性  [design]       │
│   Data Lineage Runtime Discovery 数据血缘运行时发现  [design]    │
│   ...还有 118 个模块 / 118 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 147 个模块 / 147 modules）。

### L1 基础层 / Foundation Layer (4 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 数据域-L0数据接入/D-DATA-67 | AkShare Data Source Adapter | design | design_only |
| 2 | 数据域-L0数据接入/D-DATA-78 | Data Source Health Monitor | design | design_only |
| 3 | 数据域-L3存储优化/D-DATA-84 | Smart Scheduler | design | design_only |
| 4 | 数据域-参考数据/D-DATA-113 | Market Regime Reference Data | design | design_only |

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/data_eng/__init__.py | src/zephyr/data_eng/__init__.py | prototype | orphan |
| 2 | src/zephyr/data_eng/_extensions/__init__.py | src/zephyr/data_eng/_extensions/__ini... | scaffold_placeholder | orphan |
| 3 | src/zephyr/data_eng/api/__init__.py | src/zephyr/data_eng/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/data_eng/core/__init__.py | src/zephyr/data_eng/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/data_eng/infrastructure/__init__.py | src/zephyr/data_eng/infrastructure/__... | scaffold_placeholder | orphan |
| 6 | src/zephyr/data_eng/models/__init__.py | src/zephyr/data_eng/models/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/data_eng/services/__init__.py | src/zephyr/data_eng/services/__init__.py | scaffold_placeholder | orphan |

### 未分类 / Unclassified (136 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-DATA-ENG/ADWIN Drift Detection ADWIN漂移检测 | ADWIN Drift Detection ADWIN漂移检测 | design | design_only |
| 2 | D-DATA-ENG/AI Auto Feature Discoverer AI自动特征发现器 | AI Auto Feature Discoverer AI自动特征... | design | design_only |
| 3 | D-DATA-ENG/Airflow Pipeline Airflow流水线 | Airflow Pipeline Airflow流水线 | design | design_only |
| 4 | D-DATA-ENG/Alternative Data 另类数据 | Alternative Data 另类数据 | design | design_only |
| 5 | D-DATA-ENG/Apache Beam | Apache Beam | design | design_only |
| 6 | D-DATA-ENG/Apache Iceberg v3特性 Iceberg v3 Features | Apache Iceberg v3特性 Iceberg v3 Feat... | design | design_only |
| 7 | D-DATA-ENG/CI/CD门禁集成 CI/CD Gate Integration | CI/CD门禁集成 CI/CD Gate Integration | design | design_only |
| 8 | D-DATA-ENG/CQRS Dependency Node CQRS依赖图节点 | CQRS Dependency Node CQRS依赖图节点 | design | design_only |
| 9 | D-DATA-ENG/CQRS Event Sourcing CQRS事件溯源 | CQRS Event Sourcing CQRS事件溯源 | design | design_only |
| 10 | D-DATA-ENG/CTR-TRACE-001 Data Lineage Chain CTR-TRACE-001... | CTR-TRACE-001 Data Lineage Chain CTR-... | design | design_only |
| 11 | D-DATA-ENG/Cleaning & Anomaly Engine 清洗与异常引擎 | Cleaning & Anomaly Engine 清洗与异常引擎 | design | design_only |
| 12 | D-DATA-ENG/Column-Level Lineage 列级血缘 | Column-Level Lineage 列级血缘 | design | design_only |
| 13 | D-DATA-ENG/Core Pipeline 核心管线 | Core Pipeline 核心管线 | design | design_only |
| 14 | D-DATA-ENG/DDM Drift Detection DDM漂移检测 | DDM Drift Detection DDM漂移检测 | design | design_only |
| 15 | D-DATA-ENG/Data Fusion 数据融合 | Data Fusion 数据融合 | design | design_only |
| 16 | D-DATA-ENG/Data Lifecycle Management 数据生命周期管理 | Data Lifecycle Management 数据生命周... | design | design_only |
| 17 | D-DATA-ENG/Data Lineage & Traceability 数据血缘与可追溯性 | Data Lineage & Traceability 数据血缘... | design | design_only |
| 18 | D-DATA-ENG/Data Lineage Runtime Discovery 数据血缘运行时发现 | Data Lineage Runtime Discovery 数据血... | design | design_only |
| 19 | D-DATA-ENG/Data Lineage Tracking 数据血缘追踪 | Data Lineage Tracking 数据血缘追踪 | design | design_only |
| 20 | D-DATA-ENG/Data Observability Platform 数据可观测性平台 | Data Observability Platform 数据可观... | design | design_only |
| 21 | D-DATA-ENG/Data Quality Report 数据质量报告 | Data Quality Report 数据质量报告 | design | design_only |
| 22 | D-DATA-ENG/Data Scheduler 数据调度器 | Data Scheduler 数据调度器 | design | design_only |
| 23 | D-DATA-ENG/Data Source Approval 数据源审批 | Data Source Approval 数据源审批 | design | design_only |
| 24 | D-DATA-ENG/Data Source Development 数据源开发 | Data Source Development 数据源开发 | design | design_only |
| 25 | D-DATA-ENG/Data Source Evaluation 数据源评估 | Data Source Evaluation 数据源评估 | design | design_only |
| 26 | D-DATA-ENG/Data Source Full Rollout 数据源全量 | Data Source Full Rollout 数据源全量 | design | design_only |
| 27 | D-DATA-ENG/Data Source Grayscale 数据源灰度 | Data Source Grayscale 数据源灰度 | design | design_only |
| 28 | D-DATA-ENG/Data Source Validation 数据源验证 | Data Source Validation 数据源验证 | design | design_only |
| 29 | D-DATA-ENG/Data Vendor SLA Monitor 数据供应商SLA监控 | Data Vendor SLA Monitor 数据供应商SLA... | design | design_only |
| 30 | D-DATA-ENG/DataCatalogSync 数据目录同步 | DataCatalogSync 数据目录同步 | design | design_only |
| 31 | D-DATA-ENG/DataCompressionArchive 数据压缩归档 | DataCompressionArchive 数据压缩归档 | design | design_only |
| 32 | D-DATA-ENG/DataHub Data Catalog DataHub数据目录 | DataHub Data Catalog DataHub数据目录 | design | design_only |
| 33 | D-DATA-ENG/DataLakeManager 数据湖管理器 | DataLakeManager 数据湖管理器 | design | design_only |
| 34 | D-DATA-ENG/DataLineageTracker Dependency 数据血缘追踪依赖 | DataLineageTracker Dependency 数据血... | design | design_only |
| 35 | D-DATA-ENG/DataLineageTracker 数据血缘追踪器 | DataLineageTracker 数据血缘追踪器 | design | design_only |
| 36 | D-DATA-ENG/DataMesh Dependency Node 数据网格依赖图节点 | DataMesh Dependency Node 数据网格依赖... | design | design_only |
| 37 | D-DATA-ENG/DataMeshIntegrator Data Mesh集成器 | DataMeshIntegrator Data Mesh集成器 | design | design_only |
| 38 | D-DATA-ENG/DataPipeline 数据管线 | DataPipeline 数据管线 | design | design_only |
| 39 | D-DATA-ENG/DataProductManager 数据产品管理器 | DataProductManager 数据产品管理器 | design | design_only |
| 40 | D-DATA-ENG/DataProfiler 数据画像器 | DataProfiler 数据画像器 | design | design_only |
| 41 | D-DATA-ENG/DataQualityAlert 数据质量告警 | DataQualityAlert 数据质量告警 | design | design_only |
| 42 | D-DATA-ENG/DataQualityMonitor Dependency 数据质量监控依赖 | DataQualityMonitor Dependency 数据质... | design | design_only |
| 43 | D-DATA-ENG/DataReplicationSync 数据复制同步 | DataReplicationSync 数据复制同步 | design | design_only |
| 44 | D-DATA-ENG/Debezium CDC Debezium变更数据捕获 | Debezium CDC Debezium变更数据捕获 | design | design_only |
| 45 | D-DATA-ENG/Decision 10 TrainingDataManager独立子模块 | Decision 10 TrainingDataManager独立子... | design | design_only |
| 46 | D-DATA-ENG/Decision 11 知识清洗流水线入数据工程域 | Decision 11 知识清洗流水线入数据工程域 | design | design_only |
| 47 | D-DATA-ENG/Decision 12 SyntheticDataGenerator为P2 | Decision 12 SyntheticDataGenerator为P2 | design | design_only |
| 48 | D-DATA-ENG/Decision 13 CQRS/Event Sourcing为P3 | Decision 13 CQRS/Event Sourcing为P3 | design | design_only |
| 49 | D-DATA-ENG/Decision 3 FeatureStore从D-DATA-03拆出独立 | Decision 3 FeatureStore从D-DATA-03拆... | design | design_only |
| 50 | D-DATA-ENG/Decision 4 调度器从D-DATA-01拆出 | Decision 4 调度器从D-DATA-01拆出 | design | design_only |
| 51 | D-DATA-ENG/Decision 5 StreamProcessing入骨架 | Decision 5 StreamProcessing入骨架 | design | design_only |
| 52 | D-DATA-ENG/Decision 6 DataMesh暂不入骨架 | Decision 6 DataMesh暂不入骨架 | design | design_only |
| 53 | D-DATA-ENG/Decision 7 血缘追踪从D-DATA-05拆出 | Decision 7 血缘追踪从D-DATA-05拆出 | design | design_only |
| 54 | D-DATA-ENG/Decision 8 漂移感知调度独立子模块 | Decision 8 漂移感知调度独立子模块 | design | design_only |
| 55 | D-DATA-ENG/Decision 9 PIT Manager独立于FeatureStore | Decision 9 PIT Manager独立于FeatureStore | design | design_only |
| 56 | D-DATA-ENG/Deduplication 去重 | Deduplication 去重 | design | design_only |
| 57 | D-DATA-ENG/Denoising 去噪 | Denoising 去噪 | design | design_only |
| 58 | D-DATA-ENG/DriftAwareScheduler Dependency 漂移感知调度器依赖 | DriftAwareScheduler Dependency 漂移感... | design | design_only |
| 59 | D-DATA-ENG/DriftDetected 数据分布漂移检测 | DriftDetected 数据分布漂移检测 | design | design_only |
| 60 | D-DATA-ENG/ETL Pipeline ETL管线 | ETL Pipeline ETL管线 | design | design_only |
| 61 | D-DATA-ENG/ETLPipeline Dependency ETL管线依赖 | ETLPipeline Dependency ETL管线依赖 | design | design_only |
| 62 | D-DATA-ENG/Event-Triggered Collection 事件触发采集 | Event-Triggered Collection 事件触发采集 | design | design_only |
| 63 | D-DATA-ENG/Factor Formula 因子公式 | Factor Formula 因子公式 | design | design_only |
| 64 | D-DATA-ENG/Feast Feature Store Feast特征存储 | Feast Feature Store Feast特征存储 | design | design_only |
| 65 | D-DATA-ENG/Feature Store Architecture 特征存储架构 | Feature Store Architecture 特征存储架构 | design | design_only |
| 66 | D-DATA-ENG/Feature Store Offline 离线特征存储 | Feature Store Offline 离线特征存储 | design | design_only |
| 67 | D-DATA-ENG/FeatureStore Dependency 特征存储依赖 | FeatureStore Dependency 特征存储依赖 | design | design_only |
| 68 | D-DATA-ENG/FeatureStoreUpdated 特征存储更新完成 | FeatureStoreUpdated 特征存储更新完成 | design | design_only |
| 69 | D-DATA-ENG/Format Conversion 格式转换 | Format Conversion 格式转换 | design | design_only |
| 70 | D-DATA-ENG/GPUResourceManager Dependency GPU资源管理器依赖 | GPUResourceManager Dependency GPU资源... | design | design_only |
| 71 | D-DATA-ENG/GPUResourceManager GPU资源管理器 | GPUResourceManager GPU资源管理器 | design | design_only |
| 72 | D-DATA-ENG/Get Feature Lineage 获取特征血缘 | Get Feature Lineage 获取特征血缘 | design | design_only |
| 73 | D-DATA-ENG/Get Features 获取特征 | Get Features 获取特征 | design | design_only |
| 74 | D-DATA-ENG/Great Expectations Quality Engine Great Expect... | Great Expectations Quality Engine Gre... | design | design_only |
| 75 | D-DATA-ENG/Human-AI Collaboration 人机协作模式 | Human-AI Collaboration 人机协作模式 | design | design_only |
| 76 | D-DATA-ENG/Information Value Scoring 信息价值评分 | Information Value Scoring 信息价值评分 | design | design_only |
| 77 | D-DATA-ENG/Kappa Architecture Kappa架构 | Kappa Architecture Kappa架构 | design | design_only |
| 78 | D-DATA-ENG/KnowledgeCleaningPipeline Dependency 知识清洗... | KnowledgeCleaningPipeline Dependency ... | design | design_only |
| 79 | D-DATA-ENG/KnowledgeCleaningPipeline 知识清洗流水线 | KnowledgeCleaningPipeline 知识清洗流水线 | design | design_only |
| 80 | D-DATA-ENG/L0 to L1 Data Flow L0→L1数据流 | L0 to L1 Data Flow L0→L1数据流 | design | design_only |
| 81 | D-DATA-ENG/LLM Extraction LLM提取 | LLM Extraction LLM提取 | design | design_only |
| 82 | D-DATA-ENG/Lambda Architecture Lambda架构 | Lambda Architecture Lambda架构 | design | design_only |
| 83 | D-DATA-ENG/Lightweight GAN 轻量GAN | Lightweight GAN 轻量GAN | design | design_only |
| 84 | D-DATA-ENG/LineageGapDetected 血缘链断裂检测 | LineageGapDetected 血缘链断裂检测 | design | design_only |
| 85 | D-DATA-ENG/Manual Submission 手动提交 | Manual Submission 手动提交 | design | design_only |
| 86 | D-DATA-ENG/Marquez Lineage Backend Marquez血缘后端 | Marquez Lineage Backend Marquez血缘后端 | design | design_only |
| 87 | D-DATA-ENG/Memory Consolidation 记忆巩固 | Memory Consolidation 记忆巩固 | design | design_only |
| 88 | D-DATA-ENG/Memory Forgetting 记忆遗忘 | Memory Forgetting 记忆遗忘 | design | design_only |
| 89 | D-DATA-ENG/Memory Retrieval 记忆检索 | Memory Retrieval 记忆检索 | design | design_only |
| 90 | D-DATA-ENG/MinHash Similarity MinHash相似度 | MinHash Similarity MinHash相似度 | design | design_only |
| 91 | D-DATA-ENG/Model Training Pipeline 管线 | Model Training Pipeline 管线 | design | design_only |
| 92 | D-DATA-ENG/Multi-Source Cross Validator 多源交叉验证器 | Multi-Source Cross Validator 多源交叉... | design | design_only |
| 93 | D-DATA-ENG/Multi-Timeframe Data Fusion 多时间尺度数据融合 | Multi-Timeframe Data Fusion 多时间尺... | design | design_only |
| 94 | D-DATA-ENG/New Data Source Onboarding Flow 新数据源接入流程 | New Data Source Onboarding Flow 新数... | design | design_only |
| 95 | D-DATA-ENG/OpenLineage Lineage Standard OpenLineage血缘标准 | OpenLineage Lineage Standard OpenLine... | design | design_only |
| 96 | D-DATA-ENG/OpenLineage Standard Adaptation OpenLineage标... | OpenLineage Standard Adaptation OpenL... | design | design_only |
| 97 | D-DATA-ENG/OpenLineage Standard OpenLineage标准 | OpenLineage Standard OpenLineage标准 | design | design_only |
| 98 | D-DATA-ENG/PIT Data PIT数据 | PIT Data PIT数据 | design | design_only |
| 99 | D-DATA-ENG/PITManager Dependency PIT管理器依赖 | PITManager Dependency PIT管理器依赖 | design | design_only |
| 100 | D-DATA-ENG/PITManager PIT管理器 | PITManager PIT管理器 | design | design_only |
| 101 | D-DATA-ENG/Pipeline Orchestrator 数据管线编排 | Pipeline Orchestrator 数据管线编排 | design | design_only |
| 102 | D-DATA-ENG/PipelineCompleted 管线执行成功 | PipelineCompleted 管线执行成功 | design | design_only |
| 103 | D-DATA-ENG/PipelineFailed 管线执行失败 | PipelineFailed 管线执行失败 | design | design_only |
| 104 | D-DATA-ENG/PipelineOrchestrator Dependency 管线编排器依赖 | PipelineOrchestrator Dependency 管线... | design | design_only |
| 105 | D-DATA-ENG/PipelineOrchestrator 管线编排器 | PipelineOrchestrator 管线编排器 | design | design_only |
| 106 | D-DATA-ENG/Pre/Post Market Pipeline 盘前盘后管线 | Pre/Post Market Pipeline 盘前盘后管线 | design | design_only |
| 107 | D-DATA-ENG/Quality Gate Full-Pipeline Executor Quality Ga... | Quality Gate Full-Pipeline Executor Q... | design | design_only |
| 108 | D-DATA-ENG/Raw Knowledge Packet 原始知识包 | Raw Knowledge Packet 原始知识包 | design | design_only |
| 109 | D-DATA-ENG/Raw Market Data 原始行情 | Raw Market Data 原始行情 | design | design_only |
| 110 | D-DATA-ENG/Realtime Streaming 实时流处理 | Realtime Streaming 实时流处理 | design | design_only |
| 111 | D-DATA-ENG/Register Feature 注册特征 | Register Feature 注册特征 | design | design_only |
| 112 | D-DATA-ENG/Representation Learning Drift Detection 表示学... | Representation Learning Drift Detecti... | design | design_only |
| 113 | D-DATA-ENG/SMOTE Oversampling SMOTE过采样 | SMOTE Oversampling SMOTE过采样 | design | design_only |
| 114 | D-DATA-ENG/Scheduled Collection 定时采集 | Scheduled Collection 定时采集 | design | design_only |
| 115 | D-DATA-ENG/Schema Evolution Manager Schema演进管理 | Schema Evolution Manager Schema演进管理 | design | design_only |
| 116 | D-DATA-ENG/Schema Evolution Strategy Schema演进策略 | Schema Evolution Strategy Schema演进策略 | design | design_only |
| 117 | D-DATA-ENG/Signal Logic 信号逻辑 | Signal Logic 信号逻辑 | design | design_only |
| 118 | D-DATA-ENG/SimHash Similarity SimHash相似度 | SimHash Similarity SimHash相似度 | design | design_only |
| 119 | D-DATA-ENG/Smart Scheduler 智能调度器 | Smart Scheduler 智能调度器 | design | design_only |
| 120 | D-DATA-ENG/Speaker Diarization 说话人分离 | Speaker Diarization 说话人分离 | design | design_only |
| 121 | D-DATA-ENG/Storage Expansion Path 存储扩展路径 | Storage Expansion Path 存储扩展路径 | design | design_only |
| 122 | D-DATA-ENG/Storage Expansion Phase 1 存储扩展阶段1 | Storage Expansion Phase 1 存储扩展阶段1 | design | design_only |
| 123 | D-DATA-ENG/Storage Expansion Phase 2 存储扩展阶段2 | Storage Expansion Phase 2 存储扩展阶段2 | design | design_only |
| 124 | D-DATA-ENG/Storage Expansion Phase 3 存储扩展阶段3 | Storage Expansion Phase 3 存储扩展阶段3 | design | design_only |
| 125 | D-DATA-ENG/StreamProcessingEngine Dependency 流处理引擎依赖 | StreamProcessingEngine Dependency 流... | design | design_only |
| 126 | D-DATA-ENG/StreamProcessingEngine 流处理引擎 | StreamProcessingEngine 流处理引擎 | design | design_only |
| 127 | D-DATA-ENG/SyntheticDataGenerator Dependency Node 合成数... | SyntheticDataGenerator Dependency Nod... | design | design_only |
| 128 | D-DATA-ENG/Tech Stack Evolution 技术栈演进 | Tech Stack Evolution 技术栈演进 | design | design_only |
| 129 | D-DATA-ENG/Terminology Normalization 术语标准化 | Terminology Normalization 术语标准化 | design | design_only |
| 130 | D-DATA-ENG/TrainingDataManager Dependency 训练数据管理器依赖 | TrainingDataManager Dependency 训练数... | design | design_only |
| 131 | D-DATA-ENG/TrainingDataVersioned 训练数据集版本化完成 | TrainingDataVersioned 训练数据集版本... | design | design_only |
| 132 | D-DATA-ENG/架构不变量验证器 Architecture Invariant Validator | 架构不变量验证器 Architecture Invaria... | design | design_only |
| 133 | D-DATA-ENG/测试报告器 Test Reporter | 测试报告器 Test Reporter | design | design_only |
| 134 | D-DATA-ENG/清洗去重 Clean & Deduplicate | 清洗去重 Clean & Deduplicate | design | design_only |
| 135 | D-DATA-ENG/质量SLA违约预测器 Quality SLA Breach Predictor | 质量SLA违约预测器 Quality SLA Breach ... | design | design_only |
| 136 | D-DATA-ENG/质量门禁执行器 Quality Gate Executor | 质量门禁执行器 Quality Gate Executor | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 125 条 / 125 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 125 条 / 125 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 111 条 / edges                               │
│   [event]: 7 条 / edges                                          │
│   [contract]: 5 条 / edges                                       │
│   [runtime]: 1 条 / edges                                        │
│   [config_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (111 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Model Training Pipeline 管线 → 清洗去重 Clean & Deduplicate    │
│   Model Training Pipeline 管线 → Alternative Data 另类数据       │
│   Model Training Pipeline 管线 → Core Pipeline 核心管线          │
│   清洗去重 Clean & Deduplicate → DataLineageTracker 数据血...    │
│   DataLineageTracker 数据血... → Pre/Post Market Pipeline ...    │
│   DataLineageTracker 数据血... → Raw Market Data 原始行情        │
│   Pre/Post Market Pipeline ... → Smart Scheduler 智能调度器      │
│   Smart Scheduler 智能调度器 → Quality Gate Full-Pipelin...      │
│   Quality Gate Full-Pipelin... → Multi-Timeframe Data Fusi...    │
│   Apache Iceberg v3特性 Ice... → Scheduled Collection 定时...    │
│   Multi-Timeframe Data Fusi... → ETL Pipeline ETL管线            │
│   ETL Pipeline ETL管线 → Pipeline Orchestrator 数...             │
│   Pipeline Orchestrator 数... → Data Scheduler 数据调度器        │
│   Data Scheduler 数据调度器 → Schema Evolution Manager ...       │
│   Schema Evolution Manager ... → Data Observability Platfo...    │
│   Data Observability Platfo... → PipelineOrchestrator 管线...    │
│   PipelineOrchestrator 管线... → StreamProcessingEngine 流...    │
│   StreamProcessingEngine 流... → PITManager PIT管理器            │
│   PITManager PIT管理器 → KnowledgeCleaningPipeline...            │
│   KnowledgeCleaningPipeline... → GPUResourceManager GPU资...     │
│   GPUResourceManager GPU资... → DataLakeManager 数据湖管理器     │
│   GPUResourceManager GPU资... → Signal Logic 信号逻辑            │
│   DataLakeManager 数据湖管理器 → DataCompressionArchive 数...    │
│   DataCompressionArchive 数... → DataReplicationSync 数据...     │
│   DataReplicationSync 数据... → DataProfiler 数据画像器          │
│   DataProfiler 数据画像器 → DataCatalogSync 数据目录同步         │
│   DataCatalogSync 数据目录同步 → DataProductManager 数据产...    │
│   DataProductManager 数据产... → DataMeshIntegrator Data M...    │
│   DataMeshIntegrator Data M... → CQRS Event Sourcing CQRS...     │
│   CQRS Event Sourcing CQRS... → AI Auto Feature Discovere...     │
│   AI Auto Feature Discovere... → Cleaning & Anomaly Engine...    │
│   Cleaning & Anomaly Engine... → Multi-Source Cross Valida...    │
│   Multi-Source Cross Valida... → Airflow Pipeline Airflow...     │
│   Airflow Pipeline Airflow... → OpenLineage Standard Open...     │
│   Airflow Pipeline Airflow... → PIT Data PIT数据                 │
│   Raw Knowledge Packet 原始... → Event-Triggered Collectio...    │
│   OpenLineage Standard Open... → Data Lineage & Traceabili...    │
│   OpenLineage Standard Open... → DataMesh Dependency Node ...    │
│   Data Lineage & Traceabili... → OpenLineage Standard Adap...    │
│   OpenLineage Standard Adap... → Column-Level Lineage 列级...    │
│   OpenLineage Standard Adap... → CQRS Dependency Node CQRS...    │
│   Column-Level Lineage 列级... → Feature Store Architectur...    │
│   Feature Store Architectur... → DataPipeline 数据管线           │
│   DataPipeline 数据管线 → ETLPipeline Dependency ET...           │
│   ETLPipeline Dependency ET... → PipelineOrchestrator Depe...    │
│   PipelineOrchestrator Depe... → FeatureStore Dependency ...     │
│   FeatureStore Dependency ... → DataQualityMonitor Depend...     │
│   DataQualityMonitor Depend... → DataLineageTracker Depend...    │
│   DataQualityMonitor Depend... → Data Quality Report 数据...     │
│   ...还有 62 条 / 62 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[event]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (5 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (1 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 125 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `05_d_data_eng_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
