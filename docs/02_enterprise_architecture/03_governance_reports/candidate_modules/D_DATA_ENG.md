---
doc_type: audit_report
title: 候选模块清单 — D_DATA_ENG
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_DATA_ENG 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **93** 条（原有 0 + harvest 93）。
> harvest 去重四态: likely_new=93

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0297 | Model Training Pipeline 管线 | / D-ML-01 / Model Training Pipeline / ✅ 能建 / 📋 项目内有蓝图编号ML-EXPERIMENT-DOMAIN-001已建设 / 模型训练+验证+超参搜索(PyTorch+RTX3090) / | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0537 | 清洗去重 Clean & Deduplicate | L0→L1流水线清洗去重缺口填补 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0591 | DataLineageTracker 数据血缘追踪器 | 数据血缘追踪端到端血缘列级溯源变换算子注册版本快照关联影响分析 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0593 | Pre/Post Market Pipeline 盘前盘后管线 | 盘后数据就绪时间集合竞价处理盘后校验 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0598 | Smart Scheduler 智能调度器 | 基于数据就绪状态触发+依赖感知+优先级调度 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0605 | Quality Gate Full-Pipeline Executor Quality Gate全流程执行器 | / Quality Gate L1~L4 / 全量执行L1格式/L2逻辑/L3统计/L4血缘 / 全部通过 / 按级别处理 / D-DATA-57 / | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0640 | Multi-Timeframe Data Fusion 多时间尺度数据融合 | 跨频率对齐+时间戳统一+前向填充+频率转换+融合质量评分 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0647 | ETL Pipeline ETL管线 | 抽取+转换+加载+增量同步 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0648 | Pipeline Orchestrator 数据管线编排 | DAG调度+依赖管理+重试 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0649 | Data Scheduler 数据调度器 | 定时任务+优先级队列+分时段调度 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0650 | Schema Evolution Manager Schema演进管理 | 兼容性检查+迁移 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0651 | Data Observability Platform 数据可观测性平台 | 数据健康度+异常检测+根因分析+SLA监控+可靠性评分 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0799 | PipelineOrchestrator 管线编排器 | 管线编排DAG调度依赖管理重试分时段调度 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0800 | StreamProcessingEngine 流处理引擎 | 流处理引擎实时计算窗口聚合事件时间对齐水位线背压控制 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0801 | PITManager PIT管理器 | PIT管理器DuckDB AS OF JOIN时间旅行查询任意历史时点特征快照重建PIT门控联动 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0802 | KnowledgeCleaningPipeline 知识清洗流水线 | 知识清洗流水线格式转换去重去噪术语标准化说话人分离信息价值评分 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0803 | GPUResourceManager GPU资源管理器 | GPU资源管理器PyTorch CUDA内存分区时段优先调度显存预算管理OOM防护 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0804 | DataLakeManager 数据湖管理器 | 数据湖管理分层存储热温冷生命周期 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0805 | DataCompressionArchive 数据压缩归档 | 数据压缩归档冷热分离自动归档Parquet ZSTD | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0806 | DataReplicationSync 数据复制同步 | 数据复制同步跨源同步一致性保证CDC Debezium | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0807 | DataProfiler 数据画像器 | 数据画像统计分布异常检测 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0808 | DataCatalogSync 数据目录同步 | 数据目录同步元数据自动采集搜索DataHub | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0810 | DataProductManager 数据产品管理器 | 数据产品管理器产品定义目录版本评估退役 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0811 | DataMeshIntegrator Data Mesh集成器 | Data Mesh集成器域导向去中心化联邦治理 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0812 | CQRS Event Sourcing CQRS事件溯源 | 命令查询职责分离+事件溯源读写分离+完整事件历史 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1349 | AI Auto Feature Discoverer AI自动特征发现器 | AI自动特征发现+特征评估+特征选择 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1352 | Cleaning & Anomaly Engine 清洗与异常引擎 | 自动化数据清洗+异常检测+标记+自动修复+人工审核 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1356 | Multi-Source Cross Validator 多源交叉验证器 | 多源数据交叉验证+数据比对算法+同步冲突检测 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1357 | Airflow Pipeline Airflow流水线 | Airflow工作流+自动化数据采集/处理/验证/存储+DAG定义 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2237 | OpenLineage Standard OpenLineage标准 | OpenLineage标准适配Run D-FACTOR-04 Pipeline批次Job因子计算信号生成决策Dataset Parquet分区 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2389 | Data Lineage & Traceability 数据血缘与可追溯性 | 数据血缘与可追溯性血缘链全景数据源到L0接入到L1因子到L2信号到L3决策到L4执行到L5闭环列级血缘5层级 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2390 | OpenLineage Standard Adaptation OpenLineage标准适配 | OpenLineage标准适配4概念Run到Job到Dataset到Facet MVP SQLite存储血缘覆盖L0到L1到L2 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2411 | Column-Level Lineage 列级血缘 | 列级血缘5层级L0到L1 close(miniQMT)清洗+复权close_adj到L1到L1 close_adj pct_change(20) momentum_20d到L2到L3到L4 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2621 | Feature Store Architecture 特征存储架构 | 离线PIT+在线Serving+特征注册表四维索引 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3716 | DataPipeline 数据管线 | 核心Aggregate数据管线 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3717 | ETLPipeline Dependency ETL管线依赖 | 流处理结果→ETL处理 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3718 | PipelineOrchestrator Dependency 管线编排器依赖 | ETL任务→编排器管理 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3719 | FeatureStore Dependency 特征存储依赖 | ETL产出→特征存储 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3720 | DataQualityMonitor Dependency 数据质量监控依赖 | 管线执行→质量监控 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3721 | DataLineageTracker Dependency 数据血缘追踪依赖 | 管线执行→血缘追踪 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3722 | StreamProcessingEngine Dependency 流处理引擎依赖 | 流处理结果→ETL处理 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3723 | DriftAwareScheduler Dependency 漂移感知调度器依赖 | 漂移感知→编排器调整采集频率 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3724 | PITManager Dependency PIT管理器依赖 | / DEG-08 / DEG-03 / PIT数据支撑 / PIT Manager→FeatureStore底层时间旅行查询 / | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3725 | TrainingDataManager Dependency 训练数据管理器依赖 | / DEG-09 / DEG-03 / 训练数据组装 / TrainingDataManager消费FeatureStore特征值 / | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3726 | KnowledgeCleaningPipeline Dependency 知识清洗流水线依赖 | 清洗流水线→质量监控联合判定 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3727 | GPUResourceManager Dependency GPU资源管理器依赖 | GPU资源管理→ETL管线显存预算 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3729 | Format Conversion 格式转换 | 音频/视频→Whisper转写PDF→文本提取 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3730 | Deduplication 去重 | 精确去重+近似去重SimHash/MinHash+跨源去重 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3731 | Denoising 去噪 | 口语化填充词去除+重复语句合并+无关内容裁剪 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3732 | Terminology Normalization 术语标准化 | 口语→标准术语+股票代码标准化+板块名称标准化 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3733 | Speaker Diarization 说话人分离 | 多人对话分离各说话人+标记分析师 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3734 | Information Value Scoring 信息价值评分 | LLM多维度评分相关性时效性信息量可靠性 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3735 | Data Lineage Tracking 数据血缘追踪 | OpenLineage标准数据血缘追踪全链路 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3736 | ADWIN Drift Detection ADWIN漂移检测 | ADWIN均值漂移检测算法 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3737 | DDM Drift Detection DDM漂移检测 | DDM分布变化检测算法 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3740 | Representation Learning Drift Detection 表示学习漂移检测 | 模型中间层表示变化检测Wasserstein距离 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3745 | Feature Store Offline 离线特征存储 | Parquet+Feature Store Offline | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3751 | Great Expectations Quality Engine Great Expectations质量引擎 | 自建+Great Expectations质量检查 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3752 | OpenLineage Lineage Standard OpenLineage血缘标准 | SQLite+OpenLineage血缘追踪 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3753 | Marquez Lineage Backend Marquez血缘后端 | OpenLineage+Marquez血缘追踪 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3754 | DataHub Data Catalog DataHub数据目录 | 数据目录同步+元数据自动采集+搜索 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3755 | Debezium CDC Debezium变更数据捕获 | 数据复制同步+跨源同步+CDC/Debezium | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3765 | Feast Feature Store Feast特征存储 | 自建+Feast YAML参考 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3769 | SimHash Similarity SimHash相似度 | 近似去重SimHash/MinHash相似度>0.9 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3770 | MinHash Similarity MinHash相似度 | 近似去重SimHash/MinHash相似度>0.9 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3771 | SMOTE Oversampling SMOTE过采样 | SMOTE过采样稀有市场条件数据增强 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3772 | Lightweight GAN 轻量GAN | 轻量GAN生成合成行情数据训练增强 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3773 | Human-AI Collaboration 人机协作模式 | AI自动采集+提取→人类PM审核+补充 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3774 | Scheduled Collection 定时采集 | 每日固定时间抓取指定直播/专栏 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3775 | Event-Triggered Collection 事件触发采集 | 重大政策发布触发相关分析师内容采集 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3776 | Manual Submission 手动提交 | 用户粘贴文字内容上传PDF/音频/视频 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3777 | New Data Source Onboarding Flow 新数据源接入流程 | 评估→审批→开发→验证→灰度→全量 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3778 | Schema Evolution Strategy Schema演进策略 | 新增列/删除列/修改列类型/重命名列/Schema版本 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3779 | Storage Expansion Path 存储扩展路径 | AUM驱动阶段1/2/3存储扩展 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3780 | Tech Stack Evolution 技术栈演进 | 热/温/冷存储+特征存储+事件存储+血缘追踪演进 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3781 | Data Source Evaluation 数据源评估 | 评估数据质量ROI分析 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3782 | Data Source Approval 数据源审批 | 人工审批B-012约束 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3783 | Data Source Development 数据源开发 | Connector+Schema开发 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3784 | Data Source Validation 数据源验证 | 质量门禁L1~L4验证 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3785 | Data Source Grayscale 数据源灰度 | 5%→20%监控7天 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3786 | Data Source Full Rollout 数据源全量 | 100%持续监控 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3787 | LLM Extraction LLM提取 | 从原始记录中提取关键事实/模式 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3788 | Memory Consolidation 记忆巩固 | 去重+冲突解决+版本化 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3789 | Memory Retrieval 记忆检索 | 按相关性召回记忆FAISS向量检索 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3790 | Memory Forgetting 记忆遗忘 | 衰减/归档/删除过期记忆90天热→1年温→7年冷 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3791 | Data Lifecycle Management 数据生命周期管理 | 90天热→1年温→7年冷分级衰减 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3954 | Data Vendor SLA Monitor 数据供应商SLA监控 | 数据供应商SLA监控 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3959 | Data Lineage Runtime Discovery 数据血缘运行时发现 | 数据血缘运行时发现 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3970 | 测试报告器 Test Reporter | 测试报告器 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3971 | 质量门禁执行器 Quality Gate Executor | 质量门禁执行器 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3972 | 架构不变量验证器 Architecture Invariant Validator | 架构不变量验证器 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3976 | 质量SLA违约预测器 Quality SLA Breach Predictor | 质量SLA违约预测器 | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4230 | Realtime Streaming 实时流处理 | / realtime_streaming.py / governance/ / 实时流处理 / ❌ 属于D-DATA-ENG——流处理是数据工程域 / | D_DATA_ENG | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（93 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0297 | Model Training Pipeline 管线 | / D-ML-01 / Model Training Pipeline / ✅ 能建 / 📋 项目内有蓝图编号ML-EXPERIMENT-DOMAIN-001已建设 / 模型训练+验证+超参搜索(PyTorch+RTX3090) / | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0537 | 清洗去重 Clean & Deduplicate | L0→L1流水线清洗去重缺口填补 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0591 | DataLineageTracker 数据血缘追踪器 | 数据血缘追踪端到端血缘列级溯源变换算子注册版本快照关联影响分析 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0593 | Pre/Post Market Pipeline 盘前盘后管线 | 盘后数据就绪时间集合竞价处理盘后校验 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0598 | Smart Scheduler 智能调度器 | 基于数据就绪状态触发+依赖感知+优先级调度 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0605 | Quality Gate Full-Pipeline Executor Quality Gate全流程执行器 | / Quality Gate L1~L4 / 全量执行L1格式/L2逻辑/L3统计/L4血缘 / 全部通过 / 按级别处理 / D-DATA-57 / | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0640 | Multi-Timeframe Data Fusion 多时间尺度数据融合 | 跨频率对齐+时间戳统一+前向填充+频率转换+融合质量评分 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0647 | ETL Pipeline ETL管线 | 抽取+转换+加载+增量同步 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0648 | Pipeline Orchestrator 数据管线编排 | DAG调度+依赖管理+重试 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0649 | Data Scheduler 数据调度器 | 定时任务+优先级队列+分时段调度 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0650 | Schema Evolution Manager Schema演进管理 | 兼容性检查+迁移 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0651 | Data Observability Platform 数据可观测性平台 | 数据健康度+异常检测+根因分析+SLA监控+可靠性评分 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0799 | PipelineOrchestrator 管线编排器 | 管线编排DAG调度依赖管理重试分时段调度 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0800 | StreamProcessingEngine 流处理引擎 | 流处理引擎实时计算窗口聚合事件时间对齐水位线背压控制 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0801 | PITManager PIT管理器 | PIT管理器DuckDB AS OF JOIN时间旅行查询任意历史时点特征快照重建PIT门控联动 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0802 | KnowledgeCleaningPipeline 知识清洗流水线 | 知识清洗流水线格式转换去重去噪术语标准化说话人分离信息价值评分 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0803 | GPUResourceManager GPU资源管理器 | GPU资源管理器PyTorch CUDA内存分区时段优先调度显存预算管理OOM防护 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0804 | DataLakeManager 数据湖管理器 | 数据湖管理分层存储热温冷生命周期 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0805 | DataCompressionArchive 数据压缩归档 | 数据压缩归档冷热分离自动归档Parquet ZSTD | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0806 | DataReplicationSync 数据复制同步 | 数据复制同步跨源同步一致性保证CDC Debezium | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0807 | DataProfiler 数据画像器 | 数据画像统计分布异常检测 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0808 | DataCatalogSync 数据目录同步 | 数据目录同步元数据自动采集搜索DataHub | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0810 | DataProductManager 数据产品管理器 | 数据产品管理器产品定义目录版本评估退役 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0811 | DataMeshIntegrator Data Mesh集成器 | Data Mesh集成器域导向去中心化联邦治理 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-0812 | CQRS Event Sourcing CQRS事件溯源 | 命令查询职责分离+事件溯源读写分离+完整事件历史 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-1349 | AI Auto Feature Discoverer AI自动特征发现器 | AI自动特征发现+特征评估+特征选择 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-1352 | Cleaning & Anomaly Engine 清洗与异常引擎 | 自动化数据清洗+异常检测+标记+自动修复+人工审核 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-1356 | Multi-Source Cross Validator 多源交叉验证器 | 多源数据交叉验证+数据比对算法+同步冲突检测 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-1357 | Airflow Pipeline Airflow流水线 | Airflow工作流+自动化数据采集/处理/验证/存储+DAG定义 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-2237 | OpenLineage Standard OpenLineage标准 | OpenLineage标准适配Run D-FACTOR-04 Pipeline批次Job因子计算信号生成决策Dataset Parquet分区 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-2389 | Data Lineage & Traceability 数据血缘与可追溯性 | 数据血缘与可追溯性血缘链全景数据源到L0接入到L1因子到L2信号到L3决策到L4执行到L5闭环列级血缘5层级 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-2390 | OpenLineage Standard Adaptation OpenLineage标准适配 | OpenLineage标准适配4概念Run到Job到Dataset到Facet MVP SQLite存储血缘覆盖L0到L1到L2 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-2411 | Column-Level Lineage 列级血缘 | 列级血缘5层级L0到L1 close(miniQMT)清洗+复权close_adj到L1到L1 close_adj pct_change(20) momentum_20d到L2到L3到L4 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-2621 | Feature Store Architecture 特征存储架构 | 离线PIT+在线Serving+特征注册表四维索引 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3716 | DataPipeline 数据管线 | 核心Aggregate数据管线 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3717 | ETLPipeline Dependency ETL管线依赖 | 流处理结果→ETL处理 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3718 | PipelineOrchestrator Dependency 管线编排器依赖 | ETL任务→编排器管理 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3719 | FeatureStore Dependency 特征存储依赖 | ETL产出→特征存储 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3720 | DataQualityMonitor Dependency 数据质量监控依赖 | 管线执行→质量监控 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3721 | DataLineageTracker Dependency 数据血缘追踪依赖 | 管线执行→血缘追踪 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3722 | StreamProcessingEngine Dependency 流处理引擎依赖 | 流处理结果→ETL处理 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3723 | DriftAwareScheduler Dependency 漂移感知调度器依赖 | 漂移感知→编排器调整采集频率 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3724 | PITManager Dependency PIT管理器依赖 | / DEG-08 / DEG-03 / PIT数据支撑 / PIT Manager→FeatureStore底层时间旅行查询 / | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3725 | TrainingDataManager Dependency 训练数据管理器依赖 | / DEG-09 / DEG-03 / 训练数据组装 / TrainingDataManager消费FeatureStore特征值 / | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3726 | KnowledgeCleaningPipeline Dependency 知识清洗流水线依赖 | 清洗流水线→质量监控联合判定 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3727 | GPUResourceManager Dependency GPU资源管理器依赖 | GPU资源管理→ETL管线显存预算 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3729 | Format Conversion 格式转换 | 音频/视频→Whisper转写PDF→文本提取 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3730 | Deduplication 去重 | 精确去重+近似去重SimHash/MinHash+跨源去重 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3731 | Denoising 去噪 | 口语化填充词去除+重复语句合并+无关内容裁剪 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3732 | Terminology Normalization 术语标准化 | 口语→标准术语+股票代码标准化+板块名称标准化 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3733 | Speaker Diarization 说话人分离 | 多人对话分离各说话人+标记分析师 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3734 | Information Value Scoring 信息价值评分 | LLM多维度评分相关性时效性信息量可靠性 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3735 | Data Lineage Tracking 数据血缘追踪 | OpenLineage标准数据血缘追踪全链路 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3736 | ADWIN Drift Detection ADWIN漂移检测 | ADWIN均值漂移检测算法 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3737 | DDM Drift Detection DDM漂移检测 | DDM分布变化检测算法 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3740 | Representation Learning Drift Detection 表示学习漂移检测 | 模型中间层表示变化检测Wasserstein距离 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3745 | Feature Store Offline 离线特征存储 | Parquet+Feature Store Offline | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3751 | Great Expectations Quality Engine Great Expectations质量引擎 | 自建+Great Expectations质量检查 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3752 | OpenLineage Lineage Standard OpenLineage血缘标准 | SQLite+OpenLineage血缘追踪 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3753 | Marquez Lineage Backend Marquez血缘后端 | OpenLineage+Marquez血缘追踪 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3754 | DataHub Data Catalog DataHub数据目录 | 数据目录同步+元数据自动采集+搜索 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3755 | Debezium CDC Debezium变更数据捕获 | 数据复制同步+跨源同步+CDC/Debezium | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3765 | Feast Feature Store Feast特征存储 | 自建+Feast YAML参考 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3769 | SimHash Similarity SimHash相似度 | 近似去重SimHash/MinHash相似度>0.9 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3770 | MinHash Similarity MinHash相似度 | 近似去重SimHash/MinHash相似度>0.9 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3771 | SMOTE Oversampling SMOTE过采样 | SMOTE过采样稀有市场条件数据增强 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3772 | Lightweight GAN 轻量GAN | 轻量GAN生成合成行情数据训练增强 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3773 | Human-AI Collaboration 人机协作模式 | AI自动采集+提取→人类PM审核+补充 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3774 | Scheduled Collection 定时采集 | 每日固定时间抓取指定直播/专栏 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3775 | Event-Triggered Collection 事件触发采集 | 重大政策发布触发相关分析师内容采集 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3776 | Manual Submission 手动提交 | 用户粘贴文字内容上传PDF/音频/视频 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3777 | New Data Source Onboarding Flow 新数据源接入流程 | 评估→审批→开发→验证→灰度→全量 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3778 | Schema Evolution Strategy Schema演进策略 | 新增列/删除列/修改列类型/重命名列/Schema版本 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3779 | Storage Expansion Path 存储扩展路径 | AUM驱动阶段1/2/3存储扩展 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3780 | Tech Stack Evolution 技术栈演进 | 热/温/冷存储+特征存储+事件存储+血缘追踪演进 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3781 | Data Source Evaluation 数据源评估 | 评估数据质量ROI分析 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3782 | Data Source Approval 数据源审批 | 人工审批B-012约束 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3783 | Data Source Development 数据源开发 | Connector+Schema开发 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3784 | Data Source Validation 数据源验证 | 质量门禁L1~L4验证 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3785 | Data Source Grayscale 数据源灰度 | 5%→20%监控7天 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3786 | Data Source Full Rollout 数据源全量 | 100%持续监控 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3787 | LLM Extraction LLM提取 | 从原始记录中提取关键事实/模式 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3788 | Memory Consolidation 记忆巩固 | 去重+冲突解决+版本化 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3789 | Memory Retrieval 记忆检索 | 按相关性召回记忆FAISS向量检索 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3790 | Memory Forgetting 记忆遗忘 | 衰减/归档/删除过期记忆90天热→1年温→7年冷 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3791 | Data Lifecycle Management 数据生命周期管理 | 90天热→1年温→7年冷分级衰减 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3954 | Data Vendor SLA Monitor 数据供应商SLA监控 | 数据供应商SLA监控 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3959 | Data Lineage Runtime Discovery 数据血缘运行时发现 | 数据血缘运行时发现 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3970 | 测试报告器 Test Reporter | 测试报告器 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3971 | 质量门禁执行器 Quality Gate Executor | 质量门禁执行器 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3972 | 架构不变量验证器 Architecture Invariant Validator | 架构不变量验证器 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-3976 | 质量SLA违约预测器 Quality SLA Breach Predictor | 质量SLA违约预测器 | D_DATA_ENG | harvest待评估（likely_new） |  |
| CAND-HARVEST-4230 | Realtime Streaming 实时流处理 | / realtime_streaming.py / governance/ / 实时流处理 / ❌ 属于D-DATA-ENG——流处理是数据工程域 / | D_DATA_ENG | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0297 | Model Training Pipeline 管线 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0537 | 清洗去重 Clean & Deduplicate | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0591 | DataLineageTracker 数据血缘追踪器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0593 | Pre/Post Market Pipeline 盘前盘后管线 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0598 | Smart Scheduler 智能调度器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0605 | Quality Gate Full-Pipeline Executor Quality Gate全流程执行器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0640 | Multi-Timeframe Data Fusion 多时间尺度数据融合 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0647 | ETL Pipeline ETL管线 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0648 | Pipeline Orchestrator 数据管线编排 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0649 | Data Scheduler 数据调度器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0650 | Schema Evolution Manager Schema演进管理 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0651 | Data Observability Platform 数据可观测性平台 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0799 | PipelineOrchestrator 管线编排器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0800 | StreamProcessingEngine 流处理引擎 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0801 | PITManager PIT管理器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0802 | KnowledgeCleaningPipeline 知识清洗流水线 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0803 | GPUResourceManager GPU资源管理器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0804 | DataLakeManager 数据湖管理器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0805 | DataCompressionArchive 数据压缩归档 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0806 | DataReplicationSync 数据复制同步 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0807 | DataProfiler 数据画像器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0808 | DataCatalogSync 数据目录同步 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0810 | DataProductManager 数据产品管理器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0811 | DataMeshIntegrator Data Mesh集成器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0812 | CQRS Event Sourcing CQRS事件溯源 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1349 | AI Auto Feature Discoverer AI自动特征发现器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1352 | Cleaning & Anomaly Engine 清洗与异常引擎 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1356 | Multi-Source Cross Validator 多源交叉验证器 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1357 | Airflow Pipeline Airflow流水线 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2237 | OpenLineage Standard OpenLineage标准 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2389 | Data Lineage & Traceability 数据血缘与可追溯性 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2390 | OpenLineage Standard Adaptation OpenLineage标准适配 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2411 | Column-Level Lineage 列级血缘 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2621 | Feature Store Architecture 特征存储架构 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3716 | DataPipeline 数据管线 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3717 | ETLPipeline Dependency ETL管线依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3718 | PipelineOrchestrator Dependency 管线编排器依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3719 | FeatureStore Dependency 特征存储依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3720 | DataQualityMonitor Dependency 数据质量监控依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3721 | DataLineageTracker Dependency 数据血缘追踪依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3722 | StreamProcessingEngine Dependency 流处理引擎依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3723 | DriftAwareScheduler Dependency 漂移感知调度器依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3724 | PITManager Dependency PIT管理器依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3725 | TrainingDataManager Dependency 训练数据管理器依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3726 | KnowledgeCleaningPipeline Dependency 知识清洗流水线依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3727 | GPUResourceManager Dependency GPU资源管理器依赖 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3729 | Format Conversion 格式转换 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3730 | Deduplication 去重 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3731 | Denoising 去噪 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3732 | Terminology Normalization 术语标准化 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3733 | Speaker Diarization 说话人分离 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3734 | Information Value Scoring 信息价值评分 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3735 | Data Lineage Tracking 数据血缘追踪 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3736 | ADWIN Drift Detection ADWIN漂移检测 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3737 | DDM Drift Detection DDM漂移检测 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3740 | Representation Learning Drift Detection 表示学习漂移检测 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3745 | Feature Store Offline 离线特征存储 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3751 | Great Expectations Quality Engine Great Expectations质量引擎 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3752 | OpenLineage Lineage Standard OpenLineage血缘标准 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3753 | Marquez Lineage Backend Marquez血缘后端 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3754 | DataHub Data Catalog DataHub数据目录 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3755 | Debezium CDC Debezium变更数据捕获 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3765 | Feast Feature Store Feast特征存储 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3769 | SimHash Similarity SimHash相似度 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3770 | MinHash Similarity MinHash相似度 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3771 | SMOTE Oversampling SMOTE过采样 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3772 | Lightweight GAN 轻量GAN | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3773 | Human-AI Collaboration 人机协作模式 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3774 | Scheduled Collection 定时采集 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3775 | Event-Triggered Collection 事件触发采集 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3776 | Manual Submission 手动提交 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3777 | New Data Source Onboarding Flow 新数据源接入流程 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3778 | Schema Evolution Strategy Schema演进策略 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3779 | Storage Expansion Path 存储扩展路径 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3780 | Tech Stack Evolution 技术栈演进 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3781 | Data Source Evaluation 数据源评估 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3782 | Data Source Approval 数据源审批 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3783 | Data Source Development 数据源开发 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3784 | Data Source Validation 数据源验证 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3785 | Data Source Grayscale 数据源灰度 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3786 | Data Source Full Rollout 数据源全量 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3787 | LLM Extraction LLM提取 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3788 | Memory Consolidation 记忆巩固 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3789 | Memory Retrieval 记忆检索 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3790 | Memory Forgetting 记忆遗忘 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3791 | Data Lifecycle Management 数据生命周期管理 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3954 | Data Vendor SLA Monitor 数据供应商SLA监控 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3959 | Data Lineage Runtime Discovery 数据血缘运行时发现 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3970 | 测试报告器 Test Reporter | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3971 | 质量门禁执行器 Quality Gate Executor | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3972 | 架构不变量验证器 Architecture Invariant Validator | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3976 | 质量SLA违约预测器 Quality SLA Breach Predictor | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4230 | Realtime Streaming 实时流处理 | D_DATA_ENG | 候选待评（candidate） | harvest待评估（likely_new） |
