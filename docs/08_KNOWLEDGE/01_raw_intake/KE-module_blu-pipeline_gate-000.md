---
module_id: KE-module_blu-pipeline_gate-000
title: §三 实验Pipeline Gate节点
category: module_blueprint
---

# §三 实验Pipeline Gate节点

§三 实验Pipeline Gate节点

| Gate | 节点 | 通过条件 | 失败回退 |
|------|------|------|------|
| G11.1 | Data Integrity | 完整历史数据无gap | 等待回填 |
| G11.2 | Training Convergence | loss_curve稳态 | 调整lr/epoch |
| G11.3 | Validation Metrics | Sharpe>1 IC>0.03 IR>0.5 | 拒绝→存档 |
| G11.4 | Sanity Check | 无极端预测/过拟合 | Shadow Mode→分析 |
| G13.1 | AB Traffic Split | 1%流动性分配OK | step-down 0.1% |
| G13.2 | AB Evaluation | 统计差异显著 | continue观察 |
| G13.3 | Prod Cutover | Veto by Critic Agent | rollback |
