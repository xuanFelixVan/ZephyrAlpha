---
module_id: KE-4061
title: 3.3 Distribution Dependencies（分布式依赖）
category: module_blueprint
---

# 3.3 Distribution Dependencies（分布式依赖）

3.3 Distribution Dependencies（分布式依赖）

| 依赖 | 具体对象 |
|------|---------|
| Agent Health Monitor | 5-SLO Orchestrator |
| CBG Manager + L08 Circuit | gate-engine熔断 |
| Kill Switch Agent | 全局一键熔断 |
| Graceful-Shutdown Lifecycle | startup_guard/graceful_shutdown 协同 |
| Emergency Pool | Kill Switch启动预分配 |
