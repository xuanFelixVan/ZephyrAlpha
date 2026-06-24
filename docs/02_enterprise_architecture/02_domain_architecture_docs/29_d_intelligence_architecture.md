---
doc_type: domain_architecture_diagram
title: D-INTELLIGENCE 上下文管理架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 29_d_intelligence / 上下文管理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示上下文管理（D-INTELLIGENCE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 上下文管理（D-INTELLIGENCE）的模块分布。共 274 个模块 / 274 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (56 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/intelligence/__init__.py  [prototype]               │
│   src/zephyr/intelligence/_extensions/__init__.py  [scaffold_... │
│   src/zephyr/intelligence/api/__init__.py  [scaffold_placehol... │
│   src/zephyr/intelligence/core/__init__.py  [scaffold_placeho... │
│   src/zephyr/intelligence/infrastructure/__init__.py  [scaffo... │
│   src/zephyr/intelligence/model_drift_detector.py  [prototype]   │
│   src/zephyr/intelligence/model_evaluation/__init__.py  [prot... │
│   src/zephyr/intelligence/model_evaluation/activate.py  [prod... │
│   src/zephyr/intelligence/model_evaluation/backtest_base.py  ... │
│   src/zephyr/intelligence/model_evaluation/experiment_tracker... │
│   src/zephyr/intelligence/model_evaluation/implementations/__... │
│   src/zephyr/intelligence/model_evaluation/implementations/de... │
│   src/zephyr/intelligence/model_evaluation/implementations/de... │
│   src/zephyr/intelligence/model_evaluation/inference_base.py ... │
│   src/zephyr/intelligence/model_evaluation/kb_repo.py  [produ... │
│   src/zephyr/intelligence/model_evaluation/notebook_integrati... │
│   src/zephyr/intelligence/model_evaluation/reranker.py  [prod... │
│   src/zephyr/intelligence/model_evaluation/sync_engine.py  [p... │
│   ...还有 38 个模块 / 38 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (218 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   3阶段决策门控 3-Stage Decision Gate  [design]                  │
│   4 Level Risk Control Decision Gating 4级风控决策门控  [design] │
│   4-Level Risk Decision Gate 4级风控决策门控  [design]           │
│   7 Stage Learning Pipeline 7阶段学习流水线  [design]            │
│   A/B测试框架 A/B Testing Framework  [design]                    │
│   A8 Learning System Architecture A8学习系统架构  [design]       │
│   A8 Learning System Interface A8学习系统接口  [design]          │
│   AI协作策略与人机信任模型  [design]                             │
│   AI自治运维  [design]                                           │
│   Adaptive Walk-Forward 自适应Walk-Forward  [design]             │
│   Agent Drift Detection Agent漂移检测  [design]                  │
│   AlphaEvolve元级基础设施进化 AlphaEvolve Meta-Level Infrastr... │
│   AlphaFin统一多模态框架 AlphaFin Unified Multimodal Framewor... │
│   ArchitectureOptimizer Agent 架构优化Agent  [design]            │
│   Auto Backtest & Simulation 自动回测与仿真  [design]            │
│   AutoML Engine 自动ML引擎  [design]                             │
│   AutoSkill自动技能发现 AutoSkill Automatic Skill Discovery  ... │
│   A股特色数据 A-Share Special Data  [design]                     │
│   ...还有 200 个模块 / 200 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 274 个模块 / 274 modules）。

### L1 基础层 / Foundation Layer (56 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/intelligence/__init__.py | src/zephyr/intelligence/__init__.py | prototype | orphan |
| 2 | src/zephyr/intelligence/_extensions/__init__.py | src/zephyr/intelligence/_extensions/_... | scaffold_placeholder | orphan |
| 3 | src/zephyr/intelligence/api/__init__.py | src/zephyr/intelligence/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/intelligence/core/__init__.py | src/zephyr/intelligence/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/intelligence/infrastructure/__init__.py | src/zephyr/intelligence/infrastructur... | scaffold_placeholder | orphan |
| 6 | src/zephyr/intelligence/model_drift_detector.py | src/zephyr/intelligence/model_drift_d... | prototype | draft |
| 7 | src/zephyr/intelligence/model_evaluation/__init__.py | src/zephyr/intelligence/model_evaluat... | prototype | draft |
| 8 | src/zephyr/intelligence/model_evaluation/activate.py | src/zephyr/intelligence/model_evaluat... | production | draft |
| 9 | src/zephyr/intelligence/model_evaluation/backtest_base.py | src/zephyr/intelligence/model_evaluat... | prototype | draft |
| 10 | src/zephyr/intelligence/model_evaluation/experiment_track... | src/zephyr/intelligence/model_evaluat... | prototype | draft |
| 11 | src/zephyr/intelligence/model_evaluation/implementations/... | src/zephyr/intelligence/model_evaluat... | prototype | draft |
| 12 | src/zephyr/intelligence/model_evaluation/implementations/... | src/zephyr/intelligence/model_evaluat... | prototype | draft |
| 13 | src/zephyr/intelligence/model_evaluation/implementations/... | src/zephyr/intelligence/model_evaluat... | production | draft |
| 14 | src/zephyr/intelligence/model_evaluation/inference_base.py | src/zephyr/intelligence/model_evaluat... | production | draft |
| 15 | src/zephyr/intelligence/model_evaluation/kb_repo.py | src/zephyr/intelligence/model_evaluat... | production | draft |
| 16 | src/zephyr/intelligence/model_evaluation/notebook_integra... | src/zephyr/intelligence/model_evaluat... | prototype | draft |
| 17 | src/zephyr/intelligence/model_evaluation/reranker.py | src/zephyr/intelligence/model_evaluat... | production | draft |
| 18 | src/zephyr/intelligence/model_evaluation/sync_engine.py | src/zephyr/intelligence/model_evaluat... | prototype | draft |
| 19 | src/zephyr/intelligence/model_evaluation/target_lib/__ini... | src/zephyr/intelligence/model_evaluat... | prototype | orphan |
| 20 | src/zephyr/intelligence/model_evaluation/unified_memory_a... | src/zephyr/intelligence/model_evaluat... | production | draft |
| 21 | src/zephyr/intelligence/model_profiling/__init__.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 22 | src/zephyr/intelligence/model_profiling/benchmark_suite.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 23 | src/zephyr/intelligence/model_profiling/capability_passpo... | src/zephyr/intelligence/model_profili... | production | draft |
| 24 | src/zephyr/intelligence/model_profiling/cli.py | src/zephyr/intelligence/model_profili... | production | draft |
| 25 | src/zephyr/intelligence/model_profiling/deepseek_v4_chat.py | src/zephyr/intelligence/model_profili... | production | draft |
| 26 | src/zephyr/intelligence/model_profiling/exam_orchestrator.py | src/zephyr/intelligence/model_profili... | production | draft |
| 27 | src/zephyr/intelligence/model_profiling/exam_test_cases.py | src/zephyr/intelligence/model_profili... | production | draft |
| 28 | src/zephyr/intelligence/model_profiling/model_discovery.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 29 | src/zephyr/intelligence/model_profiling/pipeline/__init__.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 30 | src/zephyr/intelligence/model_profiling/pipeline/benchmar... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 31 | src/zephyr/intelligence/model_profiling/pipeline/capabili... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 32 | src/zephyr/intelligence/model_profiling/pipeline/cli.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 33 | src/zephyr/intelligence/model_profiling/pipeline/deepseek... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 34 | src/zephyr/intelligence/model_profiling/pipeline/exam_orc... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 35 | src/zephyr/intelligence/model_profiling/pipeline/exam_tes... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 36 | src/zephyr/intelligence/model_profiling/pipeline/model_di... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 37 | src/zephyr/intelligence/model_profiling/pipeline/profiler.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 38 | src/zephyr/intelligence/model_profiling/pipeline/results_... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 39 | src/zephyr/intelligence/model_profiling/pipeline/task_mod... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 40 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 41 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | draft |
| 42 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | draft |
| 43 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 44 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 45 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 46 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 47 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | draft |
| 48 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | draft |
| 49 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | draft |
| 50 | src/zephyr/intelligence/model_profiling/pipeline_routing/... | src/zephyr/intelligence/model_profili... | production | draft |
| 51 | src/zephyr/intelligence/model_profiling/profiler.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 52 | src/zephyr/intelligence/model_profiling/provider_data.py | src/zephyr/intelligence/model_profili... | production | draft |
| 53 | src/zephyr/intelligence/model_profiling/results_writer.py | src/zephyr/intelligence/model_profili... | prototype | draft |
| 54 | src/zephyr/intelligence/model_profiling/task_model_learne... | src/zephyr/intelligence/model_profili... | prototype | draft |
| 55 | src/zephyr/intelligence/models/__init__.py | src/zephyr/intelligence/models/__init... | scaffold_placeholder | orphan |
| 56 | src/zephyr/intelligence/services/__init__.py | src/zephyr/intelligence/services/__in... | scaffold_placeholder | orphan |

### 未分类 / Unclassified (218 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-INTELLIGENCE/3阶段决策门控 3-Stage Decision Gate | 3阶段决策门控 3-Stage Decision Gate | design | design_only |
| 2 | D-INTELLIGENCE/4 Level Risk Control Decision Gating 4级风... | 4 Level Risk Control Decision Gating ... | design | design_only |
| 3 | D-INTELLIGENCE/4-Level Risk Decision Gate 4级风控决策门控 | 4-Level Risk Decision Gate 4级风控决... | design | design_only |
| 4 | D-INTELLIGENCE/7 Stage Learning Pipeline 7阶段学习流水线 | 7 Stage Learning Pipeline 7阶段学习流... | design | design_only |
| 5 | D-INTELLIGENCE/A/B测试框架 A/B Testing Framework | A/B测试框架 A/B Testing Framework | design | design_only |
| 6 | D-INTELLIGENCE/A8 Learning System Architecture A8学习系统... | A8 Learning System Architecture A8学... | design | design_only |
| 7 | D-INTELLIGENCE/A8 Learning System Interface A8学习系统接口 | A8 Learning System Interface A8学习系... | design | design_only |
| 8 | D-INTELLIGENCE/AI协作策略与人机信任模型 | AI协作策略与人机信任模型 | design | design_only |
| 9 | D-INTELLIGENCE/AI自治运维 | AI自治运维 | design | design_only |
| 10 | D-INTELLIGENCE/Adaptive Walk-Forward 自适应Walk-Forward | Adaptive Walk-Forward 自适应Walk-Forward | design | design_only |
| 11 | D-INTELLIGENCE/Agent Drift Detection Agent漂移检测 | Agent Drift Detection Agent漂移检测 | design | design_only |
| 12 | D-INTELLIGENCE/AlphaEvolve元级基础设施进化 AlphaEvolve Me... | AlphaEvolve元级基础设施进化 AlphaEvol... | design | design_only |
| 13 | D-INTELLIGENCE/AlphaFin统一多模态框架 AlphaFin Unified Mu... | AlphaFin统一多模态框架 AlphaFin Unifi... | design | design_only |
| 14 | D-INTELLIGENCE/ArchitectureOptimizer Agent 架构优化Agent | ArchitectureOptimizer Agent 架构优化A... | design | design_only |
| 15 | D-INTELLIGENCE/Auto Backtest & Simulation 自动回测与仿真 | Auto Backtest & Simulation 自动回测与... | design | design_only |
| 16 | D-INTELLIGENCE/AutoML Engine 自动ML引擎 | AutoML Engine 自动ML引擎 | design | design_only |
| 17 | D-INTELLIGENCE/AutoSkill自动技能发现 AutoSkill Automatic ... | AutoSkill自动技能发现 AutoSkill Autom... | design | design_only |
| 18 | D-INTELLIGENCE/A股特色数据 A-Share Special Data | A股特色数据 A-Share Special Data | design | design_only |
| 19 | D-INTELLIGENCE/Backtest-to-Production Deployer 回测到生产... | Backtest-to-Production Deployer 回测... | design | design_only |
| 20 | D-INTELLIGENCE/BacktestCompleted 回测已完成 | BacktestCompleted 回测已完成 | design | design_only |
| 21 | D-INTELLIGENCE/CPCV v2 Combinatorial Purged Cross-Validat... | CPCV v2 Combinatorial Purged Cross-Va... | design | design_only |
| 22 | D-INTELLIGENCE/Causal Factor Validator 因果因子验证器 | Causal Factor Validator 因果因子验证器 | design | design_only |
| 23 | D-INTELLIGENCE/Causal KG 因果方向标注 | Causal KG 因果方向标注 | design | design_only |
| 24 | D-INTELLIGENCE/Causal SHAP 因果Shapley值 | Causal SHAP 因果Shapley值 | design | design_only |
| 25 | D-INTELLIGENCE/CausalEdge 因果边 | CausalEdge 因果边 | design | design_only |
| 26 | D-INTELLIGENCE/CausalNLP 文本因果声明提取 | CausalNLP 文本因果声明提取 | design | design_only |
| 27 | D-INTELLIGENCE/Classified Knowledge Package 分类知识包 | Classified Knowledge Package 分类知识包 | design | design_only |
| 28 | D-INTELLIGENCE/Cluster Behavior Protection 群集行为防护 | Cluster Behavior Protection 群集行为防护 | design | design_only |
| 29 | D-INTELLIGENCE/CodeGenerator Agent 代码生成Agent | CodeGenerator Agent 代码生成Agent | design | design_only |
| 30 | D-INTELLIGENCE/Collection Scheduler 采集调度器 | Collection Scheduler 采集调度器 | design | design_only |
| 31 | D-INTELLIGENCE/Critic 批判器Agent | Critic 批判器Agent | design | design_only |
| 32 | D-INTELLIGENCE/Cross-Market Transmission Quantitative Mod... | Cross-Market Transmission Quantitativ... | design | design_only |
| 33 | D-INTELLIGENCE/D-RESEARCH | D-RESEARCH | design | design_only |
| 34 | D-INTELLIGENCE/DSL AST Sandbox Code Generation DSL+AST沙... | DSL AST Sandbox Code Generation DSL+A... | design | design_only |
| 35 | D-INTELLIGENCE/DSL AST Sandbox DSL+AST沙箱 | DSL AST Sandbox DSL+AST沙箱 | design | design_only |
| 36 | D-INTELLIGENCE/DSR扩展 Deflated Sharpe Ratio Extension | DSR扩展 Deflated Sharpe Ratio Extension | design | design_only |
| 37 | D-INTELLIGENCE/Data Quality Scorer 数据质量评分器 | Data Quality Scorer 数据质量评分器 | design | design_only |
| 38 | D-INTELLIGENCE/DeepSCM深度因果模型 DeepSCM Deep Causal Model | DeepSCM深度因果模型 DeepSCM Deep Caus... | design | design_only |
| 39 | D-INTELLIGENCE/Drift Alert 漂移告警 | Drift Alert 漂移告警 | design | design_only |
| 40 | D-INTELLIGENCE/E-RS-02 BacktestCompleted E-RS-02 Backtest... | E-RS-02 BacktestCompleted E-RS-02 Bac... | design | design_only |
| 41 | D-INTELLIGENCE/Effect Feedback Path 效果反馈路径 | Effect Feedback Path 效果反馈路径 | design | design_only |
| 42 | D-INTELLIGENCE/End-to-End Causal Factor Analysis 端到端因... | End-to-End Causal Factor Analysis 端... | design | design_only |
| 43 | D-INTELLIGENCE/Experiment Tracker实验追踪 | Experiment Tracker实验追踪 | design | design_only |
| 44 | D-INTELLIGENCE/ExperimentReproduced 实验复现 | ExperimentReproduced 实验复现 | design | design_only |
| 45 | D-INTELLIGENCE/Explainability Gate 可解释性门控 | Explainability Gate 可解释性门控 | design | design_only |
| 46 | D-INTELLIGENCE/Factor Mining Agent 因子挖掘Agent | Factor Mining Agent 因子挖掘Agent | design | design_only |
| 47 | D-INTELLIGENCE/Factor Proposal 因子提案 | Factor Proposal 因子提案 | design | design_only |
| 48 | D-INTELLIGENCE/Feature Store特征存储 | Feature Store特征存储 | design | design_only |
| 49 | D-INTELLIGENCE/FeatureStore PIT Feature Feed FeatureStore... | FeatureStore PIT Feature Feed Feature... | design | design_only |
| 50 | D-INTELLIGENCE/Filing NLP Engine 公告NLP引擎 | Filing NLP Engine 公告NLP引擎 | design | design_only |
| 51 | D-INTELLIGENCE/FinVision端到端图表→策略 FinVision End-to... | FinVision端到端图表→策略 FinVision E... | design | design_only |
| 52 | D-INTELLIGENCE/Generator 生成器Agent | Generator 生成器Agent | design | design_only |
| 53 | D-INTELLIGENCE/GraphRAG图增强检索 GraphRAG Graph-Enhanced... | GraphRAG图增强检索 GraphRAG Graph-Enh... | design | design_only |
| 54 | D-INTELLIGENCE/Hypothesis Manager 假设管理器 | Hypothesis Manager 假设管理器 | design | design_only |
| 55 | D-INTELLIGENCE/Hypothesis Manager假设管理 | Hypothesis Manager假设管理 | design | design_only |
| 56 | D-INTELLIGENCE/ICL作为元学习 ICL as Meta-Learning | ICL作为元学习 ICL as Meta-Learning | design | design_only |
| 57 | D-INTELLIGENCE/Judge 裁判Agent | Judge 裁判Agent | design | design_only |
| 58 | D-INTELLIGENCE/KG引导多跳推理 KG-Guided Multi-Hop Reasoning | KG引导多跳推理 KG-Guided Multi-Hop Re... | design | design_only |
| 59 | D-INTELLIGENCE/Knowledge Classification System 知识分类体系 | Knowledge Classification System 知识... | design | design_only |
| 60 | D-INTELLIGENCE/Knowledge Effectiveness Evaluator 知识效果... | Knowledge Effectiveness Evaluator 知... | design | design_only |
| 61 | D-INTELLIGENCE/Knowledge Quality Assessor 知识质量评估器 | Knowledge Quality Assessor 知识质量评... | design | design_only |
| 62 | D-INTELLIGENCE/K线分词机制 K-line Tokenization | K线分词机制 K-line Tokenization | design | design_only |
| 63 | D-INTELLIGENCE/LLM Research Agent LLM研究助手 | LLM Research Agent LLM研究助手 | design | design_only |
| 64 | D-INTELLIGENCE/LLM引导因果发现先验 LLM Prior Causal Disco... | LLM引导因果发现先验 LLM Prior Causal ... | design | design_only |
| 65 | D-INTELLIGENCE/LLM语义理解 LLM Semantic Understanding | LLM语义理解 LLM Semantic Understanding | design | design_only |
| 66 | D-INTELLIGENCE/LLM遗传编程变异算子 LLM Genetic Programmin... | LLM遗传编程变异算子 LLM Genetic Progr... | design | design_only |
| 67 | D-INTELLIGENCE/Learning System 7-Stage Pipeline 学习系统7... | Learning System 7-Stage Pipeline 学习... | design | design_only |
| 68 | D-INTELLIGENCE/Learning System Performance Attribution 学... | Learning System Performance Attributi... | design | design_only |
| 69 | D-INTELLIGENCE/LiNGAM | LiNGAM | design | design_only |
| 70 | D-INTELLIGENCE/Liquidity & Slippage Simulator 流动性与滑... | Liquidity & Slippage Simulator 流动性... | design | design_only |
| 71 | D-INTELLIGENCE/MAML快速适应 MAML Fast Adaptation | MAML快速适应 MAML Fast Adaptation | design | design_only |
| 72 | D-INTELLIGENCE/MLOps Closed Loop MLOps闭环 | MLOps Closed Loop MLOps闭环 | design | design_only |
| 73 | D-INTELLIGENCE/MLOps闭环 MLOps Closed Loop | MLOps闭环 MLOps Closed Loop | design | design_only |
| 74 | D-INTELLIGENCE/ML模型工厂 | ML模型工厂 | design | design_only |
| 75 | D-INTELLIGENCE/Market Regime Detector 市场制度检测器 | Market Regime Detector 市场制度检测器 | design | design_only |
| 76 | D-INTELLIGENCE/Meta-Harness 元优化器 Meta-Optimizer | Meta-Harness 元优化器 Meta-Optimizer | design | design_only |
| 77 | D-INTELLIGENCE/MethodologyLearner Agent 方法论学习Agent | MethodologyLearner Agent 方法论学习Agent | design | design_only |
| 78 | D-INTELLIGENCE/Module Dependency Graph 模块依赖图 | Module Dependency Graph 模块依赖图 | design | design_only |
| 79 | D-INTELLIGENCE/Module Factory Architecture 模块工厂架构 | Module Factory Architecture 模块工厂架构 | design | design_only |
| 80 | D-INTELLIGENCE/Module Factory 模块工厂 | Module Factory 模块工厂 | design | design_only |
| 81 | D-INTELLIGENCE/Module Matcher 模块匹配器 | Module Matcher 模块匹配器 | design | design_only |
| 82 | D-INTELLIGENCE/Module Registry 模块注册表 | Module Registry 模块注册表 | design | design_only |
| 83 | D-INTELLIGENCE/Module Requirement Spec 模块需求规格 | Module Requirement Spec 模块需求规格 | design | design_only |
| 84 | D-INTELLIGENCE/Monte Carlo Engine 蒙特卡洛引擎 | Monte Carlo Engine 蒙特卡洛引擎 | design | design_only |
| 85 | D-INTELLIGENCE/Multi Modal Knowledge Acquisition 多模态知... | Multi Modal Knowledge Acquisition 多... | design | design_only |
| 86 | D-INTELLIGENCE/Multimodal Knowledge Collection 多模态知识... | Multimodal Knowledge Collection 多模... | design | design_only |
| 87 | D-INTELLIGENCE/Neural Granger Causality 神经Granger因果 | Neural Granger Causality 神经Granger因果 | design | design_only |
| 88 | D-INTELLIGENCE/NewModule 新模块 | NewModule 新模块 | design | design_only |
| 89 | D-INTELLIGENCE/Notebook Integration Notebook集成 | Notebook Integration Notebook集成 | design | design_only |
| 90 | D-INTELLIGENCE/OCR 光学字符识别 | OCR 光学字符识别 | design | design_only |
| 91 | D-INTELLIGENCE/ODL-Net在线深度学习 ODL-Net Online Deep Le... | ODL-Net在线深度学习 ODL-Net Online De... | design | design_only |
| 92 | D-INTELLIGENCE/Order Matching Simulator 订单匹配模拟器 | Order Matching Simulator 订单匹配模拟器 | design | design_only |
| 93 | D-INTELLIGENCE/PC算法 PC Algorithm | PC算法 PC Algorithm | design | design_only |
| 94 | D-INTELLIGENCE/PDF预测引擎 PDF Prediction Engine | PDF预测引擎 PDF Prediction Engine | design | design_only |
| 95 | D-INTELLIGENCE/Paper Search 论文搜索 | Paper Search 论文搜索 | design | design_only |
| 96 | D-INTELLIGENCE/Paper Tracker 论文追踪器 | Paper Tracker 论文追踪器 | design | design_only |
| 97 | D-INTELLIGENCE/Point-in-Time门控 Point-in-Time Gating | Point-in-Time门控 Point-in-Time Gating | design | design_only |
| 98 | D-INTELLIGENCE/Probabilistic Backtesting 概率回测 | Probabilistic Backtesting 概率回测 | design | design_only |
| 99 | D-INTELLIGENCE/PromptOptimizer Agent 提示词优化Agent | PromptOptimizer Agent 提示词优化Agent | design | design_only |
| 100 | D-INTELLIGENCE/Purge Gap 清洗间隔 | Purge Gap 清洗间隔 | design | design_only |
| 101 | D-INTELLIGENCE/RISE 代码自纠正 Code Self-Correction | RISE 代码自纠正 Code Self-Correction | design | design_only |
| 102 | D-INTELLIGENCE/RSI Architecture RSI自进化架构 | RSI Architecture RSI自进化架构 | design | design_only |
| 103 | D-INTELLIGENCE/Reproducibility Manager可复现性管理 | Reproducibility Manager可复现性管理 | design | design_only |
| 104 | D-INTELLIGENCE/Reproducibility Pack Generator 可复现性包... | Reproducibility Pack Generator 可复现... | design | design_only |
| 105 | D-INTELLIGENCE/Research Asset Versioning 研究资产版本化 | Research Asset Versioning 研究资产版本化 | design | design_only |
| 106 | D-INTELLIGENCE/Research Catalog 研究目录 | Research Catalog 研究目录 | design | design_only |
| 107 | D-INTELLIGENCE/Research Collaboration Hub 研究协作中心 | Research Collaboration Hub 研究协作中心 | design | design_only |
| 108 | D-INTELLIGENCE/Research Data Manager 研究数据管理器 | Research Data Manager 研究数据管理器 | design | design_only |
| 109 | D-INTELLIGENCE/Research Data Sandbox 研究数据沙箱 | Research Data Sandbox 研究数据沙箱 | design | design_only |
| 110 | D-INTELLIGENCE/Research Discovery Knowledge Base 研究发现... | Research Discovery Knowledge Base 研... | design | design_only |
| 111 | D-INTELLIGENCE/Research Experiment Anomaly Detector 研究... | Research Experiment Anomaly Detector ... | design | design_only |
| 112 | D-INTELLIGENCE/Research Information Barrier 研究信息隔离 | Research Information Barrier 研究信息... | design | design_only |
| 113 | D-INTELLIGENCE/Research Information Isolation 研究信息隔离 | Research Information Isolation 研究信... | design | design_only |
| 114 | D-INTELLIGENCE/Research Knowledge Precipitator 研究知识沉... | Research Knowledge Precipitator 研究... | design | design_only |
| 115 | D-INTELLIGENCE/Research Reproducibility Pack Generator 研... | Research Reproducibility Pack Generat... | design | design_only |
| 116 | D-INTELLIGENCE/Research Workflow Engine 研究工作流引擎 | Research Workflow Engine 研究工作流引擎 | design | design_only |
| 117 | D-INTELLIGENCE/ResearchCompleted 研究完成 | ResearchCompleted 研究完成 | design | design_only |
| 118 | D-INTELLIGENCE/ResearchProject 研究项目 | ResearchProject 研究项目 | design | design_only |
| 119 | D-INTELLIGENCE/Researcher Agent 研究Agent | Researcher Agent 研究Agent | design | design_only |
| 120 | D-INTELLIGENCE/S0 多模态知识采集层 S0 Multimodal Knowledg... | S0 多模态知识采集层 S0 Multimodal Kno... | design | design_only |
| 121 | D-INTELLIGENCE/S1 知识清洗与结构化层 S1 Knowledge Cleanin... | S1 知识清洗与结构化层 S1 Knowledge Cl... | design | design_only |
| 122 | D-INTELLIGENCE/S2 知识分类与策略提取层 S2 Knowledge Class... | S2 知识分类与策略提取层 S2 Knowledge ... | design | design_only |
| 123 | D-INTELLIGENCE/S3 模块映射与工厂匹配层 S3 Module Mapping ... | S3 模块映射与工厂匹配层 S3 Module Map... | design | design_only |
| 124 | D-INTELLIGENCE/S4 模块创建与接入层 S4 Module Creation & I... | S4 模块创建与接入层 S4 Module Creatio... | design | design_only |
| 125 | D-INTELLIGENCE/S5 试运行与验证层 S5 Trial Run & Validatio... | S5 试运行与验证层 S5 Trial Run & Vali... | design | design_only |
| 126 | D-INTELLIGENCE/S6 元学习与自我进化层 S6 Meta-Learning & S... | S6 元学习与自我进化层 S6 Meta-Learnin... | design | design_only |
| 127 | D-INTELLIGENCE/SHAP值解释 SHAP Value Explanation | SHAP值解释 SHAP Value Explanation | design | design_only |
| 128 | D-INTELLIGENCE/STOP Prompt自优化 Prompt Self-Optimization | STOP Prompt自优化 Prompt Self-Optimiz... | design | design_only |
| 129 | D-INTELLIGENCE/Scenario Generator基础版 情景生成器基础版 | Scenario Generator基础版 情景生成器基... | design | design_only |
| 130 | D-INTELLIGENCE/Security Governance 安全与治理 | Security Governance 安全与治理 | design | design_only |
| 131 | D-INTELLIGENCE/Sentiment Engine 情感分析引擎 | Sentiment Engine 情感分析引擎 | design | design_only |
| 132 | D-INTELLIGENCE/Signal Confidence Scorer 信号置信度评分器 | Signal Confidence Scorer 信号置信度评... | design | design_only |
| 133 | D-INTELLIGENCE/Signal Extractor 信号提取器 | Signal Extractor 信号提取器 | design | design_only |
| 134 | D-INTELLIGENCE/Strategy Code Generation 策略代码生成 | Strategy Code Generation 策略代码生成 | design | design_only |
| 135 | D-INTELLIGENCE/Strategy Iteration Upgrader策略迭代升级 | Strategy Iteration Upgrader策略迭代升级 | design | design_only |
| 136 | D-INTELLIGENCE/Strategy Sandbox轻量版 策略沙盒轻量版 | Strategy Sandbox轻量版 策略沙盒轻量版 | design | design_only |
| 137 | D-INTELLIGENCE/Structured Knowledge Fragment 结构化知识片段 | Structured Knowledge Fragment 结构化... | design | design_only |
| 138 | D-INTELLIGENCE/Synthetic Backtesting合成回测 Synthetic Ba... | Synthetic Backtesting合成回测 Synthet... | design | design_only |
| 139 | D-INTELLIGENCE/Synthetic Data Generator基础版 合成数据生... | Synthetic Data Generator基础版 合成数... | design | design_only |
| 140 | D-INTELLIGENCE/TimePC时序因果发现 TimePC Temporal Causal ... | TimePC时序因果发现 TimePC Temporal Ca... | design | design_only |
| 141 | D-INTELLIGENCE/Trading Domain NLP Engine 交易领域NLP引擎 | Trading Domain NLP Engine 交易领域NLP... | design | design_only |
| 142 | D-INTELLIGENCE/VLM图表视觉理解 VLM Chart Visual Understan... | VLM图表视觉理解 VLM Chart Visual Unde... | design | design_only |
| 143 | D-INTELLIGENCE/Voyager 技能库 Skill Library | Voyager 技能库 Skill Library | design | design_only |
| 144 | D-INTELLIGENCE/Walk-Forward Analyzer完整版 Walk-Forward A... | Walk-Forward Analyzer完整版 Walk-Forw... | design | design_only |
| 145 | D-INTELLIGENCE/Whisper 语音转写引擎 | Whisper 语音转写引擎 | design | design_only |
| 146 | D-INTELLIGENCE/White's Reality Check 怀特现实检验 | White's Reality Check 怀特现实检验 | design | design_only |
| 147 | D-INTELLIGENCE/三层参数优化 3-Layer Parameter Optimization | 三层参数优化 3-Layer Parameter Optimi... | design | design_only |
| 148 | D-INTELLIGENCE/三重语义一致性 Triple Semantic Consistency | 三重语义一致性 Triple Semantic Consis... | design | design_only |
| 149 | D-INTELLIGENCE/三重语义一致性约束 Triple Semantic Consist... | 三重语义一致性约束 Triple Semantic Co... | design | design_only |
| 150 | D-INTELLIGENCE/事件影响知识 Event Impact Knowledge | 事件影响知识 Event Impact Knowledge | design | design_only |
| 151 | D-INTELLIGENCE/事件触发采集 Event-Triggered Collection | 事件触发采集 Event-Triggered Collection | design | design_only |
| 152 | D-INTELLIGENCE/交互式解释 Interactive Explanation | 交互式解释 Interactive Explanation | design | design_only |
| 153 | D-INTELLIGENCE/交易逻辑提取 Trading Logic Extraction | 交易逻辑提取 Trading Logic Extraction | design | design_only |
| 154 | D-INTELLIGENCE/人工干预接口 Human Intervention Interface | 人工干预接口 Human Intervention Inter... | design | design_only |
| 155 | D-INTELLIGENCE/人机协作模式 Human-AI Collaboration Mode | 人机协作模式 Human-AI Collaboration Mode | design | design_only |
| 156 | D-INTELLIGENCE/信息价值评分 Information Value Scoring | 信息价值评分 Information Value Scoring | design | design_only |
| 157 | D-INTELLIGENCE/信息论过拟合检测 Information-Theoretic Ove... | 信息论过拟合检测 Information-Theoreti... | design | design_only |
| 158 | D-INTELLIGENCE/元反思 Meta-Reflection | 元反思 Meta-Reflection | design | design_only |
| 159 | D-INTELLIGENCE/共形漂移检测 Conformal Drift Detection | 共形漂移检测 Conformal Drift Detection | design | design_only |
| 160 | D-INTELLIGENCE/决策树学习 Decision Tree Learning | 决策树学习 Decision Tree Learning | design | design_only |
| 161 | D-INTELLIGENCE/决策路径可视化 Decision Path Visualization | 决策路径可视化 Decision Path Visualiz... | design | design_only |
| 162 | D-INTELLIGENCE/创意拓宽模式 Creative Broadening Mode | 创意拓宽模式 Creative Broadening Mode | design | design_only |
| 163 | D-INTELLIGENCE/制度知识 Regime Knowledge | 制度知识 Regime Knowledge | design | design_only |
| 164 | D-INTELLIGENCE/博弈知识 Game Theory Knowledge | 博弈知识 Game Theory Knowledge | design | design_only |
| 165 | D-INTELLIGENCE/去噪 Denoising | 去噪 Denoising | design | design_only |
| 166 | D-INTELLIGENCE/去重 Deduplication | 去重 Deduplication | design | design_only |
| 167 | D-INTELLIGENCE/参数稳定性区域 Parameter Stability Plateau | 参数稳定性区域 Parameter Stability Pl... | design | design_only |
| 168 | D-INTELLIGENCE/可微因果发现 Differentiable Causal Discove... | 可微因果发现 Differentiable Causal Di... | design | design_only |
| 169 | D-INTELLIGENCE/可解释性门控 Explainability Gate | 可解释性门控 Explainability Gate | design | design_only |
| 170 | D-INTELLIGENCE/可解释设计约束 Explainable By Design Const... | 可解释设计约束 Explainable By Design ... | design | design_only |
| 171 | D-INTELLIGENCE/因子知识 Factor Knowledge | 因子知识 Factor Knowledge | design | design_only |
| 172 | D-INTELLIGENCE/因子语义去重 Factor Semantic Deduplication | 因子语义去重 Factor Semantic Deduplic... | design | design_only |
| 173 | D-INTELLIGENCE/因果发现三阶段扩展 Causal Discovery 3-Stag... | 因果发现三阶段扩展 Causal Discovery 3... | design | design_only |
| 174 | D-INTELLIGENCE/因果发现引擎 Causal Discovery Engine | 因果发现引擎 Causal Discovery Engine | design | design_only |
| 175 | D-INTELLIGENCE/因果约束反事实解释 Causal-Constrained Coun... | 因果约束反事实解释 Causal-Constrained... | design | design_only |
| 176 | D-INTELLIGENCE/因果验证层 Causal Validation Layer | 因果验证层 Causal Validation Layer | design | design_only |
| 177 | D-INTELLIGENCE/在线EWC Online Elastic Weight Consolidation | 在线EWC Online Elastic Weight Consoli... | design | design_only |
| 178 | D-INTELLIGENCE/多尺度漂移检测 Multi-Scale Drift Detection | 多尺度漂移检测 Multi-Scale Drift Dete... | design | design_only |
| 179 | D-INTELLIGENCE/多模态融合引擎 Multimodal Fusion Engine | 多模态融合引擎 Multimodal Fusion Engine | design | design_only |
| 180 | D-INTELLIGENCE/学习系统反馈路径 Path | 学习系统反馈路径 Path | design | design_only |
| 181 | D-INTELLIGENCE/宏观因果传导路径 Macro Causal Transmission... | 宏观因果传导路径 Macro Causal Transmi... | design | design_only |
| 182 | D-INTELLIGENCE/定时采集 Scheduled Collection | 定时采集 Scheduled Collection | design | design_only |
| 183 | D-INTELLIGENCE/对抗性知识增强 Adversarial Knowledge Enhan... | 对抗性知识增强 Adversarial Knowledge ... | design | design_only |
| 184 | D-INTELLIGENCE/市场状态感知Walk-Forward Regime-Aware Walk... | 市场状态感知Walk-Forward Regime-Aware... | design | design_only |
| 185 | D-INTELLIGENCE/市场状态知识 Market State Knowledge | 市场状态知识 Market State Knowledge | design | design_only |
| 186 | D-INTELLIGENCE/带干预的时序因果发现 Intervention-Enhanced... | 带干预的时序因果发现 Intervention-Enh... | design | design_only |
| 187 | D-INTELLIGENCE/带推理路径的KG-RAG KG-RAG with Reasoning Path | 带推理路径的KG-RAG KG-RAG with Reason... | design | design_only |
| 188 | D-INTELLIGENCE/延迟离线学习模式 Delayed Offline Learning ... | 延迟离线学习模式 Delayed Offline Lear... | design | design_only |
| 189 | D-INTELLIGENCE/手动提交 Manual Submission | 手动提交 Manual Submission | design | design_only |
| 190 | D-INTELLIGENCE/技能三元组 Skill Triple | 技能三元组 Skill Triple | design | design_only |
| 191 | D-INTELLIGENCE/教训知识 Lesson Learned Knowledge | 教训知识 Lesson Learned Knowledge | design | design_only |
| 192 | D-INTELLIGENCE/数学反思闭环 Mathematical Reflection Loop | 数学反思闭环 Mathematical Reflection ... | design | design_only |
| 193 | D-INTELLIGENCE/方法论知识 Methodology Knowledge | 方法论知识 Methodology Knowledge | design | design_only |
| 194 | D-INTELLIGENCE/时序基础模型骨干 TimesFM Foundation Model ... | 时序基础模型骨干 TimesFM Foundation M... | design | design_only |
| 195 | D-INTELLIGENCE/时滞因果扩展 Lagged Causal Extension | 时滞因果扩展 Lagged Causal Extension | design | design_only |
| 196 | D-INTELLIGENCE/术语标准化 Terminology Normalization | 术语标准化 Terminology Normalization | design | design_only |
| 197 | D-INTELLIGENCE/板块轮动知识 Sector Rotation Knowledge | 板块轮动知识 Sector Rotation Knowledge | design | design_only |
| 198 | D-INTELLIGENCE/格式转换 Format Conversion | 格式转换 Format Conversion | design | design_only |
| 199 | D-INTELLIGENCE/模块工厂 Module Factory | 模块工厂 Module Factory | design | design_only |
| 200 | D-INTELLIGENCE/流动性知识 Liquidity Knowledge | 流动性知识 Liquidity Knowledge | design | design_only |

> (仅显示前 200 个模块，共 218 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 270 条 / 270 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 270 条 / 270 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 240 条 / edges                               │
│   [config_depends]: 10 条 / edges                                │
│   [event]: 9 条 / edges                                          │
│   [contract]: 9 条 / edges                                       │
│   [data]: 2 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (240 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   activate.py → kb_repo.py                                       │
│   __init__.py → default_backtest_engine.py                       │
│   __init__.py → default_inference_engine.py                      │
│   exam_orchestrator.py → capability_passport.py                  │
│   exam_orchestrator.py → exam_test_cases.py                      │
│   cli.py → results_writer.py                                     │
│   cli.py → __init__.py                                           │
│   results_writer.py → profiler.py                                │
│   profiler.py → benchmark_suite.py                               │
│   profiler.py → model_discovery.py                               │
│   model_discovery.py → provider_data.py                          │
│   __init__.py → benchmark_suite.py                               │
│   __init__.py → profiler.py                                      │
│   __init__.py → model_discovery.py                               │
│   __init__.py → task_model_learner.py                            │
│   cli.py → model_discovery.py                                    │
│   cli.py → results_writer.py                                     │
│   cli.py → profiler.py                                           │
│   exam_orchestrator.py → capability_passport.py                  │
│   exam_orchestrator.py → exam_test_cases.py                      │
│   results_writer.py → profiler.py                                │
│   profiler.py → benchmark_suite.py                               │
│   profiler.py → model_discovery.py                               │
│   __init__.py → benchmark_suite.py                               │
│   __init__.py → cli.py                                           │
│   __init__.py → model_discovery.py                               │
│   __init__.py → profiler.py                                      │
│   __init__.py → task_model_learner.py                            │
│   cli.py → profiler.py                                           │
│   cli.py → model_discovery.py                                    │
│   cli.py → results_writer.py                                     │
│   profiler.py → benchmark_suite.py                               │
│   profiler.py → model_discovery.py                               │
│   __init__.py → cli.py                                           │
│   __init__.py → benchmark_suite.py                               │
│   __init__.py → profiler.py                                      │
│   __init__.py → model_discovery.py                               │
│   __init__.py → task_model_learner.py                            │
│   exam_orchestrator.py → capability_passport.py                  │
│   exam_orchestrator.py → exam_test_cases.py                      │
│   model_discovery.py → provider_data.py                          │
│   results_writer.py → profiler.py                                │
│   Cross-Market Transmission... → Reproducibility Manager可...    │
│   AI协作策略与人机信任模型 → LLM语义理解 LLM Semantic ...        │
│   ML模型工厂 → Research Asset Versioning...                      │
│   知识模型自进化 Model Know... → Paper Tracker 论文追踪器        │
│   D-RESEARCH → Feature Store特征存储                             │
│   Feature Store特征存储 → Experiment Tracker实验追踪             │
│   Experiment Tracker实验追踪 → Notebook Integration Note...      │
│   ...还有 191 条 / 191 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (10 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (9 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (9 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (2 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 270 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `29_d_intelligence_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
