---
module_id: KE-4442
title: 5.1 触发点
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# 5.1 触发点

5.1 触发点

Context Engine 启动时调用 `load_session_carryover()`，位于 `CE.__aenter__` 或 `CE.initialize()`。
