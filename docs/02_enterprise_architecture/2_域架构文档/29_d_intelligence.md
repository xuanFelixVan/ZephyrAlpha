---
doc_type: domain_architecture_doc
title: D-INTELLIGENCE context_management架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 29_d_intelligence 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 29 | Number | 29 |
| 域ID | D-INTELLIGENCE | Domain ID | D-INTELLIGENCE |
| 域名称 | context_management | Domain Name | context_management |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 273 | Module Count | 273 |
| 域内依赖 | 270 | Internal Dependencies | 270 |
| 跨域入边 | 322 | Cross-domain Incoming | 322 |
| 跨域出边 | 211 | Cross-domain Outgoing | 211 |
| 设计态模块 | 217 | Design Modules | 217 |
| 原型态模块 | 32 | Prototype Modules | 32 |
| 生产态模块 | 18 | Production Modules | 18 |
| 容量 | 273/150 (超容) | Capacity | 273/150 (超容) |
| 描述 | 上下文预算管理(context_budget/token_budget) | Description | 上下文预算管理(context_budget/token_budget) |

## 模块清单 / Module List

共 273 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| D-INTELLIGENCE/3阶段决策门控 3-Stage Decision Gate | 3阶段决策门控 3-Stage Decision Gate | design | design_only | D-INTELLIGENCE/3阶段决策门控 3-Stage Decision Gate | 3阶段决策门控 3-Stage Decision Gate | design | design_only |
| D-INTELLIGENCE/4 Level Risk Control Decision Gating 4级风控决策门控 | 4 Level Risk Control Decision Gating ... | design | design_only | D-INTELLIGENCE/4 Level Risk Control Decision Gating 4级风控决策门控 | 4 Level Risk Control Decision Gating ... | design | design_only |
| D-INTELLIGENCE/4-Level Risk Decision Gate 4级风控决策门控 | 4-Level Risk Decision Gate 4级风控决策门控 | design | design_only | D-INTELLIGENCE/4-Level Risk Decision Gate 4级风控决策门控 | 4-Level Risk Decision Gate 4级风控决策门控 | design | design_only |
| D-INTELLIGENCE/7 Stage Learning Pipeline 7阶段学习流水线 | 7 Stage Learning Pipeline 7阶段学习流水线 | design | design_only | D-INTELLIGENCE/7 Stage Learning Pipeline 7阶段学习流水线 | 7 Stage Learning Pipeline 7阶段学习流水线 | design | design_only |
| D-INTELLIGENCE/A/B测试框架 A/B Testing Framework | A/B测试框架 A/B Testing Framework | design | design_only | D-INTELLIGENCE/A/B测试框架 A/B Testing Framework | A/B测试框架 A/B Testing Framework | design | design_only |
| D-INTELLIGENCE/A8 Learning System Architecture A8学习系统架构 | A8 Learning System Architecture A8学习系统架构 | design | design_only | D-INTELLIGENCE/A8 Learning System Architecture A8学习系统架构 | A8 Learning System Architecture A8学习系统架构 | design | design_only |
| D-INTELLIGENCE/A8 Learning System Interface A8学习系统接口 | A8 Learning System Interface A8学习系统接口 | design | design_only | D-INTELLIGENCE/A8 Learning System Interface A8学习系统接口 | A8 Learning System Interface A8学习系统接口 | design | design_only |
| D-INTELLIGENCE/AI协作策略与人机信任模型 | AI协作策略与人机信任模型 | design | design_only | D-INTELLIGENCE/AI协作策略与人机信任模型 | AI协作策略与人机信任模型 | design | design_only |
| D-INTELLIGENCE/AI自治运维 | AI自治运维 | design | design_only | D-INTELLIGENCE/AI自治运维 | AI自治运维 | design | design_only |
| D-INTELLIGENCE/Adaptive Walk-Forward 自适应Walk-Forward | Adaptive Walk-Forward 自适应Walk-Forward | design | design_only | D-INTELLIGENCE/Adaptive Walk-Forward 自适应Walk-Forward | Adaptive Walk-Forward 自适应Walk-Forward | design | design_only |
| D-INTELLIGENCE/Agent Drift Detection Agent漂移检测 | Agent Drift Detection Agent漂移检测 | design | design_only | D-INTELLIGENCE/Agent Drift Detection Agent漂移检测 | Agent Drift Detection Agent漂移检测 | design | design_only |
| ...ELLIGENCE/AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-... | design | design_only | ...ELLIGENCE/AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastructure Evolution | AlphaEvolve元级基础设施进化 AlphaEvolve Meta-... | design | design_only |
| D-INTELLIGENCE/AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | AlphaFin统一多模态框架 AlphaFin Unified Mult... | design | design_only | D-INTELLIGENCE/AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framework | AlphaFin统一多模态框架 AlphaFin Unified Mult... | design | design_only |
| D-INTELLIGENCE/ArchitectureOptimizer Agent 架构优化Agent | ArchitectureOptimizer Agent 架构优化Agent | design | design_only | D-INTELLIGENCE/ArchitectureOptimizer Agent 架构优化Agent | ArchitectureOptimizer Agent 架构优化Agent | design | design_only |
| D-INTELLIGENCE/Auto Backtest & Simulation 自动回测与仿真 | Auto Backtest & Simulation 自动回测与仿真 | design | design_only | D-INTELLIGENCE/Auto Backtest & Simulation 自动回测与仿真 | Auto Backtest & Simulation 自动回测与仿真 | design | design_only |
| D-INTELLIGENCE/AutoML Engine 自动ML引擎 | AutoML Engine 自动ML引擎 | design | design_only | D-INTELLIGENCE/AutoML Engine 自动ML引擎 | AutoML Engine 自动ML引擎 | design | design_only |
| D-INTELLIGENCE/AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | AutoSkill自动技能发现 AutoSkill Automatic S... | design | design_only | D-INTELLIGENCE/AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery | AutoSkill自动技能发现 AutoSkill Automatic S... | design | design_only |
| D-INTELLIGENCE/A股特色数据 A-Share Special Data | A股特色数据 A-Share Special Data | design | design_only | D-INTELLIGENCE/A股特色数据 A-Share Special Data | A股特色数据 A-Share Special Data | design | design_only |
| D-INTELLIGENCE/Backtest-to-Production Deployer 回测到生产部署器 | Backtest-to-Production Deployer 回测到生产部署器 | design | design_only | D-INTELLIGENCE/Backtest-to-Production Deployer 回测到生产部署器 | Backtest-to-Production Deployer 回测到生产部署器 | design | design_only |
| D-INTELLIGENCE/BacktestCompleted 回测已完成 | BacktestCompleted 回测已完成 | design | design_only | D-INTELLIGENCE/BacktestCompleted 回测已完成 | BacktestCompleted 回测已完成 | design | design_only |
| ...TELLIGENCE/CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | CPCV v2 Combinatorial Purged Cross-Va... | design | design_only | ...TELLIGENCE/CPCV v2 Combinatorial Purged Cross-Validation v2 CPCV v2组合净化交叉验证v2 | CPCV v2 Combinatorial Purged Cross-Va... | design | design_only |
| D-INTELLIGENCE/Causal Factor Validator 因果因子验证器 | Causal Factor Validator 因果因子验证器 | design | design_only | D-INTELLIGENCE/Causal Factor Validator 因果因子验证器 | Causal Factor Validator 因果因子验证器 | design | design_only |
| D-INTELLIGENCE/Causal KG 因果方向标注 | Causal KG 因果方向标注 | design | design_only | D-INTELLIGENCE/Causal KG 因果方向标注 | Causal KG 因果方向标注 | design | design_only |
| D-INTELLIGENCE/Causal SHAP 因果Shapley值 | Causal SHAP 因果Shapley值 | design | design_only | D-INTELLIGENCE/Causal SHAP 因果Shapley值 | Causal SHAP 因果Shapley值 | design | design_only |
| D-INTELLIGENCE/CausalEdge 因果边 | CausalEdge 因果边 | design | design_only | D-INTELLIGENCE/CausalEdge 因果边 | CausalEdge 因果边 | design | design_only |
| D-INTELLIGENCE/CausalNLP 文本因果声明提取 | CausalNLP 文本因果声明提取 | design | design_only | D-INTELLIGENCE/CausalNLP 文本因果声明提取 | CausalNLP 文本因果声明提取 | design | design_only |
| D-INTELLIGENCE/Classified Knowledge Package 分类知识包 | Classified Knowledge Package 分类知识包 | design | design_only | D-INTELLIGENCE/Classified Knowledge Package 分类知识包 | Classified Knowledge Package 分类知识包 | design | design_only |
| D-INTELLIGENCE/Cluster Behavior Protection 群集行为防护 | Cluster Behavior Protection 群集行为防护 | design | design_only | D-INTELLIGENCE/Cluster Behavior Protection 群集行为防护 | Cluster Behavior Protection 群集行为防护 | design | design_only |
| D-INTELLIGENCE/CodeGenerator Agent 代码生成Agent | CodeGenerator Agent 代码生成Agent | design | design_only | D-INTELLIGENCE/CodeGenerator Agent 代码生成Agent | CodeGenerator Agent 代码生成Agent | design | design_only |
| D-INTELLIGENCE/Collection Scheduler 采集调度器 | Collection Scheduler 采集调度器 | design | design_only | D-INTELLIGENCE/Collection Scheduler 采集调度器 | Collection Scheduler 采集调度器 | design | design_only |
| D-INTELLIGENCE/Critic 批判器Agent | Critic 批判器Agent | design | design_only | D-INTELLIGENCE/Critic 批判器Agent | Critic 批判器Agent | design | design_only |
| D-INTELLIGENCE/Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | Cross-Market Transmission Quantitativ... | design | design_only | D-INTELLIGENCE/Cross-Market Transmission Quantitative Model 跨市场传导量化模型 | Cross-Market Transmission Quantitativ... | design | design_only |
| D-INTELLIGENCE/D-RESEARCH | D-RESEARCH | design | design_only | D-INTELLIGENCE/D-RESEARCH | D-RESEARCH | design | design_only |
| D-INTELLIGENCE/DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | DSL AST Sandbox Code Generation DSL+A... | design | design_only | D-INTELLIGENCE/DSL AST Sandbox Code Generation DSL+AST沙箱安全代码生成 | DSL AST Sandbox Code Generation DSL+A... | design | design_only |
| D-INTELLIGENCE/DSL AST Sandbox DSL+AST沙箱 | DSL AST Sandbox DSL+AST沙箱 | design | design_only | D-INTELLIGENCE/DSL AST Sandbox DSL+AST沙箱 | DSL AST Sandbox DSL+AST沙箱 | design | design_only |
| D-INTELLIGENCE/DSR扩展 Deflated Sharpe Ratio Extension | DSR扩展 Deflated Sharpe Ratio Extension | design | design_only | D-INTELLIGENCE/DSR扩展 Deflated Sharpe Ratio Extension | DSR扩展 Deflated Sharpe Ratio Extension | design | design_only |
| D-INTELLIGENCE/Data Quality Scorer 数据质量评分器 | Data Quality Scorer 数据质量评分器 | design | design_only | D-INTELLIGENCE/Data Quality Scorer 数据质量评分器 | Data Quality Scorer 数据质量评分器 | design | design_only |
| D-INTELLIGENCE/DeepSCM深度因果模型 DeepSCM Deep Causal Model | DeepSCM深度因果模型 DeepSCM Deep Causal Model | design | design_only | D-INTELLIGENCE/DeepSCM深度因果模型 DeepSCM Deep Causal Model | DeepSCM深度因果模型 DeepSCM Deep Causal Model | design | design_only |
| D-INTELLIGENCE/Drift Alert 漂移告警 | Drift Alert 漂移告警 | design | design_only | D-INTELLIGENCE/Drift Alert 漂移告警 | Drift Alert 漂移告警 | design | design_only |
| D-INTELLIGENCE/E-RS-02 BacktestCompleted E-RS-02 BacktestCompleted事件 | E-RS-02 BacktestCompleted E-RS-02 Bac... | design | design_only | D-INTELLIGENCE/E-RS-02 BacktestCompleted E-RS-02 BacktestCompleted事件 | E-RS-02 BacktestCompleted E-RS-02 Bac... | design | design_only |
| D-INTELLIGENCE/Effect Feedback Path 效果反馈路径 | Effect Feedback Path 效果反馈路径 | design | design_only | D-INTELLIGENCE/Effect Feedback Path 效果反馈路径 | Effect Feedback Path 效果反馈路径 | design | design_only |
| D-INTELLIGENCE/End-to-End Causal Factor Analysis 端到端因果因子分析 | End-to-End Causal Factor Analysis 端到端... | design | design_only | D-INTELLIGENCE/End-to-End Causal Factor Analysis 端到端因果因子分析 | End-to-End Causal Factor Analysis 端到端... | design | design_only |
| D-INTELLIGENCE/Experiment Tracker实验追踪 | Experiment Tracker实验追踪 | design | design_only | D-INTELLIGENCE/Experiment Tracker实验追踪 | Experiment Tracker实验追踪 | design | design_only |
| D-INTELLIGENCE/ExperimentReproduced 实验复现 | ExperimentReproduced 实验复现 | design | design_only | D-INTELLIGENCE/ExperimentReproduced 实验复现 | ExperimentReproduced 实验复现 | design | design_only |
| D-INTELLIGENCE/Explainability Gate 可解释性门控 | Explainability Gate 可解释性门控 | design | design_only | D-INTELLIGENCE/Explainability Gate 可解释性门控 | Explainability Gate 可解释性门控 | design | design_only |
| D-INTELLIGENCE/Factor Mining Agent 因子挖掘Agent | Factor Mining Agent 因子挖掘Agent | design | design_only | D-INTELLIGENCE/Factor Mining Agent 因子挖掘Agent | Factor Mining Agent 因子挖掘Agent | design | design_only |
| D-INTELLIGENCE/Factor Proposal 因子提案 | Factor Proposal 因子提案 | design | design_only | D-INTELLIGENCE/Factor Proposal 因子提案 | Factor Proposal 因子提案 | design | design_only |
| D-INTELLIGENCE/Feature Store特征存储 | Feature Store特征存储 | design | design_only | D-INTELLIGENCE/Feature Store特征存储 | Feature Store特征存储 | design | design_only |
| D-INTELLIGENCE/FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | FeatureStore PIT Feature Feed Feature... | design | design_only | D-INTELLIGENCE/FeatureStore PIT Feature Feed FeatureStore PIT特征供给 | FeatureStore PIT Feature Feed Feature... | design | design_only |
| D-INTELLIGENCE/Filing NLP Engine 公告NLP引擎 | Filing NLP Engine 公告NLP引擎 | design | design_only | D-INTELLIGENCE/Filing NLP Engine 公告NLP引擎 | Filing NLP Engine 公告NLP引擎 | design | design_only |
| D-INTELLIGENCE/FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | FinVision端到端图表→策略 FinVision End-to-En... | design | design_only | D-INTELLIGENCE/FinVision端到端图表→策略 FinVision End-to-End Chart to Strategy | FinVision端到端图表→策略 FinVision End-to-En... | design | design_only |
| D-INTELLIGENCE/Generator 生成器Agent | Generator 生成器Agent | design | design_only | D-INTELLIGENCE/Generator 生成器Agent | Generator 生成器Agent | design | design_only |
| D-INTELLIGENCE/GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | GraphRAG图增强检索 GraphRAG Graph-Enhanced... | design | design_only | D-INTELLIGENCE/GraphRAG图增强检索 GraphRAG Graph-Enhanced Retrieval | GraphRAG图增强检索 GraphRAG Graph-Enhanced... | design | design_only |
| D-INTELLIGENCE/Hypothesis Manager 假设管理器 | Hypothesis Manager 假设管理器 | design | design_only | D-INTELLIGENCE/Hypothesis Manager 假设管理器 | Hypothesis Manager 假设管理器 | design | design_only |
| D-INTELLIGENCE/Hypothesis Manager假设管理 | Hypothesis Manager假设管理 | design | design_only | D-INTELLIGENCE/Hypothesis Manager假设管理 | Hypothesis Manager假设管理 | design | design_only |
| D-INTELLIGENCE/ICL作为元学习 ICL as Meta-Learning | ICL作为元学习 ICL as Meta-Learning | design | design_only | D-INTELLIGENCE/ICL作为元学习 ICL as Meta-Learning | ICL作为元学习 ICL as Meta-Learning | design | design_only |
| D-INTELLIGENCE/Judge 裁判Agent | Judge 裁判Agent | design | design_only | D-INTELLIGENCE/Judge 裁判Agent | Judge 裁判Agent | design | design_only |
| D-INTELLIGENCE/KG引导多跳推理 KG-Guided Multi-Hop Reasoning | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | design | design_only | D-INTELLIGENCE/KG引导多跳推理 KG-Guided Multi-Hop Reasoning | KG引导多跳推理 KG-Guided Multi-Hop Reasoning | design | design_only |
| D-INTELLIGENCE/Knowledge Classification System 知识分类体系 | Knowledge Classification System 知识分类体系 | design | design_only | D-INTELLIGENCE/Knowledge Classification System 知识分类体系 | Knowledge Classification System 知识分类体系 | design | design_only |
| D-INTELLIGENCE/Knowledge Effectiveness Evaluator 知识效果评估器 | Knowledge Effectiveness Evaluator 知识效... | design | design_only | D-INTELLIGENCE/Knowledge Effectiveness Evaluator 知识效果评估器 | Knowledge Effectiveness Evaluator 知识效... | design | design_only |
| D-INTELLIGENCE/Knowledge Quality Assessor 知识质量评估器 | Knowledge Quality Assessor 知识质量评估器 | design | design_only | D-INTELLIGENCE/Knowledge Quality Assessor 知识质量评估器 | Knowledge Quality Assessor 知识质量评估器 | design | design_only |
| D-INTELLIGENCE/K线分词机制 K-line Tokenization | K线分词机制 K-line Tokenization | design | design_only | D-INTELLIGENCE/K线分词机制 K-line Tokenization | K线分词机制 K-line Tokenization | design | design_only |
| D-INTELLIGENCE/LLM Research Agent LLM研究助手 | LLM Research Agent LLM研究助手 | design | design_only | D-INTELLIGENCE/LLM Research Agent LLM研究助手 | LLM Research Agent LLM研究助手 | design | design_only |
| D-INTELLIGENCE/LLM引导因果发现先验 LLM Prior Causal Discovery | LLM引导因果发现先验 LLM Prior Causal Discovery | design | design_only | D-INTELLIGENCE/LLM引导因果发现先验 LLM Prior Causal Discovery | LLM引导因果发现先验 LLM Prior Causal Discovery | design | design_only |
| D-INTELLIGENCE/LLM语义理解 LLM Semantic Understanding | LLM语义理解 LLM Semantic Understanding | design | design_only | D-INTELLIGENCE/LLM语义理解 LLM Semantic Understanding | LLM语义理解 LLM Semantic Understanding | design | design_only |
| D-INTELLIGENCE/LLM遗传编程变异算子 LLM Genetic Programming Mutation | LLM遗传编程变异算子 LLM Genetic Programming M... | design | design_only | D-INTELLIGENCE/LLM遗传编程变异算子 LLM Genetic Programming Mutation | LLM遗传编程变异算子 LLM Genetic Programming M... | design | design_only |
| D-INTELLIGENCE/Learning System 7-Stage Pipeline 学习系统7阶段流水线 | Learning System 7-Stage Pipeline 学习系统... | design | design_only | D-INTELLIGENCE/Learning System 7-Stage Pipeline 学习系统7阶段流水线 | Learning System 7-Stage Pipeline 学习系统... | design | design_only |
| D-INTELLIGENCE/Learning System Performance Attribution 学习系统绩效归因 | Learning System Performance Attributi... | design | design_only | D-INTELLIGENCE/Learning System Performance Attribution 学习系统绩效归因 | Learning System Performance Attributi... | design | design_only |
| D-INTELLIGENCE/LiNGAM | LiNGAM | design | design_only | D-INTELLIGENCE/LiNGAM | LiNGAM | design | design_only |
| D-INTELLIGENCE/Liquidity & Slippage Simulator 流动性与滑点模拟器 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | design | design_only | D-INTELLIGENCE/Liquidity & Slippage Simulator 流动性与滑点模拟器 | Liquidity & Slippage Simulator 流动性与滑点模拟器 | design | design_only |
| D-INTELLIGENCE/MAML快速适应 MAML Fast Adaptation | MAML快速适应 MAML Fast Adaptation | design | design_only | D-INTELLIGENCE/MAML快速适应 MAML Fast Adaptation | MAML快速适应 MAML Fast Adaptation | design | design_only |
| D-INTELLIGENCE/MLOps Closed Loop MLOps闭环 | MLOps Closed Loop MLOps闭环 | design | design_only | D-INTELLIGENCE/MLOps Closed Loop MLOps闭环 | MLOps Closed Loop MLOps闭环 | design | design_only |
| D-INTELLIGENCE/MLOps闭环 MLOps Closed Loop | MLOps闭环 MLOps Closed Loop | design | design_only | D-INTELLIGENCE/MLOps闭环 MLOps Closed Loop | MLOps闭环 MLOps Closed Loop | design | design_only |
| D-INTELLIGENCE/ML模型工厂 | ML模型工厂 | design | design_only | D-INTELLIGENCE/ML模型工厂 | ML模型工厂 | design | design_only |
| D-INTELLIGENCE/Market Regime Detector 市场制度检测器 | Market Regime Detector 市场制度检测器 | design | design_only | D-INTELLIGENCE/Market Regime Detector 市场制度检测器 | Market Regime Detector 市场制度检测器 | design | design_only |
| D-INTELLIGENCE/Meta-Harness 元优化器 Meta-Optimizer | Meta-Harness 元优化器 Meta-Optimizer | design | design_only | D-INTELLIGENCE/Meta-Harness 元优化器 Meta-Optimizer | Meta-Harness 元优化器 Meta-Optimizer | design | design_only |
| D-INTELLIGENCE/MethodologyLearner Agent 方法论学习Agent | MethodologyLearner Agent 方法论学习Agent | design | design_only | D-INTELLIGENCE/MethodologyLearner Agent 方法论学习Agent | MethodologyLearner Agent 方法论学习Agent | design | design_only |
| D-INTELLIGENCE/Module Dependency Graph 模块依赖图 | Module Dependency Graph 模块依赖图 | design | design_only | D-INTELLIGENCE/Module Dependency Graph 模块依赖图 | Module Dependency Graph 模块依赖图 | design | design_only |
| D-INTELLIGENCE/Module Factory Architecture 模块工厂架构 | Module Factory Architecture 模块工厂架构 | design | design_only | D-INTELLIGENCE/Module Factory Architecture 模块工厂架构 | Module Factory Architecture 模块工厂架构 | design | design_only |
| D-INTELLIGENCE/Module Factory 模块工厂 | Module Factory 模块工厂 | design | design_only | D-INTELLIGENCE/Module Factory 模块工厂 | Module Factory 模块工厂 | design | design_only |
| D-INTELLIGENCE/Module Matcher 模块匹配器 | Module Matcher 模块匹配器 | design | design_only | D-INTELLIGENCE/Module Matcher 模块匹配器 | Module Matcher 模块匹配器 | design | design_only |
| D-INTELLIGENCE/Module Registry 模块注册表 | Module Registry 模块注册表 | design | design_only | D-INTELLIGENCE/Module Registry 模块注册表 | Module Registry 模块注册表 | design | design_only |
| D-INTELLIGENCE/Module Requirement Spec 模块需求规格 | Module Requirement Spec 模块需求规格 | design | design_only | D-INTELLIGENCE/Module Requirement Spec 模块需求规格 | Module Requirement Spec 模块需求规格 | design | design_only |
| D-INTELLIGENCE/Monte Carlo Engine 蒙特卡洛引擎 | Monte Carlo Engine 蒙特卡洛引擎 | design | design_only | D-INTELLIGENCE/Monte Carlo Engine 蒙特卡洛引擎 | Monte Carlo Engine 蒙特卡洛引擎 | design | design_only |
| D-INTELLIGENCE/Multi Modal Knowledge Acquisition 多模态知识采集 | Multi Modal Knowledge Acquisition 多模态... | design | design_only | D-INTELLIGENCE/Multi Modal Knowledge Acquisition 多模态知识采集 | Multi Modal Knowledge Acquisition 多模态... | design | design_only |
| D-INTELLIGENCE/Multimodal Knowledge Collection 多模态知识采集 | Multimodal Knowledge Collection 多模态知识采集 | design | design_only | D-INTELLIGENCE/Multimodal Knowledge Collection 多模态知识采集 | Multimodal Knowledge Collection 多模态知识采集 | design | design_only |
| D-INTELLIGENCE/Neural Granger Causality 神经Granger因果 | Neural Granger Causality 神经Granger因果 | design | design_only | D-INTELLIGENCE/Neural Granger Causality 神经Granger因果 | Neural Granger Causality 神经Granger因果 | design | design_only |
| D-INTELLIGENCE/NewModule 新模块 | NewModule 新模块 | design | design_only | D-INTELLIGENCE/NewModule 新模块 | NewModule 新模块 | design | design_only |
| D-INTELLIGENCE/Notebook Integration Notebook集成 | Notebook Integration Notebook集成 | design | design_only | D-INTELLIGENCE/Notebook Integration Notebook集成 | Notebook Integration Notebook集成 | design | design_only |
| D-INTELLIGENCE/OCR 光学字符识别 | OCR 光学字符识别 | design | design_only | D-INTELLIGENCE/OCR 光学字符识别 | OCR 光学字符识别 | design | design_only |
| D-INTELLIGENCE/ODL-Net在线深度学习 ODL-Net Online Deep Learning | ODL-Net在线深度学习 ODL-Net Online Deep Lea... | design | design_only | D-INTELLIGENCE/ODL-Net在线深度学习 ODL-Net Online Deep Learning | ODL-Net在线深度学习 ODL-Net Online Deep Lea... | design | design_only |
| D-INTELLIGENCE/Order Matching Simulator 订单匹配模拟器 | Order Matching Simulator 订单匹配模拟器 | design | design_only | D-INTELLIGENCE/Order Matching Simulator 订单匹配模拟器 | Order Matching Simulator 订单匹配模拟器 | design | design_only |
| D-INTELLIGENCE/PC算法 PC Algorithm | PC算法 PC Algorithm | design | design_only | D-INTELLIGENCE/PC算法 PC Algorithm | PC算法 PC Algorithm | design | design_only |
| D-INTELLIGENCE/PDF预测引擎 PDF Prediction Engine | PDF预测引擎 PDF Prediction Engine | design | design_only | D-INTELLIGENCE/PDF预测引擎 PDF Prediction Engine | PDF预测引擎 PDF Prediction Engine | design | design_only |
| D-INTELLIGENCE/Paper Search 论文搜索 | Paper Search 论文搜索 | design | design_only | D-INTELLIGENCE/Paper Search 论文搜索 | Paper Search 论文搜索 | design | design_only |
| D-INTELLIGENCE/Paper Tracker 论文追踪器 | Paper Tracker 论文追踪器 | design | design_only | D-INTELLIGENCE/Paper Tracker 论文追踪器 | Paper Tracker 论文追踪器 | design | design_only |
| D-INTELLIGENCE/Point-in-Time门控 Point-in-Time Gating | Point-in-Time门控 Point-in-Time Gating | design | design_only | D-INTELLIGENCE/Point-in-Time门控 Point-in-Time Gating | Point-in-Time门控 Point-in-Time Gating | design | design_only |
| D-INTELLIGENCE/Probabilistic Backtesting 概率回测 | Probabilistic Backtesting 概率回测 | design | design_only | D-INTELLIGENCE/Probabilistic Backtesting 概率回测 | Probabilistic Backtesting 概率回测 | design | design_only |
| D-INTELLIGENCE/PromptOptimizer Agent 提示词优化Agent | PromptOptimizer Agent 提示词优化Agent | design | design_only | D-INTELLIGENCE/PromptOptimizer Agent 提示词优化Agent | PromptOptimizer Agent 提示词优化Agent | design | design_only |
| D-INTELLIGENCE/Purge Gap 清洗间隔 | Purge Gap 清洗间隔 | design | design_only | D-INTELLIGENCE/Purge Gap 清洗间隔 | Purge Gap 清洗间隔 | design | design_only |
| D-INTELLIGENCE/RISE 代码自纠正 Code Self-Correction | RISE 代码自纠正 Code Self-Correction | design | design_only | D-INTELLIGENCE/RISE 代码自纠正 Code Self-Correction | RISE 代码自纠正 Code Self-Correction | design | design_only |
| D-INTELLIGENCE/RSI Architecture RSI自进化架构 | RSI Architecture RSI自进化架构 | design | design_only | D-INTELLIGENCE/RSI Architecture RSI自进化架构 | RSI Architecture RSI自进化架构 | design | design_only |
| D-INTELLIGENCE/Reproducibility Manager可复现性管理 | Reproducibility Manager可复现性管理 | design | design_only | D-INTELLIGENCE/Reproducibility Manager可复现性管理 | Reproducibility Manager可复现性管理 | design | design_only |
| D-INTELLIGENCE/Reproducibility Pack Generator 可复现性包生成器 | Reproducibility Pack Generator 可复现性包生成器 | design | design_only | D-INTELLIGENCE/Reproducibility Pack Generator 可复现性包生成器 | Reproducibility Pack Generator 可复现性包生成器 | design | design_only |
| D-INTELLIGENCE/Research Asset Versioning 研究资产版本化 | Research Asset Versioning 研究资产版本化 | design | design_only | D-INTELLIGENCE/Research Asset Versioning 研究资产版本化 | Research Asset Versioning 研究资产版本化 | design | design_only |
| D-INTELLIGENCE/Research Catalog 研究目录 | Research Catalog 研究目录 | design | design_only | D-INTELLIGENCE/Research Catalog 研究目录 | Research Catalog 研究目录 | design | design_only |
| D-INTELLIGENCE/Research Collaboration Hub 研究协作中心 | Research Collaboration Hub 研究协作中心 | design | design_only | D-INTELLIGENCE/Research Collaboration Hub 研究协作中心 | Research Collaboration Hub 研究协作中心 | design | design_only |
| D-INTELLIGENCE/Research Data Manager 研究数据管理器 | Research Data Manager 研究数据管理器 | design | design_only | D-INTELLIGENCE/Research Data Manager 研究数据管理器 | Research Data Manager 研究数据管理器 | design | design_only |
| D-INTELLIGENCE/Research Data Sandbox 研究数据沙箱 | Research Data Sandbox 研究数据沙箱 | design | design_only | D-INTELLIGENCE/Research Data Sandbox 研究数据沙箱 | Research Data Sandbox 研究数据沙箱 | design | design_only |
| D-INTELLIGENCE/Research Discovery Knowledge Base 研究发现知识库 | Research Discovery Knowledge Base 研究发... | design | design_only | D-INTELLIGENCE/Research Discovery Knowledge Base 研究发现知识库 | Research Discovery Knowledge Base 研究发... | design | design_only |
| D-INTELLIGENCE/Research Experiment Anomaly Detector 研究实验异常检测器 | Research Experiment Anomaly Detector ... | design | design_only | D-INTELLIGENCE/Research Experiment Anomaly Detector 研究实验异常检测器 | Research Experiment Anomaly Detector ... | design | design_only |
| D-INTELLIGENCE/Research Information Barrier 研究信息隔离 | Research Information Barrier 研究信息隔离 | design | design_only | D-INTELLIGENCE/Research Information Barrier 研究信息隔离 | Research Information Barrier 研究信息隔离 | design | design_only |
| D-INTELLIGENCE/Research Information Isolation 研究信息隔离 | Research Information Isolation 研究信息隔离 | design | design_only | D-INTELLIGENCE/Research Information Isolation 研究信息隔离 | Research Information Isolation 研究信息隔离 | design | design_only |
| D-INTELLIGENCE/Research Knowledge Precipitator 研究知识沉淀器 | Research Knowledge Precipitator 研究知识沉淀器 | design | design_only | D-INTELLIGENCE/Research Knowledge Precipitator 研究知识沉淀器 | Research Knowledge Precipitator 研究知识沉淀器 | design | design_only |
| D-INTELLIGENCE/Research Reproducibility Pack Generator 研究复现包生成器 | Research Reproducibility Pack Generat... | design | design_only | D-INTELLIGENCE/Research Reproducibility Pack Generator 研究复现包生成器 | Research Reproducibility Pack Generat... | design | design_only |
| D-INTELLIGENCE/Research Workflow Engine 研究工作流引擎 | Research Workflow Engine 研究工作流引擎 | design | design_only | D-INTELLIGENCE/Research Workflow Engine 研究工作流引擎 | Research Workflow Engine 研究工作流引擎 | design | design_only |
| D-INTELLIGENCE/ResearchCompleted 研究完成 | ResearchCompleted 研究完成 | design | design_only | D-INTELLIGENCE/ResearchCompleted 研究完成 | ResearchCompleted 研究完成 | design | design_only |
| D-INTELLIGENCE/ResearchProject 研究项目 | ResearchProject 研究项目 | design | design_only | D-INTELLIGENCE/ResearchProject 研究项目 | ResearchProject 研究项目 | design | design_only |
| D-INTELLIGENCE/Researcher Agent 研究Agent | Researcher Agent 研究Agent | design | design_only | D-INTELLIGENCE/Researcher Agent 研究Agent | Researcher Agent 研究Agent | design | design_only |
| D-INTELLIGENCE/S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | S0 多模态知识采集层 S0 Multimodal Knowledge C... | design | design_only | D-INTELLIGENCE/S0 多模态知识采集层 S0 Multimodal Knowledge Collection Layer | S0 多模态知识采集层 S0 Multimodal Knowledge C... | design | design_only |
| D-INTELLIGENCE/S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | S1 知识清洗与结构化层 S1 Knowledge Cleaning & ... | design | design_only | D-INTELLIGENCE/S1 知识清洗与结构化层 S1 Knowledge Cleaning & Structuring Layer | S1 知识清洗与结构化层 S1 Knowledge Cleaning & ... | design | design_only |
| ...LIGENCE/S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | S2 知识分类与策略提取层 S2 Knowledge Classifica... | design | design_only | ...LIGENCE/S2 知识分类与策略提取层 S2 Knowledge Classification & Strategy Extraction Layer | S2 知识分类与策略提取层 S2 Knowledge Classifica... | design | design_only |
| D-INTELLIGENCE/S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | S3 模块映射与工厂匹配层 S3 Module Mapping & Fac... | design | design_only | D-INTELLIGENCE/S3 模块映射与工厂匹配层 S3 Module Mapping & Factory Matching Layer | S3 模块映射与工厂匹配层 S3 Module Mapping & Fac... | design | design_only |
| D-INTELLIGENCE/S4 模块创建与接入层 S4 Module Creation & Integration Layer | S4 模块创建与接入层 S4 Module Creation & Inte... | design | design_only | D-INTELLIGENCE/S4 模块创建与接入层 S4 Module Creation & Integration Layer | S4 模块创建与接入层 S4 Module Creation & Inte... | design | design_only |
| D-INTELLIGENCE/S5 试运行与验证层 S5 Trial Run & Validation Layer | S5 试运行与验证层 S5 Trial Run & Validation ... | design | design_only | D-INTELLIGENCE/S5 试运行与验证层 S5 Trial Run & Validation Layer | S5 试运行与验证层 S5 Trial Run & Validation ... | design | design_only |
| D-INTELLIGENCE/S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | S6 元学习与自我进化层 S6 Meta-Learning & Self-... | design | design_only | D-INTELLIGENCE/S6 元学习与自我进化层 S6 Meta-Learning & Self-Evolution Layer | S6 元学习与自我进化层 S6 Meta-Learning & Self-... | design | design_only |
| D-INTELLIGENCE/SHAP值解释 SHAP Value Explanation | SHAP值解释 SHAP Value Explanation | design | design_only | D-INTELLIGENCE/SHAP值解释 SHAP Value Explanation | SHAP值解释 SHAP Value Explanation | design | design_only |
| D-INTELLIGENCE/STOP Prompt自优化 Prompt Self-Optimization | STOP Prompt自优化 Prompt Self-Optimization | design | design_only | D-INTELLIGENCE/STOP Prompt自优化 Prompt Self-Optimization | STOP Prompt自优化 Prompt Self-Optimization | design | design_only |
| D-INTELLIGENCE/Scenario Generator基础版 情景生成器基础版 | Scenario Generator基础版 情景生成器基础版 | design | design_only | D-INTELLIGENCE/Scenario Generator基础版 情景生成器基础版 | Scenario Generator基础版 情景生成器基础版 | design | design_only |
| D-INTELLIGENCE/Security Governance 安全与治理 | Security Governance 安全与治理 | design | design_only | D-INTELLIGENCE/Security Governance 安全与治理 | Security Governance 安全与治理 | design | design_only |
| D-INTELLIGENCE/Sentiment Engine 情感分析引擎 | Sentiment Engine 情感分析引擎 | design | design_only | D-INTELLIGENCE/Sentiment Engine 情感分析引擎 | Sentiment Engine 情感分析引擎 | design | design_only |
| D-INTELLIGENCE/Signal Confidence Scorer 信号置信度评分器 | Signal Confidence Scorer 信号置信度评分器 | design | design_only | D-INTELLIGENCE/Signal Confidence Scorer 信号置信度评分器 | Signal Confidence Scorer 信号置信度评分器 | design | design_only |
| D-INTELLIGENCE/Signal Extractor 信号提取器 | Signal Extractor 信号提取器 | design | design_only | D-INTELLIGENCE/Signal Extractor 信号提取器 | Signal Extractor 信号提取器 | design | design_only |
| D-INTELLIGENCE/Strategy Code Generation 策略代码生成 | Strategy Code Generation 策略代码生成 | design | design_only | D-INTELLIGENCE/Strategy Code Generation 策略代码生成 | Strategy Code Generation 策略代码生成 | design | design_only |
| D-INTELLIGENCE/Strategy Iteration Upgrader策略迭代升级 | Strategy Iteration Upgrader策略迭代升级 | design | design_only | D-INTELLIGENCE/Strategy Iteration Upgrader策略迭代升级 | Strategy Iteration Upgrader策略迭代升级 | design | design_only |
| D-INTELLIGENCE/Strategy Sandbox轻量版 策略沙盒轻量版 | Strategy Sandbox轻量版 策略沙盒轻量版 | design | design_only | D-INTELLIGENCE/Strategy Sandbox轻量版 策略沙盒轻量版 | Strategy Sandbox轻量版 策略沙盒轻量版 | design | design_only |
| D-INTELLIGENCE/Structured Knowledge Fragment 结构化知识片段 | Structured Knowledge Fragment 结构化知识片段 | design | design_only | D-INTELLIGENCE/Structured Knowledge Fragment 结构化知识片段 | Structured Knowledge Fragment 结构化知识片段 | design | design_only |
| D-INTELLIGENCE/Synthetic Backtesting合成回测 Synthetic Backtesting | Synthetic Backtesting合成回测 Synthetic B... | design | design_only | D-INTELLIGENCE/Synthetic Backtesting合成回测 Synthetic Backtesting | Synthetic Backtesting合成回测 Synthetic B... | design | design_only |
| D-INTELLIGENCE/Synthetic Data Generator基础版 合成数据生成器基础版 | Synthetic Data Generator基础版 合成数据生成器基础版 | design | design_only | D-INTELLIGENCE/Synthetic Data Generator基础版 合成数据生成器基础版 | Synthetic Data Generator基础版 合成数据生成器基础版 | design | design_only |
| D-INTELLIGENCE/TimePC时序因果发现 TimePC Temporal Causal Discovery | TimePC时序因果发现 TimePC Temporal Causal D... | design | design_only | D-INTELLIGENCE/TimePC时序因果发现 TimePC Temporal Causal Discovery | TimePC时序因果发现 TimePC Temporal Causal D... | design | design_only |
| D-INTELLIGENCE/Trading Domain NLP Engine 交易领域NLP引擎 | Trading Domain NLP Engine 交易领域NLP引擎 | design | design_only | D-INTELLIGENCE/Trading Domain NLP Engine 交易领域NLP引擎 | Trading Domain NLP Engine 交易领域NLP引擎 | design | design_only |
| D-INTELLIGENCE/VLM图表视觉理解 VLM Chart Visual Understanding | VLM图表视觉理解 VLM Chart Visual Understanding | design | design_only | D-INTELLIGENCE/VLM图表视觉理解 VLM Chart Visual Understanding | VLM图表视觉理解 VLM Chart Visual Understanding | design | design_only |
| D-INTELLIGENCE/Voyager 技能库 Skill Library | Voyager 技能库 Skill Library | design | design_only | D-INTELLIGENCE/Voyager 技能库 Skill Library | Voyager 技能库 Skill Library | design | design_only |
| D-INTELLIGENCE/Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | Walk-Forward Analyzer完整版 Walk-Forward... | design | design_only | D-INTELLIGENCE/Walk-Forward Analyzer完整版 Walk-Forward Analyzer Full Version | Walk-Forward Analyzer完整版 Walk-Forward... | design | design_only |
| D-INTELLIGENCE/Whisper 语音转写引擎 | Whisper 语音转写引擎 | design | design_only | D-INTELLIGENCE/Whisper 语音转写引擎 | Whisper 语音转写引擎 | design | design_only |
| D-INTELLIGENCE/White's Reality Check 怀特现实检验 | White's Reality Check 怀特现实检验 | design | design_only | D-INTELLIGENCE/White's Reality Check 怀特现实检验 | White's Reality Check 怀特现实检验 | design | design_only |
| D-INTELLIGENCE/三层参数优化 3-Layer Parameter Optimization | 三层参数优化 3-Layer Parameter Optimization | design | design_only | D-INTELLIGENCE/三层参数优化 3-Layer Parameter Optimization | 三层参数优化 3-Layer Parameter Optimization | design | design_only |
| D-INTELLIGENCE/三重语义一致性 Triple Semantic Consistency | 三重语义一致性 Triple Semantic Consistency | design | design_only | D-INTELLIGENCE/三重语义一致性 Triple Semantic Consistency | 三重语义一致性 Triple Semantic Consistency | design | design_only |
| D-INTELLIGENCE/三重语义一致性约束 Triple Semantic Consistency Constraint | 三重语义一致性约束 Triple Semantic Consistency... | design | design_only | D-INTELLIGENCE/三重语义一致性约束 Triple Semantic Consistency Constraint | 三重语义一致性约束 Triple Semantic Consistency... | design | design_only |
| D-INTELLIGENCE/事件影响知识 Event Impact Knowledge | 事件影响知识 Event Impact Knowledge | design | design_only | D-INTELLIGENCE/事件影响知识 Event Impact Knowledge | 事件影响知识 Event Impact Knowledge | design | design_only |
| D-INTELLIGENCE/事件触发采集 Event-Triggered Collection | 事件触发采集 Event-Triggered Collection | design | design_only | D-INTELLIGENCE/事件触发采集 Event-Triggered Collection | 事件触发采集 Event-Triggered Collection | design | design_only |
| D-INTELLIGENCE/交互式解释 Interactive Explanation | 交互式解释 Interactive Explanation | design | design_only | D-INTELLIGENCE/交互式解释 Interactive Explanation | 交互式解释 Interactive Explanation | design | design_only |
| D-INTELLIGENCE/交易逻辑提取 Trading Logic Extraction | 交易逻辑提取 Trading Logic Extraction | design | design_only | D-INTELLIGENCE/交易逻辑提取 Trading Logic Extraction | 交易逻辑提取 Trading Logic Extraction | design | design_only |
| D-INTELLIGENCE/人工干预接口 Human Intervention Interface | 人工干预接口 Human Intervention Interface | design | design_only | D-INTELLIGENCE/人工干预接口 Human Intervention Interface | 人工干预接口 Human Intervention Interface | design | design_only |
| D-INTELLIGENCE/人机协作模式 Human-AI Collaboration Mode | 人机协作模式 Human-AI Collaboration Mode | design | design_only | D-INTELLIGENCE/人机协作模式 Human-AI Collaboration Mode | 人机协作模式 Human-AI Collaboration Mode | design | design_only |
| D-INTELLIGENCE/信息价值评分 Information Value Scoring | 信息价值评分 Information Value Scoring | design | design_only | D-INTELLIGENCE/信息价值评分 Information Value Scoring | 信息价值评分 Information Value Scoring | design | design_only |
| D-INTELLIGENCE/信息论过拟合检测 Information-Theoretic Overfitting Detection | 信息论过拟合检测 Information-Theoretic Overfi... | design | design_only | D-INTELLIGENCE/信息论过拟合检测 Information-Theoretic Overfitting Detection | 信息论过拟合检测 Information-Theoretic Overfi... | design | design_only |
| D-INTELLIGENCE/元反思 Meta-Reflection | 元反思 Meta-Reflection | design | design_only | D-INTELLIGENCE/元反思 Meta-Reflection | 元反思 Meta-Reflection | design | design_only |
| D-INTELLIGENCE/共形漂移检测 Conformal Drift Detection | 共形漂移检测 Conformal Drift Detection | design | design_only | D-INTELLIGENCE/共形漂移检测 Conformal Drift Detection | 共形漂移检测 Conformal Drift Detection | design | design_only |
| D-INTELLIGENCE/决策树学习 Decision Tree Learning | 决策树学习 Decision Tree Learning | design | design_only | D-INTELLIGENCE/决策树学习 Decision Tree Learning | 决策树学习 Decision Tree Learning | design | design_only |
| D-INTELLIGENCE/决策路径可视化 Decision Path Visualization | 决策路径可视化 Decision Path Visualization | design | design_only | D-INTELLIGENCE/决策路径可视化 Decision Path Visualization | 决策路径可视化 Decision Path Visualization | design | design_only |
| D-INTELLIGENCE/创意拓宽模式 Creative Broadening Mode | 创意拓宽模式 Creative Broadening Mode | design | design_only | D-INTELLIGENCE/创意拓宽模式 Creative Broadening Mode | 创意拓宽模式 Creative Broadening Mode | design | design_only |
| D-INTELLIGENCE/制度知识 Regime Knowledge | 制度知识 Regime Knowledge | design | design_only | D-INTELLIGENCE/制度知识 Regime Knowledge | 制度知识 Regime Knowledge | design | design_only |
| D-INTELLIGENCE/博弈知识 Game Theory Knowledge | 博弈知识 Game Theory Knowledge | design | design_only | D-INTELLIGENCE/博弈知识 Game Theory Knowledge | 博弈知识 Game Theory Knowledge | design | design_only |
| D-INTELLIGENCE/去噪 Denoising | 去噪 Denoising | design | design_only | D-INTELLIGENCE/去噪 Denoising | 去噪 Denoising | design | design_only |
| D-INTELLIGENCE/去重 Deduplication | 去重 Deduplication | design | design_only | D-INTELLIGENCE/去重 Deduplication | 去重 Deduplication | design | design_only |
| D-INTELLIGENCE/参数稳定性区域 Parameter Stability Plateau | 参数稳定性区域 Parameter Stability Plateau | design | design_only | D-INTELLIGENCE/参数稳定性区域 Parameter Stability Plateau | 参数稳定性区域 Parameter Stability Plateau | design | design_only |
| D-INTELLIGENCE/可微因果发现 Differentiable Causal Discovery NOTEARS+ | 可微因果发现 Differentiable Causal Discover... | design | design_only | D-INTELLIGENCE/可微因果发现 Differentiable Causal Discovery NOTEARS+ | 可微因果发现 Differentiable Causal Discover... | design | design_only |
| D-INTELLIGENCE/可解释性门控 Explainability Gate | 可解释性门控 Explainability Gate | design | design_only | D-INTELLIGENCE/可解释性门控 Explainability Gate | 可解释性门控 Explainability Gate | design | design_only |
| D-INTELLIGENCE/可解释设计约束 Explainable By Design Constraint | 可解释设计约束 Explainable By Design Constraint | design | design_only | D-INTELLIGENCE/可解释设计约束 Explainable By Design Constraint | 可解释设计约束 Explainable By Design Constraint | design | design_only |
| D-INTELLIGENCE/因子知识 Factor Knowledge | 因子知识 Factor Knowledge | design | design_only | D-INTELLIGENCE/因子知识 Factor Knowledge | 因子知识 Factor Knowledge | design | design_only |
| D-INTELLIGENCE/因子语义去重 Factor Semantic Deduplication | 因子语义去重 Factor Semantic Deduplication | design | design_only | D-INTELLIGENCE/因子语义去重 Factor Semantic Deduplication | 因子语义去重 Factor Semantic Deduplication | design | design_only |
| D-INTELLIGENCE/因果发现三阶段扩展 Causal Discovery 3-Stage Extension | 因果发现三阶段扩展 Causal Discovery 3-Stage Ex... | design | design_only | D-INTELLIGENCE/因果发现三阶段扩展 Causal Discovery 3-Stage Extension | 因果发现三阶段扩展 Causal Discovery 3-Stage Ex... | design | design_only |
| D-INTELLIGENCE/因果发现引擎 Causal Discovery Engine | 因果发现引擎 Causal Discovery Engine | design | design_only | D-INTELLIGENCE/因果发现引擎 Causal Discovery Engine | 因果发现引擎 Causal Discovery Engine | design | design_only |
| D-INTELLIGENCE/因果约束反事实解释 Causal-Constrained Counterfactual Explanation | 因果约束反事实解释 Causal-Constrained Counterf... | design | design_only | D-INTELLIGENCE/因果约束反事实解释 Causal-Constrained Counterfactual Explanation | 因果约束反事实解释 Causal-Constrained Counterf... | design | design_only |
| D-INTELLIGENCE/因果验证层 Causal Validation Layer | 因果验证层 Causal Validation Layer | design | design_only | D-INTELLIGENCE/因果验证层 Causal Validation Layer | 因果验证层 Causal Validation Layer | design | design_only |
| D-INTELLIGENCE/在线EWC Online Elastic Weight Consolidation | 在线EWC Online Elastic Weight Consolida... | design | design_only | D-INTELLIGENCE/在线EWC Online Elastic Weight Consolidation | 在线EWC Online Elastic Weight Consolida... | design | design_only |
| D-INTELLIGENCE/多尺度漂移检测 Multi-Scale Drift Detection | 多尺度漂移检测 Multi-Scale Drift Detection | design | design_only | D-INTELLIGENCE/多尺度漂移检测 Multi-Scale Drift Detection | 多尺度漂移检测 Multi-Scale Drift Detection | design | design_only |
| D-INTELLIGENCE/多模态融合引擎 Multimodal Fusion Engine | 多模态融合引擎 Multimodal Fusion Engine | design | design_only | D-INTELLIGENCE/多模态融合引擎 Multimodal Fusion Engine | 多模态融合引擎 Multimodal Fusion Engine | design | design_only |
| D-INTELLIGENCE/学习系统反馈路径 Path | 学习系统反馈路径 Path | design | design_only | D-INTELLIGENCE/学习系统反馈路径 Path | 学习系统反馈路径 Path | design | design_only |
| D-INTELLIGENCE/宏观因果传导路径 Macro Causal Transmission Path | 宏观因果传导路径 Macro Causal Transmission Path | design | design_only | D-INTELLIGENCE/宏观因果传导路径 Macro Causal Transmission Path | 宏观因果传导路径 Macro Causal Transmission Path | design | design_only |
| D-INTELLIGENCE/定时采集 Scheduled Collection | 定时采集 Scheduled Collection | design | design_only | D-INTELLIGENCE/定时采集 Scheduled Collection | 定时采集 Scheduled Collection | design | design_only |
| D-INTELLIGENCE/对抗性知识增强 Adversarial Knowledge Enhancement | 对抗性知识增强 Adversarial Knowledge Enhance... | design | design_only | D-INTELLIGENCE/对抗性知识增强 Adversarial Knowledge Enhancement | 对抗性知识增强 Adversarial Knowledge Enhance... | design | design_only |
| D-INTELLIGENCE/市场状态感知Walk-Forward Regime-Aware Walk-Forward | 市场状态感知Walk-Forward Regime-Aware Walk-... | design | design_only | D-INTELLIGENCE/市场状态感知Walk-Forward Regime-Aware Walk-Forward | 市场状态感知Walk-Forward Regime-Aware Walk-... | design | design_only |
| D-INTELLIGENCE/市场状态知识 Market State Knowledge | 市场状态知识 Market State Knowledge | design | design_only | D-INTELLIGENCE/市场状态知识 Market State Knowledge | 市场状态知识 Market State Knowledge | design | design_only |
| D-INTELLIGENCE/带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | 带干预的时序因果发现 Intervention-Enhanced Temp... | design | design_only | D-INTELLIGENCE/带干预的时序因果发现 Intervention-Enhanced Temporal Causal Discovery | 带干预的时序因果发现 Intervention-Enhanced Temp... | design | design_only |
| D-INTELLIGENCE/带推理路径的KG-RAG KG-RAG with Reasoning Path | 带推理路径的KG-RAG KG-RAG with Reasoning Path | design | design_only | D-INTELLIGENCE/带推理路径的KG-RAG KG-RAG with Reasoning Path | 带推理路径的KG-RAG KG-RAG with Reasoning Path | design | design_only |
| D-INTELLIGENCE/延迟离线学习模式 Delayed Offline Learning Mode | 延迟离线学习模式 Delayed Offline Learning Mode | design | design_only | D-INTELLIGENCE/延迟离线学习模式 Delayed Offline Learning Mode | 延迟离线学习模式 Delayed Offline Learning Mode | design | design_only |
| D-INTELLIGENCE/手动提交 Manual Submission | 手动提交 Manual Submission | design | design_only | D-INTELLIGENCE/手动提交 Manual Submission | 手动提交 Manual Submission | design | design_only |
| D-INTELLIGENCE/技能三元组 Skill Triple | 技能三元组 Skill Triple | design | design_only | D-INTELLIGENCE/技能三元组 Skill Triple | 技能三元组 Skill Triple | design | design_only |
| D-INTELLIGENCE/教训知识 Lesson Learned Knowledge | 教训知识 Lesson Learned Knowledge | design | design_only | D-INTELLIGENCE/教训知识 Lesson Learned Knowledge | 教训知识 Lesson Learned Knowledge | design | design_only |
| D-INTELLIGENCE/数学反思闭环 Mathematical Reflection Loop | 数学反思闭环 Mathematical Reflection Loop | design | design_only | D-INTELLIGENCE/数学反思闭环 Mathematical Reflection Loop | 数学反思闭环 Mathematical Reflection Loop | design | design_only |
| D-INTELLIGENCE/方法论知识 Methodology Knowledge | 方法论知识 Methodology Knowledge | design | design_only | D-INTELLIGENCE/方法论知识 Methodology Knowledge | 方法论知识 Methodology Knowledge | design | design_only |
| D-INTELLIGENCE/时序基础模型骨干 TimesFM Foundation Model Backbone | 时序基础模型骨干 TimesFM Foundation Model Bac... | design | design_only | D-INTELLIGENCE/时序基础模型骨干 TimesFM Foundation Model Backbone | 时序基础模型骨干 TimesFM Foundation Model Bac... | design | design_only |
| D-INTELLIGENCE/时滞因果扩展 Lagged Causal Extension | 时滞因果扩展 Lagged Causal Extension | design | design_only | D-INTELLIGENCE/时滞因果扩展 Lagged Causal Extension | 时滞因果扩展 Lagged Causal Extension | design | design_only |
| D-INTELLIGENCE/术语标准化 Terminology Normalization | 术语标准化 Terminology Normalization | design | design_only | D-INTELLIGENCE/术语标准化 Terminology Normalization | 术语标准化 Terminology Normalization | design | design_only |
| D-INTELLIGENCE/板块轮动知识 Sector Rotation Knowledge | 板块轮动知识 Sector Rotation Knowledge | design | design_only | D-INTELLIGENCE/板块轮动知识 Sector Rotation Knowledge | 板块轮动知识 Sector Rotation Knowledge | design | design_only |
| D-INTELLIGENCE/格式转换 Format Conversion | 格式转换 Format Conversion | design | design_only | D-INTELLIGENCE/格式转换 Format Conversion | 格式转换 Format Conversion | design | design_only |
| D-INTELLIGENCE/模块工厂 Module Factory | 模块工厂 Module Factory | design | design_only | D-INTELLIGENCE/模块工厂 Module Factory | 模块工厂 Module Factory | design | design_only |
| D-INTELLIGENCE/流动性知识 Liquidity Knowledge | 流动性知识 Liquidity Knowledge | design | design_only | D-INTELLIGENCE/流动性知识 Liquidity Knowledge | 流动性知识 Liquidity Knowledge | design | design_only |

