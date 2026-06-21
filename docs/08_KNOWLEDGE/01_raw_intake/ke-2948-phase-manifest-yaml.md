---
module_id: KE-2848
status: active
title: phasemanifest.yaml 结构
category: module_blueprint
---

# phasemanifest.yaml 结构

phasemanifest.yaml 结构
```yaml
phases:
  scaffold:
    order: 1
    tasks: [TASK-INF-0101,0102,0103,0106,0112,0113,0119,0120,0121,0135,0137,0138]
    downstream_consumers: [experimental]
  experimental:
    order: 2
    tasks: [TASK-INF-0104,0105,0107,0111,0114,0122,0123,0128,0132,0133]
    downstream_consumers: [sandbox]
  sandbox:
    order: 3
    tasks: [TASK-INF-0115,0129]
    downstream_consumers: [beta]
  beta:
    order: 4
    tasks: [TASK-INF-0108,0109,0110,0116,0117,0118,0124]
    downstream_consumers: [v0_7_0]
  v0_7_0:
    order: 5
    tasks: [TASK-INF-0125,0126,0127]
    downstream_consumers: [self_calibrating]
  self_calibrating:
    order: 6
    tasks: [TASK-INF-0130,0131,0134,0136]
    downstream_consumers: []
```
