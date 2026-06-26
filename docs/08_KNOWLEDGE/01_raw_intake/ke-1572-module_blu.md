---
module_id: KE-1482
status: active
title: 13.4 健康检查
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 13.4 健康检查

13.4 健康检查

- `healthz`：进程存活 + 关键依赖可用
- `readyz`：可服务（所有 tool handler 初始化完毕）
- 暴露为 MCP Tool：`{server_id}.health_check`

---
