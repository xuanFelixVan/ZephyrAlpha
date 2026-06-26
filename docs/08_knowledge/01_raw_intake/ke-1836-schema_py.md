---
module_id: KE-1745-----schema-py-000
status: active
title: 2.2 创建 `schema.py`
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.2 创建 `schema.py`

2.2 创建 `schema.py`

创建 `D:\ZephyrAlpha\src\\zephyr\\shared\\schema.py`，实现：
- `SchemaManager.init_db(db_path: str)`: 执行 DDL，创建全部表
- `SchemaManager.migrate()`: 从旧 Schema 版本迁移
- `SchemaManager.verify()`: 校验表结构完整性
- `SchemaManager.ttl_cleanup()`: 清理超过 TTL 的 capacity_metrics 行
- `get_db_path()`: 从环境变量 `CAPACITY_METRICS_DB_PATH` / `AI_AUDIT_PROVENANCE_DB_PATH` 读取路径
