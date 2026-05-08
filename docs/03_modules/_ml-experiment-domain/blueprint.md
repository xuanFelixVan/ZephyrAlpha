---
module_id: "ML-EXPERIMENT-DOMAIN-001"
title: "ML-Experiment ML域总蓝图 — L11 ML平台 → L13 实验管线 跨层集成"
doc_type: blueprint
status: Active
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
tags: [ml-experiment-domain, l11, l13, ml-platform, experimentation, domain-integration]
submodule_path: src/zephyr/
submodule_paths_scope: ml-experiment-domain
submodule_paths_extra:
  - src/zephyr/l11_ml_platform/
  - src/zephyr/l13_experimentation/
priority: P2
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
ttl: permanent
construction_progress: not_started
blueprint_level: domain
summary: "ML实验域（L11 + L13）Level 1 集成蓝图——定义 ML平台(MOD-ML-001)到实验管线(MOD-EXP-001)的模型生命周期、AB测试链路、特征存储读写和实验元数据追踪。本蓝图不重复 L11/L13 模块内部规范，只定义跨层集成协议。"
belongs_to: "SYS-MASTER-001"
ai_role_instruction: >
  你是 ML-Experiment 域 Level 1 集成蓝图。
  职责：(1) 定义 L11 ML模型构建→L13 实验验证的完整生命周期；
  (2) 定义跨层接口契约 ME-CT-*——所有 model training/evaluation 变更 MUST 对照；
  (3) 真源优先级：SYS-MASTER-001 §七十八~§八十四 > 本蓝图 > L11/L13 模块蓝图；
  (4) 模型上线前 MUST 通过 §三 Pipeline Gate 全部节点；
  (5) 所有 experiment run MUST 登记 experiment tracking DB + Telemetry metrics。
---

# ML-Experiment ML域总蓝图

## §一 模型生命周期 Pipeline

```
Feature Store (VMS/KB) → ML Core (L11)
  ├── 特征工程[pipeline: lgbm/xgboost/linear_stack]
  ├── 训练调度[Data→Train→Validate→Sanity Gate]
  ├── 检查点存储[INF-012 database: MODEL_CHECKPOINTS table]
  └── ↓
Experiment Pipeline (L13)
  ├── AB测试[配置→分配→监控→分析师→发布/回滚]
  ├── 回测实验[ckpt→historical→PnL→Attribution→Report]
  ├── Shadow Mode测试[旁路预测→Threshold→分歧告警→正式切流]
  └── 归档[ExperimentArtifact: config/env/result, INF-012]
```

## §二 跨层接口契约

| 契约ID | 方向 | 描述 | 状态 | CT引用 |
|---------|------|------|:---:|------|
| ME-CT-FEATURE-001 | VMS/KB→L11 | 特征向量读取（ChromaDB collections: factor-signals, model-features） | Draft | MOD-INF-011 |
| ME-CT-TRAIN-001 | L11 internal | 训练Pipeline Gate：数据→训练→验证→Sanity→发布 | Draft | — |
| ME-CT-CHECKPOINT-001 | L11→L13 | 检查点导入（MODEL_CHECKPOINTS→AB/Backtest Experiment） | Draft | MOD-INF-012 |
| ME-CT-AB-001 | L13 internal | AB实验全流程：config→traffic_split→gate[eval]→analyst→deploy/rollback | Draft | — |
| ME-CT-BACKTEST-001 | L13 internal | 回测实验：ckpt→historical→PnL→Attribution→Report | Draft | — |
| ME-CT-SHADOW-001 | L13 | Shadow Mode：旁路预测→threshold→divergence alert→正式切流 | Draft | — |

## §三 实验Pipeline Gate节点

| Gate | 节点 | 通过条件 | 失败回退 |
|------|------|------|------|
| G11.1 | Data Integrity | 完整历史数据无gap | 等待回填 |
| G11.2 | Training Convergence | loss_curve稳态 | 调整lr/epoch |
| G11.3 | Validation Metrics | Sharpe>1 IC>0.03 IR>0.5 | 拒绝→存档 |
| G11.4 | Sanity Check | 无极端预测/过拟合 | Shadow Mode→分析 |
| G13.1 | AB Traffic Split | 1%流动性分配OK | step-down 0.1% |
| G13.2 | AB Evaluation | 统计差异显著 | continue观察 |
| G13.3 | Prod Cutover | Veto by Critic Agent | rollback |

## §四 故障模式

| FMEA ID | 故障 | 影响 | 缓解 |
|---------|------|------|------|
| ME-FMEA-001 | Model Pipeline Timeout | Training stuck，无法评估 | 超时kill + Checkpoint保留 |
| ME-FMEA-002 | AB Test Traffic Split Without Budget | 无限实验烧Token | Budget Enforcer(INF-024) |
| ME-FMEA-003 | Checkpoint Corruption | Shadow→Prod切流失败 | INF-020 Audit Provence + INF-021 Rollback |
| ME-FMEA-004 | AB Test 统计不显著 | 噪声误判为显著 | Bayesian戳 + Sequential Testing |


---

## 施工落盘确认（2026-05-07 审计）

| 维度 | 状态 |
|------|------|
| construction_progress | not_started（蓝图文档完成，L11/L13模块 blocked_by_infrastructure，跨层管道未施工） |
| 文档路径 | docs/03_modules/_ml-experiment-domain/blueprint.md (域集成文档) |
| 说明 | 架构/集成文档——定义跨模块契约与集成标准。底层C轨模块 blocked_by_infrastructure，代码施工待基建域就绪后启动 |
