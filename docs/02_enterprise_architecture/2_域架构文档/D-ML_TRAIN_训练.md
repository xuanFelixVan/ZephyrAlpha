---
doc_type: domain_architecture_doc
title: D-ML_TRAIN 训练架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-ML_TRAIN 训练架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-ML_TRAIN |
| 域名称 | 训练 |
| 架构层 | L2_domain |
| 模块总数 | 118 |
| 设计态模块 | 107 |
| 原型态模块 | 5 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 机器学习训练域。负责ML模型训练管线，包括数据预处理、特征选择、超参优化、模型训练、交叉验证。 |

## 模块清单

共 118 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-ML-TRAIN/AIFactorMiningEngine AI因子挖掘引擎 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/AI认知流 AI Cognitive Stream |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/AST沙箱三层安全 AST Sandbox Three-layer Security |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ArchitectureOptimizer Agent 架构优化器代理 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/AutoMLEngine 自动机器学习引擎 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/AutoSkill 自动技能发现 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Barra Risk Factor Model Barra多因子风险模型 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Bayesian Model Averaging BMA 模型 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/C-029 模型工厂 Model Factory |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/CART CART决策树 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/CCP Cost-Complexity Pruning CCP成本复杂度剪枝 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/CNN/GNN/Transformer系列 CNN/GNN/Transformer Series |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Causal Reinforcement Learning Causal RL 因果强化学习 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/CausalDiscoveryEngine 因果发现引擎 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/CodeGenerator Agent 代码生成器代理 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Concept Drift Adapter 概念漂移适配器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Continual Learning Anti-Forgetting Framework 持续学习抗遗忘框架 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/DSR/CPCV v2 Deflated Sharpe Ratio/CPCV v2 DSR/CPCV v2缩减夏普比率/CPCV v2 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Decision Tree Learning 决策树学习 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Diffusion Model Scene Generation 扩散模型场景生成 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/DriftAdapter 漂移适配器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Dynamic Conditional Correlation 动态条件相关性 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ExperimentPipeline 实验管线 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ExperimentTracker 实验追踪器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/FactorMAD 辩论式因子精炼 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/FeatureDiscovery 特征发现 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/FeatureEngineeringAutomation 特征工程自动化 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Federated Model Trainer 联邦模型训练器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/FinRLDeepRL FinRL深度强化学习 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GATE-FCFT 金融宪法微调汇总 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GATE-FCFT-01 自托管LLM |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GATE-FCFT-02 GPU算力 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GATE-FCFT-03 金融安全数据集 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GATE-FCFT-04 FinJailbreak基准 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GPU MPS Multi-Process Concurrency GPU MPS多进程并发 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GPU Resource Feed GPU资源供给 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/GPU资源争抢 GPU Resource Contention |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Gradient Boosting Gradient Boosting梯度提升 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/HMM 聚类算法 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/HyperparameterOptimizer 超参数优化器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ICL元学习 In-context Learning |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Isotonic Regression 等渗回归 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/KAN Kolmogorov-Arnold Network KAN Kolmogorov-Arnold网络 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Kinlay RL for Optimal Execution Kinlay RL最优执行 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/LOBSTER LOBSTER数据集 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/MC Dropout MC Dropout蒙特卡洛丢弃 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ML Training ML训练 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ML Training Process ML训练进程 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ML训练 模型训练 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Machine Learning 机器学习域 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Man Group AlphaGPT |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Meta-Harness 元优化器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/MethodologyLearner Agent 方法论学习器代理 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Model Deployment Saga 模型上线Saga |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Model Quantization Inference Acceleration 模型量化与推理加速 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ModelLineageTracker 模型血缘追踪器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ModelServingRequest 模型服务请求 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ModelServingResponse 模型服务响应 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ModelValidated Interface 模型验证接口 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ModelValidated 模型验证完成 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ModelVersion 模型版本 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/NewFactorDiscovered 新因子发现 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/PPO PPO策略梯度方法 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Platt Scaling Platt缩放 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/PromptOptimizer Agent 提示词优化器代理 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Prompt自优化循环 STOP模式 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/QlibAIFactorMining QlibAI因子挖掘 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Quant Beckman 2025 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/RSI架构4维度 RSI Architecture 4 Dimensions |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Random Forest Random Forest随机森林 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Reinforcement Learning Optimization 强化学习优化 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/RetrainTriggered 重训触发 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Run ai GPU Hot Swap Run:ai式GPU热交换 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/SAC SAC策略梯度方法 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Spearman相关系数 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/SyntheticDataGenerator 合成数据生成器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/TSFM Time Series Foundation Model TSFM时序基础模型 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/TWAP TWAP基准 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/Training Dataset Manager 训练数据集管理 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/TrainingDataManager 训练数据管理器 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/TrainingPipeline 训练管线 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/World Model Market Simulation 世界模型市场推演 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/bootstrap统计显著性检验 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/ml_pipeline ML管线进程 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/wandb/实验追踪系列 wandb/Experiment Tracking Series |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/xLSTM Extended Long Short-Term Memory xLSTM扩展长短期记忆网络 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/代码自纠正循环 RISE模式 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/信号预测力评估 Signal Predictive Power Evaluation |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/决策树与强化学习交易决策架构 Decision Tree & RL Trading Decision Architecture |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/分析师Agent反馈循环 Analyst Agent Feedback Loop |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/动态信号权重模型 Dynamic Signal Weighting Model |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/动态权重分配 Dynamic Weight Allocation |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/可解释性保障 Explainability Guarantee |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/因子DSL约束 Factor DSL Constraint |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/学习系统7阶段流水线 Learning System 7-stage Pipeline |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/强化学习优化 Reinforcement Learning Optimization |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/技能三元组匹配 Skill Triple Matching |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/技能依赖解析 Skill Dependency Resolution |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/技能库 Skill Library |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/技能库积累 Voyager模式 |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/技能结构化三元组格式 Skill Structured Triple Format |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/模型一致性 Model Uniformity |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/矛盾信号处理 Contradictory Signal Processing |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/策略退化检测 Strategy Degradation Detection |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/经验记忆结构化索引 Experience Memory Structured Index |  | design_only | design | 0 | 0 |
| D-ML-TRAIN/进化式代码生成 Evolutionary Code Generation |  | design_only | design | 0 | 0 |
| src/zephyr/ml_train/__init__.py | MOD-L11-001 | draft | prototype | 0 | 1 |
| src/zephyr/ml_train/_extensions/__init__.py | MOD-ML_TRAIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_train/api/__init__.py | MOD-ML_TRAIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_train/core/__init__.py | MOD-ML_TRAIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_train/implementations/__init__.py | MOD-L11-001 | draft | prototype | 0 | 1 |
| src/zephyr/ml_train/implementations/default_inference_engine.py | MOD-L11-001 | draft | prototype | 1 | 4 |
| src/zephyr/ml_train/inference_base.py | MOD-L11-001 | draft | prototype | 4 | 3 |
| src/zephyr/ml_train/infrastructure/__init__.py | MOD-ML_TRAIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_train/models/__init__.py | MOD-ML_TRAIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_train/services/__init__.py | MOD-ML_TRAIN | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_train/trainer_base.py | MOD-L11-001 | draft | prototype | 6 | 0 |
| 训练域/D-ML-106 | MOD-ML_TRAIN | design_only | design | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-FACTOR | 15 | event,data,contract,config_depends,domain_dependency |
| D-INFRA_RUNTIME | 11 | contract,event,data,config_depends |
| D-TRADING | 6 | contract,import_depends,event |
| D-DATA_ENG | 5 | contract,event,config_depends,domain_dependency |
| D-POSITION | 3 | contract,config_depends,data |
| D-MKT_DATA | 3 | contract,event |
| D-EX_SOR | 3 | contract,event |
| D-SHARED | 2 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-RISK | 23 | data,contract,config_depends,event |
| D-COMPLIANCE | 18 | event,config_depends,data,contract |
| D-AUTONOMY_CORE | 15 | data,event,contract,config_depends |
| D-SECURITY | 13 | contract,event,data |
| D-INTELLIGENCE | 13 | import_depends,contract,config_depends,data,event |
| D-SIGNAL | 11 | event,data,contract |
| D-INTEGRATION | 10 | contract,event,config_depends,data |
| D-INFRA_OPS | 8 | data,config_depends,contract,event |
| D-GOVERNANCE | 8 | event,contract,data,config_depends |
| D-OPS | 5 | contract,config_depends |
| D-KNOWLEDGE | 5 | contract,data |
| D-REPORTING | 4 | data,config_depends,contract |
| D-ML_SERVE | 4 | contract,data,event,domain_dependency |
| D-FRONTEND | 4 | event,contract |
| D-SELL_DECISION | 3 | event,config_depends,data |
| D-AUTONOMY_PERM | 3 | event,data,config_depends |
| D-SIMULATION | 2 | event,data |
| D-SHARED | 2 | import_depends |
| D-PF_CORE | 2 | data |
| D-PF_ALLOC | 2 | event,data |
| D-CROSS_ASSET | 2 | data,event |
| D-DATA_SEC | 1 | config_depends |
| D-DATA_GOV | 1 | contract |
| D-ALT_DATA | 1 | data |

## 域内依赖图

详见 [d_ml_train_dependency.mmd](d_ml_train_dependency.mmd)
