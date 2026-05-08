---
module_id: KE-module_blu-18_5________chaos_engineering_-000
title: 18.5 故障注入测试（Chaos Engineering for SQLite）
category: module_blueprint
---

# 18.5 故障注入测试（Chaos Engineering for SQLite）

18.5 故障注入测试（Chaos Engineering for SQLite）

| 故障场景 | 注入方式 | 期望行为 | 测试状态 |
|---------|---------|---------|:---:|
| WAL 文件被删除 | 手动删除 -wal 文件 | WAL 自动重建，不丢数据 | ❌ 待测试 |
| 数据库文件被截断 | 写入空文件覆盖 .db | health_check 检测 corruption → escalation | ❌ 待测试 |
| 磁盘写满 | 填满 tmp 目录 | write_file 失败 → ROLLBACK + 不丢已提交数据 | ❌ 待测试 |
| 事务中途进程崩溃 | kill -9 模拟 | WAL 恢复 → 未提交事务自动回滚 | ❌ 待测试 |
| 并发写入冲突 | 两个进程同时 BEGIN IMMEDIATE | 第二个等待 busy_timeout 5s → SQLITE_BUSY | ❌ 待测试 |
| DuckDB sqlite_scanner 不可用 | 删除 duckdb sqlite_scanner 插件 | OLAPEngine fallback 模式 + 告警 | ✅ olap_engine 已测试 |

---
