---
module_id: KE-2640----000
title: DB-025-0017：task_repo JSON1 查询+upsert 语义验证
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# DB-025-0017：task_repo JSON1 查询+upsert 语义验证

DB-025-0017：task_repo JSON1 查询+upsert 语义验证

验证 JSON1 查询使用 SQLite JSON1 扩展（json_extract/json_each），upsert 使用 ON CONFLICT DO UPDATE 保留 created_at，软删除设置 is_deleted=1 + deleted_at。
