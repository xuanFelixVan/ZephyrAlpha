---
doc_type: domain_architecture_doc
title: D-INTELLIGENCE context_management架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-INTELLIGENCE context_management架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-INTELLIGENCE |
| 域名称 | context_management |
| 架构层 | L2_domain |
| 模块总数 | 273 |
| 设计态模块 | 217 |
| 原型态模块 | 32 |
| 生产态模块 | 18 |
| 容量 | 18/150 (正常) |
| 描述 | 上下文预算管理(context_budget/token_budget) |

## 模块清单

共 273 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-INTELLIGENCE/3阶段决策门控 3-Stage Decision Gate |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/4 Level Risk Control Decision Gating 4级风控决策门控 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/4-Level Risk Decision Gate 4级风控决策门控 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/7 Stage Learning Pipeline 7阶段学习流水线 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/A/B测试框架 A/B Testing Framework |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/A8 Learning System Architecture A8学习系统架构 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/A8 Learning System Interface A8学习系统接口 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/AI协作策略与人机信任模型 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/AI自治运维 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Adaptive Walk-Forward 自适应Walk-Forward |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Agent Drift Detection Agent漂移检测 |  | design_only | design | 0 | 0 |
| ...ELLIGENCE/AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/ArchitectureOptimizer Agent 架构优化Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Auto Backtest & Simulation 自动回测与仿真 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/AutoML Engine 自动ML引擎 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/A股特色数据 A-Share Special Data |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Backtest-to-Production Deployer 回测到生产部署器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/BacktestCompleted 回测已完成 |  | design_only | design | 0 | 0 |
| ...TELLIGENCE/CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Causal Factor Validator 因果因子验证器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Causal KG 因果方向标注 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Causal SHAP 因果Shapley值 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/CausalEdge 因果边 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/CausalNLP 文本因果声明提取 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Classified Knowledge Package 分类知识包 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Cluster Behavior Protection 群集行为防护 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/CodeGenerator Agent 代码生成Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Collection Scheduler 采集调度器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Critic 批判器Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Cross-Market Transmission Quantitative Model 跨市场传导量化模型 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/D-RESEARCH |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/DSL AST Sandbox DSL+AST沙箱 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/DSR扩展 Deflated Sharpe Ratio Extension |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Data Quality Scorer 数据质量评分器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/DeepSCM深度因果模型 DeepSCM Deep Causal Model |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Drift Alert 漂移告警 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/E-RS-02 BacktestCompleted E-RS-02 BacktestCompleted事件 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Effect Feedback Path 效果反馈路径 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/End-to-End Causal Factor Analysis 端到端因果因子分析 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Experiment Tracker实验追踪 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/ExperimentReproduced 实验复现 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Explainability Gate 可解释性门控 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Factor Mining Agent 因子挖掘Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Factor Proposal 因子提案 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Feature Store特征存储 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/FeatureStore PIT Feature Feed FeatureStore PIT特征供给 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Filing NLP Engine 公告NLP引擎 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Generator 生成器Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Hypothesis Manager 假设管理器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Hypothesis Manager假设管理 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/ICL作为元学习 ICL as Meta-Learning |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Judge 裁判Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/KG引导多跳推理 KG-Guided Multi-Hop Reasoning |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Knowledge Classification System 知识分类体系 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Knowledge Effectiveness Evaluator 知识效果评估器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Knowledge Quality Assessor 知识质量评估器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/K线分词机制 K-line Tokenization |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/LLM Research Agent LLM研究助手 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/LLM引导因果发现先验 LLM Prior Causal Discovery |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/LLM语义理解 LLM Semantic Understanding |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/LLM遗传编程变异算子 LLM Genetic Programming Mutation |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Learning System 7-Stage Pipeline 学习系统7阶段流水线 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Learning System Performance Attribution 学习系统绩效归因 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/LiNGAM |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Liquidity & Slippage Simulator 流动性与滑点模拟器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/MAML快速适应 MAML Fast Adaptation |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/MLOps Closed Loop MLOps闭环 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/MLOps闭环 MLOps Closed Loop |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/ML模型工厂 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Market Regime Detector 市场制度检测器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Meta-Harness 元优化器 Meta-Optimizer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/MethodologyLearner Agent 方法论学习Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Module Dependency Graph 模块依赖图 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Module Factory Architecture 模块工厂架构 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Module Factory 模块工厂 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Module Matcher 模块匹配器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Module Registry 模块注册表 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Module Requirement Spec 模块需求规格 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Monte Carlo Engine 蒙特卡洛引擎 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Multi Modal Knowledge Acquisition 多模态知识采集 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Multimodal Knowledge Collection 多模态知识采集 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Neural Granger Causality 神经Granger因果 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/NewModule 新模块 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Notebook Integration Notebook集成 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/OCR 光学字符识别 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/ODL-Net在线深度学习 ODL-Net Online Deep Learning |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Order Matching Simulator 订单匹配模拟器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/PC算法 PC Algorithm |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/PDF预测引擎 PDF Prediction Engine |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Paper Search 论文搜索 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Paper Tracker 论文追踪器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Point-in-Time门控 Point-in-Time Gating |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Probabilistic Backtesting 概率回测 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/PromptOptimizer Agent 提示词优化Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Purge Gap 清洗间隔 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/RISE 代码自纠正 Code Self-Correction |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/RSI Architecture RSI自进化架构 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Reproducibility Manager可复现性管理 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Reproducibility Pack Generator 可复现性包生成器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Asset Versioning 研究资产版本化 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Catalog 研究目录 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Collaboration Hub 研究协作中心 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Data Manager 研究数据管理器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Data Sandbox 研究数据沙箱 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Discovery Knowledge Base 研究发现知识库 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Experiment Anomaly Detector 研究实验异常检测器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Information Barrier 研究信息隔离 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Information Isolation 研究信息隔离 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Knowledge Precipitator 研究知识沉淀器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Reproducibility Pack Generator 研究复现包生成器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Research Workflow Engine 研究工作流引擎 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/ResearchCompleted 研究完成 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/ResearchProject 研究项目 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Researcher Agent 研究Agent |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer |  | design_only | design | 0 | 0 |
| ...LIGENCE/S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/S4 模块创建与接入层 S4 Module Creation & Integration Layer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/S5 试运行与验证层 S5 Trial Run & Validation Layer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/SHAP值解释 SHAP Value Explanation |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/STOP Prompt自优化 Prompt Self-Optimization |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Scenario Generator基础版 情景生成器基础版 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Security Governance 安全与治理 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Sentiment Engine 情感分析引擎 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Signal Confidence Scorer 信号置信度评分器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Signal Extractor 信号提取器 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Strategy Code Generation 策略代码生成 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Strategy Iteration Upgrader策略迭代升级 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Strategy Sandbox轻量版 策略沙盒轻量版 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Structured Knowledge Fragment 结构化知识片段 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Synthetic Backtesting合成回测 Synthetic Backtesting |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Synthetic Data Generator基础版 合成数据生成器基础版 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/TimePC时序因果发现 TimePC Temporal Causal Discovery |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Trading Domain NLP Engine 交易领域NLP引擎 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/VLM图表视觉理解 VLM Chart Visual Understanding |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Voyager 技能库 Skill Library |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/Whisper 语音转写引擎 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/White's Reality Check 怀特现实检验 |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/三层参数优化 3-Layer Parameter Optimization |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/三重语义一致性 Triple Semantic Consistency |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/三重语义一致性约束 Triple Semantic Consistency Constraint |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/事件影响知识 Event Impact Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/事件触发采集 Event-Triggered Collection |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/交互式解释 Interactive Explanation |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/交易逻辑提取 Trading Logic Extraction |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/人工干预接口 Human Intervention Interface |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/人机协作模式 Human-AI Collaboration Mode |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/信息价值评分 Information Value Scoring |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/信息论过拟合检测 Information-Theoretic Overfitting Detection |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/元反思 Meta-Reflection |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/共形漂移检测 Conformal Drift Detection |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/决策树学习 Decision Tree Learning |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/决策路径可视化 Decision Path Visualization |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/创意拓宽模式 Creative Broadening Mode |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/制度知识 Regime Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/博弈知识 Game Theory Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/去噪 Denoising |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/去重 Deduplication |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/参数稳定性区域 Parameter Stability Plateau |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/可微因果发现 Differentiable Causal Discovery NOTEARS+ |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/可解释性门控 Explainability Gate |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/可解释设计约束 Explainable By Design Constraint |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/因子知识 Factor Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/因子语义去重 Factor Semantic Deduplication |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/因果发现三阶段扩展 Causal Discovery 3-Stage Extension |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/因果发现引擎 Causal Discovery Engine |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/因果约束反事实解释 Causal-Constrained Counterfactual Explanation |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/因果验证层 Causal Validation Layer |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/在线EWC Online Elastic Weight Consolidation |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/多尺度漂移检测 Multi-Scale Drift Detection |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/多模态融合引擎 Multimodal Fusion Engine |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/学习系统反馈路径 Path |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/宏观因果传导路径 Macro Causal Transmission Path |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/定时采集 Scheduled Collection |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/对抗性知识增强 Adversarial Knowledge Enhancement |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/市场状态感知Walk-Forward Regime-Aware Walk-Forward |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/市场状态知识 Market State Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/带推理路径的KG-RAG KG-RAG with Reasoning Path |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/延迟离线学习模式 Delayed Offline Learning Mode |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/手动提交 Manual Submission |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/技能三元组 Skill Triple |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/教训知识 Lesson Learned Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/数学反思闭环 Mathematical Reflection Loop |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/方法论知识 Methodology Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/时序基础模型骨干 TimesFM Foundation Model Backbone |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/时滞因果扩展 Lagged Causal Extension |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/术语标准化 Terminology Normalization |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/板块轮动知识 Sector Rotation Knowledge |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/格式转换 Format Conversion |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/模块工厂 Module Factory |  | design_only | design | 0 | 0 |
| D-INTELLIGENCE/流动性知识 Liquidity Knowledge |  | design_only | design | 0 | 0 |

