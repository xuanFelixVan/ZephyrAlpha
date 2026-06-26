---
module_id: KE-644----kill-switch-000
status: active
title: Step 3.5：确认 Kill Switch 配置
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# Step 3.5：确认 Kill Switch 配置

Step 3.5：确认 Kill Switch 配置

根据 DOM-L04-001 §4，必须确认 Kill Switch 参数已正确配置：

1. 全局回撤触发线（默认 2%，参见 DOM-L04-001 ABS-001）
2. 连续止损触发次数上限（默认 3 次 → 触发 kill switch）
3. Kill Switch 触发后的恢复流程（需要 Owner 手动解除）
4. 确认 kill switch 与交易所接口联通（下单阻塞 + 平仓指令可送达）
