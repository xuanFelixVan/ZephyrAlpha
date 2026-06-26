---
module_id: KE-3222
title: 2.4 Interface classification / 接口分类
category: documentation
ttl: permanent
---

# 2.4 Interface classification / 接口分类

2.4 Interface classification / 接口分类

| Interface / 接口 | Direction / 方向 | Trigger / 触发方 | Criticality / 关键性 |
|----------------|----------------|----------------|---------------------|
| Broker order submission | Outbound | Execution Engine | 🔴 Critical — 直接影响资金安全 |
| Broker fill & position callback | Inbound | Broker push | 🔴 Critical — 持仓状态真源 |
| Market data feed | Inbound | Data Provider push/pull | 🟠 High — 数据缺失影响所有下游 |
| LLM inference | Outbound | AI Agent Ops | 🟡 Medium — 可降级（缓存/跳过） |
| Feishu notification | Outbound | Analytics / Risk Engine | 🟢 Low — 告警通道，不影响主流程 |

---
