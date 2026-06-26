---
module_id: KE-641
status: active
title: Step 1：确认数据就绪
category: documentation
ttl: permanent
---

# Step 1：确认数据就绪

Step 1：确认数据就绪

1. 检查行情数据是否已入库（参见 DOM-L00-001）
2. 检查交易日志是否已同步
3. 检查风控数据是否已更新
4. 如有数据源未就绪：等待 30 分钟后重试，超过 1 小时升级为 P2 事故，通知 Owner + 数据团队负责人
