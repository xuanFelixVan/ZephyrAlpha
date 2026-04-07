---
module_id: INDEX_AI_WORKFLOW_001
title: AI工作流与舆情分析综合层索引
version: 1.4.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-07
owner: 首席文档架构师
standard_type: 专业量化机构索引
applicable_scope: AI工作流与舆情分析综合管理
compliance_level: 专业标准
parent_document: ../INDEX.md
responsibility:
  - 索引文档、导航目录
  - 舆情分析管理
layer: Layer 7 (AI报告层) + Layer 3 (舆情分析层)
---
---


## 文档职责说明

**本文档职责**: AI工作流与舆情分析综合层索引
- AI工作流模块导航和文档索引
- 舆情分析模块导航和文档索引
- 综合层职责边界说明

# AI工作流与舆情分析综合层索引

> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：AI工作流与舆情分析综合层的导航和索引
> - ✅ 本文档负责：Layer 7 (AI报告层) 相关模块索引
> - ✅ 本文档负责：Layer 3 (舆情分析层) 相关模块索引
> - ❌ 本文档不负责：其他模块内容

> **版本**: v1.2  
> **创建日期**: 2026-04-02  
> **核心定位**: AI工作流与舆情分析综合层 - 融合Layer 7 AI报告层与Layer 3舆情分析层  
> **技术栈**: MLflow + SQLite + Python + Streamlit + LangChain + SHAP

---

## 📋 目录职责定义

### 综合层定义

**10_AI_WORKFLOW目录** = **AI工作流与舆情分析综合层**

本目录融合了两个核心Layer的功能模块：

| Layer | 中文名称 | 核心职责 | 文档数量 |
|-------|---------|---------|---------|
| **Layer 7** | AI报告层 | AI工作记录、报告生成、复盘分析、决策解释、知识管理 | 15个 |
| **Layer 3** | 舆情分析层 | 舆情因子、情感分析、实时预警、数据源扩展 | 10个 |

### 职责边界说明

