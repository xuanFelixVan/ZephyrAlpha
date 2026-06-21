---
module_id: KE-4288----000
title: DB-025-0017：task_repo JSON1 查询+upsert 语义验证
category: module_blueprint
---

# DB-025-0017：task_repo JSON1 查询+upsert 语义验证

DB-025-0017：task_repo JSON1 查询+upsert 语义验证

验证 JSON1 查询使用 SQLite JSON1 扩展（json_extract/json_each），upsert 使用 ON CONFLICT DO UPDATE 保留 created_at，软删除设置 is_deleted=1 + deleted_at。
