---
module_id: KE-402
status: active
title: 5.1 State 分域
category: documentation
---

# 5.1 State 分域

5.1 State 分域

```
┌───────────────────────────────────────────────────────────────┐
│  Global Store（platform/globalStore，Zustand）               │
│  - user / auth / theme / i18n / featureFlags（5 域，只读注入）│
└───────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────────┐
│  App-Local Store（apps/{app}/store，Zustand slice）          │
│  - 每个 App 私有业务状态（订单草稿、回测配置、图表时窗等）    │
└───────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────────┐
│  Server State（packages/data-client，TanStack Query）         │
│  - 所有后端数据（GET 结果）的缓存、自动重取、乐观更新         │
│  - Query Key 规范：['resource', { filters }]                  │
│  - Mutation 规范：对应后端 OpenAPI 操作 operationId          │
└───────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌───────────────────────────┴───────────────────────────────────┐
│  Real-time State（packages/data-client，WebSocket）           │
│  - Ticker / Order / Fill / RiskAlert 推送                    │
│  - 合并到 TanStack Query Cache，订阅者自动 re-render          │
└───────────────────────────────────────────────────────────────┘
```
