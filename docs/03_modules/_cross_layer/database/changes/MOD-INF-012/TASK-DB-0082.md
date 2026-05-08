---
task_id: "DB-025-0082"
namespace: "OPS"
seq: 82
title: "Database-as-Code 原则 §18.3——YAML 代码块 4 条规则落地验证"
tags: ["fn:daas", "ly:cross_layer"]
depends_on: ["DB-025-0053", "DB-025-0054", "DB-025-0055", "DB-025-0056"]
upstream_files:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\__init__.py"
acceptance_criteria:
  - "原则1: DDL在sqlite_schema.py中定义为Python字符串常量——不是外置.sql文件"
  - "原则2: Schema版本化_MIGRATIONS注册表=single source of truth"
  - "原则3: init_db()幂等——可在CI/CD/本地任意环境重复执行"
  - "原则4: PRAGMA基线通过get_db_connection()统一配置——不允许手动调PRAGMA"
  - "反模式1: ❌手动执行SQL文件初始化数据库"
  - "反模式2: ❌不同环境使用不同的PRAGMA配置"
  - "反模式3: ❌绕过init_db()直接sqlite3.connect()"
  - "反模式4: ❌在业务代码中写DDL"
rollback_instructions: "DaaS不满足 → §20 R*"
---

# DB-025-0082：Database-as-Code 原则 §18.3——YAML 4 条规则

§18.3 YAML: 4 条 DaaS 规则全部落地验证。
