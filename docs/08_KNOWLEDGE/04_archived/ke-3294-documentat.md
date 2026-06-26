---
module_id: KE-3182
title: 11.3 伸缩触发点
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 11.3 伸缩触发点

11.3 伸缩触发点

| 触发条件 | 响应动作 |
|---------|---------|
| CPU 月均峰值 >60% | 单机升级 16→32 core |
| Memory >70% 持续 3 日 | 升级 32→64 GB |
| Storage >70% | 升级 SSD + 归档冷存 |
| Backtest TAT p95 >30min 连续 7 日 | 启用 L09 并行跑批 |
| LLM Token 月成本 >$200 | 触发降级顺序 |
| 订单 QPS >5（Post-Activation） | 拆分 broker-specific worker |

---
