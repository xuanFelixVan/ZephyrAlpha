---
module_id: KE-documentat-4_2_taskstatus___b-000
title: 4.2 TaskStatus（域 B：任务系统）
category: documentation
---

# 4.2 TaskStatus（域 B：任务系统）

4.2 TaskStatus（域 B：任务系统）

> 代码真源：`src/zephyr/shared/schemas.py` `TaskStatus` 枚举

| status | 含义 | 终态？ |
|--------|------|:------:|
| `PENDING` | 待执行 | ❌ |
| `IN_PROGRESS` | 执行中 | ❌ |
| `COMPLETED` | 已完成 | ❌ |
| `VERIFIED` | 已验证 | ✅ |
| `FAILED` | 执行失败 | ❌ |
| `BLOCKED` | 被阻塞 | ❌ |
| `WAITING` | 等待中 | ❌ |
| `READY` | 就绪待执行 | ❌ |
| `RETRY` | 重试中 | ❌ |
| `CANCELLED` | 已取消 | ✅ |

**状态流转**（代码真源：`task_repo.py`）：

```
PENDING → IN_PROGRESS → COMPLETED → VERIFIED
  ↓          ↓              ↓
BLOCKED    FAILED         CANCELLED
  ↓          ↓
 READY     RETRY → IN_PROGRESS
WAITING → READY
```
