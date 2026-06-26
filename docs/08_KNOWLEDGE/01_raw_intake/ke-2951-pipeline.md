---
module_id: KE-2851
status: active
title: §一 模型生命周期 Pipeline
category: module_blueprint
ttl: permanent
---

# §一 模型生命周期 Pipeline

§一 模型生命周期 Pipeline

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
