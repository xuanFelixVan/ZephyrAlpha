---
module_id: 05_IMPLEMENTATION_05_TECHNICAL_SPECIFICATIONS_MODULE_REGISTRY_7931
layer: layer_05
version: 1.0.0
status: Active
responsibility:
  - Module Registry相关业务
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---

## 1. 概述



### 1.1 注册中心目的



- 统一管理所有模块的定义

- 明确模块职责边界

- 追踪模块依赖关系

- 防止职责重叠和重复定?

### 1.2 注册规范



每个模块注册时需提供?- 模块ID

- 模块名称

- Layer定位

- 核心职责

- 依赖模块

- 接口契约



```
```---
```



## 2. 模块注册?

### 2.1 Layer 0 - 数据源层



| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| QMT_DATA_INTERFACE_001 | QMT数据接口 | QMT数据源接口| Active |

| BAOSTOCK_001 | BaoStock数据?| 历史行情数据获取 | Active |

| IFIND_001 | iFinD数据?| 金融数据接入 | Active |



### 2.2 Layer 1 - 数据预处理层



| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| DATACLEANER_001 | 数据清洗?| 数据清洗、缺失值处?| Active |

| DATAVALIDATOR_001 | 数据验证?| 数据质量验证 | Active |

| DATANORMALIZER_001 | 数据标准化器 | 数据标准化、归一?| Active |

| ASHARE_HISTORICAL_001 | A股历史数据| A股历史数据管?| Active |



### 2.3 Layer 2 - Alpha因子?

| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| FACTOR_CALCULATOR_001 | 因子计算?| 基础因子计算 | Active |

| FACTOR_IC_001 | 因子IC分析 | IC计算、统计、检查| Active |

| FACTOR_BACKTEST_001 | 因子回测 | 因子回测、绩效分?| Active |



### 2.4 Layer 4 - 机器学习?

| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| MODEL_TRAINING_PIPELINE_001 | 模型训练流水?| 通用训练流水?| Active |

| MODEL_SERVING_ARCHITECTURE_001 | 模型服务化架?| 模型部署、服?| Active |

| FEATURE_ENGINEERING_001 | 特征工程 | 特征生成、选择、变?| Active |

| LSTM_MODEL_001 | LSTM模型 | LSTM时间序列预测 | Active |

| TRANSFORMER_MODEL_001 | Transformer模型 | Transformer多因子建?| Active |

| QLIB_ALPHA158_001 | QlibAlpha158 | AI因子计算 | Active |

| MLOPS_PLATFORM_001 | MLOps平台 | ML生命周期管理 | Active |

| MODEL_MONITORING_001 | 模型监控 | 模型性能监控 | Active |

| ONLINE_LEARNING_001 | 在线学习 | 实时模型更新 | Active |



### 2.5 Layer 5 - 策略执行?

| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| MARKET_IMPACT_MODEL_001 | 市场冲击模型 | 交易成本估计 | Active |



### 2.6 Layer 6 - 组合优化?

| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| ALL_WEATHER_OPTIMIZER_001 | 全天候优化器 | 风险平价配置 | Active |

| BARRA_RISK_MODEL_001 | Barra风险模型 | 多因子风险模块| Active |



### 2.7 Layer 8 - 人机交互?

| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| STREAMLIT_DASHBOARD_001 | Streamlit仪表?| 可视化界?| Active |



### 2.8 数据服务?

| 模块ID | 模块名称 | 核心职责 | 状态|

|--------|----------|----------|------|

| FEATURE_STORE_001 | 特征存储 | 特征存储、服?| Active |



```
```---
```



## 3. 模块详情



### 3.1 FACTOR_CALCULATOR_001



