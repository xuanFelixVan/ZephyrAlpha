---
doc_type: domain_architecture_doc
title: D-ML_SERVE 推理架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-ML_SERVE 推理架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-ML_SERVE |
| 域名称 | 推理 |
| 架构层 | L2_domain |
| 模块总数 | 69 |
| 设计态模块 | 62 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 机器学习推理域。负责ML模型推理服务，包括模型部署、在线推理、批推理、模型版本管理、A/B测试。 |

## 模块清单

共 69 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
|  | MOD-ML_SERVE | path_invalid | design | 0 | 0 |
| D-ML-SERVE/A/B测试启动接口 AB Test Start |  | design_only | design | 0 | 0 |
| D-ML-SERVE/A/B测试指标报告接口 AB Test Metrics Report |  | design_only | design | 0 | 0 |
| D-ML-SERVE/A/B测试结论接口 AB Test Result |  | design_only | design | 0 | 0 |
| D-ML-SERVE/AI Construction Governor AI构建治理器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/AI Decision Explanation AI决策解释(旧) |  | design_only | design | 0 | 0 |
| D-ML-SERVE/AI Model A/B Tester AI模型A/B测试器(旧) |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Adversarial 对抗 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Cold→Hot禁止直接通信不变量 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/D-ML-02 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/D-ML-03 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/DriftMonitor 漂移监控器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/E-RS-03 模型预测事件 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Explanation 解释器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Fairness 公平性 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/GPU推理熔断器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Hybrid Deployment AI Manager 混合部署AI管理器(旧) |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Impact 影响分析 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Inference Circuit Breaker 推理熔断器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/InferenceDegraded 推理降级事件 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/KB Embedding BGE-M3-ONNX KB嵌入BGE-M3-ONNX |  | design_only | design | 0 | 0 |
| D-ML-SERVE/KB Embedding BGE-M3-ONNX 知识库嵌入(旧) |  | design_only | design | 0 | 0 |
| D-ML-SERVE/LLM API Integration LLM API集成 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/LLMGateway LLM网关 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ML Serving ML服务 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/MLflow Model Update MLflow模型更新(旧) |  | design_only | design | 0 | 0 |
| D-ML-SERVE/MS-01 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/MS-02 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Market Prediction & Next-Day Trend Forecast 大盘预测与次日走势预判 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model Adversarial Attack Detector 模型对抗攻击检测器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model Compression & Inference Acceleration 模型压缩与推理加速 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model Drift Monitor 模型漂移监控 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model Drift Monitor 模型漂移监控器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model Lifecycle Manager 模型生命周期管理器(旧) |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model Serving Manager 模型服务管理器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model Validator 模型验证器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Model 模型聚合根 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelABTester 模型A/B测试器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelActivated 模型激活事件 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelDeploymentPipeline 模型部署管线 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelDeprecated 模型弃用事件 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelDriftDetected 模型漂移检测 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelPerformanceDriftMonitor 模型性能漂移监控器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelPerformanceMonitor 模型性能监控器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelRiskGovernor 模型风险治理器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ModelTrained 模型训练完成事件 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Quantizer 量化器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/SERVE→TRAIN hard import依赖 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/ServingManager 服务管理器 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/TSFM 时间序列基础模型 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Version 版本 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/Warm→Cold必须异步通信不变量 |  | design_only | design | 0 | 0 |
| D-ML-SERVE/§30.4.2 D-ML-SERVE 推理域（46个模块，P0=5） |  | design_only | design | 0 | 0 |
| D-ML-SERVE/影子验证启动接口 Shadow Validation Start |  | design_only | design | 0 | 0 |
| D-ML-SERVE/影子验证指标报告接口 Shadow Metrics Report |  | design_only | design | 0 | 0 |
| D-ML-SERVE/影子验证结果接口 Shadow Validation Result |  | design_only | design | 0 | 0 |
| D-ML-SERVE/模型包格式契约 Model Package Format |  | design_only | design | 0 | 0 |
| D-ML-SERVE/模型回滚完成接口 Model Rollback Completed |  | design_only | design | 0 | 0 |
| D-ML-SERVE/模型回滚请求接口 Model Rollback Request |  | design_only | design | 0 | 0 |
| D-ML-SERVE/模型部署完成接口 Model Deploy Completed |  | design_only | design | 0 | 0 |
| D-ML-SERVE/模型部署请求接口 Model Deploy Request |  | design_only | design | 0 | 0 |
| src/zephyr/ml_serve/__init__.py | MOD-ML_SERVE | orphan | prototype | 0 | 0 |
| src/zephyr/ml_serve/_extensions/__init__.py | MOD-ML_SERVE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_serve/api/__init__.py | MOD-ML_SERVE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_serve/core/__init__.py | MOD-ML_SERVE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_serve/infrastructure/__init__.py | MOD-ML_SERVE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_serve/models/__init__.py | MOD-ML_SERVE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ml_serve/services/__init__.py | MOD-ML_SERVE | orphan | scaffold_placeholder | 0 | 0 |
| 推理域/D-ML-136 | MOD-ML_SERVE | design_only | design | 0 | 3 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-SECURITY | 11 | data,config_depends,contract,event |
| D-SIGNAL | 6 | data,config_depends,event,contract |
| D-INFRA_RUNTIME | 6 | contract,event,data,domain_dependency |
| D-FACTOR | 5 | event,contract,data,config_depends |
| D-RISK | 4 | contract,event |
| D-ML_TRAIN | 4 | data,contract,domain_dependency,event |
| D-POSITION | 3 | data,contract |
| D-DATA_ENG | 3 | data,contract |
| D-TRADING | 2 | contract,config_depends |
| D-MKT_DATA | 2 | contract,config_depends |
| D-EX_SOR | 2 | data,contract |
| D-SHARED | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 21 | event,data,contract,config_depends |
| D-OPS | 11 | contract,config_depends,event,data |
| D-GOVERNANCE | 9 | event,data,contract,config_depends |
| D-AUTONOMY_CORE | 7 | event,contract,data,config_depends |
| D-INTELLIGENCE | 6 | contract,data,domain_dependency,event |
| D-INFRA_OPS | 6 | event,contract,data |
| D-PF_CORE | 4 | data,contract,event |
| D-FRONTEND | 4 | event,contract,data |
| D-KNOWLEDGE | 3 | data,config_depends,event |
| D-REPORTING | 2 | config_depends |
| D-INTEGRATION | 2 | contract,config_depends |
| D-ALT_DATA | 2 | event,data |
| D-SIMULATION | 1 | contract |
| D-DATA_GOV | 1 | contract |
| D-CROSS_ASSET | 1 | data |
| D-AUTONOMY_PERM | 1 | data |

## 域内依赖图

详见 [d_ml_serve_dependency.mmd](d_ml_serve_dependency.mmd)