```
┌─────────────────────────────────────────────────────────────┐
│           10_AI_WORKFLOW: AI工作流与舆情分析综合层            │
├─────────────────────────────────────────────────────────────┤
│  Layer 7 (AI报告层)                                         │
│  ├── AI工作记录与优化 (AI_WORKFLOW_LOGGER)                   │
│  ├── AI工作汇报与交付 (AI_WORK_REPORTER)                     │
│  ├── 复盘模块 (POST_TRADE_REVIEW)                           │
│  ├── 自动化报告生成 (AUTO_REPORT_GENERATION)                 │
│  ├── 多智能体协作 (MULTI_AGENT_COLLABORATION)               │
│  ├── AI决策解释 (AI_DECISION_EXPLANATION)                   │
│  ├── 智能问答系统 (INTELLIGENT_QA_SYSTEM)                   │
│  ├── 知识管理 (KNOWLEDGE_MANAGEMENT)                        │
│  ├── 绩效归因 (PERFORMANCE_ATTRIBUTION)                     │
│  ├── 情景分析与压力测试 (SCENARIO_ANALYSIS_STRESS_TEST)     │
│  ├── 实时风险监控 (REAL_TIME_RISK_MONITOR)                  │
│  ├── 实盘监控 (LIVE_TRADING_MONITOR)                        │
│  ├── 性能分析 (PERFORMANCE_ANALYSIS)                        │
│  ├── 验证与测试框架 (VALIDATION_TESTING_FRAMEWORK)          │
│  └── 运维知识管理 (OPERATIONS_KNOWLEDGE_MANAGEMENT)         │
├─────────────────────────────────────────────────────────────┤
│  Layer 3 (舆情分析层)                                        │
│  ├── 舆情因子库 (SENTIMENT_FACTOR_LIBRARY)                   │
│  ├── 深度学习情感分析 (DEEP_LEARNING_SENTIMENT_ANALYZER)    │
│  ├── 实时监控仪表盘 (REAL_TIME_MONITORING_DASHBOARD)        │
│  ├── 实时预警系统 (REAL_TIME_ALERT_SYSTEM)                  │
│  ├── 舆情分析中期改进 (SENTIMENT_ANALYSIS_MEDIUM_TERM)      │
│  └── 舆情分析长期改进 (SENTIMENT_ANALYSIS_LONG_TERM)        │
├─────────────────────────────────────────────────────────────┤
│  跨Layer模块                                                 │
│  ├── 数据源扩展 (DATA_SOURCE_EXTENSION) → Layer 0           │
│  ├── 数据质量与血缘 (DATA_QUALITY_LINEAGE) → Layer 1        │
│  ├── 模型性能与版本管理 (MODEL_PERFORMANCE_VERSION) → Layer 4│
│  └── 合规监控 (COMPLIANCE_MONITORING) → Layer 10            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 快速导览
### 二级索引

| 索引名称 | 适用范围 | 路径 | 说明 |
|---------|---------|------|------|
| **舆情分析层改进蓝图文档索引** | 舆情分析层改进 | [SENTIMENT_ANALYSIS_IMPROVEMENT_PROGRESS_TRACKER.md](./SENTIMENT_ANALYSIS_IMPROVEMENT_PROGRESS_TRACKER.md) | 舆情分析层短期、中期、长期改进文档总索引 |

---

## 一、模块概述
### 1.1 模块定位

**AI工作流与舆情分析综合层**是清风量化系统的**核心基础设施**,旨在实现:

**Layer 7 (AI报告层) 核心功能**:
- ✅ **AI工作记录**: 记录AI每次工作的完整过程
- ✅ **AI工作汇报**: 向用户汇报AI工作成果
- ✅ **交易复盘**: 分析交易决策,提取经验教训
- ✅ **数据持久化**: 保存全流程数据
- ✅ **开源集成**: 集成成熟开源项目

**Layer 3 (舆情分析层) 核心功能**:
- ✅ **舆情因子库**: 舆情因子定义、计算、评估、优化
- ✅ **深度学习情感分析**: 多维度情感评估、金融领域专业模型
- ✅ **实时监控仪表盘**: 舆情热力图、情感趋势图、预警时间线
- ✅ **实时预警系统**: 实时预警、多渠道推送、规则引擎
- ✅ **数据源扩展**: Twitter/Reddit/FRED/SEC EDGAR数据采集

### 1.2 核心价值
**对个人开发者的价值**:
1. **AI工作可追溯**: 每次AI工作都有完整记录
2. **AI效果可评估**: 知道AI工作是否有效
3. **AI方式可优化**: 持续改进AI工作方式
4. **AI知识可复用**: 避免重复造轮子
5. **舆情信息可利用**: 利用舆情数据增强决策

**对系统的价值**:
1. **数据基础**: 为复盘模块提供数据支持
2. **优化基础**: 为AI工作汇报提供数据支持
3. **知识基础**: 为知识管理提供数据支持
4. **审计基础**: 为系统审计提供数据支持
5. **舆情基础**: 为策略决策提供舆情支持

### 1.3 Layer定位

```
10_AI_WORKFLOW: AI工作流与舆情分析综合层
    ├── Layer 7 (AI报告层)
    │   ├── AI工作记录与优化
    │   ├── AI工作汇报与交付
    │   ├── 复盘模块
    │   ├── 自动化报告生成
    │   ├── 多智能体协作
    │   ├── AI决策解释
    │   ├── 智能问答系统
    │   ├── 知识管理
    │   ├── 绩效归因
    │   ├── 情景分析与压力测试
    │   ├── 实时风险监控
    │   ├── 实盘监控
    │   ├── 性能分析
    │   ├── 验证与测试框架
    │   └── 运维知识管理
    ├── Layer 3 (舆情分析层)
    │   ├── 舆情因子库
    │   ├── 深度学习情感分析
    │   ├── 实时监控仪表盘
    │   ├── 实时预警系统
    │   ├── 舆情分析中期改进
    │   └── 舆情分析长期改进
    └── 跨Layer模块
        ├── 数据源扩展 (Layer 0)
        ├── 数据质量与血缘 (Layer 1)
        ├── 模型性能与版本管理 (Layer 4)
        └── 合规监控 (Layer 10)
```

---

## 二、模块架构
### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────────                   AI工作流模块架构                         ├─────────────────────────────────────────────────────────────                                                             ┌─────────────────────────────────────────────────────       Layer 8: 人机交互(Human-AI Interaction)          ├─ AI工作汇报与交付模(AI_WORK_REPORTER)              ├─ 每日工作总结                                      ├─ 实时进度通知                                      ├─ 决策汇报                                          └─ 可视化展                                     └─────────────────────────────────────────────────────                                                             ┌─────────────────────────────────────────────────────       Layer 7: AI报告(AI Reporting Layer)              ├─ 复盘模块 (POST_TRADE_REVIEW)                         ├─ 回测复盘                                          ├─ 实盘复盘                                          ├─ 因子复盘                                          └─ 风险复盘                                        └─────────────────────────────────────────────────────                                                             ┌─────────────────────────────────────────────────────       Layer 8.5: AI工作记录(AI Workflow Logging)       ├─ AI工作记录与优化模(AI_WORKFLOW_LOGGER)            ├─ 会话记录                                          ├─ 决策记录                                          ├─ 效果评估                                          └─ 知识库构                                     └─────────────────────────────────────────────────────                                                             ┌─────────────────────────────────────────────────────       Layer 0: 数据(Data Layer)                        ├─ 全流程数据保存机(FULL_PROCESS_DATA_PERSISTENCE)    ├─ 实验追踪                                          ├─ 数据血                                         ├─ 版本控制                                          └─ 数据治理                                        └─────────────────────────────────────────────────────                                                             ┌─────────────────────────────────────────────────────       开源项目集成层 (Open Source Integration)            ├─ 开源项目集成方(OPEN_SOURCE_INTEGRATION)           ├─ MLflow集成                                        ├─ Qlib集成                                          └─ 其他工具集成                                    └─────────────────────────────────────────────────────                                                              └─────────────────────────────────────────────────────────────```

