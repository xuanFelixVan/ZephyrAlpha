---
module_id: KE-4174
title: 6.3 Finding → 任务卡自动创建
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6.3 Finding → 任务卡自动创建

6.3 Finding → 任务卡自动创建

| Finding.severity | 是否自动创建任务卡 | 关联Gate |
|:---:|:---:|:---:|
| CRITICAL | ✅ 自动创建（P0） | G0-G7 阻断 |
| HIGH | ✅ 自动创建（P1） | G0-G7 阻断 |
| MEDIUM | ⚠️ 手动决定 | 警告不阻断 |
| LOW | ❌ 不创建 | — |
| INFO | ❌ 不创建 | — |