> (仅显示前 200 个模块，共 273 个)

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
    subgraph D_INTELLIGENCE["D-INTELLIGENCE context_management"]
        D_INTELLIGENCE_3_3_Stage_Decision_Gate["3阶段决策门控 3-Stage Decision Gate design"]
        D_INTELLIGENCE_4_Level_Risk_Control_Decision_Gating_4["4 Level Risk Control Decision Gating 4级风控决策门控 design"]
        D_INTELLIGENCE_4_Level_Risk_Decision_Gate_4["4-Level Risk Decision Gate 4级风控决策门控 design"]
        D_INTELLIGENCE_7_Stage_Learning_Pipeline_7["7 Stage Learning Pipeline 7阶段学习流水线 design"]
        D_INTELLIGENCE_A_B_A_B_Testing_Framework["A/B测试框架 A/B Testing Framework design"]
        D_INTELLIGENCE_A8_Learning_System_Architecture_A8["A8 Learning System Architecture A8学习系统架构 design"]
        D_INTELLIGENCE_A8_Learning_System_Interface_A8["A8 Learning System Interface A8学习系统接口 design"]
        D_INTELLIGENCE_AI["AI协作策略与人机信任模型 design"]
        D_INTELLIGENCE_AI_1["AI自治运维 design"]
        D_INTELLIGENCE_Adaptive_Walk_Forward_Walk_Forward["Adaptive Walk-Forward 自适应Walk-Forward design"]
        D_INTELLIGENCE_Agent_Drift_Detection_Agent["Agent Drift Detection Agent漂移检测 design"]
        D_INTELLIGENCE_AlphaEvolve_AlphaEvolve_Meta_Level_Infrastructure_Evolution["AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infr... design"]
        D_INTELLIGENCE_AlphaFin_AlphaFin_Unified_Multimodal_Framework["AlphaFin统一多模态框架 AlphaFin Unified Multimodal Fra... design"]
        D_INTELLIGENCE_ArchitectureOptimizer_Agent_Agent["ArchitectureOptimizer Agent 架构优化Agent design"]
        D_INTELLIGENCE_Auto_Backtest_Simulation["Auto Backtest & Simulation 自动回测与仿真 design"]
        D_INTELLIGENCE_AutoML_Engine_ML["AutoML Engine 自动ML引擎 design"]
        D_INTELLIGENCE_AutoSkill_AutoSkill_Automatic_Skill_Discovery["AutoSkill自动技能发现 AutoSkill Automatic Skill Disco... design"]
        D_INTELLIGENCE_A_A_Share_Special_Data["A股特色数据 A-Share Special Data design"]
        D_INTELLIGENCE_Backtest_to_Production_Deployer["Backtest-to-Production Deployer 回测到生产部署器 design"]
        D_INTELLIGENCE_BacktestCompleted["BacktestCompleted 回测已完成 design"]
        D_INTELLIGENCE_CPCV_v2_Combinatorial_Purged_Cross_Validation_v2_CPCV_v2_v2["CPCV v2 Combinatorial Purged Cross-Validation v... design"]
        D_INTELLIGENCE_Causal_Factor_Validator["Causal Factor Validator 因果因子验证器 design"]
        D_INTELLIGENCE_Causal_KG["Causal KG 因果方向标注 design"]
        D_INTELLIGENCE_Causal_SHAP_Shapley["Causal SHAP 因果Shapley值 design"]
        D_INTELLIGENCE_CausalEdge["CausalEdge 因果边 design"]
        D_INTELLIGENCE_CausalNLP["CausalNLP 文本因果声明提取 design"]
        D_INTELLIGENCE_Classified_Knowledge_Package["Classified Knowledge Package 分类知识包 design"]
        D_INTELLIGENCE_Cluster_Behavior_Protection["Cluster Behavior Protection 群集行为防护 design"]
        D_INTELLIGENCE_CodeGenerator_Agent_Agent["CodeGenerator Agent 代码生成Agent design"]
        D_INTELLIGENCE_Collection_Scheduler["Collection Scheduler 采集调度器 design"]
    end
    D_INTELLIGENCE_AutoML_Engine_ML -.->|import_depends| D_INTELLIGENCE_Backtest_to_Production_Deployer
    D_INTELLIGENCE_Causal_Factor_Validator -.->|import_depends| D_INTELLIGENCE_A8_Learning_System_Architecture_A8
    D_INTELLIGENCE_ArchitectureOptimizer_Agent_Agent -.->|import_depends| D_INTELLIGENCE_CodeGenerator_Agent_Agent
    D_INTELLIGENCE_Agent_Drift_Detection_Agent -.->|import_depends| D_INTELLIGENCE_Cluster_Behavior_Protection
    D_SIGNAL["D-SIGNAL design"]
    D_INTELLIGENCE_AI -.->|contract| D_SIGNAL
    D_RISK["D-RISK design"]
    D_INTELLIGENCE_Classified_Knowledge_Package -.->|event| D_RISK
    D_INFRA_RUNTIME["D-INFRA_RUNTIME design"]
    D_INTELLIGENCE_3_3_Stage_Decision_Gate -.->|data| D_INFRA_RUNTIME
    D_FACTOR["D-FACTOR design"]
    D_INTELLIGENCE_A_A_Share_Special_Data -.->|contract| D_FACTOR
    D_KNOWLEDGE["D-KNOWLEDGE design"]
    D_INTELLIGENCE_A_A_Share_Special_Data -.->|contract| D_KNOWLEDGE
    D_INTELLIGENCE_A_A_Share_Special_Data -.->|config_depends| D_SIGNAL
    D_INTELLIGENCE_CausalNLP -.->|contract| D_FACTOR
    D_SECURITY["D-SECURITY design"]
    D_INTELLIGENCE_Causal_Factor_Validator -.->|config_depends| D_SECURITY
    D_ML_SERVE["D-ML_SERVE design"]
    D_INTELLIGENCE_CPCV_v2_Combinatorial_Purged_Cross_Validation_v2_CPCV_v2_v2 -.->|contract| D_ML_SERVE
    D_INTELLIGENCE_Adaptive_Walk_Forward_Walk_Forward -.->|data| D_RISK
    D_INTELLIGENCE_Adaptive_Walk_Forward_Walk_Forward -.->|contract| D_ML_SERVE
    D_TRADING["D-TRADING design"]
    D_INTELLIGENCE_A_B_A_B_Testing_Framework -.->|event| D_TRADING
    D_INTELLIGENCE_AutoSkill_AutoSkill_Automatic_Skill_Discovery -.->|event| D_SECURITY
    D_INTELLIGENCE_ArchitectureOptimizer_Agent_Agent -.->|data| D_RISK
    D_PF_CORE["D-PF_CORE design"]
    D_INTELLIGENCE_CausalEdge -.->|event| D_PF_CORE
    D_INTEGRATION["D-INTEGRATION design"]
    D_INTEGRATION -.->|contract| D_INTELLIGENCE_AI
    D_GOVERNANCE["D-GOVERNANCE design"]
    D_GOVERNANCE -.->|event| D_INTELLIGENCE_AI
    D_INFRA_OPS["D-INFRA_OPS design"]
    D_INFRA_OPS -.->|config_depends| D_INTELLIGENCE_AutoML_Engine_ML
    D_COMPLIANCE["D-COMPLIANCE design"]
    D_COMPLIANCE -.->|contract| D_INTELLIGENCE_Backtest_to_Production_Deployer
    D_AUTONOMY_CORE["D-AUTONOMY_CORE design"]
    D_AUTONOMY_CORE -.->|data| D_INTELLIGENCE_Classified_Knowledge_Package
    D_INFRA_OPS -.->|data| D_INTELLIGENCE_Classified_Knowledge_Package
    D_GOVERNANCE -.->|contract| D_INTELLIGENCE_A_A_Share_Special_Data
    D_OPS["D-OPS design"]
    D_OPS -.->|data| D_INTELLIGENCE_CausalNLP
    D_GOV_AUDIT["D-GOV_AUDIT design"]
    D_GOV_AUDIT -.->|data| D_INTELLIGENCE_Causal_KG
    D_GOVERNANCE -.->|contract| D_INTELLIGENCE_Causal_Factor_Validator
    D_AUTONOMY_CORE -.->|event| D_INTELLIGENCE_CPCV_v2_Combinatorial_Purged_Cross_Validation_v2_CPCV_v2_v2
    D_AUTONOMY_PERM["D-AUTONOMY_PERM design"]
    D_AUTONOMY_PERM -.->|contract| D_INTELLIGENCE_Adaptive_Walk_Forward_Walk_Forward
    D_ALT_DATA["D-ALT_DATA design"]
    D_ALT_DATA -.->|data| D_INTELLIGENCE_Adaptive_Walk_Forward_Walk_Forward
    D_COMPLIANCE -.->|data| D_INTELLIGENCE_A_B_A_B_Testing_Framework
    D_AUTONOMY_PERM -.->|data| D_INTELLIGENCE_A_B_A_B_Testing_Framework
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class D_INTELLIGENCE_3_3_Stage_Decision_Gate,D_INTELLIGENCE_4_Level_Risk_Control_Decision_Gating_4,D_INTELLIGENCE_4_Level_Risk_Decision_Gate_4,D_INTELLIGENCE_7_Stage_Learning_Pipeline_7,D_INTELLIGENCE_A_B_A_B_Testing_Framework,D_INTELLIGENCE_A8_Learning_System_Architecture_A8,D_INTELLIGENCE_A8_Learning_System_Interface_A8,D_INTELLIGENCE_AI,D_INTELLIGENCE_AI_1,D_INTELLIGENCE_Adaptive_Walk_Forward_Walk_Forward,D_INTELLIGENCE_Agent_Drift_Detection_Agent,D_INTELLIGENCE_AlphaEvolve_AlphaEvolve_Meta_Level_Infrastructure_Evolution,D_INTELLIGENCE_AlphaFin_AlphaFin_Unified_Multimodal_Framework,D_INTELLIGENCE_ArchitectureOptimizer_Agent_Agent,D_INTELLIGENCE_Auto_Backtest_Simulation,D_INTELLIGENCE_AutoML_Engine_ML,D_INTELLIGENCE_AutoSkill_AutoSkill_Automatic_Skill_Discovery,D_INTELLIGENCE_A_A_Share_Special_Data,D_INTELLIGENCE_Backtest_to_Production_Deployer,D_INTELLIGENCE_BacktestCompleted,D_INTELLIGENCE_CPCV_v2_Combinatorial_Purged_Cross_Validation_v2_CPCV_v2_v2,D_INTELLIGENCE_Causal_Factor_Validator,D_INTELLIGENCE_Causal_KG,D_INTELLIGENCE_Causal_SHAP_Shapley,D_INTELLIGENCE_CausalEdge,D_INTELLIGENCE_CausalNLP,D_INTELLIGENCE_Classified_Knowledge_Package,D_INTELLIGENCE_Cluster_Behavior_Protection,D_INTELLIGENCE_CodeGenerator_Agent_Agent,D_INTELLIGENCE_Collection_Scheduler design
    class D_SIGNAL,D_RISK,D_INFRA_RUNTIME,D_FACTOR,D_KNOWLEDGE,D_SECURITY,D_ML_SERVE,D_TRADING,D_PF_CORE,D_INTEGRATION,D_GOVERNANCE,D_INFRA_OPS,D_COMPLIANCE,D_AUTONOMY_CORE,D_OPS,D_GOV_AUDIT,D_AUTONOMY_PERM,D_ALT_DATA external_design
