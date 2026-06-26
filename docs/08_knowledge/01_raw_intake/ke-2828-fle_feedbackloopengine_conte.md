---
module_id: KE-2730---feedbackloopengine-conte-003
title: fle = FeedbackLoopEngine(context_adjust=get_ce())
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# fle = FeedbackLoopEngine(context_adjust=get_ce())

fle = FeedbackLoopEngine(context_adjust=get_ce())
```

**为什么用 Protocol**：避免 FLE → CE 的硬编码 import 形成循环依赖（CE 未来可能也订阅 FLE 的 metrics 作为 `runtime_state` 输入）。

---
