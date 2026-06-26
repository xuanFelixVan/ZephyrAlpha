---
module_id: KE-3903-------6-phase-000
title: 14.1 启动拓扑 (6 Phase)
category: module_blueprint
ttl: permanent
---

# 14.1 启动拓扑 (6 Phase)

14.1 启动拓扑 (6 Phase)

| Phase | 组件 | 依赖 | 超时 |
|:--:|------|------|:--:|
| P1 | Database (sqlite), Secrets | 无 | 5s |
| P2 | Context Engine, Gate Engine | P1 | 10s |
| P3 | Market Data Pipeline | P1 | 30s |
| P4 | Factor Engine, Signal Generator | P3 | 60s |
| P5 | OMS, Risk Controller | P4 | 30s |
| P6 | Dashboard, Telemetry | P5 | 10s |
