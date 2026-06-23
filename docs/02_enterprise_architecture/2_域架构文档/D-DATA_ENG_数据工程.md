---
doc_type: domain_architecture_doc
title: D-DATA_ENG 数据工程(增值+融合+知识)架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-DATA_ENG 数据工程(增值+融合+知识)架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-DATA_ENG |
| 域名称 | 数据工程(增值+融合+知识) |
| 架构层 | L1_foundation |
| 模块总数 | 147 |
| 设计态模块 | 140 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 数据工程域。负责数据增值处理、多源数据融合与知识提取，包括ETL管线、特征工程、数据融合引擎、知识图谱构建。拆分自原D-DATA域。 |

## 模块清单

共 147 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-DATA-ENG/ADWIN Drift Detection ADWIN漂移检测 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/AI Auto Feature Discoverer AI自动特征发现器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Airflow Pipeline Airflow流水线 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Alternative Data 另类数据 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Apache Beam |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Apache Iceberg v3特性 Iceberg v3 Features |  | design_only | design | 0 | 0 |
| D-DATA-ENG/CI/CD门禁集成 CI/CD Gate Integration |  | design_only | design | 0 | 0 |
| D-DATA-ENG/CQRS Dependency Node CQRS依赖图节点 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/CQRS Event Sourcing CQRS事件溯源 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/CTR-TRACE-001 Data Lineage Chain CTR-TRACE-001数据血缘链契约 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Cleaning & Anomaly Engine 清洗与异常引擎 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Column-Level Lineage 列级血缘 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Core Pipeline 核心管线 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DDM Drift Detection DDM漂移检测 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Fusion 数据融合 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Lifecycle Management 数据生命周期管理 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Lineage & Traceability 数据血缘与可追溯性 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Lineage Runtime Discovery 数据血缘运行时发现 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Lineage Tracking 数据血缘追踪 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Observability Platform 数据可观测性平台 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Quality Report 数据质量报告 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Scheduler 数据调度器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Source Approval 数据源审批 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Source Development 数据源开发 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Source Evaluation 数据源评估 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Source Full Rollout 数据源全量 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Source Grayscale 数据源灰度 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Source Validation 数据源验证 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Data Vendor SLA Monitor 数据供应商SLA监控 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataCatalogSync 数据目录同步 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataCompressionArchive 数据压缩归档 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataHub Data Catalog DataHub数据目录 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataLakeManager 数据湖管理器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataLineageTracker Dependency 数据血缘追踪依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataLineageTracker 数据血缘追踪器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataMesh Dependency Node 数据网格依赖图节点 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataMeshIntegrator Data Mesh集成器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataPipeline 数据管线 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataProductManager 数据产品管理器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataProfiler 数据画像器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataQualityAlert 数据质量告警 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataQualityMonitor Dependency 数据质量监控依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DataReplicationSync 数据复制同步 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Debezium CDC Debezium变更数据捕获 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 10 TrainingDataManager独立子模块 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 11 知识清洗流水线入数据工程域 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 12 SyntheticDataGenerator为P2 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 13 CQRS/Event Sourcing为P3 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 3 FeatureStore从D-DATA-03拆出独立 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 4 调度器从D-DATA-01拆出 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 5 StreamProcessing入骨架 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 6 DataMesh暂不入骨架 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 7 血缘追踪从D-DATA-05拆出 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 8 漂移感知调度独立子模块 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Decision 9 PIT Manager独立于FeatureStore |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Deduplication 去重 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Denoising 去噪 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DriftAwareScheduler Dependency 漂移感知调度器依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/DriftDetected 数据分布漂移检测 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/ETL Pipeline ETL管线 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/ETLPipeline Dependency ETL管线依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Event-Triggered Collection 事件触发采集 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Factor Formula 因子公式 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Feast Feature Store Feast特征存储 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Feature Store Architecture 特征存储架构 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Feature Store Offline 离线特征存储 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/FeatureStore Dependency 特征存储依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/FeatureStoreUpdated 特征存储更新完成 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Format Conversion 格式转换 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/GPUResourceManager Dependency GPU资源管理器依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/GPUResourceManager GPU资源管理器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Get Feature Lineage 获取特征血缘 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Get Features 获取特征 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Great Expectations Quality Engine Great Expectations质量引擎 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Human-AI Collaboration 人机协作模式 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Information Value Scoring 信息价值评分 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Kappa Architecture Kappa架构 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/KnowledgeCleaningPipeline Dependency 知识清洗流水线依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/KnowledgeCleaningPipeline 知识清洗流水线 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/L0 to L1 Data Flow L0→L1数据流 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/LLM Extraction LLM提取 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Lambda Architecture Lambda架构 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Lightweight GAN 轻量GAN |  | design_only | design | 0 | 0 |
| D-DATA-ENG/LineageGapDetected 血缘链断裂检测 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Manual Submission 手动提交 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Marquez Lineage Backend Marquez血缘后端 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Memory Consolidation 记忆巩固 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Memory Forgetting 记忆遗忘 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Memory Retrieval 记忆检索 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/MinHash Similarity MinHash相似度 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Model Training Pipeline 管线 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Multi-Source Cross Validator 多源交叉验证器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Multi-Timeframe Data Fusion 多时间尺度数据融合 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/New Data Source Onboarding Flow 新数据源接入流程 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/OpenLineage Lineage Standard OpenLineage血缘标准 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/OpenLineage Standard Adaptation OpenLineage标准适配 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/OpenLineage Standard OpenLineage标准 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/PIT Data PIT数据 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/PITManager Dependency PIT管理器依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/PITManager PIT管理器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Pipeline Orchestrator 数据管线编排 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/PipelineCompleted 管线执行成功 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/PipelineFailed 管线执行失败 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/PipelineOrchestrator Dependency 管线编排器依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/PipelineOrchestrator 管线编排器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Pre/Post Market Pipeline 盘前盘后管线 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Quality Gate Full-Pipeline Executor Quality Gate全流程执行器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Raw Knowledge Packet 原始知识包 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Raw Market Data 原始行情 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Realtime Streaming 实时流处理 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Register Feature 注册特征 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Representation Learning Drift Detection 表示学习漂移检测 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/SMOTE Oversampling SMOTE过采样 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Scheduled Collection 定时采集 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Schema Evolution Manager Schema演进管理 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Schema Evolution Strategy Schema演进策略 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Signal Logic 信号逻辑 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/SimHash Similarity SimHash相似度 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Smart Scheduler 智能调度器 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Speaker Diarization 说话人分离 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Storage Expansion Path 存储扩展路径 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Storage Expansion Phase 1 存储扩展阶段1 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Storage Expansion Phase 2 存储扩展阶段2 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Storage Expansion Phase 3 存储扩展阶段3 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/StreamProcessingEngine Dependency 流处理引擎依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/StreamProcessingEngine 流处理引擎 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/SyntheticDataGenerator Dependency Node 合成数据生成器依赖图节点 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Tech Stack Evolution 技术栈演进 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/Terminology Normalization 术语标准化 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/TrainingDataManager Dependency 训练数据管理器依赖 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/TrainingDataVersioned 训练数据集版本化完成 |  | design_only | design | 0 | 0 |
| D-DATA-ENG/架构不变量验证器 Architecture Invariant Validator |  | design_only | design | 0 | 0 |
| D-DATA-ENG/测试报告器 Test Reporter |  | design_only | design | 0 | 0 |
| D-DATA-ENG/清洗去重 Clean & Deduplicate |  | design_only | design | 0 | 0 |
| D-DATA-ENG/质量SLA违约预测器 Quality SLA Breach Predictor |  | design_only | design | 0 | 0 |
| D-DATA-ENG/质量门禁执行器 Quality Gate Executor |  | design_only | design | 0 | 0 |
| src/zephyr/data_eng/__init__.py | MOD-DATA_ENG | orphan | prototype | 0 | 0 |
| src/zephyr/data_eng/_extensions/__init__.py | MOD-DATA_ENG | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_eng/api/__init__.py | MOD-DATA_ENG | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_eng/core/__init__.py | MOD-DATA_ENG | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_eng/infrastructure/__init__.py | MOD-DATA_ENG | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_eng/models/__init__.py | MOD-DATA_ENG | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/data_eng/services/__init__.py | MOD-DATA_ENG | orphan | scaffold_placeholder | 0 | 0 |
| 数据域-L0数据接入/D-DATA-67 | MOD-DATA_ENG | design_only | design | 0 | 0 |
| 数据域-L0数据接入/D-DATA-78 | MOD-DATA_ENG | design_only | design | 0 | 0 |
| 数据域-L3存储优化/D-DATA-84 | MOD-DATA_ENG | design_only | design | 0 | 0 |
| 数据域-参考数据/D-DATA-113 | MOD-DATA_ENG | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INFRA_RUNTIME | 20 | event,data,contract,config_depends,domain_dependency |
| D-SHARED | 4 | contract,event,data |
| D-EX_SOR | 4 | event,contract,data |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 29 | event,contract,data,config_depends |
| D-RISK | 26 | event,contract,data,config_depends |
| D-GOVERNANCE | 26 | data,event,contract,config_depends |
| D-MKT_DATA | 21 | data,contract,event,domain_dependency |
| D-AUTONOMY_CORE | 20 | data,contract,event,config_depends |
| D-SECURITY | 17 | contract,event,data,config_depends |
| D-INTEGRATION | 16 | config_depends,event,contract,data |
| D-FACTOR | 14 | event,data,config_depends,contract,domain_dependency |
| D-SIGNAL | 13 | event,data,contract |
| D-PF_CORE | 9 | contract,event,config_depends,data |
| D-OPS | 9 | data,contract,config_depends,event |
| D-REPORTING | 8 | contract,event,data,config_depends,domain_dependency |
| D-KNOWLEDGE | 8 | contract,event,data,domain_dependency |
| D-SELL_DECISION | 6 | contract,event,data |
| D-INFRA_OPS | 6 | event,contract,data |
| D-ML_TRAIN | 5 | event,contract,config_depends,domain_dependency |
| D-FRONTEND | 5 | data,event,contract |
| D-CROSS_ASSET | 5 | contract,data,config_depends |
| D-AUTONOMY_PERM | 5 | event,data,contract |
| D-TRADING | 4 | config_depends,data,contract |
| D-SIMULATION | 4 | data,event,contract |
| D-POSITION | 4 | config_depends,contract,data |
| D-PF_ALLOC | 4 | event,contract |
| D-INTELLIGENCE | 4 | config_depends,data,event |
| D-EX_CORE | 4 | contract,data |
| D-ALT_DATA | 4 | event,contract,domain_dependency |
| D-ML_SERVE | 3 | contract,data |
| D-DATA_GOV | 2 | contract,config_depends |

## 域内依赖图

详见 [d_data_eng_dependency.mmd](d_data_eng_dependency.mmd)
