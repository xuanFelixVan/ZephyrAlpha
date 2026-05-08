---
module_id: KE-module_blu-ct-script-gate-001-000
title: 四、集成概览（CT-SCRIPT-GATE-001）
category: module_blueprint
---

# 四、集成概览（CT-SCRIPT-GATE-001）

四、集成概览（CT-SCRIPT-GATE-001）

> 详见总蓝图 [MOD-MASTER-001 §2.8](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md)。

```
脚本 exit 0 → GATE-n PASS → 任务状态不变
脚本 exit 1 → GATE-n PASS_WITH_WARNINGS → 任务 ⚠️
脚本 exit 2 → GATE-n FAIL → 关联任务 BLOCKED
脚本 exit 3 → GATE-n CRITICAL_FAIL → 全部活跃任务 BLOCKED
```

---
---
