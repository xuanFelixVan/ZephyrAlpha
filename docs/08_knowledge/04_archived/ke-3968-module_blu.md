---
module_id: KE-3815
title: 11.3 降级条件速查表
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 11.3 降级条件速查表

11.3 降级条件速查表

| 触发条件 | 降级动作 | 上游感知 |
|---------|---------|---------|
| FLE 自己挂 | 上游本地缓冲 metrics | DEGRADE-001 |
| 下游 Protocol 未注入 | pending_actions.ndjson 缓冲 | DEGRADE-002 |
| 下游调用失败 | 同上 | DEGRADE-002 |
| SQLite 读失败 | 基线返回 None，不触发 anomaly | 日志告警 |
| Action TTL 到期 | 自动回滚默认值 | 透明 |

所有降级写 `logs/fle_degrade.log`。

---