```

> (依赖图最多显示前 30 个节点，共 273 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-RISK | 35 | data,contract,event,config_depends | D-RISK | 35 | data,contract,event,config_depends |
| D-SECURITY | 23 | event,contract,data,config_depends | D-SECURITY | 23 | event,contract,data,config_depends |
| D-SIGNAL | 22 | contract,event,data,config_depends | D-SIGNAL | 22 | contract,event,data,config_depends |
| D-FACTOR | 22 | contract,config_depends,event,data | D-FACTOR | 22 | contract,config_depends,event,data |
| D-KNOWLEDGE | 18 | config_depends,event,contract,data,domain_dependency | D-KNOWLEDGE | 18 | config_depends,event,contract,data,domain_dependency |
| D-ML_TRAIN | 13 | import_depends,config_depends,data,contract,event | D-ML_TRAIN | 13 | import_depends,config_depends,data,contract,event |
| D-MKT_DATA | 13 | event,config_depends,data,contract | D-MKT_DATA | 13 | event,config_depends,data,contract |
| D-INFRA_RUNTIME | 10 | import_depends,contract,data,event,config_depends | D-INFRA_RUNTIME | 10 | import_depends,contract,data,event,config_depends |
| D-PF_CORE | 7 | config_depends,contract,event,data | D-PF_CORE | 7 | config_depends,contract,event,data |
| D-GOVERNANCE | 7 | config_depends,import_depends | D-GOVERNANCE | 7 | config_depends,import_depends |
| D-ML_SERVE | 6 | event,contract,data,domain_dependency | D-ML_SERVE | 6 | event,contract,data,domain_dependency |
| D-INTEGRATION | 6 | import_depends | D-INTEGRATION | 6 | import_depends |
| D-EX_CORE | 6 | data,contract,config_depends | D-EX_CORE | 6 | data,contract,config_depends |
| D-POSITION | 5 | contract,config_depends | D-POSITION | 5 | contract,config_depends |
| D-EX_SOR | 4 | data,event,contract | D-EX_SOR | 4 | data,event,contract |
| D-DATA_ENG | 4 | data,event,config_depends | D-DATA_ENG | 4 | data,event,config_depends |
| D-TRADING | 3 | import_depends,event | D-TRADING | 3 | import_depends,event |
| D-SIMULATION | 3 | import_depends | D-SIMULATION | 3 | import_depends |
| D-GOV_RULE | 2 | contract,import_depends | D-GOV_RULE | 2 | contract,import_depends |
| D-SHARED | 1 | import_depends | D-SHARED | 1 | import_depends |
| D-AUTONOMY_CORE | 1 | import_depends | D-AUTONOMY_CORE | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 84 | test_depends,import_depends,event,contract,data,config_depends | D-GOVERNANCE | 84 | test_depends,import_depends,event,contract,data,config_depends |
| D-COMPLIANCE | 60 | contract,config_depends,event,data | D-COMPLIANCE | 60 | contract,config_depends,event,data |
| D-INTEGRATION | 37 | import_depends,contract,data,event,config_depends | D-INTEGRATION | 37 | import_depends,contract,data,event,config_depends |
| D-AUTONOMY_CORE | 32 | import_depends,contract,config_depends,event,data,domain_dependency | D-AUTONOMY_CORE | 32 | import_depends,contract,config_depends,event,data,domain_dependency |
| D-INFRA_OPS | 30 | event,contract,config_depends,data | D-INFRA_OPS | 30 | event,contract,config_depends,data |
| D-OPS | 12 | event,contract,data,config_depends | D-OPS | 12 | event,contract,data,config_depends |
| D-AUTONOMY_PERM | 10 | data,contract,config_depends | D-AUTONOMY_PERM | 10 | data,contract,config_depends |
| D-SIMULATION | 9 | data,contract,event | D-SIMULATION | 9 | data,contract,event |
| D-FRONTEND | 9 | event,contract,data | D-FRONTEND | 9 | event,contract,data |
| D-PF_ALLOC | 8 | config_depends,contract,event,data | D-PF_ALLOC | 8 | config_depends,contract,event,data |
| D-DATA_GOV | 7 | event,contract,data | D-DATA_GOV | 7 | event,contract,data |
| D-TRADING | 6 | import_depends | D-TRADING | 6 | import_depends |
| D-CROSS_ASSET | 6 | contract,data,config_depends | D-CROSS_ASSET | 6 | contract,data,config_depends |
| D-ALT_DATA | 4 | config_depends,contract,data | D-ALT_DATA | 4 | config_depends,contract,data |
| D-REPORTING | 3 | data,event | D-REPORTING | 3 | data,event |
| D-SELL_DECISION | 2 | data,contract | D-SELL_DECISION | 2 | data,contract |
| D-SECURITY | 1 | import_depends | D-SECURITY | 1 | import_depends |
| D-GOV_AUDIT | 1 | data | D-GOV_AUDIT | 1 | data |
| D-DATA_SEC | 1 | config_depends | D-DATA_SEC | 1 | config_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