### 2.2 数据流设
```
用户输入 AI理解 AI工作记录 AI执行 效果评估 AI优化 知识沉淀
                                                               └────────────────── 知识复用 ←───────────────────────────```

---

## 三、模块清
### 3.1 核心模块

| 模块ID | 模块名称 | 版本 | 状| 蓝图文档 | 核心职责 |
|--------|---------|------|------|----------|----------|
| **AI_WORKFLOW_LOGGER_001** | AI工作记录与优化模| 1.0 | Active | [AI_WORKFLOW_LOGGER_BLUEPRINT.md](./AI_WORKFLOW_LOGGER_BLUEPRINT.md) | AI会话记录、决策记录、效果评估、优化迭代、知识库构建 |
| **AI_WORK_REPORTER_001** | AI工作汇报与交付模| 1.0 | Active | [AI_WORK_REPORTER_BLUEPRINT.md](./AI_WORK_REPORTER_BLUEPRINT.md) | 每日工作总结、进度通知、决策汇报、交互交付、可视化展示 |
| **POST_TRADE_REVIEW_001** | 复盘模块 | 1.0 | Active | [POST_TRADE_REVIEW_BLUEPRINT.md](./POST_TRADE_REVIEW_BLUEPRINT.md) | 回测复盘、实盘复盘、因子复盘、策略复盘、风险复|
| **FULL_PROCESS_DATA_PERSISTENCE_001** | 全流程数据保存机| 1.0 | Active | [FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md](./FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md) | 实验追踪、数据血缘、版本控制、数据治|

| **COMPLIANCE_MONITORING_001** | 合规监控模块 | 1.0 | Active | [COMPLIANCE_MONITORING_BLUEPRINT.md](./COMPLIANCE_MONITORING_BLUEPRINT.md) | 交易合规检查、风控合规检查、监管报告生成、审计追踪、违规预|
| **LIVE_TRADING_MONITOR_001** | 实盘监控模块 | 1.0 | Active | [LIVE_TRADING_MONITOR_BLUEPRINT.md](./LIVE_TRADING_MONITOR_BLUEPRINT.md) | 实时交易监控、持仓风险监控、异常交易预警、性能指标监控、多渠道告警 |
| **PERFORMANCE_ANALYSIS_001** | 性能分析模块 | 1.0 | Active | [PERFORMANCE_ANALYSIS_BLUEPRINT.md](./PERFORMANCE_ANALYSIS_BLUEPRINT.md) | 性能指标采集、性能瓶颈识别、性能报告生成、优化建议生成、性能趋势分析 |
| **MULTI_AGENT_COLLABORATION_001** | 多智能体协作系统 | 1.0 | Active | [MULTI_AGENT_COLLABORATION_BLUEPRINT.md](./MULTI_AGENT_COLLABORATION_BLUEPRINT.md) | 多智能体角色定义、协作机制、任务分配、知识共享、决策融合 |
| **AUTO_REPORT_GENERATION_001** | 自动化报告生成引擎 | 1.0 | Active | [AUTO_REPORT_GENERATION_BLUEPRINT.md](./AUTO_REPORT_GENERATION_BLUEPRINT.md) | 自动化报告生成、多维度数据融合、AI决策仪表盘、多渠道推送、定时调度 |
| **REAL_TIME_RISK_MONITOR_001** | 实时风险监控系统 | 1.0 | Active | [REAL_TIME_RISK_MONITOR_BLUEPRINT.md](./REAL_TIME_RISK_MONITOR_BLUEPRINT.md) | 实时风险监控、多维度风险评估、动态预警机制、风险报告生成、风险限额管理 |
| **KNOWLEDGE_MANAGEMENT_001** | 知识管理与传承系统 | 1.0 | Active | [KNOWLEDGE_MANAGEMENT_BLUEPRINT.md](./KNOWLEDGE_MANAGEMENT_BLUEPRINT.md) | 知识库构建、知识检索、知识图谱、经验传承、学习路径规划 |
| **SCENARIO_ANALYSIS_STRESS_TEST_001** | 情景分析与压力测试系统 | 1.0 | Active | [SCENARIO_ANALYSIS_STRESS_TEST_BLUEPRINT.md](./SCENARIO_ANALYSIS_STRESS_TEST_BLUEPRINT.md) | 历史情景分析、假设情景模拟、压力测试引擎、情景报告生成、情景库管理 |
| **AI_DECISION_EXPLANATION_001** | AI决策解释系统 | 1.0 | Active | [AI_DECISION_EXPLANATION_BLUEPRINT.md](./AI_DECISION_EXPLANATION_BLUEPRINT.md) | SHAP解释引擎、LIME解释引擎、特征重要性分析、决策路径可视化、解释报告生成 |
| **INTELLIGENT_QA_SYSTEM_001** | 智能问答系统 | 1.0 | Active | [INTELLIGENT_QA_SYSTEM_BLUEPRINT.md](./INTELLIGENT_QA_SYSTEM_BLUEPRINT.md) | 自然语言理解、知识检索引擎、RAG生成引擎、上下文管理、智能推荐引擎 |
| **PERFORMANCE_ATTRIBUTION_001** | 绩效归因分析系统 | 1.0 | Active | [PERFORMANCE_ATTRIBUTION_BLUEPRINT.md](./PERFORMANCE_ATTRIBUTION_BLUEPRINT.md) | Brinson归因模型、因子归因模型、风险归因模型、归因报告生成、归因可视化 |

