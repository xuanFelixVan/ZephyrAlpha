---
module_id: KE-documentat-step_6-003
title: Step 6：注册与监控
category: documentation
---

# Step 6：注册与监控

Step 6：注册与监控

1. 在 `factor-registry.yaml` 中注册新因子，必须填写：
   - 因子 ID / 名称 / 类型
   - 回测指标（夏普 / 回撤 / IC / IC_IR）
   - 换手率与容量参数
   - 质量门控状态
2. 验证因子计算延迟 ≤ 50ms（参见 DOM-L02-001 §2 ABS-003），如超出必须优化
3. 配置衰减监控（参见 DOM-L02-001 §3 COND-001）
4. 配置告警规则
