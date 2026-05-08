---
module_id: KE-module_blu-3_4-000
title: 3.4 输出契约
category: module_blueprint
---

# 3.4 输出契约

3.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `decompose()` | `DecompositionResult`：N 张 TaskCard + SQLite 已写入 + .md 同步 | `FILE_NOT_FOUND` / `NO_CONSTRUCTION_GUIDE` / `G7_VIOLATIONS` |
| `create_task_card()` | TaskCard + task_repo.create() 成功 + .md 副本 | `GATE_BLOCKED(G0/G7)` / `DUPLICATE_ID(409)` / `PATH_NOT_COMPLIANT`(MTH-013) |
| `transition()` | task_repo.update_status() 成功 + events 记录 | `STATUS_MISMATCH(409)` / `ILLEGAL_TRANSITION(422)` / `GATE_BLOCKED(422)` |
| `dispatch()` | 管线+模型+M模块链已分配 | `INVALID_DISPATCH_STATUS(409)` / `NO_PIPELINE_AVAILABLE(503)` |
