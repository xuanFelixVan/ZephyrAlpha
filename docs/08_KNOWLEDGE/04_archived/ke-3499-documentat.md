---
module_id: KE-3363
title: 6.2 违反处置
category: documentation
ttl: permanent
---

# 6.2 违反处置

6.2 违反处置

| 违反级别    | 处置                                    |
| ------- | ------------------------------------- |
| 🔴 ABS  | 即时阻断操作 → 记录事件到 Session Log → 通知 Owner |
| 🟡 COND | 条件触发时阻断 → 记录原因 → 按领域规则处理              |
| 🟢 REC  | 记录但不阻断 → 下次审查时评估是否升级为 COND            |
