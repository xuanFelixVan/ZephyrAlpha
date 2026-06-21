---
module_id: KE-3926
title: 15.5 降级策略
category: module_blueprint
---

# 15.5 降级策略

15.5 降级策略

| 场景 | 响应 |
|------|------|
| ChromaDB 不可达 | knowledge_base / blueprint_search → `unavailable` 状态 → 返回错误 |
| SQLite 不可达 | 全局 → `unhealthy` → 503 |
| MCP Gateway 不可达 | 降级为直连模式（7 Server 直接对外） |
| 单 Server OOM | 该 Server 的 stdio 管道断开 → IDE 感知到可用工具减少 |