> (仅显示前 200 个模块，共 273 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 35 | data,contract,event,config_depends |
| D-SECURITY | 23 | event,contract,data,config_depends |
| D-SIGNAL | 22 | contract,event,data,config_depends |
| D-FACTOR | 22 | contract,config_depends,event,data |
| D-KNOWLEDGE | 18 | config_depends,event,contract,data,domain_dependency |
| D-ML_TRAIN | 13 | import_depends,config_depends,data,contract,event |
| D-MKT_DATA | 13 | event,config_depends,data,contract |
| D-INFRA_RUNTIME | 10 | import_depends,contract,data,event,config_depends |
| D-PF_CORE | 7 | config_depends,contract,event,data |
| D-GOVERNANCE | 7 | config_depends,import_depends |
| D-ML_SERVE | 6 | event,contract,data,domain_dependency |
| D-INTEGRATION | 6 | import_depends |
| D-EX_CORE | 6 | data,contract,config_depends |
| D-POSITION | 5 | contract,config_depends |
| D-EX_SOR | 4 | data,event,contract |
| D-DATA_ENG | 4 | data,event,config_depends |
| D-TRADING | 3 | import_depends,event |
| D-SIMULATION | 3 | import_depends |
| D-GOV_RULE | 2 | contract,import_depends |
| D-SHARED | 1 | import_depends |
| D-AUTONOMY_CORE | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 85 | test_depends,import_depends,event,contract,data,config_depends |
| D-COMPLIANCE | 60 | contract,config_depends,event,data |
| D-INTEGRATION | 37 | import_depends,contract,data,event,config_depends |
| D-AUTONOMY_CORE | 32 | import_depends,contract,config_depends,event,data,domain_dependency |
| D-INFRA_OPS | 30 | event,contract,config_depends,data |
| D-OPS | 12 | event,contract,data,config_depends |
| D-AUTONOMY_PERM | 10 | data,contract,config_depends |
| D-SIMULATION | 9 | data,contract,event |
| D-FRONTEND | 9 | event,contract,data |
| D-PF_ALLOC | 8 | config_depends,contract,event,data |
| D-DATA_GOV | 7 | event,contract,data |
| D-TRADING | 6 | import_depends |
| D-CROSS_ASSET | 6 | contract,data,config_depends |
| D-ALT_DATA | 4 | config_depends,contract,data |
| D-REPORTING | 3 | data,event |
| D-SELL_DECISION | 2 | data,contract |
| D-SECURITY | 1 | import_depends |
| D-DATA_SEC | 1 | config_depends |

## 域内依赖图

详见 [d_intelligence_dependency.mmd](d_intelligence_dependency.mmd)
