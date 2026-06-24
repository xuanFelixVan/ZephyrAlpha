---
doc_type: domain_architecture_diagram
title: D-ML_SERVE 推理架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 31_d_ml_serve / 推理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示推理（D-ML_SERVE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 推理（D-ML_SERVE）的模块分布。共 69 个模块 / 69 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (9 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   §30.4.2 D-ML-SERVE 推理域（46个模块，P0=5）  [design]          │
│   src/zephyr/ml_serve/__init__.py  [prototype]                   │
│   src/zephyr/ml_serve/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/ml_serve/api/__init__.py  [scaffold_placeholder]    │
│   src/zephyr/ml_serve/core/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/ml_serve/infrastructure/__init__.py  [scaffold_p... │
│   src/zephyr/ml_serve/models/__init__.py  [scaffold_placeholder] │
│   src/zephyr/ml_serve/services/__init__.py  [scaffold_placeho... │
│   推理熔断器  [design]                                           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (60 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   A/B测试启动接口 AB Test Start  [design]                        │
│   A/B测试指标报告接口 AB Test Metrics Report  [design]           │
│   A/B测试结论接口 AB Test Result  [design]                       │
│   AI Construction Governor AI构建治理器  [design]                │
│   AI Decision Explanation AI决策解释(旧)  [design]               │
│   AI Model A/B Tester AI模型A/B测试器(旧)  [design]              │
│   Adversarial 对抗  [design]                                     │
│   Cold→Hot禁止直接通信不变量  [design]                           │
│   D-ML-02  [design]                                              │
│   D-ML-03  [design]                                              │
│   DriftMonitor 漂移监控器  [design]                              │
│   E-RS-03 模型预测事件  [design]                                 │
│   Explanation 解释器  [design]                                   │
│   Fairness 公平性  [design]                                      │
│   GPU推理熔断器  [design]                                        │
│   Hybrid Deployment AI Manager 混合部署AI管理器(旧)  [design]    │
│   Impact 影响分析  [design]                                      │
│   Inference Circuit Breaker 推理熔断器  [design]                 │
│   ...还有 42 个模块 / 42 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 69 个模块 / 69 modules）。

### L2 领域层 / Domain Layer (9 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 |  | §30.4.2 D-ML-SERVE 推理域（46个模块... | design | path_invalid |
| 2 | src/zephyr/ml_serve/__init__.py | src/zephyr/ml_serve/__init__.py | prototype | orphan |
| 3 | src/zephyr/ml_serve/_extensions/__init__.py | src/zephyr/ml_serve/_extensions/__ini... | scaffold_placeholder | orphan |
| 4 | src/zephyr/ml_serve/api/__init__.py | src/zephyr/ml_serve/api/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/ml_serve/core/__init__.py | src/zephyr/ml_serve/core/__init__.py | scaffold_placeholder | orphan |
| 6 | src/zephyr/ml_serve/infrastructure/__init__.py | src/zephyr/ml_serve/infrastructure/__... | scaffold_placeholder | orphan |
| 7 | src/zephyr/ml_serve/models/__init__.py | src/zephyr/ml_serve/models/__init__.py | scaffold_placeholder | orphan |
| 8 | src/zephyr/ml_serve/services/__init__.py | src/zephyr/ml_serve/services/__init__.py | scaffold_placeholder | orphan |
| 9 | 推理域/D-ML-136 | 推理熔断器 | design | design_only |

### 未分类 / Unclassified (60 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-ML-SERVE/A/B测试启动接口 AB Test Start | A/B测试启动接口 AB Test Start | design | design_only |
| 2 | D-ML-SERVE/A/B测试指标报告接口 AB Test Metrics Report | A/B测试指标报告接口 AB Test Metrics R... | design | design_only |
| 3 | D-ML-SERVE/A/B测试结论接口 AB Test Result | A/B测试结论接口 AB Test Result | design | design_only |
| 4 | D-ML-SERVE/AI Construction Governor AI构建治理器 | AI Construction Governor AI构建治理器 | design | design_only |
| 5 | D-ML-SERVE/AI Decision Explanation AI决策解释(旧) | AI Decision Explanation AI决策解释(旧) | design | design_only |
| 6 | D-ML-SERVE/AI Model A/B Tester AI模型A/B测试器(旧) | AI Model A/B Tester AI模型A/B测试器(旧) | design | design_only |
| 7 | D-ML-SERVE/Adversarial 对抗 | Adversarial 对抗 | design | design_only |
| 8 | D-ML-SERVE/Cold→Hot禁止直接通信不变量 | Cold→Hot禁止直接通信不变量 | design | design_only |
| 9 | D-ML-SERVE/D-ML-02 | D-ML-02 | design | design_only |
| 10 | D-ML-SERVE/D-ML-03 | D-ML-03 | design | design_only |
| 11 | D-ML-SERVE/DriftMonitor 漂移监控器 | DriftMonitor 漂移监控器 | design | design_only |
| 12 | D-ML-SERVE/E-RS-03 模型预测事件 | E-RS-03 模型预测事件 | design | design_only |
| 13 | D-ML-SERVE/Explanation 解释器 | Explanation 解释器 | design | design_only |
| 14 | D-ML-SERVE/Fairness 公平性 | Fairness 公平性 | design | design_only |
| 15 | D-ML-SERVE/GPU推理熔断器 | GPU推理熔断器 | design | design_only |
| 16 | D-ML-SERVE/Hybrid Deployment AI Manager 混合部署AI管理器(旧) | Hybrid Deployment AI Manager 混合部署... | design | design_only |
| 17 | D-ML-SERVE/Impact 影响分析 | Impact 影响分析 | design | design_only |
| 18 | D-ML-SERVE/Inference Circuit Breaker 推理熔断器 | Inference Circuit Breaker 推理熔断器 | design | design_only |
| 19 | D-ML-SERVE/InferenceDegraded 推理降级事件 | InferenceDegraded 推理降级事件 | design | design_only |
| 20 | D-ML-SERVE/KB Embedding BGE-M3-ONNX KB嵌入BGE-M3-ONNX | KB Embedding BGE-M3-ONNX KB嵌入BGE-M3... | design | design_only |
| 21 | D-ML-SERVE/KB Embedding BGE-M3-ONNX 知识库嵌入(旧) | KB Embedding BGE-M3-ONNX 知识库嵌入(旧) | design | design_only |
| 22 | D-ML-SERVE/LLM API Integration LLM API集成 | LLM API Integration LLM API集成 | design | design_only |
| 23 | D-ML-SERVE/LLMGateway LLM网关 | LLMGateway LLM网关 | design | design_only |
| 24 | D-ML-SERVE/ML Serving ML服务 | ML Serving ML服务 | design | design_only |
| 25 | D-ML-SERVE/MLflow Model Update MLflow模型更新(旧) | MLflow Model Update MLflow模型更新(旧) | design | design_only |
| 26 | D-ML-SERVE/MS-01 | MS-01 | design | design_only |
| 27 | D-ML-SERVE/MS-02 | MS-02 | design | design_only |
| 28 | D-ML-SERVE/Market Prediction & Next-Day Trend Forecast 大... | Market Prediction & Next-Day Trend Fo... | design | design_only |
| 29 | D-ML-SERVE/Model Adversarial Attack Detector 模型对抗攻击... | Model Adversarial Attack Detector 模... | design | design_only |
| 30 | D-ML-SERVE/Model Compression & Inference Acceleration 模... | Model Compression & Inference Acceler... | design | design_only |
| 31 | D-ML-SERVE/Model Drift Monitor 模型漂移监控 | Model Drift Monitor 模型漂移监控 | design | design_only |
| 32 | D-ML-SERVE/Model Drift Monitor 模型漂移监控器 | Model Drift Monitor 模型漂移监控器 | design | design_only |
| 33 | D-ML-SERVE/Model Lifecycle Manager 模型生命周期管理器(旧) | Model Lifecycle Manager 模型生命周期... | design | design_only |
| 34 | D-ML-SERVE/Model Serving Manager 模型服务管理器 | Model Serving Manager 模型服务管理器 | design | design_only |
| 35 | D-ML-SERVE/Model Validator 模型验证器 | Model Validator 模型验证器 | design | design_only |
| 36 | D-ML-SERVE/Model 模型聚合根 | Model 模型聚合根 | design | design_only |
| 37 | D-ML-SERVE/ModelABTester 模型A/B测试器 | ModelABTester 模型A/B测试器 | design | design_only |
| 38 | D-ML-SERVE/ModelActivated 模型激活事件 | ModelActivated 模型激活事件 | design | design_only |
| 39 | D-ML-SERVE/ModelDeploymentPipeline 模型部署管线 | ModelDeploymentPipeline 模型部署管线 | design | design_only |
| 40 | D-ML-SERVE/ModelDeprecated 模型弃用事件 | ModelDeprecated 模型弃用事件 | design | design_only |
| 41 | D-ML-SERVE/ModelDriftDetected 模型漂移检测 | ModelDriftDetected 模型漂移检测 | design | design_only |
| 42 | D-ML-SERVE/ModelPerformanceDriftMonitor 模型性能漂移监控器 | ModelPerformanceDriftMonitor 模型性能... | design | design_only |
| 43 | D-ML-SERVE/ModelPerformanceMonitor 模型性能监控器 | ModelPerformanceMonitor 模型性能监控器 | design | design_only |
| 44 | D-ML-SERVE/ModelRiskGovernor 模型风险治理器 | ModelRiskGovernor 模型风险治理器 | design | design_only |
| 45 | D-ML-SERVE/ModelTrained 模型训练完成事件 | ModelTrained 模型训练完成事件 | design | design_only |
| 46 | D-ML-SERVE/Quantizer 量化器 | Quantizer 量化器 | design | design_only |
| 47 | D-ML-SERVE/SERVE→TRAIN hard import依赖 | SERVE→TRAIN hard import依赖 | design | design_only |
| 48 | D-ML-SERVE/ServingManager 服务管理器 | ServingManager 服务管理器 | design | design_only |
| 49 | D-ML-SERVE/TSFM 时间序列基础模型 | TSFM 时间序列基础模型 | design | design_only |
| 50 | D-ML-SERVE/Version 版本 | Version 版本 | design | design_only |
| 51 | D-ML-SERVE/Warm→Cold必须异步通信不变量 | Warm→Cold必须异步通信不变量 | design | design_only |
| 52 | D-ML-SERVE/§30.4.2 D-ML-SERVE 推理域（46个模块，P0=5） | §30.4.2 D-ML-SERVE 推理域（46个模块... | design | design_only |
| 53 | D-ML-SERVE/影子验证启动接口 Shadow Validation Start | 影子验证启动接口 Shadow Validation Start | design | design_only |
| 54 | D-ML-SERVE/影子验证指标报告接口 Shadow Metrics Report | 影子验证指标报告接口 Shadow Metrics R... | design | design_only |
| 55 | D-ML-SERVE/影子验证结果接口 Shadow Validation Result | 影子验证结果接口 Shadow Validation Re... | design | design_only |
| 56 | D-ML-SERVE/模型包格式契约 Model Package Format | 模型包格式契约 Model Package Format | design | design_only |
| 57 | D-ML-SERVE/模型回滚完成接口 Model Rollback Completed | 模型回滚完成接口 Model Rollback Compl... | design | design_only |
| 58 | D-ML-SERVE/模型回滚请求接口 Model Rollback Request | 模型回滚请求接口 Model Rollback Request | design | design_only |
| 59 | D-ML-SERVE/模型部署完成接口 Model Deploy Completed | 模型部署完成接口 Model Deploy Completed | design | design_only |
| 60 | D-ML-SERVE/模型部署请求接口 Model Deploy Request | 模型部署请求接口 Model Deploy Request | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 61 条 / 61 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 61 条 / 61 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 38 条 / edges                                │
│   [contract]: 13 条 / edges                                      │
│   [event]: 7 条 / edges                                          │
│   [config_depends]: 3 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (38 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Market Prediction & Next-... → ModelABTester 模型A/B测试器     │
│   D-ML-02 → MS-01                                                │
│   D-ML-02 → ML Serving ML服务                                    │
│   MS-01 → D-ML-03                                                │
│   D-ML-03 → MS-02                                                │
│   MS-02 → Model Validator 模型验证器                             │
│   Model Validator 模型验证器 → Model Drift Monitor 模型...       │
│   Model Drift Monitor 模型... → Model Serving Manager 模...      │
│   Model Serving Manager 模... → §30.4.2 D-ML-SERVE 推理...       │
│   §30.4.2 D-ML-SERVE 推理... → DriftMonitor 漂移监控器           │
│   DriftMonitor 漂移监控器 → ServingManager 服务管理器            │
│   ServingManager 服务管理器 → LLMGateway LLM网关                 │
│   LLMGateway LLM网关 → Model Compression & Infer...              │
│   Model Compression & Infer... → ModelRiskGovernor 模型风...     │
│   ModelRiskGovernor 模型风... → Model Adversarial Attack ...     │
│   Model Adversarial Attack ... → Inference Circuit Breaker...    │
│   Inference Circuit Breaker... → LLM API Integration LLM A...    │
│   LLM API Integration LLM A... → KB Embedding BGE-M3-ONNX ...    │
│   KB Embedding BGE-M3-ONNX ... → ModelABTester 模型A/B测试器     │
│   ModelABTester 模型A/B测试器 → ModelPerformanceMonitor ...      │
│   ModelPerformanceMonitor ... → TSFM 时间序列基础模型            │
│   TSFM 时间序列基础模型 → Quantizer 量化器                       │
│   TSFM 时间序列基础模型 → Model 模型聚合根                       │
│   Quantizer 量化器 → Fairness 公平性                             │
│   Fairness 公平性 → Explanation 解释器                           │
│   Explanation 解释器 → Impact 影响分析                           │
│   Impact 影响分析 → Adversarial 对抗                             │
│   Adversarial 对抗 → Version 版本                                │
│   Version 版本 → ModelDeploymentPipeline ...                     │
│   ModelDeploymentPipeline ... → ModelPerformanceDriftMoni...     │
│   ModelPerformanceDriftMoni... → Model Drift Monitor 模型...     │
│   Model Drift Monitor 模型... → KB Embedding BGE-M3-ONNX ...     │
│   KB Embedding BGE-M3-ONNX ... → MLflow Model Update MLflo...    │
│   MLflow Model Update MLflo... → AI Model A/B Tester AI模...     │
│   AI Model A/B Tester AI模... → AI Decision Explanation A...     │
│   AI Decision Explanation A... → Hybrid Deployment AI Mana...    │
│   Hybrid Deployment AI Mana... → Model Lifecycle Manager ...     │
│   Model Lifecycle Manager ... → AI Construction Governor ...     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    [contract] (13 条 / edges)                    │
├──────────────────────────────────────────────────────────────────┤
│   Model Serving Manager 模... → A/B测试启动接口 AB Test S...     │
│   Model Compression & Infer... → 模型部署请求接口 Model De...    │
│   ModelRiskGovernor 模型风... → 模型部署完成接口 Model De...     │
│   ModelRiskGovernor 模型风... → A/B测试指标报告接口 AB Te...     │
│   Model Adversarial Attack ... → 模型回滚请求接口 Model Ro...    │
│   Inference Circuit Breaker... → 模型包格式契约 Model Pack...    │
│   LLM API Integration LLM A... → A/B测试结论接口 AB Test R...    │
│   ModelABTester 模型A/B测试器 → 影子验证启动接口 Shadow V...     │
│   ModelPerformanceMonitor ... → 影子验证结果接口 Shadow V...     │
│   ModelPerformanceMonitor ... → A/B测试结论接口 AB Test R...     │
│   MLflow Model Update MLflo... → 模型回滚完成接口 Model Ro...    │
│   ...还有 2 条 / 2 more edges                                    │
└──────────────────────────────────────────────────────────────────┘

**[event]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (3 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 61 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `31_d_ml_serve_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
