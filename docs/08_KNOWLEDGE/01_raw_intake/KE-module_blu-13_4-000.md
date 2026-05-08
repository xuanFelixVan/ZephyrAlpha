---
module_id: KE-module_blu-13_4-000
title: 13.4 健康检查
category: module_blueprint
---

# 13.4 健康检查

13.4 健康检查

- `healthz`：进程存活 + 关键依赖可用
- `readyz`：可服务（所有 tool handler 初始化完毕）
- 暴露为 MCP Tool：`{server_id}.health_check`

---
