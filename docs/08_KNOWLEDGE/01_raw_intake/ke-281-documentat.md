---
module_id: KE-259-----14-003
status: active
title: 3.2 与后端 14 层的调用规则
category: documentation
ttl: permanent
---

# 3.2 与后端 14 层的调用规则

3.2 与后端 14 层的调用规则

```
frontend/apps/*        ──┐
frontend/platform/*    ──┼──→  L08 api_gateway（FastAPI + WebSocket + OpenAPI）──→  L00-L07/L09-L13 Python 后端
frontend/packages/*    ──┘
```

**唯一出口**：`packages/data-client/` 内部封装所有 HTTP/WebSocket 调用，通过 L08 `api_gateway/`。apps/ 与 platform/ **不得直接 fetch** 后端模块。
