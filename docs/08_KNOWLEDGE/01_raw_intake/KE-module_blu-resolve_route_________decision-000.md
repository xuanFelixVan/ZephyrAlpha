---
module_id: KE-module_blu-resolve_route_________decision-000
title: 每次 resolve_route() 调用后写入 Decision Log
category: module_blueprint
---

# 每次 resolve_route() 调用后写入 Decision Log

每次 resolve_route() 调用后写入 Decision Log
def log_decision(task_card, route, violations):
    log = RouteDecisionLog(...)
    audit_trail.append(log)
```
