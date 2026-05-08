---
module_id: KE-documentat-7_2-000
title: 7.2 部署拓扑
category: documentation
---

# 7.2 部署拓扑

7.2 部署拓扑

```
浏览器（用户）
    │ HTTPS
    ▼
┌─────────────────────────────────────────────────────────┐
│  CDN / Edge（静态文件）                                 │
│  - platform/dist/index.html + main.js                   │
│  - apps/{app}/dist/remoteEntry.js （Module Federation） │
│  - packages/ui-kit/chart-engine（CDN 共享）             │
└───────────────────────────────┬─────────────────────────┘
                                │ /api/v1/*  /ws
                                ▼
┌─────────────────────────────────────────────────────────┐
│  L08 api_gateway/（FastAPI + WebSocket）                │
│  - /api/v1/orders                                       │
│  - /api/v1/positions                                    │
│  - /api/v1/signals                                      │
│  - /ws/v1/ticker                                        │
│  - /ws/v1/order-updates                                 │
└───────────────────────────────┬─────────────────────────┘
                                │ in-process calls
                                ▼
┌─────────────────────────────────────────────────────────┐
│  src/zephyr/ (14 层 Python 后端)                        │
│  L00-L07 / L09-L13                                      │
└─────────────────────────────────────────────────────────┘
```