### 3.2 P0核心缺失模块 (🆕 新增)

| 模块ID | 模块名称 | 版本 | 状态 | 蓝图文档 | 核心职责 |
|--------|---------|------|------|----------|----------|
| **STRATEGY_LIFECYCLE_MANAGEMENT_001** | 策略生命周期管理 | 1.0 | Active | [STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT.md](./STRATEGY_LIFECYCLE_MANAGEMENT_BLUEPRINT.md) | 策略研发→测试→上线→监控→下线全流程管理 |
| **MODEL_MONITORING_DRIFT_DETECTION_001** | 模型监控与漂移检测 | 1.0 | Active | [MODEL_MONITORING_DRIFT_DETECTION_BLUEPRINT.md](./MODEL_MONITORING_DRIFT_DETECTION_BLUEPRINT.md) | 模型性能监控、数据漂移检测、概念漂移检测 |
| **TRANSACTION_COST_ANALYSIS_001** | 交易成本分析(TCA) | 1.0 | Active | [TRANSACTION_COST_ANALYSIS_BLUEPRINT.md](./TRANSACTION_COST_ANALYSIS_BLUEPRINT.md) | 交易成本分解、滑点分析、冲击成本估算 |
| **SIGNAL_DECAY_ANALYSIS_001** | 信号衰减分析 | 1.0 | Active | [SIGNAL_DECAY_ANALYSIS_BLUEPRINT.md](./SIGNAL_DECAY_ANALYSIS_BLUEPRINT.md) | 信号有效期分析、衰减曲线拟合、最优持有期计算 |
| **INTELLIGENT_SCHEDULING_SYSTEM_001** | 智能调度系统 | 1.0 | Active | [INTELLIGENT_SCHEDULING_SYSTEM_BLUEPRINT.md](./INTELLIGENT_SCHEDULING_SYSTEM_BLUEPRINT.md) | 任务调度、资源分配、优先级管理、依赖关系管理 |

### 3.3 P1重要缺失模块 (🆕 新增)

