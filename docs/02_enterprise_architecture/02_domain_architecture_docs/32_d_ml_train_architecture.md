---
doc_type: domain_architecture_diagram
title: D-ML_TRAIN 训练架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 32_d_ml_train / 训练 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示训练（D-ML_TRAIN）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 训练（D-ML_TRAIN）的模块分布。共 119 个模块 / 119 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   docs__03_modules___cross_layer__model_profiler__blueprint_m... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (12 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ml_train/__init__.py  [prototype]                   │
│   src/zephyr/ml_train/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/ml_train/api/__init__.py  [scaffold_placeholder]    │
│   src/zephyr/ml_train/core/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/ml_train/implementations/__init__.py  [prototype]   │
│   src/zephyr/ml_train/implementations/default_inference_engin... │
│   src/zephyr/ml_train/inference_base.py  [prototype]             │
│   src/zephyr/ml_train/infrastructure/__init__.py  [scaffold_p... │
│   src/zephyr/ml_train/models/__init__.py  [scaffold_placeholder] │
│   src/zephyr/ml_train/services/__init__.py  [scaffold_placeho... │
│   src/zephyr/ml_train/trainer_base.py  [prototype]               │
│   Barra Risk Factor Model  [design]                              │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (106 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   AIFactorMiningEngine AI因子挖掘引擎  [design]                  │
│   AI认知流 AI Cognitive Stream  [design]                         │
│   AST沙箱三层安全 AST Sandbox Three-layer Security  [design]     │
│   ArchitectureOptimizer Agent 架构优化器代理  [design]           │
│   AutoMLEngine 自动机器学习引擎  [design]                        │
│   AutoSkill 自动技能发现  [design]                               │
│   Barra Risk Factor Model Barra多因子风险模型  [design]          │
│   Bayesian Model Averaging BMA 模型  [design]                    │
│   C-029 模型工厂 Model Factory  [design]                         │
│   CART CART决策树  [design]                                      │
│   CCP Cost-Complexity Pruning CCP成本复杂度剪枝  [design]        │
│   CNN/GNN/Transformer系列 CNN/GNN/Transformer Series  [design]   │
│   Causal Reinforcement Learning Causal RL 因果强化学习  [design] │
│   CausalDiscoveryEngine 因果发现引擎  [design]                   │
│   CodeGenerator Agent 代码生成器代理  [design]                   │
│   Concept Drift Adapter 概念漂移适配器  [design]                 │
│   Continual Learning Anti-Forgetting Framework 持续学习抗遗忘... │
│   DSR/CPCV v2 Deflated Sharpe Ratio/CPCV v2 DSR/CPCV v2缩减夏... │
│   ...还有 88 个模块 / 88 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 119 个模块 / 119 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | docs__03_modules___cross_layer__model... | design | design_only |

### L2 领域层 / Domain Layer (12 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ml_train/__init__.py | src/zephyr/ml_train/__init__.py | prototype | draft |
| 2 | src/zephyr/ml_train/_extensions/__init__.py | src/zephyr/ml_train/_extensions/__ini... | scaffold_placeholder | orphan |
| 3 | src/zephyr/ml_train/api/__init__.py | src/zephyr/ml_train/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/ml_train/core/__init__.py | src/zephyr/ml_train/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/ml_train/implementations/__init__.py | src/zephyr/ml_train/implementations/_... | prototype | draft |
| 6 | src/zephyr/ml_train/implementations/default_inference_eng... | src/zephyr/ml_train/implementations/d... | prototype | draft |
| 7 | src/zephyr/ml_train/inference_base.py | src/zephyr/ml_train/inference_base.py | prototype | draft |
| 8 | src/zephyr/ml_train/infrastructure/__init__.py | src/zephyr/ml_train/infrastructure/__... | scaffold_placeholder | orphan |
| 9 | src/zephyr/ml_train/models/__init__.py | src/zephyr/ml_train/models/__init__.py | scaffold_placeholder | orphan |
| 10 | src/zephyr/ml_train/services/__init__.py | src/zephyr/ml_train/services/__init__.py | scaffold_placeholder | orphan |
| 11 | src/zephyr/ml_train/trainer_base.py | src/zephyr/ml_train/trainer_base.py | prototype | draft |
| 12 | 训练域/D-ML-106 | Barra Risk Factor Model | design | design_only |

### 未分类 / Unclassified (106 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-ML-TRAIN/AIFactorMiningEngine AI因子挖掘引擎 | AIFactorMiningEngine AI因子挖掘引擎 | design | design_only |
| 2 | D-ML-TRAIN/AI认知流 AI Cognitive Stream | AI认知流 AI Cognitive Stream | design | design_only |
| 3 | D-ML-TRAIN/AST沙箱三层安全 AST Sandbox Three-layer Security | AST沙箱三层安全 AST Sandbox Three-lay... | design | design_only |
| 4 | D-ML-TRAIN/ArchitectureOptimizer Agent 架构优化器代理 | ArchitectureOptimizer Agent 架构优化... | design | design_only |
| 5 | D-ML-TRAIN/AutoMLEngine 自动机器学习引擎 | AutoMLEngine 自动机器学习引擎 | design | design_only |
| 6 | D-ML-TRAIN/AutoSkill 自动技能发现 | AutoSkill 自动技能发现 | design | design_only |
| 7 | D-ML-TRAIN/Barra Risk Factor Model Barra多因子风险模型 | Barra Risk Factor Model Barra多因子风... | design | design_only |
| 8 | D-ML-TRAIN/Bayesian Model Averaging BMA 模型 | Bayesian Model Averaging BMA 模型 | design | design_only |
| 9 | D-ML-TRAIN/C-029 模型工厂 Model Factory | C-029 模型工厂 Model Factory | design | design_only |
| 10 | D-ML-TRAIN/CART CART决策树 | CART CART决策树 | design | design_only |
| 11 | D-ML-TRAIN/CCP Cost-Complexity Pruning CCP成本复杂度剪枝 | CCP Cost-Complexity Pruning CCP成本复... | design | design_only |
| 12 | D-ML-TRAIN/CNN/GNN/Transformer系列 CNN/GNN/Transformer Se... | CNN/GNN/Transformer系列 CNN/GNN/Trans... | design | design_only |
| 13 | D-ML-TRAIN/Causal Reinforcement Learning Causal RL 因果强... | Causal Reinforcement Learning Causal ... | design | design_only |
| 14 | D-ML-TRAIN/CausalDiscoveryEngine 因果发现引擎 | CausalDiscoveryEngine 因果发现引擎 | design | design_only |
| 15 | D-ML-TRAIN/CodeGenerator Agent 代码生成器代理 | CodeGenerator Agent 代码生成器代理 | design | design_only |
| 16 | D-ML-TRAIN/Concept Drift Adapter 概念漂移适配器 | Concept Drift Adapter 概念漂移适配器 | design | design_only |
| 17 | D-ML-TRAIN/Continual Learning Anti-Forgetting Framework ... | Continual Learning Anti-Forgetting Fr... | design | design_only |
| 18 | D-ML-TRAIN/DSR/CPCV v2 Deflated Sharpe Ratio/CPCV v2 DSR/... | DSR/CPCV v2 Deflated Sharpe Ratio/CPC... | design | design_only |
| 19 | D-ML-TRAIN/Decision Tree Learning 决策树学习 | Decision Tree Learning 决策树学习 | design | design_only |
| 20 | D-ML-TRAIN/Diffusion Model Scene Generation 扩散模型场景生成 | Diffusion Model Scene Generation 扩散... | design | design_only |
| 21 | D-ML-TRAIN/DriftAdapter 漂移适配器 | DriftAdapter 漂移适配器 | design | design_only |
| 22 | D-ML-TRAIN/Dynamic Conditional Correlation 动态条件相关性 | Dynamic Conditional Correlation 动态... | design | design_only |
| 23 | D-ML-TRAIN/ExperimentPipeline 实验管线 | ExperimentPipeline 实验管线 | design | design_only |
| 24 | D-ML-TRAIN/ExperimentTracker 实验追踪器 | ExperimentTracker 实验追踪器 | design | design_only |
| 25 | D-ML-TRAIN/FactorMAD 辩论式因子精炼 | FactorMAD 辩论式因子精炼 | design | design_only |
| 26 | D-ML-TRAIN/FeatureDiscovery 特征发现 | FeatureDiscovery 特征发现 | design | design_only |
| 27 | D-ML-TRAIN/FeatureEngineeringAutomation 特征工程自动化 | FeatureEngineeringAutomation 特征工程... | design | design_only |
| 28 | D-ML-TRAIN/Federated Model Trainer 联邦模型训练器 | Federated Model Trainer 联邦模型训练器 | design | design_only |
| 29 | D-ML-TRAIN/FinRLDeepRL FinRL深度强化学习 | FinRLDeepRL FinRL深度强化学习 | design | design_only |
| 30 | D-ML-TRAIN/GATE-FCFT 金融宪法微调汇总 | GATE-FCFT 金融宪法微调汇总 | design | design_only |
| 31 | D-ML-TRAIN/GATE-FCFT-01 自托管LLM | GATE-FCFT-01 自托管LLM | design | design_only |
| 32 | D-ML-TRAIN/GATE-FCFT-02 GPU算力 | GATE-FCFT-02 GPU算力 | design | design_only |
| 33 | D-ML-TRAIN/GATE-FCFT-03 金融安全数据集 | GATE-FCFT-03 金融安全数据集 | design | design_only |
| 34 | D-ML-TRAIN/GATE-FCFT-04 FinJailbreak基准 | GATE-FCFT-04 FinJailbreak基准 | design | design_only |
| 35 | D-ML-TRAIN/GPU MPS Multi-Process Concurrency GPU MPS多进... | GPU MPS Multi-Process Concurrency GPU... | design | design_only |
| 36 | D-ML-TRAIN/GPU Resource Feed GPU资源供给 | GPU Resource Feed GPU资源供给 | design | design_only |
| 37 | D-ML-TRAIN/GPU资源争抢 GPU Resource Contention | GPU资源争抢 GPU Resource Contention | design | design_only |
| 38 | D-ML-TRAIN/Gradient Boosting Gradient Boosting梯度提升 | Gradient Boosting Gradient Boosting梯... | design | design_only |
| 39 | D-ML-TRAIN/HMM 聚类算法 | HMM 聚类算法 | design | design_only |
| 40 | D-ML-TRAIN/HyperparameterOptimizer 超参数优化器 | HyperparameterOptimizer 超参数优化器 | design | design_only |
| 41 | D-ML-TRAIN/ICL元学习 In-context Learning | ICL元学习 In-context Learning | design | design_only |
| 42 | D-ML-TRAIN/Isotonic Regression 等渗回归 | Isotonic Regression 等渗回归 | design | design_only |
| 43 | D-ML-TRAIN/KAN Kolmogorov-Arnold Network KAN Kolmogorov-A... | KAN Kolmogorov-Arnold Network KAN Kol... | design | design_only |
| 44 | D-ML-TRAIN/Kinlay RL for Optimal Execution Kinlay RL最优执行 | Kinlay RL for Optimal Execution Kinla... | design | design_only |
| 45 | D-ML-TRAIN/LOBSTER LOBSTER数据集 | LOBSTER LOBSTER数据集 | design | design_only |
| 46 | D-ML-TRAIN/MC Dropout MC Dropout蒙特卡洛丢弃 | MC Dropout MC Dropout蒙特卡洛丢弃 | design | design_only |
| 47 | D-ML-TRAIN/ML Training ML训练 | ML Training ML训练 | design | design_only |
| 48 | D-ML-TRAIN/ML Training Process ML训练进程 | ML Training Process ML训练进程 | design | design_only |
| 49 | D-ML-TRAIN/ML训练 模型训练 | ML训练 模型训练 | design | design_only |
| 50 | D-ML-TRAIN/Machine Learning 机器学习域 | Machine Learning 机器学习域 | design | design_only |
| 51 | D-ML-TRAIN/Man Group AlphaGPT | Man Group AlphaGPT | design | design_only |
| 52 | D-ML-TRAIN/Meta-Harness 元优化器 | Meta-Harness 元优化器 | design | design_only |
| 53 | D-ML-TRAIN/MethodologyLearner Agent 方法论学习器代理 | MethodologyLearner Agent 方法论学习器... | design | design_only |
| 54 | D-ML-TRAIN/Model Deployment Saga 模型上线Saga | Model Deployment Saga 模型上线Saga | design | design_only |
| 55 | D-ML-TRAIN/Model Quantization Inference Acceleration 模型... | Model Quantization Inference Accelera... | design | design_only |
| 56 | D-ML-TRAIN/ModelLineageTracker 模型血缘追踪器 | ModelLineageTracker 模型血缘追踪器 | design | design_only |
| 57 | D-ML-TRAIN/ModelServingRequest 模型服务请求 | ModelServingRequest 模型服务请求 | design | design_only |
| 58 | D-ML-TRAIN/ModelServingResponse 模型服务响应 | ModelServingResponse 模型服务响应 | design | design_only |
| 59 | D-ML-TRAIN/ModelValidated Interface 模型验证接口 | ModelValidated Interface 模型验证接口 | design | design_only |
| 60 | D-ML-TRAIN/ModelValidated 模型验证完成 | ModelValidated 模型验证完成 | design | design_only |
| 61 | D-ML-TRAIN/ModelVersion 模型版本 | ModelVersion 模型版本 | design | design_only |
| 62 | D-ML-TRAIN/NewFactorDiscovered 新因子发现 | NewFactorDiscovered 新因子发现 | design | design_only |
| 63 | D-ML-TRAIN/PPO PPO策略梯度方法 | PPO PPO策略梯度方法 | design | design_only |
| 64 | D-ML-TRAIN/Platt Scaling Platt缩放 | Platt Scaling Platt缩放 | design | design_only |
| 65 | D-ML-TRAIN/PromptOptimizer Agent 提示词优化器代理 | PromptOptimizer Agent 提示词优化器代理 | design | design_only |
| 66 | D-ML-TRAIN/Prompt自优化循环 STOP模式 | Prompt自优化循环 STOP模式 | design | design_only |
| 67 | D-ML-TRAIN/QlibAIFactorMining QlibAI因子挖掘 | QlibAIFactorMining QlibAI因子挖掘 | design | design_only |
| 68 | D-ML-TRAIN/Quant Beckman 2025 | Quant Beckman 2025 | design | design_only |
| 69 | D-ML-TRAIN/RSI架构4维度 RSI Architecture 4 Dimensions | RSI架构4维度 RSI Architecture 4 Dimen... | design | design_only |
| 70 | D-ML-TRAIN/Random Forest Random Forest随机森林 | Random Forest Random Forest随机森林 | design | design_only |
| 71 | D-ML-TRAIN/Reinforcement Learning Optimization 强化学习优化 | Reinforcement Learning Optimization ... | design | design_only |
| 72 | D-ML-TRAIN/RetrainTriggered 重训触发 | RetrainTriggered 重训触发 | design | design_only |
| 73 | D-ML-TRAIN/Run ai GPU Hot Swap Run:ai式GPU热交换 | Run ai GPU Hot Swap Run:ai式GPU热交换 | design | design_only |
| 74 | D-ML-TRAIN/SAC SAC策略梯度方法 | SAC SAC策略梯度方法 | design | design_only |
| 75 | D-ML-TRAIN/Spearman相关系数 | Spearman相关系数 | design | design_only |
| 76 | D-ML-TRAIN/SyntheticDataGenerator 合成数据生成器 | SyntheticDataGenerator 合成数据生成器 | design | design_only |
| 77 | D-ML-TRAIN/TSFM Time Series Foundation Model TSFM时序基础... | TSFM Time Series Foundation Model TSF... | design | design_only |
| 78 | D-ML-TRAIN/TWAP TWAP基准 | TWAP TWAP基准 | design | design_only |
| 79 | D-ML-TRAIN/Training Dataset Manager 训练数据集管理 | Training Dataset Manager 训练数据集管理 | design | design_only |
| 80 | D-ML-TRAIN/TrainingDataManager 训练数据管理器 | TrainingDataManager 训练数据管理器 | design | design_only |
| 81 | D-ML-TRAIN/TrainingPipeline 训练管线 | TrainingPipeline 训练管线 | design | design_only |
| 82 | D-ML-TRAIN/World Model Market Simulation 世界模型市场推演 | World Model Market Simulation 世界模... | design | design_only |
| 83 | D-ML-TRAIN/bootstrap统计显著性检验 | bootstrap统计显著性检验 | design | design_only |
| 84 | D-ML-TRAIN/ml_pipeline ML管线进程 | ml_pipeline ML管线进程 | design | design_only |
| 85 | D-ML-TRAIN/wandb/实验追踪系列 wandb/Experiment Tracking S... | wandb/实验追踪系列 wandb/Experiment T... | design | design_only |
| 86 | D-ML-TRAIN/xLSTM Extended Long Short-Term Memory xLSTM扩... | xLSTM Extended Long Short-Term Memory... | design | design_only |
| 87 | D-ML-TRAIN/代码自纠正循环 RISE模式 | 代码自纠正循环 RISE模式 | design | design_only |
| 88 | D-ML-TRAIN/信号预测力评估 Signal Predictive Power Evaluation | 信号预测力评估 Signal Predictive Powe... | design | design_only |
| 89 | D-ML-TRAIN/决策树与强化学习交易决策架构 Decision Tree & R... | 决策树与强化学习交易决策架构 Decision... | design | design_only |
| 90 | D-ML-TRAIN/分析师Agent反馈循环 Analyst Agent Feedback Loop | 分析师Agent反馈循环 Analyst Agent Fee... | design | design_only |
| 91 | D-ML-TRAIN/动态信号权重模型 Dynamic Signal Weighting Model | 动态信号权重模型 Dynamic Signal Weigh... | design | design_only |
| 92 | D-ML-TRAIN/动态权重分配 Dynamic Weight Allocation | 动态权重分配 Dynamic Weight Allocation | design | design_only |
| 93 | D-ML-TRAIN/可解释性保障 Explainability Guarantee | 可解释性保障 Explainability Guarantee | design | design_only |
| 94 | D-ML-TRAIN/因子DSL约束 Factor DSL Constraint | 因子DSL约束 Factor DSL Constraint | design | design_only |
| 95 | D-ML-TRAIN/学习系统7阶段流水线 Learning System 7-stage Pi... | 学习系统7阶段流水线 Learning System 7... | design | design_only |
| 96 | D-ML-TRAIN/强化学习优化 Reinforcement Learning Optimization | 强化学习优化 Reinforcement Learning O... | design | design_only |
| 97 | D-ML-TRAIN/技能三元组匹配 Skill Triple Matching | 技能三元组匹配 Skill Triple Matching | design | design_only |
| 98 | D-ML-TRAIN/技能依赖解析 Skill Dependency Resolution | 技能依赖解析 Skill Dependency Resolution | design | design_only |
| 99 | D-ML-TRAIN/技能库 Skill Library | 技能库 Skill Library | design | design_only |
| 100 | D-ML-TRAIN/技能库积累 Voyager模式 | 技能库积累 Voyager模式 | design | design_only |
| 101 | D-ML-TRAIN/技能结构化三元组格式 Skill Structured Triple F... | 技能结构化三元组格式 Skill Structured... | design | design_only |
| 102 | D-ML-TRAIN/模型一致性 Model Uniformity | 模型一致性 Model Uniformity | design | design_only |
| 103 | D-ML-TRAIN/矛盾信号处理 Contradictory Signal Processing | 矛盾信号处理 Contradictory Signal Pro... | design | design_only |
| 104 | D-ML-TRAIN/策略退化检测 Strategy Degradation Detection | 策略退化检测 Strategy Degradation Det... | design | design_only |
| 105 | D-ML-TRAIN/经验记忆结构化索引 Experience Memory Structure... | 经验记忆结构化索引 Experience Memory ... | design | design_only |
| 106 | D-ML-TRAIN/进化式代码生成 Evolutionary Code Generation | 进化式代码生成 Evolutionary Code Gene... | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 109 条 / 109 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 109 条 / 109 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 96 条 / edges                                │
│   [config_depends]: 6 条 / edges                                 │
│   [contract]: 4 条 / edges                                       │
│   [event]: 3 条 / edges                                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (96 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   inference_base.py → trainer_base.py                            │
│   default_inference_engine.py → trainer_base.py                  │
│   default_inference_engine.py → inference_base.py                │
│   __init__.py → default_inference_engine.py                      │
│   Training Dataset Manager ... → ModelLineageTracker 模型...     │
│   ModelLineageTracker 模型... → C-029 模型工厂 Model Factory     │
│   C-029 模型工厂 Model Factory → TrainingPipeline 训练管线       │
│   TrainingPipeline 训练管线 → ExperimentTracker 实验追踪器       │
│   ExperimentTracker 实验追踪器 → AutoMLEngine 自动机器学习...    │
│   AutoMLEngine 自动机器学习... → FeatureDiscovery 特征发现       │
│   FeatureDiscovery 特征发现 → DriftAdapter 漂移适配器            │
│   DriftAdapter 漂移适配器 → SyntheticDataGenerator 合...         │
│   DriftAdapter 漂移适配器 → SAC SAC策略梯度方法                  │
│   SyntheticDataGenerator 合... → KAN Kolmogorov-Arnold Net...    │
│   KAN Kolmogorov-Arnold Net... → xLSTM Extended Long Short...    │
│   xLSTM Extended Long Short... → Continual Learning Anti-F...    │
│   Continual Learning Anti-F... → Causal Reinforcement Lear...    │
│   Causal Reinforcement Lear... → Concept Drift Adapter 概...     │
│   Concept Drift Adapter 概... → Barra Risk Factor Model B...     │
│   Barra Risk Factor Model B... → ExperimentPipeline 实验管线     │
│   ExperimentPipeline 实验管线 → HyperparameterOptimizer ...      │
│   HyperparameterOptimizer ... → TrainingDataManager 训练...      │
│   TrainingDataManager 训练... → CausalDiscoveryEngine 因...      │
│   TrainingDataManager 训练... → CART CART决策树                  │
│   CausalDiscoveryEngine 因... → QlibAIFactorMining QlibAI...     │
│   QlibAIFactorMining QlibAI... → FinRLDeepRL FinRL深度强化...    │
│   FinRLDeepRL FinRL深度强化... → AIFactorMiningEngine AI因...    │
│   AIFactorMiningEngine AI因... → FeatureEngineeringAutomat...    │
│   FeatureEngineeringAutomat... → 因子DSL约束 Factor DSL Co...    │
│   因子DSL约束 Factor DSL Co... → 进化式代码生成 Evolutiona...    │
│   进化式代码生成 Evolutiona... → 分析师Agent反馈循环 Analy...    │
│   分析师Agent反馈循环 Analy... → 技能库 Skill Library            │
│   分析师Agent反馈循环 Analy... → Machine Learning 机器学习域     │
│   技能库 Skill Library → 强化学习优化 Reinforcemen...            │
│   强化学习优化 Reinforcemen... → 技能依赖解析 Skill Depend...    │
│   强化学习优化 Reinforcemen... → PPO PPO策略梯度方法             │
│   技能依赖解析 Skill Depend... → 策略退化检测 Strategy Deg...    │
│   策略退化检测 Strategy Deg... → Decision Tree Learning 决...    │
│   策略退化检测 Strategy Deg... → LOBSTER LOBSTER数据集           │
│   策略退化检测 Strategy Deg... → CCP Cost-Complexity Pruni...    │
│   Decision Tree Learning 决... → Reinforcement Learning Op...    │
│   Reinforcement Learning Op... → 动态信号权重模型 Dynamic ...    │
│   Kinlay RL for Optimal Exe... → CodeGenerator Agent 代码...     │
│   TWAP TWAP基准 → ICL元学习 In-context Lear...                   │
│   Random Forest Random Fore... → 技能库积累 Voyager模式          │
│   Gradient Boosting Gradien... → Man Group AlphaGPT              │
│   动态信号权重模型 Dynamic ... → 信号预测力评估 Signal Pre...    │
│   信号预测力评估 Signal Pre... → 动态权重分配 Dynamic Weig...    │
│   动态权重分配 Dynamic Weig... → 矛盾信号处理 Contradictor...    │
│   ...还有 47 条 / 47 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (6 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (4 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (3 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 109 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `32_d_ml_train_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
