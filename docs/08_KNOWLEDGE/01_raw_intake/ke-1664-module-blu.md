---
module_id: KE-1574
title: 17.3 告警阈值
category: module_blueprint
---

# 17.3 告警阈值

17.3 告警阈值

| 预测指标 | Warning 阈值 | Critical 阈值 | 触发动作 |
|---------|------------|-------------|---------|
| 预测模块数 30d | > 300 | > 500 | Critical → 启动 beta 服务化准备 |
| 预测内存 30d | > 物理内存 70% | > 物理内存 90% | Critical → 触发 Kill Switch 保守模式 |
| 预测成本 30d | > $150/day | > $300/day | Critical → 自动启用 Graceful Degradation |
| 预测测试时长 30d | > 300s | > 600s | Warning → 并行化测试 |

---
