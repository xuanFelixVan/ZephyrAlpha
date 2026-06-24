---
module_id: KE-2005---13-000
title: 3. Google Context Caching (§13.2)
category: module_blueprint
---

# 3. Google Context Caching (§13.2)

3. Google Context Caching (§13.2)

| 层级 | 特征 | 我们有？ | 对应任务 |
|------|------|:---:|---------|
| Hot | 同 session 高频复用 | ❌ | AP4 缓存 |
| Warm | 跨 session 共享 60min | ❌ | TASK-014 (beta a eviction) |
| Cold | 长期存储 permanent | ✅ | VMS 全量 KE |
