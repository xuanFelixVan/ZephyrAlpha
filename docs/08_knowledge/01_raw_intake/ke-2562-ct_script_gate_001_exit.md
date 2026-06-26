---
module_id: KE-2467---exit--000
status: active
title: 8.1 CT-SCRIPT-GATE-001：脚本exit code → Gate判定
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.1 CT-SCRIPT-GATE-001：脚本exit code → Gate判定

8.1 CT-SCRIPT-GATE-001：脚本exit code → Gate判定

> 详见总蓝图 [MOD-MASTER_BLUEPRINT · CT-SCRIPT-GATE-001](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md)。

```
脚本 exit 0 → GATE-n PASS → 任务状态不变
脚本 exit 1 → GATE-n PASS_WITH_WARNINGS → 任务 ⚠️
脚本 exit 2 → GATE-n FAIL → 关联任务 BLOCKED
脚本 exit 3 → GATE-n CRITICAL_FAIL → 全部活跃任务 BLOCKED
```