```yaml

module_id: FACTOR_CALCULATOR_001_7931

name: 因子计算?layer: Layer 2 - Alpha因子?status: Active

version: 1.0.0



core_responsibilities:

  - 价值因子计?(PE, PB, PS, PCF)

  - 成长因子计算 (营收增长, 利润增长)

  - 动量因子计算 (1? 3? 6月动?

  - 技术指标计?(MA, MACD, RSI)



not_responsible_for:

  - 因子筛?  - 因子合成

  - IC计算



dependencies:

  - DATACLEANER_001 (数据清洗)

  - ASHARE_HISTORICAL_001 (历史数据)



interface_contract: IFactorCalculator v1.0

```



### 3.2 ALPHA_FACTOR_FACTORY_001



```yaml

module_id: IMPL_MODULE_REGISTRY_ALPHA_REF_001_7931

name: Alpha因子工厂

layer: Layer 2-4 - 中观策略?status: Active

version: 1.0.0



core_responsibilities:

  - 因子筛?(IC/IR筛?

  - 因子正交?  - 多因子合?  - Alpha信号生成



not_responsible_for:

  - 基础因子计算 (调用FactorCalculator)

  - AI因子计算 (调用QlibAlpha158)

  - IC计算 (调用FactorIC)



dependencies:

  - FACTOR_CALCULATOR_001 (基础因子)

  - QLIB_ALPHA158_001 (AI因子)

  - FACTOR_IC_001 (IC计算)



interface_contract: IFactorCalculator v1.0 (调用?

```



### 3.3 MODEL_TRAINING_PIPELINE_001



```yaml

module_id: IMPL_MODULE_REGISTRY_REF_001_7931

name: 模型训练流水?layer: Layer 4 - 机器学习?status: Active

version: 1.0.0



core_responsibilities:

  - 数据版本管理 (DVC)

  - 超参数优?(Optuna)

  - 实验跟踪 (MLflow)

  - 模型注册 (MLflow)



not_responsible_for:

  - 模型架构定义

  - 前向传播逻辑

  - 损失函数计算



dependencies:

  - FEATURE_STORE_001 (特征数据)

  - LSTM_MODEL_001 (LSTM训练?

  - TRANSFORMER_MODEL_001 (Transformer训练?



interface_contract: IModelTrainer v1.0 (调用?

```



```
```---
```



## 4. 依赖关系矩阵



| 模块 | 依赖模块 | 依赖类型 |

|------|----------|----------|

| AlphaFactorFactory | FactorCalculator | 调用 |

| AlphaFactorFactory | QlibAlpha158 | 调用 |

| AlphaFactorFactory | FactorIC | 调用 |

| ModelTrainingPipeline | FeatureStore | 数据 |

| ModelTrainingPipeline | LSTMTrainer | 调用 |

| ModelTrainingPipeline | TransformerTrainer | 调用 |

| FeatureStore | FeatureEngineering | 调用 |

| MLOpsPlatform | ModelMonitoring | 集成 |



```
```---
```



## 5. 职责边界检查

### 5.1 检查规范

1. **单一职责**: 每个模块只负责一种核心功?2. **无重复定?*: 相同功能不在多个模块中定?3. **明确依赖**: 依赖关系清晰，无循环依赖



### 5.2 检查结束

| 检查项 | 结果 | 说明 |

|--------|------|------|

| 因子计算职责 | ?通过 | FactorCalculator统一负责 |

| 特征计算职责 | ?通过 | FeatureEngineering统一负责 |

| IC计算职责 | ?通过 | FactorIC统一负责 |

| 模型训练职责 | ?通过 | Pipeline调用Trainer |

| Layer定位 | ?通过 | 已统一修正 |



```
```---
```



## 6. 变更记录



| 日期 | 变更内容 | 影响模块 |

|------|----------|----------|

| 2026-04-03 | 创建模块注册中心 | 全部模块 |

| 2026-04-03 | 修正Layer定位 | MLOPS, MODEL_MONITORING, ONLINE_LEARNING |

| 2026-04-03 | 明确因子计算职责 | ALPHA_FACTOR_FACTORY |



```
```---
```



**文档版本**: v1.0

**创建日期**: 2026-04-03

**维护?*: 首席技术评审官
