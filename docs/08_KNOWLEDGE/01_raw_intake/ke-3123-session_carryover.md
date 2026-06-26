---
module_id: KE-3021
status: active
title: 1.2 Session Carryover 的解决
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# 1.2 Session Carryover 的解决

1.2 Session Carryover 的解决

```
Session A 结束前
  │
  ▼
Context Engine.save_session_carryover(session_id)
  │
  ▼
写入 .runtime/sessions/session_carryover.json
  │
  │ [IDE 关闭 / 用户下班 / 机器重启]
  │
  ▼
Session B 启动后
  │
  ▼
Context Engine.load_session_carryover()
  │
  ▼
Agent 接续工作：知道上次 TODO、已尝试过的失败、已知风险
```
