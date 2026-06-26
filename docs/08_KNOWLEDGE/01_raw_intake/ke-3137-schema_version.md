---
module_id: KE-3035
title: 8.1 schema_version 约定
category: session_log
ttl: permanent
doc_type: knowledge_entry
---

# 8.1 schema_version 约定

8.1 schema_version 约定

| 版本 | 变更类型 | 迁移策略 |
|------|---------|---------|
| `1.0.0` → `1.X.0` | 向后兼容（加字段）| 老文件加载时填默认值 |
| `1.X.0` → `2.0.0` | 破坏性变更 | 强制调用 `_migrate_schema_1_to_2()` |
