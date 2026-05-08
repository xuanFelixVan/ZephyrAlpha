---
module_id: KE-governance-4_3_3___________g3_evaluate_ya-000
title: 4.3.3 评分维度（定义于 `g3_evaluate.yaml:scoring_dimensions`）
category: governance
---

# 4.3.3 评分维度（定义于 `g3_evaluate.yaml:scoring_dimensions`）

4.3.3 评分维度（定义于 `g3_evaluate.yaml:scoring_dimensions`）

| 维度 | 权重 | 语义 |
|------|:---:|------|
| `design_decision_density` | 0.30 | 独立设计决策密度 |
| `technical_specificity` | 0.25 | 技术细节具体度 |
| `reuse_potential` | 0.25 | 跨模块可复用性 |
| `irreplaceability` | 0.20 | 知识不可替代性（他处未录）|

评分公式：`weighted_sum(dim_i * weight_i)`，结果 ∈ [0, 1]。
