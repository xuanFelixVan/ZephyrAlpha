---
module_id: KE-1998----d-000
status: active
title: 3. CE-Orc Precedence (B22) — DD96
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3. CE-Orc Precedence (B22) — DD96

3. CE-Orc Precedence (B22) — DD96

CE 上下文优先级高于 Orc 系统提示：

```
CE context = "task-specific ground truth"
Orc prompt = "general guidance"
```

冲突时 inject 标记 `[CE_OVERRIDES_SYSTEM_PROMPT]`，Agent 明确知道以 CE 为准。