| 模块ID | 模块名称 | 版本 | 状态 | 蓝图文档 | 核心职责 |
|--------|---------|------|------|----------|----------|
| **CONFIGURATION_MANAGEMENT_CENTER_001** | 配置管理中心 | 1.0 | Active | [CONFIGURATION_MANAGEMENT_CENTER_BLUEPRINT.md](./CONFIGURATION_MANAGEMENT_CENTER_BLUEPRINT.md) | 配置集中管理、环境隔离、配置验证、配置版本控制 |
| **DATA_QUALITY_MONITORING_001** | 数据质量监控 | 1.0 | Active | [DATA_QUALITY_MONITORING_BLUEPRINT.md](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | 数据质量检查、数据验证、质量报告、异常告警 |
| **BACKTEST_RESULTS_MANAGEMENT_001** | 回测结果管理 | 1.0 | Active | [BACKTEST_RESULTS_MANAGEMENT_BLUEPRINT.md](./BACKTEST_RESULTS_MANAGEMENT_BLUEPRINT.md) | 回测结果存储、结果对比、性能分析、报告生成 |
| **STRATEGY_VERSION_CONTROL_001** | 策略版本控制 | 1.0 | Active | [STRATEGY_VERSION_CONTROL_BLUEPRINT.md](./STRATEGY_VERSION_CONTROL_BLUEPRINT.md) | 策略版本管理、变更追踪、版本回滚、协作管理 |
| **MARKET_REGIME_DETECTION_001** | 市场状态识别 | 1.0 | Active | [MARKET_REGIME_DETECTION_BLUEPRINT.md](./MARKET_REGIME_DETECTION_BLUEPRINT.md) | 市场状态识别、牛熊判断、震荡识别、状态转换预警 |
| **INTELLIGENT_ANOMALY_DETECTION_001** | 智能异常检测 | 1.0 | Active | [INTELLIGENT_ANOMALY_DETECTION_BLUEPRINT.md](./INTELLIGENT_ANOMALY_DETECTION_BLUEPRINT.md) | 异常检测、离群点识别、异常模式学习、实时告警 |
| **TRADE_EXECUTION_ANALYSIS_001** | 交易执行分析 | 1.0 | Active | [TRADE_EXECUTION_ANALYSIS_BLUEPRINT.md](./TRADE_EXECUTION_ANALYSIS_BLUEPRINT.md) | 执行质量评估、滑点分析、成交率统计、执行优化建议 |
| **PORTFOLIO_DIAGNOSTICS_001** | 投资组合诊断 | 1.0 | Active | [PORTFOLIO_DIAGNOSTICS_BLUEPRINT.md](./PORTFOLIO_DIAGNOSTICS_BLUEPRINT.md) | 组合健康检查、风险诊断、收益归因、优化建议 |

### 3.4 P2增强缺失模块 (🆕 新增)

| 模块ID | 模块名称 | 版本 | 状态 | 蓝图文档 | 核心职责 |
|--------|---------|------|------|----------|----------|
| **RESEARCH_WORKFLOW_MANAGEMENT_001** | 研究工作流管理 | 1.0 | Active | [RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT.md](./RESEARCH_WORKFLOW_MANAGEMENT_BLUEPRINT.md) | 研究项目管理、实验版本控制、研究成果归档、协作流程管理 |
| **FACTOR_EFFECTIVENESS_MONITORING_001** | 因子有效性监控 | 1.0 | Active | [FACTOR_EFFECTIVENESS_MONITORING_BLUEPRINT.md](./FACTOR_EFFECTIVENESS_MONITORING_BLUEPRINT.md) | 因子IC监控、因子收益预测能力、因子衰减分析、因子有效性报告 |
| **INTELLIGENT_PARAMETER_OPTIMIZATION_001** | 智能参数优化 | 1.0 | Active | [INTELLIGENT_PARAMETER_OPTIMIZATION_BLUEPRINT.md](./INTELLIGENT_PARAMETER_OPTIMIZATION_BLUEPRINT.md) | 参数空间定义、优化算法选择、优化过程跟踪、最优参数推荐 |
| **MARKET_MICROSTRUCTURE_ANALYSIS_001** | 市场微观结构分析 | 1.0 | Active | [MARKET_MICROSTRUCTURE_ANALYSIS_BLUEPRINT.md](./MARKET_MICROSTRUCTURE_ANALYSIS_BLUEPRINT.md) | 市场流动性分析、交易成本估算、市场冲击分析、微观结构指标计算 |
| **RISK_BUDGET_MANAGEMENT_001** | 风险预算管理 | 1.0 | Active | [RISK_BUDGET_MANAGEMENT_BLUEPRINT.md](./RISK_BUDGET_MANAGEMENT_BLUEPRINT.md) | 风险预算分配、风险贡献计算、组合风险监控、风险调整优化 |
| **INTELLIGENT_REPORT_DISTRIBUTION_001** | 智能报告分发 | 1.0 | Active | [INTELLIGENT_REPORT_DISTRIBUTION_BLUEPRINT.md](./INTELLIGENT_REPORT_DISTRIBUTION_BLUEPRINT.md) | 报告生成调度、多渠道分发、权限管理、分发记录跟踪 |
| **HISTORICAL_REPLAY_SYSTEM_001** | 历史回放系统 | 1.0 | Active | [HISTORICAL_REPLAY_SYSTEM_BLUEPRINT.md](./HISTORICAL_REPLAY_SYSTEM_BLUEPRINT.md) | 历史数据回放、策略回测验证、场景重现分析、性能对比评估 |

### 3.5 架构完整性分析文档 (🆕 新增)

| 文档类型 | 文档名称 | 版本 | 状态 | 文档路径 | 核心职责 |
|---------|---------|------|------|----------|----------|
| **架构分析** | Layer 7完整性分析与缺失模块补充方案 | 1.0 | Active | [LAYER_7_GAP_ANALYSIS_AND_SUPPLEMENT_BLUEPRINT.md](./LAYER_7_GAP_ANALYSIS_AND_SUPPLEMENT_BLUEPRINT.md) | 缺失模块识别、开源替代方案、蓝图补充设计 |

### 3.4 舆情分析模块

| 模块ID | 模块名称 | 版本 | 状| 蓝图文档 | 核心职责 |
|--------|---------|------|------|----------|----------|
| **AIWF_DSE_001** | 数据源扩展模块 | 1.0 | Active | [DATA_SOURCE_EXTENSION_BLUEPRINT.md](./DATA_SOURCE_EXTENSION_BLUEPRINT.md) | Twitter/Reddit/FRED/SEC EDGAR数据采集、数据源管理 |
| **AIWF_SFL_001** | 舆情因子库模块 | 1.0 | Active | [SENTIMENT_FACTOR_LIBRARY_BLUEPRINT.md](./SENTIMENT_FACTOR_LIBRARY_BLUEPRINT.md) | 因子定义、因子计算、因子评估、因子优化 |
| **AIWF_RMD_001** | 实时监控仪表盘模块 | 1.0 | Active | [REAL_TIME_MONITORING_DASHBOARD_BLUEPRINT.md](./REAL_TIME_MONITORING_DASHBOARD_BLUEPRINT.md) | 舆情热力图、情感趋势图、预警时间线 |
| **AIWF_DLSA_001** | 深度学习情感分析模块 | 1.0 | Active | [DEEP_LEARNING_SENTIMENT_ANALYZER_BLUEPRINT.md](./DEEP_LEARNING_SENTIMENT_ANALYZER_BLUEPRINT.md) | 深度学习情感分析、多维度情感评估、金融领域专业模|
| **AIWF_RTAS_001** | 实时预警系统模块 | 1.0 | Active | [REAL_TIME_ALERT_SYSTEM_BLUEPRINT.md](./REAL_TIME_ALERT_SYSTEM_BLUEPRINT.md) | 实时预警、多渠道推送、规则引擎、预警历史管|
| **AIWF_VTF_001** | 验证与测试框架模| 1.0 | Active | [VALIDATION_TESTING_FRAMEWORK_BLUEPRINT.md](./VALIDATION_TESTING_FRAMEWORK_BLUEPRINT.md) | A/B测试框架、回测验证模块、模型验证、策略验|
| **AIWF_DQLM_001** | 数据质量与血缘管理模| 1.0 | Active | [DATA_QUALITY_LINEAGE_MANAGEMENT_BLUEPRINT.md](./DATA_QUALITY_LINEAGE_MANAGEMENT_BLUEPRINT.md) | 数据质量评分、数据血缘追踪、异常检测、质量报|
| **AIWF_OKM_001** | 运维知识管理模块 | 1.0 | Active | [OPERATIONS_KNOWLEDGE_MANAGEMENT_BLUEPRINT.md](./OPERATIONS_KNOWLEDGE_MANAGEMENT_BLUEPRINT.md) | 知识库构建、运维经验沉淀、故障诊断、知识检|
| **AIWF_MPVM_001** | 模型性能与版本管理模| 1.0 | Active | [MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT.md](./MODEL_PERFORMANCE_VERSION_MANAGEMENT_BLUEPRINT.md) | 模型版本控制、性能监控、模型回滚、性能对比 |

### 3.3 舆情分析改进蓝图

| 文档类型 | 文档名称 | 版本 | 状| 文档路径 | 核心职责 |
|---------|---------|------|------|----------|----------|
| **改进蓝图** | 舆情分析层长期改进蓝图 | 1.0 | Active | [SENTIMENT_ANALYSIS_LONG_TERM_IMPROVEMENT_BLUEPRINT.md](./SENTIMENT_ANALYSIS_LONG_TERM_IMPROVEMENT_BLUEPRINT.md) | 多模态分析、AI虚拟研究团队（第7-12个月） |
| **改进蓝图** | 舆情分析层中期改进蓝| 1.0 | Active | [SENTIMENT_ANALYSIS_MEDIUM_TERM_IMPROVEMENT_BLUEPRINT.md](./SENTIMENT_ANALYSIS_MEDIUM_TERM_IMPROVEMENT_BLUEPRINT.md) | 知识图谱、流式处理、多语言支持（第4-6个月|

### 3.4 技术规格文
| 文档类型 | 文档名称 | 版本 | 状| 文档路径 | 核心职责 |
|---------|---------|------|------|----------|----------|
| **技术规* | 短期改进技术规格书 | 1.1 | Active | [SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md](./SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md) | 数据源扩展、深度学习情感分析、实时预警系统技术规|
| **技术规* | 中期改进技术规格书 | 1.0 | Active | [SENTIMENT_ANALYSIS_MEDIUM_TERM_TECHNICAL_SPECIFICATION.md](./SENTIMENT_ANALYSIS_MEDIUM_TERM_TECHNICAL_SPECIFICATION.md) | 知识图谱、流式处理、多语言支持技术规|
| **技术规* | 长期改进技术规格书 | 1.0 | Active | [SENTIMENT_ANALYSIS_LONG_TERM_TECHNICAL_SPECIFICATION.md](./SENTIMENT_ANALYSIS_LONG_TERM_TECHNICAL_SPECIFICATION.md) | 多模态分析、AI虚拟研究团队技术规|

### 3.5 项目管理文档

| 文档类型 | 文档名称 | 版本 | 状| 文档路径 | 核心职责 |
|---------|---------|------|------|----------|----------|
| **项目管理** | 项目管理文档 | 1.1 | Active | [SENTIMENT_ANALYSIS_PROJECT_MANAGEMENT.md](./SENTIMENT_ANALYSIS_PROJECT_MANAGEMENT.md) | WBS分解、甘特图、里程碑计划、资源分|
| **风险管理** | 风险管理文档 | 1.1 | Active | [SENTIMENT_ANALYSIS_RISK_MANAGEMENT.md](./SENTIMENT_ANALYSIS_RISK_MANAGEMENT.md) | 风险识别、风险评估、风险缓解措|
| **测试计划** | 测试计划文档 | 1.0 | Active | [SENTIMENT_ANALYSIS_TEST_PLAN.md](./SENTIMENT_ANALYSIS_TEST_PLAN.md) | 测试策略、单元测试、集成测试、性能测试 |
| **实施细节** | 实施细节文档 | 1.0 | Active | [SENTIMENT_ANALYSIS_IMPLEMENTATION_DETAILS.md](./SENTIMENT_ANALYSIS_IMPLEMENTATION_DETAILS.md) | 环境搭建、代码示例、配置模板、部署架|
| **进度追踪** | 改进蓝图进度追踪器 | 1.2 | Active | [SENTIMENT_ANALYSIS_IMPROVEMENT_PROGRESS_TRACKER.md](./SENTIMENT_ANALYSIS_IMPROVEMENT_PROGRESS_TRACKER.md) | 文档完成度统计、优先级分类、蓝图欠缺分析 |

### 3.6 其他文档

| 文档类型 | 文档名称 | 版本 | 状| 文档路径 | 核心职责 |
|---------|---------|------|------|----------|----------|
| **解决方案** | 开源模块解决方| 1.0 | Active | [OPEN_SOURCE_MODULE_SOLUTION.md](./OPEN_SOURCE_MODULE_SOLUTION.md) | 开源模块选型、集成方案、替代方|
**📌 开源文档使用指南**:
- **选型决策**: 阅读[开源模块解决方案](./OPEN_SOURCE_MODULE_SOLUTION.md) - 了解全景图、对比分析、推荐理由

### 3.7 模块依赖关系

```
┌─────────────────────────────────────────────────────────                   模块依赖关系                       ├─────────────────────────────────────────────────────────                                                         AI_WORK_REPORTER_001 (AI工作汇报)                                                                             AI_WORKFLOW_LOGGER_001 (AI工作记录)                                                                           FULL_PROCESS_DATA_PERSISTENCE_001 (数据持久                                                                OPEN_SOURCE_INTEGRATION_001 (开源集                                                                          POST_TRADE_REVIEW_001 (复盘模块)                                                                              AI_WORKFLOW_LOGGER_001 (AI工作记录)                                                                           FULL_PROCESS_DATA_PERSISTENCE_001 (数据持久                                                                 └─────────────────────────────────────────────────────────```

---

## 四、实施路径
### 4.1 Phase 1: 数据持久化基础设施 (Week 1)

**目标**: 部署MLflow并实现数据持久化

**任务清单**:
- [ ] 部署MLflow Tracking Server
- [ ] 实现ExperimentTracker组件
- [ ] 实现DataLineageTracker组件
- [ ] 实现VersionController组件
- [ ] 编写使用文档

**验收标准**:
- MLflow服务器正常运- 能够追踪实验
- 能够追踪数据血- 能够管理数据版本

### 4.2 Phase 2: AI工作记录与优化(Week 2)

**目标**: 实现AI工作记录和优化功
**任务清单**:
- [ ] 实现SessionRecorder组件
- [ ] 实现DecisionRecorder组件
- [ ] 实现EffectivenessEvaluator组件
- [ ] 实现WorkflowOptimizer组件
- [ ] 实现KnowledgeBaseBuilder组件

**验收标准**:
- 能够记录AI会话
- 能够记录AI决策
- 能够评估AI效果
- 能够优化AI工作方式

### 4.3 Phase 3: AI工作汇报与复(Week 3)

**目标**: 实现AI工作汇报和复盘功
**任务清单**:
- [ ] 实现DailyReporter组件
- [ ] 实现ProgressNotifier组件
- [ ] 实现DecisionReporter组件
- [ ] 实现BacktestReviewer组件
- [ ] 实现LiveTradingReviewer组件

**验收标准**:
- 能够生成每日工作总结
- 能够推送实时进度通知
- 能够汇报重要决策
- 能够分析回测结果

---

## 五、技术栈

### 5.1 核心技
| 技术组| 选择方案 | 版本 | 用|
|---------|---------|------|------|
| **追踪引擎** | MLflow | 2.x | 实验追踪与模型管|
| **数据* | SQLite | 3.x | 轻量级数据存|
| **数据格式** | Parquet + JSON | - | 高效数据存储 |
| **可视* | Plotly + Streamlit | - | 交互式可视化 |
| **编程语言** | Python | 3.10+ | 核心开发语言 |

### 5.2 开源项
| 项目名称 | 类型 | 集成优先| 用|
|---------|------|-----------|------|
| **MLflow** | 实验追踪 | P0 | 实验追踪与模型管|
| **Qlib** | 量化框架 | P1 | 量化投资框架 |
| **Optuna** | 参数优化 | P1 | 超参数优|
| **Plotly** | 可视| P1 | 交互式图|
| **Streamlit** | 仪表| P2 | 数据仪表|

---

## 六、文档治理
### 6.1 文档索引

| 文档类型 | 文档名称 | 路径 | 状|
|---------|---------|------|------|
| **总索引 | AI工作流模块总索引| `docs/10_AI_WORKFLOW/INDEX.md` | Active |
| **蓝图文档** | AI工作记录与优化模块蓝| `docs/10_AI_WORKFLOW/AI_WORKFLOW_LOGGER_BLUEPRINT.md` | Active |
| **蓝图文档** | AI工作汇报与交付模块蓝| `docs/10_AI_WORKFLOW/AI_WORK_REPORTER_BLUEPRINT.md` | Active |
| **蓝图文档** | 复盘模块蓝图 | `docs/10_AI_WORKFLOW/POST_TRADE_REVIEW_BLUEPRINT.md` | Active |
| **蓝图文档** | 全流程数据保存机制蓝| `docs/10_AI_WORKFLOW/FULL_PROCESS_DATA_PERSISTENCE_BLUEPRINT.md` | Active |

### 6.2 策略专用AI模块索引

> 以下模块位于 Layer 5-6，是策略层的专用AI模块

| 文档类型 | 文档名称 | 路径 | 状|
|---------|---------|------|------|
| **蓝图文档** | 策略生命周期管理AI蓝图 | `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/STRATEGY_LIFECYCLE_AI_BLUEPRINT.md` | Active |
| **蓝图文档** | 组合优化AI蓝图 | `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/PORTFOLIO_OPTIMIZATION_AI_BLUEPRINT.md` | Active |
| **蓝图文档** | 风险控制AI蓝图 | `docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/RISK_CONTROL_AI_BLUEPRINT.md` | Active |

### 6.3 版本管理

- **v1.0**: 初始版本,实现核心功能
- **v1.1**: 增强效果评估算法
- **v1.2**: 增加知识图谱可视- **v2.0**: 集成更多开源项
---

## 七、质量保障
### 7.1 质量指标

| 指标 | 目标| 当前| 状|
|------|--------|--------|------|
| **文档合规* | 0% | - | 待评|
| **代码覆盖* | 0% | - | 待评|
| **性能指标** | <100ms | - | 待评|
| **可用* | 9% | - | 待评|

### 7.2 质量检查清
- [ ] 所有蓝图文档符合标准模- [ ] 所有模块职责边界清- [ ] 所有接口定义完- [ ] 所有数据流图准- [ ] 所有实施路径可
---

## 八、相关文档
| 文档 | 说明 |
|------|------|
| [系统架构文档](../01_FRAMEWORK/ARCHITECTURE.md) | Layer 0-11统一架构定义 |
| [模块职责边界文档](../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md) | 模块职责边界定义 |
| | 系统总索|
| [技术栈文档](../01_FRAMEWORK/TECH_STACK.md) | 技术栈选择 |

---

**版本**: v1.0 | **更新**: 2026-04-02 | **状*: 活跃
