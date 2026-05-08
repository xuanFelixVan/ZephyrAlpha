---
module_id: KE-module_blu-bcdr__d-019-64-000
title: BCDR (D-019-64)
category: module_blueprint
---

# BCDR (D-019-64)

BCDR (D-019-64)
```
Tier 0: Agent CANNOT self-modify (OS-level enforcement)
Tier 1: Read-only Skills → no blast radius
Tier 2: Write to app state → blast radius ≤ 1 module (human approval)
Tier 3: Modify infrastructure → blast radius ≤ 1 service (human+governor co-sign)
```
