---
module_id: KE-3336
title: 5.2 决策理由
category: documentation
---

# 5.2 决策理由

5.2 决策理由

| 决策 | 选择 | 不选的替代 | 理由 |
|------|------|----------|------|
| 客户端状态库 | **Zustand** | Redux Toolkit / Jotai / MobX | 最小 API 面、零 Provider 嵌套、与 React 18 并发模式兼容好 |
| 服务端状态库 | **TanStack Query v5** | SWR / Apollo Client / Redux Query | 对 REST/OpenAPI 支持成熟、自动失效策略强、WebSocket 合并能力好 |
| 实时通道 | **原生 WebSocket + 协议 Topic 约定** | Socket.IO / SignalR | 零依赖、后端 FastAPI 原生支持、Topic 字符串可直接入 OpenAPI 扩展 |
