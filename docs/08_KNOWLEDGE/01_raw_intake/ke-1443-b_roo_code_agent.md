---
module_id: KE-1353----b-roo-code------agent--000
status: active
title: 10.2 模式 B：Roo Code / 外部 Agent JSON API
category: module_blueprint
ttl: permanent
---

# 10.2 模式 B：Roo Code / 外部 Agent JSON API

10.2 模式 B：Roo Code / 外部 Agent JSON API

```json
// → 请求
{"command": "run_phase", "phase": "discovery"}
// ← 响应
{"phase": "discovery", "orphans": 21, "zombies": 2, "status": "complete"}

// → 请求
{"command": "run_dimension", "dim_id": "DIM-TYPE-001"}
// ← 响应
{"dim_id": "DIM-TYPE-001", "pass": 1, "consecutive_clean": 0,
 "issues": [...], "converged": false, "next_action": "fix_and_rerun"}

// → 请求
{"command": "run_red_blue"}
// ← 响应
{"total": 7, "blocked": 7, "bypassed": 0, "passed": true}
```
