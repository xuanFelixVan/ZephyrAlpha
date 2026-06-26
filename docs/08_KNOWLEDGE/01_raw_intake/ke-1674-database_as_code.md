---
module_id: KE-1584---------database-as-code-000
status: active
title: 18.3 数据库作为代码（Database-as-Code）
category: module_blueprint
ttl: permanent
---

# 18.3 数据库作为代码（Database-as-Code）

18.3 数据库作为代码（Database-as-Code）

```yaml
principles:
  - "DDL 在 sqlite_schema.py 中定义为 Python 字符串常量——不是外置 .sql 文件"
  - "Schema 版本化：_MIGRATIONS 注册表 = single source of truth"
  - "init_db() 幂等——可在 CI/CD/本地任意环境重复执行"
  - "PRAGMA 基线：所有连接通过 get_db_connection() 统一配置——不允许手动调 PRAGMA"

anti_patterns_to_avoid:
  - "❌ 手动执行 SQL 文件初始化数据库"
  - "❌ 不同环境使用不同的 PRAGMA 配置"
  - "❌ 绕过 init_db() 直接 sqlite3.connect()"
  - "❌ 在业务代码中写 DDL"
```
