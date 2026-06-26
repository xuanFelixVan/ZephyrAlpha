---
module_id: KE-3393
title: 7.4 Event bus / 事件总线（当前状态）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 7.4 Event bus / 事件总线（当前状态）

7.4 Event bus / 事件总线（当前状态）

**当前架构决策：不引入消息总线。** 当前系统为单进程架构，所有层间调用为进程内同步调用。引入消息总线的条件是"需要多个并发服务"，当前未满足。
