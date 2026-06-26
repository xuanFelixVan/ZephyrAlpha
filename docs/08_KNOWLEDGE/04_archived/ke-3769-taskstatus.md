---
module_id: KE-3618----taskstatus-000
title: 6.4 与 `TaskStatus` 十状态的交互
category: governance
ttl: permanent
---

# 6.4 与 `TaskStatus` 十状态的交互

6.4 与 `TaskStatus` 十状态的交互

| `TaskStatus` | 门禁相关含义 |
|-------------|-------------|
| `PENDING` | 尚未通过 G1 |
| `IN_PROGRESS` | 通过 G1，正在进行分流/评估工作 |
| `COMPLETED` | 通过 G2，等待 G3 评估 |
| `VERIFIED` | 通过 G3，可进入激活/提取阶段（终态，不等于"已入知识库"）|
| `FAILED` | 任一门禁 P0 失败后的软删状态；可 `→RETRY→IN_PROGRESS` 重跑 |
| `BLOCKED` | G4 冲突 或 人工阻断；需 Owner 仲裁 → `READY` |
| `WAITING` | G4 依赖未就绪；`waiting_for` 字段存缺失依赖 ID |
| `READY` | 重新进入工作流的入口 |
| `RETRY` | `FAILED` 后申请重试，下一步必进 `IN_PROGRESS` |
| `CANCELLED` | 终态，不触发任何门禁 |

---
