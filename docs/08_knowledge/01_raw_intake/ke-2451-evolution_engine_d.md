---
module_id: KE-2356---------d-000
status: active
title: 6.1 Evolution Engine 反馈闭环（决策 D-023-10）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6.1 Evolution Engine 反馈闭环（决策 D-023-10）

6.1 Evolution Engine 反馈闭环（决策 D-023-10）

> **决策 D-023-10**：漂移时序数据定期喂给 Evolution Engine（`feedback_loop/evolution_engine.py`）。高频漂移模块的蓝图设计应被标记为"需要重构"或"接口设计有问题"。
>
> **决策依据**：漂移不只是需要修的问题——它是蓝图设计质量的信号。反复漂移 = 蓝图边界不清晰。

```yaml
evolution_integration:
  trigger: "每次 DEEP scan 完成后"
  payload:
    - module_id: "漂移模块"
    - drift_velocity_30d: "近 30 天漂移速度"
    - top_drift_dimensions: "最高频漂移维度 TOP 3"
    - suggested_action: "EVOLVE_BLUEPRINT | ADD_CONTRACT | SPLIT_MODULE"
  feedback_loop: "Evolution Engine → 更新 blueprint_scorer → 调整模块评分 → 影响施工优先级"
```
