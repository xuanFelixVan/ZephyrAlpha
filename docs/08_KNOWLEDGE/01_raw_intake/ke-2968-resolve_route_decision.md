---
module_id: KE-2868---------decision-000
status: active
title: 每次 resolve_route() 调用后写入 Decision Log
category: module_blueprint
---

# 每次 resolve_route() 调用后写入 Decision Log

每次 resolve_route() 调用后写入 Decision Log
def log_decision(task_card, route, violations):
    log = RouteDecisionLog(...)
    audit-trail.append(log)
```
