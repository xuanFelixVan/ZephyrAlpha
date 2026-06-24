---
module_id: KE-344---c-000
status: active
title: 4.3 KeStatus（域 C：知识条目）
category: documentation
---

# 4.3 KeStatus（域 C：知识条目）

4.3 KeStatus（域 C：知识条目）

> 代码真源：`src/zephyr/kb/kb_repo.py` `KeStatus` 枚举

| status | 含义 | 终态？ | 向量可见？ |
|--------|------|:------:|:---------:|
| `DRAFT` | 草稿 | ❌ | ❌ |
| `SUBMITTED` | 已提交待审 | ❌ | ❌ |
| `REVIEWED` | 已审阅 | ❌ | ❌ |
| `ACCEPTED` | 已接受 | ❌ | ❌ |
| `INDEXED` | 已索引 | ❌ | ✅ |
| `VERIFIED` | 已验证 | ❌ | ✅ |
| `REJECTED` | 已否决 | ❌ | ❌ |
| `DEPRECATED` | 已废弃 | ❌ | ✅ |
| `SUPERSEDED` | 已取代 | ❌ | ✅ |
| `ARCHIVED` | 已归档 | ✅ | ❌ |

**状态流转**（代码真源：`kb_repo.py`）：

```
DRAFT → SUBMITTED → REVIEWED → ACCEPTED → INDEXED → VERIFIED
                     ↓          ↓          ↓         ↓
                  REJECTED   REJECTED   REJECTED   DEPRECATED → ARCHIVED
                     ↓                              SUPERSEDED → ARCHIVED
                   DRAFT
```
